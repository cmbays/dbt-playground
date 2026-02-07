"""Custom exceptions for Multi-Agent Debug Coordination.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""


class MultiAgentDebugError(Exception):
    """Base exception for multi-agent debug operations."""


class SessionNotFoundError(MultiAgentDebugError):
    """Raised when a multi-agent session cannot be found."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Multi-agent session not found: {session_id}")


class SessionAlreadyExistsError(MultiAgentDebugError):
    """Raised when trying to create a session that already exists."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(f"Multi-agent session already exists: {session_id}")


class AgentNotFoundError(MultiAgentDebugError):
    """Raised when an agent is not found in the registry."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(f"Agent not found: {agent_name}")


class AgentAlreadyAssignedError(MultiAgentDebugError):
    """Raised when an agent is already assigned to a session."""

    def __init__(self, agent_name: str, session_id: str):
        self.agent_name = agent_name
        self.session_id = session_id
        super().__init__(f"Agent '{agent_name}' already assigned to session {session_id}")


class NoAgentsAvailableError(MultiAgentDebugError):
    """Raised when no agents are available for the required capabilities."""

    def __init__(self, required_capabilities: list[str]):
        self.required_capabilities = required_capabilities
        super().__init__(
            f"No agents available with capabilities: {', '.join(required_capabilities)}"
        )


class MergeConflictError(MultiAgentDebugError):
    """Raised when merge resolution encounters an unresolvable conflict."""

    def __init__(self, conflict_description: str):
        self.conflict_description = conflict_description
        super().__init__(f"Unresolvable merge conflict: {conflict_description}")


class InvalidSessionStateError(MultiAgentDebugError):
    """Raised when an operation is invalid for the current session state."""

    def __init__(self, session_id: str, current_state: str, attempted_action: str):
        self.session_id = session_id
        self.current_state = current_state
        self.attempted_action = attempted_action
        super().__init__(
            f"Cannot {attempted_action} session {session_id} "
            f"in state '{current_state}'"
        )
