"""
FS5 Anomaly Alerts Widget.

Displays active anomalies with severity and actions.
Implements FR-009 from PRD-027.

Version: v0.10.0
Created: 2026-02-03
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from html import escape
from typing import Literal


@dataclass
class AnomalyAlert:
    """A single anomaly alert record."""

    anomaly_id: str
    rule_id: str
    severity: Literal["INFO", "WARNING", "ERROR", "CRITICAL"]
    description: str
    detected_at: datetime
    details: dict = field(default_factory=dict)
    acknowledged: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "anomaly_id": self.anomaly_id,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "description": self.description,
            "detected_at": self.detected_at.isoformat(),
            "details": self.details,
            "acknowledged": self.acknowledged,
        }


@dataclass
class AnomalyAlertsWidget:
    """Widget displaying active anomaly alerts.

    Attributes:
        alerts: List of active anomaly alerts
        max_display: Maximum items to display
    """

    alerts: list[AnomalyAlert] = field(default_factory=list)
    max_display: int = 5

    @classmethod
    def from_anomalies(
        cls,
        anomalies: list,  # List of Anomaly from services
        max_display: int = 5
    ) -> "AnomalyAlertsWidget":
        """Create widget from anomaly list.

        Args:
            anomalies: List of Anomaly from get_active_anomalies()
            max_display: Maximum alerts to show

        Returns:
            AnomalyAlertsWidget instance
        """
        alerts = []
        for a in anomalies:
            alerts.append(AnomalyAlert(
                anomaly_id=a.anomaly_id,
                rule_id=a.rule_id,
                severity=a.severity.value,
                description=a.description,
                detected_at=a.detected_at,
                details=a.details,
                acknowledged=False,
            ))

        # Sort by severity (CRITICAL first) then by time
        severity_order = {"CRITICAL": 0, "ERROR": 1, "WARNING": 2, "INFO": 3}
        alerts.sort(key=lambda x: (severity_order.get(x.severity, 4), x.detected_at))

        return cls(
            alerts=alerts[:max_display],
            max_display=max_display,
        )

    @classmethod
    def empty(cls) -> "AnomalyAlertsWidget":
        """Create empty widget for healthy sessions."""
        return cls(alerts=[], max_display=5)

    def has_critical(self) -> bool:
        """Check if any critical alerts exist."""
        return any(a.severity == "CRITICAL" for a in self.alerts)

    def has_alerts(self) -> bool:
        """Check if any alerts exist."""
        return len(self.alerts) > 0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "alerts": [a.to_dict() for a in self.alerts],
            "count": len(self.alerts),
            "has_critical": self.has_critical(),
            "max_display": self.max_display,
        }

    def render_console(self) -> str:
        """Render widget for console output.

        Returns:
            Formatted string for terminal display
        """
        lines = [
            "┌─────────────────────────────────────────────────────────┐",
            "│                   ANOMALY ALERTS                        │",
            "├─────────────────────────────────────────────────────────┤",
        ]

        if not self.alerts:
            lines.append("│ ✓ No active anomalies - workflow is healthy            │")
        else:
            for alert in self.alerts[:self.max_display]:
                # Severity indicator
                severity_icons = {
                    "CRITICAL": "🔴",
                    "ERROR": "🟠",
                    "WARNING": "🟡",
                    "INFO": "🔵",
                }
                icon = severity_icons.get(alert.severity, "⚪")

                # Format time
                time_str = alert.detected_at.strftime("%H:%M")

                # Truncate description
                desc = alert.description[:40].ljust(40)

                lines.append(f"│ {icon} [{alert.severity[:4]:>4}] {time_str} {desc} │")

        lines.append("└─────────────────────────────────────────────────────────┘")

        return "\n".join(lines)

    def render_html(self) -> str:
        """Render widget as HTML fragment.

        Returns:
            HTML string for dashboard embedding
        """
        if not self.alerts:
            content_html = """
                <div class="no-alerts">
                    <span class="check-icon">✓</span>
                    <span>No active anomalies - workflow is healthy</span>
                </div>
            """
        else:
            items = []
            for alert in self.alerts:
                severity_class = f"severity-{alert.severity.lower()}"
                time_str = alert.detected_at.strftime("%H:%M")

                # Build details string with HTML escaping for security
                details_items = []
                for k, v in alert.details.items():
                    details_items.append(f"<li><strong>{escape(str(k))}:</strong> {escape(str(v))}</li>")
                details_html = f"<ul class='alert-details'>{''.join(details_items)}</ul>" if details_items else ""

                items.append(f"""
                    <div class="alert-item {severity_class}">
                        <div class="alert-header">
                            <span class="alert-severity">{escape(alert.severity)}</span>
                            <span class="alert-rule">{escape(alert.rule_id)}</span>
                            <span class="alert-time">{time_str}</span>
                        </div>
                        <div class="alert-description">{escape(alert.description)}</div>
                        {details_html}
                        <button class="dismiss-btn" data-anomaly-id="{escape(alert.anomaly_id)}">Dismiss</button>
                    </div>
                """)
            content_html = "\n".join(items)

        widget_class = "has-critical" if self.has_critical() else ""

        return f"""
        <div class="widget anomaly-alerts-widget {widget_class}">
            <h3>Anomaly Alerts</h3>
            <div class="widget-content alerts-container">
                {content_html}
            </div>
        </div>
        """
