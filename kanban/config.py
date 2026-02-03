"""
Configuration loader for Kanban Workflow Engine.

Loads settings from backlog/config.yml with sensible defaults.
"""

from pathlib import Path
from typing import Any
import yaml

# Default configuration if config.yml is missing or incomplete
DEFAULT_CONFIG: dict[str, Any] = {
    "version": "1.0",
    "enforcement_mode": "soft",
    "skip_penalty": 10,
    "wip_limits": {
        "understand": 5,
        "plan": 3,
        "build": 2,
        "verify": 3,
        "deploy": 2,
        "blocked": 10,
    },
    "critical_transitions": [
        ["plan", "build"],
        ["build", "verify"],
    ],
    "stage_requirements": {
        "understand": {
            "required": ["requirements_clarified", "acceptance_criteria_defined"],
            "optional": ["blocking_questions_resolved"],
        },
        "plan": {
            "required": ["branch_created"],
            "optional": ["prd_created", "tdd_created", "draft_pr_created"],
        },
        "build": {
            "required": ["tests_written", "implementation_complete", "local_tests_pass"],
            "optional": ["dev_report_written"],
        },
        "verify": {
            "required": ["code_review_approved", "changelog_updated", "ci_passing"],
            "optional": ["security_review_approved", "qa_report_approved"],
        },
        "deploy": {
            "required": ["pr_merged", "docs_updated"],
            "optional": ["learnings_extracted"],
        },
    },
    "qa_gates": {
        "enabled": False,
        "required_transitions": [["build", "verify"], ["verify", "deploy"]],
        "artifact": "QA_REPORT.md",
    },
}

# Cached config to avoid repeated file reads
_cached_config: dict[str, Any] | None = None


def load_config(config_path: str | Path | None = None, force_reload: bool = False) -> dict[str, Any]:
    """
    Load kanban configuration from backlog/config.yml.

    Args:
        config_path: Optional path to config file. Defaults to backlog/config.yml.
        force_reload: If True, bypass cache and reload from file.

    Returns:
        Configuration dictionary with kanban settings.
    """
    global _cached_config

    if _cached_config is not None and not force_reload:
        return _cached_config

    if config_path is None:
        # Try multiple locations
        possible_paths = [
            Path("backlog/config.yml"),
            Path("../backlog/config.yml"),
            Path.cwd() / "backlog" / "config.yml",
        ]
        config_path = next((p for p in possible_paths if p.exists()), None)

    config = DEFAULT_CONFIG.copy()

    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            file_config = yaml.safe_load(f)

        # Extract kanban section if present
        if file_config and "kanban" in file_config:
            kanban_config = file_config["kanban"]
            # Deep merge with defaults
            config = _deep_merge(config, kanban_config)

    _cached_config = config
    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary with defaults.
        override: Dictionary with overrides.

    Returns:
        Merged dictionary.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def get_wip_limit(stage: str) -> int:
    """Get WIP limit for a stage."""
    config = load_config()
    return config.get("wip_limits", {}).get(stage.lower(), 999)


def get_stage_requirements(stage: str) -> dict[str, list[str]]:
    """Get required and optional items for a stage."""
    config = load_config()
    return config.get("stage_requirements", {}).get(stage.lower(), {"required": [], "optional": []})


def get_enforcement_mode() -> str:
    """Get enforcement mode (soft or hard)."""
    config = load_config()
    return config.get("enforcement_mode", "soft")


def get_skip_penalty() -> int:
    """Get compliance penalty per skip."""
    config = load_config()
    return config.get("skip_penalty", 10)


def is_critical_transition(from_stage: str, to_stage: str) -> bool:
    """Check if a transition is critical (cannot skip without bypass)."""
    config = load_config()
    transitions = config.get("critical_transitions", [])
    return [from_stage.lower(), to_stage.lower()] in transitions
