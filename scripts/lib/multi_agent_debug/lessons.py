"""LESSONS.md Integration for Multi-Agent Debug Sessions.

Extracts learning patterns from multi-agent debates and feeds them
to the existing memory system (events.jsonl) and lessons analyzer
(WAVE3-021) for compound learning.

Lesson candidates come from:
  - High-confidence root causes (>=0.7 confidence)
  - Resolved conflict debates (evidence-weighted winner)

Integration points:
  - memory/events.jsonl: Emits debug_lesson events
  - scripts/consolidate-memory.py: Processes debug patterns
  - scripts/lib/lessons_analyzer/: Pattern detection pipeline

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from scripts.lib.multi_agent_debug.models import (
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


def extract_debate_patterns(
    resolution: MergeResolution,
) -> list[LessonCandidate]:
    """Extract learning patterns from multi-agent debate outcomes.

    Key insight: When agents disagree and resolution reveals truth,
    that is a valuable learning pattern. We capture both:
    1. What the correct answer was (from evidence-weighted resolution)
    2. What the incorrect hypothesis was (common misdiagnosis)

    Args:
        resolution: The merge resolution from a multi-agent session

    Returns:
        List of lesson candidates for promotion
    """
    lessons: list[LessonCandidate] = []

    # Pattern 1: From resolved conflicts (debate-driven insights)
    for conflict in resolution.conflicts:
        lesson = _extract_from_conflict(conflict, resolution.session_id)
        if lesson is not None:
            lessons.append(lesson)

    # Pattern 2: From high-confidence root causes
    for finding in resolution.consensus_findings:
        lesson = _extract_from_finding(finding, resolution.session_id)
        if lesson is not None:
            # Avoid duplicates from conflicts
            if not any(l.pattern_name == lesson.pattern_name for l in lessons):
                lessons.append(lesson)

    return lessons


def emit_lesson_events(
    lessons: list[LessonCandidate],
    events_file: Optional[str] = None,
) -> int:
    """Emit debug_lesson events to memory/events.jsonl.

    Each lesson candidate is emitted as a structured event that
    the consolidate-memory.py pipeline can process for pattern
    detection and promotion.

    Args:
        lessons: Lesson candidates to emit
        events_file: Path to events.jsonl (auto-detected if None)

    Returns:
        Number of events emitted
    """
    if not lessons:
        return 0

    events_path = _resolve_events_path(events_file)
    emitted = 0

    # Ensure parent directory exists
    events_path.parent.mkdir(parents=True, exist_ok=True)

    with events_path.open('a', encoding='utf-8') as f:
        for lesson in lessons:
            event = _build_lesson_event(lesson)
            f.write(json.dumps(event) + '\n')
            emitted += 1

    return emitted


def format_lesson_for_review(lesson: LessonCandidate) -> str:
    """Format a lesson candidate as markdown for human review.

    Args:
        lesson: The lesson candidate

    Returns:
        Formatted markdown string
    """
    lines: list[str] = []

    lines.append(f'### {lesson.pattern_name}')
    lines.append('')
    lines.append(f'**Context**: {lesson.context}')
    lines.append(f'**Confidence**: {lesson.confidence:.2f}')
    lines.append(f'**Source Session**: {lesson.source_session}')

    if lesson.source_conflict:
        lines.append(f'**Source Conflict**: {lesson.source_conflict}')

    lines.append('')
    lines.append(f'**Problem**: {lesson.problem}')
    lines.append(f'**Solution**: {lesson.solution}')
    lines.append(f'**Detection**: {lesson.detection}')

    if lesson.tags:
        tags_str = ', '.join(lesson.tags)
        lines.append(f'**Tags**: {tags_str}')

    lines.append('')

    return '\n'.join(lines)


def format_all_lessons(lessons: list[LessonCandidate]) -> str:
    """Format all lesson candidates as a review document.

    Args:
        lessons: All lesson candidates from a session

    Returns:
        Complete markdown document for review
    """
    if not lessons:
        return '## No Lesson Candidates\n\nNo patterns met the threshold for extraction.\n'

    lines: list[str] = []

    lines.append('## Lesson Candidates from Multi-Agent Debug')
    lines.append('')
    lines.append(f'**Total Candidates**: {len(lessons)}')
    lines.append(
        f'**Extraction Date**: '
        f'{datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")}'
    )
    lines.append('')
    lines.append('---')
    lines.append('')

    # Group by source type
    from_conflicts = [l for l in lessons if l.source_conflict]
    from_findings = [l for l in lessons if not l.source_conflict]

    if from_conflicts:
        lines.append('### From Debate Resolution')
        lines.append('')
        for lesson in from_conflicts:
            lines.append(format_lesson_for_review(lesson))

    if from_findings:
        lines.append('### From High-Confidence Root Causes')
        lines.append('')
        for lesson in from_findings:
            lines.append(format_lesson_for_review(lesson))

    return '\n'.join(lines)


# --- Internal Functions ---


def _extract_from_conflict(
    conflict: Conflict,
    session_id: str,
) -> Optional[LessonCandidate]:
    """Extract a lesson from a resolved conflict.

    Only extracts from evidence-weighted resolutions where the
    winning finding has sufficient confidence (>=0.7).

    Args:
        conflict: The resolved conflict
        session_id: Source session ID

    Returns:
        LessonCandidate or None if threshold not met
    """
    if conflict.resolution != ConflictResolution.EVIDENCE_WEIGHTED:
        return None

    if conflict.resolved_finding is None:
        return None

    finding = conflict.resolved_finding

    # Require minimum confidence for lesson extraction
    if finding.confidence < 0.7:
        return None

    return LessonCandidate(
        pattern_name=generate_pattern_name(finding),
        context=f'Multi-agent debate in session {session_id}',
        problem=finding.description,
        solution=finding.proposed_fix or 'Investigation finding (no fix proposed)',
        detection=(
            f'Resolved via {conflict.conflict_type.value}: '
            f'{conflict.agent_a} vs {conflict.agent_b}'
        ),
        source_session=session_id,
        source_conflict=conflict.conflict_id,
        confidence=finding.confidence,
        tags=extract_tags(finding),
    )


def _extract_from_finding(
    finding: Finding,
    session_id: str,
) -> Optional[LessonCandidate]:
    """Extract a lesson from a high-confidence finding.

    Only root_cause findings with confidence >= 0.7 and a
    proposed fix are eligible.

    Args:
        finding: The finding to evaluate
        session_id: Source session ID

    Returns:
        LessonCandidate or None if threshold not met
    """
    if finding.classification != 'root_cause':
        return None

    if finding.confidence < 0.7:
        return None

    if not finding.proposed_fix:
        return None

    return LessonCandidate(
        pattern_name=generate_pattern_name(finding),
        context=f'Multi-agent consensus in session {session_id}',
        problem=finding.description,
        solution=finding.proposed_fix,
        detection='High-confidence root cause from multi-agent investigation',
        source_session=session_id,
        confidence=finding.confidence,
        tags=extract_tags(finding),
    )


def _build_lesson_event(lesson: LessonCandidate) -> dict:
    """Build a structured event dict for events.jsonl.

    Event format matches the existing schema used by
    consolidate-memory.py and the FS1 memory system.

    Args:
        lesson: The lesson candidate

    Returns:
        Event dict ready for JSON serialization
    """
    return {
        'timestamp': datetime.now(UTC).isoformat(),
        'event': 'debug_lesson',
        'version': '1.0',
        'data': {
            'pattern_name': lesson.pattern_name,
            'problem': lesson.problem,
            'solution': lesson.solution,
            'detection': lesson.detection,
            'confidence': lesson.confidence,
            'source': 'multi_agent_session',
            'session_id': lesson.source_session,
            'conflict_id': lesson.source_conflict,
            'tags': lesson.tags,
        },
    }


def _resolve_events_path(events_file: Optional[str] = None) -> Path:
    """Resolve the path to memory/events.jsonl.

    Searches up from CWD for CLAUDE.md to find the project root,
    then returns the events.jsonl path.

    Args:
        events_file: Explicit path (used if provided)

    Returns:
        Path to events.jsonl
    """
    if events_file:
        return Path(events_file)

    # Search for project root
    for parent in [Path.cwd(), *Path.cwd().parents]:
        if (parent / 'CLAUDE.md').exists():
            return parent / 'memory' / 'events.jsonl'

    # Fallback
    return Path('memory') / 'events.jsonl'
