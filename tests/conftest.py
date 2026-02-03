"""
Pytest configuration and fixtures for FS1 Agent Memory tests.

Provides shared fixtures for:
- Temporary memory directories
- Sample log entries
- Mock input/output
- Event file handling
"""

import json
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

# Add scripts directory to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS_DIR))

# Fixed date for deterministic tests (avoids timezone issues)
TEST_DATE = date(2026, 2, 15)
TEST_DATETIME = datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC)


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def memory_dir(tmp_path: Path) -> Path:
    """Create a temporary memory directory."""
    mem_dir = tmp_path / 'memory'
    mem_dir.mkdir()
    return mem_dir


@pytest.fixture
def memory_dir_with_claude_md(tmp_path: Path) -> Path:
    """Create a temp directory structure with CLAUDE.md for project detection."""
    # Create CLAUDE.md to simulate project root
    claude_md = tmp_path / 'CLAUDE.md'
    claude_md.write_text('# Test Project\n')

    # Create memory directory
    mem_dir = tmp_path / 'memory'
    mem_dir.mkdir()

    return mem_dir


@pytest.fixture
def sample_log_entry() -> str:
    """Return a sample markdown log entry."""
    return """## [2026-02-02T10:30:00] Task: Implement customer analytics

**Task ID**: TASK-42
**Outcome**: SUCCESS
**Files Modified**: 5 (models/marts/customer.sql, models/marts/orders.sql)

**Key Decisions**:
- Use incremental: Performance (affects: marts/)
- Star schema: Easier queries (affects: marts/)

**Learnings**:
- Incremental needs unique_key
- Star schema simplifies joins

**Would Do Differently**:
- Write tests first

**Related**:
- Issue: #142 | PR: #145

---
"""


@pytest.fixture
def sample_log_file(memory_dir: Path, sample_log_entry: str) -> Path:
    """Create a sample log file in the memory directory."""
    # Use fixed date for determinism
    date_str = TEST_DATE.isoformat()
    log_file = memory_dir / f'{date_str}.md'
    log_file.write_text(sample_log_entry)
    return log_file


@pytest.fixture
def multi_day_logs(memory_dir: Path) -> list[Path]:
    """Create log files for the past 5 days from a fixed date."""
    log_files = []

    for i in range(5):
        log_date = TEST_DATE - timedelta(days=i)
        date_str = log_date.isoformat()
        log_file = memory_dir / f'{date_str}.md'

        log_file.write_text(f"""## [{date_str}T10:00:00] Task: Task for day {i}

**Outcome**: SUCCESS
**Files Modified**: {i + 1}

**Key Decisions**:
- Decision {i}: Rationale (affects: component)

**Learnings**:
- Learning {i}
- Use incremental models for large tables

**Would Do Differently**:
- Nothing noted

---
""")
        log_files.append(log_file)

    return log_files


@pytest.fixture
def logs_with_recurring_pattern(memory_dir: Path) -> list[Path]:
    """Create log files with a recurring learning pattern (3+ occurrences)."""
    log_files = []
    recurring_learning = 'Always validate input before processing'

    for i in range(3):
        log_date = TEST_DATE - timedelta(days=i)
        date_str = log_date.isoformat()
        log_file = memory_dir / f'{date_str}.md'

        log_file.write_text(f"""## [{date_str}T10:00:00] Task: Task {i}

**Outcome**: SUCCESS

**Learnings**:
- {recurring_learning}
- Unique learning {i}

---
""")
        log_files.append(log_file)

    return log_files


@pytest.fixture
def sample_events_jsonl(memory_dir: Path) -> Path:
    """Create a sample events.jsonl file."""
    events_file = memory_dir / 'events.jsonl'

    events = [
        {
            'timestamp': '2026-02-02T10:30:00Z',
            'event': 'session_logged',
            'version': '1.0',
            'data': {
                'task': 'Implement customer analytics',
                'task_id': 'TASK-42',
                'outcome': 'SUCCESS',
                'files_modified': 5,
                'decisions_count': 2,
                'learnings_count': 2,
                'improvements_count': 1,
                'related_issue': '#142',
                'related_pr': '#145',
            },
        },
        {
            'timestamp': '2026-02-02T11:00:00Z',
            'event': 'session_logged',
            'version': '1.0',
            'data': {
                'task': 'Fix null handling',
                'task_id': None,
                'outcome': 'SUCCESS',
                'files_modified': 2,
                'decisions_count': 0,
                'learnings_count': 1,
                'improvements_count': 0,
                'related_issue': None,
                'related_pr': None,
            },
        },
    ]

    with open(events_file, 'w', encoding='utf-8') as f:
        for event in events:
            f.write(json.dumps(event) + '\n')

    return events_file


@pytest.fixture
def mock_git_modified_files(monkeypatch):
    """Mock git to return a list of modified files."""

    def mock_run(*args, **kwargs):
        class MockResult:
            stdout = 'models/staging/stg_patients.sql\nmodels/marts/dim_patients.sql\n'
            returncode = 0

        return MockResult()

    monkeypatch.setattr('subprocess.run', mock_run)


@pytest.fixture
def mock_git_unavailable(monkeypatch):
    """Mock git being unavailable."""

    def mock_run(*args, **kwargs):
        raise FileNotFoundError('git not found')

    monkeypatch.setattr('subprocess.run', mock_run)


@pytest.fixture
def workflow_state_file(tmp_path: Path) -> Path:
    """Create a mock WORKFLOW_STATE.md with task reference."""
    temp_dir = tmp_path / 'temp'
    temp_dir.mkdir()

    workflow_state = temp_dir / 'WORKFLOW_STATE.md'
    workflow_state.write_text("""# Workflow State

## Active Track: feat/customer-analytics

**Task ID**: TASK-99
**Phase**: BUILD
**Status**: In Progress
""")

    return workflow_state


# Helper functions for assertions
def read_events(events_file: Path) -> list[dict]:
    """Read all events from events.jsonl."""
    if not events_file.exists():
        return []

    events = []
    with open(events_file, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events


def count_entries_in_log(log_file: Path) -> int:
    """Count the number of log entries in a file."""
    if not log_file.exists():
        return 0

    content = log_file.read_text()
    return content.count('## [')
