#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich"]
# ///
"""
Generate Chronicle Data - Prepare data for timeline playground.

Reads git history and event log to generate chronicle-data.json
for the Workflow Chronicle HTML playground visualization.

Usage:
    uv run scripts/generate-chronicle-data.py                    # Generate data
    uv run scripts/generate-chronicle-data.py --since="7 days ago"
    uv run scripts/generate-chronicle-data.py --output=stdout    # Print to stdout
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

console = Console()

# Paths
WORKFLOW_HISTORY_DIR = Path("temp/WORKFLOW_HISTORY")
EVENTS_FILE = WORKFLOW_HISTORY_DIR / "events.jsonl"
OUTPUT_FILE = WORKFLOW_HISTORY_DIR / "chronicle-data.json"


@dataclass
class CommitData:
    """Commit data for visualization."""
    sha: str
    short_sha: str
    timestamp: str
    message: str
    commit_type: str
    scope: str | None
    author: str
    co_authored_by: list[str]
    files_changed: int
    insertions: int
    deletions: int
    branch: str


@dataclass
class BranchSpan:
    """Branch lifecycle for feature layer."""
    name: str
    start_time: str
    end_time: str | None
    commit_count: int
    status: str  # active, merged, stale


@dataclass
class ChronicleData:
    """Complete data structure for playground."""
    metadata: dict[str, Any]
    layers: dict[str, Any]
    insights: dict[str, Any]
    events: list[dict[str, Any]]


def run_git(cmd: list[str]) -> str:
    """Run git command and return output."""
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def parse_conventional_commit(message: str) -> tuple[str, str | None]:
    """Parse conventional commit message for type and scope."""
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

    summary = lines[-1]
    files = insertions = deletions = 0

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


def get_commits(since: str) -> list[CommitData]:
    """Get commits from git log."""
    cmd = [
        "git", "log",
        f"--since={since}",
        "--format=%H|%h|%aI|%an|%B%x00",
        "--all",  # All branches
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    commits = []
    raw_entries = result.stdout.split("\x00")

    for entry in raw_entries:
        entry = entry.strip()
        if not entry:
            continue

        parts = entry.split("|", 4)
        if len(parts) < 5:
            continue

        sha, short_sha, timestamp_str, author, message = parts

        # Parse conventional commit
        first_line = message.split("\n")[0]
        commit_type, scope = parse_conventional_commit(first_line)

        # Extract co-authors
        co_authors = parse_co_authored_by(message)

        # Get stats
        files_changed, insertions, deletions = get_commit_stats(sha)

        # Determine branch
        branch_result = subprocess.run(
            ["git", "branch", "--contains", sha, "--format=%(refname:short)"],
            capture_output=True,
            text=True,
        )
        branches = [b for b in branch_result.stdout.split("\n") if b.strip()]
        branch = branches[0] if branches else "unknown"

        commits.append(CommitData(
            sha=sha,
            short_sha=short_sha,
            timestamp=timestamp_str,
            message=first_line.strip(),
            commit_type=commit_type,
            scope=scope,
            author=author,
            co_authored_by=co_authors,
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
            branch=branch,
        ))

    return commits


def get_branches() -> list[BranchSpan]:
    """Get branch spans for feature layer."""
    result = subprocess.run(
        ["git", "branch", "-a", "--format=%(refname:short)|%(creatordate:iso)|%(committerdate:iso)"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []

    branches = []
    for line in result.stdout.split("\n"):
        if not line.strip():
            continue

        parts = line.split("|")
        if len(parts) < 3:
            continue

        name = parts[0].strip()
        if name.startswith("origin/"):
            continue  # Skip remote tracking branches

        # Get first and last commit on branch
        log_result = subprocess.run(
            ["git", "log", name, "--format=%aI", "--reverse"],
            capture_output=True,
            text=True,
        )
        commits = [c for c in log_result.stdout.split("\n") if c.strip()]

        start_time = commits[0] if commits else None
        end_time = commits[-1] if commits else None

        # Determine status
        status = "active"
        if name in ("main", "master"):
            status = "mainline"

        branches.append(BranchSpan(
            name=name,
            start_time=start_time or "",
            end_time=end_time,
            commit_count=len(commits),
            status=status,
        ))

    return branches


def load_events() -> list[dict[str, Any]]:
    """Load events from events.jsonl."""
    if not EVENTS_FILE.exists():
        return []

    events = []
    with open(EVENTS_FILE) as f:
        for line in f:
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    return events


def compute_insights(commits: list[CommitData]) -> dict[str, Any]:
    """Compute insights from commits."""
    if not commits:
        return {"total_commits": 0}

    # Commit type distribution
    type_counts: dict[str, int] = {}
    for c in commits:
        type_counts[c.commit_type] = type_counts.get(c.commit_type, 0) + 1

    # Agent contribution
    agent_commits = sum(1 for c in commits if c.co_authored_by)
    agent_pct = int((agent_commits / len(commits)) * 100) if commits else 0

    # Total changes
    total_files = sum(c.files_changed for c in commits)
    total_insertions = sum(c.insertions for c in commits)
    total_deletions = sum(c.deletions for c in commits)

    # Time span
    if len(commits) >= 2:
        try:
            first = datetime.fromisoformat(commits[-1].timestamp)
            last = datetime.fromisoformat(commits[0].timestamp)
            duration_hours = (last - first).total_seconds() / 3600
        except ValueError:
            duration_hours = 0
    else:
        duration_hours = 0

    return {
        "total_commits": len(commits),
        "commit_types": type_counts,
        "agent_contribution_pct": agent_pct,
        "total_files_changed": total_files,
        "total_insertions": total_insertions,
        "total_deletions": total_deletions,
        "duration_hours": round(duration_hours, 1),
    }


def generate_chronicle_data(since: str) -> ChronicleData:
    """Generate complete chronicle data structure."""
    commits = get_commits(since)
    branches = get_branches()
    events = load_events()
    insights = compute_insights(commits)

    now = datetime.now(timezone.utc)

    metadata = {
        "generated_at": now.isoformat(),
        "since": since,
        "version": "1.0.0",
    }

    layers = {
        "surface": {
            "name": "Commits",
            "description": "Individual git commits",
            "data": [asdict(c) for c in commits],
        },
        "features": {
            "name": "Branches",
            "description": "Feature branch lifecycles",
            "data": [asdict(b) for b in branches],
        },
        "decisions": {
            "name": "Decisions",
            "description": "Key decisions and trade-offs (placeholder)",
            "data": [],  # Populated in Week 4 from NEGATIVE_SPACE.yaml
        },
        "bedrock": {
            "name": "Foundation",
            "description": "Project constants and architecture",
            "data": {
                "project": "dbt-playground",
                "dbt_version": "1.11.2",
                "adapter": "duckdb",
                "current_milestone": "v0.6.0",
            },
        },
    }

    return ChronicleData(
        metadata=metadata,
        layers=layers,
        insights=insights,
        events=events,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate chronicle data for timeline playground",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--since",
        default="7 days ago",
        help="Time range for data (default: 7 days ago)",
    )
    parser.add_argument(
        "--output",
        choices=["file", "stdout"],
        default="file",
        help="Output destination (default: file)",
    )

    args = parser.parse_args()

    data = generate_chronicle_data(args.since)
    output = {
        "metadata": data.metadata,
        "layers": data.layers,
        "insights": data.insights,
        "events": data.events,
    }

    if args.output == "stdout":
        print(json.dumps(output, indent=2))
    else:
        WORKFLOW_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output, f, indent=2)
        console.print(f"[green]Chronicle data generated: {OUTPUT_FILE}[/green]")
        console.print(f"  Commits: {data.insights['total_commits']}")
        console.print(f"  Events: {len(data.events)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
