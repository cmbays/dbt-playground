#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "click>=8.0.0",
#   "pyyaml>=6.0.0",
#   "jsonschema>=4.0.0",
#   "rich>=13.0.0"
# ]
# ///

"""GitHub Operations CLI - Manage GitHub issues and milestones programmatically."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import click
import yaml
from jsonschema import ValidationError, validate
from rich.console import Console
from rich.table import Table

console = Console()


# === Utilities ===


def run_gh_command(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a gh CLI command and return the result.

    Args:
        args: Command arguments (without 'gh' prefix)
        check: Whether to raise exception on non-zero exit

    Returns:
        CompletedProcess with stdout, stderr, returncode

    Raises:
        subprocess.CalledProcessError: If check=True and command fails
    """
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


def load_yaml(file_path: str) -> dict[str, Any]:
    """Load and parse YAML file.

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML content as dict

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path) as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            console.print(f"[red]YAML error: {e}[/red]")
            raise


def load_schema(schema_path: str = "docs/schemas/issue-template.schema.json") -> dict[str, Any]:
    """Load JSON schema for validation.

    Args:
        schema_path: Path to JSON schema file

    Returns:
        Schema as dict

    Raises:
        FileNotFoundError: If schema doesn't exist
    """
    path = Path(schema_path)
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    with open(path) as f:
        return json.load(f)


def get_repo_context() -> tuple[str, str]:
    """Get current repo owner and name via gh CLI.

    Returns:
        Tuple of (owner, repo)

    Raises:
        RuntimeError: If can't determine repo context
    """
    try:
        result = run_gh_command(["repo", "view", "--json", "nameWithOwner"], check=True)
        data = json.loads(result.stdout)
        owner_repo = data.get("nameWithOwner", "")
        if "/" not in owner_repo:
            raise RuntimeError("Could not determine repo context")
        return tuple(owner_repo.split("/"))
    except Exception as e:
        raise RuntimeError(f"Failed to get repo context: {e}")


# === Issue Commands ===


@click.group()
def cli():
    """GitHub Operations CLI - Manage issues and milestones."""
    pass


@cli.group()
def issue():
    """Manage GitHub issues."""
    pass


@issue.command()
@click.argument("title")
@click.option(
    "--body",
    "-b",
    default="",
    help="Issue description/body",
)
@click.option(
    "--label",
    "-l",
    multiple=True,
    help="Labels to apply (can use multiple times)",
)
@click.option(
    "--milestone",
    "-m",
    default=None,
    help="Milestone to assign",
)
@click.option(
    "--assignee",
    "-a",
    default=None,
    help="User to assign",
)
def create(
    title: str,
    body: str,
    label: tuple[str, ...],
    milestone: str | None,
    assignee: str | None,
) -> None:
    """Create a single GitHub issue.

    Example:
        github-ops issue create "feat(staging): add model" \\
          --body "Implementation details" \\
          --label "enhancement" \\
          --milestone "v0.8"
    """
    try:
        cmd = ["issue", "create", "--title", title]

        if body:
            cmd.extend(["--body", body])

        for lbl in label:
            cmd.extend(["--label", lbl])

        if milestone:
            cmd.extend(["--milestone", milestone])

        if assignee:
            cmd.extend(["--assignee", assignee])

        result = run_gh_command(cmd, check=True)

        # Parse issue number from output
        output = result.stdout.strip()
        if "#" in output:
            issue_num = output.split("#")[1].split()[0]
            console.print(f"[green]✓[/green] Created issue #{issue_num}")
        else:
            console.print(f"[green]✓[/green] Issue created")
            console.print(output)

    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Failed to create issue")
        console.print(f"Error: {e.stderr}")
        sys.exit(1)


@issue.command()
@click.argument("template_file")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview without creating",
)
def batch(template_file: str, dry_run: bool) -> None:
    """Create multiple issues from YAML template.

    Example:
        github-ops issue batch docs/templates/issues/phase-3.yaml
        github-ops issue batch docs/templates/issues/phase-3.yaml --dry-run
    """
    try:
        # Load and validate template
        template = load_yaml(template_file)
        schema = load_schema()

        try:
            validate(instance=template, schema=schema)
        except ValidationError as e:
            console.print(f"[red]✗[/red] Template validation failed")
            console.print(f"Error: {e.message}")
            sys.exit(1)

        # Extract issues
        defaults = template.get("defaults", {})
        issues = template.get("issues", [])

        if not issues:
            console.print("[yellow]⚠[/yellow] No issues found in template")
            return

        # Show summary
        console.print(f"\n[cyan]Creating {len(issues)} issue(s)...[/cyan]")

        if dry_run:
            console.print("[yellow]DRY RUN[/yellow] - No issues will be created\n")

        # Process each issue
        for i, issue_def in enumerate(issues, 1):
            title = issue_def.get("title", "")
            body = issue_def.get("description", "")
            labels = issue_def.get("labels", defaults.get("labels", []))
            milestone = issue_def.get("milestone", defaults.get("milestone"))
            assignee = issue_def.get("assignee", defaults.get("assignee"))

            # Build label args
            label_args = []
            for lbl in labels:
                label_args.extend(["--label", lbl])

            # Preview
            console.print(f"\n[{i}] {title}")
            if milestone:
                console.print(f"    Milestone: {milestone}")
            if labels:
                console.print(f"    Labels: {', '.join(labels)}")
            if assignee:
                console.print(f"    Assignee: {assignee}")

            if dry_run:
                continue

            # Create issue
            try:
                cmd = ["issue", "create", "--title", title]
                if body:
                    cmd.extend(["--body", body])
                cmd.extend(label_args)
                if milestone:
                    cmd.extend(["--milestone", milestone])
                if assignee:
                    cmd.extend(["--assignee", assignee])

                result = run_gh_command(cmd, check=True)
                output = result.stdout.strip()
                if "#" in output:
                    issue_num = output.split("#")[1].split()[0]
                    console.print(f"    [green]✓[/green] Created #{issue_num}")
                else:
                    console.print(f"    [green]✓[/green] Created")

            except subprocess.CalledProcessError as e:
                console.print(f"    [red]✗[/red] Failed: {e.stderr}")

        console.print(f"\n[green]Done![/green]\n")

    except FileNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        sys.exit(1)


@issue.command()
@click.argument("template_file")
def validate(template_file: str) -> None:
    """Validate YAML template against schema.

    Example:
        github-ops issue validate docs/templates/issues/phase-3.yaml
    """
    try:
        template = load_yaml(template_file)
        schema = load_schema()

        try:
            validate(instance=template, schema=schema)
            console.print("[green]✓[/green] Valid template")
            console.print(f"  Version: {template.get('version')}")
            console.print(f"  Issues: {len(template.get('issues', []))}")
            defaults = template.get("defaults", {})
            if defaults:
                console.print(f"  Defaults: {defaults}")

        except ValidationError as e:
            console.print("[red]✗[/red] Invalid template")
            console.print(f"Error: {e.message}")
            console.print(f"Path: {' → '.join(str(p) for p in e.path)}")
            sys.exit(1)

    except FileNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        sys.exit(1)


# === Milestone Commands ===


@cli.group()
def milestone():
    """Manage GitHub milestones."""
    pass


@milestone.command()
@click.argument("title")
@click.option(
    "--due",
    "-d",
    default=None,
    help="Due date (YYYY-MM-DD)",
)
@click.option(
    "--description",
    "-b",
    default=None,
    help="Milestone description",
)
def create(title: str, due: str | None, description: str | None) -> None:
    """Create a GitHub milestone.

    Example:
        github-ops milestone create "v0.8" --due "2026-02-28" --description "GitHub Project Management"
    """
    try:
        owner, repo = get_repo_context()

        # Build API call
        cmd = ["api", f"repos/{owner}/{repo}/milestones", "-f", f"title={title}"]

        if due:
            # Convert YYYY-MM-DD to ISO 8601
            cmd.extend(["-f", f"due_on={due}T23:59:59Z"])

        if description:
            cmd.extend(["-f", f"description={description}"])

        result = run_gh_command(cmd, check=True)
        data = json.loads(result.stdout)

        console.print(f"[green]✓[/green] Created milestone: {title}")
        if due:
            console.print(f"  Due: {due}")
        if data.get("number"):
            console.print(f"  Number: {data['number']}")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Failed to create milestone")
        console.print(f"Error: {e.stderr}")
        sys.exit(1)


@milestone.command()
def list() -> None:
    """List all milestones with progress.

    Example:
        github-ops milestone list
    """
    try:
        owner, repo = get_repo_context()

        # Fetch milestones in both states
        open_result = run_gh_command(
            ["api", f"repos/{owner}/{repo}/milestones", "-f", "state=open"],
            check=True,
        )
        closed_result = run_gh_command(
            ["api", f"repos/{owner}/{repo}/milestones", "-f", "state=closed"],
            check=True,
        )

        open_milestones = json.loads(open_result.stdout)
        closed_milestones = json.loads(closed_result.stdout)

        all_milestones = open_milestones + closed_milestones

        if not all_milestones:
            console.print("[yellow]⚠[/yellow] No milestones found")
            return

        # Build table
        table = Table(title="Milestones")
        table.add_column("Title", style="cyan")
        table.add_column("State", style="green")
        table.add_column("Open", justify="right")
        table.add_column("Closed", justify="right")
        table.add_column("Due Date")

        for m in sorted(all_milestones, key=lambda x: x.get("title", "")):
            title = m.get("title", "")
            state = "open" if m.get("state") == "open" else "closed"
            open_count = m.get("open_issues", 0)
            closed_count = m.get("closed_issues", 0)
            due_on = m.get("due_on", "")
            if due_on:
                due_on = due_on.split("T")[0]

            table.add_row(title, state, str(open_count), str(closed_count), due_on)

        console.print(table)

    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Failed to list milestones")
        console.print(f"Error: {e.stderr}")
        sys.exit(1)


@milestone.command()
@click.argument("title")
def status(title: str) -> None:
    """Show detailed status of a milestone.

    Example:
        github-ops milestone status "v0.8"
    """
    try:
        owner, repo = get_repo_context()

        # Fetch all milestones to find the one we want
        cmd = ["api", f"repos/{owner}/{repo}/milestones", "--paginate"]
        result = run_gh_command(cmd, check=True)

        milestones = json.loads(result.stdout)
        milestone = None

        for m in milestones:
            if m.get("title") == title:
                milestone = m
                break

        if not milestone:
            console.print(f"[red]Milestone '{title}' not found[/red]")
            sys.exit(1)

        # Display status
        console.print(f"\n[cyan]{title}[/cyan]")
        console.print("─" * 40)

        state = milestone.get("state", "unknown")
        open_issues = milestone.get("open_issues", 0)
        closed_issues = milestone.get("closed_issues", 0)
        total = open_issues + closed_issues
        due_on = milestone.get("due_on", "")

        console.print(f"State:        {state}")
        console.print(f"Due Date:     {due_on.split('T')[0] if due_on else 'None'}")
        console.print(f"Open Issues:  {open_issues}")
        console.print(f"Closed Issues: {closed_issues}")
        console.print(f"Total:        {total}")

        if total > 0:
            progress = (closed_issues / total) * 100
            console.print(f"Progress:     {progress:.0f}%")

        console.print()

    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Failed to get milestone status")
        console.print(f"Error: {e.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
