"""Tests for the scoring helpers in app/scoring.py (pure logic, no network)."""
from __future__ import annotations

import pytest

from app.models import CategoryScore
from app.scoring import RUBRIC_CATEGORIES, compute_total, format_scorecard


def test_compute_total_sums_all_categories() -> None:
    categories = [CategoryScore(name=name, score=3, feedback="") for name in RUBRIC_CATEGORIES]
    assert len(categories) == 4
    assert compute_total(categories) == 12


# --- format_scorecard: pin the summary bands at every boundary ---


@pytest.mark.parametrize(
    ("total", "summary"),
    [
        (-1, "Needs significant work"),
        (0, "Needs significant work"),
        (4, "Needs significant work"),
        (5, "Needs work"),
        (9, "Needs work"),
        (10, "Solid, with gaps"),
        (15, "Solid, with gaps"),
        (16, "Strong answer"),
        (19, "Strong answer"),
        (20, "Strong answer - full marks"),
        (21, "Strong answer"),  # above 20 is not "full marks": the check is exact
    ],
)
def test_format_scorecard_summary_bands(total: int, summary: str) -> None:
    categories = [CategoryScore(name="Only", score=total, feedback="")]
    assert format_scorecard(categories).summary == summary


def test_format_scorecard_totals_and_max() -> None:
    categories = [CategoryScore(name=name, score=3, feedback="") for name in RUBRIC_CATEGORIES]
    scorecard = format_scorecard(categories)
    assert scorecard.total == 12
    assert scorecard.max == 20
    assert scorecard.categories == categories
