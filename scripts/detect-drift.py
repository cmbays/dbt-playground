#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich"]
# ///
"""
Detect Drift - Context drift detection.

Detects contradictions between context files and current reality.
Identifies stale CONTEXT_BOOTSTRAP.md and other context inconsistencies.

Usage:
    uv run scripts/detect-drift.py                    # Check for drift
    uv run scripts/detect-drift.py --fix             # Regenerate stale context
"""

import argparse
import contextlib
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

# Paths
BOOTSTRAP_FILE = Path('temp/CONTEXT_BOOTSTRAP.md')
WORKFLOW_STATE_FILE = Path('temp/WORKFLOW_STATE.md')


@dataclass
class DriftIssue:
    """A detected drift issue."""

    category: str
    severity: str  # "warning", "error"
    description: str
    actual: str
    expected: str
    fixable: bool


def run_git(cmd: list[str]) -> str:
    """Run git command and return output."""
    result = subprocess.run(
        ['git'] + cmd,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ''


def get_current_branch() -> str:
    """Get current git branch."""
    return run_git(['branch', '--show-current']) or 'main'


def derive_phase(branch: str) -> str:
    """Derive phase from branch name."""
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
    return 'DEVELOPMENT'


def get_last_commit_time() -> datetime | None:
    """Get timestamp of last commit."""
    result = run_git(['log', '-1', '--format=%aI'])
    if result:
        try:
            return datetime.fromisoformat(result)
        except ValueError:
            pass
    return None


def parse_bootstrap_file() -> dict | None:
    """Parse CONTEXT_BOOTSTRAP.md for key values."""
    if not BOOTSTRAP_FILE.exists():
        return None

    content = BOOTSTRAP_FILE.read_text()

    parsed = {
        'generated_at': None,
        'branch': None,
        'phase': None,
        'last_commit_sha': None,
    }

    # Extract generated timestamp
    match = re.search(r'\*Auto-generated:\s*([^*]+)\*', content)
    if match:
        with contextlib.suppress(ValueError):
            parsed['generated_at'] = datetime.fromisoformat(
                match.group(1).strip().replace(' UTC', '+00:00')
            )

    # Extract branch
    match = re.search(r'\*\*Branch\*\*:\s*`([^`]+)`', content)
    if match:
        parsed['branch'] = match.group(1)

    # Extract phase
    match = re.search(r'\*\*Phase\*\*:\s*(\w+)', content)
    if match:
        parsed['phase'] = match.group(1)

    # Extract last commit SHA
    match = re.search(r'\*\*Last commit\*\*:\s*`([^`]+)`', content)
    if match:
        parsed['last_commit_sha'] = match.group(1)

    return parsed


def check_bootstrap_drift() -> list[DriftIssue]:
    """Check for drift in CONTEXT_BOOTSTRAP.md."""
    issues = []

    parsed = parse_bootstrap_file()
    if parsed is None:
        issues.append(
            DriftIssue(
                category='Bootstrap',
                severity='warning',
                description='CONTEXT_BOOTSTRAP.md not found',
                actual='File missing',
                expected='Auto-generated bootstrap file',
                fixable=True,
            )
        )
        return issues

    current_branch = get_current_branch()
    current_phase = derive_phase(current_branch)
    last_commit_time = get_last_commit_time()
    current_sha = run_git(['log', '-1', '--format=%h'])

    # Check branch drift
    if parsed['branch'] and parsed['branch'] != current_branch:
        issues.append(
            DriftIssue(
                category='Bootstrap',
                severity='error',
                description='Branch mismatch',
                actual=f'Bootstrap shows: {parsed["branch"]}',
                expected=f'Current branch: {current_branch}',
                fixable=True,
            )
        )

    # Check phase drift
    if parsed['phase'] and parsed['phase'] != current_phase:
        issues.append(
            DriftIssue(
                category='Bootstrap',
                severity='warning',
                description='Phase mismatch',
                actual=f'Bootstrap shows: {parsed["phase"]}',
                expected=f'Inferred phase: {current_phase}',
                fixable=True,
            )
        )

    # Check commit drift
    if parsed['last_commit_sha'] and current_sha and parsed['last_commit_sha'] != current_sha:
        issues.append(
            DriftIssue(
                category='Bootstrap',
                severity='warning',
                description='Stale commit reference',
                actual=f'Bootstrap shows: {parsed["last_commit_sha"]}',
                expected=f'Latest commit: {current_sha}',
                fixable=True,
            )
        )

    # Check age of bootstrap
    if parsed['generated_at'] and last_commit_time and last_commit_time > parsed['generated_at']:
        age_minutes = (datetime.now(UTC) - parsed['generated_at']).total_seconds() / 60
        issues.append(
            DriftIssue(
                category='Bootstrap',
                severity='warning',
                description='Bootstrap older than latest commit',
                actual=f'Generated {age_minutes:.0f}m ago',
                expected='Should be regenerated after commits',
                fixable=True,
            )
        )

    return issues


def check_worktree_drift() -> list[DriftIssue]:
    """Check for drift in git worktree state."""
    issues = []

    # Check for uncommitted changes
    status = run_git(['status', '--porcelain'])
    if status:
        lines = [line for line in status.split('\n') if line.strip()]
        issues.append(
            DriftIssue(
                category='Working Tree',
                severity='warning',
                description='Uncommitted changes present',
                actual=f'{len(lines)} modified/untracked files',
                expected='Clean working tree',
                fixable=False,
            )
        )

    # Check if branch is ahead of origin
    current_branch = get_current_branch()
    ahead = run_git(['rev-list', '--count', f'origin/{current_branch}..HEAD'])
    if ahead and int(ahead) > 0:
        issues.append(
            DriftIssue(
                category='Remote Sync',
                severity='warning',
                description='Commits not pushed to origin',
                actual=f'{ahead} commit(s) ahead of origin',
                expected='Branch synced with origin',
                fixable=False,
            )
        )

    return issues


def check_all_drift() -> list[DriftIssue]:
    """Check all drift sources."""
    issues = []
    issues.extend(check_bootstrap_drift())
    issues.extend(check_worktree_drift())
    return issues


def fix_drift(issues: list[DriftIssue]) -> int:
    """Attempt to fix fixable drift issues.

    Returns number of issues fixed.
    """
    fixed = 0

    for issue in issues:
        if not issue.fixable:
            continue

        if issue.category == 'Bootstrap':
            # Regenerate bootstrap
            result = subprocess.run(
                ['uv', 'run', 'scripts/generate-bootstrap.py'],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                fixed += 1
                console.print(f'  [green]Fixed:[/green] {issue.description}')
            break  # Only need to regenerate once

    return fixed


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Detect context drift',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check for drift
  uv run scripts/detect-drift.py

  # Fix fixable issues
  uv run scripts/detect-drift.py --fix
        """,
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix fixable drift issues',
    )

    args = parser.parse_args()

    console.print('[bold]Detecting context drift...[/bold]\n')

    issues = check_all_drift()

    if not issues:
        console.print('[green]No drift detected - context is consistent[/green]')
        return 0

    # Display issues
    table = Table(title='Drift Issues Detected')
    table.add_column('Category')
    table.add_column('Severity')
    table.add_column('Description')
    table.add_column('Fixable')

    for issue in issues:
        severity_style = 'yellow' if issue.severity == 'warning' else 'red'
        fixable_str = '[green]Yes[/green]' if issue.fixable else '[dim]No[/dim]'
        table.add_row(
            issue.category,
            f'[{severity_style}]{issue.severity}[/{severity_style}]',
            issue.description,
            fixable_str,
        )

    console.print(table)
    console.print()

    # Show details
    console.print('[bold]Details:[/bold]')
    for issue in issues:
        console.print(f'  {issue.description}:')
        console.print(f'    [dim]Actual:[/dim] {issue.actual}')
        console.print(f'    [dim]Expected:[/dim] {issue.expected}')

    console.print()

    # Fix if requested
    if args.fix:
        fixable_count = sum(1 for i in issues if i.fixable)
        if fixable_count > 0:
            console.print(f'[bold]Attempting to fix {fixable_count} issue(s)...[/bold]')
            fixed = fix_drift(issues)
            console.print(f'\n[green]Fixed {fixed} issue(s)[/green]')
        else:
            console.print('[yellow]No fixable issues found[/yellow]')

    # Return non-zero if errors present
    return 1 if any(i.severity == 'error' for i in issues) else 0


if __name__ == '__main__':
    sys.exit(main())
