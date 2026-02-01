# PRD-022: PM Orchestration System

## Overview

**Author**: Product Manager (Claude Code Agent System)
**Status**: Draft
**Created**: 2026-01-31
**Updated**: 2026-01-31

### Problem Statement

Multi-session Claude Code workflows lack persistent cross-session awareness. When multiple Claude sessions work in parallel (via git worktrees) or sequentially (across days), they cannot:

1. **See each other's work**: Session A cannot know Session B is working on a related task
2. **Avoid conflicts**: Two sessions may claim the same work or modify the same files
3. **Resume context**: A new session must re-discover what prior sessions accomplished
4. **Track health**: No proactive alerting for stalled work, blocked tasks, or drift

**Evidence of the problem**:

- `temp/WORKFLOW_STATE.md` exists but is not queryable or real-time
- Agent reports in `temp/AGENT_REPORTS/` are write-only artifacts without cross-session visibility
- Git worktree parallelism (documented in `docs/for_chris/GIT-WORKTREE-WORKFLOW.md`) lacks coordination layer
- Session resume relies on manual context loading or `--from-pr` flag without state awareness

**Impact**:

- Wasted effort from duplicate work
- Merge conflicts from uncoordinated changes
- Lost context requiring re-discovery archaeology
- No proactive issue detection (stale sessions, orphaned tasks, blocked work)

### Goal

Implement a hybrid PM orchestration system that provides:

1. **Markdown-native task management** via Backlog.md (Git-tracked, visible across worktrees)
2. **Real-time cross-session state** via SQLite database (queryable, heartbeat-enabled)
3. **Analytics on project health** via dbt integration (metrics, bottleneck detection)
4. **Proactive issue flagging** via enhanced dashboard (alerts, session grid)

**Success Outcome**: Claude Code sessions gain persistent memory and coordination capability, enabling true parallel development without conflicts.

## User Stories

### Cross-Session Awareness

As a **Claude Code session starting in a worktree**, I want to query what other sessions are actively working on so that I can avoid duplicate work and potential conflicts.

As a **resuming session**, I want to see what previous sessions accomplished and what remains blocked so that I can pick up work efficiently without re-discovery.

As a **session encountering a conflict**, I want to be alerted immediately when another session claims the same task so that I can coordinate or defer.

### Task Management

As an **agent (any persona)**, I want to create and update tasks in a Git-tracked format so that task state persists across sessions and is visible in PRs.

As a **Supervisor agent**, I want to query task status, dependencies, and blockers so that I can orchestrate work across the 5-stage workflow.

As a **developer**, I want to claim tasks atomically so that parallel sessions cannot accidentally work on the same item.

### Analytics & Health

As a **PM**, I want to see task velocity, bottleneck patterns, and cycle times so that I can identify process improvements.

As a **project maintainer**, I want proactive alerts for stale sessions, orphaned tasks, and blocked work so that issues surface before they become problems.

As a **human (Chris)**, I want a dashboard showing project health at a glance so that I can assess progress without deep-diving into conversations.

### PR Integration

As a **session linked to a PR** (via `claude --from-pr`), I want my work tracked against that PR so that PR review status is visible in the dashboard.

As a **reviewer**, I want to see which sessions are addressing PR feedback so that I know review comments are being resolved.

## Requirements

### Functional Requirements

#### FR-1: Backlog.md Core Integration

Install and configure Backlog.md for markdown-native task management.

**Capabilities**:

- Terminal Kanban board (`backlog board`)
- MCP integration for Claude tool access
- Git-tracked task files in `backlog/` directory
- Status columns mapped to 5-stage workflow (UNDERSTAND, PLAN, BUILD, VERIFY, DEPLOY, BLOCKED)

**Acceptance Criteria**:

- [ ] `backlog board` displays current tasks in terminal
- [ ] Claude can create/update tasks via MCP tool
- [ ] Task files committed to Git and visible across worktrees after push/pull
- [ ] Status column configuration matches workflow stages

#### FR-2: SQLite State Database

Implement persistent state layer for cross-session queries.

**Core Tables**:

| Table | Purpose |
|-------|---------|
| `agents` | Registry of 12+ agent personas |
| `sessions` | Active/historical Claude sessions with PR linkage |
| `session_events` | Session lifecycle (start, heartbeat, end) |
| `tasks` | Task state mirroring Backlog.md |
| `task_transitions` | Stage change history for analytics |
| `alerts` | Proactive issue flagging |
| `agent_events` | Agent invocation tracking |
| `handoffs` | Inter-agent communication log |
| `sync_log` | Backlog.md sync tracking |

**Acceptance Criteria**:

- [ ] Database initialized with schema via `scripts/pm_state_init.py`
- [ ] Sessions register on startup with worktree path, branch, PR number
- [ ] 30-second heartbeat maintains session liveness
- [ ] Stale sessions detected after 5 minutes without heartbeat
- [ ] WAL mode enabled for concurrent access

