# TDD-022: PM Orchestration System

## Overview

**Source PRD**: PRD-022-PM-ORCHESTRATION
**Author**: Technical Architect
**Status**: Draft
**Created**: 2026-01-31
**Updated**: 2026-01-31

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

**Status**: Proposed

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

**Status**: Proposed

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

**Status**: Proposed

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
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PM ORCHESTRATION SYSTEM                            │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │   CLAUDE CODE    │
                              │    SESSIONS      │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
           ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
           │ MCP: Backlog  │  │ MCP: PM State │  │ MCP: dbt      │
           │ (task mgmt)   │  │ (session/query)│  │ (analytics)   │
           └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
                   │                  │                  │
                   ▼                  ▼                  ▼
           ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
           │  backlog/     │  │ pm_state.db   │  │ dbt models    │
           │  *.md files   │  │ (SQLite)      │  │ (DuckDB)      │
           └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
                   │                  │                  │
                   └──────────────────┴──────────────────┘
                                      │
                              ┌───────▼───────┐
                              │    SYNC       │
                              │   ENGINE      │
                              └───────┬───────┘
                                      │
                              ┌───────▼───────┐
                              │   DASHBOARD   │
                              │ (Workflow Hub)│
                              └───────────────┘
```

### Data Flow

```
WRITE PATH (Task Creation):
Claude → MCP Backlog → backlog/task.md → git commit → sync → pm_state.db

WRITE PATH (Session Registration):
Claude → MCP PM State → pm_state.db (sessions table)

READ PATH (Query):
Claude → MCP PM State → pm_state.db → session list / task status / alerts

ANALYTICS PATH:
pm_state.db → DuckDB ATTACH → dbt models → dim_project_health → Dashboard
```

---

## Database Schema

### Entity Relationship Diagram

```
┌──────────────┐       ┌─────────────────┐       ┌──────────────────┐
│   agents     │       │    sessions     │       │  session_events  │
├──────────────┤       ├─────────────────┤       ├──────────────────┤
│ agent_id PK  │       │ session_id PK   │       │ event_id PK      │
│ name         │       │ worktree_path   │       │ session_id FK    │
│ persona_type │       │ branch          │       │ event_type       │
│ description  │       │ pr_number       │       │ created_at       │
│ created_at   │       │ pr_status       │       │ metadata         │
└──────────────┘       │ pr_url          │       └──────────────────┘
       │               │ status          │
       │               │ started_at      │               ┌──────────────────┐
       │               │ last_heartbeat  │               │  agent_events    │
       │               │ ended_at        │               ├──────────────────┤
       │               └─────────────────┘               │ event_id PK      │
       │                       │                         │ session_id FK    │
       ▼                       ▼                         │ agent_id FK      │
┌──────────────┐       ┌─────────────────┐               │ event_type       │
│   handoffs   │       │     tasks       │               │ created_at       │
├──────────────┤       ├─────────────────┤               │ metadata         │
│ handoff_id PK│       │ task_id PK      │               └──────────────────┘
│ session_id FK│       │ title           │
│ from_agent FK│       │ status          │               ┌──────────────────┐
│ to_agent FK  │       │ priority        │               │     alerts       │
│ context      │       │ github_issue    │               ├──────────────────┤
│ created_at   │       │ assigned_session│               │ alert_id PK      │
└──────────────┘       │ depends_on      │               │ alert_type       │
                       │ created_at      │               │ severity         │
                       │ updated_at      │               │ message          │
                       └─────────────────┘               │ session_id FK    │
                               │                         │ task_id FK       │
                               ▼                         │ acknowledged     │
                       ┌─────────────────┐               │ created_at       │
                       │task_transitions │               └──────────────────┘
                       ├─────────────────┤
                       │ transition_id PK│               ┌──────────────────┐
                       │ task_id FK      │               │    sync_log      │
                       │ from_status     │               ├──────────────────┤
                       │ to_status       │               │ sync_id PK       │
                       │ session_id FK   │               │ direction        │
                       │ created_at      │               │ file_path        │
                       └─────────────────┘               │ status           │
                                                         │ conflict         │
                                                         │ created_at       │
                                                         └──────────────────┘
