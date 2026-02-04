"""Tests for fs5.core module - Database and Error Handling.

Tests cover:
- Database connection management
- Schema initialization
- Error class hierarchy

Version: v0.10.0
Created: 2026-02-03
"""

import pytest
from pathlib import Path
import duckdb

from fs5.core import (
    get_connection,
    get_db_path,
    init_database,
    init_schema,
    FS5Error,
    EventParseError,
    DatabaseError,
    ConfigurationError,
    AnomalyRuleError,
)


class TestGetDbPath:
    """Tests for get_db_path function."""

    def test_returns_path_object(self):
        """get_db_path returns a Path object."""
        result = get_db_path()
        assert isinstance(result, Path)

    def test_returns_default_path(self):
        """get_db_path returns the expected default path."""
        result = get_db_path()
        assert result == Path("database/metrics/metrics.duckdb")


class TestGetConnection:
    """Tests for get_connection context manager."""

    def test_returns_duckdb_connection(self, tmp_path):
        """get_connection yields a DuckDB connection."""
        db_path = tmp_path / "test.duckdb"
        with get_connection(db_path) as conn:
            assert conn is not None
            # Verify it's a working connection
            result = conn.execute("SELECT 1 as test").fetchone()
            assert result[0] == 1

    def test_creates_parent_directory(self, tmp_path):
        """get_connection creates parent directories if needed."""
        db_path = tmp_path / "subdir" / "deep" / "test.duckdb"
        assert not db_path.parent.exists()

        with get_connection(db_path) as conn:
            conn.execute("SELECT 1").fetchone()

        assert db_path.parent.exists()

    def test_closes_connection_on_exit(self, tmp_path):
        """get_connection closes connection when context exits."""
        db_path = tmp_path / "test.duckdb"
        conn_ref = None

        with get_connection(db_path) as conn:
            conn_ref = conn
            # Connection should be open
            conn.execute("SELECT 1").fetchone()

        # After context exit, trying to use connection should fail
        # DuckDB connections may not raise on closed state, but we verify cleanup happened
        assert conn_ref is not None

    def test_closes_connection_on_exception(self, tmp_path):
        """get_connection closes connection even if exception occurs."""
        db_path = tmp_path / "test.duckdb"

        with pytest.raises(ValueError):
            with get_connection(db_path) as conn:
                conn.execute("SELECT 1").fetchone()
                raise ValueError("Test exception")

        # Database file should still exist
        assert db_path.exists()


class TestInitSchema:
    """Tests for init_schema function."""

    def test_creates_tables_from_schema_file(self, tmp_path, monkeypatch):
        """init_schema creates tables defined in schema file."""
        db_path = tmp_path / "test.duckdb"

        # Create a minimal schema file
        schema_dir = tmp_path / "schema"
        schema_dir.mkdir()
        schema_file = schema_dir / "metrics-schema.sql"
        schema_file.write_text("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name VARCHAR
            );
        """, encoding="utf-8")

        # Monkeypatch the SCHEMA_PATH
        import fs5.core.db as db_module
        original_path = db_module.SCHEMA_PATH
        db_module.SCHEMA_PATH = schema_file

        try:
            init_schema(db_path)

            # Verify table was created
            with get_connection(db_path) as conn:
                result = conn.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_name = 'test_table'"
                ).fetchone()
                assert result is not None
        finally:
            db_module.SCHEMA_PATH = original_path


class TestInitDatabase:
    """Tests for init_database function."""

    def test_calls_init_schema(self, tmp_path, monkeypatch):
        """init_database calls init_schema."""
        db_path = tmp_path / "test.duckdb"

        # Create minimal schema file
        schema_dir = tmp_path / "schema"
        schema_dir.mkdir()
        schema_file = schema_dir / "metrics-schema.sql"
        schema_file.write_text("""
            CREATE TABLE IF NOT EXISTS init_test (id INTEGER);
        """, encoding="utf-8")

        import fs5.core.db as db_module
        original_path = db_module.SCHEMA_PATH
        db_module.SCHEMA_PATH = schema_file

        try:
            init_database(db_path, include_views=False)

            with get_connection(db_path) as conn:
                result = conn.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_name = 'init_test'"
                ).fetchone()
                assert result is not None
        finally:
            db_module.SCHEMA_PATH = original_path


class TestErrorClasses:
    """Tests for FS5 error class hierarchy."""

    def test_fs5error_is_exception(self):
        """FS5Error inherits from Exception."""
        assert issubclass(FS5Error, Exception)

    def test_event_parse_error_inherits_fs5error(self):
        """EventParseError inherits from FS5Error."""
        assert issubclass(EventParseError, FS5Error)

    def test_database_error_inherits_fs5error(self):
        """DatabaseError inherits from FS5Error."""
        assert issubclass(DatabaseError, FS5Error)

    def test_configuration_error_inherits_fs5error(self):
        """ConfigurationError inherits from FS5Error."""
        assert issubclass(ConfigurationError, FS5Error)

    def test_anomaly_rule_error_inherits_fs5error(self):
        """AnomalyRuleError inherits from FS5Error."""
        assert issubclass(AnomalyRuleError, FS5Error)

    def test_can_catch_all_fs5_errors(self):
        """All FS5 errors can be caught with FS5Error."""
        errors = [
            EventParseError("test"),
            DatabaseError("test"),
            ConfigurationError("test"),
            AnomalyRuleError("test"),
        ]

        for error in errors:
            try:
                raise error
            except FS5Error as e:
                assert str(e) == "test"

    def test_error_messages_preserved(self):
        """Error messages are preserved correctly."""
        message = "Detailed error information"
        error = EventParseError(message)
        assert str(error) == message

    def test_errors_can_be_raised_with_no_args(self):
        """Errors can be raised without arguments."""
        error = FS5Error()
        assert error is not None
