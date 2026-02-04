"""Tests for fs5.widgets module - Dashboard Widgets.

Tests cover:
- SessionStatusWidget rendering
- ScoresWidget with breakdown
- PhaseTimelineWidget from events
- AgentActivityWidget feed
- AnomalyAlertsWidget with severity sorting
- Dashboard composition and loading

Version: v0.10.0
Created: 2026-02-03
"""

import pytest
from datetime import datetime, UTC, timedelta
from unittest.mock import patch, MagicMock

from fs5.widgets import (
    SessionStatusWidget,
    ScoresWidget,
    PhaseTimelineWidget,
    AgentActivityWidget,
    AnomalyAlertsWidget,
    Dashboard,
)
from fs5.widgets.phase_timeline import PhaseInfo
from fs5.widgets.agent_activity import AgentInvocation
from fs5.widgets.anomaly_alerts import AnomalyAlert


class TestSessionStatusWidget:
    """Tests for SessionStatusWidget."""

    def test_from_session_creates_widget(self):
        """from_session creates widget from session dict."""
        session = {
            "session_id": "sess-123",
            "current_phase": "BUILD",
            "phase_entered_at": datetime.now(UTC).isoformat(),
            "status": "active",
            "started_at": datetime.now(UTC).isoformat(),
        }

        widget = SessionStatusWidget.from_session(session, "feat/test")

        assert widget.feature_name == "feat/test"
        assert widget.current_phase == "BUILD"
        assert widget.session_status == "active"

    def test_from_session_handles_none(self):
        """from_session handles None session."""
        widget = SessionStatusWidget.from_session(None, "feat/test")

        assert widget.feature_name == "feat/test"
        assert widget.current_phase == "NOT_STARTED"
        assert widget.session_status == "unknown"
        assert widget.time_in_phase_minutes == 0

    def test_calculates_time_in_phase(self):
        """Widget calculates time in current phase."""
        phase_entered = (datetime.now(UTC) - timedelta(minutes=45)).isoformat()
        session = {
            "session_id": "sess-123",
            "current_phase": "BUILD",
            "phase_entered_at": phase_entered,
            "status": "active",
        }

        widget = SessionStatusWidget.from_session(session, "feat/test")

        assert 44 <= widget.time_in_phase_minutes <= 46  # Allow 1 minute variance

    def test_to_dict(self):
        """to_dict returns proper dictionary."""
        widget = SessionStatusWidget(
            feature_name="feat/test",
            current_phase="VERIFY",
            time_in_phase_minutes=30,
            session_status="active",
        )

        result = widget.to_dict()

        assert result["feature_name"] == "feat/test"
        assert result["current_phase"] == "VERIFY"
        assert result["time_in_phase_minutes"] == 30
        assert result["session_status"] == "active"

    def test_render_console(self):
        """render_console produces formatted string."""
        widget = SessionStatusWidget(
            feature_name="feat/test",
            current_phase="BUILD",
            time_in_phase_minutes=15,
            session_status="active",
        )

        output = widget.render_console()

        assert "SESSION STATUS" in output
        assert "feat/test" in output
        assert "BUILD" in output
        assert "active" in output

    def test_render_html(self):
        """render_html produces HTML fragment."""
        widget = SessionStatusWidget(
            feature_name="feat/test",
            current_phase="VERIFY",
            time_in_phase_minutes=20,
            session_status="stuck",
        )

        output = widget.render_html()

        assert "widget" in output
        assert "feat/test" in output
        assert "VERIFY" in output
        assert "status-stuck" in output


