"""
FS1 Memory Adapter.

Transforms FS1 memory events to canonical format.
Source: memory/events.jsonl

Version: v0.10.0
Created: 2026-02-03
"""

from datetime import datetime, UTC
from hashlib import md5
import json


def transform_fs1_event(fs1_event: dict) -> dict:
    """
    Transform FS1 memory event to canonical v2.0 format.

    Input (FS1 v1.0):
        {
            "timestamp": "2026-02-03T14:30:00Z",
            "event": "session_logged",
            "data": {
                "task": "Implemented feature X",
                "outcome": "SUCCESS",
                "session_id": "abc123",
                "patterns": ["TDD", "competitive-impl"]
            }
        }

    Output (Canonical v2.0):
        {
            "schema_version": "2.0.0",
            "event_id": "...",
            "timestamp": "2026-02-03T14:30:00Z",
            "event_type": "memory.session_logged",
            "source": {
                "type": "agent",
                "identity": "sage",
                "version": "0.10.0"
            },
            "correlation_id": "...",
            "payload": {...}
        }
    """
    timestamp = fs1_event.get("timestamp", datetime.now(UTC).isoformat())
    event_name = fs1_event.get("event", "unknown")
    data = fs1_event.get("data", {})

    # Generate deterministic event_id from timestamp + event content
    event_id = _generate_event_id(timestamp, fs1_event)

    # Map event type
    event_type = f"memory.{event_name}"

    # Extract correlation_id
    correlation_id = (
        data.get("correlation_id")
        or data.get("task_id")
        or data.get("session_id")
        or "unknown"
    )

    return {
        "schema_version": "2.0.0",
        "event_id": event_id,
        "timestamp": timestamp,
        "event_type": event_type,
        "source": {
            "type": "agent",
            "identity": "sage",
            "version": "0.10.0",
        },
        "correlation_id": correlation_id,
        "payload": data,
    }


def _generate_event_id(timestamp: str, event: dict) -> str:
    """Generate a deterministic UUIDv5-like ID from event content."""
    content = f"{timestamp}:{json.dumps(event, sort_keys=True)}"
    hash_bytes = md5(content.encode(), usedforsecurity=False).hexdigest()
    # Format as UUID
    return f"{hash_bytes[:8]}-{hash_bytes[8:12]}-{hash_bytes[12:16]}-{hash_bytes[16:20]}-{hash_bytes[20:32]}"


def batch_transform(events: list[dict]) -> list[dict]:
    """Transform a batch of FS1 events."""
    return [transform_fs1_event(e) for e in events]
