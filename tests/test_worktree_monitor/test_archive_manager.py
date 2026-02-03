"""
Worktree Monitor v2.0 - Archive Manager Tests

Tests for the ArchiveManager class that handles version-based archiving.
Test IDs: AM-01 through AM-14

Created: Phase 4 Day 3 (Track E)
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def archive_manager(tmp_path):
    """Create an ArchiveManager with a temporary directory."""
    from worktree_monitor.archive_manager import ArchiveManager

    archives_dir = tmp_path / "archives"
    return ArchiveManager(archives_dir)


@pytest.fixture
def sample_version_plan(version_plan_model):
    """Sample version plan for archiving."""
    return version_plan_model


@pytest.fixture
def sample_enriched_worktrees(sample_worktree_info, sample_worktree_info_dirty):
    """Sample enriched worktrees for archiving."""
    from worktree_monitor.models import EnrichedWorktree

    return [
        EnrichedWorktree.from_worktree_info(sample_worktree_info),
        EnrichedWorktree.from_worktree_info(sample_worktree_info_dirty),
    ]


@pytest.fixture
def populated_archive(archive_manager, sample_version_plan, sample_enriched_worktrees):
    """Archive manager with a pre-populated v0.9 archive."""
    # Archive a test version
    archive_manager.archive_version(
        version_name="v0.9",
        plan=sample_version_plan,
        worktrees=sample_enriched_worktrees,
        reason="Version completed",
    )
    return archive_manager


# =============================================================================
# AM-01: Create archive directory if not exists
# =============================================================================


class TestAM01DirectoryCreation:
    """AM-01: Archive directory creation."""

    def test_creates_directory_on_init(self, tmp_path):
        """Archive directory is created when ArchiveManager is initialized."""
        from worktree_monitor.archive_manager import ArchiveManager

        archives_dir = tmp_path / "new_archives"
        assert not archives_dir.exists()

        ArchiveManager(archives_dir)
        assert archives_dir.exists()
        assert archives_dir.is_dir()

    def test_existing_directory_not_overwritten(self, tmp_path):
        """Existing archive directory is not modified."""
        from worktree_monitor.archive_manager import ArchiveManager

        archives_dir = tmp_path / "existing_archives"
        archives_dir.mkdir()
        marker_file = archives_dir / "marker.txt"
        marker_file.write_text("existing", encoding="utf-8")

        ArchiveManager(archives_dir)
        assert marker_file.exists()
        assert marker_file.read_text() == "existing"


# =============================================================================
# AM-02: Archive workstream on completion
# =============================================================================


class TestAM02ArchiveWorkstream:
    """AM-02: Archive a complete workstream/version."""

    def test_archive_version_creates_files(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Archiving a version creates the expected directory and manifest."""
        result = archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Version completed",
        )

        # Check return value
        assert result is not None
        assert result.version == "v0.10"
        assert result.reason == "Version completed"

        # Check files created
        version_dir = archive_manager.archives_dir / "v0.10"
        assert version_dir.exists()
        manifest_file = version_dir / "manifest.json"
        assert manifest_file.exists()

    def test_archive_version_returns_version_archive(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """archive_version returns a VersionArchive object."""
        from worktree_monitor.models import VersionArchive

        result = archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Version completed",
        )

        assert isinstance(result, VersionArchive)
        assert result.version == "v0.10"


# =============================================================================
# AM-03: Archive by version not time
# =============================================================================


class TestAM03ArchiveByVersion:
    """AM-03: Archives are organized by version, not timestamp."""

    def test_directory_named_by_version(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Archive directory is named by version (e.g., v0.10), not timestamp."""
        archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Test",
        )

        # Should exist: archives/v0.10/
        version_dir = archive_manager.archives_dir / "v0.10"
        assert version_dir.exists()

        # Should NOT have timestamp-based directories
        for child in archive_manager.archives_dir.iterdir():
            assert not child.name.startswith("2026")
            assert not child.name.startswith("20")  # No year-prefixed dirs

    def test_multiple_versions_separate_directories(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Each version gets its own directory."""
        archive_manager.archive_version(
            version_name="v0.9",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Old version",
        )
        archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="New version",
        )

        assert (archive_manager.archives_dir / "v0.9").exists()
        assert (archive_manager.archives_dir / "v0.10").exists()


