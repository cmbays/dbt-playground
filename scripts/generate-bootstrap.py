#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich"]
# ///
"""
Generate Bootstrap - Quick resume context generator.

Creates CONTEXT_BOOTSTRAP.md for rapid session resume.
Uses Anchor/Orientation/Momentum structure for cognitive efficiency.

Usage:
    uv run scripts/generate-bootstrap.py                    # Generate bootstrap
    uv run scripts/generate-bootstrap.py --output=stdout    # Print to stdout
    uv run scripts/generate-bootstrap.py --include-events   # Include recent events
"""

import argparse
import contextlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from rich.console import Console

console = Console()

# Paths
WORKFLOW_HISTORY_DIR = Path('temp/WORKFLOW_HISTORY')
EVENTS_FILE = WORKFLOW_HISTORY_DIR / 'events.jsonl'
BOOTSTRAP_FILE = Path('temp/CONTEXT_BOOTSTRAP.md')


def run_git(cmd: list[str]) -> str:
    """Run git command and return output."""
    result = subprocess.run(
        ['git'] + cmd,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ''


def get_branch_name() -> str:
    """Get current git branch name."""
    return run_git(['branch', '--show-current']) or 'HEAD'


def derive_phase(branch: str) -> str:
    """Derive workflow phase from branch name."""
    if branch in ('main', 'master'):
        return 'MAINLINE'
    if branch.startswith('feat/'):
        return 'DEVELOPMENT'
    if branch.startswith('fix/'):
        return 'BUGFIX'
    if branch.startswith('docs/'):
        return 'DOCUMENTATION'
    if branch.startswith('refactor/'):
        return 'REFACTORING'
    if branch.startswith('test/'):
        return 'TESTING'
    if branch.startswith('chore/'):
        return 'MAINTENANCE'
    return 'DEVELOPMENT'


def get_last_commit() -> tuple[str, str, str, int]:
    """Get last commit info: message, sha, time_since, files_changed."""
    # Get commit info
    result = subprocess.run(
        ['git', 'log', '-1', '--format=%s|%h|%aI'],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return 'No commits', 'N/A', 'N/A', 0

    parts = result.stdout.strip().split('|')
    if len(parts) < 3:
        return result.stdout.strip(), 'N/A', 'N/A', 0

    message, sha, timestamp_str = parts[0], parts[1], parts[2]

    # Calculate time since
    try:
        commit_time = datetime.fromisoformat(timestamp_str)
        now = datetime.now(commit_time.tzinfo)
        delta = now - commit_time

        total_minutes = int(delta.total_seconds() // 60)
        if total_minutes < 60:
            time_since = f'{total_minutes}m ago'
        elif total_minutes < 1440:
            hours = total_minutes // 60
            time_since = f'{hours}h ago'
        else:
            days = total_minutes // 1440
            time_since = f'{days}d ago'
    except (ValueError, TypeError):
        time_since = 'N/A'

    # Get files changed
    stat_result = subprocess.run(
        ['git', 'show', '--stat', '--format=', '-1'],
        capture_output=True,
        text=True,
    )
    files_changed = 0
    if stat_result.returncode == 0:
        lines = [line for line in stat_result.stdout.split('\n') if line.strip()]
        files_changed = max(0, len(lines) - 1)  # Last line is summary

    return message, sha, time_since, files_changed


def get_uncommitted_status() -> tuple[int, int]:
    """Get count of staged and unstaged changes."""
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 0, 0

    staged = 0
    unstaged = 0
    for line in result.stdout.split('\n'):
        if not line:
            continue
        if line[0] in 'MADRCU':
            staged += 1
        if line[1] in 'MADRCU':
            unstaged += 1

    return staged, unstaged


def get_today_stats() -> tuple[int, int]:
    """Get commits and agent-assisted percentage for today."""
    result = subprocess.run(
        ['git', 'log', '--since=midnight', '--format=%B%x00'],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 0, 0

    commits = [c for c in result.stdout.split('\x00') if c.strip()]
    total = len(commits)
    agent = sum(1 for c in commits if 'Co-Authored-By:' in c)

    pct = int((agent / total) * 100) if total > 0 else 0
    return total, pct


def infer_next_action(branch: str, staged: int, unstaged: int) -> str:
    """Infer next action based on state."""
    if unstaged > 0:
        return f'Stage or stash {unstaged} modified file(s)'
    if staged > 0:
        return f'Commit {staged} staged file(s)'

    # Check if ahead of origin
    ahead = run_git(['rev-list', '--count', f'origin/{branch}..HEAD'])
    if ahead and ahead != '0':
        return f'Push {ahead} commit(s) to origin'

    # Check for open PR
    if branch not in ('main', 'master'):
        pr_result = subprocess.run(
            ['gh', 'pr', 'view', branch, '--json', 'state,reviewDecision'],
            capture_output=True,
            text=True,
        )
        if pr_result.returncode == 0:
            pr_data = json.loads(pr_result.stdout)
            if pr_data.get('state') == 'OPEN':
                decision = pr_data.get('reviewDecision', '')
                if decision == 'APPROVED':
                    return 'Merge approved PR'
                if decision == 'CHANGES_REQUESTED':
                    return 'Address PR review feedback'
                return 'Await PR review or follow up'
        else:
            return 'Create PR for this branch'

    return 'Continue development'


def get_recent_events(limit: int = 5) -> list[dict]:
    """Get recent events from events.jsonl."""
    if not EVENTS_FILE.exists():
        return []

    events = []
    with open(EVENTS_FILE) as f:
        for line in f:
            if line.strip():
                with contextlib.suppress(json.JSONDecodeError):
                    events.append(json.loads(line))

    return events[-limit:]


def generate_bootstrap(include_events: bool = False) -> str:
    """Generate CONTEXT_BOOTSTRAP.md content."""
    now = datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')
    branch = get_branch_name()
    phase = derive_phase(branch)
    message, sha, time_since, files_changed = get_last_commit()
    staged, unstaged = get_uncommitted_status()
    commits_today, agent_pct = get_today_stats()
    next_action = infer_next_action(branch, staged, unstaged)

    lines = [
        '# Context Bootstrap',
        '',
        f'*Auto-generated: {now}*',
        '',
        '---',
        '',
        '## Anchor (Where Am I?)',
        '',
        f'- **Branch**: `{branch}`',
        f'- **Phase**: {phase}',
        '- **Health**: --/100 *(not yet computed)*',
        '',
        '---',
        '',
        '## Orientation (What Was I Doing?)',
        '',
        f'- **Last commit**: `{sha}` - "{message}"',
        f'- **Time since**: {time_since}',
        f'- **Files changed**: {files_changed}',
        '',
        '### Working Tree Status',
        '',
        f'- Staged: {staged} file(s)',
        f'- Unstaged: {unstaged} file(s)',
        '',
        "### Today's Progress",
        '',
        f'- Commits: {commits_today}',
        f'- Agent-assisted: {agent_pct}%',
        '',
        '---',
        '',
        "## Momentum (What's Next?)",
        '',
        f'**Next Action**: {next_action}',
        '',
    ]

    if include_events:
        events = get_recent_events(5)
        if events:
            lines.extend(
                [
                    '---',
                    '',
                    '## Recent Events',
                    '',
                ]
            )
            for event in events:
                event_type = event.get('event_type', 'unknown')
                timestamp = event.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.strftime('%H:%M')
                    except ValueError:
                        pass
                lines.append(f'- `{timestamp}` **{event_type}**')
            lines.append('')

    lines.extend(
        [
            '---',
            '',
            '*Cognitive Resume Protocol: 5-second orientation*',
        ]
    )

    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Generate quick resume context',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--output',
        choices=['file', 'stdout'],
        default='file',
        help='Output destination (default: file)',
    )
    parser.add_argument(
        '--include-events',
        action='store_true',
        help='Include recent events from events.jsonl',
    )

    args = parser.parse_args()

    content = generate_bootstrap(include_events=args.include_events)

    if args.output == 'stdout':
        print(content)
    else:
        BOOTSTRAP_FILE.parent.mkdir(parents=True, exist_ok=True)
        BOOTSTRAP_FILE.write_text(content)
        console.print(f'[green]Bootstrap generated: {BOOTSTRAP_FILE}[/green]')

    return 0


if __name__ == '__main__':
    sys.exit(main())
