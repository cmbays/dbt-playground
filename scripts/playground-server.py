#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["flask", "flask-cors"]
# ///
"""
Local server for playground tools.
Provides read-only access to project files for visualization.

Usage:
    uv run scripts/playground-server.py

Then open http://localhost:5050 in your browser.
Playgrounds will auto-detect the server and load data automatically.
"""

import json
import subprocess
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PLAYGROUNDS_DIR = PROJECT_ROOT / "playgrounds"
TEMP_DIR = PROJECT_ROOT / "temp"

# Flask app
app = Flask(__name__, static_folder=str(PLAYGROUNDS_DIR))
CORS(app)  # Allow browser access from file:// URLs


# --- Static File Routes ---


@app.route("/")
def index():
    """Serve the Workflow Hub as the default page."""
    return send_from_directory(app.static_folder, "workflow-hub.html")


@app.route("/playgrounds/<path:filename>")
def serve_playground(filename):
    """Serve playground HTML files."""
    return send_from_directory(app.static_folder, filename)


# --- Git API Routes ---


@app.route("/api/worktrees")
def get_worktrees():
    """Return git worktree list output (porcelain format)."""
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return jsonify(
        {
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
        }
    )


@app.route("/api/git-status")
def get_git_status():
    """Return git status -sb output."""
    result = subprocess.run(
        ["git", "status", "-sb"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return jsonify(
        {
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
        }
    )


@app.route("/api/git-status-porcelain")
def get_git_status_porcelain():
    """Return git status --porcelain for detailed file status."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return jsonify(
        {
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
        }
    )


@app.route("/api/git-log")
def get_git_log():
    """Return last N commits (default 10, max 100)."""
    count_str = request.args.get("count", "10")

    # Validate count parameter to prevent command injection
    try:
        count = int(count_str)
        if count < 1:
            count = 1
        elif count > 100:
            count = 100
    except ValueError:
        count = 10  # Default on invalid input

    result = subprocess.run(
        ["git", "log", "--oneline", f"-{count}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return jsonify(
        {
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
        }
    )


@app.route("/api/git-branch")
def get_git_branch():
    """Return current branch name."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return jsonify(
        {
            "branch": result.stdout.strip(),
            "error": result.stderr if result.returncode != 0 else None,
        }
    )


# --- Workflow State API Routes ---


@app.route("/api/workflow-state")
def get_workflow_state():
    """Return WORKFLOW_STATE.md contents."""
    path = TEMP_DIR / "WORKFLOW_STATE.md"
    if path.exists():
        return jsonify({"content": path.read_text(), "error": None})
    return jsonify({"content": None, "error": "File not found"})


@app.route("/api/session-summaries")
def get_session_summaries():
    """Return list of SESSION_SUMMARY files (most recent first)."""
    summaries = sorted(
        TEMP_DIR.glob("SESSION_SUMMARY_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return jsonify(
        {
            "files": [
                {"name": p.name, "content": p.read_text()} for p in summaries[:5]
            ],
            "error": None,
        }
    )


@app.route("/api/agent-reports")
def get_agent_reports():
    """Return list of agent report folders and their contents."""
    reports_dir = TEMP_DIR / "AGENT_REPORTS"
    if not reports_dir.exists():
        return jsonify({"reports": [], "error": None})

    reports = []
    for folder in reports_dir.iterdir():
        if folder.is_dir() and folder.name != "README.md":
            report_files = []
            for f in folder.glob("*.md"):
                report_files.append(
                    {
                        "name": f.name,
                        "content": f.read_text(),
                        "modified": f.stat().st_mtime,
                    }
                )
            reports.append(
                {
                    "feature": folder.name,
                    "files": sorted(report_files, key=lambda x: x["modified"], reverse=True),
                }
            )

    return jsonify({"reports": reports, "error": None})


# --- Combined Data Endpoint ---


@app.route("/api/all")
def get_all_data():
    """Return all data in a single request for initial page load."""
    # Git data
    worktrees = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    status = subprocess.run(
        ["git", "status", "-sb"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    log = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    # Workflow state
    workflow_path = TEMP_DIR / "WORKFLOW_STATE.md"
    workflow_content = workflow_path.read_text() if workflow_path.exists() else None

    # Session summaries
    summaries = sorted(
        TEMP_DIR.glob("SESSION_SUMMARY_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    session_content = summaries[0].read_text() if summaries else None

    return jsonify(
        {
            "worktrees": worktrees.stdout,
            "gitStatus": status.stdout,
            "gitLog": log.stdout,
            "workflowState": workflow_content,
            "sessionSummary": session_content,
        }
    )


# --- Health Check ---


@app.route("/api/health")
def health_check():
    """Health check endpoint for detecting if server is running."""
    return jsonify({"status": "ok", "project": "dbt-playground"})


# --- Main ---

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Playground Server")
    print("=" * 50)
    print(f"\n  Project: {PROJECT_ROOT}")
    print(f"\n  URLs:")
    print(f"    Hub:        http://localhost:5050/")
    print(f"    Worktrees:  http://localhost:5050/playgrounds/worktree-coordinator.html")
    print(f"    Mermaid:    http://localhost:5050/playgrounds/mermaid-designer.html")
    print(f"\n  API Endpoints:")
    print(f"    GET /api/health          - Health check")
    print(f"    GET /api/all             - All data (combined)")
    print(f"    GET /api/worktrees       - Git worktree list")
    print(f"    GET /api/git-status      - Git status")
    print(f"    GET /api/git-log         - Recent commits")
    print(f"    GET /api/workflow-state  - WORKFLOW_STATE.md")
    print(f"    GET /api/session-summaries - Session summaries")
    print(f"    GET /api/agent-reports   - Agent reports")
    print(f"\n  Press Ctrl+C to stop\n")
    print("=" * 50 + "\n")

    app.run(port=5050, debug=False)
