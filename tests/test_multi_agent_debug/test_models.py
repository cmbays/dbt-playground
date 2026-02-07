"""Tests for multi-agent debug data models.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

import pytest
from datetime import datetime, UTC

from scripts.lib.multi_agent_debug.models import (
    AgentCapability,
    AgentFindings,
    AgentProfile,
    AgentStatus,
    Conflict,
    ConflictType,
    ComplexityAssessment,
    ComplexityFactor,
    Evidence,
    EvidenceType,
    EVIDENCE_WEIGHTS,
    Finding,
    LessonCandidate,
    MergeResolution,
    MultiAgentSession,
    SessionStatus,
    WorkAssignment,
    WorkZone,
)


# --- Fixtures ---

TEST_DATE = datetime(2026, 2, 15, tzinfo=UTC)


@pytest.fixture
def sample_zone():
    """Create a sample work zone."""
    return WorkZone(
        name='backend-api',
        description='Backend API investigation',
        files=['api/handlers.py', 'api/routes.py'],
        systems=['api-service'],
        required_capabilities=['backend'],
    )


@pytest.fixture
def sample_finding():
    """Create a sample finding with evidence."""
    return Finding(
        description='Connection pool exhaustion under load',
        classification='root_cause',
        evidence=[
            Evidence(
                description='Pool size = 1 in config',
                evidence_type=EvidenceType.CODE_ANALYSIS,
                source='config/database.py:12',
            ),
            Evidence(
                description='5s response time in logs',
                evidence_type=EvidenceType.LOG_CORRELATION,
                source='logs/api.log',
            ),
        ],
        confidence=0.9,
        files_involved=['config/database.py'],
        proposed_fix='Increase pool size to 10',
    )


# --- ComplexityAssessment Tests ---


class TestComplexityAssessment:
    """Tests for ComplexityAssessment model."""

    def test_valid_assessment(self):
        """Valid assessment with score and agents."""
        assessment = ComplexityAssessment(
            overall_score=0.5,
            suggested_agents=2,
            factors=[],
            rationale='Two systems affected',
        )
        assert assessment.overall_score == 0.5
        assert assessment.suggested_agents == 2

    def test_invalid_score_raises(self):
        """Score outside 0.0-1.0 raises ValueError."""
        with pytest.raises(ValueError, match='Complexity score must be 0.0-1.0'):
            ComplexityAssessment(overall_score=1.5, suggested_agents=1)

    def test_invalid_agents_raises(self):
        """Agent count outside 1-5 raises ValueError."""
        with pytest.raises(ValueError, match='Suggested agents must be 1-5'):
            ComplexityAssessment(overall_score=0.5, suggested_agents=0)

        with pytest.raises(ValueError, match='Suggested agents must be 1-5'):
            ComplexityAssessment(overall_score=0.5, suggested_agents=6)

    def test_factors_stored(self):
        """Complexity factors are stored correctly."""
        factors = [
            ComplexityFactor(name='concurrency', score=0.8, description='Race condition detected'),
        ]
        assessment = ComplexityAssessment(
            overall_score=0.8,
            suggested_agents=3,
            factors=factors,
        )
        assert len(assessment.factors) == 1
        assert assessment.factors[0].name == 'concurrency'


# --- AgentProfile Tests ---


class TestAgentProfile:
    """Tests for AgentProfile model."""

    def test_basic_profile(self):
        """Create a basic agent profile."""
        profile = AgentProfile(
            name='backend',
            capabilities=[
                AgentCapability(name='backend', proficiency=1.0),
                AgentCapability(name='data', proficiency=0.8),
            ],
        )
        assert profile.name == 'backend'
        assert profile.is_available
        assert len(profile.capabilities) == 2

    def test_capability_names(self):
        """capability_names returns list of names."""
        profile = AgentProfile(
            name='full-stack',
            capabilities=[
                AgentCapability(name='backend'),
                AgentCapability(name='frontend'),
            ],
        )
        assert profile.capability_names == ['backend', 'frontend']

    def test_has_capability(self):
        """has_capability checks correctly."""
        profile = AgentProfile(
            name='backend',
            capabilities=[AgentCapability(name='backend')],
        )
        assert profile.has_capability('backend') is True
        assert profile.has_capability('frontend') is False

    def test_get_proficiency(self):
        """get_proficiency returns correct value or 0.0."""
        profile = AgentProfile(
            name='backend',
            capabilities=[AgentCapability(name='backend', proficiency=0.9)],
        )
        assert profile.get_proficiency('backend') == 0.9
        assert profile.get_proficiency('frontend') == 0.0

    def test_availability_tracking(self):
        """Availability changes with current_sessions."""
        profile = AgentProfile(
            name='backend',
            max_concurrent_sessions=2,
            current_sessions=0,
        )
        assert profile.is_available is True

        profile.current_sessions = 2
        assert profile.is_available is False


# --- Evidence Tests ---


class TestEvidence:
    """Tests for Evidence model."""

    def test_evidence_weight(self):
        """Evidence weight matches type."""
        reproducible = Evidence(
            description='Bug reproduced',
            evidence_type=EvidenceType.REPRODUCIBLE,
        )
        assert reproducible.weight == 1.0

        theory = Evidence(
            description='Might be a race condition',
            evidence_type=EvidenceType.THEORY,
        )
        assert theory.weight == 0.3

    def test_all_evidence_weights(self):
        """All evidence types have defined weights."""
        for etype in EvidenceType:
            assert etype in EVIDENCE_WEIGHTS
            assert 0.0 <= EVIDENCE_WEIGHTS[etype] <= 1.0


# --- Finding Tests ---


class TestFinding:
    """Tests for Finding model."""

    def test_evidence_weight_calculation(self, sample_finding):
        """Evidence weight calculated correctly."""
        # CODE_ANALYSIS (0.6) + LOG_CORRELATION (0.8) / 2 = 0.7
        assert sample_finding.evidence_weight == pytest.approx(0.7)

    def test_no_evidence_weight(self):
        """Finding with no evidence has 0.0 weight."""
        finding = Finding(
            description='Just a guess',
            classification='theory',
        )
        assert finding.evidence_weight == 0.0


# --- AgentFindings Tests ---


class TestAgentFindings:
    """Tests for AgentFindings model."""

    def test_primary_finding(self, sample_finding, sample_zone):
        """primary_finding returns highest confidence."""
        low_finding = Finding(
            description='Minor issue',
            classification='symptom',
            confidence=0.3,
        )
        findings = AgentFindings(
            agent_name='alpha',
            session_id='test-001',
            zone=sample_zone,
            findings=[low_finding, sample_finding],
        )
        assert findings.primary_finding == sample_finding

    def test_no_findings_returns_none(self, sample_zone):
        """primary_finding returns None when empty."""
        findings = AgentFindings(
            agent_name='alpha',
            session_id='test-001',
            zone=sample_zone,
        )
        assert findings.primary_finding is None

    def test_root_cause_findings(self, sample_finding, sample_zone):
        """root_cause_findings filters correctly."""
        symptom = Finding(description='Symptom', classification='symptom')
        findings = AgentFindings(
            agent_name='alpha',
            session_id='test-001',
            zone=sample_zone,
            findings=[sample_finding, symptom],
        )
        root_causes = findings.root_cause_findings
        assert len(root_causes) == 1
        assert root_causes[0].classification == 'root_cause'


# --- MultiAgentSession Tests ---


class TestMultiAgentSession:
    """Tests for MultiAgentSession model."""

    def test_agent_count(self, sample_zone):
        """agent_count tracks assignments."""
        session = MultiAgentSession(
            session_id='MA-001',
            debug_session_id='DBG-2026-02-15-001',
            bug_description='Test bug',
            lead_agent='alpha',
            assignments=[
                WorkAssignment(agent_name='alpha', zone=sample_zone),
                WorkAssignment(agent_name='beta', zone=sample_zone),
            ],
        )
        assert session.agent_count == 2

    def test_agents_complete_tracking(self, sample_zone):
        """all_agents_complete tracks completion."""
        zone_a = WorkZone(name='zone-a', description='Zone A')
        zone_b = WorkZone(name='zone-b', description='Zone B')
        session = MultiAgentSession(
            session_id='MA-001',
            debug_session_id='DBG-2026-02-15-001',
            bug_description='Test bug',
            lead_agent='alpha',
            assignments=[
                WorkAssignment(
                    agent_name='alpha',
                    zone=zone_a,
                    status=AgentStatus.COMPLETE,
                ),
                WorkAssignment(
                    agent_name='beta',
                    zone=zone_b,
                    status=AgentStatus.INVESTIGATING,
                ),
            ],
        )
        assert session.agents_complete == 1
        assert session.all_agents_complete is False

        # Complete the second agent
        session.assignments[1].status = AgentStatus.COMPLETE
        assert session.all_agents_complete is True

    def test_get_assignment(self, sample_zone):
        """get_assignment retrieves by agent name."""
        session = MultiAgentSession(
            session_id='MA-001',
            debug_session_id='DBG-2026-02-15-001',
            bug_description='Test bug',
            lead_agent='alpha',
            assignments=[
                WorkAssignment(agent_name='alpha', zone=sample_zone),
            ],
        )
        assert session.get_assignment('alpha') is not None
        assert session.get_assignment('unknown') is None

    def test_empty_session(self):
        """Empty session has zero counts."""
        session = MultiAgentSession(
            session_id='MA-001',
            debug_session_id='DBG-2026-02-15-001',
            bug_description='Test bug',
            lead_agent='alpha',
        )
        assert session.agent_count == 0
        assert session.agents_complete == 0
        assert session.all_agents_complete is False


# --- MergeResolution Tests ---


class TestMergeResolution:
    """Tests for MergeResolution model."""

    def test_unresolved_conflicts(self):
        """has_unresolved_conflicts checks correctly."""
        resolution = MergeResolution(
            session_id='MA-001',
            lead_agent='alpha',
            participating_agents=['alpha', 'beta'],
        )
        assert resolution.has_unresolved_conflicts is False

        resolution.unresolved_conflicts.append(
            Conflict(
                conflict_id='C-001',
                conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
                agent_a='alpha',
                agent_b='beta',
                finding_a=Finding(description='A', classification='root_cause'),
                finding_b=Finding(description='B', classification='root_cause'),
                description='Agents disagree on root cause',
            )
        )
        assert resolution.has_unresolved_conflicts is True

    def test_total_conflicts(self):
        """total_conflicts sums resolved and unresolved."""
        finding = Finding(description='test', classification='root_cause')
        resolution = MergeResolution(
            session_id='MA-001',
            lead_agent='alpha',
            participating_agents=['alpha', 'beta'],
            conflicts=[
                Conflict(
                    conflict_id='C-001',
                    conflict_type=ConflictType.SCOPE_OVERLAP,
                    agent_a='alpha',
                    agent_b='beta',
                    finding_a=finding,
                    finding_b=finding,
                    description='Overlap',
                ),
            ],
            unresolved_conflicts=[
                Conflict(
                    conflict_id='C-002',
                    conflict_type=ConflictType.EVIDENCE_CONTRADICTION,
                    agent_a='alpha',
                    agent_b='beta',
                    finding_a=finding,
                    finding_b=finding,
                    description='Contradiction',
                ),
            ],
        )
        assert resolution.total_conflicts == 2


# --- LessonCandidate Tests ---


class TestLessonCandidate:
    """Tests for LessonCandidate model."""

    def test_basic_lesson(self):
        """Create a basic lesson candidate."""
        lesson = LessonCandidate(
            pattern_name='Connection Pool Sizing',
            context='Multi-user applications',
            problem='Pool size of 1 serializes requests',
            solution='Set pool min/max appropriate to concurrency',
            detection='Intermittent slow responses under load',
            source_session='MA-001',
            source_conflict='C-001',
            confidence=0.9,
            tags=['database', 'performance'],
        )
        assert lesson.pattern_name == 'Connection Pool Sizing'
        assert lesson.source_conflict == 'C-001'
        assert len(lesson.tags) == 2
