# TDD-022: PM Orchestration System (Hybrid Lite)

## Overview

**Source PRD**: PRD-022-PM-ORCHESTRATION
**Author**: Technical Architect
**Status**: Approved
**Created**: 2026-01-31
**Updated**: 2026-02-01

### Summary

This TDD defines the **Hybrid Lite** architecture for PM orchestration, superseding the original TDD-022. After installing and testing Backlog.md, the team decided to simplify the architecture by eliminating SQLite and the bi-directional sync engine in favor of:

1. **Backlog.md** - Primary task management (REST API + markdown persistence)
2. **PM_SESSIONS.json** - Lightweight session heartbeat tracking
3. **Workflow Hub Widgets** - Dashboard integration (3 widgets)

**Result**: 90% of desired features with 10% of the complexity.

### Design Goals

1. **Single source of truth**: Backlog.md markdown files (Git-tracked)
2. **No infrastructure**: No SQLite database, no sync engine
3. **Git-native**: Tasks visible in PRs, full history
4. **Rapid implementation**: 4 hours vs. 2-3 weeks original estimate
5. **Extensible**: Can add SQLite analytics layer later if proven necessary

---

## Architecture Decisions

### ADR-14: Hybrid Lite Architecture

**Status**: Approved

**Context**: The original TDD-022 proposed a complex architecture with Backlog.md, SQLite, bi-directional sync, and dbt analytics. After installing Backlog.md and testing its capabilities, we discovered it provides most features natively.

**Decision**: Adopt Hybrid Lite architecture using Backlog.md as the sole task system, with PM_SESSIONS.json for session tracking.

**Rationale**:

| Criterion | Original (SQLite) | Hybrid Lite |
|-----------|------------------|-------------|
| Implementation Time | 2-3 weeks | 4 hours |
| Systems to Maintain | 3 (MD + SQLite + Sync) | 2 (MD + JSON) |
| Task CRUD | SQL queries | REST API |
| Git Tracking | Separate from tasks | Native |
| Browser UI | Custom build | Built-in |
| Real-time Queries | SQL | REST API + JSON |

**Consequences**:

- **Positive**: Zero infrastructure, single source of truth, rapid delivery
- **Positive**: Git-tracked tasks visible in PRs and history
- **Positive**: Built-in browser UI, CLI, and MCP server from Backlog.md
- **Negative**: No SQL analytics (deferred)
- **Negative**: Non-atomic task claiming (last-write-wins)
- **Mitigation**: Assignee discipline prevents conflicts; analytics can be added later if needed

**Approval**: Architect, Supervisor, Product Manager

---

### ADR-15: Session Tracking via JSON File

**Status**: Approved

**Context**: Cross-session awareness requires tracking active Claude Code sessions, their heartbeats, and claimed tasks. Options: SQLite, Redis, or simple JSON file.

**Decision**: Use PM_SESSIONS.json in `temp/` directory with 60-second heartbeat updates.

**Rationale**:

| Criterion | SQLite | JSON File |
|-----------|--------|-----------|
| Infrastructure | Single file | Single file |
| Query Capability | Full SQL | JS parsing |
| Concurrent Access | WAL mode | Last-write-wins |
| Complexity | Medium | Low |
| Human Readable | No | Yes |

**Consequences**:

- **Positive**: Simple, no dependencies, human-readable for debugging
- **Negative**: No query engine, manual conflict resolution
- **Mitigation**: 1-2 concurrent sessions makes conflicts extremely rare

**Approval**: Architect

---

## Architecture Overview

### High-Level Stack

```
+-------------------------------------------------------------+
|                      Workflow Hub                            |
|  +------------+  +------------+  +------------+             |
|  |  Overview  |  |   Kanban   |  |  Sessions  |             |
|  |   Widget   |  |   Widget   |  |   Widget   |             |
|  +-----+------+  +-----+------+  +-----+------+             |
|        |              |              |                       |
+--------|--------------|--------------|----------------------+
         |              |              |
         v              v              v
  +-----------+   +-----------+   +--------------+
  | Backlog   |   | Backlog   |   | PM_SESSIONS  |
  | REST API  |   | Browser   |   | .json        |
  +-----------+   | (iframe)  |   +--------------+
         |        +-----------+
         v
  +---------------------+
  | backlog/tasks/*.md  |  <-- Git-tracked
  | (Markdown files)    |
  +---------------------+
```

