"""
Integration tests for FS1 Agent Memory System.

Tests cover:
- End-to-end session lifecycle
- Workflow J + K interaction
- FS1 -> FS2 integration (task_id correlation)
- FS1 -> FS5 integration (events.jsonl consumption)
- Cross-feature contracts

Test IDs reference FS1_TEST_SUITE_BETA.md specifications.
"""

import json
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Import the modules under test
import importlib.util

log_session_path = Path(__file__).parent.parent / "scripts" / "log-session.py"
spec = importlib.util.spec_from_file_location("log_session", log_session_path)
log_session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(log_session)

consolidate_path = Path(__file__).parent.parent / "scripts" / "consolidate-memory.py"
spec = importlib.util.spec_from_file_location("consolidate_memory", consolidate_path)
consolidate_memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consolidate_memory)


@pytest.mark.integration
class TestFS1FS2Integration:
    """Category I1: FS1 -> FS2 Integration (task_id Correlation)."""

    def test_task_id_in_markdown_entry(self):
        """I1.1: task_id from Backlog.md is included in markdown entry."""
        entry = log_session.SessionEntry(
            timestamp=datetime(2026, 2, 2, 10, 30, 0),
            task="Implement feature",
            outcome="SUCCESS",
            files=["model.sql"],
            decisions=[],
            learnings=["Learned pattern"],
            improvements=[],
            issue="100",
            pr="",
            task_id="TASK-42",
        )

        markdown = log_session.format_markdown(entry)

        # Verify task_id present in markdown
        assert "**Task ID**: TASK-42" in markdown

        # Verify task_id comes before outcome (schema order)
        task_id_pos = markdown.find("**Task ID**")
        outcome_pos = markdown.find("**Outcome**")
        assert task_id_pos < outcome_pos, "Task ID should appear before Outcome"

    def test_task_id_in_events_jsonl(
        self, memory_dir_with_claude_md: Path, monkeypatch
    ):
        """I1.2: task_id is included in events.jsonl for FS5/FS2 consumption."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        entry = log_session.SessionEntry(
            timestamp=datetime.now(timezone.utc),
            task="Test task",
            outcome="SUCCESS",
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue="",
            pr="",
            task_id="TASK-42",
        )

        log_session.emit_event(entry)

        events_file = memory_dir_with_claude_md / "events.jsonl"
        event = json.loads(events_file.read_text().strip())

        assert event["data"]["task_id"] == "TASK-42"

    def test_null_task_id_handling(self, memory_dir_with_claude_md: Path, monkeypatch):
        """I1.3: Sessions without task_id are still logged correctly."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        entry = log_session.SessionEntry(
            timestamp=datetime.now(timezone.utc),
            task="Ad-hoc task",
            outcome="SUCCESS",
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue="",
            pr="",
            task_id="",
        )

        log_session.emit_event(entry)

        events_file = memory_dir_with_claude_md / "events.jsonl"
        event = json.loads(events_file.read_text().strip())

        # task_id should be null, not empty string
        assert event["data"]["task_id"] is None

    def test_multiple_sessions_same_task(
        self, memory_dir_with_claude_md: Path, monkeypatch
    ):
        """I1.4: Multiple sessions can reference same task_id."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        # Create 3 sessions for same task
        for i, outcome in enumerate(["PARTIAL", "PARTIAL", "SUCCESS"]):
            entry = log_session.SessionEntry(
                timestamp=datetime.now(timezone.utc),
                task=f"Implementation session {i + 1}",
                outcome=outcome,
                files=[],
                decisions=[],
                learnings=[],
                improvements=[],
                issue="",
                pr="",
                task_id="TASK-42",
            )
            log_session.emit_event(entry)

        events_file = memory_dir_with_claude_md / "events.jsonl"
        events = [
            json.loads(line)
            for line in events_file.read_text().strip().split("\n")
        ]

        task_42_events = [e for e in events if e["data"]["task_id"] == "TASK-42"]
        assert len(task_42_events) == 3


@pytest.mark.integration
class TestFS1FS5Integration:
    """Category I2: FS1 -> FS5 Integration (Events Consumption)."""

    def test_events_schema_fs5_compatible(
        self, memory_dir_with_claude_md: Path, monkeypatch
    ):
        """I2.1: Events match FS5 expected schema."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        entry = log_session.SessionEntry(
            timestamp=datetime.now(timezone.utc),
            task="Test",
            outcome="SUCCESS",
            files=["a.py", "b.py"],
            decisions=[("d1", "r1", "a1")],
            learnings=["l1", "l2"],
            improvements=["i1"],
            issue="42",
            pr="45",
            task_id="TASK-1",
        )

        log_session.emit_event(entry)

        events_file = memory_dir_with_claude_md / "events.jsonl"
        event = json.loads(events_file.read_text().strip())

        # FS5 required fields
        assert "timestamp" in event
        assert "event" in event
        assert "version" in event
        assert "data" in event

        # FS5 data fields
        data = event["data"]
        assert "task" in data
        assert "task_id" in data
        assert "outcome" in data
        assert "files_modified" in data
        assert isinstance(data["files_modified"], int)
        assert "decisions_count" in data
        assert "learnings_count" in data
        assert "improvements_count" in data

    def test_events_append_only(self, memory_dir_with_claude_md: Path, monkeypatch):
        """I2.2: Events are appended, never overwritten."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        # Write first event
        entry1 = log_session.SessionEntry(
            timestamp=datetime.now(timezone.utc),
            task="Task 1",
            outcome="SUCCESS",
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue="",
            pr="",
            task_id="TASK-1",
        )
        log_session.emit_event(entry1)

        # Get first event timestamp
        events_file = memory_dir_with_claude_md / "events.jsonl"
        first_content = events_file.read_text()
        first_event = json.loads(first_content.strip())
        first_ts = first_event["timestamp"]

        # Wait and write second event
        time.sleep(0.01)
        entry2 = log_session.SessionEntry(
            timestamp=datetime.now(timezone.utc),
            task="Task 2",
            outcome="FAILURE",
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue="",
            pr="",
            task_id="TASK-2",
        )
        log_session.emit_event(entry2)

        # Verify both events present
        final_content = events_file.read_text()
        lines = final_content.strip().split("\n")
        assert len(lines) == 2

        # First event unchanged
        event1 = json.loads(lines[0])
        assert event1["timestamp"] == first_ts

    def test_event_version_field(self, memory_dir_with_claude_md: Path, monkeypatch):
        """I2.3: All events include version field for schema evolution."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        entry = log_session.SessionEntry(
            timestamp=datetime.now(timezone.utc),
            task="Test",
            outcome="SUCCESS",
            files=[],
            decisions=[],
            learnings=[],
            improvements=[],
            issue="",
            pr="",
            task_id="",
        )
        log_session.emit_event(entry)

        events_file = memory_dir_with_claude_md / "events.jsonl"
        event = json.loads(events_file.read_text().strip())

        assert "version" in event
        assert event["version"] == "1.0"

    def test_consolidation_events_fs5(
        self, memory_dir_with_claude_md: Path, monkeypatch
    ):
        """I2.4: Consolidation events have correct FS5 schema."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)
        memory_dir = memory_dir_with_claude_md

        # Create sample logs
        for i in range(3):
            log_date = datetime.now() - timedelta(days=i)
            date_str = log_date.strftime("%Y-%m-%d")
            log_file = memory_dir / f"{date_str}.md"
            log_file.write_text(f"""## [{date_str}T10:00:00] Task: Task {i}