# =============================================================================
# AM-04: Retrieve archived versions list
# =============================================================================


class TestAM04ListVersions:
    """AM-04: List all archived versions."""

    def test_list_empty_archives(self, archive_manager):
        """list_versions returns empty list when no archives exist."""
        result = archive_manager.list_versions()
        assert result == []

    def test_list_versions_returns_summaries(
        self, populated_archive, sample_version_plan, sample_enriched_worktrees
    ):
        """list_versions returns VersionSummary objects."""
        from worktree_monitor.models import VersionSummary

        # Add another version
        populated_archive.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Test",
        )

        result = populated_archive.list_versions()
        assert len(result) == 2
        assert all(isinstance(v, VersionSummary) for v in result)

        version_names = [v.version for v in result]
        assert "v0.9" in version_names
        assert "v0.10" in version_names


# =============================================================================
# AM-05: Retrieve specific version archive
# =============================================================================


class TestAM05GetVersion:
    """AM-05: Get a specific version archive."""

    def test_get_version_returns_archive(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """get_version returns the full VersionArchive."""
        from worktree_monitor.models import VersionArchive

        archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Test version",
        )

        result = archive_manager.get_version("v0.10")
        assert result is not None
        assert isinstance(result, VersionArchive)
        assert result.version == "v0.10"
        assert result.reason == "Test version"


# =============================================================================
# AM-06: Get version returns None for missing
# =============================================================================


class TestAM06GetVersionNotFound:
    """AM-06: get_version returns None for missing versions."""

    def test_get_nonexistent_version_returns_none(self, archive_manager):
        """get_version returns None when version doesn't exist."""
        result = archive_manager.get_version("v99.99")
        assert result is None

    def test_get_version_none_after_partial_archive(self, archive_manager, tmp_path):
        """get_version returns None if manifest is missing."""
        # Create directory but no manifest
        version_dir = archive_manager.archives_dir / "v0.10"
        version_dir.mkdir(parents=True)

        result = archive_manager.get_version("v0.10")
        assert result is None


# =============================================================================
# AM-07: Archive index updated after archive
# =============================================================================


class TestAM07ArchiveIndex:
    """AM-07: Archive index is updated when archiving."""

    def test_index_created_on_first_archive(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """archive-index.json is created on first archive."""
        index_file = archive_manager.archives_dir / "archive-index.json"
        assert not index_file.exists()

        archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="First",
        )

        assert index_file.exists()
        index_data = json.loads(index_file.read_text(encoding="utf-8"))
        assert "v0.10" in index_data["versions"]

    def test_index_updated_on_subsequent_archives(
        self, populated_archive, sample_version_plan, sample_enriched_worktrees
    ):
        """archive-index.json is updated when adding new versions."""
        populated_archive.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Second",
        )

        index_file = populated_archive.archives_dir / "archive-index.json"
        index_data = json.loads(index_file.read_text(encoding="utf-8"))
        assert "v0.9" in index_data["versions"]
        assert "v0.10" in index_data["versions"]


# =============================================================================
# AM-08: Archive preserves worktree data
# =============================================================================


class TestAM08PreserveWorktreeData:
    """AM-08: Archived data includes worktree information."""

    def test_worktree_data_in_manifest(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Manifest contains worktree data."""
        archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Test",
        )

        manifest_file = archive_manager.archives_dir / "v0.10" / "manifest.json"
        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))

        assert "worktrees" in manifest_data
        assert len(manifest_data["worktrees"]) == 2

    def test_worktree_branch_preserved(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Worktree branch names are preserved in archive."""
        archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Test",
        )

        result = archive_manager.get_version("v0.10")
        branches = [w["branch"] for w in result.worktrees]
        assert "feat/kanban-phase1" in branches


