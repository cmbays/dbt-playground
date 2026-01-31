#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich"]
# ///
"""
Workflow Glance - 3-second terminal health check.

Provides instant visibility into current workflow state.
Zero instrumentation required - git is the telemetry source.

Usage:
    uv run scripts/workflow-glance.py                    # Quick overview
    uv run scripts/workflow-glance.py --format=json      # Machine-readable
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


# ---------------------------------------------------------------------------
# Quick Health Computation (subset of compute-health-pulse.py for speed)
# ---------------------------------------------------------------------------

def get_quick_commit_velocity_score() -> tuple[int, str]:
    """Score based on recent commit activity (fast git-only check)."""
    result = subprocess.run(
        ["git", "log", "--since=7 days ago", "--format=%H"],
        capture_output=True,
        text=True,
    )
    commits = [c for c in result.stdout.split("\n") if c.strip()]
    total = len(commits)
    daily_avg = total / 7

    if daily_avg >= 3:
        score = min(100, int(50 + (daily_avg - 3) * 10))
    elif daily_avg >= 1:
        score = int(30 + daily_avg * 20)
    else:
        score = int(daily_avg * 30)

    return max(0, min(100, score)), f"{daily_avg:.1f}/day"


def get_quick_phase_duration_score() -> tuple[int, str]:
    """Score based on time in current phase (fast git-only check)."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
    )
    branch = result.stdout.strip() or "main"

    if branch in ("main", "master"):
        return 100, "mainline"

    # Get branch creation time
    first_commit = subprocess.run(
        ["git", "log", branch, "--not", "main", "--format=%aI", "--reverse", "-1"],
        capture_output=True,
        text=True,
    )

    if first_commit.returncode != 0 or not first_commit.stdout.strip():
        return 80, "new branch"

    try:
        start = datetime.fromisoformat(first_commit.stdout.strip())
        now = datetime.now(start.tzinfo)
        days = (now - start).days

        if branch.startswith("feat/"):
            expected_days = 5
        elif branch.startswith("fix/"):
            expected_days = 2
        else:
            expected_days = 3

        if days <= expected_days:
            score = 100
        elif days <= expected_days * 2:
            score = 70
        else:
            score = max(20, 100 - (days - expected_days) * 10)

        return score, f"{days}d"

    except ValueError:
        return 50, "unknown"


def get_quick_agent_collaboration_score() -> tuple[int, str]:
    """Score based on agent-assisted commit ratio (fast git-only check)."""
    result = subprocess.run(
        ["git", "log", "--since=7 days ago", "--format=%B%x00"],
        capture_output=True,
        text=True,
    )
    commits = [c for c in result.stdout.split("\x00") if c.strip()]
    total = len(commits)

    if total == 0:
        return 50, "no commits"

    agent_commits = sum(1 for c in commits if "Co-Authored-By:" in c)
    ratio = agent_commits / total

    # 40-80% agent collaboration is optimal
    if 0.4 <= ratio <= 0.8:
        score = 100
    elif 0.2 <= ratio < 0.4 or 0.8 < ratio <= 0.95:
        score = 70
    else:
        score = 40

    return score, f"{ratio*100:.0f}%"


def compute_quick_health() -> tuple[int, str]:
    """
    Compute a quick health score using only fast git operations.

    Skips the dbt test component to stay under 3 seconds.
    Uses 3 components with adjusted weights (total = 1.0).

    Returns:
        Tuple of (score, rating)
    """
    try:
        velocity_score, _ = get_quick_commit_velocity_score()
        phase_score, _ = get_quick_phase_duration_score()
        agent_score, _ = get_quick_agent_collaboration_score()

        # Adjusted weights (original 4 components at 0.25 each, now 3 at ~0.33)
        # Velocity: 0.35, Phase: 0.30, Agent: 0.35
        total_score = (
            velocity_score * 0.35 +
            phase_score * 0.30 +
            agent_score * 0.35
        )
        score = int(total_score)

        # Rating
        if score >= 85:
            rating = "EXCELLENT"
        elif score >= 70:
            rating = "GOOD"
        elif score >= 50:
            rating = "FAIR"
        else:
            rating = "POOR"

        return score, rating

    except Exception as e:
        # Graceful fallback on any error, but log it for debugging
        import sys
        print(f"[dim]Health computation failed: {e}[/dim]", file=sys.stderr)
        return None, None