```

### DDL: Core Tables

```sql
-- Enable WAL mode for concurrent access
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

-- Agent registry
CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    persona_type TEXT NOT NULL,  -- 'orchestration', 'planning', 'implementation', 'quality', 'documentation', 'services'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Active and historical sessions
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    worktree_path TEXT NOT NULL,
    branch TEXT NOT NULL,
    pr_number INTEGER,
    pr_status TEXT,  -- 'draft', 'pending', 'approved', 'changes_requested'
    pr_url TEXT,
    status TEXT NOT NULL DEFAULT 'active',  -- 'active', 'stale', 'ended'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

-- Session lifecycle events
CREATE TABLE session_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    event_type TEXT NOT NULL,  -- 'start', 'heartbeat', 'end', 'error'
    metadata TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks (mirrors Backlog.md)
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,  -- Matches markdown filename
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'UNDERSTAND',  -- Matches workflow stages
    priority TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
    github_issue INTEGER,
    assigned_session TEXT REFERENCES sessions(session_id),
    depends_on TEXT,  -- JSON array of task_ids
    tags TEXT,  -- JSON array
    backlog_md_path TEXT,  -- Path to markdown file
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task state transitions (for analytics)
CREATE TABLE task_transitions (
    transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id),
    from_status TEXT,
    to_status TEXT NOT NULL,
    session_id TEXT REFERENCES sessions(session_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Proactive alerts
CREATE TABLE alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,  -- 'info', 'warning', 'error'
    message TEXT NOT NULL,
    session_id TEXT REFERENCES sessions(session_id),
    task_id TEXT REFERENCES tasks(task_id),
    acknowledged INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent activity tracking
CREATE TABLE agent_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    agent_id TEXT NOT NULL REFERENCES agents(agent_id),
    event_type TEXT NOT NULL,  -- 'invoked', 'completed', 'handoff'
    metadata TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inter-agent handoffs
CREATE TABLE handoffs (
    handoff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    from_agent TEXT NOT NULL REFERENCES agents(agent_id),
    to_agent TEXT NOT NULL REFERENCES agents(agent_id),
    context TEXT,  -- Summary of what's being handed off
    artifact_path TEXT,  -- Path to agent report
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Backlog.md sync tracking
CREATE TABLE sync_log (
    sync_id INTEGER PRIMARY KEY AUTOINCREMENT,
    direction TEXT NOT NULL,  -- 'md_to_db', 'db_to_md'
    file_path TEXT,
    status TEXT NOT NULL,  -- 'success', 'conflict', 'error'
    conflict_resolution TEXT,  -- How conflict was resolved
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_branch ON sessions(branch);
CREATE INDEX idx_sessions_pr ON sessions(pr_number);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_session);
CREATE INDEX idx_alerts_severity ON alerts(severity, acknowledged);
CREATE INDEX idx_agent_events_session ON agent_events(session_id);
```

### DDL: Seed Data (Agents)

```sql
INSERT INTO agents (agent_id, name, persona_type, description) VALUES
('supervisor', 'Supervisor', 'orchestration', 'Interface layer, workflow orchestration, quality gates'),
('pm', 'Product Manager', 'planning', 'Requirements, PRDs, GitHub issues'),
('architect', 'Architect', 'planning', 'System design, TDDs, architecture decisions'),
('data-modeler', 'Data Modeler', 'planning', 'dbt models, naming conventions, relationships'),
('developer', 'Developer', 'implementation', 'Feature implementation, clean code'),
('dbt-developer', 'dbt Developer', 'implementation', 'SQL models, macros, dbt best practices'),
('dbt-tester', 'dbt Tester', 'quality', 'Schema tests, data quality, freshness'),
('code-reviewer', 'Code Reviewer', 'quality', 'Code quality, bugs, patterns'),
('security-reviewer', 'Security Reviewer', 'quality', 'Security vulnerabilities, remediation'),
('documenter', 'Documenter', 'documentation', 'Living docs, CLAUDE.md, changelog'),
('sage', 'Sage', 'documentation', 'Learning curation, pattern extraction'),
('git-master', 'Git Master', 'services', 'Git operations, commits, PRs'),
('healthcare-analyst', 'Healthcare Analyst', 'domain', 'Clinical data patterns, compliance');
```

---

## MCP Tool Specifications

### Tool: pm_state_query

**Purpose**: Query sessions, tasks, alerts, and analytics.

**Schema**:

```json
{
  "name": "pm_state_query",
  "description": "Query PM orchestration state including sessions, tasks, and alerts",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query_type": {
        "type": "string",
        "enum": ["sessions", "tasks", "alerts", "conflicts", "health"],
        "description": "Type of query to execute"
      },
      "filters": {
        "type": "object",
        "properties": {
          "status": { "type": "string" },
          "session_id": { "type": "string" },
          "task_id": { "type": "string" },
          "severity": { "type": "string" },
          "acknowledged": { "type": "boolean" }
        }
      }
    },
    "required": ["query_type"]
  }
}
```

**Example Queries**:

```javascript
// Get all active sessions
pm_state_query({ query_type: "sessions", filters: { status: "active" } })

