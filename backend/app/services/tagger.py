import re
from typing import List, Tuple, Dict
from collections import Counter


# Domain taxonomies for smart categorization
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Artificial Intelligence": [
        "ai", "neural", "deep learning", "machine learning", "nlp", "llm", "transformer",
        "embeddings", "rag", "supervised", "reinforcement", "clustering", "model", "gpt"
    ],
    "Computer Science": [
        "algorithm", "data structure", "database", "sql", "api", "programming", "software",
        "python", "javascript", "react", "fastapi", "network", "system", "compiler", "git"
    ],
    "Mathematics & Statistics": [
        "matrix", "vector", "calculus", "probability", "statistics", "linear algebra",
        "theorem", "equation", "formula", "variance", "distribution", "integral"
    ],
    "Business & Finance": [
        "finance", "market", "revenue", "strategy", "investment", "accounting", "management",
        "growth", "business", "economics", "customer", "product", "sales", "roi"
    ],
    "Science & Engineering": [
        "physics", "chemistry", "biology", "genetics", "energy", "mechanics", "experiment",
        "material", "circuit", "thermodynamics", "protein", "dna", "cell"
    ],
    "Humanities & Social": [
        "history", "philosophy", "psychology", "sociology", "literature", "ethics",
        "policy", "law", "government", "culture", "art", "society"
    ]
}

COMMON_STOP_WORDS = {
    "about", "above", "after", "again", "against", "all", "and", "any", "are", "aren't",
    "because", "been", "before", "being", "below", "between", "both", "but", "can", "cannot",
    "could", "did", "does", "doing", "down", "during", "each", "few", "for", "from", "further",
    "had", "has", "have", "having", "her", "here", "hers", "herself", "him", "himself", "his",
    "how", "into", "its", "itself", "more", "most", "myself", "nor", "not", "off", "once",
    "only", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she",
    "should", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
    "then", "there", "these", "they", "this", "those", "through", "too", "under", "until",
    "very", "was", "wasn't", "were", "weren't", "what", "when", "where", "which", "while",
    "who", "whom", "why", "with", "would", "you", "your", "yours", "yourself", "yourselves",
    "page", "document", "text", "also", "using", "used", "will", "show", "first", "second"
}


def extract_smart_tags(text: str, max_tags: int = 5) -> List[str]:
    """
    Extracts relevant topical tags from document text using term frequency and domain rules.
    """
    if not text:
        return []

    # Find words with length >= 4
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    filtered = [w for w in words if w not in COMMON_STOP_WORDS]

    counts = Counter(filtered)
    top_words = [word.capitalize() for word, _ in counts.most_common(max_tags)]

    # Also detect key multi-word phrases if present
    text_lower = text.lower()
    for category, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if " " in kw and kw in text_lower:
                title_kw = kw.title()
                if title_kw not in top_words:
                    top_words.insert(0, title_kw)

    return top_words[:max_tags]


def classify_category(text: str, title: str = "") -> str:
    """
    Determines the best matching category based on keyword density.
    """
    combined = (title + " " + text[:5000]).lower()

    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in combined:
                score += combined.count(kw)
        scores[cat] = score

    best_cat, best_score = max(scores.items(), key=lambda x: x[1])
    if best_score > 2:
        return best_cat
    return "General"
