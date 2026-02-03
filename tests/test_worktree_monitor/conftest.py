"""
Worktree Monitor v2.0 - Shared Test Fixtures

Pytest fixtures used across all worktree monitor tests.

Created: Phase 4 Day 0 (Pre-Work)
"""

import json
import sys
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from worktree_monitor.constants import (
    AnomalySeverity,
    AnomalyType,
    ArchiveReason,
    CodeRabbitReviewStatus,
    HeartbeatState,
    PhaseStatus,
    PRState,
    VersionStatus,
    WorkstreamStatus,
    WorktreeStatus,
)
from worktree_monitor.models import (
    Anomaly,
    ArchivedWorktree,
    CIChecks,
    CodeRabbitFeedback,
    CodeRabbitStatus,
    EnrichedWorktree,
    EpicIssues,
    HeartbeatStatus,
    MonitorOutput,
    OrchestratorStatus,
    PhaseConfig,
    PRInfo,
    TrackSummary,
    VersionPlan,
    WorkstreamConfig,
    WorktreeInfo,
)

# =============================================================================
# Time Fixtures
# =============================================================================


@pytest.fixture
def fixed_now() -> datetime:
    """Fixed timestamp for deterministic testing."""
    return datetime(2026, 2, 3, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def fixed_now_factory():
    """Factory for creating fixed timestamps with offsets."""

    def _factory(seconds_offset: int = 0) -> datetime:
        base = datetime(2026, 2, 3, 12, 0, 0, tzinfo=UTC)
        from datetime import timedelta

        return base + timedelta(seconds=seconds_offset)

    return _factory


# =============================================================================
# Version Plan YAML Fixtures
# =============================================================================


@pytest.fixture
def valid_version_plan_yaml() -> str:
    """Valid version plan YAML configuration."""
    return """
version: 1
name: v0.10
target_date: "2026-04-30"
description: Agent Orchestration Enhancements
status: IN_PROGRESS

phases:
  - name: Phase A
    order: 1
    description: Foundation (Memory, Kanban, GitHub)
    status: COMPLETE
    workstreams:
      - name: Agent Memory & Learning
        epic: 143
        branches:
          - feat/agent-memory
          - feat/memory-*
        status: COMPLETE
        color: "#7c3aed"
      - name: Kanban Workflow Engine
        epic: 144
        branches:
          - feat/kanban-phase1
          - feat/kanban-*
        status: COMPLETE
        color: "#2563eb"
      - name: GitHub Integration
        epic: 147
        branches:
          - feat/github-integration
        status: COMPLETE
        color: "#16a34a"

  - name: Phase B
    order: 2
    description: Quality & Observability
    status: IN_PROGRESS
    dependencies:
      - Phase A
    workstreams:
      - name: QA Enforcement
        epic: 145
        branches:
          - feat/qa-enforcement
          - feat/qa-*
        status: COMPLETE
        color: "#dc2626"
      - name: Metrics Dashboard
        epic: 146
        branches:
          - feat/metrics-dashboard
        status: PLANNED
        color: "#ea580c"
"""


@pytest.fixture
def minimal_version_plan_yaml() -> str:
    """Minimal valid version plan YAML."""
    return """
version: 1
name: v0.11
target_date: "2026-06-30"

phases:
  - name: Phase A
    order: 1
    workstreams:
      - name: Feature One
        epic: 200
        branches:
          - feat/feature-one
"""


@pytest.fixture
def invalid_yaml() -> str:
    """Invalid YAML syntax."""
    return """
version: 1
name: v0.10
phases:
  - name: Phase A
    order: 1
    workstreams:
      - name: "Unclosed quote
        epic: 143
"""


@pytest.fixture
def invalid_schema_yaml() -> str:
    """Valid YAML but invalid schema (missing required fields)."""
    return """
version: 1
name: v0.10
phases:
  - name: Phase A
    workstreams:
      - name: Missing Epic
        branches:
          - feat/test
"""


@pytest.fixture
def circular_dependency_yaml() -> str:
    """Version plan with circular phase dependencies."""
    return """
version: 1
name: v0.10
target_date: "2026-04-30"

phases:
  - name: Phase A
    order: 1
    dependencies:
      - Phase B
    workstreams:
      - name: Test
        epic: 100
        branches: [feat/a]
  - name: Phase B
    order: 2
    dependencies:
      - Phase A
    workstreams:
      - name: Test
        epic: 101
        branches: [feat/b]
"""


@pytest.fixture
def version_plan_dict(valid_version_plan_yaml) -> dict[str, Any]:
    """Parsed version plan as dictionary."""
    import yaml

    return yaml.safe_load(valid_version_plan_yaml)


# =============================================================================
# Git Worktree Fixtures
# =============================================================================


@pytest.fixture
def sample_porcelain_output() -> str:
    """Sample git worktree list --porcelain output."""
    return """worktree /Users/dev/dbt-playground
HEAD abc1234567890abcdef1234567890abcdef123456
branch refs/heads/main

worktree /Users/dev/dbt-playground--feat-kanban
HEAD def4567890abcdef1234567890abcdef12345678
branch refs/heads/feat/kanban-phase1

worktree /Users/dev/dbt-playground--feat-qa
HEAD 789abcdef1234567890abcdef1234567890abcdef
branch refs/heads/feat/qa-enforcement

worktree /Users/dev/dbt-playground--detached
HEAD fedcba0987654321fedcba0987654321fedcba09
detached
"""


@pytest.fixture
def sample_porcelain_single() -> str:
    """Single worktree (main only)."""
    return """worktree /Users/dev/dbt-playground
HEAD abc1234567890abcdef1234567890abcdef123456
branch refs/heads/main
"""


@pytest.fixture
def sample_worktree_info(fixed_now) -> WorktreeInfo:
    """Sample WorktreeInfo object."""
    return WorktreeInfo(
        path="/Users/dev/dbt-playground--feat-kanban",
        branch="feat/kanban-phase1",
        commit_hash="def4567890abcdef1234567890abcdef12345678",
        commit_short="def4567",
        is_main=False,
        status=WorktreeStatus.CLEAN,
        files_changed=0,
        files_staged=0,
        last_commit_msg="feat(kanban): add workflow engine",
        last_commit_date=fixed_now,
    )


@pytest.fixture
def sample_worktree_info_dirty(fixed_now) -> WorktreeInfo:
    """Sample dirty WorktreeInfo object."""
    return WorktreeInfo(
        path="/Users/dev/dbt-playground--feat-qa",
        branch="feat/qa-enforcement",
        commit_hash="789abcdef1234567890abcdef1234567890abcdef",
        commit_short="789abcd",
        is_main=False,
        status=WorktreeStatus.DIRTY,
        files_changed=3,
        files_staged=1,
        last_commit_msg="wip: qa gate",
        last_commit_date=fixed_now,
    )


@pytest.fixture
def sample_worktree_main(fixed_now) -> WorktreeInfo:
    """Sample main worktree."""
    return WorktreeInfo(
        path="/Users/dev/dbt-playground",
        branch="main",
        commit_hash="abc1234567890abcdef1234567890abcdef123456",
        commit_short="abc1234",
        is_main=True,
        status=WorktreeStatus.CLEAN,
        files_changed=0,
        files_staged=0,
        last_commit_msg="Merge PR #184",
        last_commit_date=fixed_now,
    )


# =============================================================================
# GitHub API Response Fixtures
# =============================================================================


@pytest.fixture
def mock_github_pr_response() -> dict[str, Any]:
    """Mock GitHub PR API response."""
    return {
        "url": "https://github.com/owner/repo/pull/184",
        "number": 184,
        "state": "open",
        "title": "feat(qa): implement QA enforcement",
        "created_at": "2026-02-01T10:00:00Z",
        "updated_at": "2026-02-03T08:00:00Z",
        "draft": False,
        "head": {"ref": "feat/qa-enforcement"},
        "base": {"ref": "main"},
    }


@pytest.fixture
def mock_github_pr_merged() -> dict[str, Any]:
    """Mock merged PR response."""
    return {
        "url": "https://github.com/owner/repo/pull/182",
        "number": 182,
        "state": "closed",
        "merged": True,
        "title": "feat(kanban): add workflow engine",
        "created_at": "2026-02-01T08:00:00Z",
        "updated_at": "2026-02-03T04:00:00Z",
        "merged_at": "2026-02-03T04:00:00Z",
        "draft": False,
    }


@pytest.fixture
def mock_github_ci_response() -> dict[str, Any]:
    """Mock GitHub CI checks response."""
    return {
        "total_count": 5,
        "check_runs": [
            {"name": "lint", "status": "completed", "conclusion": "success"},
            {"name": "test", "status": "completed", "conclusion": "success"},
            {"name": "build", "status": "completed", "conclusion": "success"},
            {"name": "dbt-test", "status": "completed", "conclusion": "success"},
            {"name": "security", "status": "completed", "conclusion": "success"},
        ],
    }


@pytest.fixture
def mock_github_ci_failed() -> dict[str, Any]:
    """Mock GitHub CI with failures."""
    return {
        "total_count": 3,
        "check_runs": [
            {"name": "lint", "status": "completed", "conclusion": "success"},
            {"name": "test", "status": "completed", "conclusion": "failure"},
            {"name": "build", "status": "in_progress", "conclusion": None},
        ],
    }


@pytest.fixture
def mock_github_issues_response() -> list[dict[str, Any]]:
    """Mock GitHub issues for an epic."""
    return [
        {"number": 156, "state": "closed", "title": "QA_REPORT.md template"},
        {"number": 157, "state": "closed", "title": "qa-reviewer persona"},
        {"number": 165, "state": "open", "title": "Supervisor QA gate"},
        {"number": 166, "state": "open", "title": "/qa command"},
    ]


@pytest.fixture
def mock_coderabbit_approved() -> CodeRabbitStatus:
    """CodeRabbit approved status."""
    return CodeRabbitStatus(
        status=CodeRabbitReviewStatus.APPROVED,
        feedback=None,
    )


@pytest.fixture
def mock_coderabbit_changes_requested() -> CodeRabbitStatus:
    """CodeRabbit changes requested status."""
    return CodeRabbitStatus(
        status=CodeRabbitReviewStatus.CHANGES_REQUESTED,
        feedback=CodeRabbitFeedback(major=1, minor=3, total=4),
    )


# =============================================================================
# Heartbeat/Workflow State Fixtures
# =============================================================================


@pytest.fixture
def workflow_state_fresh(fixed_now) -> dict[str, Any]:
    """Fresh workflow state (heartbeat < 30s)."""
    return {
        "last_update": fixed_now.isoformat(),
        "active_tracks": [
            {"branch": "feat/qa-enforcement", "status": "IN_PROGRESS"},
        ],
    }


@pytest.fixture
def workflow_state_stale() -> dict[str, Any]:
    """Stale workflow state (heartbeat > 60s)."""
    return {
        "last_update": "2026-02-03T11:58:00Z",  # 2 minutes old relative to fixed_now
        "active_tracks": [
            {"branch": "feat/qa-enforcement", "status": "IN_PROGRESS"},
        ],
    }


@pytest.fixture
def heartbeat_status_fresh(fixed_now) -> HeartbeatStatus:
    """Fresh heartbeat status object."""
    return HeartbeatStatus(
        state=HeartbeatState.FRESH,
        last_update=fixed_now,
        seconds_since_update=10.0,
        active_orchestrators=[
            OrchestratorStatus(
                branch="feat/qa-enforcement",
                status="IN_PROGRESS",
                request=None,
                last_update=fixed_now,
            )
        ],
    )


@pytest.fixture
def heartbeat_status_stale(fixed_now) -> HeartbeatStatus:
    """Stale heartbeat status object."""
    from datetime import timedelta

    old_time = fixed_now - timedelta(seconds=90)
    return HeartbeatStatus(
        state=HeartbeatState.STALE,
        last_update=old_time,
        seconds_since_update=90.0,
        active_orchestrators=[],
    )


# =============================================================================
# Archive Fixtures
# =============================================================================


@pytest.fixture
def tmp_archives_dir(tmp_path) -> Path:
    """Temporary archives directory."""
    archives = tmp_path / "archives"
    archives.mkdir()
    return archives


@pytest.fixture
def archived_worktree_sample(fixed_now, sample_worktree_info) -> ArchivedWorktree:
    """Sample archived worktree."""
    enriched = EnrichedWorktree.from_worktree_info(sample_worktree_info)
    enriched.track_name = "Kanban Workflow Engine"
    enriched.epic_number = 144
    return ArchivedWorktree(
        id="archive-uuid-001",
        worktree=enriched,
        archived_at=fixed_now,
        reason=ArchiveReason.MERGED,
        version="v0.10",
    )


@pytest.fixture
def archive_index_sample() -> dict[str, Any]:
    """Sample archive index JSON."""
    return {
        "version": 1,
        "versions": ["v0.9", "v0.10"],
        "last_updated": "2026-02-03T12:00:00Z",
    }


@pytest.fixture
def archived_version_v09(tmp_archives_dir) -> Path:
    """Create sample v0.9 archive directory with data."""
    v09_dir = tmp_archives_dir / "v0.9"
    v09_dir.mkdir()

    archive_data = {
        "version": "v0.9",
        "archived_at": "2026-01-15T10:00:00Z",
        "worktrees": [
            {
                "id": "old-uuid-001",
                "branch": "feat/old-feature",
                "archived_at": "2026-01-15T10:00:00Z",
                "reason": "completed",
            }
        ],
    }
    (v09_dir / "archive.json").write_text(
        json.dumps(archive_data, indent=2), encoding="utf-8"
    )
    return v09_dir


# =============================================================================
# Enriched Data Fixtures
# =============================================================================


@pytest.fixture
def enriched_worktree_full(fixed_now) -> EnrichedWorktree:
    """Fully enriched worktree with all data."""
    return EnrichedWorktree(
        path="/Users/dev/dbt-playground--feat-qa",
        branch="feat/qa-enforcement",
        commit_hash="789abcdef1234567890abcdef1234567890abcdef",
        commit_short="789abcd",
        is_main=False,
        status=WorktreeStatus.CLEAN,
        files_changed=0,
        files_staged=0,
        last_commit_msg="feat(qa): implement QA enforcement",
        last_commit_date=fixed_now,
        track_name="QA Enforcement",
        track_color="#dc2626",
        epic_number=145,
        epic_issues=EpicIssues(open=2, closed=2, total=4),
        pr=PRInfo(
            url="https://github.com/owner/repo/pull/184",
            number=184,
            state=PRState.OPEN,
            title="feat(qa): implement QA enforcement",
            draft=False,
        ),
        ci_checks=CIChecks(total=5, passed=5, failed=0, pending=0),
        coderabbit=CodeRabbitStatus(status=CodeRabbitReviewStatus.APPROVED),
        anomalies=[],
    )


@pytest.fixture
def enriched_worktree_with_anomalies(enriched_worktree_full) -> EnrichedWorktree:
    """Enriched worktree with anomalies.

    Uses deepcopy to avoid mutating the shared enriched_worktree_full fixture.
    """
    wt = deepcopy(enriched_worktree_full)
    wt.ci_checks = CIChecks(total=3, passed=1, failed=1, pending=1)
    wt.coderabbit = CodeRabbitStatus(
        status=CodeRabbitReviewStatus.CHANGES_REQUESTED,
        feedback=CodeRabbitFeedback(major=2, minor=1, total=3),
    )
    wt.anomalies = [
        Anomaly(
            type=AnomalyType.CI_FAILURE,
            severity=AnomalySeverity.HIGH,
            message="CI check 'test' failed",
            worktree_path=wt.path,
            branch=wt.branch,
        ),
        Anomaly(
            type=AnomalyType.CHANGES_REQUESTED,
            severity=AnomalySeverity.MEDIUM,
            message="CodeRabbit requested changes (2 major)",
            worktree_path=wt.path,
            branch=wt.branch,
        ),
    ]
    return wt


@pytest.fixture
def track_summary_sample() -> TrackSummary:
    """Sample track summary."""
    return TrackSummary(
        name="QA Enforcement",
        epic=145,
        color="#dc2626",
        worktree_count=1,
        issues_open=2,
        issues_closed=2,
        status=WorkstreamStatus.IN_PROGRESS,
    )


@pytest.fixture
def monitor_output_sample(
    fixed_now, enriched_worktree_full, track_summary_sample, heartbeat_status_fresh
) -> MonitorOutput:
    """Complete MonitorOutput sample."""
    return MonitorOutput(
        timestamp=fixed_now,
        config_version=1,
        milestone="v0.10",
        worktree_count=1,
        worktrees=[enriched_worktree_full],
        tracks=[track_summary_sample],
        archived=[],
        heartbeat=heartbeat_status_fresh,
        anomalies=[],
        errors=[],
    )


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture
def tmp_config_dir(tmp_path, valid_version_plan_yaml) -> Path:
    """Temporary config directory with version plan."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "version-plan.yaml").write_text(
        valid_version_plan_yaml, encoding="utf-8"
    )
    return config_dir


@pytest.fixture
def version_plan_model() -> VersionPlan:
    """Sample VersionPlan model object."""
    return VersionPlan(
        version=1,
        name="v0.10",
        target_date="2026-04-30",
        description="Agent Orchestration Enhancements",
        status=VersionStatus.IN_PROGRESS,
        phases=[
            PhaseConfig(
                name="Phase A",
                order=1,
                description="Foundation",
                status=PhaseStatus.COMPLETE,
                workstreams=[
                    WorkstreamConfig(
                        name="Agent Memory & Learning",
                        epic=143,
                        branches=["feat/agent-memory", "feat/memory-*"],
                        status=WorkstreamStatus.COMPLETE,
                        color="#7c3aed",
                    ),
                ],
            ),
            PhaseConfig(
                name="Phase B",
                order=2,
                description="Quality & Observability",
                status=PhaseStatus.IN_PROGRESS,
                dependencies=["Phase A"],
                workstreams=[
                    WorkstreamConfig(
                        name="QA Enforcement",
                        epic=145,
                        branches=["feat/qa-enforcement", "feat/qa-*"],
                        status=WorkstreamStatus.COMPLETE,
                        color="#dc2626",
                    ),
                ],
            ),
        ],
    )


# =============================================================================
# Mock Objects
# =============================================================================


@pytest.fixture
def mock_subprocess():
    """Mock for subprocess.run."""
    return MagicMock()


@pytest.fixture
def mock_gh_cli():
    """Mock for gh CLI commands."""

    def _mock_response(command: list[str]) -> str:
        cmd_str = " ".join(command)
        if "pr list" in cmd_str:
            return json.dumps([{"number": 184, "state": "open"}])
        elif "pr view" in cmd_str:
            return json.dumps(
                {
                    "number": 184,
                    "state": "open",
                    "title": "feat(qa): implement QA enforcement",
                }
            )
        return "{}"

    return _mock_response
