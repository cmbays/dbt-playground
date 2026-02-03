#!/bin/bash
# Self-hosted GitHub Actions runner setup for dbt-playground
# Run this script to install the runner (one-time setup)
#
# Prerequisites:
#   - gh CLI authenticated (gh auth status)
#   - macOS ARM64 (Apple Silicon)
#
# Usage:
#   ./scripts/setup-github-runner.sh
#
# After setup, start the runner with:
#   ./scripts/runner-start.sh

set -e

# Configuration
RUNNER_VERSION="2.331.0"  # Released Jan 2026, update periodically
RUNNER_DIR="$HOME/actions-runner"

echo "=== GitHub Actions Self-Hosted Runner Setup ==="
echo "Runner directory: $RUNNER_DIR"
echo "Runner version: $RUNNER_VERSION"
echo

# Check prerequisites
echo "Checking prerequisites..."

# Check gh CLI
if ! command -v gh &> /dev/null; then
    echo "Error: gh CLI not found. Install with: brew install gh"
    exit 1
fi

# Check gh auth
if ! gh auth status &> /dev/null; then
    echo "Error: gh CLI not authenticated. Run: gh auth login"
    exit 1
fi

# Check architecture
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ]; then
    echo "Warning: This script is optimized for ARM64 (Apple Silicon)"
    echo "Detected architecture: $ARCH"
    echo "You may need to adjust the download URL for your architecture"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Prerequisites OK"
echo

# Detect repository owner and name dynamically
echo "Detecting repository..."
if ! REPO_INFO=$(gh repo view --json owner,name --jq '{owner: .owner.login, name: .name}' 2>/dev/null); then
    echo "Error: Failed to detect repository via gh CLI"
    echo "Make sure you're in a git repository directory"
    exit 1
fi

REPO_OWNER=$(echo "$REPO_INFO" | jq -r '.owner')
REPO_NAME=$(echo "$REPO_INFO" | jq -r '.name')

if [ -z "$REPO_OWNER" ] || [ -z "$REPO_NAME" ]; then
    echo "Error: Could not extract repository owner/name"
    echo "Detected values: owner='$REPO_OWNER', name='$REPO_NAME'"
    exit 1
fi

echo "Repository: ${REPO_OWNER}/${REPO_NAME}"
echo

# Check if already installed
if [ -d "$RUNNER_DIR" ]; then
    echo "Runner directory already exists at $RUNNER_DIR"
    echo "This script currently supports a clean reinstall only."
    echo "To reconfigure in-place, run: cd \"$RUNNER_DIR\" && ./config.sh remove"
    echo
    read -p "Proceed with clean reinstall? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing runner..."
        # Try to unconfigure first if possible
        if [ -f "$RUNNER_DIR/config.sh" ]; then
            cd "$RUNNER_DIR"
            TOKEN=$(gh api -X POST "repos/${REPO_OWNER}/${REPO_NAME}/actions/runners/remove-token" --jq .token 2>/dev/null || echo "")
            if [ -n "$TOKEN" ]; then
                ./config.sh remove --token "$TOKEN" 2>/dev/null || true
            fi
            cd -
        fi
        rm -rf "$RUNNER_DIR"
    else
        echo "Aborting. Please resolve manually."
        exit 1
    fi
fi

# Create directory
echo "Creating runner directory..."
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

# Determine download URL based on architecture
if [ "$ARCH" = "arm64" ]; then
    DOWNLOAD_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz"
    ARCHIVE_NAME="actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz"
else
    DOWNLOAD_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-osx-x64-${RUNNER_VERSION}.tar.gz"
    ARCHIVE_NAME="actions-runner-osx-x64-${RUNNER_VERSION}.tar.gz"
fi

# Download runner
echo "Downloading runner from:"
echo "  $DOWNLOAD_URL"
echo
curl -fSL -o "$ARCHIVE_NAME" "$DOWNLOAD_URL"

# Verify download
if [ ! -f "$ARCHIVE_NAME" ] || [ ! -s "$ARCHIVE_NAME" ]; then
    echo "Error: Download failed"
    exit 1
fi

# Extract
echo "Extracting..."
tar xzf "./$ARCHIVE_NAME"
rm "$ARCHIVE_NAME"

# Get registration token
echo
echo "Getting registration token from GitHub..."
if ! TOKEN=$(gh api -X POST "repos/${REPO_OWNER}/${REPO_NAME}/actions/runners/registration-token" --jq .token 2>/dev/null) || [ -z "$TOKEN" ]; then
    echo "Error: Failed to get registration token"
    echo "Make sure you have admin access to the repository"
    exit 1
fi

# Configure runner
echo
echo "Configuring runner..."
./config.sh \
    --url "https://github.com/${REPO_OWNER}/${REPO_NAME}" \
    --token "$TOKEN" \
    --name "local-macos-runner" \
    --labels "self-hosted,macOS,ARM64,local" \
    --work _work \
    --replace

echo
echo "============================================="
echo "Runner installed successfully!"
echo "============================================="
echo
echo "Runner location: $RUNNER_DIR"
echo "Runner name: local-macos-runner"
echo "Labels: self-hosted, macOS, ARM64, local"
echo
echo "To start the runner:"
echo "  ./scripts/runner-start.sh"
echo
echo "To check status:"
echo "  ./scripts/runner-status.sh"
echo
echo "To stop the runner:"
echo "  ./scripts/runner-stop.sh"
echo
echo "View in GitHub:"
echo "  https://github.com/${REPO_OWNER}/${REPO_NAME}/settings/actions/runners"
echo
