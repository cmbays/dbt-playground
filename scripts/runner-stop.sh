#!/bin/bash
# Stop the GitHub Actions runner
#
# This script gracefully stops the self-hosted runner.
# Jobs in progress will be allowed to complete.
#
# Usage:
#   ./scripts/runner-stop.sh

set -e

RUNNER_PID=$(pgrep -f "Runner.Listener" 2>/dev/null || echo "")

if [ -z "$RUNNER_PID" ]; then
    echo "Runner is not running"
    exit 0
fi

echo "Stopping GitHub Actions runner (PID: $RUNNER_PID)..."

# Send SIGTERM for graceful shutdown
kill -TERM "$RUNNER_PID"

# Wait for graceful shutdown (up to 30 seconds)
echo "Waiting for graceful shutdown..."
TIMEOUT=30
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if ! pgrep -f "Runner.Listener" > /dev/null 2>&1; then
        echo
        echo "Runner stopped gracefully"
        exit 0
    fi
    sleep 1
    ELAPSED=$((ELAPSED + 1))
    printf "."
done

echo

# If still running, check again
if pgrep -f "Runner.Listener" > /dev/null 2>&1; then
    echo "Runner still running after ${TIMEOUT}s timeout"
    echo "This may indicate a job is still in progress"
    echo
    read -p "Force stop? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Force stopping runner..."
        pkill -KILL -f "Runner.Listener" || true
        echo "Runner force stopped"
    else
        echo "Runner left running. Check status with:"
        echo "  ./scripts/runner-status.sh"
    fi
else
    echo "Runner stopped"
fi