# =============================================================================
# AM-09: Archive preserves metrics
# =============================================================================


class TestAM09PreserveMetrics:
    """AM-09: Archive includes computed metrics."""

    def test_metrics_in_version_archive(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """VersionArchive includes ArchiveMetrics."""
        from worktree_monitor.models import ArchiveMetrics

        result = archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Test",
        )

        assert result.metrics is not None
        assert isinstance(result.metrics, ArchiveMetrics)

    def test_metrics_calculated_correctly(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Metrics reflect actual worktree data."""
        result = archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Test",
        )

        assert result.metrics.worktree_count == 2
        assert result.metrics.phase_count > 0


# =============================================================================
# AM-10: Duplicate archive overwrites with warning
# =============================================================================


class TestAM10DuplicateArchive:
    """AM-10: Re-archiving a version overwrites existing."""

    def test_duplicate_archive_overwrites(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Archiving same version twice overwrites the first."""
        # First archive
        archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="First archive",
        )

        # Second archive with different reason
        archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Second archive",
        )

        # Should have the new reason
        result = archive_manager.get_version("v0.10")
        assert result.reason == "Second archive"

    def test_duplicate_archive_logs_warning(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees, caplog
    ):
        """Re-archiving logs a warning."""
        import logging

        # First archive
        archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="First",
        )

        # Second archive
        with caplog.at_level(logging.WARNING):
            archive_manager.archive_version(
                version_name="v0.10",
                plan=sample_version_plan,
                worktrees=sample_enriched_worktrees,
                reason="Second",
            )

        assert any("v0.10" in record.message and "overwrite" in record.message.lower()
                   for record in caplog.records)


# =============================================================================
# AM-11: Handle archive file corruption
# =============================================================================


class TestAM11HandleCorruption:
    """AM-11: Handle corrupted archive files gracefully."""

    def test_corrupted_manifest_raises_error(self, archive_manager):
        """Corrupted manifest raises ArchiveCorruptedError."""
        from worktree_monitor.exceptions import ArchiveCorruptedError

        # Create corrupted manifest
        version_dir = archive_manager.archives_dir / "v0.10"
        version_dir.mkdir(parents=True)
        manifest_file = version_dir / "manifest.json"
        manifest_file.write_text("{ invalid json }", encoding="utf-8")

        with pytest.raises(ArchiveCorruptedError) as exc_info:
            archive_manager.get_version("v0.10")

        assert "v0.10" in str(exc_info.value)

    def test_corrupted_index_handled(self, archive_manager):
        """Corrupted index file is handled gracefully."""
        from worktree_monitor.exceptions import ArchiveCorruptedError

        # Create corrupted index
        index_file = archive_manager.archives_dir / "archive-index.json"
        index_file.write_text("not valid json", encoding="utf-8")

        # Should raise on list_versions
        with pytest.raises(ArchiveCorruptedError):
            archive_manager.list_versions()


# =============================================================================
# AM-12: Archive includes timestamp and reason
# =============================================================================


