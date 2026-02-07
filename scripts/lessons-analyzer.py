#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.2.0", "rich>=13.0.0"]
# ///
"""
LESSONS.md Analyzer CLI - WAVE3-021

Automated pattern extraction engine that analyzes debug sessions
to identify recurring root causes for compound learning.

Usage:
    uv run scripts/lessons-analyzer.py extract
    uv run scripts/lessons-analyzer.py review --pattern "Race condition"
    uv run scripts/lessons-analyzer.py generate --pattern "Race condition"
    uv run scripts/lessons-analyzer.py stats

Part of Wave 3 P1: Protocol Enhancements (Issue #238)
"""

import argparse
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add scripts directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib.lessons_analyzer import (
    AnalyzerError,
    DatabaseNotFoundError,
    InsufficientDataError,
    LessonsAnalyzer,
    NoSessionsFoundError,
    PatternNotFoundError,
)


def cmd_extract(args) -> int:
    """Handle extract command."""
    analyzer = LessonsAnalyzer()

    try:
        # Parse dates
        since = None
        until = None

        if args.since:
            since = datetime.fromisoformat(args.since)
            if since.tzinfo is None:
                since = since.replace(tzinfo=UTC)
        else:
            since = datetime.now(UTC) - timedelta(days=30)

        if args.until:
            until = datetime.fromisoformat(args.until)
            if until.tzinfo is None:
                until = until.replace(tzinfo=UTC)

        patterns = analyzer.extract(
            since=since,
            until=until,
            min_frequency=args.min_frequency,
            min_score=args.min_score,
            category=args.category,
            limit=args.limit,
        )

        # Get total session count for context
        stats = analyzer.get_stats(since=since)

        if args.format == 'json':
            output = {
                'analysis_period': {
                    'start': since.strftime('%Y-%m-%d'),
                    'end': (until or datetime.now(UTC)).strftime('%Y-%m-%d'),
                },
                'sessions_analyzed': stats['total_sessions'],
                'patterns': [
                    {
                        'pattern_name': p.pattern_name,
                        'frequency': p.frequency,
                        'last_seen': p.last_seen.strftime('%Y-%m-%d'),
                        'confidence_score': round(p.confidence_score, 2),
                        'root_causes': [
                            {'cause': rc.cause, 'count': rc.count}
                            for rc in p.root_causes
                        ],
                        'related_sessions': p.related_sessions,
                        'status': p.status,
                    }
                    for p in patterns
                ],
            }
            print(json.dumps(output, indent=2))

        elif args.format == 'markdown':
            print(f'# Pattern Analysis ({since.strftime("%Y-%m-%d")} to {datetime.now(UTC).strftime("%Y-%m-%d")})\n')
            print(f'Sessions analyzed: {stats["total_sessions"]}')
            print(f'Patterns detected: {len(patterns)}\n')

            for p in patterns:
                entry = analyzer.generate_entry(p)
                print(entry)
                print()

        else:  # table format
            print(f'Pattern Analysis ({since.strftime("%Y-%m-%d")} to {datetime.now(UTC).strftime("%Y-%m-%d")})')
            print(f'Sessions analyzed: {stats["total_sessions"]}')
            print(f'Patterns detected: {len(patterns)}')
            print()

            if not patterns:
                print('  No patterns found matching criteria.')
                print()
                print('Try lowering --min-frequency or --min-score, or widening --since date.')
            else:
                print(f'{"Rank":<5} | {"Pattern":<34} | {"Freq":<4} | {"Last Seen":<10} | {"Score":<5} | {"Status":<10}')
                print('-' * 5 + '-+-' + '-' * 34 + '-+-' + '-' * 4 + '-+-' + '-' * 10 + '-+-' + '-' * 5 + '-+-' + '-' * 10)

                for i, p in enumerate(patterns, 1):
                    name = p.pattern_name[:32] + '..' if len(p.pattern_name) > 34 else p.pattern_name
                    print(f'{i:<5} | {name:<34} | {p.frequency:<4} | {p.last_seen.strftime("%Y-%m-%d"):<10} | {p.confidence_score:.2f} | {p.status:<10}')

                print()
                print(f"Use 'lessons-analyzer.py review --pattern \"<name>\"' for details.")
                print(f"Use 'lessons-analyzer.py generate --pattern \"<name>\"' to create LESSONS entry.")

        return 0

    except DatabaseNotFoundError as e:
        print(f'[ERROR] {e}')
        return 1
    except NoSessionsFoundError as e:
        print(f'[WARN] {e}')
        print('Try widening your date range with --since or removing filters.')
        return 0  # Not an error, just no data
    except InsufficientDataError as e:
        print(f'[WARN] {e}')
        return 0
    except AnalyzerError as e:
        print(f'[ERROR] {e}')
        return 1
    finally:
        analyzer.close()


