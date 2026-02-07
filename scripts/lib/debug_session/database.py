"""DuckDB database operations for Debug Session Tracker.

Handles schema creation, CRUD operations, and queries.
Per ADR-015, uses dedicated database at database/debug_sessions/debug_sessions.duckdb
"""

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

import duckdb

from scripts.lib.debug_session.exceptions import DatabaseConnectionError
from scripts.lib.debug_session.models import DebugSession, DebugStep

# Schema SQL
SCHEMA_SQL = """
-- Debug sessions table
CREATE TABLE IF NOT EXISTS debug_sessions (
    session_id VARCHAR PRIMARY KEY,
    bug_id VARCHAR,
    bug_description VARCHAR NOT NULL,
    severity VARCHAR DEFAULT 'medium',
    tags VARCHAR[],
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_minutes INTEGER,
    root_cause VARCHAR,
    resolution VARCHAR,
    outcome VARCHAR DEFAULT 'in_progress',
    step_count INTEGER DEFAULT 0,
    context VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Debug steps table
-- Note: Foreign key removed due to DuckDB update constraint issues
CREATE TABLE IF NOT EXISTS debug_steps (
    session_id VARCHAR NOT NULL,
    step_number INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    protocol_phase VARCHAR NOT NULL,
    findings TEXT NOT NULL,
    evidence VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id, step_number)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON debug_sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_sessions_outcome ON debug_sessions(outcome);
CREATE INDEX IF NOT EXISTS idx_steps_session ON debug_steps(session_id);

-- View for active session
CREATE OR REPLACE VIEW v_active_session AS
SELECT * FROM debug_sessions
WHERE outcome = 'in_progress'
ORDER BY start_time DESC
LIMIT 1;

-- View for session summary (used by WAVE3-021 Analyzer)
CREATE OR REPLACE VIEW v_session_summary AS
SELECT
    session_id,
    bug_description,
    DATE(start_time) as session_date,
    root_cause,
    outcome,
    duration_minutes,
    step_count,
    tags,
    CASE
        WHEN root_cause ILIKE '%race%' OR root_cause ILIKE '%concurrent%' THEN 'race_condition'
        WHEN root_cause ILIKE '%null%' OR root_cause ILIKE '%none%' THEN 'null_handling'
        WHEN root_cause ILIKE '%timeout%' THEN 'timeout'
        WHEN root_cause ILIKE '%state%' OR root_cause ILIKE '%corrupt%' THEN 'state_management'
        WHEN root_cause ILIKE '%import%' OR root_cause ILIKE '%module%' THEN 'import_error'
        WHEN root_cause ILIKE '%type%' OR root_cause ILIKE '%cast%' THEN 'type_error'
        ELSE 'other'
    END as pattern_category
FROM debug_sessions
WHERE outcome != 'in_progress';
"""


def get_db_path() -> Path:
    """Get database path, creating directory if needed."""
    # Find project root via CLAUDE.md
    for parent in [Path.cwd(), *Path.cwd().parents]:
        if (parent / 'CLAUDE.md').exists():
            db_dir = parent / 'database' / 'debug_sessions'
            db_dir.mkdir(parents=True, exist_ok=True)
            return db_dir / 'debug_sessions.duckdb'

    # Fallback to temp directory
    db_dir = Path('temp') / 'database' / 'debug_sessions'
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / 'debug_sessions.duckdb'


def connect(db_path: Optional[Path] = None) -> duckdb.DuckDBPyConnection:
    """Connect to DuckDB with recovery handling.

    Args:
        db_path: Optional path to database (uses default if not provided)

    Returns:
        DuckDB connection

    Raises:
        DatabaseConnectionError: If connection fails and cannot recover
    """
    if db_path is None:
        db_path = get_db_path()

    backup_path = db_path.with_suffix('.duckdb.bak')

    try:
        conn = duckdb.connect(str(db_path))

        # Check if schema exists
        result = conn.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'debug_sessions'"
        ).fetchone()

        if result[0] == 0:
            # Initialize schema
            conn.execute(SCHEMA_SQL)

        return conn

    except duckdb.IOException as e:
        # Attempt recovery from backup
        if backup_path.exists():
            try:
                shutil.copy(backup_path, db_path)
                return duckdb.connect(str(db_path))
            except OSError as backup_error:
                import logging
                logging.error(f'Failed to restore backup during recovery: {backup_error}')
        raise DatabaseConnectionError(f'Database corrupted and no backup: {e}') from e


def insert_session(conn: duckdb.DuckDBPyConnection, session: DebugSession) -> None:
    """Insert a new debug session."""
    conn.execute(
        """
        INSERT INTO debug_sessions
        (session_id, bug_id, bug_description, severity, tags, start_time,
         context, outcome, step_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            session.session_id,
            session.bug_id,
            session.bug_description,
            session.severity,
            session.tags,
            session.start_time,
            session.context,
            session.outcome,
            session.step_count,
        ],
    )


def update_session(conn: duckdb.DuckDBPyConnection, session: DebugSession) -> None:
    """Update an existing debug session."""
    conn.execute(
        """
        UPDATE debug_sessions SET
            end_time = ?,
            duration_minutes = ?,
            root_cause = ?,
            resolution = ?,
            outcome = ?,
            step_count = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE session_id = ?
        """,
        [
            session.end_time,
            session.duration_minutes,
            session.root_cause,
            session.resolution,
            session.outcome,
            session.step_count,
            session.session_id,
        ],
    )


def insert_step(conn: duckdb.DuckDBPyConnection, step: DebugStep) -> None:
    """Insert a debug step."""
    conn.execute(
        """
        INSERT INTO debug_steps
        (session_id, step_number, timestamp, protocol_phase, findings, evidence)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            step.session_id,
            step.step_number,
            step.timestamp,
            step.protocol_phase,
            step.findings,
            step.evidence,
        ],
    )


