---
audience: [architect, developer, multi-agent]
priority: high
size: small
dependencies: []
last_updated: 2026-02-04
status: approved
tags: [architecture, debugging, wave3, multi-agent, persistence]
---

# ADR-019: Debug Session Persistence Strategy

**Status**: Approved
**Date**: 2026-02-04
**Deciders**: Architect, Planner
**Related Issue**: #226
**Wave 3 Task**: WAVE3-004

---

## Context

The Wave 3 Debug Agent protocol requires persistence of debug sessions across multiple dimensions:

1. **Session Continuity**: Debug sessions may span restarts, async collaboration, or multi-day investigations
2. **Multi-Agent Coordination**: Multiple agents may debug the same system simultaneously
3. **Forensic Analysis**: Post-incident review requires access to historical debug attempts
4. **Knowledge Transfer**: Handoff between agents or developers requires context preservation

The original Phase 1 protocol used `progress.txt` as a single-file state tracker, which:
- Does not scale to concurrent debugging sessions
- Has no session isolation (all debug notes interleaved)
- Cannot support async multi-agent workflows
- Lacks structured schema for tooling integration

We need a persistence strategy that enables multi-agent coordination while remaining filesystem-based (no external database for Tier 1 local development).

## Decision

**Use timestamp-based folder structure (DEBUG_REPORTS/) with session-scoped report files.**

### Directory Structure

```
temp/DEBUG_REPORTS/
├── 2026-02-04_14-30_null-pointer-exception/
│   ├── session_manifest.md          # Session ID, agents, timestamps
│   ├── agent_1_findings.md          # First agent's debug findings
│   ├── agent_2_findings.md          # Second agent's findings
│   ├── merge_resolution.md          # Merged resolution (if multi-agent)
│   ├── evidence/                    # Logs, screenshots, traces
│   │   ├── stacktrace.txt
│   │   └── reproduction_steps.md
│   └── outcome.md                   # Final resolution + LESSONS entry
│
├── 2026-02-04_09-15_api-timeout/
│   └── ...
│
└── .active_sessions/                # Symlinks to currently active sessions
    └── session_abc123 -> ../2026-02-04_14-30_null-pointer-exception/
```

### Folder Naming Convention

```
{YYYY-MM-DD}_{HH-MM}_{bug-slug}/
```

- **Timestamp**: Enables chronological sorting and filtering
- **Bug slug**: Human-readable identifier (max 50 chars, kebab-case)
- **Uniqueness**: Timestamp + slug combination is unique

### Session Manifest Format

```markdown
# Debug Session Manifest

**Session ID**: session-2026-02-04-143000
**Status**: ACTIVE | RESOLVED | ABANDONED
**Created**: 2026-02-04 14:30:00 UTC
**Updated**: 2026-02-04 16:45:00 UTC

---

## Bug Reference

**Source**: {issue or report reference}
**Description**: {brief bug description}

---

## Participating Agents

| Agent | Findings File | Status | Focus Area |
|-------|---------------|--------|------------|
| primary | agent_primary_findings.md | COMPLETE | {area} |
| secondary | agent_secondary_findings.md | IN_PROGRESS | {area} |

---

## Session Outcome

**Classification**: ROOT_CAUSE | SYMPTOM | UNKNOWN
**Expedited**: Yes | No
**Related Files**: src/api/handler.py, tests/test_handler.py
```

## Rationale

### Why Filesystem Over Database

| Factor | Filesystem | SQLite | Winner |
|--------|-----------|--------|--------|
| Tier 1 complexity | Zero setup | Schema required | Filesystem |
| Git tracking | Native | Requires export | Filesystem |
| Human readability | Direct | SQL queries | Filesystem |
| Multi-agent writes | File locking | ACID transactions | SQLite |
| Tooling integration | Any editor | Requires driver | Filesystem |

**Decision**: For Tier 1 local development, filesystem simplicity outweighs database benefits. Tier 2+ may introduce database for concurrent writes if needed.

### Why Timestamp-Based Folders

1. **Natural sorting**: `ls -la` shows chronological order
2. **Easy filtering**: `find . -name "2026-02-04*"` for today's sessions
3. **Cleanup automation**: Delete folders older than N days
4. **No collision risk**: Timestamp + slug is unique

### Why Session-Scoped Files

1. **Atomic operations**: Each agent writes to own file (no merge conflicts)
2. **Parallel debugging**: Multiple agents work simultaneously
3. **Clear audit trail**: Each agent's contribution is traceable
4. **Flexible merging**: Resolution can reference any combination of findings

## Consequences

### Positive

- **Zero infrastructure**: Works immediately on any filesystem
- **Git-trackable**: Debug sessions can be committed for forensic analysis
- **Human-readable**: Developers can browse sessions without tooling
- **Multi-agent ready**: Each agent has isolated write space
- **Cleanup friendly**: Old sessions are self-contained for deletion

### Negative

- **Manual cleanup required**: Sessions accumulate without scheduled cleanup
- **No query capability**: Cannot easily search "all sessions involving file X"
- **Race conditions possible**: Two agents could create same folder at same millisecond
- **Disk space**: Large evidence files (logs, traces) could accumulate

### Mitigation

| Negative | Mitigation |
|----------|------------|
| Manual cleanup | Add cleanup script (`scripts/cleanup-debug-sessions.py --older-than 30d`) |
| No query | Add indexing script for Tier 2+ (`scripts/index-debug-sessions.py`) |
| Race conditions | Include random suffix in session ID if collision detected |
| Disk space | Evidence folder size limits in session_manifest.md |

## Alternatives Considered

### Alternative 1: Single File (progress.txt Extended)

**Pros**: Simpler, already exists
**Cons**: No session isolation, merge conflicts, no multi-agent support
**Rejected**: Does not scale to Wave 3 requirements

### Alternative 2: SQLite Database

**Pros**: ACID transactions, query capability, concurrent writes
**Cons**: Schema overhead, not Git-native, requires tooling
**Rejected**: Over-engineering for Tier 1; can add in Tier 2 if needed

### Alternative 3: JSONL Append-Only Log

**Pros**: Simple, append-only, easy parsing
**Cons**: No session grouping, hard to navigate, no evidence storage
**Rejected**: Lacks structure for multi-agent coordination

## Implementation Notes

1. **Folder creation**: Debug Agent creates folder at session start (Step 1)
2. **Metadata update**: JSON file updated after each step
3. **Findings write**: Each agent writes to `agent_{id}_findings.md`
4. **Resolution merge**: Lead agent creates `merge_resolution.md` when multiple agents involved
5. **LESSONS integration**: `outcome.md` includes LESSONS.md entry draft
6. **Cleanup**: Weekly cron or manual `cleanup-debug-sessions.py`

## Related

- [ADR-005: Agent Memory Directory Structure](ADR-005-agent-memory-structure.md) - Memory persistence pattern
- [ADR-008: Inter-Agent Report Pattern](../specs/TDD-HISTORICAL.md#adr-8-inter-agent-report-pattern) - Agent report conventions
- [WAVE3_PATHWAY_STRATEGY.md](../../temp/vibe_coding/WAVE3_PATHWAY_STRATEGY.md) - Tier maturation framework
- [x_post_backend.txt](../../temp/vibe_coding/x_post_backend.txt) - Original Debug Agent protocol

---

*Approved as part of Wave 3 Backend Leveling (WAVE3-004)*