def cmd_review(args) -> int:
    """Handle review command."""
    analyzer = LessonsAnalyzer()

    try:
        pattern = analyzer.review(args.pattern)

        print(f'Pattern Review: {pattern.pattern_name}')
        print('=' * (len(pattern.pattern_name) + 17))
        print()
        print('Summary:')
        print(f'  Frequency: {pattern.frequency} occurrences')
        print(f'  First seen: {pattern.first_seen.strftime("%Y-%m-%d")}')
        print(f'  Last seen: {pattern.last_seen.strftime("%Y-%m-%d")}')

        conf_level = 'HIGH' if pattern.confidence_score >= 0.85 else ('MEDIUM' if pattern.confidence_score >= 0.7 else 'LOW')
        print(f'  Confidence: {pattern.confidence_score:.2f} ({conf_level})')
        print(f'  Status: {pattern.status}')

        print()
        print('Root Cause Variants:')
        for i, rc in enumerate(pattern.root_causes, 1):
            print(f'  {i}. {rc.cause} ({rc.count} occurrences)')
            for sid in rc.example_sessions[:2]:
                print(f'     - {sid}')

        if pattern.tags:
            from collections import Counter
            tag_counts = Counter(pattern.tags)
            tags_str = ', '.join(f'{t} ({c})' for t, c in tag_counts.most_common(5))
            print()
            print(f'Related Tags:')
            print(f'  {tags_str}')

        if pattern.avg_debug_minutes:
            print()
            print(f'Average Debug Time: {int(pattern.avg_debug_minutes)} minutes')

        # Show suggested mitigations
        from scripts.lib.lessons_analyzer.generator import infer_mitigations
        mitigations = pattern.suggested_mitigations or infer_mitigations(pattern)
        print()
        print('Suggested Mitigations:')
        for i, mit in enumerate(mitigations, 1):
            print(f'  {i}. {mit}')

        print()
        if pattern.status == 'PROMOTE':
            print(f"Ready to promote? Run: lessons-analyzer.py generate --pattern \"{pattern.pattern_name}\"")
        elif pattern.status == 'CANDIDATE':
            print('This pattern is a candidate for promotion. Consider more data before promoting.')
        else:
            print('This pattern needs more data or review before promotion.')

        return 0

    except PatternNotFoundError as e:
        print(f'[ERROR] Pattern not found: {e.pattern_name}')
        print()

        similar = analyzer.find_similar_patterns(args.pattern)
        if similar:
            print('Did you mean one of these?')
            for name in similar:
                print(f'  - {name}')
        else:
            print("Use 'lessons-analyzer.py extract' to see available patterns.")

        return 1
    except (DatabaseNotFoundError, NoSessionsFoundError, InsufficientDataError) as e:
        print(f'[ERROR] {e}')
        return 1
    finally:
        analyzer.close()


def cmd_generate(args) -> int:
    """Handle generate command."""
    analyzer = LessonsAnalyzer()

    try:
        pattern = analyzer.review(args.pattern)

        entry = analyzer.generate_entry(pattern, include_sessions=args.include_sessions)

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(entry)
            print(f'[OK] Entry written to {output_path}')
        else:
            print(entry)

        return 0

    except PatternNotFoundError as e:
        print(f'[ERROR] Pattern not found: {e.pattern_name}')

        similar = analyzer.find_similar_patterns(args.pattern)
        if similar:
            print()
            print('Did you mean one of these?')
            for name in similar:
                print(f'  - {name}')

        return 1
    except (DatabaseNotFoundError, NoSessionsFoundError, InsufficientDataError) as e:
        print(f'[ERROR] {e}')
        return 1
    finally:
        analyzer.close()


