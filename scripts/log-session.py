#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Session logging script for Agent Memory System.

Usage:
    uv run scripts/log-session.py                    # Interactive mode
    uv run scripts/log-session.py --task "Task"      # Quick mode
    uv run scripts/log-session.py --help             # Show help

Implements:
    - GAP-1: task_id field for FS2 correlation
    - GAP-5: events.jsonl emission for FS5 consumption

Part of FS1: Agent Memory & Learning System (Epic #143)
Issues: #150, #151, #152
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

# Configure logging
logger = logging.getLogger(__name__)

# Add scripts directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent))

from lib.memory_utils import get_memory_dir


class SessionEntry(NamedTuple):
    """Validated session log entry."""

    timestamp: datetime
    task: str
    outcome: str
    files: list[str]
    decisions: list[tuple[str, str, str]]  # (decision, rationale, affects)
    learnings: list[str]
    improvements: list[str]
    issue: str
    pr: str
    task_id: str


def get_today_log() -> Path:
    """Get path to today's log file."""
    memory_dir = get_memory_dir()
    today = datetime.now(UTC).strftime('%Y-%m-%d')
    return memory_dir / f'{today}.md'


def detect_task_id() -> str | None:
    """Detect task_id from WORKFLOW_STATE.md if available."""
    try:
        workflow_state = Path('temp/WORKFLOW_STATE.md')
        if not workflow_state.exists():
            return None

        content = workflow_state.read_text()
        # Look for task reference patterns
        match = re.search(r'(?:Task ID|TASK)[:\s]+([A-Z]+-\d+)', content, re.IGNORECASE)
        return match.group(1) if match else None
    except (OSError, UnicodeDecodeError, re.error):
        return None


def get_modified_files() -> list[str]:
    """Get list of modified files from git status."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1'],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except subprocess.CalledProcessError as e:
        logger.warning('git diff failed: %s', e.stderr or e)
        return []
    except subprocess.SubprocessError as e:
        logger.warning('subprocess error running git: %s', e)
        return []
    except FileNotFoundError:
        logger.warning('git command not found')
        return []
    except OSError as e:
        logger.warning('OS error running git: %s', e)
        return []


def validate_entry(entry: SessionEntry) -> list[str]:
    """Validate entry against schema. Returns list of warnings (non-blocking)."""
    warnings = []

    if not entry.task:
        warnings.append('[WARN] Task description is empty')

    if entry.outcome not in ('SUCCESS', 'FAILURE', 'PARTIAL'):
        warnings.append(f"[WARN] Unknown outcome '{entry.outcome}', using as-is")

    if entry.task_id and not re.match(r'^[A-Z]+-\d+$', entry.task_id):
        warnings.append(f"[WARN] Task ID '{entry.task_id}' has unusual format")

    return warnings


def format_markdown(entry: SessionEntry) -> str:
    """Format entry as markdown."""
    lines = [
        f'## [{entry.timestamp.replace(tzinfo=None).isoformat(timespec="seconds")}] Task: {entry.task}',
        '',
    ]

    if entry.task_id:
        lines.append(f'**Task ID**: {entry.task_id}')

    lines.append(f'**Outcome**: {entry.outcome}')

    if entry.files:
        if len(entry.files) <= 5:
            lines.append(f'**Files Modified**: {len(entry.files)} ({", ".join(entry.files)})')
        else:
            lines.append(f'**Files Modified**: {len(entry.files)}')

    lines.extend(['', '**Key Decisions**:'])
    if entry.decisions:
        for decision, rationale, affects in entry.decisions:
            line = f'- {decision}'
            if rationale:
                line += f': {rationale}'
            if affects:
                line += f' (affects: {affects})'
            lines.append(line)
    else:
        lines.append('- None documented')

    lines.extend(['', '**Learnings**:'])
    if entry.learnings:
        for learning in entry.learnings:
            lines.append(f'- {learning}')
    else:
        lines.append('- None documented')

    lines.extend(['', '**Would Do Differently**:'])
    if entry.improvements:
        for improvement in entry.improvements:
            lines.append(f'- {improvement}')
    else:
        lines.append('- Nothing noted')

    lines.extend(['', '**Related**:'])
    related_parts = []
    if entry.issue:
        related_parts.append(f'Issue: #{entry.issue}')
    if entry.pr:
        related_parts.append(f'PR: #{entry.pr}')
    lines.append(f'- {" | ".join(related_parts)}' if related_parts else '- None')

    lines.extend(['', '---', ''])

    return '\n'.join(lines)


def emit_event(entry: SessionEntry) -> None:
    """Emit event to events.jsonl for FS5 consumption (GAP-5)."""
    memory_dir = get_memory_dir()
    events_file = memory_dir / 'events.jsonl'

    event = {
        'timestamp': entry.timestamp.astimezone(UTC).isoformat(),
        'event': 'session_logged',
        'version': '1.0',
        'data': {
            'task': entry.task,
            'task_id': entry.task_id or None,
            'outcome': entry.outcome,
            'files_modified': len(entry.files),
            'decisions_count': len(entry.decisions),
            'learnings_count': len(entry.learnings),
            'improvements_count': len(entry.improvements),
            'related_issue': f'#{entry.issue}' if entry.issue else None,
            'related_pr': f'#{entry.pr}' if entry.pr else None,
        },
    }

    with open(events_file, 'a') as f:
        f.write(json.dumps(event) + '\n')


def prompt_input(prompt: str, default: str = '') -> str:
    """Prompt for input with optional default."""
    if default:
        value = input(f'{prompt} [{default}]: ').strip()
        return value if value else default
    return input(f'{prompt}: ').strip()


def prompt_list(prompt: str) -> list[str]:
    """Prompt for a list of items."""
    print(f'{prompt} (enter empty line when done):')
    items = []
    while True:
        item = input(f'  {len(items) + 1}. ').strip()
        if not item:
            break
        items.append(item)
    return items


def gather_full() -> SessionEntry:
    """Gather entry data interactively (full mode)."""
    print('\n=== Session Log Entry ===\n')

    task = prompt_input('Task description')

    outcome = prompt_input('Outcome (SUCCESS/FAILURE/PARTIAL)', 'SUCCESS').upper()
    if outcome not in ('SUCCESS', 'FAILURE', 'PARTIAL'):
        print(f'[WARN] Unknown outcome "{outcome}", using as-is')

    files = get_modified_files()
    if files:
        print(f'\nDetected {len(files)} modified files:')
        for f in files[:5]:
            print(f'  - {f}')
        if len(files) > 5:
            print(f'  ... and {len(files) - 5} more')
        if input('Use these files? [Y/n]: ').strip().lower() == 'n':
            files = []

    detected_task_id = detect_task_id()
    if detected_task_id:
        task_id = prompt_input('\nTask ID', detected_task_id)
    else:
        task_id = prompt_input('\nBacklog.md task ID (e.g., TASK-42, or empty)')

    print('\nKey decisions (format: decision | rationale | affects):')
    decisions = []
    while True:
        decision_input = input(f'  {len(decisions) + 1}. ').strip()
        if not decision_input:
            break
        parts = [p.strip() for p in decision_input.split('|')]
        if len(parts) >= 2:
            decisions.append((parts[0], parts[1], parts[2] if len(parts) > 2 else ''))
        else:
            decisions.append((decision_input, '', ''))

    learnings = prompt_list('\nLearnings')
    improvements = prompt_list('\nWould do differently')

    issue = prompt_input('\nRelated issue number (or empty)')
    pr = prompt_input('Related PR number (or empty)')

    return SessionEntry(
        timestamp=datetime.now(UTC),
        task=task,
        outcome=outcome,
        files=files,
        decisions=decisions,
        learnings=learnings,
        improvements=improvements,
        issue=issue,
        pr=pr,
        task_id=task_id,
    )


def gather_quick(task: str, outcome: str = 'SUCCESS', task_id: str = '') -> SessionEntry:
    """Gather entry with minimal input (quick mode)."""
    return SessionEntry(
        timestamp=datetime.now(UTC),
        task=task,
        outcome=outcome,
        files=get_modified_files(),
        decisions=[],
        learnings=[],
        improvements=[],
        issue='',
        pr='',
        task_id=task_id or detect_task_id() or '',
    )


def main():
    parser = argparse.ArgumentParser(
        description='Log session entry to memory',
        epilog='Part of FS1: Agent Memory & Learning System',
    )
    parser.add_argument('--task', '-t', help='Task description (enables quick mode)')
    parser.add_argument(
        '--outcome',
        '-o',
        default='SUCCESS',
        choices=['SUCCESS', 'FAILURE', 'PARTIAL'],
        help='Task outcome (default: SUCCESS)',
    )
    parser.add_argument('--task-id', '-i', help='Backlog.md task ID (e.g., TASK-42)')
    args = parser.parse_args()

    try:
        # Gather entry based on mode
        if args.task:
            entry = gather_quick(args.task, args.outcome, args.task_id or '')
        else:
            entry = gather_full()

        # Validate (non-blocking warnings)
        warnings = validate_entry(entry)
        for warning in warnings:
            print(warning)

        # Write markdown
        log_file = get_today_log()
        markdown = format_markdown(entry)
        with open(log_file, 'a') as f:
            f.write(markdown)

        # Emit event for FS5 (GAP-5)
        emit_event(entry)

        print(f'\n[OK] Entry logged to {log_file}')
        print('[OK] Event emitted to memory/events.jsonl')

    except KeyboardInterrupt:
        print('\nCancelled')
        return 1
    except FileNotFoundError as e:
        print(f'Error: {e}')
        return 1
    except PermissionError as e:
        print(f'Permission error: {e}')
        return 1
    except OSError as e:
        print(f'OS error: {e}')
        return 1
    else:
        return 0

    return 1  # Fallback for any unhandled path


if __name__ == '__main__':
    exit(main())