### Data Flow

```
WRITE PATH (Task Operations):
Supervisor --> Backlog.md REST API --> backlog/tasks/*.md --> git commit

WRITE PATH (Session Registration):
Supervisor --> PM_SESSIONS.json

READ PATH (Dashboard):
Workflow Hub --> Backlog.md REST API --> Task stats
Workflow Hub --> PM_SESSIONS.json --> Active sessions

SYNC PATH (Cross-Worktree):
Worktree A: git push --> GitHub --> Worktree B: git pull
```

---

## Component Specifications

### 1. Backlog.md Integration

#### REST API Endpoints

Backlog.md provides a complete REST API at `http://localhost:6420`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/tasks` | GET | List all tasks |
| `/api/tasks` | POST | Create task |
| `/api/tasks/:id` | GET | Get task |
| `/api/tasks/:id` | PUT | Update task |
| `/api/tasks/:id` | DELETE | Delete task |
| `/api/config` | GET | Get board config |
| `/api/milestones` | GET | Get milestones |

#### Task Object Schema

```json
{
  "id": "TASK-2",
  "title": "API Test Task",
  "status": "BUILD",
  "assignee": ["session-abc123"],
  "createdDate": "2026-02-01 05:06",
  "updatedDate": "2026-02-01 05:07",
  "labels": ["test", "api"],
  "dependencies": [],
  "priority": "high",
  "acceptanceCriteriaItems": [],
  "definitionOfDoneItems": [],
  "description": "Task description in markdown",
  "filePath": "/path/to/backlog/tasks/task-2.md",
  "lastModified": "2026-02-01T05:07:00Z"
}
```

#### Markdown File Format

All API changes persist immediately to markdown:

```yaml
# backlog/tasks/task-2.md
---
id: TASK-2
title: API Test Task
status: BUILD
assignee:
  - session-abc123
labels:
  - test
  - api
priority: high
createdDate: 2026-02-01 05:06
updatedDate: 2026-02-01 05:07
---

Task description in markdown format.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

---

### 2. PM_SESSIONS.json Schema

#### File Location

`temp/PM_SESSIONS.json`

#### Schema Definition

```typescript
interface PMSessionsFile {
  version: "1.0.0";
  last_cleanup: string;           // ISO 8601 timestamp
  sessions: Session[];
}

interface Session {
  session_id: string;             // UUID v4
  worktree: string;               // Absolute path to worktree
  branch: string;                 // Current git branch
  pr_number: number | null;       // Linked PR number
  pr_status: string | null;       // draft | pending | approved
  last_heartbeat: string;         // ISO 8601 timestamp
  claimed_tasks: string[];        // Array of TASK-IDs
  status: "active" | "stale" | "ended";
  started_at: string;             // ISO 8601 timestamp
  ended_at: string | null;        // ISO 8601 timestamp
}
```

#### Example File

```json
{
  "version": "1.0.0",
  "last_cleanup": "2026-02-01T00:00:00Z",
  "sessions": [
    {
      "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "worktree": "/Users/cmbays/Documents/claude/parent-dbt-playground/dbt-playground",
      "branch": "main",
      "pr_number": null,
      "pr_status": null,
      "last_heartbeat": "2026-02-01T05:10:00Z",
      "claimed_tasks": ["TASK-5", "TASK-7"],
      "status": "active",
      "started_at": "2026-02-01T04:00:00Z",
      "ended_at": null
    },
    {
      "session_id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
      "worktree": "/Users/cmbays/Documents/claude/parent-dbt-playground/dbt-playground--customer-analytics",
      "branch": "feat/customer-analytics",
      "pr_number": 131,
      "pr_status": "draft",
      "last_heartbeat": "2026-02-01T05:08:00Z",
      "claimed_tasks": ["TASK-12"],
      "status": "active",
      "started_at": "2026-02-01T03:30:00Z",
      "ended_at": null
    }
  ]
}
```

