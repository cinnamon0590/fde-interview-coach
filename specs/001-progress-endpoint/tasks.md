# Tasks 001: `GET /progress`

These tasks implement [spec.md](spec.md). Each one is a single small change
with its own test and can be reviewed on its own. Do them in order, because
each builds on the one before. All tests are in `tests/test_progress.py`.

## T1: Response schema
- **Change:** add `ProgressResponse` to `app/models.py` with
  `rounds_practised: int` and `average_total: float | None`.
- **Test:** none on its own. T2 and T3 exercise it.
- **Done when:** `mypy app` passes.

## T2: Summary of no results (pure)
- **Change:** in `app/progress.py`, write `summarise_progress([])`, returning
  `rounds_practised=0` and `average_total=None`.
- **Test:** `test_summary_of_no_results`
- **Done when:** the test passes with no disk access. (Spec AC1)

## T3: Count and average (pure)
- **Change:** `rounds_practised = len(results)`, and the mean of `total`
  rounded to 2 dp.
- **Tests:** `test_summary_counts_every_result_and_averages_totals` (10, 12 and
  14 give 3 and 12.0), and `test_summary_same_round_repeated_counts_each_time`
  (5 and 6 give 2 and 5.5).
- **Done when:** both tests pass. (Spec AC2)

## T4: Tolerant results loader
- **Change:** in `app/data.py`, make `load_results()` return `[]` when the file
  is missing or blank, not raise.
- **Tests:** `test_progress_with_missing_results_file` and
  `test_progress_with_blank_results_file`
- **Done when:** both tests pass using the `tmp_data` fixture. (Spec AC1, AC4)

## T5: Endpoint
- **Change:** add `GET /progress` to `app/main.py` as a thin handler:
  `summarise_progress(data.load_results())`.
- **Test:** `test_progress_with_empty_results`, which expects `200` and
  `{"rounds_practised": 0, "average_total": null}`.
- **Done when:** the test passes. (Spec AC1)

## T6: `/score` feeds `/progress`
- **Change:** none expected if `/score` already saves results. This task checks
  the two endpoints work together.
- **Tests:** `test_score_saves_result_and_progress_reflects_it` and
  `test_score_creates_missing_results_file`
- **Done when:** each successful score raises `rounds_practised` by 1.
  (Spec AC3)

## T7: Rejected scores don't count
- **Change:** `/score` validates the round and question *before* it saves.
- **Test:** `test_score_rejects_unknown_round_or_question`, which expects a
  404, an unchanged file and `rounds_practised == 0`.
- **Done when:** the test passes. (Spec AC3)

## Every task
`pytest -q`, `ruff check .` and `mypy app` all pass. No test touches the real
`data/results.json` or the network. (Spec AC4)
