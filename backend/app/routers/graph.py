from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import GraphDataResponse
from app.utils.security import get_current_user
from app.services.knowledge_graph import build_user_knowledge_graph

router = APIRouter(prefix="/api/graph", tags=["Knowledge Graph"])


@router.get("", response_model=GraphDataResponse)
def get_knowledge_graph(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SCRUM-26: Interactive Knowledge Graph Visualization
    Returns nodes and edges connecting documents, notes, tags, and conceptual topics.
    """
    return build_user_knowledge_graph(db, current_user.id)
