# Debug Command

Start, track, and complete debug sessions following the 7-step Debug Protocol with automatic session tracking.

## Usage

```
/debug start "Bug description" [--severity high|medium|low] [--tags tag1,tag2]
/debug step <phase> "findings" [--evidence path]
/debug end "root cause" --time 45m [--outcome resolved|escalated|inconclusive]
/debug status
/debug history [--since date] [--pattern text]
```

## Commands

### Start a Debug Session

```
/debug start "Race condition in queue processing"
/debug start "API timeout on /users endpoint" --severity high --tags api,performance
```

Initializes:
- Creates Session Tracker entry
- Generates trace_id for observability
- Captures initial context

Output:

```
Debug Session Started
------
Session ID: DBG-2026-02-05-001
Bug: Race condition in queue processing
Severity: medium
Tags: async, queue

Protocol Phases:
  1-reproduce    - Confirm bug exists reliably
  2-blast_radius - Identify affected components
  3-root_cause   - Identify underlying cause
  4-fix_design   - Design the solution
  5-implement    - Code the fix
  6-verify       - Confirm fix works
  7-prevent      - Add tests/docs to prevent recurrence

Next: Use '/debug step 1-reproduce "findings"' to log progress
```

### Log Debug Steps

```
/debug step 1-reproduce "Bug confirmed: duplicates appear when queue > 10 items"
/debug step 2-blast_radius "Affects worker and scheduler modules"
/debug step 3-root_cause "Missing mutex lock on queue consumer" --evidence temp/investigation.md
```

Output:

```
Step 2 logged (2-blast_radius)
------
Findings: Affects worker and scheduler modules

Session: DBG-2026-02-05-001
Duration so far: 15m
Steps logged: 2/7

Next phases:
  [x] 1-reproduce
  [x] 2-blast_radius
  [ ] 3-root_cause    <- Suggested next
  [ ] 4-fix_design
  [ ] 5-implement
  [ ] 6-verify
  [ ] 7-prevent
```

### End Debug Session

```
/debug end "Missing mutex lock on queue consumer" --time 45m
/debug end "N+1 query in user lookup" --time 1h 30m --outcome resolved
/debug end "Issue escalated to vendor" --time 2h --outcome escalated
```

Output:

```
Debug Session Complete
------
Session ID: DBG-2026-02-05-001
Duration: 45m
Steps: 5
Outcome: resolved

Summary:
  Bug: Race condition in queue processing
  Root Cause: Missing mutex lock on queue consumer
  Fix: Added asyncio.Lock to consumer

Event logged to memory/events.jsonl
Session saved to database

Tip: Run 'lessons-analyzer.py extract' to check for patterns
```

### Check Status

```
/debug status
```

Shows active session or recent history:

```
Active Session: DBG-2026-02-05-001
------
Bug: Race condition in queue processing
Started: 15 minutes ago
Current Phase: 3-root_cause
Steps Logged: 3

Recent Steps:
  1. [1-reproduce] Bug confirmed: duplicates when queue > 10
  2. [2-blast_radius] Affects worker and scheduler modules
  3. [3-root_cause] Investigating locking behavior...

Commands:
  /debug step 4-fix_design "Design the fix"
  /debug end "root cause" --time 45m
```

### Query History

```
/debug history
/debug history --since 2026-02-01
/debug history --pattern "race condition"
/debug history --tags async
```

Output:

```
Debug Session History (last 7 days)
------
ID                      | Date       | Bug                           | Root Cause              | Duration | Outcome
------------------------|------------|-------------------------------|-------------------------|----------|----------
DBG-2026-02-05-001      | 2026-02-05 | Race condition in queue...    | Missing mutex lock      | 45m      | resolved
DBG-2026-02-04-002      | 2026-02-04 | API timeout on /users         | N+1 query pattern       | 1h 30m   | resolved
DBG-2026-02-04-001      | 2026-02-04 | Null pointer in handler       | Missing null check      | 20m      | resolved

3 sessions found

Use 'lessons-analyzer.py extract' to identify patterns
```

## Protocol Phases Reference

| Phase | Name | Purpose | Key Questions |
|-------|------|---------|---------------|
| 1-reproduce | Reproduce | Confirm bug exists | Can I trigger this reliably? |
| 2-blast_radius | Blast Radius | Identify scope | What else might be affected? |
| 3-root_cause | Root Cause | Find underlying issue | Why is this happening? |
| 4-fix_design | Fix Design | Plan the solution | What's the minimal safe fix? |
| 5-implement | Implement | Code the fix | Does this address root cause? |
| 6-verify | Verify | Confirm fix works | Is the bug gone? No regressions? |
| 7-prevent | Prevent | Add safeguards | How do we prevent recurrence? |

