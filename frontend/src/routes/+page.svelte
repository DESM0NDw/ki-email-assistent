<script lang="ts">
  import '../app.css';

  type Example = { id: string; label: string; subject: string; body: string };
  type Result = { category: string; priority: string; sentiment: string; summary: string; reply: string };

  let examples = $state<Example[]>([]);
  let subject = $state('');
  let body = $state('');
  let loading = $state(false);
  let result = $state<Result | null>(null);
  let error = $state('');
  let activeStep = $state(-1);

  const STEPS = [
    { path: 'M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75', label: 'E-Mail empfangen' },
    { path: 'm21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z', label: 'KI analysiert' },
    { path: 'M9.568 3H5.25A2.25 2.25 0 0 0 3 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 0 0 5.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 0 0 9.568 3Z', label: 'Kategorisiert' },
    { path: 'm16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10', label: 'Antwort generiert' },
  ];

  const PRIORITY_COLOR: Record<string, string> = {
    Hoch: 'priority-high',
    Mittel: 'priority-mid',
    Niedrig: 'priority-low',
  };

  const SENTIMENT_COLOR: Record<string, string> = {
    Positiv: 'sentiment-pos',
    Neutral: 'sentiment-neu',
    Negativ: 'sentiment-neg',
  };

  import { onMount } from 'svelte';
  onMount(async () => {
    const res = await fetch('/api/examples');
    examples = await res.json();
  });

  function selectExample(ex: Example) {
    subject = ex.subject;
    body = ex.body;
    result = null;
    error = '';
  }

  async function runSteps() {
    for (let i = 0; i < STEPS.length; i++) {
      activeStep = i;
      await new Promise(r => setTimeout(r, i === 1 ? 800 : 400));
    }
  }

  async function analyze() {
    if (!subject.trim() || !body.trim() || loading) return;
    loading = true;
    result = null;
    error = '';
    activeStep = 0;

    try {
      const [res] = await Promise.all([
        fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ subject, body }),
        }),
        runSteps(),
      ]);

      if (!res.ok) throw new Error();
      result = await res.json();
      activeStep = STEPS.length;
    } catch {
      error = 'Fehler bei der Analyse. Bitte erneut versuchen.';
      activeStep = -1;
    } finally {
      loading = false;
    }
  }

  function onKeydown(e: KeyboardEvent) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') analyze();
  }
</script>