@dataclass
class WorkflowState:
    """Current workflow state summary."""
    branch: str
    phase: str
    active_time: str
    today_commits: int
    today_files: int
    agent_pct: int
    last_commit_message: str
    last_commit_time: str
    time_since_last: str
    health: int | None
    health_rating: str | None
    next_action: str


def run_git(cmd: list[str]) -> str:
    """Run git command and return output."""
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def get_branch_name() -> str:
    """Get current git branch name."""
    return run_git(["branch", "--show-current"]) or "HEAD"


def derive_phase_from_branch(branch: str) -> str:
    """Derive workflow phase from branch name."""
    if branch == "main" or branch == "master":
        return "MAINLINE"
    if branch.startswith("feat/"):
        return "DEVELOPMENT"
    if branch.startswith("fix/"):
        return "BUGFIX"
    if branch.startswith("docs/"):
        return "DOCUMENTATION"
    if branch.startswith("refactor/"):
        return "REFACTORING"
    if branch.startswith("test/"):
        return "TESTING"
    if branch.startswith("chore/"):
        return "MAINTENANCE"
    return "DEVELOPMENT"


def get_today_stats() -> tuple[int, int, int]:
    """Get commits, files changed, agent percentage for today."""
    # Get today's commits
    result = subprocess.run(
        ["git", "log", "--since=midnight", "--format=%H|%B%x00"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 0, 0, 0

    commits = [c for c in result.stdout.split("\x00") if c.strip()]
    total_commits = len(commits)
    agent_commits = 0

    for commit in commits:
        if "Co-Authored-By:" in commit:
            agent_commits += 1

    # Get files changed today
    files_result = subprocess.run(
        ["git", "diff", "--stat", "--name-only", "@{midnight}..HEAD"],
        capture_output=True,
        text=True,
    )
    files_changed = len([f for f in files_result.stdout.split("\n") if f.strip()])

    agent_pct = int((agent_commits / total_commits) * 100) if total_commits > 0 else 0

    return total_commits, files_changed, agent_pct


def get_last_commit_info() -> tuple[str, str, str]:
    """Get last commit message, time, and time since."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%s|%aI"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return "No commits", "N/A", "N/A"

    parts = result.stdout.strip().split("|")
    if len(parts) < 2:
        return result.stdout.strip(), "N/A", "N/A"

    message = parts[0][:60]
    timestamp_str = parts[1]

    try:
        commit_time = datetime.fromisoformat(timestamp_str)
        time_str = commit_time.strftime("%H:%M")
        now = datetime.now(commit_time.tzinfo)
        delta = now - commit_time

        total_minutes = int(delta.total_seconds() // 60)
        if total_minutes < 60:
            time_since = f"{total_minutes}m ago"
        elif total_minutes < 1440:
            hours = total_minutes // 60
            mins = total_minutes % 60
            time_since = f"{hours}h {mins}m ago"
        else:
            days = total_minutes // 1440
            time_since = f"{days}d ago"

        return message, time_str, time_since
    except (ValueError, TypeError):
        return message, "N/A", "N/A"


def get_active_time() -> str:
    """Calculate active time from first commit today to now."""
    result = subprocess.run(
        ["git", "log", "--since=midnight", "--reverse", "--format=%aI", "-1"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return "0m"

    try:
        first_commit = datetime.fromisoformat(result.stdout.strip())
        now = datetime.now(first_commit.tzinfo)
        delta = now - first_commit

        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    except (ValueError, TypeError):
        return "0m"


def infer_next_action(branch: str, last_message: str) -> str:
    """Infer next action based on branch state and last commit."""
    # Check if there are uncommitted changes
    status = run_git(["status", "--porcelain"])
    if status:
        return "Commit or stash pending changes"

    # Check if branch is ahead of origin
    ahead = run_git(["rev-list", "--count", f"origin/{branch}..HEAD"])
    if ahead and int(ahead) > 0:
        return f"Push {ahead} commit(s) to origin"

    # Check for PRs
    if branch not in ("main", "master"):
        # Check if PR exists
        pr_check = subprocess.run(
            ["gh", "pr", "view", branch, "--json", "state"],
            capture_output=True,
            text=True,
        )
        if pr_check.returncode == 0:
            pr_data = json.loads(pr_check.stdout)
            if pr_data.get("state") == "OPEN":
                return "Address PR review comments or await merge"
            return "PR merged - consider cleanup"

        return "Create PR for review"

    # On main branch
    if "docs" in last_message.lower():
        return "Consider next feature or enhancement"
    if "feat" in last_message.lower():
        return "Add tests or documentation"
    if "fix" in last_message.lower():
        return "Verify fix and update tests"

    return "Continue development"


def get_workflow_state() -> WorkflowState:
    """Gather complete workflow state."""
    branch = get_branch_name()
    phase = derive_phase_from_branch(branch)
    active_time = get_active_time()
    commits, files, agent_pct = get_today_stats()
    message, time_str, time_since = get_last_commit_info()
    next_action = infer_next_action(branch, message)

    # Compute quick health score (fast git-only check)
    health_score, health_rating = compute_quick_health()

    return WorkflowState(
        branch=branch,
        phase=phase,
        active_time=active_time,
        today_commits=commits,
        today_files=files,
        agent_pct=agent_pct,
        last_commit_message=message,
        last_commit_time=time_str,
        time_since_last=time_since,
        health=health_score,
        health_rating=health_rating,
        next_action=next_action,
    )


def format_glance(state: WorkflowState) -> None:
    """Print human-readable glance output."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Header line
    header = Text()
    header.append("WORKFLOW GLANCE", style="bold white")
    header.append(f"  {now}", style="dim")

    console.print(Panel(header, border_style="blue", padding=(0, 1)))

    # Main info table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Label", style="dim", width=8)
    table.add_column("Value", style="bold")
    table.add_column("Label2", style="dim", width=10)
    table.add_column("Value2", style="bold")

    # Health display with score and rating
    if state.health is None:
        health_str = "--/100"
    else:
        # Color based on rating
        color_map = {
            "EXCELLENT": "green",
            "GOOD": "blue",
            "FAIR": "yellow",
            "POOR": "red",
        }
        color = color_map.get(state.health_rating, "white")
        health_str = f"[{color}]{state.health} {state.health_rating}[/{color}]"

    table.add_row(
        "Branch:",
        state.branch,
        "Active:",
        state.active_time,
    )
    table.add_row(
        "Phase:",
        state.phase,
        "Health:",
        Text.from_markup(health_str) if state.health else health_str,
    )

    console.print(table)
    console.print()

    # Today's stats
    stats_text = Text()
    stats_text.append("TODAY: ", style="bold")
    stats_text.append(f"{state.today_commits} commits", style="cyan")
    stats_text.append(" | ", style="dim")
    stats_text.append(f"{state.today_files} files", style="cyan")
    stats_text.append(" | ", style="dim")
    stats_text.append(f"{state.agent_pct}% agent-assisted", style="magenta")

    console.print(stats_text)
    console.print()

    # Last commit
    last_text = Text()
    last_text.append("LAST: ", style="dim")
    last_text.append(f'"{state.last_commit_message}"', style="white")
    last_text.append(f" ({state.time_since_last})", style="dim")
    console.print(last_text)

    # Next action
    next_text = Text()
    next_text.append("NEXT: ", style="bold yellow")
    next_text.append(state.next_action, style="white")
    console.print(next_text)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Quick workflow status check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    state = get_workflow_state()

    if args.format == "json":
        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "branch": state.branch,
            "phase": state.phase,
            "active_time": state.active_time,
            "today": {
                "commits": state.today_commits,
                "files_changed": state.today_files,
                "agent_assisted_pct": state.agent_pct,
            },
            "last_commit": {
                "message": state.last_commit_message,
                "time": state.last_commit_time,
                "time_since": state.time_since_last,
            },
            "health": {
                "score": state.health,
                "rating": state.health_rating,
            },
            "next_action": state.next_action,
        }
        print(json.dumps(output, indent=2))
    else:
        format_glance(state)

    return 0


if __name__ == "__main__":
    sys.exit(main())
