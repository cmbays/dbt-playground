"""Scoring algorithm for pattern extraction.

Multi-factor scoring: (Frequency * 0.4) + (Recency * 0.3) + (Consistency * 0.3)

Adopted from FS1 consolidate-memory.py patterns.
"""

import math
from datetime import datetime

from scripts.lib.lessons_analyzer.models import DebugSessionData, PATTERN_STATUS


def frequency_weight(count: int, max_count: int = 10) -> float:
    """Calculate frequency weight using logarithmic scaling.

    Prevents dominance by high-frequency patterns.
    Capped at max_count occurrences for normalization.

    Args:
        count: Number of occurrences
        max_count: Maximum count for normalization (default 10)

    Returns:
        Weight between 0.0 and 1.0

    Examples:
        count=2 -> ~0.46
        count=3 -> ~0.58
        count=5 -> ~0.73
        count=10 -> 1.00
    """
    if count <= 0:
        return 0.0

    normalized_count = min(count, max_count)
    return math.log(normalized_count + 1) / math.log(max_count + 1)


def recency_weight(days_since_last: int, decay_period: int = 30) -> float:
    """Calculate recency weight with linear decay.

    More recent patterns get higher weight.

    Args:
        days_since_last: Days since last occurrence
        decay_period: Number of days for full decay (default 30)

    Returns:
        Weight between 0.0 and 1.0

    Examples:
        days=0 -> 1.00 (today)
        days=7 -> ~0.77
        days=15 -> 0.50
        days=30 -> 0.00
    """
    if days_since_last <= 0:
        return 1.0

    return max(0.0, 1.0 - (days_since_last / decay_period))


def consistency_weight(sessions: list[DebugSessionData]) -> float:
    """Calculate consistency weight based on tag diversity and time spread.

    Higher score if pattern appears across:
    - Different tags (diverse contexts)
    - Different time periods (not clustered)

    Args:
        sessions: List of debug sessions in the pattern

    Returns:
        Weight between 0.0 and 1.0
    """
    if len(sessions) < 2:
        return 0.0

    # Tag diversity: unique tags / total tag occurrences
    all_tags = [tag for s in sessions for tag in s.tags]
    if all_tags:
        tag_diversity = len(set(all_tags)) / len(all_tags)
    else:
        tag_diversity = 0.5  # Neutral if no tags

    # Time spread: days between first and last occurrence
    dates = [s.start_time for s in sessions]
    date_spread = (max(dates) - min(dates)).days
    time_score = min(1.0, date_spread / 14)  # Max at 14+ days spread

    # Combine: 60% tag diversity, 40% time spread
    return (0.6 * tag_diversity) + (0.4 * time_score)


def calculate_score(
    frequency: int,
    days_since_last: int,
    sessions: list[DebugSessionData],
) -> float:
    """Calculate total pattern score.

    Formula: (Frequency * 0.4) + (Recency * 0.3) + (Consistency * 0.3)

    Args:
        frequency: Number of occurrences
        days_since_last: Days since last occurrence
        sessions: List of sessions for consistency calculation

    Returns:
        Score between 0.0 and 1.0
    """
    freq_w = frequency_weight(frequency)
    rec_w = recency_weight(days_since_last)
    cons_w = consistency_weight(sessions)

    return (freq_w * 0.4) + (rec_w * 0.3) + (cons_w * 0.3)


def classify_pattern(score: float, frequency: int) -> str:
    """Classify pattern based on score and frequency.

    Args:
        score: Confidence score (0.0 to 1.0)
        frequency: Number of occurrences

    Returns:
        Pattern status: PROMOTE, CANDIDATE, REVIEW, or IGNORE
    """
    # Check in order from highest to lowest threshold
    if score >= PATTERN_STATUS['PROMOTE']['min_score'] and frequency >= PATTERN_STATUS['PROMOTE']['min_freq']:
        return 'PROMOTE'

    if score >= PATTERN_STATUS['CANDIDATE']['min_score'] and frequency >= PATTERN_STATUS['CANDIDATE']['min_freq']:
        return 'CANDIDATE'

    if score >= PATTERN_STATUS['REVIEW']['min_score'] and frequency >= PATTERN_STATUS['REVIEW']['min_freq']:
        return 'REVIEW'

    return 'IGNORE'
