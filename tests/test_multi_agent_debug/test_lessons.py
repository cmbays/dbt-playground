"""Tests for multi-agent debug LESSONS.md integration.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

import json
import pytest
from datetime import datetime, UTC
from pathlib import Path

from scripts.lib.multi_agent_debug.lessons import (
    extract_debate_patterns,
    emit_lesson_events,
    format_lesson_for_review,
    format_all_lessons,
    _extract_from_conflict,
    _extract_from_finding,
    _build_lesson_event,
    _resolve_events_path,
    _generate_pattern_name,
    _extract_tags,
)
from scripts.lib.multi_agent_debug.models import (
    Conflict,
    ConflictResolution,
    ConflictType,
    Evidence,
    EvidenceType,
    Finding,
    LessonCandidate,
    MergeResolution,
)


# --- Fixtures ---

TEST_DATE = datetime(2026, 2, 15, tzinfo=UTC)


@pytest.fixture
def high_confidence_finding():
    """A high-confidence root cause finding with proposed fix."""
    return Finding(
        description='Connection pool size = 1 causing serialization',
        classification='root_cause',
        evidence=[
            Evidence(
                description='Pool config shows pool_size=1',
                evidence_type=EvidenceType.CODE_ANALYSIS,
                source='config/database.py:12',
            ),
            Evidence(
                description='Reproduced with concurrent requests',
                evidence_type=EvidenceType.REPRODUCIBLE,
            ),
        ],
        confidence=0.95,
        files_involved=['config/database.py'],
        proposed_fix='Increase pool size to 10',
    )


@pytest.fixture
def low_confidence_finding():
    """A low-confidence finding below lesson threshold."""
    return Finding(
        description='Maybe a memory leak',
        classification='root_cause',
        evidence=[
            Evidence(
                description='Heap seems to grow',
                evidence_type=EvidenceType.THEORY,
            ),
        ],
        confidence=0.3,
        proposed_fix='Investigate memory allocation',
    )


@pytest.fixture
def symptom_finding():
    """A symptom finding (not root_cause, should not generate lesson)."""
    return Finding(
        description='Frontend spinner on data load',
        classification='symptom',
        confidence=0.8,
        proposed_fix='Add timeout to fetch calls',
    )


@pytest.fixture
def resolved_conflict(high_confidence_finding, low_confidence_finding):
    """A conflict resolved via evidence weighting."""
    return Conflict(
        conflict_id='C-001',
        conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
        agent_a='backend',
        agent_b='data',
        finding_a=high_confidence_finding,
        finding_b=low_confidence_finding,
        description='Disagreement on root cause',
        resolution=ConflictResolution.EVIDENCE_WEIGHTED,
        resolved_finding=high_confidence_finding,
    )


@pytest.fixture
def escalated_conflict(high_confidence_finding):
    """A conflict escalated to human (not evidence-weighted)."""
    other = Finding(
        description='Network partition causing timeouts',
        classification='root_cause',
        evidence=[
            Evidence(
                description='Traceroute shows packet loss',
                evidence_type=EvidenceType.LOG_CORRELATION,
            ),
        ],
        confidence=0.85,
        proposed_fix='Add circuit breaker',
    )
    return Conflict(
        conflict_id='C-002',
        conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
        agent_a='backend',
        agent_b='infra',
        finding_a=high_confidence_finding,
        finding_b=other,
        description='Both have strong evidence',
        resolution=ConflictResolution.HUMAN_ESCALATED,
        resolution_rationale='Evidence too close',
    )


@pytest.fixture
def merge_resolution_with_conflicts(
    high_confidence_finding, resolved_conflict,
):
    """A merge resolution with resolved conflicts and consensus."""
    return MergeResolution(
        session_id='MA-LESSON-001',
        lead_agent='backend',
        participating_agents=['backend', 'data', 'infra'],
        consensus_findings=[high_confidence_finding],
        conflicts=[resolved_conflict],
        agreed_fixes=[{'file': 'config/database.py', 'change': 'Increase pool', 'priority': 'P0'}],
        deployment_order=['Increase pool size'],
        unresolved_conflicts=[],
        lessons_extracted=[],
    )


@pytest.fixture
def merge_resolution_clean(high_confidence_finding, symptom_finding):
    """A merge resolution with no conflicts."""
    return MergeResolution(
        session_id='MA-LESSON-002',
        lead_agent='backend',
        participating_agents=['backend', 'frontend'],
        consensus_findings=[high_confidence_finding, symptom_finding],
        conflicts=[],
        agreed_fixes=[],
        deployment_order=[],
        unresolved_conflicts=[],
        lessons_extracted=[],
    )


# --- extract_debate_patterns Tests ---


class TestExtractDebatePatterns:
    """Tests for the main extraction function."""

    def test_extracts_from_resolved_conflicts(
        self, merge_resolution_with_conflicts,
    ):
        """Resolved conflicts produce lesson candidates."""
        lessons = extract_debate_patterns(merge_resolution_with_conflicts)
        conflict_lessons = [l for l in lessons if l.source_conflict]
        assert len(conflict_lessons) >= 1

    def test_extracts_from_high_confidence_findings(
        self, merge_resolution_clean,
    ):
        """High-confidence root causes produce lesson candidates."""
        lessons = extract_debate_patterns(merge_resolution_clean)
        assert len(lessons) >= 1
        # Should come from the root_cause finding, not the symptom
        assert any('pool' in l.problem.lower() for l in lessons)

    def test_no_duplicates(self, merge_resolution_with_conflicts):
        """Same finding from conflict and consensus is not duplicated."""
        lessons = extract_debate_patterns(merge_resolution_with_conflicts)
        pattern_names = [l.pattern_name for l in lessons]
        assert len(pattern_names) == len(set(pattern_names))

    def test_empty_resolution(self):
        """Empty resolution produces no lessons."""
        resolution = MergeResolution(
            session_id='MA-EMPTY',
            lead_agent='backend',
            participating_agents=[],
            consensus_findings=[],
            conflicts=[],
        )
        lessons = extract_debate_patterns(resolution)
        assert len(lessons) == 0

    def test_only_low_confidence_no_lessons(self, low_confidence_finding):
        """Only low-confidence findings produce no lessons."""
        resolution = MergeResolution(
            session_id='MA-LOW',
            lead_agent='backend',
            participating_agents=['backend'],
            consensus_findings=[low_confidence_finding],
            conflicts=[],
        )
        lessons = extract_debate_patterns(resolution)
        assert len(lessons) == 0

    def test_symptom_only_no_lessons(self, symptom_finding):
        """Only symptom findings produce no lessons."""
        resolution = MergeResolution(
            session_id='MA-SYMP',
            lead_agent='frontend',
            participating_agents=['frontend'],
            consensus_findings=[symptom_finding],
            conflicts=[],
        )
        lessons = extract_debate_patterns(resolution)
        assert len(lessons) == 0


# --- _extract_from_conflict Tests ---


class TestExtractFromConflict:
    """Tests for conflict-based lesson extraction."""

    def test_evidence_weighted_produces_lesson(self, resolved_conflict):
        """Evidence-weighted resolution produces a lesson."""
        lesson = _extract_from_conflict(resolved_conflict, 'MA-001')
        assert lesson is not None
        assert lesson.source_conflict == 'C-001'
        assert lesson.source_session == 'MA-001'

    def test_human_escalated_no_lesson(self, escalated_conflict):
        """Human-escalated conflicts do not produce lessons."""
        lesson = _extract_from_conflict(escalated_conflict, 'MA-001')
        assert lesson is None

    def test_no_resolved_finding_no_lesson(self, high_confidence_finding):
        """Conflict without resolved_finding produces no lesson."""
        conflict = Conflict(
            conflict_id='C-003',
            conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
            agent_a='a',
            agent_b='b',
            finding_a=high_confidence_finding,
            finding_b=high_confidence_finding,
            description='Test',
            resolution=ConflictResolution.EVIDENCE_WEIGHTED,
            resolved_finding=None,
        )
        lesson = _extract_from_conflict(conflict, 'MA-001')
        assert lesson is None

    def test_low_confidence_winner_no_lesson(self, low_confidence_finding):
        """Winning finding with low confidence produces no lesson."""
        conflict = Conflict(
            conflict_id='C-004',
            conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
            agent_a='a',
            agent_b='b',
            finding_a=low_confidence_finding,
            finding_b=low_confidence_finding,
            description='Test',
            resolution=ConflictResolution.EVIDENCE_WEIGHTED,
            resolved_finding=low_confidence_finding,
        )
        lesson = _extract_from_conflict(conflict, 'MA-001')
        assert lesson is None

    def test_lesson_has_correct_detection(self, resolved_conflict):
        """Lesson detection describes the conflict type and agents."""
        lesson = _extract_from_conflict(resolved_conflict, 'MA-001')
        assert lesson is not None
        assert 'root_cause_disagreement' in lesson.detection
        assert 'backend' in lesson.detection
        assert 'data' in lesson.detection


# --- _extract_from_finding Tests ---


class TestExtractFromFinding:
    """Tests for finding-based lesson extraction."""

    def test_high_confidence_root_cause(self, high_confidence_finding):
        """High-confidence root cause produces lesson."""
        lesson = _extract_from_finding(high_confidence_finding, 'MA-001')
        assert lesson is not None
        assert lesson.confidence >= 0.7

    def test_low_confidence_no_lesson(self, low_confidence_finding):
        """Low-confidence finding produces no lesson."""
        lesson = _extract_from_finding(low_confidence_finding, 'MA-001')
        assert lesson is None

    def test_symptom_no_lesson(self, symptom_finding):
        """Symptom findings produce no lesson."""
        lesson = _extract_from_finding(symptom_finding, 'MA-001')
        assert lesson is None

    def test_no_proposed_fix_no_lesson(self):
        """Root cause without proposed fix produces no lesson."""
        finding = Finding(
            description='Database issue found',
            classification='root_cause',
            confidence=0.9,
            proposed_fix=None,
        )
        lesson = _extract_from_finding(finding, 'MA-001')
        assert lesson is None

    def test_lesson_has_no_conflict_id(self, high_confidence_finding):
        """Finding-based lessons have no conflict_id."""
        lesson = _extract_from_finding(high_confidence_finding, 'MA-001')
        assert lesson is not None
        assert lesson.source_conflict is None


# --- emit_lesson_events Tests ---


class TestEmitLessonEvents:
    """Tests for event emission to events.jsonl."""

    def test_emit_creates_events(self, tmp_path):
        """Emitting lessons creates events in file."""
        events_file = str(tmp_path / 'events.jsonl')
        lessons = [
            LessonCandidate(
                pattern_name='Test Pattern',
                context='Test context',
                problem='Test problem',
                solution='Test solution',
                detection='Test detection',
                source_session='MA-001',
                confidence=0.9,
                tags=['test'],
            ),
        ]
        count = emit_lesson_events(lessons, events_file)
        assert count == 1

        content = Path(events_file).read_text(encoding='utf-8')
        event = json.loads(content.strip())
        assert event['event'] == 'debug_lesson'
        assert event['version'] == '1.0'
        assert event['data']['pattern_name'] == 'Test Pattern'
        assert event['data']['source'] == 'multi_agent_session'

    def test_emit_multiple_events(self, tmp_path):
        """Emitting multiple lessons creates multiple events."""
        events_file = str(tmp_path / 'events.jsonl')
        lessons = [
            LessonCandidate(
                pattern_name=f'Pattern {i}',
                context='ctx',
                problem='prob',
                solution='sol',
                detection='det',
                source_session='MA-001',
                confidence=0.8,
            )
            for i in range(3)
        ]
        count = emit_lesson_events(lessons, events_file)
        assert count == 3

        lines = Path(events_file).read_text(encoding='utf-8').strip().split('\n')
        assert len(lines) == 3

    def test_emit_empty_list(self, tmp_path):
        """Emitting empty list does nothing."""
        events_file = str(tmp_path / 'events.jsonl')
        count = emit_lesson_events([], events_file)
        assert count == 0
        assert not Path(events_file).exists()

    def test_emit_appends_to_existing(self, tmp_path):
        """Events are appended, not overwritten."""
        events_file = str(tmp_path / 'events.jsonl')
        Path(events_file).write_text(
            '{"existing": true}\n', encoding='utf-8',
        )

        lessons = [
            LessonCandidate(
                pattern_name='New',
                context='ctx',
                problem='prob',
                solution='sol',
                detection='det',
                source_session='MA-001',
                confidence=0.8,
            ),
        ]
        emit_lesson_events(lessons, events_file)

        lines = Path(events_file).read_text(encoding='utf-8').strip().split('\n')
        assert len(lines) == 2

    def test_event_has_timestamp(self, tmp_path):
        """Events include ISO timestamp."""
        events_file = str(tmp_path / 'events.jsonl')
        lessons = [
            LessonCandidate(
                pattern_name='Test',
                context='ctx',
                problem='prob',
                solution='sol',
                detection='det',
                source_session='MA-001',
                confidence=0.8,
            ),
        ]
        emit_lesson_events(lessons, events_file)

        content = Path(events_file).read_text(encoding='utf-8')
        event = json.loads(content.strip())
        assert 'timestamp' in event
        # Should be valid ISO format
        datetime.fromisoformat(event['timestamp'])

    def test_event_includes_conflict_id(self, tmp_path):
        """Events from conflicts include conflict_id."""
        events_file = str(tmp_path / 'events.jsonl')
        lessons = [
            LessonCandidate(
                pattern_name='Debate Lesson',
                context='ctx',
                problem='prob',
                solution='sol',
                detection='det',
                source_session='MA-001',
                source_conflict='C-001',
                confidence=0.9,
            ),
        ]
        emit_lesson_events(lessons, events_file)

        content = Path(events_file).read_text(encoding='utf-8')
        event = json.loads(content.strip())
        assert event['data']['conflict_id'] == 'C-001'


# --- _build_lesson_event Tests ---


class TestBuildLessonEvent:
    """Tests for event construction."""

    def test_event_structure(self):
        """Event has required top-level fields."""
        lesson = LessonCandidate(
            pattern_name='Test',
            context='ctx',
            problem='prob',
            solution='sol',
            detection='det',
            source_session='MA-001',
            confidence=0.9,
            tags=['test'],
        )
        event = _build_lesson_event(lesson)
        assert 'timestamp' in event
        assert event['event'] == 'debug_lesson'
        assert event['version'] == '1.0'
        assert 'data' in event

    def test_event_data_fields(self):
        """Event data has all required fields."""
        lesson = LessonCandidate(
            pattern_name='Pattern X',
            context='ctx',
            problem='Database issue',
            solution='Fix pool',
            detection='Evidence weighting',
            source_session='MA-002',
            source_conflict='C-005',
            confidence=0.85,
            tags=['database', 'performance'],
        )
        event = _build_lesson_event(lesson)
        data = event['data']

        assert data['pattern_name'] == 'Pattern X'
        assert data['problem'] == 'Database issue'
        assert data['solution'] == 'Fix pool'
        assert data['detection'] == 'Evidence weighting'
        assert data['confidence'] == 0.85
        assert data['source'] == 'multi_agent_session'
        assert data['session_id'] == 'MA-002'
        assert data['conflict_id'] == 'C-005'
        assert data['tags'] == ['database', 'performance']


# --- format Tests ---


class TestFormatLessonForReview:
    """Tests for lesson formatting."""

    def test_format_includes_pattern_name(self):
        """Formatted lesson includes pattern name as heading."""
        lesson = LessonCandidate(
            pattern_name='Pool Size Issue',
            context='Debug session MA-001',
            problem='Pool too small',
            solution='Increase pool',
            detection='Code analysis',
            source_session='MA-001',
            confidence=0.9,
        )
        result = format_lesson_for_review(lesson)
        assert '### Pool Size Issue' in result
        assert 'Debug session MA-001' in result
        assert '0.90' in result

    def test_format_includes_conflict_source(self):
        """Formatted lesson shows conflict source when present."""
        lesson = LessonCandidate(
            pattern_name='Test',
            context='ctx',
            problem='prob',
            solution='sol',
            detection='det',
            source_session='MA-001',
            source_conflict='C-001',
            confidence=0.9,
        )
        result = format_lesson_for_review(lesson)
        assert 'C-001' in result

    def test_format_includes_tags(self):
        """Formatted lesson shows tags."""
        lesson = LessonCandidate(
            pattern_name='Test',
            context='ctx',
            problem='prob',
            solution='sol',
            detection='det',
            source_session='MA-001',
            confidence=0.9,
            tags=['database', 'performance'],
        )
        result = format_lesson_for_review(lesson)
        assert 'database' in result
        assert 'performance' in result


class TestFormatAllLessons:
    """Tests for formatting all lessons."""

    def test_format_empty_lessons(self):
        """Empty lessons list produces 'no candidates' message."""
        result = format_all_lessons([])
        assert 'No Lesson Candidates' in result

    def test_format_groups_by_source(self):
        """Lessons are grouped by source type."""
        lessons = [
            LessonCandidate(
                pattern_name='From Conflict',
                context='ctx',
                problem='prob',
                solution='sol',
                detection='det',
                source_session='MA-001',
                source_conflict='C-001',
                confidence=0.9,
            ),
            LessonCandidate(
                pattern_name='From Finding',
                context='ctx',
                problem='prob',
                solution='sol',
                detection='det',
                source_session='MA-001',
                confidence=0.9,
            ),
        ]
        result = format_all_lessons(lessons)
        assert 'From Debate Resolution' in result
        assert 'From High-Confidence Root Causes' in result

    def test_format_includes_count(self):
        """Document shows total candidate count."""
        lessons = [
            LessonCandidate(
                pattern_name=f'Pattern {i}',
                context='ctx',
                problem='prob',
                solution='sol',
                detection='det',
                source_session='MA-001',
                confidence=0.9,
            )
            for i in range(3)
        ]
        result = format_all_lessons(lessons)
        assert 'Total Candidates**: 3' in result


# --- Internal Function Tests ---


class TestGeneratePatternName:
    """Tests for pattern name generation."""

    def test_short_name_title_cased(self):
        """Short names are title-cased."""
        finding = Finding(
            description='pool size wrong',
            classification='root_cause',
        )
        name = _generate_pattern_name(finding)
        assert name == 'Pool Size Wrong'

    def test_long_name_truncated(self):
        """Long names are truncated at 60 chars."""
        finding = Finding(
            description='A' * 100,
            classification='root_cause',
        )
        name = _generate_pattern_name(finding)
        assert len(name) <= 60
        assert name.endswith('...')


class TestExtractTags:
    """Tests for tag extraction from findings."""

    def test_database_keywords(self):
        """Database keywords produce database tag."""
        finding = Finding(
            description='Database pool connection issue',
            classification='root_cause',
        )
        tags = _extract_tags(finding)
        assert 'database' in tags

    def test_no_keywords_uses_classification(self):
        """No matching keywords falls back to classification."""
        finding = Finding(
            description='Something unusual happened',
            classification='root_cause',
        )
        tags = _extract_tags(finding)
        assert 'root_cause' in tags

    def test_includes_fix_text(self):
        """Tags extracted from both description and proposed_fix."""
        finding = Finding(
            description='Something happened',
            classification='root_cause',
            proposed_fix='Fix the database connection pool',
        )
        tags = _extract_tags(finding)
        assert 'database' in tags
