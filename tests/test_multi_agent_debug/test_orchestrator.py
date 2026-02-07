"""Tests for multi-agent debug session orchestrator.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

import pytest
from datetime import datetime, UTC

from scripts.lib.multi_agent_debug.exceptions import (
    InvalidSessionStateError,
    SessionAlreadyExistsError,
    SessionNotFoundError,
)
from scripts.lib.multi_agent_debug.models import (
    AgentFindings,
    AgentStatus,
    Conflict,
    ConflictType,
    Evidence,
    EvidenceType,
    Finding,
    MergeResolution,
    SessionStatus,
    WorkZone,
)
from scripts.lib.multi_agent_debug.orchestrator import SessionOrchestrator
from scripts.lib.multi_agent_debug.registry import (
    AgentRegistry,
    create_default_registry,
)


# --- Fixtures ---

TEST_DATE = datetime(2026, 2, 15, tzinfo=UTC)


@pytest.fixture
def registry():
    """Create a registry with test agents."""
    reg = AgentRegistry()
    reg.register_agent('alpha', capabilities=['backend', 'data'])
    reg.register_agent('beta', capabilities=['frontend', 'performance'])
    reg.register_agent('gamma', capabilities=['infra', 'security'])
    return reg


@pytest.fixture
def orchestrator(registry):
    """Create an orchestrator with test registry."""
    return SessionOrchestrator(registry)


@pytest.fixture
def two_zones():
    """Create two work zones."""
    return [
        WorkZone(
            name='backend-zone',
            description='Backend API investigation',
            files=['api/handlers.py'],
            systems=['api-service'],
            required_capabilities=['backend'],
        ),
        WorkZone(
            name='frontend-zone',
            description='Frontend UI investigation',
            files=['components/App.tsx'],
            systems=['web-app'],
            required_capabilities=['frontend'],
        ),
    ]


@pytest.fixture
def created_session(orchestrator, two_zones):
    """Create a session in SETUP state."""
    return orchestrator.create_session(
        session_id='MA-001',
        debug_session_id='DBG-2026-02-15-001',
        bug_description='API timeout under concurrent load',
        lead_agent='alpha',
        zones=two_zones,
        session_folder='temp/DEBUG_REPORTS/session-test',
    )


@pytest.fixture
def investigating_session(orchestrator, created_session):
    """Create a session in INVESTIGATING state."""
    orchestrator.start_investigation('MA-001')
    return orchestrator.get_session('MA-001')


@pytest.fixture
def sample_findings():
    """Create sample agent findings."""
    return AgentFindings(
        agent_name='alpha',
        session_id='MA-001',
        zone=WorkZone(
            name='backend-zone',
            description='Backend API investigation',
        ),
        findings=[
            Finding(
                description='Connection pool size = 1',
                classification='root_cause',
                evidence=[
                    Evidence(
                        description='Config shows pool_size=1',
                        evidence_type=EvidenceType.CODE_ANALYSIS,
                        source='config/database.py:12',
                    ),
                ],
                confidence=0.9,
                files_involved=['config/database.py'],
                proposed_fix='Increase pool size to 10',
            ),
        ],
        investigation_time_minutes=30,
    )


@pytest.fixture
def beta_findings():
    """Create sample findings for beta agent."""
    return AgentFindings(
        agent_name='beta',
        session_id='MA-001',
        zone=WorkZone(
            name='frontend-zone',
            description='Frontend UI investigation',
        ),
        findings=[
            Finding(
                description='Frontend lacks timeout handling',
                classification='symptom',
                evidence=[
                    Evidence(
                        description='No timeout in fetch call',
                        evidence_type=EvidenceType.CODE_ANALYSIS,
                        source='hooks/useDataFetch.js:45',
                    ),
                ],
                confidence=0.7,
                files_involved=['hooks/useDataFetch.js'],
                proposed_fix='Add 5s timeout to fetch',
            ),
        ],
        investigation_time_minutes=25,
    )


# --- Session Creation Tests ---


class TestSessionCreation:
    """Tests for creating multi-agent debug sessions."""

    def test_create_session(self, orchestrator, two_zones):
        """Create a new session."""
        session = orchestrator.create_session(
            session_id='MA-001',
            debug_session_id='DBG-001',
            bug_description='Test bug',
            lead_agent='alpha',
            zones=two_zones,
            session_folder='temp/sessions/test',
        )
        assert session.session_id == 'MA-001'
        assert session.debug_session_id == 'DBG-001'
        assert session.status == SessionStatus.SETUP
        assert session.lead_agent == 'alpha'
        assert session.agent_count == 2

    def test_create_session_sets_timestamps(self, orchestrator, two_zones):
        """Session creation sets timestamps."""
        session = orchestrator.create_session(
            session_id='MA-002',
            debug_session_id='DBG-002',
            bug_description='Test bug',
            lead_agent='alpha',
            zones=two_zones,
            session_folder='temp/sessions/test',
        )
        assert session.created_at is not None
        assert session.updated_at is not None

    def test_create_session_assesses_complexity(self, orchestrator, two_zones):
        """Session creation performs complexity assessment."""
        session = orchestrator.create_session(
            session_id='MA-003',
            debug_session_id='DBG-003',
            bug_description='Race condition in microservice with deadlock',
            lead_agent='alpha',
            zones=two_zones,
            session_folder='temp/sessions/test',
        )
        assert session.complexity is not None
        assert session.complexity.overall_score > 0

    def test_create_session_with_context(self, orchestrator, two_zones):
        """Context is passed to complexity assessment."""
        session = orchestrator.create_session(
            session_id='MA-004',
            debug_session_id='DBG-004',
            bug_description='Bug in API',
            lead_agent='alpha',
            zones=two_zones,
            session_folder='temp/sessions/test',
            context='Kubernetes microservice with concurrent thread pool',
        )
        assert session.complexity.overall_score > 0.1

    def test_create_duplicate_raises(self, orchestrator, two_zones):
        """Creating duplicate session raises error."""
        orchestrator.create_session(
            session_id='MA-DUP',
            debug_session_id='DBG-DUP',
            bug_description='Test bug',
            lead_agent='alpha',
            zones=two_zones,
            session_folder='temp/sessions/test',
        )
        with pytest.raises(SessionAlreadyExistsError):
            orchestrator.create_session(
                session_id='MA-DUP',
                debug_session_id='DBG-DUP2',
                bug_description='Another bug',
                lead_agent='alpha',
                zones=two_zones,
                session_folder='temp/sessions/test2',
            )

    def test_create_session_assigns_agents_to_zones(
        self, orchestrator, two_zones,
    ):
        """Agents are assigned to zones based on capability matching."""
        session = orchestrator.create_session(
            session_id='MA-005',
            debug_session_id='DBG-005',
            bug_description='Test bug',
            lead_agent='alpha',
            zones=two_zones,
            session_folder='temp/sessions/test',
        )
        # Backend zone should go to alpha (has backend capability)
        backend_assignment = session.get_assignment('alpha')
        assert backend_assignment is not None
        assert backend_assignment.zone.name == 'backend-zone'

        # Frontend zone should go to beta (has frontend capability)
        frontend_assignment = session.get_assignment('beta')
        assert frontend_assignment is not None
        assert frontend_assignment.zone.name == 'frontend-zone'

    def test_session_count(self, orchestrator, two_zones):
        """Session count tracks correctly."""
        assert orchestrator.session_count == 0
        orchestrator.create_session(
            session_id='MA-006',
            debug_session_id='DBG-006',
            bug_description='Test',
            lead_agent='alpha',
            zones=two_zones,
            session_folder='temp/test',
        )
        assert orchestrator.session_count == 1


# --- Investigation Lifecycle Tests ---


class TestInvestigationLifecycle:
    """Tests for investigation state transitions."""

    def test_start_investigation(self, orchestrator, created_session):
        """Start investigation transitions to INVESTIGATING."""
        session = orchestrator.start_investigation('MA-001')
        assert session.status == SessionStatus.INVESTIGATING

    def test_start_investigation_updates_agents(
        self, orchestrator, created_session,
    ):
        """Starting investigation sets all agents to INVESTIGATING."""
        session = orchestrator.start_investigation('MA-001')
        for assignment in session.assignments:
            assert assignment.status == AgentStatus.INVESTIGATING
            assert assignment.started_at is not None

    def test_start_wrong_state_raises(self, orchestrator, created_session):
        """Starting investigation from wrong state raises error."""
        orchestrator.start_investigation('MA-001')
        with pytest.raises(InvalidSessionStateError):
            orchestrator.start_investigation('MA-001')

    def test_start_nonexistent_raises(self, orchestrator):
        """Starting nonexistent session raises error."""
        with pytest.raises(SessionNotFoundError):
            orchestrator.start_investigation('NONEXISTENT')


# --- Findings Submission Tests ---


class TestFindingsSubmission:
    """Tests for submitting agent findings."""

    def test_submit_findings(
        self, orchestrator, investigating_session, sample_findings,
    ):
        """Submit findings stores them in session."""
        session = orchestrator.submit_findings('MA-001', sample_findings)
        assert len(session.agent_findings) == 1
        assert session.agent_findings[0].agent_name == 'alpha'

    def test_submit_findings_marks_agent_complete(
        self, orchestrator, investigating_session, sample_findings,
    ):
        """Submitting findings marks agent as COMPLETE."""
        session = orchestrator.submit_findings('MA-001', sample_findings)
        assignment = session.get_assignment('alpha')
        assert assignment.status == AgentStatus.COMPLETE
        assert assignment.completed_at is not None

    def test_submit_all_findings_transitions_to_merging(
        self, orchestrator, investigating_session,
        sample_findings, beta_findings,
    ):
        """When all agents submit, session transitions to MERGING."""
        orchestrator.submit_findings('MA-001', sample_findings)
        session = orchestrator.submit_findings('MA-001', beta_findings)
        assert session.status == SessionStatus.MERGING

    def test_submit_partial_stays_investigating(
        self, orchestrator, investigating_session, sample_findings,
    ):
        """Partial submissions keep session in INVESTIGATING."""
        session = orchestrator.submit_findings('MA-001', sample_findings)
        assert session.status == SessionStatus.INVESTIGATING

    def test_submit_wrong_state_raises(
        self, orchestrator, created_session, sample_findings,
    ):
        """Submitting in wrong state raises error."""
        with pytest.raises(InvalidSessionStateError):
            orchestrator.submit_findings('MA-001', sample_findings)

    def test_submit_nonexistent_raises(self, orchestrator, sample_findings):
        """Submitting to nonexistent session raises error."""
        with pytest.raises(SessionNotFoundError):
            orchestrator.submit_findings('NONEXISTENT', sample_findings)


# --- Agent Blocked Tests ---


class TestAgentBlocked:
    """Tests for marking agents as blocked."""

    def test_mark_agent_blocked(
        self, orchestrator, investigating_session,
    ):
        """Mark agent as blocked."""
        session = orchestrator.mark_agent_blocked(
            'MA-001', 'alpha', ['Cannot access database logs'],
        )
        assignment = session.get_assignment('alpha')
        assert assignment.status == AgentStatus.BLOCKED

    def test_mark_blocked_wrong_state_raises(
        self, orchestrator, created_session,
    ):
        """Marking blocked in wrong state raises error."""
        with pytest.raises(InvalidSessionStateError):
            orchestrator.mark_agent_blocked(
                'MA-001', 'alpha', ['blocker'],
            )


# --- Session Completion Tests ---


class TestSessionCompletion:
    """Tests for completing sessions."""

    def test_complete_session(
        self, orchestrator, investigating_session,
        sample_findings, beta_findings,
    ):
        """Complete session with resolution."""
        orchestrator.submit_findings('MA-001', sample_findings)
        orchestrator.submit_findings('MA-001', beta_findings)

        resolution = MergeResolution(
            session_id='MA-001',
            lead_agent='alpha',
            participating_agents=['alpha', 'beta'],
            consensus_findings=[sample_findings.findings[0]],
            deployment_order=['backend-fix', 'frontend-fix'],
        )

        session = orchestrator.complete_session('MA-001', resolution)
        assert session.status == SessionStatus.RESOLVED
        assert session.resolution is not None
        assert len(session.resolution.consensus_findings) == 1

    def test_complete_releases_agents(
        self, orchestrator, investigating_session,
        sample_findings, beta_findings, registry,
    ):
        """Completing session releases all agents."""
        orchestrator.submit_findings('MA-001', sample_findings)
        orchestrator.submit_findings('MA-001', beta_findings)

        resolution = MergeResolution(
            session_id='MA-001',
            lead_agent='alpha',
            participating_agents=['alpha', 'beta'],
        )
        orchestrator.complete_session('MA-001', resolution)

        # Agents should be available again
        assert registry.get_agent('alpha').current_sessions == 0
        assert registry.get_agent('beta').current_sessions == 0

    def test_complete_wrong_state_raises(
        self, orchestrator, investigating_session,
    ):
        """Completing in wrong state raises error."""
        resolution = MergeResolution(
            session_id='MA-001',
            lead_agent='alpha',
            participating_agents=['alpha'],
        )
        with pytest.raises(InvalidSessionStateError):
            orchestrator.complete_session('MA-001', resolution)


# --- Session Escalation Tests ---


class TestSessionEscalation:
    """Tests for escalating sessions."""

    def test_escalate_from_investigating(
        self, orchestrator, investigating_session,
    ):
        """Escalate session from INVESTIGATING."""
        session = orchestrator.escalate_session(
            'MA-001', 'Cannot reproduce issue',
        )
        assert session.status == SessionStatus.ESCALATED

    def test_escalate_from_setup(self, orchestrator, created_session):
        """Escalate session from SETUP."""
        session = orchestrator.escalate_session(
            'MA-001', 'Insufficient agents available',
        )
        assert session.status == SessionStatus.ESCALATED

    def test_escalate_releases_agents(
        self, orchestrator, investigating_session, registry,
    ):
        """Escalating releases all agents."""
        orchestrator.escalate_session('MA-001', 'reason')
        assert registry.get_agent('alpha').current_sessions == 0
        assert registry.get_agent('beta').current_sessions == 0

    def test_escalate_resolved_raises(
        self, orchestrator, investigating_session,
        sample_findings, beta_findings,
    ):
        """Cannot escalate already resolved session."""
        orchestrator.submit_findings('MA-001', sample_findings)
        orchestrator.submit_findings('MA-001', beta_findings)
        resolution = MergeResolution(
            session_id='MA-001',
            lead_agent='alpha',
            participating_agents=['alpha', 'beta'],
        )
        orchestrator.complete_session('MA-001', resolution)

        with pytest.raises(InvalidSessionStateError):
            orchestrator.escalate_session('MA-001', 'reason')

    def test_escalate_already_escalated_raises(
        self, orchestrator, investigating_session,
    ):
        """Cannot escalate already escalated session."""
        orchestrator.escalate_session('MA-001', 'reason')
        with pytest.raises(InvalidSessionStateError):
            orchestrator.escalate_session('MA-001', 'reason again')


# --- Session Status & Query Tests ---


class TestSessionStatus:
    """Tests for session status queries."""

    def test_get_session(self, orchestrator, created_session):
        """Get session by ID."""
        session = orchestrator.get_session('MA-001')
        assert session.session_id == 'MA-001'

    def test_get_nonexistent_raises(self, orchestrator):
        """Getting nonexistent session raises error."""
        with pytest.raises(SessionNotFoundError):
            orchestrator.get_session('NONEXISTENT')

    def test_get_session_status(self, orchestrator, created_session):
        """Get session status summary."""
        status = orchestrator.get_session_status('MA-001')
        assert status['session_id'] == 'MA-001'
        assert status['status'] == 'setup'
        assert status['agent_count'] == 2
        assert status['agents_complete'] == 0
        assert status['all_complete'] is False

    def test_get_session_status_with_findings(
        self, orchestrator, investigating_session, sample_findings,
    ):
        """Status includes findings summary when available."""
        orchestrator.submit_findings('MA-001', sample_findings)
        status = orchestrator.get_session_status('MA-001')

        # Find alpha's agent info
        alpha_info = next(
            a for a in status['agents'] if a['agent'] == 'alpha'
        )
        assert alpha_info['status'] == 'complete'
        assert alpha_info['finding_count'] == 1
        assert 'Connection pool' in alpha_info['primary_finding']

    def test_get_all_sessions(self, orchestrator, two_zones):
        """Get all sessions."""
        orchestrator.create_session(
            session_id='MA-010',
            debug_session_id='DBG-010',
            bug_description='Bug 1',
            lead_agent='alpha',
            zones=two_zones,
            session_folder='temp/test',
        )
        orchestrator.create_session(
            session_id='MA-011',
            debug_session_id='DBG-011',
            bug_description='Bug 2',
            lead_agent='alpha',
            zones=two_zones[:1],
            session_folder='temp/test2',
        )
        sessions = orchestrator.get_all_sessions()
        assert len(sessions) == 2

    def test_active_sessions(self, orchestrator, two_zones):
        """Active sessions filters correctly."""
        orchestrator.create_session(
            session_id='MA-020',
            debug_session_id='DBG-020',
            bug_description='Active bug',
            lead_agent='alpha',
            zones=two_zones,
            session_folder='temp/test',
        )
        assert len(orchestrator.active_sessions) == 1

    def test_active_sessions_excludes_resolved(
        self, orchestrator, investigating_session,
        sample_findings, beta_findings,
    ):
        """Active sessions excludes resolved sessions."""
        orchestrator.submit_findings('MA-001', sample_findings)
        orchestrator.submit_findings('MA-001', beta_findings)
        resolution = MergeResolution(
            session_id='MA-001',
            lead_agent='alpha',
            participating_agents=['alpha', 'beta'],
        )
        orchestrator.complete_session('MA-001', resolution)
        assert len(orchestrator.active_sessions) == 0


# --- Full Lifecycle Test ---


class TestFullLifecycle:
    """Integration tests for complete session lifecycle."""

    def test_full_lifecycle(self, orchestrator, two_zones):
        """Test complete session lifecycle: create -> investigate -> merge -> resolve."""
        # 1. Create session
        session = orchestrator.create_session(
            session_id='MA-FULL',
            debug_session_id='DBG-FULL',
            bug_description='API timeout with database deadlock',
            lead_agent='alpha',
            zones=two_zones,
            session_folder='temp/sessions/full-test',
            context='Concurrent requests causing serialization',
        )
        assert session.status == SessionStatus.SETUP
        assert session.agent_count == 2

        # 2. Start investigation
        session = orchestrator.start_investigation('MA-FULL')
        assert session.status == SessionStatus.INVESTIGATING

        # 3. Submit alpha findings (root cause)
        alpha_findings = AgentFindings(
            agent_name='alpha',
            session_id='MA-FULL',
            zone=two_zones[0],
            findings=[
                Finding(
                    description='Connection pool undersized',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='Pool size = 1',
                            evidence_type=EvidenceType.CODE_ANALYSIS,
                        ),
                        Evidence(
                            description='Reproduced with 3 concurrent requests',
                            evidence_type=EvidenceType.REPRODUCIBLE,
                        ),
                    ],
                    confidence=0.95,
                    proposed_fix='Increase pool to 10',
                ),
            ],
            investigation_time_minutes=30,
        )
        session = orchestrator.submit_findings('MA-FULL', alpha_findings)
        assert session.agents_complete == 1
        assert session.status == SessionStatus.INVESTIGATING

        # 4. Submit beta findings (symptom)
        beta_findings = AgentFindings(
            agent_name='beta',
            session_id='MA-FULL',
            zone=two_zones[1],
            findings=[
                Finding(
                    description='Frontend shows infinite spinner',
                    classification='symptom',
                    evidence=[
                        Evidence(
                            description='No timeout on fetch',
                            evidence_type=EvidenceType.CODE_ANALYSIS,
                        ),
                    ],
                    confidence=0.7,
                    proposed_fix='Add 5s fetch timeout',
                ),
            ],
            investigation_time_minutes=25,
        )
        session = orchestrator.submit_findings('MA-FULL', beta_findings)
        assert session.agents_complete == 2
        assert session.status == SessionStatus.MERGING

        # 5. Complete with resolution
        resolution = MergeResolution(
            session_id='MA-FULL',
            lead_agent='alpha',
            participating_agents=['alpha', 'beta'],
            consensus_findings=[alpha_findings.findings[0]],
            deployment_order=['backend-pool-fix', 'frontend-timeout'],
            resolution_time_minutes=15,
        )
        session = orchestrator.complete_session('MA-FULL', resolution)
        assert session.status == SessionStatus.RESOLVED
        assert session.resolution is not None
        assert len(session.resolution.deployment_order) == 2
