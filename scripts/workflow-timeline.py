#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich"]
# ///
"""
Workflow Timeline - Git-based workflow observability.

Parses git history to reconstruct workflow timeline with agent tracking.
Zero instrumentation required - git is the telemetry source.

Usage:
    uv run scripts/workflow-timeline.py                    # Last 24 hours
    uv run scripts/workflow-timeline.py --since="8 hours ago"
    uv run scripts/workflow-timeline.py --since="2 days ago" --format=json
    uv run scripts/workflow-timeline.py --branch=feat/x    # Specific branch
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

# Schema version for event output
SCHEMA_VERSION = "1.0.0"


@dataclass
class CommitInfo:
    """Parsed commit information."""
    sha: str
    short_sha: str
    timestamp: datetime
    author: str
    author_email: str
    message: str
    commit_type: str = "other"
    scope: str | None = None
    co_authored_by: list[str] = field(default_factory=list)
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0


@dataclass
class TimelineEvent:
    """Schema-compliant event for JSON export."""
    schema_version: str
    timestamp: str
    event_type: str
    source: dict[str, Any]
    correlation_id: str
    payload: dict[str, Any]


def parse_conventional_commit(message: str) -> tuple[str, str | None]:
    """Parse conventional commit message for type and scope.

    Examples:
        feat(staging): add model -> ('feat', 'staging')
        fix: correct bug -> ('fix', None)
        chore(deps): update -> ('chore', 'deps')
    """
    pattern = r'^(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(?:\(([^)]+)\))?:'
    match = re.match(pattern, message.lower())
    if match:
        return match.group(1), match.group(2)
    return "other", None


def parse_co_authored_by(message: str) -> list[str]:
    """Extract Co-Authored-By names from commit message."""
    pattern = r'Co-Authored-By:\s*([^<]+)'
    matches = re.findall(pattern, message, re.IGNORECASE)
    return [name.strip() for name in matches]


def get_branch_name() -> str:
    """Get current git branch name."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip() or "HEAD"


def get_commit_stats(sha: str) -> tuple[int, int, int]:
    """Get files changed, insertions, deletions for a commit."""
    result = subprocess.run(
        ["git", "show", "--stat", "--format=", sha],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 0, 0, 0

    lines = result.stdout.strip().split("\n")
    if not lines or not lines[-1]:
        return 0, 0, 0

    # Parse summary line like: "3 files changed, 45 insertions(+), 12 deletions(-)"
    summary = lines[-1]
    files = 0
    insertions = 0
    deletions = 0

    files_match = re.search(r'(\d+) files? changed', summary)
    if files_match:
        files = int(files_match.group(1))

    ins_match = re.search(r'(\d+) insertions?\(\+\)', summary)
    if ins_match:
        insertions = int(ins_match.group(1))

    del_match = re.search(r'(\d+) deletions?\(-\)', summary)
    if del_match:
        deletions = int(del_match.group(1))

    return files, insertions, deletions


def get_commits(since: str = "24 hours ago", branch: str | None = None) -> list[CommitInfo]:
    """Get commits from git log."""
    cmd = [
        "git", "log",
        f"--since={since}",
        "--format=%H|%h|%aI|%an|%ae|%B%x00",  # NULL separator for multi-line messages
    ]
    if branch:
        cmd.append(branch)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"[red]Error running git log: {result.stderr}[/red]")
        return []

    commits = []
    raw_entries = result.stdout.split("\x00")

    for entry in raw_entries:
        entry = entry.strip()
        if not entry:
            continue

        # Split on first newline to separate header from body
        parts = entry.split("|", 5)
        if len(parts) < 6:
            continue

        sha, short_sha, timestamp_str, author, author_email, message = parts

        # Parse timestamp
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except ValueError:
            continue

        # Parse conventional commit
        first_line = message.split("\n")[0]
        commit_type, scope = parse_conventional_commit(first_line)

        # Extract co-authors
        co_authors = parse_co_authored_by(message)

        # Get stats
        files_changed, insertions, deletions = get_commit_stats(sha)

        commits.append(CommitInfo(
            sha=sha,
            short_sha=short_sha,
            timestamp=timestamp,
            author=author,
            author_email=author_email,
            message=first_line.strip(),
            commit_type=commit_type,
            scope=scope,
            co_authored_by=co_authors,
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
        ))

    return commits


def derive_phase(commit_type: str, scope: str | None) -> str:
    """Derive workflow phase from commit type and scope."""
    if commit_type == "docs":
        if scope in ("prd", "specs"):
            return "PM"
        if scope in ("tdd", "architecture"):
            return "ARCH"
        return "DOCS"
    if commit_type == "feat":
        return "DEV"
    if commit_type in ("fix", "refactor"):
        return "DEV"
    if commit_type == "test":
        return "TEST"
    if commit_type == "chore":
        return "OPS"
    return "DEV"


