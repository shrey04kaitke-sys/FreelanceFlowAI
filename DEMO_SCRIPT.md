# FreelanceFlow AI demo script

Target length: 2–3 minutes. Use the synthetic bakery brief from `sample_brief.md`; do not record real client information.

## Setup before recording

1. Start Ollama and confirm `ollama list` includes `gemma3:1b`.
2. Start the backend on `127.0.0.1:8000`.
3. Start the Vite frontend on `127.0.0.1:5173`.
4. Open the frontend in a clean browser session.
5. Keep the backend terminal available but do not show local paths or private files.

## Narration and shot list

### 0:00–0:20 — The problem

**Screen:** Dashboard.

**Narration:** “A freelance brief often arrives as a vague paragraph, but the freelancer still needs a proposal, scope, milestones, pricing assumptions, and an invoice draft. FreelanceFlow AI turns that rough starting point into reviewable project documents without sending the brief to a paid cloud AI API.”

### 0:20–0:40 — Start with a brief

**Screen:** New Project page.

**Action:** Click **Load demo brief**.

**Narration:** “I’ll use a synthetic bakery brief so no private client information is exposed. The brief includes a mobile website, weekly menu, cake enquiries, opening hours, owner updates, and Friday reviews.”

### 0:40–1:00 — Gemma analysis

**Screen:** Click **Analyze brief**, then show the AI Workspace.

**Narration:** “Gemma 3 1B is running locally through Ollama. The analyzer extracts goals, deliverables, assumptions, missing information, and risks. The workspace records which model generated the artifact, and every draft carries a human-review warning.”

**Expected output:** Editable structured analysis with fields such as objectives, deliverables, assumptions, missing information, and risks. Some uncertain fields may be `TBD`.

### 1:00–1:35 — Proposal and scope

**Screen:** Proposal tab, then Scope of work tab.

**Action:** Generate each document and edit one sentence or field.

**Narration:** “The same brief can produce a proposal and a scope of work. I can edit the generated JSON-backed draft before saving or exporting. Missing client information remains visible as `TBD`; the assistant is not authorized to invent commitments.”

### 1:35–1:55 — Milestones and pricing

**Screen:** Milestones tab, then Pricing assistant.

**Action:** Generate milestones. Add or edit a line item, rate, hours, and direct cost. Calculate.

**Narration:** “Milestones include phases, dependencies, and review checkpoints. Pricing is deterministic Python arithmetic using only my own rate, hours, and direct costs. The model does not invent market prices.”

### 1:55–2:15 — Invoice draft and export

**Screen:** Invoice draft tab.

**Action:** Generate invoice, show the `DRAFT` badge, click Download Markdown.

**Narration:** “The invoice is explicitly a draft, not a tax-compliant invoice. I can review it and export Markdown. Milestones and cost breakdowns also support CSV export through the API.”

### 2:15–2:35 — Privacy and history

**Screen:** Settings & Privacy, then Projects & History.

**Narration:** “Inference stays with the local Ollama service configured on this machine. Briefs are not automatically saved. History requires an explicit save action and can be deleted. This is local-first, not a claim that every aspect of the operating environment is completely offline.”

### 2:35–2:50 — Open innovation

**Screen:** Settings page with model status.

**Narration:** “Gemma is the default open-weight model and Qwen is an optional fallback. Running the model locally provides control over client data and avoids per-request cloud AI charges, while the tradeoff is local hardware and model latency.”

## Fallback instructions

- If Ollama is unavailable, show the Settings page error state rather than fabricating output.
- If Gemma is missing, install it with `ollama pull gemma3:1b` or configure the documented Qwen fallback.
- If generation times out, use the shorter demo brief and retry.
- If a model returns incomplete JSON, the backend normalizes omitted required fields to explicit `TBD`; show the human-review warning.
- If the frontend cannot reach FastAPI, restart the backend and show the honest connectivity error.

## Recording safety

- Use only the synthetic bakery brief.
- Do not show terminals containing environment variables, local paths, credentials, or private files.
- Do not claim deployment, users, revenue, or challenge submission.
- Do not call the output legal, tax, or professionally verified advice.