class TestScoresWidget:
    """Tests for ScoresWidget."""

    def test_from_adherence_score(self):
        """from_adherence_score creates widget from score object."""
        from fs5.services.adherence import AdherenceScore, Penalty

        score = AdherenceScore(
            final_score=95,
            base_points=85,
            completion_bonus=20,
            penalties=[
                Penalty(type="redo", count=1, points_deducted=5, details="BUILD:1"),
                Penalty(type="skip", count=1, points_deducted=15, details="UNDERSTAND"),
            ],
            phases_completed=["PLAN", "BUILD", "VERIFY", "DEPLOY"],
        )

        widget = ScoresWidget.from_adherence_score(score)

        assert widget.adherence_score == 95
        assert widget.adherence_rating == "GOOD"
        assert widget.adherence_breakdown["base_points"] == 85
        assert widget.adherence_breakdown["completion_bonus"] == 20
        assert len(widget.adherence_breakdown["penalties"]) == 2

    def test_empty_creates_zero_widget(self):
        """empty() creates widget with all zeros."""
        widget = ScoresWidget.empty()

        assert widget.adherence_score == 0
        assert widget.adherence_rating == "POOR"
        assert widget.health_pulse == 0
        assert widget.test_total == 0

    def test_with_test_results(self):
        """Widget includes test results when provided."""
        from fs5.services.adherence import AdherenceScore

        score = AdherenceScore(final_score=100, base_points=100, completion_bonus=0)

        test_results = {
            "passed": 42,
            "total": 45,
            "pass_rate": 93.3,
        }

        widget = ScoresWidget.from_adherence_score(score, test_results=test_results)

        assert widget.test_passed == 42
        assert widget.test_total == 45
        assert widget.test_pass_rate == 93.3

    def test_render_console_shows_bars(self):
        """render_console shows progress bars."""
        widget = ScoresWidget(
            adherence_score=90,
            adherence_rating="GOOD",
            health_pulse=75,
            test_passed=38,
            test_total=40,
            test_pass_rate=95.0,
        )

        output = widget.render_console()

        assert "SCORES" in output
        assert "90" in output
        assert "GOOD" in output

    def test_render_html_includes_penalties(self):
        """render_html includes penalty list."""
        widget = ScoresWidget(
            adherence_score=80,
            adherence_rating="GOOD",
            adherence_breakdown={
                "base_points": 100,
                "completion_bonus": 0,
                "penalties": [
                    {"type": "redo", "count": 2, "deducted": 10, "details": "BUILD:2"},
                    {"type": "skip", "count": 1, "deducted": 15, "details": "UNDERSTAND"},
                ],
            },
        )

        output = widget.render_html()

        assert "penalty-list" in output or "penalty" in output
        assert "redo" in output
        assert "-10" in output


class TestPhaseTimelineWidget:
    """Tests for PhaseTimelineWidget."""

    def test_from_events(self):
        """from_events creates timeline from phase events."""
        events = [
            _make_phase_event("UNDERSTAND", "entered", "2026-02-03T14:00:00Z"),
            _make_phase_event("UNDERSTAND", "exited", "2026-02-03T14:25:00Z"),
            _make_phase_event("PLAN", "entered", "2026-02-03T14:30:00Z"),
            _make_phase_event("PLAN", "exited", "2026-02-03T15:00:00Z"),
            _make_phase_event("BUILD", "entered", "2026-02-03T15:05:00Z"),
            # BUILD not yet exited
        ]

        widget = PhaseTimelineWidget.from_events(events)

        assert len(widget.phases) == 5
        assert widget.current_phase == "BUILD"

        # Check phase statuses
        phase_statuses = {p.name: p.status for p in widget.phases}
        assert phase_statuses["UNDERSTAND"] == "completed"
        assert phase_statuses["PLAN"] == "completed"
        assert phase_statuses["BUILD"] == "current"
        assert phase_statuses["VERIFY"] == "pending"
        assert phase_statuses["DEPLOY"] == "pending"

    def test_calculates_durations(self):
        """Timeline calculates phase durations."""
        events = [
            _make_phase_event("UNDERSTAND", "entered", "2026-02-03T14:00:00Z"),
            _make_phase_event("UNDERSTAND", "exited", "2026-02-03T14:30:00Z"),  # 30 min
        ]

        widget = PhaseTimelineWidget.from_events(events)

        understand = next(p for p in widget.phases if p.name == "UNDERSTAND")
        assert understand.duration_minutes == 30

    def test_empty_creates_pending_phases(self):
        """empty() creates widget with all pending phases."""
        widget = PhaseTimelineWidget.empty()

        assert len(widget.phases) == 5
        assert all(p.status == "pending" for p in widget.phases)
        assert widget.current_phase is None

    def test_to_dict(self):
        """to_dict includes phase details."""
        widget = PhaseTimelineWidget(
            phases=[
                PhaseInfo(name="UNDERSTAND", status="completed", duration_minutes=25),
                PhaseInfo(name="PLAN", status="current", duration_minutes=15),
            ],
            current_phase="PLAN",
        )

        result = widget.to_dict()

        assert len(result["phases"]) == 2
        assert result["current_phase"] == "PLAN"
        assert result["phases"][0]["name"] == "UNDERSTAND"
        assert result["phases"][0]["status"] == "completed"

    def test_render_console_shows_timeline(self):
        """render_console shows visual timeline."""
        widget = PhaseTimelineWidget.empty()
        widget.phases[0].status = "completed"
        widget.phases[1].status = "current"

        output = widget.render_console()

        assert "PHASE TIMELINE" in output
        assert "UNDE" in output or "UNDERSTAND" in output


