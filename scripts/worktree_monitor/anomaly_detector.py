"""
Worktree Monitor v2.0 - Anomaly Detector

Extracted from WorktreeMonitor for Single Responsibility Principle.

Created: Phase 4 Day 5 (Review Fixes)
"""

from .constants import (
    AnomalySeverity,
    AnomalyType,
    HeartbeatState,
    WorktreeStatus,
)
from .models import (
    Anomaly,
    EnrichedWorktree,
    HeartbeatStatus,
)


class AnomalyDetector:
    """Detects anomalies across worktrees and heartbeat."""

    def detect(
        self,
        worktrees: list[EnrichedWorktree],
        heartbeat: HeartbeatStatus | None,
    ) -> list[Anomaly]:
        """Detect all anomalies."""
        anomalies: list[Anomaly] = []
        anomalies.extend(self._detect_worktree_anomalies(worktrees))
        anomalies.extend(self._detect_heartbeat_anomalies(heartbeat))
        return anomalies

    def _detect_worktree_anomalies(self, worktrees: list[EnrichedWorktree]) -> list[Anomaly]:
        """Detect anomalies in worktrees."""
        anomalies: list[Anomaly] = []

        for wt in worktrees:
            # CI failures
            if wt.ci_checks and wt.ci_checks.has_failures:
                anomalies.append(
                    Anomaly(
                        type=AnomalyType.CI_FAILURE,
                        severity=AnomalySeverity.HIGH,
                        message=f'CI check failed ({wt.ci_checks.failed} failures)',
                        worktree_path=wt.path,
                        branch=wt.branch,
                    )
                )

            # CodeRabbit changes requested
            if wt.coderabbit and wt.coderabbit.has_changes_requested:
                anomalies.append(
                    Anomaly(
                        type=AnomalyType.CHANGES_REQUESTED,
                        severity=AnomalySeverity.MEDIUM,
                        message='CodeRabbit requested changes',
                        worktree_path=wt.path,
                        branch=wt.branch,
                    )
                )

            # Dirty worktree
            if wt.status == WorktreeStatus.DIRTY:
                anomalies.append(
                    Anomaly(
                        type=AnomalyType.DIRTY_WORKTREE,
                        severity=AnomalySeverity.LOW,
                        message=f'Uncommitted changes ({wt.files_changed} files)',
                        worktree_path=wt.path,
                        branch=wt.branch,
                    )
                )

        return anomalies

    def _detect_heartbeat_anomalies(self, heartbeat: HeartbeatStatus | None) -> list[Anomaly]:
        """Detect anomalies in heartbeat status."""
        if heartbeat is None:
            return []

        anomalies: list[Anomaly] = []

        if heartbeat.state == HeartbeatState.WARNING:
            anomalies.append(
                Anomaly(
                    type=AnomalyType.STALE_HEARTBEAT,
                    severity=AnomalySeverity.LOW,
                    message=f'Heartbeat warning ({int(heartbeat.seconds_since_update)}s)',
                )
            )
        elif heartbeat.state == HeartbeatState.STALE:
            anomalies.append(
                Anomaly(
                    type=AnomalyType.STALE_HEARTBEAT,
                    severity=AnomalySeverity.MEDIUM,
                    message=f'Heartbeat stale ({int(heartbeat.seconds_since_update)}s)',
                )
            )
        elif heartbeat.state == HeartbeatState.DISCONNECTED:
            anomalies.append(
                Anomaly(
                    type=AnomalyType.DISCONNECTED_ORCHESTRATOR,
                    severity=AnomalySeverity.HIGH,
                    message='No active orchestrator',
                )
            )

        return anomalies

    def attach_to_worktrees(
        self,
        worktrees: list[EnrichedWorktree],
        anomalies: list[Anomaly],
    ) -> None:
        """Attach relevant anomalies to their worktrees."""
        for anomaly in anomalies:
            if anomaly.worktree_path:
                for wt in worktrees:
                    if wt.path == anomaly.worktree_path:
                        wt.anomalies.append(anomaly)
                        break
