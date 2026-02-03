"""
Unit tests for scripts/consolidate-memory.py

Tests cover:
- Log file parsing
- Pattern detection algorithm
- Keyword extraction and overlap
- Pattern scoring (multi-factor)
- MEMORY_INDEX.md generation
- Event emission for consolidation

Test IDs reference FS1_TEST_SUITE_ALPHA.md and FS1_TEST_SUITE_BETA.md specifications.
"""

# Import the module under test
import importlib.util
import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

script_path = Path(__file__).parent.parent / 'scripts' / 'consolidate-memory.py'
spec = importlib.util.spec_from_file_location('consolidate_memory', script_path)
consolidate_memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consolidate_memory)


class TestNormalization:
    """Tests for text normalization and keyword extraction."""

    def test_normalize_basic_text(self):
        """Normalize extracts keywords from text."""
        text = 'Use incremental models for performance'
        keywords = consolidate_memory.normalize(text)

        assert 'incremental' in keywords
        assert 'models' in keywords
        assert 'performance' in keywords
        # Stop words should be excluded
        assert 'use' not in keywords
        assert 'for' not in keywords

    def test_normalize_filters_short_words(self):
        """Words <= 2 characters are excluded."""
        # The normalize function filters words <= 2 chars AND stop words
        # "not" is 3 chars but is a stop word, so use "nothing" which is not a stop word
        text = 'the nothing matters anymore'
        keywords = consolidate_memory.normalize(text)

        # "nothing" is in stop words, "matters" and "anymore" should pass
        assert 'matters' in keywords
        assert 'anymore' in keywords
        # Short words and stop words excluded
        assert 'the' not in keywords

    def test_normalize_handles_empty_string(self):
        """Empty string returns empty set."""
        keywords = consolidate_memory.normalize('')
        assert keywords == set()

    def test_normalize_handles_only_stop_words(self):
        """Text with only stop words returns empty set."""
        text = 'the a an is are was were'
        keywords = consolidate_memory.normalize(text)
        assert keywords == set()


class TestKeywordOverlap:
    """Tests for keyword overlap calculation (T4.5)."""

    def test_keyword_overlap_high_similarity(self):
        """T4.5: Similar texts have high overlap."""
        text1 = 'Use incremental models for performance'
        text2 = 'Incremental models improve performance'

        kw1 = consolidate_memory.normalize(text1)
        kw2 = consolidate_memory.normalize(text2)

        overlap = consolidate_memory.keyword_overlap(kw1, kw2)
        assert overlap > 0.5, 'Similar texts should have >50% overlap'

    def test_keyword_overlap_low_similarity(self):
        """Different texts have low overlap."""
        text1 = 'Use incremental models for performance'
        text2 = 'Something completely different'

        kw1 = consolidate_memory.normalize(text1)
        kw2 = consolidate_memory.normalize(text2)

        overlap = consolidate_memory.keyword_overlap(kw1, kw2)
        assert overlap < 0.5, 'Different texts should have <50% overlap'

    def test_keyword_overlap_empty_sets(self):
        """Empty sets return 0.0 overlap."""
        assert consolidate_memory.keyword_overlap(set(), set()) == 0.0
        assert consolidate_memory.keyword_overlap({'a', 'b'}, set()) == 0.0
        assert consolidate_memory.keyword_overlap(set(), {'a', 'b'}) == 0.0

    def test_keyword_overlap_identical_sets(self):
        """Identical sets return 1.0 overlap."""
        kw = {'incremental', 'models', 'performance'}
        assert consolidate_memory.keyword_overlap(kw, kw) == 1.0


