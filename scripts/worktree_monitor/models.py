"""
Worktree Monitor v2.0 - Data Models

All shared dataclasses used across the worktree monitor system.
This module is the single source of truth for data structures.

Created: Phase 4 Day 0 (Pre-Work)
Updated: Phase 4 Day 3 (Refactoring) - Added SerializableMixin
"""

from dataclasses import dataclass, field
from datetime import datetime

from .constants import (
    VersionStatus,
    PhaseStatus,
    WorkstreamStatus,
    HeartbeatState,
    RequestType,
    WorktreeStatus,
    PRState,
    CodeRabbitReviewStatus,
    AnomalyType,
    AnomalySeverity,
    ArchiveReason,
)
from .serialization import SerializableMixin


# =============================================================================
# Configuration Models (from version-plan.yaml)
# =============================================================================


@dataclass
class WorkstreamConfig(SerializableMixin):
    """Configuration for a single workstream within a phase."""

    name: str
    epic: int
    branches: list[str]  # Can include glob patterns like "feat/kanban-*"
    status: WorkstreamStatus = WorkstreamStatus.PLANNED
    color: str | None = None


@dataclass
class PhaseConfig(SerializableMixin):
    """Configuration for a single phase within a version."""

    name: str
    order: int
    description: str = ""
    status: PhaseStatus = PhaseStatus.PLANNED
    dependencies: list[str] = field(default_factory=list)
    workstreams: list[WorkstreamConfig] = field(default_factory=list)


@dataclass
class VersionPlan(SerializableMixin):
    """Complete version plan configuration."""

    version: int  # Schema version
    name: str  # e.g., "v0.10"
    target_date: str  # ISO date string
    description: str = ""
    status: VersionStatus = VersionStatus.PLANNED
    phases: list[PhaseConfig] = field(default_factory=list)


# =============================================================================
# Git/Worktree Models
# =============================================================================


@dataclass
class WorktreeInfo(SerializableMixin):
    """Basic git worktree information."""

    path: str
    branch: str
    commit_hash: str
    commit_short: str
    is_main: bool
    status: WorktreeStatus
    files_changed: int = 0
    files_staged: int = 0
    last_commit_msg: str = ""
    last_commit_date: datetime | None = None


# =============================================================================
# GitHub API Models
# =============================================================================


@dataclass
class EpicIssues(SerializableMixin):
    """Issue counts for an epic."""

    open: int
    closed: int
    total: int


@dataclass
class PRInfo(SerializableMixin):
    """Pull request information."""

    url: str
    number: int
    state: PRState
    title: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    draft: bool = False


@dataclass
class CIChecks(SerializableMixin):
    """CI check status summary."""

    total: int
    passed: int
    failed: int
    pending: int

    @property
    def all_passed(self) -> bool:
        """Check if all CI checks have passed."""
        return self.total > 0 and self.passed == self.total

    @property
    def has_failures(self) -> bool:
        """Check if any CI checks have failed."""
        return self.failed > 0


@dataclass
class CodeRabbitFeedback(SerializableMixin):
    """CodeRabbit feedback counts."""

    major: int
    minor: int
    total: int


@dataclass
class CodeRabbitStatus(SerializableMixin):
    """CodeRabbit review status."""

    status: CodeRabbitReviewStatus | None = None
    feedback: CodeRabbitFeedback | None = None

    @property
    def has_changes_requested(self) -> bool:
        """Check if CodeRabbit requested changes."""
        return self.status == CodeRabbitReviewStatus.CHANGES_REQUESTED


# =============================================================================
# Heartbeat/Orchestrator Models
# =============================================================================


@dataclass
class OrchestratorRequest(SerializableMixin):
    """Request from an orchestrator."""

    branch: str
    request_type: RequestType
    message: str = ""
    timestamp: datetime | None = None


@dataclass
class OrchestratorStatus(SerializableMixin):
    """Status of an individual orchestrator."""

    branch: str
    status: str  # Free-form status text
    request: RequestType | None = None
    last_update: datetime | None = None


@dataclass
class HeartbeatStatus(SerializableMixin):
    """Overall heartbeat status."""

    state: HeartbeatState
    last_update: datetime
    seconds_since_update: float
    active_orchestrators: list[OrchestratorStatus] = field(default_factory=list)
    requests: list[OrchestratorRequest] = field(default_factory=list)


# =============================================================================
# Anomaly/Monitoring Models
# =============================================================================


@dataclass
class Anomaly(SerializableMixin):
    """Detected anomaly for a worktree."""

    type: AnomalyType
    severity: AnomalySeverity
    message: str
    worktree_path: str | None = None
    branch: str | None = None