## Integration with Session Tracker

This command wraps `scripts/debug-tracker.py` for seamless integration:

| /debug Command | debug-tracker.py Equivalent |
|----------------|----------------------------|
| `/debug start "bug"` | `debug-tracker.py start --bug "bug"` |
| `/debug step 1-reproduce "found"` | `debug-tracker.py log --phase 1-reproduce --findings "found"` |
| `/debug end "cause" --time 45m` | `debug-tracker.py end --root-cause "cause" --fix-time 45m` |
| `/debug status` | `debug-tracker.py status` |
| `/debug history` | `debug-tracker.py query` |

## Observability Hooks

When observability is enabled (see OBSERVABILITY_INTEGRATION.md):

- **trace_id**: Generated at session start, correlates all spans
- **Spans**: Each step emits a span to Jaeger/Tempo
- **Metrics**: Session duration, step counts emitted to Prometheus
- **Logs**: Structured JSON with session_id for correlation

```
# Enable trace correlation (optional)
/debug start "bug" --trace-id abc123
```

## API Contract Validation

For API debugging, the command can trigger contract validation:

```
/debug step 2-blast_radius "Checking API contracts" --validate-contracts
```

This will:
1. Run API contract tests
2. Log results as evidence
3. Flag any contract violations

## Workflow Integration

### With Supervisor

The Supervisor can trigger debug sessions:

```
super: Bug found in CI - test_queue_processing failing
  -> Recommends: /debug start "test_queue_processing CI failure" --severity high
```

### With QA

After fixing, QA gate checks debug session:

```
/qa
  -> Checks: Active debug session? Ensure /debug end was called
```

### With Memory System

Sessions feed the compound learning loop:

```
Debug Session End
       |
       v
memory/events.jsonl <- Event emitted
       |
       v
lessons-analyzer.py extract <- Pattern detection
       |
       v
LEARNINGS.md <- Recurring patterns promoted
```

## Flags Reference

| Flag | Description | Default |
|------|-------------|---------|
| `--severity` | Bug severity (high, medium, low) | medium |
| `--tags` | Comma-separated categorization tags | none |
| `--evidence` | Path to supporting files | none |
| `--time` | Time spent debugging (e.g., "45m", "1h 30m") | required for end |
| `--outcome` | Session outcome | resolved |
| `--trace-id` | Correlation ID for observability | auto-generated |
| `--since` | Query start date (ISO format) | 7 days ago |
| `--pattern` | Text pattern to search | none |
| `--format` | Output format (table, json) | table |
| `--force` | Force start (ends active session) | false |

## Examples

### Quick Bug Fix

```
/debug start "TypeError in user handler"
/debug step 1-reproduce "Triggered on null user_id"
/debug step 3-root_cause "Missing null check before access"
/debug step 5-implement "Added guard clause"
/debug step 6-verify "Tests passing"
/debug end "Missing null check" --time 15m
```

### Complex Investigation

```
/debug start "Intermittent timeout in payments" --severity high --tags payments,timeout,production

/debug step 1-reproduce "Reproduced: happens on high traffic"
/debug step 2-blast_radius "Affects payment-service, notification-service, audit-log"
/debug step 3-root_cause "Connection pool exhaustion under load"
/debug step 4-fix_design "Increase pool size + add circuit breaker"
/debug step 5-implement "Updated config, added resilience4j"
/debug step 6-verify "Load test passing at 2x traffic"
/debug step 7-prevent "Added pool metrics alert, documented in runbook"

/debug end "Connection pool exhaustion" --time 3h --resolution "Increased pool + circuit breaker"
```

### Escalated Issue

```
/debug start "Third-party API returning 500s" --tags vendor,external

/debug step 1-reproduce "Confirmed: all calls failing"
/debug step 2-blast_radius "Affects order processing, reporting"

/debug end "Vendor API outage" --time 30m --outcome escalated
```

## Related

- [[../agents/debug-agent.md]] - Debug Agent persona
- [[dbt-debug.md]] - dbt-specific debugging
- [[qa.md]] - QA gate integration
- `scripts/debug-tracker.py` - Session Tracker CLI
- `scripts/lessons-analyzer.py` - Pattern extraction
- `temp/vibe_coding/OBSERVABILITY_INTEGRATION.md` - Observability setup
