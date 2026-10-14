# CLAUDE.md — FDE Interview Prep Assistant

## What we're building
A small FastAPI app that runs mock Forward Deployed Engineer interviews and
scores the answers against a 4-category rubric (0–5 each, max 20). Favour
**clarity over cleverness** — every line should be explainable in an interview.

## Stack
- Python 3.11+, **FastAPI** (served by uvicorn), **Pydantic v2**
- Data: plain **JSON files** in `data/` — no database
- Scoring: an offline **mock** scorer, or the **OpenAI API** when
  `OPENAI_API_KEY` is set (the model id lives in one constant, `app/config.MODEL_ID`)
- Tests: **pytest** + FastAPI `TestClient` — never call the network in a test
- Lint/types: **ruff** (rules E, F; line length 100) and **mypy**

## Project layout
- `app/main.py` — endpoints only; thin handlers that delegate
- `app/models.py` — every Pydantic request/response/record schema
- `app/data.py` — the ONLY module that touches files in `data/`
- `app/scoring.py` — mock scorer, OpenAI scorer, total + scorecard assembly
- `app/progress.py` — pure logic for `/progress` (no I/O)
- `app/config.py` — paths, `MODEL_ID`, `USE_MOCK`; all settings live here
- `data/` — `questions.json`, `rubric.md`, `results.json` (written by `/score`)
- `resources/` — interview guides (served via MCP in Module 5)
- `tests/` — one file per feature area

Endpoints: `GET /health`, `GET /rounds`, `GET /questions?round=`,
`POST /score`, `GET /progress`.

## Conventions
- Every module starts with a docstring saying what it's for and why it's separate,
  then `from __future__ import annotations`.
- Type hints on every function, including the return type.
- Keep I/O and logic apart: disk access in `data.py`, calculations in pure
  functions that take and return models (as in `progress.py`).
- Validate before you change anything: e.g. `/score` returns 404 for an unknown
  round or question *before* anything is scored or saved.
- Unknown resources mean `HTTPException(status_code=404, detail=...)`.
- "No data yet" is `None`, not `0`.
- Comments explain *why*, not *what*. Keep functions small and flat.
- Tests that hit endpoints use a `tmp_data`-style fixture: copy `questions.json`
  to `tmp_path`, monkeypatch `app.data.DATA_DIR` (not `app.config`'s) and
  `app.scoring.USE_MOCK = True`.

## Guardrails for you, the agent
- **Workshop exercises are intentional — don't "fix" them unprompted.** The
  `compute_total()` bug, the messy `format_scorecard()` and the
  `score_with_openai()` stub in `app/scoring.py` are for Module 3. Point them
  out if relevant, but change them only when asked.
- Never read or write the real `data/results.json` in tests; never call
  OpenAI (or any network) from tests.
- Never commit `.env` or API keys. The app's OpenAI key is unrelated to Claude
  Code's Anthropic credential — don't mix them up.
- Don't add dependencies, a database, or new frameworks without asking.
- Don't edit `../checkpoints/` — those are reference snapshots.
- Change the model only via `MODEL_ID` / `OPENAI_MODEL`; never hard-code one.
- Before multi-file changes, state the plan. After any change, run `pytest -q`
  and report the real result.

## How to run
```
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload      # open http://127.0.0.1:8000/docs
pytest -q
ruff check . && mypy app
```
Optional: `cp .env.example .env` and set `OPENAI_API_KEY` for real scoring.
