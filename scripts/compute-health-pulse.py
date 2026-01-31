#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich", "pyyaml"]
# ///
"""
Compute Health Pulse - Composite workflow health score.

Computes a single 0-100 score representing overall workflow health.
Shows component breakdown and primary driver.

Usage:
    uv run scripts/compute-health-pulse.py                    # Show health pulse
    uv run scripts/compute-health-pulse.py --format=json      # JSON output
    uv run scripts/compute-health-pulse.py --verbose          # Show component details
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Paths
BASELINES_FILE = Path("temp/WORKFLOW_HISTORY/baselines/ratchet-history.json")


@dataclass
class HealthComponent:
    """Individual health component score."""
    name: str
    score: int  # 0-100
    weight: float
    status: str  # "good", "fair", "poor"
    detail: str


@dataclass
class HealthPulse:
    """Complete health pulse result."""
    score: int
    rating: str  # "EXCELLENT", "GOOD", "FAIR", "POOR"
    components: list[HealthComponent]
    primary_driver: str
    trend: int | None  # Change from last measurement


def run_git(cmd: list[str]) -> str:
    """Run git command and return output."""
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def get_commit_velocity_score() -> HealthComponent:
    """Score based on recent commit activity.

    Baseline: 3-5 commits/day is healthy for active development.
    """
    # Get commits from last 7 days
    result = subprocess.run(
        ["git", "log", "--since=7 days ago", "--format=%H"],
        capture_output=True,
        text=True,
    )
    commits = [c for c in result.stdout.split("\n") if c.strip()]
    total = len(commits)
    daily_avg = total / 7

    # Scoring
    if daily_avg >= 3:
        score = min(100, int(50 + (daily_avg - 3) * 10))
        status = "good"
    elif daily_avg >= 1:
        score = int(30 + daily_avg * 20)
        status = "fair"
    else:
        score = int(daily_avg * 30)
        status = "poor"

    score = max(0, min(100, score))

    return HealthComponent(
        name="Commit Velocity",
        score=score,
        weight=0.25,
        status=status,
        detail=f"{total} commits in 7 days ({daily_avg:.1f}/day)",
    )


def get_phase_duration_score() -> HealthComponent:
    """Score based on time in current phase.

    Uses branch age as proxy for phase duration.
    """
    branch = run_git(["branch", "--show-current"]) or "main"

    if branch in ("main", "master"):
        return HealthComponent(
            name="Phase Duration",
            score=100,
            weight=0.25,
            status="good",
            detail="On mainline (no active phase)",
        )

    # Get branch creation time (first commit on branch not on main)
    first_commit = run_git([
        "log", branch, "--not", "main",
        "--format=%aI", "--reverse", "-1"
    ])

    if not first_commit:
        return HealthComponent(
            name="Phase Duration",
            score=80,
            weight=0.25,
            status="good",
            detail="New branch (no divergence yet)",
        )

    try:
        start = datetime.fromisoformat(first_commit)
        now = datetime.now(start.tzinfo)
        days = (now - start).days

        # Scoring based on phase type
        if branch.startswith("feat/"):
            expected_days = 5
        elif branch.startswith("fix/"):
            expected_days = 2
        else:
            expected_days = 3

        if days <= expected_days:
            score = 100
            status = "good"
        elif days <= expected_days * 2:
            score = 70
            status = "fair"
        else:
            score = max(20, 100 - (days - expected_days) * 10)
            status = "poor"

        return HealthComponent(
            name="Phase Duration",
            score=score,
            weight=0.25,
            status=status,
            detail=f"{days} days on {branch} (expected: {expected_days}d)",
        )

    except ValueError:
        return HealthComponent(
            name="Phase Duration",
            score=50,
            weight=0.25,
            status="fair",
            detail="Could not determine branch age",
        )


def get_test_coverage_score() -> HealthComponent:
    """Score based on dbt test pass rate and count.

    Uses baseline from ratchet-history.json.
    """
    # Try to get baseline
    baseline = 80  # Default
    if BASELINES_FILE.exists():
        try:
            with open(BASELINES_FILE) as f:
                data = json.load(f)
            for metric in data.get("metrics", []):
                if metric["name"] == "test_count_minimum":
                    baseline = metric["current_baseline"]
                    break
        except (json.JSONDecodeError, KeyError):
            pass

    # Run dbt test in dbt_project directory
    dbt_project_dir = Path.cwd() / "dbt_project"
    if not dbt_project_dir.exists():
        # Try from parent if we're in a subdirectory
        dbt_project_dir = Path.cwd().parent / "dbt_project"

    if dbt_project_dir.exists():
        result = subprocess.run(
            ["uv", "run", "dbt", "test"],
            capture_output=True,
            text=True,
            cwd=dbt_project_dir,
            timeout=120,
        )
    else:
        # Return placeholder if dbt_project not found
        return HealthComponent(
            name="Test Coverage",
            score=50,
            weight=0.25,
            status="fair",
            detail="dbt_project directory not found",
        )

    # Parse output for pass count
    output = result.stdout + result.stderr
    import re
    match = re.search(r'PASS=(\d+)', output)
    pass_count = int(match.group(1)) if match else 0

    error_match = re.search(r'ERROR=(\d+)', output)
    error_count = int(error_match.group(1)) if error_match else 0

    if error_count > 0:
        score = max(0, 100 - error_count * 20)
        status = "poor"
        detail = f"{pass_count} passed, {error_count} failed"
    elif pass_count >= baseline:
        score = min(100, int(80 + (pass_count - baseline) * 0.5))
        status = "good"
        detail = f"{pass_count} tests passing (baseline: {baseline})"
    else:
        score = int((pass_count / baseline) * 80)
        status = "fair"
        detail = f"{pass_count} tests (below baseline {baseline})"

    return HealthComponent(
        name="Test Coverage",
        score=score,
        weight=0.25,
        status=status,
        detail=detail,
    )


def get_agent_collaboration_score() -> HealthComponent:
    """Score based on agent-assisted commit ratio.

    Higher agent collaboration indicates effective AI-assisted development.
    """
    result = subprocess.run(
        ["git", "log", "--since=7 days ago", "--format=%B%x00"],
        capture_output=True,
        text=True,
    )
    commits = [c for c in result.stdout.split("\x00") if c.strip()]
    total = len(commits)

    if total == 0:
        return HealthComponent(
            name="Agent Collaboration",
            score=50,
            weight=0.25,
            status="fair",
            detail="No recent commits to analyze",
        )

    agent_commits = sum(1 for c in commits if "Co-Authored-By:" in c)
    ratio = agent_commits / total

    # 40-80% agent collaboration is optimal
    if 0.4 <= ratio <= 0.8:
        score = 100
        status = "good"
    elif 0.2 <= ratio < 0.4 or 0.8 < ratio <= 0.95:
        score = 70
        status = "fair"
    else:
        score = 40
        status = "poor"

    return HealthComponent(
        name="Agent Collaboration",
        score=score,
        weight=0.25,
        status=status,
        detail=f"{agent_commits}/{total} commits agent-assisted ({ratio*100:.0f}%)",
    )


def compute_health_pulse() -> HealthPulse:
    """Compute complete health pulse."""
    components = [
        get_commit_velocity_score(),
        get_phase_duration_score(),
        get_test_coverage_score(),
        get_agent_collaboration_score(),
    ]

    # Weighted average
    total_score = sum(c.score * c.weight for c in components)
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

    # Find primary driver (lowest weighted contribution)
    contributions = [(c.name, c.score * c.weight) for c in components]
    primary_driver = min(contributions, key=lambda x: x[1])[0]

    return HealthPulse(
        score=score,
        rating=rating,
        components=components,
        primary_driver=primary_driver,
        trend=None,  # Trend calculation requires history
    )


def render_bar(score: int, width: int = 10) -> str:
    """Render ASCII progress bar."""
    filled = int(score / 100 * width)
    empty = width - filled
    return "=" * filled + "-" * empty


def format_health_pulse(pulse: HealthPulse, verbose: bool = False) -> None:
    """Print formatted health pulse output."""
    # Color based on rating
    color_map = {
        "EXCELLENT": "green",
        "GOOD": "blue",
        "FAIR": "yellow",
        "POOR": "red",
    }
    color = color_map.get(pulse.rating, "white")

    # Header
    bar = render_bar(pulse.score)
    header = Text()
    header.append("HEALTH PULSE: ", style="bold")
    header.append(f"{pulse.score}", style=f"bold {color}")
    header.append(f" [{bar}] ", style="dim")
    header.append(pulse.rating, style=f"bold {color}")

    console.print(Panel(header, border_style=color))

    # Primary driver
    driver_text = Text()
    driver_text.append("Primary Driver: ", style="dim")
    driver_text.append(pulse.primary_driver, style="bold yellow")
    if any(c.name == pulse.primary_driver and c.status == "poor" for c in pulse.components):
        driver_text.append(" (dragging down)", style="red")
    console.print(driver_text)
    console.print()

    # Component details
    if verbose:
        console.print("[bold]Components:[/bold]")
        for c in pulse.components:
            status_color = {"good": "green", "fair": "yellow", "poor": "red"}.get(c.status, "white")
            console.print(f"  {c.name:20} [{render_bar(c.score, 8)}] {c.score:3d}  [dim]{c.detail}[/dim]")
    else:
        console.print("[dim]Use --verbose for component breakdown[/dim]")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute workflow health pulse",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show component breakdown",
    )

    args = parser.parse_args()

    pulse = compute_health_pulse()

    if args.format == "json":
        output = {
            "score": pulse.score,
            "rating": pulse.rating,
            "primary_driver": pulse.primary_driver,
            "trend": pulse.trend,
            "components": [
                {
                    "name": c.name,
                    "score": c.score,
                    "weight": c.weight,
                    "status": c.status,
                    "detail": c.detail,
                }
                for c in pulse.components
            ],
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }
        print(json.dumps(output, indent=2))
    else:
        format_health_pulse(pulse, verbose=args.verbose)

    return 0


if __name__ == "__main__":
    sys.exit(main())
