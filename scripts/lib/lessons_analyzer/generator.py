"""LESSONS.md entry generator.

Generates formatted entries following LEARNINGS.md style.
"""

from datetime import datetime

from scripts.lib.lessons_analyzer.models import Pattern


def infer_when_to_apply(pattern: Pattern) -> str:
    """Infer when to apply this pattern based on keywords.

    Args:
        pattern: Pattern to analyze

    Returns:
        Context string for when to apply
    """
    pattern_lower = pattern.pattern_name.lower()
    tags_str = ' '.join(pattern.tags).lower() if pattern.tags else ''

    if 'race' in pattern_lower or 'concurrent' in pattern_lower:
        return 'Any concurrent/async code with shared mutable state'

    if 'null' in pattern_lower or 'none' in pattern_lower:
        return 'Code paths that may receive None/null values from external sources'

    if 'timeout' in pattern_lower:
        return 'External service calls, database queries, or network operations'

    if 'state' in pattern_lower or 'corrupt' in pattern_lower:
        return 'State management in complex flows or multi-step processes'

    if 'import' in pattern_lower or 'module' in pattern_lower:
        return 'Module initialization or dynamic imports'

    if 'type' in pattern_lower or 'cast' in pattern_lower:
        return 'Type conversions or data transformations'

    # Fallback based on tags
    if 'async' in tags_str:
        return 'Async/concurrent code execution'
    if 'api' in tags_str:
        return 'API endpoints or external integrations'
    if 'database' in tags_str or 'sql' in tags_str:
        return 'Database operations and queries'

    return 'Similar contexts to the documented sessions'


def infer_mitigations(pattern: Pattern) -> list[str]:
    """Infer mitigations based on pattern keywords.

    Args:
        pattern: Pattern to analyze

    Returns:
        List of suggested mitigations
    """
    mitigations = []
    pattern_lower = pattern.pattern_name.lower()
    causes_text = ' '.join(rc.cause.lower() for rc in pattern.root_causes)

    if 'race' in pattern_lower or 'concurrent' in pattern_lower:
        mitigations.extend([
            'Add mutex/lock on shared mutable state',
            'Use thread-safe data structures',
            'Add race condition to code review checklist',
        ])

    if 'null' in pattern_lower or 'none' in causes_text:
        mitigations.extend([
            'Add explicit null checks before use',
            'Use Optional types with type hints',
            'Enable strict null checking in linter',
        ])

    if 'timeout' in pattern_lower:
        mitigations.extend([
            'Configure appropriate timeouts with retry logic',
            'Add circuit breaker pattern for external calls',
            'Monitor and alert on timeout rates',
        ])

    if 'state' in pattern_lower or 'corruption' in causes_text:
        mitigations.extend([
            'Use immutable data structures where possible',
            'Add schema validation on state transitions',
            'Implement state machine pattern for complex flows',
        ])

    if 'import' in pattern_lower or 'module' in pattern_lower:
        mitigations.extend([
            'Use explicit import paths',
            'Document module dependencies',
            'Add import validation to CI',
        ])

    if 'type' in pattern_lower or 'cast' in causes_text:
        mitigations.extend([
            'Add runtime type validation',
            'Use type hints comprehensively',
            'Enable strict type checking',
        ])

    if not mitigations:
        mitigations = [
            'Document pattern in team knowledge base',
            'Add to code review checklist',
            'Consider automated detection in CI',
        ]

    return mitigations[:4]  # Limit to 4 mitigations