class TestAM12TimestampAndReason:
    """AM-12: Archives include metadata."""

    def test_archive_includes_timestamp(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """VersionArchive includes archived_at timestamp."""
        result = archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Test",
        )

        assert result.archived_at is not None
        assert isinstance(result.archived_at, datetime)

    def test_archive_includes_reason(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """VersionArchive includes the provided reason."""
        result = archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Milestone completed successfully",
        )

        assert result.reason == "Milestone completed successfully"

    def test_timestamp_persisted_to_manifest(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Timestamp is persisted in manifest file."""
        archive_manager.archive_version(
            version_name="v0.10",
            plan=sample_version_plan,
            worktrees=sample_enriched_worktrees,
            reason="Test",
        )

        manifest_file = archive_manager.archives_dir / "v0.10" / "manifest.json"
        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))

        assert "archived_at" in manifest_data
        # Should be ISO format string
        datetime.fromisoformat(manifest_data["archived_at"])


# =============================================================================
# AM-13: Permission error handled gracefully
# =============================================================================


class TestAM13PermissionErrors:
    """AM-13: Permission errors are handled gracefully."""

    def test_permission_error_on_write(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Permission errors raise ArchiveWriteError."""
        from worktree_monitor.exceptions import ArchiveWriteError

        # Mock os.rename to raise PermissionError
        with patch("os.rename", side_effect=PermissionError("Permission denied")):
            with pytest.raises(ArchiveWriteError) as exc_info:
                archive_manager.archive_version(
                    version_name="v0.10",
                    plan=sample_version_plan,
                    worktrees=sample_enriched_worktrees,
                    reason="Test",
                )

            assert "Permission" in str(exc_info.value) or "permission" in str(exc_info.value).lower()

    def test_permission_error_includes_path(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Permission error includes the path that failed."""
        from worktree_monitor.exceptions import ArchiveWriteError

        with patch("os.rename", side_effect=PermissionError("Permission denied")):
            with pytest.raises(ArchiveWriteError) as exc_info:
                archive_manager.archive_version(
                    version_name="v0.10",
                    plan=sample_version_plan,
                    worktrees=sample_enriched_worktrees,
                    reason="Test",
                )

            # Should have path in details
            assert exc_info.value.path is not None


# =============================================================================
# AM-14: No automatic deletion
# =============================================================================


class TestAM14NoAutomaticDeletion:
    """AM-14: Archives are never automatically deleted."""

    def test_archive_manager_has_no_delete_method(self, archive_manager):
        """ArchiveManager does not expose delete methods."""
        # These methods should NOT exist
        assert not hasattr(archive_manager, "delete_version")
        assert not hasattr(archive_manager, "delete_archive")
        assert not hasattr(archive_manager, "cleanup")
        assert not hasattr(archive_manager, "prune")

    def test_multiple_archives_all_preserved(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Multiple versions are all preserved."""
        versions = ["v0.8", "v0.9", "v0.10"]
        for v in versions:
            archive_manager.archive_version(
                version_name=v,
                plan=sample_version_plan,
                worktrees=sample_enriched_worktrees,
                reason=f"Archiving {v}",
            )

        # All should exist
        for v in versions:
            assert (archive_manager.archives_dir / v).exists()
            assert archive_manager.get_version(v) is not None


# =============================================================================
# AM-15: Version name validation
# =============================================================================


class TestAM15VersionNameValidation:
    """AM-15: Version names must match expected format."""

    def test_valid_version_names(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Valid version names are accepted."""
        valid_names = ["v0.1", "v0.10", "v1.0", "v10.20", "v999.999"]
        for name in valid_names:
            # Should not raise
            archive = archive_manager.archive_version(
                version_name=name,
                plan=sample_version_plan,
                worktrees=sample_enriched_worktrees,
            )
            assert archive.version == name

    def test_invalid_version_names_rejected(
        self, archive_manager, sample_version_plan, sample_enriched_worktrees
    ):
        """Invalid version names raise InvalidVersionNameError."""
        from worktree_monitor.exceptions import InvalidVersionNameError

        invalid_names = [
            "0.10",  # Missing 'v' prefix
            "version0.10",  # Wrong prefix
            "v0",  # Missing minor version
            "v0.10.0",  # Patch version not allowed
            "v.10",  # Missing major version
            "vA.B",  # Non-numeric
            "v0.10-beta",  # Suffix not allowed
            "../v0.10",  # Path traversal attempt
        ]
        for name in invalid_names:
            with pytest.raises(InvalidVersionNameError) as excinfo:
                archive_manager.archive_version(
                    version_name=name,
                    plan=sample_version_plan,
                    worktrees=sample_enriched_worktrees,
                )
            assert name in str(excinfo.value)
