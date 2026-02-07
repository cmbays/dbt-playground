"""Shared utilities for Multi-Agent Debug modules.

Provides common functions for pattern extraction and tag generation
used across multiple modules.

Part of WAVE3-030: Multi-agent debugging coordination (Issue #266)
"""

from scripts.lib.multi_agent_debug.models import Finding


def generate_pattern_name(finding: Finding) -> str:
    """Generate a human-readable pattern name from a finding.

    Args:
        finding: The finding

    Returns:
        Title-cased pattern name (max 60 chars)
    """
    desc = finding.description
    if len(desc) > 60:
        desc = desc[:57] + '...'
    return desc.title()


def extract_tags(finding: Finding) -> list[str]:
    """Extract tags from a finding based on keyword matching.

    Args:
        finding: The finding

    Returns:
        List of matching tags
    """
    tags: list[str] = []
    text = (finding.description + ' ' + (finding.proposed_fix or '')).lower()

    tag_keywords = {
        'database': ['database', 'db', 'sql', 'query', 'pool', 'connection'],
        'performance': ['slow', 'timeout', 'latency', 'bottleneck', 'memory'],
        'concurrency': ['race', 'concurrent', 'thread', 'lock', 'deadlock'],
        'configuration': ['config', 'setting', 'parameter', 'env'],
        'frontend': ['ui', 'component', 'render', 'dom', 'css'],
        'api': ['api', 'endpoint', 'request', 'response', 'http'],
        'security': ['auth', 'token', 'permission', 'credential'],
    }

    for tag, keywords in tag_keywords.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)

    return tags
