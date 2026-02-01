# Permission Auto-Approval System

## Overview

Reduces permission prompt interruptions when running multiple Claude Code sessions by automatically evaluating requests using a three-tier system.

## Architecture

```text
PermissionRequest Event
        │
        ▼
┌───────────────────┐
│ Tier 1: Hard Block│  rm -rf /, sudo, git push --force, writes to .env
│ (instant deny)    │
└───────────────────┘
        │ (pass)
        ▼
┌───────────────────┐
│ Tier 2: Fast Allow│  dbt commands, git status, reads, GIT_MASTER ops
│ (instant approve) │
└───────────────────┘
        │ (unknown)
        ▼
┌───────────────────┐
│ Tier 3: Fallthru  │  Unknown operations go to user prompt
│ (user decides)    │
└───────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `.claude/hooks/permission-auto-approve.js` | Main hook logic |
| `.claude/hooks/permission-config.js` | Pattern configuration |
| `.claude/hooks/audit/logger.js` | Audit trail module |
| `.claude/hooks/audit/permission-decisions.jsonl` | Audit log |

## Tier 1: Hard Blocks (Always Denied)

### Bash Commands

- `rm -rf /`, `rm -rf ~/`, `rm -rf *` - Destructive deletes
- `sudo`, `su -` - Privilege escalation
- `chmod 777` - Insecure permissions
- `git push --force main` - Force push to protected branch
- `git reset --hard` - Discard changes
- `curl | sh` - Remote code execution

### File Writes

- `.env`, `.env.local`, `.env.prod` - Environment secrets
- `credentials.json`, `secrets.yaml` - Credential files
- `*.pem`, `*.key`, `id_rsa` - Keys and certificates

## Tier 2: Fast Allows (Auto-Approved)

### Bash Commands

- **File exploration**: `ls`, `cat`, `head`, `tail`, `find`, `grep`
- **Git reads**: `git status`, `git log`, `git diff`, `git branch`
- **Git writes with auth**: `GIT_MASTER_AUTHORIZED=true git commit`
- **dbt operations**: `dbt build`, `dbt test`, `dbt run`
- **Python/uv**: `uv sync`, `uv run`, `pytest`
- **npm**: `npm test`, `npm run lint`

### Read Operations

All `Read`, `Glob`, and `Grep` operations are auto-approved.

## Audit Log

Decisions logged to `.claude/hooks/audit/permission-decisions.jsonl`:

```json
{
  "timestamp": "2026-02-01T10:30:00.000Z",
  "session_id": "abc123",
  "tool": "Bash",
  "input_summary": "dbt build",
  "decision": "allow",
  "tier": 2
}
```

### View Audit Stats

```bash
# Recent decisions
tail -20 .claude/hooks/audit/permission-decisions.jsonl | jq .

# Count by type
jq -s 'group_by(.decision) | map({decision: .[0].decision, count: length})' \
  .claude/hooks/audit/permission-decisions.jsonl
```

## Customization

Edit `.claude/hooks/permission-config.js` to add patterns:

```javascript
fastAllowPatterns: {
  bash: [
    /^my-custom-command/,  // Add new safe command
  ]
}
```

## Security Notes

- Unknown operations always fall through to user
- Hooks never read sensitive file contents
- All auto-decisions are logged for forensics
- Hook errors don't block operations (fail-open)
