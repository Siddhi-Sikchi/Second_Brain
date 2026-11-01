from datetime import datetime, timedelta
from typing import Tuple


def sm2_scheduler(
    repetition_level: int,
    interval_days: int,
    ease_factor: float,
    rating: str
) -> Tuple[int, int, float, datetime]:
    """
    Implements the SuperMemo-2 (SM-2) spaced repetition algorithm.
    Ratings:
      - 'again': reset interval to 1 day
      - 'hard': multiply interval by 1.2
      - 'good': normal SM-2 multiplier
      - 'easy': generous interval boost and increase ease factor
    Returns: (new_repetition_level, new_interval_days, new_ease_factor, next_review_date)
    """
    rating = rating.lower()

    if rating == "again":
        new_repetition = 0
        new_interval = 1
        new_ease = max(1.3, ease_factor - 0.2)
    elif rating == "hard":
        new_repetition = repetition_level + 1
        new_interval = max(1, int(interval_days * 1.2))
        new_ease = max(1.3, ease_factor - 0.15)
    elif rating == "good":
        new_repetition = repetition_level + 1
        if new_repetition == 1:
            new_interval = 1
        elif new_repetition == 2:
            new_interval = 6
        else:
            new_interval = max(1, int(interval_days * ease_factor))
        new_ease = ease_factor
    elif rating == "easy":
        new_repetition = repetition_level + 1
        if new_repetition == 1:
            new_interval = 3
        elif new_repetition == 2:
            new_interval = 8
        else:
            new_interval = max(1, int(interval_days * ease_factor * 1.3))
        new_ease = ease_factor + 0.15
    else:
        new_repetition = repetition_level
        new_interval = interval_days
        new_ease = ease_factor

    next_review = datetime.utcnow() + timedelta(days=new_interval)
    return new_repetition, new_interval, round(new_ease, 2), next_review
