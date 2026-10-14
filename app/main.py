"""FastAPI app for the FDE Interview Prep Assistant.

Run it:
    uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/docs  -- the interactive API page is our "UI".
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException

from . import data, scoring
from .models import ProgressResponse, Question, ResultRecord, ScoreRequest, ScoreResponse
from .progress import summarise_progress

app = FastAPI(title="FDE Interview Prep Assistant")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}


@app.get("/rounds")
def get_rounds() -> list[str]:
    """List the available interview round types."""
    return data.load_rounds()


@app.get("/questions")
def get_questions(round: str) -> list[Question]:
    """Return the questions for one round, e.g. /questions?round=decomposition."""
    questions = data.load_questions(round=round)
    if not questions:
        raise HTTPException(status_code=404, detail=f"No questions for round '{round}'")
    return questions


@app.post("/score")
def post_score(request: ScoreRequest) -> ScoreResponse:
    """Score a candidate's answer against the rubric and save the result."""
    # Reject before scoring, so a made-up round or question never gets saved.
    round_question_ids = {q.id for q in data.load_questions(round=request.round)}
    if request.question_id not in round_question_ids:
        raise HTTPException(
            status_code=404,
            detail=f"No question '{request.question_id}' in round '{request.round}'",
        )
    scorecard = scoring.score_answer(request.answer)
    data.save_result(
        ResultRecord(
            round=request.round,
            question_id=request.question_id,
            total=scorecard.total,
            max=scorecard.max,
        )
    )
    return scorecard


@app.get("/progress")
def get_progress() -> ProgressResponse:
    """How many rounds have been practised, and the average total score."""
    return summarise_progress(data.load_results())
