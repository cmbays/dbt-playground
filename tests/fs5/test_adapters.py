"""Tests for fs5.adapters module - FS1 and FS3 Event Transformers.

Tests cover:
- FS1 (Memory) event transformation to canonical format
- FS3 (QA) event transformation to canonical format
- Batch transformation
- QA report parsing fallback

Version: v0.10.0
Created: 2026-02-03
"""

import pytest
from datetime import datetime, UTC
from pathlib import Path
import json

from fs5.adapters import (
    transform_fs1_event,
    fs1_batch_transform,
    transform_fs3_event,
    fs3_batch_transform,
    parse_qa_report,
)


class TestFS1Adapter:
    """Tests for FS1 Memory event adapter."""

    def test_transform_basic_event(self):
        """Basic FS1 event transforms to canonical format."""
        fs1_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "event": "session_logged",
            "data": {
                "task": "Implemented feature X",
                "outcome": "SUCCESS",
                "session_id": "abc123",
            },
        }

        result = transform_fs1_event(fs1_event)

        assert result["schema_version"] == "2.0.0"
        assert result["event_type"] == "memory.session_logged"
        assert result["timestamp"] == "2026-02-03T14:30:00Z"
        assert "event_id" in result

    def test_transform_sets_source(self):
        """Transformed event has correct source fields."""
        fs1_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "event": "pattern_detected",
            "data": {},
        }

        result = transform_fs1_event(fs1_event)

        assert result["source"]["type"] == "agent"
        assert result["source"]["identity"] == "sage"
        assert result["source"]["version"] == "0.10.0"

    def test_transform_extracts_correlation_id(self):
        """Correlation ID extracted from data.correlation_id."""
        fs1_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "event": "session_logged",
            "data": {
                "correlation_id": "feat/test-feature",
            },
        }

        result = transform_fs1_event(fs1_event)

        assert result["correlation_id"] == "feat/test-feature"

    def test_transform_falls_back_to_task_id(self):
        """Correlation ID falls back to task_id."""
        fs1_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "event": "session_logged",
            "data": {
                "task_id": "TASK-42",
            },
        }

        result = transform_fs1_event(fs1_event)

        assert result["correlation_id"] == "TASK-42"

    def test_transform_falls_back_to_session_id(self):
        """Correlation ID falls back to session_id."""
        fs1_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "event": "session_logged",
            "data": {
                "session_id": "sess-123",
            },
        }

        result = transform_fs1_event(fs1_event)

        assert result["correlation_id"] == "sess-123"

    def test_transform_unknown_correlation_id(self):
        """Correlation ID defaults to 'unknown' when no IDs present."""
        fs1_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "event": "session_logged",
            "data": {},
        }

        result = transform_fs1_event(fs1_event)

        assert result["correlation_id"] == "unknown"

    def test_transform_preserves_payload(self):
        """Original data preserved in payload."""
        fs1_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "event": "session_logged",
            "data": {
                "task": "My task",
                "outcome": "SUCCESS",
                "patterns": ["TDD", "competitive-impl"],
            },
        }

        result = transform_fs1_event(fs1_event)

        assert result["payload"]["task"] == "My task"
        assert result["payload"]["outcome"] == "SUCCESS"
        assert result["payload"]["patterns"] == ["TDD", "competitive-impl"]

    def test_event_id_is_deterministic(self):
        """Same event produces same event_id."""
        fs1_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "event": "session_logged",
            "data": {"task": "test"},
        }

        result1 = transform_fs1_event(fs1_event)
        result2 = transform_fs1_event(fs1_event)

        assert result1["event_id"] == result2["event_id"]

    def test_event_id_is_uuid_format(self):
        """Event ID is in UUID format."""
        fs1_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "event": "session_logged",
            "data": {},
        }

        result = transform_fs1_event(fs1_event)
        event_id = result["event_id"]

        # UUID format: 8-4-4-4-12
        parts = event_id.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_batch_transform(self):
        """Batch transform processes multiple events."""
        events = [
            {"timestamp": "2026-02-03T14:00:00Z", "event": "e1", "data": {}},
            {"timestamp": "2026-02-03T14:01:00Z", "event": "e2", "data": {}},
            {"timestamp": "2026-02-03T14:02:00Z", "event": "e3", "data": {}},
        ]

        results = fs1_batch_transform(events)

        assert len(results) == 3
        assert results[0]["event_type"] == "memory.e1"
        assert results[1]["event_type"] == "memory.e2"
        assert results[2]["event_type"] == "memory.e3"


