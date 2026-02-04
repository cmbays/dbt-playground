"""FS5 Test Fixtures.

Provides common fixtures for testing the FS5 metrics module.

Version: v0.10.0
Created: 2026-02-03
"""

import json
import sys
import pytest
from pathlib import Path
from datetime import datetime, UTC, timedelta
import duckdb

# Add project root to path for fs5 and kanban imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def test_db(tmp_path):
    """Temporary DuckDB database with schema applied.

    Creates an in-memory style database in tmp_path with
    the full metrics schema applied.

    Yields:
        DuckDB connection with schema initialized.
    """
    db_path = tmp_path / "test_metrics.duckdb"
    schema_path = Path("database/metrics/schema/metrics-schema.sql")

    conn = duckdb.connect(str(db_path))
    if schema_path.exists():
        conn.execute(schema_path.read_text(encoding="utf-8"))
    yield conn
    conn.close()


@pytest.fixture
def mock_jsonl_dir(tmp_path):
    """Create mock JSONL directory structure.

    Sets up the expected directory structure for JSONL event files.

    Returns:
        Path to the temporary directory root.
    """
    (tmp_path / "memory").mkdir()
    (tmp_path / "temp" / "WORKFLOW_HISTORY").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def sample_memory_events():
    """Sample memory events for testing.

    Returns:
        List of event dictionaries matching memory/events.jsonl format.
    """
    return [
        {
            "timestamp": "2026-02-03T14:30:00Z",
            "event": "session_logged",
            "data": {
                "task": "Implemented feature X",
                "outcome": "SUCCESS",
                "session_id": "abc123",
                "correlation_id": "feat/test",
            },
        }
    ]


@pytest.fixture
def sample_chronicle_events():
    """Sample chronicle events for testing.

    Returns:
        List of event dictionaries matching chronicle events.jsonl format.
    """
    return [
        {
            "event_id": "evt-001",
            "timestamp": "2026-02-03T15:00:00Z",
            "event_type": "phase.entered",
            "correlation_id": "feat/test",
            "source": "workflow-hub",
            "data": {
                "phase": "BUILD",
                "previous_phase": "PLAN",
            },
        }
    ]


@pytest.fixture
def sample_qa_events():
    """Sample QA events for testing.

    Returns:
        List of event dictionaries matching QA_METRICS_LOG.jsonl format.
    """
    return [
        {
            "timestamp": "2026-02-03T16:00:00Z",
            "gate": "pre-commit",
            "status": "PASSED",
            "session_id": "sess-001",
            "reviewer": "qa-agent",
            "checks": ["lint", "test", "format"],
        }
    ]
