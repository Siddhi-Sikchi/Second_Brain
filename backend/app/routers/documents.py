import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Document, Tag
from app.schemas import DocumentResponse, DocumentDetailResponse, DocumentUpdate
from app.utils.security import get_current_user
from app.config import settings
from app.services.text_extractor import process_document_file, TextExtractionError
from app.services.summarizer import generate_ai_summary
from app.services.tagger import extract_smart_tags, classify_category
from app.services.search_engine import index_document_chunks

router = APIRouter(prefix="/api/documents", tags=["Document Processing"])

# Allowed MIME types and extensions
ALLOWED_EXTENSIONS = {
    ".pdf": "pdf",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".txt": "text",
    ".md": "text",
    ".json": "doc",
    ".csv": "doc",
    ".py": "doc"
}


@router.post("/upload", response_model=DocumentDetailResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SCRUM-12: Upload PDF and Documents
    SCRUM-13: Upload Images and Create Notes
    SCRUM-21: Document Text Extraction and OCR Engine
    SCRUM-23: AI-Powered Document Summarization
    SCRUM-24: Automated Smart Tagging and Taxonomy Engine
    """
    filename = file.filename or "untitled"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS.keys())}"
        )

    file_type = ALLOWED_EXTENSIONS[ext]

    # Generate unique stored filename
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    upload_dir = settings.upload_path
    file_dest = upload_dir / unique_name

    # Save to disk while verifying file size limit
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    total_bytes = 0

    try:
        with open(file_dest, "wb") as buffer:
            while chunk := await file.read(1024 * 64):
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    buffer.close()
                    if file_dest.exists():
                        file_dest.unlink()
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        if file_dest.exists():
            file_dest.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving uploaded file: {str(e)}"
        )

    doc_title = (title or Path(filename).stem).strip()

    # Create document record
    doc = Document(
        user_id=current_user.id,
        title=doc_title,
        original_filename=filename,
        stored_filename=unique_name,
        file_path=str(file_dest),
        file_type=file_type,
        file_size=total_bytes,
        mime_type=file.content_type or "application/octet-stream",
        processing_status="processing",
        category=category or "General"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Execute extraction and AI processing pipeline
    try:
        extracted_info = process_document_file(file_dest, file_type)
        doc.extracted_text = extracted_info["extracted_text"]
        doc.page_count = extracted_info["page_count"]
        doc.word_count = extracted_info["word_count"]
        doc.char_count = extracted_info["char_count"]

        # Smart Categorization
        if not category:
            doc.category = classify_category(doc.extracted_text or "", doc.title)

        # AI Summarization
        summary_res = await generate_ai_summary(doc.extracted_text or "", doc.title)
        doc.summary = summary_res["summary"]
        doc.key_takeaways = summary_res["key_takeaways"]

        # Smart Tagging
        extracted_tags = extract_smart_tags(doc.extracted_text or "", max_tags=4)
        if tags:
            user_tags = [t.strip() for t in tags.split(",") if t.strip()]
            all_tags_list = list(dict.fromkeys(user_tags + extracted_tags))
        else:
            all_tags_list = extracted_tags

        for tag_name in all_tags_list:
            clean_name = tag_name.strip()
            if not clean_name:
                continue
            existing_tag = db.query(Tag).filter(
                Tag.user_id == current_user.id,
                Tag.name.ilike(clean_name)
            ).first()
            if not existing_tag:
                existing_tag = Tag(user_id=current_user.id, name=clean_name)
                db.add(existing_tag)
                db.flush()
            if existing_tag not in doc.tags:
                doc.tags.append(existing_tag)

        # Vector chunk indexing for RAG search
        if doc.extracted_text:
            index_document_chunks(db, current_user.id, doc.id, doc.extracted_text)

        doc.processing_status = "completed"
    except Exception as e:
        doc.processing_status = "failed"
        doc.error_message = str(e)

    db.commit()
    db.refresh(doc)
    return doc


@router.get("", response_model=List[DocumentResponse])
def list_documents(
    category: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SCRUM-22: Document Metadata Management and Knowledge Library View
    List and filter all documents owned by user.
    """
    query = db.query(Document).filter(Document.user_id == current_user.id)

    if category:
        query = query.filter(Document.category == category)
    if file_type:
        query = query.filter(Document.file_type == file_type)
    if status:
        query = query.filter(Document.processing_status == status)
    if tag:
        query = query.filter(Document.tags.any(Tag.name.ilike(tag)))

    return query.order_by(Document.created_at.desc()).all()


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete document details including extracted text."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    update_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update title, category, summary, or tags."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if update_data.title is not None:
        doc.title = update_data.title.strip()
    if update_data.category is not None:
        doc.category = update_data.category.strip()
    if update_data.summary is not None:
        doc.summary = update_data.summary.strip()
    if update_data.tags is not None:
        doc.tags.clear()
        for tname in update_data.tags:
            tag_name = tname.strip()
            if tag_name:
                tag = db.query(Tag).filter(
                    Tag.user_id == current_user.id,
                    Tag.name.ilike(tag_name)
                ).first()
                if not tag:
                    tag = Tag(user_id=current_user.id, name=tag_name)
                    db.add(tag)
                    db.flush()
                doc.tags.append(tag)

    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete document, physical file, and associated chunk vectors."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Delete physical file
    try:
        p = Path(doc.file_path)
        if p.exists():
            p.unlink()
    except Exception:
        pass

    db.delete(doc)
    db.commit()
    return {"success": True, "message": f"Document '{doc.title}' deleted successfully."}


@router.post("/{document_id}/summarize", response_model=DocumentResponse)
async def regenerate_summary(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate AI summary for document."""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    summary_res = await generate_ai_summary(doc.extracted_text or "", doc.title)
    doc.summary = summary_res["summary"]
    doc.key_takeaways = summary_res["key_takeaways"]
    db.commit()
    db.refresh(doc)
    return doc
