# KI-E-Mail-Assistent

AI email automation demo. Paste an email, get automatic categorization, priority, sentiment analysis, and a reply draft.

**Live:** https://email-demo.autonomika.de

## How it works

1. User inputs email subject + body (or selects an example)
2. [Groq](https://groq.com/) (llama-3.1-8b-instant) analyzes the email
3. Returns: category, priority (Hoch/Mittel/Niedrig), sentiment, summary, reply draft
4. In a real integration this runs fully automated via n8n (see workflow below)

## n8n Automation Workflow

The included n8n workflow (`docs/n8n-workflow.json`) shows how this would run against a real Gmail inbox:

```
Gmail Trigger → Groq API → JSON parsen → Switch Priorität
                                              ├─ Hoch   → Slack Alert senden
                                              ├─ Mittel → Gmail Label setzen
                                              └─ Niedrig → Gmail Archivieren
                                                    └─→ Antwort-Entwurf erstellen
```

Import via: n8n → Import from file → `docs/n8n-workflow.json`

## Stack

| Layer | Tech |
|-------|------|
| Frontend | SvelteKit + adapter-static + Nginx |
| Backend | FastAPI + Python |
| LLM | Groq API (`llama-3.1-8b-instant`) |
| Automation | n8n |
| Deploy | Docker Compose on Hetzner Cloud |

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # add GROQ_API_KEY
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Deploy

```bash
docker compose build --no-cache
docker compose up -d
```

Requires the `1panel-network` Docker network and a `GROQ_API_KEY` in the backend environment.
