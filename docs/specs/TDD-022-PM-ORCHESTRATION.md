# TDD-022: PM Orchestration System

> **SUPERSEDED**: This document has been superseded by [TDD-022-PM-ORCHESTRATION-HYBRID-LITE.md](./TDD-022-PM-ORCHESTRATION-HYBRID-LITE.md).
>
> After installing and testing Backlog.md, the team decided to simplify the architecture by eliminating SQLite and the bi-directional sync engine. See the Hybrid Lite TDD for the current design.
>
> This document is retained for historical reference only.

---

## Overview

**Source PRD**: PRD-022-PM-ORCHESTRATION
**Author**: Technical Architect
**Status**: Superseded
**Created**: 2026-01-31
**Updated**: 2026-02-01

### Summary

This TDD defines the technical architecture for a hybrid PM orchestration system combining:

- **Backlog.md** - Markdown-native task management (Git-tracked)
- **SQLite** - Cross-session state database (real-time awareness)
- **dbt Integration** - Analytics on agent productivity and project health
- **MCP Tools** - Claude access to query and update state

The system enables multi-session Claude Code workflows to coordinate work, avoid conflicts, and maintain persistent context.

---

## Architecture Decisions

### ADR-1: Backlog.md for Task Management

**Status**: Superseded by ADR-14 (Hybrid Lite)

**Context**: Claude Code sessions need persistent task tracking that:

- Is Git-tracked (visible in PRs, survives session termination)
- Works across worktrees after git push/pull
- Integrates with Claude via MCP
- Maintains human readability

**Decision**: Use Backlog.md as the primary task management layer.

**Rationale**:

| Criterion | Backlog.md | GitHub Issues | Pure SQLite | Vibe Kanban |
|-----------|------------|---------------|-------------|-------------|
| Git-Tracked | Yes | No | No | No |
| MCP Integration | Yes | Yes (gh CLI) | Custom | No |
| Offline Support | Yes | No | Yes | Yes |
| Human-Readable | Markdown | Web UI | SQL | Web UI |
| Terminal Kanban | Yes | No | No | Yes |
| Worktree Sync | Push/Pull | API | Manual | External |

**Consequences**:

- **Positive**: Tasks visible in PRs and Git history
- **Positive**: Works offline, no external services
- **Positive**: Terminal-native workflow (`backlog board`)
- **Negative**: Requires sync layer for real-time state
- **Mitigation**: SQLite layer provides real-time queries; sync keeps them aligned

**Approval**: Architect

---

### ADR-2: SQLite for Cross-Session State

**Status**: Superseded by ADR-15 (JSON File)

**Context**: Cross-session awareness requires:

- Real-time queries (which sessions are active?)
- Atomic operations (task claiming, conflict detection)
- Historical tracking (session lifecycle, task transitions)
- Low latency (<100ms for queries)

**Decision**: Use SQLite with WAL mode as the state database.

**Rationale**:

| Criterion | SQLite | PostgreSQL | Redis | JSON Files |
|-----------|--------|------------|-------|------------|
| Infrastructure | None | Docker/Install | Docker | None |
| Query Language | SQL | SQL | Commands | JS parsing |
| Concurrent Access | WAL mode | Excellent | Excellent | File locks |
| dbt Integration | Attach via DuckDB | Direct | No | No |
| Portability | Single file | Server | Server | Files |

**Consequences**:

- **Positive**: Zero infrastructure, single-file portability
- **Positive**: Full SQL query capability
- **Positive**: DuckDB can attach SQLite for dbt analytics
- **Negative**: Single-machine limitation
- **Mitigation**: Can migrate to Turso (SQLite-compatible) for multi-machine if needed

**Approval**: Architect

---

### ADR-3: dbt for PM Analytics

**Status**: Deferred (may be implemented in v1.0+)

**Context**: Project health metrics require:

- Session activity analysis
- Task flow and bottleneck detection
- Agent productivity tracking
- Trend analysis over time

**Decision**: Connect SQLite state to dbt as a source, build analytics models.

**Rationale**:

| Criterion | dbt Analytics | Custom Python | Metabase | No Analytics |
|-----------|---------------|---------------|----------|--------------|
| Existing Tooling | Yes (project uses dbt) | Manual | New tool | N/A |
| Testing | Data tests | Unit tests | None | N/A |
| Documentation | dbt docs | Manual | Auto | N/A |
| Incremental | Supported | Manual | Auto | N/A |

**Consequences**:

- **Positive**: Consistent with project tooling
- **Positive**: Tested and documented metrics
- **Positive**: Can join PM state with Synthea data if needed
- **Negative**: Adds models to maintain
- **Mitigation**: Separate `pm_state` source keeps it isolated

**Approval**: Architect

---

## High-Level Architecture

```
+-----------------------------------------------------------------------------+
|                          PM ORCHESTRATION SYSTEM                             |
+-----------------------------------------------------------------------------+

                              +------------------+
                              |   CLAUDE CODE    |
                              |    SESSIONS      |
                              +--------+---------+
                                       |
                    +------------------+------------------+
                    |                  |                  |
                    v                  v                  v
           +---------------+  +---------------+  +---------------+
           | MCP: Backlog  |  | MCP: PM State |  | MCP: dbt      |
           | (task mgmt)   |  | (session/query)|  | (analytics)   |
           +-------+-------+  +-------+-------+  +-------+-------+
                   |                  |                  |
                   v                  v                  v
           +---------------+  +---------------+  +---------------+
           |  backlog/     |  | pm_state.db   |  | dbt models    |
           |  *.md files   |  | (SQLite)      |  | (DuckDB)      |
           +-------+-------+  +-------+-------+  +-------+-------+
                   |                  |                  |
                   +------------------+------------------+
                                      |
                              +-------v-------+
                              |    SYNC       |
                              |   ENGINE      |
                              +-------+-------+
                                      |
                              +-------v-------+
                              |   DASHBOARD   |
                              | (Workflow Hub)|
                              +---------------+
```

---

*[Remainder of original document omitted for brevity. See git history for full content.]*

---

## Related

- **Current Design**: [TDD-022-PM-ORCHESTRATION-HYBRID-LITE.md](./TDD-022-PM-ORCHESTRATION-HYBRID-LITE.md)
- **PRD**: PRD-022-PM-ORCHESTRATION.md
- **Architecture Decision**: temp/AGENT_REPORTS/pm-orchestration-backlog/ARCH_DECISION_HYBRID_LITE.md
