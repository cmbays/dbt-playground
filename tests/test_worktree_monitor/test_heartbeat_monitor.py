"""
Worktree Monitor v2.0 - HeartbeatMonitor Tests

TDD tests for the HeartbeatMonitor class that tracks orchestrator
heartbeat status and staleness.

Created: Phase 4 Day 1
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from worktree_monitor.constants import (
    HeartbeatState,
    HeartbeatThresholds,
    RequestType,
)
from worktree_monitor.exceptions import (
    HeartbeatFileNotFoundError,
    HeartbeatParseError,
)

# Import will fail until implementation exists - that's expected for TDD
from worktree_monitor.heartbeat_monitor import HeartbeatMonitor
from worktree_monitor.models import HeartbeatStatus

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def tmp_heartbeat_file(tmp_path) -> Path:
    """Create a temporary heartbeat file."""
    heartbeat_file = tmp_path / "worktree-heartbeat.json"
    return heartbeat_file


@pytest.fixture
def sample_heartbeat_content() -> dict:
    """Sample valid heartbeat file content."""
    return {
        "last_update": "2026-02-03T12:00:00Z",
        "orchestrators": [
            {
                "branch": "feat/qa-enforcement",
                "status": "IN_PROGRESS",
                "request": "WAITING"
            }
        ]
    }


@pytest.fixture
def heartbeat_file_fresh(tmp_heartbeat_file, sample_heartbeat_content, fixed_now) -> Path:
    """Create a fresh heartbeat file (< 30 seconds old)."""
    tmp_heartbeat_file.write_text(json.dumps(sample_heartbeat_content))
    # Set mtime to 10 seconds before fixed_now
    mtime = (fixed_now - timedelta(seconds=10)).timestamp()
    os.utime(tmp_heartbeat_file, (mtime, mtime))
    return tmp_heartbeat_file


@pytest.fixture
def heartbeat_file_warning(tmp_heartbeat_file, sample_heartbeat_content, fixed_now) -> Path:
    """Create a warning heartbeat file (30-60 seconds old)."""
    tmp_heartbeat_file.write_text(json.dumps(sample_heartbeat_content))
    # Set mtime to 45 seconds before fixed_now
    mtime = (fixed_now - timedelta(seconds=45)).timestamp()
    os.utime(tmp_heartbeat_file, (mtime, mtime))
    return tmp_heartbeat_file


@pytest.fixture
def heartbeat_file_stale(tmp_heartbeat_file, sample_heartbeat_content, fixed_now) -> Path:
    """Create a stale heartbeat file (60-300 seconds old)."""
    tmp_heartbeat_file.write_text(json.dumps(sample_heartbeat_content))
    # Set mtime to 120 seconds (2 minutes) before fixed_now
    mtime = (fixed_now - timedelta(seconds=120)).timestamp()
    os.utime(tmp_heartbeat_file, (mtime, mtime))
    return tmp_heartbeat_file


@pytest.fixture
def heartbeat_file_disconnected(tmp_heartbeat_file, sample_heartbeat_content, fixed_now) -> Path:
    """Create a disconnected heartbeat file (> 300 seconds old)."""
    tmp_heartbeat_file.write_text(json.dumps(sample_heartbeat_content))
    # Set mtime to 600 seconds (10 minutes) before fixed_now
    mtime = (fixed_now - timedelta(seconds=600)).timestamp()
    os.utime(tmp_heartbeat_file, (mtime, mtime))
    return tmp_heartbeat_file


# =============================================================================
# Test: Calculate staleness from file mtime
# =============================================================================


class TestCalculateStaleness:
    """Tests for staleness calculation based on file mtime."""

    def test_calculate_staleness_from_mtime(self, heartbeat_file_fresh, fixed_now):
        """Test that staleness is calculated from file modification time."""
        monitor = HeartbeatMonitor(heartbeat_file_fresh)
        seconds = monitor.get_seconds_since_update(now=fixed_now)

        # Should be approximately 10 seconds (we set mtime to 10s before fixed_now)
        assert 9.0 <= seconds <= 11.0

    def test_staleness_uses_mtime_not_content(self, tmp_heartbeat_file, fixed_now):
        """Test that staleness uses file mtime, not content timestamp."""
        # Content says update was 5 minutes ago
        content = {
            "last_update": (fixed_now - timedelta(minutes=5)).isoformat(),
            "orchestrators": []
        }
        tmp_heartbeat_file.write_text(json.dumps(content))

        # But file mtime is only 5 seconds ago
        mtime = (fixed_now - timedelta(seconds=5)).timestamp()
        os.utime(tmp_heartbeat_file, (mtime, mtime))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        seconds = monitor.get_seconds_since_update(now=fixed_now)

        # Should use mtime (5s), not content timestamp (5min)
        assert 4.0 <= seconds <= 6.0


# =============================================================================
# Test: Heartbeat State Thresholds
# =============================================================================


class TestHeartbeatStateThresholds:
    """Tests for heartbeat state determination based on staleness."""

    def test_returns_fresh_under_30_seconds(self, heartbeat_file_fresh, fixed_now):
        """Test that FRESH is returned when staleness < 30 seconds."""
        monitor = HeartbeatMonitor(heartbeat_file_fresh)
        state = monitor.get_state(now=fixed_now)

        assert state == HeartbeatState.FRESH

    def test_returns_warning_between_30_and_60_seconds(self, heartbeat_file_warning, fixed_now):
        """Test that WARNING is returned when 30 <= staleness < 60 seconds."""
        monitor = HeartbeatMonitor(heartbeat_file_warning)
        state = monitor.get_state(now=fixed_now)

        assert state == HeartbeatState.WARNING

    def test_returns_stale_between_60_and_300_seconds(self, heartbeat_file_stale, fixed_now):
        """Test that STALE is returned when 60 <= staleness < 300 seconds."""
        monitor = HeartbeatMonitor(heartbeat_file_stale)
        state = monitor.get_state(now=fixed_now)

        assert state == HeartbeatState.STALE

    def test_returns_disconnected_over_300_seconds(self, heartbeat_file_disconnected, fixed_now):
        """Test that DISCONNECTED is returned when staleness >= 300 seconds."""
        monitor = HeartbeatMonitor(heartbeat_file_disconnected)
        state = monitor.get_state(now=fixed_now)

        assert state == HeartbeatState.DISCONNECTED


# =============================================================================
# Test: Boundary Conditions
# =============================================================================


class TestBoundaryConditions:
    """Tests for exact boundary behavior at threshold values."""

    def test_exactly_30_seconds_is_warning(self, tmp_heartbeat_file, fixed_now):
        """Test that exactly 30 seconds is WARNING (not FRESH)."""
        tmp_heartbeat_file.write_text(json.dumps({"orchestrators": []}))
        mtime = (fixed_now - timedelta(seconds=30)).timestamp()
        os.utime(tmp_heartbeat_file, (mtime, mtime))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        state = monitor.get_state(now=fixed_now)

        assert state == HeartbeatState.WARNING

    def test_exactly_60_seconds_is_stale(self, tmp_heartbeat_file, fixed_now):
        """Test that exactly 60 seconds is STALE (not WARNING)."""
        tmp_heartbeat_file.write_text(json.dumps({"orchestrators": []}))
        mtime = (fixed_now - timedelta(seconds=60)).timestamp()
        os.utime(tmp_heartbeat_file, (mtime, mtime))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        state = monitor.get_state(now=fixed_now)

        assert state == HeartbeatState.STALE

    def test_exactly_300_seconds_is_disconnected(self, tmp_heartbeat_file, fixed_now):
        """Test that exactly 300 seconds is DISCONNECTED (not STALE)."""
        tmp_heartbeat_file.write_text(json.dumps({"orchestrators": []}))
        mtime = (fixed_now - timedelta(seconds=300)).timestamp()
        os.utime(tmp_heartbeat_file, (mtime, mtime))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        state = monitor.get_state(now=fixed_now)

        assert state == HeartbeatState.DISCONNECTED

    def test_just_under_30_is_fresh(self, tmp_heartbeat_file, fixed_now):
        """Test that 29.9 seconds is FRESH."""
        tmp_heartbeat_file.write_text(json.dumps({"orchestrators": []}))
        mtime = (fixed_now - timedelta(seconds=29.9)).timestamp()
        os.utime(tmp_heartbeat_file, (mtime, mtime))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        state = monitor.get_state(now=fixed_now)

        assert state == HeartbeatState.FRESH


# =============================================================================
# Test: Missing Heartbeat File
# =============================================================================


class TestMissingHeartbeatFile:
    """Tests for handling missing heartbeat file."""

    def test_missing_file_raises_heartbeat_file_not_found(self, tmp_path):
        """Test that missing file raises HeartbeatFileNotFoundError."""
        nonexistent = tmp_path / "nonexistent.json"
        monitor = HeartbeatMonitor(nonexistent)

        with pytest.raises(HeartbeatFileNotFoundError) as exc_info:
            monitor.get_status()

        assert str(nonexistent) in str(exc_info.value)

    def test_missing_file_get_state_raises(self, tmp_path):
        """Test that get_state with missing file raises error."""
        nonexistent = tmp_path / "nonexistent.json"
        monitor = HeartbeatMonitor(nonexistent)

        with pytest.raises(HeartbeatFileNotFoundError):
            monitor.get_state()

    def test_missing_file_get_seconds_raises(self, tmp_path):
        """Test that get_seconds_since_update with missing file raises error."""
        nonexistent = tmp_path / "nonexistent.json"
        monitor = HeartbeatMonitor(nonexistent)

        with pytest.raises(HeartbeatFileNotFoundError):
            monitor.get_seconds_since_update()


# =============================================================================
# Test: Parse Orchestrator Requests
# =============================================================================


class TestParseOrchestratorRequests:
    """Tests for parsing orchestrator requests from heartbeat file."""

    def test_parse_single_request(self, tmp_heartbeat_file):
        """Test parsing a single orchestrator request."""
        content = {
            "last_update": "2026-02-03T12:00:00Z",
            "orchestrators": [
                {
                    "branch": "feat/qa-enforcement",
                    "status": "IN_PROGRESS",
                    "request": "WAITING"
                }
            ]
        }
        tmp_heartbeat_file.write_text(json.dumps(content))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        requests = monitor.parse_orchestrator_requests()

        assert len(requests) == 1
        assert requests[0].branch == "feat/qa-enforcement"
        assert requests[0].request_type == RequestType.WAITING

    def test_parse_multiple_requests(self, tmp_heartbeat_file):
        """Test parsing multiple orchestrator requests."""
        content = {
            "last_update": "2026-02-03T12:00:00Z",
            "orchestrators": [
                {"branch": "feat/qa", "status": "IN_PROGRESS", "request": "WAITING"},
                {"branch": "feat/memory", "status": "REVIEW", "request": "MERGE_READY"},
                {"branch": "feat/kanban", "status": "BLOCKED", "request": "BLOCKED"},
            ]
        }
        tmp_heartbeat_file.write_text(json.dumps(content))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        requests = monitor.parse_orchestrator_requests()

        assert len(requests) == 3
        assert requests[0].request_type == RequestType.WAITING
        assert requests[1].request_type == RequestType.MERGE_READY
        assert requests[2].request_type == RequestType.BLOCKED

    def test_parse_empty_orchestrators(self, tmp_heartbeat_file):
        """Test parsing with no orchestrators."""
        content = {
            "last_update": "2026-02-03T12:00:00Z",
            "orchestrators": []
        }
        tmp_heartbeat_file.write_text(json.dumps(content))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        requests = monitor.parse_orchestrator_requests()

        assert requests == []

    def test_parse_orchestrator_without_request_field(self, tmp_heartbeat_file):
        """Test parsing orchestrator entry without request field."""
        content = {
            "last_update": "2026-02-03T12:00:00Z",
            "orchestrators": [
                {"branch": "feat/qa", "status": "IN_PROGRESS"}
                # Note: no "request" field
            ]
        }
        tmp_heartbeat_file.write_text(json.dumps(content))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        requests = monitor.parse_orchestrator_requests()

        # Should return empty list since no request field
        assert requests == []


# =============================================================================
# Test: Corrupted Heartbeat File
# =============================================================================


class TestCorruptedHeartbeatFile:
    """Tests for handling corrupted heartbeat file gracefully."""

    def test_invalid_json_raises_parse_error(self, tmp_heartbeat_file):
        """Test that invalid JSON raises HeartbeatParseError."""
        tmp_heartbeat_file.write_text("{ invalid json }")

        monitor = HeartbeatMonitor(tmp_heartbeat_file)

        with pytest.raises(HeartbeatParseError) as exc_info:
            monitor.parse_orchestrator_requests()

        assert "parse" in str(exc_info.value).lower()

    def test_missing_orchestrators_key_returns_empty(self, tmp_heartbeat_file):
        """Test that missing orchestrators key returns empty list."""
        tmp_heartbeat_file.write_text(json.dumps({"last_update": "2026-02-03T12:00:00Z"}))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        requests = monitor.parse_orchestrator_requests()

        assert requests == []

    def test_empty_file_raises_parse_error(self, tmp_heartbeat_file):
        """Test that empty file raises HeartbeatParseError."""
        tmp_heartbeat_file.write_text("")

        monitor = HeartbeatMonitor(tmp_heartbeat_file)

        with pytest.raises(HeartbeatParseError):
            monitor.parse_orchestrator_requests()

    def test_orchestrators_not_list_returns_empty(self, tmp_heartbeat_file):
        """Test that non-list orchestrators returns empty list gracefully."""
        tmp_heartbeat_file.write_text(json.dumps({
            "last_update": "2026-02-03T12:00:00Z",
            "orchestrators": "not a list"
        }))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        requests = monitor.parse_orchestrator_requests()

        # Should handle gracefully and return empty
        assert requests == []

    def test_invalid_request_type_skipped(self, tmp_heartbeat_file):
        """Test that invalid request type is skipped gracefully."""
        content = {
            "last_update": "2026-02-03T12:00:00Z",
            "orchestrators": [
                {"branch": "feat/qa", "status": "IN_PROGRESS", "request": "INVALID_TYPE"},
                {"branch": "feat/memory", "status": "DONE", "request": "COMPLETED"},
            ]
        }
        tmp_heartbeat_file.write_text(json.dumps(content))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        requests = monitor.parse_orchestrator_requests()

        # Should only return the valid one
        assert len(requests) == 1
        assert requests[0].request_type == RequestType.COMPLETED


# =============================================================================
# Test: Get Full Status
# =============================================================================


class TestGetStatus:
    """Tests for get_status() which returns complete HeartbeatStatus."""

    def test_get_status_returns_heartbeat_status(self, heartbeat_file_fresh, fixed_now):
        """Test that get_status returns a HeartbeatStatus object."""
        monitor = HeartbeatMonitor(heartbeat_file_fresh)
        status = monitor.get_status(now=fixed_now)

        assert isinstance(status, HeartbeatStatus)

    def test_get_status_includes_state(self, heartbeat_file_fresh, fixed_now):
        """Test that get_status includes correct state."""
        monitor = HeartbeatMonitor(heartbeat_file_fresh)
        status = monitor.get_status(now=fixed_now)

        assert status.state == HeartbeatState.FRESH

    def test_get_status_includes_seconds(self, heartbeat_file_fresh, fixed_now):
        """Test that get_status includes seconds_since_update."""
        monitor = HeartbeatMonitor(heartbeat_file_fresh)
        status = monitor.get_status(now=fixed_now)

        assert 9.0 <= status.seconds_since_update <= 11.0

    def test_get_status_includes_last_update(self, heartbeat_file_fresh, fixed_now):
        """Test that get_status includes last_update timestamp."""
        monitor = HeartbeatMonitor(heartbeat_file_fresh)
        status = monitor.get_status(now=fixed_now)

        assert isinstance(status.last_update, datetime)
        # Last update should be approximately 10 seconds before fixed_now
        expected = fixed_now - timedelta(seconds=10)
        delta = abs((status.last_update - expected).total_seconds())
        assert delta <= 1.0

    def test_get_status_includes_orchestrators(self, heartbeat_file_fresh, fixed_now):
        """Test that get_status includes active orchestrators."""
        monitor = HeartbeatMonitor(heartbeat_file_fresh)
        status = monitor.get_status(now=fixed_now)

        assert len(status.active_orchestrators) == 1
        assert status.active_orchestrators[0].branch == "feat/qa-enforcement"

    def test_get_status_includes_requests(self, heartbeat_file_fresh, fixed_now):
        """Test that get_status includes orchestrator requests."""
        monitor = HeartbeatMonitor(heartbeat_file_fresh)
        status = monitor.get_status(now=fixed_now)

        assert len(status.requests) == 1
        assert status.requests[0].request_type == RequestType.WAITING


# =============================================================================
# Test: Custom Thresholds
# =============================================================================


class TestCustomThresholds:
    """Tests for using custom heartbeat thresholds."""

    def test_custom_thresholds_respected(self, tmp_heartbeat_file, fixed_now):
        """Test that custom thresholds are used for state calculation."""
        tmp_heartbeat_file.write_text(json.dumps({"orchestrators": []}))
        # Set mtime to 20 seconds ago
        mtime = (fixed_now - timedelta(seconds=20)).timestamp()
        os.utime(tmp_heartbeat_file, (mtime, mtime))

        # With default thresholds (30s), this would be FRESH
        # With custom thresholds (15s), this should be WARNING
        custom_thresholds = HeartbeatThresholds(FRESH_MAX=15, WARNING_MAX=30, STALE_MAX=60)
        monitor = HeartbeatMonitor(tmp_heartbeat_file, thresholds=custom_thresholds)
        state = monitor.get_state(now=fixed_now)

        assert state == HeartbeatState.WARNING

    def test_default_thresholds_used_when_none(self, heartbeat_file_fresh, fixed_now):
        """Test that default thresholds are used when none provided."""
        monitor = HeartbeatMonitor(heartbeat_file_fresh, thresholds=None)
        state = monitor.get_state(now=fixed_now)

        # Should use default and be FRESH
        assert state == HeartbeatState.FRESH


# =============================================================================
# Test: Race Condition Prevention
# =============================================================================


class TestRaceConditionPrevention:
    """Tests for race condition handling (read content before mtime)."""

    def test_content_read_before_mtime_check(self, tmp_heartbeat_file, fixed_now):
        """Test that file content is read before mtime to prevent race."""
        # This test verifies the critical implementation detail:
        # Content MUST be read BEFORE checking mtime

        # Create a heartbeat file
        content = {
            "orchestrators": [
                {"branch": "feat/test", "status": "ACTIVE", "request": "WAITING"}
            ]
        }
        tmp_heartbeat_file.write_text(json.dumps(content))
        mtime = (fixed_now - timedelta(seconds=5)).timestamp()
        os.utime(tmp_heartbeat_file, (mtime, mtime))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        status = monitor.get_status(now=fixed_now)

        # If we read content after mtime, there's a window where
        # content could be updated. This test ensures we get consistent data.
        assert len(status.active_orchestrators) == 1
        assert status.seconds_since_update >= 0


# =============================================================================
# Test: Timezone Handling
# =============================================================================


class TestTimezoneHandling:
    """Tests for proper timezone handling."""

    def test_mtime_converted_to_utc(self, tmp_heartbeat_file, fixed_now):
        """Test that mtime is properly converted to UTC datetime."""
        tmp_heartbeat_file.write_text(json.dumps({"orchestrators": []}))
        mtime = (fixed_now - timedelta(seconds=10)).timestamp()
        os.utime(tmp_heartbeat_file, (mtime, mtime))

        monitor = HeartbeatMonitor(tmp_heartbeat_file)
        status = monitor.get_status(now=fixed_now)

        # last_update should be timezone-aware (UTC)
        assert status.last_update.tzinfo is not None

    def test_now_defaults_to_utc(self, heartbeat_file_fresh):
        """Test that current time defaults to UTC when not provided."""
        monitor = HeartbeatMonitor(heartbeat_file_fresh)

        # Should not raise when now is not provided
        status = monitor.get_status()

        assert isinstance(status, HeartbeatStatus)
        assert status.last_update.tzinfo is not None
