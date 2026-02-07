"""Tests for multi-agent debug conflict detector.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

import pytest
from datetime import datetime, UTC

from scripts.lib.multi_agent_debug.conflict_detector import (
    detect_conflicts,
    resolve_conflict_by_evidence,
    calculate_finding_weight,
    get_conflict_summary,
    _findings_disagree,
    _evidence_contradicts,
    _get_file_overlap,
    _classifications_conflict,
    _calculate_finding_weight,
)
from scripts.lib.multi_agent_debug.models import (
    AgentFindings,
    Conflict,
    ConflictResolution,
    ConflictType,
    Evidence,
    EvidenceType,
    Finding,
    WorkZone,
)


# --- Fixtures ---

TEST_DATE = datetime(2026, 2, 15, tzinfo=UTC)


@pytest.fixture
def backend_zone():
    """Create a backend work zone."""
    return WorkZone(
        name='backend',
        description='Backend investigation',
        files=['api/handlers.py'],
        required_capabilities=['backend'],
    )


@pytest.fixture
def frontend_zone():
    """Create a frontend work zone."""
    return WorkZone(
        name='frontend',
        description='Frontend investigation',
        files=['components/App.tsx'],
        required_capabilities=['frontend'],
    )


@pytest.fixture
def alpha_root_cause_findings(backend_zone):
    """Alpha agent: root cause = connection pool."""
    return AgentFindings(
        agent_name='alpha',
        session_id='MA-001',
        zone=backend_zone,
        findings=[
            Finding(
                description='Connection pool size is 1 causing serialization',
                classification='root_cause',
                evidence=[
                    Evidence(
                        description='Pool config shows pool_size=1',
                        evidence_type=EvidenceType.CODE_ANALYSIS,
                        source='config/database.py:12',
                    ),
                    Evidence(
                        description='Reproduced with 3 concurrent requests',
                        evidence_type=EvidenceType.REPRODUCIBLE,
                    ),
                ],
                confidence=0.95,
                files_involved=['config/database.py'],
                proposed_fix='Increase pool size to 10',
            ),
        ],
    )


@pytest.fixture
def beta_symptom_findings(frontend_zone):
    """Beta agent: symptom = infinite spinner."""
    return AgentFindings(
        agent_name='beta',
        session_id='MA-001',
        zone=frontend_zone,
        findings=[
            Finding(
                description='Frontend shows infinite loading spinner',
                classification='symptom',
                evidence=[
                    Evidence(
                        description='No timeout on fetch call',
                        evidence_type=EvidenceType.CODE_ANALYSIS,
                        source='hooks/useDataFetch.js:45',
                    ),
                ],
                confidence=0.7,
                files_involved=['hooks/useDataFetch.js'],
                proposed_fix='Add 5s timeout to fetch',
            ),
        ],
    )


@pytest.fixture
def gamma_disagreeing_findings(backend_zone):
    """Gamma agent: different root cause = memory leak."""
    return AgentFindings(
        agent_name='gamma',
        session_id='MA-001',
        zone=backend_zone,
        findings=[
            Finding(
                description='Memory leak in request handler allocations',
                classification='root_cause',
                evidence=[
                    Evidence(
                        description='Heap grows over time',
                        evidence_type=EvidenceType.THEORY,
                    ),
                ],
                confidence=0.4,
                files_involved=['api/handlers.py'],
                proposed_fix='Fix memory allocation pattern',
            ),
        ],
    )


@pytest.fixture
def overlapping_findings(backend_zone):
    """Agent with overlapping file scope."""
    return AgentFindings(
        agent_name='delta',
        session_id='MA-001',
        zone=backend_zone,
        findings=[
            Finding(
                description='Database driver version is outdated',
                classification='contributing',
                evidence=[
                    Evidence(
                        description='Old driver version',
                        evidence_type=EvidenceType.CODE_ANALYSIS,
                        source='config/database.py:1',
                    ),
                ],
                confidence=0.6,
                files_involved=['config/database.py'],
                proposed_fix='Upgrade database driver',
            ),
        ],
    )


# --- detect_conflicts Tests ---


class TestDetectConflicts:
    """Tests for conflict detection."""

    def test_no_conflicts_complementary_findings(
        self, alpha_root_cause_findings, beta_symptom_findings,
    ):
        """Complementary findings (root cause + symptom) have no conflicts."""
        conflicts = detect_conflicts([
            alpha_root_cause_findings,
            beta_symptom_findings,
        ])
        # No root cause disagreement (one is symptom)
        root_cause_conflicts = [
            c for c in conflicts
            if c.conflict_type == ConflictType.ROOT_CAUSE_DISAGREEMENT
        ]
        assert len(root_cause_conflicts) == 0

    def test_root_cause_disagreement_detected(
        self, alpha_root_cause_findings, gamma_disagreeing_findings,
    ):
        """Different root causes trigger disagreement conflict."""
        conflicts = detect_conflicts([
            alpha_root_cause_findings,
            gamma_disagreeing_findings,
        ])
        root_cause_conflicts = [
            c for c in conflicts
            if c.conflict_type == ConflictType.ROOT_CAUSE_DISAGREEMENT
        ]
        assert len(root_cause_conflicts) >= 1
        assert root_cause_conflicts[0].agent_a == 'alpha'
        assert root_cause_conflicts[0].agent_b == 'gamma'

    def test_scope_overlap_detected(
        self, alpha_root_cause_findings, overlapping_findings,
    ):
        """Overlapping file scope with different conclusions triggers conflict."""
        conflicts = detect_conflicts([
            alpha_root_cause_findings,
            overlapping_findings,
        ])
        scope_conflicts = [
            c for c in conflicts
            if c.conflict_type == ConflictType.SCOPE_OVERLAP
        ]
        assert len(scope_conflicts) >= 1

    def test_classification_mismatch_detected(self, backend_zone):
        """Same file with different classifications triggers conflict."""
        agent_a = AgentFindings(
            agent_name='alpha',
            session_id='MA-001',
            zone=backend_zone,
            findings=[
                Finding(
                    description='Config issue in database module',
                    classification='root_cause',
                    confidence=0.8,
                    files_involved=['config/database.py'],
                ),
            ],
        )
        agent_b = AgentFindings(
            agent_name='beta',
            session_id='MA-001',
            zone=backend_zone,
            findings=[
                Finding(
                    description='Config problem is just a symptom',
                    classification='symptom',
                    confidence=0.5,
                    files_involved=['config/database.py'],
                ),
            ],
        )
        conflicts = detect_conflicts([agent_a, agent_b])
        classification_conflicts = [
            c for c in conflicts
            if c.conflict_type == ConflictType.CLASSIFICATION_MISMATCH
        ]
        assert len(classification_conflicts) >= 1

    def test_multiple_agent_pairs(
        self, alpha_root_cause_findings,
        beta_symptom_findings,
        gamma_disagreeing_findings,
    ):
        """Three agents generate pairwise conflict checks."""
        conflicts = detect_conflicts([
            alpha_root_cause_findings,
            beta_symptom_findings,
            gamma_disagreeing_findings,
        ])
        # At least alpha-gamma should disagree on root cause
        assert len(conflicts) >= 1

    def test_empty_findings_no_conflicts(self):
        """No findings means no conflicts."""
        conflicts = detect_conflicts([])
        assert conflicts == []

    def test_single_agent_no_conflicts(self, alpha_root_cause_findings):
        """Single agent cannot have conflicts."""
        conflicts = detect_conflicts([alpha_root_cause_findings])
        assert conflicts == []

    def test_conflict_ids_are_unique(
        self, alpha_root_cause_findings,
        gamma_disagreeing_findings,
        overlapping_findings,
    ):
        """All conflict IDs are unique."""
        conflicts = detect_conflicts([
            alpha_root_cause_findings,
            gamma_disagreeing_findings,
            overlapping_findings,
        ])
        ids = [c.conflict_id for c in conflicts]
        assert len(ids) == len(set(ids))

    def test_evidence_contradiction_detected(self, backend_zone):
        """Evidence from same source with different conclusions detected."""
        agent_a = AgentFindings(
            agent_name='alpha',
            session_id='MA-001',
            zone=backend_zone,
            findings=[
                Finding(
                    description='Pool is undersized for traffic',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='Pool config is wrong',
                            evidence_type=EvidenceType.CODE_ANALYSIS,
                            source='config/database.py:12',
                        ),
                    ],
                    confidence=0.9,
                ),
            ],
        )
        agent_b = AgentFindings(
            agent_name='beta',
            session_id='MA-001',
            zone=backend_zone,
            findings=[
                Finding(
                    description='Driver version causing connection drops',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='Driver changelog shows known bug',
                            evidence_type=EvidenceType.LOG_CORRELATION,
                            source='config/database.py:12',
                        ),
                    ],
                    confidence=0.6,
                ),
            ],
        )
        conflicts = detect_conflicts([agent_a, agent_b])
        evidence_conflicts = [
            c for c in conflicts
            if c.conflict_type == ConflictType.EVIDENCE_CONTRADICTION
        ]
        assert len(evidence_conflicts) >= 1


# --- resolve_conflict_by_evidence Tests ---


class TestResolveConflictByEvidence:
    """Tests for evidence-weighted conflict resolution."""

    def test_resolve_clear_winner(self):
        """Clear evidence winner resolves conflict."""
        # Strong evidence: reproducible + code analysis
        finding_a = Finding(
            description='Pool size is the problem',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Reproduced',
                    evidence_type=EvidenceType.REPRODUCIBLE,
                ),
                Evidence(
                    description='Found in code',
                    evidence_type=EvidenceType.CODE_ANALYSIS,
                ),
            ],
            confidence=0.9,
        )
        # Weak evidence: theory only
        finding_b = Finding(
            description='Memory leak is the problem',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Maybe',
                    evidence_type=EvidenceType.THEORY,
                ),
            ],
            confidence=0.3,
        )

        conflict = Conflict(
            conflict_id='C-001',
            conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
            agent_a='alpha',
            agent_b='gamma',
            finding_a=finding_a,
            finding_b=finding_b,
            description='Root cause disagreement',
        )

        resolved = resolve_conflict_by_evidence(conflict)
        assert resolved.is_resolved
        assert resolved.resolution == ConflictResolution.EVIDENCE_WEIGHTED
        assert resolved.resolved_finding == finding_a
        assert 'alpha' in resolved.resolution_rationale

    def test_resolve_too_close_escalates(self):
        """Close evidence weights escalate to human."""
        finding_a = Finding(
            description='Issue A',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Code analysis',
                    evidence_type=EvidenceType.CODE_ANALYSIS,
                ),
            ],
            confidence=0.7,
        )
        finding_b = Finding(
            description='Issue B',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Log correlation',
                    evidence_type=EvidenceType.LOG_CORRELATION,
                ),
            ],
            confidence=0.6,
        )

        conflict = Conflict(
            conflict_id='C-002',
            conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
            agent_a='alpha',
            agent_b='beta',
            finding_a=finding_a,
            finding_b=finding_b,
            description='Close call',
        )

        resolved = resolve_conflict_by_evidence(conflict)
        assert resolved.resolution == ConflictResolution.HUMAN_ESCALATED
        assert 'too close' in resolved.resolution_rationale.lower()

    def test_resolve_b_wins(self):
        """Agent B can win if they have stronger evidence."""
        finding_a = Finding(
            description='Weak theory',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Guess',
                    evidence_type=EvidenceType.UNSUBSTANTIATED,
                ),
            ],
            confidence=0.2,
        )
        finding_b = Finding(
            description='Strong finding',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Reproduced consistently',
                    evidence_type=EvidenceType.REPRODUCIBLE,
                ),
            ],
            confidence=0.95,
        )

        conflict = Conflict(
            conflict_id='C-003',
            conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
            agent_a='alpha',
            agent_b='beta',
            finding_a=finding_a,
            finding_b=finding_b,
            description='B should win',
        )

        resolved = resolve_conflict_by_evidence(conflict)
        assert resolved.resolved_finding == finding_b
        assert 'beta' in resolved.resolution_rationale


# --- calculate_finding_weight Tests ---


class TestCalculateFindingWeight:
    """Tests for evidence weight calculation."""

    def test_reproducible_high_weight(self):
        """Reproducible evidence has highest weight."""
        finding = Finding(
            description='Reproduced bug',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Reproduced',
                    evidence_type=EvidenceType.REPRODUCIBLE,
                ),
            ],
            confidence=1.0,
        )
        weight = calculate_finding_weight(finding)
        assert weight > 0.8

    def test_unsubstantiated_low_weight(self):
        """Unsubstantiated evidence has lowest weight."""
        finding = Finding(
            description='Just a guess',
            classification='theory',
            evidence=[
                Evidence(
                    description='Maybe',
                    evidence_type=EvidenceType.UNSUBSTANTIATED,
                ),
            ],
            confidence=0.1,
        )
        weight = calculate_finding_weight(finding)
        assert weight < 0.2

    def test_no_evidence_uses_confidence(self):
        """No evidence relies on confidence alone."""
        finding = Finding(
            description='No evidence',
            classification='root_cause',
            confidence=0.5,
        )
        weight = calculate_finding_weight(finding)
        # 0.0 * 0.6 + 0.5 * 0.4 = 0.2
        assert weight == pytest.approx(0.2)

    def test_weight_range(self):
        """Weight is always between 0 and 1."""
        for etype in EvidenceType:
            for conf in [0.0, 0.5, 1.0]:
                finding = Finding(
                    description='Test',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='Test',
                            evidence_type=etype,
                        ),
                    ],
                    confidence=conf,
                )
                weight = calculate_finding_weight(finding)
                assert 0.0 <= weight <= 1.0


# --- get_conflict_summary Tests ---


class TestGetConflictSummary:
    """Tests for conflict summary generation."""

    def test_empty_summary(self):
        """Empty conflicts produces zero summary."""
        summary = get_conflict_summary([])
        assert summary['total'] == 0
        assert summary['resolved'] == 0
        assert summary['unresolved'] == 0

    def test_summary_counts(self):
        """Summary counts are correct."""
        finding = Finding(description='test', classification='root_cause')
        conflicts = [
            Conflict(
                conflict_id='C-001',
                conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
                agent_a='a',
                agent_b='b',
                finding_a=finding,
                finding_b=finding,
                description='Test',
                resolution=ConflictResolution.EVIDENCE_WEIGHTED,
            ),
            Conflict(
                conflict_id='C-002',
                conflict_type=ConflictType.SCOPE_OVERLAP,
                agent_a='a',
                agent_b='c',
                finding_a=finding,
                finding_b=finding,
                description='Test 2',
            ),
        ]
        summary = get_conflict_summary(conflicts)
        assert summary['total'] == 2
        assert summary['resolved'] == 1
        assert summary['unresolved'] == 1

    def test_summary_by_type(self):
        """Summary groups by conflict type."""
        finding = Finding(description='test', classification='root_cause')
        conflicts = [
            Conflict(
                conflict_id='C-001',
                conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
                agent_a='a',
                agent_b='b',
                finding_a=finding,
                finding_b=finding,
                description='Test',
            ),
            Conflict(
                conflict_id='C-002',
                conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
                agent_a='a',
                agent_b='c',
                finding_a=finding,
                finding_b=finding,
                description='Test 2',
            ),
        ]
        summary = get_conflict_summary(conflicts)
        assert summary['by_type']['root_cause_disagreement'] == 2

    def test_summary_escalation_flag(self):
        """Summary flags when escalation needed."""
        finding = Finding(description='test', classification='root_cause')
        conflicts = [
            Conflict(
                conflict_id='C-001',
                conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
                agent_a='a',
                agent_b='b',
                finding_a=finding,
                finding_b=finding,
                description='Test',
                resolution=ConflictResolution.HUMAN_ESCALATED,
            ),
        ]
        summary = get_conflict_summary(conflicts)
        assert summary['requires_escalation'] is True


# --- Helper Function Tests ---


class TestHelperFunctions:
    """Tests for internal helper functions."""

    def test_findings_disagree_different(self):
        """Different descriptions disagree."""
        a = Finding(description='Pool size is wrong', classification='root_cause')
        b = Finding(description='Memory leak detected', classification='root_cause')
        assert _findings_disagree(a, b) is True

    def test_findings_disagree_same(self):
        """Same description does not disagree."""
        a = Finding(description='Pool size is wrong', classification='root_cause')
        b = Finding(description='Pool size is wrong', classification='root_cause')
        assert _findings_disagree(a, b) is False

    def test_findings_disagree_similar(self):
        """Similar descriptions with high overlap do not disagree."""
        a = Finding(
            description='Connection pool size configuration problem',
            classification='root_cause',
        )
        b = Finding(
            description='Connection pool size misconfigured',
            classification='root_cause',
        )
        assert _findings_disagree(a, b) is False

    def test_evidence_contradicts_same_source(self):
        """Same source with different conclusions contradicts."""
        a = Finding(
            description='Pool is undersized',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Config wrong',
                    evidence_type=EvidenceType.CODE_ANALYSIS,
                    source='config/db.py:10',
                ),
            ],
        )
        b = Finding(
            description='Driver version causing drops',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Driver bug',
                    evidence_type=EvidenceType.CODE_ANALYSIS,
                    source='config/db.py:10',
                ),
            ],
        )
        assert _evidence_contradicts(a, b) is True

    def test_evidence_no_contradiction_different_sources(self):
        """Different sources do not contradict."""
        a = Finding(
            description='Pool issue',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Config wrong',
                    evidence_type=EvidenceType.CODE_ANALYSIS,
                    source='config/db.py',
                ),
            ],
        )
        b = Finding(
            description='UI issue',
            classification='symptom',
            evidence=[
                Evidence(
                    description='UI lag',
                    evidence_type=EvidenceType.CODE_ANALYSIS,
                    source='components/App.tsx',
                ),
            ],
        )
        assert _evidence_contradicts(a, b) is False

    def test_evidence_no_contradiction_no_sources(self):
        """No sources means no contradiction."""
        a = Finding(
            description='Issue A',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Something',
                    evidence_type=EvidenceType.THEORY,
                ),
            ],
        )
        b = Finding(
            description='Issue B',
            classification='root_cause',
            evidence=[
                Evidence(
                    description='Something else',
                    evidence_type=EvidenceType.THEORY,
                ),
            ],
        )
        assert _evidence_contradicts(a, b) is False

    def test_file_overlap(self):
        """File overlap detected correctly."""
        a = Finding(
            description='A',
            classification='root_cause',
            files_involved=['config/db.py', 'api/handlers.py'],
        )
        b = Finding(
            description='B',
            classification='root_cause',
            files_involved=['config/db.py', 'utils/helpers.py'],
        )
        overlap = _get_file_overlap(a, b)
        assert overlap == ['config/db.py']

    def test_no_file_overlap(self):
        """No overlap returns empty list."""
        a = Finding(
            description='A',
            classification='root_cause',
            files_involved=['api/handlers.py'],
        )
        b = Finding(
            description='B',
            classification='root_cause',
            files_involved=['ui/App.tsx'],
        )
        overlap = _get_file_overlap(a, b)
        assert overlap == []

    def test_classifications_conflict_root_vs_symptom(self):
        """Root cause vs symptom is a conflict."""
        a = Finding(description='A', classification='root_cause')
        b = Finding(description='B', classification='symptom')
        assert _classifications_conflict(a, b) is True

    def test_classifications_conflict_root_vs_contributing(self):
        """Root cause vs contributing is a conflict."""
        a = Finding(description='A', classification='root_cause')
        b = Finding(description='B', classification='contributing')
        assert _classifications_conflict(a, b) is True

    def test_classifications_no_conflict_same(self):
        """Same classification is not a conflict."""
        a = Finding(description='A', classification='root_cause')
        b = Finding(description='B', classification='root_cause')
        assert _classifications_conflict(a, b) is False

    def test_classifications_no_conflict_symptom_contributing(self):
        """Symptom vs contributing is not classified as conflicting."""
        a = Finding(description='A', classification='symptom')
        b = Finding(description='B', classification='contributing')
        assert _classifications_conflict(a, b) is False
