"""
Unit tests for scripts/log-session.py

Tests cover:
- Directory structure validation (T1.x)
- Entry creation and formatting (T2.x)
- CLI argument parsing
- Event emission (GAP-5)
- Task ID handling (GAP-1)

Test IDs reference FS1_TEST_SUITE_ALPHA.md specifications.
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

# We need to handle the import carefully since the script uses dashes
import importlib.util

script_path = Path(__file__).parent.parent / 'scripts' / 'log-session.py'
spec = importlib.util.spec_from_file_location('log_session', script_path)
log_session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(log_session)


@pytest.mark.smoke
class TestDirectoryStructure:
    """Category 1: Directory Structure tests (T1.x)."""

    def test_memory_directory_exists(self, project_root: Path):
        """T1.1: memory/ directory exists in project root."""
        memory_dir = project_root / 'memory'
        assert memory_dir.exists(), 'memory/ directory should exist'
        assert memory_dir.is_dir(), 'memory/ should be a directory'

    def test_gitkeep_exists(self, project_root: Path):
        """T1.2: memory/ contains .gitkeep for git tracking."""
        memory_dir = project_root / 'memory'
        gitkeep = memory_dir / '.gitkeep'
        assert gitkeep.exists(), '.gitkeep should exist in memory/'

    def test_memory_not_gitignored(self, project_root: Path):
        """T1.3: memory/ is not in .gitignore."""
        gitignore = project_root / '.gitignore'
        if gitignore.exists():
            content = gitignore.read_text()
            lines = [line.strip() for line in content.split('\n')]
            assert 'memory/' not in lines, 'memory/ should not be gitignored'
            assert 'memory' not in lines, 'memory should not be gitignored'

    def test_memory_directory_writable(self, memory_dir: Path):
        """T1.4: memory/ directory is writable."""
        test_file = memory_dir / '.test_write'
        try:
            test_file.write_text('test')
            assert test_file.exists()
        finally:
            test_file.unlink(missing_ok=True)


class TestScriptStructure:
    """Category 2a: Script existence and structure tests."""

    def test_log_session_script_exists(self, project_root: Path):
        """T2.1: scripts/log-session.py exists."""
        script = project_root / 'scripts' / 'log-session.py'
        assert script.exists(), 'log-session.py should exist in scripts/'

    def test_script_has_pep723_header(self, project_root: Path):
        """T2.2: Script has valid PEP 723 inline metadata."""
        script = project_root / 'scripts' / 'log-session.py'
        content = script.read_text()
        assert '# /// script' in content, 'PEP 723 header start missing'
        assert 'requires-python' in content, 'requires-python missing'
        assert '# ///' in content, 'PEP 723 header end missing'


class TestSessionEntry:
    """Tests for SessionEntry creation and validation."""

    def test_session_entry_creation(self):
        """SessionEntry can be created with all fields."""
        entry = log_session.SessionEntry(
            timestamp=datetime.now(),
            task='Test task',
            outcome='SUCCESS',
            files=['file1.py', 'file2.py'],
            decisions=[('decision', 'rationale', 'affects')],
            learnings=['learned something'],
            improvements=['would do better'],
            issue='42',
            pr='45',
            task_id='TASK-1',
        )

        assert entry.task == 'Test task'
        assert entry.outcome == 'SUCCESS'
        assert len(entry.files) == 2
        assert len(entry.decisions) == 1
        assert entry.task_id == 'TASK-1'

    def test_session_entry_with_empty_fields(self):
        """SessionEntry works with empty optional fields."""
        entry = log_session.SessionEntry(
            timestamp=datetime.now(),
            task='Minimal task',
            outcome='SUCCESS',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='',
        )

        assert entry.task == 'Minimal task'
        assert entry.files == []
        assert entry.task_id == ''


class TestEntryValidation:
    """Tests for entry validation logic."""

    def test_validate_empty_task_warns(self):
        """Validation warns on empty task."""
        entry = log_session.SessionEntry(
            timestamp=datetime.now(),
            task='',
            outcome='SUCCESS',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='',
        )

        warnings = log_session.validate_entry(entry)
        assert any('Task description is empty' in w for w in warnings)

    def test_validate_unknown_outcome_warns(self):
        """Validation warns on unknown outcome."""
        entry = log_session.SessionEntry(
            timestamp=datetime.now(),
            task='Test',
            outcome='UNKNOWN',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='',
        )

        warnings = log_session.validate_entry(entry)
        assert any('Unknown outcome' in w for w in warnings)

    def test_validate_valid_outcomes_no_warn(self):
        """Valid outcomes (SUCCESS, FAILURE, PARTIAL) don't warn."""
        for outcome in ['SUCCESS', 'FAILURE', 'PARTIAL']:
            entry = log_session.SessionEntry(
                timestamp=datetime.now(),
                task='Test',
                outcome=outcome,
                files=[],
                decisions=[],
                learnings=[],
                improvements=[],
                issue='',
                pr='',
                task_id='',
            )

            warnings = log_session.validate_entry(entry)
            assert not any('Unknown outcome' in w for w in warnings)

    def test_validate_unusual_task_id_warns(self):
        """Validation warns on unusual task_id format."""
        entry = log_session.SessionEntry(
            timestamp=datetime.now(),
            task='Test',
            outcome='SUCCESS',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='invalid-format',
        )

        warnings = log_session.validate_entry(entry)
        assert any('unusual format' in w for w in warnings)

    def test_validate_valid_task_id_no_warn(self):
        """Valid task_id format (e.g., TASK-42) doesn't warn."""
        entry = log_session.SessionEntry(
            timestamp=datetime.now(),
            task='Test',
            outcome='SUCCESS',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='TASK-42',
        )

        warnings = log_session.validate_entry(entry)
        assert not any('unusual format' in w for w in warnings)


