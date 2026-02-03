"""
Compliance scoring for Kanban Workflow Engine.

Calculates and reports workflow compliance scores based on
stage completion and skip history.
"""

from typing import Any

from .checklist import STAGES
from .config import get_skip_penalty

# Use canonical stage list from checklist module
REQUIRED_STAGES = STAGES


def calculate_compliance_score(checklist: dict[str, Any]) -> float:
    """
    Calculate compliance score for a task.

    Formula:
    - Base: (completed_stages / total_stages) * 100
    - Penalty: -skip_penalty per skip
    - Floor: 0

    Bypasses are tracked but do not affect score.

    Args:
        checklist: Task's workflow checklist dictionary.

    Returns:
        Compliance score between 0 and 100.

    Example:
        >>> checklist = {"stages": {...}, "compliance": {"skips": []}}
        >>> score = calculate_compliance_score(checklist)
        >>> print(f"Score: {score}")
    """
    stages = checklist.get("stages", {})
    completed = sum(
        1 for stage in REQUIRED_STAGES
        if stages.get(stage, {}).get("status") == "complete"
    )
    total = len(REQUIRED_STAGES)

    base_score = (completed / total) * 100

    skips = len(checklist.get("compliance", {}).get("skips", []))
    penalty = skips * get_skip_penalty()

    return max(0, round(base_score - penalty, 1))


def get_rating(score: float) -> str:
    """
    Convert compliance score to rating label.

    Args:
        score: Compliance score (0-100).

    Returns:
        Rating string: "excellent", "acceptable", "needs_improvement", or "poor".
    """
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "acceptable"
    elif score >= 40:
        return "needs_improvement"
    else:
        return "poor"


def get_rating_color(score: float) -> str:
    """
    Get color for rating visualization.

    Args:
        score: Compliance score (0-100).

    Returns:
        Color name for UI display.
    """
    if score >= 80:
        return "green"
    elif score >= 60:
        return "yellow"
    elif score >= 40:
        return "orange"
    else:
        return "red"


def get_compliance_breakdown(checklist: dict[str, Any]) -> dict[str, Any]:
    """
    Get detailed compliance breakdown for display.

    Args:
        checklist: Task's workflow checklist dictionary.

    Returns:
        Dictionary with detailed breakdown including:
        - score: Current score
        - rating: Rating label
        - stages: Stage completion stats
        - penalties: Skip penalty breakdown
        - bypasses: Bypass summary
        - calculation: Human-readable formula
    """
    stages = checklist.get("stages", {})
    compliance = checklist.get("compliance", {})

    completed_count = sum(
        1 for stage in REQUIRED_STAGES
        if stages.get(stage, {}).get("status") == "complete"
    )

    skip_count = len(compliance.get("skips", []))
    bypass_count = len(compliance.get("bypasses", []))

    score = compliance.get("score", calculate_compliance_score(checklist))
    penalty = get_skip_penalty()

    return {
        "score": score,
        "rating": get_rating(score),
        "color": get_rating_color(score),
        "stages": {
            "required": len(REQUIRED_STAGES),
            "completed": completed_count,
            "percentage": round(completed_count / len(REQUIRED_STAGES) * 100, 1),
            "details": {
                stage: stages.get(stage, {}).get("status", "unknown")
                for stage in REQUIRED_STAGES
            },
        },
        "penalties": {
            "skip_count": skip_count,
            "skip_penalty_each": penalty,
            "total_penalty": skip_count * penalty,
        },
        "bypasses": {
            "count": bypass_count,
            "types": [b.get("type") for b in compliance.get("bypasses", [])],
        },
        "calculation": (
            f"({completed_count}/{len(REQUIRED_STAGES)} × 100) - "
            f"({skip_count} × {penalty}) = {score}"
        ),
    }


def update_compliance_score(checklist: dict[str, Any]) -> float:
    """
    Recalculate and update compliance score in checklist.

    Args:
        checklist: Task's workflow checklist dictionary (modified in place).

    Returns:
        New compliance score.
    """
    score = calculate_compliance_score(checklist)
    checklist["compliance"]["score"] = score
    return score
