"""Session Orchestrator for Multi-Agent Debug Sessions.

Manages the lifecycle of multi-agent debug sessions: creation,
agent spawning, investigation tracking, and session completion.
Wraps the coordination protocol with session state management.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

from datetime import UTC, datetime
from typing import Optional

from scripts.lib.multi_agent_debug.exceptions import (
    AgentNotFoundError,
    InvalidSessionStateError,
    SessionAlreadyExistsError,
    SessionNotFoundError,
)
from scripts.lib.multi_agent_debug.models import (
    AgentFindings,
    AgentProfile,
    AgentStatus,
    MultiAgentSession,
    SessionStatus,
    WorkZone,
)
from scripts.lib.multi_agent_debug.protocol import (
    assess_complexity,
    create_session_config,
    SessionConfig,
)
from scripts.lib.multi_agent_debug.registry import AgentRegistry


class SessionOrchestrator:
    """Orchestrates multi-agent debug session lifecycle.

    Manages creation, agent assignment, investigation tracking,
    and completion of multi-agent debug sessions. Acts as the
    hub in the hub-and-spoke coordination model.
    """

    def __init__(self, registry: AgentRegistry):
        """Initialize orchestrator with an agent registry.

        Args:
            registry: Registry of available agents
        """
        self._registry = registry
        self._sessions: dict[str, MultiAgentSession] = {}

    @property
    def session_count(self) -> int:
        """Total number of sessions (all states)."""
        return len(self._sessions)

    @property
    def active_sessions(self) -> list[MultiAgentSession]:
        """Sessions currently in progress."""
        return [
            s for s in self._sessions.values()
            if s.status in (SessionStatus.SETUP, SessionStatus.INVESTIGATING)
        ]

    def create_session(
        self,
        session_id: str,
        debug_session_id: str,
        bug_description: str,
        lead_agent: str,
        zones: list[WorkZone],
        session_folder: str,
        context: Optional[str] = None,
    ) -> MultiAgentSession:
        """Create a new multi-agent debug session.

        Assesses complexity, assigns agents to zones, and initializes
        the session in SETUP state.

        Args:
            session_id: Unique session identifier
            debug_session_id: Link to parent DebugSessionTracker session
            bug_description: Description of the bug being investigated
            lead_agent: Name of the lead coordinator agent
            zones: Work zones to partition among agents
            session_folder: Path for session artifacts
            context: Additional context for complexity assessment

        Returns:
            The created session

        Raises:
            SessionAlreadyExistsError: If session_id already exists
        """
        if session_id in self._sessions:
            raise SessionAlreadyExistsError(session_id)

        # Get available agents
        available = self._registry.get_available_agents()
        if not available:
            available = self._registry.get_all_agents()

        # Create session config (assesses complexity, partitions work)
        config = create_session_config(
            bug_description=bug_description,
            lead_agent=lead_agent,
            agents=available,
            zones=zones,
            session_folder=session_folder,
            session_id=session_id,
            debug_session_id=debug_session_id,
            context=context,
        )

        now = datetime.now(UTC)

        # Create session
        session = MultiAgentSession(
            session_id=session_id,
            debug_session_id=debug_session_id,
            bug_description=bug_description,
            lead_agent=lead_agent,
            status=SessionStatus.SETUP,
            complexity=config.complexity,
            assignments=list(config.assignments),
            created_at=now,
            updated_at=now,
        )

        # Register assignments in the registry
        for assignment in session.assignments:
            self._registry.assign_agent(
                agent_name=assignment.agent_name,
                session_id=session_id,
                zone=assignment.zone,
            )

        self._sessions[session_id] = session
        return session

    def start_investigation(self, session_id: str) -> MultiAgentSession:
        """Transition session from SETUP to INVESTIGATING.

        All assigned agents begin their investigation work.

        Args:
            session_id: Session to start

        Returns:
            The updated session

        Raises:
            SessionNotFoundError: If session not found
            InvalidSessionStateError: If not in SETUP state
        """
        session = self._get_session(session_id)
        self._require_state(session, SessionStatus.SETUP, 'start investigation')

        session.status = SessionStatus.INVESTIGATING
        session.updated_at = datetime.now(UTC)

        # Update all assignments to INVESTIGATING
        for assignment in session.assignments:
            assignment.status = AgentStatus.INVESTIGATING
            assignment.started_at = datetime.now(UTC)
            self._registry.update_agent_status(
                agent_name=assignment.agent_name,
                session_id=session_id,
                status=AgentStatus.INVESTIGATING,
            )

        return session

    def submit_findings(
        self,
        session_id: str,
        findings: AgentFindings,
    ) -> MultiAgentSession:
        """Submit an agent's findings for a session.

        Marks the agent as COMPLETE and stores their findings.
        If all agents are complete, transitions session to MERGING.

        Args:
            session_id: Session ID
            findings: The agent's investigation findings

        Returns:
            The updated session

        Raises:
            SessionNotFoundError: If session not found
            InvalidSessionStateError: If not in INVESTIGATING state
        """
        # Validate session and state
        session = self._get_session(session_id)
        self._require_state(
            session, SessionStatus.INVESTIGATING, 'submit findings',
        )

        # Validate session ID match if present in findings
        if hasattr(findings, 'session_id') and findings.session_id != session_id:
            raise ValueError(
                f"Findings session_id '{findings.session_id}' does not match "
                f"session '{session_id}'"
            )

        # Validate agent assignment before mutating state
        assignment = session.get_assignment(findings.agent_name)
        if not assignment:
            raise AgentNotFoundError(
                f"Agent '{findings.agent_name}' not assigned to session '{session_id}'"
            )

        # All validations passed - now mutate state
        session.agent_findings.append(findings)
        assignment.status = AgentStatus.COMPLETE
        assignment.completed_at = datetime.now(UTC)
        self._registry.update_agent_status(
            agent_name=findings.agent_name,
            session_id=session_id,
            status=AgentStatus.COMPLETE,
            findings_path=assignment.findings_path,
        )

        session.updated_at = datetime.now(UTC)

        # Auto-transition to MERGING when all agents complete
        if session.all_agents_complete:
            session.status = SessionStatus.MERGING

        return session

    def mark_agent_blocked(
        self,
        session_id: str,
        agent_name: str,
        blockers: list[str],
    ) -> MultiAgentSession:
        """Mark an agent as blocked during investigation.

        Args:
            session_id: Session ID
            agent_name: Name of the blocked agent
            blockers: List of blocker descriptions

        Returns:
            The updated session

        Raises:
            SessionNotFoundError: If session not found
            InvalidSessionStateError: If not in INVESTIGATING state
        """
        session = self._get_session(session_id)
        self._require_state(
            session, SessionStatus.INVESTIGATING, 'mark agent blocked',
        )

        assignment = session.get_assignment(agent_name)
        if not assignment:
            raise AgentNotFoundError(
                f"Agent '{agent_name}' not assigned to session '{session_id}'"
            )

        assignment.status = AgentStatus.BLOCKED
        assignment.blockers = blockers
        self._registry.update_agent_status(
            agent_name=agent_name,
            session_id=session_id,
            status=AgentStatus.BLOCKED,
        )

        session.updated_at = datetime.now(UTC)
        return session

    def complete_session(
        self,
        session_id: str,
        resolution: 'MergeResolution',
    ) -> MultiAgentSession:
        """Complete a session with a merge resolution.

        Transitions from MERGING to RESOLVED and releases all agents.

        Args:
            session_id: Session ID
            resolution: The merge resolution

        Returns:
            The completed session

        Raises:
            SessionNotFoundError: If session not found
            InvalidSessionStateError: If not in MERGING state
        """
        session = self._get_session(session_id)
        self._require_state(
            session, SessionStatus.MERGING, 'complete session',
        )

        session.resolution = resolution
        session.status = SessionStatus.RESOLVED
        session.updated_at = datetime.now(UTC)

        # Release all agents
        for assignment in session.assignments:
            self._registry.release_agent(
                agent_name=assignment.agent_name,
                session_id=session_id,
            )

        return session

    def escalate_session(
        self,
        session_id: str,
        reason: str,
    ) -> MultiAgentSession:
        """Escalate a session that cannot be resolved by agents.

        Transitions to ESCALATED and releases all agents.

        Args:
            session_id: Session ID
            reason: Reason for escalation

        Returns:
            The escalated session

        Raises:
            SessionNotFoundError: If session not found
            InvalidSessionStateError: If in RESOLVED or ESCALATED state
        """
        session = self._get_session(session_id)

        if session.status in (SessionStatus.RESOLVED, SessionStatus.ESCALATED):
            raise InvalidSessionStateError(
                session_id, session.status.value, 'escalate',
            )

        session.status = SessionStatus.ESCALATED
        session.escalation_reason = reason
        session.updated_at = datetime.now(UTC)

        # Release all agents
        for assignment in session.assignments:
            self._registry.release_agent(
                agent_name=assignment.agent_name,
                session_id=session_id,
            )

        return session

    def get_session(self, session_id: str) -> MultiAgentSession:
        """Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            The session

        Raises:
            SessionNotFoundError: If not found
        """
        return self._get_session(session_id)

    def get_session_status(self, session_id: str) -> dict:
        """Get a summary of session status.

        Args:
            session_id: Session ID

        Returns:
            Dict with status summary

        Raises:
            SessionNotFoundError: If not found
        """
        session = self._get_session(session_id)

        agents_info = []
        for assignment in session.assignments:
            info = {
                'agent': assignment.agent_name,
                'zone': assignment.zone.name,
                'status': assignment.status.value,
            }
            findings = session.get_findings(assignment.agent_name)
            if findings:
                info['finding_count'] = len(findings.findings)
                primary = findings.primary_finding
                if primary:
                    info['primary_finding'] = primary.description
            agents_info.append(info)

        return {
            'session_id': session.session_id,
            'status': session.status.value,
            'bug_description': session.bug_description,
            'lead_agent': session.lead_agent,
            'agent_count': session.agent_count,
            'agents_complete': session.agents_complete,
            'all_complete': session.all_agents_complete,
            'agents': agents_info,
            'has_resolution': session.resolution is not None,
            'created_at': session.created_at,
            'updated_at': session.updated_at,
        }

    def get_all_sessions(self) -> list[MultiAgentSession]:
        """Get all sessions.

        Returns:
            List of all sessions
        """
        return list(self._sessions.values())

    def _get_session(self, session_id: str) -> MultiAgentSession:
        """Internal: get session or raise."""
        if session_id not in self._sessions:
            raise SessionNotFoundError(session_id)
        return self._sessions[session_id]

    def _require_state(
        self,
        session: MultiAgentSession,
        required: SessionStatus,
        action: str,
    ) -> None:
        """Internal: require session to be in a specific state."""
        if session.status != required:
            raise InvalidSessionStateError(
                session.session_id,
                session.status.value,
                action,
            )