@pytest.mark.smoke
class TestMarkdownFormatting:
    """Tests for markdown entry formatting."""

    def test_format_basic_entry(self):
        """T2.4: Basic entry formatting works."""
        entry = log_session.SessionEntry(
            timestamp=datetime(2026, 2, 2, 10, 30, 0),
            task='Test task',
            outcome='SUCCESS',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='',
        )

        markdown = log_session.format_markdown(entry)

        assert '## [2026-02-02T10:30:00] Task: Test task' in markdown
        assert '**Outcome**: SUCCESS' in markdown
        assert '---' in markdown  # Entry separator

    def test_format_entry_with_task_id(self):
        """T2.7: Entry includes task_id when provided (GAP-1)."""
        entry = log_session.SessionEntry(
            timestamp=datetime(2026, 2, 2, 10, 30, 0),
            task='Test task',
            outcome='SUCCESS',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='TASK-42',
        )

        markdown = log_session.format_markdown(entry)

        assert '**Task ID**: TASK-42' in markdown

    def test_format_entry_without_task_id(self):
        """T2.8: Entry omits task_id line when not provided."""
        entry = log_session.SessionEntry(
            timestamp=datetime(2026, 2, 2, 10, 30, 0),
            task='Test task',
            outcome='SUCCESS',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='',
        )

        markdown = log_session.format_markdown(entry)

        assert '**Task ID**' not in markdown

    def test_format_entry_with_files(self):
        """Entry includes file count and names."""
        entry = log_session.SessionEntry(
            timestamp=datetime(2026, 2, 2, 10, 30, 0),
            task='Test task',
            outcome='SUCCESS',
            files=['file1.py', 'file2.sql', 'file3.md'],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='',
        )

        markdown = log_session.format_markdown(entry)

        assert '**Files Modified**: 3' in markdown
        assert 'file1.py' in markdown

    def test_format_entry_with_many_files(self):
        """Entry shows count only for >5 files."""
        entry = log_session.SessionEntry(
            timestamp=datetime(2026, 2, 2, 10, 30, 0),
            task='Test task',
            outcome='SUCCESS',
            files=[f'file{i}.py' for i in range(10)],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='',
        )

        markdown = log_session.format_markdown(entry)

        assert '**Files Modified**: 10' in markdown
        # Should NOT list all 10 files
        assert 'file9.py' not in markdown

    def test_format_entry_with_decisions(self):
        """Entry includes formatted decisions."""
        entry = log_session.SessionEntry(
            timestamp=datetime(2026, 2, 2, 10, 30, 0),
            task='Test task',
            outcome='SUCCESS',
            files=[],
            decisions=[
                ('Use incremental', 'Performance', 'marts/'),
                ('Star schema', 'Easier queries', ''),
            ],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='',
        )

        markdown = log_session.format_markdown(entry)

        assert '**Key Decisions**:' in markdown
        assert '- Use incremental: Performance (affects: marts/)' in markdown
        assert '- Star schema: Easier queries' in markdown

    def test_format_entry_with_learnings(self):
        """Entry includes learnings."""
        entry = log_session.SessionEntry(
            timestamp=datetime(2026, 2, 2, 10, 30, 0),
            task='Test task',
            outcome='SUCCESS',
            files=[],
            decisions=[],
            learnings=['Learning 1', 'Learning 2'],
            improvements=[],
            issue='',
            pr='',
            task_id='',
        )

        markdown = log_session.format_markdown(entry)

        assert '**Learnings**:' in markdown
        assert '- Learning 1' in markdown
        assert '- Learning 2' in markdown

    def test_format_entry_with_related(self):
        """Entry includes related issue and PR."""
        entry = log_session.SessionEntry(
            timestamp=datetime(2026, 2, 2, 10, 30, 0),
            task='Test task',
            outcome='SUCCESS',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='142',
            pr='145',
            task_id='',
        )

        markdown = log_session.format_markdown(entry)

        assert '**Related**:' in markdown
        assert 'Issue: #142' in markdown
        assert 'PR: #145' in markdown


