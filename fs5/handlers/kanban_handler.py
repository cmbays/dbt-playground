"""
FS5 Kanban Handler.

Receives real-time transition events from FS2 and processes them
for adherence scoring and anomaly detection.

Version: v0.10.0
Created: 2026-02-03
"""

import logging
from datetime import datetime, UTC
from uuid import uuid4
import json

logger = logging.getLogger(__name__)


def handle_kanban_transition(
    task_id: str,
    from_stage: str,
    to_stage: str,
    result: dict,
    checklist: dict
) -> None:
    """
    Process a kanban transition event.

    Called in real-time when FS2 transition_task() completes.

    Actions:
    1. Update session phase tracking
    2. Check for anomalies (skip, out-of-order)
    3. Persist transition event
    """
    from fs5.services.adherence import update_session_phase
    from fs5.services.anomaly import check_transition_anomalies, persist_anomaly
    from fs5.core.db import get_connection

    # Create canonical event
    event = {
        "schema_version": "2.0.0",
        "event_id": str(uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": "workflow.phase_entered" if to_stage else "workflow.phase_exited",
        "source": {
            "type": "system",
            "identity": "kanban",
            "version": "0.10.0"
        },
        "correlation_id": task_id,
        "payload": {
            "phase": to_stage,
            "previous_phase": from_stage,
            "checklist_status": checklist
        }
    }

    # Update session tracking
    try:
        update_session_phase(task_id, to_stage, from_stage)
    except Exception as e:
        # Don't fail transition if session tracking fails, but log for debugging
        logger.warning(f"Session tracking failed for {task_id}: {e}")

    # Check for anomalies
    try:
        anomalies = check_transition_anomalies(task_id, from_stage, to_stage)
        for anomaly in anomalies:
            persist_anomaly(anomaly)
    except Exception as e:
        # Don't fail transition if anomaly detection fails, but log for debugging
        logger.warning(f"Anomaly detection failed for {task_id}: {e}")

    # Persist transition event
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO transition_events (
                    event_id, timestamp, task_id, from_stage, to_stage, payload
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                event["event_id"],
                event["timestamp"],
                task_id,
                from_stage,
                to_stage,
                json.dumps(event["payload"]),
            ])
    except Exception as e:
        # Don't fail the transition if persistence fails, but log for debugging
        logger.warning(f"Event persistence failed for {task_id}: {e}")


def register_handler() -> None:
    """Register the FS5 handler with FS2."""
    from kanban.events import register_transition_handler
    register_transition_handler(handle_kanban_transition)


def unregister_handler() -> None:
    """Unregister the FS5 handler from FS2."""
    from kanban.events import unregister_transition_handler
    unregister_transition_handler(handle_kanban_transition)