#### Update Patterns

| Operation | When | What Changes |
|-----------|------|--------------|
| Register | Session start | New session object added |
| Heartbeat | Every 60s | `last_heartbeat` timestamp |
| Claim task | Task assignment | `claimed_tasks` array |
| Release task | Task completion | `claimed_tasks` array |
| End session | Session close | `status: "ended"`, `ended_at` set |
| Stale detection | Heartbeat check | `status: "stale"` if >5 min since heartbeat |
| Cleanup | Daily | Remove sessions >30 days old |

---

### 3. Workflow Hub Widgets

#### Widget 1: PM Overview

**Purpose**: Display task statistics and active work summary.

**Data Source**: Backlog.md REST API (`GET /api/tasks`, `GET /api/config`)

**Display Elements**:

- Status grid with counts per column
- Active tasks list (BUILD + VERIFY status)
- Blocked tasks alert section
- Link to full Backlog.md browser

```javascript
// Widget structure
{
  id: 'pm-overview',
  title: 'PM Overview',
  icon: 'chart-bar',
  async render() {
    const tasks = await fetch('http://localhost:6420/api/tasks').then(r => r.json());
    const config = await fetch('http://localhost:6420/api/config').then(r => r.json());
    // Render status grid, active tasks, blocked alerts
  }
}
```

#### Widget 2: Kanban Board (iframe)

**Purpose**: Embed full Backlog.md browser UI for drag-and-drop task management.

**Data Source**: Backlog.md browser at `http://localhost:6420`

**Implementation**: iframe with sandbox permissions

```html
<iframe
  src="http://localhost:6420"
  sandbox="allow-same-origin allow-scripts allow-forms"
  style="width: 100%; height: calc(100vh - 120px); border: none;"
></iframe>
```

#### Widget 3: Active Sessions

**Purpose**: Show session grid with heartbeat status and claimed tasks.

**Data Source**: `temp/PM_SESSIONS.json` (requires file server proxy)

**Display Elements**:

- Session cards with branch, PR link, health status
- Claimed tasks per session
- Stale session alerts
- Last heartbeat timestamp

---

## Sequence Diagrams

### Session Registration and Heartbeat

```
                    Supervisor                  PM_SESSIONS.json
                        |                             |
                        |  1. Generate UUID           |
                        |--+                          |
                        |  |                          |
                        |<-+                          |
                        |                             |
                        |  2. Read existing sessions  |
                        |<----------------------------|
                        |                             |
                        |  3. Add new session object  |
                        |---------------------------->|
                        |                             |
                        |  4. Start heartbeat loop    |
                        |--+                          |
                        |  | (every 60s)              |
                        |  |                          |
               +--------|<-+                          |
               |        |                             |
  Every 60s    |        |  5. Update last_heartbeat   |
               +------->|---------------------------->|
                        |                             |
                        |  6. Check for stale sessions|
                        |<----------------------------|
                        |                             |
                        |  7. Mark stale if >5 min    |
                        |---------------------------->|
```

### Task Claiming Workflow

```
      Supervisor              Backlog.md API           PM_SESSIONS.json
          |                         |                        |
          |  1. GET /api/tasks/:id  |                        |
          |------------------------>|                        |
          |                         |                        |
          |  2. Check assignee      |                        |
          |<------------------------|                        |
          |                         |                        |
          |  3. If unassigned,      |                        |
          |     PUT assignee        |                        |
          |------------------------>|                        |
          |                         |                        |
          |                         |  (persists to md)      |
          |                         |--------+               |
          |                         |        |               |
          |                         |<-------+               |
          |                         |                        |
          |  4. Update claimed_tasks|                        |
          |------------------------------------------------->|
          |                         |                        |
          |  5. Confirm claim       |                        |
          |<------------------------|                        |
```

