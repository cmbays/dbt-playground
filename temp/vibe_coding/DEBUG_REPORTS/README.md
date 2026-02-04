# Multi-Agent Debug Session Coordination

This folder enables parallel debugging by multiple agents without conflicts.

## Purpose

When multiple agents debug the same codebase concurrently, they need:

1. **Isolation**: Each agent works in a dedicated session folder
2. **Coordination**: Agents share findings without overwriting each other
3. **Merge Protocol**: A clear process to combine independent discoveries
4. **History**: Persistent record of what was tried and learned

## Folder Structure

```
DEBUG_REPORTS/
├── README.md                          # This file
├── DEBUG_SESSION_REPORT.md            # Template for debug sessions
└── [session-YYYY-MM-DD-HHmmss]/       # Session folders (timestamp-based)
    ├── agent_A_findings.md            # Agent A's investigation
    ├── agent_B_findings.md            # Agent B's investigation
    └── merge_resolution.md            # Combined findings + final fix
```

## Naming Convention

### Session Folders

Format: `session-YYYY-MM-DD-HHmmss`

Examples:
- `session-2026-02-04-143022` (Feb 4, 2026 at 2:30:22 PM)
- `session-2026-02-04-091545` (Feb 4, 2026 at 9:15:45 AM)

**Why timestamps?** Enables chronological sorting and guarantees uniqueness across concurrent sessions.

### Agent Finding Files

Format: `agent_[name]_findings.md`

Examples:
- `agent_alpha_findings.md`
- `agent_beta_findings.md`
- `agent_debugger1_findings.md`

Use short, distinct names. Avoid spaces or special characters.

## When to Use

Use DEBUG_REPORTS for:

| Scenario | Use DEBUG_REPORTS? |
|----------|-------------------|
| Single agent, simple bug | No - use standard debug protocol |
| Single agent, complex bug | Optional - useful for history |
| Multiple agents, same bug | **Yes** - required for coordination |
| Post-mortem analysis | **Yes** - preserves investigation trail |
| Recurring bug patterns | **Yes** - enables pattern matching |

## Multi-Agent Coordination Rules

### Rule 1: Claim Before Investigating

Before starting, create your findings file with a header:

```markdown
# Agent [Name] Findings

**Session**: session-2026-02-04-143022
**Agent**: [your-name]
**Status**: IN_PROGRESS
**Started**: 2026-02-04 14:30:22 UTC
```

This signals to other agents that you're working on this area.

### Rule 2: Scope Your Investigation

Each agent should focus on a specific angle:

| Agent | Focus Area | Example |
|-------|-----------|---------|
| Agent A | Frontend behavior | UI rendering, event handlers |
| Agent B | Backend logic | API endpoints, data processing |
| Agent C | Data layer | Database queries, schema issues |
| Agent D | Infrastructure | Config, environment, dependencies |

Declare your scope in the findings file header.

### Rule 3: Log Incrementally

Update your findings as you investigate, not just at the end:

```markdown
## Investigation Log

### 14:32 - Checked error logs
- Found: TypeError at line 42 in processor.js
- Observation: Error occurs only on null input

### 14:45 - Traced data flow
- Source: API returns null when user not found
- Expected: Should return empty object {}
```

### Rule 4: Flag Cross-Cuts

If you discover something in another agent's scope:

```markdown
## Cross-Scope Observations

**For Agent B (Backend)**:
- The API at /users/{id} returns null instead of 404
- This may be the root cause; please verify
```

### Rule 5: Merge Before Fixing

Before implementing any fix:

1. All agents write final findings
2. One agent creates `merge_resolution.md`
3. Team reviews merged findings
4. Single coordinated fix is implemented

## Handoff Protocol

### Starting a Session

```bash
# 1. Create session folder
mkdir -p temp/vibe_coding/DEBUG_REPORTS/session-$(date +%Y-%m-%d-%H%M%S)

# 2. Copy template
cp temp/vibe_coding/DEBUG_REPORTS/DEBUG_SESSION_REPORT.md \
   temp/vibe_coding/DEBUG_REPORTS/session-XXXXX/agent_[name]_findings.md

# 3. Update header and begin investigation
```

### Completing Your Investigation

1. Update status from `IN_PROGRESS` to `COMPLETE`
2. Add final summary section
3. Note confidence level (Low/Medium/High)
4. Flag any blockers for merge

### Merge Process

The merge coordinator (usually the senior agent or session initiator):

1. Creates `merge_resolution.md`
2. Synthesizes all agent findings
3. Identifies root cause vs symptoms
4. Proposes unified fix
5. Gets approval before implementation

## Session Completion Checklist

Before closing a debug session:

- [ ] All participating agents have status `COMPLETE`
- [ ] `merge_resolution.md` exists with final diagnosis
- [ ] Root cause identified (not just symptom)
- [ ] Fix verified (reproduction steps pass)
- [ ] LESSONS.md updated with pattern to prevent recurrence
- [ ] Session folder retained for future reference

## Example: Multi-Agent Debug Session

### Scenario

Bug: "Orders page crashes for some users"

### Session Structure

```
session-2026-02-04-143022/
├── agent_frontend_findings.md    # UI team investigation
├── agent_backend_findings.md     # API team investigation
├── agent_data_findings.md        # Database team investigation
└── merge_resolution.md           # Combined diagnosis
```

### Outcome

- **Agent Frontend**: Found crash on null order.items
- **Agent Backend**: Found API returns null for canceled orders
- **Agent Data**: Found schema allows NULL on items column
- **Merge**: Root cause is missing NOT NULL constraint + missing API validation
- **Fix**: Add constraint + API null check + frontend defensive coding

## Integration with Existing Systems

### With AGENT_REPORTS

```
temp/
├── AGENT_REPORTS/           # Feature development workflow
│   └── [feature]/
│       ├── PM_REPORT.md
│       └── ...
└── vibe_coding/
    └── DEBUG_REPORTS/       # Debug coordination (THIS)
        └── [session]/
            └── ...
```

DEBUG_REPORTS is for **bug investigation**, not feature development.

### With LESSONS.md

After every resolved debug session:

1. Extract the pattern that caused the bug
2. Add entry to `docs/reference/LEARNINGS.md`
3. Reference the debug session folder for context

### With progress.txt

Update project progress after significant debug sessions:

```
[2026-02-04] Debug session session-2026-02-04-143022 resolved
- Bug: Orders page crash
- Root cause: Missing NOT NULL constraint
- Status: Fixed and deployed
```

## Related Documents

- [x_post_backend.txt](../x_post_backend.txt) - 7-step Debug Agent protocol
- [WAVE3_TASK_QUEUE.md](../WAVE3_TASK_QUEUE.md) - Task definitions
- [WAVE3_PATHWAY_STRATEGY.md](../WAVE3_PATHWAY_STRATEGY.md) - Tier maturation context
- [LEARNINGS.md](../../../docs/reference/LEARNINGS.md) - Pattern library

---

*Created: 2026-02-04 | WAVE3-001*
