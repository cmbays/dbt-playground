# Self-Hosted GitHub Actions Runner Guide

## What Is This?

A self-hosted runner allows GitHub Actions to run on your local Mac instead of GitHub's cloud servers. This is necessary for private repositories with limited Actions minutes.

**Benefits**:

- No GitHub Actions minute consumption
- Faster builds (native Apple Silicon performance)
- Access to local resources (databases, files)
- No cold-start delays

**Trade-offs**:

- Must be running during CI operations
- Uses local CPU/RAM/disk
- Requires manual start/stop

## Quick Start

### One-Time Setup (First Time Only)

1. **Verify gh CLI is authenticated**:

   ```bash
   gh auth status
   ```

2. **Install the runner**:

   ```bash
   cd ~/Documents/claude/parent-dbt-playground/dbt-playground
   ./scripts/setup-github-runner.sh
   ```

3. **Verify installation**:

   ```bash
   ls -la ~/actions-runner
   ./scripts/runner-status.sh
   ```

### Daily Workflow

#### Start Runner Before Work

```bash
# Terminal 1: Start the runner (keep this open)
./scripts/runner-start.sh
```

The runner runs in the foreground. Keep this terminal open while working.

#### Run CI Tests

Now when you push to a PR, GitHub Actions will use your local runner instead of cloud runners.

**Check status**:

```bash
# Terminal 2: Check runner status
./scripts/runner-status.sh

# Check PR checks
gh pr checks <PR_NUMBER>

# View recent workflow runs
gh run list --limit 5
```

#### Stop Runner After Work

```bash
# When done for the day
./scripts/runner-stop.sh
```

## When to Use

### Start Runner

- Before pushing commits that trigger CI
- Before creating/updating PRs
- When running `/dbt-run` or test commands via CI
- At the start of your development session

### Stop Runner

- When done with development for the day
- Before closing your laptop
- To free up system resources
- When traveling or on battery power

## Understanding the Status

### Runner Status Output

```bash
$ ./scripts/runner-status.sh

=============================================
GitHub Actions Runner Status
=============================================

LOCAL STATUS: RUNNING
  PID: 12345
  Uptime: 02:30:15

INSTALLATION:
  Directory: /Users/cmbays/actions-runner
  Runner name: local-macos-runner

GITHUB STATUS:
  Registered runners:
  - local-macos-runner: online

RECENT WORKFLOW RUNS:
STATUS  TITLE                    WORKFLOW    BRANCH  EVENT
ok      feat: add new model      dbt Tests   feat/x  pull_request
ok      fix: null handling       Test Suite  fix/y   push
```

### Status Meanings

| Status | Meaning | Action |
|--------|---------|--------|
| `RUNNING` | Runner is active | CI can use it |
| `NOT RUNNING` | Runner is stopped | Start with `runner-start.sh` |
| `online` (GitHub) | GitHub sees runner | Everything working |
| `offline` (GitHub) | GitHub can't reach runner | Check if running locally |

## Troubleshooting

### Runner Won't Start

```bash
# Check if already running
./scripts/runner-status.sh

# Check for stale processes
ps aux | grep Runner

# If stale, kill and restart
pkill -f "Runner.Listener"
./scripts/runner-start.sh
```

### "Runner Not Found" Error

```bash
# Reinstall the runner
rm -rf ~/actions-runner
./scripts/setup-github-runner.sh
```

### Jobs Still Queued (Not Running)

1. **Verify runner is running locally**:

   ```bash
   ./scripts/runner-status.sh
   ```

2. **Check GitHub sees the runner**:
   - Go to: <https://github.com/cmbays/dbt-playground/settings/actions/runners>
   - Runner should show as "online"

3. **Check labels match**:
   - Workflows use `runs-on: self-hosted`
   - Runner has label `self-hosted`

4. **Restart runner**:

   ```bash
   ./scripts/runner-stop.sh
   ./scripts/runner-start.sh
   ```

### Registration Token Expired

Tokens expire after 1 hour. If setup fails:

```bash
# Get a fresh token and reconfigure
cd ~/actions-runner
TOKEN=$(gh api -X POST repos/cmbays/dbt-playground/actions/runners/registration-token --jq .token)
./config.sh --url https://github.com/cmbays/dbt-playground --token "$TOKEN" --replace
```

### Performance Issues

The runner uses local CPU/RAM. If your Mac slows down:

1. **Check what's running**:

   ```bash
   top -o cpu -n 10
   ```

2. **Stop runner temporarily**:

   ```bash
   ./scripts/runner-stop.sh
   ```

3. **Close other applications**

4. **Restart with lower load**:
   - Edit workflow to reduce `max-parallel` in matrix

### Logs and Diagnostics

```bash
# View runner logs
tail -f ~/actions-runner/_diag/*.log

# View specific job log
gh run view <run-id> --log

# View failed job
gh run view <run-id> --log-failed
```

## Best Practices

1. **Always start runner before pushing** - Otherwise jobs queue indefinitely

2. **Keep terminal open** - Runner needs active terminal session (unless using service mode)

3. **Stop when done** - Free up resources when not developing

4. **Monitor resource usage** - Use Activity Monitor to check CPU/RAM

5. **Update periodically** - Check for runner updates monthly

6. **Check status after wake** - If laptop was sleeping, verify runner is still connected

## Advanced Usage

### Run as Background Service (Optional)

For continuous operation without keeping a terminal open:

```bash
cd ~/actions-runner

# Install as macOS service
sudo ./svc.sh install

# Start service
sudo ./svc.sh start

# Check status
sudo ./svc.sh status
```

To stop and uninstall:

```bash
sudo ./svc.sh stop
sudo ./svc.sh uninstall
```

**Note**: Service mode starts automatically on login but uses resources continuously.

### Multiple Runners (Advanced)

For parallel job execution:

```bash
# Create second runner
mkdir -p ~/actions-runner-2
cd ~/actions-runner-2
# Download and configure with different name
```

### Updating the Runner

GitHub releases new runner versions periodically:

```bash
# Check current version
~/actions-runner/run.sh --version

# Update (re-run setup)
rm -rf ~/actions-runner
./scripts/setup-github-runner.sh
```

## Commands Reference

| Command | Purpose |
|---------|---------|
| `./scripts/setup-github-runner.sh` | One-time installation |
| `./scripts/runner-start.sh` | Start runner (keep terminal open) |
| `./scripts/runner-stop.sh` | Stop runner |
| `./scripts/runner-status.sh` | Check if running + recent runs |
| `gh run list` | View recent workflow runs |
| `gh pr checks <PR>` | Check CI status for PR |
| `gh run view <id> --log` | View workflow run logs |

## GitHub Settings

View and manage runners in GitHub:

- **Runners page**: <https://github.com/cmbays/dbt-playground/settings/actions/runners>
- **Workflow runs**: <https://github.com/cmbays/dbt-playground/actions>

## Workflow Integration

All workflows in this repository are configured to use self-hosted runners:

| Workflow | Timeout | Triggers |
|----------|---------|----------|
| PR Validation | 10 min | PR open/edit |
| Issue Linker | 10 min | PR open/edit |
| PR Labeler | 10 min | PR open/sync |
| Project Automation | 10 min | Issue open/label |
| dbt Tests | 30 min | PR + push to main |
| Test Suite | 30 min | PR + push to main |
| Lint | 15 min | PR + push to main |

If the runner is not available, jobs will queue until it comes online (or timeout after 24 hours).