### Cross-Session Visibility

```
   Worktree A              GitHub                 Worktree B
       |                     |                        |
       |  1. Update task     |                        |
       |  (via Backlog API)  |                        |
       |                     |                        |
       |  2. git commit      |                        |
       |-------------------->|                        |
       |                     |                        |
       |  3. git push        |                        |
       |-------------------->|                        |
       |                     |                        |
       |                     |  4. Remote updated     |
       |                     |----------------------->|
       |                     |                        |
       |                     |  5. git fetch/pull     |
       |                     |<-----------------------|
       |                     |                        |
       |                     |  6. backlog board      |
       |                     |      shows update      |
       |                     |                        |
       |                     |                        |
   +---+---+                 |                        |
   | Note: Backlog.md also   |                        |
   | scans remote branches   |                        |
   | for cross-session       |                        |
   | visibility (last 30d)   |                        |
   +-------------------------+                        |
```

---

## Testing Strategy

### Unit Tests

| Test | Description | Verification |
|------|-------------|--------------|
| Session registration | Creates valid session object | JSON schema validation |
| Heartbeat update | Updates timestamp correctly | Timestamp within 1s of expected |
| Stale detection | Marks sessions >5 min old as stale | Status changes to "stale" |
| Task claiming | Adds task to claimed_tasks array | Array contains task ID |
| Cleanup | Removes sessions >30 days old | Old sessions not in file |

### Integration Tests

| Test | Description | Verification |
|------|-------------|--------------|
| Backlog API CRUD | Create, read, update, delete tasks | API returns expected data |
| Session <-> Backlog | Claimed task shows assignee | Markdown file has assignee |
| Widget data fetch | Overview widget loads data | Stats match API response |
| iframe embed | Kanban widget loads board | iframe accessible, interactive |

### End-to-End Tests

| Test | Description | Verification |
|------|-------------|--------------|
| Two worktrees | Both register separate sessions | PM_SESSIONS.json has 2 entries |
| Task claim conflict | Second session sees claimed task | Assignee shown in Backlog board |
| Stale detection | Session inactive >5 min | Widget shows stale warning |
| Session cleanup | End session | Status: "ended", ended_at set |
| Git sync | Push in A, pull in B | Task visible in both worktrees |

### Test Commands

```bash
# Start Backlog.md server
backlog browser --port 6420

# Verify API
curl http://localhost:6420/api/tasks

# Run session registration
node scripts/pm_sessions.js register

# Check stale sessions
node scripts/pm_sessions.js check-stale

# List all sessions
node scripts/pm_sessions.js list
```

---

## Migration from WORKFLOW_STATE.md

### Current State

```yaml
# temp/WORKFLOW_STATE.md (manually maintained)
Active Track: feat/pm-orchestration-backlog
Phase: VERIFY
```

### Migration Steps

1. **Create Backlog task** for each active WORKFLOW_STATE entry:

   ```bash
   backlog task create --title "PM Orchestration - Backlog.md Core" \
     --status VERIFY \
     --labels "epic:pm-orchestration,phase:1"
   ```

2. **Assign session** to migrated task:

   ```bash
   curl -X PUT http://localhost:6420/api/tasks/TASK-N \
     -H "Content-Type: application/json" \
     -d '{"assignee": ["current-session-id"]}'
   ```

3. **Update CLAUDE.md** to reference Backlog.md instead of WORKFLOW_STATE.md

4. **Archive WORKFLOW_STATE.md** (keep for reference during transition)

### Post-Migration Verification

- [ ] All active work has corresponding Backlog tasks
- [ ] Sessions registered in PM_SESSIONS.json
- [ ] Workflow Hub widgets display data
- [ ] WORKFLOW_STATE.md references removed from CLAUDE.md

---

## File Changes Summary

### New Files

