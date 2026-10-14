---
description: Summarise practice history from data/results.json — rounds practised, average /20, weakest category, next focus
allowed-tools: Read
---

Read `data/results.json` (read-only — never modify it) and `data/rubric.md`,
then give a short practice report.

## If there are no results
If the file is missing, empty, or `[]`, reply only:
"No results yet — score an answer with `POST /score` first, then run `/report` again."
Stop there.

## Otherwise report these four things

1. **Rounds practised** — the number of saved results (each is one scored
   answer), with a per-round breakdown, e.g. "5 (decomposition 3, behavioral 2)".
2. **Average total** — the mean of each record's `total`, to one decimal place,
   shown as "x / 20". Use each record's `max` if it isn't 20 and say so.
3. **Weakest rubric category** — if records include per-category scores (a
   `categories` list of `{name, score}`), average each category across records
   and name the lowest with its average out of 5. The current `ResultRecord`
   only saves `round`, `question_id`, `total` and `max`. If that's all there is,
   say plainly that per-category scores aren't saved yet, so the weakest
   category can't be worked out. Then name the **lowest-scoring round type**
   instead, labelled as a stand-in. Never guess a category.
4. **One thing to focus on next** — one concrete, actionable suggestion tied to
   the weakest category (or the stand-in round), drawing on what `rubric.md`
   says that category rewards. Example: "Next decomposition answer, name your
   riskiest assumption and how you'd test it in week 1."

Keep it under ~10 lines. Base every number on the file, and show your counts so
they can be checked.