#### FR-3: MCP Tool Integration

Expose state database via MCP tools for Claude access.

**Tools**:

| Tool | Purpose |
|------|---------|
| `pm_state_query` | Read sessions, tasks, alerts, conflicts |
| `pm_state_update` | Register session, heartbeat, claim task |
| `pm_state_analytics` | Query dbt analytics models |

**Acceptance Criteria**:

- [ ] MCP server registered in `.mcp.json`
- [ ] Session can query other active sessions
- [ ] Task claiming is atomic (no race conditions)
- [ ] Conflict detection returns blocking alert

#### FR-4: dbt Analytics Integration

Connect SQLite state to dbt for analytics models.

**Model Structure**:

```
models/
├── staging/pm_state/
│   ├── stg_pm_state__sessions.sql
│   ├── stg_pm_state__tasks.sql
│   └── stg_pm_state__alerts.sql
├── intermediate/pm_state/
│   ├── int_pm_state__session_metrics.sql
│   └── int_pm_state__task_flow.sql
└── marts/pm_analytics/
    ├── fct_agent_productivity.sql
    ├── fct_task_bottlenecks.sql
    └── dim_project_health.sql
```

**Acceptance Criteria**:

- [ ] DuckDB attaches SQLite via `on-run-start` hook
- [ ] Staging models pass data tests (unique, not_null)
- [ ] `dim_project_health` returns health score
- [ ] Session metrics available for dashboard

#### FR-5: Bi-directional Sync

Synchronize Backlog.md (markdown) with SQLite (state database).

**Sync Protocol**:

1. **MD → DB**: On git commit, parse Backlog.md files and update DB
2. **DB → MD**: On status change via MCP, update Backlog.md file
3. **Conflict Resolution**: Last-write-wins with conflict log entry

**Acceptance Criteria**:

- [ ] Sync script runs on git hook (post-commit)
- [ ] Status changes in DB reflect in MD within 30 seconds
- [ ] Conflict log captures resolution decisions
- [ ] Manual sync command available: `python scripts/backlog_sync.py`

#### FR-6: Session-PR Linkage

Integrate with Claude's `--from-pr` feature for PR-centric workflow.

**Capabilities**:

- Store `pr_number`, `pr_status`, `pr_url` in sessions table
- Detect PR linkage via `gh pr view --json number`
- Track PR review status (draft, pending, approved, changes_requested)
- Resume any PR via `claude --from-pr 123`

**Acceptance Criteria**:

- [ ] Sessions auto-detect linked PR on startup
- [ ] PR status visible in dashboard
- [ ] Alert generated for "changes_requested" status
- [ ] Resume via `--from-pr` loads session context

#### FR-7: Proactive Alert System

Generate alerts for issues requiring attention.

**Alert Types**:

| Alert | Condition | Severity |
|-------|-----------|----------|
| Stale Session | No heartbeat > 5 min | Warning |
| Task Conflict | Two sessions claim same task | Error |
| Blocked Work | Task status = BLOCKED | Warning |
| Long-Running | Task in progress > 4 hrs | Info |
| Orphaned Task | In Progress but no active session | Error |
| Branch Drift | Branch behind main by 10+ commits | Warning |
| PR Changes Requested | PR status = changes_requested | Warning |
| PR Approved Stale | Approved but not merged > 24 hrs | Info |

**Acceptance Criteria**:

- [ ] Alerts written to `alerts` table with severity
- [ ] Dashboard displays alert feed
- [ ] Alerts can be acknowledged (dismissed)
- [ ] Critical alerts (Error) surface prominently

#### FR-8: Dashboard Component

Extend Workflow Hub or create PM Dashboard for visualization.

**Components**:

1. **Session Grid**: Active sessions with heartbeat status, PR linkage
2. **Alert Feed**: Proactive issues with severity and acknowledge button
3. **Health Score**: From `dim_project_health` (velocity, blocked rate)
4. **Task Board**: Kanban synced with Backlog.md
5. **PR Status Panel**: Review status for all linked PRs

**Acceptance Criteria**:

- [ ] Dashboard accessible via `/playground:pm` or extended Workflow Hub
- [ ] Auto-refresh every 30 seconds
- [ ] Sessions display heartbeat freshness (green/yellow/red)
- [ ] Health score prominently displayed

### Non-Functional Requirements

1. **NFR-1 Performance**: State queries return in <100ms for up to 100 sessions
2. **NFR-2 Reliability**: SQLite WAL mode prevents data corruption on crashes
3. **NFR-3 Portability**: Works on macOS/Linux without external services
4. **NFR-4 Simplicity**: No Docker, Redis, or cloud dependencies required
5. **NFR-5 Git-Native**: Task state is Git-tracked and PR-visible
6. **NFR-6 Backward Compatible**: Existing WORKFLOW_STATE.md continues working during migration