// Get unacknowledged alerts
pm_state_query({ query_type: "alerts", filters: { acknowledged: false } })

// Check for conflicts with current branch
pm_state_query({ query_type: "conflicts", filters: { branch: "feat/customer-analytics" } })

// Get project health score
pm_state_query({ query_type: "health" })
```

### Tool: pm_state_update

**Purpose**: Register sessions, send heartbeats, claim tasks.

**Schema**:

```json
{
  "name": "pm_state_update",
  "description": "Update PM orchestration state",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["register_session", "heartbeat", "end_session", "claim_task", "release_task", "acknowledge_alert"],
        "description": "Action to perform"
      },
      "session_id": { "type": "string" },
      "task_id": { "type": "string" },
      "alert_id": { "type": "integer" },
      "metadata": { "type": "object" }
    },
    "required": ["action"]
  }
}
```

**Example Updates**:

```javascript
// Register new session
pm_state_update({
  action: "register_session",
  metadata: {
    worktree_path: "/Users/cmbays/Documents/claude/dbt-playground",
    branch: "feat/customer-analytics",
    pr_number: 123
  }
})

// Send heartbeat (every 30 seconds)
pm_state_update({ action: "heartbeat", session_id: "abc-123" })

// Claim a task (atomic)
pm_state_update({ action: "claim_task", session_id: "abc-123", task_id: "add-dbt-expectations" })
```

### Tool: pm_state_analytics

**Purpose**: Query dbt analytics models for metrics.

**Schema**:

```json
{
  "name": "pm_state_analytics",
  "description": "Query dbt-powered analytics on PM state",
  "inputSchema": {
    "type": "object",
    "properties": {
      "metric": {
        "type": "string",
        "enum": ["health_score", "task_velocity", "bottlenecks", "agent_productivity"],
        "description": "Metric to retrieve"
      },
      "time_range": {
        "type": "string",
        "enum": ["1d", "7d", "30d", "all"],
        "default": "7d"
      }
    },
    "required": ["metric"]
  }
}
```

---

## dbt Model Structure

### Source Configuration

```yaml
# models/staging/pm_state/_pm_state__sources.yml
version: 2

