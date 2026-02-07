# Debug Command

Start, track, and complete debug sessions following the 7-step Debug Protocol with automatic session tracking. Supports single-agent and multi-agent team debugging.

## Quick Decision: Single vs Team Debug

```
Is the bug complex? (multi-service, concurrency, >10 files affected)
  |
  +-- No  --> /debug start "bug"                    (single agent, fast)
  |
  +-- Yes --> /debug start "bug" --team              (multi-agent team)
  |           /debug start "bug" --agents 3          (fixed agent count)
  |
  +-- Unsure --> /debug start "bug" --assess         (run complexity analyzer)
```

**Token cost estimate**: Team debug spawns 2-5 agents. Each agent session uses ~2k-10k tokens depending on investigation depth. The `--assess` flag shows cost estimate before spawning.

## Usage

```
/debug start "Bug description" [--severity high|medium|low] [--tags tag1,tag2]
/debug start "Bug description" --team [--lead backend|frontend|data|infra]
/debug start "Bug description" --agents N [--lead backend]
/debug start "Bug description" --assess
/debug step <phase> "findings" [--evidence path]
/debug end "root cause" --time 45m [--outcome resolved|escalated|inconclusive]
/debug status [--team]
/debug history [--since date] [--pattern text]
/debug assign <agent> <zone>
/debug findings <agent>
/debug merge
/debug conflicts
```

## Commands

### Start a Debug Session

#### Single Agent (Default)

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

#### Multi-Agent Team Debug

```
/debug start "Distributed timeout across payment and notification services" --team
/debug start "Data inconsistency in user cache" --agents 3 --lead data
/debug start "Intermittent API failures" --assess
```

**--team**: Runs complexity analyzer, spawns optimal number of agents (2-5).

**--agents N**: Skip complexity analysis, spawn exactly N agents.

**--lead**: Designate lead agent focus area (backend, frontend, data, infra, security).

**--assess**: Run complexity analysis only (no agent spawn), show assessment and cost estimate.

Output (--team):

```
Multi-Agent Debug Session Started
------
Session ID: MA-2026-02-06-001
Bug: Distributed timeout across payment and notification services
Mode: TEAM (3 agents)
Lead: backend

Complexity Assessment:
  Score: 0.72 (3 agents suggested)
  Factors: multi_service (0.67), performance (0.33)
  Estimated token cost: ~6k-15k tokens

Agent Assignments:
  Agent     | Zone                | Capabilities    | Status
  ----------|---------------------|-----------------|--------
  backend   | payment-service     | backend, data   | assigned
  infra     | notification-svc    | infra, perf     | assigned
  data      | cache-layer         | data, backend   | assigned

Session Folder: temp/DEBUG_REPORTS/session-20260206-001/

Phase: SETUP -> Use '/debug step 1-reproduce "findings"' to begin
       All agents investigate in parallel during phases 1-3.

Team Commands:
  /debug assign <agent> <zone>    - Reassign agent to zone
  /debug findings <agent>         - View agent's findings
  /debug merge                    - Trigger merge resolution
  /debug conflicts                - Show detected conflicts
  /debug status --team            - Show all agents' status
```

Output (--assess):

```
Complexity Assessment
------
Bug: Distributed timeout across payment and notification services

Score: 0.72 / 1.0
Suggested Agents: 3
Factors:
  - multi_service (0.67): Detected: distributed, microservice
  - performance (0.33): Detected: timeout

Required Capabilities: backend, infra, performance
Estimated Token Cost: ~6k-15k tokens

Recommendation: Use --team for automated spawning, or --agents 3 for manual control.

Commands:
  /debug start "..." --team           # Accept recommendation
  /debug start "..." --agents 2       # Override agent count
  /debug start "..."                  # Single agent (simpler)
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
/debug status --team
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

Team status (--team flag):

```
Multi-Agent Session: MA-2026-02-06-001
------
Bug: Distributed timeout across services
Status: INVESTIGATING
Lead: backend

Agent Status:
  Agent     | Zone              | Status        | Findings | Primary Finding
  ----------|-------------------|---------------|----------|----------------
  backend   | payment-service   | investigating | 0        | -
  infra     | notification-svc  | complete      | 2        | Pool exhaustion
  data      | cache-layer       | investigating | 1        | Stale cache TTL

Progress: 1/3 agents complete
Conflicts: 0 detected

Commands:
  /debug findings infra              # View completed agent's findings
  /debug merge                       # Trigger merge (when all complete)
```

### Team Commands (Multi-Agent Only)

#### Assign Agent to Zone

```
/debug assign data cache-layer
/debug assign security auth-module
```

Reassigns an agent to a different investigation zone.

#### View Agent Findings

```
/debug findings backend
/debug findings infra
```

Shows the detailed findings submitted by a specific agent.

#### Trigger Merge Resolution

```
/debug merge
```

Runs the merge resolution engine:
1. Collects all agent findings
2. Detects conflicts between findings (root cause disagreements, evidence contradictions)
3. Resolves conflicts via evidence weighting (reproducible > log > code analysis > theory)
4. Generates consensus findings and deployment order
5. Extracts lesson candidates for LESSONS.md

Output:

```
Merge Resolution Complete
------
Session: MA-2026-02-06-001

