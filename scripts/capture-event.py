#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema", "rich"]
# ///
"""
Capture Event - Structured event ingestion with validation.

Appends schema-validated events to the event log.
Invalid events are logged but rejected (graceful degradation).

Usage:
    uv run scripts/capture-event.py --type=phase.entered --data='{"phase":"DEVELOPMENT"}'
    uv run scripts/capture-event.py --type=artifact.created --data='{"path":"models/stg_customers.sql","artifact_type":"model"}'
    uv run scripts/capture-event.py --type=commit --data='{"sha":"abc123","message":"feat: add model"}'
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError
from rich.console import Console

console = Console()

# Paths
WORKFLOW_HISTORY_DIR = Path("temp/WORKFLOW_HISTORY")
EVENTS_FILE = WORKFLOW_HISTORY_DIR / "events.jsonl"
SCHEMA_FILE = WORKFLOW_HISTORY_DIR / "schema/event-schema.json"
REJECTED_LOG = WORKFLOW_HISTORY_DIR / "rejected-events.log"

# Schema version
SCHEMA_VERSION = "1.0.0"

# Valid event types per schema
VALID_EVENT_TYPES = [
    "commit",
    "phase.entered",
    "phase.exited",
    "artifact.created",
    "artifact.modified",
    "session.started",
    "session.ended",
    "agent.invoked",
    "agent.handoff",
]


def get_branch_name() -> str:
    """Get current git branch name."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def load_schema() -> dict | None:
    """Load event schema from file."""
    if not SCHEMA_FILE.exists():
        console.print(f"[yellow]Warning: Schema file not found at {SCHEMA_FILE}[/yellow]")
        return None

    with open(SCHEMA_FILE) as f:
        return json.load(f)


def validate_event(event: dict, schema: dict | None) -> tuple[bool, str]:
    """Validate event against schema.

    Returns:
        (is_valid, error_message)
    """
    if schema is None:
        # No schema available - basic validation only
        required = ["timestamp", "event_type", "source", "correlation_id"]
        missing = [f for f in required if f not in event]
        if missing:
            return False, f"Missing required fields: {missing}"
        return True, ""

    try:
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(event))
        if errors:
            error_messages = [e.message for e in errors[:3]]  # Limit to first 3
            return False, "; ".join(error_messages)
        return True, ""
    except Exception as e:
        return False, f"Validation error: {e}"


def log_rejected_event(event: dict, reason: str) -> None:
    """Log rejected event for debugging."""
    WORKFLOW_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    entry = {
        "rejected_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "event": event,
    }

    with open(REJECTED_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def append_event(event: dict) -> bool:
    """Append valid event to events.jsonl."""
    WORKFLOW_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(event) + "\n")
        return True
    except Exception as e:
        console.print(f"[red]Error writing event: {e}[/red]")
        return False


def build_event(event_type: str, payload: dict) -> dict:
    """Build complete event structure."""
    branch = get_branch_name()

    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "source": {
            "type": "human",  # Manual capture is human-initiated
            "identity": branch,
            "session_id": None,
        },
        "correlation_id": branch,
        "payload": payload,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture and validate workflow events",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Record phase transition
  uv run scripts/capture-event.py --type=phase.entered \\
    --data='{"phase":"DEVELOPMENT"}'

  # Record artifact creation
  uv run scripts/capture-event.py --type=artifact.created \\
    --data='{"path":"models/stg_customers.sql","artifact_type":"model"}'

  # Record agent invocation
  uv run scripts/capture-event.py --type=agent.invoked \\
    --data='{"agent":"dbt-developer","task":"implement staging model"}'
        """,
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=VALID_EVENT_TYPES,
        help="Event type",
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Event payload as JSON string",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate but don't append event",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output on success",
    )

    args = parser.parse_args()

    # Parse payload
    try:
        payload = json.loads(args.data)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON in --data: {e}[/red]")
        return 1

    # Build event
    event = build_event(args.type, payload)

    # Load schema and validate
    schema = load_schema()
    is_valid, error_msg = validate_event(event, schema)

    if not is_valid:
        console.print(f"[red]Event validation failed: {error_msg}[/red]")
        log_rejected_event(event, error_msg)
        return 1

    if args.dry_run:
        console.print("[green]Event is valid (dry-run mode)[/green]")
        console.print(json.dumps(event, indent=2))
        return 0

    # Append event
    if append_event(event):
        if not args.quiet:
            console.print(f"[green]Event captured: {args.type}[/green]")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
