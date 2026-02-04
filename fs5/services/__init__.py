"""FS5 Services Module.

Contains business logic services including anomaly detection
and adherence scoring.

Version: v0.10.0
Created: 2026-02-03
"""

from fs5.services.adherence import (
    # Constants
    CANONICAL_ORDER,
    COMPLETION_BONUS,
    MAX_SCORE,
    MIN_SCORE,
    PENALTY_VALUES,
    PHASE_BASELINES,
    PHASE_POINTS,
    # Classes
    AdherenceScore,
    Penalty,
    # Functions
    calculate_adherence_score,
    get_session_status,
    update_session_phase,
)

from fs5.services.anomaly import (
    # Classes
    Anomaly,
    Severity,
    # Functions
    check_transition_anomalies,
    detect_anomalies,
    get_active_anomalies,
    load_rules_config,
    persist_anomaly,
    resolve_anomaly,
)

__all__ = [
    # Adherence Constants
    "CANONICAL_ORDER",
    "COMPLETION_BONUS",
    "MAX_SCORE",
    "MIN_SCORE",
    "PENALTY_VALUES",
    "PHASE_BASELINES",
    "PHASE_POINTS",
    # Adherence Classes
    "AdherenceScore",
    "Penalty",
    # Adherence Functions
    "calculate_adherence_score",
    "get_session_status",
    "update_session_phase",
    # Anomaly Classes
    "Anomaly",
    "Severity",
    # Anomaly Functions
    "check_transition_anomalies",
    "detect_anomalies",
    "get_active_anomalies",
    "load_rules_config",
    "persist_anomaly",
    "resolve_anomaly",
]
