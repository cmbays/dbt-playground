#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
Generate worktrees.json for the Workflow Hub Worktree Monitor UI.

This script runs the WorktreeMonitor orchestrator and outputs JSON data
that the browser-based UI consumes.

Usage:
    # One-shot generation
    uv run scripts/generate-worktrees-json.py

    # Continuous polling (for development)
    uv run scripts/generate-worktrees-json.py --poll --interval 10

    # Specify output file
    uv run scripts/generate-worktrees-json.py -o playgrounds/worktrees.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

# Add scripts directory to path for local imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from worktree_monitor import (
    WorktreeMonitor,
    VersionPlanLoader,
    WorktreeDiscovery,
    GitHubAdapter,
    HeartbeatMonitor,
    ArchiveManager,
)

# Default paths
DEFAULT_OUTPUT = PROJECT_ROOT / "playgrounds" / "worktrees.json"
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "version-plan.yaml"
DEFAULT_WORKFLOW_STATE = PROJECT_ROOT / "temp" / "WORKFLOW_STATE.md"
DEFAULT_ARCHIVES_DIR = PROJECT_ROOT / "playgrounds" / "archives"
DEFAULT_REPO = "cmbays/dbt-playground"


def create_default_config() -> Path:
    """Create a minimal version-plan.yaml if one doesn't exist."""
    config_path = DEFAULT_CONFIG
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if not config_path.exists():
        default_config = {
            "version": 1,
            "milestone": "v0.10",
            "phases": [
                {
                    "id": "phase-active",
                    "name": "Active Development",
                    "order": 1,
                    "status": "IN_PROGRESS",
                    "workstreams": [
                        {
                            "id": "ws-default",
                            "name": "Development",
                            "epic": 0,
                            "description": "Active development work",
                            "branches": [
                                "feat/*",
                                "fix/*",
                                "refactor/*",
                            ],
                            "status": "IN_PROGRESS",
                        }
                    ],
                }
            ],
        }
        import yaml
        config_path.write_text(yaml.dump(default_config, default_flow_style=False), encoding="utf-8")
        print(f"Created default config: {config_path}")

    return config_path


def setup_monitor(
    config_path: Path,
    workflow_state_path: Path,
    archives_dir: Path,
    repo: str,
) -> WorktreeMonitor:
    """Initialize the WorktreeMonitor with all components."""

    # Ensure config exists
    if not config_path.exists():
        config_path = create_default_config()

    # Initialize components
    version_plan_loader = VersionPlanLoader(config_path)
    worktree_discovery = WorktreeDiscovery()
    github_adapter = GitHubAdapter(repo)
    heartbeat_monitor = HeartbeatMonitor(workflow_state_path)
    archive_manager = ArchiveManager(archives_dir)

    # Create monitor (AnomalyDetector is internal)
    monitor = WorktreeMonitor(
        version_plan_loader=version_plan_loader,
        worktree_discovery=worktree_discovery,
        github_adapter=github_adapter,
        heartbeat_monitor=heartbeat_monitor,
        archive_manager=archive_manager,
    )

    return monitor


def generate_json(monitor: WorktreeMonitor, output_path: Path) -> bool:
    """Collect data and write JSON output.

    Returns:
        True if successful, False otherwise.
    """
    try:
        output = monitor.collect()

        # Write using atomic write
        monitor.write_output(output, output_path)

        return True
    except Exception as e:
        print(f"Error collecting data: {e}", file=sys.stderr)
        return False


def run_polling(
    monitor: WorktreeMonitor,
    output_path: Path,
    interval: int,
) -> None:
    """Run continuous polling loop."""
    print(f"Starting polling mode (interval: {interval}s)")
    print(f"Output: {output_path}")
    print("Press Ctrl+C to stop...")

    try:
        while True:
            start = time.monotonic()
            success = generate_json(monitor, output_path)
            elapsed = time.monotonic() - start

            status = "OK" if success else "FAILED"
            timestamp = datetime.now(UTC).strftime("%H:%M:%S")
            print(f"[{timestamp}] {status} ({elapsed:.2f}s)")

            # Sleep for remaining interval
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nPolling stopped.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate worktrees.json for Workflow Hub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSON file path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Version plan YAML config (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--workflow-state",
        type=Path,
        default=DEFAULT_WORKFLOW_STATE,
        help=f"WORKFLOW_STATE.md path for heartbeat (default: {DEFAULT_WORKFLOW_STATE})",
    )
    parser.add_argument(
        "--archives-dir",
        type=Path,
        default=DEFAULT_ARCHIVES_DIR,
        help=f"Archives directory (default: {DEFAULT_ARCHIVES_DIR})",
    )
    parser.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help=f"GitHub repo (owner/name) for PR status (default: {DEFAULT_REPO})",
    )
    parser.add_argument(
        "--poll",
        action="store_true",
        help="Run in continuous polling mode",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Polling interval in seconds (default: 10)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    try:
        monitor = setup_monitor(
            config_path=args.config,
            workflow_state_path=args.workflow_state,
            archives_dir=args.archives_dir,
            repo=args.repo,
        )
    except Exception as e:
        print(f"Failed to initialize monitor: {e}", file=sys.stderr)
        return 1

    if args.poll:
        run_polling(monitor, args.output, args.interval)
        return 0
    else:
        # One-shot generation
        success = generate_json(monitor, args.output)
        if success:
            print(f"Generated: {args.output}")
            return 0
        else:
            return 1


if __name__ == "__main__":
    sys.exit(main())
