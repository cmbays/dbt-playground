"""FS5 Metrics & Dashboard Module.

This module provides the metrics collection, anomaly detection,
and dashboard infrastructure for the dbt-playground project.

Submodules:
- fs5.core: Database and error handling
- fs5.services: Adherence scoring and anomaly detection
- fs5.adapters: Event source adapters (FS1, FS3)
- fs5.handlers: Event handlers (kanban transitions)
- fs5.widgets: Dashboard widgets

Version: v0.10.0
Created: 2026-02-03
"""

from fs5.core.db import get_connection, init_database, init_schema, init_views
from fs5.core.errors import (
    FS5Error,
    EventParseError,
    DatabaseError,
    ConfigurationError,
    AnomalyRuleError,
)

# Re-export key services for convenience
from fs5.services import (
    calculate_adherence_score,
    AdherenceScore,
    detect_anomalies,
    Anomaly,
    Severity,
)

# Re-export dashboard
from fs5.widgets import Dashboard

__version__ = "0.10.0"
__all__ = [
    # Core
    "get_connection",
    "init_database",
    "init_schema",
    "init_views",
    # Errors
    "FS5Error",
    "EventParseError",
    "DatabaseError",
    "ConfigurationError",
    "AnomalyRuleError",
    # Services
    "calculate_adherence_score",
    "AdherenceScore",
    "detect_anomalies",
    "Anomaly",
    "Severity",
    # Dashboard
    "Dashboard",
]
