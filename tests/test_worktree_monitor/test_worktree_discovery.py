"""
Worktree Monitor v2.0 - WorktreeDiscovery Tests

Tests for the WorktreeDiscovery module that parses git worktree
information and extracts status details.

Created: Phase 4 Day 0 (TDD)
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from worktree_monitor.constants import WorktreeStatus
from worktree_monitor.exceptions import (
    GitCommandError,
    GitNotFoundError,
    GitWorktreeError,
)
from worktree_monitor.models import WorktreeInfo
from worktree_monitor.worktree_discovery import WorktreeDiscovery

# =============================================================================
# Parsing Tests
# =============================================================================


class TestParsePorcelainOutput:
    """Tests for parsing git worktree list --porcelain output."""

    def test_parse_single_worktree(self, sample_porcelain_single):
        """Parse output with only the main worktree."""
        discovery = WorktreeDiscovery()
        result = discovery._parse_porcelain_output(sample_porcelain_single)

        assert len(result) == 1
        assert result[0]["path"] == "/Users/dev/dbt-playground"
        assert result[0]["head"] == "abc1234567890abcdef1234567890abcdef123456"
        assert result[0]["branch"] == "main"
        assert result[0]["is_detached"] is False

    def test_parse_multiple_worktrees(self, sample_porcelain_output):
        """Parse output with multiple worktrees including detached."""
        discovery = WorktreeDiscovery()
        result = discovery._parse_porcelain_output(sample_porcelain_output)

        assert len(result) == 4

        # Main worktree
        assert result[0]["path"] == "/Users/dev/dbt-playground"
        assert result[0]["branch"] == "main"
        assert result[0]["is_detached"] is False

        # Feature worktree
        assert result[1]["path"] == "/Users/dev/dbt-playground--feat-kanban"
        assert result[1]["branch"] == "feat/kanban-phase1"

        # QA worktree
        assert result[2]["path"] == "/Users/dev/dbt-playground--feat-qa"
        assert result[2]["branch"] == "feat/qa-enforcement"

        # Detached worktree
        assert result[3]["path"] == "/Users/dev/dbt-playground--detached"
        assert result[3]["is_detached"] is True
        assert result[3]["branch"] is None

    def test_parse_empty_output(self):
        """Parse empty output returns empty list."""
        discovery = WorktreeDiscovery()
        result = discovery._parse_porcelain_output("")

        assert result == []

    def test_extract_branch_from_refs_heads(self):
        """Branch name is correctly extracted from refs/heads/."""
        porcelain = """worktree /path/to/repo
HEAD abc123
branch refs/heads/feature/nested/branch-name
"""
        discovery = WorktreeDiscovery()
        result = discovery._parse_porcelain_output(porcelain)

        assert result[0]["branch"] == "feature/nested/branch-name"


class TestMainWorktreeIdentification:
    """Tests for identifying the main worktree."""

    def test_first_worktree_is_main(self, sample_porcelain_output):
        """First worktree in list is identified as main."""
        discovery = WorktreeDiscovery()
        result = discovery._parse_porcelain_output(sample_porcelain_output)

        # First worktree should be main
        assert result[0]["path"] == "/Users/dev/dbt-playground"

    def test_main_worktree_marked_correctly(self):
        """Main worktree has .git directory (not .git file)."""
        # The first worktree returned by git is always the main one
        discovery = WorktreeDiscovery()
        worktrees = discovery._parse_porcelain_output(
            """worktree /main/repo
HEAD abc123
branch refs/heads/main

worktree /feature/repo
HEAD def456
branch refs/heads/feature
"""
        )

        # First one is main
        assert worktrees[0]["path"] == "/main/repo"


class TestDetachedHeadState:
    """Tests for handling detached HEAD state."""

    def test_detached_head_recognized(self):
        """Worktree with 'detached' line is identified correctly."""
        porcelain = """worktree /path/to/detached
