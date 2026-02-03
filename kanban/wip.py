"""
WIP (Work-in-Progress) tracking for Kanban Workflow Engine.

Tracks task counts per stage and enforces WIP limits.

Issue: #164 (WIP count tracking in WORKFLOW_STATE.md)
Epic: #144 (Kanban Workflow Engine)
"""

from pathlib import Path
from typing import Any
import re
import logging

from .config import get_wip_limit

logger = logging.getLogger("kanban.wip")

# Default WIP state file location
DEFAULT_WIP_FILE = Path("temp/WORKFLOW_STATE.md")

# In-memory WIP counts (can be persisted to state file)
_wip_counts: dict[str, int] = {
    "understand": 0,
    "plan": 0,
    "build": 0,
    "verify": 0,
    "deploy": 0,
    "blocked": 0,
}


def get_wip_counts() -> dict[str, int]:
    """
    Get current WIP counts for all stages.

    Returns:
        Dictionary mapping stage names to task counts.

    Example:
        >>> counts = get_wip_counts()
        >>> print(f"Build queue: {counts['build']}")
    """
    return _wip_counts.copy()


def count_tasks_in_stage(stage: str) -> int:
    """
    Get the current count of tasks in a specific stage.

    Args:
        stage: Stage name (understand, plan, build, verify, deploy, blocked).

    Returns:
        Number of tasks currently in the stage.
    """
    return _wip_counts.get(stage.lower(), 0)


def update_wip_counts(from_stage: str | None, to_stage: str) -> dict[str, int]:
    """
    Update WIP counts after a transition.

    Args:
        from_stage: Stage task is leaving (None for new tasks).
        to_stage: Stage task is entering.

    Returns:
        Updated WIP counts dictionary.

    Example:
        >>> # Task moves from plan to build
        >>> update_wip_counts("plan", "build")
        >>> # New task enters understand
        >>> update_wip_counts(None, "understand")
    """
    if from_stage:
        from_key = from_stage.lower()
        if from_key in _wip_counts and _wip_counts[from_key] > 0:
            _wip_counts[from_key] -= 1

    to_key = to_stage.lower()
    if to_key in _wip_counts:
        _wip_counts[to_key] += 1

    return _wip_counts.copy()


def set_wip_counts(counts: dict[str, int]) -> None:
    """
    Set WIP counts directly (for initialization or testing).

    Args:
        counts: Dictionary mapping stage names to counts.
    """
    global _wip_counts
    for stage, count in counts.items():
        if stage.lower() in _wip_counts:
            _wip_counts[stage.lower()] = max(0, count)


def reset_wip_counts() -> None:
    """Reset all WIP counts to zero."""
    global _wip_counts
    _wip_counts = {
        "understand": 0,
        "plan": 0,
        "build": 0,
        "verify": 0,
        "deploy": 0,
        "blocked": 0,
    }


def check_wip_capacity(stage: str) -> dict[str, Any]:
    """
    Check WIP capacity for a stage.

    Args:
        stage: Stage name to check.

    Returns:
        Dictionary with capacity info:
        - current: Current count
        - limit: WIP limit
        - available: Remaining capacity
        - at_limit: True if at or over limit
        - percentage: Usage percentage
    """
    stage_lower = stage.lower()
    current = _wip_counts.get(stage_lower, 0)
    limit = get_wip_limit(stage_lower)
    available = max(0, limit - current)
    percentage = int(current / limit * 100) if limit > 0 else 0

    return {
        "current": current,
        "limit": limit,
        "available": available,
        "at_limit": current >= limit,
        "percentage": percentage,
    }


def get_wip_summary() -> dict[str, Any]:
    """
    Get a summary of WIP status across all stages.

    Returns:
        Dictionary with overall WIP summary including:
        - stages: Per-stage capacity info
        - total_tasks: Total tasks across all stages
        - bottlenecks: Stages at or near capacity
    """
    stages = {}
    total = 0
    bottlenecks = []

    for stage in _wip_counts:
        capacity = check_wip_capacity(stage)
        stages[stage] = capacity
        total += capacity["current"]

        if capacity["at_limit"]:
            bottlenecks.append({"stage": stage, "status": "at_limit"})
        elif capacity["percentage"] >= 80:
            bottlenecks.append({"stage": stage, "status": "near_limit"})

    return {
        "stages": stages,
        "total_tasks": total,
        "bottlenecks": bottlenecks,
    }


