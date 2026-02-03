"""
Worktree Monitor v2.0 - GitHubAdapter Tests

TDD tests for the GitHubAdapter class that handles GitHub API
interactions via the gh CLI with caching support.

Test IDs: GH-01 through GH-14

Created: Phase 4 Day 3
"""

import json
import time
from datetime import datetime, timezone
from subprocess import CompletedProcess
from unittest.mock import patch, MagicMock

import pytest

from worktree_monitor.github_adapter import GitHubAdapter
from worktree_monitor.constants import PRState as PRStateEnum
from worktree_monitor.models import PRInfo, CIChecks
from worktree_monitor.exceptions import GitHubAPIError, RateLimitError


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def adapter():
    """Create a GitHubAdapter instance for testing."""
    return GitHubAdapter(repo="owner/repo", cache_ttl=60)


@pytest.fixture
def mock_pr_response_open():
    """Mock gh API response for an open PR."""
    return [
        {
            "number": 184,
            "state": "open",
            "title": "feat(qa): implement QA enforcement",
            "url": "https://github.com/owner/repo/pull/184",
            "headRefName": "feat/qa-enforcement",
            "isDraft": False,
            "createdAt": "2026-02-01T10:00:00Z",
            "updatedAt": "2026-02-03T08:00:00Z",
            "merged": False,
        }
    ]


@pytest.fixture
def mock_pr_response_merged():
    """Mock gh API response for a merged PR."""
    return [
        {
            "number": 182,
            "state": "closed",
            "title": "feat(kanban): add workflow engine",
            "url": "https://github.com/owner/repo/pull/182",
            "headRefName": "feat/kanban-phase1",
            "isDraft": False,
            "createdAt": "2026-02-01T08:00:00Z",
            "updatedAt": "2026-02-03T04:00:00Z",
            "merged": True,
            "mergedAt": "2026-02-03T04:00:00Z",
        }
    ]


@pytest.fixture
def mock_pr_response_closed():
    """Mock gh API response for a closed (not merged) PR."""
    return [
        {
            "number": 180,
            "state": "closed",
            "title": "feat(abandoned): some feature",
            "url": "https://github.com/owner/repo/pull/180",
            "headRefName": "feat/abandoned",
            "isDraft": False,
            "createdAt": "2026-01-20T10:00:00Z",
            "updatedAt": "2026-01-25T12:00:00Z",
            "merged": False,
        }
    ]


@pytest.fixture
def mock_ci_all_passing():
    """Mock gh API response for CI checks all passing."""
    return {
        "checkRuns": [
            {"name": "lint", "status": "COMPLETED", "conclusion": "SUCCESS"},
            {"name": "test", "status": "COMPLETED", "conclusion": "SUCCESS"},
            {"name": "build", "status": "COMPLETED", "conclusion": "SUCCESS"},
        ]
    }


@pytest.fixture
def mock_ci_some_failing():
    """Mock gh API response for CI checks with failures."""
    return {
        "checkRuns": [
            {"name": "lint", "status": "COMPLETED", "conclusion": "SUCCESS"},
            {"name": "test", "status": "COMPLETED", "conclusion": "FAILURE"},
            {"name": "build", "status": "COMPLETED", "conclusion": "SUCCESS"},
        ]
    }


@pytest.fixture
def mock_ci_pending():
    """Mock gh API response for CI checks with pending."""
    return {
        "checkRuns": [
            {"name": "lint", "status": "COMPLETED", "conclusion": "SUCCESS"},
            {"name": "test", "status": "IN_PROGRESS", "conclusion": None},
            {"name": "build", "status": "QUEUED", "conclusion": None},
        ]
    }


@pytest.fixture
def mock_reviews_approved():
    """Mock gh API response for reviews with CodeRabbit approved."""
    return [
        {
            "author": {"login": "coderabbitai"},
            "state": "APPROVED",
            "submittedAt": "2026-02-03T10:00:00Z",
        }
    ]


@pytest.fixture
def mock_reviews_changes_requested():
    """Mock gh API response for reviews with CodeRabbit requesting changes."""
    return [
        {
            "author": {"login": "coderabbitai"},
            "state": "CHANGES_REQUESTED",
            "submittedAt": "2026-02-03T10:00:00Z",
        }
    ]


@pytest.fixture
def mock_reviews_no_coderabbit():
    """Mock gh API response for reviews without CodeRabbit."""
    return [
        {
            "author": {"login": "human-reviewer"},
            "state": "APPROVED",
            "submittedAt": "2026-02-03T10:00:00Z",
        }
    ]


# =============================================================================
# GH-01: Fetch PR for branch
# =============================================================================


