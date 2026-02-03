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

v0.7.0 - Added session-states and github-issues endpoints for Workflow Hub
"""

import json
import subprocess
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
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


# --- Session State API Routes (v0.7) ---


@app.route("/api/session-states")
def get_session_states():
    """Return all SESSION_STATE files for Workflow Hub v0.7."""
    states_dir = TEMP_DIR / "SESSION_STATE"
    if not states_dir.exists():
        return jsonify({"sessions": [], "error": None})

    sessions = []
    for f in states_dir.glob("*.md"):
        if f.name == ".gitkeep":
            continue
        try:
            content = f.read_text()
            sessions.append({
                "id": f.stem,
                "content": content,
                "modified": f.stat().st_mtime,
            })
        except Exception:
            # Skip files that can't be read
            continue

    # Sort by modification time, most recent first
    sessions.sort(key=lambda x: x["modified"], reverse=True)
    return jsonify({"sessions": sessions, "error": None})


@app.route("/api/github-issues")
def get_github_issues():
    """Return GitHub issues via gh CLI for Workflow Hub v0.7."""
    try:
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--json", "number,title,labels,state,createdAt",
                "--state", "open",
                "-L", "50"
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,  # Timeout after 30 seconds
        )
        if result.returncode == 0:
            issues = json.loads(result.stdout) if result.stdout else []
            return jsonify({"issues": issues, "error": None})
        return jsonify({"issues": [], "error": result.stderr or "gh command failed"})
    except subprocess.TimeoutExpired:
        return jsonify({"issues": [], "error": "GitHub CLI timeout"})
    except FileNotFoundError:
        return jsonify({"issues": [], "error": "gh CLI not installed"})
    except Exception as e:
        return jsonify({"issues": [], "error": str(e)})


@app.route("/api/pm-sessions")
def get_pm_sessions():
    """Return PM_SESSIONS.json for Workflow Hub v0.9."""
    pm_sessions_file = TEMP_DIR / "PM_SESSIONS.json"
    if not pm_sessions_file.exists():
        return jsonify({
            "version": "1.0.0",
            "last_cleanup": None,
            "sessions": [],
            "error": None
        })

    try:
        with open(pm_sessions_file) as f:
            data = json.load(f)
        return jsonify({**data, "error": None})
    except Exception as e:
        return jsonify({
            "version": "1.0.0",
            "last_cleanup": None,
            "sessions": [],
            "error": str(e)
        })


@app.route("/api/backlog/tasks")
def get_backlog_tasks():
    """Proxy Backlog.md API for CORS compatibility (v0.9)."""
    import urllib.request
    try:
        with urllib.request.urlopen("http://localhost:6420/api/tasks", timeout=5) as response:
            data = json.loads(response.read().decode())
        # Return the array directly, as expected by the widget
        return jsonify(data)
    except urllib.error.URLError:
        return jsonify([]), 503  # Empty array with error status
    except Exception:
        return jsonify([]), 500  # Empty array with error status


@app.route("/api/backlog/config")
def get_backlog_config():
    """Proxy Backlog.md config endpoint for connection check (v0.9)."""
    import urllib.error
    import urllib.request
    try:
        with urllib.request.urlopen("http://localhost:6420/api/config", timeout=5) as response:
            data = json.loads(response.read().decode())
        return jsonify(data)
    except urllib.error.HTTPError as e:
        # Server responded with error - but it's running, so connection is OK
        # Return a minimal config to indicate connection is working
        return jsonify({"status": "connected", "error": e.reason})
    except (urllib.error.URLError, ConnectionRefusedError):
        return jsonify({"error": "Backlog.md API not available"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

    # Session states (v0.7)
    states_dir = TEMP_DIR / "SESSION_STATE"
    session_states = []
    if states_dir.exists():
        for f in states_dir.glob("*.md"):
            if f.name != ".gitkeep":
                try:
                    session_states.append({
                        "id": f.stem,
                        "content": f.read_text(),
                        "modified": f.stat().st_mtime,
                    })
                except Exception:
                    continue

    return jsonify(
        {
            "worktrees": worktrees.stdout,
            "gitStatus": status.stdout,
            "gitLog": log.stdout,
            "workflowState": workflow_content,
            "sessionSummary": session_content,
            "sessionStates": session_states,
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
    print("\n  URLs:")
    print("    Hub:        http://localhost:5050/")
    print("    Worktrees:  http://localhost:5050/playgrounds/worktree-coordinator.html")
    print("    Mermaid:    http://localhost:5050/playgrounds/mermaid-designer.html")
    print("\n  API Endpoints:")
    print("    GET /api/health            - Health check")
    print("    GET /api/all               - All data (combined)")
    print("    GET /api/worktrees         - Git worktree list")
    print("    GET /api/git-status        - Git status")
    print("    GET /api/git-log           - Recent commits")
    print("    GET /api/workflow-state    - WORKFLOW_STATE.md")
    print("    GET /api/session-summaries - Session summaries")
    print("    GET /api/session-states    - Session state files (v0.7)")
    print("    GET /api/github-issues     - GitHub issues via gh (v0.7)")
    print("    GET /api/pm-sessions       - PM sessions tracker (v0.9)")
    print("    GET /api/backlog/tasks     - Backlog.md proxy (v0.9)")
    print("    GET /api/agent-reports     - Agent reports")
    print("\n  Press Ctrl+C to stop\n")
    print("=" * 50 + "\n")

    app.run(port=5050, debug=False)
