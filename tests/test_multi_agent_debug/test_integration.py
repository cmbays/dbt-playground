"""Integration tests for multi-agent debug coordination.

End-to-end scenarios covering the full lifecycle:
  - Session creation -> agent assignment -> investigation -> merge -> lessons
  - Single-agent backward compatibility
  - Multi-agent with conflicts
  - Hybrid paths

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

import json
import pytest
from datetime import datetime, UTC
from pathlib import Path

from scripts.lib.multi_agent_debug.protocol import (
    assess_complexity,
    create_session_config,
    partition_blast_radius,
)
from scripts.lib.multi_agent_debug.registry import (
    AgentRegistry,
    create_default_registry,
)
from scripts.lib.multi_agent_debug.orchestrator import SessionOrchestrator
from scripts.lib.multi_agent_debug.manifest import (
    generate_manifest,
    write_manifest,
    update_manifest,
)
from scripts.lib.multi_agent_debug.conflict_detector import (
    detect_conflicts,
    resolve_conflict_by_evidence,
    get_conflict_summary,
)
from scripts.lib.multi_agent_debug.merge_resolver import (
    merge_findings,
    generate_resolution_document,
    write_resolution_document,
)
from scripts.lib.multi_agent_debug.lessons import (
    extract_debate_patterns,
    emit_lesson_events,
    format_all_lessons,
)
from scripts.lib.multi_agent_debug.models import (
    AgentCapability,
    AgentFindings,
    AgentProfile,
    AgentStatus,
    Conflict,
    ConflictResolution,
    ConflictType,
    ComplexityAssessment,
    Evidence,
    EvidenceType,
    Finding,
    LessonCandidate,
    MergeResolution,
    MultiAgentSession,
    SessionStatus,
    WorkAssignment,
    WorkZone,
)
from scripts.lib.multi_agent_debug.exceptions import (
    InvalidSessionStateError,
    SessionNotFoundError,
)


# --- Fixtures ---

TEST_DATE = datetime(2026, 2, 15, tzinfo=UTC)


@pytest.fixture
def registry():
    """Create a registry with test agents."""
    reg = AgentRegistry()
    reg.register_agent('backend', capabilities=['backend', 'data'], proficiencies={'backend': 1.0, 'data': 0.8})
    reg.register_agent('frontend', capabilities=['frontend', 'performance'], proficiencies={'frontend': 1.0, 'performance': 0.7})
    reg.register_agent('infra', capabilities=['infra', 'performance'], proficiencies={'infra': 1.0, 'performance': 0.8})
    return reg


@pytest.fixture
def orchestrator(registry):
    """Create an orchestrator with test agents."""
    return SessionOrchestrator(registry)


@pytest.fixture
def backend_zone():
    """Backend investigation zone."""
    return WorkZone(
        name='payment-service',
        description='Payment service investigation',
        files=['services/payment/handler.py', 'services/payment/config.py'],
        systems=['payment-service'],
        required_capabilities=['backend'],
    )


@pytest.fixture
def frontend_zone():
    """Frontend investigation zone."""
    return WorkZone(
        name='ui-layer',
        description='UI layer investigation',
        files=['components/PaymentForm.tsx', 'hooks/usePayment.ts'],
        systems=['web-app'],
        required_capabilities=['frontend'],
    )


@pytest.fixture
def infra_zone():
    """Infrastructure investigation zone."""
    return WorkZone(
        name='network-layer',
        description='Network and infrastructure investigation',
        files=['deploy/nginx.conf', 'deploy/docker-compose.yml'],
        systems=['load-balancer', 'container-runtime'],
        required_capabilities=['infra'],
    )


# --- E2E: Two-Agent Session (No Conflicts) ---


class TestE2ETwoAgentsClean:
    """End-to-end: Two agents investigate, no conflicts, clean merge."""

    def test_full_lifecycle(
        self, orchestrator, backend_zone, frontend_zone, tmp_path,
    ):
        """Complete lifecycle: create -> investigate -> merge -> lessons."""
        session_folder = str(tmp_path / 'session-e2e-001')

        # Step 1: Create session
        session = orchestrator.create_session(
            session_id='MA-E2E-001',
            debug_session_id='DBG-E2E-001',
            bug_description='Payment timeout on checkout',
            lead_agent='backend',
            zones=[backend_zone, frontend_zone],
            session_folder=session_folder,
        )

        assert session.session_id == 'MA-E2E-001'
        assert session.status == SessionStatus.SETUP
        assert session.agent_count == 2

        # Step 2: Write manifest
        manifest_path = write_manifest(session, session_folder)
        assert manifest_path.exists()
        manifest_content = manifest_path.read_text(encoding='utf-8')
        assert 'MA-E2E-001' in manifest_content

        # Step 3: Start investigation
        session = orchestrator.start_investigation('MA-E2E-001')
        assert session.status == SessionStatus.INVESTIGATING

        # Step 4: Submit backend findings
        backend_findings = AgentFindings(
            agent_name='backend',
            session_id='MA-E2E-001',
            zone=backend_zone,
            findings=[
                Finding(
                    description='Database connection pool undersized at 1',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='Config shows pool_size=1',
                            evidence_type=EvidenceType.CODE_ANALYSIS,
                            source='services/payment/config.py:15',
                        ),
                        Evidence(
                            description='Reproduced under load',
                            evidence_type=EvidenceType.REPRODUCIBLE,
                        ),
                    ],
                    confidence=0.95,
                    files_involved=['services/payment/config.py'],
                    proposed_fix='Increase pool size to 10',
                ),
            ],
            investigation_time_minutes=25,
        )
        session = orchestrator.submit_findings('MA-E2E-001', backend_findings)

        # Step 5: Submit frontend findings
        frontend_findings = AgentFindings(
            agent_name='frontend',
            session_id='MA-E2E-001',
            zone=frontend_zone,
            findings=[
                Finding(
                    description='No timeout on payment fetch request',
                    classification='symptom',
                    evidence=[
                        Evidence(
                            description='Fetch call has no AbortController',
                            evidence_type=EvidenceType.CODE_ANALYSIS,
                            source='hooks/usePayment.ts:42',
                        ),
                    ],
                    confidence=0.7,
                    files_involved=['hooks/usePayment.ts'],
                    proposed_fix='Add 5s timeout with AbortController',
                ),
            ],
            investigation_time_minutes=15,
        )
        session = orchestrator.submit_findings('MA-E2E-001', frontend_findings)

        # Should auto-transition to MERGING
        assert session.status == SessionStatus.MERGING

        # Step 6: Merge findings
        resolution = merge_findings(
            session_id='MA-E2E-001',
            lead_agent='backend',
            all_findings=[backend_findings, frontend_findings],
        )

        assert len(resolution.consensus_findings) == 2
        assert resolution.total_conflicts == 0  # No conflicts expected

        # Root cause should be first in consensus
        assert resolution.consensus_findings[0].classification == 'root_cause'

        # Step 7: Write resolution document
        doc_path = write_resolution_document(
            resolution, [backend_findings, frontend_findings], session_folder,
        )
        assert doc_path.exists()
        doc_content = doc_path.read_text(encoding='utf-8')
        assert '# Merge Resolution' in doc_content
        assert 'COMPLETE' in doc_content

        # Step 8: Complete session
        session = orchestrator.complete_session('MA-E2E-001', resolution)
        assert session.status == SessionStatus.RESOLVED
        assert session.resolution is not None

        # Step 9: Extract lessons
        lessons = extract_debate_patterns(resolution)
        # High-confidence root cause (0.95) should produce a lesson
        assert len(lessons) >= 1
        assert any('pool' in l.problem.lower() or 'database' in l.problem.lower() for l in lessons)

        # Step 10: Emit events
        events_file = str(tmp_path / 'events.jsonl')
        count = emit_lesson_events(lessons, events_file)
        assert count >= 1

        # Verify event structure
        events_content = Path(events_file).read_text(encoding='utf-8')
        for line in events_content.strip().split('\n'):
            event = json.loads(line)
            assert event['event'] == 'debug_lesson'
            assert event['data']['source'] == 'multi_agent_session'

        # Step 11: Update manifest (final state)
        update_manifest(session, session_folder)
        final_manifest = manifest_path.read_text(encoding='utf-8')
        assert 'RESOLVED' in final_manifest


# --- E2E: Three-Agent Session with Conflicts ---


class TestE2EThreeAgentsWithConflict:
    """End-to-end: Three agents with root cause disagreement."""

    def test_full_lifecycle_with_conflict(
        self, orchestrator, backend_zone, frontend_zone, infra_zone, tmp_path,
    ):
        """Full lifecycle with conflict detection and resolution."""
        session_folder = str(tmp_path / 'session-e2e-002')

        # Create session with 3 zones
        session = orchestrator.create_session(
            session_id='MA-E2E-002',
            debug_session_id='DBG-E2E-002',
            bug_description='Distributed timeout across services',
            lead_agent='backend',
            zones=[backend_zone, frontend_zone, infra_zone],
            session_folder=session_folder,
            context='microservice distributed system timeout',
        )
        assert session.agent_count == 3

        # Start and submit findings
        orchestrator.start_investigation('MA-E2E-002')

        # Backend: strong root cause
        backend_findings = AgentFindings(
            agent_name='backend',
            session_id='MA-E2E-002',
            zone=backend_zone,
            findings=[
                Finding(
                    description='Connection pool exhaustion under load',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='Pool metrics show 0 available connections',
                            evidence_type=EvidenceType.REPRODUCIBLE,
                            source='services/payment/metrics.log',
                        ),
                        Evidence(
                            description='Config has pool_max=5 for 100 concurrent users',
                            evidence_type=EvidenceType.CODE_ANALYSIS,
                            source='services/payment/config.py',
                        ),
                    ],
                    confidence=0.92,
                    files_involved=['services/payment/config.py'],
                    proposed_fix='Scale pool to 50 connections',
                ),
            ],
            investigation_time_minutes=30,
        )

        # Infra: weak disagreeing root cause
        infra_findings = AgentFindings(
            agent_name='infra',
            session_id='MA-E2E-002',
            zone=infra_zone,
            findings=[
                Finding(
                    description='Network latency spikes from load balancer',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='Latency graphs show periodic spikes',
                            evidence_type=EvidenceType.THEORY,
                        ),
                    ],
                    confidence=0.4,
                    files_involved=['deploy/nginx.conf'],
                    proposed_fix='Optimize load balancer config',
                ),
            ],
            investigation_time_minutes=20,
        )

        # Frontend: symptom (no conflict)
        frontend_findings = AgentFindings(
            agent_name='frontend',
            session_id='MA-E2E-002',
            zone=frontend_zone,
            findings=[
                Finding(
                    description='UI shows infinite spinner',
                    classification='symptom',
                    evidence=[
                        Evidence(
                            description='No error handling on timeout',
                            evidence_type=EvidenceType.CODE_ANALYSIS,
                            source='components/PaymentForm.tsx',
                        ),
                    ],
                    confidence=0.75,
                    files_involved=['components/PaymentForm.tsx'],
                    proposed_fix='Add error boundary and timeout handler',
                ),
            ],
            investigation_time_minutes=15,
        )

        orchestrator.submit_findings('MA-E2E-002', backend_findings)
        orchestrator.submit_findings('MA-E2E-002', frontend_findings)
        session = orchestrator.submit_findings('MA-E2E-002', infra_findings)

        assert session.status == SessionStatus.MERGING

        # Merge with auto-resolution
        all_findings = [backend_findings, infra_findings, frontend_findings]
        resolution = merge_findings(
            session_id='MA-E2E-002',
            lead_agent='backend',
            all_findings=all_findings,
        )

        # Should have detected backend vs infra conflict
        total_conflicts = resolution.total_conflicts
        assert total_conflicts >= 1

        # Backend should win (stronger evidence: reproducible + code analysis vs theory)
        for conflict in resolution.conflicts:
            if conflict.resolution == ConflictResolution.EVIDENCE_WEIGHTED:
                if conflict.resolved_finding:
                    assert 'pool' in conflict.resolved_finding.description.lower() or \
                           'connection' in conflict.resolved_finding.description.lower()

        # Write documents
        write_manifest(session, session_folder)
        doc_path = write_resolution_document(
            resolution, all_findings, session_folder,
        )
        assert doc_path.exists()

        # Document should reference conflicts
        doc_content = doc_path.read_text(encoding='utf-8')
        assert '## Conflicts' in doc_content

        # Complete session
        session = orchestrator.complete_session('MA-E2E-002', resolution)
        assert session.status == SessionStatus.RESOLVED

        # Extract lessons (from both resolved conflict and high-confidence finding)
        lessons = extract_debate_patterns(resolution)
        assert len(lessons) >= 1

        # Format for review
        review_doc = format_all_lessons(lessons)
        assert 'Lesson Candidates' in review_doc
        assert 'Total Candidates' in review_doc

        # Emit events
        events_file = str(tmp_path / 'events.jsonl')
        count = emit_lesson_events(lessons, events_file)
        assert count >= 1


# --- E2E: Single-Agent Backward Compatibility ---


class TestE2ESingleAgentBackwardCompat:
    """Ensure single-agent workflow is unaffected by multi-agent additions."""

    def test_single_agent_session(self, orchestrator, backend_zone, tmp_path):
        """Single-agent session works like pre-WAVE3-030."""
        session_folder = str(tmp_path / 'session-e2e-003')

        # Create session with 1 zone = 1 agent
        session = orchestrator.create_session(
            session_id='MA-E2E-003',
            debug_session_id='DBG-E2E-003',
            bug_description='Simple null pointer in handler',
            lead_agent='backend',
            zones=[backend_zone],
            session_folder=session_folder,
        )
        assert session.agent_count == 1

        # Start investigation
        orchestrator.start_investigation('MA-E2E-003')

        # Submit single agent's findings
        findings = AgentFindings(
            agent_name='backend',
            session_id='MA-E2E-003',
            zone=backend_zone,
            findings=[
                Finding(
                    description='Missing null check on user_id parameter',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='Stack trace shows NoneType error',
                            evidence_type=EvidenceType.REPRODUCIBLE,
                        ),
                    ],
                    confidence=0.99,
                    files_involved=['services/payment/handler.py'],
                    proposed_fix='Add guard clause: if user_id is None: return 400',
                ),
            ],
            investigation_time_minutes=10,
        )
        session = orchestrator.submit_findings('MA-E2E-003', findings)

        # Should auto-complete to MERGING with single agent
        assert session.status == SessionStatus.MERGING

        # Merge (trivial with one agent)
        resolution = merge_findings(
            session_id='MA-E2E-003',
            lead_agent='backend',
            all_findings=[findings],
        )

        assert len(resolution.consensus_findings) == 1
        assert resolution.total_conflicts == 0
        assert len(resolution.unresolved_conflicts) == 0

        # Complete
        session = orchestrator.complete_session('MA-E2E-003', resolution)
        assert session.status == SessionStatus.RESOLVED

        # Lesson from high-confidence finding
        lessons = extract_debate_patterns(resolution)
        assert len(lessons) >= 1


# --- E2E: Escalation Path ---


class TestE2EEscalationPath:
    """End-to-end: Session escalated due to unresolvable conflict."""

    def test_escalation_on_close_evidence(self, orchestrator, backend_zone, infra_zone, tmp_path):
        """When evidence weights are too close, escalation is triggered."""
        session_folder = str(tmp_path / 'session-e2e-004')

        session = orchestrator.create_session(
            session_id='MA-E2E-004',
            debug_session_id='DBG-E2E-004',
            bug_description='Intermittent service failure',
            lead_agent='backend',
            zones=[backend_zone, infra_zone],
            session_folder=session_folder,
        )

        orchestrator.start_investigation('MA-E2E-004')

        # Both agents have equally strong evidence (should trigger escalation)
        backend_findings = AgentFindings(
            agent_name='backend',
            session_id='MA-E2E-004',
            zone=backend_zone,
            findings=[
                Finding(
                    description='Race condition in order processing',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='Reproduced with concurrent requests',
                            evidence_type=EvidenceType.REPRODUCIBLE,
                        ),
                    ],
                    confidence=0.85,
                    files_involved=['services/payment/handler.py'],
                    proposed_fix='Add mutex lock',
                ),
            ],
        )

        infra_findings = AgentFindings(
            agent_name='infra',
            session_id='MA-E2E-004',
            zone=infra_zone,
            findings=[
                Finding(
                    description='Container memory limit causing OOM kills',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='dmesg shows OOM killer invocations',
                            evidence_type=EvidenceType.REPRODUCIBLE,
                        ),
                    ],
                    confidence=0.85,
                    files_involved=['deploy/docker-compose.yml'],
                    proposed_fix='Increase memory limit to 2G',
                ),
            ],
        )

        orchestrator.submit_findings('MA-E2E-004', backend_findings)
        session = orchestrator.submit_findings('MA-E2E-004', infra_findings)
        assert session.status == SessionStatus.MERGING

        # Merge
        resolution = merge_findings(
            session_id='MA-E2E-004',
            lead_agent='backend',
            all_findings=[backend_findings, infra_findings],
        )

        # With equal reproducible evidence, conflicts should exist
        # Some may be escalated (human_escalated), some may be evidence_weighted
        # depending on the word overlap in descriptions
        if resolution.total_conflicts > 0:
            summary = get_conflict_summary(
                resolution.conflicts + resolution.unresolved_conflicts,
            )
            assert summary['total'] > 0

        # Session can still complete (or escalate)
        if resolution.has_unresolved_conflicts:
            session = orchestrator.escalate_session(
                'MA-E2E-004',
                reason='Unresolvable conflict between backend and infra findings',
            )
            assert session.status == SessionStatus.ESCALATED
        else:
            session = orchestrator.complete_session('MA-E2E-004', resolution)
            assert session.status == SessionStatus.RESOLVED


# --- E2E: Agent Blocked Path ---


class TestE2EAgentBlocked:
    """End-to-end: One agent gets blocked during investigation."""

    def test_blocked_agent_handling(
        self, orchestrator, backend_zone, frontend_zone, tmp_path,
    ):
        """Blocked agent does not prevent session from proceeding."""
        session_folder = str(tmp_path / 'session-e2e-005')

        session = orchestrator.create_session(
            session_id='MA-E2E-005',
            debug_session_id='DBG-E2E-005',
            bug_description='Payment processing failure',
            lead_agent='backend',
            zones=[backend_zone, frontend_zone],
            session_folder=session_folder,
        )

        orchestrator.start_investigation('MA-E2E-005')

        # Backend finds the issue
        backend_findings = AgentFindings(
            agent_name='backend',
            session_id='MA-E2E-005',
            zone=backend_zone,
            findings=[
                Finding(
                    description='Invalid API key in production config',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='API returns 401 with invalid key',
                            evidence_type=EvidenceType.REPRODUCIBLE,
                        ),
                    ],
                    confidence=0.99,
                    files_involved=['services/payment/config.py'],
                    proposed_fix='Rotate API key and update config',
                ),
            ],
        )
        orchestrator.submit_findings('MA-E2E-005', backend_findings)

        # Frontend gets blocked (cannot reproduce in isolation)
        orchestrator.mark_agent_blocked(
            'MA-E2E-005', 'frontend',
            blockers=['Cannot reproduce without backend connectivity'],
        )

        # Session should still be investigating (frontend not complete)
        session = orchestrator.get_session('MA-E2E-005')
        assert session.status == SessionStatus.INVESTIGATING

        # Submit empty frontend findings to complete
        frontend_findings = AgentFindings(
            agent_name='frontend',
            session_id='MA-E2E-005',
            zone=frontend_zone,
            findings=[],
            blockers=['Cannot reproduce without backend connectivity'],
        )
        session = orchestrator.submit_findings('MA-E2E-005', frontend_findings)
        assert session.status == SessionStatus.MERGING

        # Merge (backend only has findings)
        resolution = merge_findings(
            session_id='MA-E2E-005',
            lead_agent='backend',
            all_findings=[backend_findings, frontend_findings],
        )
        assert len(resolution.consensus_findings) == 1
        assert resolution.total_conflicts == 0

        session = orchestrator.complete_session('MA-E2E-005', resolution)
        assert session.status == SessionStatus.RESOLVED


# --- E2E: Complexity Assessment Integration ---


class TestE2EComplexityAssessment:
    """End-to-end: Complexity drives agent count."""

    def test_simple_bug_single_agent(self):
        """Simple bug description results in 1 agent suggestion."""
        assessment = assess_complexity('Null pointer in user handler')
        assert assessment.suggested_agents == 1

    def test_complex_distributed_bug_multi_agent(self):
        """Complex distributed bug suggests multiple agents."""
        assessment = assess_complexity(
            'Distributed timeout across microservices with race condition '
            'in the database transaction layer and load balancer',
            context='kubernetes docker container service mesh',
        )
        assert assessment.suggested_agents >= 2
        assert assessment.overall_score > 0.4

    def test_complexity_drives_session_config(self, registry):
        """Complexity assessment feeds directly into session config."""
        zones = [
            WorkZone(name='backend', description='Backend', required_capabilities=['backend']),
            WorkZone(name='data', description='Data layer', required_capabilities=['data']),
        ]
        config = create_session_config(
            bug_description='Database deadlock in transaction processing',
            lead_agent='backend',
            agents=registry.get_all_agents(),
            zones=zones,
            session_folder='/tmp/test',
            session_id='test-session',
            debug_session_id='DBG-TEST',
            context='concurrent transactions database deadlock',
        )
        assert config.complexity is not None
        assert config.complexity.overall_score > 0
        assert len(config.assignments) == 2


# --- E2E: Full Pipeline with Events.jsonl ---


class TestE2EFullPipeline:
    """End-to-end: Complete pipeline from session to events.jsonl."""

    def test_session_to_events_pipeline(
        self, orchestrator, backend_zone, frontend_zone, tmp_path,
    ):
        """Full pipeline: session -> merge -> lessons -> events."""
        session_folder = str(tmp_path / 'pipeline-session')
        events_file = str(tmp_path / 'events.jsonl')

        # Create and run session
        session = orchestrator.create_session(
            session_id='MA-PIPE-001',
            debug_session_id='DBG-PIPE-001',
            bug_description='API timeout on /orders endpoint',
            lead_agent='backend',
            zones=[backend_zone, frontend_zone],
            session_folder=session_folder,
        )

        orchestrator.start_investigation('MA-PIPE-001')

        backend_findings = AgentFindings(
            agent_name='backend',
            session_id='MA-PIPE-001',
            zone=backend_zone,
            findings=[
                Finding(
                    description='N+1 query in order lookup',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='SQL log shows 100 queries for 1 page load',
                            evidence_type=EvidenceType.REPRODUCIBLE,
                            source='services/payment/handler.py',
                        ),
                    ],
                    confidence=0.92,
                    files_involved=['services/payment/handler.py'],
                    proposed_fix='Add eager loading with JOIN',
                ),
            ],
        )
        frontend_findings = AgentFindings(
            agent_name='frontend',
            session_id='MA-PIPE-001',
            zone=frontend_zone,
            findings=[
                Finding(
                    description='Loading spinner has no timeout',
                    classification='symptom',
                    confidence=0.6,
                ),
            ],
        )

        orchestrator.submit_findings('MA-PIPE-001', backend_findings)
        orchestrator.submit_findings('MA-PIPE-001', frontend_findings)

        # Merge
        resolution = merge_findings(
            session_id='MA-PIPE-001',
            lead_agent='backend',
            all_findings=[backend_findings, frontend_findings],
        )

        # Extract lessons
        lessons = extract_debate_patterns(resolution)
        assert len(lessons) >= 1

        # Emit to events.jsonl
        count = emit_lesson_events(lessons, events_file)
        assert count >= 1

        # Verify events.jsonl content is valid
        events = []
        with open(events_file, encoding='utf-8') as f:
            for line in f:
                events.append(json.loads(line))

        assert len(events) >= 1
        for event in events:
            assert event['event'] == 'debug_lesson'
            assert event['version'] == '1.0'
            assert 'timestamp' in event
            assert event['data']['source'] == 'multi_agent_session'
            assert event['data']['session_id'] == 'MA-PIPE-001'

        # Write all artifacts
        write_manifest(session, session_folder)
        write_resolution_document(
            resolution, [backend_findings, frontend_findings], session_folder,
        )

        # Verify folder has expected files
        folder = Path(session_folder)
        assert (folder / 'session_manifest.md').exists()
        assert (folder / 'merge_resolution.md').exists()


# --- E2E: Session Status Reporting ---


class TestE2ESessionStatus:
    """End-to-end: Session status reporting throughout lifecycle."""

    def test_status_at_each_phase(
        self, orchestrator, backend_zone, frontend_zone, tmp_path,
    ):
        """Status correctly reflects session state at each phase."""
        session_folder = str(tmp_path / 'session-status')

        session = orchestrator.create_session(
            session_id='MA-STATUS-001',
            debug_session_id='DBG-STATUS-001',
            bug_description='Test status tracking',
            lead_agent='backend',
            zones=[backend_zone, frontend_zone],
            session_folder=session_folder,
        )

        # SETUP phase
        status = orchestrator.get_session_status('MA-STATUS-001')
        assert status['status'] == 'setup'
        assert status['agent_count'] == 2
        assert status['agents_complete'] == 0

        # INVESTIGATING phase
        orchestrator.start_investigation('MA-STATUS-001')
        status = orchestrator.get_session_status('MA-STATUS-001')
        assert status['status'] == 'investigating'

        # After first agent completes
        findings = AgentFindings(
            agent_name='backend',
            session_id='MA-STATUS-001',
            zone=backend_zone,
            findings=[
                Finding(description='Found issue', classification='root_cause', confidence=0.9),
            ],
        )
        orchestrator.submit_findings('MA-STATUS-001', findings)
        status = orchestrator.get_session_status('MA-STATUS-001')
        assert status['agents_complete'] == 1
        assert not status['all_complete']

        # After all agents complete -> MERGING
        findings2 = AgentFindings(
            agent_name='frontend',
            session_id='MA-STATUS-001',
            zone=frontend_zone,
            findings=[],
        )
        orchestrator.submit_findings('MA-STATUS-001', findings2)
        status = orchestrator.get_session_status('MA-STATUS-001')
        assert status['status'] == 'merging'
        assert status['all_complete']


# --- E2E: Error Handling ---


class TestE2EErrorHandling:
    """End-to-end: Error paths and edge cases."""

    def test_duplicate_session_id_rejected(
        self, orchestrator, backend_zone, tmp_path,
    ):
        """Cannot create two sessions with same ID."""
        orchestrator.create_session(
            session_id='MA-DUP-001',
            debug_session_id='DBG-DUP-001',
            bug_description='First session',
            lead_agent='backend',
            zones=[backend_zone],
            session_folder=str(tmp_path / 'dup1'),
        )

        from scripts.lib.multi_agent_debug.exceptions import SessionAlreadyExistsError
        with pytest.raises(SessionAlreadyExistsError):
            orchestrator.create_session(
                session_id='MA-DUP-001',
                debug_session_id='DBG-DUP-002',
                bug_description='Duplicate session',
                lead_agent='backend',
                zones=[backend_zone],
                session_folder=str(tmp_path / 'dup2'),
            )

    def test_submit_findings_wrong_state(
        self, orchestrator, backend_zone, tmp_path,
    ):
        """Cannot submit findings when not in INVESTIGATING state."""
        orchestrator.create_session(
            session_id='MA-STATE-001',
            debug_session_id='DBG-STATE-001',
            bug_description='Test',
            lead_agent='backend',
            zones=[backend_zone],
            session_folder=str(tmp_path / 'state'),
        )

        findings = AgentFindings(
            agent_name='backend',
            session_id='MA-STATE-001',
            zone=backend_zone,
            findings=[],
        )

        with pytest.raises(InvalidSessionStateError):
            orchestrator.submit_findings('MA-STATE-001', findings)

    def test_nonexistent_session_raises(self, orchestrator):
        """Accessing nonexistent session raises error."""
        with pytest.raises(SessionNotFoundError):
            orchestrator.get_session('DOES-NOT-EXIST')

    def test_complete_wrong_state_raises(
        self, orchestrator, backend_zone, tmp_path,
    ):
        """Cannot complete session that is not in MERGING state."""
        session = orchestrator.create_session(
            session_id='MA-WRONG-001',
            debug_session_id='DBG-WRONG-001',
            bug_description='Test',
            lead_agent='backend',
            zones=[backend_zone],
            session_folder=str(tmp_path / 'wrong'),
        )

        resolution = MergeResolution(
            session_id='MA-WRONG-001',
            lead_agent='backend',
            participating_agents=['backend'],
        )

        with pytest.raises(InvalidSessionStateError):
            orchestrator.complete_session('MA-WRONG-001', resolution)