Consensus:
  ROOT CAUSE: Connection pool size = 1 (confidence: 0.95)
  SYMPTOM: Frontend spinner on data load (confidence: 0.70)

Conflicts: 1 detected, 1 resolved
  C-001: root_cause_disagreement
    backend says "pool undersized" vs data says "memory leak"
    Resolution: evidence_weighted (backend: 0.80, data: 0.22)

Deployment Order:
  1. Increase pool size to 10 (P0 - critical)
  2. Add 5s timeout to fetch calls (P2 - optional)

Lessons Extracted: 1
  - "Connection Pool Size = 1 Causing Serialization"

Files:
  merge_resolution.md -> temp/DEBUG_REPORTS/session-20260206-001/
  Events -> memory/events.jsonl (debug_lesson)
```

#### Show Conflicts

```
/debug conflicts
```

Shows detected conflicts between agent findings without triggering merge.

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

### Session Flags

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

### Multi-Agent Flags (WAVE3-030)

| Flag | Description | Default |
|------|-------------|---------|
| `--team` | Start multi-agent session (complexity-assessed) | false |
| `--agents N` | Start multi-agent session with N agents (1-5) | auto |
| `--lead` | Lead agent focus (backend, frontend, data, infra, security) | backend |
| `--assess` | Run complexity analysis only (no agent spawn) | false |

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

### Multi-Agent Team Debug

```
# Assess complexity first
/debug start "Distributed timeout across payment and notification services" --assess
# -> Score: 0.72, suggests 3 agents

# Start team debug
/debug start "Distributed timeout across payment and notification services" --team --tags distributed,timeout

# All agents investigate in parallel during phases 1-3
/debug step 1-reproduce "Reproduced under load: payment-service responds >5s"
/debug step 2-blast_radius "payment-service, notification-service, cache-layer"

# View agent findings as they complete
/debug findings backend
/debug findings infra

# Check for conflicts
/debug conflicts

# When all agents complete, trigger merge
/debug merge

# Review merge resolution, then close
/debug end "Connection pool exhaustion" --time 2h --outcome resolved
```

### Quick Team Debug (Fixed Agent Count)

```
# Skip complexity analysis, spawn 2 agents directly
/debug start "Race condition in order processing" --agents 2 --lead backend

# Agents investigate in parallel
/debug status --team

# Merge and close
/debug merge
/debug end "Missing lock on order consumer" --time 45m
```

## Multi-Agent Coordination Protocol

The multi-agent debug mode uses the WAVE3-030 coordination protocol:

```
Bug Report -> Complexity Assessment -> Agent Spawning
                                            |
                                   +--------+--------+
                                   |        |        |
                               Agent A  Agent B  Agent C
                               (zone 1) (zone 2) (zone 3)
                                   |        |        |
                                   +--------+--------+
                                            |
                                   Conflict Detection
                                            |
                                   Evidence Weighting
                                            |
                                   Merge Resolution
                                            |
                                   +--------+--------+
                                   |                  |
                              LESSONS.md          merge_resolution.md
                              Integration         (in DEBUG_REPORTS/)
```

### Coordination Model

- **Hub-and-spoke**: Lead agent orchestrates, specialists investigate
- **Non-overlapping zones**: Blast radius partitioned to avoid duplicate work
- **Evidence-weighted resolution**: Reproducible > logs > code analysis > theory > unsubstantiated
- **Human escalation**: When evidence weights are too close (diff < 0.2), humans decide

### LESSONS.md Integration

Multi-agent debates produce lesson candidates automatically:
- High-confidence root causes (>=0.7) extracted as patterns
- Resolved conflict debates (evidence-weighted winner) recorded
- Events emitted to `memory/events.jsonl` with `event_type="debug_lesson"`
- Fed to existing `scripts/consolidate-memory.py` pipeline for pattern detection

### Module Reference

| Module | Purpose |
|--------|---------|
| `scripts/lib/multi_agent_debug/protocol.py` | Complexity assessment, blast radius partitioning |
| `scripts/lib/multi_agent_debug/registry.py` | Agent capabilities, availability, assignments |
| `scripts/lib/multi_agent_debug/orchestrator.py` | Session lifecycle management |
| `scripts/lib/multi_agent_debug/manifest.py` | Session manifest generation |
| `scripts/lib/multi_agent_debug/conflict_detector.py` | Conflict detection, evidence weighting |
| `scripts/lib/multi_agent_debug/merge_resolver.py` | Merge resolution engine |
| `scripts/lib/multi_agent_debug/lessons.py` | LESSONS.md pattern extraction from debates |

## Related

- [[../agents/debug-agent.md]] - Debug Agent persona
- [[dbt-debug.md]] - dbt-specific debugging
- [[qa.md]] - QA gate integration
- `scripts/debug-tracker.py` - Session Tracker CLI
- `scripts/lessons-analyzer.py` - Pattern extraction
- `scripts/lib/multi_agent_debug/` - Multi-agent coordination library (WAVE3-030)
- `temp/vibe_coding/OBSERVABILITY_INTEGRATION.md` - Observability setup
- `temp/WAVE3-030_SPRINT_PLAN.md` - Sprint plan and design decisions
