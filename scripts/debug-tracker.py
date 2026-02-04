#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.2.0", "rich>=13.0.0"]
# ///
"""
Debug Session Tracker CLI - WAVE3-020

Track and persist debug sessions for compound learning.
Captures debugging workflows following the 7-step Debug Agent protocol.

Usage:
    uv run scripts/debug-tracker.py start --bug "Race condition" --tags "async,queue"
    uv run scripts/debug-tracker.py log --phase "1-reproduce" --findings "Bug confirmed"
    uv run scripts/debug-tracker.py end --root-cause "Missing lock" --fix-time "45m"
    uv run scripts/debug-tracker.py query --since "2026-02-01"
    uv run scripts/debug-tracker.py status

Part of Wave 3 P1: Protocol Enhancements (Issue #237)
"""

import argparse
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add scripts directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib.debug_session import (
    DebugSessionError,
    DebugSessionTracker,
    NoActiveSessionError,
    SessionAlreadyActiveError,
)
from scripts.lib.debug_session.models import PROTOCOL_PHASES
from scripts.lib.debug_session.utils import format_duration, format_time_ago, truncate_text


def cmd_start(args) -> int:
    """Handle start command."""
    tracker = DebugSessionTracker()

    try:
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else []

        session_id = tracker.start_session(
            bug_description=args.bug,
            tags=tags,
            severity=args.severity,
            context=args.context,
            force=args.force,
        )

        print(f'Session started: {session_id}')
        print(f'Bug: {args.bug}')
        if tags:
            print(f'Tags: {", ".join(tags)}')
        print()
        print("Use 'debug-tracker.py log' to add debug steps.")

        return 0

    except SessionAlreadyActiveError as e:
        print(f'[ERROR] {e}')
        return 1
    except DebugSessionError as e:
        print(f'[ERROR] {e}')
        return 1
    finally:
        tracker.close()


def cmd_log(args) -> int:
    """Handle log command."""
    tracker = DebugSessionTracker()

    try:
        step_number = tracker.log_step(
            phase=args.phase,
            findings=args.findings,
            evidence=args.evidence,
            step_number=args.step,
        )

        print(f'Step {step_number} logged ({args.phase}):')
        print(f'  Findings: {args.findings}')
        if args.evidence:
            print(f'  Evidence: {args.evidence}')

        status = tracker.get_status()
        if status['active']:
            print(f'\nSession {status["session"].session_id}: {status["session"].step_count} step(s) logged')

        return 0

    except NoActiveSessionError as e:
        print(f'[ERROR] {e}')
        print("Use 'debug-tracker.py start' to begin a session.")
        return 1
    except ValueError as e:
        print(f'[ERROR] {e}')
        print(f'\nValid phases:')
        for phase, desc in PROTOCOL_PHASES.items():
            print(f'  {phase}: {desc}')
        return 1
    except DebugSessionError as e:
        print(f'[ERROR] {e}')
        return 1
    finally:
        tracker.close()


def cmd_end(args) -> int:
    """Handle end command."""
    tracker = DebugSessionTracker()

    try:
        session = tracker.end_session(
            root_cause=args.root_cause,
            fix_time=args.fix_time,
            resolution=args.resolution,
            outcome=args.outcome,
        )

        print(f'Session {session.session_id} completed.')
        print()
        print('Summary:')
        print(f'  Duration: {format_duration(session.duration_minutes)}')
        print(f'  Steps: {session.step_count}')
        print(f'  Root Cause: {session.root_cause}')
        print(f'  Outcome: {session.outcome.upper()}')
        print()
        print("Session logged to database. Run 'lessons-analyzer.py' to check for patterns.")

        return 0

    except NoActiveSessionError as e:
        print(f'[ERROR] {e}')

        # Show recent sessions for reference
        status = tracker.get_status()
        if status.get('recent_sessions'):
            print('\nRecent sessions:')
            for s in status['recent_sessions'][:3]:
                duration = format_duration(s.duration_minutes) if s.duration_minutes else 'N/A'
                print(f'  {s.session_id}: {truncate_text(s.bug_description, 40)} ({s.outcome}, {duration})')

        return 1
    except ValueError as e:
        print(f'[ERROR] {e}')
        return 1
    except DebugSessionError as e:
        print(f'[ERROR] {e}')
        return 1
    finally:
        tracker.close()


