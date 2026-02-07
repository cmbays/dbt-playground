"""Agent Registry for Multi-Agent Debug Coordination.

Tracks agent capabilities, availability, and assignments.
Provides lookup for matching agents to work zones based on
required capabilities.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

from datetime import UTC, datetime
from typing import Optional

from scripts.lib.multi_agent_debug.exceptions import (
    AgentAlreadyAssignedError,
    AgentNotFoundError,
    NoAgentsAvailableError,
)
from scripts.lib.multi_agent_debug.models import (
    AgentCapability,
    AgentProfile,
    AgentStatus,
    WorkAssignment,
    WorkZone,
)


class AgentRegistry:
    """Registry for tracking debug agent profiles and assignments.

    Provides agent registration, capability-based lookup,
    and assignment tracking for multi-agent debug sessions.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._agents: dict[str, AgentProfile] = {}
        self._assignments: dict[str, list[WorkAssignment]] = {}

    @property
    def agent_count(self) -> int:
        """Total number of registered agents."""
        return len(self._agents)

    @property
    def available_count(self) -> int:
        """Number of agents available for assignment."""
        return sum(1 for a in self._agents.values() if a.is_available)

    def register_agent(
        self,
        name: str,
        capabilities: Optional[list[str]] = None,
        proficiencies: Optional[dict[str, float]] = None,
        max_concurrent: int = 1,
    ) -> AgentProfile:
        """Register a new agent in the registry.

        Args:
            name: Unique agent name
            capabilities: List of capability names (e.g., ['backend', 'data'])
            proficiencies: Optional map of capability -> proficiency (0.0-1.0)
            max_concurrent: Maximum concurrent sessions

        Returns:
            The registered agent profile
        """
        caps = []
        if capabilities:
            for cap_name in capabilities:
                proficiency = 1.0
                if proficiencies and cap_name in proficiencies:
                    proficiency = proficiencies[cap_name]
                caps.append(AgentCapability(
                    name=cap_name,
                    proficiency=proficiency,
                ))

        profile = AgentProfile(
            name=name,
            capabilities=caps,
            max_concurrent_sessions=max_concurrent,
        )

        self._agents[name] = profile
        self._assignments[name] = []

        return profile

    def unregister_agent(self, name: str) -> None:
        """Remove an agent from the registry.

        Args:
            name: Agent name to remove

        Raises:
            AgentNotFoundError: If agent not found
        """
        if name not in self._agents:
            raise AgentNotFoundError(name)
        del self._agents[name]
        del self._assignments[name]

    def get_agent(self, name: str) -> AgentProfile:
        """Get an agent profile by name.

        Args:
            name: Agent name

        Returns:
            Agent profile

        Raises:
            AgentNotFoundError: If agent not found
        """
        if name not in self._agents:
            raise AgentNotFoundError(name)
        return self._agents[name]

    def get_all_agents(self) -> list[AgentProfile]:
        """Get all registered agents.

        Returns:
            List of all agent profiles
        """
        return list(self._agents.values())

    def get_available_agents(
        self,
        required_capabilities: Optional[list[str]] = None,
    ) -> list[AgentProfile]:
        """Get agents that are available and match capabilities.

        Args:
            required_capabilities: Optional list of required capabilities

        Returns:
            List of matching available agents
        """
        available = [a for a in self._agents.values() if a.is_available]

        if required_capabilities:
            matched = []
            for agent in available:
                has_any = any(
                    agent.has_capability(cap)
                    for cap in required_capabilities
                )
                if has_any:
                    matched.append(agent)
            return matched

        return available

    def find_best_agents(
        self,
        required_capabilities: list[str],
        count: int,
    ) -> list[AgentProfile]:
        """Find the best N agents for given capabilities.

        Ranks agents by capability match and proficiency,
        returns the top N available agents.

        Args:
            required_capabilities: Capabilities needed
            count: Number of agents to return

        Returns:
            List of best-matching agents

        Raises:
            NoAgentsAvailableError: If not enough agents available
        """
        available = self.get_available_agents()
        if not available:
            raise NoAgentsAvailableError(required_capabilities)

        # Score each agent
        scored: list[tuple[float, AgentProfile]] = []
        for agent in available:
            score = 0.0
            for cap in required_capabilities:
                if agent.has_capability(cap):
                    score += agent.get_proficiency(cap)
            scored.append((score, agent))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Return top N
        result = [agent for _, agent in scored[:count]]

        if len(result) < count:
            raise NoAgentsAvailableError(required_capabilities)

        return result

    def assign_agent(
        self,
        agent_name: str,
        session_id: str,
        zone: WorkZone,
    ) -> WorkAssignment:
        """Assign an agent to a work zone in a session.

        Args:
            agent_name: Name of agent to assign
            session_id: Session ID
            zone: Work zone to assign

        Returns:
            The work assignment

        Raises:
            AgentNotFoundError: If agent not found
            AgentAlreadyAssignedError: If agent already in this session
        """
        if agent_name not in self._agents:
            raise AgentNotFoundError(agent_name)

        agent = self._agents[agent_name]

        # Check if already assigned to this zone in this session
        for existing in self._assignments[agent_name]:
            if existing.session_id == session_id and existing.zone.name == zone.name:
                raise AgentAlreadyAssignedError(agent_name, session_id)

        assignment = WorkAssignment(
            agent_name=agent_name,
            session_id=session_id,
            zone=zone,
            status=AgentStatus.ASSIGNED,
            started_at=datetime.now(UTC),
        )

        self._assignments[agent_name].append(assignment)
        agent.current_sessions += 1

        return assignment

    def update_agent_status(
        self,
        agent_name: str,
        session_id: str,
        status: AgentStatus,
        findings_path: Optional[str] = None,
    ) -> WorkAssignment:
        """Update an agent's status in a session.

        Args:
            agent_name: Agent name
            session_id: Session ID (used for identification context)
            status: New status
            findings_path: Path to findings file (when complete)

        Returns:
            Updated work assignment

        Raises:
            AgentNotFoundError: If agent not found
        """
        if agent_name not in self._agents:
            raise AgentNotFoundError(agent_name)

        assignments = self._assignments[agent_name]
        if not assignments:
            raise AgentNotFoundError(
                f"No assignments found for agent '{agent_name}'"
            )

        # Find the assignment for this specific session
        assignment = None
        for a in assignments:
            if a.session_id == session_id:
                assignment = a
                break

        if not assignment:
            raise AgentNotFoundError(
                f"No assignment found for agent '{agent_name}' in session '{session_id}'"
            )

        assignment.status = status

        if findings_path:
            assignment.findings_path = findings_path

        if status == AgentStatus.COMPLETE:
            assignment.completed_at = datetime.now(UTC)

        return assignment

    def release_agent(self, agent_name: str, session_id: str) -> None:
        """Release an agent from a session assignment.

        Args:
            agent_name: Agent name
            session_id: Session to release from

        Raises:
            AgentNotFoundError: If agent not found
        """
        if agent_name not in self._agents:
            raise AgentNotFoundError(agent_name)

        agent = self._agents[agent_name]
        assignments = self._assignments[agent_name]

        # Find and remove the assignment for this session
        assignment_to_remove = None
        for assignment in assignments:
            if assignment.session_id == session_id:
                assignment_to_remove = assignment
                break

        if assignment_to_remove:
            assignments.remove(assignment_to_remove)
            if agent.current_sessions > 0:
                agent.current_sessions -= 1

    def get_agent_assignments(self, agent_name: str) -> list[WorkAssignment]:
        """Get all assignments for an agent.

        Args:
            agent_name: Agent name

        Returns:
            List of work assignments

        Raises:
            AgentNotFoundError: If agent not found
        """
        if agent_name not in self._agents:
            raise AgentNotFoundError(agent_name)
        return list(self._assignments[agent_name])

    def get_session_agents(self, session_id: str) -> list[AgentProfile]:
        """Get all agents assigned to a specific session.

        Args:
            session_id: Session ID

        Returns:
            List of agent profiles with assignments in this session
        """
        agents_in_session = []
        for agent_name, assignments in self._assignments.items():
            # Check if any assignments match this session
            for assignment in assignments:
                if assignment.session_id == session_id:
                    agents_in_session.append(self._agents[agent_name])
                    break  # Don't add same agent twice
        return agents_in_session

    def get_utilization(self) -> dict[str, dict]:
        """Get utilization metrics for all agents.

        Returns:
            Dict mapping agent name to utilization info
        """
        utilization = {}
        for name, agent in self._agents.items():
            utilization[name] = {
                'name': name,
                'capabilities': agent.capability_names,
                'current_sessions': agent.current_sessions,
                'max_sessions': agent.max_concurrent_sessions,
                'is_available': agent.is_available,
                'active_assignments': len(self._assignments[name]),
            }
        return utilization

    def clear(self) -> None:
        """Clear all agents and assignments."""
        self._agents.clear()
        self._assignments.clear()


