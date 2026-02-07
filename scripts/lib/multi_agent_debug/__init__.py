"""Multi-Agent Debug Coordination library for WAVE3-030.

This module provides coordination protocol, agent registry,
session orchestration, conflict detection, merge resolution,
and LESSONS.md integration for multi-agent debugging workflows.

Part of Wave 3 P3: Multi-Agent Scale (Issue #266)

Core Components:
    - protocol: Complexity assessment and blast radius partitioning
    - registry: Agent capability tracking and assignment management
    - orchestrator: Multi-agent session lifecycle
    - manifest: Session manifest generation
    - conflict_detector: Conflict detection and evidence weighting
    - merge_resolver: Merge resolution engine
    - lessons: LESSONS.md integration and event emission
    - models: Shared data models (dataclasses)
    - exceptions: Custom exception hierarchy
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
from scripts.lib.multi_agent_debug.orchestrator import (
    SessionOrchestrator,
)
from scripts.lib.multi_agent_debug.manifest import (
    generate_manifest,
    write_manifest,
    update_manifest,
)
from scripts.lib.multi_agent_debug.conflict_detector import (
    detect_conflicts,
    resolve_conflict_by_evidence,
    calculate_finding_weight,
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
    format_lesson_for_review,
    format_all_lessons,
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
    # Orchestrator (Day 2)
    'SessionOrchestrator',
    # Manifest (Day 2)
    'generate_manifest',
    'write_manifest',
    'update_manifest',
    # Conflict Detector (Day 3)
    'detect_conflicts',
    'resolve_conflict_by_evidence',
    'calculate_finding_weight',
    'get_conflict_summary',
    # Merge Resolver (Day 3)
    'merge_findings',
    'generate_resolution_document',
    'write_resolution_document',
    # Lessons (Day 4)
    'extract_debate_patterns',
    'emit_lesson_events',
    'format_lesson_for_review',
    'format_all_lessons',
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
