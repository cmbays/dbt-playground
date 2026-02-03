"""
Checklist operations for Kanban Workflow Engine.

Provides functions for creating, validating, and updating workflow checklists.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import re

from .config import get_stage_requirements

# Schema version
SCHEMA_VERSION = "1.0"

# Valid stages
STAGES = ["understand", "plan", "build", "verify", "deploy"]

# Valid statuses
STATUSES = ["pending", "in_progress", "complete", "skipped"]


def create_checklist(task_id: str, agent: str | None = None) -> dict[str, Any]:
    """
    Create a new workflow checklist for a task.

    Args:
        task_id: The task identifier (e.g., "TASK-100").
        agent: Optional agent name to associate with initial stage.

    Returns:
        New checklist dictionary with default structure.

    Raises:
        ValueError: If task_id doesn't match expected format.
    """
    if not re.match(r"^TASK-[0-9]+$", task_id):
        raise ValueError(f"Invalid task_id format: {task_id}. Expected TASK-[0-9]+")

    now = datetime.now(timezone.utc).isoformat()

    checklist = {
        "version": SCHEMA_VERSION,
        "task_id": task_id,
        "created_at": now,
        "stages": {},
        "compliance": {
            "score": 100,
            "skips": [],
            "bypasses": [],
        },
    }

    # Initialize all stages with requirements from config
    for stage in STAGES:
        requirements = get_stage_requirements(stage)
        checklist["stages"][stage] = {
            "status": "pending",
            "required_items": requirements.get("required", []),
            "completed_items": [],
            "started_at": None,
            "completed_at": None,
            "agent": None,
        }

    # Mark first stage as in_progress
    checklist["stages"]["understand"]["status"] = "in_progress"
    checklist["stages"]["understand"]["started_at"] = now
    checklist["stages"]["understand"]["agent"] = agent

    return checklist


def validate_checklist(checklist: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate a checklist against the schema.

    Args:
        checklist: Checklist dictionary to validate.

    Returns:
        Tuple of (is_valid, list of error messages).
    """
    errors = []

    # Required top-level fields
    required_fields = ["version", "task_id", "created_at", "stages", "compliance"]
    for field in required_fields:
        if field not in checklist:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    # Validate version
    if checklist.get("version") != SCHEMA_VERSION:
        errors.append(f"Invalid version: {checklist.get('version')}. Expected {SCHEMA_VERSION}")

    # Validate task_id format
    task_id = checklist.get("task_id", "")
    if not re.match(r"^TASK-[0-9]+$", task_id):
        errors.append(f"Invalid task_id format: {task_id}")

    # Validate stages
    stages = checklist.get("stages", {})
    for stage in STAGES:
        if stage not in stages:
            errors.append(f"Missing stage: {stage}")
        else:
            stage_data = stages[stage]
            if stage_data.get("status") not in STATUSES:
                errors.append(f"Invalid status for {stage}: {stage_data.get('status')}")

    # Validate compliance
    compliance = checklist.get("compliance", {})
    if "score" not in compliance:
        errors.append("Missing compliance.score")
    elif not isinstance(compliance["score"], (int, float)):
        errors.append("compliance.score must be a number")
    elif not (0 <= compliance["score"] <= 100):
        errors.append("compliance.score must be between 0 and 100")

    if "skips" not in compliance or not isinstance(compliance["skips"], list):
        errors.append("compliance.skips must be a list")

    if "bypasses" not in compliance or not isinstance(compliance["bypasses"], list):
        errors.append("compliance.bypasses must be a list")

    return len(errors) == 0, errors


def mark_item_complete(
    checklist: dict[str, Any],
    stage: str,
    item: str,
    agent: str | None = None
) -> bool:
    """
    Mark a checklist item as complete.

    Args:
        checklist: Checklist dictionary to update.
        stage: Stage name (e.g., "build").
        item: Item name (e.g., "tests_written").
        agent: Optional agent that completed the item.

    Returns:
        True if item was marked complete, False if already complete or invalid.
    """
    stage = stage.lower()
    if stage not in STAGES:
        return False

    stage_data = checklist.get("stages", {}).get(stage)
    if not stage_data:
        return False

    completed = stage_data.get("completed_items", [])
    if item in completed:
        return False  # Already complete

    completed.append(item)
    stage_data["completed_items"] = completed

    # Update agent if provided
    if agent:
        stage_data["agent"] = agent

    return True