class TestAgentActivityWidget:
    """Tests for AgentActivityWidget."""

    def test_from_events(self):
        """from_events creates activity feed from agent events."""
        events = [
            _make_agent_event("code-reviewer", "Review code", "2026-02-03T14:00:00Z", "inv-1"),
            _make_agent_completed_event("inv-1", "success", "2026-02-03T14:05:00Z"),
            _make_agent_event("tester", "Run tests", "2026-02-03T14:10:00Z", "inv-2"),
        ]

        widget = AgentActivityWidget.from_events(events)

        assert len(widget.invocations) == 2

        # Most recent first
        assert widget.invocations[0].agent_name == "tester"
        assert widget.invocations[1].agent_name == "code-reviewer"

    def test_calculates_duration(self):
        """Widget calculates invocation duration."""
        events = [
            _make_agent_event("reviewer", "Review", "2026-02-03T14:00:00Z", "inv-1"),
            _make_agent_completed_event("inv-1", "success", "2026-02-03T14:05:00Z"),  # 5 min
        ]

        widget = AgentActivityWidget.from_events(events)

        assert widget.invocations[0].duration_seconds == 300  # 5 minutes

    def test_respects_max_display(self):
        """Widget respects max_display limit."""
        events = [
            _make_agent_event("agent1", "Task", f"2026-02-03T14:0{i}:00Z", f"inv-{i}")
            for i in range(10)
        ]

        widget = AgentActivityWidget.from_events(events, max_display=5)

        assert len(widget.invocations) == 5

    def test_empty_creates_empty_widget(self):
        """empty() creates widget with no invocations."""
        widget = AgentActivityWidget.empty()

        assert len(widget.invocations) == 0
        assert widget.max_display == 10

    def test_render_console_shows_activity(self):
        """render_console shows activity entries."""
        widget = AgentActivityWidget(
            invocations=[
                AgentInvocation(
                    agent_name="code-reviewer",
                    action="Review PR",
                    timestamp=datetime.now(UTC),
                    outcome="success",
                ),
            ],
        )

        output = widget.render_console()

        assert "AGENT ACTIVITY" in output
        # Agent name is truncated to 12 chars in console output
        assert "code-reviewe" in output  # "code-reviewer" truncated


