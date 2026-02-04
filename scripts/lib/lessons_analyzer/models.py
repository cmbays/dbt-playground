"""Data models for LESSONS.md Analyzer.

Provides typed dataclasses for sessions, patterns, and analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DebugSessionData:
    """Represents a debug session from database for analysis."""

    session_id: str
    bug_description: str
    root_cause: str
    tags: list[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: int
    outcome: str
    step_count: int

    @property
    def session_date(self) -> datetime:
        """Return start_time date for compatibility."""
        return self.start_time


@dataclass
class RootCauseVariant:
    """Specific root cause within a pattern."""

    cause: str
    count: int
    example_sessions: list[str]


@dataclass
class Pattern:
    """Extracted pattern from analysis."""

    pattern_name: str
    frequency: int
    first_seen: datetime
    last_seen: datetime
    confidence_score: float
    root_causes: list[RootCauseVariant]
    tags: list[str]
    related_sessions: list[str]
    suggested_mitigations: list[str] = field(default_factory=list)
    status: str = 'REVIEW'  # PROMOTE, CANDIDATE, REVIEW, IGNORE
    avg_debug_minutes: float = 0.0

    @property
    def days_since_last(self) -> int:
        """Days since pattern was last seen."""
        now = datetime.now()
        last = self.last_seen
        # Handle timezone-aware vs naive datetime comparison
        if last.tzinfo is not None and now.tzinfo is None:
            now = now.replace(tzinfo=last.tzinfo)
        elif last.tzinfo is None and now.tzinfo is not None:
            last = last.replace(tzinfo=now.tzinfo)
        return (now - last).days


# Pattern status thresholds
PATTERN_STATUS = {
    'PROMOTE': {'min_score': 0.8, 'min_freq': 3},
    'CANDIDATE': {'min_score': 0.7, 'min_freq': 2},
    'REVIEW': {'min_score': 0.5, 'min_freq': 2},
    'IGNORE': {'min_score': 0.0, 'min_freq': 0},
}
