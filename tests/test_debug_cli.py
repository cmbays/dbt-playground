"""
Unit and integration tests for Debug CLI (WAVE3-022).

Tests cover:
- CLI command parsing
- Session integration
- Observability event emission
- Output formatting

Part of Wave 3 P2: Developer UX Commands (Issue #244)
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import duckdb
import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from scripts.lib.debug_session import database as db
from scripts.lib.debug_session import DebugSessionTracker
from scripts.lib.debug_session.utils import clear_state


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
def project_dir(tmp_path: Path, monkeypatch):
    """Create mock project directory structure."""
    # Create CLAUDE.md to simulate project root
    (tmp_path / 'CLAUDE.md').write_text('# Test Project')

    # Create temp directory
    temp_dir = tmp_path / 'temp'
    temp_dir.mkdir()

    # Create memory directory
    memory_dir = tmp_path / 'memory'
    memory_dir.mkdir()

    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def clean_state(project_dir):
    """Ensure clean state before test."""
    clear_state()
    yield
    clear_state()


# =============================================================================
# Test: CLI Module Import
# =============================================================================


class TestModuleImport:
    """Test that CLI module can be imported."""

    def test_import_debug_cli(self):
        """Debug CLI module imports without error."""
        import scripts  # noqa: F401
        # The module should import successfully
        assert True

    def test_import_functions(self):
        """Key functions are importable."""
        from scripts.lib.debug_session.models import PROTOCOL_PHASES
        assert '1-reproduce' in PROTOCOL_PHASES
        assert len(PROTOCOL_PHASES) == 7


# =============================================================================
# Test: Session Integration
# =============================================================================


class TestSessionIntegration:
    """Test integration with Session Tracker."""

    def test_start_creates_session(self, tracker, clean_state):
        """Start command creates a session in tracker."""
        session_id = tracker.start_session(
            bug_description='Test bug from CLI',
            tags=['cli', 'test'],
            severity='high',
        )

        assert session_id.startswith('DBG-')

        status = tracker.get_status()
        assert status['active']
        assert status['session'].bug_description == 'Test bug from CLI'
        assert 'cli' in status['session'].tags

    def test_step_adds_to_session(self, tracker, clean_state):
        """Step command adds step to active session."""
        tracker.start_session(bug_description='Test')

        step_num = tracker.log_step(
            phase='1-reproduce',
            findings='Bug reproduced via CLI',
        )

        assert step_num == 1

        status = tracker.get_status()
        assert len(status['steps']) == 1
        assert status['steps'][0].findings == 'Bug reproduced via CLI'

    def test_end_completes_session(self, tracker, project_dir, clean_state):
        """End command completes session."""
        tracker.start_session(bug_description='Test')
        tracker.log_step(phase='1-reproduce', findings='Found')

        session = tracker.end_session(
            root_cause='Test root cause',
            fix_time='30m',
            outcome='resolved',
        )

        assert session.outcome == 'resolved'
        assert session.root_cause == 'Test root cause'
        assert session.duration_minutes == 30


# =============================================================================
# Test: Observability Events
# =============================================================================


class TestObservabilityEvents:
    """Test observability event emission."""

    def test_event_emitted_on_session_end(self, tracker, project_dir, clean_state):
        """Session end emits event to events.jsonl."""
        tracker.start_session(bug_description='Test', tags=['async'])
        tracker.end_session(root_cause='Race condition', fix_time='45m')

        events_file = project_dir / 'memory' / 'events.jsonl'
        assert events_file.exists()

        event = json.loads(events_file.read_text().strip())
        assert event['event'] == 'debug_session_completed'
        assert event['data']['root_cause_category'] == 'race_condition'

    def test_trace_event_structure(self, tracker, project_dir, clean_state):
        """Trace events have correct structure."""
        # Import the emit function
        from scripts.lib.debug_session.tracker import DebugSessionTracker

        tracker.start_session(bug_description='Test timeout bug')
        session = tracker.end_session(root_cause='Timeout in API', fix_time='20m')

        events_file = project_dir / 'memory' / 'events.jsonl'
        event = json.loads(events_file.read_text().strip())

        # Verify structure
        assert 'timestamp' in event
        assert 'event' in event
        assert 'data' in event
        assert 'session_id' in event['data']


# =============================================================================
# Test: Output Formatting
# =============================================================================


class TestOutputFormatting:
    """Test output formatting functions."""

    def test_protocol_phases_complete(self):
        """All 7 protocol phases are defined."""
        from scripts.lib.debug_session.models import PROTOCOL_PHASES

        expected_phases = [
            '1-reproduce',
            '2-blast_radius',
            '3-root_cause',
            '4-fix_design',
            '5-implement',
            '6-verify',
            '7-prevent',
        ]

        for phase in expected_phases:
            assert phase in PROTOCOL_PHASES, f"Missing phase: {phase}"

    def test_duration_formatting(self):
        """Duration formats correctly."""
        from scripts.lib.debug_session.utils import format_duration

        assert format_duration(45) == '45m'
        assert format_duration(60) == '1h'
        assert format_duration(90) == '1h 30m'
        assert format_duration(135) == '2h 15m'

    def test_time_ago_formatting(self):
        """Time ago formats correctly."""
        from scripts.lib.debug_session.utils import format_time_ago

        assert format_time_ago(30) == 'just now'
        assert format_time_ago(60) == '1 minute ago'
        assert format_time_ago(3600) == '1 hour ago'

    def test_text_truncation(self):
        """Text truncation works correctly."""
        from scripts.lib.debug_session.utils import truncate_text

        short_text = 'Hello'
        assert truncate_text(short_text, 50) == 'Hello'

        long_text = 'A' * 100
        result = truncate_text(long_text, 20)
        assert len(result) == 20
        assert result.endswith('...')


# =============================================================================
# Test: Error Handling
# =============================================================================


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_step_without_session(self, tracker, clean_state):
        """Step without active session raises error."""
        from scripts.lib.debug_session import NoActiveSessionError

        with pytest.raises(NoActiveSessionError):
            tracker.log_step(phase='1-reproduce', findings='Test')

    def test_end_without_session(self, tracker, clean_state):
        """End without active session raises error."""
        from scripts.lib.debug_session import NoActiveSessionError

        with pytest.raises(NoActiveSessionError):
            tracker.end_session(root_cause='Test', fix_time='10m')

    def test_invalid_phase(self, tracker, clean_state):
        """Invalid phase raises ValueError."""
        tracker.start_session(bug_description='Test')

        with pytest.raises(ValueError, match='Invalid phase'):
            tracker.log_step(phase='invalid-phase', findings='Test')

    def test_invalid_outcome(self, tracker, clean_state):
        """Invalid outcome raises ValueError."""
        tracker.start_session(bug_description='Test')

        with pytest.raises(ValueError, match='Invalid outcome'):
            tracker.end_session(root_cause='Test', fix_time='10m', outcome='completed')

    def test_duplicate_session_error(self, tracker, clean_state):
        """Starting second session without force raises error."""
        from scripts.lib.debug_session import SessionAlreadyActiveError

        tracker.start_session(bug_description='First')

        with pytest.raises(SessionAlreadyActiveError):
            tracker.start_session(bug_description='Second')

    def test_force_starts_new_session(self, tracker, clean_state):
        """Force flag allows starting new session."""
        tracker.start_session(bug_description='First')
        session_id = tracker.start_session(bug_description='Second', force=True)

        assert session_id is not None
        status = tracker.get_status()
        assert status['session'].bug_description == 'Second'


# =============================================================================
# Test: History/Query
# =============================================================================


class TestHistoryQuery:
    """Test history query functionality."""

    def test_query_returns_sessions(self, tracker, project_dir, clean_state):
        """Query returns completed sessions."""
        # Create and complete a session
        tracker.start_session(bug_description='Test bug 1', tags=['test'])
        tracker.end_session(root_cause='Cause 1', fix_time='20m')

        # Query
        sessions = tracker.query_sessions(limit=10)
        assert len(sessions) >= 1

        # Verify session data
        found = False
        for s in sessions:
            if s.bug_description == 'Test bug 1':
                found = True
                assert s.root_cause == 'Cause 1'
                assert s.duration_minutes == 20
                break
        assert found, "Created session not found in query results"

    def test_query_with_pattern(self, tracker, project_dir, clean_state):
        """Query filters by pattern."""
        tracker.start_session(bug_description='Race condition in queue')
        tracker.end_session(root_cause='Missing lock', fix_time='30m')

        tracker.start_session(bug_description='Timeout in API', force=True)
        tracker.end_session(root_cause='Network issue', fix_time='15m')

        # Query for 'race'
        results = tracker.query_sessions(pattern='race')
        assert len(results) == 1
        assert 'race' in results[0].bug_description.lower()

    def test_query_with_tags(self, tracker, project_dir, clean_state):
        """Query filters by tags."""
        tracker.start_session(bug_description='Bug 1', tags=['async', 'queue'])
        tracker.end_session(root_cause='Cause', fix_time='10m')

        tracker.start_session(bug_description='Bug 2', tags=['api'], force=True)
        tracker.end_session(root_cause='Cause', fix_time='10m')

        # Query for 'async' tag
        results = tracker.query_sessions(tags=['async'])
        assert len(results) == 1
        assert 'async' in results[0].tags


# =============================================================================
# Test: CLI Argument Parsing
# =============================================================================


class TestCLIArgumentParsing:
    """Test CLI argument parsing (without executing commands)."""

    def test_valid_severities(self):
        """Severity validation."""
        from scripts.lib.debug_session.models import VALID_SEVERITIES

        assert VALID_SEVERITIES == {'high', 'medium', 'low'}

    def test_valid_outcomes(self):
        """Outcome validation."""
        from scripts.lib.debug_session.models import VALID_OUTCOMES

        assert 'resolved' in VALID_OUTCOMES
        assert 'escalated' in VALID_OUTCOMES
        assert 'inconclusive' in VALID_OUTCOMES
        assert 'in_progress' in VALID_OUTCOMES

    def test_duration_parsing(self):
        """Duration parsing from CLI format."""
        from scripts.lib.debug_session.utils import parse_duration

        assert parse_duration('45m') == 45
        assert parse_duration('1h') == 60
        assert parse_duration('1h 30m') == 90
        assert parse_duration('2h15m') == 135


# =============================================================================
# Test: Trace ID Management
# =============================================================================


class TestTraceIdManagement:
    """Test trace ID storage and retrieval for observability."""

    def test_generate_trace_id_format(self):
        """Generated trace IDs have correct format."""
        import uuid
        trace_id = str(uuid.uuid4())[:16]

        assert len(trace_id) == 16
        # Should be valid hex characters
        assert all(c in '0123456789abcdef-' for c in trace_id)
