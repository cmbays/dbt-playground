"""Merge Resolution Engine for Multi-Agent Debug Sessions.

Synthesizes N agent findings into a consensus resolution.
Applies evidence weighting, detects conflicts, resolves them
where possible, and produces a merge_resolution.md document.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from scripts.lib.multi_agent_debug.conflict_detector import (
    detect_conflicts,
    resolve_conflict_by_evidence,
    get_conflict_summary,
)
from scripts.lib.multi_agent_debug.manifest import _findings_filename
from scripts.lib.multi_agent_debug.models import (
    AgentFindings,
    Conflict,
    ConflictResolution,
    Finding,
    LessonCandidate,
    MergeResolution,
)
from scripts.lib.multi_agent_debug.utils import (
    generate_pattern_name,
    extract_tags,
)


def merge_findings(
    session_id: str,
    lead_agent: str,
    all_findings: list[AgentFindings],
    auto_resolve: bool = True,
) -> MergeResolution:
    """Merge findings from all agents into a consensus resolution.

    Process:
    1. Collect all findings from all agents
    2. Detect conflicts between findings
    3. Attempt automatic resolution via evidence weighting
    4. Build consensus findings from non-conflicting + resolved
    5. Extract deployment order from proposed fixes
    6. Identify potential lessons

    Args:
        session_id: Session ID
        lead_agent: Name of the lead agent
        all_findings: Findings from all participating agents
        auto_resolve: Whether to auto-resolve conflicts by evidence

    Returns:
        MergeResolution with consensus findings and conflicts
    """
    participating = [f.agent_name for f in all_findings]
    start_time = datetime.now(UTC)

    # Step 1: Detect conflicts
    conflicts = detect_conflicts(all_findings)

    # Step 2: Attempt resolution
    resolved_conflicts: list[Conflict] = []
    unresolved_conflicts: list[Conflict] = []

    if auto_resolve:
        for conflict in conflicts:
            resolved = resolve_conflict_by_evidence(conflict)
            if resolved.is_resolved:
                # Human-escalated conflicts go to unresolved even if marked resolved
                if resolved.resolution == ConflictResolution.HUMAN_ESCALATED:
                    unresolved_conflicts.append(resolved)
                else:
                    resolved_conflicts.append(resolved)
            else:
                unresolved_conflicts.append(resolved)
    else:
        unresolved_conflicts = conflicts

    # Step 3: Build consensus findings
    # Exclude findings that are part of unresolved conflicts
    unresolved_descriptions: set[str] = set()
    for conflict in unresolved_conflicts:
        unresolved_descriptions.add(conflict.finding_a.description)
        unresolved_descriptions.add(conflict.finding_b.description)

    # Filter out findings from unresolved conflicts
    filtered_findings = []
    for agent_findings in all_findings:
        filtered = AgentFindings(
            agent_name=agent_findings.agent_name,
            session_id=agent_findings.session_id,
            zone=agent_findings.zone,
            findings=[
                f for f in agent_findings.findings
                if f.description not in unresolved_descriptions
            ],
            cross_scope_observations=agent_findings.cross_scope_observations,
            blockers=agent_findings.blockers,
            investigation_time_minutes=agent_findings.investigation_time_minutes,
        )
        filtered_findings.append(filtered)

    consensus = _build_consensus(filtered_findings, resolved_conflicts)

    # Step 4: Extract deployment order
    deployment_order = _extract_deployment_order(consensus)

    # Step 5: Build agreed fixes
    agreed_fixes = _extract_agreed_fixes(consensus)

    # Step 6: Extract lessons
    lessons = _extract_lessons(
        session_id, consensus, resolved_conflicts,
    )

    # Calculate resolution time
    end_time = datetime.now(UTC)
    resolution_minutes = int(
        (end_time - start_time).total_seconds() / 60
    )

    return MergeResolution(
        session_id=session_id,
        lead_agent=lead_agent,
        participating_agents=participating,
        consensus_findings=consensus,
        conflicts=resolved_conflicts,
        agreed_fixes=agreed_fixes,
        deployment_order=deployment_order,
        unresolved_conflicts=unresolved_conflicts,
        lessons_extracted=[l.pattern_name for l in lessons],
        resolution_time_minutes=resolution_minutes,
    )


def generate_resolution_document(
    resolution: MergeResolution,
    all_findings: list[AgentFindings],
) -> str:
    """Generate merge_resolution.md document content.

    Args:
        resolution: The merge resolution
        all_findings: Original findings from all agents

    Returns:
        Markdown content for merge_resolution.md
    """
    lines: list[str] = []

    # Header
    lines.append('# Merge Resolution')
    lines.append('')
    lines.append(f'**Session**: {resolution.session_id}')
    lines.append(
        f'**Merge Date**: '
        f'{datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")}'
    )
    lines.append(f'**Lead Agent**: {resolution.lead_agent}')
    lines.append('')
    lines.append('---')
    lines.append('')

    # Participating Agents
    lines.append('## Participating Agents')
    lines.append('')
    lines.append(
        '| Agent | Findings File | Status | Key Finding |'
    )
    lines.append(
        '|-------|---------------|--------|-------------|'
    )

    for agent_findings in all_findings:
        primary = agent_findings.primary_finding
        key_finding = primary.description if primary else 'No findings'
        status = 'COMPLETE'
        filename = _findings_filename(agent_findings.agent_name)
        lines.append(
            f'| {agent_findings.agent_name} '
            f'| {filename} '
            f'| {status} '
            f'| {key_finding} |'
        )

    lines.append('')
    lines.append('---')
    lines.append('')

    # Consensus Finding
    lines.append('## Consensus Finding')
    lines.append('')

    if resolution.consensus_findings:
        root_causes = [
            f for f in resolution.consensus_findings
            if f.classification == 'root_cause'
        ]
        symptoms = [
            f for f in resolution.consensus_findings
            if f.classification == 'symptom'
        ]
        contributing = [
            f for f in resolution.consensus_findings
            if f.classification == 'contributing'
        ]

        if root_causes:
            lines.append('### Root Cause')
            lines.append('')
            for finding in root_causes:
                lines.append(
                    f'**{finding.description}** '
                    f'(confidence: {finding.confidence:.1f})'
                )
                if finding.evidence:
                    lines.append('')
                    lines.append('Evidence:')
                    for ev in finding.evidence:
                        lines.append(
                            f'- [{ev.evidence_type.value}] '
                            f'{ev.description}'
                        )
                        if ev.source:
                            lines.append(f'  Source: `{ev.source}`')
                lines.append('')

        # Classification table
        if len(resolution.consensus_findings) > 1:
            lines.append('### Root vs Symptom Classification')
            lines.append('')
            lines.append(
                '| Finding | Classification | Confidence |'
            )
            lines.append(
                '|---------|----------------|------------|'
            )
            for finding in resolution.consensus_findings:
                lines.append(
                    f'| {finding.description} '
                    f'| **{finding.classification.upper()}** '
                    f'| {finding.confidence:.1f} |'
                )
            lines.append('')
    else:
        lines.append('No consensus findings established.')
        lines.append('')

    lines.append('---')
    lines.append('')

    # Agreed Fixes
    if resolution.agreed_fixes:
        lines.append('## Agreed Fix')
        lines.append('')
        lines.append('| File | Change | Priority |')
        lines.append('|------|--------|----------|')
        for fix in resolution.agreed_fixes:
            lines.append(
                f'| {fix.get("file", "N/A")} '
                f'| {fix.get("change", "N/A")} '
                f'| {fix.get("priority", "N/A")} |'
            )
        lines.append('')

    # Deployment Order
    if resolution.deployment_order:
        lines.append('### Deployment Order')
        lines.append('')
        for i, step in enumerate(resolution.deployment_order, 1):
            lines.append(f'{i}. **{step}**')
        lines.append('')

    lines.append('---')
    lines.append('')

    # Conflicts
    if resolution.conflicts or resolution.unresolved_conflicts:
        lines.append('## Conflicts')
        lines.append('')

        if resolution.conflicts:
            lines.append('### Resolved Conflicts')
            lines.append('')
            lines.append(
                '| ID | Type | Agent A | Agent B | Resolution |'
            )
            lines.append(
                '|----|------|---------|---------|------------|'
            )
            for conflict in resolution.conflicts:
                res_str = (
                    conflict.resolution.value if conflict.resolution
                    else 'pending'
                )
                lines.append(
                    f'| {conflict.conflict_id} '
                    f'| {conflict.conflict_type.value} '
                    f'| {conflict.agent_a} '
                    f'| {conflict.agent_b} '
                    f'| {res_str} |'
                )
            lines.append('')

        if resolution.unresolved_conflicts:
            lines.append('### Unresolved Conflicts (Require Escalation)')
            lines.append('')
            for conflict in resolution.unresolved_conflicts:
                lines.append(
                    f'- **{conflict.conflict_id}**: '
                    f'{conflict.description}'
                )
                if conflict.resolution_rationale:
                    lines.append(
                        f'  Rationale: {conflict.resolution_rationale}'
                    )
            lines.append('')

    # Lessons
    if resolution.lessons_extracted:
        lines.append('---')
        lines.append('')
        lines.append('## Lessons Extracted')
        lines.append('')
        for lesson in resolution.lessons_extracted:
            lines.append(f'- {lesson}')
        lines.append('')

    # Session Outcome
    lines.append('---')
    lines.append('')
    lines.append('## Session Outcome')
    lines.append('')
    lines.append(
        f'**Status**: '
        f'{"COMPLETE" if not resolution.has_unresolved_conflicts else "ESCALATION REQUIRED"}'
    )
    lines.append(
        f'**Total Conflicts**: {resolution.total_conflicts}'
    )
    lines.append(
        f'**Resolved**: {len(resolution.conflicts)}'
    )
    lines.append(
        f'**Unresolved**: {len(resolution.unresolved_conflicts)}'
    )
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append(
        f'*Merge resolution generated at '
        f'{datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")}*'
    )
    lines.append('')

    return '\n'.join(lines)


def write_resolution_document(
    resolution: MergeResolution,
    all_findings: list[AgentFindings],
    session_folder: str,
) -> Path:
    """Generate and write merge_resolution.md to disk.

    Args:
        resolution: The merge resolution
        all_findings: Original findings from all agents
        session_folder: Path to session folder

    Returns:
        Path to the written file
    """
    content = generate_resolution_document(resolution, all_findings)

    folder = Path(session_folder)
    folder.mkdir(parents=True, exist_ok=True)

    doc_path = folder / 'merge_resolution.md'
    doc_path.write_text(content, encoding='utf-8')

    return doc_path


# --- Internal Functions ---


def _build_consensus(
    all_findings: list[AgentFindings],
    resolved_conflicts: list[Conflict],
) -> list[Finding]:
    """Build consensus findings from all agent findings.

    Strategy:
    1. Collect all findings that are NOT part of any conflict
    2. For resolved conflicts, use the winning finding
    3. Deduplicate by description similarity
    4. Sort by classification (root_cause first) then confidence

    Args:
        all_findings: All agent findings
        resolved_conflicts: Conflicts that were resolved

    Returns:
        Ordered list of consensus findings
    """
    # Collect conflicted finding descriptions
    conflicted_descriptions: set[str] = set()
    for conflict in resolved_conflicts:
        conflicted_descriptions.add(conflict.finding_a.description)
        conflicted_descriptions.add(conflict.finding_b.description)

    # Collect non-conflicted findings
    consensus: list[Finding] = []
    seen_descriptions: set[str] = set()

    # First: add resolved conflict winners
    for conflict in resolved_conflicts:
        if conflict.resolved_finding:
            desc = conflict.resolved_finding.description
            if desc not in seen_descriptions:
                consensus.append(conflict.resolved_finding)
                seen_descriptions.add(desc)

    # Second: add non-conflicted findings
    for agent_findings in all_findings:
        for finding in agent_findings.findings:
            if (
                finding.description not in conflicted_descriptions
                and finding.description not in seen_descriptions
            ):
                consensus.append(finding)
                seen_descriptions.add(finding.description)

    # Sort: root_cause first, then by confidence descending
    classification_order = {
        'root_cause': 0,
        'contributing': 1,
        'symptom': 2,
    }
    consensus.sort(
        key=lambda f: (
            classification_order.get(f.classification, 3),
            -f.confidence,
        ),
    )

    return consensus


def _extract_deployment_order(
    consensus: list[Finding],
) -> list[str]:
    """Extract deployment order from consensus findings.

    Root cause fixes deploy first, then contributing, then symptoms.

    Args:
        consensus: Consensus findings

    Returns:
        Ordered list of deployment steps
    """
    order: list[str] = []
    seen: set[str] = set()

    for finding in consensus:
        if finding.proposed_fix and finding.proposed_fix not in seen:
            order.append(finding.proposed_fix)
            seen.add(finding.proposed_fix)

    return order


def _extract_agreed_fixes(
    consensus: list[Finding],
) -> list[dict]:
    """Extract agreed fixes from consensus findings.

    Args:
        consensus: Consensus findings

    Returns:
        List of fix dicts with file, change, priority
    """
    fixes: list[dict] = []

    priority_map = {
        'root_cause': 'P0 (critical)',
        'contributing': 'P1 (recommended)',
        'symptom': 'P2 (optional)',
    }

    for finding in consensus:
        if finding.proposed_fix:
            fix = {
                'change': finding.proposed_fix,
                'priority': priority_map.get(
                    finding.classification, 'P2 (optional)',
                ),
            }
            if finding.files_involved:
                fix['file'] = ', '.join(finding.files_involved)
            else:
                fix['file'] = 'TBD'
            fixes.append(fix)

    return fixes


def _extract_lessons(
    session_id: str,
    consensus_findings: list[Finding],
    resolved_conflicts: list[Conflict],
) -> list[LessonCandidate]:
    """Extract potential lessons from the merge process.

    Lessons come from:
    - Resolved conflicts (debate produced insight)
    - Consensus findings (high-confidence root causes that survived merge)

    Args:
        session_id: Session ID
        consensus_findings: Consensus findings from merge resolution
        resolved_conflicts: Resolved conflicts

    Returns:
        List of lesson candidates
    """
    lessons: list[LessonCandidate] = []

    # From resolved conflicts: debate-driven insights
    for conflict in resolved_conflicts:
        if (
            conflict.resolution == ConflictResolution.EVIDENCE_WEIGHTED
            and conflict.resolved_finding
        ):
            finding = conflict.resolved_finding
            lessons.append(LessonCandidate(
                pattern_name=generate_pattern_name(finding),
                context=f'Multi-agent debug session: {session_id}',
                problem=finding.description,
                solution=finding.proposed_fix or 'Investigation finding',
                detection=(
                    f'Identified through {conflict.conflict_type.value} '
                    f'resolution'
                ),
                source_session=session_id,
                source_conflict=conflict.conflict_id,
                confidence=finding.confidence,
                tags=extract_tags(finding),
            ))

    # From high-confidence consensus root causes
    # Note: Using 0.8 threshold (stricter than lessons.py's 0.7)
    # because merge resolution extracts lessons only from consensus findings
    # that have survived conflict resolution and agent agreement.
    for finding in consensus_findings:
        if (
            finding.classification == 'root_cause'
            and finding.confidence >= 0.8
            and finding.proposed_fix
        ):
            pattern = generate_pattern_name(finding)
            # Avoid duplicates from conflicts
            if not any(l.pattern_name == pattern for l in lessons):
                lessons.append(LessonCandidate(
                    pattern_name=pattern,
                    context=f'Consensus finding from multi-agent session',
                    problem=finding.description,
                    solution=finding.proposed_fix,
                    detection='High-confidence consensus root cause',
                    source_session=session_id,
                    confidence=finding.confidence,
                    tags=extract_tags(finding),
                ))

    return lessons
