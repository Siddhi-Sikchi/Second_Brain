from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, RevisionItem
from app.schemas import RevisionItemResponse, RevisionReviewRequest
from app.utils.security import get_current_user
from app.services.spaced_repetition import sm2_scheduler

router = APIRouter(prefix="/api/revision", tags=["Spaced Repetition & Revision"])


@router.get("/due", response_model=List[RevisionItemResponse])
def get_due_revisions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SCRUM-29: Spaced Repetition and Revision Scheduling System
    Get all revision items scheduled for review on or before today.
    """
    now = datetime.utcnow()
    return db.query(RevisionItem).filter(
        RevisionItem.user_id == current_user.id,
        RevisionItem.next_review_date <= now
    ).order_by(RevisionItem.next_review_date.asc()).all()


@router.get("/all", response_model=List[RevisionItemResponse])
def get_all_revisions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all scheduled items in the user's revision queue."""
    return db.query(RevisionItem).filter(
        RevisionItem.user_id == current_user.id
    ).order_by(RevisionItem.next_review_date.asc()).all()


@router.post("/{item_id}/review", response_model=RevisionItemResponse)
def submit_revision_review(
    item_id: int,
    req: RevisionReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record review feedback and update SM-2 schedule.
    """
    item = db.query(RevisionItem).filter(
        RevisionItem.id == item_id,
        RevisionItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Revision item not found.")

    new_rep, new_interval, new_ease, next_date = sm2_scheduler(
        repetition_level=item.repetition_level,
        interval_days=item.interval_days,
        ease_factor=item.ease_factor,
        rating=req.rating
    )

    item.repetition_level = new_rep
    item.interval_days = new_interval
    item.ease_factor = new_ease
    item.next_review_date = next_date
    item.last_reviewed_at = datetime.utcnow()
    item.review_count += 1

    db.commit()
    db.refresh(item)
    return item
