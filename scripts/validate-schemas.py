#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema", "rich"]
# ///
"""
Validate Schemas - Pre-commit schema validation.

Validates all events in events.jsonl against the event schema.
Suitable for use as a pre-commit hook.

Usage:
    uv run scripts/validate-schemas.py                    # Validate events.jsonl
    uv run scripts/validate-schemas.py --verbose          # Show details
    uv run scripts/validate-schemas.py --fix              # Remove invalid lines
"""

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError
from rich.console import Console

console = Console()

# Paths
WORKFLOW_HISTORY_DIR = Path("temp/WORKFLOW_HISTORY")
EVENTS_FILE = WORKFLOW_HISTORY_DIR / "events.jsonl"
SCHEMA_FILE = WORKFLOW_HISTORY_DIR / "schema/event-schema.json"


def load_schema() -> dict | None:
    """Load event schema from file."""
    if not SCHEMA_FILE.exists():
        console.print(f"[yellow]Warning: Schema file not found at {SCHEMA_FILE}[/yellow]")
        return None

    with open(SCHEMA_FILE) as f:
        return json.load(f)


def validate_events(verbose: bool = False) -> tuple[int, int, list[tuple[int, str, str]]]:
    """Validate all events in events.jsonl.

    Returns:
        (valid_count, invalid_count, errors_list)
        errors_list contains (line_number, event_preview, error_message)
    """
    if not EVENTS_FILE.exists():
        if verbose:
            console.print("[dim]No events.jsonl file found - nothing to validate[/dim]")
        return 0, 0, []

    schema = load_schema()
    if schema is None:
        console.print("[red]Cannot validate without schema[/red]")
        return 0, 0, []

    validator = Draft202012Validator(schema)

    valid_count = 0
    invalid_count = 0
    errors: list[tuple[int, str, str]] = []

    with open(EVENTS_FILE) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            # Parse JSON
            try:
                event = json.loads(line)
            except json.JSONDecodeError as e:
                invalid_count += 1
                errors.append((line_num, line[:50], f"Invalid JSON: {e}"))
                continue

            # Validate against schema
            validation_errors = list(validator.iter_errors(event))
            if validation_errors:
                invalid_count += 1
                error_msg = "; ".join(e.message for e in validation_errors[:2])
                preview = line[:50] + "..." if len(line) > 50 else line
                errors.append((line_num, preview, error_msg))
            else:
                valid_count += 1

    return valid_count, invalid_count, errors


def fix_invalid_events() -> tuple[int, int]:
    """Remove invalid events from events.jsonl.

    Returns:
        (kept_count, removed_count)
    """
    if not EVENTS_FILE.exists():
        return 0, 0

    schema = load_schema()
    if schema is None:
        return 0, 0

    validator = Draft202012Validator(schema)

    valid_lines = []
    removed_count = 0

    with open(EVENTS_FILE) as f:
        for line in f:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            try:
                event = json.loads(line_stripped)
                if validator.is_valid(event):
                    valid_lines.append(line_stripped)
                else:
                    removed_count += 1
            except json.JSONDecodeError:
                removed_count += 1

    # Write back valid lines
    with open(EVENTS_FILE, "w") as f:
        for line in valid_lines:
            f.write(line + "\n")

    return len(valid_lines), removed_count


def validate_schema_files() -> list[tuple[str, str]]:
    """Validate all schema files are valid JSON Schema.

    Returns:
        list of (filename, error_message) for invalid schemas
    """
    schema_dir = WORKFLOW_HISTORY_DIR / "schema"
    if not schema_dir.exists():
        return []

    errors = []
    for schema_file in schema_dir.glob("*.json"):
        try:
            with open(schema_file) as f:
                schema = json.load(f)

            # Basic schema structure check
            if "$schema" not in schema:
                errors.append((schema_file.name, "Missing $schema declaration"))

        except json.JSONDecodeError as e:
            errors.append((schema_file.name, f"Invalid JSON: {e}"))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate events against schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate events.jsonl
  uv run scripts/validate-schemas.py

  # Show validation details
  uv run scripts/validate-schemas.py --verbose

  # Remove invalid events
  uv run scripts/validate-schemas.py --fix

  # Use as pre-commit hook
  # Add to .pre-commit-config.yaml:
  #   - id: validate-workflow-schemas
  #     entry: uv run scripts/validate-schemas.py
  #     language: system
  #     pass_filenames: false
        """,
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show validation details",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Remove invalid events from events.jsonl",
    )
    parser.add_argument(
        "--check-schemas",
        action="store_true",
        help="Also validate schema files themselves",
    )

    args = parser.parse_args()

    exit_code = 0

    # Check schema files if requested
    if args.check_schemas:
        console.print("[bold]Checking schema files...[/bold]")
        schema_errors = validate_schema_files()
        if schema_errors:
            for filename, error in schema_errors:
                console.print(f"  [red]ERROR[/red] {filename}: {error}")
            exit_code = 1
        else:
            console.print("  [green]All schema files valid[/green]")
        console.print()

    # Fix mode
    if args.fix:
        console.print("[bold]Fixing invalid events...[/bold]")
        kept, removed = fix_invalid_events()
        if removed > 0:
            console.print(f"  [yellow]Removed {removed} invalid event(s)[/yellow]")
            console.print(f"  [green]Kept {kept} valid event(s)[/green]")
        else:
            console.print(f"  [green]All {kept} events are valid - nothing to fix[/green]")
        return 0

    # Validation mode
    console.print("[bold]Validating events.jsonl...[/bold]")
    valid, invalid, errors = validate_events(verbose=args.verbose)

    if invalid == 0:
        console.print(f"  [green]All {valid} events are valid[/green]")
    else:
        console.print(f"  [green]Valid: {valid}[/green]")
        console.print(f"  [red]Invalid: {invalid}[/red]")

        if args.verbose and errors:
            console.print("\n[bold]Validation errors:[/bold]")
            for line_num, preview, error_msg in errors:
                console.print(f"  Line {line_num}: [dim]{preview}[/dim]")
                console.print(f"           [red]{error_msg}[/red]")

        exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
