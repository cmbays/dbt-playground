"""FS5 Dashboard Widgets Module.

Contains widget components for the metrics dashboard.

Widgets:
- SessionStatusWidget: Current session phase and status
- ScoresWidget: Adherence and health scores
- PhaseTimelineWidget: Visual phase progression
- AgentActivityWidget: Agent invocation feed
- AnomalyAlertsWidget: Active anomaly display

Version: v0.10.0
Created: 2026-02-03
"""

from fs5.widgets.session_status import SessionStatusWidget
from fs5.widgets.scores import ScoresWidget
from fs5.widgets.phase_timeline import PhaseTimelineWidget
from fs5.widgets.agent_activity import AgentActivityWidget
from fs5.widgets.anomaly_alerts import AnomalyAlertsWidget
from fs5.widgets.dashboard import Dashboard

__all__ = [
    "SessionStatusWidget",
    "ScoresWidget",
    "PhaseTimelineWidget",
    "AgentActivityWidget",
    "AnomalyAlertsWidget",
    "Dashboard",
]
