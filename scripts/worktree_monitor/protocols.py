"""
Worktree Monitor v2.0 - Protocol Definitions

Protocols for dependency injection and testability.

Created: Phase 4 Day 5 (Review Fixes)
"""

from datetime import datetime
from typing import Protocol, runtime_checkable

from .constants import HeartbeatState
from .models import (
    CIChecks,
    HeartbeatStatus,
    PhaseConfig,
    PRInfo,
    VersionPlan,
    VersionSummary,
    WorkstreamConfig,
    WorktreeInfo,
)


@runtime_checkable
class VersionPlanLoaderProtocol(Protocol):
    """Protocol for loading version plan configuration."""

    def load(self) -> VersionPlan:
        """Load the version plan from source."""
        ...

    def reload_if_changed(self) -> VersionPlan | None:
        """Reload if source has changed, return None if unchanged."""
        ...

    def get_workstream_for_branch(self, branch: str) -> tuple[PhaseConfig, WorkstreamConfig] | None:
        """Match a branch to its workstream configuration."""
        ...


@runtime_checkable
class WorktreeDiscoveryProtocol(Protocol):
    """Protocol for discovering git worktrees."""

    def list_worktrees(self) -> list[WorktreeInfo]:
        """List all worktrees in the repository."""
        ...


@runtime_checkable
class GitHubAdapterProtocol(Protocol):
    """Protocol for GitHub API access."""

    def get_pr_state(self, branch: str) -> PRInfo | None:
        """Get PR info for a branch."""
        ...

    def get_ci_status(self, pr_number: int) -> CIChecks:
        """Get CI check status for a PR."""
        ...

    def get_coderabbit_status(self, pr_number: int) -> str | None:
        """Get CodeRabbit review status for a PR."""
        ...

    def clear_cache(self) -> None:
        """Clear the adapter's cache."""
        ...


@runtime_checkable
class HeartbeatMonitorProtocol(Protocol):
    """Protocol for heartbeat monitoring."""

    def get_status(self, now: datetime | None = None) -> HeartbeatStatus:
        """Get current heartbeat status."""
        ...

    def get_state(self) -> HeartbeatState:
        """Get current heartbeat state."""
        ...


@runtime_checkable
class ArchiveManagerProtocol(Protocol):
    """Protocol for archive management."""

    def list_versions(self) -> list[VersionSummary]:
        """List all archived versions."""
        ...
