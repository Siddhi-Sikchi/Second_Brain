from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Quiz, QuizQuestion, QuizAttempt
from app.schemas import (
    QuizCreateRequest, QuizDetailResponse, QuizQuestionResponse,
    QuizSubmission, QuizResultResponse, QuizAttemptHistoryItem
)
from app.utils.security import get_current_user
from app.services.quiz_engine import generate_quiz_questions, evaluate_quiz_submission

router = APIRouter(prefix="/api/quizzes", tags=["AI Quiz Generator"])


@router.post("/generate", response_model=QuizDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    req: QuizCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SCRUM-27: AI Quiz Generator and Interactive Assessment Engine
    Generate quiz with MCQs and short-answers grounded strictly in user content.
    """
    questions_data = await generate_quiz_questions(
        db=db,
        user_id=current_user.id,
        source_type=req.source_type,
        source_id=req.source_id,
        question_count=req.question_count
    )

    if not questions_data:
        raise HTTPException(
            status_code=400,
            detail="Unable to generate quiz questions from selected sources. Please ensure source documents contain text."
        )

    quiz = Quiz(
        user_id=current_user.id,
        title=req.title,
        description=f"Generated from {req.source_type} source",
        source_type=req.source_type,
        source_id=req.source_id,
        question_count=len(questions_data)
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    for q_item in questions_data:
        question = QuizQuestion(
            quiz_id=quiz.id,
            question_text=q_item["question_text"],
            question_type=q_item.get("question_type", "mcq"),
            options=q_item.get("options", []),
            correct_answer=q_item["correct_answer"],
            explanation=q_item.get("explanation", ""),
            source_excerpt=q_item.get("source_excerpt", ""),
            order_index=q_item.get("order_index", 0)
        )
        db.add(question)

    db.commit()
    db.refresh(quiz)
    return quiz


@router.get("", response_model=List[QuizDetailResponse])
def list_quizzes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all quizzes created by user."""
    return db.query(Quiz).filter(Quiz.user_id == current_user.id).order_by(Quiz.created_at.desc()).all()


@router.get("/{quiz_id}", response_model=QuizDetailResponse)
def get_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a quiz and its questions."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return quiz


@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
def submit_quiz(
    quiz_id: int,
    submission: QuizSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit answers, grade attempt, and enlist mistakes into spaced repetition revision.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    answers_map: Dict[int, str] = {ans.question_id: ans.user_answer for ans in submission.answers}
    result = evaluate_quiz_submission(
        db=db,
        quiz=quiz,
        user_id=current_user.id,
        answers_map=answers_map,
        time_taken_seconds=submission.time_taken_seconds
    )
    return result


@router.get("/attempts/history", response_model=List[QuizAttemptHistoryItem])
def get_attempts_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical quiz attempts for user."""
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id
    ).order_by(QuizAttempt.completed_at.desc()).all()

    history = []
    for att in attempts:
        quiz_title = att.quiz.title if att.quiz else "Quiz"
        history.append(QuizAttemptHistoryItem(
            id=att.id,
            quiz_id=att.quiz_id,
            quiz_title=quiz_title,
            score=att.score,
            total_questions=att.total_questions,
            correct_count=att.correct_count,
            time_taken_seconds=att.time_taken_seconds,
            completed_at=att.completed_at
        ))
    return history
