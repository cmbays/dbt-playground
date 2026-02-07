"""Session Manifest Generator for Multi-Agent Debug Sessions.

Generates session_manifest.md documents that track active agents,
work zones, status, and session progress. Uses the P0 template
format from temp/DEBUG_REPORTS/.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from scripts.lib.multi_agent_debug.models import (
    AgentStatus,
    MultiAgentSession,
    SessionStatus,
)


def generate_manifest(
    session: MultiAgentSession,
    session_folder: str,
) -> str:
    """Generate session manifest markdown content.

    Creates a structured markdown document tracking the session's
    agents, work zones, status, and progress.

    Args:
        session: The multi-agent session
        session_folder: Path to the session's artifact folder

    Returns:
        Markdown content for session_manifest.md
    """
    lines: list[str] = []

    # Header
    lines.append('# Debug Session Manifest')
    lines.append('')
    lines.append(f'**Session ID**: {session.session_id}')
    lines.append(f'**Status**: {session.status.value.upper()}')

    if session.created_at:
        created_str = session.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
        lines.append(f'**Created**: {created_str}')

    if session.status == SessionStatus.RESOLVED and session.updated_at:
        completed_str = session.updated_at.strftime('%Y-%m-%d %H:%M:%S UTC')
        lines.append(f'**Completed**: {completed_str}')

    lines.append(f'**Debug Session**: {session.debug_session_id}')
    lines.append('')
    lines.append('---')
    lines.append('')

    # Bug Reference
    lines.append('## Bug Reference')
    lines.append('')
    lines.append(f'**Description**: {session.bug_description}')
    lines.append(f'**Lead Agent**: {session.lead_agent}')

    if session.complexity:
        lines.append(
            f'**Complexity**: {session.complexity.overall_score:.2f} '
            f'({session.complexity.suggested_agents} agent(s) suggested)'
        )
        if session.complexity.factors:
            factor_names = ', '.join(
                f.name for f in session.complexity.factors
            )
            lines.append(f'**Factors**: {factor_names}')

    lines.append('')
    lines.append('---')
    lines.append('')

    # Participating Agents table
    lines.append('## Participating Agents')
    lines.append('')
    lines.append(
        '| Agent | Zone | Status | Findings File | Started | Completed |'
    )
    lines.append(
        '|-------|------|--------|---------------|---------|-----------|'
    )

    for assignment in session.assignments:
        status_icon = _status_icon(assignment.status)
        findings_file = _findings_filename(assignment.agent_name)

        started = ''
        if assignment.started_at:
            started = assignment.started_at.strftime('%H:%M:%S')

        completed = ''
        if assignment.completed_at:
            completed = assignment.completed_at.strftime('%H:%M:%S')

        lines.append(
            f'| {assignment.agent_name} '
            f'| {assignment.zone.name} '
            f'| {status_icon} {assignment.status.value} '
            f'| {findings_file} '
            f'| {started} '
            f'| {completed} |'
        )

    lines.append('')
    lines.append('---')
    lines.append('')

    # Work Zones
    lines.append('## Work Zones')
    lines.append('')

    for assignment in session.assignments:
        zone = assignment.zone
        lines.append(f'### {zone.name}')
        lines.append('')
        lines.append(f'**Description**: {zone.description}')
        lines.append(f'**Assigned To**: {assignment.agent_name}')

        if zone.files:
            files_str = ', '.join(f'`{f}`' for f in zone.files)
            lines.append(f'**Files**: {files_str}')

        if zone.systems:
            systems_str = ', '.join(zone.systems)
            lines.append(f'**Systems**: {systems_str}')

        if zone.required_capabilities:
            caps_str = ', '.join(zone.required_capabilities)
            lines.append(f'**Required Capabilities**: {caps_str}')

        lines.append('')

    lines.append('---')
    lines.append('')

    # Session Progress
    lines.append('## Session Progress')
    lines.append('')
    lines.append(
        f'- **Total Agents**: {session.agent_count}'
    )
    lines.append(
        f'- **Agents Complete**: {session.agents_complete}'
    )
    lines.append(
        f'- **All Complete**: '
        f'{"Yes" if session.all_agents_complete else "No"}'
    )

    # Findings summary if available
    if session.agent_findings:
        lines.append('')
        lines.append('### Findings Summary')
        lines.append('')

        for agent_findings in session.agent_findings:
            primary = agent_findings.primary_finding
            lines.append(
                f'**{agent_findings.agent_name}**: '
                f'{len(agent_findings.findings)} finding(s)'
            )
            if primary:
                lines.append(
                    f'  - Primary: {primary.description} '
                    f'(confidence: {primary.confidence:.1f})'
                )
            if agent_findings.blockers:
                blockers_str = ', '.join(agent_findings.blockers)
                lines.append(f'  - Blockers: {blockers_str}')
            lines.append('')

    # Resolution summary if available
    if session.resolution:
        lines.append('')
        lines.append('---')
        lines.append('')
        lines.append('## Resolution Summary')
        lines.append('')
        lines.append(
            f'- **Consensus Findings**: '
            f'{len(session.resolution.consensus_findings)}'
        )
        lines.append(
            f'- **Total Conflicts**: '
            f'{session.resolution.total_conflicts}'
        )
        lines.append(
            f'- **Unresolved Conflicts**: '
            f'{len(session.resolution.unresolved_conflicts)}'
        )
        if session.resolution.deployment_order:
            order_str = ' -> '.join(session.resolution.deployment_order)
            lines.append(f'- **Deployment Order**: {order_str}')

    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append(
        f'*Generated at '
        f'{datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")}*'
    )
    lines.append('')

    return '\n'.join(lines)


def write_manifest(
    session: MultiAgentSession,
    session_folder: str,
) -> Path:
    """Generate and write session manifest to disk.

    Args:
        session: The multi-agent session
        session_folder: Path to the session's artifact folder

    Returns:
        Path to the written manifest file
    """
    content = generate_manifest(session, session_folder)

    folder = Path(session_folder)
    folder.mkdir(parents=True, exist_ok=True)

    manifest_path = folder / 'session_manifest.md'
    manifest_path.write_text(content, encoding='utf-8')

    return manifest_path


def update_manifest(
    session: MultiAgentSession,
    session_folder: str,
) -> Path:
    """Re-generate and overwrite the session manifest.

    Called when session state changes (agent completes, findings
    submitted, session resolved, etc.).

    Args:
        session: The updated session
        session_folder: Path to the session's artifact folder

    Returns:
        Path to the updated manifest file
    """
    return write_manifest(session, session_folder)


def _status_icon(status: AgentStatus) -> str:
    """Get a text icon for agent status.

    Args:
        status: Agent status

    Returns:
        Text icon string
    """
    icons = {
        AgentStatus.REGISTERED: '[.]',
        AgentStatus.ASSIGNED: '[>]',
        AgentStatus.INVESTIGATING: '[~]',
        AgentStatus.COMPLETE: '[x]',
        AgentStatus.BLOCKED: '[!]',
    }
    return icons.get(status, '[ ]')


def _findings_filename(agent_name: str) -> str:
    """Generate findings filename for an agent.

    Args:
        agent_name: Agent name

    Returns:
        Filename like agent_backend_findings.md
    """
    safe_name = agent_name.replace(' ', '_').replace('-', '_').lower()
    return f'agent_{safe_name}_findings.md'
