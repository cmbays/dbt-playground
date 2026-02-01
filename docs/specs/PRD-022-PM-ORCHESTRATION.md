# PRD-022: PM Orchestration System

## Overview

**Author**: Product Manager (Claude Code Agent System)
**Status**: Approved (Hybrid Lite)
**Created**: 2026-01-31
**Updated**: 2026-02-01

> **Architecture Update**: After discovery and evaluation of Backlog.md capabilities,
> the original SQLite + bi-directional sync architecture has been **replaced with
> Hybrid Lite**. See [ARCH_DECISION_HYBRID_LITE.md](../../temp/AGENT_REPORTS/pm-orchestration-backlog/ARCH_DECISION_HYBRID_LITE.md)
> for the full rationale.

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

Implement a **Hybrid Lite** PM orchestration system that provides:

1. **Markdown-native task management** via Backlog.md (Git-tracked, visible across worktrees)
2. **Lightweight session tracking** via PM_SESSIONS.json (heartbeat-enabled)
3. **Dashboard integration** via Workflow Hub widgets (visual coordination)

**Success Outcome**: Claude Code sessions gain persistent memory and coordination capability, enabling true parallel development without conflicts.

---

## Architecture Decision: Hybrid Lite

> **Key Insight**: Backlog.md provides 90% of our requirements out of the box.
> Adding SQLite creates complexity without proportional value for v0.9.

### Hybrid Lite Stack

```
Backlog.md (markdown + REST API + MCP)
    +
PM_SESSIONS.json (simple heartbeat tracker)
    |
    v
Workflow Hub (3 widgets)
```

### Why Hybrid Lite Over SQLite

| Factor | Original (SQLite) | Hybrid Lite |
|--------|------------------|-------------|
| Implementation time | 2-3 weeks | 4 hours |
| Systems to maintain | 3 (MD + SQLite + dbt) | 1 + 1 file |
| Sync complexity | Bi-directional engine | None (single source) |
| Browser UI | Must build custom | Built-in |
| MCP integration | Must build custom | Built-in |
| Git integration | Separate from tasks | Native |

### Confirmed Backlog.md Capabilities

- Full REST API (CRUD on tasks)
- Custom status columns (5-stage workflow)
- Assignee tracking per task
- Dependencies, labels, priorities
- Browser UI (drag-and-drop Kanban)
- Cross-worktree visibility via git remote branches
- Built-in MCP server for Claude
- CLI tools (`backlog task`, `backlog board`, etc.)

---

## User Stories

### Cross-Session Awareness

As a **Claude Code session starting in a worktree**, I want to query what other sessions are actively working on so that I can avoid duplicate work and potential conflicts.

As a **resuming session**, I want to see what previous sessions accomplished and what remains blocked so that I can pick up work efficiently without re-discovery.

As a **session encountering a conflict**, I want to be alerted immediately when another session claims the same task so that I can coordinate or defer.

### Task Management

As an **agent (any persona)**, I want to create and update tasks in a Git-tracked format so that task state persists across sessions and is visible in PRs.

As a **Supervisor agent**, I want to query task status, dependencies, and blockers so that I can orchestrate work across the 5-stage workflow.

As a **developer**, I want to claim tasks via assignee field so that parallel sessions can see what is being worked on.

### Dashboard Visibility

As a **PM**, I want to see task statistics at a glance so that I can assess project health quickly.

As a **project maintainer**, I want to see active sessions with heartbeat status so that I know which worktrees are actively being used.

As a **human (Chris)**, I want a dashboard showing project health at a glance so that I can assess progress without deep-diving into conversations.

---

## Requirements (v0.9 Scope)

### Functional Requirements

#### FR-1: Backlog.md Core Integration

Install and configure Backlog.md for markdown-native task management.

**Capabilities**:

- Terminal Kanban board (`backlog board`)
- MCP integration for Claude tool access
- REST API for programmatic access
- Git-tracked task files in `backlog/` directory
- Status columns mapped to 5-stage workflow (UNDERSTAND, PLAN, BUILD, VERIFY, DEPLOY, BLOCKED)

