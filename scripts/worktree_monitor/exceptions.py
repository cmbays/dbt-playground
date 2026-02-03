"""
Worktree Monitor v2.0 - Custom Exceptions

Typed exception hierarchy for consistent error handling across all modules.

Created: Phase 4 Day 0 (Pre-Work)
"""

from typing import Any

# =============================================================================
# Base Exception
# =============================================================================


class WorktreeMonitorError(Exception):
    """Base exception for all worktree monitor errors.

    All custom exceptions in this module inherit from this class,
    allowing callers to catch all monitor-related errors with a single
    except clause if desired.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f'{self.message} | Details: {self.details}'
        return self.message


# =============================================================================
# Configuration Errors
# =============================================================================


class ConfigError(WorktreeMonitorError):
    """Base class for configuration-related errors."""

    pass


class VersionPlanNotFoundError(ConfigError):
    """Raised when the version plan YAML file cannot be found."""

    def __init__(self, path: str):
        super().__init__(
            f'Version plan file not found: {path}',
            details={'path': path},
        )
        self.path = path


class VersionPlanValidationError(ConfigError):
    """Raised when version plan YAML fails validation against schema."""

    def __init__(self, message: str, validation_errors: list[str] | None = None):
        super().__init__(
            message,
            details={'validation_errors': validation_errors or []},
        )
        self.validation_errors = validation_errors or []


class VersionPlanSchemaError(ConfigError):
    """Raised when version plan has structural/schema issues."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(
            message,
            details={'field': field} if field else {},
        )
        self.field = field


class VersionPlanParseError(ConfigError):
    """Raised when YAML parsing fails (syntax errors)."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        details = {}
        if line is not None:
            details['line'] = line
        if column is not None:
            details['column'] = column
        super().__init__(message, details=details)
        self.line = line
        self.column = column


# =============================================================================
# Git Errors
# =============================================================================


class GitError(WorktreeMonitorError):
    """Base class for git-related errors."""

    pass


class GitNotFoundError(GitError):
    """Raised when git executable is not found."""

    def __init__(self, path: str = 'git'):
        super().__init__(
            f'Git executable not found: {path}',
            details={'executable': path},
        )
        self.executable = path


class GitCommandError(GitError):
    """Raised when a git command fails."""

    def __init__(
        self,
        command: str,
        return_code: int,
        stderr: str | None = None,
    ):
        message = f'Git command failed: {command} (exit code {return_code})'
        if stderr:
            message += f'\nStderr: {stderr}'
        super().__init__(
            message,
            details={
                'command': command,
                'return_code': return_code,
                'stderr': stderr,
            },
        )
        self.command = command
        self.return_code = return_code
        self.stderr = stderr


class GitWorktreeError(GitError):
    """Raised when worktree operations fail."""

    def __init__(self, message: str, worktree_path: str | None = None):
        super().__init__(
            message,
            details={'worktree_path': worktree_path} if worktree_path else {},
        )
        self.worktree_path = worktree_path


# =============================================================================
# GitHub API Errors
# =============================================================================


class GitHubError(WorktreeMonitorError):
    """Base class for GitHub API-related errors."""

    pass


class GitHubAPIError(GitHubError):
    """Raised when GitHub API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        endpoint: str | None = None,
    ):
        super().__init__(
            message,
            details={
                'status_code': status_code,
                'endpoint': endpoint,
            },
        )
        self.status_code = status_code
        self.endpoint = endpoint


class RateLimitError(GitHubError):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(
        self,
        remaining: int = 0,
        reset_at: str | None = None,
    ):
        super().__init__(
            f'GitHub API rate limit exceeded. Remaining: {remaining}',
            details={
                'remaining': remaining,
                'reset_at': reset_at,
            },
        )
        self.remaining = remaining
        self.reset_at = reset_at


class GitHubAuthError(GitHubError):
    """Raised when GitHub authentication fails."""

    def __init__(self, message: str = 'GitHub authentication failed'):
        super().__init__(message)


class GitHubNotFoundError(GitHubError):
    """Raised when a GitHub resource is not found (404)."""

    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            f'{resource_type} not found: {identifier}',
            details={
                'resource_type': resource_type,
                'identifier': identifier,
            },
        )
        self.resource_type = resource_type
        self.identifier = identifier


# =============================================================================
# Archive Errors
# =============================================================================


class ArchiveError(WorktreeMonitorError):
    """Base class for archive-related errors."""

    pass


class ArchiveNotFoundError(ArchiveError):
    """Raised when archive directory or file is not found."""

    def __init__(self, path: str):
        super().__init__(
            f'Archive not found: {path}',
            details={'path': path},
        )
        self.path = path


class ArchiveCorruptedError(ArchiveError):
    """Raised when archive data is corrupted or invalid."""

    def __init__(self, path: str, reason: str):
        super().__init__(
            f'Archive corrupted: {path}. Reason: {reason}',
            details={'path': path, 'reason': reason},
        )
        self.path = path
        self.reason = reason


class ArchiveWriteError(ArchiveError):
    """Raised when writing to archive fails."""

    def __init__(self, path: str, reason: str):
        super().__init__(
            f'Failed to write archive: {path}. Reason: {reason}',
            details={'path': path, 'reason': reason},
        )
        self.path = path
        self.reason = reason


class InvalidVersionNameError(ArchiveError):
    """Raised when version name does not match expected format."""

    def __init__(self, version_name: str, expected_pattern: str = r"^v\d+\.\d+"):
        super().__init__(
            f"Invalid version name: '{version_name}'. Expected format matching: {expected_pattern}",
            details={"version_name": version_name, "expected_pattern": expected_pattern},
        )
        self.version_name = version_name
        self.expected_pattern = expected_pattern


# =============================================================================
# Heartbeat Errors
# =============================================================================


class HeartbeatError(WorktreeMonitorError):
    """Base class for heartbeat-related errors."""

    pass


class HeartbeatFileNotFoundError(HeartbeatError):
    """Raised when heartbeat file does not exist."""

    def __init__(self, path: str):
        super().__init__(
            f'Heartbeat file not found: {path}',
            details={'path': path},
        )
        self.path = path


class HeartbeatParseError(HeartbeatError):
    """Raised when heartbeat file content cannot be parsed."""

    def __init__(self, path: str, reason: str):
        super().__init__(
            f'Failed to parse heartbeat file: {path}. Reason: {reason}',
            details={'path': path, 'reason': reason},
        )
        self.path = path
        self.reason = reason


# =============================================================================
# Monitor Errors
# =============================================================================


class MonitorError(WorktreeMonitorError):
    """Base class for monitor orchestrator errors."""

    pass


class ComponentError(MonitorError):
    """Raised when a monitor component fails but operation can continue.

    This is used for graceful degradation - the monitor can continue
    with partial data when one component fails.
    """

    def __init__(
        self,
        component: str,
        message: str,
        original_error: Exception | None = None,
    ):
        super().__init__(
            f"Component '{component}' failed: {message}",
            details={
                'component': component,
                'original_error': str(original_error) if original_error else None,
            },
        )
        self.component = component
        self.original_error = original_error


class CollectionError(MonitorError):
    """Raised when data collection fails completely."""

    def __init__(self, message: str, component_errors: list[ComponentError] | None = None):
        super().__init__(
            message,
            details={
                'component_errors': [str(e) for e in (component_errors or [])],
            },
        )
        self.component_errors = component_errors or []
