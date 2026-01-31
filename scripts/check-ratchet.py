#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich"]
# ///
"""
Check Ratchet - Quality non-degradation enforcement.

Validates that quality metrics meet or exceed baselines.
Baselines can only increase, never decrease (the ratchet effect).

Usage:
    uv run scripts/check-ratchet.py --metric=test_count_minimum --value=175
    uv run scripts/check-ratchet.py --check-all
    uv run scripts/check-ratchet.py --show-baselines
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

BASELINES_FILE = Path("temp/WORKFLOW_HISTORY/baselines/ratchet-history.json")
AUTO_INCREASE_THRESHOLD = 1.1  # 10% improvement triggers baseline update


def load_baselines() -> dict:
    """Load baseline data from file."""
    if not BASELINES_FILE.exists():
        console.print(f"[yellow]Warning: {BASELINES_FILE} not found[/yellow]")
        return {"metrics": []}

    with open(BASELINES_FILE) as f:
        return json.load(f)


def save_baselines(data: dict) -> None:
    """Save baseline data to file."""
    BASELINES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BASELINES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_current_baseline(metric_name: str) -> tuple[float | None, dict | None]:
    """Get current baseline value for a metric.

    Returns (baseline_value, metric_dict) or (None, None) if not found.
    """
    data = load_baselines()
    for metric in data.get("metrics", []):
        if metric.get("name") == metric_name:
            return metric.get("current_baseline"), metric
    return None, None


def schedule_baseline_increase(metric_name: str, new_value: float, reason: str) -> bool:
    """Schedule a baseline increase (appends to immutable history)."""
    data = load_baselines()

    for metric in data.get("metrics", []):
        if metric.get("name") == metric_name:
            old_value = metric.get("current_baseline", 0)

            # Append to history (immutable)
            history_entry = {
                "action": "baseline_increased",
                "date": datetime.now(timezone.utc).isoformat(),
                "value": new_value,
                "previous_value": old_value,
                "reason": reason,
            }
            metric.setdefault("history", []).append(history_entry)

            # Update current baseline
            metric["current_baseline"] = new_value

            # Update last_updated
            data["last_updated"] = datetime.now(timezone.utc).isoformat()

            save_baselines(data)
            return True

    return False


def check_ratchet(metric_name: str, new_value: float) -> tuple[bool, str]:
    """Check if a value meets the ratchet baseline.

    Returns:
        (passed, message)
    """
    baseline, metric = get_current_baseline(metric_name)

    if baseline is None:
        return True, f"No baseline defined for '{metric_name}' - allowing"

    if new_value >= baseline:
        # Check for auto-increase
        if new_value >= baseline * AUTO_INCREASE_THRESHOLD:
            improvement_pct = ((new_value - baseline) / baseline) * 100
            reason = f"Auto-increased: {improvement_pct:.1f}% improvement over previous baseline"
            schedule_baseline_increase(metric_name, new_value, reason)
            return True, f"PASSED and RAISED: {new_value} >= baseline {baseline} (+{improvement_pct:.1f}%)"

        return True, f"PASSED: {new_value} >= baseline {baseline}"

    else:
        deficit = baseline - new_value
        return False, f"BLOCKED: {new_value} < baseline {baseline} (deficit: {deficit})"


def get_current_test_count() -> int:
    """Get current test count from dbt."""
    dbt_project_dir = Path.cwd() / "dbt_project"
    if not dbt_project_dir.exists():
        return 0

    result = subprocess.run(
        ["uv", "run", "dbt", "test"],
        capture_output=True,
        text=True,
        cwd=dbt_project_dir,
        timeout=120,
    )

    import re
    match = re.search(r'PASS=(\d+)', result.stdout + result.stderr)
    return int(match.group(1)) if match else 0


def get_current_model_count() -> int:
    """Get current model count from dbt."""
    dbt_project_dir = Path.cwd() / "dbt_project"
    if not dbt_project_dir.exists():
        return 0

    result = subprocess.run(
        ["uv", "run", "dbt", "ls", "--resource-type", "model"],
        capture_output=True,
        text=True,
        cwd=dbt_project_dir,
    )

    return len([l for l in result.stdout.split("\n") if l.strip()])


def check_all_metrics() -> list[tuple[str, bool, str, float, float]]:
    """Check all defined metrics against their baselines.

    Returns list of (metric_name, passed, message, current_value, baseline).
    """
    results = []
    data = load_baselines()

    for metric in data.get("metrics", []):
        name = metric.get("name")
        baseline = metric.get("current_baseline", 0)

        # Get current value based on metric type
        if name == "test_count_minimum":
            current = get_current_test_count()
        elif name == "model_count_minimum":
            current = get_current_model_count()
        elif name == "staging_model_count":
            # Count staging models specifically
            dbt_project_dir = Path.cwd() / "dbt_project"
            if dbt_project_dir.exists():
                result = subprocess.run(
                    ["uv", "run", "dbt", "ls", "--select", "staging.*"],
                    capture_output=True,
                    text=True,
                    cwd=dbt_project_dir,
                )
                current = len([l for l in result.stdout.split("\n") if l.strip()])
            else:
                current = 0
        elif name == "test_coverage_ratio":
            tests = get_current_test_count()
            models = get_current_model_count()
            current = round(tests / models, 1) if models > 0 else 0
        else:
            # Unknown metric, skip
            continue

        passed, message = check_ratchet(name, current)
        results.append((name, passed, message, current, baseline))

    return results


def show_baselines() -> None:
    """Display all baselines in table format."""
    data = load_baselines()

    table = Table(title="Quality Ratchet Baselines")
    table.add_column("Metric", style="bold")
    table.add_column("Current Baseline", justify="right")
    table.add_column("Unit")
    table.add_column("Last Updated")
    table.add_column("History Count", justify="right")

    for metric in data.get("metrics", []):
        history = metric.get("history", [])
        last_updated = history[-1].get("date", "N/A")[:10] if history else "N/A"

        table.add_row(
            metric.get("name", "?"),
            str(metric.get("current_baseline", "?")),
            metric.get("unit", "?"),
            last_updated,
            str(len(history)),
        )

    console.print(table)
    console.print(f"\n[dim]Baselines file: {BASELINES_FILE}[/dim]")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check quality metrics against ratchet baselines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check a specific metric
  uv run scripts/check-ratchet.py --metric=test_count_minimum --value=175

  # Check all metrics against current state
  uv run scripts/check-ratchet.py --check-all

  # Show current baselines
  uv run scripts/check-ratchet.py --show-baselines
        """,
    )
    parser.add_argument(
        "--metric",
        help="Metric name to check",
    )
    parser.add_argument(
        "--value",
        type=float,
        help="Value to check against baseline",
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="Check all metrics against current state",
    )
    parser.add_argument(
        "--show-baselines",
        action="store_true",
        help="Display all baselines",
    )

    args = parser.parse_args()

    if args.show_baselines:
        show_baselines()
        return 0

    if args.check_all:
        console.print("[bold]Checking all quality metrics...[/bold]\n")
        results = check_all_metrics()

        all_passed = True
        for name, passed, message, current, baseline in results:
            status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
            console.print(f"  {status} {name}: {current} (baseline: {baseline})")
            if not passed:
                console.print(f"       [red]{message}[/red]")
                all_passed = False

        console.print()
        if all_passed:
            console.print("[green]All quality gates passed![/green]")
            return 0
        else:
            console.print("[red]Quality gate failure - deployment blocked[/red]")
            return 1

    if args.metric and args.value is not None:
        passed, message = check_ratchet(args.metric, args.value)
        if passed:
            console.print(f"[green]{message}[/green]")
            return 0
        else:
            console.print(f"[red]{message}[/red]")
            return 1

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
