"""
FS5 Phase Timeline Widget.

Displays visual progression through the 5-stage workflow.
Implements FR-007 from PRD-027.

Version: v0.10.0
Created: 2026-02-03
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Literal

# Canonical phase order
CANONICAL_ORDER = ["UNDERSTAND", "PLAN", "BUILD", "VERIFY", "DEPLOY"]


@dataclass
class PhaseInfo:
    """Information about a single phase."""

    name: str
    status: Literal["completed", "current", "pending"]
    duration_minutes: int | None = None
    entered_at: datetime | None = None
    exited_at: datetime | None = None


@dataclass
class PhaseTimelineWidget:
    """Widget displaying workflow phase timeline.

    Attributes:
        phases: List of PhaseInfo for each canonical phase
        current_phase: Name of current phase (or None)
    """

    phases: list[PhaseInfo] = field(default_factory=list)
    current_phase: str | None = None

    @classmethod
    def from_events(cls, events: list[dict]) -> "PhaseTimelineWidget":
        """Create widget from phase transition events.

        Args:
            events: List of workflow.phase_entered/exited events

        Returns:
            PhaseTimelineWidget instance
        """
        # Track phase data
        phase_data: dict[str, dict] = {}
        current_phase = None

        for event in events:
            event_type = event.get("event_type", "")
            payload = event.get("payload", {})

            # Handle string payloads
            if isinstance(payload, str):
                import json
                try:
                    payload = json.loads(payload)
                except (json.JSONDecodeError, TypeError):
                    payload = {}

            phase = payload.get("phase")
            if not phase or phase not in CANONICAL_ORDER:
                continue

            timestamp = event.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            if phase not in phase_data:
                phase_data[phase] = {
                    "entered_at": None,
                    "exited_at": None,
                }

            if event_type == "workflow.phase_entered":
                phase_data[phase]["entered_at"] = timestamp
                current_phase = phase
            elif event_type == "workflow.phase_exited":
                phase_data[phase]["exited_at"] = timestamp
                if current_phase == phase:
                    current_phase = None

        # Build phase list
        phases = []
        for phase_name in CANONICAL_ORDER:
            data = phase_data.get(phase_name, {})
            entered = data.get("entered_at")
            exited = data.get("exited_at")

            # Determine status
            if exited:
                status = "completed"
            elif entered:
                status = "current"
            else:
                status = "pending"

            # Calculate duration
            duration = None
            if entered:
                end_time = exited or datetime.now(UTC)
                duration = int((end_time - entered).total_seconds() / 60)

            phases.append(PhaseInfo(
                name=phase_name,
                status=status,
                duration_minutes=duration,
                entered_at=entered,
                exited_at=exited,
            ))

        return cls(
            phases=phases,
            current_phase=current_phase,
        )

    @classmethod
    def empty(cls) -> "PhaseTimelineWidget":
        """Create empty widget for new sessions."""
        phases = [
            PhaseInfo(name=phase, status="pending")
            for phase in CANONICAL_ORDER
        ]
        return cls(phases=phases, current_phase=None)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "phases": [
                {
                    "name": p.name,
                    "status": p.status,
                    "duration_minutes": p.duration_minutes,
                    "entered_at": p.entered_at.isoformat() if p.entered_at else None,
                    "exited_at": p.exited_at.isoformat() if p.exited_at else None,
                }
                for p in self.phases
            ],
            "current_phase": self.current_phase,
        }

    def render_console(self) -> str:
        """Render widget for console output.

        Returns:
            Formatted string for terminal display
        """
        lines = [
            "┌─────────────────────────────────────────────────────────┐",
            "│                    PHASE TIMELINE                       │",
            "├─────────────────────────────────────────────────────────┤",
        ]

        # Build timeline visual
        phase_chars = []
        for p in self.phases:
            if p.status == "completed":
                phase_chars.append("●")
            elif p.status == "current":
                phase_chars.append("◐")
            else:
                phase_chars.append("○")

        timeline = "──".join(phase_chars)
        lines.append(f"│  {timeline}  │")

        # Phase labels
        labels = "  ".join(f"{p.name[:4]:>4}" for p in self.phases)
        lines.append(f"│  {labels}  │")

        # Durations for completed/current phases
        durations = []
        for p in self.phases:
            if p.duration_minutes is not None:
                durations.append(f"{p.duration_minutes:>4}m")
            else:
                durations.append("    -")
        duration_line = "  ".join(durations)
        lines.append(f"│  {duration_line}  │")

        lines.append("├─────────────────────────────────────────────────────────┤")
        lines.append(f"│ Current: {self.current_phase or 'NOT_STARTED':<46} │")
        lines.append("└─────────────────────────────────────────────────────────┘")

        return "\n".join(lines)

    def render_html(self) -> str:
        """Render widget as HTML fragment.

        Returns:
            HTML string for dashboard embedding
        """
        phase_items = []
        for i, p in enumerate(self.phases):
            status_class = f"phase-{p.status}"
            duration_str = f"{p.duration_minutes}m" if p.duration_minutes else "-"

            # Connector (except for last phase)
            connector = ""
            if i < len(self.phases) - 1:
                next_status = self.phases[i + 1].status
                connector_class = "connector-completed" if p.status == "completed" else "connector-pending"
                connector = f'<div class="phase-connector {connector_class}"></div>'

            phase_items.append(f"""
                <div class="phase-item {status_class}">
                    <div class="phase-circle"></div>
                    <div class="phase-label">{p.name}</div>
                    <div class="phase-duration">{duration_str}</div>
                </div>
                {connector}
            """)

        return f"""
        <div class="widget phase-timeline-widget">
            <h3>Phase Timeline</h3>
            <div class="widget-content">
                <div class="timeline-container">
                    {''.join(phase_items)}
                </div>
                <div class="current-phase">
                    Current Phase: <strong>{self.current_phase or 'NOT_STARTED'}</strong>
                </div>
            </div>
        </div>
        """
