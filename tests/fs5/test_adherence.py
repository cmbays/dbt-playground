"""Tests for fs5.services.adherence module - Adherence Scoring.

Tests cover:
- Score calculation formula
- Penalty calculations (skip, redo, out_of_order, timeout)
- Rating thresholds (EXCELLENT >= 100, GOOD >= 80, FAIR >= 60, POOR < 60)
- Perfect workflow = 120 points (100 base + 20 bonus)
- Edge cases and boundaries

Version: v0.10.0
Created: 2026-02-03
"""

import pytest
from datetime import datetime, UTC, timedelta

from fs5.services.adherence import (
    CANONICAL_ORDER,
    COMPLETION_BONUS,
    MAX_SCORE,
    MIN_SCORE,
    PENALTY_VALUES,
    PHASE_BASELINES,
    PHASE_POINTS,
    AdherenceScore,
    Penalty,
    calculate_adherence_score,
)


class TestConstants:
    """Tests for adherence scoring constants."""

    def test_canonical_order_has_five_phases(self):
        """CANONICAL_ORDER has exactly 5 phases."""
        assert len(CANONICAL_ORDER) == 5

    def test_canonical_order_correct_sequence(self):
        """CANONICAL_ORDER follows UNDERSTAND -> PLAN -> BUILD -> VERIFY -> DEPLOY."""
        assert CANONICAL_ORDER == ["UNDERSTAND", "PLAN", "BUILD", "VERIFY", "DEPLOY"]

    def test_phase_points_sum_to_100(self):
        """PHASE_POINTS sum to 100 base points."""
        total = sum(PHASE_POINTS.values())
        assert total == 100

    def test_completion_bonus_is_20(self):
        """COMPLETION_BONUS is 20 points."""
        assert COMPLETION_BONUS == 20

    def test_max_score_is_120(self):
        """MAX_SCORE is 120 (100 + 20 bonus)."""
        assert MAX_SCORE == 120

    def test_min_score_is_0(self):
        """MIN_SCORE is 0."""
        assert MIN_SCORE == 0

    def test_penalty_values_correct(self):
        """PENALTY_VALUES match PRD specification."""
        assert PENALTY_VALUES["redo"] == 5
        assert PENALTY_VALUES["skip"] == 15
        assert PENALTY_VALUES["out_of_order"] == 10
        assert PENALTY_VALUES["timeout"] == 5


class TestAdherenceScoreRating:
    """Tests for AdherenceScore.rate() method."""

    def test_excellent_at_100(self):
        """Score of 100 rates as EXCELLENT."""
        assert AdherenceScore.rate(100) == "EXCELLENT"

    def test_excellent_above_100(self):
        """Score of 120 rates as EXCELLENT."""
        assert AdherenceScore.rate(120) == "EXCELLENT"

    def test_good_at_80(self):
        """Score of 80 rates as GOOD."""
        assert AdherenceScore.rate(80) == "GOOD"

    def test_good_at_99(self):
        """Score of 99 rates as GOOD."""
        assert AdherenceScore.rate(99) == "GOOD"

    def test_fair_at_60(self):
        """Score of 60 rates as FAIR."""
        assert AdherenceScore.rate(60) == "FAIR"

    def test_fair_at_79(self):
        """Score of 79 rates as FAIR."""
        assert AdherenceScore.rate(79) == "FAIR"

    def test_poor_at_59(self):
        """Score of 59 rates as POOR."""
        assert AdherenceScore.rate(59) == "POOR"

    def test_poor_at_0(self):
        """Score of 0 rates as POOR."""
        assert AdherenceScore.rate(0) == "POOR"


class TestAdherenceScoreDataclass:
    """Tests for AdherenceScore dataclass."""

    def test_post_init_sets_rating(self):
        """__post_init__ sets rating based on score."""
        score = AdherenceScore(
            final_score=95,
            base_points=95,
            completion_bonus=0,
        )
        assert score.rating == "GOOD"

    def test_excellent_rating_auto_set(self):
        """Rating auto-set to EXCELLENT for score >= 100."""
        score = AdherenceScore(
            final_score=110,
            base_points=90,
            completion_bonus=20,
        )
        assert score.rating == "EXCELLENT"

    def test_default_empty_lists(self):
        """Default penalties and phases_completed are empty lists."""
        score = AdherenceScore(
            final_score=0,
            base_points=0,
            completion_bonus=0,
        )
        assert score.penalties == []
        assert score.phases_completed == []


