#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich", "pyyaml"]
# ///
"""
Check Negative Space - Query rejected decisions registry.

Matches questions against the negative space registry to surface
previously rejected decisions and their rationale.

Usage:
    uv run scripts/check-negative-space.py --question "Should we use Snowflake?"
    uv run scripts/check-negative-space.py --list
    uv run scripts/check-negative-space.py --check-triggers
"""

import argparse
import sys
from difflib import SequenceMatcher
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

NEGATIVE_SPACE_FILE = Path("temp/NEGATIVE_SPACE.yaml")


def load_negative_space() -> list[dict]:
    """Load negative space registry."""
    if not NEGATIVE_SPACE_FILE.exists():
        console.print(f"[yellow]Warning: {NEGATIVE_SPACE_FILE} not found[/yellow]")
        return []

    with open(NEGATIVE_SPACE_FILE) as f:
        data = yaml.safe_load(f)

    return data.get("decisions_not_made", [])


def similarity(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings."""
    a_lower = a.lower()
    b_lower = b.lower()

    # Direct substring match
    if a_lower in b_lower or b_lower in a_lower:
        return 0.8

    # Sequence matcher for fuzzy match
    return SequenceMatcher(None, a_lower, b_lower).ratio()


def find_matches(question: str, decisions: list[dict], threshold: float = 0.4) -> list[tuple[dict, float]]:
    """Find decisions matching the question."""
    matches = []

    # Extract keywords from question
    keywords = set(question.lower().split())
    stop_words = {"should", "we", "the", "a", "an", "use", "add", "is", "are", "do", "does", "?"}
    keywords = keywords - stop_words

    for decision in decisions:
        stored_question = decision.get("question", "")
        score = similarity(question, stored_question)

        # Boost score for keyword matches
        stored_keywords = set(stored_question.lower().split()) - stop_words
        keyword_overlap = len(keywords & stored_keywords) / max(len(keywords), 1)
        score = max(score, keyword_overlap)

        # Check rationale for keyword matches too
        rationale = decision.get("rationale", "").lower()
        for keyword in keywords:
            if keyword in rationale:
                score += 0.1

        if score >= threshold:
            matches.append((decision, min(score, 1.0)))

    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def format_decision(decision: dict, score: float | None = None) -> None:
    """Format and print a single decision."""
    answer_colors = {
        "NO": "red",
        "NOT_YET": "yellow",
        "PENDING": "blue",
    }
    answer = decision.get("answer", "UNKNOWN")
    color = answer_colors.get(answer, "white")

    # Header with match score
    header = Text()
    header.append(f"[{decision.get('id', '??')}] ", style="dim")
    header.append(decision.get("question", "Unknown question"), style="bold")
    if score is not None:
        header.append(f" (match: {score:.0%})", style="dim")

    console.print(Panel(header, border_style=color))

    # Answer
    console.print(f"  [bold]Answer:[/bold] [{color}]{answer}[/{color}]")
    console.print(f"  [bold]Date:[/bold] {decision.get('date', 'Unknown')}")
    console.print(f"  [bold]Raised by:[/bold] {decision.get('raised_by', 'Unknown')}")
    console.print(f"  [bold]Confidence:[/bold] {decision.get('confidence', 'Unknown')}")

    # Rationale
    rationale = decision.get("rationale", "").strip()
    if rationale:
        console.print(f"\n  [bold]Rationale:[/bold]")
        for line in rationale.split("\n"):
            console.print(f"    {line}")

    # Trigger
    trigger = decision.get("reconsidering_trigger", "")
    if trigger:
        console.print(f"\n  [bold yellow]Reconsider when:[/bold yellow]")
        console.print(f"    {trigger}")

    console.print()


def list_all_decisions(decisions: list[dict]) -> None:
    """List all decisions in table format."""
    table = Table(title="Negative Space Registry")
    table.add_column("ID", style="dim")
    table.add_column("Question")
    table.add_column("Answer")
    table.add_column("Confidence")
    table.add_column("Date")

    answer_colors = {
        "NO": "red",
        "NOT_YET": "yellow",
        "PENDING": "blue",
    }

    for decision in decisions:
        answer = decision.get("answer", "?")
        color = answer_colors.get(answer, "white")
        table.add_row(
            decision.get("id", "?"),
            decision.get("question", "?")[:50] + "..." if len(decision.get("question", "")) > 50 else decision.get("question", "?"),
            f"[{color}]{answer}[/{color}]",
            decision.get("confidence", "?"),
            decision.get("date", "?"),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(decisions)} decisions[/dim]")


def check_triggers(decisions: list[dict]) -> None:
    """Check if any reconsideration triggers might apply."""
    console.print("[bold]Checking reconsideration triggers...[/bold]\n")

    triggered = []
    for decision in decisions:
        trigger = decision.get("reconsidering_trigger", "")
        if not trigger:
            continue

        # Simple heuristics for trigger checking
        trigger_lower = trigger.lower()

        # Check data size triggers
        if "10gb" in trigger_lower or "1m rows" in trigger_lower:
            # Would need actual data size check
            pass

        # Check team size triggers
        if "team grows" in trigger_lower:
            # Would need team size info
            pass

        # For now, just list all triggers
        console.print(f"[dim]{decision.get('id')}[/dim] {decision.get('question', '')[:40]}...")
        console.print(f"    [yellow]Trigger:[/yellow] {trigger}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Query the negative space registry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for a specific decision
  uv run scripts/check-negative-space.py --question "Should we use Snowflake?"

  # List all decisions
  uv run scripts/check-negative-space.py --list

  # Check reconsideration triggers
  uv run scripts/check-negative-space.py --check-triggers
        """,
    )
    parser.add_argument(
        "--question",
        help="Question to match against registry",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all decisions",
    )
    parser.add_argument(
        "--check-triggers",
        action="store_true",
        help="Check reconsideration triggers",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.4,
        help="Match threshold 0.0-1.0 (default: 0.4)",
    )

    args = parser.parse_args()

    decisions = load_negative_space()

    if not decisions:
        console.print("[yellow]No decisions in registry[/yellow]")
        return 1

    if args.list:
        list_all_decisions(decisions)
        return 0

    if args.check_triggers:
        check_triggers(decisions)
        return 0

    if args.question:
        matches = find_matches(args.question, decisions, args.threshold)

        if not matches:
            console.print(f"[green]No matching decisions found for:[/green] {args.question}")
            console.print("[dim]This question has not been previously addressed in negative space.[/dim]")
            return 0

        console.print(f"[bold]Found {len(matches)} matching decision(s):[/bold]\n")
        for decision, score in matches[:3]:  # Top 3 matches
            format_decision(decision, score)

        return 0

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
