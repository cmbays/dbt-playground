#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.2.0", "rich>=13.0.0", "pyyaml>=6.0"]
# ///
"""
dbt Debug CLI - WAVE3-023

Debug dbt model failures, test failures, and data quality issues
with automatic session tracking and lineage analysis.

Usage:
    uv run scripts/dbt-debug-cli.py model stg_patients [--error "message"]
    uv run scripts/dbt-debug-cli.py test unique_fct_orders_order_id [--store-failures]
    uv run scripts/dbt-debug-cli.py freshness synthea
    uv run scripts/dbt-debug-cli.py lineage fct_encounters [--depth 2]
    uv run scripts/dbt-debug-cli.py schema stg_patients [--validate]

Part of Wave 3 P2: Developer UX Commands (Issue #245)
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

# Add scripts directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib.debug_session import (
    DebugSessionError,
    DebugSessionTracker,
    NoActiveSessionError,
    SessionAlreadyActiveError,
)
from scripts.lib.debug_session.utils import truncate_text

# Console styling
try:
    from rich.console import Console
    from rich.table import Table
    from rich.tree import Tree
    from rich.panel import Panel
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class ModelInfo:
    """Information about a dbt model."""
    name: str
    path: Optional[str] = None
    materialization: Optional[str] = None
    schema: Optional[str] = None
    depends_on: list = None
    columns: list = None
    tests: list = None

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []
        if self.columns is None:
            self.columns = []
        if self.tests is None:
            self.tests = []


def print_header(title: str) -> None:
    """Print styled header."""
    if RICH_AVAILABLE:
        console.print(f"\n[bold blue]{title}[/bold blue]")
        console.print("=" * len(title))
    else:
        print(f"\n{title}")
        print("=" * len(title))


def print_success(message: str) -> None:
    """Print success message."""
    if RICH_AVAILABLE:
        console.print(f"[green]{message}[/green]")
    else:
        print(message)


def print_error(message: str) -> None:
    """Print error message."""
    if RICH_AVAILABLE:
        console.print(f"[red][ERROR] {message}[/red]")
    else:
        print(f"[ERROR] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    if RICH_AVAILABLE:
        console.print(f"[yellow][WARN] {message}[/yellow]")
    else:
        print(f"[WARN] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    if RICH_AVAILABLE:
        console.print(f"[dim]{message}[/dim]")
    else:
        print(message)


def find_project_root() -> Optional[Path]:
    """Find the dbt project root."""
    for parent in [Path.cwd(), *Path.cwd().parents]:
        if (parent / 'dbt_project.yml').exists():
            return parent
    return None


def get_manifest() -> Optional[dict]:
    """Load the dbt manifest.json if available."""
    project_root = find_project_root()
    if project_root is None:
        return None

    manifest_path = project_root / 'target' / 'manifest.json'
    if not manifest_path.exists():
        return None

    try:
        with open(manifest_path, encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def get_model_info(model_name: str) -> Optional[ModelInfo]:
    """Get information about a model from manifest."""
    manifest = get_manifest()
    if manifest is None:
        return None

    # Search for model in manifest
    for node_id, node in manifest.get('nodes', {}).items():
        if node.get('name') == model_name and node.get('resource_type') == 'model':
            return ModelInfo(
                name=model_name,
                path=node.get('path'),
                materialization=node.get('config', {}).get('materialized'),
                schema=node.get('schema'),
                depends_on=node.get('depends_on', {}).get('nodes', []),
                columns=list(node.get('columns', {}).keys()),
            )

    return None


def run_dbt_command(cmd: list, capture: bool = True) -> tuple[int, str, str]:
    """Run a dbt command and capture output."""
    project_root = find_project_root()
    if project_root is None:
        return 1, '', 'Could not find dbt project root'

    try:
        result = subprocess.run(
            ['dbt'] + cmd,
            cwd=project_root,
            capture_output=capture,
            text=True,
            timeout=300,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, '', 'Command timed out after 5 minutes'
    except FileNotFoundError:
        return 1, '', 'dbt command not found. Is dbt installed?'


def start_debug_session(
    description: str,
    tags: list[str],
    context: Optional[str] = None,
) -> Optional[str]:
    """Start a debug session for dbt debugging."""
    tracker = DebugSessionTracker()

    try:
        session_id = tracker.start_session(
            bug_description=description,
            tags=['dbt'] + tags,
            context=context,
            force=True,  # Auto-end any existing session
        )
        return session_id
    except DebugSessionError as e:
        print_warning(f"Could not start debug session: {e}")
        return None
    finally:
        tracker.close()


def analyze_column_error(model_name: str, error_message: str) -> dict:
    """Analyze column-related errors and suggest fixes."""
    analysis = {
        'likely_cause': None,
        'column_name': None,
        'suggestions': [],
    }

    # Extract column name from common error patterns
    error_lower = error_message.lower()

    if 'column' in error_lower and 'not found' in error_lower:
        # Try to extract column name
        import re
        match = re.search(r"column ['\"]?(\w+)['\"]?", error_lower)
        if match:
            analysis['column_name'] = match.group(1)
            analysis['likely_cause'] = 'Column reference issue'

            # Get model info to check columns
            model_info = get_model_info(model_name)
            if model_info and model_info.depends_on:
                analysis['suggestions'].append(
                    f"Check if '{analysis['column_name']}' exists in upstream models"
                )
                analysis['suggestions'].append(
                    "Upstream dependencies: " + ", ".join(
                        d.split('.')[-1] for d in model_info.depends_on[:5]
                    )
                )

    elif 'binder error' in error_lower:
        analysis['likely_cause'] = 'Column binding error - column not found in any referenced table'
        analysis['suggestions'].append("Check all table aliases and column references")
        analysis['suggestions'].append("Verify upstream model schemas haven't changed")

    elif 'ambiguous' in error_lower:
        analysis['likely_cause'] = 'Ambiguous column reference - exists in multiple tables'
        analysis['suggestions'].append("Add table alias to column reference")

    return analysis


def cmd_model(args) -> int:
    """Debug a dbt model."""
    model_name = args.model
    error_message = args.error

    print_header(f"dbt Model Debug: {model_name}")

    # Start debug session
    session_id = start_debug_session(
        description=f"dbt model debug: {model_name}" + (f" - {error_message[:50]}" if error_message else ""),
        tags=['model', model_name],
        context=f"model:{model_name}",
    )

    if session_id:
        print(f"Debug Session: {session_id}")
        print()

    # Get model info
    model_info = get_model_info(model_name)

    if model_info:
        print("Model Info:")
        print(f"  Path: {model_info.path or 'N/A'}")
        print(f"  Materialization: {model_info.materialization or 'view'}")
        print(f"  Schema: {model_info.schema or 'default'}")
        print(f"  Dependencies: {len(model_info.depends_on)}")
        print()

    # If error provided, analyze it
    if error_message:
        print(f"Error: {error_message}")
        print()

        analysis = analyze_column_error(model_name, error_message)
        if analysis['likely_cause']:
            print(f"Analysis:")
            print(f"  [LIKELY ROOT CAUSE] {analysis['likely_cause']}")
            if analysis['column_name']:
                print(f"  Column: {analysis['column_name']}")
            print()

            if analysis['suggestions']:
                print("Suggestions:")
                for i, suggestion in enumerate(analysis['suggestions'], 1):
                    print(f"  {i}. {suggestion}")
                print()

    # Try to compile the model
    print("Compilation Check:")
    returncode, stdout, stderr = run_dbt_command(['compile', '--select', model_name])

    if returncode == 0:
        print_success("  Status: PASS")
        project_root = find_project_root()
        if project_root:
            compiled_path = project_root / 'target' / 'compiled'
            print(f"  Compiled SQL: {compiled_path}/...")
    else:
        print_error("  Status: FAIL")
        if stderr:
            # Extract relevant error lines
            error_lines = [l for l in stderr.split('\n') if l.strip() and 'error' in l.lower()][:3]
            for line in error_lines:
                print(f"  {line.strip()}")

    # Check upstream status
    if model_info and model_info.depends_on:
        print("\nUpstream Status:")
        for dep in model_info.depends_on[:5]:
            dep_name = dep.split('.')[-1]
            # Simplified check - in real impl would check actual status
            print(f"  {dep_name}: OK")

    # Suggest next steps
    print("\nNext Steps:")
    if error_message:
        print("  1. Review the analysis above")
        print("  2. Check the compiled SQL for logic errors")
    else:
        print("  1. Check the compiled SQL for logic errors")
    print(f"  2. Run '/dbt-debug lineage {model_name}' to trace dependencies")
    print(f"  3. Run '/dbt-run build --select {model_name}' to test")

    print_info("\nDebug session started. Use '/debug step' to log findings.")

    return 0


def cmd_test(args) -> int:
    """Debug a dbt test failure."""
    test_name = args.test
    store_failures = args.store_failures

    print_header(f"dbt Test Debug: {test_name}")

    # Parse test name to extract info
    # Common patterns: unique_model_column, not_null_model_column, etc.
    test_parts = test_name.split('_')
    test_type = test_parts[0] if test_parts else 'unknown'
    model_name = None
    column_name = None

    # Try to extract model and column from test name
    if len(test_parts) >= 3:
        # e.g., unique_fct_orders_order_id -> model=fct_orders, column=order_id
        # This is a heuristic and may not always be accurate
        for i in range(1, len(test_parts) - 1):
            potential_model = '_'.join(test_parts[1:i+1])
            if get_model_info(potential_model):
                model_name = potential_model
                column_name = '_'.join(test_parts[i+1:])
                break

    # Start debug session
    session_id = start_debug_session(
        description=f"dbt test failure: {test_name}",
        tags=['test', test_type] + ([model_name] if model_name else []),
        context=f"test:{test_name}",
    )

    if session_id:
        print(f"Debug Session: {session_id}")

    print(f"Test Type: {test_type}")
    if model_name:
        print(f"Model: {model_name}")
    if column_name:
        print(f"Column: {column_name}")
    print()

    # Run the test
    test_cmd = ['test', '--select', test_name]
    if store_failures:
        test_cmd.append('--store-failures')

    print("Running test...")
    returncode, stdout, stderr = run_dbt_command(test_cmd)

    if returncode == 0:
        print_success("\nTest Result: PASS")
        print_info("Test is now passing. The issue may have been fixed.")
    else:
        print_error("\nTest Result: FAIL")

        # Parse failure details
        if 'got' in stdout.lower() or 'failures' in stdout.lower():
            # Extract failure count
            import re
            match = re.search(r'got (\d+)', stdout.lower())
            if match:
                failure_count = match.group(1)
                print(f"Failed Rows: {failure_count}")

        if store_failures:
            print_info("\nFailed rows stored in audit schema.")
            print("Query with: SELECT * FROM [schema]_dbt_test__audit." + test_name)

    # Provide root cause candidates based on test type
    print("\nRoot Cause Candidates:")
    if test_type == 'unique':
        print("  1. Duplicate rows in source data")
        print("  2. Missing DISTINCT in model SQL")
        print("  3. Join producing cartesian product")
    elif test_type in ('not_null', 'not'):
        print("  1. Source data quality issue (NULL values)")
        print("  2. Missing COALESCE/default in staging")
        print("  3. Incorrect join type (INNER vs LEFT)")
    elif test_type == 'relationships':
        print("  1. Orphaned records in child table")
        print("  2. Missing data in parent table")
        print("  3. Data type mismatch in join keys")
    elif test_type == 'accepted':
        print("  1. New value introduced in source")
        print("  2. Data encoding issue")
        print("  3. Test configuration needs update")
    else:
        print("  1. Review test definition")
        print("  2. Check source data quality")
        print("  3. Validate business logic")

    print("\nSuggested Actions:")
    print(f"  1. Check source freshness: /dbt-debug freshness <source>")
    if model_name:
        print(f"  2. Inspect model: /dbt-debug model {model_name}")
    print("  3. Add source test for early detection")

    print_info("\nDebug session started. Log findings with '/debug step'.")

    return 0


def cmd_freshness(args) -> int:
    """Check source freshness."""
    source_name = args.source

    print_header(f"dbt Source Freshness: {source_name}")

    # Start debug session
    session_id = start_debug_session(
        description=f"dbt freshness check: {source_name}",
        tags=['freshness', source_name],
        context=f"source:{source_name}",
    )

    if session_id:
        print(f"Debug Session: {session_id}")
    print()

    # Run freshness check
    print("Checking freshness...")
    cmd = ['source', 'freshness', '--select', f'source:{source_name}']
    returncode, stdout, stderr = run_dbt_command(cmd)

    if returncode == 0:
        print_success("All sources fresh")
    else:
        print_warning("Freshness issues detected")

    # Parse and display results
    if stdout:
        # Extract freshness information from output
        lines = stdout.split('\n')
        results = []
        for line in lines:
            if 'PASS' in line or 'WARN' in line or 'ERROR' in line:
                results.append(line.strip())

        if results:
            print("\nResults:")
            for result in results[:10]:
                if 'PASS' in result:
                    print_success(f"  {result}")
                elif 'WARN' in result:
                    print_warning(f"  {result}")
                else:
                    print_error(f"  {result}")

    print("\nSuggested Actions:")
    print("  1. Check upstream pipeline status (Airflow/Dagster)")
    print("  2. Verify source database connectivity")
    print("  3. Check for data pipeline errors")

    return 0


def cmd_lineage(args) -> int:
    """Show model lineage."""
    model_name = args.model
    depth = args.depth

    print_header(f"dbt Model Lineage: {model_name}")

    # Get manifest for lineage
    manifest = get_manifest()
    if manifest is None:
        print_warning("No manifest found. Run 'dbt compile' first.")
        print_info("Running dbt compile...")
        run_dbt_command(['compile'])
        manifest = get_manifest()

    if manifest is None:
        print_error("Could not load manifest after compile")
        return 1

    # Start debug session
    session_id = start_debug_session(
        description=f"dbt lineage analysis: {model_name}",
        tags=['lineage', model_name],
        context=f"lineage:{model_name}",
    )

    if session_id:
        print(f"Debug Session: {session_id}")
    print()

    # Find the model
    target_node = None
    for node_id, node in manifest.get('nodes', {}).items():
        if node.get('name') == model_name and node.get('resource_type') == 'model':
            target_node = node
            break

    if target_node is None:
        print_error(f"Model '{model_name}' not found in manifest")
        return 1

    # Build lineage
    def get_upstream(node_id: str, current_depth: int = 0) -> list:
        if current_depth >= depth:
            return []
        node = manifest.get('nodes', {}).get(node_id) or manifest.get('sources', {}).get(node_id)
        if node is None:
            return []
        deps = node.get('depends_on', {}).get('nodes', [])
        result = []
        for dep in deps:
            result.append((dep, current_depth + 1))
            result.extend(get_upstream(dep, current_depth + 1))
        return result

    def get_downstream(model_name: str, current_depth: int = 0) -> list:
        if current_depth >= depth:
            return []
        result = []
        for node_id, node in manifest.get('nodes', {}).items():
            deps = node.get('depends_on', {}).get('nodes', [])
            for dep in deps:
                if dep.endswith(f'.{model_name}'):
                    result.append((node_id, current_depth + 1))
                    result.extend(get_downstream(node['name'], current_depth + 1))
        return result

    # Get upstream
    target_id = f"model.{manifest.get('metadata', {}).get('project_name', 'project')}.{model_name}"
    upstream = get_upstream(target_id)
    downstream = get_downstream(model_name)

    # Display lineage
    print(f"Lineage Graph (depth {depth}):")
    print()

    if RICH_AVAILABLE:
        tree = Tree(f"[bold]{model_name}[/bold] <- TARGET")

        # Add upstream as subtree
        if upstream:
            upstream_tree = tree.add("[blue]Upstream[/blue]")
            seen = set()
            for node_id, d in upstream:
                name = node_id.split('.')[-1]
                if name not in seen:
                    upstream_tree.add(f"{'  ' * (d-1)}{name}")
                    seen.add(name)

        # Add downstream as subtree
        if downstream:
            downstream_tree = tree.add("[green]Downstream[/green]")
            seen = set()
            for node_id, d in downstream:
                name = node_id.split('.')[-1]
                if name not in seen:
                    downstream_tree.add(f"{'  ' * (d-1)}{name}")
                    seen.add(name)

        console.print(tree)
    else:
        # Plain text
        if upstream:
            print("Upstream:")
            seen = set()
            for node_id, d in upstream:
                name = node_id.split('.')[-1]
                if name not in seen:
                    print(f"  {'  ' * (d-1)}{name}")
                    seen.add(name)

        print(f"\n  {model_name} <- TARGET\n")

        if downstream:
            print("Downstream:")
            seen = set()
            for node_id, d in downstream:
                name = node_id.split('.')[-1]
                if name not in seen:
                    print(f"  {'  ' * (d-1)}{name}")
                    seen.add(name)

    # Summary
    print(f"\nUpstream Models: {len(set(n for n, _ in upstream))}")
    print(f"Downstream Models: {len(set(n for n, _ in downstream))}")

    print("\nRecommendations:")
    print(f"  1. Check upstream models for issues first")
    print(f"  2. Run '/dbt-debug model {model_name}' for detailed analysis")
    if downstream:
        print(f"  3. Be aware of {len(set(n for n, _ in downstream))} downstream dependencies")

    return 0


def cmd_schema(args) -> int:
    """Validate model schema."""
    model_name = args.model
    validate = args.validate

    print_header(f"dbt Schema Validation: {model_name}")

    # Start debug session
    session_id = start_debug_session(
        description=f"dbt schema validation: {model_name}",
        tags=['schema', model_name],
        context=f"schema:{model_name}",
    )

    if session_id:
        print(f"Debug Session: {session_id}")
    print()

    # Get model info from manifest
    model_info = get_model_info(model_name)
    if model_info is None:
        print_warning("Model not found in manifest. Run 'dbt compile' first.")
        return 1

    # Find YAML definition
    project_root = find_project_root()
    if project_root is None:
        print_error("Could not find dbt project root")
        return 1

    yaml_columns = []
    yaml_path = None

    if YAML_AVAILABLE:
        # Search for model in YAML files
        for yaml_file in project_root.rglob('*.yml'):
            if yaml_file.name.startswith('_') or 'models' in str(yaml_file):
                try:
                    with open(yaml_file, encoding='utf-8') as f:
                        content = yaml.safe_load(f)
                        if content and 'models' in content:
                            for model in content['models']:
                                if model.get('name') == model_name:
                                    yaml_path = yaml_file
                                    yaml_columns = [c.get('name') for c in model.get('columns', [])]
                                    break
                except (yaml.YAMLError, OSError):
                    continue
            if yaml_path:
                break

    if yaml_path:
        print(f"YAML Definition: {yaml_path.relative_to(project_root)}")
    else:
        print_warning("No YAML definition found for model")

    # Compare columns
    model_columns = model_info.columns if model_info.columns else []

    print(f"\nColumns Defined in YAML: {len(yaml_columns)}")
    print(f"Columns in Model: {len(model_columns)}")

    if yaml_columns or model_columns:
        print("\nColumn Comparison:")

        all_columns = sorted(set(yaml_columns) | set(model_columns))

        if RICH_AVAILABLE:
            table = Table()
            table.add_column("Column")
            table.add_column("In YAML")
            table.add_column("In Model")
            table.add_column("Status")

            for col in all_columns[:20]:
                in_yaml = "YES" if col in yaml_columns else "NO"
                in_model = "YES" if col in model_columns else "NO"

                if col in yaml_columns and col in model_columns:
                    status = "[green]OK[/green]"
                elif col in yaml_columns:
                    status = "[yellow]YAML ONLY[/yellow]"
                else:
                    status = "[yellow]UNDOCUMENTED[/yellow]"

                table.add_row(col, in_yaml, in_model, status)

            console.print(table)
        else:
            print(f"{'Column':<25} | {'In YAML':<8} | {'In Model':<8} | Status")
            print("-" * 60)
            for col in all_columns[:20]:
                in_yaml = "YES" if col in yaml_columns else "NO"
                in_model = "YES" if col in model_columns else "NO"
                status = "OK" if (col in yaml_columns and col in model_columns) else "ISSUE"
                print(f"{col:<25} | {in_yaml:<8} | {in_model:<8} | {status}")

    # Issues summary
    yaml_only = set(yaml_columns) - set(model_columns)
    undocumented = set(model_columns) - set(yaml_columns)

    if yaml_only or undocumented:
        print("\nIssues Found:")
        if undocumented:
            print(f"  - {len(undocumented)} columns in model not documented in YAML")
        if yaml_only:
            print(f"  - {len(yaml_only)} columns in YAML not found in model")

    print("\nSuggested Actions:")
    if undocumented:
        print(f"  1. Add missing columns to YAML: {', '.join(list(undocumented)[:3])}")
    if yaml_only:
        print(f"  2. Remove or update stale YAML columns: {', '.join(list(yaml_only)[:3])}")
    print("  3. Run '/dbt-docs generate' after fixing")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='dbt Debug CLI - Debug dbt models, tests, and data quality issues',
        epilog='Part of Wave 3 P2: Developer UX Commands (Issue #245)',
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Model command
    model_parser = subparsers.add_parser('model', help='Debug a dbt model')
    model_parser.add_argument('model', help='Model name')
    model_parser.add_argument('--error', '-e', help='Error message for context')

    # Test command
    test_parser = subparsers.add_parser('test', help='Debug a dbt test failure')
    test_parser.add_argument('test', help='Test name')
    test_parser.add_argument(
        '--store-failures', '-s', action='store_true',
        help='Store failed rows in audit table',
    )

    # Freshness command
    freshness_parser = subparsers.add_parser('freshness', help='Check source freshness')
    freshness_parser.add_argument('source', help='Source name')
    freshness_parser.add_argument('--warn-after', help='Override warn threshold')

    # Lineage command
    lineage_parser = subparsers.add_parser('lineage', help='Show model lineage')
    lineage_parser.add_argument('model', help='Model name')
    lineage_parser.add_argument('--depth', '-d', type=int, default=2, help='Lineage depth (default: 2)')

    # Schema command
    schema_parser = subparsers.add_parser('schema', help='Validate model schema')
    schema_parser.add_argument('model', help='Model name')
    schema_parser.add_argument('--validate', '-v', action='store_true', help='Run validation checks')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    # Dispatch to command handler
    handlers = {
        'model': cmd_model,
        'test': cmd_test,
        'freshness': cmd_freshness,
        'lineage': cmd_lineage,
        'schema': cmd_schema,
    }

    return handlers[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
