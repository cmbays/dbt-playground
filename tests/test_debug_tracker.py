"""
Unit and integration tests for Debug Session Tracker (WAVE3-020).

Tests cover:
- Session lifecycle (start, log, end)
- Database operations
- CLI argument parsing
- Error handling
- Event emission

Part of Wave 3 P1: Protocol Enhancements (Issue #237)
"""

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import duckdb
import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from scripts.lib.debug_session import (
    DatabaseConnectionError,
    DebugSession,
    DebugSessionError,
    DebugSessionTracker,
    DebugStep,
    NoActiveSessionError,
    SessionAlreadyActiveError,
    SessionState,
    ValidationError,
)
from scripts.lib.debug_session import database as db
from scripts.lib.debug_session.models import PROTOCOL_PHASES, VALID_OUTCOMES, VALID_SEVERITIES
from scripts.lib.debug_session.utils import (
    clear_state,
    format_duration,
    format_time_ago,
    load_state,
    parse_duration,
    save_state,
    truncate_text,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_db(tmp_path: Path):
    """Create temporary DuckDB for testing."""
    db_path = tmp_path / 'test_debug.duckdb'
    conn = duckdb.connect(str(db_path))
    conn.execute(db.SCHEMA_SQL)
    return conn


@pytest.fixture
def tracker(temp_db):
    """Create tracker with temp database."""
    return DebugSessionTracker(conn=temp_db)


@pytest.fixture
def seeded_db(temp_db):
    """Seed database with test sessions."""
    sessions = [
        ('DBG-2026-02-01-001', 'Race condition in queue', 'Missing mutex lock', ['async', 'queue'], 'resolved', 45, 3),
        ('DBG-2026-02-02-001', 'API timeout', 'N+1 query pattern', ['api', 'performance'], 'resolved', 80, 2),
        ('DBG-2026-02-03-001', 'Null pointer exception', 'Missing null check', ['validation'], 'resolved', 20, 1),
    ]

    for sid, desc, cause, tags, outcome, duration, days_ago in sessions:
        # Calculate start_time in Python to avoid DuckDB interval parameter issue
        start_time = datetime.now(UTC) - timedelta(days=days_ago)
        temp_db.execute(
            """
            INSERT INTO debug_sessions
            (session_id, bug_description, root_cause, tags, outcome, duration_minutes, start_time, severity)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'medium')
            """,
            [sid, desc, cause, tags, outcome, duration, start_time],
        )

    return temp_db


@pytest.fixture
def memory_dir_for_events(tmp_path: Path, monkeypatch):
    """Create memory directory structure for event emission."""
    # Create CLAUDE.md to simulate project root
    (tmp_path / 'CLAUDE.md').write_text('# Test Project')
    memory_dir = tmp_path / 'memory'
    memory_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    return memory_dir


@pytest.fixture
def state_dir(tmp_path: Path, monkeypatch):
    """Create temp directory for state file."""
    (tmp_path / 'CLAUDE.md').write_text('# Test')
    (tmp_path / 'temp').mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path / 'temp'


# =============================================================================
# Unit Tests: Models
# =============================================================================


class TestDebugStepModel:
    """Tests for DebugStep data class."""

    def test_valid_step_creation(self):
        """Step can be created with valid phase."""
        step = DebugStep(
            session_id='DBG-2026-02-04-001',
            step_number=1,
            timestamp=datetime.now(UTC),
            protocol_phase='1-reproduce',
            findings='Bug reproduced successfully',
        )
        assert step.protocol_phase == '1-reproduce'

    def test_invalid_phase_raises(self):
        """Invalid phase raises ValueError."""
        with pytest.raises(ValueError, match='Invalid phase'):
            DebugStep(
                session_id='DBG-2026-02-04-001',
                step_number=1,
                timestamp=datetime.now(UTC),
                protocol_phase='invalid-phase',
                findings='Test',
            )

    def test_all_valid_phases(self):
        """All 7 protocol phases are valid."""
        for phase in PROTOCOL_PHASES:
            step = DebugStep(
                session_id='test',
                step_number=1,
                timestamp=datetime.now(UTC),
                protocol_phase=phase,
                findings='Test',
            )
            assert step.protocol_phase == phase


class TestDebugSessionModel:
    """Tests for DebugSession data class."""

    def test_valid_session_creation(self):
        """Session can be created with defaults."""
        session = DebugSession(
            session_id='DBG-2026-02-04-001',
            bug_description='Test bug',
            start_time=datetime.now(UTC),
        )
        assert session.severity == 'medium'
        assert session.outcome == 'in_progress'
        assert session.tags == []

    def test_invalid_severity_raises(self):
        """Invalid severity raises ValueError."""
        with pytest.raises(ValueError, match='Invalid severity'):
            DebugSession(
                session_id='test',
                bug_description='Test',
                start_time=datetime.now(UTC),
                severity='critical',  # Not valid
            )

    def test_invalid_outcome_raises(self):
        """Invalid outcome raises ValueError."""
        with pytest.raises(ValueError, match='Invalid outcome'):
            DebugSession(
                session_id='test',
                bug_description='Test',
                start_time=datetime.now(UTC),
                outcome='completed',  # Not valid
            )


class TestSessionState:
    """Tests for SessionState data class."""

    def test_to_dict(self):
        """State converts to dict correctly."""
        state = SessionState(
            session_id='DBG-2026-02-04-001',
            start_time=datetime(2026, 2, 4, 10, 0, 0, tzinfo=UTC),
            step_count=3,
            last_phase='3-root_cause',
        )
        d = state.to_dict()
        assert d['session_id'] == 'DBG-2026-02-04-001'
        assert d['step_count'] == 3
        assert d['last_phase'] == '3-root_cause'

    def test_from_dict(self):
        """State can be created from dict."""
        d = {
            'session_id': 'DBG-2026-02-04-001',
            'start_time': '2026-02-04T10:00:00+00:00',
            'step_count': 3,
            'last_phase': '3-root_cause',
        }
        state = SessionState.from_dict(d)
        assert state.session_id == 'DBG-2026-02-04-001'
        assert state.step_count == 3


# =============================================================================
# Unit Tests: Utilities
# =============================================================================


class TestParseDuration:
    """Tests for duration parsing."""

    def test_parse_minutes_only(self):
        """Parse '45m' format."""
        assert parse_duration('45m') == 45

    def test_parse_hours_only(self):
        """Parse '2h' format."""
        assert parse_duration('2h') == 120

    def test_parse_hours_and_minutes(self):
        """Parse '1h 30m' format."""
        assert parse_duration('1h 30m') == 90

    def test_parse_hours_and_minutes_no_space(self):
        """Parse '2h15m' format."""
        assert parse_duration('2h15m') == 135

    def test_parse_just_number(self):
        """Parse '45' as minutes."""
        assert parse_duration('45') == 45

    def test_parse_case_insensitive(self):
        """Parse 'H' and 'M' formats."""
        assert parse_duration('2H 30M') == 150

    def test_parse_empty_raises(self):
        """Empty string raises ValidationError."""
        with pytest.raises(ValidationError, match='cannot be empty'):
            parse_duration('')

    def test_parse_invalid_raises(self):
        """Invalid format raises ValidationError."""
        with pytest.raises(ValidationError, match='Invalid duration format'):
            parse_duration('invalid')


class TestFormatDuration:
    """Tests for duration formatting."""

    def test_format_minutes_only(self):
        """Format small durations as minutes."""
        assert format_duration(45) == '45m'

    def test_format_exact_hour(self):
        """Format exact hours."""
        assert format_duration(60) == '1h'
        assert format_duration(120) == '2h'

    def test_format_hours_and_minutes(self):
        """Format hours with minutes."""
        assert format_duration(90) == '1h 30m'
        assert format_duration(135) == '2h 15m'


class TestFormatTimeAgo:
    """Tests for time ago formatting."""

    def test_just_now(self):
        """Recent times show 'just now'."""
        assert format_time_ago(30) == 'just now'

    def test_minutes(self):
        """Show minutes."""
        assert format_time_ago(300) == '5 minutes ago'
        assert format_time_ago(60) == '1 minute ago'

    def test_hours(self):
        """Show hours."""
        assert format_time_ago(3600) == '1 hour ago'
        assert format_time_ago(7200) == '2 hours ago'

    def test_days(self):
        """Show days."""
        assert format_time_ago(86400) == '1 day ago'
        assert format_time_ago(172800) == '2 days ago'


class TestTruncateText:
    """Tests for text truncation."""

    def test_short_text_unchanged(self):
        """Short text passes through."""
        assert truncate_text('short', 50) == 'short'

    def test_long_text_truncated(self):
        """Long text is truncated with ellipsis."""
        result = truncate_text('this is a very long text that should be truncated', 20)
        assert len(result) == 20
        assert result.endswith('...')


class TestStatePersistence:
    """Tests for state save/load."""

    def test_save_and_load_state(self, state_dir):
        """State persists correctly."""
        state = SessionState(
            session_id='DBG-2026-02-04-001',
            start_time=datetime(2026, 2, 4, 10, 0, 0, tzinfo=UTC),
            step_count=3,
            last_phase='3-root_cause',
        )
        save_state(state)

        loaded = load_state()
        assert loaded is not None
        assert loaded.session_id == state.session_id
        assert loaded.step_count == 3

    def test_clear_state(self, state_dir):
        """State can be cleared."""
        state = SessionState(
            session_id='test',
            start_time=datetime.now(UTC),
        )
        save_state(state)
        clear_state()

        assert load_state() is None

    def test_load_missing_state(self, state_dir):
        """Loading missing state returns None."""
        clear_state()
        assert load_state() is None


# =============================================================================
# Unit Tests: Database Operations
# =============================================================================


class TestDatabaseSchema:
    """Tests for database schema."""

    def test_tables_created(self, temp_db):
        """Schema creates required tables."""
        tables = temp_db.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
        table_names = [t[0] for t in tables]

        assert 'debug_sessions' in table_names
        assert 'debug_steps' in table_names

    def test_views_created(self, temp_db):
        """Schema creates required views."""
        # Check v_active_session exists and is queryable
        result = temp_db.execute('SELECT * FROM v_active_session').fetchall()
        assert result == []  # Empty but exists

        # Check v_session_summary exists
        result = temp_db.execute('SELECT * FROM v_session_summary').fetchall()
        assert result == []


class TestDatabaseOperations:
    """Tests for database CRUD operations."""

    def test_insert_and_get_session(self, temp_db):
        """Session can be inserted and retrieved."""
        session = DebugSession(
            session_id='DBG-2026-02-04-001',
            bug_description='Test bug',
            start_time=datetime.now(UTC),
            tags=['test'],
        )
        db.insert_session(temp_db, session)

        retrieved = db.get_session(temp_db, 'DBG-2026-02-04-001')
        assert retrieved is not None
        assert retrieved.bug_description == 'Test bug'
        assert 'test' in retrieved.tags

    def test_insert_and_get_step(self, temp_db):
        """Step can be inserted and retrieved."""
        # First create session
        session = DebugSession(
            session_id='DBG-2026-02-04-001',
            bug_description='Test',
            start_time=datetime.now(UTC),
        )
        db.insert_session(temp_db, session)

        # Add step
        step = DebugStep(
            session_id='DBG-2026-02-04-001',
            step_number=1,
            timestamp=datetime.now(UTC),
            protocol_phase='1-reproduce',
            findings='Bug reproduced',
        )
        db.insert_step(temp_db, step)

        steps = db.get_steps(temp_db, 'DBG-2026-02-04-001')
        assert len(steps) == 1
        assert steps[0].findings == 'Bug reproduced'

    def test_get_active_session(self, temp_db):
        """Active session can be retrieved."""
        session = DebugSession(
            session_id='DBG-2026-02-04-001',
            bug_description='Test',
            start_time=datetime.now(UTC),
            outcome='in_progress',
        )
        db.insert_session(temp_db, session)

        active = db.get_active_session(temp_db)
        assert active is not None
        assert active.session_id == 'DBG-2026-02-04-001'

    def test_query_by_pattern(self, seeded_db):
        """Sessions can be queried by pattern."""
        results = db.query_sessions(seeded_db, pattern='race')
        assert len(results) == 1
        assert 'race' in results[0].bug_description.lower()

    def test_query_by_tags(self, seeded_db):
        """Sessions can be queried by tags."""
        results = db.query_sessions(seeded_db, tags=['async'])
        assert len(results) == 1
        assert 'async' in results[0].tags


# =============================================================================
# Integration Tests: Tracker
# =============================================================================


class TestTrackerStartSession:
    """Tests for session start."""

    def test_start_creates_session(self, tracker):
        """Start creates a new session."""
        session_id = tracker.start_session(
            bug_description='Test bug',
            tags=['test'],
        )
        assert session_id.startswith('DBG-')

        status = tracker.get_status()
        assert status['active']
        assert status['session'].bug_description == 'Test bug'

    def test_start_with_active_raises(self, tracker):
        """Starting when session active raises error."""
        tracker.start_session(bug_description='First')

        with pytest.raises(SessionAlreadyActiveError):
            tracker.start_session(bug_description='Second')

    def test_start_with_force(self, tracker):
        """Force start ends existing session."""
        tracker.start_session(bug_description='First')
        session_id = tracker.start_session(bug_description='Second', force=True)

        assert session_id is not None
        status = tracker.get_status()
        assert status['active']
        assert status['session'].bug_description == 'Second'


class TestTrackerLogStep:
    """Tests for step logging."""

    def test_log_adds_step(self, tracker, state_dir):
        """Log adds step to session."""
        tracker.start_session(bug_description='Test')

        step_num = tracker.log_step(
            phase='1-reproduce',
            findings='Bug reproduced',
        )
        assert step_num == 1

        status = tracker.get_status()
        assert len(status['steps']) == 1

    def test_log_without_session_raises(self, tracker, state_dir):
        """Log without active session raises error."""
        # Ensure no leftover state
        clear_state()
        with pytest.raises(NoActiveSessionError):
            tracker.log_step(phase='1-reproduce', findings='Test')

    def test_log_updates_state(self, tracker, state_dir):
        """Log updates session state."""
        tracker.start_session(bug_description='Test')
        tracker.log_step(phase='1-reproduce', findings='Step 1')
        tracker.log_step(phase='2-blast_radius', findings='Step 2')

        state = load_state()
        assert state.step_count == 2
        assert state.last_phase == '2-blast_radius'


class TestTrackerEndSession:
    """Tests for session end."""

    def test_end_completes_session(self, tracker, state_dir, memory_dir_for_events):
        """End completes session with outcome."""
        tracker.start_session(bug_description='Test')
        tracker.log_step(phase='1-reproduce', findings='Reproduced')

        session = tracker.end_session(
            root_cause='Missing check',
            fix_time='30m',
            outcome='resolved',
        )

        assert session.outcome == 'resolved'
        assert session.duration_minutes == 30

        # State should be cleared
        assert load_state() is None

    def test_end_without_session_raises(self, tracker):
        """End without active session raises error."""
        with pytest.raises(NoActiveSessionError):
            tracker.end_session(root_cause='Test', fix_time='10m')

    def test_end_emits_event(self, tracker, state_dir, memory_dir_for_events):
        """End emits event to events.jsonl."""
        tracker.start_session(bug_description='Test', tags=['async'])
        session = tracker.end_session(
            root_cause='Race condition',
            fix_time='45m',
        )

        events_file = memory_dir_for_events / 'events.jsonl'
        assert events_file.exists()

        event = json.loads(events_file.read_text().strip())
        assert event['event'] == 'debug_session_completed'
        assert event['data']['session_id'] == session.session_id
        assert event['data']['root_cause_category'] == 'race_condition'


class TestTrackerQuery:
    """Tests for session queries."""

    def test_query_all(self, seeded_db):
        """Query returns all sessions."""
        tracker = DebugSessionTracker(conn=seeded_db)
        sessions = tracker.query_sessions(limit=10)
        assert len(sessions) == 3

    def test_query_with_filters(self, seeded_db):
        """Query filters work correctly."""
        tracker = DebugSessionTracker(conn=seeded_db)

        # By pattern
        results = tracker.query_sessions(pattern='timeout')
        assert len(results) == 1

        # By outcome
        results = tracker.query_sessions(outcome='resolved')
        assert len(results) == 3


class TestTrackerStatus:
    """Tests for status command."""

    def test_status_active_session(self, tracker, state_dir):
        """Status shows active session."""
        tracker.start_session(bug_description='Test bug', tags=['test'])

        status = tracker.get_status()
        assert status['active']
        assert 'session' in status
        assert 'elapsed_seconds' in status

    def test_status_no_session(self, tracker):
        """Status shows recent sessions when none active."""
        status = tracker.get_status()
        assert not status['active']
        assert 'recent_sessions' in status


# =============================================================================
# Integration Tests: Full Lifecycle
# =============================================================================


class TestFullLifecycle:
    """End-to-end lifecycle tests."""

    def test_complete_debug_session(self, tracker, state_dir, memory_dir_for_events):
        """Complete start -> log -> end lifecycle."""
        # Start
        session_id = tracker.start_session(
            bug_description='Race condition in worker queue',
            tags=['async', 'queue', 'timing'],
            severity='high',
        )
        assert session_id.startswith('DBG-')

        # Log steps
        tracker.log_step(
            phase='1-reproduce',
            findings='Reproduced: job runs twice when queue has >10 items',
        )
        tracker.log_step(
            phase='2-blast_radius',
            findings='Affects worker module and job scheduler',
        )
        tracker.log_step(
            phase='3-root_cause',
            findings='Missing lock on queue consumer',
        )
        tracker.log_step(
            phase='5-implement',
            findings='Added asyncio.Lock to prevent concurrent access',
        )
        tracker.log_step(
            phase='6-verify',
            findings='Tests passing, no more duplicate jobs',
        )

        # End
        session = tracker.end_session(
            root_cause='Missing mutex lock on queue consumer',
            resolution='Added asyncio.Lock to prevent concurrent access',
            fix_time='45m',
            outcome='resolved',
        )

        # Verify
        assert session.step_count == 5
        assert session.duration_minutes == 45
        assert session.outcome == 'resolved'

        # Check database
        details = tracker.get_session_details(session_id)
        assert details is not None
        assert len(details['steps']) == 5

        # Check event emitted
        events_file = memory_dir_for_events / 'events.jsonl'
        assert events_file.exists()


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error scenarios."""

    def test_session_already_active_error(self, tracker, state_dir):
        """SessionAlreadyActiveError contains session ID."""
        tracker.start_session(bug_description='First')

        with pytest.raises(SessionAlreadyActiveError) as exc_info:
            tracker.start_session(bug_description='Second')

        assert exc_info.value.session_id is not None

    def test_invalid_phase_error(self, tracker, state_dir):
        """Invalid phase gives helpful error."""
        tracker.start_session(bug_description='Test')

        with pytest.raises(ValueError, match='Invalid phase'):
            tracker.log_step(phase='invalid', findings='Test')

    def test_invalid_outcome_error(self, tracker, state_dir):
        """Invalid outcome gives helpful error."""
        tracker.start_session(bug_description='Test')

        with pytest.raises(ValueError, match='Invalid outcome'):
            tracker.end_session(root_cause='Test', fix_time='10m', outcome='completed')


# =============================================================================
# CLI Tests (using subprocess would be heavier, testing args parsing instead)
# =============================================================================


class TestCLIParsing:
    """Tests for CLI argument validation."""

    def test_valid_phases_enum(self):
        """All valid phases are in PROTOCOL_PHASES."""
        expected = {
            '1-reproduce',
            '2-blast_radius',
            '3-root_cause',
            '4-fix_design',
            '5-implement',
            '6-verify',
            '7-prevent',
        }
        assert set(PROTOCOL_PHASES.keys()) == expected

    def test_valid_outcomes_enum(self):
        """All valid outcomes are in VALID_OUTCOMES."""
        expected = {'resolved', 'escalated', 'inconclusive', 'in_progress'}
        assert VALID_OUTCOMES == expected

    def test_valid_severities_enum(self):
        """All valid severities are in VALID_SEVERITIES."""
        expected = {'high', 'medium', 'low'}
        assert VALID_SEVERITIES == expected
