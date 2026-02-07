"""Custom exceptions for Debug Session Tracker.

Provides a clear exception hierarchy for different error types.
"""


class DebugSessionError(Exception):
    """Base exception for debug session errors."""

    pass


class NoActiveSessionError(DebugSessionError):
    """Raised when operation requires active session but none exists."""

    pass


class SessionAlreadyActiveError(DebugSessionError):
    """Raised when starting session but one is already active."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(
            f"Session '{session_id}' is already active. "
            f"Use 'end' to complete it or 'start --force' to override."
        )


class DatabaseConnectionError(DebugSessionError):
    """Raised when DuckDB connection fails."""

    pass


class ValidationError(DebugSessionError):
    """Raised when input validation fails."""

    pass
