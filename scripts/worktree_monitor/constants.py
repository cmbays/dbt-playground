"""
Worktree Monitor v2.0 - Constants and Enums

Centralized definitions for all status enums and configuration thresholds.
This module is the single source of truth for status values used across
the worktree monitor system.

Created: Phase 4 Day 0 (Pre-Work)
"""

from enum import Enum
from dataclasses import dataclass


# =============================================================================
# Status Enums
# =============================================================================


class VersionStatus(str, Enum):
    """Status of a version in the version plan."""

    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    ARCHIVED = "ARCHIVED"


class PhaseStatus(str, Enum):
    """Status of a phase within a version."""

    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


class WorkstreamStatus(str, Enum):
    """Status of a workstream within a phase."""

    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    ARCHIVED = "ARCHIVED"


class HeartbeatState(str, Enum):
    """Staleness state for heartbeat monitoring.

    Thresholds:
    - FRESH: < 30 seconds since last update (green)
    - WARNING: 30-60 seconds since last update (yellow)
    - STALE: 60-300 seconds since last update (red)
    - DISCONNECTED: > 300 seconds since last update (grey)
    """

    FRESH = "FRESH"
    WARNING = "WARNING"
    STALE = "STALE"
    DISCONNECTED = "DISCONNECTED"


class RequestType(str, Enum):
    """Types of orchestrator requests."""

    WAITING = "WAITING"  # Informational - orchestrator is waiting
    PERMISSION_NEEDED = "PERMISSION_NEEDED"  # Human approval required
    MERGE_READY = "MERGE_READY"  # PR ready for merge
    REVIEW_NEEDED = "REVIEW_NEEDED"  # Code review requested
    BLOCKED = "BLOCKED"  # Dependency blocker
    COMPLETED = "COMPLETED"  # Workstream done


class AnomalySeverity(str, Enum):
    """Severity levels for detected anomalies."""

    HIGH = "HIGH"  # CI failure, blocked
    MEDIUM = "MEDIUM"  # Changes requested, stale heartbeat
    LOW = "LOW"  # Dirty status, warnings


class WorktreeStatus(str, Enum):
    """Git worktree status."""

    CLEAN = "clean"
    DIRTY = "dirty"
    DETACHED = "detached"


class PRState(str, Enum):
    """Pull request state."""

    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class CICheckStatus(str, Enum):
    """Individual CI check status."""

    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    SKIPPED = "skipped"


class CodeRabbitReviewStatus(str, Enum):
    """CodeRabbit review status."""

    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    COMMENTED = "commented"
    PENDING = "pending"


class AnomalyType(str, Enum):
    """Types of anomalies that can be detected."""

    CI_FAILURE = "CI_FAILURE"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    STALE_HEARTBEAT = "STALE_HEARTBEAT"
    DIRTY_WORKTREE = "DIRTY_WORKTREE"
    BLOCKED_WORKSTREAM = "BLOCKED_WORKSTREAM"
    DISCONNECTED_ORCHESTRATOR = "DISCONNECTED_ORCHESTRATOR"


class ArchiveReason(str, Enum):
    """Reasons for archiving a workstream."""

    COMPLETED = "completed"
    MERGED = "merged"
    CLOSED = "closed"
    MANUAL = "manual"


# =============================================================================
# Threshold Configuration
# =============================================================================


@dataclass(frozen=True)
class HeartbeatThresholds:
    """Threshold values for heartbeat staleness detection.

    All values are in seconds.
    """

    FRESH_MAX: int = 30  # Under this = FRESH (green)
    WARNING_MAX: int = 60  # Under this = WARNING (yellow)
    STALE_MAX: int = 300  # Under this = STALE (red), over = DISCONNECTED

    def get_state(self, seconds_since_update: float) -> HeartbeatState:
        """Determine heartbeat state based on seconds since last update.

        Args:
            seconds_since_update: Time elapsed since last heartbeat update.

        Returns:
            HeartbeatState enum value.

        Note:
            Boundary behavior:
            - Exactly 30s = WARNING (not FRESH)
            - Exactly 60s = STALE (not WARNING)
            - Exactly 300s = DISCONNECTED (not STALE)
        """
        if seconds_since_update < self.FRESH_MAX:
            return HeartbeatState.FRESH
        elif seconds_since_update < self.WARNING_MAX:
            return HeartbeatState.WARNING
        elif seconds_since_update < self.STALE_MAX:
            return HeartbeatState.STALE
        else:
            return HeartbeatState.DISCONNECTED


@dataclass(frozen=True)
class CacheConfig:
    """Cache TTL configuration for GitHub API responses.

    All values are in seconds.
    """

    PR_TTL: int = 30  # PR state changes frequently
    CI_TTL: int = 30  # CI checks update during runs
    ISSUES_TTL: int = 300  # Issue counts change less frequently
    CODERABBIT_TTL: int = 60  # Review status
    RATE_LIMIT_THRESHOLD: int = 100  # Extend TTL when below this


@dataclass(frozen=True)
class RefreshConfig:
    """UI refresh configuration."""

    AUTO_REFRESH_SECONDS: int = 10
    HEARTBEAT_UPDATE_SECONDS: int = 30


# =============================================================================
# Default Instances
# =============================================================================

# Default threshold instances for use throughout the application
HEARTBEAT_THRESHOLDS = HeartbeatThresholds()
CACHE_CONFIG = CacheConfig()
REFRESH_CONFIG = RefreshConfig()


# =============================================================================
# CSS Class Mappings (for UI)
# =============================================================================

HEARTBEAT_CSS_CLASSES = {
    HeartbeatState.FRESH: "heartbeat-fresh",
    HeartbeatState.WARNING: "heartbeat-warning",
    HeartbeatState.STALE: "heartbeat-stale",
    HeartbeatState.DISCONNECTED: "heartbeat-disconnected",
}

ANOMALY_CSS_CLASSES = {
    AnomalyType.CI_FAILURE: "anomaly-ci-failure",
    AnomalyType.CHANGES_REQUESTED: "anomaly-changes-requested",
    AnomalyType.STALE_HEARTBEAT: "anomaly-stale",
    AnomalyType.DIRTY_WORKTREE: "anomaly-dirty",
    AnomalyType.BLOCKED_WORKSTREAM: "anomaly-blocked",
    AnomalyType.DISCONNECTED_ORCHESTRATOR: "anomaly-disconnected",
}
