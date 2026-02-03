"""
Worktree Monitor v2.0 - Heartbeat Monitor

Monitors orchestrator heartbeat files to track session staleness
and parse orchestrator requests.

Created: Phase 4 Day 1

CRITICAL IMPLEMENTATION NOTE:
When reading heartbeat status, we MUST read file content BEFORE
checking mtime to avoid race conditions where the file is updated
between reading mtime and reading content.
"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .constants import (
    HEARTBEAT_THRESHOLDS,
    HeartbeatState,
    HeartbeatThresholds,
    RequestType,
)
from .exceptions import HeartbeatFileNotFoundError, HeartbeatParseError
from .models import HeartbeatStatus, OrchestratorRequest, OrchestratorStatus

logger = logging.getLogger(__name__)


class HeartbeatMonitor:
    """Monitor for tracking orchestrator heartbeat status.

    The heartbeat file is a JSON file that orchestrators update periodically.
    This monitor tracks the file's modification time to determine staleness
    and parses orchestrator requests from the file content.

    Attributes:
        heartbeat_path: Path to the heartbeat JSON file.
        thresholds: HeartbeatThresholds for state determination.
    """

    def __init__(
        self,
        heartbeat_path: Path,
        thresholds: HeartbeatThresholds | None = None,
    ) -> None:
        """Initialize the heartbeat monitor.

        Args:
            heartbeat_path: Path to the heartbeat JSON file.
            thresholds: Optional custom thresholds for state determination.
                       If None, uses default HEARTBEAT_THRESHOLDS.
        """
        self.heartbeat_path = heartbeat_path
        self.thresholds = thresholds if thresholds is not None else HEARTBEAT_THRESHOLDS

    def get_status(self, now: datetime | None = None) -> HeartbeatStatus:
        """Get the current heartbeat status.

        CRITICAL: Reads file content BEFORE checking mtime to avoid race conditions.

        Args:
            now: Current timestamp for staleness calculation.
                 If None, uses current UTC time.

        Returns:
            HeartbeatStatus with state, timestamps, and orchestrator data.

        Raises:
            HeartbeatFileNotFoundError: If heartbeat file doesn't exist.
            HeartbeatParseError: If heartbeat file cannot be parsed.
        """
        if now is None:
            now = datetime.now(UTC)

        # CRITICAL: Read content BEFORE mtime to avoid race condition
        content = self._read_content()
        mtime = self._get_mtime()

        # Calculate staleness
        last_update = datetime.fromtimestamp(mtime, tz=UTC)
        seconds_since_update = (now - last_update).total_seconds()
        state = self.thresholds.get_state(seconds_since_update)

        # Parse orchestrator data from content
        active_orchestrators = self._parse_orchestrators(content)
        requests = self._parse_requests_from_content(content)

        return HeartbeatStatus(
            state=state,
            last_update=last_update,
            seconds_since_update=seconds_since_update,
            active_orchestrators=active_orchestrators,
            requests=requests,
        )

    def get_state(self, now: datetime | None = None) -> HeartbeatState:
        """Get just the heartbeat state (FRESH/WARNING/STALE/DISCONNECTED).

        Args:
            now: Current timestamp for staleness calculation.
                 If None, uses current UTC time.

        Returns:
            HeartbeatState enum value.

        Raises:
            HeartbeatFileNotFoundError: If heartbeat file doesn't exist.
        """
        if now is None:
            now = datetime.now(UTC)

        seconds = self.get_seconds_since_update(now=now)
        return self.thresholds.get_state(seconds)

    def get_seconds_since_update(self, now: datetime | None = None) -> float:
        """Get seconds since the last heartbeat update.

        Args:
            now: Current timestamp for calculation.
                 If None, uses current UTC time.

        Returns:
            Number of seconds since last file modification.

        Raises:
            HeartbeatFileNotFoundError: If heartbeat file doesn't exist.
        """
        if now is None:
            now = datetime.now(UTC)

        mtime = self._get_mtime()
        last_update = datetime.fromtimestamp(mtime, tz=UTC)
        return (now - last_update).total_seconds()

    def parse_orchestrator_requests(self) -> list[OrchestratorRequest]:
        """Parse orchestrator requests from the heartbeat file.

        Returns:
            List of OrchestratorRequest objects for orchestrators
            that have a valid request type set.

        Raises:
            HeartbeatFileNotFoundError: If heartbeat file doesn't exist.
            HeartbeatParseError: If heartbeat file cannot be parsed.
        """
        content = self._read_content()
        return self._parse_requests_from_content(content)

    def _read_content(self) -> dict[str, Any]:
        """Read and parse heartbeat file content.

        Returns:
            Parsed JSON content as dictionary.

        Raises:
            HeartbeatFileNotFoundError: If file doesn't exist.
            HeartbeatParseError: If JSON parsing fails.
        """
        try:
            text = self.heartbeat_path.read_text(encoding='utf-8')
        except FileNotFoundError as e:
            raise HeartbeatFileNotFoundError(str(self.heartbeat_path)) from e

        try:
            if not text.strip():
                raise HeartbeatParseError(
                    str(self.heartbeat_path),
                    'File is empty',
                )
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise HeartbeatParseError(
                str(self.heartbeat_path),
                f'Invalid JSON: {e}',
            ) from e

    def _get_mtime(self) -> float:
        """Get the file modification time.

        Returns:
            File modification time as Unix timestamp.

        Raises:
            HeartbeatFileNotFoundError: If file doesn't exist.
        """
        try:
            return self.heartbeat_path.stat().st_mtime
        except FileNotFoundError as e:
            raise HeartbeatFileNotFoundError(str(self.heartbeat_path)) from e

    def _iter_orchestrator_entries(self, content: dict[str, Any]) -> list[dict[str, Any]]:
        """Get valid orchestrator entries from content.

        Args:
            content: Parsed heartbeat file content.

        Returns:
            List of valid orchestrator entry dictionaries.
        """
        orchestrators_data = content.get('orchestrators', [])
        if not isinstance(orchestrators_data, list):
            return []
        return [entry for entry in orchestrators_data if isinstance(entry, dict)]

    def _parse_request_type(self, value: str | None, branch: str) -> RequestType | None:
        """Parse a request type string into RequestType enum.

        Args:
            value: Raw request type string from heartbeat data.
            branch: Branch name for logging context.

        Returns:
            RequestType if valid, None otherwise.
        """
        if not value:
            return None
        try:
            return RequestType(value)
        except ValueError as e:
            logger.debug(
                'Invalid RequestType value %r for branch %r: %s',
                value,
                branch,
                e,
            )
            return None

    def _parse_orchestrators(self, content: dict[str, Any]) -> list[OrchestratorStatus]:
        """Parse orchestrator statuses from content.

        Args:
            content: Parsed heartbeat file content.

        Returns:
            List of OrchestratorStatus objects.
        """
        result: list[OrchestratorStatus] = []
        for entry in self._iter_orchestrator_entries(content):
            branch = entry.get('branch', '')
            status_str = entry.get('status', '')
            request_type = self._parse_request_type(entry.get('request'), branch)

            result.append(
                OrchestratorStatus(
                    branch=branch,
                    status=status_str,
                    request=request_type,
                    last_update=None,
                )
            )

        return result

    def _parse_requests_from_content(self, content: dict[str, Any]) -> list[OrchestratorRequest]:
        """Parse orchestrator requests from content.

        Only returns requests for orchestrators that have a valid request type.

        Args:
            content: Parsed heartbeat file content.

        Returns:
            List of OrchestratorRequest objects.
        """
        result: list[OrchestratorRequest] = []
        for entry in self._iter_orchestrator_entries(content):
            branch = entry.get('branch', '')
            request_type = self._parse_request_type(entry.get('request'), branch)
            if request_type is None:
                continue

            result.append(
                OrchestratorRequest(
                    branch=branch,
                    request_type=request_type,
                    message=entry.get('message', ''),
                    timestamp=None,
                )
            )

        return result