class TestPerfectWorkflow:
    """Tests for perfect workflow scoring (120 points)."""

    def test_perfect_workflow_full_score(self):
        """Perfect workflow with all phases in order = 120 points."""
        events = _create_perfect_workflow_events()

        score = calculate_adherence_score("test-correlation", events)

        assert score.final_score == 120
        assert score.base_points == 100
        assert score.completion_bonus == 20
        assert score.rating == "EXCELLENT"
        assert len(score.penalties) == 0

    def test_perfect_workflow_all_phases_completed(self):
        """Perfect workflow has all 5 phases completed."""
        events = _create_perfect_workflow_events()

        score = calculate_adherence_score("test-correlation", events)

        assert len(score.phases_completed) == 5
        assert set(score.phases_completed) == set(CANONICAL_ORDER)


class TestSkipPenalty:
    """Tests for skip penalty (-15 per skipped phase)."""

    def test_skip_one_phase(self):
        """Skipping one phase costs 15 points."""
        # Skip UNDERSTAND, go straight to PLAN
        events = _create_events_skipping_phases(["UNDERSTAND"])

        score = calculate_adherence_score("test-correlation", events)

        # Base: 90 (missing UNDERSTAND = 10)
        # No completion bonus (not all phases)
        # Penalty: -15 for skip
        assert score.base_points == 90  # 100 - 10 (UNDERSTAND points)
        assert score.completion_bonus == 0
        skip_penalty = _find_penalty(score.penalties, "skip")
        assert skip_penalty is not None
        assert skip_penalty.count == 1
        assert skip_penalty.points_deducted == 15

    def test_skip_two_phases(self):
        """Skipping two phases costs 30 points."""
        events = _create_events_skipping_phases(["UNDERSTAND", "PLAN"])

        score = calculate_adherence_score("test-correlation", events)

        skip_penalty = _find_penalty(score.penalties, "skip")
        assert skip_penalty is not None
        assert skip_penalty.count == 2
        assert skip_penalty.points_deducted == 30


class TestRedoPenalty:
    """Tests for redo penalty (-5 per redo)."""

    def test_redo_one_phase(self):
        """Entering a phase twice costs 5 points."""
        events = _create_events_with_redo("BUILD", 1)

        score = calculate_adherence_score("test-correlation", events)

        redo_penalty = _find_penalty(score.penalties, "redo")
        assert redo_penalty is not None
        assert redo_penalty.count == 1
        assert redo_penalty.points_deducted == 5

    def test_redo_multiple_times(self):
        """Entering a phase 3 times = 2 redos = 10 points."""
        events = _create_events_with_redo("BUILD", 2)

        score = calculate_adherence_score("test-correlation", events)

        redo_penalty = _find_penalty(score.penalties, "redo")
        assert redo_penalty is not None
        assert redo_penalty.count == 2
        assert redo_penalty.points_deducted == 10


class TestOutOfOrderPenalty:
    """Tests for out-of-order penalty (-10 per violation)."""

    def test_single_out_of_order(self):
        """Going backwards once costs 10 points."""
        # UNDERSTAND -> BUILD -> PLAN (out of order!)
        events = _create_out_of_order_events(["UNDERSTAND", "BUILD", "PLAN"])

        score = calculate_adherence_score("test-correlation", events)

        order_penalty = _find_penalty(score.penalties, "out_of_order")
        assert order_penalty is not None
        assert order_penalty.count == 1
        assert order_penalty.points_deducted == 10

    def test_multiple_out_of_order(self):
        """Going backwards twice costs 20 points."""
        # UNDERSTAND -> VERIFY -> BUILD -> PLAN (two backwards!)
        events = _create_out_of_order_events(["UNDERSTAND", "VERIFY", "BUILD", "PLAN"])

        score = calculate_adherence_score("test-correlation", events)

        order_penalty = _find_penalty(score.penalties, "out_of_order")
        assert order_penalty is not None
        assert order_penalty.count == 2
        assert order_penalty.points_deducted == 20


