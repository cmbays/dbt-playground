#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.2.0", "rich>=13.0.0"]
# ///
"""
Debug CLI - WAVE3-022

Unified debug command interface for the 7-step Debug Protocol.
Integrates with Session Tracker for persistent debugging workflows.

Usage:
    uv run scripts/debug-cli.py start "Bug description" [--severity high] [--tags a,b]
    uv run scripts/debug-cli.py step 1-reproduce "Findings"
    uv run scripts/debug-cli.py end "Root cause" --time 45m
    uv run scripts/debug-cli.py status
    uv run scripts/debug-cli.py history [--since 2026-02-01]

Part of Wave 3 P2: Developer UX Commands (Issue #244)
"""

import argparse
import json
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Optional

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

# Console styling
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


def print_header(title: str) -> None:
    """Print styled header."""
    if RICH_AVAILABLE:
        console.print(f"\n[bold blue]{title}[/bold blue]")
        console.print("=" * len(title))
    else:
        print(f"\n{title}")
        print("=" * len(title))


def print_success(message: str) -> None:
    """Print success message."""
    if RICH_AVAILABLE:
        console.print(f"[green]{message}[/green]")
    else:
        print(message)


def print_error(message: str) -> None:
    """Print error message."""
    if RICH_AVAILABLE:
        console.print(f"[red][ERROR] {message}[/red]")
    else:
        print(f"[ERROR] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    if RICH_AVAILABLE:
        console.print(f"[dim]{message}[/dim]")
    else:
        print(message)


def generate_trace_id() -> str:
    """Generate a trace ID for observability correlation."""
    return str(uuid.uuid4())[:16]


def emit_observability_event(
    event_type: str,
    session_id: str,
    trace_id: str,
    data: dict,
) -> None:
    """Emit observability event for tracing integration.

    Events are logged to temp/debug_traces.jsonl for observability integration.
    """
    # Find project root
    project_root = None
    for parent in [Path.cwd(), *Path.cwd().parents]:
        if (parent / 'CLAUDE.md').exists():
            project_root = parent
            break

    if project_root is None:
        return  # Silently skip if not in project

    traces_dir = project_root / 'temp'
    traces_dir.mkdir(exist_ok=True)
    traces_file = traces_dir / 'debug_traces.jsonl'

    event = {
        'timestamp': datetime.now(UTC).isoformat(),
        'event_type': event_type,
        'trace_id': trace_id,
        'session_id': session_id,
        'span_name': f'vibe-code-debug/{event_type}',
        'data': data,
    }

    try:
        with open(traces_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')
    except OSError:
        pass  # Best effort


def cmd_start(args) -> int:
    """Handle start command."""
    tracker = DebugSessionTracker()

    try:
        # Parse tags
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else []

        # Generate trace ID for observability
        trace_id = args.trace_id or generate_trace_id()

        session_id = tracker.start_session(
            bug_description=args.bug,
            tags=tags,
            severity=args.severity,
            context=args.context,
            force=args.force,
        )

        print_header("Debug Session Started")
        print(f"Session ID: {session_id}")
        print(f"Bug: {args.bug}")
        print(f"Severity: {args.severity}")
        if tags:
            print(f"Tags: {', '.join(tags)}")
        print(f"Trace ID: {trace_id}")

        print("\nProtocol Phases:")
        for phase, desc in PROTOCOL_PHASES.items():
            print(f"  {phase:<15} - {desc}")

        print_info("\nNext: Use '/debug step 1-reproduce \"findings\"' to log progress")

        # Emit observability event
        emit_observability_event(
            event_type='session_started',
            session_id=session_id,
            trace_id=trace_id,
            data={
                'bug_description': args.bug,
                'severity': args.severity,
                'tags': tags,
            },
        )

        # Store trace_id for correlation
        _store_trace_id(session_id, trace_id)

        return 0

    except SessionAlreadyActiveError as e:
        print_error(f"Session already active: {e.session_id}")
        print_info("Use --force to end current session and start new one")
        print_info("Or use '/debug status' to see current session")
        return 1
    except DebugSessionError as e:
        print_error(str(e))
        return 1
    finally:
        tracker.close()


def cmd_step(args) -> int:
    """Handle step command."""
    tracker = DebugSessionTracker()

    try:
        step_number = tracker.log_step(
            phase=args.phase,
            findings=args.findings,
            evidence=args.evidence,
        )

        status = tracker.get_status()
        session = status['session']
        elapsed = status['elapsed_seconds']
        steps = status['steps']

        print_header(f"Step {step_number} logged ({args.phase})")
        print(f"Findings: {args.findings}")
        if args.evidence:
            print(f"Evidence: {args.evidence}")

        print(f"\nSession: {session.session_id}")
        print(f"Duration so far: {format_time_ago(elapsed).replace(' ago', '')}")
        print(f"Steps logged: {len(steps)}/7")

        # Show phase checklist
        print("\nPhase Progress:")
        completed_phases = {s.protocol_phase for s in steps}
        suggested_next = None
        for phase in PROTOCOL_PHASES:
            if phase in completed_phases:
                print(f"  [x] {phase}")
            else:
                mark = "<- Suggested next" if suggested_next is None else ""
                if suggested_next is None:
                    suggested_next = phase
                print(f"  [ ] {phase}  {mark}")

        # Emit observability event
        trace_id = _load_trace_id(session.session_id)
        if trace_id:
            emit_observability_event(
                event_type=f'step_{args.phase}',
                session_id=session.session_id,
                trace_id=trace_id,
                data={
                    'step_number': step_number,
                    'phase': args.phase,
                    'findings_preview': args.findings[:100],
                },
            )

        return 0

    except NoActiveSessionError as e:
        print_error(str(e))
        print_info("Use '/debug start \"bug description\"' to begin a session")
        return 1
    except ValueError as e:
        print_error(str(e))
        print("\nValid phases:")
        for phase, desc in PROTOCOL_PHASES.items():
            print(f"  {phase}: {desc}")
        return 1
    except DebugSessionError as e:
        print_error(str(e))
        return 1
    finally:
        tracker.close()


def cmd_end(args) -> int:
    """Handle end command."""
    tracker = DebugSessionTracker()

    try:
        # Get trace_id before ending
        status = tracker.get_status()
        trace_id = None
        if status['active']:
            trace_id = _load_trace_id(status['session'].session_id)

        session = tracker.end_session(
            root_cause=args.root_cause,
            fix_time=args.time,
            resolution=args.resolution,
            outcome=args.outcome,
        )

        print_header("Debug Session Complete")
        print(f"Session ID: {session.session_id}")
        print(f"Duration: {format_duration(session.duration_minutes)}")
        print(f"Steps: {session.step_count}")
        print(f"Outcome: {session.outcome.upper()}")

        print("\nSummary:")
        print(f"  Bug: {truncate_text(session.bug_description, 50)}")
        print(f"  Root Cause: {session.root_cause}")
        if session.resolution:
            print(f"  Fix: {session.resolution}")

        print_success("\nEvent logged to memory/events.jsonl")
        print_success("Session saved to database")

        print_info("\nTip: Run 'lessons-analyzer.py extract' to check for patterns")

        # Emit observability event
        if trace_id:
            emit_observability_event(
                event_type='session_completed',
                session_id=session.session_id,
                trace_id=trace_id,
                data={
                    'duration_minutes': session.duration_minutes,
                    'step_count': session.step_count,
                    'outcome': session.outcome,
                    'root_cause': session.root_cause,
                },
            )
            _clear_trace_id(session.session_id)

        return 0

    except NoActiveSessionError as e:
        print_error(str(e))

        # Show recent sessions
        status = tracker.get_status()
        recent = status.get('recent_sessions', [])
        if recent:
            print("\nRecent sessions:")
            for s in recent[:3]:
                duration = format_duration(s.duration_minutes) if s.duration_minutes else 'N/A'
                print(f"  {s.session_id}: {truncate_text(s.bug_description, 40)} ({s.outcome}, {duration})")

        return 1
    except ValueError as e:
        print_error(str(e))
        return 1
    except DebugSessionError as e:
        print_error(str(e))
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

            print_header(f"Active Session: {session.session_id}")
            print(f"Bug: {session.bug_description}")
            print(f"Started: {format_time_ago(elapsed)}")
            print(f"Current Phase: {status.get('last_phase', 'none')}")
            print(f"Steps Logged: {len(steps)}")
            if session.tags:
                print(f"Tags: {', '.join(session.tags)}")

            if steps:
                print("\nRecent Steps:")
                for step in steps[-3:]:
                    print(f"  {step.step_number}. [{step.protocol_phase}] {truncate_text(step.findings, 50)}")

            print("\nCommands:")
            # Suggest next phase
            completed = {s.protocol_phase for s in steps}
            for phase in PROTOCOL_PHASES:
                if phase not in completed:
                    print(f"  /debug step {phase} \"findings\"")
                    break
            print(f"  /debug end \"root cause\" --time 45m")

        else:
            print_header("No Active Session")

            recent = status.get('recent_sessions', [])
            if recent:
                print("Recent sessions:")
                for s in recent[:5]:
                    duration = format_duration(s.duration_minutes) if s.duration_minutes else 'N/A'
                    print(f"  {s.session_id}: {truncate_text(s.bug_description, 40)} ({s.outcome}, {duration})")

            print_info("\nUse '/debug start \"bug description\"' to begin a new session")

        return 0

    except DebugSessionError as e:
        print_error(str(e))
        return 1
    finally:
        tracker.close()


def cmd_history(args) -> int:
    """Handle history command."""
    tracker = DebugSessionTracker()

    try:
        # Parse dates
        since = None
        if args.since:
            since = datetime.fromisoformat(args.since)
            if since.tzinfo is None:
                since = since.replace(tzinfo=UTC)
        else:
            since = datetime.now(UTC) - timedelta(days=7)

        # Parse tags
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else None

        sessions = tracker.query_sessions(
            since=since,
            pattern=args.pattern,
            tags=tags,
            outcome=args.outcome,
            limit=args.limit,
        )

        if args.format == 'json':
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
            days = (datetime.now(UTC) - since).days
            print_header(f"Debug Session History (last {days} days)")

            if not sessions:
                print("  No sessions found.")
                print_info("\nTry widening your search with --since or removing filters.")

            else:
                if RICH_AVAILABLE:
                    table = Table()
                    table.add_column("ID", style="cyan")
                    table.add_column("Date")
                    table.add_column("Bug")
                    table.add_column("Root Cause")
                    table.add_column("Duration")
                    table.add_column("Outcome")

                    for s in sessions:
                        duration = format_duration(s.duration_minutes) if s.duration_minutes else 'N/A'
                        outcome_style = "green" if s.outcome == "resolved" else "yellow"
                        table.add_row(
                            s.session_id,
                            s.start_time.strftime('%Y-%m-%d'),
                            truncate_text(s.bug_description, 28),
                            truncate_text(s.root_cause or '', 25),
                            duration,
                            f"[{outcome_style}]{s.outcome}[/{outcome_style}]",
                        )

                    console.print(table)

                else:
                    # Plain text table
                    print(f"{'ID':<22} | {'Date':<10} | {'Bug':<28} | {'Root Cause':<25} | {'Duration':<8} | {'Outcome':<10}")
                    print('-' * 115)

                    for s in sessions:
                        duration = format_duration(s.duration_minutes) if s.duration_minutes else 'N/A'
                        print(
                            f"{s.session_id:<22} | "
                            f"{s.start_time.strftime('%Y-%m-%d'):<10} | "
                            f"{truncate_text(s.bug_description, 26):<28} | "
                            f"{truncate_text(s.root_cause or '', 23):<25} | "
                            f"{duration:<8} | "
                            f"{s.outcome:<10}"
                        )

                print(f"\n{len(sessions)} sessions found")
                print_info("\nUse 'lessons-analyzer.py extract' to identify patterns")

        return 0

    except ValueError as e:
        print_error(f"Invalid date format: {e}")
        print_info("Use ISO format: YYYY-MM-DD")
        return 1
    except DebugSessionError as e:
        print_error(str(e))
        return 1
    finally:
        tracker.close()


def _get_trace_file() -> Optional[Path]:
    """Get path to trace ID storage file."""
    for parent in [Path.cwd(), *Path.cwd().parents]:
        if (parent / 'CLAUDE.md').exists():
            trace_file = parent / 'temp' / '.debug_trace_ids.json'
            trace_file.parent.mkdir(exist_ok=True)
            return trace_file
    return None


def _store_trace_id(session_id: str, trace_id: str) -> None:
    """Store trace ID for session correlation."""
    trace_file = _get_trace_file()
    if trace_file is None:
        return

    data = {}
    if trace_file.exists():
        try:
            data = json.loads(trace_file.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            data = {}

    data[session_id] = trace_id

    try:
        trace_file.write_text(json.dumps(data), encoding='utf-8')
    except OSError:
        pass


def _load_trace_id(session_id: str) -> Optional[str]:
    """Load trace ID for session."""
    trace_file = _get_trace_file()
    if trace_file is None or not trace_file.exists():
        return None

    try:
        data = json.loads(trace_file.read_text(encoding='utf-8'))
        return data.get(session_id)
    except (json.JSONDecodeError, OSError):
        return None


def _clear_trace_id(session_id: str) -> None:
    """Clear trace ID after session ends."""
    trace_file = _get_trace_file()
    if trace_file is None or not trace_file.exists():
        return

    try:
        data = json.loads(trace_file.read_text(encoding='utf-8'))
        data.pop(session_id, None)
        trace_file.write_text(json.dumps(data), encoding='utf-8')
    except (json.JSONDecodeError, OSError):
        pass


def main():
    parser = argparse.ArgumentParser(
        description='Debug CLI - 7-step Debug Protocol with Session Tracking',
        epilog='Part of Wave 3 P2: Developer UX Commands (Issue #244)',
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Start command
    start_parser = subparsers.add_parser('start', help='Begin a new debug session')
    start_parser.add_argument('bug', help='Bug description')
    start_parser.add_argument('--tags', '-t', help='Comma-separated tags')
    start_parser.add_argument(
        '--severity', '-s', default='medium',
        choices=['high', 'medium', 'low'],
        help='Bug severity (default: medium)',
    )
    start_parser.add_argument('--context', '-c', help='Initial file:line context')
    start_parser.add_argument('--trace-id', help='Custom trace ID for observability')
    start_parser.add_argument(
        '--force', '-f', action='store_true',
        help='Force start (ends any active session)',
    )

    # Step command
    step_parser = subparsers.add_parser('step', help='Log a debug step')
    step_parser.add_argument(
        'phase',
        choices=list(PROTOCOL_PHASES.keys()),
        help='Protocol phase',
    )
    step_parser.add_argument('findings', help='What was discovered')
    step_parser.add_argument('--evidence', '-e', help='Path to supporting evidence')

    # End command
    end_parser = subparsers.add_parser('end', help='Complete the current session')
    end_parser.add_argument('root_cause', help='The identified root cause')
    end_parser.add_argument('--time', '-t', required=True, help='Time spent (e.g., "45m", "1h 30m")')
    end_parser.add_argument('--resolution', '-r', help='How it was fixed')
    end_parser.add_argument(
        '--outcome', '-o', default='resolved',
        choices=['resolved', 'escalated', 'inconclusive'],
        help='Session outcome (default: resolved)',
    )

    # Status command
    subparsers.add_parser('status', help='Show current session state')

    # History command
    history_parser = subparsers.add_parser('history', help='Query debug session history')
    history_parser.add_argument('--since', help='Start date (ISO format, default: 7 days ago)')
    history_parser.add_argument('--pattern', '-p', help='Pattern in description or root cause')
    history_parser.add_argument('--tags', '-t', help='Filter by tags (comma-separated)')
    history_parser.add_argument(
        '--outcome', '-o',
        choices=['resolved', 'escalated', 'inconclusive'],
        help='Filter by outcome',
    )
    history_parser.add_argument('--limit', '-l', type=int, default=20, help='Max results (default: 20)')
    history_parser.add_argument(
        '--format', '-f', default='table',
        choices=['table', 'json'],
        help='Output format (default: table)',
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    # Dispatch to command handler
    handlers = {
        'start': cmd_start,
        'step': cmd_step,
        'end': cmd_end,
        'status': cmd_status,
        'history': cmd_history,
    }

    return handlers[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
