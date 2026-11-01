from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Note, Tag
from app.schemas import NoteCreate, NoteUpdate, NoteResponse
from app.utils.security import get_current_user
from app.services.tagger import extract_smart_tags, classify_category
from app.services.summarizer import generate_ai_summary
from app.services.search_engine import index_note_chunks

router = APIRouter(prefix="/api/notes", tags=["Notes Management"])


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_in: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SCRUM-13: Upload Images and Create Notes
    Create a new note with automatic word count, category detection, and RAG indexing.
    """
    word_count = len(note_in.content.split())
    category = note_in.category or classify_category(note_in.content, note_in.title)

    note = Note(
        user_id=current_user.id,
        title=note_in.title.strip(),
        content=note_in.content.strip(),
        category=category,
        word_count=word_count,
        is_pinned=note_in.is_pinned or False
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    # Auto summary if content has sufficient length
    if word_count > 40:
        summary_res = await generate_ai_summary(note.content, note.title)
        note.summary = summary_res["summary"]

    # Handle tags (provided + smart auto-tags)
    suggested_tags = extract_smart_tags(note.content, max_tags=3)
    user_tags = note_in.tags or []
    all_tags = list(dict.fromkeys(user_tags + suggested_tags))

    for tname in all_tags:
        clean_name = tname.strip()
        if not clean_name:
            continue
        tag = db.query(Tag).filter(Tag.user_id == current_user.id, Tag.name.ilike(clean_name)).first()
        if not tag:
            tag = Tag(user_id=current_user.id, name=clean_name)
            db.add(tag)
            db.flush()
        if tag not in note.tags:
            note.tags.append(tag)

    # Index chunks for search/RAG
    index_note_chunks(db, current_user.id, note.id, note.content)

    db.commit()
    db.refresh(note)
    return note


@router.get("", response_model=List[NoteResponse])
def list_notes(
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    is_archived: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List notes with optional category and tag filtering."""
    query = db.query(Note).filter(
        Note.user_id == current_user.id,
        Note.is_archived == is_archived
    )
    if category:
        query = query.filter(Note.category == category)
    if tag:
        query = query.filter(Note.tags.any(Tag.name.ilike(tag)))

    return query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).all()


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve a single note."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update note content, title, tags, or pinned status."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    if note_update.title is not None:
        note.title = note_update.title.strip()
    if note_update.content is not None:
        note.content = note_update.content.strip()
        note.word_count = len(note.content.split())
        index_note_chunks(db, current_user.id, note.id, note.content)
    if note_update.category is not None:
        note.category = note_update.category.strip()
    if note_update.is_pinned is not None:
        note.is_pinned = note_update.is_pinned
    if note_update.is_archived is not None:
        note.is_archived = note_update.is_archived

    if note_update.tags is not None:
        note.tags.clear()
        for tname in note_update.tags:
            clean_name = tname.strip()
            if clean_name:
                tag = db.query(Tag).filter(Tag.user_id == current_user.id, Tag.name.ilike(clean_name)).first()
                if not tag:
                    tag = Tag(user_id=current_user.id, name=clean_name)
                    db.add(tag)
                    db.flush()
                note.tags.append(tag)

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_200_OK)
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete note and remove associated vector chunks."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    db.delete(note)
    db.commit()
    return {"success": True, "message": f"Note '{note.title}' deleted successfully."}