class TestAnomalyAlertsWidget:
    """Tests for AnomalyAlertsWidget."""

    def test_from_anomalies(self):
        """from_anomalies creates widget from anomaly list."""
        from fs5.services.anomaly import Anomaly, Severity

        anomalies = [
            Anomaly(
                anomaly_id="a1",
                rule_id="qa_skipping",
                severity=Severity.CRITICAL,
                correlation_id="test",
                detected_at=datetime.now(UTC),
                description="QA skipped",
                details={},
            ),
            Anomaly(
                anomaly_id="a2",
                rule_id="stuck_session",
                severity=Severity.WARNING,
                correlation_id="test",
                detected_at=datetime.now(UTC),
                description="Session stuck",
                details={},
            ),
        ]

        widget = AnomalyAlertsWidget.from_anomalies(anomalies)

        assert len(widget.alerts) == 2
        assert widget.has_alerts()
        assert widget.has_critical()

    def test_sorts_by_severity(self):
        """Alerts are sorted by severity (CRITICAL first)."""
        from fs5.services.anomaly import Anomaly, Severity

        now = datetime.now(UTC)
        anomalies = [
            Anomaly(
                anomaly_id="a1",
                rule_id="info_rule",
                severity=Severity.INFO,
                correlation_id="test",
                detected_at=now,
                description="Info",
                details={},
            ),
            Anomaly(
                anomaly_id="a2",
                rule_id="critical_rule",
                severity=Severity.CRITICAL,
                correlation_id="test",
                detected_at=now,
                description="Critical",
                details={},
            ),
            Anomaly(
                anomaly_id="a3",
                rule_id="warning_rule",
                severity=Severity.WARNING,
                correlation_id="test",
                detected_at=now,
                description="Warning",
                details={},
            ),
        ]

        widget = AnomalyAlertsWidget.from_anomalies(anomalies)

        # CRITICAL should be first
        assert widget.alerts[0].severity == "CRITICAL"
        assert widget.alerts[1].severity == "WARNING"
        assert widget.alerts[2].severity == "INFO"

    def test_empty_creates_no_alerts(self):
        """empty() creates widget with no alerts."""
        widget = AnomalyAlertsWidget.empty()

        assert len(widget.alerts) == 0
        assert not widget.has_alerts()
        assert not widget.has_critical()

    def test_has_critical_false_when_no_critical(self):
        """has_critical returns False when no CRITICAL alerts."""
        widget = AnomalyAlertsWidget(
            alerts=[
                AnomalyAlert(
                    anomaly_id="a1",
                    rule_id="test",
                    severity="WARNING",
                    description="Warning alert",
                    detected_at=datetime.now(UTC),
                ),
            ],
        )

        assert not widget.has_critical()

    def test_render_console_shows_alerts(self):
        """render_console shows alert entries."""
        widget = AnomalyAlertsWidget(
            alerts=[
                AnomalyAlert(
                    anomaly_id="a1",
                    rule_id="qa_skipping",
                    severity="CRITICAL",
                    description="DEPLOY without VERIFY",
                    detected_at=datetime.now(UTC),
                    details={"from_stage": "BUILD"},
                ),
            ],
        )

        output = widget.render_console()

        assert "ANOMALY ALERTS" in output
        assert "CRIT" in output

    def test_render_html_has_critical_class(self):
        """render_html has special class for critical alerts."""
        widget = AnomalyAlertsWidget(
            alerts=[
                AnomalyAlert(
                    anomaly_id="a1",
                    rule_id="test",
                    severity="CRITICAL",
                    description="Critical!",
                    detected_at=datetime.now(UTC),
                ),
            ],
        )

        output = widget.render_html()

        assert "has-critical" in output
        assert "severity-critical" in output