class TestFetchPRForBranch:
    """GH-01: Test fetching PR for a branch."""

    def test_fetch_pr_returns_pr_info(self, adapter, mock_pr_response_open):
        """Test that fetching PR returns PRInfo object."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_pr_response_open),
                stderr="",
            )

            result = adapter.get_pr_state("feat/qa-enforcement")

            assert result is not None
            assert isinstance(result, PRInfo)
            assert result.number == 184
            assert result.title == "feat(qa): implement QA enforcement"


# =============================================================================
# GH-02: Handle branch with no PR
# =============================================================================


class TestBranchNoPR:
    """GH-02: Test handling branch with no associated PR."""

    def test_no_pr_returns_none(self, adapter):
        """Test that branch with no PR returns None."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout="[]",  # Empty array = no PRs
                stderr="",
            )

            result = adapter.get_pr_state("feat/no-pr-branch")

            assert result is None


# =============================================================================
# GH-03: Parse PR state open
# =============================================================================


class TestParsePRStateOpen:
    """GH-03: Test parsing open PR state."""

    def test_open_pr_state(self, adapter, mock_pr_response_open):
        """Test that open PR is parsed correctly."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_pr_response_open),
                stderr="",
            )

            result = adapter.get_pr_state("feat/qa-enforcement")

            assert result.state == PRStateEnum.OPEN


# =============================================================================
# GH-04: Parse PR state merged
# =============================================================================


class TestParsePRStateMerged:
    """GH-04: Test parsing merged PR state."""

    def test_merged_pr_state(self, adapter, mock_pr_response_merged):
        """Test that merged PR is parsed correctly."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_pr_response_merged),
                stderr="",
            )

            result = adapter.get_pr_state("feat/kanban-phase1")

            assert result.state == PRStateEnum.MERGED


# =============================================================================
# GH-05: Parse PR state closed
# =============================================================================


class TestParsePRStateClosed:
    """GH-05: Test parsing closed (not merged) PR state."""

    def test_closed_pr_state(self, adapter, mock_pr_response_closed):
        """Test that closed (not merged) PR is parsed correctly."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_pr_response_closed),
                stderr="",
            )

            result = adapter.get_pr_state("feat/abandoned")

            assert result.state == PRStateEnum.CLOSED


# =============================================================================
# GH-06: CI status all passing
# =============================================================================


class TestCIStatusAllPassing:
    """GH-06: Test CI status when all checks are passing."""

    def test_ci_all_passing(self, adapter, mock_ci_all_passing):
        """Test that all passing CI is correctly identified."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_ci_all_passing),
                stderr="",
            )

            result = adapter.get_ci_status(184)

            assert isinstance(result, CIChecks)
            assert result.total == 3
            assert result.passed == 3
            assert result.failed == 0
            assert result.pending == 0
            assert result.all_passed is True


# =============================================================================
# GH-07: CI status some failing
# =============================================================================


class TestCIStatusSomeFailing:
    """GH-07: Test CI status when some checks are failing."""

    def test_ci_some_failing(self, adapter, mock_ci_some_failing):
        """Test that failing CI checks are correctly identified."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_ci_some_failing),
                stderr="",
            )

            result = adapter.get_ci_status(184)

            assert result.total == 3
            assert result.passed == 2
            assert result.failed == 1
            assert result.pending == 0
            assert result.has_failures is True


# =============================================================================
# GH-08: CI status pending
# =============================================================================


class TestCIStatusPending:
    """GH-08: Test CI status when checks are pending."""

    def test_ci_pending(self, adapter, mock_ci_pending):
        """Test that pending CI checks are correctly identified."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_ci_pending),
                stderr="",
            )

            result = adapter.get_ci_status(184)

            assert result.total == 3
            assert result.passed == 1
            assert result.pending == 2
            assert result.all_passed is False


# =============================================================================
# GH-09: CodeRabbit approved
# =============================================================================


class TestCodeRabbitApproved:
    """GH-09: Test CodeRabbit approved status."""

    def test_coderabbit_approved(self, adapter, mock_reviews_approved):
        """Test that CodeRabbit approved is correctly identified."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_reviews_approved),
                stderr="",
            )

            result = adapter.get_coderabbit_status(184)

            assert result == "approved"


# =============================================================================
# GH-10: CodeRabbit changes requested
# =============================================================================


class TestCodeRabbitChangesRequested:
    """GH-10: Test CodeRabbit changes requested status."""

    def test_coderabbit_changes_requested(self, adapter, mock_reviews_changes_requested):
        """Test that CodeRabbit changes requested is correctly identified."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_reviews_changes_requested),
                stderr="",
            )

            result = adapter.get_coderabbit_status(184)

            assert result == "changes_requested"


# =============================================================================
# GH-11: CodeRabbit not present
# =============================================================================


class TestCodeRabbitNotPresent:
    """GH-11: Test when CodeRabbit review is not present."""

    def test_coderabbit_not_present(self, adapter, mock_reviews_no_coderabbit):
        """Test that missing CodeRabbit review returns None."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_reviews_no_coderabbit),
                stderr="",
            )

            result = adapter.get_coderabbit_status(184)

            assert result is None

    def test_empty_reviews_returns_none(self, adapter):
        """Test that empty reviews list returns None."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout="[]",
                stderr="",
            )

            result = adapter.get_coderabbit_status(184)

            assert result is None

    def test_coderabbit_with_user_field(self, adapter):
        """Test that CodeRabbit is found using 'user' field (REST API format)."""
        # REST API uses "user" instead of "author"
        reviews_with_user_field = [
            {
                "user": {"login": "coderabbitai"},
                "state": "APPROVED",
                "submittedAt": "2026-02-03T10:00:00Z",
            }
        ]
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(reviews_with_user_field),
                stderr="",
            )

            result = adapter.get_coderabbit_status(184)

            assert result == "approved"