@pytest.mark.smoke
class TestEventEmission:
    """Tests for events.jsonl emission (GAP-5)."""

    def test_events_jsonl_created(self, memory_dir_with_claude_md: Path, monkeypatch):
        """T2.9: events.jsonl is created after session log."""
        # Change to temp directory so get_memory_dir finds CLAUDE.md
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        entry = log_session.SessionEntry(
            timestamp=datetime.now(UTC),
            task='Test task',
            outcome='SUCCESS',
            files=['file.py'],
            decisions=[],
            learnings=['learned something'],
            improvements=[],
            issue='',
            pr='',
            task_id='TASK-1',
        )

        log_session.emit_event(entry)

        events_file = memory_dir_with_claude_md / 'events.jsonl'
        assert events_file.exists(), 'events.jsonl should be created'

    def test_events_jsonl_format(self, memory_dir_with_claude_md: Path, monkeypatch):
        """T2.10: events.jsonl has correct JSON format."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        entry = log_session.SessionEntry(
            timestamp=datetime(2026, 2, 2, 10, 30, 0, tzinfo=UTC),
            task='Test task',
            outcome='SUCCESS',
            files=['file.py'],
            decisions=[('d1', 'r1', 'a1')],
            learnings=['learned'],
            improvements=['improve'],
            issue='42',
            pr='45',
            task_id='TASK-1',
        )

        log_session.emit_event(entry)

        events_file = memory_dir_with_claude_md / 'events.jsonl'
        line = events_file.read_text().strip()
        event = json.loads(line)

        assert event['event'] == 'session_logged'
        assert event['version'] == '1.0'
        assert 'timestamp' in event
        assert event['data']['task'] == 'Test task'
        assert event['data']['task_id'] == 'TASK-1'
        assert event['data']['outcome'] == 'SUCCESS'
        assert event['data']['files_modified'] == 1
        assert event['data']['decisions_count'] == 1
        assert event['data']['learnings_count'] == 1
        assert event['data']['improvements_count'] == 1
        assert event['data']['related_issue'] == '#42'
        assert event['data']['related_pr'] == '#45'

    def test_events_null_task_id(self, memory_dir_with_claude_md: Path, monkeypatch):
        """I1.3: Sessions without task_id have null in JSON."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        entry = log_session.SessionEntry(
            timestamp=datetime.now(UTC),
            task='Ad-hoc task',
            outcome='SUCCESS',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='',
        )

        log_session.emit_event(entry)

        events_file = memory_dir_with_claude_md / 'events.jsonl'
        event = json.loads(events_file.read_text().strip())

        # task_id should be None (null in JSON), not empty string
        assert event['data']['task_id'] is None

    def test_events_append_only(self, memory_dir_with_claude_md: Path, monkeypatch):
        """I2.2: Events are appended, never overwritten."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        # Write first event
        entry1 = log_session.SessionEntry(
            timestamp=datetime.now(UTC),
            task='Task 1',
            outcome='SUCCESS',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='TASK-1',
        )
        log_session.emit_event(entry1)

        # Write second event
        entry2 = log_session.SessionEntry(
            timestamp=datetime.now(UTC),
            task='Task 2',
            outcome='FAILURE',
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue='',
            pr='',
            task_id='TASK-2',
        )
        log_session.emit_event(entry2)

        # Verify both events present
        events_file = memory_dir_with_claude_md / 'events.jsonl'
        lines = events_file.read_text().strip().split('\n')
        assert len(lines) == 2

        event1 = json.loads(lines[0])
        event2 = json.loads(lines[1])

        assert event1['data']['task'] == 'Task 1'
        assert event2['data']['task'] == 'Task 2'


class TestQuickMode:
    """Tests for quick mode entry creation."""

    def test_quick_mode_creates_entry(self, mock_git_unavailable):
        """T2.4: Quick mode creates minimal valid entry."""
        entry = log_session.gather_quick(task='Quick task', outcome='SUCCESS')

        assert entry.task == 'Quick task'
        assert entry.outcome == 'SUCCESS'
        assert entry.decisions == []
        assert entry.learnings == []
        assert entry.improvements == []

    def test_quick_mode_with_task_id(self, mock_git_unavailable):
        """Quick mode accepts task_id parameter."""
        entry = log_session.gather_quick(task='Quick task', outcome='SUCCESS', task_id='TASK-42')

        assert entry.task_id == 'TASK-42'

    def test_quick_mode_outcome_default(self, mock_git_unavailable):
        """Quick mode defaults to SUCCESS outcome."""
        entry = log_session.gather_quick(task='Quick task')

        assert entry.outcome == 'SUCCESS'


class TestTaskIdDetection:
    """Tests for automatic task_id detection from WORKFLOW_STATE.md."""

    def test_detect_task_id_from_workflow_state(self, tmp_path: Path, monkeypatch):
        """Task ID is detected from WORKFLOW_STATE.md."""
        # The detect_task_id function looks for temp/WORKFLOW_STATE.md relative to cwd
        # Create the temp directory in the location the function expects
        temp_dir = tmp_path / 'temp'
        temp_dir.mkdir()

        workflow_state = temp_dir / 'WORKFLOW_STATE.md'
        workflow_state.write_text("""# Workflow State

