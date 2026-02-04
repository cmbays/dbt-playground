"""FS5 Database Connection Management.

Provides connection management for the metrics DuckDB database,
including schema initialization and connection context managers.

Version: v0.10.0
Created: 2026-02-03
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import duckdb

DEFAULT_DB_PATH = Path("database/metrics/metrics.duckdb")
SCHEMA_PATH = Path("database/metrics/schema/metrics-schema.sql")
VIEWS_PATH = Path("database/metrics/schema/live-views.sql")


def get_db_path() -> Path:
    """Get the metrics database path.

    Returns:
        Path to the metrics DuckDB database file.
    """
    return DEFAULT_DB_PATH


@contextmanager
def get_connection(db_path: Path | None = None) -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """Get a DuckDB connection as a context manager.

    Creates the parent directory if it doesn't exist and manages
    connection lifecycle automatically.

    Args:
        db_path: Optional path to database file. Uses default if not specified.

    Yields:
        DuckDB connection object.

    Example:
        with get_connection() as conn:
            result = conn.execute("SELECT * FROM sessions").fetchall()
    """
    path = db_path or get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(path))
    try:
        yield conn
    finally:
        conn.close()


def init_schema(db_path: Path | None = None) -> None:
    """Initialize the database with schema only (no views).

    Creates the core tables without attempting to create views
    that depend on external JSONL files.

    Args:
        db_path: Optional path to database file. Uses default if not specified.

    Raises:
        FileNotFoundError: If schema file doesn't exist.
        duckdb.Error: If SQL execution fails.
    """
    with get_connection(db_path) as conn:
        if SCHEMA_PATH.exists():
            conn.execute(SCHEMA_PATH.read_text(encoding="utf-8"))


def init_views(db_path: Path | None = None) -> None:
    """Initialize the live JSONL views.

    Creates views that query JSONL event files. Only call this
    when the JSONL files exist or DuckDB will raise an error.

    Args:
        db_path: Optional path to database file. Uses default if not specified.

    Raises:
        FileNotFoundError: If views file doesn't exist.
        duckdb.IOException: If JSONL files don't exist.
    """
    with get_connection(db_path) as conn:
        if VIEWS_PATH.exists():
            conn.execute(VIEWS_PATH.read_text(encoding="utf-8"))


def init_database(db_path: Path | None = None, include_views: bool = False) -> None:
    """Initialize the database with schema and optionally views.

    Reads and executes the schema DDL. Views are only created
    if include_views=True and the source JSONL files exist.

    Args:
        db_path: Optional path to database file. Uses default if not specified.
        include_views: If True, also create JSONL views (requires files to exist).

    Raises:
        FileNotFoundError: If schema files don't exist.
        duckdb.Error: If SQL execution fails.
    """
    init_schema(db_path)
    if include_views:
        init_views(db_path)
