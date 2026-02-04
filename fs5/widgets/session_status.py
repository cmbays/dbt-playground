"""
FS5 Session Status Widget.

Displays current session phase, status, and time-in-phase.
Implements FR-005 from PRD-027.

Version: v0.10.0
Created: 2026-02-03
"""

from dataclasses import dataclass
from datetime import datetime, UTC
from html import escape
from typing import Literal


@dataclass
class SessionStatusWidget:
    """Widget displaying current session status.

    Attributes:
        feature_name: Active ticket/feature name (correlation_id)
        current_phase: Current workflow phase
        time_in_phase_minutes: Minutes spent in current phase
        session_status: Overall session status
        started_at: Session start timestamp
    """

    feature_name: str
    current_phase: str | None
    time_in_phase_minutes: int
    session_status: Literal["active", "stuck", "complete", "unknown"]
    started_at: datetime | None = None

    def __post_init__(self):
        """Set defaults for display."""
        if self.current_phase is None:
            self.current_phase = "NOT_STARTED"

    @classmethod
    def from_session(cls, session: dict | None, feature_name: str = "unknown") -> "SessionStatusWidget":
        """Create widget from session data.

        Args:
            session: Session dict from get_session_status() or None
            feature_name: Feature name to display

        Returns:
            SessionStatusWidget instance
        """
        if session is None:
            return cls(
                feature_name=feature_name,
                current_phase=None,
                time_in_phase_minutes=0,
                session_status="unknown",
                started_at=None,
            )

        # Calculate time in phase
        phase_entered = session.get("phase_entered_at")
        if phase_entered:
            if isinstance(phase_entered, str):
                phase_entered = datetime.fromisoformat(phase_entered.replace("Z", "+00:00"))
            time_in_phase = int((datetime.now(UTC) - phase_entered).total_seconds() / 60)
        else:
            time_in_phase = 0

        # Determine session status
        status = session.get("status", "unknown")
        if status == "active" and time_in_phase > 30:
            # Could be stuck - let anomaly detection confirm
            status = "active"  # Don't auto-mark as stuck

        return cls(
            feature_name=feature_name,
            current_phase=session.get("current_phase"),
            time_in_phase_minutes=time_in_phase,
            session_status=status,
            started_at=session.get("started_at"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "feature_name": self.feature_name,
            "current_phase": self.current_phase,
            "time_in_phase_minutes": self.time_in_phase_minutes,
            "session_status": self.session_status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }

    def render_console(self) -> str:
        """Render widget for console output.

        Returns:
            Formatted string for terminal display
        """
        status_icon = {
            "active": "●",
            "stuck": "⚠",
            "complete": "✓",
            "unknown": "?",
        }.get(self.session_status, "?")

        phase_display = self.current_phase or "NOT_STARTED"

        lines = [
            "┌─────────────────────────────────────┐",
            "│         SESSION STATUS              │",
            "├─────────────────────────────────────┤",
            f"│ Feature: {self.feature_name[:26]:<26} │",
            f"│ Phase:   {phase_display:<26} │",
            f"│ Time:    {self.time_in_phase_minutes} minutes{' ' * (18 - len(str(self.time_in_phase_minutes)))}│",
            f"│ Status:  {status_icon} {self.session_status:<23} │",
            "└─────────────────────────────────────┘",
        ]
        return "\n".join(lines)

    def render_html(self) -> str:
        """Render widget as HTML fragment.

        Returns:
            HTML string for dashboard embedding
        """
        status_class = {
            "active": "status-active",
            "stuck": "status-stuck",
            "complete": "status-complete",
            "unknown": "status-unknown",
        }.get(self.session_status, "status-unknown")

        phase_display = self.current_phase or "NOT_STARTED"

        return f"""
        <div class="widget session-status-widget">
            <h3>Session Status</h3>
            <div class="widget-content">
                <div class="stat">
                    <span class="label">Feature</span>
                    <span class="value">{escape(self.feature_name)}</span>
                </div>
                <div class="stat">
                    <span class="label">Current Phase</span>
                    <span class="value phase-{phase_display.lower()}">{phase_display}</span>
                </div>
                <div class="stat">
                    <span class="label">Time in Phase</span>
                    <span class="value">{self.time_in_phase_minutes} min</span>
                </div>
                <div class="stat">
                    <span class="label">Status</span>
                    <span class="value {status_class}">{self.session_status.upper()}</span>
                </div>
            </div>
        </div>
        """
