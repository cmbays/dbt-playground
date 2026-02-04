"""
Worktree Monitor v2.0 - Package Exports

This package provides comprehensive worktree monitoring for the dbt-playground
project, integrating git worktree discovery, GitHub API status, heartbeat
monitoring, and version plan configuration.

Created: Phase 4 Day 0 (Pre-Work)
Updated: Phase 4 Day 4 (Orchestrator)
"""

# Main orchestrator
from .anomaly_detector import AnomalyDetector
from .archive_manager import ArchiveManager

# Constants and enums
from .constants import (
    ANOMALY_CSS_CLASSES,
    CACHE_CONFIG,
    # CSS mappings
    HEARTBEAT_CSS_CLASSES,
    # Default instances
    HEARTBEAT_THRESHOLDS,
    REFRESH_CONFIG,
    AnomalySeverity,
    AnomalyType,
    ArchiveReason,
    CacheConfig,
    CICheckStatus,
    CodeRabbitReviewStatus,
    HeartbeatState,
    # Configuration classes
    HeartbeatThresholds,
    PhaseStatus,
    PRState,
    RefreshConfig,
    RequestType,
    # Status enums
    VersionStatus,
    WorkstreamStatus,
    WorktreeStatus,
)

# Exceptions
from .exceptions import (
    ArchiveCorruptedError,
    # Archive
    ArchiveError,
    ArchiveNotFoundError,
    ArchiveWriteError,
    CollectionError,
    ComponentError,
    # Configuration
    ConfigError,
    GitCommandError,
    # Git
    GitError,
    GitHubAPIError,
    GitHubAuthError,
    # GitHub
    GitHubError,
    GitHubNotFoundError,
    GitNotFoundError,
    GitWorktreeError,
    # Heartbeat
    HeartbeatError,
    HeartbeatFileNotFoundError,
    HeartbeatParseError,
    InvalidVersionNameError,
    # Monitor
    MonitorError,
    RateLimitError,
    VersionPlanNotFoundError,
    VersionPlanParseError,
    VersionPlanSchemaError,
    VersionPlanValidationError,
    # Base
    WorktreeMonitorError,
)
from .github_adapter import GitHubAdapter
from .heartbeat_monitor import HeartbeatMonitor

# Data models
from .models import (
    Anomaly,
    # Archive models
    ArchivedWorktree,
    ArchiveIndex,
    ArchiveMetrics,
    CIChecks,
    CodeRabbitFeedback,
    CodeRabbitStatus,
    ComponentFailureInfo,
    EnrichedWorktree,
    EpicIssues,
    # Heartbeat models
    HeartbeatStatus,
    # Output models
    MonitorOutput,
    OrchestratorRequest,
    OrchestratorStatus,
    PhaseConfig,
    # GitHub models
    PRInfo,
    TrackSummary,
    VersionArchive,
    # Configuration models
    VersionPlan,
    VersionSummary,
    WorkstreamConfig,
    # Git/Worktree models
    WorktreeInfo,
)
from .monitor import MonitorWriteError, WorktreeMonitor

# Protocol definitions (for type hints and DI)
from .protocols import (
    ArchiveManagerProtocol,
    GitHubAdapterProtocol,
    HeartbeatMonitorProtocol,
    VersionPlanLoaderProtocol,
    WorktreeDiscoveryProtocol,
)

# Serialization utilities
from .serialization import SerializableMixin, serialize_value

# Core modules
from .version_plan_loader import VersionPlanLoader
from .worktree_discovery import WorktreeDiscovery

__all__ = [
    # Main orchestrator
    'WorktreeMonitor',
    'MonitorWriteError',
    # Core modules
    'VersionPlanLoader',
    'WorktreeDiscovery',
    'GitHubAdapter',
    'HeartbeatMonitor',
    'ArchiveManager',
    'AnomalyDetector',
    # Protocols
    'VersionPlanLoaderProtocol',
    'WorktreeDiscoveryProtocol',
    'GitHubAdapterProtocol',
    'HeartbeatMonitorProtocol',
    'ArchiveManagerProtocol',
    # Data models
    'VersionPlan',
    'PhaseConfig',
    'WorkstreamConfig',
    'WorktreeInfo',
    'EnrichedWorktree',
    'PRInfo',
    'CIChecks',
    'CodeRabbitStatus',
    'CodeRabbitFeedback',
    'EpicIssues',
    'HeartbeatStatus',
    'OrchestratorStatus',
    'OrchestratorRequest',
    'MonitorOutput',
    'TrackSummary',
    'Anomaly',
    'ComponentFailureInfo',
    'ArchivedWorktree',
    'VersionArchive',
    'VersionSummary',
    'ArchiveIndex',
    'ArchiveMetrics',
    # Constants and enums
    'VersionStatus',
    'PhaseStatus',
    'WorkstreamStatus',
    'HeartbeatState',
    'RequestType',
    'WorktreeStatus',
    'PRState',
    'CICheckStatus',
    'CodeRabbitReviewStatus',
    'AnomalyType',
    'AnomalySeverity',
    'ArchiveReason',
    'HeartbeatThresholds',
    'CacheConfig',
    'RefreshConfig',
    'HEARTBEAT_THRESHOLDS',
    'CACHE_CONFIG',
    'REFRESH_CONFIG',
    'HEARTBEAT_CSS_CLASSES',
    'ANOMALY_CSS_CLASSES',
    # Exceptions
    'WorktreeMonitorError',
    'ConfigError',
    'VersionPlanNotFoundError',
    'VersionPlanValidationError',
    'VersionPlanSchemaError',
    'VersionPlanParseError',
    'GitError',
    'GitNotFoundError',
    'GitCommandError',
    'GitWorktreeError',
    'GitHubError',
    'GitHubAPIError',
    'RateLimitError',
    'GitHubAuthError',
    'GitHubNotFoundError',
    'ArchiveError',
    'ArchiveNotFoundError',
    'ArchiveCorruptedError',
    'ArchiveWriteError',
    'InvalidVersionNameError',
    'HeartbeatError',
    'HeartbeatFileNotFoundError',
    'HeartbeatParseError',
    'MonitorError',
    'ComponentError',
    'CollectionError',
    # Serialization
    'SerializableMixin',
    'serialize_value',
]
