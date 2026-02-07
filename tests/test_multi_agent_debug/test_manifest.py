"""Tests for session manifest generator.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

import pytest
from datetime import datetime, UTC
from pathlib import Path

from scripts.lib.multi_agent_debug.manifest import (
    generate_manifest,
    write_manifest,
    update_manifest,
    _status_icon,
    _findings_filename,
)
from scripts.lib.multi_agent_debug.models import (
    AgentFindings,
    AgentStatus,
    ComplexityAssessment,
    ComplexityFactor,
    Evidence,
    EvidenceType,
    Finding,
    MergeResolution,
    MultiAgentSession,
    SessionStatus,
    WorkAssignment,
    WorkZone,
)


# --- Fixtures ---

TEST_DATE = datetime(2026, 2, 15, 10, 0, 0, tzinfo=UTC)


@pytest.fixture
def backend_zone():
    """Create a backend work zone."""
    return WorkZone(
        name='backend-api',
        description='Backend API investigation',
        files=['api/handlers.py', 'api/routes.py'],
        systems=['api-service'],
        required_capabilities=['backend'],
    )


@pytest.fixture
def frontend_zone():
    """Create a frontend work zone."""
    return WorkZone(
        name='frontend-ui',
        description='Frontend UI investigation',
        files=['components/Dashboard.tsx'],
        systems=['web-app'],
        required_capabilities=['frontend'],
    )


@pytest.fixture
def basic_session(backend_zone, frontend_zone):
    """Create a basic session in SETUP state."""
    return MultiAgentSession(
        session_id='MA-TEST-001',
        debug_session_id='DBG-2026-02-15-001',
        bug_description='API timeout under concurrent load',
        lead_agent='alpha',
        status=SessionStatus.SETUP,
        complexity=ComplexityAssessment(
            overall_score=0.65,
            suggested_agents=3,
            factors=[
                ComplexityFactor(
                    name='concurrency',
                    score=0.8,
                    description='Detected: concurrent, thread',
                ),
                ComplexityFactor(
                    name='data_layer',
                    score=0.5,
                    description='Detected: database',
                ),
            ],
            rationale='Complexity factors detected: concurrency, data_layer.',
        ),
        assignments=[
            WorkAssignment(
                agent_name='alpha',
            session_id="MA-TEST-001",
            zone=backend_zone,
                status=AgentStatus.ASSIGNED,
            ),
            WorkAssignment(
                agent_name='beta',
            session_id="MA-TEST-001",
            zone=frontend_zone,
                status=AgentStatus.ASSIGNED,
            ),
        ],
        created_at=TEST_DATE,
        updated_at=TEST_DATE,
    )


@pytest.fixture
def investigating_session(basic_session):
    """Create a session in INVESTIGATING state."""
    session = basic_session
    session.status = SessionStatus.INVESTIGATING
    for assignment in session.assignments:
        assignment.status = AgentStatus.INVESTIGATING
        assignment.started_at = TEST_DATE
    return session


@pytest.fixture
def completed_session(investigating_session, backend_zone, frontend_zone):
    """Create a completed session with findings and resolution."""
    session = investigating_session
    session.status = SessionStatus.RESOLVED
    completed_time = datetime(2026, 2, 15, 11, 30, 0, tzinfo=UTC)
    session.updated_at = completed_time

    # Mark agents complete
    for assignment in session.assignments:
        assignment.status = AgentStatus.COMPLETE
        assignment.completed_at = completed_time

    # Add findings
    session.agent_findings = [
        AgentFindings(
            agent_name='alpha',
            session_id='MA-TEST-001',
            zone=backend_zone,
            findings=[
                Finding(
                    description='Connection pool size = 1',
                    classification='root_cause',
                    evidence=[
                        Evidence(
                            description='Pool config in database.py',
                            evidence_type=EvidenceType.CODE_ANALYSIS,
                        ),
                    ],
                    confidence=0.9,
                ),
            ],
            investigation_time_minutes=30,
        ),
        AgentFindings(
            agent_name='beta',
            session_id='MA-TEST-001',
            zone=frontend_zone,
            findings=[
                Finding(
                    description='No timeout on fetch',
                    classification='symptom',
                    confidence=0.7,
                ),
            ],
            investigation_time_minutes=25,
        ),
    ]

    # Add resolution
    session.resolution = MergeResolution(
        session_id='MA-TEST-001',
        lead_agent='alpha',
        participating_agents=['alpha', 'beta'],
        consensus_findings=[session.agent_findings[0].findings[0]],
        deployment_order=['backend-fix', 'frontend-fix'],
    )

    return session


# --- generate_manifest Tests ---


class TestGenerateManifest:
    """Tests for manifest content generation."""

    def test_manifest_contains_session_id(self, basic_session):
        """Manifest includes session ID."""
        content = generate_manifest(basic_session, 'temp/test')
        assert 'MA-TEST-001' in content

    def test_manifest_contains_status(self, basic_session):
        """Manifest includes session status."""
        content = generate_manifest(basic_session, 'temp/test')
        assert 'SETUP' in content

    def test_manifest_contains_bug_description(self, basic_session):
        """Manifest includes bug description."""
        content = generate_manifest(basic_session, 'temp/test')
        assert 'API timeout under concurrent load' in content

    def test_manifest_contains_lead_agent(self, basic_session):
        """Manifest includes lead agent."""
        content = generate_manifest(basic_session, 'temp/test')
        assert 'alpha' in content

    def test_manifest_contains_debug_session_id(self, basic_session):
        """Manifest includes linked debug session ID."""
        content = generate_manifest(basic_session, 'temp/test')
        assert 'DBG-2026-02-15-001' in content

    def test_manifest_contains_complexity(self, basic_session):
        """Manifest includes complexity assessment."""
        content = generate_manifest(basic_session, 'temp/test')
        assert '0.65' in content
        assert '3 agent(s) suggested' in content
        assert 'concurrency' in content
        assert 'data_layer' in content

    def test_manifest_contains_agent_table(self, basic_session):
        """Manifest includes agent table."""
        content = generate_manifest(basic_session, 'temp/test')
        assert '| Agent |' in content
        assert 'alpha' in content
        assert 'beta' in content
        assert 'backend-api' in content
        assert 'frontend-ui' in content

    def test_manifest_contains_work_zones(self, basic_session):
        """Manifest includes work zone details."""
        content = generate_manifest(basic_session, 'temp/test')
        assert '## Work Zones' in content
        assert 'Backend API investigation' in content
        assert 'Frontend UI investigation' in content
        assert '`api/handlers.py`' in content

    def test_manifest_contains_progress(self, basic_session):
        """Manifest includes progress section."""
        content = generate_manifest(basic_session, 'temp/test')
        assert '## Session Progress' in content
        assert 'Total Agents' in content
        assert 'Agents Complete' in content

    def test_investigating_manifest(self, investigating_session):
        """Manifest for investigating session shows status."""
        content = generate_manifest(investigating_session, 'temp/test')
        assert 'INVESTIGATING' in content
        assert '[~] investigating' in content

    def test_completed_manifest_has_findings(self, completed_session):
        """Completed manifest includes findings summary."""
        content = generate_manifest(completed_session, 'temp/test')
        assert 'Findings Summary' in content
        assert 'Connection pool size = 1' in content
        assert 'confidence: 0.9' in content

    def test_completed_manifest_has_resolution(self, completed_session):
        """Completed manifest includes resolution summary."""
        content = generate_manifest(completed_session, 'temp/test')
        assert 'Resolution Summary' in content
        assert 'Consensus Findings' in content
        assert 'backend-fix -> frontend-fix' in content

    def test_manifest_has_completed_timestamp(self, completed_session):
        """Completed session shows completion timestamp."""
        content = generate_manifest(completed_session, 'temp/test')
        assert 'Completed' in content

    def test_manifest_has_generation_timestamp(self, basic_session):
        """Manifest includes generation timestamp."""
        content = generate_manifest(basic_session, 'temp/test')
        assert 'Generated at' in content

    def test_manifest_is_valid_markdown(self, basic_session):
        """Manifest content is valid markdown structure."""
        content = generate_manifest(basic_session, 'temp/test')
        # Check it starts with a heading
        assert content.startswith('# Debug Session Manifest')
        # Check it has section headers
        assert '## Bug Reference' in content
        assert '## Participating Agents' in content
        assert '## Work Zones' in content
        assert '## Session Progress' in content

    def test_blocked_agent_shows_icon(self, investigating_session):
        """Blocked agent shows blocked icon."""
        investigating_session.assignments[0].status = AgentStatus.BLOCKED
        content = generate_manifest(investigating_session, 'temp/test')
        assert '[!] blocked' in content

    def test_session_without_complexity(self):
        """Session without complexity assessment still generates."""
        session = MultiAgentSession(
            session_id='MA-SIMPLE',
            debug_session_id='DBG-SIMPLE',
            bug_description='Simple bug',
            lead_agent='alpha',
            created_at=TEST_DATE,
            updated_at=TEST_DATE,
        )
        content = generate_manifest(session, 'temp/test')
        assert 'MA-SIMPLE' in content
        assert 'Simple bug' in content

    def test_findings_with_blockers(self, investigating_session, backend_zone):
        """Findings with blockers are shown in manifest."""
        investigating_session.agent_findings = [
            AgentFindings(
                agent_name='alpha',
                session_id='MA-TEST-001',
                zone=backend_zone,
                findings=[],
                blockers=['Cannot access prod logs', 'VPN required'],
            ),
        ]
        content = generate_manifest(investigating_session, 'temp/test')
        assert 'Cannot access prod logs' in content


# --- write_manifest Tests ---


class TestWriteManifest:
    """Tests for writing manifest to disk."""

    def test_write_manifest_creates_file(self, basic_session, tmp_path):
        """Writing manifest creates file on disk."""
        folder = str(tmp_path / 'session-test')
        result = write_manifest(basic_session, folder)
        assert result.exists()
        assert result.name == 'session_manifest.md'

    def test_write_manifest_creates_directory(self, basic_session, tmp_path):
        """Writing manifest creates directory if needed."""
        folder = str(tmp_path / 'nested' / 'session-test')
        result = write_manifest(basic_session, folder)
        assert Path(folder).is_dir()
        assert result.exists()

    def test_write_manifest_content(self, basic_session, tmp_path):
        """Written manifest has correct content."""
        folder = str(tmp_path / 'session-test')
        result = write_manifest(basic_session, folder)
        content = result.read_text(encoding='utf-8')
        assert 'MA-TEST-001' in content
        assert '# Debug Session Manifest' in content

    def test_update_manifest_overwrites(self, basic_session, tmp_path):
        """Update manifest overwrites existing file."""
        folder = str(tmp_path / 'session-test')

        # Write initial
        write_manifest(basic_session, folder)

        # Update with new status
        basic_session.status = SessionStatus.INVESTIGATING
        result = update_manifest(basic_session, folder)
        content = result.read_text(encoding='utf-8')
        assert 'INVESTIGATING' in content


# --- Helper Function Tests ---


class TestHelperFunctions:
    """Tests for manifest helper functions."""

    def test_status_icons(self):
        """Status icons map correctly."""
        assert _status_icon(AgentStatus.REGISTERED) == '[.]'
        assert _status_icon(AgentStatus.ASSIGNED) == '[>]'
        assert _status_icon(AgentStatus.INVESTIGATING) == '[~]'
        assert _status_icon(AgentStatus.COMPLETE) == '[x]'
        assert _status_icon(AgentStatus.BLOCKED) == '[!]'

    def test_findings_filename(self):
        """Findings filename generated correctly."""
        assert _findings_filename('backend') == 'agent_backend_findings.md'
        assert _findings_filename('alpha') == 'agent_alpha_findings.md'
        assert _findings_filename('my-agent') == 'agent_my_agent_findings.md'
        assert _findings_filename('MY AGENT') == 'agent_my_agent_findings.md'