def _ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime has UTC timezone."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def get_active_session(conn: duckdb.DuckDBPyConnection) -> Optional[DebugSession]:
    """Get the current active session."""
    result = conn.execute('SELECT * FROM v_active_session').fetchone()
    if result is None:
        return None

    return DebugSession(
        session_id=result[0],
        bug_id=result[1],
        bug_description=result[2],
        severity=result[3],
        tags=result[4] or [],
        start_time=_ensure_utc(result[5]),
        end_time=_ensure_utc(result[6]),
        duration_minutes=result[7],
        root_cause=result[8],
        resolution=result[9],
        outcome=result[10],
        step_count=result[11],
        context=result[12],
    )


def get_session(conn: duckdb.DuckDBPyConnection, session_id: str) -> Optional[DebugSession]:
    """Get a session by ID."""
    result = conn.execute(
        'SELECT * FROM debug_sessions WHERE session_id = ?', [session_id]
    ).fetchone()
    if result is None:
        return None

    return DebugSession(
        session_id=result[0],
        bug_id=result[1],
        bug_description=result[2],
        severity=result[3],
        tags=result[4] or [],
        start_time=_ensure_utc(result[5]),
        end_time=_ensure_utc(result[6]),
        duration_minutes=result[7],
        root_cause=result[8],
        resolution=result[9],
        outcome=result[10],
        step_count=result[11],
        context=result[12],
    )


def get_steps(conn: duckdb.DuckDBPyConnection, session_id: str) -> list[DebugStep]:
    """Get all steps for a session."""
    results = conn.execute(
        """
        SELECT session_id, step_number, timestamp, protocol_phase, findings, evidence
        FROM debug_steps
        WHERE session_id = ?
        ORDER BY step_number
        """,
        [session_id],
    ).fetchall()

    return [
        DebugStep(
            session_id=row[0],
            step_number=row[1],
            timestamp=_ensure_utc(row[2]),
            protocol_phase=row[3],
            findings=row[4],
            evidence=row[5],
        )
        for row in results
    ]


def get_next_step_number(conn: duckdb.DuckDBPyConnection, session_id: str) -> int:
    """Get the next step number for a session."""
    result = conn.execute(
        'SELECT COALESCE(MAX(step_number), 0) + 1 FROM debug_steps WHERE session_id = ?',
        [session_id],
    ).fetchone()
    return result[0]


def query_sessions(
    conn: duckdb.DuckDBPyConnection,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    pattern: Optional[str] = None,
    tags: Optional[list[str]] = None,
    outcome: Optional[str] = None,
    limit: int = 20,
) -> list[DebugSession]:
    """Query sessions with filters."""
    query = 'SELECT * FROM debug_sessions WHERE 1=1'
    params = []

    if since:
        query += ' AND start_time >= ?'
        params.append(since)

    if until:
        query += ' AND start_time <= ?'
        params.append(until)

    if pattern:
        query += ' AND (root_cause ILIKE ? OR bug_description ILIKE ?)'
        pattern_param = f'%{pattern}%'
        params.extend([pattern_param, pattern_param])

    if tags:
        # Check if any of the provided tags exist in the session's tags array
        for tag in tags:
            query += ' AND list_contains(tags, ?)'
            params.append(tag)

    if outcome:
        query += ' AND outcome = ?'
        params.append(outcome)

    query += ' ORDER BY start_time DESC LIMIT ?'
    params.append(limit)

    results = conn.execute(query, params).fetchall()

    return [
        DebugSession(
            session_id=row[0],
            bug_id=row[1],
            bug_description=row[2],
            severity=row[3],
            tags=row[4] or [],
            start_time=_ensure_utc(row[5]),
            end_time=_ensure_utc(row[6]),
            duration_minutes=row[7],
            root_cause=row[8],
            resolution=row[9],
            outcome=row[10],
            step_count=row[11],
            context=row[12],
        )
        for row in results
    ]


def get_recent_sessions(conn: duckdb.DuckDBPyConnection, limit: int = 5) -> list[DebugSession]:
    """Get most recent sessions."""
    return query_sessions(conn, limit=limit)


def get_session_count(conn: duckdb.DuckDBPyConnection) -> int:
    """Get total session count."""
    result = conn.execute('SELECT COUNT(*) FROM debug_sessions').fetchone()
    return result[0]


def generate_session_id(conn: Optional[duckdb.DuckDBPyConnection] = None) -> str:
    """Generate a unique session ID in format DBG-YYYY-MM-DD-NNN.

    Args:
        conn: Optional database connection (creates one if not provided)
    """
    today = datetime.now(UTC).strftime('%Y-%m-%d')
    close_conn = False

    # Get the highest session number for today
    try:
        if conn is None:
            conn = connect()
            close_conn = True

        result = conn.execute(
            """
            SELECT session_id FROM debug_sessions
            WHERE session_id LIKE ?
            ORDER BY session_id DESC LIMIT 1
            """,
            [f'DBG-{today}-%'],
        ).fetchone()

        if result:
            # Extract counter from last session
            last_counter = int(result[0].split('-')[-1])
            counter = last_counter + 1
        else:
            counter = 1

        if close_conn:
            conn.close()
    except (duckdb.CatalogException, duckdb.IOException, ValueError):
        # Expected errors when querying non-existent tables or invalid queries
        counter = 1
    except OSError:
        # File system errors during database operations
        counter = 1

    return f'DBG-{today}-{counter:03d}'