def calculate_active_time(commits: list[CommitInfo]) -> str:
    """Calculate active time from first to last commit."""
    if len(commits) < 2:
        return "0m"

    first = commits[-1].timestamp
    last = commits[0].timestamp
    delta = last - first

    hours = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)

    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def calculate_gaps(commits: list[CommitInfo]) -> list[tuple[int, str]]:
    """Calculate gaps between commits, return (minutes, description) tuples."""
    gaps = []
    for i in range(len(commits) - 1):
        current = commits[i]
        previous = commits[i + 1]
        delta = current.timestamp - previous.timestamp
        minutes = int(delta.total_seconds() // 60)
        if minutes > 30:  # Only report significant gaps
            hours = minutes // 60
            mins = minutes % 60
            if hours > 0:
                gap_str = f"{hours}h {mins}m"
            else:
                gap_str = f"{mins}m"
            gaps.append((minutes, gap_str))
    return gaps


def format_timeline(commits: list[CommitInfo], branch: str) -> None:
    """Print human-readable timeline."""
    if not commits:
        console.print("[yellow]No commits found in the specified time range.[/yellow]")
        return

    active_time = calculate_active_time(commits)
    agent_commits = sum(1 for c in commits if c.co_authored_by)
    agent_pct = int((agent_commits / len(commits)) * 100) if commits else 0

    # Header
    header = Text()
    header.append(f"WORKFLOW TIMELINE: ", style="bold")
    header.append(f"{branch}", style="cyan")
    header.append(f" ({active_time} active)", style="dim")

    console.print(Panel(header, border_style="blue"))
    console.print()

    # Timeline table
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Time", style="dim", width=6)
    table.add_column("Phase", style="bold", width=6)
    table.add_column("Details", no_wrap=False)

    prev_timestamp = None
    for commit in reversed(commits):  # Oldest first
        time_str = commit.timestamp.strftime("%H:%M")
        phase = derive_phase(commit.commit_type, commit.scope)

        details = Text()
        details.append(f"{commit.commit_type}", style="green" if commit.commit_type == "feat" else "yellow")
        if commit.scope:
            details.append(f"({commit.scope})", style="dim")
        details.append(f": {commit.message.split(':')[-1].strip()[:60]}")

        if commit.co_authored_by:
            details.append(f"\n       Agent: ", style="dim")
            details.append(", ".join(commit.co_authored_by), style="magenta")

        # Calculate gap from previous
        if prev_timestamp:
            delta = commit.timestamp - prev_timestamp
            minutes = int(delta.total_seconds() // 60)
            if minutes > 30:
                hours = minutes // 60
                mins = minutes % 60
                gap_str = f"{hours}h {mins}m" if hours > 0 else f"{mins}m"
                details.append(f"\n       Gap: {gap_str}", style="dim yellow")

        table.add_row(time_str, f"[{phase}]", details)
        prev_timestamp = commit.timestamp

    console.print(table)
    console.print()

    # Insights
    console.print("[bold]INSIGHTS:[/bold]")
    console.print(f"  Session duration: {active_time}")
    console.print(f"  Agent contribution: {agent_commits}/{len(commits)} commits ({agent_pct}%)")

    gaps = calculate_gaps(commits)
    if gaps:
        max_gap = max(gaps, key=lambda x: x[0])
        console.print(f"  Largest gap: {max_gap[1]}")


def commits_to_events(commits: list[CommitInfo], branch: str) -> list[TimelineEvent]:
    """Convert commits to schema-compliant events."""
    events = []
    for commit in commits:
        event = TimelineEvent(
            schema_version=SCHEMA_VERSION,
            timestamp=commit.timestamp.isoformat(),
            event_type="commit",
            source={
                "type": "git",
                "identity": branch,
                "session_id": None,
            },
            correlation_id=branch,
            payload={
                "sha": commit.sha,
                "short_sha": commit.short_sha,
                "message": commit.message,
                "author": commit.author,
                "author_email": commit.author_email,
                "co_authored_by": commit.co_authored_by,
                "commit_type": commit.commit_type,
                "scope": commit.scope,
                "files_changed": commit.files_changed,
                "insertions": commit.insertions,
                "deletions": commit.deletions,
            },
        )
        events.append(event)
    return events


def validate_event(event: dict[str, Any], schema_path: Path) -> bool:
    """Validate event against JSON schema (basic validation)."""
    required_fields = ["schema_version", "timestamp", "event_type", "source", "correlation_id"]
    for field in required_fields:
        if field not in event:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate workflow timeline from git history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run scripts/workflow-timeline.py --since="8 hours ago"
  uv run scripts/workflow-timeline.py --since="2 days ago" --format=json
  uv run scripts/workflow-timeline.py --branch=feat/customer-analytics
        """,
    )
    parser.add_argument(
        "--since",
        default="24 hours ago",
        help="Time range for commits (default: 24 hours ago)",
    )
    parser.add_argument(
        "--branch",
        default=None,
        help="Branch to analyze (default: current branch)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Get branch name
    branch = args.branch or get_branch_name()

    # Get commits
    commits = get_commits(since=args.since, branch=args.branch)

    if args.format == "json":
        events = commits_to_events(commits, branch)
        output = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "branch": branch,
                "since": args.since,
                "event_count": len(events),
            },
            "events": [asdict(e) for e in events],
        }
        print(json.dumps(output, indent=2))
    else:
        format_timeline(commits, branch)

    return 0


if __name__ == "__main__":
    sys.exit(main())