@dataclass
class ComponentFailureInfo(SerializableMixin):
    """Information about a component failure (for graceful degradation).

    Note: Renamed from ComponentError to avoid conflict with the exception
    class of the same name in exceptions.py.
    """

    component: str
    message: str
    timestamp: datetime | None = None


# =============================================================================
# Enriched/Output Models
# =============================================================================


@dataclass
class EnrichedWorktree:
    """Worktree with all enrichments from config, GitHub, and monitoring.

    Uses composition: base WorktreeInfo is stored in `base` field.
    Property delegates provide backward-compatible access to base fields.
    """

    # Base git data (composition instead of duplication)
    base: WorktreeInfo

    # Track enrichment (from config)
    track_name: str | None = None
    track_color: str | None = None
    epic_number: int | None = None

    # GitHub enrichment
    epic_issues: EpicIssues | None = None
    pr: PRInfo | None = None
    ci_checks: CIChecks | None = None
    coderabbit: CodeRabbitStatus | None = None

    # Anomalies
    anomalies: list[Anomaly] = field(default_factory=list)

    # Property delegates for backward compatibility
    @property
    def path(self) -> str:
        return self.base.path

    @property
    def branch(self) -> str:
        return self.base.branch

    @property
    def commit_hash(self) -> str:
        return self.base.commit_hash

    @property
    def commit_short(self) -> str:
        return self.base.commit_short

    @property
    def is_main(self) -> bool:
        return self.base.is_main

    @property
    def status(self) -> WorktreeStatus:
        return self.base.status

    @property
    def files_changed(self) -> int:
        return self.base.files_changed

    @property
    def files_staged(self) -> int:
        return self.base.files_staged

    @property
    def last_commit_msg(self) -> str:
        return self.base.last_commit_msg

    @property
    def last_commit_date(self) -> datetime | None:
        return self.base.last_commit_date

    def to_dict(self) -> dict:
        """Serialize to dict, flattening base fields for backward compatibility."""
        return {
            # Flattened base fields
            "path": self.base.path,
            "branch": self.base.branch,
            "commit_hash": self.base.commit_hash,
            "commit_short": self.base.commit_short,
            "is_main": self.base.is_main,
            "status": self.base.status.value,
            "files_changed": self.base.files_changed,
            "files_staged": self.base.files_staged,
            "last_commit_msg": self.base.last_commit_msg,
            "last_commit_date": (
                self.base.last_commit_date.isoformat()
                if self.base.last_commit_date
                else None
            ),
            # Enrichment fields
            "track_name": self.track_name,
            "track_color": self.track_color,
            "epic_number": self.epic_number,
            "epic_issues": self.epic_issues.to_dict() if self.epic_issues else None,
            "pr": self.pr.to_dict() if self.pr else None,
            "ci_checks": self.ci_checks.to_dict() if self.ci_checks else None,
            "coderabbit": self.coderabbit.to_dict() if self.coderabbit else None,
            "anomalies": [a.to_dict() for a in self.anomalies],
        }

    @classmethod
    def from_worktree_info(cls, info: "WorktreeInfo") -> "EnrichedWorktree":
        """Create an EnrichedWorktree from basic WorktreeInfo."""
        return cls(base=info)


@dataclass
class TrackSummary(SerializableMixin):
    """Summary of a track/workstream for the UI."""

    name: str
    epic: int
    color: str
    worktree_count: int = 0
    issues_open: int = 0
    issues_closed: int = 0
    status: WorkstreamStatus = WorkstreamStatus.PLANNED


@dataclass
class ArchivedWorktree(SerializableMixin):
    """Archived worktree with metadata."""

    id: str  # UUID
    worktree: EnrichedWorktree
    archived_at: datetime
    reason: ArchiveReason
    version: str  # Version this worktree belonged to (e.g., "v0.10")


@dataclass
class MonitorOutput(SerializableMixin):
    """Complete monitor output for the UI."""

    timestamp: datetime
    config_version: int
    milestone: str
    worktree_count: int
    worktrees: list[EnrichedWorktree]
    tracks: list[TrackSummary] = field(default_factory=list)
    archived: list[ArchivedWorktree] = field(default_factory=list)
    heartbeat: HeartbeatStatus | None = None
    anomalies: list[Anomaly] = field(default_factory=list)
    errors: list[ComponentFailureInfo] = field(default_factory=list)


# =============================================================================
# Archive Index Model
# =============================================================================


@dataclass
class ArchiveIndex(SerializableMixin):
    """Index of all archived versions."""

    version: int  # Schema version
    versions: list[str]  # List of archived version names
    last_updated: datetime
