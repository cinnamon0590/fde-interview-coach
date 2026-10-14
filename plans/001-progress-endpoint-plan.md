# Plan: GET /progress (Module 2, built fresh)

## Context
`my-coach/` already contains a finished `/progress` (from a later state), so the
Module 2 exercise isn't real. User chose: reset to the Module 1 checkpoint (keeping
the new CLAUDE.md), then build `/progress` from scratch. "Rounds practised" =
**distinct round types** (5 decomposition attempts count as 1).

In the Module 1 checkpoint, `POST /score` is a stub that saves nothing, and
`data.save_result(record: dict)` exists but is unused. Wiring `/score` is Module 3
(and CLAUDE.md says not to touch the scoring exercises unprompted), so `/progress`
only *reads* `data/results.json`; tests supply results files directly.

## Step 0 — Reset (keep CLAUDE.md, .venv)
- Copy `checkpoints/01-understand-claudemd/code/` over `my-coach/`, **excluding
  `CLAUDE.md`** (no `--delete`, so `.venv/` survives), e.g.
  `rsync -a --exclude CLAUDE.md checkpoints/01-understand-claudemd/code/ my-coach/`
- Remove the later-state files the copy won't delete:
  `my-coach/app/progress.py`, `my-coach/tests/test_progress.py`.
- Run `pytest -q` → expect the 3 basic tests passing.

## 1. Files and changes
| File | Change |
|---|---|
| `app/models.py` | Add `ResultRecord` (`round`, `question_id`, `total`, `max`) and `ProgressResponse` (`rounds_practised: int`, `average_total: float \| None`). |
| `app/data.py` | Add `load_results() -> list[ResultRecord]`: missing file → `[]`, else parse each entry. Leave `save_result` as-is (Module 3). |
| `app/progress.py` (new) | Pure `summarise_progress(results) -> ProgressResponse`: distinct `round` count; mean of `total` rounded to 2 dp; empty → `(0, None)`. No I/O. |
| `app/main.py` | `GET /progress` → `summarise_progress(data.load_results())`. |
| `tests/test_progress.py` (new) | Unit tests for `summarise_progress`; endpoint tests via a `tmp_data` fixture that monkeypatches `app.data.DATA_DIR` and writes its own `results.json`. |

## 2. Order
1. Models → 2. `summarise_progress` + unit tests (pure, easiest to pin down) →
3. `load_results` → 4. **empty-results guard** (below) → 5. endpoint →
6. endpoint test(s) → `pytest -q`, `ruff check .`, `mypy app`.

### Empty-results guard (never divide by zero)
- In `summarise_progress`: `if not results: return ProgressResponse(rounds_practised=0, average_total=None)`
  **before** any `sum(...) / len(...)`, with a comment on why `None`, not `0`.
- In `load_results`, all three "nothing scored" shapes reach that guard as `[]`:
  missing file, `[]`, and a zero-byte/whitespace-only file (`json.loads("")` would
  otherwise raise → 500).

### Test note
- Write at least **one endpoint test** for `GET /progress`: with `tmp_data`
  pointing at a `results.json` containing `[]`, assert `200` and
  `{"rounds_practised": 0, "average_total": null}`. This pins the divide-by-zero
  guard end to end. (Unit tests and the populated/missing-file cases are extras.)

## 3. What could break / easy to get wrong
- Tests touching real `data/results.json`: must patch `app.data.DATA_DIR`
  (patching `app.config.DATA_DIR` does nothing — `data.py` imported the name).
- Empty list → ZeroDivisionError; missing file → FileNotFoundError.
- Returning `0` instead of `None` for "nothing scored yet".
- Malformed/legacy entries in `results.json` → Pydantic `ValidationError` → 500.
- `/progress` will always show `(0, null)` in the live app until Module 3 wires
  `/score` to save — expected, not a bug.
- Once `/score` saves, totals come from the buggy `compute_total()` (drops first
  category), so averages are understated and pre-/post-fix records won't mix cleanly.

## 4. Riskiest assumption
That the `results.json` record shape this endpoint reads (`round`, `total`, …) is
the shape `/score` will actually write in Module 3. Nothing writes the file yet, so
`/progress` is built against a contract with no producer; `ResultRecord` should be
the single shared definition both sides use.

## Verification
- `pytest -q`: basic tests + new unit tests (empty, distinct-round counting,
  repeated round counts once, averaging) + endpoint tests (empty file, missing file,
  populated file).
- `uvicorn app.main:app --reload`, open `/docs`, call `GET /progress` → `{"rounds_practised": 0, "average_total": null}`.
- `ruff check . && mypy app` clean.