## Acceptance Criteria

### Phase 0: Foundation (Days 1-2)

- [ ] 5-stage workflow mapped to Backlog.md status columns
- [ ] Task locking convention documented
- [ ] Dual-write plan for WORKFLOW_STATE.md migration

### Phase 1: Backlog.md Core (Week 1)

- [ ] Backlog.md installed and configured
- [ ] MCP integration functional
- [ ] Active tasks migrated from WORKFLOW_STATE.md
- [ ] Terminal Kanban operational

### Phase 2: Database Foundation (Week 2)

- [ ] SQLite schema created (9 tables)
- [ ] Basic MCP tools operational
- [ ] Session registration working
- [ ] Heartbeat loop functional

### Phase 3: dbt Integration (Week 3)

- [ ] Staging models passing tests
- [ ] Analytics marts running
- [ ] Health score queryable
- [ ] `dbt show --select dim_project_health` returns data

### Phase 4: Multi-Session Orchestration (Week 4)

- [ ] Atomic task claiming works
- [ ] Conflict detection alerts
- [ ] `--from-pr` integration complete
- [ ] Two sessions can coordinate without conflict

### Phase 5: Sync + Dashboard (Weeks 5-6)

- [ ] Bi-directional sync operational
- [ ] Dashboard shows sessions and alerts
- [ ] Health score displayed
- [ ] Auto-refresh functional

## Scope

### In Scope

**Phase 0-1 (Foundation + Core)**:

- Backlog.md installation and configuration
- 5-stage workflow column mapping
- MCP integration
- Migration from WORKFLOW_STATE.md

**Phase 2-3 (Database + Analytics)**:

- SQLite state schema
- Session registration protocol
- dbt staging and analytics models
- Basic health metrics

**Phase 4-5 (Orchestration + Dashboard)**:

- Multi-session conflict detection
- PR linkage via `--from-pr`
- Bi-directional sync
- Dashboard with alerts

### Out of Scope

- Cloud database (Turso) - future enhancement if multi-machine needed
- GitHub Actions integration for state updates
- Mobile dashboard
- Historical session replay
- Machine learning for bottleneck prediction
- Integration with external PM tools (Jira, Linear)

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Backlog.md | External package | Available via Homebrew |
| SQLite | System library | Built into Python |
| DuckDB | dbt adapter | Already configured |
| Claude MCP | Feature | Available |
| gh CLI | GitHub integration | Already configured |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Session Discovery | <2 seconds | Time to query active sessions |
| Conflict Rate | 0 undetected | No two sessions work same task |
| Context Resume | <1 minute | Time to resume session via `--from-pr` |
| Alert Response | <5 minutes | Time from issue to alert visibility |
| Health Score Accuracy | >90% | Health score reflects actual state |
| Stale Session Detection | 100% | All stale sessions flagged |

## Open Questions

1. **Should we use Turso for multi-machine state?**
   - Recommendation: Start with SQLite; migrate to Turso only if multi-machine becomes a requirement.

2. **How do we handle conflicting sync updates?**
   - Recommendation: Last-write-wins with conflict log; can implement OT/CRDT later if needed.

3. **Should the dashboard be a new playground or extend Workflow Hub?**
   - Recommendation: Extend Workflow Hub to avoid UI proliferation.

4. **What happens if Backlog.md is abandoned?**
   - Recommendation: MIT license allows forking; SQLite layer provides fallback.

5. **How do we handle agent reports integration?**
   - Recommendation: Keep `temp/AGENT_REPORTS/` separate; dashboard links to them.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Task storage | Backlog.md (markdown) | Git-tracked, visible in PRs, human-readable |
| State storage | SQLite | Zero infrastructure, portable, queryable |
| Analytics | dbt | Consistent with project tooling, enables metrics marts |
| Dashboard | HTML playground | Single-file, no build step, consistent with existing playgrounds |
| Sync approach | Bi-directional | Both sources are authoritative; last-write-wins |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Backlog.md abandoned | Low | Medium | MIT license, can fork |
| SQLite concurrency limits | Low | Medium | WAL mode; Turso if scaling needed |
| Sync conflicts | Medium | Low | Last-write-wins, conflict logging |
| Dashboard scope creep | Medium | Medium | Time-box to 2 weeks |
| Migration disruption | Medium | Medium | Dual-write during Phase 1 |

## Related

- **TDD**: TDD-022-PM-ORCHESTRATION.md (to be created)
- **ADRs**: ADR-001, ADR-002, ADR-003 (to be created)
- **Prior Art**: temp/WORKFLOW_STATE.md, WORKFLOW_STAGES.md
- **Playgrounds**: playgrounds/workflow-hub.html
- **Agent Docs**: .claude/agents/supervisor.md
