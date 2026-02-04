"""
Worktree Monitor v2.0 - GitHub Adapter

Adapter for GitHub API via gh CLI with caching support.
Provides methods to fetch PR state, CI status, and CodeRabbit review status.

Created: Phase 4 Day 3
"""

import json
import random
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .constants import PRState as PRStateEnum
from .models import PRInfo, CIChecks
from .exceptions import GitHubAPIError, RateLimitError


@dataclass
class CacheEntry:
    """Single cache entry with TTL tracking."""

    data: Any
    timestamp: float


class GitHubAdapter:
    """Adapter for GitHub API via gh CLI with caching.

    Provides methods to:
    - Get PR state for a branch
    - Get CI check status for a PR
    - Get CodeRabbit review status for a PR

    All methods use in-memory caching with configurable TTL.
    """

    # Repository name validation pattern (owner/repo format)
    REPO_NAME_PATTERN = re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')

    # Cache TTL defaults (in seconds)
    DEFAULT_CACHE_TTL = 60

    # Maximum cache entries to prevent unbounded growth
    MAX_CACHE_SIZE = 1000

    # Sentinel value for caching None results
    _CACHED_NONE = "__NONE__"

    # Retry configuration for transient failures
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BASE_DELAY = 1.0  # seconds
    DEFAULT_MAX_DELAY = 10.0  # seconds

    # Transient error indicators in stderr
    TRANSIENT_ERROR_PATTERNS = (
        "connection reset",
        "connection refused",
        "network is unreachable",
        "temporary failure",
        "timeout",
        "502",
        "503",
        "504",
    )

    def __init__(self, repo: str, cache_ttl: int | None = None):
        """Initialize GitHubAdapter.

        Args:
            repo: Repository in 'owner/repo' format
            cache_ttl: Cache TTL in seconds (defaults to DEFAULT_CACHE_TTL)

        Raises:
            ValueError: If repo format is invalid
        """
        if not self.REPO_NAME_PATTERN.match(repo):
            raise ValueError(
                f"Invalid repository format: '{repo}'. "
                "Expected 'owner/repo' with alphanumeric, underscore, dot, or hyphen characters."
            )
        self.repo = repo
        self.cache_ttl = cache_ttl if cache_ttl is not None else self.DEFAULT_CACHE_TTL
        self._cache: dict[str, CacheEntry] = {}

    def _get_cached(self, key: str, ttl: int | None = None) -> Any | None:
        """Get value from cache if not expired.

        Args:
            key: Cache key
            ttl: TTL override (uses default if None)

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]
        effective_ttl = ttl if ttl is not None else self.cache_ttl
        age = time.time() - entry.timestamp

        if age >= effective_ttl:
            del self._cache[key]
            return None

        return entry.data

    def _set_cached(self, key: str, value: Any) -> None:
        """Store value in cache with current timestamp.

        Enforces MAX_CACHE_SIZE by evicting oldest entries when full.
        Only evicts when inserting a new key, not when updating existing.
        Stores None values as _CACHED_NONE sentinel.

        Args:
            key: Cache key
            value: Value to cache (None is stored as sentinel)
        """
        # Only enforce cache size limit when inserting a NEW key
        if key not in self._cache:
            while len(self._cache) >= self.MAX_CACHE_SIZE:
                # Find and remove the oldest entry by timestamp
                oldest_key = min(self._cache, key=lambda k: self._cache[k].timestamp)
                del self._cache[oldest_key]

        # Store None as sentinel to distinguish from cache miss
        store_value = self._CACHED_NONE if value is None else value
        self._cache[key] = CacheEntry(data=store_value, timestamp=time.time())

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()

    def _is_transient_error(self, stderr: str) -> bool:
        """Check if stderr indicates a transient/retriable error.

        Args:
            stderr: Error output from gh CLI

        Returns:
            True if error appears transient and should be retried
        """
        stderr_lower = stderr.lower()
        return any(pattern in stderr_lower for pattern in self.TRANSIENT_ERROR_PATTERNS)

    def _run_gh_command(self, args: list[str]) -> str:
        """Execute gh CLI command with retry logic for transient failures.

        Implements exponential backoff with jitter for transient errors.
        Does NOT retry: FileNotFoundError, TimeoutExpired, rate-limit errors.

        Args:
            args: Command arguments (without 'gh' prefix)

        Returns:
            Command stdout

        Raises:
            RateLimitError: When GitHub API rate limit is exceeded (no retry)
            GitHubAPIError: For other API errors (after retries exhausted)
        """
        cmd = ["gh"] + args
        endpoint = " ".join(args)
        last_error: Exception | None = None
        last_stderr: str = ""

        for attempt in range(self.DEFAULT_MAX_RETRIES):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            except FileNotFoundError as e:
                # Not retriable - gh CLI not installed
                raise GitHubAPIError(
                    message="gh CLI not found. Please install GitHub CLI.",
                    status_code=None,
                    endpoint=endpoint,
                ) from e
            except subprocess.TimeoutExpired as e:
                # Not retriable - command timed out
                raise GitHubAPIError(
                    message="gh CLI command timed out",
                    status_code=None,
                    endpoint=endpoint,
                ) from e

            # Check for success
            if result.returncode == 0:
                return result.stdout

            # Check for non-retriable errors
            stderr = result.stderr
            stderr_lower = stderr.lower()

            # Rate limit errors are not retriable
            if "rate limit" in stderr_lower:
                raise RateLimitError(remaining=0)

            # Check if this is a transient error worth retrying
            if not self._is_transient_error(stderr):
                # Non-transient error, fail immediately
                raise GitHubAPIError(
                    message=f"gh CLI failed: {stderr}",
                    status_code=result.returncode,
                    endpoint=endpoint,
                )

            # Transient error - prepare for retry
            last_error = GitHubAPIError(
                message=f"gh CLI failed: {stderr}",
                status_code=result.returncode,
                endpoint=endpoint,
            )
            last_stderr = stderr

            # Calculate delay with exponential backoff and jitter
            if attempt < self.DEFAULT_MAX_RETRIES - 1:
                delay = min(
                    self.DEFAULT_BASE_DELAY * (2 ** attempt),
                    self.DEFAULT_MAX_DELAY,
                )
                # Add jitter (0-50% of delay)
                jitter = random.uniform(0, delay * 0.5)
                time.sleep(delay + jitter)

        # All retries exhausted
        raise GitHubAPIError(
            message=f"gh CLI failed after {self.DEFAULT_MAX_RETRIES} attempts: {last_stderr}",
            status_code=None,
            endpoint=endpoint,
        ) from last_error

    def get_pr_state(self, branch: str) -> PRInfo | None:
        """Get PR state for a branch.

        Args:
            branch: Branch name to find PR for

        Returns:
            PRInfo if PR exists, None otherwise

        Raises:
            RateLimitError: When GitHub API rate limit is exceeded
            GitHubAPIError: For other API errors
        """
        cache_key = f"pr:{branch}"
        # Use instance cache_ttl (allows per-adapter TTL configuration)
        cached = self._get_cached(cache_key)
        # Check for cached "no PR" sentinel (distinguishes from cache miss)
        if cached == self._CACHED_NONE:
            return None
        if cached is not None:
            return cached

        # Query GitHub for PRs with this head branch
        args = [
            "pr",
            "list",
            "--repo",
            self.repo,
            "--head",
            branch,
            "--state",
            "all",
            "--json",
            "number,state,title,url,headRefName,isDraft,createdAt,updatedAt,merged,mergedAt",
            "--limit",
            "1",
        ]

        output = self._run_gh_command(args)

        try:
            prs = json.loads(output)
        except json.JSONDecodeError:
            prs = []

        if not prs:
            self._set_cached(cache_key, None)
            return None

        pr_data = prs[0]
        pr_info = self._parse_pr_response(pr_data)
        self._set_cached(cache_key, pr_info)
        return pr_info

    def _parse_pr_response(self, pr_data: dict[str, Any]) -> PRInfo:
        """Parse PR API response into PRInfo model.

        Args:
            pr_data: Raw PR data from gh CLI

        Returns:
            PRInfo dataclass instance
        """
        # Determine PR state based on state and merged fields
        state_str = pr_data.get("state", "open").lower()
        is_merged = pr_data.get("merged", False)

        if state_str == "closed" and is_merged:
            state = PRStateEnum.MERGED
        elif state_str == "closed":
            state = PRStateEnum.CLOSED
        else:
            state = PRStateEnum.OPEN

        # Parse timestamps
        created_at = None
        updated_at = None

        if pr_data.get("createdAt"):
            created_at = datetime.fromisoformat(
                pr_data["createdAt"].replace("Z", "+00:00")
            )
        if pr_data.get("updatedAt"):
            updated_at = datetime.fromisoformat(
                pr_data["updatedAt"].replace("Z", "+00:00")
            )

        return PRInfo(
            url=pr_data.get("url", ""),
            number=pr_data.get("number", 0),
            state=state,
            title=pr_data.get("title", ""),
            created_at=created_at,
            updated_at=updated_at,
            draft=pr_data.get("isDraft", False),
        )

    def get_ci_status(self, pr_number: int) -> CIChecks:
        """Get CI check status for a PR.

        Args:
            pr_number: PR number to get CI status for

        Returns:
            CIChecks with counts of passed/failed/pending checks

        Raises:
            RateLimitError: When GitHub API rate limit is exceeded
            GitHubAPIError: For other API errors
        """
        cache_key = f"ci:{pr_number}"
        # Use instance cache_ttl (allows per-adapter TTL configuration)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Query GitHub for check runs on the PR
        args = [
            "pr",
            "view",
            str(pr_number),
            "--repo",
            self.repo,
            "--json",
            "statusCheckRollup",
        ]

        output = self._run_gh_command(args)

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            data = {}

        # Handle both formats: statusCheckRollup or checkRuns directly
        check_runs = []
        if "statusCheckRollup" in data:
            check_runs = data.get("statusCheckRollup", []) or []
        elif "checkRuns" in data:
            check_runs = data.get("checkRuns", []) or []

        ci_checks = self._parse_ci_response(check_runs)
        self._set_cached(cache_key, ci_checks)
        return ci_checks

    def _parse_ci_response(self, check_runs: list[dict[str, Any]]) -> CIChecks:
        """Parse CI check runs into CIChecks model.

        CI Status Logic:
        - COMPLETED + SUCCESS = passed
        - COMPLETED + FAILURE/CANCELLED/TIMED_OUT = failed
        - IN_PROGRESS/QUEUED/PENDING = pending

        Args:
            check_runs: List of check run data

        Returns:
            CIChecks dataclass instance
        """
        passed = 0
        failed = 0
        pending = 0

        for check in check_runs:
            status = check.get("status", "").upper()
            conclusion = check.get("conclusion", "").upper() if check.get("conclusion") else ""

            if status == "COMPLETED":
                if conclusion == "SUCCESS":
                    passed += 1
                elif conclusion in ("FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"):
                    failed += 1
                else:
                    # NEUTRAL, SKIPPED, or unknown = treat as passed
                    passed += 1
            else:
                # IN_PROGRESS, QUEUED, PENDING, WAITING
                pending += 1

        total = passed + failed + pending

        return CIChecks(
            total=total,
            passed=passed,
            failed=failed,
            pending=pending,
        )

    def get_coderabbit_status(self, pr_number: int) -> str | None:
        """Get CodeRabbit review status for a PR.

        Args:
            pr_number: PR number to get CodeRabbit status for

        Returns:
            'approved', 'changes_requested', or None if no CodeRabbit review

        Raises:
            RateLimitError: When GitHub API rate limit is exceeded
            GitHubAPIError: For other API errors
        """
        cache_key = f"coderabbit:{pr_number}"
        # Use instance cache_ttl (allows per-adapter TTL configuration)
        cached = self._get_cached(cache_key)
        # Check for cached "no CodeRabbit review" sentinel
        if cached == self._CACHED_NONE:
            return None
        if cached is not None:
            return cached

        # Query GitHub for PR reviews
        args = [
            "api",
            f"repos/{self.repo}/pulls/{pr_number}/reviews",
        ]

        output = self._run_gh_command(args)

        try:
            reviews = json.loads(output)
        except json.JSONDecodeError:
            reviews = []

        result = self._parse_coderabbit_status(reviews)

        # Cache result (None is automatically stored as sentinel by _set_cached)
        self._set_cached(cache_key, result)
        return result

    def _parse_coderabbit_status(self, reviews: list[dict[str, Any]]) -> str | None:
        """Parse reviews to find CodeRabbit status.

        Looks for the most recent review from coderabbitai user.

        Args:
            reviews: List of review data from GitHub API

        Returns:
            'approved', 'changes_requested', or None
        """
        # Find CodeRabbit reviews (most recent first)
        # Check both "author" and "user" fields as GitHub API returns different structures
        coderabbit_reviews = [
            r for r in reviews
            if self._get_review_author_login(r).lower() == "coderabbitai"
        ]

        if not coderabbit_reviews:
            return None

        # Sort by submittedAt to get most recent
        coderabbit_reviews.sort(
            key=lambda r: r.get("submittedAt", ""),
            reverse=True,
        )

        latest_review = coderabbit_reviews[0]
        state = latest_review.get("state", "").upper()

        if state == "APPROVED":
            return "approved"
        elif state == "CHANGES_REQUESTED":
            return "changes_requested"
        else:
            return None

    def _get_review_author_login(self, review: dict[str, Any]) -> str:
        """Extract author login from review data.

        GitHub API returns author info as either 'author' or 'user' depending
        on the endpoint used.

        Args:
            review: Review data from GitHub API

        Returns:
            Author login string, or empty string if not found
        """
        # Try "user" field first (common in REST API responses)
        user_login = review.get("user", {}).get("login", "")
        if user_login:
            return user_login

        # Fall back to "author" field (common in GraphQL responses)
        return review.get("author", {}).get("login", "")
