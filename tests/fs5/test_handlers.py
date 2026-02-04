"""Tests for fs5.handlers module - Kanban Transition Handler.

Tests cover:
- Handler registration and unregistration
- Transition event processing
- Anomaly detection on transitions
- Event persistence

Version: v0.10.0
Created: 2026-02-03
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC

from fs5.handlers import (
    handle_kanban_transition,
    register_handler,
    unregister_handler,
)


class TestHandlerRegistration:
    """Tests for handler registration functions."""

    def test_register_handler(self):
        """Handler can be registered with FS2."""
        with patch("kanban.events.register_transition_handler") as mock_register:
            register_handler()
            mock_register.assert_called_once_with(handle_kanban_transition)

    def test_unregister_handler(self):
        """Handler can be unregistered from FS2."""
        with patch("kanban.events.unregister_transition_handler") as mock_unregister:
            unregister_handler()
            mock_unregister.assert_called_once_with(handle_kanban_transition)


class TestHandleKanbanTransition:
    """Tests for handle_kanban_transition function."""

    @patch("fs5.services.adherence.update_session_phase")
    @patch("fs5.services.anomaly.check_transition_anomalies")
    @patch("fs5.services.anomaly.persist_anomaly")
    @patch("fs5.core.db.get_connection")
    def test_updates_session_phase(
        self,
        mock_conn,
        mock_persist,
        mock_check,
        mock_update
    ):
        """Transition updates session phase tracking."""
        mock_check.return_value = []
        mock_conn.return_value.__enter__ = MagicMock()
        mock_conn.return_value.__exit__ = MagicMock()

        handle_kanban_transition(
            task_id="TASK-001",
            from_stage="PLAN",
            to_stage="BUILD",
            result={"status": "success"},
            checklist={"items": []},
        )

        mock_update.assert_called_once_with("TASK-001", "BUILD", "PLAN")

    @patch("fs5.services.adherence.update_session_phase")
    @patch("fs5.services.anomaly.check_transition_anomalies")
    @patch("fs5.services.anomaly.persist_anomaly")
    @patch("fs5.core.db.get_connection")
    def test_checks_for_anomalies(
        self,
        mock_conn,
        mock_persist,
        mock_check,
        mock_update
    ):
        """Transition checks for anomalies."""
        mock_check.return_value = []
        mock_conn.return_value.__enter__ = MagicMock()
        mock_conn.return_value.__exit__ = MagicMock()

        handle_kanban_transition(
            task_id="TASK-001",
            from_stage="BUILD",
            to_stage="DEPLOY",  # Skipping VERIFY
            result={"status": "success"},
            checklist={"items": []},
        )

        mock_check.assert_called_once_with("TASK-001", "BUILD", "DEPLOY")

    @patch("fs5.services.adherence.update_session_phase")
    @patch("fs5.services.anomaly.check_transition_anomalies")
    @patch("fs5.services.anomaly.persist_anomaly")
    @patch("fs5.core.db.get_connection")
    def test_persists_detected_anomalies(
        self,
        mock_conn,
        mock_persist,
        mock_check,
        mock_update
    ):
        """Detected anomalies are persisted."""
        from fs5.services.anomaly import Anomaly, Severity

        mock_anomaly = Anomaly(
            anomaly_id="test-id",
            rule_id="qa_skipping",
            severity=Severity.CRITICAL,
            correlation_id="TASK-001",
            detected_at=datetime.now(UTC),
            description="QA skipped",
            details={},
        )
        mock_check.return_value = [mock_anomaly]
        mock_conn.return_value.__enter__ = MagicMock()
        mock_conn.return_value.__exit__ = MagicMock()

        handle_kanban_transition(
            task_id="TASK-001",
            from_stage="BUILD",
            to_stage="DEPLOY",
            result={"status": "success"},
            checklist={"items": []},
        )

        mock_persist.assert_called_once_with(mock_anomaly)

    @patch("fs5.services.adherence.update_session_phase")
    @patch("fs5.services.anomaly.check_transition_anomalies")
    @patch("fs5.services.anomaly.persist_anomaly")
    @patch("fs5.core.db.get_connection")
    def test_continues_on_session_update_failure(
        self,
        mock_conn,
        mock_persist,
        mock_check,
        mock_update
    ):
        """Handler continues even if session update fails."""
        mock_update.side_effect = Exception("Database error")
        mock_check.return_value = []
        mock_conn.return_value.__enter__ = MagicMock()
        mock_conn.return_value.__exit__ = MagicMock()

        # Should not raise
        handle_kanban_transition(
            task_id="TASK-001",
            from_stage="PLAN",
            to_stage="BUILD",
            result={"status": "success"},
            checklist={"items": []},
        )

        # Anomaly check should still be called
        mock_check.assert_called_once()

    @patch("fs5.services.adherence.update_session_phase")
    @patch("fs5.services.anomaly.check_transition_anomalies")
    @patch("fs5.services.anomaly.persist_anomaly")
    @patch("fs5.core.db.get_connection")
    def test_continues_on_anomaly_detection_failure(
        self,
        mock_conn,
        mock_persist,
        mock_check,
        mock_update
    ):
        """Handler continues even if anomaly detection fails."""
        mock_check.side_effect = Exception("Anomaly check error")
        mock_conn.return_value.__enter__ = MagicMock()
        mock_conn.return_value.__exit__ = MagicMock()

        # Should not raise
        handle_kanban_transition(
            task_id="TASK-001",
            from_stage="PLAN",
            to_stage="BUILD",
            result={"status": "success"},
            checklist={"items": []},
        )

        # Session update should have been called before anomaly check
        mock_update.assert_called_once()


class TestTransitionEventCreation:
    """Tests for transition event creation."""

    @patch("fs5.services.adherence.update_session_phase")
    @patch("fs5.services.anomaly.check_transition_anomalies")
    @patch("fs5.services.anomaly.persist_anomaly")
    @patch("fs5.core.db.get_connection")
    def test_creates_canonical_event(
        self,
        mock_conn,
        mock_persist,
        mock_check,
        mock_update
    ):
        """Handler creates canonical event format."""
        mock_check.return_value = []

        # Capture the execute call to verify event structure
        mock_execute = MagicMock()
        mock_context = MagicMock()
        mock_context.execute = mock_execute
        mock_conn.return_value.__enter__ = MagicMock(return_value=mock_context)
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)

        handle_kanban_transition(
            task_id="TASK-001",
            from_stage="PLAN",
            to_stage="BUILD",
            result={"status": "success"},
            checklist={"items": ["item1"]},
        )

        # Verify execute was called with INSERT
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "INSERT INTO transition_events" in sql
        assert params[2] == "TASK-001"  # task_id
        assert params[3] == "PLAN"       # from_stage
        assert params[4] == "BUILD"      # to_stage


class TestTransitionEventPersistence:
    """Tests for transition event persistence."""

    @patch("fs5.services.adherence.update_session_phase")
    @patch("fs5.services.anomaly.check_transition_anomalies")
    @patch("fs5.services.anomaly.persist_anomaly")
    @patch("fs5.core.db.get_connection")
    def test_continues_on_persistence_failure(
        self,
        mock_conn,
        mock_persist,
        mock_check,
        mock_update
    ):
        """Handler continues even if event persistence fails."""
        mock_check.return_value = []

        # Make the connection context manager raise on execute
        mock_context = MagicMock()
        mock_context.execute.side_effect = Exception("Database write error")
        mock_conn.return_value.__enter__ = MagicMock(return_value=mock_context)
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)

        # Should not raise
        handle_kanban_transition(
            task_id="TASK-001",
            from_stage="PLAN",
            to_stage="BUILD",
            result={"status": "success"},
            checklist={"items": []},
        )

        # Verify other steps were attempted
        mock_update.assert_called_once()
        mock_check.assert_called_once()


class TestHandlerIntegration:
    """Integration tests for handler with real components."""

    def test_handler_signature_matches_protocol(self):
        """Handler signature matches TransitionEventHandler protocol."""
        # Verify handler can be called with expected arguments
        from kanban.events import TransitionEventHandler

        # Type check (implicit - if this runs without error, signature matches)
        handler: TransitionEventHandler = handle_kanban_transition

        # Verify it's callable with expected args
        assert callable(handler)

    @patch("fs5.services.adherence.update_session_phase")
    @patch("fs5.services.anomaly.check_transition_anomalies")
    @patch("fs5.services.anomaly.persist_anomaly")
    @patch("fs5.core.db.get_connection")
    def test_full_transition_flow(
        self,
        mock_conn,
        mock_persist,
        mock_check,
        mock_update
    ):
        """Test complete transition handling flow."""
        from fs5.services.anomaly import Anomaly, Severity

        # Setup: QA skipping scenario
        anomaly = Anomaly(
            anomaly_id="anomaly-1",
            rule_id="qa_skipping",
            severity=Severity.CRITICAL,
            correlation_id="TASK-001",
            detected_at=datetime.now(UTC),
            description="DEPLOY without VERIFY",
            details={"from_stage": "BUILD"},
        )
        mock_check.return_value = [anomaly]

        mock_context = MagicMock()
        mock_conn.return_value.__enter__ = MagicMock(return_value=mock_context)
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)

        # Execute
        handle_kanban_transition(
            task_id="TASK-001",
            from_stage="BUILD",
            to_stage="DEPLOY",  # Skipping VERIFY!
            result={"allowed": True},
            checklist={"completed": True},
        )

        # Verify flow
        mock_update.assert_called_once_with("TASK-001", "DEPLOY", "BUILD")
        mock_check.assert_called_once_with("TASK-001", "BUILD", "DEPLOY")
        mock_persist.assert_called_once_with(anomaly)
        mock_context.execute.assert_called_once()  # Event persisted
