# ADR-002: SQLite State Layer for Cross-Session Awareness

**Status**: Superseded by Hybrid Lite Architecture (2026-02-01)
**Date**: 2026-01-31
**Decision Makers**: Architect
**Context**: PRD-022, TDD-022 (PM Orchestration System)

> **UPDATE (2026-02-01)**: This decision was **reversed** after discovering Backlog.md's
> full capabilities. SQLite complexity deemed unnecessary for v0.9. See:
>
> - ARCH_DECISION_HYBRID_LITE.md for reversal rationale
> - Issue #140 for future consideration
> - PRD-022 (updated) for Hybrid Lite scope

---

## Context

The PM Orchestration System requires real-time cross-session awareness:

1. **Session discovery** - Which Claude sessions are currently active?
2. **Conflict detection** - Are two sessions working on the same task?
3. **Heartbeat monitoring** - Is a session still alive or stale?
4. **Alert generation** - Surface issues proactively
5. **Historical tracking** - Analyze productivity patterns over time

Backlog.md (ADR-001) provides Git-tracked task persistence but cannot support:

- Real-time queries across worktrees
- Atomic task claiming
- Session lifecycle tracking
- Sub-second query latency

## Decision

**Use SQLite with WAL mode as the cross-session state database.**

The database (`pm_state.db`) lives in the project root and provides:

- Session registration and heartbeat tracking
- Task state mirroring (synced with Backlog.md)
- Alert storage and acknowledgment
- Agent event logging for analytics

## Rationale

### Options Considered

| Criterion | SQLite (WAL) | PostgreSQL | Redis | JSON Files | Turso |
|-----------|--------------|------------|-------|------------|-------|
| Infrastructure | **None** | Docker/Install | Docker | **None** | Cloud (SQLite-compatible) |
| Query Language | **SQL** | **SQL** | Commands | JS parsing | **SQL** |
| Concurrent Access | Good (WAL) | **Excellent** | **Excellent** | Poor | **Excellent** |
| dbt Integration | **Attach via DuckDB** | Direct | No | No | **Attach** |
| Latency | **<10ms** | ~50ms | **<5ms** | ~20ms | ~100ms (network) |
| Portability | **Single file** | Server | Server | Files | Cloud |
| Multi-Machine | No | Yes | **Yes** | Via sync | **Yes** |
| Cost | **Free** | **Free** (self-host) | **Free** (self-host) | **Free** | Free tier |

### Why SQLite

1. **Zero infrastructure**: No Docker, no server, no cloud account
2. **Single file portability**: Entire state in `pm_state.db`
3. **Full SQL**: Complex queries for analytics
4. **dbt compatible**: DuckDB can `ATTACH` SQLite databases
5. **WAL mode**: Enables concurrent reads while writing
6. **Battle-tested**: SQLite is in production on billions of devices

### Why Not PostgreSQL

- Requires Docker or local installation
- Overkill for single-machine, single-user scenario
- Adds operational complexity (backups, migrations, credentials)
- Can migrate later if needed

### Why Not Redis

- Requires server process
- Not SQL (learning curve)
- No dbt integration
- Better for high-throughput caching than structured state

### Why Not JSON Files

- No atomic operations (race conditions)
- Complex queries require parsing
- No indexing (slow as data grows)
- dbt cannot query directly

### Why Not Turso (Yet)

- Network latency adds 100ms+ per query
- Requires account and API key
- Free tier has limits
- **Upgrade path**: If multi-machine needed, migrate to Turso (SQLite-compatible)

## Consequences

### Positive

1. **Zero-config**: Works immediately, no setup
2. **Fast queries**: <10ms for typical operations
3. **dbt integration**: Analytics models can join PM state with project data
4. **Atomic operations**: SQLite transactions for task claiming
5. **Portability**: Copy `pm_state.db` to move state
6. **Durability**: WAL mode protects against crashes

### Negative

1. **Single-machine only**: Cannot share state across computers
2. **Concurrent write limits**: One writer at a time (WAL helps but doesn't eliminate)
3. **File locking**: May conflict with some backup tools
4. **No real-time sync**: Worktrees must query same file

### Mitigation

| Negative | Mitigation |
|----------|------------|
| Single-machine | Turso migration path (SQLite-compatible) |
| Write limits | WAL mode; batch writes; most ops are reads |
| File locking | Use `busy_timeout`; document backup approach |
| No sync | Single `pm_state.db` in project root, accessed by all worktrees |

## WAL Mode Configuration

```sql
-- Enable Write-Ahead Logging for concurrent access
PRAGMA journal_mode = WAL;

-- Wait up to 5 seconds for locks before failing
PRAGMA busy_timeout = 5000;

-- Synchronous mode for durability vs. performance
PRAGMA synchronous = NORMAL;
```

**WAL Benefits**:

- Readers don't block writers
- Writers don't block readers
- Crash recovery is faster
- Works across multiple processes (worktrees)

## Alternatives Not Chosen

### LevelDB/RocksDB

- Key-value only (no SQL)
- More complex API
- No dbt integration

### MongoDB (Local)

- Heavyweight for this use case
- Requires server process
- Document model less suitable for relational queries

### DuckDB (Single DB)

- Could use DuckDB for both analytics and state
- Chose SQLite for state to keep concerns separate
- DuckDB ATTACH allows querying both

### Plain Files with Locking

- Error-prone concurrency
- No query capability
- More code to maintain

## Implementation Notes

1. Create `scripts/pm_state_init.py` with DDL
2. Place `pm_state.db` in project root (excluded from Git via .gitignore)
3. Configure dbt to attach SQLite in `on-run-start`
4. Add `pm_state.db` to `.gitignore`
5. Document backup procedure

## Schema Summary

```
agents          - 12+ agent personas
sessions        - Active/historical sessions with PR linkage
session_events  - Lifecycle events (start, heartbeat, end)
tasks           - Task state (synced with Backlog.md)
task_transitions - Status change history
alerts          - Proactive issue flagging
agent_events    - Agent invocation tracking
handoffs        - Inter-agent communication
sync_log        - Backlog.md sync audit
```

See TDD-022 for full DDL.

## Related Decisions

- **ADR-001**: Backlog.md for task management (complementary)
- **ADR-003**: dbt for PM analytics (consumes this data)

## Review Cycle

This decision should be reviewed:

- If multi-machine development becomes common
- If query latency becomes problematic
- If Turso offers compelling local-first features

---

**Approval**: Pending (Architect review required)
