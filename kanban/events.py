"""
FS2 Transition Event Hook.

This module provides a hook system for FS5 to receive real-time
notifications when workflow phase transitions occur.

Version: v0.10.0
Created: 2026-02-03
"""

from typing import Protocol, Any


class TransitionEventHandler(Protocol):
    """Protocol for transition event handlers."""

    def __call__(
        self,
        task_id: str,
        from_stage: str,
        to_stage: str,
        result: dict[str, Any],
        checklist: dict[str, Any],
    ) -> None:
        """
        Handle a transition event.

        Args:
            task_id: The task being transitioned
            from_stage: Previous stage (e.g., "PLAN")
            to_stage: New stage (e.g., "BUILD")
            result: Transition result object
            checklist: Checklist state at transition time
        """
        ...


# Module-level handler registry
_handlers: list[TransitionEventHandler] = []


def register_transition_handler(handler: TransitionEventHandler) -> None:
    """
    Register a handler to receive transition events.

    FS5 calls this during initialization to receive real-time events.
    Multiple handlers can be registered.
    """
    if handler not in _handlers:
        _handlers.append(handler)


def unregister_transition_handler(handler: TransitionEventHandler) -> None:
    """Remove a previously registered handler."""
    if handler in _handlers:
        _handlers.remove(handler)


def emit_transition_event(
    task_id: str,
    from_stage: str,
    to_stage: str,
    result: dict[str, Any],
    checklist: dict[str, Any],
) -> None:
    """
    Emit a transition event to all registered handlers.

    Called by transition_task() in transitions.py after successful transitions.
    Handlers are called synchronously but errors are caught to prevent
    breaking the transition flow.
    """
    for handler in _handlers:
        try:
            handler(task_id, from_stage, to_stage, result, checklist)
        except Exception:
            # Never fail the transition due to handler errors
            # Consider: Add logging here
            pass


def get_handler_count() -> int:
    """Get the number of registered handlers (for testing)."""
    return len(_handlers)


def clear_handlers() -> None:
    """Clear all handlers (for testing)."""
    _handlers.clear()
