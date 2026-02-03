"""
Worktree Monitor v2.0 - Data Models

All shared dataclasses used across the worktree monitor system.
This module is the single source of truth for data structures.

Created: Phase 4 Day 0 (Pre-Work)
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any

from .constants import (
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
)


# =============================================================================
# Configuration Models (from version-plan.yaml)
# =============================================================================


@dataclass
class WorkstreamConfig:
    """Configuration for a single workstream within a phase."""

    name: str
    epic: int
    branches: list[str]  # Can include glob patterns like "feat/kanban-*"
    status: WorkstreamStatus = WorkstreamStatus.PLANNED
    color: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "epic": self.epic,
            "branches": self.branches,
            "status": self.status.value,
            "color": self.color,
        }


@dataclass
class PhaseConfig:
    """Configuration for a single phase within a version."""

    name: str
    order: int
    description: str = ""
    status: PhaseStatus = PhaseStatus.PLANNED
    dependencies: list[str] = field(default_factory=list)
    workstreams: list[WorkstreamConfig] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "order": self.order,
            "description": self.description,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "workstreams": [w.to_dict() for w in self.workstreams],
        }


@dataclass
class VersionPlan:
    """Complete version plan configuration."""

    version: int  # Schema version
    name: str  # e.g., "v0.10"
    target_date: str  # ISO date string
    description: str = ""
    status: VersionStatus = VersionStatus.PLANNED
    phases: list[PhaseConfig] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "target_date": self.target_date,
            "description": self.description,
            "status": self.status.value,
            "phases": [p.to_dict() for p in self.phases],
        }


# =============================================================================
# Git/Worktree Models
# =============================================================================


@dataclass
class WorktreeInfo:
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "branch": self.branch,
            "commit_hash": self.commit_hash,
            "commit_short": self.commit_short,
            "is_main": self.is_main,
            "status": self.status.value,
            "files_changed": self.files_changed,
            "files_staged": self.files_staged,
            "last_commit_msg": self.last_commit_msg,
            "last_commit_date": (
                self.last_commit_date.isoformat() if self.last_commit_date else None
            ),
        }


# =============================================================================
# GitHub API Models
# =============================================================================


@dataclass
class EpicIssues:
    """Issue counts for an epic."""

    open: int
    closed: int
    total: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PRInfo:
    """Pull request information."""

    url: str
    number: int
    state: PRState
    title: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    draft: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "number": self.number,
            "state": self.state.value,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "draft": self.draft,
        }


@dataclass
class CIChecks:
    """CI check status summary."""

    total: int
    passed: int
    failed: int
    pending: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def all_passed(self) -> bool:
        """Check if all CI checks have passed."""
        return self.total > 0 and self.passed == self.total

    @property
    def has_failures(self) -> bool:
        """Check if any CI checks have failed."""
        return self.failed > 0


@dataclass
class CodeRabbitFeedback:
    """CodeRabbit feedback counts."""

    major: int
    minor: int
    total: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CodeRabbitStatus:
    """CodeRabbit review status."""

    status: CodeRabbitReviewStatus | None = None
    feedback: CodeRabbitFeedback | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value if self.status else None,
            "feedback": self.feedback.to_dict() if self.feedback else None,
        }

    @property
    def has_changes_requested(self) -> bool:
        """Check if CodeRabbit requested changes."""
        return self.status == CodeRabbitReviewStatus.CHANGES_REQUESTED


# =============================================================================
# Heartbeat/Orchestrator Models
# =============================================================================


@dataclass
class OrchestratorRequest:
    """Request from an orchestrator."""

    branch: str
    request_type: RequestType
    message: str = ""
    timestamp: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch": self.branch,
            "request_type": self.request_type.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class OrchestratorStatus:
    """Status of an individual orchestrator."""

    branch: str
    status: str  # Free-form status text
    request: RequestType | None = None
    last_update: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch": self.branch,
            "status": self.status,
            "request": self.request.value if self.request else None,
            "last_update": self.last_update.isoformat() if self.last_update else None,
        }


@dataclass
class HeartbeatStatus:
    """Overall heartbeat status."""

    state: HeartbeatState
    last_update: datetime
    seconds_since_update: float
    active_orchestrators: list[OrchestratorStatus] = field(default_factory=list)
    requests: list[OrchestratorRequest] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "last_update": self.last_update.isoformat(),
            "seconds_since_update": self.seconds_since_update,
            "active_orchestrators": [o.to_dict() for o in self.active_orchestrators],
            "requests": [r.to_dict() for r in self.requests],
        }


# =============================================================================
# Anomaly/Monitoring Models
# =============================================================================


@dataclass
class Anomaly:
    """Detected anomaly for a worktree."""

    type: AnomalyType
    severity: AnomalySeverity
    message: str
    worktree_path: str | None = None
    branch: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "message": self.message,
            "worktree_path": self.worktree_path,
            "branch": self.branch,
        }


@dataclass
class ComponentFailureInfo:
    """Information about a component failure (for graceful degradation).

    Note: Renamed from ComponentError to avoid conflict with the exception
    class of the same name in exceptions.py.
    """

    component: str
    message: str
    timestamp: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


# =============================================================================
# Enriched/Output Models
# =============================================================================


@dataclass
class EnrichedWorktree:
    """Worktree with all enrichments from config, GitHub, and monitoring."""

    # Base git data
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "branch": self.branch,
            "commit_hash": self.commit_hash,
            "commit_short": self.commit_short,
            "is_main": self.is_main,
            "status": self.status.value,
            "files_changed": self.files_changed,
            "files_staged": self.files_staged,
            "last_commit_msg": self.last_commit_msg,
            "last_commit_date": (
                self.last_commit_date.isoformat() if self.last_commit_date else None
            ),
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
    def from_worktree_info(cls, info: WorktreeInfo) -> "EnrichedWorktree":
        """Create an EnrichedWorktree from basic WorktreeInfo."""
        return cls(
            path=info.path,
            branch=info.branch,
            commit_hash=info.commit_hash,
            commit_short=info.commit_short,
            is_main=info.is_main,
            status=info.status,
            files_changed=info.files_changed,
            files_staged=info.files_staged,
            last_commit_msg=info.last_commit_msg,
            last_commit_date=info.last_commit_date,
        )


@dataclass
class TrackSummary:
    """Summary of a track/workstream for the UI."""

    name: str
    epic: int
    color: str
    worktree_count: int = 0
    issues_open: int = 0
    issues_closed: int = 0
    status: WorkstreamStatus = WorkstreamStatus.PLANNED

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "epic": self.epic,
            "color": self.color,
            "worktree_count": self.worktree_count,
            "issues_open": self.issues_open,
            "issues_closed": self.issues_closed,
            "status": self.status.value,
        }


@dataclass
class ArchivedWorktree:
    """Archived worktree with metadata."""

    id: str  # UUID
    worktree: EnrichedWorktree
    archived_at: datetime
    reason: ArchiveReason
    version: str  # Version this worktree belonged to (e.g., "v0.10")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "worktree": self.worktree.to_dict(),
            "archived_at": self.archived_at.isoformat(),
            "reason": self.reason.value,
            "version": self.version,
        }


@dataclass
class MonitorOutput:
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "config_version": self.config_version,
            "milestone": self.milestone,
            "worktree_count": self.worktree_count,
            "worktrees": [w.to_dict() for w in self.worktrees],
            "tracks": [t.to_dict() for t in self.tracks],
            "archived": [a.to_dict() for a in self.archived],
            "heartbeat": self.heartbeat.to_dict() if self.heartbeat else None,
            "anomalies": [a.to_dict() for a in self.anomalies],
            "errors": [e.to_dict() for e in self.errors],
        }


# =============================================================================
# Archive Index Model
# =============================================================================


@dataclass
class ArchiveIndex:
    """Index of all archived versions."""

    version: int  # Schema version
    versions: list[str]  # List of archived version names
    last_updated: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "versions": self.versions,
            "last_updated": self.last_updated.isoformat(),
        }