class TestFS3Adapter:
    """Tests for FS3 QA event adapter."""

    def test_transform_basic_event(self):
        """Basic FS3 QA event transforms to canonical format."""
        fs3_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "gate": "code_review",
            "status": "PASSED",
            "reviewer": "code-reviewer",
            "evidence": "No critical issues found",
            "session_id": "abc123",
        }

        result = transform_fs3_event(fs3_event)

        assert result["schema_version"] == "2.0.0"
        assert result["event_type"] == "qa.gate_passed"
        assert result["correlation_id"] == "abc123"

    def test_transform_skipped_status(self):
        """SKIPPED status maps to qa.gate_skipped."""
        fs3_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "gate": "security_review",
            "status": "SKIPPED",
            "session_id": "test",
        }

        result = transform_fs3_event(fs3_event)

        assert result["event_type"] == "qa.gate_skipped"

    def test_transform_failed_status(self):
        """FAILED status maps to qa.gate_failed."""
        fs3_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "gate": "unit_tests",
            "status": "FAILED",
            "session_id": "test",
        }

        result = transform_fs3_event(fs3_event)

        assert result["event_type"] == "qa.gate_failed"

    def test_transform_unknown_status(self):
        """Unknown status maps to qa.gate_checked."""
        fs3_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "gate": "custom_gate",
            "status": "PENDING",
            "session_id": "test",
        }

        result = transform_fs3_event(fs3_event)

        assert result["event_type"] == "qa.gate_checked"

    def test_transform_sets_source_from_reviewer(self):
        """Source identity set from reviewer field."""
        fs3_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "gate": "code_review",
            "status": "PASSED",
            "reviewer": "security-reviewer",
            "session_id": "test",
        }

        result = transform_fs3_event(fs3_event)

        assert result["source"]["identity"] == "security-reviewer"

    def test_transform_payload_contains_gate_info(self):
        """Payload contains gate, status, and evidence."""
        fs3_event = {
            "timestamp": "2026-02-03T14:30:00Z",
            "gate": "pre_commit",
            "status": "PASSED",
            "evidence": "All checks passed",
            "session_id": "test",
        }

        result = transform_fs3_event(fs3_event)

        assert result["payload"]["gate"] == "pre_commit"
        assert result["payload"]["status"] == "PASSED"
        assert result["payload"]["evidence"] == "All checks passed"

    def test_batch_transform(self):
        """Batch transform processes multiple QA events."""
        events = [
            {"timestamp": "2026-02-03T14:00:00Z", "gate": "lint", "status": "PASSED", "session_id": "s1"},
            {"timestamp": "2026-02-03T14:01:00Z", "gate": "test", "status": "FAILED", "session_id": "s1"},
        ]

        results = fs3_batch_transform(events)

        assert len(results) == 2
        assert results[0]["event_type"] == "qa.gate_passed"
        assert results[1]["event_type"] == "qa.gate_failed"


class TestQAReportParser:
    """Tests for QA report markdown parsing."""

    def test_parse_qa_report_with_passed_gates(self, tmp_path):
        """Parse QA report with passed gates."""
        report_path = tmp_path / "QA_REPORT.md"
        report_path.write_text("""
# QA Report

## Gates

- [x] Code Review: PASSED
- [x] Unit Tests: PASSED
- [ ] Security Review: PENDING
""", encoding="utf-8")

        results = parse_qa_report(str(report_path))

        assert len(results) == 3

        # Find passed gates
        passed = [r for r in results if r["event_type"] == "qa.gate_passed"]
        assert len(passed) == 2

    def test_parse_qa_report_with_skipped_gates(self, tmp_path):
        """Parse QA report with skipped gates."""
        report_path = tmp_path / "QA_REPORT.md"
        report_path.write_text("""
# QA Report

- [~] Performance Tests: SKIPPED
- [x] Lint: PASSED
""", encoding="utf-8")

        results = parse_qa_report(str(report_path))

        skipped = [r for r in results if r["event_type"] == "qa.gate_skipped"]
        assert len(skipped) == 1

    def test_parse_qa_report_nonexistent_file(self):
        """Parse returns empty list for nonexistent file."""
        results = parse_qa_report("/nonexistent/path/QA_REPORT.md")

        assert results == []

    def test_parse_qa_report_normalizes_gate_names(self, tmp_path):
        """Gate names are normalized (lowercase, underscores)."""
        report_path = tmp_path / "QA_REPORT.md"
        report_path.write_text("""
- [x] Code Review: PASSED
- [x] Unit Tests: PASSED
""", encoding="utf-8")

        results = parse_qa_report(str(report_path))

        gate_names = [r["payload"]["gate"] for r in results]
        assert "code_review" in gate_names
        assert "unit_tests" in gate_names

    def test_parse_qa_report_sets_evidence(self, tmp_path):
        """Parsed events have evidence indicating source."""
        report_path = tmp_path / "QA_REPORT.md"
        report_path.write_text("- [x] Lint: PASSED\n", encoding="utf-8")

        results = parse_qa_report(str(report_path))

        assert results[0]["payload"]["evidence"] == f"Parsed from {report_path}"


class TestEventIdGeneration:
    """Tests for deterministic event ID generation."""

    def test_different_events_have_different_ids(self):
        """Different events produce different event IDs."""
        event1 = {"timestamp": "2026-02-03T14:00:00Z", "event": "e1", "data": {}}
        event2 = {"timestamp": "2026-02-03T14:01:00Z", "event": "e1", "data": {}}

        result1 = transform_fs1_event(event1)
        result2 = transform_fs1_event(event2)

        assert result1["event_id"] != result2["event_id"]

    def test_same_event_same_id(self):
        """Identical events produce identical event IDs."""
        event = {"timestamp": "2026-02-03T14:00:00Z", "event": "test", "data": {"key": "value"}}

        result1 = transform_fs1_event(event)
        result2 = transform_fs1_event(event)

        assert result1["event_id"] == result2["event_id"]
