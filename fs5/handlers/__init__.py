"""FS5 Handlers Module.

Contains event handlers and processors for the metrics system.

Version: v0.10.0
Created: 2026-02-03
"""

from fs5.handlers.kanban_handler import (
    handle_kanban_transition,
    register_handler,
    unregister_handler,
)

__all__ = [
    "handle_kanban_transition",
    "register_handler",
    "unregister_handler",
]
