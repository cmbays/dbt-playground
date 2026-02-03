"""
Kanban Workflow Transition Guards - Procedural Implementation (Beta Design).

This module implements workflow transition validation using explicit
procedural code. All logic is visible and traceable.

Issue: #155 (Implement transition guards in Supervisor)
Epic: #144 (Kanban Workflow Engine)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Protocol
import logging

from .config import (
    load_config,
    get_enforcement_mode,
    get_wip_limit,
    is_critical_transition,
    get_skip_penalty,
)
from .checklist import (
    is_stage_complete,
    get_incomplete_items,
    mark_stage_complete,
    start_stage,
    add_skip_record,
    add_bypass_record,
)

logger = logging.getLogger("kanban.transitions")


class Stage(Enum):
    """Workflow stages."""
    UNDERSTAND = "understand"
    PLAN = "plan"
    BUILD = "build"
    VERIFY = "verify"
    DEPLOY = "deploy"
    BLOCKED = "blocked"


# Explicit transition matrix - easy to read and modify
VALID_TRANSITIONS: dict[Stage, list[Stage]] = {
    Stage.UNDERSTAND: [Stage.PLAN, Stage.BLOCKED],
    Stage.PLAN: [Stage.BUILD, Stage.BLOCKED],
    Stage.BUILD: [Stage.VERIFY, Stage.BLOCKED],
    Stage.VERIFY: [Stage.DEPLOY, Stage.BLOCKED],
    Stage.DEPLOY: [],  # Terminal state
    Stage.BLOCKED: [Stage.UNDERSTAND, Stage.PLAN, Stage.BUILD, Stage.VERIFY, Stage.DEPLOY],
}

# Stage sequence for skip detection
STAGE_SEQUENCE: list[Stage] = [
    Stage.UNDERSTAND,
    Stage.PLAN,
    Stage.BUILD,
    Stage.VERIFY,
    Stage.DEPLOY,
]


@dataclass
class TransitionResult:
    """Result of a transition attempt."""
    success: bool
    message: str
    warnings: list[str] = field(default_factory=list)
    blocked_by: str | None = None
    sage_invoked: bool = False


class QAGateResult(Protocol):
    """Protocol for QA gate results (FS3 compatibility)."""
    passed: bool
    message: str
    missing_artifacts: list[str] | None


# FS3 QA Gate Hooks - FS3 registers their functions here
_qa_gate_hooks: list[Callable] = []


def register_qa_gate_hook(hook: Callable) -> None:
    """
    Register a QA gate hook function.

    FS3 calls this to add their QA validation. The hook is called
    during transition validation for BUILD->VERIFY and VERIFY->DEPLOY.

    Args:
        hook: Function with signature:
              (task_id: str, from_stage: str, to_stage: str) -> QAGateResult

    Example:
        >>> def my_qa_check(task_id, from_stage, to_stage):
        ...     return QAGateResult(passed=True, message="OK")
        >>> register_qa_gate_hook(my_qa_check)
    """
    _qa_gate_hooks.append(hook)
    logger.info(f"Registered QA gate hook: {hook.__name__}")


def transition_task(
    task_id: str,
    from_stage: str,
    to_stage: str,
    checklist: dict,
    bypass_reason: str | None = None,
    current_user: str = "system"
) -> TransitionResult:
    """
    Execute a workflow transition with full validation.

    This is the main entry point for all transitions. It runs guards
    in sequence and returns success or failure with details.

    Args:
        task_id: The task identifier (e.g., "TASK-100").
        from_stage: Current stage name.
        to_stage: Target stage name.
        checklist: Task's workflow checklist dictionary.
        bypass_reason: Optional reason for bypassing guards.
        current_user: User/agent performing the transition.

    Returns:
        TransitionResult with success status and details.

    Example:
        >>> result = transition_task(
        ...     "TASK-100", "plan", "build",
        ...     checklist=my_checklist
        ... )
        >>> if result.success:
        ...     print("Transition complete")
    """
    # Convert to enums
    try:
        from_enum = Stage(from_stage.lower())
        to_enum = Stage(to_stage.lower())
    except ValueError as e:
        return TransitionResult(
            success=False,
            message=f"Invalid stage: {e}",
            blocked_by="stage_validation"
        )

    all_warnings: list[str] = []
    sage_invoked = False
    enforcement_mode = get_enforcement_mode()

    # ─────────────────────────────────────────────────────────
    # GUARD 1: Validate transition is allowed
    # ─────────────────────────────────────────────────────────
    if to_enum not in VALID_TRANSITIONS.get(from_enum, []):
        return TransitionResult(
            success=False,
            message=f"Invalid transition: {from_stage} -> {to_stage}",
            blocked_by="valid_transition"
        )

    # ─────────────────────────────────────────────────────────
    # GUARD 2: Check for stage skip
    # ─────────────────────────────────────────────────────────
    skip_result = _check_skip(
        from_enum, to_enum, task_id, checklist, bypass_reason, current_user
    )
    if skip_result is not None:
        if not skip_result.success:
            return skip_result
        # Skip was allowed - collect warnings
        all_warnings.extend(skip_result.warnings)
        sage_invoked = skip_result.sage_invoked

    # ─────────────────────────────────────────────────────────
    # GUARD 3: Validate checklist completion
    # ─────────────────────────────────────────────────────────
    if from_enum != Stage.BLOCKED:
        checklist_result = _validate_checklist(
            checklist, from_enum, bypass_reason, current_user
        )
        if not checklist_result.success:
            if enforcement_mode == "hard":
                return checklist_result
            else:
                all_warnings.append(f"SOFT: {checklist_result.message}")
        all_warnings.extend(checklist_result.warnings)

    # ─────────────────────────────────────────────────────────
    # GUARD 4: Check WIP limit
    # ─────────────────────────────────────────────────────────
    if to_enum != Stage.BLOCKED:
        wip_result = _check_wip_limit(
            to_enum, checklist, bypass_reason, current_user
        )
        if not wip_result.success:
            if enforcement_mode == "hard":
                return wip_result
            else:
                all_warnings.append(f"SOFT: {wip_result.message}")
        all_warnings.extend(wip_result.warnings)

    # ─────────────────────────────────────────────────────────
    # GUARD 5: Run FS3 QA gates (if registered)
    # ─────────────────────────────────────────────────────────
    for qa_hook in _qa_gate_hooks:
        try:
            qa_result = qa_hook(task_id, from_stage, to_stage)
            if not qa_result.passed:
                if bypass_reason:
                    all_warnings.append(f"QA bypassed: {qa_result.message}")
                    add_bypass_record(
                        checklist, "qa_gate", to_stage, bypass_reason, current_user
                    )
                else:
                    return TransitionResult(
                        success=False,
                        message=f"QA gate failed: {qa_result.message}",
                        blocked_by="qa_gate"
                    )
        except (KeyboardInterrupt, SystemExit):
            raise  # Re-raise critical signals
        except Exception as e:
            logger.warning(f"QA hook error: {e}")
            all_warnings.append(f"QA hook warning: {e}")

    # ─────────────────────────────────────────────────────────
    # All guards passed - execute transition
    # ─────────────────────────────────────────────────────────
    _execute_transition(checklist, from_enum, to_enum, current_user)

    logger.info(f"TRANSITION: {task_id} {from_stage} -> {to_stage}")

    return TransitionResult(
        success=True,
        message=f"Transitioned {task_id}: {from_stage} -> {to_stage}",
        warnings=all_warnings,
        sage_invoked=sage_invoked
    )


def _check_skip(
    from_stage: Stage,
    to_stage: Stage,
    task_id: str,
    checklist: dict,
    bypass_reason: str | None,
    current_user: str
) -> TransitionResult | None:
    """
    Check if transition would skip a stage.

    Returns None if no skip detected, otherwise returns a TransitionResult.
    """
    if to_stage == Stage.BLOCKED:
        return None  # Can always go to BLOCKED

    try:
        from_idx = STAGE_SEQUENCE.index(from_stage)
        to_idx = STAGE_SEQUENCE.index(to_stage)
    except ValueError:
        return None  # BLOCKED not in sequence

    # Check if skipping
    if to_idx - from_idx <= 1:
        return None  # Normal progression

    # Collect all skipped stages
    skipped_stages = STAGE_SEQUENCE[from_idx + 1:to_idx]
    skipped_names = [s.value for s in skipped_stages]

    # Check if this is a critical skip
    is_critical = is_critical_transition(from_stage.value, to_stage.value)

    if is_critical and not bypass_reason:
        return TransitionResult(
            success=False,
            message=f"Critical skip blocked. Skipped stages: {skipped_names}. "
                    f"Provide bypass_reason to override.",
            blocked_by="skip_detection"
        )

    # Log each skipped stage to checklist
    for skipped_stage in skipped_stages:
        add_skip_record(
            checklist,
            from_stage.value,
            to_stage.value,
            skipped_stage.value,
            bypass_reason
        )

    # Reduce compliance score (penalty per skipped stage)
    penalty_per_skip = get_skip_penalty()
    total_penalty = penalty_per_skip * len(skipped_stages)
    checklist["compliance"]["score"] = max(
        0, checklist["compliance"]["score"] - total_penalty
    )

    # TODO: Invoke Sage for learning extraction
    # sage: Extract learnings from workflow skip...

    return TransitionResult(
        success=True,
        message="Skip allowed",
        warnings=[
            f"WARNING: Skipped stages {skipped_names}. "
            f"Compliance score reduced by {total_penalty} ({penalty_per_skip} × {len(skipped_stages)})."
        ],
        sage_invoked=True  # Will invoke Sage
    )


def _validate_checklist(
    checklist: dict,
    stage: Stage,
    bypass_reason: str | None,
    current_user: str
) -> TransitionResult:
    """
    Validate all required checklist items are complete for a stage.
    """
    incomplete = get_incomplete_items(checklist, stage.value)

    if not incomplete:
        return TransitionResult(success=True, message="Checklist complete")

    if bypass_reason:
        add_bypass_record(
            checklist, "checklist_incomplete", stage.value, bypass_reason, current_user
        )
        return TransitionResult(
            success=True,
            message="Checklist bypassed",
            warnings=[f"Bypassed incomplete items: {incomplete}"]
        )

    return TransitionResult(
        success=False,
        message=f"Cannot transition from {stage.value}. "
                f"Incomplete items: {incomplete}",
        blocked_by="checklist_validation"
    )


def _check_wip_limit(
    target_stage: Stage,
    checklist: dict,
    bypass_reason: str | None,
    current_user: str
) -> TransitionResult:
    """
    Check WIP limit for target stage.
    """
    # Import here to avoid circular dependency
    from .wip import count_tasks_in_stage

    current = count_tasks_in_stage(target_stage.value)
    limit = get_wip_limit(target_stage.value)
    percentage = int(current / limit * 100) if limit > 0 else 0

    # At or over limit
    if current >= limit:
        if bypass_reason:
            add_bypass_record(
                checklist, "wip_limit", target_stage.value, bypass_reason, current_user
            )
            return TransitionResult(
                success=True,
                message="WIP limit bypassed",
                warnings=[f"WIP bypass: {target_stage.value} now at {current + 1}/{limit}"]
            )
        return TransitionResult(
            success=False,
            message=f"WIP limit reached for {target_stage.value} ({current}/{limit}). "
                    f"Complete existing work or provide bypass_reason.",
            blocked_by="wip_limit"
        )

    # Approaching limit (80%)
    if percentage >= 80:
        return TransitionResult(
            success=True,
            message="WIP OK",
            warnings=[
                f"Approaching WIP limit: {target_stage.value} "
                f"({current}/{limit} = {percentage}%)"
            ]
        )

    return TransitionResult(success=True, message="WIP OK")


def _execute_transition(
    checklist: dict,
    from_stage: Stage,
    to_stage: Stage,
    agent: str | None = None
) -> None:
    """
    Execute the actual transition after all guards pass.
    """
    # Mark current stage complete (unless coming from BLOCKED)
    if from_stage != Stage.BLOCKED:
        mark_stage_complete(checklist, from_stage.value, agent)

    # Start new stage (unless going to terminal DEPLOY complete)
    if to_stage != Stage.BLOCKED:
        start_stage(checklist, to_stage.value, agent)

    # WIP counts will be updated by the caller via update_wip_counts()


def get_next_stage(current: Stage) -> Stage | None:
    """
    Get the expected next stage in normal workflow.

    Args:
        current: Current stage.

    Returns:
        Next stage in sequence, or None if at terminal.
    """
    try:
        idx = STAGE_SEQUENCE.index(current)
        return STAGE_SEQUENCE[idx + 1] if idx < len(STAGE_SEQUENCE) - 1 else None
    except ValueError:
        return None


def is_valid_transition(from_stage: str, to_stage: str) -> bool:
    """
    Check if a transition is valid.

    Args:
        from_stage: Source stage name.
        to_stage: Target stage name.

    Returns:
        True if transition is allowed.
    """
    try:
        from_enum = Stage(from_stage.lower())
        to_enum = Stage(to_stage.lower())
        return to_enum in VALID_TRANSITIONS.get(from_enum, [])
    except ValueError:
        return False