class TestLogParsing:
    """Tests for markdown log file parsing."""

    def test_parse_log_file_basic(self, memory_dir: Path):
        """Parse extracts entries from log file."""
        log_file = memory_dir / '2026-02-02.md'
        log_file.write_text("""## [2026-02-02T10:00:00] Task: Test task

**Task ID**: TASK-1
**Outcome**: SUCCESS
**Files Modified**: 2

**Key Decisions**:
- Decision 1: Rationale (affects: component)

**Learnings**:
- Learning 1
- Learning 2

**Would Do Differently**:
- Improvement 1

---
""")

        entries = consolidate_memory.parse_log_file(log_file)

        assert len(entries) == 1
        entry = entries[0]
        assert entry['task'] == 'Test task'
        assert entry['task_id'] == 'TASK-1'
        assert entry['outcome'] == 'SUCCESS'
        assert 'Learning 1' in entry['learnings']
        assert 'Learning 2' in entry['learnings']
        assert 'Decision 1: Rationale (affects: component)' in entry['decisions']
        assert 'Improvement 1' in entry['improvements']

    def test_parse_log_file_multiple_entries(self, memory_dir: Path):
        """Parse handles multiple entries in one file."""
        log_file = memory_dir / '2026-02-02.md'
        log_file.write_text("""## [2026-02-02T10:00:00] Task: Task 1

**Outcome**: SUCCESS

**Learnings**:
- Learning A

---

## [2026-02-02T11:00:00] Task: Task 2

**Outcome**: FAILURE

**Learnings**:
- Learning B

---
""")

        entries = consolidate_memory.parse_log_file(log_file)

        assert len(entries) == 2
        assert entries[0]['task'] == 'Task 1'
        assert entries[1]['task'] == 'Task 2'
        assert entries[0]['outcome'] == 'SUCCESS'
        assert entries[1]['outcome'] == 'FAILURE'

    def test_parse_log_file_filters_none_documented(self, memory_dir: Path):
        """Parse filters out 'None documented' placeholders."""
        log_file = memory_dir / '2026-02-02.md'
        log_file.write_text("""## [2026-02-02T10:00:00] Task: Test task

**Outcome**: SUCCESS

**Learnings**:
- None documented

**Key Decisions**:
- None documented

---
""")

        entries = consolidate_memory.parse_log_file(log_file)

        assert len(entries) == 1
        assert entries[0].get('learnings', []) == []
        assert entries[0].get('decisions', []) == []


class TestPatternGrouping:
    """Tests for grouping similar items (T4.4)."""

    def test_group_similar_detects_patterns(self):
        """T4.4: Patterns detected when appearing 2+ times."""
        today = date.today()

        items = [
            consolidate_memory.TextItem(
                today, 'learning', 'Always validate input before processing', 'Task 1'
            ),
            consolidate_memory.TextItem(
                today, 'learning', 'Validate input before you process it', 'Task 2'
            ),
            consolidate_memory.TextItem(today, 'learning', 'Something completely unique', 'Task 3'),
        ]

        groups = consolidate_memory.group_similar(items, threshold=0.5)

        # Should find one group for the similar items
        pattern_groups = [g for g in groups if g.count >= 2]
        assert len(pattern_groups) >= 1

        # The unique item should not form a group
        unique_in_group = any(
            'unique' in item.text.lower() for g in groups for item in g.items if g.count >= 2
        )
        assert not unique_in_group

    def test_group_similar_respects_threshold(self):
        """Grouping respects the overlap threshold."""
        today = date.today()

        items = [
            consolidate_memory.TextItem(today, 'learning', 'Use incremental models', 'Task 1'),
            consolidate_memory.TextItem(today, 'learning', 'Incremental model usage', 'Task 2'),
        ]

        # High threshold - may not group
        groups_high = consolidate_memory.group_similar(items, threshold=0.9)
        groups_high_count = sum(1 for g in groups_high if g.count >= 2)

        # Low threshold - should group
        groups_low = consolidate_memory.group_similar(items, threshold=0.3)
        groups_low_count = sum(1 for g in groups_low if g.count >= 2)

        # Lower threshold should find more groups
        assert groups_low_count >= groups_high_count

    def test_group_similar_groups_by_category(self):
        """Items are only grouped within their category."""
        today = date.today()

        items = [
            consolidate_memory.TextItem(today, 'learning', 'Validate input first', 'Task 1'),
            consolidate_memory.TextItem(today, 'learning', 'Validate input always', 'Task 2'),
            consolidate_memory.TextItem(today, 'decision', 'Validate input first', 'Task 3'),
        ]

        groups = consolidate_memory.group_similar(items, threshold=0.5)

        # Learning group should only contain learnings
        for group in groups:
            if group.count >= 2:
                assert all(item.category == group.category for item in group.items)

    def test_group_similar_empty_input(self):
        """Empty input returns empty groups."""
        groups = consolidate_memory.group_similar([])
        assert groups == []


