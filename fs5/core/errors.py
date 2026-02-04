"""FS5 Exception Classes.

Defines the exception hierarchy for the FS5 metrics module.
All exceptions inherit from FS5Error for easy catching.

Version: v0.10.0
Created: 2026-02-03
"""


class FS5Error(Exception):
    """Base exception for FS5 module.

    All FS5-specific exceptions inherit from this class,
    allowing callers to catch all FS5 errors with a single
    except clause if desired.
    """

    pass


class EventParseError(FS5Error):
    """Failed to parse event from source.

    Raised when JSONL parsing fails or event data is malformed.
    """

    pass


class DatabaseError(FS5Error):
    """Database operation failed.

    Raised for connection failures, query errors, or
    constraint violations.
    """

    pass


class ConfigurationError(FS5Error):
    """Invalid configuration.

    Raised when configuration values are missing, invalid,
    or incompatible.
    """

    pass


class AnomalyRuleError(FS5Error):
    """Anomaly rule execution failed.

    Raised when an anomaly detection rule cannot be evaluated,
    typically due to missing data or invalid rule definition.
    """

    pass
