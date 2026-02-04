"""Custom exceptions for LESSONS.md Analyzer.

Provides a clear exception hierarchy for different error types.
"""


class AnalyzerError(Exception):
    """Base exception for analyzer errors."""

    pass


class NoSessionsFoundError(AnalyzerError):
    """Raised when no sessions match query criteria."""

    pass


class PatternNotFoundError(AnalyzerError):
    """Raised when specified pattern doesn't exist."""

    def __init__(self, pattern_name: str):
        self.pattern_name = pattern_name
        super().__init__(f"Pattern not found: '{pattern_name}'")


class DatabaseNotFoundError(AnalyzerError):
    """Raised when debug_sessions database is missing."""

    pass


class InsufficientDataError(AnalyzerError):
    """Raised when not enough data for meaningful analysis."""

    pass
