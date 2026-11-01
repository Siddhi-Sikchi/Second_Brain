import math
import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Document, Note, Chunk
from app.schemas import SearchResultItem, RagAskResponse, Citation
from app.config import settings
import httpx


# Stop words for local tokenizer
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "did", "do",
    "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had",
    "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself",
    "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its", "itself", "let's",
    "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "she", "should", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "were", "weren't", "what", "when", "where", "which", "while", "who", "whom", "why",
    "with", "would", "you", "your", "yours", "yourself", "yourselves"
}


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alpha words, filtering stop words."""
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
    return [w for w in words if w not in STOP_WORDS]


def compute_tf_vector(text: str) -> Dict[str, float]:
    """Compute term frequency vector with L2 normalization."""
    tokens = tokenize(text)
    if not tokens:
        return {}

    counts = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1

    # L2 normalize
    norm = math.sqrt(sum(v * v for v in counts.values()))
    if norm == 0:
        return {}
    return {k: v / norm for k, v in counts.items()}


def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """Compute cosine similarity between two sparse term vectors."""
    if not vec1 or not vec2:
        return 0.0

    common_keys = set(vec1.keys()) & set(vec2.keys())
    return sum(vec1[k] * vec2[k] for k in common_keys)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks of approx chunk_size characters,
    preserving word boundaries.
    """
    if not text.strip():
        return []

    words = text.split()
    chunks = []
    current_words = []
    current_len = 0

    for word in words:
        current_words.append(word)
        current_len += len(word) + 1

        if current_len >= chunk_size:
            chunk_str = " ".join(current_words)
            chunks.append(chunk_str)

            # Overlap: keep last few words
            overlap_words = []
            overlap_len = 0
            for w in reversed(current_words):
                overlap_words.insert(0, w)
                overlap_len += len(w) + 1
                if overlap_len >= overlap:
                    break
            current_words = overlap_words
            current_len = overlap_len

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def index_document_chunks(db: Session, user_id: int, document_id: int, text: str):
    """Chunk and store document in database."""
    # Delete existing chunks for this document
    db.query(Chunk).filter(Chunk.user_id == user_id, Chunk.document_id == document_id).delete()

    chunks = chunk_text(text)
    for idx, content in enumerate(chunks):
        tf_vec = compute_tf_vector(content)
        chunk = Chunk(
            user_id=user_id,
            document_id=document_id,
            chunk_index=idx,
            content=content,
            token_count=len(content.split()),
            embedding=tf_vec
        )
        db.add(chunk)
    db.commit()


def index_note_chunks(db: Session, user_id: int, note_id: int, text: str):
    """Chunk and store note in database."""
    # Delete existing chunks for this note
    db.query(Chunk).filter(Chunk.user_id == user_id, Chunk.note_id == note_id).delete()

    chunks = chunk_text(text)
    for idx, content in enumerate(chunks):
        tf_vec = compute_tf_vector(content)
        chunk = Chunk(
            user_id=user_id,
            note_id=note_id,
            chunk_index=idx,
            content=content,
            token_count=len(content.split()),
            embedding=tf_vec
        )
        db.add(chunk)
    db.commit()


def search_knowledge_base(
    db: Session,
    user_id: int,
    query_str: str,
    file_type: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 15
) -> List[SearchResultItem]:
    """
    Hybrid search combining keyword matching and vector cosine similarity.
    """
    query_vec = compute_tf_vector(query_str)
    query_terms = tokenize(query_str)

    results = []

    # 1. Search Documents
    doc_query = db.query(Document).filter(
        Document.user_id == user_id,
        Document.processing_status == "completed"
    )
    if file_type:
        doc_query = doc_query.filter(Document.file_type == file_type)
    if category:
        doc_query = doc_query.filter(Document.category == category)

    docs = doc_query.all()
    for doc in docs:
        content = doc.extracted_text or doc.title
        doc_vec = compute_tf_vector(content)
        vec_score = cosine_similarity(query_vec, doc_vec)

        # Keyword match boost
        kw_score = 0.0
        content_lower = content.lower()
        title_lower = doc.title.lower()
        for term in query_terms:
            if term in title_lower:
                kw_score += 0.5
            if term in content_lower:
                kw_score += 0.1

        total_score = (vec_score * 0.7) + min(kw_score, 0.3)

        if total_score > 0.05 or any(term in content_lower for term in query_terms):
            # Extract relevant snippet
            snippet = extract_best_snippet(content, query_terms)
            tags_list = [t.name for t in doc.tags]
            if tag and tag not in tags_list:
                continue

            results.append(SearchResultItem(
                id=doc.id,
                title=doc.title,
                type="document",
                snippet=snippet,
                relevance_score=round(total_score, 3),
                category=doc.category or "General",
                created_at=doc.created_at,
                tags=tags_list
            ))

    # 2. Search Notes
    note_query = db.query(Note).filter(
        Note.user_id == user_id,
        Note.is_archived == False
    )
    if category:
        note_query = note_query.filter(Note.category == category)

    notes = note_query.all()
    for note in notes:
        content = note.content
        note_vec = compute_tf_vector(content)
        vec_score = cosine_similarity(query_vec, note_vec)

        kw_score = 0.0
        content_lower = content.lower()
        title_lower = note.title.lower()
        for term in query_terms:
            if term in title_lower:
                kw_score += 0.5
            if term in content_lower:
                kw_score += 0.1

        total_score = (vec_score * 0.7) + min(kw_score, 0.3)

        if total_score > 0.05 or any(term in content_lower for term in query_terms):
            snippet = extract_best_snippet(content, query_terms)
            tags_list = [t.name for t in note.tags]
            if tag and tag not in tags_list:
                continue

            results.append(SearchResultItem(
                id=note.id,
                title=note.title,
                type="note",
                snippet=snippet,
                relevance_score=round(total_score, 3),
                category=note.category or "General",
                created_at=note.created_at,
                tags=tags_list
            ))

    # Sort by relevance score descending
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    return results[:limit]


