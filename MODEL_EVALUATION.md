# Local model evaluation

This is a small, qualitative comparison of the two locally installed models. It is not a benchmark and does not claim that either model is universally better.

## Environment

- Date: 2026-10-18
- Hardware observed: 23.7 GB system memory; 8.1 GB free during inspection; approximately 179 GB free disk space.
- Models: `gemma3:1b` (806 MB) and `qwen2.5:3b` (1.9 GB).
- Task: run the same client-brief analysis workflow against three fixed, synthetic briefs.
- Validation: every response had to be valid JSON and pass the existing required-field validator.
- Data handling: briefs are synthetic and results were not persisted.

## Observed results

The comparison command is:

```powershell
Set-Location FreelanceFlowAI
.\backend\.venv\Scripts\python.exe -m backend.evaluate_models
```

The recorded run on this machine produced valid structured output for all three briefs with both models:

| Model | Bakery website | Student portfolio | Bicycle repair |
| --- | --- | --- | --- |
| `gemma3:1b` | Validated | Validated | Validated |
| `qwen2.5:3b` | Validated | Validated | Validated |

Qualitatively, Gemma was fast enough for the local workflow and consistently surfaced explicit unknowns in the short briefs. Its smaller responses were concise, but occasionally less detailed in risk phrasing. Qwen produced more elaborated assumptions and risk descriptions, with a slower first response and higher local resource cost. These observations are limited to three synthetic briefs and should not be treated as a general model ranking.

## Product decision

FreelanceFlow defaults to `gemma3:1b` for the Best Use of Gemma story and keeps `qwen2.5:3b` as an environment-configurable fallback. Each generated artifact reports the actual model selected by the backend. Users can override both names through environment variables.
