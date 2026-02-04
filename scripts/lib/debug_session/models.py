"""Data models for Debug Session Tracker.

Provides typed dataclasses for sessions and steps.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# Valid protocol phases from 7-step Debug Agent
PROTOCOL_PHASES = {
    '1-reproduce': 'Confirm bug exists reliably',
    '2-blast_radius': 'Identify affected components',
    '3-root_cause': 'Identify underlying cause',
    '4-fix_design': 'Design the solution',
    '5-implement': 'Code the fix',
    '6-verify': 'Confirm fix works',
    '7-prevent': 'Add tests/docs to prevent recurrence',
}

# Valid outcomes
VALID_OUTCOMES = {'resolved', 'escalated', 'inconclusive', 'in_progress'}

# Valid severity levels
VALID_SEVERITIES = {'high', 'medium', 'low'}


@dataclass
class DebugStep:
    """A single step in a debug session."""

    session_id: str
    step_number: int
    timestamp: datetime
    protocol_phase: str
    findings: str
    evidence: Optional[str] = None

    def __post_init__(self):
        """Validate phase is valid."""
        if self.protocol_phase not in PROTOCOL_PHASES:
            valid = ', '.join(PROTOCOL_PHASES.keys())
            raise ValueError(f"Invalid phase '{self.protocol_phase}'. Valid: {valid}")


@dataclass
class DebugSession:
    """A debug session tracking bug investigation."""

    session_id: str
    bug_description: str
    start_time: datetime
    severity: str = 'medium'
    tags: list[str] = field(default_factory=list)
    bug_id: Optional[str] = None
    context: Optional[str] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    outcome: str = 'in_progress'
    step_count: int = 0

    def __post_init__(self):
        """Validate fields."""
        if self.severity not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity '{self.severity}'. Valid: {VALID_SEVERITIES}")
        if self.outcome not in VALID_OUTCOMES:
            raise ValueError(f"Invalid outcome '{self.outcome}'. Valid: {VALID_OUTCOMES}")


@dataclass
class SessionState:
    """Lightweight state for CLI responsiveness."""

    session_id: str
    start_time: datetime
    step_count: int = 0
    last_phase: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'step_count': self.step_count,
            'last_phase': self.last_phase,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SessionState':
        """Create from dictionary."""
        return cls(
            session_id=data['session_id'],
            start_time=datetime.fromisoformat(data['start_time']),
            step_count=data.get('step_count', 0),
            last_phase=data.get('last_phase'),
        )