sources:
  - name: pm_state
    description: PM orchestration state from SQLite database
    database: pm_state  # Attached via DuckDB
    schema: main
    tables:
      - name: sessions
        description: Active and historical Claude Code sessions
        columns:
          - name: session_id
            description: Unique session identifier
            data_tests:
              - unique
              - not_null
      - name: tasks
        description: Task state mirroring Backlog.md
        columns:
          - name: task_id
            data_tests:
              - unique
              - not_null
      - name: task_transitions
        description: Task status change history
      - name: alerts
        description: Proactive issue flagging
      - name: agent_events
        description: Agent invocation tracking
```

### DuckDB Attach Hook

```yaml
# dbt_project.yml (add to on-run-start)
on-run-start:
  - "ATTACH 'pm_state.db' AS pm_state (TYPE sqlite)"
```

### Staging Models

```sql
-- models/staging/pm_state/stg_pm_state__sessions.sql
with source as (
    select * from {{ source('pm_state', 'sessions') }}
)

select
    session_id
    , worktree_path
    , branch
    , pr_number
    , pr_status
    , pr_url
    , status as session_status
    , started_at
    , last_heartbeat
    , ended_at
    , case
        when status = 'active'
         and last_heartbeat < datetime('now', '-5 minutes')
        then true
        else false
      end as is_stale
    , julianday(coalesce(ended_at, datetime('now'))) - julianday(started_at) as session_duration_days
from source
```

```sql
-- models/staging/pm_state/stg_pm_state__tasks.sql
with source as (
    select * from {{ source('pm_state', 'tasks') }}
)

select
    task_id
    , title
    , status as task_status
    , priority
    , github_issue
    , assigned_session
    , json(depends_on) as depends_on_json
    , json(tags) as tags_json
    , backlog_md_path
    , created_at
    , updated_at
    , julianday(updated_at) - julianday(created_at) as task_age_days
from source
```

### Intermediate Models

```sql
-- models/intermediate/pm_state/int_pm_state__session_metrics.sql
with sessions as (
    select * from {{ ref('stg_pm_state__sessions') }}
)

, agent_events as (
    select
        session_id
        , count(*) as event_count
        , count(distinct agent_id) as agents_used
    from {{ source('pm_state', 'agent_events') }}
    group by session_id
)

select
    s.session_id
    , s.branch
    , s.pr_number
    , s.session_status
    , s.is_stale
    , s.session_duration_days
    , coalesce(ae.event_count, 0) as agent_events
    , coalesce(ae.agents_used, 0) as unique_agents
from sessions s
left join agent_events ae on s.session_id = ae.session_id
```

```sql
-- models/intermediate/pm_state/int_pm_state__task_flow.sql
with tasks as (
    select * from {{ ref('stg_pm_state__tasks') }}
)

, transitions as (
    select
        task_id
        , count(*) as transition_count
        , min(created_at) as first_transition
        , max(created_at) as last_transition
    from {{ source('pm_state', 'task_transitions') }}
    group by task_id
)

select
    t.task_id
    , t.title
    , t.task_status
    , t.priority
    , t.github_issue
    , t.task_age_days
    , coalesce(tr.transition_count, 0) as status_changes
    , tr.first_transition
    , tr.last_transition
    , case t.task_status
        when 'UNDERSTAND' then 1
        when 'PLAN' then 2
        when 'BUILD' then 3
        when 'VERIFY' then 4
        when 'DEPLOY' then 5
        when 'BLOCKED' then 0
      end as stage_order
from tasks t
left join transitions tr on t.task_id = tr.task_id
```

### Analytics Marts

```sql
-- models/marts/pm_analytics/dim_project_health.sql
with sessions as (
    select * from {{ ref('int_pm_state__session_metrics') }}
)

, tasks as (
    select * from {{ ref('int_pm_state__task_flow') }}
)

, alerts as (
    select
        severity
        , acknowledged
        , count(*) as alert_count
    from {{ source('pm_state', 'alerts') }}
    group by severity, acknowledged
)

, session_metrics as (
    select
        count(*) filter (where session_status = 'active') as active_sessions
        , count(*) filter (where is_stale) as stale_sessions
        , avg(session_duration_days) as avg_session_duration
    from sessions
)