def format_wip_for_state_file() -> str:
    """
    Format WIP counts for WORKFLOW_STATE.md.

    Returns:
        Markdown-formatted WIP section.

    Example output:
        ## WIP Counts
        | Stage | Current | Limit | Status |
        |-------|---------|-------|--------|
        | understand | 2 | 5 | OK |
        | plan | 3 | 3 | AT LIMIT |
        | build | 1 | 2 | OK |
        | verify | 0 | 3 | OK |
        | deploy | 0 | 2 | OK |
        | blocked | 1 | 10 | OK |
    """
    lines = [
        "## WIP Counts",
        "",
        "| Stage | Current | Limit | Status |",
        "|-------|---------|-------|--------|",
    ]

    for stage in ["understand", "plan", "build", "verify", "deploy", "blocked"]:
        capacity = check_wip_capacity(stage)
        if capacity["at_limit"]:
            status = "AT LIMIT"
        elif capacity["percentage"] >= 80:
            status = "NEAR LIMIT"
        else:
            status = "OK"

        lines.append(
            f"| {stage} | {capacity['current']} | {capacity['limit']} | {status} |"
        )

    return "\n".join(lines)


def parse_wip_from_state_file(content: str) -> dict[str, int] | None:
    """
    Parse WIP counts from WORKFLOW_STATE.md content.

    Args:
        content: Markdown content of state file.

    Returns:
        Dictionary of stage counts, or None if section not found.
    """
    # Look for WIP Counts section
    wip_pattern = r"## WIP Counts\s*\n\n\|[^\n]+\n\|[-|\s]+\n((?:\|[^\n]+\n)+)"
    match = re.search(wip_pattern, content)

    if not match:
        return None

    counts = {}
    rows = match.group(1).strip().split("\n")

    for row in rows:
        # Parse: | stage | current | limit | status |
        parts = [p.strip() for p in row.split("|") if p.strip()]
        if len(parts) >= 2:
            stage = parts[0].lower()
            try:
                count = int(parts[1])
                counts[stage] = count
            except ValueError:
                continue

    return counts


def load_wip_from_file(file_path: Path | str | None = None) -> bool:
    """
    Load WIP counts from WORKFLOW_STATE.md.

    Args:
        file_path: Path to state file. Defaults to temp/WORKFLOW_STATE.md.

    Returns:
        True if loaded successfully, False otherwise.
    """
    path = Path(file_path) if file_path else DEFAULT_WIP_FILE

    if not path.exists():
        logger.debug(f"WIP state file not found: {path}")
        return False

    try:
        content = path.read_text()
        counts = parse_wip_from_state_file(content)

        if counts:
            set_wip_counts(counts)
            logger.info(f"Loaded WIP counts from {path}")
            return True
        else:
            logger.debug("No WIP section found in state file")
            return False

    except Exception as e:
        logger.warning(f"Error loading WIP from {path}: {e}")
        return False


def save_wip_to_file(file_path: Path | str | None = None) -> bool:
    """
    Save WIP counts to WORKFLOW_STATE.md.

    Updates the WIP Counts section if it exists, or appends it.

    Args:
        file_path: Path to state file. Defaults to temp/WORKFLOW_STATE.md.

    Returns:
        True if saved successfully, False otherwise.
    """
    path = Path(file_path) if file_path else DEFAULT_WIP_FILE

    wip_section = format_wip_for_state_file()

    try:
        if path.exists():
            content = path.read_text()

            # Replace existing WIP section or append
            wip_pattern = r"## WIP Counts\s*\n\n\|[^\n]+\n\|[-|\s]+\n(?:\|[^\n]+\n)+"
            if re.search(wip_pattern, content):
                content = re.sub(wip_pattern, wip_section + "\n", content)
            else:
                content = content.rstrip() + "\n\n" + wip_section + "\n"

            path.write_text(content)
        else:
            # Create new file with WIP section
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# Workflow State\n\n{wip_section}\n")

        logger.info(f"Saved WIP counts to {path}")
        return True

    except Exception as e:
        logger.warning(f"Error saving WIP to {path}: {e}")
        return False