<div class="wrapper">

  <!-- Header -->
  <header>
    <div class="header-inner">
      <div class="header-left">
        <div class="icon">
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
          </svg>
        </div>
        <div>
          <h1>KI-E-Mail-Assistent</h1>
          <p class="subtitle">Eingehende Mails sortiert, priorisiert und mit Antwort-Entwurf versehen</p>
        </div>
      </div>
      <div class="header-right">
        <span class="demo-badge"><span class="pulse"></span>DEMO</span>
        <a href="https://desmond.autonomika.de" class="back-link" target="_blank">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
          Portfolio
        </a>
      </div>
    </div>
  </header>

  <!-- Automation flow -->
  <div class="flow-bar">
    <p class="flow-label">So läuft die Automation:</p>
    <div class="flow-steps">
      {#each STEPS as step, i}
        <div class="flow-step {activeStep === i ? 'active' : ''} {activeStep > i ? 'done' : ''}">
          <svg class="step-icon" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d={step.path} />
          </svg>
          <span class="step-label">{step.label}</span>
        </div>
        {#if i < STEPS.length - 1}
          <div class="flow-arrow {activeStep > i ? 'done' : ''}">→</div>
        {/if}
      {/each}
    </div>
    <p class="flow-hint">In der echten Integration läuft dieser Prozess vollautomatisch im Hintergrund — keine manuelle Eingabe nötig.</p>
  </div>

  <main>

    <div class="content">

      <!-- Input -->
      <div class="input-panel">
        <div class="panel-header">
          <h2>E-Mail eingeben</h2>
          <span class="panel-hint">Ctrl+Enter zum Analysieren</span>
        </div>

        {#if examples.length > 0}
          <div class="examples">
            <p class="examples-label">Beispiele:</p>
            <div class="example-chips">
              {#each examples as ex}
                <button class="example-chip" onclick={() => selectExample(ex)}>{ex.label}</button>
              {/each}
            </div>
          </div>
        {/if}

        <div class="field">
          <label for="subject">Betreff</label>
          <input
            id="subject"
            type="text"
            placeholder="Betreff der E-Mail..."
            bind:value={subject}
            disabled={loading}
          />
        </div>

        <div class="field">
          <label for="body">Inhalt</label>
          <textarea
            id="body"
            placeholder="E-Mail-Text hier eingeben..."
            bind:value={body}
            onkeydown={onKeydown}
            disabled={loading}
            rows="10"
          ></textarea>
        </div>

        <button class="analyze-btn" onclick={analyze} disabled={loading || !subject.trim() || !body.trim()}>
          {#if loading}
            <span class="spinner"></span>
            Analysiere...
          {:else}
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
            </svg>
            E-Mail analysieren
          {/if}
        </button>
        <div class="warn-box">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="flex-shrink:0;margin-top:1px">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
          </svg>
          <span>Eingaben werden zur Verarbeitung an <strong>Groq (USA)</strong> übermittelt und können dort gespeichert werden. Bitte <strong>keine echten oder vertraulichen E-Mails</strong> eingeben.</span>
        </div>
      </div>

      <!-- Result -->
      <div class="result-panel">
        <div class="panel-header">
          <h2>Analyse-Ergebnis</h2>
        </div>

        {#if error}
          <div class="error">{error}</div>
        {:else if result}
          <div class="result">
            <div class="tags">
              <div class="tag-row">
                <span class="tag-label">Kategorie</span>
                <span class="tag category">{result.category}</span>
              </div>
              <div class="tag-row">
                <span class="tag-label">Priorität</span>
                <span class="tag {PRIORITY_COLOR[result.priority] ?? 'priority-mid'}">{result.priority}</span>
              </div>
              <div class="tag-row">
                <span class="tag-label">Stimmung</span>
                <span class="tag {SENTIMENT_COLOR[result.sentiment] ?? 'sentiment-neu'}">{result.sentiment}</span>
              </div>
            </div>

            <div class="result-section">
              <h3>Zusammenfassung</h3>
              <p>{result.summary}</p>
            </div>

            <div class="result-section reply-section">
              <div class="reply-header">
                <h3>Antwortvorschlag</h3>
                <button class="copy-btn" onclick={() => navigator.clipboard.writeText(result!.reply)}>
                  <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184" />
                  </svg>
                  Kopieren
                </button>
              </div>
              <p class="reply-text">{result.reply}</p>
            </div>
          </div>
        {:else}
          <div class="empty-state">
            <svg width="40" height="40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
            </svg>
            <p>E-Mail eingeben und analysieren</p>
            <p class="empty-hint">Oder ein Beispiel oben auswählen</p>
          </div>
        {/if}
      </div>

    </div>

    <!-- n8n Workflow Diagram -->
    <div class="n8n-section">
      <div class="n8n-head">
        <span class="n8n-badge">n8n</span>
        <div>
          <p class="n8n-title">Echte Automation</p>
          <p class="n8n-desc">So läuft dieser Prozess als n8n-Workflow für ein echtes Postfach — vollautomatisch, ohne manuelle Eingabe.</p>
        </div>
      </div>

      <div class="n8n-diagram">
        <div class="n8n-node nd-trigger">
          <svg class="nd-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
          </svg>
          <div class="nd-text">
            <span class="nd-type">Gmail Trigger</span>
            <span class="nd-name">Neue E-Mail</span>
          </div>
        </div>
        <span class="n8n-arr">→</span>
        <div class="n8n-node">
          <svg class="nd-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
          </svg>
          <div class="nd-text">
            <span class="nd-type">HTTP Request</span>
            <span class="nd-name">Groq API</span>
          </div>
        </div>
        <span class="n8n-arr">→</span>
        <div class="n8n-node">
          <svg class="nd-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5" />
          </svg>
          <div class="nd-text">
            <span class="nd-type">Code Node</span>
            <span class="nd-name">JSON parsen</span>
          </div>
        </div>
        <span class="n8n-arr">→</span>
        <div class="n8n-node nd-switch">
          <svg class="nd-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="m3.75 13.5 10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75Z" />
          </svg>
          <div class="nd-text">
            <span class="nd-type">Switch</span>
            <span class="nd-name">Priorität?</span>
          </div>
        </div>
        <span class="n8n-arr">→</span>
        <div class="n8n-branch-col">
          <div class="n8n-node">
            <svg class="nd-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
            </svg>
            <div class="nd-text">
              <span class="lbl-high">Hoch</span>
              <span class="nd-name">Slack Alert</span>
            </div>
          </div>
          <div class="n8n-node">
            <svg class="nd-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9.568 3H5.25A2.25 2.25 0 0 0 3 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 0 0 5.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 0 0 9.568 3Z" />
            </svg>
            <div class="nd-text">
              <span class="lbl-mid">Mittel</span>
              <span class="nd-name">Label setzen</span>
            </div>
          </div>
          <div class="n8n-node">
            <svg class="nd-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="m20.25 7.5-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z" />
            </svg>
            <div class="nd-text">
              <span class="lbl-low">Niedrig</span>
              <span class="nd-name">Archivieren</span>
            </div>
          </div>
        </div>
        <span class="n8n-arr">→</span>
        <div class="n8n-node nd-output">
          <svg class="nd-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
          </svg>
          <div class="nd-text">
            <span class="nd-type">Gmail</span>
            <span class="nd-name">Antwort-Entwurf</span>
          </div>
        </div>
      </div>

      <div class="n8n-divider">
        <span>Echter n8n Workflow</span>
      </div>
      <img src="/n8n-workflow-v2.png" alt="n8n Workflow Screenshot" class="n8n-screenshot" />
    </div>

  </main>

  <footer>
    Demo von <a href="https://desmond.autonomika.de" target="_blank">Desmond Wong</a>
    &middot; Stack: Groq &middot; llama-3.1-8b &middot; SvelteKit
    &middot; <a href="/impressum">Impressum & Datenschutz</a>
  </footer>

</div>

<style>
  .wrapper { min-height: 100vh; display: flex; flex-direction: column; background: #0c0c0c; }

  /* Header */
  header {
    position: sticky; top: 0; z-index: 20;
    background: rgba(12,12,12,0.95); backdrop-filter: blur(8px);
    border-bottom: 1px solid #1e1e1e;
  }
  .header-inner {
    max-width: 1200px; margin: 0 auto; padding: 0 1.25rem;
    height: 52px; display: flex; align-items: center; justify-content: space-between;
  }
  .header-left { display: flex; align-items: center; gap: 0.75rem; }
  .icon {
    width: 34px; height: 34px; border-radius: 9px; flex-shrink: 0;
    background: rgba(34,211,238,0.1); color: #22d3ee;
    display: flex; align-items: center; justify-content: center;
  }
  h1 { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; }
  .subtitle { font-size: 0.7rem; color: #94a3b8; }
  .header-right { display: flex; align-items: center; gap: 0.75rem; }
  .demo-badge {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.05em;
    color: #22d3ee; background: rgba(34,211,238,0.1);
    border: 1px solid rgba(34,211,238,0.2); padding: 2px 8px; border-radius: 999px;
  }
  .pulse { width: 5px; height: 5px; border-radius: 50%; background: #22d3ee; animation: pulse 1.5s ease-in-out infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
  .back-link {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.72rem; color: #94a3b8; text-decoration: none; transition: color 0.15s;
  }
  .back-link:hover { color: #94a3b8; }

  /* Flow bar */
  .flow-bar {
    background: #111; border-bottom: 1px solid #1e1e1e;
    padding: 0.75rem 1.25rem; display: flex; flex-direction: column; align-items: center;
  }
  .flow-label { font-size: 0.75rem; color: #b0bfcc; margin-bottom: 0.5rem; }
  .flow-steps {
    display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; justify-content: center;
  }
  .flow-step {
    display: flex; align-items: center; gap: 0.4rem;
    background: #0c0c0c; border: 1px solid #1e1e1e;
    border-radius: 8px; padding: 0.35rem 0.65rem;
    font-size: 0.82rem; color: #b0bfcc;
    transition: all 0.3s;
  }
  .flow-step.active {
    border-color: #22d3ee; color: #22d3ee; background: rgba(34,211,238,0.06);
  }
  .flow-step.done { border-color: #22c55e; color: #22c55e; background: rgba(34,197,94,0.06); }
  .step-icon { flex-shrink: 0; }
  .flow-arrow { font-size: 0.75rem; color: #475569; transition: color 0.3s; }
  .flow-arrow.done { color: #22c55e; }
  .flow-hint { font-size: 0.73rem; color: #94a3b8; margin-top: 0.5rem; text-align: center; }

  /* Main content */
  main { flex: 1; max-width: 1200px; width: 100%; margin: 0 auto; padding: 1.25rem; }
  .content { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }

  /* Panels */
  .input-panel, .result-panel {
    background: #111; border: 1px solid #1e1e1e; border-radius: 14px;
    padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem;
  }
  .panel-header {
    display: flex; align-items: center; justify-content: space-between;
  }
  h2 { font-size: 0.9rem; font-weight: 700; color: #f1f5f9; }
  .panel-hint { font-size: 0.73rem; color: #94a3b8; }

  /* Examples */
  .examples { display: flex; flex-direction: column; gap: 0.4rem; }
  .examples-label { font-size: 0.75rem; color: #b0bfcc; }
  .example-chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .example-chip {
    font-size: 0.8rem; color: #b0bfcc; background: #0c0c0c;
    border: 1px solid #252525; padding: 0.25rem 0.6rem; border-radius: 999px;
    cursor: pointer; transition: all 0.15s; text-align: left;
  }
  .example-chip:hover { background: #1a1a1a; color: #f1f5f9; border-color: #22d3ee; }

  /* Fields */
  .field { display: flex; flex-direction: column; gap: 0.35rem; }
  label { font-size: 0.82rem; color: #c8d8e4; font-weight: 500; }
  input, textarea {
    background: #0c0c0c; border: 1px solid #252525; color: #e2e8f0;
    border-radius: 10px; padding: 0.55rem 0.85rem; font-size: 0.83rem;
    outline: none; transition: border-color 0.15s; resize: vertical;
    font-family: inherit;
  }
  input:focus, textarea:focus { border-color: #22d3ee; }
  input::placeholder, textarea::placeholder { color: #475569; }
  input:disabled, textarea:disabled { opacity: 0.5; }

  /* Analyze button */
  .analyze-btn {
    display: flex; align-items: center; justify-content: center; gap: 0.5rem;
    background: #22d3ee; color: #000; border: none;
    border-radius: 10px; padding: 0.65rem 1rem; font-size: 0.85rem; font-weight: 600;
    cursor: pointer; transition: background 0.15s;
  }
  .analyze-btn:hover:not(:disabled) { background: #06b6d4; }
  .analyze-btn:disabled { opacity: 0.4; cursor: default; }
  .spinner {
    width: 14px; height: 14px; border: 2px solid rgba(0,0,0,0.3);
    border-top-color: #000; border-radius: 50%; animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .warn-box {
    display: flex; align-items: flex-start; gap: 0.5rem;
    background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.2);
    border-radius: 8px; padding: 0.6rem 0.75rem;
    font-size: 0.75rem; color: #b8900a; line-height: 1.5;
  }
  .warn-box strong { color: #d4a820; }

  /* Result */
  .tags { display: flex; flex-direction: column; gap: 0.5rem; }
  .tag-row { display: flex; align-items: center; gap: 0.5rem; }
  .tag-label { font-size: 0.78rem; color: #b0bfcc; width: 70px; flex-shrink: 0; }
  .tag {
    font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 5px;
  }
  .category { color: #60a5fa; background: rgba(96,165,250,0.1); border: 1px solid rgba(96,165,250,0.2); }
  .priority-high { color: #f87171; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.2); }
  .priority-mid { color: #22d3ee; background: rgba(34,211,238,0.1); border: 1px solid rgba(34,211,238,0.2); }
  .priority-low { color: #4ade80; background: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.2); }
  .sentiment-pos { color: #4ade80; background: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.2); }
  .sentiment-neu { color: #94a3b8; background: rgba(148,163,184,0.1); border: 1px solid rgba(148,163,184,0.2); }
  .sentiment-neg { color: #f87171; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.2); }

  .result-section { display: flex; flex-direction: column; gap: 0.4rem; }
  .result-section h3 { font-size: 0.8rem; font-weight: 600; color: #b0bfcc; text-transform: uppercase; letter-spacing: 0.05em; }
  .result-section p { font-size: 0.92rem; color: #e2eaf2; line-height: 1.6; }

  .reply-section { background: #0c0c0c; border: 1px solid #1e1e1e; border-radius: 10px; padding: 0.85rem; }
  .reply-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
  .copy-btn {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.68rem; color: #475569; background: #111;
    border: 1px solid #252525; border-radius: 6px; padding: 2px 8px;
    cursor: pointer; transition: all 0.15s;
  }
  .copy-btn:hover { color: #94a3b8; border-color: #333; }
  .reply-text { font-size: 0.92rem; color: #e2eaf2; line-height: 1.7; white-space: pre-wrap; }

  /* Empty state */
  .empty-state {
    flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 0.75rem; color: #94a3b8; padding: 3rem 1rem; text-align: center;
  }
  .empty-state p { font-size: 0.9rem; color: #b0bfcc; }
  .empty-hint { font-size: 0.8rem; color: #94a3b8; }

  .error { background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; border-radius: 10px; padding: 0.75rem; font-size: 0.83rem; }

  footer { text-align: center; font-size: 0.68rem; color: #475569; padding: 0.6rem; border-top: 1px solid #1e1e1e; }
  footer a { color: #64748b; text-decoration: none; }
  footer a:hover { color: #94a3b8; }

  /* n8n section */
  .n8n-section {
    margin-top: 1.5rem;
    background: #111; border: 1px solid #1e1e1e; border-radius: 14px; padding: 1.25rem;
  }
  .n8n-head { display: flex; align-items: flex-start; gap: 0.75rem; margin-bottom: 1rem; }
  .n8n-badge {
    font-size: 0.65rem; font-weight: 800; letter-spacing: 0.04em;
    background: #f97316; color: white; padding: 2px 8px; border-radius: 5px; flex-shrink: 0; margin-top: 2px;
  }
  .n8n-title { font-size: 0.88rem; font-weight: 700; color: #f1f5f9; }
  .n8n-desc { font-size: 0.76rem; color: #94a3b8; margin-top: 2px; line-height: 1.5; }

  .n8n-diagram { display: flex; align-items: center; justify-content: center; gap: 0.4rem; overflow-x: auto; padding: 0.25rem 0; }
  .n8n-branch-col { display: flex; flex-direction: column; gap: 0.4rem; }
  .n8n-arr { font-size: 0.8rem; color: #333; flex-shrink: 0; }
  .n8n-vline { width: 1px; height: 1.25rem; background: #333; margin: 0.1rem 0; }
  .n8n-node { display: flex; align-items: center; gap: 0.6rem; flex-shrink: 0; background: #0c0c0c; border: 1px solid #252525; border-radius: 9px; padding: 0.5rem 0.85rem; }
  .nd-trigger { border-color: rgba(249,115,22,0.4); }
  .nd-switch { border-color: rgba(34,211,238,0.4); }
  .nd-output { border-color: rgba(34,197,94,0.4); }
  .nd-icon { width: 16px; height: 16px; flex-shrink: 0; color: #94a3b8; }
  .nd-text { display: flex; flex-direction: column; gap: 2px; }
  .nd-type { font-size: 0.68rem; color: #94a3b8; line-height: 1.3; }
  .nd-name { font-size: 0.82rem; font-weight: 600; color: #e2e8f0; line-height: 1.3; }
  .lbl-high { font-size: 0.68rem; font-weight: 700; padding: 1px 6px; border-radius: 999px; color: #f87171; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.2); }
  .lbl-mid { font-size: 0.68rem; font-weight: 700; padding: 1px 6px; border-radius: 999px; color: #22d3ee; background: rgba(34,211,238,0.1); border: 1px solid rgba(34,211,238,0.2); }
  .lbl-low { font-size: 0.68rem; font-weight: 700; padding: 1px 6px; border-radius: 999px; color: #4ade80; background: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.2); }

  .n8n-divider {
    display: flex; align-items: center; gap: 0.75rem; margin: 1.25rem 0 1rem;
  }
  .n8n-divider::before, .n8n-divider::after { content: ''; flex: 1; height: 1px; background: #1e1e1e; }
  .n8n-divider span { font-size: 0.72rem; color: #94a3b8; white-space: nowrap; }
  .n8n-screenshot { width: 100%; border-radius: 10px; border: 1px solid #1e1e1e; }

  /* Mobile */
  @media (max-width: 768px) {
    .content { grid-template-columns: 1fr; }
    .subtitle { display: none; }
    .flow-steps { gap: 0.3rem; }
    .flow-arrow { display: none; }
  }
</style>
