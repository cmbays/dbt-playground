"""
Worktree Monitor v2.0 - Worktree Discovery Module

Discovers and parses git worktree information using git commands.
Provides structured WorktreeInfo objects with status details.

Created: Phase 4 Day 0 (Implementation)
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from .constants import WorktreeStatus
from .exceptions import GitCommandError, GitNotFoundError, GitWorktreeError
from .models import WorktreeInfo


class WorktreeDiscovery:
    """Discovers git worktrees and their status.

    This class provides methods to:
    - List all worktrees in a repository
    - Get detailed status for individual worktrees
    - Parse git porcelain output formats

    Attributes:
        repo_path: Path to the git repository (or None for current directory).
        git_executable: Path to the git executable.
    """

    # Default timeout for git commands (seconds)
    DEFAULT_GIT_TIMEOUT = 30

    def __init__(
        self,
        repo_path: Path | None = None,
        git_executable: str = "git",
        git_timeout: int | None = None,
    ) -> None:
        """Initialize WorktreeDiscovery.

        Args:
            repo_path: Path to the git repository. If None, uses current directory.
            git_executable: Path to the git executable. Defaults to "git".
            git_timeout: Timeout for git commands in seconds. Defaults to 30.
        """
        self.repo_path = repo_path
        self.git_executable = git_executable
        self.git_timeout = git_timeout if git_timeout is not None else self.DEFAULT_GIT_TIMEOUT

    def list_worktrees(self) -> list[WorktreeInfo]:
        """List all worktrees with basic info.

        Returns:
            List of WorktreeInfo objects for each worktree.

        Raises:
            GitWorktreeError: If listing worktrees fails.
        """
        parsed = self._get_raw_worktree_data()
        return [self._build_worktree_info(wt, idx) for idx, wt in enumerate(parsed)]

    def _get_raw_worktree_data(self) -> list[dict[str, Any]]:
        """Get raw worktree data from git.

        Returns:
            List of parsed worktree dictionaries.

        Raises:
            GitWorktreeError: If git command fails.
        """
        try:
            porcelain_output = self._run_git_command(
                ["worktree", "list", "--porcelain"]
            )
        except GitCommandError as e:
            raise GitWorktreeError(
                f"Failed to list worktrees: {e.message}",
                worktree_path=str(self.repo_path) if self.repo_path else None,
            ) from e

        return self._parse_porcelain_output(porcelain_output)

    def _build_worktree_info(self, wt_data: dict[str, Any], idx: int) -> WorktreeInfo:
        """Build WorktreeInfo from parsed worktree data.

        Args:
            wt_data: Parsed worktree dictionary.
            idx: Index of this worktree (0 = main).

        Returns:
            WorktreeInfo object.
        """
        wt_path = Path(wt_data["path"])

        # Get status and commit info with graceful fallbacks
        try:
            files_changed, files_staged = self._get_git_status(wt_path)
        except (GitCommandError, GitNotFoundError):
            files_changed, files_staged = 0, 0

        try:
            commit_hash, commit_msg, commit_date = self._get_last_commit(wt_path)
        except (GitCommandError, GitNotFoundError):
            commit_hash = wt_data.get("head", "")
            commit_msg = ""
            commit_date = None

        # Use parsed head if commit_hash not set
        if not commit_hash:
            commit_hash = wt_data.get("head", "")

        return WorktreeInfo(
            path=wt_data["path"],
            branch=wt_data.get("branch") or "",
            commit_hash=commit_hash,
            commit_short=commit_hash[:7] if commit_hash else "",
            is_main=(idx == 0),
            status=self._determine_status(
                wt_data.get("is_detached", False), files_changed, files_staged
            ),
            files_changed=files_changed,
            files_staged=files_staged,
            last_commit_msg=commit_msg,
            last_commit_date=commit_date,
        )

    def get_worktree_status(self, worktree_path: Path) -> WorktreeInfo:
        """Get detailed status for a single worktree.

        Args:
            worktree_path: Path to the worktree directory.

        Returns:
            WorktreeInfo object with current status.

        Raises:
            GitWorktreeError: If getting status fails.
        """
        # Get status
        try:
            files_changed, files_staged = self._get_git_status(worktree_path)
        except (GitCommandError, GitNotFoundError) as e:
            raise GitWorktreeError(
                f"Failed to get status for worktree: {e}",
                worktree_path=str(worktree_path),
            ) from e

        # Get commit info
        try:
            commit_hash, commit_msg, commit_date = self._get_last_commit(worktree_path)
        except (GitCommandError, GitNotFoundError):
            commit_hash = ""
            commit_msg = ""
            commit_date = None

        # Get branch name
        try:
            branch = self._run_git_command(
                ["rev-parse", "--abbrev-ref", "HEAD"], cwd=worktree_path
            ).strip()
        except (GitCommandError, GitNotFoundError):
            branch = ""

        # Determine status
        is_detached = branch == "HEAD"
        if is_detached:
            branch = ""
        status = self._determine_status(is_detached, files_changed, files_staged)

        return WorktreeInfo(
            path=str(worktree_path),
            branch=branch,
            commit_hash=commit_hash,
            commit_short=commit_hash[:7] if commit_hash else "",
            is_main=False,  # Cannot determine from single worktree query
            status=status,
            files_changed=files_changed,
            files_staged=files_staged,
            last_commit_msg=commit_msg,
            last_commit_date=commit_date,
        )

    def _determine_status(
        self,
        is_detached: bool,
        files_changed: int,
        files_staged: int,
    ) -> WorktreeStatus:
        """Determine worktree status from state flags.

        Args:
            is_detached: Whether the worktree has a detached HEAD.
            files_changed: Number of changed files (staged or unstaged).
            files_staged: Number of staged files.

        Returns:
            WorktreeStatus enum value.
        """
        if is_detached:
            return WorktreeStatus.DETACHED
        elif files_changed > 0 or files_staged > 0:
            return WorktreeStatus.DIRTY
        return WorktreeStatus.CLEAN

    def _parse_porcelain_output(self, output: str) -> list[dict[str, Any]]:
        """Parse git worktree list --porcelain output.

        The porcelain format is:
            worktree /path/to/worktree
            HEAD <commit-hash>
            branch refs/heads/<branch-name>
            (or 'detached' for detached HEAD)
            <blank line>

        Args:
            output: Raw porcelain output from git worktree list.

        Returns:
            List of dictionaries with parsed worktree data.
            Each dict has keys: path, head, branch (or None), is_detached.
        """
        if not output.strip():
            return []

        worktrees = []
        current_wt: dict[str, Any] = {}

        for line in output.split("\n"):
            line = line.rstrip()

            if line.startswith("worktree "):
                # Start of new worktree block
                if current_wt:
                    worktrees.append(current_wt)
                current_wt = {
                    "path": line[9:],  # Remove "worktree " prefix
                    "is_detached": False,
                    "branch": None,
                }

            elif line.startswith("HEAD "):
                current_wt["head"] = line[5:]  # Remove "HEAD " prefix

            elif line.startswith("branch "):
                # Extract branch name from refs/heads/...
                branch_ref = line[7:]  # Remove "branch " prefix
                if branch_ref.startswith("refs/heads/"):
                    current_wt["branch"] = branch_ref[11:]  # Remove "refs/heads/"
                else:
                    current_wt["branch"] = branch_ref

            elif line == "detached":
                current_wt["is_detached"] = True
                current_wt["branch"] = None

        # Don't forget the last worktree
        if current_wt:
            worktrees.append(current_wt)

        return worktrees

    def _get_git_status(self, worktree_path: Path) -> tuple[int, int]:
        """Get (files_changed, files_staged) for a worktree.

        Uses git status --porcelain to get file status.
        Format: XY filename where X=index status, Y=worktree status

        Args:
            worktree_path: Path to the worktree directory.

        Returns:
            Tuple of (files_changed, files_staged).
        """
        output = self._run_git_command(
            ["status", "--porcelain"], cwd=worktree_path
        )

        # Don't strip the whole string - we need leading spaces for status codes
        # Instead, strip trailing whitespace and check if empty
        output = output.rstrip()
        if not output:
            return 0, 0

        files_changed = 0
        files_staged = 0

        for line in output.split("\n"):
            # Strip only trailing whitespace from each line, preserve leading
            line = line.rstrip()
            if not line:
                continue

            # First two characters are status codes
            # X = index status (staged)
            # Y = worktree status (unstaged)
            if len(line) >= 2:
                x_status = line[0]  # Index (staged)
                y_status = line[1]  # Worktree (unstaged)

                # Any non-space character means a change
                if x_status != " " or y_status != " ":
                    files_changed += 1

                # Staged changes (X is not space and not ?)
                if x_status not in (" ", "?"):
                    files_staged += 1

        return files_changed, files_staged

    def _get_last_commit(
        self, worktree_path: Path
    ) -> tuple[str, str, datetime | None]:
        """Get (hash, message, date) for last commit.

        Args:
            worktree_path: Path to the worktree directory.

        Returns:
            Tuple of (full_hash, commit_message, commit_datetime).
            Returns ("", "", None) if no commits or error.
        """
        # Format: %H = full hash, %s = subject, %aI = author date ISO format
        output = self._run_git_command(
            ["log", "-1", "--format=%H%n%s%n%aI"], cwd=worktree_path
        ).strip()

        if not output:
            return "", "", None

        lines = output.split("\n")
        if len(lines) < 3:
            return "", "", None

        commit_hash = lines[0]
        commit_msg = lines[1]
        date_str = lines[2]

        # Parse ISO date
        commit_date = None
        if date_str:
            try:
                commit_date = datetime.fromisoformat(date_str)
            except ValueError:
                pass

        return commit_hash, commit_msg, commit_date

    def _run_git_command(
        self, args: list[str], cwd: Path | None = None
    ) -> str:
        """Run a git command and return stdout.

        Args:
            args: Arguments to pass to git (not including 'git' itself).
            cwd: Working directory for the command. Defaults to repo_path.

        Returns:
            stdout from the command.

        Raises:
            GitNotFoundError: If git executable not found.
            GitCommandError: If git command returns non-zero exit code or times out.
        """
        cmd = [self.git_executable] + args
        working_dir = cwd or self.repo_path

        try:
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                timeout=self.git_timeout,
            )
        except FileNotFoundError as e:
            raise GitNotFoundError(self.git_executable) from e
        except subprocess.TimeoutExpired as e:
            raise GitCommandError(
                command=" ".join(cmd),
                return_code=-1,
                stderr=f"Command timed out after {self.git_timeout} seconds",
            ) from e

        if result.returncode != 0:
            raise GitCommandError(
                command=" ".join(cmd),
                return_code=result.returncode,
                stderr=result.stderr.strip() if result.stderr else None,
            )

        return result.stdout
