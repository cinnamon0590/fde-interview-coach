# Spec 001: `GET /progress`

## Why
Candidates need to see whether practice is paying off without reading
`results.json` by hand. `/progress` reduces the saved results to two numbers.

## Returns
`200` with `ProgressResponse`:
- `rounds_practised: int`: the number of saved results (each scored answer is one).
- `average_total: float | null`: the mean `total` across those results, to 2 dp,
  or `null` if there are none.

## Reads
`data/results.json` only, read through `data.load_results()`. It is read-only.
The calculation happens in the pure function `progress.summarise_progress()`.

## Acceptance criteria
1. **Empty:** a missing, blank or `[]` file returns
   `{"rounds_practised": 0, "average_total": null}`. Use `null`, not `0`.
2. Totals 10, 12 and 14 in any rounds return `{"rounds_practised": 3, "average_total": 12.0}`.
3. Every successful `POST /score` raises `rounds_practised` by 1. A score
   rejected with 404 changes nothing.
4. Tests use the `tmp_data` fixture. They never touch the real `results.json`
   or the network.

## Out of scope
Per-category averages, per-round breakdowns, trends, normalising by `max`,
handling a malformed `results.json`, auth, and a database.
