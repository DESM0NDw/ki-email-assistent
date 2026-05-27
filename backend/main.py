import os
import time
from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

EXAMPLES = [
    {
        "id": "support",
        "label": "Kundenanfrage — Technischer Support",
        "subject": "Problem mit der Rechnungsstellung",
        "body": "Guten Tag,\n\nich habe seit gestern keinen Zugriff mehr auf mein Konto und kann keine Rechnungen mehr abrufen. Ich benötige die Rechnung vom letzten Monat dringend für meine Buchhaltung. Können Sie mir bitte schnellstmöglich helfen? Das ist sehr dringend.\n\nMit freundlichen Grüßen\nMarkus Bauer",
    },
    {
        "id": "sales",
        "label": "Vertriebsanfrage — Neukunde",
        "subject": "Interesse an Ihrer Software",
        "body": "Hallo,\n\nwir sind ein mittelständisches Unternehmen mit ca. 50 Mitarbeitern und suchen nach einer Lösung für unser Projektmanagement. Ich habe Ihre Produktseite besucht und bin interessiert. Könnten Sie mir mehr Informationen zu den Preisen und einer möglichen Testphase zukommen lassen?\n\nBeste Grüße\nSandra Müller\nGeschäftsführerin, TechFlow GmbH",
    },
    {
        "id": "complaint",
        "label": "Beschwerde — Unzufriedener Kunde",
        "subject": "Sehr enttäuscht von Ihrem Service",
        "body": "Ich bin absolut unzufrieden mit Ihrem Service! Ich warte seit zwei Wochen auf eine Antwort auf meine Anfrage und habe bisher nichts gehört. Das ist kein akzeptabler Kundenservice. Wenn sich das nicht sofort ändert, werde ich meinen Vertrag kündigen und eine negative Bewertung hinterlassen.\n\nMax Schneider",
    },
    {
        "id": "internal",
        "label": "Interne E-Mail — Meetinganfrage",
        "subject": "Teammeeting nächste Woche",
        "body": "Hi zusammen,\n\nich würde gerne nächste Woche ein kurzes Teammeeting abhalten um den Status der Q3-Projekte zu besprechen. Wäre Dienstag 10 Uhr oder Mittwoch 14 Uhr für alle möglich? Bitte kurz Bescheid geben.\n\nDanke und Grüße\nLisa",
    },
]

RATE_LIMIT = 20
RATE_WINDOW = 3600
_requests: dict = defaultdict(list)


def get_ip(request: Request) -> str:
    fwd = request.headers.get("X-Forwarded-For")
    return fwd.split(",")[0].strip() if fwd else request.client.host


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.method == "POST":
        ip = get_ip(request)
        now = time.time()
        _requests[ip] = [t for t in _requests[ip] if now - t < RATE_WINDOW]
        if len(_requests[ip]) >= RATE_LIMIT:
            return JSONResponse(status_code=429, content={"detail": "Zu viele Anfragen. Bitte später erneut versuchen."})
        _requests[ip].append(now)
    return await call_next(request)


groq_client = Groq(api_key=GROQ_API_KEY)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/examples")
def get_examples():
    return [{"id": e["id"], "label": e["label"], "subject": e["subject"], "body": e["body"]} for e in EXAMPLES]


class AnalyzeRequest(BaseModel):
    subject: str
    body: str


class AnalyzeResponse(BaseModel):
    category: str
    priority: str
    sentiment: str
    summary: str
    reply: str


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    prompt = f"""Analysiere die folgende E-Mail und antworte ausschließlich im angegebenen JSON-Format.

Betreff: {req.subject}
Inhalt: {req.body}

Antworte mit diesem JSON (keine weiteren Erklärungen, nur JSON):
{{
  "category": "<eine von: Support, Vertrieb, Beschwerde, Intern, Spam, Sonstiges>",
  "priority": "<eine von: Hoch, Mittel, Niedrig>",
  "sentiment": "<eine von: Positiv, Neutral, Negativ>",
  "summary": "<1-2 Sätze was die E-Mail zusammenfasst>",
  "reply": "<professioneller Antwortvorschlag auf Deutsch, 3-5 Sätze>"
}}"""

    completion = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.2,
    )

    import json
    text = completion.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    data = json.loads(text.strip())
    return AnalyzeResponse(**data)