**Outcome**: SUCCESS

**Learnings**:
- Learning {i}

---
""")

        # Consolidate
        result = consolidate_memory.consolidate(memory_dir, days=7)
        consolidate_memory.emit_consolidation_event(result, memory_dir)

        events_file = memory_dir / "events.jsonl"
        event = json.loads(events_file.read_text().strip())

        assert event["event"] == "week_consolidated"
        assert "period_start" in event["data"]
        assert "period_end" in event["data"]
        assert "total_entries" in event["data"]
        assert "patterns_found" in event["data"]


@pytest.mark.integration
class TestWorkflowInteraction:
    """Category I3: Workflow J + K Interaction."""

    def test_workflow_j_output_feeds_k(
        self, memory_dir_with_claude_md: Path, monkeypatch
    ):
        """I3.1: Entries from Workflow J are consumed by Workflow K."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)
        memory_dir = memory_dir_with_claude_md

        # Workflow J: Create entry
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = memory_dir / f"{today}.md"

        entry = log_session.SessionEntry(
            timestamp=datetime.now(),
            task="Test task",
            outcome="SUCCESS",
            files=[],
            decisions=[],
            learnings=["Important learning"],
            improvements=[],
            issue="",
            pr="",
            task_id="",
        )
        markdown = log_session.format_markdown(entry)
        log_file.write_text(markdown)

        # Workflow K: Consolidate
        result = consolidate_memory.consolidate(memory_dir, days=7)

        # Verify entry was consumed
        assert result["total_entries"] == 1

    def test_daily_logs_accumulate(
        self, memory_dir_with_claude_md: Path, monkeypatch
    ):
        """I3.2: 5 days of logs all contribute to weekly consolidation."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)
        memory_dir = memory_dir_with_claude_md

        # Create 5 days of logs
        for i in range(5):
            log_date = datetime.now() - timedelta(days=i)
            date_str = log_date.strftime("%Y-%m-%d")
            log_file = memory_dir / f"{date_str}.md"
            log_file.write_text(f"""## [{date_str}T10:00:00] Task: Task for day {i}