class TestDashboard:
    """Tests for Dashboard class."""

    def test_empty_creates_all_widgets(self):
        """empty() creates dashboard with all empty widgets."""
        dashboard = Dashboard.empty("feat/test")

        assert dashboard.session_status is not None
        assert dashboard.scores is not None
        assert dashboard.phase_timeline is not None
        assert dashboard.agent_activity is not None
        assert dashboard.anomaly_alerts is not None
        assert dashboard.generated_at is not None

    def test_to_dict(self):
        """to_dict includes all widgets."""
        dashboard = Dashboard.empty("feat/test")
        result = dashboard.to_dict()

        assert "session_status" in result
        assert "scores" in result
        assert "phase_timeline" in result
        assert "agent_activity" in result
        assert "anomaly_alerts" in result
        assert "generated_at" in result

    def test_to_json(self):
        """to_json produces valid JSON."""
        import json

        dashboard = Dashboard.empty("feat/test")
        json_str = dashboard.to_json()

        # Should not raise
        parsed = json.loads(json_str)
        assert parsed["session_status"]["feature_name"] == "feat/test"

    def test_render_console(self):
        """render_console produces complete dashboard."""
        dashboard = Dashboard.empty("feat/test")
        output = dashboard.render_console()

        assert "FS5 METRICS DASHBOARD" in output
        assert "SESSION STATUS" in output
        assert "SCORES" in output
        assert "PHASE TIMELINE" in output
        assert "AGENT ACTIVITY" in output
        assert "ANOMALY ALERTS" in output

    def test_render_html(self):
        """render_html produces complete HTML page."""
        dashboard = Dashboard.empty("feat/test")
        output = dashboard.render_html()

        assert "<!DOCTYPE html>" in output
        assert "FS5 Metrics Dashboard" in output
        assert "dashboard-grid" in output

    @patch("fs5.services.get_session_status")
    @patch("fs5.services.calculate_adherence_score")
    @patch("fs5.services.get_active_anomalies")
    @patch("fs5.core.db.get_connection")
    def test_load_integrates_all_data(
        self,
        mock_conn,
        mock_anomalies,
        mock_score,
        mock_session
    ):
        """Dashboard.load() integrates data from all sources."""
        from fs5.services.adherence import AdherenceScore

        mock_session.return_value = {
            "session_id": "sess-1",
            "current_phase": "BUILD",
            "phase_entered_at": datetime.now(UTC).isoformat(),
            "status": "active",
        }

        mock_score.return_value = AdherenceScore(
            final_score=100,
            base_points=100,
            completion_bonus=0,
        )

        mock_anomalies.return_value = []

        # Mock DB connection
        mock_context = MagicMock()
        mock_context.execute.return_value.fetchall.return_value = []
        mock_conn.return_value.__enter__ = MagicMock(return_value=mock_context)
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)

        dashboard = Dashboard.load("feat/test")

        assert dashboard.session_status.feature_name == "feat/test"
        assert dashboard.session_status.current_phase == "BUILD"
        assert dashboard.scores.adherence_score == 100

    def test_save_html(self, tmp_path):
        """save_html writes HTML file."""
        dashboard = Dashboard.empty("feat/test")
        output_path = tmp_path / "dashboard.html"

        dashboard.save_html(output_path)

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content


# --- Helper Functions ---

def _make_phase_event(phase: str, event_type: str, timestamp: str) -> dict:
    """Create a phase entered/exited event."""
    return {
        "timestamp": timestamp,
        "event_type": f"workflow.phase_{event_type}",
        "payload": {"phase": phase},
    }


def _make_agent_event(
    agent_type: str,
    action: str,
    timestamp: str,
    invocation_id: str
) -> dict:
    """Create an agent invoked event."""
    return {
        "timestamp": timestamp,
        "event_type": "agent.invoked",
        "payload": {
            "agent_type": agent_type,
            "action": action,
            "invocation_id": invocation_id,
        },
    }


def _make_agent_completed_event(
    invocation_id: str,
    outcome: str,
    timestamp: str
) -> dict:
    """Create an agent completed event."""
    return {
        "timestamp": timestamp,
        "event_type": "agent.completed",
        "payload": {
            "invocation_id": invocation_id,
            "outcome": outcome,
        },
    }
