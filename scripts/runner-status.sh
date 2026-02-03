#!/bin/bash
# Check GitHub Actions runner status
#
# Shows whether the runner is running locally and recent workflow status.
#
# Usage:
#   ./scripts/runner-status.sh

set -e

RUNNER_DIR="$HOME/actions-runner"

echo "============================================="
echo "GitHub Actions Runner Status"
echo "============================================="
echo

# Check local runner process
RUNNER_PID=$(pgrep -f "Runner.Listener" 2>/dev/null || echo "")

if [ -n "$RUNNER_PID" ]; then
    echo "LOCAL STATUS: RUNNING"
    echo "  PID: $RUNNER_PID"

    # Get process info
    if command -v ps &> /dev/null; then
        UPTIME=$(ps -o etime= -p "$RUNNER_PID" 2>/dev/null | xargs || echo "unknown")
        echo "  Uptime: $UPTIME"
    fi
else
    echo "LOCAL STATUS: NOT RUNNING"
    echo
    echo "  Start with: ./scripts/runner-start.sh"
fi

echo

# Check if runner is installed
if [ -d "$RUNNER_DIR" ]; then
    echo "INSTALLATION:"
    echo "  Directory: $RUNNER_DIR"

    # Check for .runner file which contains config
    if [ -f "$RUNNER_DIR/.runner" ]; then
        RUNNER_NAME=$(grep -o '"agentName":"[^"]*"' "$RUNNER_DIR/.runner" 2>/dev/null | cut -d'"' -f4 || echo "unknown")
        echo "  Runner name: $RUNNER_NAME"
    fi
else
    echo "INSTALLATION: NOT FOUND"
    echo "  Run setup: ./scripts/setup-github-runner.sh"
fi

echo

# Check GitHub status if gh is available
if command -v gh &> /dev/null; then
    echo "GITHUB STATUS:"

    # Try to get runner info from GitHub
    RUNNERS=$(gh api repos/cmbays/dbt-playground/actions/runners --jq '.runners[] | "  - \(.name): \(.status)"' 2>/dev/null || echo "")

    if [ -n "$RUNNERS" ]; then
        echo "  Registered runners:"
        echo "$RUNNERS"
    else
        echo "  No runners registered or unable to query"
    fi

    echo
    echo "RECENT WORKFLOW RUNS:"
    gh run list --repo cmbays/dbt-playground --limit 5 2>/dev/null || echo "  Unable to fetch workflow runs"
fi

echo
echo "============================================="
echo "Quick commands:"
echo "  Start:  ./scripts/runner-start.sh"
echo "  Stop:   ./scripts/runner-stop.sh"
echo "  GitHub: https://github.com/cmbays/dbt-playground/settings/actions/runners"
echo "============================================="