# =============================================================================
# GH-12: Cache hit returns cached data
# =============================================================================


class TestCacheHit:
    """GH-12: Test that cache hit returns cached data without API call."""

    def test_pr_cache_hit(self, adapter, mock_pr_response_open):
        """Test that second PR call uses cache."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_pr_response_open),
                stderr="",
            )

            # First call
            result1 = adapter.get_pr_state("feat/qa-enforcement")
            # Second call (should use cache)
            result2 = adapter.get_pr_state("feat/qa-enforcement")

            # subprocess.run should only be called once
            assert mock_run.call_count == 1
            assert result1.number == result2.number

    def test_ci_cache_hit(self, adapter, mock_ci_all_passing):
        """Test that second CI call uses cache."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_ci_all_passing),
                stderr="",
            )

            # First call
            result1 = adapter.get_ci_status(184)
            # Second call (should use cache)
            result2 = adapter.get_ci_status(184)

            # subprocess.run should only be called once
            assert mock_run.call_count == 1
            assert result1.total == result2.total


# =============================================================================
# GH-13: Cache TTL expiration
# =============================================================================


class TestCacheTTLExpiration:
    """GH-13: Test that cache expires after TTL."""

    def test_cache_expires_after_ttl(self, mock_pr_response_open):
        """Test that cache expires and makes new API call after TTL."""
        # Create adapter with default TTL (60 seconds)
        adapter = GitHubAdapter(repo="owner/repo", cache_ttl=60)

        # Use time mocking instead of real sleep for reliable, fast tests
        mock_time = MagicMock()
        initial_time = 1000.0

        with patch("subprocess.run") as mock_run, \
             patch("worktree_monitor.github_adapter.time.time", mock_time):

            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_pr_response_open),
                stderr="",
            )

            # First call at t=1000
            mock_time.return_value = initial_time
            adapter.get_pr_state("feat/qa-enforcement")

            # Second call still within TTL (t=1050, 50 seconds later)
            mock_time.return_value = initial_time + 50
            adapter.get_pr_state("feat/qa-enforcement")

            # Should still be using cache (only 1 API call)
            assert mock_run.call_count == 1

            # Third call after TTL expired (t=1061, 61 seconds later)
            mock_time.return_value = initial_time + 61
            adapter.get_pr_state("feat/qa-enforcement")

            # Cache expired, should make a new API call (2 total)
            assert mock_run.call_count == 2


# =============================================================================
# GH-14: Rate limit handling
# =============================================================================


class TestRateLimitHandling:
    """GH-14: Test rate limit error handling."""

    def test_rate_limit_raises_error(self, adapter):
        """Test that rate limit response raises RateLimitError."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=1,
                stdout="",
                stderr="API rate limit exceeded for user",
            )

            with pytest.raises(RateLimitError):
                adapter.get_pr_state("feat/qa-enforcement")

    def test_rate_limit_error_includes_message(self, adapter):
        """Test that RateLimitError includes rate limit message."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=1,
                stdout="",
                stderr="API rate limit exceeded. Try again in 30 minutes.",
            )

            with pytest.raises(RateLimitError) as exc_info:
                adapter.get_pr_state("feat/qa-enforcement")

            assert "rate limit" in str(exc_info.value).lower()


# =============================================================================
# Additional Error Handling Tests
# =============================================================================


class TestGitHubAPIError:
    """Test GitHubAPIError handling for general API failures."""

    def test_api_error_raised_on_failure(self, adapter):
        """Test that non-rate-limit errors raise GitHubAPIError."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=1,
                stdout="",
                stderr="Not Found",
            )

            with pytest.raises(GitHubAPIError):
                adapter.get_pr_state("feat/nonexistent")

    def test_gh_cli_not_found(self, adapter):
        """Test handling when gh CLI is not installed."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("gh not found")

            with pytest.raises(GitHubAPIError) as exc_info:
                adapter.get_pr_state("feat/test")

            assert "gh" in str(exc_info.value).lower()


class TestCacheClearing:
    """Test cache management functionality."""

    def test_clear_cache(self, adapter, mock_pr_response_open):
        """Test that clear_cache() removes all cached data."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = CompletedProcess(
                args=[],
                returncode=0,
                stdout=json.dumps(mock_pr_response_open),
                stderr="",
            )

            # First call
            adapter.get_pr_state("feat/qa-enforcement")
            assert mock_run.call_count == 1

            # Clear cache
            adapter.clear_cache()

            # Second call (should make new API call)
            adapter.get_pr_state("feat/qa-enforcement")
            assert mock_run.call_count == 2