**Acceptance Criteria**:

- [x] `backlog board` displays current tasks in terminal
- [x] Backlog.md REST API functional at localhost:6420
- [x] Task files committed to Git and visible across worktrees after push/pull
- [x] Status column configuration matches workflow stages

**Status**: Complete (v1.35.4 installed)

#### FR-2: PM_SESSIONS.json Tracker

Implement lightweight session tracking file.

**Schema**:

```json
{
  "version": "1.0.0",
  "last_cleanup": "ISO-8601",
  "sessions": [
    {
      "session_id": "uuid",
      "worktree": "/absolute/path",
      "branch": "feat/example",
      "pr_number": 131,
      "pr_status": "draft",
      "last_heartbeat": "ISO-8601",
      "claimed_tasks": ["TASK-5"],
      "status": "active|stale|ended",
      "started_at": "ISO-8601",
      "ended_at": null
    }
  ]
}
```

**Acceptance Criteria**:

- [ ] Session registration on Supervisor startup
- [ ] Heartbeat update every 60 seconds
- [ ] Stale detection after 5 minutes without heartbeat
- [ ] Task claiming tracked in `claimed_tasks` array
- [ ] Session cleanup (remove entries > 30 days old)

#### FR-3: Workflow Hub Widgets

Add PM widgets to existing Workflow Hub playground.

**Widgets**:

| Widget | Purpose | Data Source |
|--------|---------|-------------|
| PM Overview | Task stats, active work, blocked items | Backlog.md REST API |
| Task Board | Full Kanban view | Backlog.md browser (iframe) |
| Active Sessions | Session grid with heartbeat status | PM_SESSIONS.json |

**Acceptance Criteria**:

- [ ] PM Overview widget displays status counts and active tasks
- [ ] Task Board widget embeds Backlog.md browser UI
- [ ] Active Sessions widget shows heartbeat freshness (healthy/warning)
- [ ] Stale sessions highlighted visually
- [ ] Link to full Backlog.md browser

#### FR-4: Supervisor Integration

Update Supervisor to use Backlog.md API for task management.

**Capabilities**:

- Query tasks via REST API
- Create tasks for new features
- Update task status on stage transitions
- Claim tasks via assignee update
- Register and maintain session heartbeat

**Acceptance Criteria**:

- [ ] Supervisor can query active tasks from API
- [ ] Supervisor can transition task status via API
- [ ] Supervisor registers session on startup
- [ ] Supervisor maintains heartbeat loop
- [ ] No remaining WORKFLOW_STATE.md dependencies for task tracking

### Non-Functional Requirements

1. **NFR-1 Performance**: API queries return in <500ms
2. **NFR-2 Reliability**: Session tracker resilient to file corruption
3. **NFR-3 Portability**: Works on macOS/Linux without external services
4. **NFR-4 Simplicity**: No Docker, Redis, or cloud dependencies required
5. **NFR-5 Git-Native**: Task state is Git-tracked and PR-visible

---

## Acceptance Criteria (v0.9)

### Phase 1: PM_SESSIONS.json (1 hour)

- [ ] PM_SESSIONS.json file created in `temp/`
- [ ] Session registration helper functions
- [ ] Heartbeat update mechanism
- [ ] Stale detection logic
- [ ] Task claiming tracker

### Phase 2: Workflow Hub Widgets (2 hours)

- [ ] PM Overview widget implemented
- [ ] Task Board widget with iframe embed
- [ ] Active Sessions widget with heartbeat status
- [ ] CSS styles for new widgets
- [ ] Error states for when Backlog.md not running

### Phase 3: Supervisor Integration (1 hour)

- [ ] Session lifecycle hooks (start, heartbeat, end)
- [ ] Backlog.md API calls for task CRUD
- [ ] Task claiming coordination
- [ ] WORKFLOW_STATE.md migration path documented

---

## Scope

