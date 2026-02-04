"""
Worktree Monitor v2.0 - Package Exports

This package provides comprehensive worktree monitoring for the dbt-playground
project, integrating git worktree discovery, GitHub API status, heartbeat
monitoring, and version plan configuration.

Created: Phase 4 Day 0 (Pre-Work)
Updated: Phase 4 Day 4 (Orchestrator)
"""

# Main orchestrator
from .monitor import WorktreeMonitor, MonitorWriteError

# Core modules
from .version_plan_loader import VersionPlanLoader
from .worktree_discovery import WorktreeDiscovery
from .github_adapter import GitHubAdapter
from .heartbeat_monitor import HeartbeatMonitor
from .archive_manager import ArchiveManager
from .anomaly_detector import AnomalyDetector

# Protocol definitions (for type hints and DI)
from .protocols import (
    VersionPlanLoaderProtocol,
    WorktreeDiscoveryProtocol,
    GitHubAdapterProtocol,
    HeartbeatMonitorProtocol,
    ArchiveManagerProtocol,
)

# Data models
from .models import (
    # Configuration models
    VersionPlan,
    PhaseConfig,
    WorkstreamConfig,
    # Git/Worktree models
    WorktreeInfo,
    EnrichedWorktree,
    # GitHub models
    PRInfo,
    CIChecks,
    CodeRabbitStatus,
    CodeRabbitFeedback,
    EpicIssues,
    # Heartbeat models
    HeartbeatStatus,
    OrchestratorStatus,
    OrchestratorRequest,
    # Output models
    MonitorOutput,
    TrackSummary,
    Anomaly,
    ComponentFailureInfo,
    # Archive models
    ArchivedWorktree,
    VersionArchive,
    VersionSummary,
    ArchiveIndex,
    ArchiveMetrics,
)

# Constants and enums
from .constants import (
    # Status enums
    VersionStatus,
    PhaseStatus,
    WorkstreamStatus,
    HeartbeatState,
    RequestType,
    WorktreeStatus,
    PRState,
    CICheckStatus,
    CodeRabbitReviewStatus,
    AnomalyType,
    AnomalySeverity,
    ArchiveReason,
    # Configuration classes
    HeartbeatThresholds,
    CacheConfig,
    RefreshConfig,
    # Default instances
    HEARTBEAT_THRESHOLDS,
    CACHE_CONFIG,
    REFRESH_CONFIG,
    # CSS mappings
    HEARTBEAT_CSS_CLASSES,
    ANOMALY_CSS_CLASSES,
)

# Exceptions
from .exceptions import (
    # Base
    WorktreeMonitorError,
    # Configuration
    ConfigError,
    VersionPlanNotFoundError,
    VersionPlanValidationError,
    VersionPlanSchemaError,
    VersionPlanParseError,
    # Git
    GitError,
    GitNotFoundError,
    GitCommandError,
    GitWorktreeError,
    # GitHub
    GitHubError,
    GitHubAPIError,
    RateLimitError,
    GitHubAuthError,
    GitHubNotFoundError,
    # Archive
    ArchiveError,
    ArchiveNotFoundError,
    ArchiveCorruptedError,
    ArchiveWriteError,
    InvalidVersionNameError,
    # Heartbeat
    HeartbeatError,
    HeartbeatFileNotFoundError,
    HeartbeatParseError,
    # Monitor
    MonitorError,
    ComponentError,
    CollectionError,
)

# Serialization utilities
from .serialization import SerializableMixin, serialize_value

__all__ = [
    # Main orchestrator
    "WorktreeMonitor",
    "MonitorWriteError",
    # Core modules
    "VersionPlanLoader",
    "WorktreeDiscovery",
    "GitHubAdapter",
    "HeartbeatMonitor",
    "ArchiveManager",
    "AnomalyDetector",
    # Protocols
    "VersionPlanLoaderProtocol",
    "WorktreeDiscoveryProtocol",
    "GitHubAdapterProtocol",
    "HeartbeatMonitorProtocol",
    "ArchiveManagerProtocol",
    # Data models
    "VersionPlan",
    "PhaseConfig",
    "WorkstreamConfig",
    "WorktreeInfo",
    "EnrichedWorktree",
    "PRInfo",
    "CIChecks",
    "CodeRabbitStatus",
    "CodeRabbitFeedback",
    "EpicIssues",
    "HeartbeatStatus",
    "OrchestratorStatus",
    "OrchestratorRequest",
    "MonitorOutput",
    "TrackSummary",
    "Anomaly",
    "ComponentFailureInfo",
    "ArchivedWorktree",
    "VersionArchive",
    "VersionSummary",
    "ArchiveIndex",
    "ArchiveMetrics",
    # Constants and enums
    "VersionStatus",
    "PhaseStatus",
    "WorkstreamStatus",
    "HeartbeatState",
    "RequestType",
    "WorktreeStatus",
    "PRState",
    "CICheckStatus",
    "CodeRabbitReviewStatus",
    "AnomalyType",
    "AnomalySeverity",
    "ArchiveReason",
    "HeartbeatThresholds",
    "CacheConfig",
    "RefreshConfig",
    "HEARTBEAT_THRESHOLDS",
    "CACHE_CONFIG",
    "REFRESH_CONFIG",
    "HEARTBEAT_CSS_CLASSES",
    "ANOMALY_CSS_CLASSES",
    # Exceptions
    "WorktreeMonitorError",
    "ConfigError",
    "VersionPlanNotFoundError",
    "VersionPlanValidationError",
    "VersionPlanSchemaError",
    "VersionPlanParseError",
    "GitError",
    "GitNotFoundError",
    "GitCommandError",
    "GitWorktreeError",
    "GitHubError",
    "GitHubAPIError",
    "RateLimitError",
    "GitHubAuthError",
    "GitHubNotFoundError",
    "ArchiveError",
    "ArchiveNotFoundError",
    "ArchiveCorruptedError",
    "ArchiveWriteError",
    "InvalidVersionNameError",
    "HeartbeatError",
    "HeartbeatFileNotFoundError",
    "HeartbeatParseError",
    "MonitorError",
    "ComponentError",
    "CollectionError",
    # Serialization
    "SerializableMixin",
    "serialize_value",
]
