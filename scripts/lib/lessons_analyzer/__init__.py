"""LESSONS.md Analyzer library for WAVE3-021.

Automated pattern extraction engine that analyzes debug sessions
to identify recurring root causes for compound learning.

Part of Wave 3 P1: Protocol Enhancements (Issue #238)
"""

from scripts.lib.lessons_analyzer.analyzer import LessonsAnalyzer
from scripts.lib.lessons_analyzer.exceptions import (
    AnalyzerError,
    DatabaseNotFoundError,
    InsufficientDataError,
    NoSessionsFoundError,
    PatternNotFoundError,
)
from scripts.lib.lessons_analyzer.models import DebugSessionData, Pattern, RootCauseVariant
from scripts.lib.lessons_analyzer.scoring import (
    calculate_score,
    classify_pattern,
    consistency_weight,
    frequency_weight,
    recency_weight,
)

__all__ = [
    'LessonsAnalyzer',
    'Pattern',
    'RootCauseVariant',
    'DebugSessionData',
    'AnalyzerError',
    'NoSessionsFoundError',
    'PatternNotFoundError',
    'DatabaseNotFoundError',
    'InsufficientDataError',
    'calculate_score',
    'classify_pattern',
    'frequency_weight',
    'recency_weight',
    'consistency_weight',
]