def cmd_stats(args) -> int:
    """Handle stats command."""
    analyzer = LessonsAnalyzer()

    try:
        since = None
        if args.since:
            since = datetime.fromisoformat(args.since)
            if since.tzinfo is None:
                since = since.replace(tzinfo=UTC)
        else:
            since = datetime.now(UTC) - timedelta(days=30)

        stats = analyzer.get_stats(since=since)

        print(f'Debug Session Statistics ({stats["analysis_period"]["start"]} to {stats["analysis_period"]["end"]})')
        print('=' * 60)
        print()

        print('Overall:')
        print(f'  Total sessions: {stats["total_sessions"]}')
        for outcome, count in stats['by_outcome'].items():
            pct = int(count / stats['total_sessions'] * 100) if stats['total_sessions'] > 0 else 0
            print(f'  {outcome.title()}: {count} ({pct}%)')

        if stats['by_category']:
            print()
            print('By Category:')
            for cat, data in stats['by_category'].items():
                print(f'  {cat}: {data["count"]} sessions (avg {data["avg_duration"]} min)')

        if stats['top_tags']:
            print()
            print('Top Tags:')
            tags_str = ', '.join(f'{t["tag"]} ({t["count"]})' for t in stats['top_tags'][:10])
            print(f'  {tags_str}')

        print()
        print('Learning Efficiency:')
        print(f'  Patterns detected: {stats["patterns_detected"]}')
        print(f'  Patterns ready to promote: {stats["patterns_promoted"]}')
        print(f'  Patterns as candidates: {stats["patterns_candidates"]}')
        if stats['avg_duration_minutes']:
            print(f'  Avg debug time: {stats["avg_duration_minutes"]} minutes')

        return 0

    except DatabaseNotFoundError as e:
        print(f'[ERROR] {e}')
        return 1
    except AnalyzerError as e:
        print(f'[ERROR] {e}')
        return 1
    finally:
        analyzer.close()


def main():
    parser = argparse.ArgumentParser(
        description='LESSONS.md Analyzer - Extract patterns from debug sessions',
        epilog='Part of Wave 3 P1: Protocol Enhancements (Issue #238)',
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Analyze sessions and extract patterns')
    extract_parser.add_argument('--min-frequency', type=int, default=2, help='Minimum occurrence count')
    extract_parser.add_argument('--min-score', type=float, default=0.7, help='Minimum confidence score')
    extract_parser.add_argument('--since', help='Start date (ISO format)')
    extract_parser.add_argument('--until', help='End date (ISO format)')
    extract_parser.add_argument('--category', help='Filter by pattern category')
    extract_parser.add_argument(
        '--format', '-f', default='table', choices=['table', 'json', 'markdown'], help='Output format'
    )
    extract_parser.add_argument('--limit', '-l', type=int, default=10, help='Max patterns to show')

    # Review command
    review_parser = subparsers.add_parser('review', help='Deep-dive on a specific pattern')
    review_parser.add_argument('--pattern', '-p', required=True, help='Pattern name to review')

    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Create LESSONS.md formatted entry')
    generate_parser.add_argument('--pattern', '-p', required=True, help='Pattern name to generate entry for')
    generate_parser.add_argument('--output', '-o', help='Write to file path (stdout if not specified)')
    generate_parser.add_argument('--include-sessions', type=int, default=3, help='Number of example sessions')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show pattern statistics')
    stats_parser.add_argument('--since', help='Start date (ISO format)')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    # Dispatch to command handler
    handlers = {
        'extract': cmd_extract,
        'review': cmd_review,
        'generate': cmd_generate,
        'stats': cmd_stats,
    }

    return handlers[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
