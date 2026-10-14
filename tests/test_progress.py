"""Tests for GET /progress and for POST /score saving its result.

Every test points app.data.DATA_DIR at a temp folder, so the real
data/results.json is never read or written. Scoring is forced to the offline
mock, so no test touches the network.
"""
from __future__ import annotations

import json
import shutil

import pytest
from fastapi.testclient import TestClient

from app.config import DATA_DIR
from app.main import app
from app.models import ResultRecord
from app.progress import summarise_progress

client = TestClient(app)


@pytest.fixture
def tmp_data(tmp_path, monkeypatch):
    """A temp data dir with the real question bank and an empty results file."""
    shutil.copy(DATA_DIR / "questions.json", tmp_path / "questions.json")
    (tmp_path / "results.json").write_text("[]", encoding="utf-8")
    # Patch app.data's name, not app.config's: data.py imported DATA_DIR by name.
    monkeypatch.setattr("app.data.DATA_DIR", tmp_path)
    monkeypatch.setattr("app.scoring.USE_MOCK", True)
    return tmp_path


def record(round: str, total: int) -> ResultRecord:
    return ResultRecord(round=round, question_id="q", total=total, max=20)


# --- summarise_progress (pure, no disk) ---


def test_summary_of_no_results() -> None:
    progress = summarise_progress([])
    assert progress.rounds_practised == 0
    assert progress.average_total is None


def test_summary_counts_every_result_and_averages_totals() -> None:
    results = [record("decomposition", 10), record("behavioral", 12), record("decomposition", 14)]
    progress = summarise_progress(results)
    assert progress.rounds_practised == 3
    assert progress.average_total == 12.0


def test_summary_same_round_repeated_counts_each_time() -> None:
    progress = summarise_progress([record("behavioral", 5), record("behavioral", 6)])
    assert progress.rounds_practised == 2
    assert progress.average_total == 5.5


# --- endpoints ---


def test_progress_with_empty_results(tmp_data) -> None:
    resp = client.get("/progress")
    assert resp.status_code == 200
    assert resp.json() == {"rounds_practised": 0, "average_total": None}


def test_progress_with_missing_results_file(tmp_data) -> None:
    (tmp_data / "results.json").unlink()
    resp = client.get("/progress")
    assert resp.status_code == 200
    assert resp.json() == {"rounds_practised": 0, "average_total": None}


@pytest.mark.parametrize(
    ("round", "question_id"),
    [
        ("made-up-round", "dec-01"),  # round doesn't exist
        ("decomposition", "no-such-q"),  # question doesn't exist
        ("behavioral", "dec-01"),  # question exists, but in another round
    ],
)
def test_score_rejects_unknown_round_or_question(tmp_data, round, question_id) -> None:
    resp = client.post(
        "/score", json={"round": round, "question_id": question_id, "answer": "anything"}
    )
    assert resp.status_code == 404
    assert json.loads((tmp_data / "results.json").read_text(encoding="utf-8")) == []
    assert client.get("/progress").json()["rounds_practised"] == 0


def test_score_saves_result_and_progress_reflects_it(tmp_data) -> None:
    first = client.post(
        "/score", json={"round": "decomposition", "question_id": "dec-01", "answer": "short"}
    )
    second = client.post(
        "/score",
        json={"round": "behavioral", "question_id": "beh-01", "answer": "a\nlonger\nanswer " * 40},
    )
    assert first.status_code == 200
    assert second.status_code == 200

    saved = json.loads((tmp_data / "results.json").read_text(encoding="utf-8"))
    assert [r["round"] for r in saved] == ["decomposition", "behavioral"]
    assert saved[0]["total"] == first.json()["total"]

    progress = client.get("/progress").json()
    expected_average = (first.json()["total"] + second.json()["total"]) / 2
    assert progress["rounds_practised"] == 2
    assert progress["average_total"] == round(expected_average, 2)


def test_progress_with_blank_results_file(tmp_data) -> None:
    (tmp_data / "results.json").write_text("", encoding="utf-8")
    resp = client.get("/progress")
    assert resp.status_code == 200
    assert resp.json() == {"rounds_practised": 0, "average_total": None}


def test_score_creates_missing_results_file(tmp_data) -> None:
    (tmp_data / "results.json").unlink()
    resp = client.post(
        "/score", json={"round": "decomposition", "question_id": "dec-01", "answer": "short"}
    )
    assert resp.status_code == 200
    assert client.get("/progress").json()["rounds_practised"] == 1
