"""Data models for Multi-Agent Debug Coordination.

Provides typed dataclasses for multi-agent sessions, agent profiles,
work assignments, conflicts, and merge resolutions.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# --- Enums ---


class SessionStatus(Enum):
    """Multi-agent session lifecycle states."""

    SETUP = 'setup'
    INVESTIGATING = 'investigating'
    MERGING = 'merging'
    RESOLVED = 'resolved'
    ESCALATED = 'escalated'


class AgentStatus(Enum):
    """Agent assignment lifecycle states."""

    REGISTERED = 'registered'
    ASSIGNED = 'assigned'
    INVESTIGATING = 'investigating'
    COMPLETE = 'complete'
    BLOCKED = 'blocked'


class ConflictType(Enum):
    """Types of conflicts between agent findings."""

    ROOT_CAUSE_DISAGREEMENT = 'root_cause_disagreement'
    EVIDENCE_CONTRADICTION = 'evidence_contradiction'
    SCOPE_OVERLAP = 'scope_overlap'
    CLASSIFICATION_MISMATCH = 'classification_mismatch'


class ConflictResolution(Enum):
    """How a conflict was resolved."""

    EVIDENCE_WEIGHTED = 'evidence_weighted'
    HUMAN_ESCALATED = 'human_escalated'
    MERGED = 'merged'
    DEFERRED = 'deferred'


class EvidenceType(Enum):
    """Types of evidence with associated weights."""

    REPRODUCIBLE = 'reproducible'          # weight: 1.0
    LOG_CORRELATION = 'log_correlation'    # weight: 0.8
    CODE_ANALYSIS = 'code_analysis'        # weight: 0.6
    THEORY = 'theory'                      # weight: 0.3
    UNSUBSTANTIATED = 'unsubstantiated'    # weight: 0.1


# Evidence weight mapping
EVIDENCE_WEIGHTS: dict[EvidenceType, float] = {
    EvidenceType.REPRODUCIBLE: 1.0,
    EvidenceType.LOG_CORRELATION: 0.8,
    EvidenceType.CODE_ANALYSIS: 0.6,
    EvidenceType.THEORY: 0.3,
    EvidenceType.UNSUBSTANTIATED: 0.1,
}


# --- Complexity Assessment ---


@dataclass
class ComplexityFactor:
    """A factor contributing to bug complexity."""

    name: str
    score: float       # 0.0 to 1.0
    description: str


@dataclass
class ComplexityAssessment:
    """Assessment of bug complexity to determine agent count."""

    overall_score: float    # 0.0 to 1.0
    suggested_agents: int   # 1 to 5
    factors: list[ComplexityFactor] = field(default_factory=list)
    rationale: str = ''

    def __post_init__(self):
        """Validate assessment."""
        if not 0.0 <= self.overall_score <= 1.0:
            raise ValueError(
                f"Complexity score must be 0.0-1.0, got {self.overall_score}"
            )
        if not 1 <= self.suggested_agents <= 5:
            raise ValueError(
                f"Suggested agents must be 1-5, got {self.suggested_agents}"
            )


# --- Agent Models ---


@dataclass
class AgentCapability:
    """A specific capability an agent possesses."""

    name: str                # e.g., 'backend', 'frontend', 'data', 'infra'
    proficiency: float = 1.0  # 0.0 to 1.0


@dataclass
class AgentProfile:
    """Profile of a debug agent with capabilities."""

    name: str
    capabilities: list[AgentCapability] = field(default_factory=list)
    max_concurrent_sessions: int = 1
    current_sessions: int = 0

    @property
    def is_available(self) -> bool:
        """Check if agent can take on more work."""
        return self.current_sessions < self.max_concurrent_sessions

    @property
    def capability_names(self) -> list[str]:
        """Get list of capability names."""
        return [c.name for c in self.capabilities]

    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capability_names

    def get_proficiency(self, capability: str) -> float:
        """Get proficiency for a capability (0.0 if not present)."""
        for cap in self.capabilities:
            if cap.name == capability:
                return cap.proficiency
        return 0.0


# --- Work Assignment Models ---


@dataclass
class WorkZone:
    """A partition of the blast radius for agent investigation."""

    name: str
    description: str
    files: list[str] = field(default_factory=list)
    systems: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)


@dataclass
class WorkAssignment:
    """Assignment of an agent to a work zone."""

    agent_name: str
    zone: WorkZone
    status: AgentStatus = AgentStatus.ASSIGNED
    findings_path: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# --- Findings Models ---


@dataclass
class Evidence:
    """A piece of evidence supporting a finding."""

    description: str
    evidence_type: EvidenceType
    source: str = ''        # file path, log entry, etc.
    data: str = ''          # actual evidence content

    @property
    def weight(self) -> float:
        """Get the weight for this evidence type."""
        return EVIDENCE_WEIGHTS[self.evidence_type]


@dataclass
class Finding:
    """A single finding from an agent's investigation."""

    description: str
    classification: str     # 'root_cause', 'symptom', 'contributing'
    evidence: list[Evidence] = field(default_factory=list)
    confidence: float = 0.5  # 0.0 to 1.0
    files_involved: list[str] = field(default_factory=list)
    proposed_fix: Optional[str] = None

    @property
    def evidence_weight(self) -> float:
        """Calculate total evidence weight for this finding."""
        if not self.evidence:
            return 0.0
        return sum(e.weight for e in self.evidence) / len(self.evidence)


