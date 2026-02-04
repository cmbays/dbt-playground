"""
FS5 Adherence Scoring Service.

Calculates workflow adherence scores based on the canonical 5-stage workflow:
UNDERSTAND -> PLAN -> BUILD -> VERIFY -> DEPLOY

Scoring Formula (from PRD-027):
    adherence_score = base_points + completion_bonus - penalties

Phase Points:
    UNDERSTAND: 10
    PLAN: 25
    BUILD: 30
    VERIFY: 20
    DEPLOY: 15
    Total: 100

Completion Bonus: +20 if all phases completed in canonical order
Penalties:
    - redo: -5 per redo (phase entered after previously exited)
    - skip: -15 per skipped phase
    - out_of_order: -10 per out-of-order transition
    - timeout: -5 per timeout (phase > 2x baseline duration)

Rating Thresholds:
    EXCELLENT: >= 100
    GOOD: >= 80
    FAIR: >= 60
    POOR: < 60

Score range: 0-120 (clamped)

Version: v0.10.0
Created: 2026-02-03
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Literal
from uuid import uuid4

# Phase point values (from PRD-027 FR-001)
PHASE_POINTS: dict[str, int] = {
    "UNDERSTAND": 10,
    "PLAN": 25,
    "BUILD": 30,
    "VERIFY": 20,
    "DEPLOY": 15,
}

# Canonical phase order
CANONICAL_ORDER: list[str] = ["UNDERSTAND", "PLAN", "BUILD", "VERIFY", "DEPLOY"]

# Penalty values (from PRD-027 FR-001)
PENALTY_VALUES: dict[str, int] = {
    "redo": 5,           # Per redo
    "skip": 15,          # Per skipped phase
    "out_of_order": 10,  # Per out-of-order transition
    "timeout": 5,        # Per phase timeout (>2x baseline)
}

# Phase duration baselines in minutes (from PRD-027)
PHASE_BASELINES: dict[str, int] = {
    "UNDERSTAND": 30,
    "PLAN": 60,
    "BUILD": 120,
    "VERIFY": 60,
    "DEPLOY": 30,
}

# Completion bonus for perfect workflow
COMPLETION_BONUS = 20

# Score bounds
MIN_SCORE = 0
MAX_SCORE = 120


@dataclass
class Penalty:
    """A single penalty applied to adherence score."""

    type: Literal["redo", "skip", "out_of_order", "timeout"]
    count: int
    points_deducted: int
    details: str | None = None


@dataclass
class AdherenceScore:
    """Result of adherence score calculation."""

    final_score: int              # 0-120 (100 base + 20 bonus max)
    base_points: int              # Sum of completed phase points
    completion_bonus: int         # 20 if all phases in order, else 0
    penalties: list[Penalty] = field(default_factory=list)
    phases_completed: list[str] = field(default_factory=list)
    rating: Literal["EXCELLENT", "GOOD", "FAIR", "POOR"] = "POOR"

    def __post_init__(self):
        """Set rating based on score."""
        self.rating = self.rate(self.final_score)

    @staticmethod
    def rate(score: int) -> Literal["EXCELLENT", "GOOD", "FAIR", "POOR"]:
        """Determine rating from score."""
        if score >= 100:
            return "EXCELLENT"
        if score >= 80:
            return "GOOD"
        if score >= 60:
            return "FAIR"
        return "POOR"


def calculate_adherence_score(
    correlation_id: str,
    events: list[dict] | None = None
) -> AdherenceScore:
    """
    Calculate adherence score for a feature/session.

    Args:
        correlation_id: Feature branch or task ID
        events: Optional pre-fetched events (queries v_unified_events if None)

    Returns:
        AdherenceScore with full breakdown

    Algorithm:
        1. Extract phase transitions from events
        2. Calculate base_points (sum of completed phase points)
        3. Check for completion_bonus (all 5 phases in canonical order)
        4. Calculate penalties (redos, skips, out-of-order, timeouts)
        5. final_score = base_points + completion_bonus - sum(penalties)
        6. Clamp to 0-120 range
    """
    if events is None:
        events = _fetch_events_for_correlation(correlation_id)

    # Extract phase transitions
    phase_data = _extract_phase_data(events)

    # Calculate base points
    phases_completed = list(phase_data.keys())
    base_points = sum(PHASE_POINTS.get(p, 0) for p in phases_completed)

    # Check for completion bonus
    completion_bonus = 0
    if _is_perfect_order(phases_completed):
        completion_bonus = COMPLETION_BONUS

    # Calculate penalties
    penalties = []

    # Redo penalties
    redo_penalties = _calculate_redo_penalties(phase_data)
    if redo_penalties:
        penalties.append(redo_penalties)

    # Skip penalties
    skip_penalties = _calculate_skip_penalties(phases_completed)
    if skip_penalties:
        penalties.append(skip_penalties)

    # Out-of-order penalties
    order_penalties = _calculate_order_penalties(events)
    if order_penalties:
        penalties.append(order_penalties)

    # Timeout penalties
    timeout_penalties = _calculate_timeout_penalties(phase_data)
    if timeout_penalties:
        penalties.append(timeout_penalties)

    # Calculate final score
    total_penalty = sum(p.points_deducted for p in penalties)
    raw_score = base_points + completion_bonus - total_penalty
    final_score = max(MIN_SCORE, min(MAX_SCORE, raw_score))

    return AdherenceScore(
        final_score=final_score,
        base_points=base_points,
        completion_bonus=completion_bonus,
        penalties=penalties,
        phases_completed=phases_completed,
    )


def _fetch_events_for_correlation(correlation_id: str) -> list[dict]:
    """Fetch events from v_unified_events for a correlation_id."""
    from fs5.core.db import get_connection

    with get_connection() as conn:
        result = conn.execute("""
            SELECT
                event_timestamp,
                event_type,
                payload
            FROM v_unified_events
            WHERE correlation_id = ?
              AND event_type IN (
                  'workflow.phase_entered',
                  'workflow.phase_exited'
              )
            ORDER BY event_timestamp
        """, [correlation_id]).fetchall()

        return [
            {
                "timestamp": row[0],
                "event_type": row[1],
                "payload": row[2]
            }
            for row in result
        ]


def _extract_phase_data(events: list[dict]) -> dict[str, dict]:
    """
    Extract phase timing data from events.

    Returns dict mapping phase -> {
        'entered_times': [...],
        'exited_times': [...],
        'enter_count': int,
        'duration_seconds': int or None
    }
    """
    phase_data: dict[str, dict] = {}

    for event in events:
        event_type = event.get("event_type", "")
        payload = event.get("payload", {})

        # Handle both string and dict payloads
        if isinstance(payload, str):
            import json
            try:
                payload = json.loads(payload)
            except (json.JSONDecodeError, TypeError):
                payload = {}

        phase = payload.get("phase")
        if not phase:
            continue

        if phase not in phase_data:
            phase_data[phase] = {
                "entered_times": [],
                "exited_times": [],
                "enter_count": 0,
                "duration_seconds": None,
            }

        timestamp = event.get("timestamp")
        if event_type == "workflow.phase_entered":
            phase_data[phase]["entered_times"].append(timestamp)
            phase_data[phase]["enter_count"] += 1
        elif event_type == "workflow.phase_exited":
            phase_data[phase]["exited_times"].append(timestamp)

    # Calculate durations
    for phase, data in phase_data.items():
        if data["entered_times"] and data["exited_times"]:
            first_enter = _parse_timestamp(data["entered_times"][0])
            last_exit = _parse_timestamp(data["exited_times"][-1])
            if first_enter and last_exit:
                data["duration_seconds"] = int((last_exit - first_enter).total_seconds())

    return phase_data


def _parse_timestamp(ts) -> datetime | None:
    """Parse timestamp to datetime."""
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _is_perfect_order(phases_completed: list[str]) -> bool:
    """Check if all phases completed in canonical order."""
    if len(phases_completed) != len(CANONICAL_ORDER):
        return False

    # Get expected indices
    for i, phase in enumerate(phases_completed):
        if phase not in CANONICAL_ORDER:
            return False
        expected_idx = CANONICAL_ORDER.index(phase)
        if i != expected_idx:
            return False

    return phases_completed == CANONICAL_ORDER


def _calculate_redo_penalties(phase_data: dict[str, dict]) -> Penalty | None:
    """Calculate penalties for phase redos (entering a phase more than once)."""
    total_redos = 0
    details = []

    for phase, data in phase_data.items():
        redos = data["enter_count"] - 1
        if redos > 0:
            total_redos += redos
            details.append(f"{phase}:{redos}")

    if total_redos == 0:
        return None

    return Penalty(
        type="redo",
        count=total_redos,
        points_deducted=total_redos * PENALTY_VALUES["redo"],
        details=", ".join(details),
    )


def _calculate_skip_penalties(phases_completed: list[str]) -> Penalty | None:
    """Calculate penalties for skipped phases."""
    skipped = []

    for phase in CANONICAL_ORDER:
        if phase not in phases_completed:
            skipped.append(phase)

    if not skipped:
        return None

    return Penalty(
        type="skip",
        count=len(skipped),
        points_deducted=len(skipped) * PENALTY_VALUES["skip"],
        details=", ".join(skipped),
    )


def _calculate_order_penalties(events: list[dict]) -> Penalty | None:
    """Calculate penalties for out-of-order transitions."""
    # Get sequence of phase entries
    entry_sequence = []

    for event in events:
        if event.get("event_type") != "workflow.phase_entered":
            continue

        payload = event.get("payload", {})
        if isinstance(payload, str):
            import json
            try:
                payload = json.loads(payload)
            except (json.JSONDecodeError, TypeError):
                continue

        phase = payload.get("phase")
        if phase and phase in CANONICAL_ORDER:
            entry_sequence.append(phase)

    # Count out-of-order transitions
    violations = 0
    details = []

    for i in range(1, len(entry_sequence)):
        prev_phase = entry_sequence[i - 1]
        curr_phase = entry_sequence[i]

        prev_idx = CANONICAL_ORDER.index(prev_phase)
        curr_idx = CANONICAL_ORDER.index(curr_phase)

        # Going backwards is out of order (not counting re-entry to same phase)
        if curr_idx < prev_idx:
            violations += 1
            details.append(f"{prev_phase}->{curr_phase}")

    if violations == 0:
        return None

    return Penalty(
        type="out_of_order",
        count=violations,
        points_deducted=violations * PENALTY_VALUES["out_of_order"],
        details=", ".join(details),
    )


def _calculate_timeout_penalties(phase_data: dict[str, dict]) -> Penalty | None:
    """Calculate penalties for phases exceeding 2x baseline duration."""
    timeouts = 0
    details = []

    for phase, data in phase_data.items():
        duration_sec = data.get("duration_seconds")
        if duration_sec is None:
            continue

        baseline_min = PHASE_BASELINES.get(phase, 60)
        threshold_sec = baseline_min * 2 * 60  # 2x baseline in seconds

        if duration_sec > threshold_sec:
            timeouts += 1
            duration_min = duration_sec // 60
            details.append(f"{phase}:{duration_min}m>{baseline_min * 2}m")

    if timeouts == 0:
        return None

    return Penalty(
        type="timeout",
        count=timeouts,
        points_deducted=timeouts * PENALTY_VALUES["timeout"],
        details=", ".join(details),
    )


def update_session_phase(
    task_id: str,
    new_phase: str,
    previous_phase: str | None = None
) -> None:
    """
    Update session tracking when phase changes.

    Called by kanban handler on transitions.
    Updates sessions table with current phase.
    """
    from fs5.core.db import get_connection

    with get_connection() as conn:
        # Check if session exists for this task
        existing = conn.execute("""
            SELECT session_id FROM sessions
            WHERE correlation_id = ? AND status = 'active'
            LIMIT 1
        """, [task_id]).fetchone()

        now = datetime.now(UTC)

        if existing:
            # Update existing session
            conn.execute("""
                UPDATE sessions
                SET current_phase = ?,
                    phase_entered_at = ?,
                    updated_at = ?
                WHERE session_id = ?
            """, [new_phase, now, now, existing[0]])
        else:
            # Create new session
            session_id = str(uuid4())
            conn.execute("""
                INSERT INTO sessions (
                    session_id, correlation_id, started_at,
                    current_phase, phase_entered_at, status
                )
                VALUES (?, ?, ?, ?, ?, 'active')
            """, [session_id, task_id, now, new_phase, now])


def get_session_status(correlation_id: str) -> dict | None:
    """Get current session status for a correlation_id."""
    from fs5.core.db import get_connection

    with get_connection() as conn:
        result = conn.execute("""
            SELECT
                session_id,
                current_phase,
                phase_entered_at,
                status,
                started_at
            FROM sessions
            WHERE correlation_id = ?
            ORDER BY started_at DESC
            LIMIT 1
        """, [correlation_id]).fetchone()

        if not result:
            return None

        return {
            "session_id": str(result[0]),
            "current_phase": result[1],
            "phase_entered_at": result[2],
            "status": result[3],
            "started_at": result[4],
        }