, task_metrics as (
    select
        count(*) as total_tasks
        , count(*) filter (where task_status = 'BLOCKED') as blocked_tasks
        , count(*) filter (where task_status = 'DEPLOY') as completed_tasks
        , avg(task_age_days) filter (where task_status != 'DEPLOY') as avg_wip_age
    from tasks
)

, alert_metrics as (
    select
        sum(alert_count) filter (where severity = 'error' and acknowledged = 0) as unack_errors
        , sum(alert_count) filter (where severity = 'warning' and acknowledged = 0) as unack_warnings
    from alerts
)

select
    current_timestamp as calculated_at
    , sm.active_sessions
    , sm.stale_sessions
    , sm.avg_session_duration
    , tm.total_tasks
    , tm.blocked_tasks
    , tm.completed_tasks
    , tm.avg_wip_age
    , am.unack_errors
    , am.unack_warnings
    -- Health score: 100 - deductions
    , greatest(0, 100
        - (sm.stale_sessions * 10)  -- -10 per stale session
        - (tm.blocked_tasks * 5)    -- -5 per blocked task
        - (coalesce(am.unack_errors, 0) * 15)  -- -15 per unack error
        - (coalesce(am.unack_warnings, 0) * 3)  -- -3 per unack warning
      ) as health_score
from session_metrics sm
cross join task_metrics tm
cross join alert_metrics am
```

```sql
-- models/marts/pm_analytics/fct_agent_productivity.sql
with agent_events as (
    select
        ae.agent_id
        , a.name as agent_name
        , a.persona_type
        , date(ae.created_at) as activity_date
        , count(*) as invocations
        , count(distinct ae.session_id) as sessions
    from {{ source('pm_state', 'agent_events') }} ae
    left join {{ source('pm_state', 'agents') }} a on ae.agent_id = a.agent_id
    group by ae.agent_id, a.name, a.persona_type, date(ae.created_at)
)

select
    agent_id
    , agent_name
    , persona_type
    , activity_date
    , invocations
    , sessions
    , invocations * 1.0 / sessions as invocations_per_session
from agent_events
```

```sql
-- models/marts/pm_analytics/fct_task_bottlenecks.sql
with tasks as (
    select * from {{ ref('int_pm_state__task_flow') }}
)

, stage_durations as (
    select
        tt.task_id
        , tt.to_status as stage
        , julianday(lead(tt.created_at) over (
            partition by tt.task_id order by tt.created_at
          )) - julianday(tt.created_at) as stage_duration_days
    from {{ source('pm_state', 'task_transitions') }} tt
)

select
    stage
    , count(*) as tasks_in_stage
    , avg(stage_duration_days) as avg_duration_days
    , max(stage_duration_days) as max_duration_days
    , percentile_cont(0.9) within group (order by stage_duration_days) as p90_duration_days
from stage_durations
where stage_duration_days is not null
group by stage
order by avg_duration_days desc
```

---

## Sync Architecture

### Bi-directional Sync Protocol

```
┌─────────────────────────────────────────────────────────────────┐
│                      SYNC PROTOCOL                               │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────┐                              ┌─────────────┐
  │ Backlog.md  │                              │  SQLite DB  │
  │   (*.md)    │                              │ (pm_state)  │
  └──────┬──────┘                              └──────┬──────┘
         │                                            │
         ├────── On git commit ──────────────────────▶│
         │       (MD → DB sync)                       │
         │                                            │
         │       1. Parse frontmatter                 │
         │       2. Extract status, priority, deps    │
         │       3. Upsert to tasks table            │
         │       4. Record in sync_log                │
         │                                            │
         │◀────── On MCP update ──────────────────────┤
         │        (DB → MD sync)                      │
         │                                            │
         │        1. Read task from DB               │
         │        2. Update frontmatter in MD         │
         │        3. Record in sync_log               │
         │                                            │
         │                                            │
    CONFLICT RESOLUTION:                              │
    - Last-write-wins (timestamp comparison)          │
    - Log conflict in sync_log                        │
    - Alert generated for manual review               │
         │                                            │
         └────────────────────────────────────────────┘