def cmd_query(args) -> int:
    """Handle query command."""
    tracker = DebugSessionTracker()

    try:
        # Parse dates
        since = None
        until = None

        if args.since:
            since = datetime.fromisoformat(args.since)
            if since.tzinfo is None:
                since = since.replace(tzinfo=UTC)
        else:
            # Default: 7 days ago
            since = datetime.now(UTC) - timedelta(days=7)

        if args.until:
            until = datetime.fromisoformat(args.until)
            if until.tzinfo is None:
                until = until.replace(tzinfo=UTC)

        # Parse tags
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else None

        sessions = tracker.query_sessions(
            since=since,
            until=until,
            pattern=args.pattern,
            tags=tags,
            outcome=args.outcome,
            limit=args.limit,
        )

        if args.format == 'json':
            import json

            output = []
            for s in sessions:
                output.append({
                    'session_id': s.session_id,
                    'date': s.start_time.strftime('%Y-%m-%d'),
                    'bug_description': s.bug_description,
                    'root_cause': s.root_cause,
                    'duration_minutes': s.duration_minutes,
                    'outcome': s.outcome,
                    'tags': s.tags,
                })
            print(json.dumps(output, indent=2))
        else:
            # Table format
            print('Sessions matching query:')
            print()

            if not sessions:
                print('  No sessions found.')
            else:
                # Header
                print(f'{"ID":<22} | {"Date":<10} | {"Bug Description":<28} | {"Root Cause":<25} | {"Duration":<8} | {"Outcome":<10}')
                print('-' * 22 + '-+-' + '-' * 10 + '-+-' + '-' * 28 + '-+-' + '-' * 25 + '-+-' + '-' * 8 + '-+-' + '-' * 10)

                for s in sessions:
                    date_str = s.start_time.strftime('%Y-%m-%d')
                    duration = format_duration(s.duration_minutes) if s.duration_minutes else 'N/A'
                    bug = truncate_text(s.bug_description, 26)
                    cause = truncate_text(s.root_cause or '', 23)

                    print(f'{s.session_id:<22} | {date_str:<10} | {bug:<28} | {cause:<25} | {duration:<8} | {s.outcome:<10}')

                print()
                print(f'{len(sessions)} sessions found')

        return 0

    except ValueError as e:
        print(f'[ERROR] Invalid date format: {e}')
        print('Use ISO format: YYYY-MM-DD')
        return 1
    except DebugSessionError as e:
        print(f'[ERROR] {e}')
        return 1
    finally:
        tracker.close()


def cmd_status(args) -> int:
    """Handle status command."""
    tracker = DebugSessionTracker()

    try:
        status = tracker.get_status()

        if status['active']:
            session = status['session']
            elapsed = status['elapsed_seconds']
            steps = status['steps']

            print(f'Current Session: {session.session_id}')
            print(f'  Bug: {session.bug_description}')
            print(f'  Started: {session.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")} ({format_time_ago(elapsed)})')
            print(f'  Steps: {session.step_count}')
            if status['last_phase']:
                print(f'  Last Phase: {status["last_phase"]}')
            if session.tags:
                print(f'  Tags: {", ".join(session.tags)}')

            if steps:
                print()
                print('Recent steps:')
                for step in steps[-3:]:
                    print(f'  {step.step_number}. [{step.protocol_phase}] {truncate_text(step.findings, 50)}')

        else:
            print('No active session.')
            print()

            recent = status.get('recent_sessions', [])
            if recent:
                print('Recent sessions:')
                for s in recent[:5]:
                    duration = format_duration(s.duration_minutes) if s.duration_minutes else 'N/A'
                    print(f'  {s.session_id}: {truncate_text(s.bug_description, 40)} ({s.outcome}, {duration})')

            print()
            print("Use 'debug-tracker.py start' to begin a new session.")

        return 0

    except DebugSessionError as e:
        print(f'[ERROR] {e}')
        return 1
    finally:
        tracker.close()


def main():
    parser = argparse.ArgumentParser(
        description='Debug Session Tracker - Track and persist debug sessions',
        epilog='Part of Wave 3 P1: Protocol Enhancements (Issue #237)',
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Start command
    start_parser = subparsers.add_parser('start', help='Begin a new debug session')
    start_parser.add_argument('--bug', '-b', required=True, help='Bug description')
    start_parser.add_argument('--tags', '-t', help='Comma-separated tags')
    start_parser.add_argument(
        '--severity', '-s', default='medium', choices=['high', 'medium', 'low'], help='Bug severity'
    )
    start_parser.add_argument('--context', '-c', help='Initial file:line context')
    start_parser.add_argument(
        '--force', '-f', action='store_true', help='Force start (ends any active session)'
    )

    # Log command
    log_parser = subparsers.add_parser('log', help='Add a step to the current session')
    log_parser.add_argument(
        '--phase',
        '-p',
        required=True,
        choices=list(PROTOCOL_PHASES.keys()),
        help='Protocol phase',
    )
    log_parser.add_argument('--findings', '-f', required=True, help='What was discovered')
    log_parser.add_argument('--evidence', '-e', help='Path to supporting evidence')
    log_parser.add_argument('--step', '-s', type=int, help='Specific step number')

    # End command
    end_parser = subparsers.add_parser('end', help='Complete the current session')
    end_parser.add_argument('--root-cause', '-r', required=True, help='The identified root cause')
    end_parser.add_argument('--resolution', help='How it was fixed')
    end_parser.add_argument('--fix-time', '-t', required=True, help='Time spent (e.g., "45m", "1h 30m")')
    end_parser.add_argument(
        '--outcome',
        '-o',
        default='resolved',
        choices=['resolved', 'escalated', 'inconclusive'],
        help='Session outcome',
    )

    # Query command
    query_parser = subparsers.add_parser('query', help='Search and filter sessions')
    query_parser.add_argument('--since', help='Start date (ISO format)')
    query_parser.add_argument('--until', help='End date (ISO format)')
    query_parser.add_argument('--pattern', '-p', help='Pattern in root cause or description')
    query_parser.add_argument('--tags', '-t', help='Filter by tags (comma-separated)')
    query_parser.add_argument('--outcome', '-o', choices=['resolved', 'escalated', 'inconclusive'])
    query_parser.add_argument('--limit', '-l', type=int, default=20, help='Max results')
    query_parser.add_argument(
        '--format', '-f', default='table', choices=['table', 'json'], help='Output format'
    )

    # Status command
    subparsers.add_parser('status', help='Show current session state')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    # Dispatch to command handler
    handlers = {
        'start': cmd_start,
        'log': cmd_log,
        'end': cmd_end,
        'query': cmd_query,
        'status': cmd_status,
    }

    return handlers[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
