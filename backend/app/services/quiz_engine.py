import json
import random
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Document, Note, Quiz, QuizQuestion, QuizAttempt, RevisionItem
from app.schemas import QuestionEvaluation, QuizResultResponse
from app.config import settings
import httpx
from datetime import datetime, timedelta


def clean_sentence(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def heuristic_generate_questions(text: str, question_count: int = 5) -> List[Dict[str, Any]]:
    """
    Offline deterministic question generator grounded in document text.
    Extracts high-information factual sentences and creates MCQs with plausible distractors.
    """
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    candidate_sentences = [
        clean_sentence(s) for s in raw_sentences
        if 40 <= len(clean_sentence(s)) <= 250 and not s.startswith("---")
    ]

    if not candidate_sentences:
        candidate_sentences = [
            f"The primary concept discussed in this document is {text[:100].strip()}."
        ]

    # Collect key candidate terms from the text
    all_capitalized = list(set(re.findall(r'\b[A-Z][a-z]{3,}\b', text)))
    if len(all_capitalized) < 5:
        all_capitalized += ["Architecture", "System", "Optimization", "Database", "Algorithm", "Security"]

    random.seed(42)
    selected_sentences = random.sample(candidate_sentences, min(len(candidate_sentences), question_count))

    generated_questions = []
    for idx, sentence in enumerate(selected_sentences):
        words = re.findall(r'\b[a-zA-Z]{4,}\b', sentence)
        if not words:
            continue

        # Choose an informative key word from the sentence as target
        # Prefer capitalized or longer words
        target_word = None
        for w in words:
            if w[0].isupper() and w.lower() not in {"this", "that", "these", "those"}:
                target_word = w
                break
        if not target_word:
            target_word = max(words, key=len)

        # Create question by cloze deletion / inquiry
        blanked = sentence.replace(target_word, "______", 1)
        question_text = f"Fill in the blank: \"{blanked}\""

        # Distractors
        distractors = [w for w in all_capitalized if w.lower() != target_word.lower()]
        random.shuffle(distractors)
        options = [target_word] + distractors[:3]
        random.shuffle(options)

        generated_questions.append({
            "question_text": question_text,
            "question_type": "mcq",
            "options": options,
            "correct_answer": target_word,
            "explanation": f"According to the source text: \"{sentence}\"",
            "source_excerpt": sentence,
            "order_index": idx
        })

    return generated_questions[:question_count]


async def generate_quiz_questions(
    db: Session,
    user_id: int,
    source_type: str,
    source_id: Optional[int],
    question_count: int
) -> List[Dict[str, Any]]:
    """
    Generates quiz questions grounded strictly in user content.
    Uses Gemini API if configured, otherwise heuristic engine.
    """
    combined_text = ""

    if source_type == "document" and source_id:
        doc = db.query(Document).filter(Document.id == source_id, Document.user_id == user_id).first()
        if doc:
            combined_text = doc.extracted_text or doc.title
    elif source_type == "note" and source_id:
        note = db.query(Note).filter(Note.id == source_id, Note.user_id == user_id).first()
        if note:
            combined_text = note.content
    else:
        # All user documents and notes
        docs = db.query(Document).filter(Document.user_id == user_id, Document.processing_status == "completed").all()
        notes = db.query(Note).filter(Note.user_id == user_id, Note.is_archived == False).all()
        texts = [d.extracted_text for d in docs if d.extracted_text] + [n.content for n in notes]
        combined_text = "\n\n".join(texts)

    if not combined_text.strip():
        combined_text = "Knowledge management systems organize notes, documents, and concepts for effective retrieval and learning."

    # Gemini online generation if key present
    if settings.GEMINI_API_KEY:
        try:
            prompt = (
                f"You are an academic test maker. Generate exactly {question_count} multiple-choice questions "
                f"strictly grounded in the text below. "
                f"Output MUST be valid JSON array of objects with keys: "
                f"'question_text', 'question_type' ('mcq'), 'options' (array of 4 distinct choices), "
                f"'correct_answer', 'explanation', 'source_excerpt'.\n\n"
                f"SOURCE TEXT:\n{combined_text[:12000]}\n\n"
                f"JSON OUTPUT:"
            )

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }

            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_json)
                    if isinstance(parsed, list) and len(parsed) > 0:
                        for idx, q in enumerate(parsed):
                            q["order_index"] = idx
                        return parsed[:question_count]
        except Exception:
            pass

    # Deterministic local fallback
    return heuristic_generate_questions(combined_text, question_count=question_count)


def evaluate_quiz_submission(
    db: Session,
    quiz: Quiz,
    user_id: int,
    answers_map: Dict[int, str],
    time_taken_seconds: int
) -> QuizResultResponse:
    """
    Grades quiz answers, computes score, creates QuizAttempt,
    and enlists missed questions into the spaced repetition queue!
    """
    evaluations: List[QuestionEvaluation] = []
    correct_count = 0
    total_questions = len(quiz.questions)

    for q in quiz.questions:
        user_ans = answers_map.get(q.id, "").strip()
        correct_ans = q.correct_answer.strip()

        # Case-insensitive comparison
        is_corr = (user_ans.lower() == correct_ans.lower())
        if is_corr:
            correct_count += 1
        else:
            # Enlist failed question into Spaced Repetition queue for revision
            existing_rev = db.query(RevisionItem).filter(
                RevisionItem.user_id == user_id,
                RevisionItem.item_type == "quiz_question",
                RevisionItem.item_id == q.id
            ).first()

            if not existing_rev:
                rev_item = RevisionItem(
                    user_id=user_id,
                    item_type="quiz_question",
                    item_id=q.id,
                    title=f"Review: {q.question_text[:80]}",
                    content_preview=f"Correct answer: {correct_ans}\n{q.explanation or ''}",
                    interval_days=1,
                    ease_factor=2.5,
                    repetition_level=0,
                    next_review_date=datetime.utcnow() + timedelta(days=1)
                )
                db.add(rev_item)

        evaluations.append(QuestionEvaluation(
            question_id=q.id,
            question_text=q.question_text,
            user_answer=user_ans,
            correct_answer=correct_ans,
            is_correct=is_corr,
            explanation=q.explanation,
            source_excerpt=q.source_excerpt
        ))

    score_pct = (correct_count / total_questions * 100.0) if total_questions > 0 else 0.0

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=user_id,
        score=round(score_pct, 1),
        total_questions=total_questions,
        correct_count=correct_count,
        answers_data=[{"q": q.id, "ans": answers_map.get(q.id, "")} for q in quiz.questions],
        time_taken_seconds=time_taken_seconds,
        completed_at=datetime.utcnow()
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return QuizResultResponse(
        attempt_id=attempt.id,
        quiz_id=quiz.id,
        quiz_title=quiz.title,
        score=attempt.score,
        total_questions=total_questions,
        correct_count=correct_count,
        time_taken_seconds=time_taken_seconds,
        completed_at=attempt.completed_at,
        evaluations=evaluations
    )
