"""
Worktree Monitor v2.0 - Main Orchestrator

Integrates all modules to produce MonitorOutput for the UI.

Design principles:
- Dependency Injection: All modules passed via constructor for testability
- Graceful Degradation: Component failures don't crash the system
- Single Responsibility: Orchestration only, no data transformation logic
- Immutable Output: MonitorOutput is constructed fresh each collect()

Created: Phase 4 Day 4
"""

import json
import logging
import os
import tempfile
import time
import threading
import uuid
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .anomaly_detector import AnomalyDetector
from .archive_manager import ArchiveManager
from .constants import (
    AnomalySeverity,
    AnomalyType,
    ArchiveReason,
    CodeRabbitReviewStatus,
    HeartbeatState,
    WorkstreamStatus,
    WorktreeStatus,
)
from .exceptions import (
    ArchiveCorruptedError,
    GitHubAPIError,
    GitWorktreeError,
    HeartbeatFileNotFoundError,
    HeartbeatParseError,
    MonitorError,
    RateLimitError,
    VersionPlanNotFoundError,
    VersionPlanParseError,
    VersionPlanValidationError,
)
from .github_adapter import GitHubAdapter
from .heartbeat_monitor import HeartbeatMonitor
from .models import (
    Anomaly,
    ArchivedWorktree,
    CodeRabbitStatus,
    ComponentFailureInfo,
    EnrichedWorktree,
    HeartbeatStatus,
    MonitorOutput,
    PhaseConfig,
    PRInfo,
    CIChecks,
    TrackSummary,
    VersionPlan,
    WorkstreamConfig,
    WorktreeInfo,
)
from .version_plan_loader import VersionPlanLoader
from .worktree_discovery import WorktreeDiscovery

logger = logging.getLogger(__name__)


class MonitorWriteError(MonitorError):
    """Raised when writing monitor output fails."""

    def __init__(self, path: str, reason: str):
        super().__init__(
            f"Failed to write monitor output: {path}. Reason: {reason}",
            details={"path": path, "reason": reason},
        )
        self.path = path
        self.reason = reason


