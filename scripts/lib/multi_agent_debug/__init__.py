"""Multi-Agent Debug Coordination library for WAVE3-030.

This module provides coordination protocol, agent registry,
session orchestration, conflict detection, and merge resolution
for multi-agent debugging workflows.

Part of Wave 3 P3: Multi-Agent Scale (Issue #266)

Core Components:
    - protocol: Complexity assessment and blast radius partitioning
    - registry: Agent capability tracking and assignment management
    - orchestrator: Multi-agent session lifecycle (Day 2)
    - conflict: Conflict detection and evidence weighting (Day 3)
    - merge: Merge resolution engine (Day 3)
    - manifest: Session manifest generation (Day 2)
    - lessons: LESSONS.md integration (Day 4)
"""

from scripts.lib.multi_agent_debug.exceptions import (
    AgentAlreadyAssignedError,
    AgentNotFoundError,
    InvalidSessionStateError,
    MergeConflictError,
    MultiAgentDebugError,
    NoAgentsAvailableError,
    SessionAlreadyExistsError,
    SessionNotFoundError,
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
    ComplexityFactor,
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
from scripts.lib.multi_agent_debug.protocol import (
    assess_complexity,
    create_session_config,
    get_required_capabilities,
    partition_blast_radius,
    SessionConfig,
)
from scripts.lib.multi_agent_debug.registry import (
    AgentRegistry,
    create_default_registry,
)

__all__ = [
    # Protocol
    'assess_complexity',
    'create_session_config',
    'get_required_capabilities',
    'partition_blast_radius',
    'SessionConfig',
    # Registry
    'AgentRegistry',
    'create_default_registry',
    # Models
    'AgentCapability',
    'AgentFindings',
    'AgentProfile',
    'AgentStatus',
    'Conflict',
    'ConflictResolution',
    'ConflictType',
    'ComplexityAssessment',
    'ComplexityFactor',
    'Evidence',
    'EvidenceType',
    'Finding',
    'LessonCandidate',
    'MergeResolution',
    'MultiAgentSession',
    'SessionStatus',
    'WorkAssignment',
    'WorkZone',
    # Exceptions
    'AgentAlreadyAssignedError',
    'AgentNotFoundError',
    'InvalidSessionStateError',
    'MergeConflictError',
    'MultiAgentDebugError',
    'NoAgentsAvailableError',
    'SessionAlreadyExistsError',
    'SessionNotFoundError',
]
