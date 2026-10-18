# FreelanceFlow AI

FreelanceFlow AI now includes a full-stack web application plus the original Streamlit implementation.

## Full-stack application

- `backend/`: FastAPI REST API with Pydantic validation, local Ollama generation, SQLite history, and exports. It defaults to `gemma3:1b` and falls back to `qwen2.5:3b`.
- `frontend/`: React + TypeScript + Vite + Tailwind CSS responsive UI.
- `app.py`: preserved legacy Streamlit application. It remains runnable and is not used by the new frontend.

### Backend setup (PowerShell)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
cd ..
uvicorn backend.main:app --reload --port 8000
```

### Frontend setup (second PowerShell terminal)

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open `http://localhost:5173`. Ollama should be running locally and `ollama list` should include `gemma3:1b` or the configured fallback. The default Gemma model is 806 MB; Qwen remains available as a 1.9 GB fallback. The application is local-first, but this documentation does not claim that the complete operating environment is completely offline.

### API endpoints

`GET /api/health`, `GET /api/models`, `GET /api/demo-brief`, `POST /api/analyze`, `POST /api/proposal`, `POST /api/scope`, `POST /api/milestones`, `POST /api/pricing`, `POST /api/invoice`, `GET/POST/DELETE /api/history`, and `GET /api/exports/csv`.

The frontend calls these endpoints through typed functions in `frontend/src/api.ts`. No generated content is mocked.

### Model provenance and evaluation

Gemma is a real part of the product workflow: it extracts goals, requirements, deliverables, assumptions, missing information, and risks from synthetic or user-provided briefs, then supports proposals, scopes, milestones, and invoice drafts. The workspace shows the actual model used for each generated artifact. See [MODEL_EVALUATION.md](./MODEL_EVALUATION.md) for the fixed-brief comparison and its limitations.

### Full-stack tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
cd ..\frontend
npm run typecheck
npm run build
```

Backend tests use a fake Ollama client and do not download models. A separate real Ollama smoke test should be run when Ollama is available.

FreelanceFlow AI is a local-first Streamlit MVP for student freelancers, independent developers, and small businesses. It turns a rough client brief into reviewable drafts for brief analysis, proposals, a scope of work, milestones, transparent pricing, and a draft invoice.

## Setup

1. Install Ollama and start it.
2. Confirm a local model exists with `ollama list`. This project was tested with `qwen2.5:3b`; set `OLLAMA_MODEL` if yours differs.
3. Create an environment and install dependencies:

```powershell
cd FreelanceFlowAI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

4. Launch:

```powershell
streamlit run app.py
```

## Features and safe-use boundaries

- Local Ollama generation with model discovery and clear errors for missing models, timeouts, unreachable services, and malformed JSON.
- Structured output validation before rendering. If a model omits a required field, the backend marks it explicitly as `TBD` rather than inventing a commitment, then validates the normalized response.
- Editable generated drafts and Markdown/text downloads.
- CSV exports for milestones and estimates.
- Pricing uses only user-entered hours, rates, and costs; it does not present market pricing as verified.
- Invoice output is explicitly `DRAFT` and not tax compliant.
- Invoice references are generated locally for each draft; they are not an accounting-system sequence.
- Optional local SQLite history requires an explicit checkbox and can be deleted from the sidebar.
- History endpoints have no user authentication and are intended for the documented loopback-only local launch; do not expose FastAPI on a network or public deployment without adding authentication and per-user authorization.
- CSV exports neutralize spreadsheet formula-leading values; exports should still be treated as untrusted files.
- A demo brief is available from the sidebar.

Review every generated document. It is not legal, tax, contractual, or professional advice and should not be treated as a verified commitment.

## Architecture

`app.py` owns the Streamlit UI. `freelanceflow/ollama_client.py` handles local HTTP calls and failure translation; `prompts.py` defines workflow prompts; `schemas.py` validates brief and model output; `pricing.py` contains deterministic arithmetic; `exports.py` handles downloads; `history.py` provides opt-in SQLite persistence. The app has no paid API, cloud database, credentials, or external integration.

## Testing

```powershell
pytest -q
```

The Ollama tests use a fake session, so tests do not download a model. The launch check still requires a local Ollama service.

## Troubleshooting

- **Ollama is not reachable:** start Ollama and verify `http://127.0.0.1:11434/api/tags`.
- **Model not installed:** run `ollama list`, then set `OLLAMA_MODEL` in `.env`.
- **Timeouts:** shorten the brief or increase `OLLAMA_TIMEOUT_SECONDS`.
- **Malformed output:** retry; the app refuses to export non-object structured responses and marks omitted required fields as explicit `TBD` unknowns.

## Screenshots

Run the app, load the demo brief, and capture the Analyze, Pricing, and Invoice tabs for a submission post. Do not include real client data in screenshots.

## Future improvements

Add versioned project records with per-project deletion, richer schema validation, a small local document editor, PDF export, configurable invoice fields, test coverage for Streamlit interactions, and optional encrypted local storage.

## Hacktoberfest Week 2: Side Hustle preparation

Problem: freelancers lose time translating vague requirements into clear, defensible project documents.

Solution: a local-first assistant that produces editable, transparent drafts while keeping client data and inference on the user's computer. The default local model is Gemma (`gemma3:1b`) through Ollama; Qwen (`qwen2.5:3b`) remains an optional fallback.

Demo walkthrough: load the bakery brief, analyze missing information and risks, generate a proposal and scope, plan milestones, enter your own rate and hours, then create and edit the invoice draft. Export Markdown and CSV. The workspace shows which model generated each artifact.

Submission checklist (verify against the live challenge page before submitting):

- [x] New open-source project with MIT license.
- [x] Core open-weight Gemma use through local Ollama.
- [x] Qwen preserved as an optional fallback.
- [x] Setup and architecture documented.
- [x] Demo brief and reproducible walkthrough included.
- [x] Fixed-brief Gemma/Qwen comparison documented in [MODEL_EVALUATION.md](./MODEL_EVALUATION.md).
- [x] DEV submission draft follows the live Week 2 headings and uses `devchallenge, hf26challenge`.
- [x] Best Use of Gemma is the only claimed prize category, based on implemented usage.
- [ ] Public repository link.
- [ ] Deployed app or demo video link.
- [ ] DEV post written and reviewed by the author.
- [ ] First user feedback.
- [ ] Confirm eligibility, exact deadline, required tags, and submission template immediately before publishing.

Do not submit or publish without reviewing the official rules and approving the final article.

## Publishing

After creating a public repository and demo/video, use the prepared project description and walkthrough as the basis for a DEV draft. Disclose AI assistance honestly and include links to the code and demo. No submission has been made by this repository.

## License

MIT.
