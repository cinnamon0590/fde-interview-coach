# FDE Interview Coach

A small FastAPI app for practising **Forward Deployed Engineer** interviews. It serves
interview questions, scores your answers against a 4-category rubric, and tracks your
progress over time.

## The rubric

Each answer is scored **0–5** on four categories, for a total out of **20**:

| Category | What it checks |
| --- | --- |
| Clarifying questions | Did you surface unknowns (data, stakeholders, constraints, success criteria) before solving? |
| Decomposition | Did you turn a vague problem into a scoped, sequenced plan with a testable first deliverable? |
| Risk identification | Did you name the riskiest assumption and how you'd de-risk it? |
| Communication | Was the answer structured, concise, and easy for a non-technical listener to follow? |

The full rubric is in [`data/rubric.md`](data/rubric.md).

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000/docs**. The interactive API page is the app's UI.

## API

| Endpoint | What it does |
| --- | --- |
| `GET /health` | Liveness check |
| `GET /rounds` | List the round types: `behavioral`, `client-roleplay`, `decomposition`, `system-design` |
| `GET /questions?round=<round>` | Questions for one round (404 if the round is unknown) |
| `POST /score` | Score an answer and save the result to `data/results.json` |
| `GET /progress` | Number of answers scored so far and the average total (`null` until something is scored) |

Example:

```bash
curl -X POST http://127.0.0.1:8000/score \
  -H "Content-Type: application/json" \
  -d '{"round": "decomposition", "question_id": "dec-01", "answer": "First I would ask..."}'
```

`/score` checks that the round and question exist **before** scoring anything, so an
unknown one returns 404 and nothing is saved.

## Scoring

By default answers are scored by an **offline mock scorer**. It's deterministic and needs
no API key: longer, more structured answers score a little higher. It's there so the app
and tests work with zero setup. It isn't a real judge of quality.

Scoring with OpenAI is **not implemented yet**: `score_with_openai()` in
`app/scoring.py` is a stub that still uses the mock. When it's built, it will run when
`OPENAI_API_KEY` is set in the environment, using the model from `OPENAI_MODEL` (default
`gpt-4o-mini`). See [`.env.example`](.env.example). The app reads these from the
environment and doesn't load `.env` itself, so export them in your shell first.

## Project layout

```
app/
  main.py        endpoints only: thin handlers that delegate
  models.py      every Pydantic request/response/record schema
  data.py        the only module that reads or writes files in data/
  scoring.py     mock scorer, OpenAI scorer (stub), total + scorecard
  progress.py    pure logic for /progress (no I/O)
  config.py      paths, MODEL_ID, USE_MOCK
data/            questions.json, rubric.md, results.json
resources/       interview guides (served by the MCP server)
mcp/server.py    "interview-guides" MCP server
specs/, plans/   the spec, tasks and plan written before /progress was built
tests/           pytest suite, one file per feature area
```

## Development

```bash
pytest -q                 # tests never touch the network or the real results.json
ruff check . && mypy app  # lint and type-check
```

Tests use a temporary copy of the data directory and force the mock scorer.

## Built with Claude Code

This project was built with [Claude Code](https://claude.com/claude-code) and includes the
setup it uses:

- **`CLAUDE.md`**: the project's conventions and guardrails for the agent.
- **Hooks** (`.claude/settings.json`): one blocks reading `.env`, and one runs ruff and mypy
  after every edit.
- **MCP server** (`mcp/server.py`): offers `list_guides` and `get_guide` for the interview
  guides in `resources/`. It's set up in `.mcp.json` with relative paths, so start
  Claude Code from the project root.
- **Skill and command**: `interview-coach` runs a mock round in the terminal, and `/report`
  summarises your practice history.

The OpenAI key this app uses is separate from the Anthropic credential Claude Code uses.
