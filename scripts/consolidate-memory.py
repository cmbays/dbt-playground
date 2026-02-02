#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Weekly memory consolidation script for Agent Memory System.

Usage:
    uv run scripts/consolidate-memory.py              # Consolidate last 7 days
    uv run scripts/consolidate-memory.py --days 14    # Custom date range
    uv run scripts/consolidate-memory.py --help       # Show help

Part of FS1: Agent Memory & Learning System (Epic #143)
Issues: #153
"""

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from math import log
from pathlib import Path

# Add scripts directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.memory_utils import get_memory_dir

# Stop words to ignore in keyword extraction
STOP_WORDS = {
    'the',
    'a',
    'an',
    'is',
    'are',
    'was',
    'were',
    'be',
    'been',
    'being',
    'have',
    'has',
    'had',
    'do',
    'does',
    'did',
    'will',
    'would',
    'could',
    'should',
    'may',
    'might',
    'must',
    'to',
    'of',
    'in',
    'for',
    'on',
    'with',
    'at',
    'by',
    'from',
    'as',
    'into',
    'through',
    'during',
    'before',
    'after',
    'and',
    'but',
    'or',
    'if',
    'because',
    'while',
    'this',
    'that',
    'it',
    'its',
    'not',
    'no',
    'yes',
    'also',
    'just',
    'only',
    'very',
    'more',
    'most',
    'some',
    'can',
    'need',
    'use',
    'using',
    'used',
    'none',
    'documented',
    'nothing',
    'noted',
}


@dataclass
class TextItem:
    """A piece of text from log entries."""

    entry_date: date
    category: str  # 'learning', 'decision', 'improvement'
    text: str
    source_task: str


@dataclass
class PatternGroup:
    """Group of similar text items."""

    category: str
    items: list[TextItem] = field(default_factory=list)
    summary: str = ''
    score: float = 0.0
    status: str = 'REVIEW'

    @property
    def count(self) -> int:
        return len(self.items)

    @property
    def dates(self) -> list[date]:
        return sorted({item.entry_date for item in self.items})


def normalize(text: str) -> set[str]:
    """Convert text to normalized keyword set."""
    words = re.findall(r'\b[a-z][a-z0-9_]+\b', text.lower())
    return {w for w in words if len(w) > 2 and w not in STOP_WORDS}


def keyword_overlap(set1: set[str], set2: set[str]) -> float:
    """Calculate overlap ratio between keyword sets."""
    if not set1 or not set2:
        return 0.0
    smaller = min(len(set1), len(set2))
    overlap = len(set1 & set2)
    return overlap / smaller if smaller > 0 else 0.0


def parse_log_file(path: Path) -> list[dict]:
    """Parse markdown log file into entries."""
    content = path.read_text()
    entries = []

    sections = re.split(r'^## \[', content, flags=re.MULTILINE)

    for section in sections[1:]:
        entry = {}

        # Parse timestamp and task
        match = re.match(r'([\d\-T:]+)\] Task: (.+)', section)
        if match:
            entry['timestamp'] = match.group(1)
            entry['task'] = match.group(2).strip()

        # Parse task_id
        task_id_match = re.search(r'\*\*Task ID\*\*:\s*(\S+)', section)
        if task_id_match:
            entry['task_id'] = task_id_match.group(1)

        # Parse outcome
        outcome_match = re.search(r'\*\*Outcome\*\*:\s*(\w+)', section)
        if outcome_match:
            entry['outcome'] = outcome_match.group(1)

        # Parse learnings
        learnings_match = re.search(r'\*\*Learnings\*\*:\n((?:- .+\n?)+)', section)
        if learnings_match:
            learnings = re.findall(r'- (.+)', learnings_match.group(1))
            entry['learnings'] = [
                learning for learning in learnings if learning not in ('None documented', 'None')
            ]

        # Parse decisions
        decisions_match = re.search(r'\*\*Key Decisions\*\*:\n((?:- .+\n?)+)', section)
        if decisions_match:
            decisions = re.findall(r'- (.+)', decisions_match.group(1))
            entry['decisions'] = [
                decision for decision in decisions if decision not in ('None documented', 'None')
            ]

        # Parse improvements
        improve_match = re.search(r'\*\*Would Do Differently\*\*:\n((?:- .+\n?)+)', section)
        if improve_match:
            improvements = re.findall(r'- (.+)', improve_match.group(1))
            entry['improvements'] = [
                improvement
                for improvement in improvements
                if improvement not in ('Nothing noted', 'Nothing')
            ]

        if entry:
            entries.append(entry)

    return entries


def group_similar(items: list[TextItem], threshold: float = 0.5) -> list[PatternGroup]:
    """Group items by keyword overlap using greedy matching."""
    if not items:
        return []

    by_category = {}
    for item in items:
        by_category.setdefault(item.category, []).append(item)

    groups = []

    for category, cat_items in by_category.items():
        used = set()
        keywords_cache = {i: normalize(item.text) for i, item in enumerate(cat_items)}

        for i, item1 in enumerate(cat_items):
            if i in used:
                continue

            group = PatternGroup(category=category, items=[item1])
            kw1 = keywords_cache[i]
            used.add(i)

            for j, item2 in enumerate(cat_items):
                if j in used:
                    continue

                kw2 = keywords_cache[j]
                if keyword_overlap(kw1, kw2) >= threshold:
                    group.items.append(item2)
                    used.add(j)

            if group.count >= 2:
                group.summary = min(group.items, key=lambda x: len(x.text)).text
                groups.append(group)

    return groups


def score_pattern(group: PatternGroup, today: date) -> float:
    """Score pattern by frequency, recency, and consistency (Alpha's multi-factor)."""
    if group.count < 2:
        return 0.0

    # Frequency (log scale)
    freq_score = log(group.count + 1) / log(10)

    # Recency (higher for recent patterns)
    days_ago = [(today - item.entry_date).days for item in group.items]
    avg_days = sum(days_ago) / len(days_ago)
    recency_score = max(0, 1 - (avg_days / 14))

    # Consistency (patterns across different tasks)
    unique_tasks = len({item.source_task for item in group.items if item.source_task})
    consistency_score = min(1.0, unique_tasks / group.count) if group.count > 0 else 0

    # Weighted combination
    return (0.4 * freq_score) + (0.3 * recency_score) + (0.3 * consistency_score)


def determine_status(group: PatternGroup) -> str:
    """Determine promotion status based on score and spread."""
    if group.score >= 0.7:
        return 'CANDIDATE'
    elif group.score >= 0.4:
        return 'REVIEW'
    elif group.count >= 3 or group.count >= 2 and len(group.dates) >= 2:
        return 'CANDIDATE'
    elif group.count >= 2:
        return 'REVIEW'
    return 'REJECTED'


def generate_memory_index(result: dict) -> str:
    """Generate MEMORY_INDEX.md content."""
    lines = [
        '# Memory Index',
        '',
        f'**Generated**: {datetime.now(UTC).isoformat(timespec="seconds")}',
        f'**Period**: {result["period_start"]} to {result["period_end"]}',
        f'**Total Entries**: {result["total_entries"]}',
        '',
        '---',
        '',
        '## Weekly Summary',
        '',
    ]

    # Daily summary
    if result.get('daily_summary'):
        lines.extend(
            [
                '| Day | Entries | Outcomes |',
                '|-----|---------|----------|',
            ]
        )
        for day in result['daily_summary']:
            lines.append(f'| {day["date"]} | {day["count"]} | {day["outcomes"]} |')
        lines.append('')

    # Patterns
    lines.extend(
        [
            '---',
            '',
            '## Recurring Patterns (2+ occurrences)',
            '',
        ]
    )

    if result['patterns']:
        for i, pattern in enumerate(result['patterns'][:10], 1):
            lines.extend(
                [
                    '',  # Blank line before heading for markdownlint
                    f'### Pattern {i}: {pattern["category"].title()}',
                    '',
                    f'**Occurrences**: {pattern["count"]} ({", ".join(pattern["dates"])})',
                    f'**Summary**: {pattern["summary"]}',
                    f'**Score**: {pattern["score"]:.2f}',
                    f'**Promotion Status**: {pattern["status"]}',
                    '',
                ]
            )
    else:
        lines.append('No recurring patterns detected this period.')
        lines.append('')

    # Topics index
    lines.extend(
        [
            '---',
            '',
            '## Topics Index',
            '',
            '| Topic | Count |',
            '|-------|-------|',
        ]
    )
    for topic, count in list(result['topics_index'].items())[:15]:
        lines.append(f'| {topic} | {count} |')
    lines.append('')

    # Failed experiments
    if result['failed_experiments']:
        lines.extend(
            [
                '---',
                '',
                '## Failed Experiments',
                '',
                '| Date | Task | Learnings |',
                '|------|------|-----------|',
            ]
        )
        for exp in result['failed_experiments'][:5]:
            learnings = '; '.join(exp.get('learnings', [])[:2]) or 'None documented'
            lines.append(f'| {exp["date"]} | {exp["task"][:30]}... | {learnings[:50]}... |')
        lines.append('')

    # Promotion candidates
    if result['promotion_candidates']:
        lines.extend(
            [
                '---',
                '',
                '## Promotion Candidates for LEARNINGS.md',
                '',
            ]
        )
        for candidate in result['promotion_candidates']:
            lines.append(f'- [ ] {candidate}')
        lines.append('')

    lines.extend(
        [
            '---',
            '',
            '*Generated by Sage Workflow K (consolidate-memory.py)*',
            '',  # Trailing newline
        ]
    )

    return '\n'.join(lines)


def emit_consolidation_event(result: dict, memory_dir: Path) -> None:
    """Emit consolidation event to events.jsonl."""
    events_file = memory_dir / 'events.jsonl'

    event = {
        'timestamp': datetime.now(UTC).isoformat(),
        'event': 'week_consolidated',
        'version': '1.0',
        'data': {
            'period_start': result['period_start'],
            'period_end': result['period_end'],
            'total_entries': result['total_entries'],
            'patterns_found': len(result['patterns']),
            'patterns_promoted': len([p for p in result['patterns'] if p['status'] == 'CANDIDATE']),
        },
    }

    with open(events_file, 'a') as f:
        f.write(json.dumps(event) + '\n')


def consolidate(memory_dir: Path, days: int = 7) -> dict:
    """Main consolidation function."""
    today = date.today()
    cutoff = today - timedelta(days=days)

    items = []
    total_entries = 0
    failures = []
    daily_counts = {}

    for log_file in sorted(memory_dir.glob('????-??-??.md')):
        try:
            file_date = date.fromisoformat(log_file.stem)
        except ValueError:
            continue

        if file_date < cutoff:
            continue

        entries = parse_log_file(log_file)
        total_entries += len(entries)
        daily_counts[file_date.isoformat()] = {
            'count': len(entries),
            'outcomes': Counter(e.get('outcome', 'UNKNOWN') for e in entries),
        }

        for entry in entries:
            if entry.get('outcome') == 'FAILURE':
                failures.append(
                    {
                        'date': file_date.isoformat(),
                        'task': entry.get('task', 'Unknown'),
                        'learnings': entry.get('learnings', []),
                    }
                )

            for learning in entry.get('learnings', []):
                items.append(
                    TextItem(
                        entry_date=file_date,
                        category='learning',
                        text=learning,
                        source_task=entry.get('task', ''),
                    )
                )

            for decision in entry.get('decisions', []):
                items.append(
                    TextItem(
                        entry_date=file_date,
                        category='decision',
                        text=decision,
                        source_task=entry.get('task', ''),
                    )
                )

            for improvement in entry.get('improvements', []):
                items.append(
                    TextItem(
                        entry_date=file_date,
                        category='improvement',
                        text=improvement,
                        source_task=entry.get('task', ''),
                    )
                )

    # Group and score
    groups = group_similar(items, threshold=0.5)

    for group in groups:
        group.score = score_pattern(group, today)
        group.status = determine_status(group)

    groups.sort(key=lambda g: g.score, reverse=True)

    # Build topics index
    all_keywords = []
    for item in items:
        all_keywords.extend(normalize(item.text))
    topics = dict(Counter(all_keywords).most_common(20))

    # Daily summary
    daily_summary = []
    for d, data in sorted(daily_counts.items()):
        outcomes_str = ', '.join(f'{k}: {v}' for k, v in data['outcomes'].items())
        daily_summary.append({'date': d, 'count': data['count'], 'outcomes': outcomes_str})

    return {
        'period_start': cutoff.isoformat(),
        'period_end': today.isoformat(),
        'total_entries': total_entries,
        'patterns': [
            {
                'category': g.category,
                'summary': g.summary,
                'count': g.count,
                'dates': [d.isoformat() for d in g.dates],
                'score': round(g.score, 3),
                'status': g.status,
            }
            for g in groups
        ],
        'promotion_candidates': [g.summary for g in groups if g.status == 'CANDIDATE'],
        'topics_index': topics,
        'failed_experiments': failures,
        'daily_summary': daily_summary,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Consolidate memory logs for pattern detection',
        epilog='Part of FS1: Agent Memory & Learning System',
    )
    parser.add_argument(
        '--days', '-d', type=int, default=7, help='Number of days to consolidate (default: 7)'
    )
    parser.add_argument('--dry-run', action='store_true', help='Show results without writing files')
    args = parser.parse_args()

    try:
        memory_dir = get_memory_dir()
        print('\n=== Memory Consolidation ===')
        print(f'Directory: {memory_dir}')
        print(f'Period: {args.days} days\n')

        result = consolidate(memory_dir, args.days)

        print(f'Entries found: {result["total_entries"]}')
        print(f'Patterns detected: {len(result["patterns"])}')
        print(f'Promotion candidates: {len(result["promotion_candidates"])}')

        if result['promotion_candidates']:
            print('\nPromotion candidates for LEARNINGS.md:')
            for candidate in result['promotion_candidates']:
                print(f'  - {candidate}')

        if not args.dry_run:
            # Write MEMORY_INDEX.md
            index_content = generate_memory_index(result)
            index_file = memory_dir / 'MEMORY_INDEX.md'
            index_file.write_text(index_content)
            print(f'\n[OK] Written: {index_file}')

            # Emit event
            emit_consolidation_event(result, memory_dir)
            print('[OK] Event emitted to memory/events.jsonl')
        else:
            print('\n[DRY RUN] No files written')

        return 0

    except FileNotFoundError as e:
        print(f'Error: {e}')
        return 1
    except Exception as e:
        print(f'Error: {e}')
        return 1


if __name__ == '__main__':
    exit(main())