def is_stage_complete(checklist: dict[str, Any], stage: str) -> bool:
    """
    Check if all required items are complete for a stage.

    Args:
        checklist: Checklist dictionary.
        stage: Stage name to check.

    Returns:
        True if all required items are complete.
    """
    stage = stage.lower()
    stage_data = checklist.get("stages", {}).get(stage, {})

    required = set(stage_data.get("required_items", []))
    completed = set(stage_data.get("completed_items", []))

    return required.issubset(completed)


def get_incomplete_items(checklist: dict[str, Any], stage: str) -> list[str]:
    """
    Get list of incomplete required items for a stage.

    Args:
        checklist: Checklist dictionary.
        stage: Stage name to check.

    Returns:
        List of incomplete required item names.
    """
    stage = stage.lower()
    stage_data = checklist.get("stages", {}).get(stage, {})

    required = set(stage_data.get("required_items", []))
    completed = set(stage_data.get("completed_items", []))

    return list(required - completed)


def mark_stage_complete(
    checklist: dict[str, Any],
    stage: str,
    agent: str | None = None
) -> None:
    """
    Mark a stage as complete.

    Args:
        checklist: Checklist dictionary to update.
        stage: Stage name to mark complete.
        agent: Optional agent that completed the stage.
    """
    stage = stage.lower()
    stage_data = checklist.get("stages", {}).get(stage)
    if not stage_data:
        return

    now = datetime.now(timezone.utc).isoformat()
    stage_data["status"] = "complete"
    stage_data["completed_at"] = now
    if agent:
        stage_data["agent"] = agent


def start_stage(
    checklist: dict[str, Any],
    stage: str,
    agent: str | None = None
) -> None:
    """
    Mark a stage as in_progress.

    Args:
        checklist: Checklist dictionary to update.
        stage: Stage name to start.
        agent: Optional agent working on the stage.
    """
    stage = stage.lower()
    stage_data = checklist.get("stages", {}).get(stage)
    if not stage_data:
        return

    now = datetime.now(timezone.utc).isoformat()
    stage_data["status"] = "in_progress"
    stage_data["started_at"] = now
    if agent:
        stage_data["agent"] = agent


def add_skip_record(
    checklist: dict[str, Any],
    from_stage: str,
    to_stage: str,
    skipped_stage: str,
    reason: str | None = None
) -> None:
    """
    Add a skip record to the checklist compliance section.

    Args:
        checklist: Checklist dictionary to update.
        from_stage: Source stage of the transition.
        to_stage: Target stage of the transition.
        skipped_stage: Stage that was skipped.
        reason: Optional reason for the skip.
    """
    now = datetime.now(timezone.utc).isoformat()
    skip_record = {
        "from_stage": from_stage.lower(),
        "to_stage": to_stage.lower(),
        "skipped_stage": skipped_stage.lower(),
        "timestamp": now,
        "reason": reason,
        "learning_extracted": False,
    }
    checklist["compliance"]["skips"].append(skip_record)


def add_bypass_record(
    checklist: dict[str, Any],
    bypass_type: str,
    stage: str,
    reason: str,
    authorized_by: str
) -> None:
    """
    Add a bypass record to the checklist compliance section.

    Args:
        checklist: Checklist dictionary to update.
        bypass_type: Type of bypass (wip_limit, checklist_incomplete, etc.).
        stage: Stage where bypass occurred.
        reason: Reason for the bypass.
        authorized_by: User/agent that authorized the bypass.
    """
    now = datetime.now(timezone.utc).isoformat()
    bypass_record = {
        "type": bypass_type,
        "stage": stage.lower(),
        "reason": reason,
        "authorized_by": authorized_by,
        "timestamp": now,
    }
    checklist["compliance"]["bypasses"].append(bypass_record)
