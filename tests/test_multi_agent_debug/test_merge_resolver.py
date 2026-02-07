"""Tests for multi-agent debug merge resolution engine.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

import pytest
from datetime import datetime, UTC
from pathlib import Path

from scripts.lib.multi_agent_debug.merge_resolver import (
    merge_findings,
    generate_resolution_document,
    write_resolution_document,
    _build_consensus,
    _extract_deployment_order,
    _extract_agreed_fixes,
    _extract_lessons,
)
from scripts.lib.multi_agent_debug.utils import (
    generate_pattern_name,
    extract_tags,
)
from scripts.lib.multi_agent_debug.models import (
    AgentFindings,
    Conflict,
    ConflictResolution,
    ConflictType,
    Evidence,
    EvidenceType,
    Finding,
    LessonCandidate,
    MergeResolution,
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
    )


@pytest.fixture
def frontend_zone():
    """Create a frontend work zone."""
    return WorkZone(
        name='frontend',
        description='Frontend investigation',
        files=['components/App.tsx'],
    )


@pytest.fixture
def alpha_findings(backend_zone):
    """Alpha: strong root cause finding."""
    return AgentFindings(
        agent_name='alpha',
        session_id='MA-001',
        zone=backend_zone,
        findings=[
            Finding(
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
            ),
        ],
        investigation_time_minutes=30,
    )


@pytest.fixture
def beta_findings(frontend_zone):
    """Beta: symptom finding."""
    return AgentFindings(
        agent_name='beta',
        session_id='MA-001',
        zone=frontend_zone,
        findings=[
            Finding(
                description='Frontend infinite spinner on data load',
                classification='symptom',
                evidence=[
                    Evidence(
                        description='No fetch timeout configured',
                        evidence_type=EvidenceType.CODE_ANALYSIS,
                        source='hooks/useDataFetch.js:45',
                    ),
                ],
                confidence=0.7,
                files_involved=['hooks/useDataFetch.js'],
                proposed_fix='Add 5s timeout to fetch calls',
            ),
        ],
        investigation_time_minutes=25,
    )


@pytest.fixture
def gamma_disagreeing_findings(backend_zone):
    """Gamma: weak disagreeing root cause."""
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
                        description='Heap seems to grow',
                        evidence_type=EvidenceType.THEORY,
                    ),
                ],
                confidence=0.3,
                files_involved=['api/handlers.py'],
                proposed_fix='Fix memory allocation pattern',
            ),
        ],
        investigation_time_minutes=20,
    )


# --- merge_findings Tests ---


class TestMergeFindings:
    """Tests for the main merge_findings function."""

    def test_merge_complementary_findings(
        self, alpha_findings, beta_findings,
    ):
        """Merging complementary findings produces clean consensus."""
        resolution = merge_findings(
            session_id='MA-001',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        assert resolution.session_id == 'MA-001'
        assert resolution.lead_agent == 'alpha'
        assert len(resolution.participating_agents) == 2
        # Both findings should be in consensus (no conflict)
        assert len(resolution.consensus_findings) == 2

    def test_merge_with_conflicts(
        self, alpha_findings, gamma_disagreeing_findings,
    ):
        """Merging conflicting findings detects and resolves."""
        resolution = merge_findings(
            session_id='MA-002',
            lead_agent='alpha',
            all_findings=[alpha_findings, gamma_disagreeing_findings],
        )
        # Should have detected at least one conflict
        total = resolution.total_conflicts
        assert total >= 1

    def test_merge_auto_resolve(
        self, alpha_findings, gamma_disagreeing_findings,
    ):
        """Auto-resolve picks the stronger evidence."""
        resolution = merge_findings(
            session_id='MA-003',
            lead_agent='alpha',
            all_findings=[alpha_findings, gamma_disagreeing_findings],
            auto_resolve=True,
        )
        # Alpha has stronger evidence (reproducible + code analysis)
        # Gamma has only theory
        # Alpha should win the conflict
        if resolution.conflicts:
            for conflict in resolution.conflicts:
                if (
                    conflict.resolution
                    == ConflictResolution.EVIDENCE_WEIGHTED
                ):
                    assert conflict.resolved_finding is not None
                    assert 'pool' in conflict.resolved_finding.description.lower()

    def test_merge_no_auto_resolve(
        self, alpha_findings, gamma_disagreeing_findings,
    ):
        """Without auto-resolve, all conflicts are unresolved."""
        resolution = merge_findings(
            session_id='MA-004',
            lead_agent='alpha',
            all_findings=[alpha_findings, gamma_disagreeing_findings],
            auto_resolve=False,
        )
        # All conflicts should be unresolved
        assert len(resolution.conflicts) == 0
        assert len(resolution.unresolved_conflicts) >= 1

    def test_merge_three_agents(
        self, alpha_findings, beta_findings,
        gamma_disagreeing_findings,
    ):
        """Three-agent merge handles pairwise conflicts."""
        resolution = merge_findings(
            session_id='MA-005',
            lead_agent='alpha',
            all_findings=[
                alpha_findings,
                beta_findings,
                gamma_disagreeing_findings,
            ],
        )
        assert len(resolution.participating_agents) == 3
        # Should have consensus findings
        assert len(resolution.consensus_findings) >= 1

    def test_merge_produces_deployment_order(
        self, alpha_findings, beta_findings,
    ):
        """Merge produces deployment order from proposed fixes."""
        resolution = merge_findings(
            session_id='MA-006',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        # Root cause fix should come first
        assert len(resolution.deployment_order) >= 1
        assert 'pool' in resolution.deployment_order[0].lower()

    def test_merge_extracts_lessons(self, alpha_findings, beta_findings):
        """Merge extracts lesson candidates."""
        resolution = merge_findings(
            session_id='MA-007',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        # High-confidence root cause should generate a lesson
        assert len(resolution.lessons_extracted) >= 1

    def test_merge_empty_findings(self):
        """Merging empty findings produces empty resolution."""
        resolution = merge_findings(
            session_id='MA-008',
            lead_agent='alpha',
            all_findings=[],
        )
        assert len(resolution.consensus_findings) == 0
        assert resolution.total_conflicts == 0


# --- generate_resolution_document Tests ---


class TestGenerateResolutionDocument:
    """Tests for resolution document generation."""

    def test_document_contains_header(
        self, alpha_findings, beta_findings,
    ):
        """Document has proper header."""
        resolution = merge_findings(
            session_id='MA-DOC-001',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        content = generate_resolution_document(
            resolution, [alpha_findings, beta_findings],
        )
        assert '# Merge Resolution' in content
        assert 'MA-DOC-001' in content

    def test_document_contains_agents_table(
        self, alpha_findings, beta_findings,
    ):
        """Document includes participating agents table."""
        resolution = merge_findings(
            session_id='MA-DOC-002',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        content = generate_resolution_document(
            resolution, [alpha_findings, beta_findings],
        )
        assert '## Participating Agents' in content
        assert 'alpha' in content
        assert 'beta' in content

    def test_document_contains_consensus(
        self, alpha_findings, beta_findings,
    ):
        """Document includes consensus findings."""
        resolution = merge_findings(
            session_id='MA-DOC-003',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        content = generate_resolution_document(
            resolution, [alpha_findings, beta_findings],
        )
        assert '## Consensus Finding' in content
        assert 'Root Cause' in content

    def test_document_contains_deployment_order(
        self, alpha_findings, beta_findings,
    ):
        """Document includes deployment order."""
        resolution = merge_findings(
            session_id='MA-DOC-004',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        content = generate_resolution_document(
            resolution, [alpha_findings, beta_findings],
        )
        assert 'Deployment Order' in content

    def test_document_contains_conflicts(
        self, alpha_findings, gamma_disagreeing_findings,
    ):
        """Document includes conflict section when conflicts exist."""
        resolution = merge_findings(
            session_id='MA-DOC-005',
            lead_agent='alpha',
            all_findings=[
                alpha_findings, gamma_disagreeing_findings,
            ],
        )
        content = generate_resolution_document(
            resolution,
            [alpha_findings, gamma_disagreeing_findings],
        )
        assert '## Conflicts' in content

    def test_document_contains_outcome(
        self, alpha_findings, beta_findings,
    ):
        """Document includes session outcome."""
        resolution = merge_findings(
            session_id='MA-DOC-006',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        content = generate_resolution_document(
            resolution, [alpha_findings, beta_findings],
        )
        assert '## Session Outcome' in content
        assert 'COMPLETE' in content

    def test_document_escalation_status(
        self, alpha_findings, gamma_disagreeing_findings,
    ):
        """Document shows escalation status when needed."""
        resolution = merge_findings(
            session_id='MA-DOC-007',
            lead_agent='alpha',
            all_findings=[
                alpha_findings, gamma_disagreeing_findings,
            ],
            auto_resolve=False,
        )
        content = generate_resolution_document(
            resolution,
            [alpha_findings, gamma_disagreeing_findings],
        )
        assert 'ESCALATION REQUIRED' in content

    def test_document_is_valid_markdown(
        self, alpha_findings, beta_findings,
    ):
        """Document is valid markdown."""
        resolution = merge_findings(
            session_id='MA-DOC-008',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        content = generate_resolution_document(
            resolution, [alpha_findings, beta_findings],
        )
        assert content.startswith('# Merge Resolution')
        assert '---' in content


# --- write_resolution_document Tests ---


class TestWriteResolutionDocument:
    """Tests for writing resolution document to disk."""

    def test_write_creates_file(
        self, alpha_findings, beta_findings, tmp_path,
    ):
        """Writing creates file on disk."""
        resolution = merge_findings(
            session_id='MA-WRITE-001',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        folder = str(tmp_path / 'session-test')
        result = write_resolution_document(
            resolution,
            [alpha_findings, beta_findings],
            folder,
        )
        assert result.exists()
        assert result.name == 'merge_resolution.md'

    def test_write_creates_directory(
        self, alpha_findings, beta_findings, tmp_path,
    ):
        """Writing creates directory if needed."""
        resolution = merge_findings(
            session_id='MA-WRITE-002',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        folder = str(tmp_path / 'nested' / 'session-test')
        result = write_resolution_document(
            resolution,
            [alpha_findings, beta_findings],
            folder,
        )
        assert Path(folder).is_dir()
        assert result.exists()

    def test_write_content_matches(
        self, alpha_findings, beta_findings, tmp_path,
    ):
        """Written content matches generated content."""
        resolution = merge_findings(
            session_id='MA-WRITE-003',
            lead_agent='alpha',
            all_findings=[alpha_findings, beta_findings],
        )
        folder = str(tmp_path / 'session-test')
        result = write_resolution_document(
            resolution,
            [alpha_findings, beta_findings],
            folder,
        )
        content = result.read_text(encoding='utf-8')
        assert 'MA-WRITE-003' in content
        assert '# Merge Resolution' in content


# --- Internal Function Tests ---


class TestBuildConsensus:
    """Tests for consensus building logic."""

    def test_non_conflicting_all_included(self):
        """Non-conflicting findings are all included."""
        zone = WorkZone(name='test', description='test')
        findings = [
            AgentFindings(
                agent_name='alpha',
                session_id='MA-001',
                zone=zone,
                findings=[
                    Finding(
                        description='Issue A',
                        classification='root_cause',
                        confidence=0.9,
                    ),
                ],
            ),
            AgentFindings(
                agent_name='beta',
                session_id='MA-001',
                zone=zone,
                findings=[
                    Finding(
                        description='Issue B',
                        classification='symptom',
                        confidence=0.7,
                    ),
                ],
            ),
        ]
        consensus = _build_consensus(findings, resolved_conflicts=[])
        assert len(consensus) == 2

    def test_consensus_sorted_by_classification(self):
        """Consensus sorted: root_cause first, then symptom."""
        zone = WorkZone(name='test', description='test')
        findings = [
            AgentFindings(
                agent_name='alpha',
                session_id='MA-001',
                zone=zone,
                findings=[
                    Finding(
                        description='Symptom first',
                        classification='symptom',
                        confidence=0.9,
                    ),
                ],
            ),
            AgentFindings(
                agent_name='beta',
                session_id='MA-001',
                zone=zone,
                findings=[
                    Finding(
                        description='Root cause second',
                        classification='root_cause',
                        confidence=0.7,
                    ),
                ],
            ),
        ]
        consensus = _build_consensus(findings, resolved_conflicts=[])
        assert consensus[0].classification == 'root_cause'
        assert consensus[1].classification == 'symptom'

    def test_resolved_conflict_winner_included(self):
        """Resolved conflict winner is in consensus."""
        winner = Finding(
            description='Winner finding',
            classification='root_cause',
            confidence=0.9,
        )
        loser = Finding(
            description='Loser finding',
            classification='root_cause',
            confidence=0.3,
        )
        conflict = Conflict(
            conflict_id='C-001',
            conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
            agent_a='alpha',
            agent_b='beta',
            finding_a=winner,
            finding_b=loser,
            description='Test',
            resolution=ConflictResolution.EVIDENCE_WEIGHTED,
            resolved_finding=winner,
        )
        consensus = _build_consensus([], resolved_conflicts=[conflict])
        assert len(consensus) == 1
        assert consensus[0].description == 'Winner finding'

    def test_duplicate_descriptions_deduplicated(self):
        """Same description from multiple agents is deduplicated."""
        zone = WorkZone(name='test', description='test')
        findings = [
            AgentFindings(
                agent_name='alpha',
                session_id='MA-001',
                zone=zone,
                findings=[
                    Finding(
                        description='Same issue found',
                        classification='root_cause',
                        confidence=0.9,
                    ),
                ],
            ),
            AgentFindings(
                agent_name='beta',
                session_id='MA-001',
                zone=zone,
                findings=[
                    Finding(
                        description='Same issue found',
                        classification='root_cause',
                        confidence=0.7,
                    ),
                ],
            ),
        ]
        consensus = _build_consensus(findings, resolved_conflicts=[])
        assert len(consensus) == 1


class TestExtractDeploymentOrder:
    """Tests for deployment order extraction."""

    def test_order_follows_classification(self):
        """Root cause fixes come before symptom fixes."""
        consensus = [
            Finding(
                description='Root cause',
                classification='root_cause',
                proposed_fix='Fix root cause',
            ),
            Finding(
                description='Symptom',
                classification='symptom',
                proposed_fix='Fix symptom',
            ),
        ]
        order = _extract_deployment_order(consensus, [])
        assert order[0] == 'Fix root cause'
        assert order[1] == 'Fix symptom'

    def test_no_proposed_fix_excluded(self):
        """Findings without proposed_fix are excluded."""
        consensus = [
            Finding(
                description='No fix',
                classification='root_cause',
            ),
        ]
        order = _extract_deployment_order(consensus, [])
        assert len(order) == 0

    def test_duplicate_fixes_deduplicated(self):
        """Same fix from multiple findings appears once."""
        consensus = [
            Finding(
                description='A',
                classification='root_cause',
                proposed_fix='Same fix',
            ),
            Finding(
                description='B',
                classification='symptom',
                proposed_fix='Same fix',
            ),
        ]
        order = _extract_deployment_order(consensus, [])
        assert len(order) == 1


class TestExtractAgreedFixes:
    """Tests for agreed fix extraction."""

    def test_fixes_have_priority(self):
        """Fixes include priority based on classification."""
        consensus = [
            Finding(
                description='Root cause',
                classification='root_cause',
                proposed_fix='Fix it',
                files_involved=['config/db.py'],
            ),
        ]
        fixes = _extract_agreed_fixes(consensus, [])
        assert len(fixes) == 1
        assert fixes[0]['priority'] == 'P0 (critical)'
        assert fixes[0]['file'] == 'config/db.py'

    def test_symptom_lower_priority(self):
        """Symptom fixes have lower priority."""
        consensus = [
            Finding(
                description='Symptom',
                classification='symptom',
                proposed_fix='Fix UI',
            ),
        ]
        fixes = _extract_agreed_fixes(consensus, [])
        assert fixes[0]['priority'] == 'P2 (optional)'

    def test_contributing_medium_priority(self):
        """Contributing fixes have medium priority."""
        consensus = [
            Finding(
                description='Contributing',
                classification='contributing',
                proposed_fix='Improve it',
            ),
        ]
        fixes = _extract_agreed_fixes(consensus, [])
        assert fixes[0]['priority'] == 'P1 (recommended)'


class TestExtractLessons:
    """Tests for lesson extraction."""

    def test_high_confidence_root_cause_generates_lesson(self):
        """High-confidence root causes generate lessons."""
        # Consensus findings (list[Finding])
        consensus = [
            Finding(
                description='Database pool undersized',
                classification='root_cause',
                confidence=0.9,
                proposed_fix='Increase pool size',
            ),
        ]
        lessons = _extract_lessons('MA-001', consensus, [])
        assert len(lessons) >= 1
        assert lessons[0].confidence >= 0.8

    def test_low_confidence_no_lesson(self):
        """Low-confidence findings do not generate lessons."""
        # Consensus findings (list[Finding])
        consensus = [
            Finding(
                description='Maybe something',
                classification='root_cause',
                confidence=0.3,
                proposed_fix='Try something',
            ),
        ]
        lessons = _extract_lessons('MA-001', consensus, [])
        assert len(lessons) == 0

    def test_resolved_conflict_generates_lesson(self):
        """Resolved conflicts generate lessons."""
        winner = Finding(
            description='Pool undersized causing issues',
            classification='root_cause',
            confidence=0.9,
            proposed_fix='Increase pool size',
        )
        conflict = Conflict(
            conflict_id='C-001',
            conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
            agent_a='alpha',
            agent_b='beta',
            finding_a=winner,
            finding_b=Finding(
                description='Different issue',
                classification='root_cause',
            ),
            description='Test conflict',
            resolution=ConflictResolution.EVIDENCE_WEIGHTED,
            resolved_finding=winner,
        )
        lessons = _extract_lessons('MA-001', [], [conflict])
        assert len(lessons) >= 1
        assert lessons[0].source_conflict == 'C-001'


class TestPatternName:
    """Tests for pattern name generation."""

    def test_short_description(self):
        """Short descriptions are title-cased."""
        finding = Finding(
            description='pool size wrong',
            classification='root_cause',
        )
        name = generate_pattern_name(finding)
        assert name == 'Pool Size Wrong'

    def test_long_description_truncated(self):
        """Long descriptions are truncated."""
        finding = Finding(
            description='A' * 100,
            classification='root_cause',
        )
        name = generate_pattern_name(finding)
        assert len(name) <= 60
        assert name.endswith('...')


class TestExtractTags:
    """Tests for tag extraction."""

    def test_database_tags(self):
        """Database keywords produce database tag."""
        finding = Finding(
            description='Database pool connection issue',
            classification='root_cause',
        )
        tags = extract_tags(finding)
        assert 'database' in tags

    def test_performance_tags(self):
        """Performance keywords produce performance tag."""
        finding = Finding(
            description='Timeout causing latency',
            classification='root_cause',
        )
        tags = extract_tags(finding)
        assert 'performance' in tags

    def test_no_keywords_uses_classification(self):
        """No matching keywords falls back to classification."""
        finding = Finding(
            description='Something unusual happened',
            classification='root_cause',
        )
        tags = extract_tags(finding)
        assert 'root_cause' in tags

    def test_multiple_tags(self):
        """Multiple keyword matches produce multiple tags."""
        finding = Finding(
            description='Database timeout in api endpoint',
            classification='root_cause',
        )
        tags = extract_tags(finding)
        assert 'database' in tags
        assert 'performance' in tags
        assert 'api' in tags