@dataclass
class AgentFindings:
    """Complete findings from one agent's investigation."""

    agent_name: str
    session_id: str
    zone: WorkZone
    findings: list[Finding] = field(default_factory=list)
    cross_scope_observations: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    investigation_time_minutes: int = 0

    @property
    def primary_finding(self) -> Optional[Finding]:
        """Get the highest-confidence finding."""
        if not self.findings:
            return None
        return max(self.findings, key=lambda f: f.confidence)

    @property
    def root_cause_findings(self) -> list[Finding]:
        """Get findings classified as root cause."""
        return [f for f in self.findings if f.classification == 'root_cause']


# --- Conflict Models ---


@dataclass
class Conflict:
    """A conflict between agent findings."""

    conflict_id: str
    conflict_type: ConflictType
    agent_a: str
    agent_b: str
    finding_a: Finding
    finding_b: Finding
    description: str
    resolution: Optional[ConflictResolution] = None
    resolution_rationale: Optional[str] = None
    resolved_finding: Optional[Finding] = None

    @property
    def is_resolved(self) -> bool:
        """Check if conflict has been resolved."""
        return self.resolution is not None


# --- Merge Resolution Models ---


@dataclass
class MergeResolution:
    """Result of merging multiple agent findings."""

    session_id: str
    lead_agent: str
    participating_agents: list[str]
    consensus_findings: list[Finding] = field(default_factory=list)
    conflicts: list[Conflict] = field(default_factory=list)
    agreed_fixes: list[dict] = field(default_factory=list)
    deployment_order: list[str] = field(default_factory=list)
    unresolved_conflicts: list[Conflict] = field(default_factory=list)
    lessons_extracted: list[str] = field(default_factory=list)
    resolution_time_minutes: int = 0

    @property
    def has_unresolved_conflicts(self) -> bool:
        """Check if there are unresolved conflicts requiring escalation."""
        return len(self.unresolved_conflicts) > 0

    @property
    def total_conflicts(self) -> int:
        """Total number of conflicts found."""
        return len(self.conflicts) + len(self.unresolved_conflicts)


# --- Session Models ---


@dataclass
class MultiAgentSession:
    """A multi-agent debugging session."""

    session_id: str
    debug_session_id: str    # Links to DebugSession from WAVE3-020
    bug_description: str
    lead_agent: str
    status: SessionStatus = SessionStatus.SETUP
    complexity: Optional[ComplexityAssessment] = None
    assignments: list[WorkAssignment] = field(default_factory=list)
    agent_findings: list[AgentFindings] = field(default_factory=list)
    resolution: Optional[MergeResolution] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def agent_count(self) -> int:
        """Number of agents assigned."""
        return len(self.assignments)

    @property
    def agents_complete(self) -> int:
        """Number of agents that have completed investigation."""
        return sum(
            1 for a in self.assignments
            if a.status == AgentStatus.COMPLETE
        )

    @property
    def all_agents_complete(self) -> bool:
        """Check if all agents have completed their investigation."""
        return (
            len(self.assignments) > 0
            and all(
                a.status == AgentStatus.COMPLETE
                for a in self.assignments
            )
        )

    def get_assignment(self, agent_name: str) -> Optional[WorkAssignment]:
        """Get assignment for a specific agent."""
        for assignment in self.assignments:
            if assignment.agent_name == agent_name:
                return assignment
        return None

    def get_findings(self, agent_name: str) -> Optional[AgentFindings]:
        """Get findings for a specific agent."""
        for findings in self.agent_findings:
            if findings.agent_name == agent_name:
                return findings
        return None


# --- Lesson Models ---


@dataclass
class LessonCandidate:
    """A potential lesson extracted from multi-agent debate."""

    pattern_name: str
    context: str
    problem: str
    solution: str
    detection: str
    source_session: str
    source_conflict: Optional[str] = None  # conflict_id if from debate
    confidence: float = 0.5
    tags: list[str] = field(default_factory=list)
