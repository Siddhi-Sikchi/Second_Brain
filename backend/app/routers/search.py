from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import SearchQuery, SearchResultItem, RagAskRequest, RagAskResponse
from app.utils.security import get_current_user
from app.services.search_engine import search_knowledge_base, ask_rag_question

router = APIRouter(prefix="/api/search", tags=["AI Search Engine & RAG"])


@router.post("", response_model=List[SearchResultItem])
def search_endpoint(
    search_req: SearchQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SCRUM-25: Hybrid Keyword and Semantic RAG Search Engine
    Search notes and documents with TF-IDF vectors and keyword match density.
    """
    return search_knowledge_base(
        db=db,
        user_id=current_user.id,
        query_str=search_req.query,
        file_type=search_req.file_type,
        category=search_req.category,
        tag=search_req.tag,
        limit=search_req.limit or 15
    )


@router.post("/rag", response_model=RagAskResponse)
async def ask_rag_endpoint(
    rag_req: RagAskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SCRUM-25: Hybrid Keyword and Semantic RAG Search Engine
    Ask questions with RAG grounding, citations, and confidence scoring.
    """
    return await ask_rag_question(
        db=db,
        user_id=current_user.id,
        question=rag_req.question,
        doc_filter_ids=rag_req.document_ids,
        note_filter_ids=rag_req.note_ids
    )