```

### Backlog.md Task Format

```yaml
# backlog/add-dbt-expectations.md
---
title: "Integrate dbt_expectations package"
status: "BUILD"
priority: high
github_issue: 111
tags:
  - epic:v0.8
  - dbt
  - testing
depends_on:
  - install-dbt-packages
assigned_session: null
---

## Context

Enable advanced data quality testing with dbt_expectations package.

## Acceptance Criteria

- [ ] Package installed in packages.yml
- [ ] 5+ expectations added to staging models
- [ ] All tests passing

## Notes

See https://github.com/calogica/dbt-expectations
```

### Sync Script Pseudocode

```python
# scripts/backlog_sync.py

def sync_md_to_db(md_path: Path, db: sqlite3.Connection):
    """Parse markdown file and upsert to database."""
    content = md_path.read_text()
    frontmatter = parse_frontmatter(content)

    task_id = md_path.stem  # filename without extension

    db.execute("""
        INSERT OR REPLACE INTO tasks
        (task_id, title, status, priority, github_issue, depends_on, tags, backlog_md_path, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        task_id,
        frontmatter.get('title'),
        frontmatter.get('status', 'UNDERSTAND'),
        frontmatter.get('priority', 'medium'),
        frontmatter.get('github_issue'),
        json.dumps(frontmatter.get('depends_on', [])),
        json.dumps(frontmatter.get('tags', [])),
        str(md_path)
    ))

    log_sync(db, 'md_to_db', str(md_path), 'success')


def sync_db_to_md(task_id: str, db: sqlite3.Connection, backlog_dir: Path):
    """Update markdown file from database state."""
    row = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not row:
        return

    md_path = backlog_dir / f"{task_id}.md"
    if not md_path.exists():
        return

    content = md_path.read_text()
    updated = update_frontmatter(content, {
        'status': row['status'],
        'priority': row['priority'],
        'assigned_session': row['assigned_session']
    })

    md_path.write_text(updated)
    log_sync(db, 'db_to_md', str(md_path), 'success')
```

---

## Session Lifecycle

### Session Registration Protocol

```javascript
// On Claude session start (hook: session-start.js)

async function registerSession() {
  // 1. Generate session UUID
  const sessionId = uuidv4();

  // 2. Detect worktree path and branch
  const worktreePath = process.cwd();
  const branch = await exec('git branch --show-current');

  // 3. Check for linked PR
  let prNumber = null;
  let prStatus = null;
  let prUrl = null;
  try {
    const prInfo = await exec('gh pr view --json number,state,url');
    const pr = JSON.parse(prInfo);
    prNumber = pr.number;
    prStatus = pr.state;
    prUrl = pr.url;
  } catch (e) {
    // No PR linked to current branch
  }

  // 4. Register in database
  await mcpTool('pm_state_update', {
    action: 'register_session',
    metadata: { worktreePath, branch, prNumber, prStatus, prUrl }
  });

  // 5. Check for conflicts
  const conflicts = await mcpTool('pm_state_query', {
    query_type: 'conflicts',
    filters: { branch }
  });

  if (conflicts.length > 0) {
    console.warn('⚠️ Conflict detected:', conflicts);
    await mcpTool('pm_state_update', {
      action: 'create_alert',
      metadata: { type: 'task_conflict', severity: 'error', sessions: conflicts }
    });
  }

  // 6. Start heartbeat loop
  setInterval(() => {
    mcpTool('pm_state_update', { action: 'heartbeat', session_id: sessionId });
  }, 30000);

  return sessionId;
}
```

### Atomic Task Claiming

```sql
-- Atomic claim with optimistic locking
BEGIN IMMEDIATE;

-- Check if task is unclaimed or already claimed by us
SELECT assigned_session FROM tasks
WHERE task_id = :task_id
  AND (assigned_session IS NULL OR assigned_session = :session_id);

-- If row returned, claim it
UPDATE tasks
SET assigned_session = :session_id,
    updated_at = CURRENT_TIMESTAMP
WHERE task_id = :task_id
  AND (assigned_session IS NULL OR assigned_session = :session_id);

-- Check affected rows to confirm success
-- If 0 rows affected, another session claimed it first

COMMIT;
```

---

## File Changes Summary

### New Files

| File | Purpose |
|------|---------|
| `scripts/pm_state_init.py` | Database initialization script |
| `scripts/pm_state_mcp_server.ts` | MCP server for state tools |
| `scripts/backlog_sync.py` | Bi-directional sync engine |
| `.claude/hooks/session-start.js` | Session registration hook |
| `.claude/hooks/session-end.js` | Session termination hook |
| `.claude/mcp/pm-state-server.json` | MCP configuration |
| `.claude/rules/task-claiming.md` | Task locking convention |
| `docs/reference/BACKLOG_WORKFLOW.md` | Workflow documentation |
| `docs/reference/PM_STATE_SCHEMA.md` | Schema documentation |
| `models/staging/pm_state/*.sql` | Staging models (3) |
| `models/staging/pm_state/*.yml` | Source and model configs |
| `models/intermediate/pm_state/*.sql` | Intermediate models (2) |
| `models/marts/pm_analytics/*.sql` | Analytics marts (3) |
| `backlog/.backlog/config.yml` | Backlog.md configuration |
| `playgrounds/pm-dashboard.html` | Dashboard extension |

### Modified Files

| File | Change |
|------|--------|
| `CLAUDE.md` | Add Backlog.md workflow section |
| `dbt_project.yml` | Add on-run-start hook for SQLite attach |
| `.mcp.json` | Add pm-state server |
| `playgrounds/workflow-hub.html` | Add Backlog.md adapter |

---

## Testing Strategy

### Unit Tests

- [ ] Task frontmatter parsing handles all field types
- [ ] Sync handles missing files gracefully
- [ ] Heartbeat timeout detection works

### Integration Tests

- [ ] Session registration creates database record
- [ ] Task claiming is atomic (concurrent test)
- [ ] dbt models build successfully
- [ ] MCP tools return expected results

### E2E Tests

- [ ] Two worktrees can register sessions simultaneously
- [ ] Task claimed in worktree A is visible as claimed in worktree B
- [ ] Dashboard displays correct session grid
- [ ] Alerts appear within 30 seconds of trigger condition

---

## Implementation Sequence

1. [ ] **Phase 0**: Create Backlog.md config, map workflow stages
2. [ ] **Phase 1**: Install Backlog.md, configure MCP, migrate tasks
3. [ ] **Phase 2**: Create SQLite schema, implement basic MCP tools
4. [ ] **Phase 3**: Build dbt models, add data tests
5. [ ] **Phase 4**: Add session hooks, implement conflict detection
6. [ ] **Phase 5**: Build sync engine, extend dashboard

---

## Security Considerations

- Database file permissions should be 0600 (owner read/write only)
- No secrets stored in database (sessions are local identifiers)
- MCP tools should validate session ownership before task operations
- Sync script should not execute arbitrary content from markdown files

## Performance Considerations

- SQLite WAL mode enables concurrent reads
- Index on `sessions.status` for frequent active session queries
- Heartbeat interval (30s) balances freshness vs. overhead
- dbt models are incremental-ready if volume grows

---

## Related

- **PRD**: PRD-022-PM-ORCHESTRATION.md
- **ADRs**: ADR-001, ADR-002, ADR-003 (in docs/decisions/)
- **Prior Art**: temp/WORKFLOW_STATE.md
- **Workflow Reference**: docs/reference/WORKFLOW_STAGES.md
- **Agent Orchestration**: .claude/agents/AGENTS.md