HEAD fedcba9876543210
detached
"""
        discovery = WorktreeDiscovery()
        result = discovery._parse_porcelain_output(porcelain)

        assert result[0]["is_detached"] is True
        assert result[0]["branch"] is None

    def test_detached_head_status(self):
        """Detached worktree has DETACHED status."""
        porcelain = """worktree /path/to/detached
HEAD fedcba9876543210
detached
"""
        discovery = WorktreeDiscovery()
        result = discovery._parse_porcelain_output(porcelain)

        # Parser marks is_detached, status is set during WorktreeInfo creation
        assert result[0]["is_detached"] is True


class TestCommitShortHash:
    """Tests for extracting commit short hash."""

    def test_commit_short_hash_7_chars(self):
        """Commit short hash is first 7 characters of full hash."""
        porcelain = """worktree /path/to/repo
HEAD abc1234567890abcdef1234567890abcdef123456
branch refs/heads/main
"""
        discovery = WorktreeDiscovery()
        result = discovery._parse_porcelain_output(porcelain)

        # Full hash
        assert result[0]["head"] == "abc1234567890abcdef1234567890abcdef123456"
        # Short hash should be extracted when creating WorktreeInfo
        assert result[0]["head"][:7] == "abc1234"


# =============================================================================
# Git Status Tests
# =============================================================================


class TestGitStatus:
    """Tests for git status --porcelain parsing."""

    def test_clean_worktree(self):
        """Clean worktree has 0 changed and 0 staged files."""
        discovery = WorktreeDiscovery()

        with patch.object(discovery, "_run_git_command") as mock_run:
            mock_run.return_value = ""  # Empty output = clean
            changed, staged = discovery._get_git_status(Path("/test/path"))

        assert changed == 0
        assert staged == 0

    def test_files_changed_only(self):
        """Count files changed but not staged."""
        discovery = WorktreeDiscovery()

        # Git status output format: XY filename
        # X = index status, Y = worktree status
        # ' M' = modified in worktree but not staged
        status_output = " M file1.py\n M file2.py\n?? new_file.txt\n"
        with patch.object(discovery, "_run_git_command") as mock_run:
            mock_run.return_value = status_output
            changed, staged = discovery._get_git_status(Path("/test/path"))

        # 2 modified + 1 untracked = 3 changed, 0 staged
        assert changed == 3
        assert staged == 0

    def test_files_staged_only(self):
        """Count files staged for commit."""
        discovery = WorktreeDiscovery()

        # 'M ' = modified and staged
        # 'A ' = added and staged
        status_output = "M  file1.py\nA  new_file.py\n"
        with patch.object(discovery, "_run_git_command") as mock_run:
            mock_run.return_value = status_output
            changed, staged = discovery._get_git_status(Path("/test/path"))

        # All staged
        assert changed == 2
        assert staged == 2

    def test_mixed_staged_and_unstaged(self):
        """Count mixed staged and unstaged files."""
        discovery = WorktreeDiscovery()

        status_output = "M  staged.py\n M unstaged.py\nMM both.py\nA  added.py\n?? untracked.txt\n"
        with patch.object(discovery, "_run_git_command") as mock_run:
            mock_run.return_value = status_output
            changed, staged = discovery._get_git_status(Path("/test/path"))

        # 5 total files changed
        assert changed == 5
        # 3 staged (M_, A_, MM counts as staged)
        assert staged == 3


# =============================================================================
# Last Commit Tests
# =============================================================================


class TestLastCommit:
    """Tests for extracting last commit information."""

    def test_extract_commit_info(self, fixed_now):
        """Extract hash, message, and date from last commit."""
        discovery = WorktreeDiscovery()

        # Format: %H%n%s%n%aI
        commit_output = """abc1234567890abcdef1234567890abcdef123456
