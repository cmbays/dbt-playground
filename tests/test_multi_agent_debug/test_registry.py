"""Tests for agent registry.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

import pytest

from scripts.lib.multi_agent_debug.exceptions import (
    AgentAlreadyAssignedError,
    AgentNotFoundError,
    NoAgentsAvailableError,
)
from scripts.lib.multi_agent_debug.models import (
    AgentStatus,
    WorkZone,
)
from scripts.lib.multi_agent_debug.registry import (
    AgentRegistry,
    create_default_registry,
)


# --- Fixtures ---


@pytest.fixture
def registry():
    """Create a fresh registry."""
    return AgentRegistry()


@pytest.fixture
def populated_registry():
    """Create a registry with agents registered."""
    reg = AgentRegistry()
    reg.register_agent('backend', capabilities=['backend', 'data'])
    reg.register_agent('frontend', capabilities=['frontend', 'performance'])
    reg.register_agent('infra', capabilities=['infra', 'security'])
    return reg


@pytest.fixture
def sample_zone():
    """Create a sample work zone."""
    return WorkZone(
        name='api-zone',
        description='API investigation zone',
        required_capabilities=['backend'],
    )


# --- Registration Tests ---


class TestAgentRegistration:
    """Tests for agent registration."""

    def test_register_agent(self, registry):
        """Register a new agent."""
        profile = registry.register_agent('backend', capabilities=['backend', 'data'])
        assert profile.name == 'backend'
        assert 'backend' in profile.capability_names
        assert 'data' in profile.capability_names
        assert registry.agent_count == 1

    def test_register_with_proficiencies(self, registry):
        """Register agent with custom proficiencies."""
        profile = registry.register_agent(
            'backend',
            capabilities=['backend', 'data'],
            proficiencies={'backend': 1.0, 'data': 0.6},
        )
        assert profile.get_proficiency('backend') == 1.0
        assert profile.get_proficiency('data') == 0.6

    def test_register_multiple_agents(self, registry):
        """Register multiple agents."""
        registry.register_agent('a', capabilities=['backend'])
        registry.register_agent('b', capabilities=['frontend'])
        registry.register_agent('c', capabilities=['infra'])
        assert registry.agent_count == 3

    def test_unregister_agent(self, populated_registry):
        """Unregister an agent."""
        populated_registry.unregister_agent('backend')
        assert populated_registry.agent_count == 2

    def test_unregister_nonexistent_raises(self, registry):
        """Unregistering nonexistent agent raises error."""
        with pytest.raises(AgentNotFoundError):
            registry.unregister_agent('nonexistent')

    def test_get_agent(self, populated_registry):
        """Get agent by name."""
        agent = populated_registry.get_agent('backend')
        assert agent.name == 'backend'

    def test_get_agent_not_found(self, populated_registry):
        """Getting nonexistent agent raises error."""
        with pytest.raises(AgentNotFoundError):
            populated_registry.get_agent('nonexistent')

    def test_get_all_agents(self, populated_registry):
        """Get all registered agents."""
        agents = populated_registry.get_all_agents()
        assert len(agents) == 3
        names = {a.name for a in agents}
        assert names == {'backend', 'frontend', 'infra'}


# --- Availability Tests ---


class TestAgentAvailability:
    """Tests for agent availability queries."""

    def test_available_count(self, populated_registry):
        """Available count tracks correctly."""
        assert populated_registry.available_count == 3

    def test_get_available_agents_all(self, populated_registry):
        """All agents available by default."""
        available = populated_registry.get_available_agents()
        assert len(available) == 3

    def test_get_available_with_capability(self, populated_registry):
        """Filter by required capability."""
        available = populated_registry.get_available_agents(
            required_capabilities=['backend'],
        )
        assert len(available) == 1
        assert available[0].name == 'backend'

    def test_get_available_with_multiple_capabilities(self, populated_registry):
        """Filter by multiple capabilities (OR match)."""
        available = populated_registry.get_available_agents(
            required_capabilities=['backend', 'frontend'],
        )
        assert len(available) == 2

    def test_no_matching_capability(self, populated_registry):
        """No agents match required capability."""
        available = populated_registry.get_available_agents(
            required_capabilities=['quantum_computing'],
        )
        assert len(available) == 0

    def test_find_best_agents(self, populated_registry):
        """Find best agents by capability match."""
        best = populated_registry.find_best_agents(
            required_capabilities=['backend'],
            count=1,
        )
        assert len(best) == 1
        assert best[0].name == 'backend'

    def test_find_best_agents_insufficient(self, populated_registry):
        """Not enough agents available raises error."""
        with pytest.raises(NoAgentsAvailableError):
            populated_registry.find_best_agents(
                required_capabilities=['backend'],
                count=5,
            )


# --- Assignment Tests ---


class TestAgentAssignment:
    """Tests for agent assignment operations."""

    def test_assign_agent(self, populated_registry, sample_zone):
        """Assign agent to work zone."""
        assignment = populated_registry.assign_agent(
            'backend', 'session-001', sample_zone,
        )
        assert assignment.agent_name == 'backend'
        assert assignment.zone.name == 'api-zone'
        assert assignment.status == AgentStatus.ASSIGNED
        assert assignment.started_at is not None

    def test_assign_updates_session_count(self, populated_registry, sample_zone):
        """Assignment increments current_sessions."""
        populated_registry.assign_agent('backend', 'session-001', sample_zone)
        agent = populated_registry.get_agent('backend')
        assert agent.current_sessions == 1

    def test_assign_nonexistent_raises(self, populated_registry, sample_zone):
        """Assigning nonexistent agent raises error."""
        with pytest.raises(AgentNotFoundError):
            populated_registry.assign_agent(
                'nonexistent', 'session-001', sample_zone,
            )

    def test_assign_same_zone_raises(self, populated_registry, sample_zone):
        """Assigning same zone twice raises error."""
        populated_registry.assign_agent('backend', 'session-001', sample_zone)
        with pytest.raises(AgentAlreadyAssignedError):
            populated_registry.assign_agent('backend', 'session-001', sample_zone)

    def test_update_agent_status(self, populated_registry, sample_zone):
        """Update agent status."""
        populated_registry.assign_agent('backend', 'session-001', sample_zone)
        assignment = populated_registry.update_agent_status(
            'backend',
            'session-001',
            AgentStatus.INVESTIGATING,
        )
        assert assignment.status == AgentStatus.INVESTIGATING

    def test_update_status_complete_sets_timestamp(
        self, populated_registry, sample_zone,
    ):
        """Completing sets completed_at timestamp."""
        populated_registry.assign_agent('backend', 'session-001', sample_zone)
        assignment = populated_registry.update_agent_status(
            'backend',
            'session-001',
            AgentStatus.COMPLETE,
            findings_path='temp/findings.md',
        )
        assert assignment.status == AgentStatus.COMPLETE
        assert assignment.completed_at is not None
        assert assignment.findings_path == 'temp/findings.md'

    def test_update_nonexistent_raises(self, populated_registry):
        """Updating nonexistent agent raises error."""
        with pytest.raises(AgentNotFoundError):
            populated_registry.update_agent_status(
                'nonexistent', 'session-001', AgentStatus.COMPLETE,
            )

    def test_release_agent(self, populated_registry, sample_zone):
        """Release agent decrements session count."""
        populated_registry.assign_agent('backend', 'session-001', sample_zone)
        assert populated_registry.get_agent('backend').current_sessions == 1

        populated_registry.release_agent('backend', 'session-001')
        assert populated_registry.get_agent('backend').current_sessions == 0

    def test_release_nonexistent_raises(self, populated_registry):
        """Releasing nonexistent agent raises error."""
        with pytest.raises(AgentNotFoundError):
            populated_registry.release_agent('nonexistent', 'session-001')

    def test_get_agent_assignments(self, populated_registry, sample_zone):
        """Get all assignments for an agent."""
        populated_registry.assign_agent('backend', 'session-001', sample_zone)
        assignments = populated_registry.get_agent_assignments('backend')
        assert len(assignments) == 1

    def test_get_agent_assignments_not_found(self, populated_registry):
        """Getting assignments for nonexistent agent raises error."""
        with pytest.raises(AgentNotFoundError):
            populated_registry.get_agent_assignments('nonexistent')


# --- Utilization Tests ---


class TestUtilization:
    """Tests for utilization tracking."""

    def test_get_utilization(self, populated_registry, sample_zone):
        """Get utilization metrics."""
        populated_registry.assign_agent('backend', 'session-001', sample_zone)

        utilization = populated_registry.get_utilization()
        assert 'backend' in utilization
        assert utilization['backend']['current_sessions'] == 1
        assert utilization['backend']['is_available'] is False
        assert utilization['frontend']['current_sessions'] == 0
        assert utilization['frontend']['is_available'] is True


# --- Default Registry Tests ---


class TestDefaultRegistry:
    """Tests for default registry creation."""

    def test_create_default_registry(self):
        """Default registry has pre-defined agents."""
        registry = create_default_registry()
        assert registry.agent_count == 5  # backend, frontend, data, infra, security

    def test_default_agents_have_capabilities(self):
        """Default agents have expected capabilities."""
        registry = create_default_registry()

        backend = registry.get_agent('backend')
        assert backend.has_capability('backend')
        assert backend.has_capability('data')

        frontend = registry.get_agent('frontend')
        assert frontend.has_capability('frontend')

        infra = registry.get_agent('infra')
        assert infra.has_capability('infra')
        assert infra.has_capability('security')

    def test_default_agents_available(self):
        """All default agents start available."""
        registry = create_default_registry()
        assert registry.available_count == 5


# --- Clear Tests ---


class TestClear:
    """Tests for clearing registry."""

    def test_clear_removes_all(self, populated_registry):
        """Clear removes all agents and assignments."""
        populated_registry.clear()
        assert populated_registry.agent_count == 0
        assert populated_registry.available_count == 0
