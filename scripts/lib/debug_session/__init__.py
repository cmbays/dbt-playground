"""Debug Session Tracker library for WAVE3-020.

This module provides session lifecycle management for debugging workflows,
enabling compound learning through persistent storage and pattern extraction.

Part of Wave 3 P1: Protocol Enhancements (Issue #237)
"""

from scripts.lib.debug_session.exceptions import (
    DatabaseConnectionError,
    DebugSessionError,
    NoActiveSessionError,
    SessionAlreadyActiveError,
    ValidationError,
)
from scripts.lib.debug_session.models import DebugSession, DebugStep, SessionState
from scripts.lib.debug_session.tracker import DebugSessionTracker

__all__ = [
    'DebugSessionTracker',
    'DebugSession',
    'DebugStep',
    'SessionState',
    'DebugSessionError',
    'NoActiveSessionError',
    'SessionAlreadyActiveError',
    'DatabaseConnectionError',
    'ValidationError',
]
