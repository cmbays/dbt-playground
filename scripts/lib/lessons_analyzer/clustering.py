"""Pattern clustering algorithm for LESSONS.md Analyzer.

Groups debug sessions by keyword overlap in root_cause field.
"""

import re
from collections import Counter
from typing import Optional

from scripts.lib.lessons_analyzer.models import DebugSessionData, Pattern, RootCauseVariant
from scripts.lib.lessons_analyzer.scoring import calculate_score, classify_pattern

# Stop words to exclude from keyword extraction
STOP_WORDS = {
    'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'be',
    'are', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought',
    'used', 'get', 'got', 'getting', 'this', 'that', 'these', 'those', 'it', 'its',
    'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither', 'not', 'only',
    'just', 'also', 'very', 'too', 'quite', 'rather', 'more', 'most', 'less', 'least',
    'all', 'any', 'some', 'no', 'none', 'one', 'two', 'three', 'first', 'second',
    'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose', 'there',
    'here', 'now', 'then', 'always', 'never', 'sometimes', 'often', 'usually',
    'error', 'issue', 'problem', 'bug', 'fix', 'fixed', 'caused', 'due',
}


def normalize_keywords(text: str) -> set[str]:
    """Extract normalized keywords from text.

    Args:
        text: Text to extract keywords from

    Returns:
        Set of normalized keywords
    """
    if not text:
        return set()

    # Extract words (alphanumeric + underscore)
    words = re.findall(r'\b[a-z][a-z0-9_]+\b', text.lower())

    # Filter out stop words and short words
    return {w for w in words if len(w) > 2 and w not in STOP_WORDS}


def keyword_overlap(set1: set[str], set2: set[str]) -> float:
    """Calculate overlap between keyword sets.

    Uses modified Jaccard-like measure based on smaller set size.

    Args:
        set1: First keyword set
        set2: Second keyword set

    Returns:
        Overlap ratio (0.0 to 1.0)
    """
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    smaller = min(len(set1), len(set2))

    return intersection / smaller if smaller > 0 else 0.0


def extract_pattern_name(sessions: list[DebugSessionData]) -> str:
    """Generate descriptive pattern name from clustered sessions.

    Uses most common keywords across root causes.

    Args:
        sessions: List of debug sessions in the cluster

    Returns:
        Human-readable pattern name
    """
    all_keywords = []
    for session in sessions:
        all_keywords.extend(normalize_keywords(session.root_cause))

    # Get top keywords
    common = Counter(all_keywords).most_common(4)
    keywords = [kw for kw, _ in common]

    if not keywords:
        return 'Unclassified pattern'

    # Build readable name based on common patterns
    keywords_set = set(keywords)

    if keywords_set & {'race', 'condition', 'concurrent', 'lock', 'mutex'}:
        context = next((k for k in keywords if k not in {'race', 'condition', 'concurrent', 'lock', 'mutex'}), 'async code')
        return f'Race condition in {context}'

    if keywords_set & {'null', 'none', 'undefined', 'missing'}:
        return 'Missing null check'

    if keywords_set & {'timeout', 'timed'}:
        context = next((k for k in keywords if k not in {'timeout', 'timed', 'out'}), 'external service')
        return f'Timeout from {context}'

    if keywords_set & {'state', 'corrupt', 'corrupted', 'invalid'}:
        return 'State corruption'

    if keywords_set & {'import', 'module', 'package'}:
        return 'Import/module error'

    if keywords_set & {'type', 'cast', 'conversion'}:
        return 'Type conversion error'

    # Generic: capitalize top keywords
    return ' '.join(keywords[:3]).title()


def extract_variants(sessions: list[DebugSessionData]) -> list[RootCauseVariant]:
    """Extract root cause variants from clustered sessions.

    Groups similar root causes and counts occurrences.

    Args:
        sessions: List of debug sessions

    Returns:
        List of root cause variants with counts
    """
    cause_counts: dict[str, list[str]] = {}

    for session in sessions:
        # Normalize root cause for grouping
        cause = session.root_cause.strip()

        # Simple grouping by first 50 chars (could be enhanced)
        key = cause[:50] if len(cause) > 50 else cause

        if key not in cause_counts:
            cause_counts[key] = []
        cause_counts[key].append(session.session_id)

    variants = []
    for cause, session_ids in sorted(cause_counts.items(), key=lambda x: -len(x[1])):
        variants.append(RootCauseVariant(
            cause=cause,
            count=len(session_ids),
            example_sessions=session_ids[:3],  # Limit to 3 examples
        ))

    return variants


def cluster_root_causes(
    sessions: list[DebugSessionData],
    threshold: float = 0.5,
    min_cluster_size: int = 2,
) -> list[Pattern]:
    """Group sessions by keyword overlap in root_cause field.

    Uses greedy matching with configurable overlap threshold.

    Args:
        sessions: List of debug sessions to cluster
        threshold: Minimum keyword overlap to cluster (default 0.5)
        min_cluster_size: Minimum sessions per cluster (default 2)

    Returns:
        List of extracted patterns
    """
    if not sessions:
        return []

    # Pre-compute keywords for each session
    session_keywords = {
        s.session_id: normalize_keywords(s.root_cause)
        for s in sessions
    }

    clusters: list[list[DebugSessionData]] = []
    used: set[str] = set()

    # Sort sessions by date (newest first) for better clustering
    sorted_sessions = sorted(sessions, key=lambda s: s.start_time, reverse=True)

    for session in sorted_sessions:
        if session.session_id in used:
            continue

        # Start new cluster with this session
        cluster = [session]
        used.add(session.session_id)
        kw1 = session_keywords[session.session_id]

        # Find similar sessions
        for other in sorted_sessions:
            if other.session_id in used:
                continue

            kw2 = session_keywords[other.session_id]
            overlap = keyword_overlap(kw1, kw2)

            if overlap >= threshold:
                cluster.append(other)
                used.add(other.session_id)

        if len(cluster) >= min_cluster_size:
            clusters.append(cluster)

    # Convert clusters to patterns
    patterns = []
    for cluster in clusters:
        # Calculate dates
        dates = [s.start_time for s in cluster]
        first_seen = min(dates)
        last_seen = max(dates)

        # Calculate score (use current time for recency, not first session)
        from datetime import datetime
        from datetime import timezone as tz
        now = datetime.now(tz.utc)
        # Convert naive datetime to UTC if needed
        last_seen_utc = last_seen if last_seen.tzinfo else last_seen.replace(tzinfo=tz.utc)
        days_since_last = (now - last_seen_utc).days
        score = calculate_score(len(cluster), days_since_last, cluster)
        status = classify_pattern(score, len(cluster))

        # Calculate average debug time
        durations = [s.duration_minutes for s in cluster if s.duration_minutes]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Aggregate tags
        all_tags = []
        for s in cluster:
            all_tags.extend(s.tags)
        unique_tags = list(set(all_tags))

        pattern = Pattern(
            pattern_name=extract_pattern_name(cluster),
            frequency=len(cluster),
            first_seen=first_seen,
            last_seen=last_seen,
            confidence_score=score,
            root_causes=extract_variants(cluster),
            tags=unique_tags,
            related_sessions=[s.session_id for s in cluster],
            status=status,
            avg_debug_minutes=avg_duration,
        )
        patterns.append(pattern)

    # Sort by score descending
    patterns.sort(key=lambda p: p.confidence_score, reverse=True)

    return patterns