### In Scope (v0.9)

**Hybrid Lite Implementation**:

- Backlog.md as primary task management system
- PM_SESSIONS.json for session heartbeats
- 3 widgets in Workflow Hub
- Supervisor integration with Backlog.md API
- Cross-worktree visibility via git

### Out of Scope (v0.9)

**Deferred to Future Enhancements**:

- SQLite state database (see Future Enhancements)
- Bi-directional sync engine (unnecessary with single source)
- dbt analytics models for PM state (see Future Enhancements)
- Custom dashboard beyond Hub widgets
- PR review status tracking in sessions
- Advanced alerting system

**Permanently Out of Scope**:

- Cloud database (Turso)
- GitHub Actions integration for state updates
- Mobile dashboard
- Historical session replay
- Machine learning for bottleneck prediction
- Integration with external PM tools (Jira, Linear)

---

## Future Enhancements

> These items were in the original PRD-022 scope but have been deferred.
> They should only be implemented if the Hybrid Lite approach proves insufficient.

### SQLite State Database (Deferred)

**When to consider**: If we encounter frequent task claiming race conditions or need genuine SQL analytics.

**Original scope**:

- 9-table schema (agents, sessions, tasks, etc.)
- Session heartbeat stored in DB
- Atomic task claiming via SQL transactions
- WAL mode for concurrent access

### dbt Analytics Integration (Deferred)

**When to consider**: If we need metrics like task velocity, bottleneck detection, or agent productivity.

**Original scope**:

```
models/
  staging/pm_state/
    stg_pm_state__sessions.sql
    stg_pm_state__tasks.sql
  marts/pm_analytics/
    fct_task_bottlenecks.sql
    dim_project_health.sql
```

### Bi-directional Sync (Not Needed)

**Status**: Eliminated by Hybrid Lite architecture.

With Backlog.md as the single source of truth, there is no need for a sync engine between markdown and database. All changes persist directly to markdown via the REST API.

### Advanced Alert System (Deferred)

**When to consider**: If simple stale detection proves insufficient.

**Original scope**:

| Alert | Condition |
|-------|-----------|
| Task Conflict | Two sessions claim same task |
| Orphaned Task | In Progress but no active session |
| Branch Drift | Branch behind main by 10+ commits |
| PR Changes Requested | PR needs attention |

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Backlog.md | External package | Installed (v1.35.4) |
| Workflow Hub | Internal playground | Available |
| gh CLI | GitHub integration | Already configured |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Session Discovery | <2 seconds | Time to see other sessions in Hub |
| Task Visibility | 100% | All active tasks visible across worktrees |
| Stale Detection | <6 minutes | Time from stale to flagged |
| Implementation Time | <4 hours | Total time to complete Phase 1-3 |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Backlog.md abandoned | Low | Medium | MIT license, can fork |
| Task claiming conflicts | Low | Low | Assignee discipline + git conflict resolution |
| Performance at scale | Low | Low | Test with realistic load first |
| Missing analytics | Medium | Low | Can parse markdown later if truly needed |

---

## Related

- **Architecture Decision**: [ARCH_DECISION_HYBRID_LITE.md](../../temp/AGENT_REPORTS/pm-orchestration-backlog/ARCH_DECISION_HYBRID_LITE.md)
- **Implementation Plan**: [IMPLEMENTATION_PLAN.md](../../temp/AGENT_REPORTS/pm-orchestration-backlog/IMPLEMENTATION_PLAN.md)
- **TDD**: TDD-022-PM-ORCHESTRATION.md (original technical design, reference only)
- **Prior Art**: temp/WORKFLOW_STATE.md, WORKFLOW_STAGES.md
- **Playgrounds**: playgrounds/workflow-hub.html
- **Agent Docs**: .claude/agents/supervisor.md
- **Backlog Config**: backlog/config.yml

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-31 | Initial PRD with SQLite + sync architecture |
| 2026-02-01 | Updated to Hybrid Lite architecture after Backlog.md discovery |