def generate_description(pattern: Pattern) -> str:
    """Generate pattern description.

    Args:
        pattern: Pattern to describe

    Returns:
        Description string
    """
    pattern_lower = pattern.pattern_name.lower()

    if 'race' in pattern_lower:
        return (
            'Race conditions occur when multiple threads or coroutines access '
            'shared state without proper synchronization. This pattern typically '
            'manifests as intermittent failures that are hard to reproduce.'
        )

    if 'null' in pattern_lower:
        return (
            'Null reference errors occur when code assumes a value will be present '
            'but receives None/null instead. Often happens at API boundaries or '
            'during data transformation.'
        )

    if 'timeout' in pattern_lower:
        return (
            'Timeout errors occur when operations take longer than expected, '
            'typically in external service calls or complex queries. Can cascade '
            'into system-wide issues if not handled properly.'
        )

    if 'state' in pattern_lower:
        return (
            'State corruption occurs when system state becomes inconsistent, '
            'often due to partial updates, missing validations, or concurrent '
            'modifications.'
        )

    # Generic description
    freq = pattern.frequency
    days = pattern.days_since_last
    return (
        f'This pattern has occurred {freq} times and was last seen '
        f'{days} days ago. Review the related sessions for common symptoms '
        'and effective mitigations.'
    )


def generate_symptoms(pattern: Pattern) -> str:
    """Generate symptom list based on pattern.

    Args:
        pattern: Pattern to analyze

    Returns:
        Formatted symptom list
    """
    pattern_lower = pattern.pattern_name.lower()

    if 'race' in pattern_lower:
        return """- Intermittent failures under load
- Different results between runs
- "Works on my machine" bugs
- Timing-dependent test failures"""

    if 'null' in pattern_lower:
        return """- NoneType/null reference errors
- KeyError or AttributeError
- Unexpected empty values
- Failures on edge case inputs"""

    if 'timeout' in pattern_lower:
        return """- Request timeouts or hung operations
- Slow response times under load
- Connection pool exhaustion
- Cascading failures"""

    if 'state' in pattern_lower:
        return """- Inconsistent data between reads
- Invalid state transitions
- Stale data after updates
- Partial operation results"""

    # Generic symptoms from root causes
    symptoms = ['- Unexpected behavior in production']
    for rc in pattern.root_causes[:2]:
        symptoms.append(f'- Related to: {rc.cause[:50]}')
    return '\n'.join(symptoms)


def generate_lessons_entry(pattern: Pattern, include_sessions: int = 3) -> str:
    """Generate LESSONS.md formatted entry from pattern.

    Args:
        pattern: Pattern to generate entry for
        include_sessions: Number of example sessions to include

    Returns:
        Formatted markdown entry
    """
    # Determine confidence level
    if pattern.confidence_score >= 0.85:
        conf_level = 'HIGH'
    elif pattern.confidence_score >= 0.7:
        conf_level = 'MEDIUM'
    else:
        conf_level = 'LOW'

    # Format root causes with percentages
    total_count = sum(rc.count for rc in pattern.root_causes)
    root_causes_formatted = []
    for rc in pattern.root_causes:
        pct = int((rc.count / total_count) * 100) if total_count > 0 else 0
        root_causes_formatted.append(f'{rc.cause} ({pct}%)')

    # Get mitigations
    mitigations = pattern.suggested_mitigations or infer_mitigations(pattern)

    # Build entry
    entry = f"""### Pattern: {pattern.pattern_name}

**When to apply**: {infer_when_to_apply(pattern)}

**Proven in**: v0.11+ ({pattern.frequency} occurrences: {pattern.first_seen.strftime('%Y-%m-%d')} to {pattern.last_seen.strftime('%Y-%m-%d')})

**Description**: {generate_description(pattern)}

**Common Root Causes**:
"""
    for i, rc in enumerate(root_causes_formatted, 1):
        entry += f'{i}. {rc}\n'

    entry += f"""
**Symptoms**:
{generate_symptoms(pattern)}

**Mitigations**:
"""
    for i, mit in enumerate(mitigations, 1):
        entry += f'{i}. {mit}\n'

    entry += f"""
**Debug Time**: Average {int(pattern.avg_debug_minutes)} minutes

**See also**:
- Sessions: {', '.join(pattern.related_sessions[:include_sessions])}

---

*Generated by WAVE3-021 Analyzer on {datetime.now().strftime('%Y-%m-%d')}*
*Confidence: {pattern.confidence_score:.2f} ({conf_level}) | Frequency: {pattern.frequency} | Status: {pattern.status}*
"""

    return entry
