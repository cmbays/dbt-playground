"""FS5 Core Module.

Contains database connection management and error classes.
"""

from fs5.core.db import get_connection, get_db_path, init_database, init_schema, init_views
from fs5.core.errors import (
    FS5Error,
    EventParseError,
    DatabaseError,
    ConfigurationError,
    AnomalyRuleError,
)

__all__ = [
    "get_connection",
    "get_db_path",
    "init_database",
    "init_schema",
    "init_views",
    "FS5Error",
    "EventParseError",
    "DatabaseError",
    "ConfigurationError",
    "AnomalyRuleError",
]