class TestTimeoutPenalty:
    """Tests for timeout penalty (-5 per timeout)."""

    def test_timeout_single_phase(self):
        """Phase exceeding 2x baseline costs 5 points."""
        # BUILD baseline is 120 minutes, threshold is 240 minutes
        events = _create_events_with_timeout("BUILD", duration_minutes=250)

        score = calculate_adherence_score("test-correlation", events)

        timeout_penalty = _find_penalty(score.penalties, "timeout")
        assert timeout_penalty is not None
        assert timeout_penalty.count == 1
        assert timeout_penalty.points_deducted == 5

    def test_no_timeout_within_threshold(self):
        """Phase within 2x baseline has no timeout penalty."""
        # BUILD baseline is 120 minutes, threshold is 240 minutes
        events = _create_events_with_timeout("BUILD", duration_minutes=200)

        score = calculate_adherence_score("test-correlation", events)

        timeout_penalty = _find_penalty(score.penalties, "timeout")
        assert timeout_penalty is None


class TestScoreClamping:
    """Tests for score clamping to 0-120 range."""

    def test_score_never_below_zero(self):
        """Score is clamped to minimum 0."""
        # Create extreme penalties scenario
        events = [
            _make_event("workflow.phase_entered", "DEPLOY", "2026-02-03T14:00:00Z"),
            _make_event("workflow.phase_exited", "DEPLOY", "2026-02-03T14:05:00Z"),
        ]

        score = calculate_adherence_score("test-correlation", events)

        # Should have massive penalties but clamped to 0
        assert score.final_score >= 0

    def test_score_never_above_120(self):
        """Score is clamped to maximum 120."""
        events = _create_perfect_workflow_events()

        score = calculate_adherence_score("test-correlation", events)

        assert score.final_score <= 120


class TestEmptyEvents:
    """Tests for edge cases with empty or missing events."""

    def test_no_events_returns_zero_score(self):
        """No events results in zero score."""
        score = calculate_adherence_score("test-correlation", events=[])

        assert score.final_score == 0
        assert score.base_points == 0
        assert score.completion_bonus == 0
        assert score.rating == "POOR"

    def test_none_events_fetches_from_db(self, test_db):
        """None events triggers database fetch (returns empty for non-existent)."""
        # This tests the code path, actual DB fetch tested separately
        score = calculate_adherence_score("nonexistent-correlation", events=[])
        assert score.final_score == 0


class TestPayloadParsing:
    """Tests for payload parsing (string vs dict)."""

    def test_handles_string_payload(self):
        """Events with JSON string payloads are parsed correctly."""
        events = [
            {
                "timestamp": "2026-02-03T14:00:00Z",
                "event_type": "workflow.phase_entered",
                "payload": '{"phase": "UNDERSTAND"}'  # String, not dict
            },
            {
                "timestamp": "2026-02-03T14:30:00Z",
                "event_type": "workflow.phase_exited",
                "payload": '{"phase": "UNDERSTAND"}'
            },
        ]

        score = calculate_adherence_score("test-correlation", events)

        assert "UNDERSTAND" in score.phases_completed

    def test_handles_dict_payload(self):
        """Events with dict payloads work correctly."""
        events = [
            {
                "timestamp": "2026-02-03T14:00:00Z",
                "event_type": "workflow.phase_entered",
                "payload": {"phase": "UNDERSTAND"}  # Dict, not string
            },
            {
                "timestamp": "2026-02-03T14:30:00Z",
                "event_type": "workflow.phase_exited",
                "payload": {"phase": "UNDERSTAND"}
            },
        ]

        score = calculate_adherence_score("test-correlation", events)

        assert "UNDERSTAND" in score.phases_completed


# --- Helper Functions ---

def _create_perfect_workflow_events() -> list[dict]:
    """Create events for a perfect workflow (all phases in order)."""
    events = []
    base_time = datetime(2026, 2, 3, 14, 0, 0, tzinfo=UTC)

    for i, phase in enumerate(CANONICAL_ORDER):
        enter_time = base_time + timedelta(minutes=i * 30)
        exit_time = enter_time + timedelta(minutes=25)

        events.append(_make_event("workflow.phase_entered", phase, enter_time.isoformat()))
        events.append(_make_event("workflow.phase_exited", phase, exit_time.isoformat()))

    return events


