"""
Worktree Monitor v2.0 - Version Plan Loader

Loads, validates, and provides access to version plan configuration from YAML files.
Supports hot-reload detection and branch-to-workstream matching with glob patterns.

Created: Phase 4 Day 1
"""

from enum import Enum
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml

from .constants import PhaseStatus, VersionStatus, WorkstreamStatus
from .exceptions import (
    VersionPlanNotFoundError,
    VersionPlanParseError,
    VersionPlanValidationError,
)
from .models import PhaseConfig, VersionPlan, WorkstreamConfig


class VersionPlanLoader:
    """Loader for version plan YAML configuration files.

    Provides:
    - YAML loading with error handling
    - Validation against expected schema
    - Default value application for optional fields
    - Hot-reload detection based on file modification time
    - Branch-to-workstream matching with glob patterns

    Example:
        loader = VersionPlanLoader(Path("config/version-plan.yaml"))
        plan = loader.load()
        workstream = loader.match_branch_to_workstream("feat/kanban-phase1")
    """

    def __init__(self, config_path: Path | str, schema_path: Path | str | None = None):
        """Initialize the loader with path to version-plan.yaml.

        Args:
            config_path: Path to the version plan YAML file.
            schema_path: Optional path to JSON Schema for validation (not implemented).
        """
        self._config_path = Path(config_path)
        self._schema_path = Path(schema_path) if schema_path else None
        self._cached_plan: VersionPlan | None = None
        self._last_mtime: float | None = None

    def load(self) -> VersionPlan:
        """Load and validate version plan from YAML file.

        Returns:
            VersionPlan model populated from YAML.

        Raises:
            VersionPlanNotFoundError: If the file doesn't exist.
            VersionPlanParseError: If YAML syntax is invalid.
            VersionPlanValidationError: If schema validation fails.
        """
        # Check file exists
        if not self._config_path.exists():
            raise VersionPlanNotFoundError(str(self._config_path))

        # Load YAML content
        raw_data = self._load_yaml()

        # Validate and transform to model
        plan = self._validate_and_build_model(raw_data)

        # Cache for hot-reload
        self._cached_plan = plan
        self._last_mtime = self._config_path.stat().st_mtime

        return plan

    def reload_if_changed(self) -> VersionPlan | None:
        """Reload if file has changed since last load.

        Returns:
            New VersionPlan if file was modified, None if unchanged.
            Returns None on error (graceful degradation - keeps cached config).
        """
        if not self._config_path.exists():
            return None

        current_mtime = self._config_path.stat().st_mtime

        # No previous load or file hasn't changed
        if self._last_mtime is None or current_mtime == self._last_mtime:
            return None

        # File has changed - try to reload
        try:
            plan = self.load()
            return plan
        except (VersionPlanParseError, VersionPlanValidationError):
            # Graceful degradation: return None, keep cached plan
            # Update mtime to prevent repeated failed reloads
            self._last_mtime = current_mtime
            return None

    def match_branch_to_workstream(self, branch: str) -> WorkstreamConfig | None:
        """Match a branch name to a workstream using glob patterns.

        Args:
            branch: Git branch name (e.g., "feat/kanban-phase1").

        Returns:
            WorkstreamConfig if a match is found, None otherwise.
        """
        result = self._find_workstream(branch)
        return result[1] if result else None

    def get_workstream_for_branch(
        self, branch: str
    ) -> tuple[PhaseConfig, WorkstreamConfig] | None:
        """Get phase and workstream for a branch.

        Args:
            branch: Git branch name.

        Returns:
            Tuple of (PhaseConfig, WorkstreamConfig) if found, None otherwise.
        """
        return self._find_workstream(branch)

    def _find_workstream(
        self, branch: str
    ) -> tuple[PhaseConfig, WorkstreamConfig] | None:
        """Internal method to find phase and workstream for a branch.

        Args:
            branch: Git branch name.

        Returns:
            Tuple of (PhaseConfig, WorkstreamConfig) if found, None otherwise.
        """
        if self._cached_plan is None:
            return None

        for phase in self._cached_plan.phases:
            for workstream in phase.workstreams:
                if self._branch_matches_workstream(branch, workstream):
                    return (phase, workstream)

        return None

    def _branch_matches_workstream(
        self, branch: str, workstream: WorkstreamConfig
    ) -> bool:
        """Check if a branch matches any of the workstream's branch patterns.

        Uses fnmatch for glob-style pattern matching.

        Args:
            branch: Git branch name.
            workstream: WorkstreamConfig to check against.

        Returns:
            True if branch matches any pattern, False otherwise.
        """
        for pattern in workstream.branches:
            if fnmatch(branch, pattern):
                return True
        return False

    def _load_yaml(self) -> dict[str, Any]:
        """Load YAML content from file.

        Returns:
            Parsed YAML as dictionary.

        Raises:
            VersionPlanParseError: If YAML syntax is invalid.
        """
        try:
            content = self._config_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            if data is None:
                raise VersionPlanParseError(
                    "YAML file is empty or contains only comments"
                )
            return data
        except yaml.YAMLError as e:
            # Extract line/column info if available
            line = None
            column = None
            if hasattr(e, "problem_mark") and e.problem_mark:
                line = e.problem_mark.line + 1
                column = e.problem_mark.column + 1

            raise VersionPlanParseError(
                f"Failed to parse YAML: {e}", line=line, column=column
            ) from e

    def _validate_and_build_model(self, data: dict[str, Any]) -> VersionPlan:
        """Validate YAML data and build VersionPlan model.

        Args:
            data: Parsed YAML dictionary.

        Returns:
            VersionPlan model.

        Raises:
            VersionPlanValidationError: If validation fails.
        """
        errors: list[str] = []

        # Validate required top-level fields
        if "version" not in data:
            errors.append("Missing required field: 'version'")
        elif not isinstance(data.get("version"), int):
            errors.append("Field 'version' must be an integer")

        if "name" not in data:
            errors.append("Missing required field: 'name'")

        if "target_date" not in data:
            errors.append("Missing required field: 'target_date'")

        if "phases" not in data:
            errors.append("Missing required field: 'phases'")
        elif not isinstance(data.get("phases"), list):
            errors.append("Field 'phases' must be a list")
        elif len(data.get("phases", [])) == 0:
            errors.append("Field 'phases' must have at least one phase")

        # Validate status enum if present
        if "status" in data and data["status"] not in [s.value for s in VersionStatus]:
            errors.append(
                f"Invalid status value: '{data['status']}'. "
                f"Must be one of: {[s.value for s in VersionStatus]}"
            )

        if errors:
            raise VersionPlanValidationError(
                f"Version plan validation failed: {'; '.join(errors)}",
                validation_errors=errors,
            )

        # Build phases
        phases = self._build_phases(data.get("phases", []))

        # Build VersionPlan with defaults
        return VersionPlan(
            version=data["version"],
            name=data["name"],
            target_date=data["target_date"],
            description=data.get("description", ""),
            status=self._parse_status(
                data.get("status", "PLANNED"), VersionStatus, VersionStatus.PLANNED
            ),
            phases=phases,
        )

    def _build_phases(self, phases_data: list[dict[str, Any]]) -> list[PhaseConfig]:
        """Build list of PhaseConfig from YAML data.

        Args:
            phases_data: List of phase dictionaries from YAML.

        Returns:
            List of PhaseConfig models.

        Raises:
            VersionPlanValidationError: If phase validation fails.
        """
        phases = []
        errors: list[str] = []

        for i, phase_data in enumerate(phases_data):
            try:
                phase = self._build_phase(phase_data, i)
                phases.append(phase)
            except VersionPlanValidationError as e:
                errors.extend(e.validation_errors)

        if errors:
            raise VersionPlanValidationError(
                f"Phase validation failed: {'; '.join(errors)}",
                validation_errors=errors,
            )

        return phases

    def _build_phase(self, data: dict[str, Any], index: int) -> PhaseConfig:
        """Build a single PhaseConfig from YAML data.

        Args:
            data: Phase dictionary from YAML.
            index: Phase index (for error messages).

        Returns:
            PhaseConfig model.

        Raises:
            VersionPlanValidationError: If validation fails.
        """
        errors: list[str] = []

        if "name" not in data:
            errors.append(f"Phase {index + 1}: Missing required field 'name'")

        if "order" not in data:
            errors.append(f"Phase {index + 1}: Missing required field 'order'")
        elif not isinstance(data.get("order"), int):
            errors.append(f"Phase {index + 1}: Field 'order' must be an integer")

        if "workstreams" not in data:
            errors.append(f"Phase {index + 1}: Missing required field 'workstreams'")
        elif not isinstance(data.get("workstreams"), list):
            errors.append(f"Phase {index + 1}: Field 'workstreams' must be a list")

        # Validate status enum if present
        if "status" in data and data["status"] not in [s.value for s in PhaseStatus]:
            errors.append(
                f"Phase {index + 1}: Invalid status value: '{data['status']}'"
            )

        if errors:
            raise VersionPlanValidationError(
                f"Phase validation failed",
                validation_errors=errors,
            )

        # Build workstreams
        workstreams = self._build_workstreams(
            data.get("workstreams", []), data.get("name", f"Phase {index + 1}")
        )

        return PhaseConfig(
            name=data["name"],
            order=data["order"],
            description=data.get("description", ""),
            status=self._parse_status(
                data.get("status", "PLANNED"), PhaseStatus, PhaseStatus.PLANNED
            ),
            dependencies=data.get("dependencies", []),
            workstreams=workstreams,
        )

    def _build_workstreams(
        self, workstreams_data: list[dict[str, Any]], phase_name: str
    ) -> list[WorkstreamConfig]:
        """Build list of WorkstreamConfig from YAML data.

        Args:
            workstreams_data: List of workstream dictionaries from YAML.
            phase_name: Parent phase name (for error messages).

        Returns:
            List of WorkstreamConfig models.

        Raises:
            VersionPlanValidationError: If workstream validation fails.
        """
        workstreams = []
        errors: list[str] = []

        for i, ws_data in enumerate(workstreams_data):
            try:
                ws = self._build_workstream(ws_data, phase_name, i)
                workstreams.append(ws)
            except VersionPlanValidationError as e:
                errors.extend(e.validation_errors)

        if errors:
            raise VersionPlanValidationError(
                f"Workstream validation failed",
                validation_errors=errors,
            )

        return workstreams

    def _build_workstream(
        self, data: dict[str, Any], phase_name: str, index: int
    ) -> WorkstreamConfig:
        """Build a single WorkstreamConfig from YAML data.

        Args:
            data: Workstream dictionary from YAML.
            phase_name: Parent phase name (for error messages).
            index: Workstream index (for error messages).

        Returns:
            WorkstreamConfig model.

        Raises:
            VersionPlanValidationError: If validation fails.
        """
        errors: list[str] = []

        if "name" not in data:
            errors.append(
                f"{phase_name}, Workstream {index + 1}: Missing required field 'name'"
            )

        if "epic" not in data:
            errors.append(
                f"{phase_name}, Workstream {index + 1}: Missing required field 'epic'"
            )

        if "branches" not in data:
            errors.append(
                f"{phase_name}, Workstream {index + 1}: Missing required field 'branches'"
            )
        elif not isinstance(data.get("branches"), list):
            errors.append(
                f"{phase_name}, Workstream {index + 1}: Field 'branches' must be a list"
            )

        # Validate status enum if present
        if "status" in data and data["status"] not in [
            s.value for s in WorkstreamStatus
        ]:
            errors.append(
                f"{phase_name}, Workstream {index + 1}: Invalid status value: '{data['status']}'"
            )

        if errors:
            raise VersionPlanValidationError(
                f"Workstream validation failed",
                validation_errors=errors,
            )

        return WorkstreamConfig(
            name=data["name"],
            epic=data["epic"],
            branches=data.get("branches", []),
            status=self._parse_status(
                data.get("status", "PLANNED"), WorkstreamStatus, WorkstreamStatus.PLANNED
            ),
            color=data.get("color"),
        )

    @staticmethod
    def _parse_status(value: str, enum_class: type[Enum], default: Enum) -> Enum:
        """Parse a status string into the specified enum type.

        Args:
            value: String value to parse.
            enum_class: The enum class to convert to.
            default: Default value if parsing fails.

        Returns:
            Enum value, or default if parsing fails.
        """
        try:
            return enum_class(value)
        except ValueError:
            return default
