"""Tests for kanban.events module - Event Hook System.

Tests cover:
- Handler registration
- Handler unregistration
- Event emission to multiple handlers
- Error handling in handlers

Version: v0.10.0
Created: 2026-02-03
"""

import pytest
from unittest.mock import MagicMock

from kanban.events import (
    register_transition_handler,
    unregister_transition_handler,
    emit_transition_event,
    get_handler_count,
    clear_handlers,
)


class TestHandlerRegistration:
    """Tests for handler registration."""

    def setup_method(self):
        """Clear handlers before each test."""
        clear_handlers()

    def teardown_method(self):
        """Clear handlers after each test."""
        clear_handlers()

    def test_register_adds_handler(self):
        """Registering adds handler to registry."""
        handler = MagicMock()

        register_transition_handler(handler)

        assert get_handler_count() == 1

    def test_register_multiple_handlers(self):
        """Can register multiple handlers."""
        handler1 = MagicMock()
        handler2 = MagicMock()

        register_transition_handler(handler1)
        register_transition_handler(handler2)

        assert get_handler_count() == 2

    def test_register_same_handler_twice_no_duplicate(self):
        """Registering same handler twice does not create duplicate."""
        handler = MagicMock()

        register_transition_handler(handler)
        register_transition_handler(handler)

        assert get_handler_count() == 1


class TestHandlerUnregistration:
    """Tests for handler unregistration."""

    def setup_method(self):
        """Clear handlers before each test."""
        clear_handlers()

    def teardown_method(self):
        """Clear handlers after each test."""
        clear_handlers()

    def test_unregister_removes_handler(self):
        """Unregistering removes handler from registry."""
        handler = MagicMock()
        register_transition_handler(handler)

        unregister_transition_handler(handler)

        assert get_handler_count() == 0

    def test_unregister_nonexistent_handler_no_error(self):
        """Unregistering non-existent handler does not raise."""
        handler = MagicMock()

        # Should not raise
        unregister_transition_handler(handler)

        assert get_handler_count() == 0

    def test_unregister_only_removes_specified_handler(self):
        """Unregistering removes only the specified handler."""
        handler1 = MagicMock()
        handler2 = MagicMock()
        register_transition_handler(handler1)
        register_transition_handler(handler2)

        unregister_transition_handler(handler1)

        assert get_handler_count() == 1


class TestEventEmission:
    """Tests for event emission."""

    def setup_method(self):
        """Clear handlers before each test."""
        clear_handlers()

    def teardown_method(self):
        """Clear handlers after each test."""
        clear_handlers()

    def test_emit_calls_registered_handler(self):
        """Emit calls registered handler with correct arguments."""
        handler = MagicMock()
        register_transition_handler(handler)

        emit_transition_event(
            task_id="TASK-001",
            from_stage="PLAN",
            to_stage="BUILD",
            result={"status": "success"},
            checklist={"items": ["item1"]},
        )

        handler.assert_called_once_with(
            "TASK-001",
            "PLAN",
            "BUILD",
            {"status": "success"},
            {"items": ["item1"]},
        )

    def test_emit_calls_all_handlers(self):
        """Emit calls all registered handlers."""
        handler1 = MagicMock()
        handler2 = MagicMock()
        handler3 = MagicMock()

        register_transition_handler(handler1)
        register_transition_handler(handler2)
        register_transition_handler(handler3)

        emit_transition_event(
            task_id="TASK-001",
            from_stage="PLAN",
            to_stage="BUILD",
            result={},
            checklist={},
        )

        handler1.assert_called_once()
        handler2.assert_called_once()
        handler3.assert_called_once()

    def test_emit_no_handlers_no_error(self):
        """Emit with no handlers does not raise."""
        # Should not raise
        emit_transition_event(
            task_id="TASK-001",
            from_stage="PLAN",
            to_stage="BUILD",
            result={},
            checklist={},
        )


