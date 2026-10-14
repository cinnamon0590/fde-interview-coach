"""Pydantic schemas — the shape of every request and response.

Pydantic validates data at the edges of the app, so the rest of the code can
trust the values it is handed.
"""
from __future__ import annotations

from pydantic import BaseModel


class Question(BaseModel):
    """One interview question."""

    id: str
    round: str
    prompt: str


class ScoreRequest(BaseModel):
    """Body of POST /score."""

    round: str
    question_id: str
    answer: str


class CategoryScore(BaseModel):
    """The score for a single rubric category (0..5)."""

    name: str
    score: int
    max: int = 5
    feedback: str


class ScoreResponse(BaseModel):
    """The full scorecard returned by POST /score."""

    total: int
    max: int
    categories: list[CategoryScore]
    summary: str


class ResultRecord(BaseModel):
    """One saved result in data/results.json (written by /score, read by /progress)."""

    round: str
    question_id: str
    total: int
    max: int


class ProgressResponse(BaseModel):
    """Body of GET /progress."""

    rounds_practised: int  # one per saved result (each scored answer)
    average_total: float | None  # None when nothing has been scored yet