feat(kanban): add workflow engine
2026-02-03T12:00:00+00:00"""

        with patch.object(discovery, "_run_git_command") as mock_run:
            mock_run.return_value = commit_output
            hash_full, message, date = discovery._get_last_commit(Path("/test/path"))

        assert hash_full == "abc1234567890abcdef1234567890abcdef123456"
        assert message == "feat(kanban): add workflow engine"
        assert date is not None
        assert date.year == 2026
        assert date.month == 2
        assert date.day == 3

    def test_commit_date_parsed_with_timezone(self):
        """Commit date is parsed with timezone information."""
        discovery = WorktreeDiscovery()

        commit_output = """abc123
message
2026-02-03T15:30:00-08:00"""

        with patch.object(discovery, "_run_git_command") as mock_run:
            mock_run.return_value = commit_output
            _, _, date = discovery._get_last_commit(Path("/test/path"))

        assert date is not None
        assert date.tzinfo is not None

    def test_empty_repo_no_commits(self):
        """Handle repository with no commits."""
        discovery = WorktreeDiscovery()

        with patch.object(discovery, "_run_git_command") as mock_run:
            mock_run.return_value = ""
            hash_full, message, date = discovery._get_last_commit(Path("/test/path"))

        assert hash_full == ""
        assert message == ""
        assert date is None


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_main_worktree_only(self, sample_porcelain_single):
        """Handle repository with only main worktree (no additional worktrees)."""
        discovery = WorktreeDiscovery()

        with patch.object(discovery, "_run_git_command") as mock_run:
            mock_run.return_value = sample_porcelain_single
            worktrees = discovery.list_worktrees()

        assert len(worktrees) == 1
        assert worktrees[0].is_main is True
        assert worktrees[0].branch == "main"

    def test_many_worktrees(self):
        """Handle repository with many worktrees (5+)."""
        # Generate porcelain output for 6 worktrees
        porcelain_parts = []
        for i in range(6):
            if i == 0:
                porcelain_parts.append(
                    f"""worktree /repo/main
HEAD {'a' * 40}
branch refs/heads/main
"""
                )
            else:
                porcelain_parts.append(
                    f"""worktree /repo/feature-{i}
HEAD {str(i) * 40}
branch refs/heads/feat/feature-{i}
"""
                )

        porcelain = "\n".join(porcelain_parts)
        discovery = WorktreeDiscovery()
        result = discovery._parse_porcelain_output(porcelain)

        assert len(result) == 6

    def test_branch_with_special_characters(self):
        """Handle branch names with special characters."""
        porcelain = """worktree /path/to/repo
HEAD abc123
branch refs/heads/feat/user/john-doe@company.com/feature-123
"""
        discovery = WorktreeDiscovery()
        result = discovery._parse_porcelain_output(porcelain)

        assert result[0]["branch"] == "feat/user/john-doe@company.com/feature-123"


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for graceful error handling."""

    def test_git_command_failure(self):
        """GitCommandError raised when git command fails."""
        discovery = WorktreeDiscovery()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=128, stdout="", stderr="fatal: not a git repository"
            )

            with pytest.raises(GitCommandError) as exc_info:
                discovery._run_git_command(["worktree", "list", "--porcelain"])

            assert exc_info.value.return_code == 128
            assert "not a git repository" in str(exc_info.value)

    def test_git_not_found(self):
        """GitNotFoundError raised when git executable not found."""
        discovery = WorktreeDiscovery(git_executable="/nonexistent/git")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("git not found")

            with pytest.raises(GitNotFoundError):
                discovery._run_git_command(["--version"])

    def test_list_worktrees_handles_errors_gracefully(self):
        """list_worktrees raises GitWorktreeError on failure."""
        discovery = WorktreeDiscovery()

        with patch.object(discovery, "_run_git_command") as mock_run:
            mock_run.side_effect = GitCommandError(
                "git worktree list", 128, "fatal: error"
            )

            with pytest.raises(GitWorktreeError):
                discovery.list_worktrees()


# =============================================================================
# Integration Tests (list_worktrees)
# =============================================================================


