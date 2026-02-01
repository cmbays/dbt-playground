# ADR-001: Backlog.md Adoption for Task Management

**Status**: Proposed
**Date**: 2026-01-31
**Decision Makers**: Architect, PM
**Context**: PRD-022, TDD-022 (PM Orchestration System)

---

## Context

The PM Orchestration System requires a task management layer that:

1. **Persists across sessions** - Tasks survive session termination
2. **Is Git-tracked** - Visible in PRs, version controlled
3. **Works across worktrees** - Available after git push/pull
4. **Integrates with Claude** - MCP tool access for create/update
5. **Human-readable** - Usable without specialized tools
6. **Terminal-native** - Fits CLI-first development workflow

Current state: `temp/WORKFLOW_STATE.md` provides basic tracking but:

- Is a single file (doesn't scale, merge conflicts)
- Has no MCP integration
- Lacks structured querying

## Decision

**Adopt Backlog.md as the primary task management layer.**

Backlog.md is an MIT-licensed, markdown-native task management tool that provides:

- Individual task files in a `backlog/` directory
- YAML frontmatter for structured metadata
- Terminal Kanban board (`backlog board`)
- MCP integration for Claude access
- Full Git workflow support

## Rationale

### Options Considered

| Criterion | Backlog.md | GitHub Issues | Pure SQLite | Vibe Kanban | WORKFLOW_STATE.md |
|-----------|------------|---------------|-------------|-------------|-------------------|
| Git-Tracked | **Yes** | No | No | No | Yes |
| MCP Integration | **Yes** | Via gh CLI | Custom build | No | No |
| Offline Support | **Yes** | No | **Yes** | Yes | **Yes** |
| Human-Readable | **Markdown** | Web UI | SQL | Web UI | Markdown |
| Terminal Kanban | **Yes** | No | No | **Yes** | No |
| Worktree Sync | **Push/Pull** | API sync | Manual | External | Push/Pull |
| Structured Metadata | **YAML FM** | JSON API | Schema | JSON | Unstructured |
| Query Capability | Basic | **Full API** | **SQL** | Basic | None |
| Scalability | Good | Excellent | Excellent | Good | Poor |

### Why Backlog.md Over Alternatives

**vs. GitHub Issues**:

- Git-tracked means visible in PRs and history
- Works offline
- No API rate limits or external dependencies
- Faster iteration (no network round-trips)

**vs. Pure SQLite**:

- Human-readable without tooling
- Natural Git workflow
- No sync complexity for single-session use
- Still get SQLite via hybrid approach for real-time queries

**vs. Vibe Kanban**:

- Markdown files are portable
- No external service dependency
- Git history for audit trail
- MCP integration available

**vs. Extended WORKFLOW_STATE.md**:

- Individual files prevent merge conflicts
- Structured frontmatter enables tooling
- Terminal Kanban for visibility
- MCP integration for Claude access

### Why Hybrid with SQLite

Backlog.md alone lacks real-time cross-session awareness. The hybrid approach:

- Backlog.md = **Source of truth** (Git-tracked, PR-visible)
- SQLite = **Real-time state** (queries, heartbeats, alerts)
- Sync engine = **Keeps them aligned** (bi-directional)

This preserves the "markdown + Git" philosophy while adding the querying capability needed for cross-session orchestration.

## Consequences

### Positive

1. **Git-native workflow**: Tasks are code; review in PRs like any other change
2. **Terminal-first**: `backlog board` fits CLI development style
3. **MCP integration**: Claude can manage tasks directly
4. **Offline capable**: No external service required
5. **Human-readable**: Anyone can view/edit tasks in any text editor
6. **Portability**: Standard markdown, not locked to a vendor

### Negative

1. **Sync complexity**: Bi-directional sync with SQLite adds moving parts
2. **Eventual consistency**: Worktrees see changes after push/pull, not instantly
3. **Tool dependency**: Backlog.md is a third-party tool (MIT licensed)
4. **Learning curve**: Team must learn Backlog.md conventions

### Mitigation

| Negative | Mitigation |
|----------|------------|
| Sync complexity | Start simple (last-write-wins), log conflicts for review |
| Eventual consistency | SQLite provides real-time; markdown is "eventually consistent" |
| Tool dependency | MIT license allows forking; SQLite layer is fallback |
| Learning curve | Document in BACKLOG_WORKFLOW.md; training sessions |

## Alternatives Not Chosen

### Linear/Jira/Notion

- External SaaS tools outside project scope
- Require accounts, API keys, ongoing cost
- Not Git-tracked

### Custom React Dashboard

- Significant development effort
- Maintenance burden
- Not terminal-native

### Plain Text Files (No Tooling)

- No terminal Kanban
- No MCP integration
- Unstructured = hard to query

## Implementation Notes

1. Install: `brew install backlog-md`
2. Initialize: `backlog init "dbt-playground"`
3. Configure MCP: `claude mcp add backlog`
4. Map workflow stages to status columns in config
5. Migrate active tasks from WORKFLOW_STATE.md

## Related Decisions

- **ADR-002**: SQLite for cross-session state (complements this decision)
- **ADR-003**: dbt for PM analytics (consumes data from both layers)

## Review Cycle

This decision should be reviewed:

- After 3 months of use
- If Backlog.md project becomes unmaintained
- If multi-machine requirements emerge (consider Turso)

---

**Approval**: Pending (Architect review required)
