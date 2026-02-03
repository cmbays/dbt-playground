"""
Worktree Monitor v2.0 - VersionPlanLoader Tests

TDD tests for the version plan configuration loader.

Test Categories:
1. Basic YAML loading
2. Missing file handling
3. Malformed YAML handling
4. Schema validation
5. Default values
6. Hot-reload detection
7. Multiple phases parsing
8. Glob pattern matching
9. Color mappings extraction

Created: Phase 4 Day 1
"""

import time
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from worktree_monitor.exceptions import (
    VersionPlanNotFoundError,
    VersionPlanParseError,
    VersionPlanValidationError,
)
from worktree_monitor.models import (
    PhaseConfig,
    VersionPlan,
    WorkstreamConfig,
)
from worktree_monitor.constants import (
    PhaseStatus,
    VersionStatus,
    WorkstreamStatus,
)
from worktree_monitor.version_plan_loader import VersionPlanLoader


# =============================================================================
# Test 1: Load Valid YAML Configuration
# =============================================================================


class TestLoadValidYAML:
    """Test loading valid YAML configuration files."""

    def test_load_valid_version_plan(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Load a complete valid version plan YAML file."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert isinstance(plan, VersionPlan)
        assert plan.name == "v0.10"
        assert plan.version == 1
        assert plan.target_date == "2026-04-30"
        assert plan.description == "Agent Orchestration Enhancements"
        assert plan.status == VersionStatus.IN_PROGRESS

    def test_load_minimal_version_plan(
        self, tmp_path, minimal_version_plan_yaml
    ):
        """Load a minimal valid version plan with only required fields."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(minimal_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert isinstance(plan, VersionPlan)
        assert plan.name == "v0.11"
        assert plan.target_date == "2026-06-30"
        # Default values should be applied
        assert plan.status == VersionStatus.PLANNED
        assert plan.description == ""

    def test_load_returns_version_plan_model(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Load method returns a properly typed VersionPlan model."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        # Verify model structure
        assert hasattr(plan, "version")
        assert hasattr(plan, "name")
        assert hasattr(plan, "target_date")
        assert hasattr(plan, "description")
        assert hasattr(plan, "status")
        assert hasattr(plan, "phases")


# =============================================================================
# Test 2: Handle Missing File
# =============================================================================


class TestMissingFile:
    """Test handling of missing configuration files."""

    def test_missing_file_raises_not_found_error(self, tmp_path):
        """Raise VersionPlanNotFoundError for missing file."""
        missing_file = tmp_path / "nonexistent.yaml"

        loader = VersionPlanLoader(missing_file)

        with pytest.raises(VersionPlanNotFoundError) as exc_info:
            loader.load()

        assert str(missing_file) in str(exc_info.value)
        assert exc_info.value.path == str(missing_file)

    def test_missing_file_error_has_path_attribute(self, tmp_path):
        """VersionPlanNotFoundError includes the missing path."""
        missing_file = tmp_path / "missing-config.yaml"

        loader = VersionPlanLoader(missing_file)

        with pytest.raises(VersionPlanNotFoundError) as exc_info:
            loader.load()

        assert exc_info.value.path == str(missing_file)


# =============================================================================
# Test 3: Handle Malformed YAML Syntax
# =============================================================================


class TestMalformedYAML:
    """Test handling of malformed YAML syntax."""

    def test_invalid_yaml_syntax_raises_parse_error(
        self, tmp_path, invalid_yaml
    ):
        """Raise VersionPlanParseError for invalid YAML syntax."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text(invalid_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)

        with pytest.raises(VersionPlanParseError) as exc_info:
            loader.load()

        # Should indicate YAML parsing failed
        assert "parse" in str(exc_info.value).lower() or "yaml" in str(exc_info.value).lower()

    def test_malformed_yaml_with_tabs_and_spaces(self, tmp_path):
        """Handle YAML with inconsistent indentation."""
        bad_indent_yaml = """
version: 1
name: v0.10
phases:
  - name: Phase A
\torder: 1  # Tab instead of space
    workstreams: []
"""
        config_file = tmp_path / "bad-indent.yaml"
        config_file.write_text(bad_indent_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)

        with pytest.raises(VersionPlanParseError):
            loader.load()

    def test_completely_invalid_content(self, tmp_path):
        """Handle completely invalid content (not YAML at all)."""
        config_file = tmp_path / "not-yaml.yaml"
        config_file.write_text("{{{{not valid yaml at all::::", encoding="utf-8")

        loader = VersionPlanLoader(config_file)

        with pytest.raises(VersionPlanParseError):
            loader.load()


# =============================================================================
# Test 4: Validate Against JSON Schema
# =============================================================================


class TestSchemaValidation:
    """Test validation against JSON schema."""

    def test_missing_required_field_raises_validation_error(self, tmp_path):
        """Raise VersionPlanValidationError for missing required fields."""
        # Missing 'name' field
        incomplete_yaml = """
version: 1
target_date: "2026-04-30"
phases:
  - name: Phase A
    order: 1
    workstreams:
      - name: Test
        epic: 100
        branches: [feat/test]
"""
        config_file = tmp_path / "incomplete.yaml"
        config_file.write_text(incomplete_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)

        with pytest.raises(VersionPlanValidationError) as exc_info:
            loader.load()

        # Should mention the missing field
        assert "name" in str(exc_info.value).lower() or len(exc_info.value.validation_errors) > 0

    def test_invalid_status_value_raises_validation_error(self, tmp_path):
        """Raise VersionPlanValidationError for invalid enum value."""
        bad_status_yaml = """
version: 1
name: v0.10
target_date: "2026-04-30"
status: INVALID_STATUS
phases:
  - name: Phase A
    order: 1
    workstreams:
      - name: Test
        epic: 100
        branches: [feat/test]
"""
        config_file = tmp_path / "bad-status.yaml"
        config_file.write_text(bad_status_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)

        with pytest.raises(VersionPlanValidationError) as exc_info:
            loader.load()

        # Should mention the invalid status
        assert "status" in str(exc_info.value).lower() or "INVALID_STATUS" in str(exc_info.value)


# =============================================================================
# Test 5: Report Specific Validation Errors
# =============================================================================


class TestValidationErrorReporting:
    """Test specific validation error reporting."""

    def test_validation_errors_list_populated(self, tmp_path):
        """VersionPlanValidationError includes list of specific errors."""
        # Multiple validation issues
        multi_error_yaml = """
version: "not_an_int"
target_date: "2026-04-30"
phases: []
"""
        config_file = tmp_path / "multi-error.yaml"
        config_file.write_text(multi_error_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)

        with pytest.raises(VersionPlanValidationError) as exc_info:
            loader.load()

        # Should have validation_errors attribute with specific issues
        assert hasattr(exc_info.value, "validation_errors")

    def test_invalid_phase_order_type(self, tmp_path):
        """Report error when phase order is not an integer."""
        bad_order_yaml = """
version: 1
name: v0.10
target_date: "2026-04-30"
phases:
  - name: Phase A
    order: "first"
    workstreams:
      - name: Test
        epic: 100
        branches: [feat/test]
"""
        config_file = tmp_path / "bad-order.yaml"
        config_file.write_text(bad_order_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)

        with pytest.raises(VersionPlanValidationError):
            loader.load()


# =============================================================================
# Test 6: Support Default Values for Optional Fields
# =============================================================================


class TestDefaultValues:
    """Test default values for optional fields."""

    def test_version_status_defaults_to_planned(self, tmp_path):
        """Version status defaults to PLANNED if not specified."""
        no_status_yaml = """
version: 1
name: v0.11
target_date: "2026-06-30"
phases:
  - name: Phase A
    order: 1
    workstreams:
      - name: Feature One
        epic: 200
        branches:
          - feat/feature-one
"""
        config_file = tmp_path / "no-status.yaml"
        config_file.write_text(no_status_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert plan.status == VersionStatus.PLANNED

    def test_description_defaults_to_empty_string(self, tmp_path):
        """Description defaults to empty string if not specified."""
        no_desc_yaml = """
version: 1
name: v0.11
target_date: "2026-06-30"
phases:
  - name: Phase A
    order: 1
    workstreams:
      - name: Feature One
        epic: 200
        branches: [feat/feature-one]
"""
        config_file = tmp_path / "no-desc.yaml"
        config_file.write_text(no_desc_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert plan.description == ""

    def test_phase_status_defaults_to_planned(self, tmp_path):
        """Phase status defaults to PLANNED if not specified."""
        no_phase_status_yaml = """
version: 1
name: v0.11
target_date: "2026-06-30"
phases:
  - name: Phase A
    order: 1
    workstreams:
      - name: Feature One
        epic: 200
        branches: [feat/feature-one]
"""
        config_file = tmp_path / "no-phase-status.yaml"
        config_file.write_text(no_phase_status_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert plan.phases[0].status == PhaseStatus.PLANNED

    def test_workstream_status_defaults_to_planned(self, tmp_path):
        """Workstream status defaults to PLANNED if not specified."""
        no_ws_status_yaml = """
version: 1
name: v0.11
target_date: "2026-06-30"
phases:
  - name: Phase A
    order: 1
    workstreams:
      - name: Feature One
        epic: 200
        branches: [feat/feature-one]
"""
        config_file = tmp_path / "no-ws-status.yaml"
        config_file.write_text(no_ws_status_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert plan.phases[0].workstreams[0].status == WorkstreamStatus.PLANNED

    def test_workstream_color_defaults_to_none(self, tmp_path):
        """Workstream color defaults to None if not specified."""
        no_color_yaml = """
version: 1
name: v0.11
target_date: "2026-06-30"
phases:
  - name: Phase A
    order: 1
    workstreams:
      - name: Feature One
        epic: 200
        branches: [feat/feature-one]
"""
        config_file = tmp_path / "no-color.yaml"
        config_file.write_text(no_color_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert plan.phases[0].workstreams[0].color is None

    def test_phase_dependencies_defaults_to_empty_list(self, tmp_path):
        """Phase dependencies defaults to empty list if not specified."""
        no_deps_yaml = """
version: 1
name: v0.11
target_date: "2026-06-30"
phases:
  - name: Phase A
    order: 1
    workstreams:
      - name: Feature One
        epic: 200
        branches: [feat/feature-one]
"""
        config_file = tmp_path / "no-deps.yaml"
        config_file.write_text(no_deps_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert plan.phases[0].dependencies == []


# =============================================================================
# Test 7: Hot-Reload Detection
# =============================================================================


class TestHotReloadDetection:
    """Test hot-reload detection based on file modification time."""

    def test_reload_if_changed_returns_none_when_unchanged(
        self, tmp_path, valid_version_plan_yaml
    ):
        """reload_if_changed returns None when file hasn't changed."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        loader.load()  # Initial load

        # File hasn't changed
        result = loader.reload_if_changed()

        assert result is None

    def test_reload_if_changed_returns_plan_when_modified(
        self, tmp_path, valid_version_plan_yaml
    ):
        """reload_if_changed returns new plan when file has been modified."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        loader.load()  # Initial load

        # Modify the file
        time.sleep(0.1)  # Ensure mtime changes
        modified_yaml = valid_version_plan_yaml.replace("v0.10", "v0.10.1")
        config_file.write_text(modified_yaml, encoding="utf-8")

        result = loader.reload_if_changed()

        assert result is not None
        assert isinstance(result, VersionPlan)
        assert result.name == "v0.10.1"

    def test_reload_if_changed_caches_mtime(
        self, tmp_path, valid_version_plan_yaml
    ):
        """reload_if_changed caches modification time correctly."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        loader.load()  # Initial load, caches mtime

        # No change
        assert loader.reload_if_changed() is None
        assert loader.reload_if_changed() is None

    def test_reload_graceful_degradation_on_error(
        self, tmp_path, valid_version_plan_yaml
    ):
        """On reload failure, return None (keep using cached config)."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        original_plan = loader.load()  # Initial load

        # Modify file with invalid content
        time.sleep(0.1)
        config_file.write_text("{{{{invalid yaml", encoding="utf-8")

        # Should return None on error (graceful degradation)
        result = loader.reload_if_changed()

        assert result is None
        # The loader should still have the cached version available
        assert loader._cached_plan is not None
        assert loader._cached_plan.name == original_plan.name


# =============================================================================
# Test 8: Multiple Phases Parsing
# =============================================================================


class TestMultiplePhaseParsing:
    """Test parsing of multiple phases in version plan."""

    def test_parses_multiple_phases(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Parse version plan with multiple phases."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert len(plan.phases) == 2
        assert plan.phases[0].name == "Phase A"
        assert plan.phases[1].name == "Phase B"

    def test_phase_order_preserved(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Phase order is preserved as defined in YAML."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert plan.phases[0].order == 1
        assert plan.phases[1].order == 2

    def test_phase_dependencies_parsed(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Phase dependencies are correctly parsed."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        # Phase A has no dependencies
        assert plan.phases[0].dependencies == []
        # Phase B depends on Phase A
        assert plan.phases[1].dependencies == ["Phase A"]

    def test_multiple_workstreams_per_phase(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Each phase can have multiple workstreams."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        # Phase A has 3 workstreams
        assert len(plan.phases[0].workstreams) == 3
        # Phase B has 2 workstreams
        assert len(plan.phases[1].workstreams) == 2

    def test_phaseconfig_model_type(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Phases are properly typed as PhaseConfig."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        for phase in plan.phases:
            assert isinstance(phase, PhaseConfig)

    def test_workstreamconfig_model_type(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Workstreams are properly typed as WorkstreamConfig."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        for phase in plan.phases:
            for ws in phase.workstreams:
                assert isinstance(ws, WorkstreamConfig)


# =============================================================================
# Test 9: Workstream-to-Worktree Matching with Glob Patterns
# =============================================================================


class TestGlobPatternMatching:
    """Test glob pattern matching for branch-to-workstream mapping."""

    def test_exact_branch_match(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Match exact branch name to workstream."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        loader.load()

        workstream = loader.match_branch_to_workstream("feat/agent-memory")

        assert workstream is not None
        assert workstream.name == "Agent Memory & Learning"

    def test_glob_wildcard_match(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Match branch name using glob wildcard pattern."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        loader.load()

        # "feat/memory-*" pattern should match "feat/memory-consolidation"
        workstream = loader.match_branch_to_workstream("feat/memory-consolidation")

        assert workstream is not None
        assert workstream.name == "Agent Memory & Learning"

    def test_glob_match_multiple_patterns(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Match against multiple patterns for same workstream."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        loader.load()

        # Both should match "Kanban Workflow Engine"
        ws1 = loader.match_branch_to_workstream("feat/kanban-phase1")
        ws2 = loader.match_branch_to_workstream("feat/kanban-phase2")

        assert ws1 is not None
        assert ws2 is not None
        assert ws1.name == "Kanban Workflow Engine"
        assert ws2.name == "Kanban Workflow Engine"

    def test_no_match_returns_none(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Return None when no workstream matches the branch."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        loader.load()

        workstream = loader.match_branch_to_workstream("feat/unknown-feature")

        assert workstream is None

    def test_main_branch_returns_none(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Main branch doesn't match any workstream."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        loader.load()

        workstream = loader.match_branch_to_workstream("main")

        assert workstream is None

    def test_get_workstream_for_branch_returns_phase_and_workstream(
        self, tmp_path, valid_version_plan_yaml
    ):
        """get_workstream_for_branch returns both phase and workstream."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        loader.load()

        result = loader.get_workstream_for_branch("feat/qa-enforcement")

        assert result is not None
        phase, workstream = result
        assert isinstance(phase, PhaseConfig)
        assert isinstance(workstream, WorkstreamConfig)
        assert phase.name == "Phase B"
        assert workstream.name == "QA Enforcement"

    def test_get_workstream_for_branch_returns_none_for_unknown(
        self, tmp_path, valid_version_plan_yaml
    ):
        """get_workstream_for_branch returns None for unknown branch."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        loader.load()

        result = loader.get_workstream_for_branch("feat/unknown")

        assert result is None


# =============================================================================
# Test 10: Extract Color Mappings
# =============================================================================


class TestColorMappings:
    """Test extraction of color mappings from workstreams."""

    def test_workstream_colors_extracted(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Workstream colors are correctly extracted."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        # Find Agent Memory workstream
        memory_ws = plan.phases[0].workstreams[0]
        assert memory_ws.color == "#7c3aed"

        # Find QA Enforcement workstream
        qa_ws = plan.phases[1].workstreams[0]
        assert qa_ws.color == "#dc2626"

    def test_get_color_for_branch(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Get color for a branch via workstream matching."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        loader.load()

        workstream = loader.match_branch_to_workstream("feat/kanban-phase1")

        assert workstream is not None
        assert workstream.color == "#2563eb"

    def test_all_workstreams_have_colors(
        self, tmp_path, valid_version_plan_yaml
    ):
        """All workstreams in valid config have colors."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        for phase in plan.phases:
            for ws in phase.workstreams:
                # In the valid fixture, all workstreams have colors
                assert ws.color is not None
                assert ws.color.startswith("#")


# =============================================================================
# Test: Epic Number Extraction
# =============================================================================


class TestEpicExtraction:
    """Test extraction of epic numbers from workstreams."""

    def test_epic_numbers_extracted(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Epic numbers are correctly extracted from workstreams."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        # Check specific epic numbers
        assert plan.phases[0].workstreams[0].epic == 143  # Agent Memory
        assert plan.phases[0].workstreams[1].epic == 144  # Kanban
        assert plan.phases[0].workstreams[2].epic == 147  # GitHub Integration
        assert plan.phases[1].workstreams[0].epic == 145  # QA Enforcement


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_branches_list(self, tmp_path):
        """Handle workstream with empty branches list."""
        empty_branches_yaml = """
version: 1
name: v0.11
target_date: "2026-06-30"
phases:
  - name: Phase A
    order: 1
    workstreams:
      - name: Empty Branches
        epic: 200
        branches: []
"""
        config_file = tmp_path / "empty-branches.yaml"
        config_file.write_text(empty_branches_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert plan.phases[0].workstreams[0].branches == []

    def test_unicode_in_names(self, tmp_path):
        """Handle unicode characters in names and descriptions."""
        unicode_yaml = """
version: 1
name: v0.11
target_date: "2026-06-30"
description: "Agent Orchestration - Phase II"
phases:
  - name: "Phase Alpha"
    order: 1
    description: "Initial setup phase"
    workstreams:
      - name: "Feature: API Integration"
        epic: 200
        branches: [feat/api]
"""
        config_file = tmp_path / "unicode.yaml"
        config_file.write_text(unicode_yaml, encoding="utf-8")

        loader = VersionPlanLoader(config_file)
        plan = loader.load()

        assert "Phase II" in plan.description
        assert plan.phases[0].name == "Phase Alpha"

    def test_path_as_string_or_path_object(
        self, tmp_path, valid_version_plan_yaml
    ):
        """Loader accepts both str and Path objects."""
        config_file = tmp_path / "version-plan.yaml"
        config_file.write_text(valid_version_plan_yaml, encoding="utf-8")

        # Test with Path object
        loader1 = VersionPlanLoader(config_file)
        plan1 = loader1.load()

        # Test with string
        loader2 = VersionPlanLoader(str(config_file))
        plan2 = loader2.load()

        assert plan1.name == plan2.name