def extract_best_snippet(text: str, query_terms: List[str], max_len: int = 240) -> str:
    """Find the sentence or window with the highest match density."""
    if not text:
        return ""

    sentences = re.split(r'(?<=[.!?])\s+', text)
    best_sentence = ""
    best_matches = -1

    for s in sentences:
        s_lower = s.lower()
        matches = sum(1 for term in query_terms if term in s_lower)
        if matches > best_matches:
            best_matches = matches
            best_sentence = s

    if best_sentence:
        clean = best_sentence.strip()
        if len(clean) > max_len:
            return clean[:max_len] + "..."
        return clean

    return text[:max_len].strip() + "..."


async def ask_rag_question(
    db: Session,
    user_id: int,
    question: str,
    doc_filter_ids: Optional[List[int]] = None,
    note_filter_ids: Optional[List[int]] = None
) -> RagAskResponse:
    """
    RAG Engine:
    1. Search chunks for top-k relevant excerpts.
    2. Ground the answer strictly on retrieved excerpts.
    3. Return citations with relevance scores.
    """
    q_vec = compute_tf_vector(question)
    q_terms = tokenize(question)

    # Query all user chunks
    chunk_query = db.query(Chunk).filter(Chunk.user_id == user_id)
    if doc_filter_ids:
        chunk_query = chunk_query.filter(Chunk.document_id.in_(doc_filter_ids))
    if note_filter_ids:
        chunk_query = chunk_query.filter(Chunk.note_id.in_(note_filter_ids))

    all_chunks = chunk_query.all()

    # Score chunks
    scored_chunks = []
    for ch in all_chunks:
        emb = ch.embedding or {}
        sim = cosine_similarity(q_vec, emb)
        # Term overlap boost
        ch_lower = ch.content.lower()
        kw_boost = sum(0.15 for t in q_terms if t in ch_lower)
        total = sim + min(kw_boost, 0.4)

        if total > 0.05:
            scored_chunks.append((total, ch))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_k = scored_chunks[:4]

    if not top_k or top_k[0][0] < 0.12:
        return RagAskResponse(
            question=question,
            answer="Based on your uploaded documents and notes, there is not enough information to answer this question. Please upload relevant study materials or notes to expand your knowledge base.",
            is_grounded=False,
            citations=[],
            confidence_score=0.0
        )

    # Build citations
    citations = []
    context_blocks = []
    for rank, (score, ch) in enumerate(top_k):
        title = "Unknown Source"
        stype = "document"
        sid = 0

        if ch.document_id and ch.document:
            title = ch.document.title
            stype = "document"
            sid = ch.document.id
        elif ch.note_id and ch.note:
            title = ch.note.title
            stype = "note"
            sid = ch.note.id

        citations.append(Citation(
            source_title=title,
            source_type=stype,
            source_id=sid,
            page=ch.chunk_index + 1,
            excerpt=ch.content[:220].strip() + "...",
            relevance=round(score, 3)
        ))
        context_blocks.append(f"[{stype.upper()}: {title}]\n{ch.content}")

    context_str = "\n\n".join(context_blocks)

    # AI Synthesis with Gemini if available, else local synthesis
    if settings.GEMINI_API_KEY:
        try:
            rag_prompt = (
                f"You are Second Brain's academic QA assistant. Answer the user's question using ONLY the provided context.\n"
                f"If the context does not contain the answer, say 'I cannot find the answer in your uploaded notes.'\n"
                f"Cite your sources using [Document/Note Title].\n\n"
                f"CONTEXT:\n{context_str}\n\n"
                f"QUESTION: {question}\n\n"
                f"ANSWER:"
            )

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": rag_prompt}]}]
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    answer_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    return RagAskResponse(
                        question=question,
                        answer=answer_text,
                        is_grounded=True,
                        citations=citations,
                        confidence_score=round(top_k[0][0], 3)
                    )
        except Exception:
            pass

    # Local fallback synthesizer
    # Extract top informative sentences from top chunks
    key_sentences = []
    for _, ch in top_k:
        sents = re.split(r'(?<=[.!?])\s+', ch.content)
        for s in sents:
            s_lower = s.lower()
            if any(t in s_lower for t in q_terms) and len(s.strip()) > 20:
                key_sentences.append(s.strip())
                if len(key_sentences) >= 3:
                    break
        if len(key_sentences) >= 3:
            break

    if not key_sentences:
        key_sentences = [top_k[0][1].content[:250].strip() + "..."]

    synthesized_answer = (
        f"According to your knowledge base:\n\n"
        + " ".join(key_sentences)
        + f"\n\n(Information retrieved from {citations[0].source_title} and related materials)."
    )

    return RagAskResponse(
        question=question,
        answer=synthesized_answer,
        is_grounded=True,
        citations=citations,
        confidence_score=round(min(top_k[0][0], 0.95), 3)
    )