class WorktreeMonitor:
    """Main orchestrator for worktree monitoring.

    Integrates all modules to produce MonitorOutput:
    - VersionPlanLoader: Configuration and branch-to-workstream mapping
    - WorktreeDiscovery: Git worktree enumeration
    - GitHubAdapter: PR/CI/CodeRabbit status
    - HeartbeatMonitor: Orchestrator liveliness tracking
    - ArchiveManager: Historical version data

    Supports graceful degradation when components fail.

    Example:
        monitor = WorktreeMonitor(
            version_plan_loader=VersionPlanLoader(config_path),
            worktree_discovery=WorktreeDiscovery(repo_path),
            github_adapter=GitHubAdapter(repo="owner/repo"),
            heartbeat_monitor=HeartbeatMonitor(heartbeat_path),
            archive_manager=ArchiveManager(archives_dir),
        )

        output = monitor.collect()
        monitor.write_output(output, output_path)
    """

    # Rate limit cooldown period
    RATE_LIMIT_COOLDOWN_MINUTES = 5

    # Maximum workers for parallel GitHub enrichment
    MAX_GITHUB_WORKERS = 5

    def __init__(
        self,
        version_plan_loader: VersionPlanLoader,
        worktree_discovery: WorktreeDiscovery,
        github_adapter: GitHubAdapter,
        heartbeat_monitor: HeartbeatMonitor | None = None,
        archive_manager: ArchiveManager | None = None,
        *,
        include_main_worktree: bool = True,
        github_enrichment_enabled: bool = True,
        anomaly_detection_enabled: bool = True,
    ) -> None:
        """Initialize the WorktreeMonitor.

        Args:
            version_plan_loader: Required. Loads configuration and matches branches.
            worktree_discovery: Required. Discovers git worktrees.
            github_adapter: Required. Fetches PR/CI data (can disable via flag).
            heartbeat_monitor: Optional. Tracks orchestrator liveliness.
            archive_manager: Optional. Provides historical version data.
            include_main_worktree: Include the main worktree in output (default True).
            github_enrichment_enabled: Fetch GitHub data for worktrees (default True).
            anomaly_detection_enabled: Detect anomalies in worktrees (default True).
        """
        self._version_plan_loader = version_plan_loader
        self._worktree_discovery = worktree_discovery
        self._github_adapter = github_adapter
        self._heartbeat_monitor = heartbeat_monitor
        self._archive_manager = archive_manager

        self._include_main_worktree = include_main_worktree
        self._github_enrichment_enabled = github_enrichment_enabled
        self._anomaly_detection_enabled = anomaly_detection_enabled

        # Anomaly detector (extracted for SRP)
        self._anomaly_detector = AnomalyDetector()

        # Internal state
        self._cached_plan: VersionPlan | None = None
        self._last_collection: datetime | None = None
        self._rate_limited_until: datetime | None = None
        self._recent_errors: deque[str] = deque(maxlen=100)

    def collect(self, now: datetime | None = None) -> MonitorOutput:
        """Collect all monitoring data and return structured output.

        This is the primary method for data collection. It:
        1. Reloads configuration if changed (hot-reload)
        2. Discovers all git worktrees
        3. Enriches worktrees with GitHub data (if enabled)
        4. Detects anomalies (if enabled)
        5. Collects heartbeat status (if configured)
        6. Lists archived versions (if configured)

        Uses graceful degradation: component failures are recorded in
        output.errors but don't crash the collection.

        Args:
            now: Current timestamp (for testing). Defaults to UTC now.

        Returns:
            MonitorOutput with all collected data.

        Note:
            This method never raises exceptions. All errors are captured
            in MonitorOutput.errors as ComponentFailureInfo objects.
        """
        if now is None:
            now = datetime.now(UTC)

        errors: list[ComponentFailureInfo] = []

        # 1. Load/reload configuration
        plan = self._load_version_plan(now, errors)

        # 2. Discover worktrees
        worktrees_raw = self._collect_worktrees(now, errors)

        # 3. Enrich worktrees (parallel for performance)
        worktrees = self._enrich_worktrees_parallel(worktrees_raw, plan, now)

        # 4. Collect heartbeat
        heartbeat = self._collect_heartbeat(now, errors)

        # 5. Detect anomalies (using extracted detector)
        if self._anomaly_detection_enabled:
            anomalies = self._anomaly_detector.detect(worktrees, heartbeat)
            self._anomaly_detector.attach_to_worktrees(worktrees, anomalies)
        else:
            anomalies = []

        # 6. Build track summaries
        tracks = self._build_track_summaries(plan, worktrees) if plan else []

        # 7. Collect archived versions
        archived = self._collect_archived_versions(now, errors)

        # 8. Build output
        self._last_collection = now

        # Update recent errors for health summary
        self._recent_errors.clear()
        self._recent_errors.extend(err.message for err in errors)

        return MonitorOutput(
            timestamp=now,
            config_version=plan.version if plan else 0,
            milestone=plan.name if plan else "Unknown",
            worktree_count=len(worktrees),
            worktrees=worktrees,
            tracks=tracks,
            archived=archived,
            heartbeat=heartbeat,
            anomalies=anomalies,
            errors=errors,
        )

    def write_output(self, output: MonitorOutput, path: Path) -> None:
        """Write MonitorOutput to JSON file atomically.

        Uses temp file + rename pattern to prevent partial writes.
        Creates parent directories if they don't exist.

        Args:
            output: MonitorOutput to write.
            path: Target file path (e.g., playgrounds/worktrees.json).

        Raises:
            MonitorWriteError: If writing fails (permissions, disk full, etc).
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = self._serialize_output(output)
        self._atomic_write_json(path, data)

    def get_version_plan(self) -> VersionPlan | None:
        """Get the currently loaded version plan.

        Returns the cached plan from the last collect() call.
        Returns None if no collection has occurred or plan failed to load.

        Returns:
            VersionPlan or None.
        """
        return self._cached_plan

    def clear_cache(self) -> None:
        """Clear the GitHub adapter's cache.

        Call this to force fresh API calls on next collect().
        Useful when user manually triggers refresh.
        """
        self._github_adapter.clear_cache()
        self._rate_limited_until = None

    def get_health_summary(self) -> dict[str, Any]:
        """Get a quick health summary without full collection.

        Returns minimal status info for health checks:
        - version_plan_loaded: bool
        - heartbeat_state: str or None
        - worktree_count: int (from cache or 0)
        - last_collection: datetime or None
        - errors: list of recent error summaries

        Returns:
            Dictionary with health summary fields.
        """
        # Get heartbeat state if monitor is configured
        heartbeat_state: str | None = None
        if self._heartbeat_monitor is not None:
            try:
                state = self._heartbeat_monitor.get_state()
                heartbeat_state = state.value
            except (HeartbeatFileNotFoundError, HeartbeatParseError):
                heartbeat_state = HeartbeatState.DISCONNECTED.value

        # Get worktree count if possible
        worktree_count = 0
        try:
            worktrees = self._worktree_discovery.list_worktrees()
            if not self._include_main_worktree:
                worktrees = [wt for wt in worktrees if not wt.is_main]
            worktree_count = len(worktrees)
        except GitWorktreeError:
            pass

        return {
            "version_plan_loaded": self._cached_plan is not None,
            "heartbeat_state": heartbeat_state,
            "worktree_count": worktree_count,
            "last_collection": (
                self._last_collection.isoformat() if self._last_collection else None
            ),
            "errors": list(self._recent_errors),
        }

    def run_polling(
        self,
        output_path: Path,
        interval_seconds: int = 10,
        stop_event: threading.Event | None = None,
        max_runtime_seconds: int | None = None,
    ) -> None:
        """Run continuous polling mode.

        Collects and writes output at regular intervals until stopped.

        Args:
            output_path: Path to write worktrees.json.
            interval_seconds: Seconds between collections (default 10, minimum 1).
            stop_event: Event to signal stop. Required if max_runtime_seconds is None.
            max_runtime_seconds: Maximum runtime in seconds. If None, stop_event is required.

        Raises:
            ValueError: If interval_seconds < 1 or neither stop_event nor max_runtime_seconds provided.
            MonitorWriteError: If too many consecutive write failures occur.
        """
        if interval_seconds < 1:
            raise ValueError(f"interval_seconds must be >= 1, got {interval_seconds}")

        if stop_event is None and max_runtime_seconds is None:
            raise ValueError(
                "Either stop_event or max_runtime_seconds must be provided "
                "to prevent infinite polling"
            )

        MAX_CONSECUTIVE_FAILURES = 10
        consecutive_failures = 0
        start_time = time.monotonic()

        while not (stop_event and stop_event.is_set()):
            # Check max runtime
            if max_runtime_seconds is not None:
                elapsed = time.monotonic() - start_time
                if elapsed >= max_runtime_seconds:
                    logger.info(f"Max runtime ({max_runtime_seconds}s) reached. Stopping.")
                    break

            try:
                output = self.collect()
                self.write_output(output, output_path)
                consecutive_failures = 0  # Reset on success
            except MonitorWriteError as e:
                consecutive_failures += 1
                logger.error(f"Write failed ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES}): {e}")
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    logger.critical("Too many consecutive write failures. Monitor stopping.")
                    raise

            # Sleep in small increments for responsive stop
            for _ in range(interval_seconds):
                if stop_event and stop_event.is_set():
                    break
                # Also check max runtime during sleep
                if max_runtime_seconds is not None:
                    if time.monotonic() - start_time >= max_runtime_seconds:
                        break
                time.sleep(1)

    # -------------------------------------------------------------------------
    # Private: Configuration Loading
    # -------------------------------------------------------------------------

    def _load_version_plan(
        self,
        now: datetime,
        errors: list[ComponentFailureInfo],
    ) -> VersionPlan | None:
        """Load version plan with hot-reload and error handling.

        Args:
            now: Current timestamp for error records.
            errors: List to append errors to.

        Returns:
            VersionPlan if loaded successfully, cached plan on error, or None.
        """
        try:
            # Try reload if changed
            new_plan = self._version_plan_loader.reload_if_changed()
            if new_plan is not None:
                self._cached_plan = new_plan
                logger.info("Version plan reloaded")
            elif self._cached_plan is None:
                # First load
                self._cached_plan = self._version_plan_loader.load()
            return self._cached_plan
        except (
            VersionPlanNotFoundError,
            VersionPlanParseError,
            VersionPlanValidationError,
        ) as e:
            errors.append(ComponentFailureInfo(
                component="VersionPlanLoader",
                message=str(e),
                timestamp=now,
            ))
            return self._cached_plan  # Use stale cache

    # -------------------------------------------------------------------------
    # Private: Worktree Collection
    # -------------------------------------------------------------------------

    def _collect_worktrees(
        self,
        now: datetime,
        errors: list[ComponentFailureInfo],
    ) -> list[WorktreeInfo]:
        """Discover worktrees with error handling.

        Args:
            now: Current timestamp for error records.
            errors: List to append errors to.

        Returns:
            List of WorktreeInfo, empty list on failure.
        """
        try:
            worktrees = self._worktree_discovery.list_worktrees()
            if not self._include_main_worktree:
                worktrees = [wt for wt in worktrees if not wt.is_main]
            return worktrees
        except GitWorktreeError as e:
            errors.append(ComponentFailureInfo(
                component="WorktreeDiscovery",
                message=str(e),
                timestamp=now,
            ))
            return []

    def _enrich_worktree(
        self,
        worktree: WorktreeInfo,
        plan: VersionPlan | None,
        now: datetime,
    ) -> EnrichedWorktree:
        """Enrich a single worktree with config and GitHub data.

        Args:
            worktree: Base WorktreeInfo from discovery.
            plan: VersionPlan for branch matching (can be None).
            now: Current timestamp for rate limiting.

        Returns:
            EnrichedWorktree with all available enrichments.
            GitHub failures result in None fields, not exceptions.
        """
        enriched = EnrichedWorktree.from_worktree_info(worktree)

        # Match to workstream
        if plan:
            phase, workstream = self._match_workstream(worktree.branch, plan)
            if workstream:
                enriched.track_name = workstream.name
                enriched.track_color = workstream.color
                enriched.epic_number = workstream.epic

        # GitHub enrichment
        if self._should_fetch_github(worktree, now):
            pr, ci, coderabbit = self._fetch_github_data(worktree.branch, now)
            enriched.pr = pr
            enriched.ci_checks = ci
            enriched.coderabbit = coderabbit

        return enriched

    def _should_fetch_github(self, worktree: WorktreeInfo, now: datetime) -> bool:
        """Check if we should fetch GitHub data for this worktree.

        Args:
            worktree: WorktreeInfo to check.
            now: Current timestamp for rate limit check.

        Returns:
            True if GitHub data should be fetched.
        """
        if not self._github_enrichment_enabled:
            return False
        if worktree.is_main:
            return False
        if self._rate_limited_until and now < self._rate_limited_until:
            return False
        return True

    def _match_workstream(
        self,
        branch: str,
        plan: VersionPlan,
    ) -> tuple[PhaseConfig | None, WorkstreamConfig | None]:
        """Match branch to phase and workstream.

        Args:
            branch: Git branch name.
            plan: VersionPlan with workstream definitions.

        Returns:
            Tuple of (PhaseConfig, WorkstreamConfig) if found, (None, None) otherwise.
        """
        result = self._version_plan_loader.get_workstream_for_branch(branch)
        return result if result else (None, None)

    def _fetch_github_data(
        self,
        branch: str,
        now: datetime,
    ) -> tuple[PRInfo | None, CIChecks | None, CodeRabbitStatus | None]:
        """Fetch GitHub data for a branch.

        Errors are logged but not raised (graceful degradation).

        Args:
            branch: Git branch name.
            now: Current timestamp for rate limiting.

        Returns:
            Tuple of (pr_info, ci_checks, coderabbit_status).
            Any or all can be None on error.
        """
        pr_info = None
        ci_checks = None
        coderabbit = None

        try:
            pr_info = self._github_adapter.get_pr_state(branch)
            if pr_info:
                ci_checks = self._github_adapter.get_ci_status(pr_info.number)
                cr_str = self._github_adapter.get_coderabbit_status(pr_info.number)
                if cr_str:
                    try:
                        coderabbit = CodeRabbitStatus(
                            status=CodeRabbitReviewStatus(cr_str)
                        )
                    except ValueError:
                        # Unknown status string, log and continue
                        logger.warning(f"Unknown CodeRabbit status '{cr_str}' for PR - please update enum")
        except RateLimitError as e:
            logger.warning(f"GitHub rate limit hit: {e}")
            self._rate_limited_until = now + timedelta(
                minutes=self.RATE_LIMIT_COOLDOWN_MINUTES
            )
        except GitHubAPIError as e:
            logger.debug(f"GitHub API error for {branch}: {e}")

        return pr_info, ci_checks, coderabbit

    def _enrich_worktrees_parallel(
        self,
        worktrees_raw: list[WorktreeInfo],
        plan: VersionPlan | None,
        now: datetime,
    ) -> list[EnrichedWorktree]:
        """Enrich worktrees in parallel using thread pool.

        Uses ThreadPoolExecutor for parallel GitHub API calls.
        Falls back to sequential processing on any error.

        Args:
            worktrees_raw: List of discovered worktrees.
            plan: VersionPlan for workstream matching.
            now: Current timestamp.

        Returns:
            List of EnrichedWorktree in same order as input.
        """
        if not worktrees_raw:
            return []

        # If GitHub enrichment disabled, just do sequential (fast)
        if not self._github_enrichment_enabled:
            return [self._enrich_worktree(wt, plan, now) for wt in worktrees_raw]

        # Use thread pool for parallel enrichment
        results: dict[int, EnrichedWorktree] = {}

        try:
            with ThreadPoolExecutor(max_workers=self.MAX_GITHUB_WORKERS) as executor:
                # Submit all tasks with their index to preserve order
                future_to_idx = {
                    executor.submit(self._enrich_worktree, wt, plan, now): idx
                    for idx, wt in enumerate(worktrees_raw)
                }

                # Collect results as they complete
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        results[idx] = future.result()
                    except Exception as e:
                        # On error, create a basic enriched worktree without GitHub data
                        logger.warning(f"Enrichment failed for worktree {idx}: {e}")
                        results[idx] = EnrichedWorktree.from_worktree_info(worktrees_raw[idx])
        except Exception as e:
            # Fallback to sequential on thread pool error
            logger.warning(f"Parallel enrichment failed, falling back to sequential: {e}")
            return [self._enrich_worktree(wt, plan, now) for wt in worktrees_raw]

        # Return in original order
        return [results[i] for i in range(len(worktrees_raw))]

    # -------------------------------------------------------------------------
    # Private: Heartbeat Collection
    # -------------------------------------------------------------------------

    def _collect_heartbeat(
        self,
        now: datetime,
        errors: list[ComponentFailureInfo],
    ) -> HeartbeatStatus | None:
        """Collect heartbeat status.

        Args:
            now: Current timestamp.
            errors: List to append errors to.

        Returns:
            HeartbeatStatus if available, None if not configured or parse error.
        """
        if self._heartbeat_monitor is None:
            return None

        try:
            return self._heartbeat_monitor.get_status(now=now)
        except HeartbeatFileNotFoundError:
            # No file = disconnected (not an error)
            return HeartbeatStatus(
                state=HeartbeatState.DISCONNECTED,
                last_update=now,
                seconds_since_update=-1.0,  # Sentinel: -1 means "never updated" (JSON-safe)
                active_orchestrators=[],
                requests=[],
            )
        except HeartbeatParseError as e:
            errors.append(ComponentFailureInfo(
                component="HeartbeatMonitor",
                message=str(e),
                timestamp=now,
            ))
            return None

    # -------------------------------------------------------------------------
    # Private: Track Summaries
    # -------------------------------------------------------------------------

    def _build_track_summaries(
        self,
        plan: VersionPlan,
        worktrees: list[EnrichedWorktree],
    ) -> list[TrackSummary]:
        """Build track summaries from plan and worktrees.

        Aggregates worktree counts and issue counts per workstream.

        Args:
            plan: VersionPlan with workstream definitions.
            worktrees: Enriched worktrees to aggregate.

        Returns:
            List of TrackSummary, one per workstream.
        """
        summaries: list[TrackSummary] = []

        for phase in plan.phases:
            for ws in phase.workstreams:
                # Count worktrees for this workstream
                wt_count = sum(
                    1 for wt in worktrees
                    if wt.track_name == ws.name
                )

                # Aggregate issue counts
                open_issues = 0
                closed_issues = 0
                for wt in worktrees:
                    if wt.track_name == ws.name and wt.epic_issues:
                        open_issues += wt.epic_issues.open
                        closed_issues += wt.epic_issues.closed

                summaries.append(TrackSummary(
                    name=ws.name,
                    epic=ws.epic,
                    color=ws.color or "#888888",
                    worktree_count=wt_count,
                    issues_open=open_issues,
                    issues_closed=closed_issues,
                    status=ws.status,
                ))

        return summaries

    # -------------------------------------------------------------------------
    # Private: Archive Collection
    # -------------------------------------------------------------------------

    def _collect_archived_versions(
        self,
        now: datetime,
        errors: list[ComponentFailureInfo],
    ) -> list[ArchivedWorktree]:
        """Collect archived version data.

        Args:
            now: Current timestamp.
            errors: List to append errors to.

        Returns:
            List of ArchivedWorktree from archive manager.
        """
        if self._archive_manager is None:
            return []

        archived: list[ArchivedWorktree] = []
        try:
            summaries = self._archive_manager.list_versions()
            for summary in summaries:
                try:
                    version_archive = self._archive_manager.get_version(summary.version)
                    if version_archive and version_archive.worktrees:
                        # Convert each worktree dict to ArchivedWorktree
                        for wt_dict in version_archive.worktrees:
                            try:
                                archived_wt = self._dict_to_archived_worktree(
                                    wt_dict,
                                    version_archive.archived_at,
                                    version_archive.reason,
                                    version_archive.version,
                                )
                                archived.append(archived_wt)
                            except (KeyError, ValueError) as e:
                                # Skip malformed worktree data
                                logger.warning(
                                    f"Skipping malformed worktree in {summary.version}: {e}"
                                )
                except ArchiveCorruptedError as e:
                    # Log but continue with other versions
                    logger.warning(f"Skipping corrupted archive {summary.version}: {e}")
        except ArchiveCorruptedError as e:
            errors.append(ComponentFailureInfo(
                component="ArchiveManager",
                message=str(e),
                timestamp=now,
            ))

        return archived

    def _dict_to_archived_worktree(
        self,
        wt_dict: dict[str, Any],
        archived_at: datetime,
        reason: str,
        version: str,
    ) -> ArchivedWorktree:
        """Convert a serialized worktree dict to ArchivedWorktree.

        Args:
            wt_dict: Serialized worktree data from archive.
            archived_at: When the version was archived.
            reason: Reason for archiving.
            version: Version name (e.g., "v0.10").

        Returns:
            ArchivedWorktree instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        # Parse last_commit_date if present
        last_commit_date = None
        if wt_dict.get("last_commit_date"):
            last_commit_date = datetime.fromisoformat(wt_dict["last_commit_date"])

        # Reconstruct WorktreeInfo
        worktree_info = WorktreeInfo(
            path=wt_dict["path"],
            branch=wt_dict["branch"],
            commit_hash=wt_dict["commit_hash"],
            commit_short=wt_dict["commit_short"],
            is_main=wt_dict.get("is_main", False),
            status=WorktreeStatus(wt_dict.get("status", "unknown")),
            files_changed=wt_dict.get("files_changed", 0),
            files_staged=wt_dict.get("files_staged", 0),
            last_commit_msg=wt_dict.get("last_commit_msg", ""),
            last_commit_date=last_commit_date,
        )

        # Create EnrichedWorktree
        enriched = EnrichedWorktree.from_worktree_info(worktree_info)
        enriched.track_name = wt_dict.get("track_name")
        enriched.track_color = wt_dict.get("track_color")
        enriched.epic_number = wt_dict.get("epic_number")

        # Map reason string to ArchiveReason enum
        try:
            archive_reason = ArchiveReason(reason) if reason else ArchiveReason.MANUAL
        except ValueError:
            archive_reason = ArchiveReason.MANUAL

        return ArchivedWorktree(
            id=str(uuid.uuid4()),
            worktree=enriched,
            archived_at=archived_at,
            reason=archive_reason,
            version=version,
        )

    # -------------------------------------------------------------------------
    # Private: Serialization
    # -------------------------------------------------------------------------

    def _serialize_output(self, output: MonitorOutput) -> dict[str, Any]:
        """Serialize MonitorOutput to dictionary for JSON.

        Handles special serialization for EnrichedWorktree which has
        a custom to_dict() method.

        Args:
            output: MonitorOutput to serialize.

        Returns:
            Dictionary ready for JSON serialization.
        """
        return {
            "timestamp": output.timestamp.isoformat(),
            "config_version": output.config_version,
            "milestone": output.milestone,
            "worktree_count": output.worktree_count,
            "worktrees": [wt.to_dict() for wt in output.worktrees],
            "tracks": [t.to_dict() for t in output.tracks],
            "archived": [a.to_dict() for a in output.archived],
            "heartbeat": output.heartbeat.to_dict() if output.heartbeat else None,
            "anomalies": [a.to_dict() for a in output.anomalies],
            "errors": [e.to_dict() for e in output.errors],
        }

    # -------------------------------------------------------------------------
    # Private: File I/O
    # -------------------------------------------------------------------------

    def _atomic_write_json(self, path: Path, data: dict[str, Any]) -> None:
        """Write JSON atomically using temp file + rename.

        Creates parent directories as needed.

        Args:
            path: Target file path.
            data: Dictionary to serialize.

        Raises:
            MonitorWriteError: On write failure.
        """
        dir_path = path.parent
        try:
            fd, temp_path = tempfile.mkstemp(
                suffix=".tmp",
                prefix=path.stem + "_",
                dir=dir_path,
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, default=str)
                os.replace(temp_path, path)
            except (OSError, TypeError, ValueError):
                try:
                    os.unlink(temp_path)
                except FileNotFoundError:
                    pass  # Already cleaned up or never created
                raise
        except PermissionError as e:
            raise MonitorWriteError(str(path), f"Permission denied: {e}") from e
        except OSError as e:
            raise MonitorWriteError(str(path), f"IO error: {e}") from e
