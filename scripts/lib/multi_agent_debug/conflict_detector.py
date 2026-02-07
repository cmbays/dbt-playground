"""Conflict Detector for Multi-Agent Debug Sessions.

Identifies contradictions and disagreements between agent findings.
Uses evidence-weighted comparison to determine which findings have
stronger support. Escalates unresolvable conflicts.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

from itertools import combinations
from typing import Optional

from scripts.lib.multi_agent_debug.models import (
    AgentFindings,
    Conflict,
    ConflictResolution,
    ConflictType,
    Evidence,
    EVIDENCE_WEIGHTS,
    Finding,
)


def detect_conflicts(
    all_findings: list[AgentFindings],
) -> list[Conflict]:
    """Detect conflicts between agent findings.

    Compares findings from all agent pairs looking for:
    - Root cause disagreements (different root causes identified)
    - Evidence contradictions (conflicting evidence)
    - Scope overlaps (overlapping file investigations)
    - Classification mismatches (same issue classified differently)

    Args:
        all_findings: Findings from all participating agents

    Returns:
        List of detected conflicts
    """
    conflicts: list[Conflict] = []
    conflict_counter = 0

    # Compare each pair of agent findings
    for findings_a, findings_b in combinations(all_findings, 2):
        # Check root cause disagreements
        root_cause_conflicts = _detect_root_cause_disagreements(
            findings_a, findings_b, conflict_counter,
        )
        conflict_counter += len(root_cause_conflicts)
        conflicts.extend(root_cause_conflicts)

        # Check evidence contradictions
        evidence_conflicts = _detect_evidence_contradictions(
            findings_a, findings_b, conflict_counter,
        )
        conflict_counter += len(evidence_conflicts)
        conflicts.extend(evidence_conflicts)

        # Check scope overlaps
        scope_conflicts = _detect_scope_overlaps(
            findings_a, findings_b, conflict_counter,
        )
        conflict_counter += len(scope_conflicts)
        conflicts.extend(scope_conflicts)

        # Check classification mismatches
        classification_conflicts = _detect_classification_mismatches(
            findings_a, findings_b, conflict_counter,
        )
        conflict_counter += len(classification_conflicts)
        conflicts.extend(classification_conflicts)

    return conflicts


def resolve_conflict_by_evidence(conflict: Conflict) -> Conflict:
    """Attempt to resolve a conflict using evidence weighting.

    Compares the total evidence weight of each side. The side with
    stronger evidence (higher total weight) wins.

    Args:
        conflict: The conflict to resolve

    Returns:
        The conflict with resolution applied (or marked for escalation)
    """
    weight_a = _calculate_finding_weight(conflict.finding_a)
    weight_b = _calculate_finding_weight(conflict.finding_b)

    # Significant difference threshold: 0.2
    weight_diff = abs(weight_a - weight_b)

    if weight_diff < 0.2:
        # Too close to call - escalate to human
        conflict.resolution = ConflictResolution.HUMAN_ESCALATED
        conflict.resolution_rationale = (
            f'Evidence weights too close '
            f'({weight_a:.2f} vs {weight_b:.2f}, diff {weight_diff:.2f}). '
            f'Requires human judgment.'
        )
        return conflict

    if weight_a > weight_b:
        winner = conflict.finding_a
        winner_agent = conflict.agent_a
        loser_agent = conflict.agent_b
    else:
        winner = conflict.finding_b
        winner_agent = conflict.agent_b
        loser_agent = conflict.agent_a

    conflict.resolution = ConflictResolution.EVIDENCE_WEIGHTED
    conflict.resolved_finding = winner
    conflict.resolution_rationale = (
        f'Agent {winner_agent} finding has stronger evidence '
        f'({max(weight_a, weight_b):.2f} vs {min(weight_a, weight_b):.2f}). '
        f'Agent {loser_agent} finding deprioritized.'
    )

    return conflict


def calculate_finding_weight(finding: Finding) -> float:
    """Calculate the total evidence weight for a finding.

    Combines evidence type weights with finding confidence.

    Args:
        finding: The finding to weigh

    Returns:
        Combined weight (0.0 to 1.0)
    """
    return _calculate_finding_weight(finding)


def get_conflict_summary(conflicts: list[Conflict]) -> dict:
    """Generate a summary of all conflicts.

    Args:
        conflicts: List of conflicts

    Returns:
        Summary dict with counts, resolution stats, etc.
    """
    resolved = [c for c in conflicts if c.is_resolved]
    unresolved = [c for c in conflicts if not c.is_resolved]

    # Count by type
    by_type: dict[str, int] = {}
    for conflict in conflicts:
        type_name = conflict.conflict_type.value
        by_type[type_name] = by_type.get(type_name, 0) + 1

    # Count by resolution
    by_resolution: dict[str, int] = {}
    for conflict in resolved:
        if conflict.resolution:
            res_name = conflict.resolution.value
            by_resolution[res_name] = by_resolution.get(res_name, 0) + 1

    return {
        'total': len(conflicts),
        'resolved': len(resolved),
        'unresolved': len(unresolved),
        'by_type': by_type,
        'by_resolution': by_resolution,
        'requires_escalation': any(
            c.resolution == ConflictResolution.HUMAN_ESCALATED
            for c in conflicts
        ),
    }


# --- Internal Detection Functions ---


def _detect_root_cause_disagreements(
    findings_a: AgentFindings,
    findings_b: AgentFindings,
    start_id: int,
) -> list[Conflict]:
    """Detect when agents identify different root causes.

    A disagreement exists when both agents have root_cause findings
    that point to different issues (non-overlapping file sets and
    different descriptions).
    """
    conflicts: list[Conflict] = []
    root_a = findings_a.root_cause_findings
    root_b = findings_b.root_cause_findings

    if not root_a or not root_b:
        return conflicts

    for finding_a in root_a:
        for finding_b in root_b:
            # Check if they're describing different things
            if _findings_disagree(finding_a, finding_b):
                conflicts.append(Conflict(
                    conflict_id=f'C-{start_id + len(conflicts):03d}',
                    conflict_type=ConflictType.ROOT_CAUSE_DISAGREEMENT,
                    agent_a=findings_a.agent_name,
                    agent_b=findings_b.agent_name,
                    finding_a=finding_a,
                    finding_b=finding_b,
                    description=(
                        f'Agent {findings_a.agent_name} identifies root cause '
                        f'as "{finding_a.description}" while agent '
                        f'{findings_b.agent_name} identifies it as '
                        f'"{finding_b.description}"'
                    ),
                ))

    return conflicts


def _detect_evidence_contradictions(
    findings_a: AgentFindings,
    findings_b: AgentFindings,
    start_id: int,
) -> list[Conflict]:
    """Detect contradicting evidence between agents.

    Evidence contradicts when the same source file is cited
    with opposing conclusions.
    """
    conflicts: list[Conflict] = []

    for finding_a in findings_a.findings:
        for finding_b in findings_b.findings:
            if _evidence_contradicts(finding_a, finding_b):
                conflicts.append(Conflict(
                    conflict_id=f'C-{start_id + len(conflicts):03d}',
                    conflict_type=ConflictType.EVIDENCE_CONTRADICTION,
                    agent_a=findings_a.agent_name,
                    agent_b=findings_b.agent_name,
                    finding_a=finding_a,
                    finding_b=finding_b,
                    description=(
                        f'Agents cite overlapping sources with different '
                        f'conclusions: {findings_a.agent_name} says '
                        f'"{finding_a.description}", {findings_b.agent_name} '
                        f'says "{finding_b.description}"'
                    ),
                ))

    return conflicts


def _detect_scope_overlaps(
    findings_a: AgentFindings,
    findings_b: AgentFindings,
    start_id: int,
) -> list[Conflict]:
    """Detect overlapping scope between agent findings.

    Scope overlap occurs when agents investigate the same files
    and reach different conclusions.
    """
    conflicts: list[Conflict] = []

    for finding_a in findings_a.findings:
        for finding_b in findings_b.findings:
            overlap = _get_file_overlap(finding_a, finding_b)
            if overlap and _findings_disagree(finding_a, finding_b):
                conflicts.append(Conflict(
                    conflict_id=f'C-{start_id + len(conflicts):03d}',
                    conflict_type=ConflictType.SCOPE_OVERLAP,
                    agent_a=findings_a.agent_name,
                    agent_b=findings_b.agent_name,
                    finding_a=finding_a,
                    finding_b=finding_b,
                    description=(
                        f'Agents overlap on files {overlap} with different '
                        f'conclusions'
                    ),
                ))

    return conflicts


def _detect_classification_mismatches(
    findings_a: AgentFindings,
    findings_b: AgentFindings,
    start_id: int,
) -> list[Conflict]:
    """Detect when agents classify similar issues differently.

    Mismatch occurs when findings reference the same files but
    one classifies as root_cause and another as symptom/contributing.
    """
    conflicts: list[Conflict] = []

    for finding_a in findings_a.findings:
        for finding_b in findings_b.findings:
            overlap = _get_file_overlap(finding_a, finding_b)
            if overlap and _classifications_conflict(finding_a, finding_b):
                conflicts.append(Conflict(
                    conflict_id=f'C-{start_id + len(conflicts):03d}',
                    conflict_type=ConflictType.CLASSIFICATION_MISMATCH,
                    agent_a=findings_a.agent_name,
                    agent_b=findings_b.agent_name,
                    finding_a=finding_a,
                    finding_b=finding_b,
                    description=(
                        f'Agent {findings_a.agent_name} classifies issue in '
                        f'{overlap} as "{finding_a.classification}" while '
                        f'agent {findings_b.agent_name} classifies it as '
                        f'"{finding_b.classification}"'
                    ),
                ))

    return conflicts


# --- Internal Helper Functions ---


def _calculate_finding_weight(finding: Finding) -> float:
    """Calculate combined weight for a finding.

    Combines evidence quality with finding confidence:
    weight = (evidence_weight * 0.6) + (confidence * 0.4)
    """
    evidence_weight = finding.evidence_weight
    confidence = finding.confidence
    return evidence_weight * 0.6 + confidence * 0.4


def _findings_disagree(finding_a: Finding, finding_b: Finding) -> bool:
    """Check if two findings describe different issues.

    Two findings disagree if they have different descriptions
    AND the word overlap between descriptions is below a threshold.
    """
    if finding_a.description == finding_b.description:
        return False

    # Simple word overlap check
    words_a = set(finding_a.description.lower().split())
    words_b = set(finding_b.description.lower().split())

    if not words_a or not words_b:
        return True

    # Stop words to exclude from comparison
    stop_words = {
        'the', 'a', 'an', 'is', 'in', 'on', 'at', 'to', 'for', 'of',
        'and', 'or', 'but', 'with', 'from', 'by', 'as', 'it', 'that',
        'this', 'be', 'are', 'was', 'were', 'has', 'have', 'had',
    }
    words_a -= stop_words
    words_b -= stop_words

    if not words_a or not words_b:
        return True

    overlap = len(words_a & words_b)
    min_words = min(len(words_a), len(words_b))

    # Low overlap = disagreement (threshold: 50%)
    overlap_ratio = overlap / min_words if min_words > 0 else 0.0
    return overlap_ratio < 0.5


def _evidence_contradicts(finding_a: Finding, finding_b: Finding) -> bool:
    """Check if evidence from two findings contradicts.

    Evidence contradicts when findings reference the same source
    files but reach different conclusions (findings disagree).
    """
    sources_a = {e.source for e in finding_a.evidence if e.source}
    sources_b = {e.source for e in finding_b.evidence if e.source}

    if not sources_a or not sources_b:
        return False

    # Check for overlapping sources
    overlapping_sources = sources_a & sources_b
    if not overlapping_sources:
        return False

    # Same source, different conclusions
    return _findings_disagree(finding_a, finding_b)


def _get_file_overlap(
    finding_a: Finding,
    finding_b: Finding,
) -> list[str]:
    """Get overlapping files between two findings.

    Returns:
        List of files that appear in both findings
    """
    files_a = set(finding_a.files_involved)
    files_b = set(finding_b.files_involved)
    return sorted(files_a & files_b)


def _classifications_conflict(
    finding_a: Finding,
    finding_b: Finding,
) -> bool:
    """Check if two findings have conflicting classifications.

    Conflicting classifications are:
    - root_cause vs symptom
    - root_cause vs contributing
    """
    classes = {finding_a.classification, finding_b.classification}

    conflicting_pairs = [
        {'root_cause', 'symptom'},
        {'root_cause', 'contributing'},
    ]

    return classes in conflicting_pairs
