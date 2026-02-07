"""Tests for multi-agent debug coordination protocol.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

import pytest

from scripts.lib.multi_agent_debug.models import (
    AgentCapability,
    AgentProfile,
    WorkZone,
)
from scripts.lib.multi_agent_debug.protocol import (
    assess_complexity,
    create_session_config,
    get_required_capabilities,
    partition_blast_radius,
    _calculate_agent_zone_score,
)


# --- Fixtures ---


@pytest.fixture
def simple_agents():
    """Create a simple list of agents."""
    return [
        AgentProfile(
            name='backend',
            capabilities=[
                AgentCapability(name='backend', proficiency=1.0),
                AgentCapability(name='data', proficiency=0.8),
            ],
        ),
        AgentProfile(
            name='frontend',
            capabilities=[
                AgentCapability(name='frontend', proficiency=1.0),
                AgentCapability(name='performance', proficiency=0.7),
            ],
        ),
        AgentProfile(
            name='infra',
            capabilities=[
                AgentCapability(name='infra', proficiency=1.0),
                AgentCapability(name='security', proficiency=0.6),
            ],
        ),
    ]


@pytest.fixture
def simple_zones():
    """Create simple work zones."""
    return [
        WorkZone(
            name='api-layer',
            description='API endpoint investigation',
            files=['api/handlers.py'],
            systems=['api-service'],
            required_capabilities=['backend'],
        ),
        WorkZone(
            name='ui-layer',
            description='UI behavior investigation',
            files=['components/Dashboard.tsx'],
            systems=['web-app'],
            required_capabilities=['frontend'],
        ),
    ]


# --- assess_complexity Tests ---


class TestAssessComplexity:
    """Tests for complexity assessment."""

    def test_simple_bug_returns_single_agent(self):
        """Simple bug description suggests 1 agent."""
        result = assess_complexity("Button color is wrong")
        assert result.suggested_agents == 1
        assert result.overall_score < 0.4

    def test_complex_distributed_bug(self):
        """Complex distributed bug suggests multiple agents."""
        result = assess_complexity(
            "Race condition in microservice queue processing causing "
            "timeout cascade across API gateway and database deadlock"
        )
        assert result.suggested_agents >= 2
        assert result.overall_score >= 0.4
        assert len(result.factors) >= 2

    def test_multi_service_keywords_detected(self):
        """Multi-service keywords increase complexity."""
        result = assess_complexity("Kubernetes pod failing with distributed tracing")
        factor_names = [f.name for f in result.factors]
        assert 'multi_service' in factor_names

    def test_concurrency_keywords_detected(self):
        """Concurrency keywords increase complexity."""
        result = assess_complexity("Race condition with mutex lock contention")
        factor_names = [f.name for f in result.factors]
        assert 'concurrency' in factor_names

    def test_data_layer_keywords_detected(self):
        """Data layer keywords increase complexity."""
        result = assess_complexity("Database deadlock on transaction commit")
        factor_names = [f.name for f in result.factors]
        assert 'data_layer' in factor_names

    def test_context_included_in_analysis(self):
        """Context string is analyzed alongside description."""
        result_without = assess_complexity("Something is slow")
        result_with = assess_complexity(
            "Something is slow",
            context="Kubernetes microservice with concurrent thread pool",
        )
        assert result_with.overall_score >= result_without.overall_score

    def test_affected_files_increase_complexity(self):
        """Many affected files increase blast radius factor."""
        result = assess_complexity(
            "Bug in processing",
            affected_files=[f"file_{i}.py" for i in range(15)],
        )
        factor_names = [f.name for f in result.factors]
        assert 'large_blast_radius' in factor_names

    def test_affected_systems_increase_complexity(self):
        """Multiple affected systems increase complexity."""
        result = assess_complexity(
            "Cross-system failure",
            affected_systems=['api', 'database', 'cache'],
        )
        factor_names = [f.name for f in result.factors]
        assert 'multi_system' in factor_names

    def test_score_capped_at_one(self):
        """Overall score never exceeds 1.0."""
        result = assess_complexity(
            "Race condition in distributed microservice with database deadlock "
            "and timeout cascade causing memory leak in kubernetes container "
            "with concurrent thread pool and stale cache state",
            affected_files=[f"file_{i}.py" for i in range(30)],
            affected_systems=['api', 'db', 'cache', 'queue', 'gateway'],
        )
        assert result.overall_score <= 1.0

    def test_max_agents_is_five(self):
        """Agent count never exceeds 5."""
        result = assess_complexity(
            "Everything is broken in every service simultaneously",
            affected_files=[f"file_{i}.py" for i in range(50)],
            affected_systems=[f"system_{i}" for i in range(10)],
        )
        assert result.suggested_agents <= 5

    def test_rationale_populated(self):
        """Rationale string is populated."""
        result = assess_complexity("Simple typo")
        assert len(result.rationale) > 0

    def test_performance_keywords_detected(self):
        """Performance keywords increase complexity."""
        result = assess_complexity("Memory leak causing timeout and slow throughput")
        factor_names = [f.name for f in result.factors]
        assert 'performance' in factor_names


# --- get_required_capabilities Tests ---


class TestGetRequiredCapabilities:
    """Tests for capability requirement extraction."""

    def test_empty_factors_returns_backend(self):
        """No factors defaults to backend capability."""
        assessment = assess_complexity("Simple bug")
        caps = get_required_capabilities(assessment)
        assert 'backend' in caps

    def test_multi_service_needs_backend_infra(self):
        """Multi-service bugs need backend and infra."""
        assessment = assess_complexity("Kubernetes microservice failure")
        caps = get_required_capabilities(assessment)
        assert 'backend' in caps
        assert 'infra' in caps

    def test_data_layer_needs_data(self):
        """Data layer bugs need data capability."""
        assessment = assess_complexity("Database schema migration failed")
        caps = get_required_capabilities(assessment)
        assert 'data' in caps

    def test_capabilities_sorted(self):
        """Returned capabilities are sorted alphabetically."""
        assessment = assess_complexity(
            "Kubernetes database timeout with concurrent auth issue"
        )
        caps = get_required_capabilities(assessment)
        assert caps == sorted(caps)


# --- partition_blast_radius Tests ---


class TestPartitionBlastRadius:
    """Tests for blast radius partitioning."""

    def test_basic_partitioning(self, simple_agents, simple_zones):
        """Zones are assigned to matching agents."""
        assignments = partition_blast_radius(simple_zones, simple_agents)
        assert len(assignments) == 2

        # Check agents assigned to matching zones
        agent_names = {a.agent_name for a in assignments}
        assert len(agent_names) == 2  # No duplicate assignments

    def test_capability_matching(self, simple_agents, simple_zones):
        """Agents matched to zones by capability."""
        assignments = partition_blast_radius(simple_zones, simple_agents)

        # Backend zone should go to backend agent
        api_assignment = next(a for a in assignments if a.zone.name == 'api-layer')
        assert api_assignment.agent_name == 'backend'

        # Frontend zone should go to frontend agent
        ui_assignment = next(a for a in assignments if a.zone.name == 'ui-layer')
        assert ui_assignment.agent_name == 'frontend'

    def test_more_zones_than_agents_raises(self, simple_agents):
        """More zones than agents raises ValueError."""
        zones = [
            WorkZone(name=f'zone-{i}', description=f'Zone {i}')
            for i in range(5)
        ]
        with pytest.raises(ValueError, match='More zones'):
            partition_blast_radius(zones, simple_agents)

    def test_fewer_zones_than_agents(self, simple_agents):
        """Fewer zones than agents assigns subset."""
        zones = [
            WorkZone(
                name='single-zone',
                description='Only zone',
                required_capabilities=['backend'],
            ),
        ]
        assignments = partition_blast_radius(zones, simple_agents)
        assert len(assignments) == 1
        assert assignments[0].agent_name == 'backend'

    def test_no_capability_requirements_fallback(self):
        """Zones without required capabilities get neutral scoring."""
        agents = [
            AgentProfile(name='agent-a'),
            AgentProfile(name='agent-b'),
        ]
        zones = [
            WorkZone(name='generic', description='No specific requirements'),
        ]
        assignments = partition_blast_radius(zones, agents)
        assert len(assignments) == 1


# --- _calculate_agent_zone_score Tests ---


class TestAgentZoneScore:
    """Tests for agent-zone match scoring."""

    def test_perfect_match(self):
        """Agent with all required capabilities scores high."""
        agent = AgentProfile(
            name='backend',
            capabilities=[AgentCapability(name='backend', proficiency=1.0)],
        )
        zone = WorkZone(
            name='api',
            description='API zone',
            required_capabilities=['backend'],
        )
        score = _calculate_agent_zone_score(agent, zone)
        assert score == 1.0

    def test_no_match(self):
        """Agent with no matching capabilities scores low."""
        agent = AgentProfile(
            name='frontend',
            capabilities=[AgentCapability(name='frontend', proficiency=1.0)],
        )
        zone = WorkZone(
            name='api',
            description='API zone',
            required_capabilities=['backend'],
        )
        score = _calculate_agent_zone_score(agent, zone)
        assert score == 0.0

    def test_partial_match(self):
        """Agent with some capabilities scores proportionally."""
        agent = AgentProfile(
            name='fullstack',
            capabilities=[
                AgentCapability(name='backend', proficiency=0.8),
                AgentCapability(name='frontend', proficiency=0.6),
            ],
        )
        zone = WorkZone(
            name='mixed',
            description='Mixed zone',
            required_capabilities=['backend', 'data'],
        )
        score = _calculate_agent_zone_score(agent, zone)
        # 1/2 match ratio (0.5 * 0.6) + proficiency 0.8 (0.8 * 0.4) = 0.3 + 0.32
        assert 0.0 < score < 1.0

    def test_no_requirements_neutral(self):
        """No requirements gives neutral score."""
        agent = AgentProfile(name='any')
        zone = WorkZone(name='generic', description='No requirements')
        score = _calculate_agent_zone_score(agent, zone)
        assert score == 0.5


# --- create_session_config Tests ---


class TestCreateSessionConfig:
    """Tests for session config creation."""

    def test_config_creation(self, simple_agents, simple_zones):
        """Creates complete session config."""
        config = create_session_config(
            bug_description='API timeout under load',
            lead_agent='backend',
            agents=simple_agents,
            zones=simple_zones,
            session_folder='temp/DEBUG_REPORTS/session-2026-02-15',
            debug_session_id='DBG-2026-02-15-001',
        )
        assert config.lead_agent == 'backend'
        assert config.agent_count == 2
        assert config.debug_session_id == 'DBG-2026-02-15-001'
        assert config.complexity is not None

    def test_config_agent_names(self, simple_agents, simple_zones):
        """Config tracks all agent names."""
        config = create_session_config(
            bug_description='Test bug',
            lead_agent='backend',
            agents=simple_agents,
            zones=simple_zones,
            session_folder='temp/sessions/test',
            debug_session_id='DBG-001',
        )
        assert len(config.agent_names) == 2

    def test_config_with_context(self, simple_agents, simple_zones):
        """Context is passed through to complexity assessment."""
        config = create_session_config(
            bug_description='Bug in API',
            lead_agent='backend',
            agents=simple_agents,
            zones=simple_zones,
            session_folder='temp/sessions/test',
            debug_session_id='DBG-001',
            context='Kubernetes microservice with race condition',
        )
        assert config.complexity.overall_score > 0.1  # Context detected
