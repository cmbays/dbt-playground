#!/bin/bash
# Start the GitHub Actions runner
#
# This script starts the self-hosted runner in the foreground.
# The runner must be running for GitHub Actions to use it.
#
# Usage:
#   ./scripts/runner-start.sh
#
# To run in background (advanced):
#   nohup ./scripts/runner-start.sh > ~/actions-runner/runner.log 2>&1 &

set -e

RUNNER_DIR="$HOME/actions-runner"

# Check if runner is installed
if [ ! -d "$RUNNER_DIR" ]; then
    echo "Runner not installed at $RUNNER_DIR"
    echo
    echo "Run the setup script first:"
    echo "  ./scripts/setup-github-runner.sh"
    exit 1
fi

# Check if runner is already running
if pgrep -f "Runner.Listener" > /dev/null; then
    PID=$(pgrep -f "Runner.Listener")
    echo "Runner is already running (PID: $PID)"
    echo
    echo "To stop it:"
    echo "  ./scripts/runner-stop.sh"
    exit 1
fi

# Check if run.sh exists
if [ ! -f "$RUNNER_DIR/run.sh" ]; then
    echo "Error: run.sh not found in $RUNNER_DIR"
    echo "The runner may not be properly configured."
    echo
    echo "Try reinstalling:"
    echo "  ./scripts/setup-github-runner.sh"
    exit 1
fi

echo "============================================="
echo "Starting GitHub Actions Runner"
echo "============================================="
echo
echo "Runner directory: $RUNNER_DIR"
echo "Press Ctrl+C to stop the runner"
echo
echo "View status in GitHub:"
echo "  https://github.com/cmbays/dbt-playground/settings/actions/runners"
echo
echo "---------------------------------------------"
echo

cd "$RUNNER_DIR"
./run.sh
