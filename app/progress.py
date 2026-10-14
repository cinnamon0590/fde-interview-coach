"""Summarise saved results into a progress report.

Pure logic, no disk access (that lives in data.py), so it's easy to test.
"""
from __future__ import annotations

from .models import ProgressResponse, ResultRecord


def summarise_progress(results: list[ResultRecord]) -> ProgressResponse:
    """Count rounds practised (one per saved result) and average the total score."""
    if not results:
        # None, not 0: "no attempts yet" is different from "scored zero".
        return ProgressResponse(rounds_practised=0, average_total=None)
    # Each saved result is one practised round, matching how /report counts them.
    rounds_practised = len(results)
    average_total = round(sum(r.total for r in results) / len(results), 2)
    return ProgressResponse(rounds_practised=rounds_practised, average_total=average_total)
