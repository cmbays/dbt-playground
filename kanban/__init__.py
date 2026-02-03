"""
Kanban Workflow Engine for dbt-playground.

This module implements workflow discipline enforcement through:
- Per-ticket checklists (Issue #154)
- Transition guards (Issue #155)
- WIP tracking (Issue #164)

Version: 1.0
Epic: #144 (Kanban Workflow Engine)
"""

from .transitions import (
    transition_task,
    register_qa_gate_hook,
    TransitionResult,
    Stage,
)
from .compliance import calculate_compliance_score, get_rating
from .checklist import create_checklist, validate_checklist, mark_item_complete
from .wip import get_wip_counts, update_wip_counts
from .config import load_config

__version__ = "1.0.0"
__all__ = [
    # Transitions
    "transition_task",
    "register_qa_gate_hook",
    "TransitionResult",
    "Stage",
    # Compliance
    "calculate_compliance_score",
    "get_rating",
    # Checklist
    "create_checklist",
    "validate_checklist",
    "mark_item_complete",
    # WIP
    "get_wip_counts",
    "update_wip_counts",
    # Config
    "load_config",
]