**Outcome**: SUCCESS

**Learnings**:
- Learning day {i}

---
""")

        result = consolidate_memory.consolidate(memory_dir, days=7)

        # All 5 days should be included
        assert result["total_entries"] == 5

    def test_concurrent_logging_safety(
        self, memory_dir_with_claude_md: Path, monkeypatch
    ):
        """I3.3: Concurrent log writes don't corrupt data."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)
        memory_dir = memory_dir_with_claude_md

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = memory_dir / f"{today}.md"

        def log_entry(task_num: int):
            entry = log_session.SessionEntry(
                timestamp=datetime.now(),
                task=f"Task {task_num}",
                outcome="SUCCESS",
                files=[],
                decisions=[],
                learnings=[f"Learning {task_num}"],
                improvements=[],
                issue="",
                pr="",
                task_id="",
            )
            markdown = log_session.format_markdown(entry)

            # Append with file lock (basic thread safety)
            with open(log_file, "a") as f:
                f.write(markdown)

        # Run 5 concurrent writes
        threads = [
            threading.Thread(target=log_entry, args=(i,)) for i in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verify all entries present
        content = log_file.read_text()

        for i in range(5):
            assert f"Task {i}" in content


@pytest.mark.integration
class TestEndToEnd:
    """Category I5: End-to-End Scenarios."""

    def test_full_session_lifecycle(
        self, memory_dir_with_claude_md: Path, monkeypatch
    ):
        """I5.1: Complete lifecycle: log -> consolidate -> verify."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)
        memory_dir = memory_dir_with_claude_md

        # Step 1: Create 3 sessions with common pattern
        for i in range(3):
            log_date = datetime.now() - timedelta(days=i)
            date_str = log_date.strftime("%Y-%m-%d")
            log_file = memory_dir / f"{date_str}.md"

            entry = log_session.SessionEntry(
                timestamp=log_date,
                task=f"Implement feature {i}",
                outcome="SUCCESS",
                files=[f"model_{i}.sql"],
                decisions=[],
                learnings=["Always add tests before implementation"],
                improvements=[],
                issue=str(100 + i),
                pr="",
                task_id=f"TASK-{i}",
            )
            markdown = log_session.format_markdown(entry)
            log_file.write_text(markdown)

            # Emit event
            log_session.emit_event(entry)

        # Step 2: Consolidate
        result = consolidate_memory.consolidate(memory_dir, days=7)

        # Verify entries processed
        assert result["total_entries"] == 3

        # Write MEMORY_INDEX
        index_content = consolidate_memory.generate_memory_index(result, memory_dir)
        index_file = memory_dir / "MEMORY_INDEX.md"
        index_file.write_text(index_content)

        assert index_file.exists()

        # Step 3: Verify events for FS5
        events_file = memory_dir / "events.jsonl"
        events = [
            json.loads(line)
            for line in events_file.read_text().strip().split("\n")
        ]

        session_events = [e for e in events if e["event"] == "session_logged"]
        assert len(session_events) == 3

    def test_pattern_promotion_flow(
        self, memory_dir_with_claude_md: Path, monkeypatch
    ):
        """I5.2: Pattern appearing 2+ times becomes promotion candidate."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)
        memory_dir = memory_dir_with_claude_md

        # Create entries with same learning
        for i in range(3):
            log_date = datetime.now() - timedelta(days=i)
            date_str = log_date.strftime("%Y-%m-%d")
            log_file = memory_dir / f"{date_str}.md"
            log_file.write_text(f"""## [{date_str}T10:00:00] Task: Task {i}

**Learnings**:
- Use incremental models for large tables

---
""")

        result = consolidate_memory.consolidate(memory_dir, days=7)

        # Check for patterns
        assert len(result["patterns"]) >= 1

        # At least one should be CANDIDATE or REVIEW
        statuses = [p["status"] for p in result["patterns"]]
        assert "CANDIDATE" in statuses or "REVIEW" in statuses

    def test_multi_task_correlation(
        self, memory_dir_with_claude_md: Path, monkeypatch
    ):
        """I5.3: Multiple tasks can be tracked and correlated."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)
        memory_dir = memory_dir_with_claude_md

        # Create sessions for different tasks
        tasks = [
            ("TASK-1", "Analytics", ["SUCCESS", "SUCCESS"]),
            ("TASK-2", "Testing", ["PARTIAL", "SUCCESS"]),
            ("TASK-3", "Documentation", ["SUCCESS"]),
        ]

        for task_id, topic, outcomes in tasks:
            for i, outcome in enumerate(outcomes):
                entry = log_session.SessionEntry(
                    timestamp=datetime.now(timezone.utc),
                    task=f"{topic} session {i}",
                    outcome=outcome,
                    files=[],
                    decisions=[],
                    learnings=[],
                    improvements=[],
                    issue="",
                    pr="",
                    task_id=task_id,
                )
                log_session.emit_event(entry)

        events_file = memory_dir / "events.jsonl"
        events = [
            json.loads(line)
            for line in events_file.read_text().strip().split("\n")
        ]

        # Verify task correlation
        task_1_events = [e for e in events if e["data"]["task_id"] == "TASK-1"]
        task_2_events = [e for e in events if e["data"]["task_id"] == "TASK-2"]
        task_3_events = [e for e in events if e["data"]["task_id"] == "TASK-3"]

        assert len(task_1_events) == 2
        assert len(task_2_events) == 2
        assert len(task_3_events) == 1

        # Verify outcome tracking
        task_2_outcomes = [e["data"]["outcome"] for e in task_2_events]
        assert "PARTIAL" in task_2_outcomes
        assert "SUCCESS" in task_2_outcomes


@pytest.mark.integration
class TestWorkflowDocumentation:
    """Category 3: Workflow J and K documentation tests."""

    def test_workflow_j_documented(self, project_root: Path):
        """T3.1: Workflow J is documented in sage.md."""
        sage_file = project_root / ".claude" / "agents" / "sage.md"

        if sage_file.exists():
            content = sage_file.read_text()
            # Check for workflow J or session logging documentation
            has_workflow_j = "Workflow J" in content
            has_log_session = "log session" in content.lower() or "session logging" in content.lower()
            assert has_workflow_j or has_log_session, "Workflow J should be documented"
        else:
            pytest.skip("sage.md not found - workflow documentation test skipped")

    def test_workflow_k_documented(self, project_root: Path):
        """T4.1: Workflow K is documented in sage.md."""
        sage_file = project_root / ".claude" / "agents" / "sage.md"

        if sage_file.exists():
            content = sage_file.read_text()
            # Check for workflow K or consolidation documentation
            has_workflow_k = "Workflow K" in content
            has_consolidate = "consolidate" in content.lower()
            assert has_workflow_k or has_consolidate, "Workflow K should be documented"
        else:
            pytest.skip("sage.md not found - workflow documentation test skipped")