Task ID: TASK-99
**Phase**: BUILD
""")

        # Change to tmp_path so temp/WORKFLOW_STATE.md is found
        monkeypatch.chdir(tmp_path)

        task_id = log_session.detect_task_id()
        assert task_id == 'TASK-99'

    def test_detect_task_id_missing_file(self, tmp_path: Path, monkeypatch):
        """Returns None when WORKFLOW_STATE.md doesn't exist."""
        monkeypatch.chdir(tmp_path)

        task_id = log_session.detect_task_id()
        assert task_id is None

    def test_detect_task_id_no_match(self, tmp_path: Path, monkeypatch):
        """Returns None when no task pattern found."""
        temp_dir = tmp_path / 'temp'
        temp_dir.mkdir()

        workflow_state = temp_dir / 'WORKFLOW_STATE.md'
        workflow_state.write_text("""# Workflow State

No task information here.
""")

        monkeypatch.chdir(tmp_path)

        task_id = log_session.detect_task_id()
        assert task_id is None


class TestModifiedFilesDetection:
    """Tests for git modified files detection."""

    def test_get_modified_files_success(self, mock_git_modified_files):
        """Modified files are retrieved from git."""
        files = log_session.get_modified_files()

        assert len(files) == 2
        assert 'models/staging/stg_patients.sql' in files
        assert 'models/marts/dim_patients.sql' in files

    def test_get_modified_files_git_unavailable(self, mock_git_unavailable):
        """Empty list returned when git unavailable."""
        files = log_session.get_modified_files()

        assert files == []


class TestMemoryDirDetection:
    """Tests for memory directory detection."""

    def test_get_memory_dir_creates_if_needed(self, memory_dir_with_claude_md: Path, monkeypatch):
        """Memory directory is created if it doesn't exist."""
        # Remove memory dir
        memory_dir_with_claude_md.rmdir()

        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        result = log_session.get_memory_dir()

        assert result.exists()
        assert result.is_dir()

    def test_get_memory_dir_not_found(self, tmp_path: Path, monkeypatch):
        """FileNotFoundError raised when project root not found."""
        # Create a temp dir without CLAUDE.md
        monkeypatch.chdir(tmp_path)

        with pytest.raises(FileNotFoundError, match='Could not find project root'):
            log_session.get_memory_dir()


class TestTodayLogPath:
    """Tests for today's log file path generation."""

    def test_get_today_log(self, memory_dir_with_claude_md: Path, monkeypatch):
        """Today's log path is correctly generated."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        today = datetime.now().strftime('%Y-%m-%d')
        expected = memory_dir_with_claude_md / f'{today}.md'

        result = log_session.get_today_log()

        assert result == expected