class TestPatternScoring:
    """Tests for pattern scoring algorithm."""

    def test_score_pattern_basic(self):
        """Patterns with 2+ occurrences get non-zero score."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        group = consolidate_memory.PatternGroup(
            category='learning',
            items=[
                consolidate_memory.TextItem(today, 'learning', 'Pattern text', 'Task 1'),
                consolidate_memory.TextItem(yesterday, 'learning', 'Pattern text', 'Task 2'),
            ],
        )

        score = consolidate_memory.score_pattern(group, today)
        assert score > 0

    def test_score_pattern_single_item(self):
        """Single-item patterns score 0."""
        today = date.today()

        group = consolidate_memory.PatternGroup(
            category='learning',
            items=[
                consolidate_memory.TextItem(today, 'learning', 'Single item', 'Task 1'),
            ],
        )

        score = consolidate_memory.score_pattern(group, today)
        assert score == 0.0

    def test_score_pattern_recency_factor(self):
        """Recent patterns score higher than old ones."""
        today = date.today()

        # Recent pattern
        recent_group = consolidate_memory.PatternGroup(
            category='learning',
            items=[
                consolidate_memory.TextItem(today, 'learning', 'Recent', 'Task 1'),
                consolidate_memory.TextItem(
                    today - timedelta(days=1), 'learning', 'Recent', 'Task 2'
                ),
            ],
        )

        # Old pattern
        old_group = consolidate_memory.PatternGroup(
            category='learning',
            items=[
                consolidate_memory.TextItem(
                    today - timedelta(days=10), 'learning', 'Old', 'Task 1'
                ),
                consolidate_memory.TextItem(
                    today - timedelta(days=12), 'learning', 'Old', 'Task 2'
                ),
            ],
        )

        recent_score = consolidate_memory.score_pattern(recent_group, today)
        old_score = consolidate_memory.score_pattern(old_group, today)

        assert recent_score > old_score

    def test_score_pattern_frequency_factor(self):
        """More frequent patterns score higher."""
        today = date.today()

        # 3 occurrences
        frequent = consolidate_memory.PatternGroup(
            category='learning',
            items=[
                consolidate_memory.TextItem(today, 'learning', 'Frequent', f'Task {i}')
                for i in range(3)
            ],
        )

        # 2 occurrences
        less_frequent = consolidate_memory.PatternGroup(
            category='learning',
            items=[
                consolidate_memory.TextItem(today, 'learning', 'Less frequent', f'Task {i}')
                for i in range(2)
            ],
        )

        freq_score = consolidate_memory.score_pattern(frequent, today)
        less_score = consolidate_memory.score_pattern(less_frequent, today)

        assert freq_score > less_score


class TestStatusDetermination:
    """Tests for promotion status determination."""

    def test_determine_status_candidate_high_score(self):
        """High-scoring patterns are CANDIDATE."""
        group = consolidate_memory.PatternGroup(category='learning')
        group.score = 0.8

        status = consolidate_memory.determine_status(group)
        assert status == 'CANDIDATE'

    def test_determine_status_review_medium_score(self):
        """Medium-scoring patterns are REVIEW."""
        group = consolidate_memory.PatternGroup(category='learning')
        group.score = 0.5

        status = consolidate_memory.determine_status(group)
        assert status == 'REVIEW'

    def test_determine_status_candidate_high_count(self):
        """Patterns with 3+ occurrences are CANDIDATE."""
        today = date.today()
        group = consolidate_memory.PatternGroup(
            category='learning',
            items=[
                consolidate_memory.TextItem(today, 'learning', 'Pattern', f'Task {i}')
                for i in range(3)
            ],
        )
        group.score = 0.3  # Low score but high count

        status = consolidate_memory.determine_status(group)
        assert status == 'CANDIDATE'


class TestConsolidation:
    """Tests for main consolidation function."""

    def test_consolidate_reads_log_files(self, multi_day_logs: list[Path]):
        """Consolidation reads all log files in date range."""
        memory_dir = multi_day_logs[0].parent

        result = consolidate_memory.consolidate(memory_dir, days=7)

        assert result['total_entries'] == 5
        assert 'period_start' in result
        assert 'period_end' in result

    def test_consolidate_detects_patterns(self, logs_with_recurring_pattern: list[Path]):
        """T4.4: Consolidation detects recurring patterns."""
        memory_dir = logs_with_recurring_pattern[0].parent

        result = consolidate_memory.consolidate(memory_dir, days=7)

        # Should find the recurring pattern
        assert len(result['patterns']) > 0

        # Find patterns with 2+ occurrences
        recurring = [p for p in result['patterns'] if p['count'] >= 2]
        assert len(recurring) > 0

    def test_consolidate_builds_topics_index(self, multi_day_logs: list[Path]):
        """Consolidation builds topic index."""
        memory_dir = multi_day_logs[0].parent

        result = consolidate_memory.consolidate(memory_dir, days=7)

        assert 'topics_index' in result
        assert len(result['topics_index']) > 0

    def test_consolidate_tracks_failures(self, memory_dir: Path):
        """Consolidation tracks failed experiments."""
        today = datetime.now(UTC).strftime('%Y-%m-%d')
        log_file = memory_dir / f'{today}.md'
        log_file.write_text("""## [2026-02-02T10:00:00] Task: Failed experiment

