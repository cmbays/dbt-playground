"""
FS5 Agent Activity Widget.

Displays chronological feed of agent invocations.
Implements FR-008 from PRD-027.

Version: v0.10.0
Created: 2026-02-03
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Literal


@dataclass
class AgentInvocation:
    """A single agent invocation record."""

    agent_name: str
    action: str
    timestamp: datetime
    outcome: Literal["success", "failure", "redo", "pending"]
    artifact_path: str | None = None
    duration_seconds: int | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "outcome": self.outcome,
            "artifact_path": self.artifact_path,
            "duration_seconds": self.duration_seconds,
        }


@dataclass
class AgentActivityWidget:
    """Widget displaying agent activity feed.

    Attributes:
        invocations: List of agent invocations
        max_display: Maximum items to display
    """

    invocations: list[AgentInvocation] = field(default_factory=list)
    max_display: int = 10

    @classmethod
    def from_events(
        cls,
        events: list[dict],
        max_display: int = 10
    ) -> "AgentActivityWidget":
        """Create widget from agent invocation events.

        Args:
            events: List of agent.invoked/completed events
            max_display: Maximum items to show

        Returns:
            AgentActivityWidget instance
        """
        invocations = []

        # Build invocation map for matching starts with completions
        invocation_map: dict[str, dict] = {}

        for event in events:
            event_type = event.get("event_type", "")
            payload = event.get("payload", {})

            if isinstance(payload, str):
                import json
                try:
                    payload = json.loads(payload)
                except (json.JSONDecodeError, TypeError):
                    payload = {}

            timestamp = event.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            if event_type == "agent.invoked":
                agent_name = payload.get("agent_type", "unknown")
                action = payload.get("action", payload.get("task", ""))
                invocation_id = payload.get("invocation_id", str(len(invocations)))

                invocation_map[invocation_id] = {
                    "agent_name": agent_name,
                    "action": action[:50] if action else "Task",  # Truncate long actions
                    "timestamp": timestamp,
                    "outcome": "pending",
                    "artifact_path": None,
                    "start_time": timestamp,
                }

            elif event_type == "agent.completed":
                invocation_id = payload.get("invocation_id")
                outcome = payload.get("outcome", "success").lower()
                artifact = payload.get("artifact_path")

                if invocation_id and invocation_id in invocation_map:
                    invocation_map[invocation_id]["outcome"] = outcome
                    invocation_map[invocation_id]["artifact_path"] = artifact

                    # Calculate duration
                    start = invocation_map[invocation_id].get("start_time")
                    if start and timestamp:
                        duration = int((timestamp - start).total_seconds())
                        invocation_map[invocation_id]["duration_seconds"] = duration

        # Convert map to list of AgentInvocations
        for inv_id, data in invocation_map.items():
            invocations.append(AgentInvocation(
                agent_name=data["agent_name"],
                action=data["action"],
                timestamp=data["timestamp"] or datetime.now(UTC),
                outcome=data["outcome"],
                artifact_path=data.get("artifact_path"),
                duration_seconds=data.get("duration_seconds"),
            ))

        # Sort by timestamp descending (most recent first)
        invocations.sort(key=lambda x: x.timestamp, reverse=True)

        return cls(
            invocations=invocations[:max_display],
            max_display=max_display,
        )

    @classmethod
    def empty(cls) -> "AgentActivityWidget":
        """Create empty widget for new sessions."""
        return cls(invocations=[], max_display=10)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "invocations": [inv.to_dict() for inv in self.invocations],
            "count": len(self.invocations),
            "max_display": self.max_display,
        }

    def render_console(self) -> str:
        """Render widget for console output.

        Returns:
            Formatted string for terminal display
        """
        lines = [
            "┌─────────────────────────────────────────────────────────┐",
            "│                   AGENT ACTIVITY                        │",
            "├─────────────────────────────────────────────────────────┤",
        ]

        if not self.invocations:
            lines.append("│ No agent activity recorded                              │")
        else:
            for inv in self.invocations[:self.max_display]:
                # Format timestamp as HH:MM
                time_str = inv.timestamp.strftime("%H:%M")

                # Outcome icon
                outcome_icon = {
                    "success": "✓",
                    "failure": "✗",
                    "redo": "↺",
                    "pending": "…",
                }.get(inv.outcome, "?")

                # Truncate agent name and action
                agent = inv.agent_name[:12].ljust(12)
                action = inv.action[:30].ljust(30)

                lines.append(f"│ {time_str} {outcome_icon} {agent} {action} │")

        lines.append("└─────────────────────────────────────────────────────────┘")

        return "\n".join(lines)

    def render_html(self) -> str:
        """Render widget as HTML fragment.

        Returns:
            HTML string for dashboard embedding
        """
        if not self.invocations:
            items_html = '<div class="no-activity">No agent activity recorded</div>'
        else:
            items = []
            for inv in self.invocations:
                outcome_class = f"outcome-{inv.outcome}"
                time_str = inv.timestamp.strftime("%H:%M")
                duration_str = f" ({inv.duration_seconds}s)" if inv.duration_seconds else ""
                artifact_link = ""
                if inv.artifact_path:
                    artifact_link = f'<a href="{inv.artifact_path}" class="artifact-link">📄</a>'

                items.append(f"""
                    <div class="activity-item {outcome_class}">
                        <span class="activity-time">{time_str}</span>
                        <span class="activity-agent">{inv.agent_name}</span>
                        <span class="activity-action">{inv.action}{duration_str}</span>
                        {artifact_link}
                    </div>
                """)
            items_html = "\n".join(items)

        return f"""
        <div class="widget agent-activity-widget">
            <h3>Agent Activity</h3>
            <div class="widget-content activity-feed">
                {items_html}
            </div>
        </div>
        """
