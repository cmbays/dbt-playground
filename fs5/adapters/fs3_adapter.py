"""
FS3 QA Adapter.

Transforms FS3 QA events to canonical format.
Source: temp/QA_METRICS_LOG.jsonl

Version: v0.10.0
Created: 2026-02-03
"""

from datetime import datetime, UTC
from hashlib import md5
from pathlib import Path
import json
import re


def transform_fs3_event(fs3_event: dict) -> dict:
    """
    Transform FS3 QA event to canonical v2.0 format.

    Input (FS3 format):
        {
            "timestamp": "2026-02-03T14:30:00Z",
            "gate": "code_review",
            "status": "PASSED",
            "reviewer": "code-reviewer",
            "evidence": "No critical issues found",
            "session_id": "abc123"
        }

    Output (Canonical v2.0):
        {
            "schema_version": "2.0.0",
            "event_id": "...",
            "timestamp": "...",
            "event_type": "qa.gate_passed",
            "source": {
                "type": "agent",
                "identity": "code-reviewer"
            },
            "correlation_id": "abc123",
            "payload": {...}
        }
    """
    timestamp = fs3_event.get("timestamp", datetime.now(UTC).isoformat())
    status = fs3_event.get("status", "CHECKED")
    gate = fs3_event.get("gate", "unknown")
    reviewer = fs3_event.get("reviewer", "qa-reviewer")
    session_id = fs3_event.get("session_id", "unknown")

    # Generate event_id
    event_id = _generate_event_id(timestamp, fs3_event)

    # Map status to event type
    event_type_map = {
        "PASSED": "qa.gate_passed",
        "SKIPPED": "qa.gate_skipped",
        "FAILED": "qa.gate_failed",
    }
    event_type = event_type_map.get(status, "qa.gate_checked")

    return {
        "schema_version": "2.0.0",
        "event_id": event_id,
        "timestamp": timestamp,
        "event_type": event_type,
        "source": {
            "type": "agent",
            "identity": reviewer,
            "version": "0.10.0",
        },
        "correlation_id": session_id,
        "payload": {
            "gate": gate,
            "status": status,
            "evidence": fs3_event.get("evidence"),
        },
    }


def _generate_event_id(timestamp: str, event: dict) -> str:
    """Generate a deterministic UUID-like ID from event content."""
    content = f"{timestamp}:{json.dumps(event, sort_keys=True)}"
    hash_bytes = md5(content.encode(), usedforsecurity=False).hexdigest()
    return f"{hash_bytes[:8]}-{hash_bytes[8:12]}-{hash_bytes[12:16]}-{hash_bytes[16:20]}-{hash_bytes[20:32]}"


def batch_transform(events: list[dict]) -> list[dict]:
    """Transform a batch of FS3 events."""
    return [transform_fs3_event(e) for e in events]


def parse_qa_report(report_path: str) -> list[dict]:
    """
    Fallback parser for QA_REPORT.md.

    Extracts gate status from markdown checkboxes:
    - [x] Code Review: PASSED -> qa.gate_passed
    - [ ] Security Review: PENDING -> qa.gate_checked
    - [~] Unit Tests: SKIPPED -> qa.gate_skipped
    """
    path = Path(report_path)
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8")
    events = []

    # Pattern: - [x], - [ ], - [~] followed by gate name
    pattern = r"- \[([ x~])\] ([^:]+): (\w+)"

    for match in re.finditer(pattern, content, re.IGNORECASE):
        check, gate, status = match.groups()

        # Map checkbox to status
        status_map = {
            "x": "PASSED",
            " ": "PENDING",
            "~": "SKIPPED",
        }
        mapped_status = status_map.get(check.lower(), status.upper())

        events.append({
            "timestamp": datetime.now(UTC).isoformat(),
            "gate": gate.strip().lower().replace(" ", "_"),
            "status": mapped_status,
            "reviewer": "qa-reviewer",
            "evidence": f"Parsed from {report_path}",
            "session_id": "unknown",
        })

    return [transform_fs3_event(e) for e in events]