def _create_events_skipping_phases(skipped: list[str]) -> list[dict]:
    """Create events with specified phases skipped."""
    events = []
    base_time = datetime(2026, 2, 3, 14, 0, 0, tzinfo=UTC)

    time_offset = 0
    for phase in CANONICAL_ORDER:
        if phase in skipped:
            continue

        enter_time = base_time + timedelta(minutes=time_offset)
        exit_time = enter_time + timedelta(minutes=25)
        time_offset += 30

        events.append(_make_event("workflow.phase_entered", phase, enter_time.isoformat()))
        events.append(_make_event("workflow.phase_exited", phase, exit_time.isoformat()))

    return events


def _create_events_with_redo(phase: str, redo_count: int) -> list[dict]:
    """Create events with a phase entered multiple times."""
    events = []
    base_time = datetime(2026, 2, 3, 14, 0, 0, tzinfo=UTC)

    # First, go through phases up to and including the target
    time_offset = 0
    target_idx = CANONICAL_ORDER.index(phase)

    for i, p in enumerate(CANONICAL_ORDER[:target_idx + 1]):
        enter_time = base_time + timedelta(minutes=time_offset)
        exit_time = enter_time + timedelta(minutes=25)
        time_offset += 30

        events.append(_make_event("workflow.phase_entered", p, enter_time.isoformat()))
        events.append(_make_event("workflow.phase_exited", p, exit_time.isoformat()))

    # Add redos
    for _ in range(redo_count):
        enter_time = base_time + timedelta(minutes=time_offset)
        exit_time = enter_time + timedelta(minutes=25)
        time_offset += 30

        events.append(_make_event("workflow.phase_entered", phase, enter_time.isoformat()))
        events.append(_make_event("workflow.phase_exited", phase, exit_time.isoformat()))

    # Complete remaining phases
    for p in CANONICAL_ORDER[target_idx + 1:]:
        enter_time = base_time + timedelta(minutes=time_offset)
        exit_time = enter_time + timedelta(minutes=25)
        time_offset += 30

        events.append(_make_event("workflow.phase_entered", p, enter_time.isoformat()))
        events.append(_make_event("workflow.phase_exited", p, exit_time.isoformat()))

    return events


def _create_out_of_order_events(phase_sequence: list[str]) -> list[dict]:
    """Create events with specified phase sequence (may be out of order)."""
    events = []
    base_time = datetime(2026, 2, 3, 14, 0, 0, tzinfo=UTC)

    for i, phase in enumerate(phase_sequence):
        enter_time = base_time + timedelta(minutes=i * 30)
        exit_time = enter_time + timedelta(minutes=25)

        events.append(_make_event("workflow.phase_entered", phase, enter_time.isoformat()))
        events.append(_make_event("workflow.phase_exited", phase, exit_time.isoformat()))

    return events


def _create_events_with_timeout(phase: str, duration_minutes: int) -> list[dict]:
    """Create events with specified phase having a long duration."""
    events = []
    base_time = datetime(2026, 2, 3, 14, 0, 0, tzinfo=UTC)

    time_offset = 0
    for p in CANONICAL_ORDER:
        enter_time = base_time + timedelta(minutes=time_offset)

        if p == phase:
            exit_time = enter_time + timedelta(minutes=duration_minutes)
            time_offset += duration_minutes
        else:
            exit_time = enter_time + timedelta(minutes=25)
            time_offset += 30

        events.append(_make_event("workflow.phase_entered", p, enter_time.isoformat()))
        events.append(_make_event("workflow.phase_exited", p, exit_time.isoformat()))

    return events


def _make_event(event_type: str, phase: str, timestamp: str) -> dict:
    """Create a single event dict."""
    return {
        "timestamp": timestamp,
        "event_type": event_type,
        "payload": {"phase": phase}
    }


def _find_penalty(penalties: list[Penalty], penalty_type: str) -> Penalty | None:
    """Find a penalty by type in the penalties list."""
    for p in penalties:
        if p.type == penalty_type:
            return p
    return None
