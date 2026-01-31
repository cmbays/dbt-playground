#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["click", "pyyaml", "jsonschema", "rich"]
# ///
"""
GitHub Operations - CLI for batch GitHub issue and milestone management.

Provides commands for:
- Issue creation (single and batch from YAML)
- YAML template validation
- Milestone management (create, list, status)

Usage:
    uv run scripts/github-ops.py issue create "Title" --body "Description"
    uv run scripts/github-ops.py issue batch docs/templates/issues/phase-3.yaml
    uv run scripts/github-ops.py issue validate temp/issues.yaml
    uv run scripts/github-ops.py milestone create "v0.8" --due "2026-02-28"
    uv run scripts/github-ops.py milestone list
    uv run scripts/github-ops.py milestone status "v0.8"
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import click
import yaml
from jsonschema import Draft202012Validator
from rich.console import Console
from rich.table import Table

console = Console()

# Schema file location
SCHEMA_FILE = Path(__file__).parent.parent / "docs/schemas/issue-template.schema.json"


def get_repo_info() -> tuple[str, str]:
    """Get the current repository owner and name."""
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
            capture_output=True,
            text=True,
            check=True,
        )
        owner_repo = result.stdout.strip()
        owner, repo = owner_repo.split("/")
        return owner, repo
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error getting repository info: {e.stderr}[/red]")
        sys.exit(1)
    except ValueError:
        console.print("[red]Error: Could not parse repository name[/red]")
        sys.exit(1)


def run_gh_command(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a gh CLI command and return the result."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=check,
        )
        return result
    except subprocess.CalledProcessError as e:
        console.print(f"[red]GitHub CLI error: {e.stderr}[/red]")
        raise


def load_yaml_template(file_path: Path) -> dict[str, Any]:
    """Load and parse a YAML template file."""
    if not file_path.exists():
        console.print(f"[red]Error: Template file not found: {file_path}[/red]")
        sys.exit(1)

    with open(file_path) as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            console.print(f"[red]Error parsing YAML: {e}[/red]")
            sys.exit(1)


def load_schema() -> dict[str, Any] | None:
    """Load the JSON schema for issue templates."""
    if not SCHEMA_FILE.exists():
        console.print(f"[yellow]Warning: Schema file not found at {SCHEMA_FILE}[/yellow]")
        return None

    with open(SCHEMA_FILE) as f:
        return json.load(f)


def validate_template(template: dict[str, Any]) -> list[str]:
    """Validate a template against the JSON schema.

    Returns:
        List of error messages (empty if valid)
    """
    schema = load_schema()
    if schema is None:
        return ["Schema file not found - cannot validate"]

    validator = Draft202012Validator(schema)
    errors = []

    for error in validator.iter_errors(template):
        path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        errors.append(f"{path}: {error.message}")

    return errors


# =============================================================================
# Issue Commands
# =============================================================================


@click.group()
def cli():
    """GitHub Operations CLI - Manage issues and milestones."""
    pass


@cli.group()
def issue():
    """Issue management commands."""
    pass


@issue.command("create")
@click.argument("title")
@click.option("--body", "-b", default="", help="Issue body/description")
@click.option("--label", "-l", multiple=True, help="Labels to apply (can be repeated)")
@click.option("--milestone", "-m", help="Milestone to assign")
@click.option("--assignee", "-a", help="User to assign")
@click.option("--body-file", type=click.Path(exists=True), help="Read body from file")
def issue_create(
    title: str,
    body: str,
    label: tuple[str, ...],
    milestone: str | None,
    assignee: str | None,
    body_file: str | None,
):
    """Create a single GitHub issue.

    Example:
        uv run scripts/github-ops.py issue create "Bug: fix login" --label bug --milestone v0.8
    """
    # Build command
    cmd = ["issue", "create", "--title", title]

    # Handle body
    if body_file:
        cmd.extend(["--body-file", body_file])
    elif body:
        cmd.extend(["--body", body])
    else:
        cmd.extend(["--body", ""])

    # Add labels
    for lbl in label:
        cmd.extend(["--label", lbl])

    # Add milestone
    if milestone:
        cmd.extend(["--milestone", milestone])

    # Add assignee
    if assignee:
        cmd.extend(["--assignee", assignee])

    console.print(f"[bold]Creating issue:[/bold] {title}")

    try:
        result = run_gh_command(cmd)
        # Parse issue URL from output
        issue_url = result.stdout.strip()
        console.print(f"[green]Created issue:[/green] {issue_url}")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to create issue: {e.stderr}[/red]")
        sys.exit(1)


@issue.command("batch")
@click.argument("template_file", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Show what would be created without creating")
def issue_batch(template_file: str, dry_run: bool):
    """Create multiple issues from a YAML template.

    TEMPLATE_FILE should be a YAML file with issue definitions.
    See docs/schemas/issue-template.schema.json for the schema.

    Example:
        uv run scripts/github-ops.py issue batch docs/templates/issues/phase-3.yaml
        uv run scripts/github-ops.py issue batch temp/issues.yaml --dry-run
    """
    template_path = Path(template_file)
    template = load_yaml_template(template_path)

    # Validate template
    errors = validate_template(template)
    if errors:
        console.print("[red]Template validation failed:[/red]")
        for error in errors:
            console.print(f"  - {error}")
        sys.exit(1)

    # Extract defaults
    defaults = template.get("defaults", {})
    default_labels = defaults.get("labels", [])
    default_milestone = defaults.get("milestone")
    default_assignee = defaults.get("assignee")

    issues = template.get("issues", [])

    if not issues:
        console.print("[yellow]No issues found in template[/yellow]")
        return

    console.print(f"[bold]Processing {len(issues)} issue(s)...[/bold]")

    if dry_run:
        console.print("[yellow]DRY RUN - No issues will be created[/yellow]\n")

    created_count = 0
    failed_count = 0

    for i, issue_def in enumerate(issues, 1):
        title = issue_def.get("title", "Untitled")
        description = issue_def.get("description", "")

        # Merge defaults with issue-specific values
        labels = issue_def.get("labels", []) + default_labels
        milestone = issue_def.get("milestone") or default_milestone
        assignee = issue_def.get("assignee") or default_assignee
        priority = issue_def.get("priority")

        # Add priority as a label if specified
        if priority:
            priority_label = f"priority:{priority}"
            if priority_label not in labels:
                labels.append(priority_label)

        console.print(f"\n[bold]Issue {i}/{len(issues)}:[/bold] {title}")

        if dry_run:
            console.print(f"  Description: {description[:50]}...")
            console.print(f"  Labels: {labels}")
            console.print(f"  Milestone: {milestone}")
            console.print(f"  Assignee: {assignee}")
            continue

        # Build command
        cmd = ["issue", "create", "--title", title, "--body", description]

        for lbl in labels:
            cmd.extend(["--label", lbl])

        if milestone:
            cmd.extend(["--milestone", milestone])

        if assignee:
            cmd.extend(["--assignee", assignee])

        try:
            result = run_gh_command(cmd)
            issue_url = result.stdout.strip()
            console.print(f"  [green]Created:[/green] {issue_url}")
            created_count += 1
        except subprocess.CalledProcessError as e:
            console.print(f"  [red]Failed:[/red] {e.stderr}")
            failed_count += 1

    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Created: [green]{created_count}[/green]")
    if failed_count > 0:
        console.print(f"  Failed: [red]{failed_count}[/red]")


@issue.command("validate")
@click.argument("template_file", type=click.Path(exists=True))
def issue_validate(template_file: str):
    """Validate a YAML issue template against the schema.

    Example:
        uv run scripts/github-ops.py issue validate docs/templates/issues/phase-3.yaml
    """
    template_path = Path(template_file)
    template = load_yaml_template(template_path)

    console.print(f"[bold]Validating:[/bold] {template_path}")

    errors = validate_template(template)

    if errors:
        console.print("\n[red]Validation FAILED[/red]")
        for error in errors:
            console.print(f"  - {error}")
        sys.exit(1)
    else:
        console.print("\n[green]Valid template[/green]")

        # Show summary
        issues = template.get("issues", [])
        defaults = template.get("defaults", {})

        console.print(f"  Version: {template.get('version', 'not specified')}")
        console.print(f"  Issues: {len(issues)}")
        if defaults:
            console.print(f"  Defaults: {defaults}")


# =============================================================================
# Milestone Commands
# =============================================================================


@cli.group()
def milestone():
    """Milestone management commands."""
    pass


@milestone.command("create")
@click.argument("title")
@click.option("--due", "-d", help="Due date (YYYY-MM-DD format)")
@click.option("--description", "-D", default="", help="Milestone description")
def milestone_create(title: str, due: str | None, description: str):
    """Create a new milestone.

    Example:
        uv run scripts/github-ops.py milestone create "v0.8" --due "2026-02-28"
        uv run scripts/github-ops.py milestone create "v0.9" --due "2026-03-31" --description "Data quality"
    """
    owner, repo = get_repo_info()

    # Build API request
    api_args = [
        "api",
        f"repos/{owner}/{repo}/milestones",
        "-f", f"title={title}",
    ]

    if description:
        api_args.extend(["-f", f"description={description}"])

    if due:
        # Convert YYYY-MM-DD to ISO 8601 format
        try:
            due_date = datetime.strptime(due, "%Y-%m-%d")
            due_iso = due_date.strftime("%Y-%m-%dT23:59:59Z")
            api_args.extend(["-f", f"due_on={due_iso}"])
        except ValueError:
            console.print(f"[red]Invalid date format: {due}. Use YYYY-MM-DD[/red]")
            sys.exit(1)

    console.print(f"[bold]Creating milestone:[/bold] {title}")

    try:
        result = run_gh_command(api_args)
        data = json.loads(result.stdout)
        console.print(f"[green]Created milestone #{data['number']}:[/green] {title}")
        if due:
            console.print(f"  Due: {due}")
        console.print(f"  URL: {data['html_url']}")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr
        if "already_exists" in error_msg.lower() or "422" in error_msg:
            console.print(f"[yellow]Milestone '{title}' already exists[/yellow]")
        else:
            console.print(f"[red]Failed to create milestone: {error_msg}[/red]")
        sys.exit(1)


@milestone.command("list")
@click.option("--state", type=click.Choice(["open", "closed", "all"]), default="all", help="Filter by state")
def milestone_list(state: str):
    """List all milestones.

    Example:
        uv run scripts/github-ops.py milestone list
        uv run scripts/github-ops.py milestone list --state open
    """
    owner, repo = get_repo_info()

    # For 'all', we need to fetch both open and closed separately
    if state == "all":
        milestones = []
        for ms_state in ["open", "closed"]:
            api_args = [
                "api",
                f"repos/{owner}/{repo}/milestones?state={ms_state}",
            ]
            try:
                result = run_gh_command(api_args)
                milestones.extend(json.loads(result.stdout))
            except subprocess.CalledProcessError:
                pass
    else:
        api_args = [
            "api",
            f"repos/{owner}/{repo}/milestones?state={state}",
        ]
        result = run_gh_command(api_args)
        milestones = json.loads(result.stdout)

    if not milestones:
        console.print("[yellow]No milestones found[/yellow]")
        return

    table = Table(title="Milestones")
    table.add_column("Title", style="bold")
    table.add_column("State")
    table.add_column("Due Date")
    table.add_column("Open")
    table.add_column("Closed")
    table.add_column("Progress")

    for ms in milestones:
        ms_title = ms["title"]
        ms_state = ms["state"]
        due_on = ms.get("due_on")
        open_issues = ms["open_issues"]
        closed_issues = ms["closed_issues"]
        total = open_issues + closed_issues

        # Format due date
        if due_on:
            due_date = datetime.fromisoformat(due_on.replace("Z", "+00:00"))
            due_str = due_date.strftime("%Y-%m-%d")
        else:
            due_str = "-"

        # Calculate progress
        if total > 0:
            progress = (closed_issues / total) * 100
            progress_str = f"{progress:.0f}%"
        else:
            progress_str = "-"

        # Color state
        state_style = "green" if ms_state == "open" else "dim"

        table.add_row(
            ms_title,
            f"[{state_style}]{ms_state}[/{state_style}]",
            due_str,
            str(open_issues),
            str(closed_issues),
            progress_str,
        )

    console.print(table)


@milestone.command("status")
@click.argument("title")
def milestone_status(title: str):
    """Show detailed status for a specific milestone.

    Example:
        uv run scripts/github-ops.py milestone status "v0.8"
    """
    owner, repo = get_repo_info()

    # Get all milestones (both open and closed) and find the one we want
    milestones = []
    for ms_state in ["open", "closed"]:
        api_args = [
            "api",
            f"repos/{owner}/{repo}/milestones?state={ms_state}",
        ]
        try:
            result = run_gh_command(api_args)
            milestones.extend(json.loads(result.stdout))
        except subprocess.CalledProcessError:
            pass

    # Find matching milestone
    milestone = None
    for ms in milestones:
        if ms["title"] == title:
            milestone = ms
            break

    try:
        if not milestone:
            console.print(f"[red]Milestone '{title}' not found[/red]")
            sys.exit(1)

        # Display milestone info
        console.print(f"\n[bold]Milestone: {title}[/bold]")
        console.print(f"  State: {milestone['state']}")

        if milestone.get("description"):
            console.print(f"  Description: {milestone['description']}")

        if milestone.get("due_on"):
            due_date = datetime.fromisoformat(milestone["due_on"].replace("Z", "+00:00"))
            console.print(f"  Due Date: {due_date.strftime('%Y-%m-%d')}")

            # Check if overdue
            if milestone["state"] == "open" and due_date < datetime.now(due_date.tzinfo):
                console.print("  [red]OVERDUE[/red]")

        open_issues = milestone["open_issues"]
        closed_issues = milestone["closed_issues"]
        total = open_issues + closed_issues

        console.print(f"\n[bold]Progress:[/bold]")
        console.print(f"  Open Issues: {open_issues}")
        console.print(f"  Closed Issues: {closed_issues}")
        console.print(f"  Total: {total}")

        if total > 0:
            progress = (closed_issues / total) * 100
            bar_width = 30
            filled = int(bar_width * progress / 100)
            bar = "[green]" + "=" * filled + "[/green]" + "-" * (bar_width - filled)
            console.print(f"  Progress: [{bar}] {progress:.1f}%")
        else:
            console.print("  Progress: No issues assigned")

        # Get issues in this milestone
        console.print(f"\n[bold]Issues:[/bold]")

        issues_result = run_gh_command([
            "issue", "list",
            "--milestone", title,
            "--state", "all",
            "--json", "number,title,state",
        ])
        issues = json.loads(issues_result.stdout)

        if issues:
            for issue in issues:
                state_icon = "[green]o[/green]" if issue["state"] == "OPEN" else "[dim]x[/dim]"
                console.print(f"  {state_icon} #{issue['number']}: {issue['title']}")
        else:
            console.print("  (no issues)")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to get milestone status: {e.stderr}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
