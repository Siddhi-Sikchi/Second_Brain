import re
from typing import List, Tuple, Dict, Any
import httpx
from app.config import settings


def split_sentences(text: str) -> List[str]:
    """Split text into sentences using regex boundary detection."""
    clean_text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)
    return [s.strip() for s in sentences if len(s.strip()) > 15]


def extractive_summary(text: str, max_sentences: int = 4) -> Tuple[str, List[str]]:
    """
    Intelligent deterministic extractive summarizer based on word frequency scoring.
    Does not require external APIs or internet access.
    Returns: (summary_paragraph, list_of_key_takeaways)
    """
    sentences = split_sentences(text)
    if not sentences:
        fallback = text[:300].strip()
        return fallback, [fallback] if fallback else []

    if len(sentences) <= max_sentences:
        return " ".join(sentences), sentences

    # Calculate word frequencies (ignoring common stop words)
    stop_words = {
        "the", "and", "is", "in", "to", "of", "a", "that", "it", "with", "as", "for",
        "was", "on", "are", "by", "this", "be", "or", "from", "at", "an", "your", "all",
        "which", "we", "can", "has", "have", "not", "but", "their", "will", "more"
    }

    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    freq = {}
    for w in words:
        if w not in stop_words:
            freq[w] = freq.get(w, 0) + 1

    # Score sentences based on word frequencies and position boost
    scored_sentences = []
    for idx, sentence in enumerate(sentences):
        score = 0.0
        words_in_sent = re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower())
        for w in words_in_sent:
            score += freq.get(w, 0)

        # Length normalization
        if len(words_in_sent) > 0:
            score = score / len(words_in_sent)

        # Position weight: first sentence and introductory sentences carry higher weight
        if idx == 0:
            score *= 1.4
        elif idx == 1:
            score *= 1.2

        scored_sentences.append((idx, score, sentence))

    # Pick top sentences while preserving chronological order
    top_ranked = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:max_sentences]
    ordered_top = sorted(top_ranked, key=lambda x: x[0])

    summary_paragraph = " ".join([item[2] for item in ordered_top])
    takeaways = [item[2] for item in ordered_top[:3]]

    return summary_paragraph, takeaways


async def generate_ai_summary(text: str, title: str = "") -> Dict[str, Any]:
    """
    Generates summary and key takeaways.
    Uses Google Gemini API if GEMINI_API_KEY is configured, else falls back to extractive summarizer.
    """
    if not text.strip():
        return {
            "summary": "No content available to summarize.",
            "key_takeaways": [],
            "engine": "none"
        }

    # If Gemini API key is configured, attempt call
    if settings.GEMINI_API_KEY:
        try:
            prompt = (
                f"You are an expert academic knowledge assistant. "
                f"Summarize the following document titled '{title}'.\n\n"
                f"Provide:\n"
                f"1. A concise, clear 2-3 sentence executive summary.\n"
                f"2. Three to five key bullet points.\n\n"
                f"Format your response as:\n"
                f"SUMMARY: <summary text>\n"
                f"TAKEAWAYS:\n"
                f"- <point 1>\n"
                f"- <point 2>\n"
                f"- <point 3>\n\n"
                f"Document text:\n{text[:12000]}"
            )

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidate = data["candidates"][0]["content"]["parts"][0]["text"]

                    # Parse output
                    summary_part = ""
                    takeaways = []
                    if "TAKEAWAYS:" in candidate:
                        parts = candidate.split("TAKEAWAYS:")
                        summary_part = parts[0].replace("SUMMARY:", "").strip()
                        raw_points = parts[1].strip().split("\n")
                        takeaways = [p.lstrip("-* ").strip() for p in raw_points if p.strip()]
                    else:
                        summary_part = candidate.strip()
                        takeaways = [s.strip() for s in split_sentences(candidate)[:3]]

                    return {
                        "summary": summary_part,
                        "key_takeaways": takeaways,
                        "engine": "gemini"
                    }
        except Exception:
            # Fall back to local extractive engine on any network/API error
            pass

    # Local deterministic fallback
    summary_text, takeaways = extractive_summary(text, max_sentences=4)
    return {
        "summary": summary_text,
        "key_takeaways": takeaways,
        "engine": "local_extractive"
    }