# --- Default Agent Profiles ---

# Pre-defined agent profiles for common debug scenarios
DEFAULT_AGENTS: dict[str, dict] = {
    'backend': {
        'capabilities': ['backend', 'data', 'security'],
        'proficiencies': {'backend': 1.0, 'data': 0.8, 'security': 0.6},
    },
    'frontend': {
        'capabilities': ['frontend', 'performance'],
        'proficiencies': {'frontend': 1.0, 'performance': 0.7},
    },
    'data': {
        'capabilities': ['data', 'backend'],
        'proficiencies': {'data': 1.0, 'backend': 0.5},
    },
    'infra': {
        'capabilities': ['infra', 'performance', 'security'],
        'proficiencies': {'infra': 1.0, 'performance': 0.8, 'security': 0.7},
    },
    'security': {
        'capabilities': ['security', 'backend', 'infra'],
        'proficiencies': {'security': 1.0, 'backend': 0.6, 'infra': 0.5},
    },
}


def create_default_registry() -> AgentRegistry:
    """Create a registry pre-populated with default agent profiles.

    Returns:
        AgentRegistry with default agents registered
    """
    registry = AgentRegistry()
    for name, config in DEFAULT_AGENTS.items():
        registry.register_agent(
            name=name,
            capabilities=config['capabilities'],
            proficiencies=config['proficiencies'],
        )
    return registry
