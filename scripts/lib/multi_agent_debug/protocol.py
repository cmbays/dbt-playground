"""Coordination Protocol for Multi-Agent Debug Sessions.

Implements the hub-and-spoke coordination model where a lead coordinator
orchestrates specialist agents. Includes complexity assessment to determine
optimal agent count and blast radius partitioning.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

from dataclasses import dataclass
from typing import Optional

from scripts.lib.multi_agent_debug.models import (
    AgentCapability,
    AgentProfile,
    ComplexityAssessment,
    ComplexityFactor,
    WorkAssignment,
    WorkZone,
)


# --- Complexity Thresholds ---

# Map complexity score ranges to suggested agent counts
COMPLEXITY_AGENT_MAP: list[tuple[float, int]] = [
    (0.0, 1),    # 0.0 - 0.2: single agent
    (0.2, 1),    # 0.2 - 0.4: single agent
    (0.4, 2),    # 0.4 - 0.6: two agents
    (0.6, 3),    # 0.6 - 0.8: three agents
    (0.8, 4),    # 0.8 - 0.9: four agents
    (0.9, 5),    # 0.9 - 1.0: five agents
]

# Keywords that indicate specific complexity factors
COMPLEXITY_KEYWORDS: dict[str, list[str]] = {
    'multi_service': [
        'microservice', 'cross-service', 'distributed', 'api gateway',
        'service mesh', 'kubernetes', 'docker', 'container',
    ],
    'data_layer': [
        'database', 'migration', 'schema', 'query', 'index',
        'transaction', 'deadlock', 'connection pool',
    ],
    'concurrency': [
        'race condition', 'concurrent', 'parallel', 'async', 'thread',
        'mutex', 'lock', 'semaphore', 'queue',
    ],
    'state_management': [
        'state', 'cache', 'session', 'stale', 'inconsistent',
        'eventual consistency', 'replication',
    ],
    'security': [
        'auth', 'permission', 'token', 'csrf', 'xss', 'injection',
        'credential', 'certificate',
    ],
    'performance': [
        'slow', 'timeout', 'latency', 'memory leak', 'cpu',
        'throughput', 'bottleneck', 'n+1',
    ],
    'infrastructure': [
        'deploy', 'ci/cd', 'pipeline', 'network', 'dns',
        'load balancer', 'proxy', 'firewall',
    ],
}

# Capability requirements for complexity factors
FACTOR_CAPABILITIES: dict[str, list[str]] = {
    'multi_service': ['backend', 'infra'],
    'data_layer': ['data', 'backend'],
    'concurrency': ['backend'],
    'state_management': ['backend', 'data'],
    'security': ['security', 'backend'],
    'performance': ['backend', 'infra'],
    'infrastructure': ['infra'],
}


def assess_complexity(
    bug_description: str,
    context: Optional[str] = None,
    affected_files: Optional[list[str]] = None,
    affected_systems: Optional[list[str]] = None,
) -> ComplexityAssessment:
    """Assess bug complexity to determine optimal agent count.

    Analyzes the bug description and context for complexity factors
    (multi-service, data layer, concurrency, etc.) and suggests
    an appropriate number of agents.

    Args:
        bug_description: Description of the bug
        context: Additional context (file paths, stack traces, etc.)
        affected_files: Known affected files
        affected_systems: Known affected systems/services

    Returns:
        ComplexityAssessment with score and suggested agent count
    """
    factors: list[ComplexityFactor] = []
    search_text = bug_description.lower()
    if context:
        search_text += ' ' + context.lower()

    # Analyze keyword presence
    for factor_name, keywords in COMPLEXITY_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in search_text]
        if matches:
            # Score based on number of keyword matches
            score = min(len(matches) / 3.0, 1.0)
            factors.append(ComplexityFactor(
                name=factor_name,
                score=score,
                description=f"Detected: {', '.join(matches[:3])}",
            ))

    # Factor in affected files count
    if affected_files:
        file_count = len(affected_files)
        if file_count > 10:
            factors.append(ComplexityFactor(
                name='large_blast_radius',
                score=min(file_count / 20.0, 1.0),
                description=f"{file_count} files affected",
            ))

    # Factor in affected systems count
    if affected_systems:
        system_count = len(affected_systems)
        if system_count > 1:
            factors.append(ComplexityFactor(
                name='multi_system',
                score=min(system_count / 5.0, 1.0),
                description=f"{system_count} systems affected",
            ))

    # Calculate overall score
    if not factors:
        overall_score = 0.1  # Simple bug, single agent
    else:
        overall_score = min(
            sum(f.score for f in factors) / len(factors) * 1.2,
            1.0,
        )

    # Map score to agent count
    suggested_agents = 1
    for threshold, count in COMPLEXITY_AGENT_MAP:
        if overall_score >= threshold:
            suggested_agents = count

    # Build rationale
    if not factors:
        rationale = "Simple bug with no complexity indicators. Single agent sufficient."
    else:
        factor_list = ', '.join(f.name for f in factors)
        rationale = (
            f"Complexity factors detected: {factor_list}. "
            f"Score {overall_score:.2f} suggests {suggested_agents} agent(s)."
        )

    return ComplexityAssessment(
        overall_score=overall_score,
        suggested_agents=suggested_agents,
        factors=factors,
        rationale=rationale,
    )


def get_required_capabilities(
    complexity: ComplexityAssessment,
) -> list[str]:
    """Determine required agent capabilities from complexity assessment.

    Args:
        complexity: The complexity assessment

    Returns:
        List of required capability names
    """
    capabilities: set[str] = set()

    for factor in complexity.factors:
        if factor.name in FACTOR_CAPABILITIES:
            capabilities.update(FACTOR_CAPABILITIES[factor.name])

    # Always include 'backend' as a base capability
    if not capabilities:
        capabilities.add('backend')

    return sorted(capabilities)


def partition_blast_radius(
    zones: list[WorkZone],
    agents: list[AgentProfile],
) -> list[WorkAssignment]:
    """Partition blast radius into non-overlapping work assignments.

    Matches agents to zones based on capability alignment. Each zone
    is assigned to the agent with the best capability match.

    Args:
        zones: Work zones to assign (pre-defined by lead agent)
        agents: Available agents to assign

    Returns:
        List of work assignments

    Raises:
        ValueError: If more zones than agents
    """
    if len(zones) > len(agents):
        raise ValueError(
            f"More zones ({len(zones)}) than available agents ({len(agents)}). "
            f"Reduce zone count or add agents."
        )

    assignments: list[WorkAssignment] = []
    assigned_agents: set[str] = set()

    for zone in zones:
        best_agent: Optional[AgentProfile] = None
        best_score = -1.0

        for agent in agents:
            if agent.name in assigned_agents:
                continue

            # Score agent-zone match based on capability alignment
            score = _calculate_agent_zone_score(agent, zone)
            if score > best_score:
                best_score = score
                best_agent = agent

        if best_agent is None:
            # Assign first unassigned agent (fallback)
            for agent in agents:
                if agent.name not in assigned_agents:
                    best_agent = agent
                    break

        if best_agent is not None:
            assignments.append(WorkAssignment(
                agent_name=best_agent.name,
                zone=zone,
            ))
            assigned_agents.add(best_agent.name)

    return assignments


def _calculate_agent_zone_score(
    agent: AgentProfile,
    zone: WorkZone,
) -> float:
    """Calculate how well an agent matches a work zone.

    Args:
        agent: Agent profile with capabilities
        zone: Work zone with required capabilities

    Returns:
        Match score (0.0 to 1.0)
    """
    if not zone.required_capabilities:
        return 0.5  # No requirements, neutral score

    matching_caps = 0
    total_proficiency = 0.0

    for required in zone.required_capabilities:
        if agent.has_capability(required):
            matching_caps += 1
            total_proficiency += agent.get_proficiency(required)

    if not zone.required_capabilities:
        return 0.5

    match_ratio = matching_caps / len(zone.required_capabilities)
    avg_proficiency = (
        total_proficiency / matching_caps if matching_caps > 0 else 0.0
    )

    # Combined score: 60% match ratio + 40% proficiency
    return match_ratio * 0.6 + avg_proficiency * 0.4


@dataclass
class SessionConfig:
    """Configuration for starting a multi-agent debug session."""

    bug_description: str
    lead_agent: str
    complexity: ComplexityAssessment
    zones: list[WorkZone]
    assignments: list[WorkAssignment]
    session_folder: str     # Path to DEBUG_REPORTS/session-{timestamp}/
    debug_session_id: str   # Links to DebugSessionTracker

    @property
    def agent_count(self) -> int:
        """Number of agents in this session."""
        return len(self.assignments)

    @property
    def agent_names(self) -> list[str]:
        """Names of all assigned agents."""
        return [a.agent_name for a in self.assignments]


def create_session_config(
    bug_description: str,
    lead_agent: str,
    agents: list[AgentProfile],
    zones: list[WorkZone],
    session_folder: str,
    debug_session_id: str,
    context: Optional[str] = None,
) -> SessionConfig:
    """Create a complete session configuration.

    Assesses complexity, partitions blast radius, and produces
    a ready-to-execute session config.

    Args:
        bug_description: Description of the bug
        lead_agent: Name of the lead coordinator agent
        agents: Available agents
        zones: Work zones to partition
        session_folder: Path for session artifacts
        debug_session_id: Link to parent debug session
        context: Additional context

    Returns:
        Complete session configuration
    """
    # Assess complexity
    affected_files = []
    for zone in zones:
        affected_files.extend(zone.files)
    affected_systems = []
    for zone in zones:
        affected_systems.extend(zone.systems)

    complexity = assess_complexity(
        bug_description=bug_description,
        context=context,
        affected_files=affected_files,
        affected_systems=list(set(affected_systems)),
    )

    # Partition work
    assignments = partition_blast_radius(zones, agents)

    return SessionConfig(
        bug_description=bug_description,
        lead_agent=lead_agent,
        complexity=complexity,
        zones=zones,
        assignments=assignments,
        session_folder=session_folder,
        debug_session_id=debug_session_id,
    )
