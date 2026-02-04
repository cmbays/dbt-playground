"""
FS5 Dashboard.

Main dashboard combining all widgets for a complete session overview.
Implements FR-005 through FR-009 from PRD-027.

Version: v0.10.0
Created: 2026-02-03
"""

from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
import json

from fs5.widgets.session_status import SessionStatusWidget
from fs5.widgets.scores import ScoresWidget
from fs5.widgets.phase_timeline import PhaseTimelineWidget
from fs5.widgets.agent_activity import AgentActivityWidget
from fs5.widgets.anomaly_alerts import AnomalyAlertsWidget


@dataclass
class Dashboard:
    """Complete metrics dashboard.

    Combines all widgets for a comprehensive session overview.

    Attributes:
        session_status: Current session status widget
        scores: Adherence and health scores widget
        phase_timeline: Phase progression widget
        agent_activity: Agent invocation feed widget
        anomaly_alerts: Active anomalies widget
        generated_at: Dashboard generation timestamp
    """

    session_status: SessionStatusWidget
    scores: ScoresWidget
    phase_timeline: PhaseTimelineWidget
    agent_activity: AgentActivityWidget
    anomaly_alerts: AnomalyAlertsWidget
    generated_at: datetime | None = None

    def __post_init__(self):
        """Set generation timestamp."""
        if self.generated_at is None:
            self.generated_at = datetime.now(UTC)

    @classmethod
    def load(cls, correlation_id: str) -> "Dashboard":
        """Load dashboard for a correlation_id from database.

        Args:
            correlation_id: Feature branch or task ID

        Returns:
            Dashboard instance with all widgets populated
        """
        from fs5.services import (
            calculate_adherence_score,
            get_active_anomalies,
            get_session_status,
        )
        from fs5.core.db import get_connection

        # Get session status
        session = get_session_status(correlation_id)
        session_widget = SessionStatusWidget.from_session(session, correlation_id)

        # Fetch events for timeline and activity
        events = []
        try:
            with get_connection() as conn:
                result = conn.execute("""
                    SELECT event_timestamp, event_type, payload
                    FROM v_unified_events
                    WHERE correlation_id = ?
                    ORDER BY event_timestamp
                """, [correlation_id]).fetchall()

                events = [
                    {
                        "timestamp": row[0],
                        "event_type": row[1],
                        "payload": row[2]
                    }
                    for row in result
                ]
        except Exception:
            # Database or view doesn't exist yet
            pass

        # Build phase timeline
        phase_timeline = PhaseTimelineWidget.from_events(events)

        # Build agent activity
        agent_activity = AgentActivityWidget.from_events(events)

        # Calculate adherence score
        score = calculate_adherence_score(correlation_id, events)
        scores_widget = ScoresWidget.from_adherence_score(score)

        # Get anomalies
        anomalies = get_active_anomalies(correlation_id)
        anomaly_widget = AnomalyAlertsWidget.from_anomalies(anomalies)

        return cls(
            session_status=session_widget,
            scores=scores_widget,
            phase_timeline=phase_timeline,
            agent_activity=agent_activity,
            anomaly_alerts=anomaly_widget,
        )

    @classmethod
    def empty(cls, feature_name: str = "unknown") -> "Dashboard":
        """Create empty dashboard for new sessions.

        Args:
            feature_name: Name of the feature/session

        Returns:
            Dashboard instance with empty widgets
        """
        return cls(
            session_status=SessionStatusWidget(
                feature_name=feature_name,
                current_phase=None,
                time_in_phase_minutes=0,
                session_status="unknown",
            ),
            scores=ScoresWidget.empty(),
            phase_timeline=PhaseTimelineWidget.empty(),
            agent_activity=AgentActivityWidget.empty(),
            anomaly_alerts=AnomalyAlertsWidget.empty(),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_status": self.session_status.to_dict(),
            "scores": self.scores.to_dict(),
            "phase_timeline": self.phase_timeline.to_dict(),
            "agent_activity": self.agent_activity.to_dict(),
            "anomaly_alerts": self.anomaly_alerts.to_dict(),
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent)

    def render_console(self) -> str:
        """Render full dashboard for console output.

        Returns:
            Formatted string for terminal display
        """
        divider = "=" * 60

        sections = [
            divider,
            "                    FS5 METRICS DASHBOARD",
            f"              Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S') if self.generated_at else 'unknown'}",
            divider,
            "",
            self.session_status.render_console(),
            "",
            self.scores.render_console(),
            "",
            self.phase_timeline.render_console(),
            "",
            self.agent_activity.render_console(),
            "",
            self.anomaly_alerts.render_console(),
            "",
            divider,
        ]

        return "\n".join(sections)

    def render_html(self, title: str = "FS5 Metrics Dashboard") -> str:
        """Render full dashboard as HTML page.

        Args:
            title: Page title

        Returns:
            Complete HTML page
        """
        generated_str = self.generated_at.strftime('%Y-%m-%d %H:%M:%S') if self.generated_at else 'unknown'

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-card: #0f3460;
            --text-primary: #eee;
            --text-secondary: #aaa;
            --accent-blue: #4cc9f0;
            --accent-green: #00ff88;
            --accent-yellow: #ffc107;
            --accent-red: #ff4757;
            --accent-purple: #9b59b6;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }}

        .dashboard-header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: var(--bg-secondary);
            border-radius: 10px;
        }}

        .dashboard-header h1 {{
            color: var(--accent-blue);
            margin-bottom: 10px;
        }}

        .dashboard-header .timestamp {{
            color: var(--text-secondary);
            font-size: 0.9em;
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        .widget {{
            background: var(--bg-card);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}

        .widget h3 {{
            color: var(--accent-blue);
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .widget-content {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        /* Session Status */
        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .stat .label {{
            color: var(--text-secondary);
        }}

        .stat .value {{
            font-weight: bold;
        }}

        .status-active {{ color: var(--accent-green); }}
        .status-stuck {{ color: var(--accent-yellow); }}
        .status-complete {{ color: var(--accent-blue); }}
        .status-unknown {{ color: var(--text-secondary); }}

        /* Scores */
        .score-row {{
            margin-bottom: 15px;
        }}

        .score-item {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
        }}

        .score-label {{
            color: var(--text-secondary);
            min-width: 100px;
        }}

        .score-value {{
            font-size: 1.5em;
            font-weight: bold;
        }}

        .score-max {{
            color: var(--text-secondary);
        }}

        progress {{
            flex-grow: 1;
            height: 8px;
            border-radius: 4px;
            appearance: none;
        }}

        progress::-webkit-progress-bar {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }}

        progress::-webkit-progress-value {{
            background: var(--accent-blue);
            border-radius: 4px;
        }}

        .rating-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }}

        .rating-excellent {{ background: var(--accent-green); color: #000; }}
        .rating-good {{ background: var(--accent-blue); color: #000; }}
        .rating-fair {{ background: var(--accent-yellow); color: #000; }}
        .rating-poor {{ background: var(--accent-red); color: #fff; }}

        .penalty-list {{
            list-style: none;
            margin-top: 10px;
            padding-left: 10px;
            font-size: 0.9em;
        }}

        .penalty {{
            color: var(--accent-red);
            padding: 4px 0;
        }}

        /* Phase Timeline */
        .timeline-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
        }}

        .phase-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }}

        .phase-circle {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 3px solid var(--text-secondary);
        }}

        .phase-completed .phase-circle {{
            background: var(--accent-green);
            border-color: var(--accent-green);
        }}

        .phase-current .phase-circle {{
            background: var(--accent-blue);
            border-color: var(--accent-blue);
            animation: pulse 1.5s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}

        .phase-label {{
            font-size: 0.8em;
            color: var(--text-secondary);
        }}

        .phase-duration {{
            font-size: 0.75em;
            color: var(--accent-blue);
        }}

        .phase-connector {{
            flex-grow: 1;
            height: 3px;
            background: var(--text-secondary);
            margin: 0 5px;
        }}

        .connector-completed {{
            background: var(--accent-green);
        }}

        .current-phase {{
            text-align: center;
            padding-top: 15px;
            color: var(--text-secondary);
        }}

        /* Agent Activity */
        .activity-feed {{
            max-height: 300px;
            overflow-y: auto;
        }}

        .activity-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 5px;
            background: rgba(255, 255, 255, 0.05);
        }}

        .activity-time {{
            color: var(--text-secondary);
            font-size: 0.9em;
        }}

        .activity-agent {{
            color: var(--accent-purple);
            font-weight: bold;
        }}

        .activity-action {{
            flex-grow: 1;
            color: var(--text-primary);
        }}

        .outcome-success {{ border-left: 3px solid var(--accent-green); }}
        .outcome-failure {{ border-left: 3px solid var(--accent-red); }}
        .outcome-redo {{ border-left: 3px solid var(--accent-yellow); }}
        .outcome-pending {{ border-left: 3px solid var(--text-secondary); }}

        .no-activity {{
            text-align: center;
            padding: 20px;
            color: var(--text-secondary);
        }}

        /* Anomaly Alerts */
        .alerts-container {{
            max-height: 300px;
            overflow-y: auto;
        }}

        .no-alerts {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 20px;
            color: var(--accent-green);
        }}

        .check-icon {{
            font-size: 1.5em;
        }}

        .alert-item {{
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.05);
        }}

        .severity-critical {{
            border-left: 4px solid var(--accent-red);
            background: rgba(255, 71, 87, 0.1);
        }}

        .severity-error {{
            border-left: 4px solid #ff6b35;
            background: rgba(255, 107, 53, 0.1);
        }}

        .severity-warning {{
            border-left: 4px solid var(--accent-yellow);
            background: rgba(255, 193, 7, 0.1);
        }}

        .severity-info {{
            border-left: 4px solid var(--accent-blue);
            background: rgba(76, 201, 240, 0.1);
        }}

        .alert-header {{
            display: flex;
            gap: 15px;
            margin-bottom: 8px;
        }}

        .alert-severity {{
            font-weight: bold;
            font-size: 0.8em;
        }}

        .alert-rule {{
            color: var(--text-secondary);
            font-size: 0.85em;
        }}

        .alert-time {{
            margin-left: auto;
            color: var(--text-secondary);
            font-size: 0.85em;
        }}

        .alert-description {{
            margin-bottom: 10px;
        }}

        .alert-details {{
            list-style: none;
            font-size: 0.9em;
            color: var(--text-secondary);
        }}

        .alert-details li {{
            padding: 2px 0;
        }}

        .dismiss-btn {{
            background: transparent;
            border: 1px solid var(--text-secondary);
            color: var(--text-secondary);
            padding: 5px 15px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.85em;
            margin-top: 10px;
        }}

        .dismiss-btn:hover {{
            background: var(--text-secondary);
            color: var(--bg-primary);
        }}

        .has-critical {{
            animation: alertPulse 2s infinite;
        }}

        @keyframes alertPulse {{
            0%, 100% {{ box-shadow: 0 0 0 0 rgba(255, 71, 87, 0.4); }}
            50% {{ box-shadow: 0 0 15px 5px rgba(255, 71, 87, 0.2); }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>🎯 FS5 Metrics Dashboard</h1>
        <div class="timestamp">Generated: {generated_str}</div>
    </div>

    <div class="dashboard-grid">
        {self.session_status.render_html()}
        {self.scores.render_html()}
        {self.phase_timeline.render_html()}
        {self.anomaly_alerts.render_html()}
        {self.agent_activity.render_html()}
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);

        // Dismiss button handler
        document.querySelectorAll('.dismiss-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const anomalyId = btn.dataset.anomalyId;
                // TODO: Send dismiss request to backend
                btn.closest('.alert-item').style.display = 'none';
            }});
        }});
    </script>
</body>
</html>"""

    def save_html(self, path: str | Path) -> None:
        """Save dashboard as HTML file.

        Args:
            path: Output file path
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render_html(), encoding="utf-8")
