"""
Unified SM-2 Spaced Repetition Service.

Supports two rating scales:
  - 0-5 scale (standard SM-2): 0=blackout, 1=incorrect, 2=incorrect but easy to recall,
    3=correct with difficulty, 4=correct with hesitation, 5=perfect
  - 1-4 scale (flashcard-friendly): 1=Again, 2=Hard, 3=Good, 4=Easy

The 1-4 scale is mapped to equivalent 0-5 values internally so the core algorithm
is identical for both flashcards and topics.
"""
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field


@dataclass
class SM2Result:
    """Result of an SM-2 review calculation."""
    easiness_factor: float
    interval: int          # days until next review
    repetitions: int       # consecutive successful reviews
    next_review_date: datetime


def _map_rating(rating: int, scale: int) -> int:
    """Map rating to 0-5 scale for unified processing."""
    if scale == 5:
        return max(0, min(5, rating))
    elif scale == 4:
        # 1(Again)→0, 2(Hard)→2, 3(Good)→4, 4(Easy)→5
        mapping = {1: 0, 2: 2, 3: 4, 4: 5}
        return mapping.get(rating, 3)
    else:
        raise ValueError(f"Unsupported rating scale: {scale}. Use 4 or 5.")


def apply_sm2(
    quality: int,
    scale: int = 5,
    current_ef: float = 2.5,
    current_interval: int = 0,
    current_repetitions: int = 0,
) -> SM2Result:
    """
    Apply the SM-2 algorithm.

    Args:
        quality: User's quality rating (on the given scale)
        scale: Rating scale — 5 for 0-5, 4 for 1-4
        current_ef: Current easiness factor
        current_interval: Current interval in days
        current_repetitions: Current consecutive successful review count

    Returns:
        SM2Result with updated values
    """
    q = _map_rating(quality, scale)

    # Standard SM-2 easiness factor update
    new_ef = current_ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ef = max(1.3, new_ef)

    if q < 3:
        # Failed review — reset
        new_repetitions = 0
        new_interval = 1
    else:
        new_repetitions = current_repetitions + 1
        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = int(current_interval * new_ef)

    next_review = datetime.now(timezone.utc) + timedelta(days=new_interval)

    return SM2Result(
        easiness_factor=round(new_ef, 2),
        interval=new_interval,
        repetitions=new_repetitions,
        next_review_date=next_review,
    )