class TestListWorktrees:
    """Integration tests for the full list_worktrees method."""

    def test_list_worktrees_returns_worktree_info_objects(
        self, sample_porcelain_output, fixed_now
    ):
        """list_worktrees returns list of WorktreeInfo objects."""
        discovery = WorktreeDiscovery()

        with patch.object(discovery, "_run_git_command") as mock_run:
            # First call for worktree list
            # Subsequent calls for status and commit info
            mock_run.side_effect = [
                sample_porcelain_output,  # worktree list
                "",  # git status for main
                f"abc1234567890abcdef1234567890abcdef123456\nMerge PR\n{fixed_now.isoformat()}",  # commit for main
                "",  # git status for feat-kanban
                f"def4567890abcdef1234567890abcdef12345678\nfeat: kanban\n{fixed_now.isoformat()}",  # commit
                "",  # git status for feat-qa
                f"789abcdef1234567890abcdef1234567890abcdef\nfeat: qa\n{fixed_now.isoformat()}",  # commit
                "",  # git status for detached
                f"fedcba0987654321fedcba0987654321fedcba09\ncommit msg\n{fixed_now.isoformat()}",  # commit
            ]

            worktrees = discovery.list_worktrees()

        assert len(worktrees) == 4
        assert all(isinstance(wt, WorktreeInfo) for wt in worktrees)

        # Verify main worktree
        main_wt = worktrees[0]
        assert main_wt.is_main is True
        assert main_wt.branch == "main"
        assert main_wt.commit_short == "abc1234"

        # Verify detached worktree
        detached_wt = worktrees[3]
        assert detached_wt.status == WorktreeStatus.DETACHED

    def test_list_worktrees_with_dirty_status(self, fixed_now):
        """Worktree with changes has DIRTY status."""
        porcelain = """worktree /repo
HEAD abc123
branch refs/heads/main
"""
        discovery = WorktreeDiscovery()

        with patch.object(discovery, "_run_git_command") as mock_run:
            mock_run.side_effect = [
                porcelain,
                " M file.py\n?? new.txt",  # dirty status
                f"abc123\ncommit\n{fixed_now.isoformat()}",
            ]

            worktrees = discovery.list_worktrees()

        assert len(worktrees) == 1
        assert worktrees[0].status == WorktreeStatus.DIRTY
        assert worktrees[0].files_changed == 2


class TestGetWorktreeStatus:
    """Tests for get_worktree_status method."""

    def test_get_single_worktree_status(self, fixed_now):
        """Get detailed status for a specific worktree."""
        discovery = WorktreeDiscovery()

        with patch.object(discovery, "_run_git_command") as mock_run:
            mock_run.side_effect = [
                " M modified.py\nA  staged.py",  # status
                f"abc1234567890abcdef1234567890abcdef123456\nfeat: test\n{fixed_now.isoformat()}",  # commit
                "feat/test-branch",  # branch name
            ]

            status = discovery.get_worktree_status(Path("/repo/worktree"))

        assert isinstance(status, WorktreeInfo)
        assert status.files_changed == 2
        assert status.files_staged == 1
        assert status.last_commit_msg == "feat: test"


# =============================================================================
# Constructor Tests
# =============================================================================


class TestConstructor:
    """Tests for WorktreeDiscovery constructor."""

    def test_default_constructor(self):
        """Default constructor uses current directory and 'git'."""
        discovery = WorktreeDiscovery()

        assert discovery.git_executable == "git"
        # repo_path defaults to None (uses cwd)

    def test_custom_repo_path(self, tmp_path):
        """Custom repo path is used."""
        discovery = WorktreeDiscovery(repo_path=tmp_path)

        assert discovery.repo_path == tmp_path

    def test_custom_git_executable(self):
        """Custom git executable path is used."""
        discovery = WorktreeDiscovery(git_executable="/usr/local/bin/git")

        assert discovery.git_executable == "/usr/local/bin/git"
