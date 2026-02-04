"""
Unit and integration tests for LESSONS.md Analyzer (WAVE3-021).

Tests cover:
- Scoring algorithm
- Pattern clustering
- Entry generation
- CLI commands
- Integration with debug sessions

Part of Wave 3 P1: Protocol Enhancements (Issue #238)
"""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import duckdb
import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from scripts.lib.debug_session import database as db
from scripts.lib.lessons_analyzer import (
    AnalyzerError,
    DebugSessionData,
    InsufficientDataError,
    LessonsAnalyzer,
    NoSessionsFoundError,
    Pattern,
    PatternNotFoundError,
    RootCauseVariant,
    calculate_score,
    classify_pattern,
    consistency_weight,
    frequency_weight,
    recency_weight,
)
from scripts.lib.lessons_analyzer.clustering import (
    cluster_root_causes,
    extract_pattern_name,
    keyword_overlap,
    normalize_keywords,
)
from scripts.lib.lessons_analyzer.generator import (
    generate_lessons_entry,
    infer_mitigations,
    infer_when_to_apply,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def make_session():
    """Factory for creating test sessions."""

    def _make_session(
        session_id: str = None,
        root_cause: str = 'Test root cause',
        tags: list = None,
        days_ago: int = 0,
        duration: int = 30,
    ) -> DebugSessionData:
        return DebugSessionData(
            session_id=session_id or f'DBG-TEST-{id(root_cause) % 1000}',
            bug_description='Test bug',
            root_cause=root_cause,
            tags=tags or [],
            start_time=datetime.now(UTC) - timedelta(days=days_ago),
            end_time=datetime.now(UTC) - timedelta(days=days_ago) + timedelta(minutes=duration),
            duration_minutes=duration,
            outcome='resolved',
            step_count=3,
        )

    return _make_session


@pytest.fixture
def sample_pattern(make_session):
    """Sample pattern for testing."""
    return Pattern(
        pattern_name='Race condition in async startup',
        frequency=4,
        first_seen=datetime(2026, 1, 15, tzinfo=UTC),
        last_seen=datetime(2026, 2, 4, tzinfo=UTC),
        confidence_score=0.85,
        root_causes=[
            RootCauseVariant('Missing mutex lock', 2, ['DBG-001', 'DBG-002']),
            RootCauseVariant('Timing assumption', 1, ['DBG-003']),
            RootCauseVariant('Init order', 1, ['DBG-004']),
        ],
        tags=['async', 'queue', 'startup'],
        related_sessions=['DBG-001', 'DBG-002', 'DBG-003', 'DBG-004'],
        avg_debug_minutes=45.0,
        status='PROMOTE',
    )


@pytest.fixture
def temp_db(tmp_path: Path):
    """Create temporary DuckDB with debug sessions."""
    db_path = tmp_path / 'test_debug.duckdb'
    conn = duckdb.connect(str(db_path))
    conn.execute(db.SCHEMA_SQL)
    return conn


@pytest.fixture
def seeded_analyzer_db(temp_db):
    """Seed database with test sessions for analysis."""
    from datetime import timedelta

    # Root causes designed to have high keyword overlap for clustering
    sessions = [
        # Race condition pattern (3 occurrences) - share 'race' and 'lock' keywords
        ('DBG-2026-02-01-001', 'Queue race', 'Race condition missing lock on queue', ['async', 'queue'], 30, 0),
        ('DBG-2026-02-03-001', 'Cache race', 'Race condition lock not acquired on cache', ['async', 'cache'], 45, 2),
        ('DBG-2026-02-04-001', 'Worker race', 'Race condition concurrent lock access', ['async', 'worker'], 40, 3),
        # Null check pattern (2 occurrences) - share 'null' and 'check' keywords
        ('DBG-2026-02-02-001', 'Null pointer', 'Null check missing on input validation', ['validation'], 20, 1),
        ('DBG-2026-02-04-002', 'None error', 'Null check failed for API response', ['validation', 'api'], 25, 3),
    ]

    for sid, desc, cause, tags, duration, days_ago in sessions:
        # Calculate start_time in Python to avoid DuckDB interval parameter issue
        start_time = datetime.now(UTC) - timedelta(days=days_ago)
        temp_db.execute(
            """
            INSERT INTO debug_sessions
            (session_id, bug_description, root_cause, tags, outcome, duration_minutes, start_time, severity, step_count)
            VALUES (?, ?, ?, ?, 'resolved', ?, ?, 'medium', 3)
            """,
            [sid, desc, cause, tags, duration, start_time],
        )

    return temp_db


# =============================================================================
# Unit Tests: Scoring Algorithm
# =============================================================================


class TestFrequencyWeight:
    """Tests for frequency weight calculation."""

    def test_zero_count_returns_zero(self):
        """Zero count gives zero weight."""
        assert frequency_weight(0) == 0.0

    def test_small_counts(self):
        """Small counts scale logarithmically."""
        # count=1 should be around 0.28
        assert 0.25 < frequency_weight(1) < 0.35

        # count=2 should be higher
        assert frequency_weight(2) > frequency_weight(1)

    def test_mid_counts(self):
        """Mid-range counts."""
        # count=5 should be around 0.73
        assert 0.65 < frequency_weight(5) < 0.80

    def test_max_count_is_one(self):
        """Max count (10) gives weight of 1.0."""
        assert frequency_weight(10) == pytest.approx(1.0, rel=0.01)

    def test_above_max_capped(self):
        """Counts above max are capped."""
        assert frequency_weight(15) == pytest.approx(1.0, rel=0.01)


class TestRecencyWeight:
    """Tests for recency weight calculation."""

    def test_today_is_one(self):
        """Today (0 days) gives weight of 1.0."""
        assert recency_weight(0) == 1.0

    def test_linear_decay(self):
        """Weight decays linearly."""
        # Halfway through decay period
        assert recency_weight(15) == pytest.approx(0.5, rel=0.01)

    def test_end_of_decay_is_zero(self):
        """End of decay period is 0."""
        assert recency_weight(30) == 0.0

    def test_beyond_decay_is_zero(self):
        """Beyond decay period is still 0."""
        assert recency_weight(45) == 0.0

    def test_custom_decay_period(self):
        """Custom decay period works."""
        # 7 day decay
        assert recency_weight(7, decay_period=7) == 0.0
        assert recency_weight(3, decay_period=7) == pytest.approx(0.57, rel=0.1)


class TestConsistencyWeight:
    """Tests for consistency weight calculation."""

    def test_single_session_is_zero(self, make_session):
        """Single session gives zero consistency."""
        session = make_session(tags=['async'])
        assert consistency_weight([session]) == 0.0

    def test_diverse_tags_score_higher(self, make_session):
        """Diverse tags give higher score."""
        sessions = [
            make_session(session_id='s1', tags=['async', 'queue'], days_ago=0),
            make_session(session_id='s2', tags=['cache', 'startup'], days_ago=7),
            make_session(session_id='s3', tags=['async', 'race'], days_ago=14),
        ]
        score = consistency_weight(sessions)
        assert score > 0.5

    def test_same_tags_score_lower(self, make_session):
        """Same tags give lower score."""
        sessions = [
            make_session(session_id='s1', tags=['async'], days_ago=0),
            make_session(session_id='s2', tags=['async'], days_ago=1),
        ]
        score = consistency_weight(sessions)
        assert score < 0.5

    def test_time_spread_contributes(self, make_session):
        """Time spread increases consistency score."""
        # Clustered (same day)
        clustered = [
            make_session(session_id='s1', tags=['a'], days_ago=0),
            make_session(session_id='s2', tags=['b'], days_ago=0),
        ]
        clustered_score = consistency_weight(clustered)

        # Spread (14 days apart)
        spread = [
            make_session(session_id='s3', tags=['a'], days_ago=0),
            make_session(session_id='s4', tags=['b'], days_ago=14),
        ]
        spread_score = consistency_weight(spread)

        assert spread_score > clustered_score


class TestCalculateScore:
    """Tests for total score calculation."""

    def test_high_quality_pattern(self, make_session):
        """High-quality pattern scores well."""
        sessions = [
            make_session(session_id='s1', tags=['async', 'queue'], days_ago=0),
            make_session(session_id='s2', tags=['cache', 'startup'], days_ago=7),
            make_session(session_id='s3', tags=['async', 'race'], days_ago=14),
            make_session(session_id='s4', tags=['worker', 'async'], days_ago=20),
        ]
        score = calculate_score(frequency=4, days_since_last=0, sessions=sessions)
        assert score >= 0.7

    def test_low_quality_pattern(self, make_session):
        """Low-quality pattern scores poorly."""
        sessions = [
            make_session(session_id='s1', tags=['import'], days_ago=25),
            make_session(session_id='s2', tags=['import'], days_ago=26),
        ]
        score = calculate_score(frequency=2, days_since_last=25, sessions=sessions)
        assert score < 0.5


class TestClassifyPattern:
    """Tests for pattern classification."""

    def test_promote_threshold(self):
        """PROMOTE requires score >= 0.8 and freq >= 3."""
        assert classify_pattern(0.85, 3) == 'PROMOTE'
        assert classify_pattern(0.80, 3) == 'PROMOTE'
        assert classify_pattern(0.85, 2) == 'CANDIDATE'  # freq too low

    def test_candidate_threshold(self):
        """CANDIDATE requires score >= 0.7 and freq >= 2."""
        assert classify_pattern(0.75, 2) == 'CANDIDATE'
        assert classify_pattern(0.70, 2) == 'CANDIDATE'

    def test_review_threshold(self):
        """REVIEW requires score >= 0.5 and freq >= 2."""
        assert classify_pattern(0.55, 2) == 'REVIEW'
        assert classify_pattern(0.50, 2) == 'REVIEW'

    def test_ignore_below_threshold(self):
        """Below threshold returns IGNORE."""
        assert classify_pattern(0.40, 2) == 'IGNORE'
        assert classify_pattern(0.60, 1) == 'IGNORE'


# =============================================================================
# Unit Tests: Clustering
# =============================================================================


class TestNormalizeKeywords:
    """Tests for keyword normalization."""

    def test_extracts_words(self):
        """Extracts alphanumeric words."""
        keywords = normalize_keywords('Missing mutex lock on queue')
        assert 'missing' in keywords
        assert 'mutex' in keywords
        assert 'lock' in keywords
        assert 'queue' in keywords

    def test_filters_stop_words(self):
        """Filters common stop words."""
        keywords = normalize_keywords('the bug is in the code')
        assert 'the' not in keywords
        assert 'bug' not in keywords  # Also a stop word
        assert 'code' in keywords

    def test_filters_short_words(self):
        """Filters words <= 2 chars."""
        keywords = normalize_keywords('a is to be or not')
        assert len(keywords) == 0

    def test_empty_string(self):
        """Empty string returns empty set."""
        assert normalize_keywords('') == set()

    def test_case_insensitive(self):
        """Normalizes to lowercase."""
        keywords = normalize_keywords('MISSING Mutex Lock')
        assert 'missing' in keywords
        assert 'MISSING' not in keywords


class TestKeywordOverlap:
    """Tests for keyword overlap calculation."""

    def test_identical_sets(self):
        """Identical sets have 1.0 overlap."""
        s1 = {'mutex', 'lock', 'race'}
        s2 = {'mutex', 'lock', 'race'}
        assert keyword_overlap(s1, s2) == 1.0

    def test_no_overlap(self):
        """Disjoint sets have 0.0 overlap."""
        s1 = {'mutex', 'lock'}
        s2 = {'null', 'pointer'}
        assert keyword_overlap(s1, s2) == 0.0

    def test_partial_overlap(self):
        """Partial overlap calculated correctly."""
        s1 = {'mutex', 'lock', 'race'}
        s2 = {'mutex', 'lock', 'async'}
        # 2 overlap / 3 smaller = 0.67
        assert keyword_overlap(s1, s2) == pytest.approx(0.67, rel=0.1)

    def test_empty_sets(self):
        """Empty sets have 0 overlap."""
        assert keyword_overlap(set(), {'a'}) == 0.0
        assert keyword_overlap({'a'}, set()) == 0.0


class TestExtractPatternName:
    """Tests for pattern name extraction."""

    def test_race_condition_pattern(self, make_session):
        """Race condition detected in name."""
        sessions = [
            make_session(root_cause='Missing mutex lock causing race'),
            make_session(root_cause='Race condition on startup'),
        ]
        name = extract_pattern_name(sessions)
        assert 'race' in name.lower()

    def test_null_check_pattern(self, make_session):
        """Null check pattern detected."""
        sessions = [
            make_session(root_cause='Missing null check'),
            make_session(root_cause='Null pointer exception'),
        ]
        name = extract_pattern_name(sessions)
        assert 'null' in name.lower()


class TestClusterRootCauses:
    """Tests for clustering algorithm."""

    def test_clusters_similar_causes(self, make_session):
        """Similar root causes are clustered."""
        sessions = [
            make_session(session_id='s1', root_cause='Missing mutex lock', days_ago=0),
            make_session(session_id='s2', root_cause='Mutex lock not acquired', days_ago=1),
            make_session(session_id='s3', root_cause='Lock missing on shared state', days_ago=2),
        ]

        patterns = cluster_root_causes(sessions, threshold=0.3, min_cluster_size=2)

        assert len(patterns) >= 1
        # All should be in one cluster
        assert patterns[0].frequency >= 2

    def test_separates_different_causes(self, make_session):
        """Different root causes stay separate."""
        sessions = [
            make_session(session_id='s1', root_cause='Missing mutex lock'),
            make_session(session_id='s2', root_cause='Missing mutex lock'),
            make_session(session_id='s3', root_cause='Null pointer exception'),
            make_session(session_id='s4', root_cause='Null reference error'),
        ]

        patterns = cluster_root_causes(sessions, threshold=0.4, min_cluster_size=2)

        # Should have 2 patterns
        assert len(patterns) == 2


# =============================================================================
# Unit Tests: Generator
# =============================================================================


class TestInferWhenToApply:
    """Tests for when-to-apply inference."""

    def test_race_condition_context(self, sample_pattern):
        """Race condition gets async context."""
        sample_pattern.pattern_name = 'Race condition in async startup'
        result = infer_when_to_apply(sample_pattern)
        assert 'concurrent' in result.lower() or 'async' in result.lower()

    def test_timeout_context(self, sample_pattern):
        """Timeout gets external service context."""
        sample_pattern.pattern_name = 'Timeout from external API'
        result = infer_when_to_apply(sample_pattern)
        assert 'external' in result.lower() or 'service' in result.lower()


class TestInferMitigations:
    """Tests for mitigation inference."""

    def test_race_condition_mitigations(self, sample_pattern):
        """Race condition gets lock-related mitigations."""
        sample_pattern.pattern_name = 'Race condition'
        mitigations = infer_mitigations(sample_pattern)
        assert any('lock' in m.lower() or 'mutex' in m.lower() for m in mitigations)

    def test_null_check_mitigations(self, sample_pattern):
        """Null check gets validation mitigations."""
        sample_pattern.pattern_name = 'Missing null check'
        sample_pattern.root_causes = [RootCauseVariant('Null pointer', 1, [])]
        mitigations = infer_mitigations(sample_pattern)
        assert any('null' in m.lower() or 'optional' in m.lower() for m in mitigations)

    def test_max_four_mitigations(self, sample_pattern):
        """Returns at most 4 mitigations."""
        mitigations = infer_mitigations(sample_pattern)
        assert len(mitigations) <= 4


class TestGenerateLessonsEntry:
    """Tests for LESSONS.md entry generation."""

    def test_entry_has_required_sections(self, sample_pattern):
        """Entry contains all required sections."""
        entry = generate_lessons_entry(sample_pattern)

        assert '### Pattern:' in entry
        assert '**When to apply**:' in entry
        assert '**Proven in**:' in entry
        assert '**Description**:' in entry
        assert '**Common Root Causes**:' in entry
        assert '**Symptoms**:' in entry
        assert '**Mitigations**:' in entry
        assert '**Debug Time**:' in entry
        assert '**See also**:' in entry

    def test_entry_has_metadata_footer(self, sample_pattern):
        """Entry has generator metadata footer."""
        entry = generate_lessons_entry(sample_pattern)

        assert '*Generated by WAVE3-021 Analyzer' in entry
        assert f'Frequency: {sample_pattern.frequency}' in entry
        assert f'Status: {sample_pattern.status}' in entry

    def test_root_causes_have_percentages(self, sample_pattern):
        """Root causes show percentages."""
        entry = generate_lessons_entry(sample_pattern)

        # Should have percentage in root causes
        assert '%' in entry


# =============================================================================
# Integration Tests: Analyzer
# =============================================================================


class TestAnalyzerExtract:
    """Tests for pattern extraction."""

    def test_extracts_patterns(self, seeded_analyzer_db):
        """Extracts patterns from seeded data."""
        analyzer = LessonsAnalyzer(conn=seeded_analyzer_db)

        patterns = analyzer.extract(min_frequency=2, min_score=0.3)

        assert len(patterns) >= 1
        # Should find race condition pattern
        race_patterns = [p for p in patterns if 'race' in p.pattern_name.lower() or 'mutex' in p.pattern_name.lower() or 'lock' in p.pattern_name.lower()]
        assert len(race_patterns) >= 1

    def test_respects_min_frequency(self, seeded_analyzer_db):
        """Minimum frequency filter works."""
        analyzer = LessonsAnalyzer(conn=seeded_analyzer_db)

        # With min_frequency=3, only race pattern qualifies
        patterns = analyzer.extract(min_frequency=3, min_score=0.0)

        # All patterns should have freq >= 3
        for p in patterns:
            assert p.frequency >= 3

    def test_respects_min_score(self, seeded_analyzer_db):
        """Minimum score filter works."""
        analyzer = LessonsAnalyzer(conn=seeded_analyzer_db)

        patterns = analyzer.extract(min_frequency=2, min_score=0.6)

        for p in patterns:
            assert p.confidence_score >= 0.6


class TestAnalyzerReview:
    """Tests for pattern review."""

    def test_review_finds_pattern(self, seeded_analyzer_db):
        """Review finds pattern by name."""
        analyzer = LessonsAnalyzer(conn=seeded_analyzer_db)

        # First extract to get pattern names
        patterns = analyzer.extract(min_frequency=2, min_score=0.0)
        if patterns:
            pattern = analyzer.review(patterns[0].pattern_name)
            assert pattern is not None

    def test_review_partial_match(self, seeded_analyzer_db):
        """Review works with partial name match."""
        analyzer = LessonsAnalyzer(conn=seeded_analyzer_db)

        # Should find something with 'lock' or 'race'
        try:
            pattern = analyzer.review('lock')
            assert pattern is not None
        except PatternNotFoundError:
            # Try alternative
            pattern = analyzer.review('race')
            assert pattern is not None

    def test_review_not_found_raises(self, seeded_analyzer_db):
        """Review raises when pattern not found."""
        analyzer = LessonsAnalyzer(conn=seeded_analyzer_db)

        with pytest.raises(PatternNotFoundError):
            analyzer.review('nonexistent_pattern_xyz')


class TestAnalyzerStats:
    """Tests for statistics."""

    def test_stats_returns_dict(self, seeded_analyzer_db):
        """Stats returns expected structure."""
        analyzer = LessonsAnalyzer(conn=seeded_analyzer_db)

        stats = analyzer.get_stats()

        assert 'total_sessions' in stats
        assert 'by_outcome' in stats
        assert 'by_category' in stats
        assert 'top_tags' in stats
        assert 'patterns_detected' in stats

    def test_stats_counts_correctly(self, seeded_analyzer_db):
        """Stats counts are accurate."""
        analyzer = LessonsAnalyzer(conn=seeded_analyzer_db)

        stats = analyzer.get_stats()

        # We seeded 5 sessions
        assert stats['total_sessions'] == 5
        assert stats['by_outcome'].get('resolved', 0) == 5


class TestAnalyzerGenerate:
    """Tests for entry generation."""

    def test_generate_produces_valid_entry(self, seeded_analyzer_db):
        """Generate produces valid markdown."""
        analyzer = LessonsAnalyzer(conn=seeded_analyzer_db)

        patterns = analyzer.extract(min_frequency=2, min_score=0.0)
        if patterns:
            entry = analyzer.generate_entry(patterns[0])

            assert '### Pattern:' in entry
            assert patterns[0].pattern_name in entry


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestAnalyzerErrors:
    """Tests for error handling."""

    def test_no_sessions_error(self, temp_db):
        """NoSessionsFoundError when no data."""
        analyzer = LessonsAnalyzer(conn=temp_db)

        with pytest.raises(NoSessionsFoundError):
            analyzer.extract()

    def test_insufficient_data_error(self, temp_db):
        """InsufficientDataError with single session."""
        # Add just one session
        temp_db.execute(
            """
            INSERT INTO debug_sessions
            (session_id, bug_description, root_cause, tags, outcome, duration_minutes, start_time, severity)
            VALUES ('DBG-001', 'Single bug', 'Single cause', [], 'resolved', 30, CURRENT_TIMESTAMP, 'medium')
            """
        )

        analyzer = LessonsAnalyzer(conn=temp_db)

        with pytest.raises(InsufficientDataError):
            analyzer.extract()

    def test_pattern_not_found_error(self, seeded_analyzer_db):
        """PatternNotFoundError contains pattern name."""
        analyzer = LessonsAnalyzer(conn=seeded_analyzer_db)

        with pytest.raises(PatternNotFoundError) as exc_info:
            analyzer.review('nonexistent_xyz')

        assert 'nonexistent_xyz' in str(exc_info.value)


# =============================================================================
# Pattern Data Structure Tests
# =============================================================================


class TestPatternModel:
    """Tests for Pattern data class."""

    def test_days_since_last(self, sample_pattern):
        """Days since last is calculated."""
        days = sample_pattern.days_since_last
        assert isinstance(days, int)
        assert days >= 0

    def test_root_cause_variant(self):
        """RootCauseVariant holds data correctly."""
        variant = RootCauseVariant(
            cause='Missing null check',
            count=3,
            example_sessions=['DBG-001', 'DBG-002', 'DBG-003'],
        )
        assert variant.cause == 'Missing null check'
        assert variant.count == 3
        assert len(variant.example_sessions) == 3
