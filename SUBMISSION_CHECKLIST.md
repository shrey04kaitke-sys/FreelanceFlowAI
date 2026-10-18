# Hacktoberfest Week 2 submission checklist

This checklist is for the Hacktoberfest 2026 Week 2 Open-Source AI Challenge. The project has not been published, deployed, or submitted.

## Launch on Windows PowerShell

### Terminal 1: FastAPI

```powershell
Set-Location 'C:\Users\shrey\OneDrive\Desktop\BOOKS NAME & IMAGES\00_Home\03_projects\freelanceAI\FreelanceFlowAI'
.\backend\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2: React/Vite

```powershell
Set-Location 'C:\Users\shrey\OneDrive\Desktop\BOOKS NAME & IMAGES\00_Home\03_projects\freelanceAI\FreelanceFlowAI\frontend'
node .\node_modules\vite\bin\vite.js --host 127.0.0.1 --port 5173
```

Open `http://localhost:5173`. Confirm Ollama is running and `ollama list` includes `gemma3:1b` or the configured fallback.

## Automated verification

```powershell
Set-Location 'C:\Users\shrey\OneDrive\Desktop\BOOKS NAME & IMAGES\00_Home\03_projects\freelanceAI\FreelanceFlowAI'
.\backend\.venv\Scripts\python.exe -m pytest -q backend\tests tests
Set-Location .\frontend
node .\node_modules\typescript\bin\tsc --noEmit
node .\node_modules\vite\bin\vite.js build
```

## Manual product checklist

- [ ] `/api/health` reports Ollama reachable and configured/fallback models.
- [ ] `/api/models` lists `gemma3:1b` and `qwen2.5:3b` when both are installed.
- [ ] Load the demo brief and analyze it with the real Gemma model.
- [ ] Generate proposal, scope, and milestone drafts.
- [ ] Edit a generated document and confirm the edited content remains visible.
- [ ] Generate a pricing estimate using user-entered rate, hours, and direct costs.
- [ ] Generate an invoice and confirm it is labelled `DRAFT`.
- [ ] Download Markdown and CSV/text exports and inspect their contents.
- [ ] Save history only after explicit consent, then inspect and delete the record.
- [ ] Stop Ollama or set an unavailable model and confirm the UI shows an understandable error.
- [ ] Try a too-short brief and confirm validation prevents generation.
- [ ] Review all generated content before sharing with a client.

## Safe GitHub publication checklist

- [ ] Run `git status --short --ignored` from the project root.
- [ ] Confirm no `.env` or `.env.*` secret files are tracked.
- [ ] Confirm no `*.sqlite3`, `*.db`, client briefs, logs, screenshots containing private data, `.venv`, `node_modules`, or build output is tracked.
- [ ] Keep the API bound to `127.0.0.1`; do not expose history endpoints publicly without authentication and per-user authorization.
- [ ] Keep `.env.example`, `backend/.env.example`, and `frontend/.env.example`; they contain non-secret local defaults only.
- [ ] Review dependency manifests and lockfiles for intended versions.
- [ ] Add a public repository URL to `DEV_ARTICLE_DRAFT.md` only after the repository exists.
- [ ] Create a new repository and make the first commit only after reviewing the staged file list.
- [ ] Do not publish client data, credentials, local model caches, or personal information.

## Demo recording shot list

1. Dashboard empty state and privacy positioning.
2. New Project page with the synthetic bakery brief.
3. Local AI status and model provenance.
4. Brief analysis showing goals, deliverables, assumptions, missing information, and risks.
5. Proposal or scope draft being edited.
6. Milestone plan with review checkpoints and dependencies.
7. Pricing assistant with transparent user-entered values.
8. Invoice draft with the visible `DRAFT` warning.
9. Markdown/CSV export action.
10. History save consent, saved record, and deletion.
11. Settings page showing backend/Ollama status and retention information.

Use only the synthetic demo brief in recordings unless every client has explicitly consented.

## Remaining placeholders

- Public GitHub URL: `<ADD_AFTER_REPOSITORY_CREATION>`
- Demo video or deployed URL: `<ADD_AFTER_RECORDING_OR_DEPLOYMENT>`
- First-user name/role: `<ADD_ONLY_WITH_CONSENT>`
- First-user feedback and observed improvement: `<ADD_VERIFIED_FEEDBACK_OR_REMOVE_SECTION>`

## Final article review

- [ ] Keep front matter `published: false` until final human approval.
- [ ] Keep tags exactly `devchallenge, hf26challenge`.
- [ ] Confirm headings match the live template: What I Built, Demo, Code, How I Built It, My First User, Prize Categories.
- [ ] Claim Best Use of Gemma only because Gemma is the default core model and its real local integration is demonstrated.
- [ ] Include the actual repository and demo/video links.
- [ ] Describe the three-brief model comparison as qualitative, not a general benchmark.
- [ ] Include actual tests and limitations without inventing user feedback or performance.
- [ ] Check the live challenge page for deadline, eligibility, rules, and required template immediately before publishing.
- [ ] Review screenshots and article text for private briefs, credentials, and local paths.
- [ ] Publish only after explicit author approval.