**Outcome**: FAILURE

**Learnings**:
- Learned from failure

---
""")

        result = consolidate_memory.consolidate(memory_dir, days=7)

        assert len(result['failed_experiments']) == 1
        assert result['failed_experiments'][0]['task'] == 'Failed experiment'

    def test_consolidate_respects_date_range(self, memory_dir: Path):
        """Consolidation only includes entries in date range."""
        # Create old entry (15 days ago)
        old_date = (datetime.now(UTC) - timedelta(days=15)).strftime('%Y-%m-%d')
        old_file = memory_dir / f'{old_date}.md'
        old_file.write_text("""## [2026-01-18T10:00:00] Task: Old task

**Learnings**:
- Old learning

---
""")

        # Create recent entry
        recent_date = (datetime.now(UTC) - timedelta(days=2)).strftime('%Y-%m-%d')
        recent_file = memory_dir / f'{recent_date}.md'
        recent_file.write_text("""## [2026-01-31T10:00:00] Task: Recent task

**Learnings**:
- Recent learning

---
""")

        result = consolidate_memory.consolidate(memory_dir, days=7)

        # Only recent entry should be included
        assert result['total_entries'] == 1


class TestMemoryIndexGeneration:
    """Tests for MEMORY_INDEX.md generation."""

    def test_generate_memory_index_basic(self, memory_dir: Path):
        """Index is generated with basic structure."""
        result = {
            'period_start': '2026-01-26',
            'period_end': '2026-02-02',
            'total_entries': 5,
            'patterns': [],
            'promotion_candidates': [],
            'topics_index': {'incremental': 3, 'models': 2},
            'failed_experiments': [],
            'daily_summary': [],
        }

        content = consolidate_memory.generate_memory_index(result)

        assert '# Memory Index' in content
        assert '**Period**: 2026-01-26 to 2026-02-02' in content
        assert '**Total Entries**: 5' in content

    def test_generate_memory_index_with_patterns(self, memory_dir: Path):
        """Index includes pattern information."""
        result = {
            'period_start': '2026-01-26',
            'period_end': '2026-02-02',
            'total_entries': 5,
            'patterns': [
                {
                    'category': 'learning',
                    'summary': 'Use incremental models',
                    'count': 3,
                    'dates': ['2026-02-01', '2026-02-02'],
                    'score': 0.75,
                    'status': 'CANDIDATE',
                }
            ],
            'promotion_candidates': ['Use incremental models'],
            'topics_index': {},
            'failed_experiments': [],
            'daily_summary': [],
        }

        content = consolidate_memory.generate_memory_index(result)

        assert 'Use incremental models' in content
        assert 'CANDIDATE' in content
        assert 'Pattern 1' in content


class TestEventEmission:
    """Tests for consolidation event emission (GAP-5)."""

    def test_emit_consolidation_event(self, memory_dir: Path):
        """T4.6: Consolidation emits week_consolidated event."""
        result = {
            'period_start': '2026-01-26',
            'period_end': '2026-02-02',
            'total_entries': 5,
            'patterns': [{'status': 'CANDIDATE'}, {'status': 'REVIEW'}],
        }

        consolidate_memory.emit_consolidation_event(result, memory_dir)

        events_file = memory_dir / 'events.jsonl'
        assert events_file.exists()

        event = json.loads(events_file.read_text().strip())
        assert event['event'] == 'week_consolidated'
        assert event['version'] == '1.0'
        assert event['data']['period_start'] == '2026-01-26'
        assert event['data']['period_end'] == '2026-02-02'
        assert event['data']['total_entries'] == 5
        assert event['data']['patterns_found'] == 2
        assert event['data']['patterns_promoted'] == 1  # Only CANDIDATE

    def test_emit_consolidation_event_appends(self, memory_dir: Path):
        """Events are appended to existing file."""
        # Create existing event
        events_file = memory_dir / 'events.jsonl'
        events_file.write_text('{"event": "existing"}\n')

        result = {
            'period_start': '2026-01-26',
            'period_end': '2026-02-02',
            'total_entries': 5,
            'patterns': [],
        }

        consolidate_memory.emit_consolidation_event(result, memory_dir)

        lines = events_file.read_text().strip().split('\n')
        assert len(lines) == 2


class TestTextItem:
    """Tests for TextItem dataclass."""

    def test_text_item_creation(self):
        """TextItem can be created with all fields."""
        today = date.today()
        item = consolidate_memory.TextItem(
            entry_date=today,
            category='learning',
            text='Test text',
            source_task='Task 1',
        )

        assert item.entry_date == today
        assert item.category == 'learning'
        assert item.text == 'Test text'
        assert item.source_task == 'Task 1'


class TestPatternGroup:
    """Tests for PatternGroup dataclass."""

    def test_pattern_group_count(self):
        """PatternGroup count property works."""
        today = date.today()
        group = consolidate_memory.PatternGroup(
            category='learning',
            items=[
                consolidate_memory.TextItem(today, 'learning', 'Text 1', 'Task 1'),
                consolidate_memory.TextItem(today, 'learning', 'Text 2', 'Task 2'),
            ],
        )

        assert group.count == 2

    def test_pattern_group_dates(self):
        """PatternGroup dates property returns unique sorted dates."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        group = consolidate_memory.PatternGroup(
            category='learning',
            items=[
                consolidate_memory.TextItem(today, 'learning', 'Text 1', 'Task 1'),
                consolidate_memory.TextItem(today, 'learning', 'Text 2', 'Task 2'),
                consolidate_memory.TextItem(yesterday, 'learning', 'Text 3', 'Task 3'),
            ],
        )

        dates = group.dates
        assert len(dates) == 2
        assert dates == [yesterday, today]  # Sorted


class TestMemoryDirDetection:
    """Tests for memory directory detection."""

    def test_get_memory_dir_finds_project(self, memory_dir_with_claude_md: Path, monkeypatch):
        """get_memory_dir finds project root with CLAUDE.md."""
        monkeypatch.chdir(memory_dir_with_claude_md.parent)

        result = consolidate_memory.get_memory_dir()
        assert result == memory_dir_with_claude_md

    def test_get_memory_dir_creates_directory(self, tmp_path: Path, monkeypatch):
        """get_memory_dir creates memory/ if needed."""
        # Create CLAUDE.md but not memory/
        claude_md = tmp_path / 'CLAUDE.md'
        claude_md.write_text('# Test')

        monkeypatch.chdir(tmp_path)

        result = consolidate_memory.get_memory_dir()
        assert result.exists()
        assert result.is_dir()

    def test_get_memory_dir_not_found(self, tmp_path: Path, monkeypatch):
        """get_memory_dir raises when project root not found."""
        monkeypatch.chdir(tmp_path)

        with pytest.raises(FileNotFoundError, match='Could not find project root'):
            consolidate_memory.get_memory_dir()
