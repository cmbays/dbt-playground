"""
Worktree Monitor v2.0 - Archive Manager

Manages version-based archives for historical tracking.
Archives are organized by version name (e.g., v0.10/) not by timestamp.

Design decisions:
- PM Decision #2: Archive by VERSION not time
- CRIT-02: Atomic writes via temp file + rename
- No automatic deletion - archives are permanent

Created: Phase 4 Day 3 (Track E)
"""

import json
import logging
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .exceptions import (
    ArchiveCorruptedError,
    ArchiveWriteError,
    InvalidVersionNameError,
)
from .models import (
    ArchiveMetrics,
    EnrichedWorktree,
    VersionArchive,
    VersionPlan,
    VersionSummary,
)

logger = logging.getLogger(__name__)


class ArchiveManager:
    """Manages version-based archives for historical tracking.

    Archives are organized by version name:
        archives/
            v0.9/
                manifest.json
            v0.10/
                manifest.json
            archive-index.json

    The archive-index.json maintains a list of all archived versions
    for quick enumeration without scanning directories.
    """

    INDEX_FILENAME = 'archive-index.json'
    MANIFEST_FILENAME = 'manifest.json'
    INDEX_SCHEMA_VERSION = 1

    # Version name pattern: v followed by major.minor (e.g., v0.10, v1.0)
    VERSION_PATTERN = re.compile(r'^v\d+\.\d+$')

    def __init__(self, archives_dir: Path):
        """Initialize with archives directory path.

        Creates the directory if it doesn't exist.

        Args:
            archives_dir: Path to the archives directory.
        """
        self.archives_dir = Path(archives_dir)
        self.archives_dir.mkdir(parents=True, exist_ok=True)

    def archive_version(
        self,
        version_name: str,
        plan: VersionPlan,
        worktrees: list[EnrichedWorktree],
        reason: str = '',
    ) -> VersionArchive:
        """Archive a complete version.

        Creates a versioned directory with manifest. If the version
        already exists, it will be overwritten with a warning.

        Args:
            version_name: Version identifier (e.g., "v0.10").
            plan: The VersionPlan configuration.
            worktrees: List of EnrichedWorktree objects to archive.
            reason: Reason for archiving.

        Returns:
            VersionArchive object with all archived data.

        Raises:
            InvalidVersionNameError: If version_name doesn't match expected format.
            ArchiveWriteError: If writing fails due to permissions or other IO errors.
        """
        # Validate version name format
        if not self.VERSION_PATTERN.match(version_name):
            raise InvalidVersionNameError(version_name)

        version_dir = self.archives_dir / version_name

        # Check for existing archive
        if version_dir.exists():
            logger.warning(
                f'Archive for version {version_name} already exists. '
                'Will overwrite with new archive.'
            )

        # Create version directory
        version_dir.mkdir(parents=True, exist_ok=True)

        # Compute metrics
        metrics = self._compute_metrics(plan, worktrees)

        # Extract phase names
        phases = [phase.name for phase in plan.phases]

        # Serialize worktrees
        worktree_data = [wt.to_dict() for wt in worktrees]

        # Create archive timestamp
        archived_at = datetime.now(UTC)

        # Create VersionArchive object
        archive = VersionArchive(
            version=version_name,
            archived_at=archived_at,
            reason=reason,
            phases=phases,
            worktrees=worktree_data,
            metrics=metrics,
            plan_snapshot=plan.to_dict(),
        )

        # Write manifest atomically
        manifest_path = version_dir / self.MANIFEST_FILENAME
        self._atomic_write_json(manifest_path, archive.to_dict())

        # Update index
        self._update_index(version_name)

        logger.info(f'Archived version {version_name} with {len(worktrees)} worktrees')
        return archive

    def list_versions(self) -> list[VersionSummary]:
        """List all archived versions from index.

        Returns:
            List of VersionSummary objects, one per archived version.

        Raises:
            ArchiveCorruptedError: If the index file is corrupted.
        """
        index_path = self.archives_dir / self.INDEX_FILENAME

        if not index_path.exists():
            return []

        try:
            index_data = json.loads(index_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise ArchiveCorruptedError(
                str(index_path),
                f'Invalid JSON in archive index: {e}',
            ) from e

        summaries = []
        for version_name in index_data.get('versions', []):
            # Skip invalid/corrupted version names to prevent path traversal
            if not self.VERSION_PATTERN.match(version_name):
                logger.warning(f'Skipping invalid version name in index: {version_name}')
                continue
            archive = self.get_version(version_name)
            if archive:
                summaries.append(
                    VersionSummary(
                        version=archive.version,
                        archived_at=archive.archived_at,
                        worktree_count=len(archive.worktrees),
                        reason=archive.reason,
                    )
                )

        return summaries

    def get_version(self, version_name: str) -> VersionArchive | None:
        """Load a specific version archive.

        Args:
            version_name: Version identifier (e.g., "v0.10").

        Returns:
            VersionArchive if found, None if not found or invalid name.

        Raises:
            ArchiveCorruptedError: If the manifest file is corrupted.
        """
        # Validate version_name to prevent path traversal attacks
        if not self.VERSION_PATTERN.match(version_name):
            logger.warning(f'Invalid version name rejected: {version_name}')
            return None

        version_dir = self.archives_dir / version_name
        manifest_path = version_dir / self.MANIFEST_FILENAME

        if not manifest_path.exists():
            return None

        try:
            manifest_data = json.loads(manifest_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise ArchiveCorruptedError(
                str(manifest_path),
                f'Invalid JSON in manifest: {e}',
            ) from e

        # Parse datetime
        archived_at_str = manifest_data.get('archived_at')
        if archived_at_str:
            archived_at = datetime.fromisoformat(archived_at_str)
        else:
            archived_at = datetime.now(UTC)

        # Parse metrics
        metrics_data = manifest_data.get('metrics', {})
        metrics = ArchiveMetrics(
            worktree_count=metrics_data.get('worktree_count', 0),
            phase_count=metrics_data.get('phase_count', 0),
            workstream_count=metrics_data.get('workstream_count', 0),
            total_commits=metrics_data.get('total_commits', 0),
            total_prs_merged=metrics_data.get('total_prs_merged', 0),
        )

        return VersionArchive(
            version=manifest_data.get('version', version_name),
            archived_at=archived_at,
            reason=manifest_data.get('reason', ''),
            phases=manifest_data.get('phases', []),
            worktrees=manifest_data.get('worktrees', []),
            metrics=metrics,
            plan_snapshot=manifest_data.get('plan_snapshot'),
        )

    def _compute_metrics(
        self, plan: VersionPlan, worktrees: list[EnrichedWorktree]
    ) -> ArchiveMetrics:
        """Compute metrics from plan and worktrees.

        Args:
            plan: The VersionPlan configuration.
            worktrees: List of EnrichedWorktree objects.

        Returns:
            ArchiveMetrics with computed values.
        """
        phase_count = len(plan.phases)
        workstream_count = sum(len(phase.workstreams) for phase in plan.phases)

        # Count PRs that are merged
        prs_merged = sum(1 for wt in worktrees if wt.pr and wt.pr.state.value == 'merged')

        return ArchiveMetrics(
            worktree_count=len(worktrees),
            phase_count=phase_count,
            workstream_count=workstream_count,
            total_commits=0,  # Could be enhanced later
            total_prs_merged=prs_merged,
        )

    def _update_index(self, version_name: str) -> None:
        """Update the archive index with a new version.

        Args:
            version_name: Version to add to the index.

        Raises:
            ArchiveWriteError: If writing fails.
        """
        index_path = self.archives_dir / self.INDEX_FILENAME

        # Load existing index or create new
        if index_path.exists():
            try:
                index_data = json.loads(index_path.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                # Corrupted index, start fresh
                logger.warning('Corrupted archive index, creating new one')
                index_data = {
                    'version': self.INDEX_SCHEMA_VERSION,
                    'versions': [],
                }
        else:
            index_data = {
                'version': self.INDEX_SCHEMA_VERSION,
                'versions': [],
            }

        # Add version if not already present
        if version_name not in index_data['versions']:
            index_data['versions'].append(version_name)

        # Update timestamp
        index_data['last_updated'] = datetime.now(UTC).isoformat()

        # Write atomically
        self._atomic_write_json(index_path, index_data)

    def _atomic_write_json(self, path: Path, data: dict[str, Any]) -> None:
        """Write JSON data atomically using temp file + rename.

        This ensures partial writes don't corrupt the file.

        Args:
            path: Target file path.
            data: Dictionary to serialize as JSON.

        Raises:
            ArchiveWriteError: If writing fails.
        """
        # Create temp file in same directory for atomic rename
        dir_path = path.parent
        try:
            fd, temp_path = tempfile.mkstemp(
                suffix='.tmp',
                prefix=path.stem + '_',
                dir=dir_path,
            )
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)

                # Atomic replace (works consistently across platforms)
                os.replace(temp_path, path)
            except (OSError, TypeError, ValueError):
                # Clean up temp file on write/replace failures, then re-raise
                # for outer handlers to convert to ArchiveWriteError
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
        except PermissionError as e:
            raise ArchiveWriteError(str(path), f'Permission denied: {e}') from e
        except OSError as e:
            raise ArchiveWriteError(str(path), f'IO error: {e}') from e