class TestErrorHandling:
    """Tests for error handling in event emission."""

    def setup_method(self):
        """Clear handlers before each test."""
        clear_handlers()

    def teardown_method(self):
        """Clear handlers after each test."""
        clear_handlers()

    def test_handler_exception_does_not_propagate(self):
        """Exception in handler does not propagate to caller."""
        handler = MagicMock(side_effect=Exception("Handler error"))
        register_transition_handler(handler)

        # Should not raise
        emit_transition_event(
            task_id="TASK-001",
            from_stage="PLAN",
            to_stage="BUILD",
            result={},
            checklist={},
        )

    def test_handler_exception_does_not_stop_other_handlers(self):
        """Exception in one handler does not stop other handlers."""
        failing_handler = MagicMock(side_effect=Exception("Handler error"))
        succeeding_handler = MagicMock()

        register_transition_handler(failing_handler)
        register_transition_handler(succeeding_handler)

        emit_transition_event(
            task_id="TASK-001",
            from_stage="PLAN",
            to_stage="BUILD",
            result={},
            checklist={},
        )

        # Both handlers should have been called
        failing_handler.assert_called_once()
        succeeding_handler.assert_called_once()


class TestClearHandlers:
    """Tests for clear_handlers utility."""

    def test_clear_removes_all_handlers(self):
        """clear_handlers removes all registered handlers."""
        handler1 = MagicMock()
        handler2 = MagicMock()

        register_transition_handler(handler1)
        register_transition_handler(handler2)

        clear_handlers()

        assert get_handler_count() == 0

    def test_clear_on_empty_no_error(self):
        """clear_handlers on empty registry does not raise."""
        clear_handlers()  # Already empty
        clear_handlers()  # Still should not raise

        assert get_handler_count() == 0


class TestGetHandlerCount:
    """Tests for get_handler_count utility."""

    def setup_method(self):
        """Clear handlers before each test."""
        clear_handlers()

    def teardown_method(self):
        """Clear handlers after each test."""
        clear_handlers()

    def test_returns_zero_when_empty(self):
        """Returns 0 when no handlers registered."""
        assert get_handler_count() == 0

    def test_returns_correct_count(self):
        """Returns correct count of registered handlers."""
        for i in range(5):
            register_transition_handler(MagicMock())

        assert get_handler_count() == 5


class TestHandlerProtocol:
    """Tests for handler protocol compliance."""

    def setup_method(self):
        """Clear handlers before each test."""
        clear_handlers()

    def teardown_method(self):
        """Clear handlers after each test."""
        clear_handlers()

    def test_function_as_handler(self):
        """Plain function can be used as handler."""
        call_log = []

        def handler(task_id, from_stage, to_stage, result, checklist):
            call_log.append((task_id, from_stage, to_stage))

        register_transition_handler(handler)

        emit_transition_event(
            task_id="TASK-001",
            from_stage="PLAN",
            to_stage="BUILD",
            result={},
            checklist={},
        )

        assert call_log == [("TASK-001", "PLAN", "BUILD")]

    def test_callable_object_as_handler(self):
        """Callable object can be used as handler."""

        class CallableHandler:
            def __init__(self):
                self.calls = []

            def __call__(self, task_id, from_stage, to_stage, result, checklist):
                self.calls.append((task_id, to_stage))

        handler = CallableHandler()
        register_transition_handler(handler)

        emit_transition_event(
            task_id="TASK-002",
            from_stage="BUILD",
            to_stage="VERIFY",
            result={},
            checklist={},
        )

        assert handler.calls == [("TASK-002", "VERIFY")]

    def test_method_as_handler(self):
        """Instance method can be used as handler."""

        class EventTracker:
            def __init__(self):
                self.events = []

            def on_transition(self, task_id, from_stage, to_stage, result, checklist):
                self.events.append({"task": task_id, "to": to_stage})

        tracker = EventTracker()
        register_transition_handler(tracker.on_transition)

        emit_transition_event(
            task_id="TASK-003",
            from_stage="VERIFY",
            to_stage="DEPLOY",
            result={},
            checklist={},
        )

        assert tracker.events == [{"task": "TASK-003", "to": "DEPLOY"}]
