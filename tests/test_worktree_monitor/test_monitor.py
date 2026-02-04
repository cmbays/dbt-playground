"""
Worktree Monitor v2.0 - WorktreeMonitor Orchestrator Tests

TDD tests for the main WorktreeMonitor orchestrator class.

Test Categories:
1. Initialization (WM-INIT-*)
2. Collection (WM-COLLECT-*)
3. Enrichment (WM-ENRICH-*)
4. GitHub Integration (WM-GITHUB-*)
5. Anomaly Detection (WM-ANOMALY-*)
6. Write Output (WM-WRITE-*)
7. Additional Tests (hot-reload, health summary, cache)

Created: Phase 4 Day 4
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from worktree_monitor.constants import (
    AnomalySeverity,
    AnomalyType,
    CodeRabbitReviewStatus,
    HeartbeatState,
    PhaseStatus,
    PRState,
    VersionStatus,
    WorkstreamStatus,
    WorktreeStatus,
)
from worktree_monitor.exceptions import (
    ArchiveCorruptedError,
    GitHubAPIError,
    GitWorktreeError,
    HeartbeatFileNotFoundError,
    HeartbeatParseError,
    RateLimitError,
    VersionPlanNotFoundError,
    VersionPlanParseError,
    VersionPlanValidationError,
)
from worktree_monitor.models import (
    Anomaly,
    CIChecks,
    CodeRabbitStatus,
    ComponentFailureInfo,
    EnrichedWorktree,
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
from worktree_monitor.monitor import MonitorWriteError, WorktreeMonitor


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_version_plan_loader(version_plan_model):
    """Mock VersionPlanLoader with sample plan."""
    loader = MagicMock()
    loader.reload_if_changed.return_value = None
    loader.load.return_value = version_plan_model
    loader.get_workstream_for_branch.return_value = None
    loader.match_branch_to_workstream.return_value = None
    return loader


@pytest.fixture
def mock_worktree_discovery(sample_worktree_main, sample_worktree_info):
    """Mock WorktreeDiscovery with sample worktrees."""
    discovery = MagicMock()
    discovery.list_worktrees.return_value = [
        sample_worktree_main,
        sample_worktree_info,
    ]
    return discovery


@pytest.fixture
def mock_github_adapter():
    """Mock GitHubAdapter with no data."""
    adapter = MagicMock()
    adapter.get_pr_state.return_value = None
    adapter.get_ci_status.return_value = None
    adapter.get_coderabbit_status.return_value = None
    adapter.clear_cache.return_value = None
    return adapter


@pytest.fixture
def mock_heartbeat_monitor(heartbeat_status_fresh):
    """Mock HeartbeatMonitor returning fresh status."""
    monitor = MagicMock()
    monitor.get_status.return_value = heartbeat_status_fresh
    monitor.get_state.return_value = HeartbeatState.FRESH
    return monitor


@pytest.fixture
def mock_archive_manager():
    """Mock ArchiveManager returning empty list."""
    manager = MagicMock()
    manager.list_versions.return_value = []
    return manager


@pytest.fixture
def worktree_monitor(
    mock_version_plan_loader,
    mock_worktree_discovery,
    mock_github_adapter,
):
    """Fully mocked WorktreeMonitor with required dependencies only."""
    return WorktreeMonitor(
        version_plan_loader=mock_version_plan_loader,
        worktree_discovery=mock_worktree_discovery,
        github_adapter=mock_github_adapter,
    )


@pytest.fixture
def worktree_monitor_full(
    mock_version_plan_loader,
    mock_worktree_discovery,
    mock_github_adapter,
    mock_heartbeat_monitor,
    mock_archive_manager,
):
    """Fully mocked WorktreeMonitor with all dependencies."""
    return WorktreeMonitor(
        version_plan_loader=mock_version_plan_loader,
        worktree_discovery=mock_worktree_discovery,
        github_adapter=mock_github_adapter,
        heartbeat_monitor=mock_heartbeat_monitor,
        archive_manager=mock_archive_manager,
    )


# =============================================================================
# Test 1: Initialization (WM-INIT-*)
# =============================================================================


class TestInitialization:
    """Test WorktreeMonitor constructor."""

    def test_wm_init_01_constructor_accepts_all_parameters(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        mock_heartbeat_monitor,
        mock_archive_manager,
    ):
        """WM-INIT-01: Constructor accepts all parameters."""
        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
            heartbeat_monitor=mock_heartbeat_monitor,
            archive_manager=mock_archive_manager,
            include_main_worktree=False,
            github_enrichment_enabled=False,
            anomaly_detection_enabled=False,
        )

        assert monitor._version_plan_loader is mock_version_plan_loader
        assert monitor._worktree_discovery is mock_worktree_discovery
        assert monitor._github_adapter is mock_github_adapter
        assert monitor._heartbeat_monitor is mock_heartbeat_monitor
        assert monitor._archive_manager is mock_archive_manager
        assert monitor._include_main_worktree is False
        assert monitor._github_enrichment_enabled is False
        assert monitor._anomaly_detection_enabled is False

    def test_wm_init_02_constructor_with_optional_params_none(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
    ):
        """WM-INIT-02: Constructor with optional params None."""
        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
            heartbeat_monitor=None,
            archive_manager=None,
        )

        assert monitor._heartbeat_monitor is None
        assert monitor._archive_manager is None
        # Default values for keyword args
        assert monitor._include_main_worktree is True
        assert monitor._github_enrichment_enabled is True
        assert monitor._anomaly_detection_enabled is True

    def test_constructor_initializes_internal_state(self, worktree_monitor):
        """Constructor initializes internal state correctly."""
        assert worktree_monitor._cached_plan is None
        assert worktree_monitor._last_collection is None
        assert worktree_monitor._rate_limited_until is None
        assert len(worktree_monitor._recent_errors) == 0


# =============================================================================
# Test 2: Collection (WM-COLLECT-*)
# =============================================================================


class TestCollect:
    """Test WorktreeMonitor.collect() method."""

    def test_wm_collect_01_returns_monitor_output(
        self, worktree_monitor, fixed_now
    ):
        """WM-COLLECT-01: Collect returns MonitorOutput."""
        output = worktree_monitor.collect(now=fixed_now)

        assert isinstance(output, MonitorOutput)
        assert output.timestamp == fixed_now
        assert isinstance(output.worktrees, list)
        assert isinstance(output.tracks, list)
        assert isinstance(output.anomalies, list)
        assert isinstance(output.errors, list)

    def test_wm_collect_02_handles_empty_worktree_list(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        fixed_now,
    ):
        """WM-COLLECT-02: Collect handles empty worktree list."""
        mock_worktree_discovery.list_worktrees.return_value = []

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        output = monitor.collect(now=fixed_now)

        assert output.worktree_count == 0
        assert output.worktrees == []

    def test_wm_collect_03_records_component_errors(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        fixed_now,
    ):
        """WM-COLLECT-03: Collect records component errors."""
        # Make version plan loader raise an error
        mock_version_plan_loader.reload_if_changed.side_effect = (
            VersionPlanNotFoundError("/path/to/config.yaml")
        )
        mock_version_plan_loader.load.side_effect = (
            VersionPlanNotFoundError("/path/to/config.yaml")
        )

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        output = monitor.collect(now=fixed_now)

        # Should have error recorded but not crash
        assert len(output.errors) >= 1
        assert output.errors[0].component == "VersionPlanLoader"

    def test_collect_records_worktree_discovery_error(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        fixed_now,
    ):
        """Collect records WorktreeDiscovery errors."""
        mock_worktree_discovery.list_worktrees.side_effect = GitWorktreeError(
            "git worktree list failed"
        )

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        output = monitor.collect(now=fixed_now)

        assert output.worktrees == []
        assert any(
            err.component == "WorktreeDiscovery" for err in output.errors
        )

    def test_collect_updates_last_collection_timestamp(
        self, worktree_monitor, fixed_now
    ):
        """Collect updates last_collection timestamp."""
        assert worktree_monitor._last_collection is None

        worktree_monitor.collect(now=fixed_now)

        assert worktree_monitor._last_collection == fixed_now

    def test_collect_sets_config_version_and_milestone(
        self, worktree_monitor, fixed_now, version_plan_model
    ):
        """Collect sets config_version and milestone from plan."""
        worktree_monitor._version_plan_loader.load.return_value = (
            version_plan_model
        )

        output = worktree_monitor.collect(now=fixed_now)

        assert output.config_version == version_plan_model.version
        assert output.milestone == version_plan_model.name


# =============================================================================
# Test 3: Enrichment (WM-ENRICH-*)
# =============================================================================


class TestEnrichment:
    """Test worktree enrichment with track info."""

    def test_wm_enrich_01_enrich_adds_track_info(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        sample_worktree_info,
        fixed_now,
    ):
        """WM-ENRICH-01: Enrich adds track info."""
        # Setup workstream matching
        workstream = WorkstreamConfig(
            name="QA Enforcement",
            epic=145,
            branches=["feat/qa-*"],
            status=WorkstreamStatus.IN_PROGRESS,
            color="#dc2626",
        )
        phase = PhaseConfig(
            name="Phase B",
            order=2,
            workstreams=[workstream],
            status=PhaseStatus.IN_PROGRESS,
        )
        mock_version_plan_loader.get_workstream_for_branch.return_value = (
            phase,
            workstream,
        )

        # Single worktree with matching branch
        wt = WorktreeInfo(
            path="/test/path",
            branch="feat/qa-enforcement",
            commit_hash="abc123",
            commit_short="abc",
            is_main=False,
            status=WorktreeStatus.CLEAN,
            files_changed=0,
            files_staged=0,
            last_commit_msg="test",
            last_commit_date=fixed_now,
        )
        mock_worktree_discovery.list_worktrees.return_value = [wt]

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        output = monitor.collect(now=fixed_now)

        assert len(output.worktrees) == 1
        enriched = output.worktrees[0]
        assert enriched.track_name == "QA Enforcement"
        assert enriched.track_color == "#dc2626"
        assert enriched.epic_number == 145

    def test_wm_enrich_02_enrich_handles_no_match(
        self, worktree_monitor, fixed_now
    ):
        """WM-ENRICH-02: Enrich handles no match."""
        # Default mock returns None for workstream matching
        output = worktree_monitor.collect(now=fixed_now)

        # Should have worktrees but without track info
        for wt in output.worktrees:
            if not wt.is_main:
                assert wt.track_name is None


# =============================================================================
# Test 4: GitHub Integration (WM-GITHUB-*)
# =============================================================================


class TestGitHubIntegration:
    """Test GitHub enrichment behavior."""

    def test_wm_github_01_github_enrichment_disabled(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        fixed_now,
    ):
        """WM-GITHUB-01: GitHub enrichment disabled."""
        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
            github_enrichment_enabled=False,
        )

        monitor.collect(now=fixed_now)

        # GitHub adapter should not be called
        mock_github_adapter.get_pr_state.assert_not_called()

    def test_wm_github_02_rate_limit_disables_further_calls(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        sample_worktree_info,
        fixed_now,
    ):
        """WM-GITHUB-02: Rate limit disables further calls."""
        # Setup two non-main worktrees
        wt1 = WorktreeInfo(
            path="/test/wt1",
            branch="feat/branch1",
            commit_hash="abc123",
            commit_short="abc",
            is_main=False,
            status=WorktreeStatus.CLEAN,
            files_changed=0,
            files_staged=0,
            last_commit_msg="test1",
            last_commit_date=fixed_now,
        )
        wt2 = WorktreeInfo(
            path="/test/wt2",
            branch="feat/branch2",
            commit_hash="def456",
            commit_short="def",
            is_main=False,
            status=WorktreeStatus.CLEAN,
            files_changed=0,
            files_staged=0,
            last_commit_msg="test2",
            last_commit_date=fixed_now,
        )
        mock_worktree_discovery.list_worktrees.return_value = [wt1, wt2]

        # First call raises rate limit error
        mock_github_adapter.get_pr_state.side_effect = [
            RateLimitError(429, "Rate limited"),
            PRInfo(
                url="http://test",
                number=1,
                state=PRState.OPEN,
                title="Test",
                draft=False,
            ),
        ]

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        output = monitor.collect(now=fixed_now)

        # Should be rate limited
        assert monitor._rate_limited_until is not None
        assert monitor._rate_limited_until > fixed_now

    def test_github_adapter_api_error_graceful(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        sample_worktree_info,
        fixed_now,
    ):
        """GitHub API errors are handled gracefully."""
        mock_worktree_discovery.list_worktrees.return_value = [
            sample_worktree_info
        ]
        mock_github_adapter.get_pr_state.side_effect = GitHubAPIError(
            "API error"
        )

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        output = monitor.collect(now=fixed_now)

        # Should not crash, just have no PR data
        assert len(output.worktrees) == 1
        assert output.worktrees[0].pr is None

    def test_main_worktree_skips_github(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        sample_worktree_main,
        fixed_now,
    ):
        """Main worktree skips GitHub enrichment."""
        mock_worktree_discovery.list_worktrees.return_value = [
            sample_worktree_main
        ]

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        monitor.collect(now=fixed_now)

        # GitHub adapter should not be called for main
        mock_github_adapter.get_pr_state.assert_not_called()

    def test_rate_limit_expires_and_resumes(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        sample_worktree_info,
        fixed_now,
    ):
        """Rate limit expires and GitHub calls resume."""
        # Setup: one worktree that's not main
        sample_worktree_info.is_main = False
        mock_worktree_discovery.list_worktrees.return_value = [sample_worktree_info]

        # First call raises rate limit
        mock_github_adapter.get_pr_state.side_effect = RateLimitError(429, "Rate limited")

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        # First collect triggers rate limit
        monitor.collect(now=fixed_now)
        assert monitor._rate_limited_until is not None

        # Reset mock for subsequent calls
        mock_github_adapter.get_pr_state.reset_mock()
        mock_github_adapter.get_pr_state.side_effect = None
        mock_github_adapter.get_pr_state.return_value = PRInfo(
            url="http://test", number=1, state=PRState.OPEN, title="Test", draft=False
        )

        # Collect DURING rate limit - should skip GitHub (no call)
        during_limit = fixed_now + timedelta(minutes=1)
        monitor.collect(now=during_limit)
        mock_github_adapter.get_pr_state.assert_not_called()

        # Collect AFTER rate limit expires - should call GitHub again
        after_limit = fixed_now + timedelta(minutes=6)  # RATE_LIMIT_COOLDOWN_MINUTES = 5
        output = monitor.collect(now=after_limit)
        mock_github_adapter.get_pr_state.assert_called_once()


# =============================================================================
# Test 5: Anomaly Detection (WM-ANOMALY-*)
# =============================================================================


class TestAnomalyDetection:
    """Test anomaly detection functionality."""

    def test_wm_anomaly_01_detects_ci_failure(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        fixed_now,
    ):
        """WM-ANOMALY-01: Detects CI failure."""
        wt = WorktreeInfo(
            path="/test/path",
            branch="feat/ci-failing",
            commit_hash="abc123",
            commit_short="abc",
            is_main=False,
            status=WorktreeStatus.CLEAN,
            files_changed=0,
            files_staged=0,
            last_commit_msg="test",
            last_commit_date=fixed_now,
        )
        mock_worktree_discovery.list_worktrees.return_value = [wt]

        # Setup PR with failing CI
        mock_github_adapter.get_pr_state.return_value = PRInfo(
            url="http://test",
            number=123,
            state=PRState.OPEN,
            title="Test PR",
            draft=False,
        )
        mock_github_adapter.get_ci_status.return_value = CIChecks(
            total=3, passed=1, failed=2, pending=0
        )

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        output = monitor.collect(now=fixed_now)

        ci_anomalies = [
            a for a in output.anomalies if a.type == AnomalyType.CI_FAILURE
        ]
        assert len(ci_anomalies) == 1
        assert ci_anomalies[0].severity == AnomalySeverity.HIGH

    def test_wm_anomaly_02_detects_stale_heartbeat(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        mock_heartbeat_monitor,
        fixed_now,
    ):
        """WM-ANOMALY-02: Detects stale heartbeat."""
        mock_heartbeat_monitor.get_status.return_value = HeartbeatStatus(
            state=HeartbeatState.STALE,
            last_update=fixed_now - timedelta(seconds=90),
            seconds_since_update=90.0,
            active_orchestrators=[],
        )

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
            heartbeat_monitor=mock_heartbeat_monitor,
        )

        output = monitor.collect(now=fixed_now)

        stale_anomalies = [
            a
            for a in output.anomalies
            if a.type == AnomalyType.STALE_HEARTBEAT
        ]
        assert len(stale_anomalies) == 1
        assert stale_anomalies[0].severity == AnomalySeverity.MEDIUM

    def test_detects_dirty_worktree(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        fixed_now,
    ):
        """Detects dirty worktree anomaly."""
        wt = WorktreeInfo(
            path="/test/dirty",
            branch="feat/dirty-branch",
            commit_hash="abc123",
            commit_short="abc",
            is_main=False,
            status=WorktreeStatus.DIRTY,
            files_changed=5,
            files_staged=2,
            last_commit_msg="wip",
            last_commit_date=fixed_now,
        )
        mock_worktree_discovery.list_worktrees.return_value = [wt]

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        output = monitor.collect(now=fixed_now)

        dirty_anomalies = [
            a
            for a in output.anomalies
            if a.type == AnomalyType.DIRTY_WORKTREE
        ]
        assert len(dirty_anomalies) == 1
        assert dirty_anomalies[0].severity == AnomalySeverity.LOW
        assert "5 files" in dirty_anomalies[0].message

    def test_detects_disconnected_orchestrator(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        mock_heartbeat_monitor,
        fixed_now,
    ):
        """Detects disconnected orchestrator anomaly."""
        mock_heartbeat_monitor.get_status.return_value = HeartbeatStatus(
            state=HeartbeatState.DISCONNECTED,
            last_update=fixed_now,
            seconds_since_update=float("inf"),
            active_orchestrators=[],
        )

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
            heartbeat_monitor=mock_heartbeat_monitor,
        )

        output = monitor.collect(now=fixed_now)

        disconnected = [
            a
            for a in output.anomalies
            if a.type == AnomalyType.DISCONNECTED_ORCHESTRATOR
        ]
        assert len(disconnected) == 1
        assert disconnected[0].severity == AnomalySeverity.HIGH

    def test_multiple_anomaly_types_together(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        mock_heartbeat_monitor,
        fixed_now,
    ):
        """Multiple anomaly types detected together."""
        wt = WorktreeInfo(
            path="/test/multi",
            branch="feat/multi-issues",
            commit_hash="abc123",
            commit_short="abc",
            is_main=False,
            status=WorktreeStatus.DIRTY,
            files_changed=3,
            files_staged=0,
            last_commit_msg="wip",
            last_commit_date=fixed_now,
        )
        mock_worktree_discovery.list_worktrees.return_value = [wt]

        # Failing CI
        mock_github_adapter.get_pr_state.return_value = PRInfo(
            url="http://test",
            number=100,
            state=PRState.OPEN,
            title="Test",
            draft=False,
        )
        mock_github_adapter.get_ci_status.return_value = CIChecks(
            total=2, passed=1, failed=1, pending=0
        )

        # Stale heartbeat
        mock_heartbeat_monitor.get_status.return_value = HeartbeatStatus(
            state=HeartbeatState.STALE,
            last_update=fixed_now - timedelta(seconds=90),
            seconds_since_update=90.0,
            active_orchestrators=[],
        )

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
            heartbeat_monitor=mock_heartbeat_monitor,
        )

        output = monitor.collect(now=fixed_now)

        # Should have: CI failure, dirty worktree, stale heartbeat
        anomaly_types = {a.type for a in output.anomalies}
        assert AnomalyType.CI_FAILURE in anomaly_types
        assert AnomalyType.DIRTY_WORKTREE in anomaly_types
        assert AnomalyType.STALE_HEARTBEAT in anomaly_types

    def test_anomaly_detection_disabled(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        fixed_now,
    ):
        """Anomaly detection can be disabled."""
        wt = WorktreeInfo(
            path="/test/dirty",
            branch="feat/dirty",
            commit_hash="abc123",
            commit_short="abc",
            is_main=False,
            status=WorktreeStatus.DIRTY,
            files_changed=10,
            files_staged=0,
            last_commit_msg="wip",
            last_commit_date=fixed_now,
        )
        mock_worktree_discovery.list_worktrees.return_value = [wt]

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
            anomaly_detection_enabled=False,
        )

        output = monitor.collect(now=fixed_now)

        assert output.anomalies == []


# =============================================================================
# Test 6: Write Output (WM-WRITE-*)
# =============================================================================


class TestWriteOutput:
    """Test MonitorOutput file writing."""

    def test_wm_write_01_write_creates_file(
        self, worktree_monitor, fixed_now, tmp_path
    ):
        """WM-WRITE-01: Write creates file."""
        output = worktree_monitor.collect(now=fixed_now)
        output_path = tmp_path / "worktrees.json"

        worktree_monitor.write_output(output, output_path)

        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["timestamp"] == fixed_now.isoformat()

    def test_wm_write_02_write_is_atomic(
        self, worktree_monitor, fixed_now, tmp_path
    ):
        """WM-WRITE-02: Write is atomic (no partial files)."""
        output = worktree_monitor.collect(now=fixed_now)
        output_path = tmp_path / "worktrees.json"

        # Write should complete atomically
        worktree_monitor.write_output(output, output_path)

        # File should exist and be valid JSON
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)
        assert "timestamp" in data

        # No temp files should remain
        temp_files = list(tmp_path.glob("*.tmp"))
        assert len(temp_files) == 0

    def test_write_creates_parent_directories(
        self, worktree_monitor, fixed_now, tmp_path
    ):
        """Write creates parent directories if needed."""
        output = worktree_monitor.collect(now=fixed_now)
        output_path = tmp_path / "nested" / "dir" / "worktrees.json"

        worktree_monitor.write_output(output, output_path)

        assert output_path.exists()

    def test_write_raises_monitor_write_error_on_permission_denied(
        self, worktree_monitor, fixed_now, tmp_path
    ):
        """Write raises MonitorWriteError on permission denied."""
        output = worktree_monitor.collect(now=fixed_now)

        # Create directory and make it read-only
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        os.chmod(readonly_dir, 0o444)

        try:
            output_path = readonly_dir / "worktrees.json"
            with pytest.raises(MonitorWriteError) as exc_info:
                worktree_monitor.write_output(output, output_path)

            assert "Permission denied" in exc_info.value.reason
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)

    def test_atomic_write_cleans_up_temp_on_json_error(
        self, worktree_monitor, fixed_now, tmp_path
    ):
        """Atomic write cleans up temp file on JSON serialization error."""
        output = worktree_monitor.collect(now=fixed_now)
        output_path = tmp_path / "worktrees.json"

        # Patch json.dump to raise an error after temp file is created
        # Note: TypeError is caught in inner try, temp file cleaned up, then re-raised
        with patch("worktree_monitor.monitor.json.dump") as mock_dump:
            mock_dump.side_effect = TypeError("Cannot serialize object")

            with pytest.raises(TypeError):
                worktree_monitor.write_output(output, output_path)

        # No temp files should remain
        temp_files = list(tmp_path.glob("*.tmp"))
        assert len(temp_files) == 0, f"Temp files remain: {temp_files}"

        # Output file should not exist (atomic - all or nothing)
        assert not output_path.exists()


# =============================================================================
# Test 7: Additional Tests (hot-reload, health summary, cache)
# =============================================================================


class TestHotReload:
    """Test configuration hot-reload behavior."""

    def test_hot_reload_detection(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        version_plan_model,
        fixed_now,
    ):
        """Hot-reload updates cached plan when file changes."""
        # First call: no reload
        mock_version_plan_loader.reload_if_changed.return_value = None
        mock_version_plan_loader.load.return_value = version_plan_model

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        monitor.collect(now=fixed_now)
        assert monitor._cached_plan == version_plan_model

        # Second call: reload with new plan
        new_plan = VersionPlan(
            version=2,
            name="v0.11",
            target_date="2026-06-30",
            phases=[],
            status=VersionStatus.PLANNED,
        )
        mock_version_plan_loader.reload_if_changed.return_value = new_plan

        monitor.collect(now=fixed_now)
        assert monitor._cached_plan == new_plan


class TestMainWorktreeFiltering:
    """Test main worktree filtering behavior."""

    def test_main_worktree_included_by_default(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        sample_worktree_main,
        sample_worktree_info,
        fixed_now,
    ):
        """Main worktree is included by default."""
        mock_worktree_discovery.list_worktrees.return_value = [
            sample_worktree_main,
            sample_worktree_info,
        ]

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        output = monitor.collect(now=fixed_now)

        assert output.worktree_count == 2
        branches = [wt.branch for wt in output.worktrees]
        assert "main" in branches

    def test_main_worktree_excluded_when_disabled(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        sample_worktree_main,
        sample_worktree_info,
        fixed_now,
    ):
        """Main worktree excluded when include_main_worktree=False."""
        mock_worktree_discovery.list_worktrees.return_value = [
            sample_worktree_main,
            sample_worktree_info,
        ]

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
            include_main_worktree=False,
        )

        output = monitor.collect(now=fixed_now)

        assert output.worktree_count == 1
        branches = [wt.branch for wt in output.worktrees]
        assert "main" not in branches


class TestHealthSummary:
    """Test get_health_summary() method."""

    def test_health_summary_output(self, worktree_monitor_full, fixed_now):
        """Health summary returns expected fields."""
        # Do a collection first
        worktree_monitor_full.collect(now=fixed_now)

        summary = worktree_monitor_full.get_health_summary()

        assert "version_plan_loaded" in summary
        assert "heartbeat_state" in summary
        assert "worktree_count" in summary
        assert "last_collection" in summary
        assert "errors" in summary

    def test_health_summary_before_collection(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
    ):
        """Health summary works before any collection."""
        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        summary = monitor.get_health_summary()

        assert summary["version_plan_loaded"] is False
        assert summary["last_collection"] is None


class TestClearCache:
    """Test clear_cache() method."""

    def test_clear_cache_resets_rate_limit(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        fixed_now,
    ):
        """clear_cache resets rate limit state."""
        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )

        # Simulate rate limit
        monitor._rate_limited_until = fixed_now + timedelta(minutes=5)

        monitor.clear_cache()

        assert monitor._rate_limited_until is None
        mock_github_adapter.clear_cache.assert_called_once()


class TestGetVersionPlan:
    """Test get_version_plan() method."""

    def test_get_version_plan_returns_cached(
        self, worktree_monitor, version_plan_model, fixed_now
    ):
        """get_version_plan returns cached plan after collection."""
        worktree_monitor._version_plan_loader.load.return_value = (
            version_plan_model
        )

        worktree_monitor.collect(now=fixed_now)

        plan = worktree_monitor.get_version_plan()
        assert plan == version_plan_model

    def test_get_version_plan_returns_none_before_collection(
        self, worktree_monitor
    ):
        """get_version_plan returns None before any collection."""
        plan = worktree_monitor.get_version_plan()
        assert plan is None


class TestHeartbeatCollection:
    """Test heartbeat collection behavior."""

    def test_heartbeat_not_configured(self, worktree_monitor, fixed_now):
        """Heartbeat is None when monitor not configured."""
        output = worktree_monitor.collect(now=fixed_now)

        assert output.heartbeat is None

    def test_heartbeat_file_not_found(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        mock_heartbeat_monitor,
        fixed_now,
    ):
        """Heartbeat file not found returns DISCONNECTED state."""
        mock_heartbeat_monitor.get_status.side_effect = (
            HeartbeatFileNotFoundError("/path/to/heartbeat.json")
        )

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
            heartbeat_monitor=mock_heartbeat_monitor,
        )

        output = monitor.collect(now=fixed_now)

        assert output.heartbeat is not None
        assert output.heartbeat.state == HeartbeatState.DISCONNECTED

    def test_heartbeat_parse_error_records_error(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        mock_heartbeat_monitor,
        fixed_now,
    ):
        """Heartbeat parse error is recorded in errors."""
        mock_heartbeat_monitor.get_status.side_effect = HeartbeatParseError(
            "/path/to/heartbeat.json", "Invalid JSON"
        )

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
            heartbeat_monitor=mock_heartbeat_monitor,
        )

        output = monitor.collect(now=fixed_now)

        assert output.heartbeat is None
        assert any(
            err.component == "HeartbeatMonitor" for err in output.errors
        )


class TestArchiveCollection:
    """Test archive collection behavior."""

    def test_archive_not_configured(self, worktree_monitor, fixed_now):
        """Archived is empty when manager not configured."""
        output = worktree_monitor.collect(now=fixed_now)

        assert output.archived == []

    def test_archive_corrupted_records_error(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        mock_archive_manager,
        fixed_now,
    ):
        """Archive corruption is recorded in errors."""
        mock_archive_manager.list_versions.side_effect = ArchiveCorruptedError(
            "v0.9", "Invalid index"
        )

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
            archive_manager=mock_archive_manager,
        )

        output = monitor.collect(now=fixed_now)

        assert output.archived == []
        assert any(
            err.component == "ArchiveManager" for err in output.errors
        )


# =============================================================================
# Test 8: Run Polling (WM-POLL-*)
# =============================================================================


class TestRunPolling:
    """Test run_polling() continuous polling behavior."""

    def test_run_polling_rejects_invalid_interval_zero(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        tmp_path,
    ):
        """run_polling rejects interval_seconds=0 with ValueError."""
        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )
        output_path = tmp_path / "worktrees.json"

        with pytest.raises(ValueError) as exc_info:
            monitor.run_polling(output_path, interval_seconds=0)

        assert "interval_seconds must be >= 1" in str(exc_info.value)
        assert "got 0" in str(exc_info.value)

    def test_run_polling_rejects_invalid_interval_negative(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        tmp_path,
    ):
        """run_polling rejects interval_seconds=-1 with ValueError."""
        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )
        output_path = tmp_path / "worktrees.json"

        with pytest.raises(ValueError) as exc_info:
            monitor.run_polling(output_path, interval_seconds=-1)

        assert "interval_seconds must be >= 1" in str(exc_info.value)
        assert "got -1" in str(exc_info.value)

    def test_run_polling_respects_stop_event(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        tmp_path,
    ):
        """run_polling stops when stop_event is set."""
        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )
        output_path = tmp_path / "worktrees.json"
        stop_event = threading.Event()

        # Start polling in background thread
        poll_thread = threading.Thread(
            target=monitor.run_polling,
            args=(output_path,),
            kwargs={"interval_seconds": 1, "stop_event": stop_event},
        )
        poll_thread.start()

        # Wait briefly to allow at least one cycle
        time.sleep(0.5)

        # Signal stop
        stop_event.set()

        # Verify thread stops within timeout (2 seconds should be plenty)
        poll_thread.join(timeout=2.0)
        assert not poll_thread.is_alive(), "Polling thread did not stop in time"

        # Verify output file was created
        assert output_path.exists(), "Output file should be created during polling"

    def test_run_polling_writes_output_each_cycle(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        tmp_path,
    ):
        """run_polling writes output file each cycle with valid JSON."""
        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )
        output_path = tmp_path / "worktrees.json"
        stop_event = threading.Event()

        # Start polling with 1-second interval
        poll_thread = threading.Thread(
            target=monitor.run_polling,
            args=(output_path,),
            kwargs={"interval_seconds": 1, "stop_event": stop_event},
        )
        poll_thread.start()

        # Wait for ~2.5 seconds to allow multiple cycles
        time.sleep(2.5)

        # Stop polling
        stop_event.set()
        poll_thread.join(timeout=2.0)

        # Verify file exists and contains valid JSON
        assert output_path.exists()
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

        # Verify it has expected structure
        assert "timestamp" in data
        assert "worktree_count" in data
        assert "worktrees" in data

    def test_run_polling_escalates_consecutive_failures(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        tmp_path,
    ):
        """run_polling raises after MAX_CONSECUTIVE_FAILURES (10) write failures."""
        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )
        output_path = tmp_path / "worktrees.json"

        # Mock write_output to always raise MonitorWriteError
        with patch.object(
            monitor,
            "write_output",
            side_effect=MonitorWriteError(str(output_path), "Simulated disk full"),
        ):
            with pytest.raises(MonitorWriteError) as exc_info:
                # This should fail after 10 consecutive failures
                monitor.run_polling(output_path, interval_seconds=1, stop_event=None)

            assert "Simulated disk full" in exc_info.value.reason

    def test_run_polling_recovery_after_transient_error(
        self,
        mock_version_plan_loader,
        mock_worktree_discovery,
        mock_github_adapter,
        tmp_path,
    ):
        """run_polling recovers after a transient discovery error."""
        # Configure discovery to fail once, then succeed
        call_count = [0]
        original_list = mock_worktree_discovery.list_worktrees

        def failing_then_succeeding():
            call_count[0] += 1
            if call_count[0] == 1:
                raise GitWorktreeError("Transient git error")
            return original_list.return_value

        mock_worktree_discovery.list_worktrees.side_effect = failing_then_succeeding

        monitor = WorktreeMonitor(
            version_plan_loader=mock_version_plan_loader,
            worktree_discovery=mock_worktree_discovery,
            github_adapter=mock_github_adapter,
        )
        output_path = tmp_path / "worktrees.json"
        stop_event = threading.Event()

        # Start polling
        poll_thread = threading.Thread(
            target=monitor.run_polling,
            args=(output_path,),
            kwargs={"interval_seconds": 1, "stop_event": stop_event},
        )
        poll_thread.start()

        # Wait for recovery (first call fails, second should succeed)
        time.sleep(2.5)

        # Stop polling
        stop_event.set()
        poll_thread.join(timeout=2.0)

        # Verify polling continued and file was created
        assert not poll_thread.is_alive(), "Thread should have stopped"
        assert output_path.exists(), "Output file should exist after recovery"

        # Verify multiple calls were made (showing recovery)
        assert call_count[0] >= 2, "Discovery should have been called multiple times"