| File | Purpose |
|------|---------|
| `temp/PM_SESSIONS.json` | Session heartbeat tracking |
| `scripts/pm_sessions.js` | Session management CLI |
| `playgrounds/widgets/pm-overview.js` | Overview widget component |
| `playgrounds/widgets/pm-sessions.js` | Sessions widget component |

### Modified Files

| File | Change |
|------|--------|
| `playgrounds/workflow-hub.html` | Add 3 PM widgets |
| `.claude/agents/supervisor.md` | Session lifecycle hooks |
| `CLAUDE.md` | Replace WORKFLOW_STATE references |

### Backlog.md Files (created by tool)

| File | Purpose |
|------|---------|
| `backlog/.backlog/config.yml` | Board configuration |
| `backlog/tasks/*.md` | Individual task files |

---

## Implementation Sequence

### Phase 1: PM_SESSIONS.json (1 hour)

- [ ] Create initial JSON file with schema
- [ ] Implement register, heartbeat, end functions
- [ ] Implement stale detection
- [ ] Add CLI interface for testing

### Phase 2: Workflow Hub Widgets (2 hours)

- [ ] Widget 1: PM Overview (fetch from API, render stats)
- [ ] Widget 2: Kanban iframe (embed Backlog.md browser)
- [ ] Widget 3: Active Sessions (read JSON, show grid)
- [ ] Add CSS styles for widgets

### Phase 3: Supervisor Integration (1 hour)

- [ ] Add session lifecycle hooks (start, heartbeat, end)
- [ ] Replace WORKFLOW_STATE calls with Backlog API
- [ ] Add task claiming workflow
- [ ] Test orchestration flow

---

## Security Considerations

- **PM_SESSIONS.json permissions**: File in `temp/` is gitignored by default
- **No credentials**: Session IDs are local identifiers only
- **Backlog.md API**: Local-only server (localhost:6420), no auth needed
- **Task content**: No sensitive data in task descriptions

## Performance Considerations

- **Heartbeat interval**: 60s balances freshness vs. file I/O
- **Stale threshold**: 5 minutes allows for temporary disconnections
- **API calls**: Widgets fetch on load, no polling (manual refresh)
- **iframe**: Full Backlog.md UI, may be heavy on low-memory systems

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Task claiming conflicts | Low | Low | Assignee discipline, git conflict resolution |
| Backlog.md abandoned | Low | Medium | MIT license, can fork; core is markdown files |
| Performance at scale | Low | Low | Test with realistic load; <100 tasks expected |
| Missing analytics | Medium | Low | Parse markdown if truly needed; defer to v1.0 |
| JSON file corruption | Low | Medium | Git tracks `backlog/`; `temp/` is ephemeral anyway |

---

## Success Criteria

### v0.9 Must Have

- [x] Backlog.md installed and configured
- [ ] PM_SESSIONS.json tracks sessions with heartbeats
- [ ] Stale sessions detected within 6 minutes
- [ ] 3 Workflow Hub widgets functional
- [ ] Supervisor creates/updates tasks via API
- [ ] Tasks sync across worktrees via git

### Future (v1.0+)

- [ ] SQLite analytics layer (if proven necessary)
- [ ] Advanced alerting system
- [ ] Custom dashboard (if Backlog.md UI insufficient)
- [ ] dbt models for PM analytics

---

## Related

- **PRD**: PRD-022-PM-ORCHESTRATION
- **Original TDD**: TDD-022-PM-ORCHESTRATION.md (superseded)
- **Architecture Decision**: temp/AGENT_REPORTS/pm-orchestration-backlog/ARCH_DECISION_HYBRID_LITE.md
- **Implementation Plan**: temp/AGENT_REPORTS/pm-orchestration-backlog/IMPLEMENTATION_PLAN.md
- **ADR Index**: docs/reference/ADR_INDEX.md
- **Workflow Stages**: docs/reference/WORKFLOW_STAGES.md
- **Related TDD**: TDD-023-HUB-KANBAN.md (Kanban component design)
