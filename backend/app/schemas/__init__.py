from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ===================== AUTH & USER SCHEMAS =====================

class UserRegister(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)


class UserLogin(BaseModel):
    email: str
    password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


# ===================== TAG SCHEMAS =====================

class TagBase(BaseModel):
    name: str
    color: Optional[str] = "#3b82f6"


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===================== NOTE SCHEMAS =====================

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str
    category: Optional[str] = "General"
    tags: Optional[List[str]] = []
    is_pinned: Optional[bool] = False


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: Optional[str] = None
    category: str
    word_count: int
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


# ===================== DOCUMENT SCHEMAS =====================

class DocumentResponse(BaseModel):
    id: int
    title: str
    original_filename: str
    file_type: str
    file_size: int
    processing_status: str
    error_message: Optional[str] = None
    page_count: int
    word_count: int
    summary: Optional[str] = None
    key_takeaways: Optional[List[str]] = None
    category: str
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    extracted_text: Optional[str] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None


# ===================== SEARCH & RAG SCHEMAS =====================

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1)
    file_type: Optional[str] = None
    category: Optional[str] = None
    tag: Optional[str] = None
    limit: Optional[int] = 10


class SearchResultItem(BaseModel):
    id: int
    title: str
    type: str  # document or note
    snippet: str
    relevance_score: float
    category: str
    created_at: datetime
    tags: List[str] = []


class Citation(BaseModel):
    source_title: str
    source_type: str  # document or note
    source_id: int
    page: Optional[int] = None
    excerpt: str
    relevance: float


class RagAskRequest(BaseModel):
    question: str = Field(..., min_length=2)
    document_ids: Optional[List[int]] = None
    note_ids: Optional[List[int]] = None


class RagAskResponse(BaseModel):
    question: str
    answer: str
    is_grounded: bool
    citations: List[Citation]
    confidence_score: float


# ===================== KNOWLEDGE GRAPH SCHEMAS =====================

class GraphNodeSchema(BaseModel):
    id: str  # e.g., "doc_1", "note_2", "tag_science"
    label: str
    group: str  # document, note, tag, category
    val: float
    source_id: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None


class GraphEdgeSchema(BaseModel):
    source: str
    target: str
    relation: str
    weight: float


class GraphDataResponse(BaseModel):
    nodes: List[GraphNodeSchema]
    links: List[GraphEdgeSchema]
    total_nodes: int
    total_edges: int


# ===================== QUIZ SCHEMAS =====================

class QuizCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    source_type: str = "all"  # all, document, note
    source_id: Optional[int] = None
    question_count: int = Field(default=5, ge=1, le=20)


class QuizQuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    order_index: int

    class Config:
        from_attributes = True


class QuizDetailResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    source_type: str
    source_id: Optional[int] = None
    question_count: int
    created_at: datetime
    questions: List[QuizQuestionResponse] = []

    class Config:
        from_attributes = True


class QuizSubmitAnswer(BaseModel):
    question_id: int
    user_answer: str


class QuizSubmission(BaseModel):
    answers: List[QuizSubmitAnswer]
    time_taken_seconds: int = 0


class QuestionEvaluation(BaseModel):
    question_id: int
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: Optional[str] = None
    source_excerpt: Optional[str] = None


class QuizResultResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    quiz_title: str
    score: float
    total_questions: int
    correct_count: int
    time_taken_seconds: int
    completed_at: datetime
    evaluations: List[QuestionEvaluation]


class QuizAttemptHistoryItem(BaseModel):
    id: int
    quiz_id: int
    quiz_title: str
    score: float
    total_questions: int
    correct_count: int
    time_taken_seconds: int
    completed_at: datetime

    class Config:
        from_attributes = True


# ===================== REVISION SCHEMAS =====================

class RevisionItemResponse(BaseModel):
    id: int
    item_type: str
    item_id: Optional[int] = None
    title: str
    content_preview: Optional[str] = None
    repetition_level: int
    interval_days: int
    ease_factor: float
    next_review_date: datetime
    last_reviewed_at: Optional[datetime] = None
    review_count: int

    class Config:
        from_attributes = True


class RevisionReviewRequest(BaseModel):
    rating: str = Field(..., pattern="^(again|hard|good|easy)$")


# ===================== ANALYTICS SCHEMAS =====================

class AnalyticsSummaryResponse(BaseModel):
    total_documents: int
    total_notes: int
    total_words: int
    total_quizzes_taken: int
    average_quiz_score: float
    storage_used_bytes: int
    active_streak_days: int
    categories: Dict[str, int]
    top_tags: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
