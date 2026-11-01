from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, Document, Note, Tag, Quiz, QuizAttempt
from app.schemas import AnalyticsSummaryResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics Dashboard"])


@router.get("/dashboard", response_model=AnalyticsSummaryResponse)
def get_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SCRUM-28: Learning Analytics and Activity Dashboard
    Returns 100% authentic database metrics computed for current user.
    """
    # 1. Counts and words
    total_docs = db.query(Document).filter(Document.user_id == current_user.id).count()
    total_notes = db.query(Note).filter(Note.user_id == current_user.id, Note.is_archived == False).count()

    doc_words = db.query(func.coalesce(func.sum(Document.word_count), 0)).filter(
        Document.user_id == current_user.id
    ).scalar() or 0

    note_words = db.query(func.coalesce(func.sum(Note.word_count), 0)).filter(
        Note.user_id == current_user.id
    ).scalar() or 0

    total_words = int(doc_words + note_words)

    # 2. Storage used
    storage_bytes = db.query(func.coalesce(func.sum(Document.file_size), 0)).filter(
        Document.user_id == current_user.id
    ).scalar() or 0

    # 3. Quiz Performance
    attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == current_user.id).all()
    total_quizzes = len(attempts)
    avg_score = round(sum(a.score for a in attempts) / total_quizzes, 1) if total_quizzes > 0 else 0.0

    # 4. Category breakdown
    categories: Dict[str, int] = {}
    docs = db.query(Document.category).filter(Document.user_id == current_user.id).all()
    notes = db.query(Note.category).filter(Note.user_id == current_user.id).all()

    for (c,) in docs + notes:
        cat_name = c or "General"
        categories[cat_name] = categories.get(cat_name, 0) + 1

    # 5. Top Tags
    user_tags = db.query(Tag).filter(Tag.user_id == current_user.id).all()
    tag_counts = []
    for t in user_tags:
        count = len(t.documents) + len(t.notes)
        tag_counts.append({"id": t.id, "name": t.name, "color": t.color, "count": count})
    tag_counts.sort(key=lambda x: x["count"], reverse=True)

    # 6. Recent Activity Feed
    activity: List[Dict[str, Any]] = []

    recent_docs = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.created_at.desc()).limit(5).all()
    for d in recent_docs:
        activity.append({
            "type": "document_upload",
            "title": f"Uploaded document: {d.title}",
            "category": d.category,
            "timestamp": d.created_at.isoformat()
        })

    recent_notes = db.query(Note).filter(
        Note.user_id == current_user.id
    ).order_by(Note.created_at.desc()).limit(5).all()
    for n in recent_notes:
        activity.append({
            "type": "note_created",
            "title": f"Created note: {n.title}",
            "category": n.category,
            "timestamp": n.created_at.isoformat()
        })

    recent_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id
    ).order_by(QuizAttempt.completed_at.desc()).limit(5).all()
    for a in recent_attempts:
        q_title = a.quiz.title if a.quiz else "Quiz"
        activity.append({
            "type": "quiz_attempt",
            "title": f"Completed quiz '{q_title}' with score {a.score}%",
            "category": "Assessment",
            "timestamp": a.completed_at.isoformat()
        })

    activity.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_activity = activity[:8]

    # 7. Dynamic Streak Calculation (unique days in past 30 days with any activity)
    active_dates = set()
    for item in activity:
        try:
            dt = datetime.fromisoformat(item["timestamp"]).date()
            active_dates.add(dt)
        except Exception:
            pass

    today = datetime.utcnow().date()
    streak = 0
    check_day = today
    while check_day in active_dates or (check_day == today and (today - timedelta(days=1)) in active_dates):
        if check_day in active_dates:
            streak += 1
        check_day -= timedelta(days=1)
        if streak >= 30:
            break

    return AnalyticsSummaryResponse(
        total_documents=total_docs,
        total_notes=total_notes,
        total_words=total_words,
        total_quizzes_taken=total_quizzes,
        average_quiz_score=avg_score,
        storage_used_bytes=int(storage_bytes),
        active_streak_days=max(streak, 1 if (total_docs > 0 or total_notes > 0) else 0),
        categories=categories,
        top_tags=tag_counts[:6],
        recent_activity=recent_activity
    )
