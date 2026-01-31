---
prd_number: PRD-019
epic: E19-Multi-Session-Orchestration
version: 0.7.0
status: draft
author: pm
created: 2026-01-31
last_updated: 2026-01-31
supersedes: PRD-014 (Playground 7: Workflow Hub section)
---

# PRD-019: Workflow Hub v0.7 - Multi-Session Orchestration Command Center

## Overview

### Vision Statement

The Workflow Hub evolves from a single-session resume tool to a **multi-session orchestration command center**. It enables a single human operator (Chris) to manage 2-6 parallel Claude Code sessions ("teams"), each working on different milestones across potentially multiple worktrees, with real-time visibility into progress, blockers, and context health.

**The Hub answers three critical questions:**

1. **Where are my teams?** - What is each session working on, in what workflow stage?
2. **Who is blocked?** - Which sessions need human intervention or decisions?
3. **How healthy is the system?** - Are context windows filling up? Are issues being addressed?

### Problem Statement

As the project scales from 1-2 concurrent sessions to 5-6, manual coordination becomes untenable:

1. **State Fragmentation**: Each session maintains its own context; no unified view exists
2. **Blocked Session Discovery**: A blocked session may sit idle until the human checks manually
3. **Context Window Blindness**: No visibility into token usage until compaction fails
4. **Backlog Drift**: GitHub issues exist but are not surfaced in the workflow tool
5. **Workflow Adherence**: No tracking of whether sessions follow the 5-stage workflow

### Goals

| Goal | Metric | Target |
|------|--------|--------|
| Session visibility | Time to understand all session status | <30 seconds |
| Blocker discovery | Time from blocked to human awareness | <5 minutes (with 10s polling) |
| Context health | Token budget visibility | Always visible, polling configurable |
| Backlog integration | GitHub issues visible in tool | 100% of P0/P1 issues displayed |
| Workflow tracking | Stage visibility per session | 5 stages shown per session |

### Research Items (Pre-Build)

Before building the Kanban board component, we must research existing solutions:

| Research Item | Purpose | Deliverable |
|---------------|---------|-------------|
| Kanban solutions (Jira, Plane, Linear, GitHub Projects) | Avoid reinventing | ADR with recommendation |
| Multi-team state architecture | Prevent file conflicts | ADR with state schema |
| Existing workflow tools | Learn patterns | Summary in research issue |

## User Stories

### MVP (Phase 1)

**US-1**: As a human operator, I want to see the token budget for each active session so that I know when to trigger context cleanup.

**US-2**: As a human operator, I want to see my GitHub issues backlog (P0/P1/P2) so that I can assign work to sessions.

**US-3**: As a human operator, I want the Hub to poll for updates every 10 seconds so that I see near-real-time status without manual refresh.

**US-4**: As a human operator, I want to see which workflow stage (UNDERSTAND/PLAN/BUILD/VERIFY/DEPLOY) each session is in so that I understand progress.

### Phase 2 (Kanban)

**US-5**: As a human operator, I want a Kanban board with lanes (Backlog, Grooming, Ready, In Progress, Blocked, Review, Done) so that I can track work visually.

**US-6**: As a human operator, I want cards to show title, issue #, assigned session/worktree, workflow stage, and context health so that I have full visibility at a glance.

**US-7**: As a human operator, I want to click a card to see expanded details including blocking reasons and dependency visualization.

### Phase 3 (Session Chat)

**US-8**: As a human operator, I want to click a card to open a chat interface for async feedback/clarification with the session working on that item.

### Phase 4 (State Architecture Refinement)

**US-9**: As a human operator managing 5-6 sessions, I want shared state that does not create file conflicts so that parallel teams can update status concurrently.

## Requirements

### Functional Requirements

#### FR-1: Token Budget Tracking (MVP - P0)

Display context window health for each session.

**Data Source**: `/usage` and `/context` CLI commands (manual refresh button for now)

**Display**:

```text
Session: feat/customer-analytics (worktree: dbt-playground--customer)
Context: [=======---] 72% (144K / 200K tokens)
Status: Healthy (under 80%)
```

**Thresholds**:

- Green: <60%
- Yellow: 60-80%
- Red: >80% (trigger cleanup workflow)

**Polling**: Configurable, default 5 minutes (separate from main 10s poll due to CLI cost)

**Acceptance Criteria**:

- [ ] Display token usage as percentage and absolute numbers
- [ ] Color-code by threshold
- [ ] Manual refresh button per session
- [ ] Configurable polling interval

#### FR-2: GitHub Issues Backlog (MVP - P0)

Display prioritized backlog from GitHub Issues.

**Data Source**: `gh issue list --json` with label filtering

**Labels**: P0 (Critical), P1 (High), P2 (Medium) - PM assigns labels

**Display**:

```text
BACKLOG (15 issues)

P0 - Critical
  #78 Workflow Hub token tracking [waiting-for-session]
  #79 Fix broken pagination [blocked:needs-design]

P1 - High
  #35 Add dbt_expectations tests
  #36 Singular tests for business rules

[Show P2...] (8 more)
```

**Limiting**: Show top N items (configurable, default 10) with "Show all" expansion

**Acceptance Criteria**:

- [ ] Fetch issues via `gh issue list`
- [ ] Group by priority label (P0/P1/P2)
- [ ] Show issue #, title, relevant labels
- [ ] Limit display with expansion option
- [ ] Link to GitHub issue on click

#### FR-3: Real-Time Polling (MVP - P0)

Poll for updates without manual refresh.

**Polling Interval**: Configurable, default 10 seconds

**Data Polled**:

- `temp/WORKFLOW_STATE.md` - session status
- `temp/SESSION_STATE/[session-id].md` - per-session state (new)
- `temp/AGENT_REPORTS/*/` - recent agent activity

**Display**:

- Last updated timestamp
- Polling status indicator (active/paused)
- Pause/resume toggle

**Acceptance Criteria**:

- [ ] Poll configured files on interval
- [ ] Display "Last updated: Xs ago"
- [ ] Pause/resume polling toggle
- [ ] Configurable interval (settings panel)

#### FR-4: Workflow Stage Tracking (MVP - P1)

Display 5-stage workflow progress per session.

**Stages**: UNDERSTAND -> PLAN -> BUILD -> VERIFY -> DEPLOY

**Data Source**: Parse from `SESSION_STATE/[session-id].md`

**Display**:

```text
Session: feat/customer-analytics
Stage: BUILD [===>----] 3/7 models
       UNDERSTAND  PLAN  BUILD  VERIFY  DEPLOY
          [x]      [x]    [*]    [ ]     [ ]
```

**Sub-task Granularity**: Show progress within BUILD (e.g., "model 3 of 7")

**Acceptance Criteria**:

- [ ] Display 5-stage pipeline per session
- [ ] Highlight current stage
- [ ] Show sub-task progress when available
- [ ] Link to stage documentation

#### FR-5: Blocked Session Detection (MVP - P1)

Surface blocked sessions prominently.

**Blocked Triggers** (from SESSION_STATE):

- `blocked: true` flag
- `blocking_reason: "..."` text
- Aggregated decisions needed
- Repeated failures (3+ of same error)
- Milestone completion awaiting review

**Display**:

```text
[!] BLOCKED SESSIONS (2)

feat/tuva-integration
  Reason: Needs schema decision - 3 options proposed
  Waiting since: 15 minutes
  [View Details] [Provide Input]

feat/security-review
  Reason: Approval needed for external API
  Waiting since: 2 hours
  [View Details] [Approve] [Reject]
```

**Acceptance Criteria**:

- [ ] Parse blocked status from session state
- [ ] Display blocking reason
- [ ] Show waiting duration
- [ ] Provide action buttons (view, provide input)

#### FR-6: Session Identity (MVP - P1)

Identify sessions by milestone/worktree, not human-assigned names.

**Naming Convention**: `{milestone-slug}` or `{worktree-name}`

**Examples**:

- `feat/customer-analytics` (branch-based)
- `v0.7-token-tracking` (milestone-based)
- `dbt-playground--tuva` (worktree directory)

**Display**: Show both milestone and worktree when applicable

**Acceptance Criteria**:

- [ ] Auto-derive session name from worktree or branch
- [ ] Display milestone association
- [ ] Support multiple issues per session (session works toward milestone)

#### FR-7: Dependency Visualization (MVP - P2)

Show blocked item dependencies.

**Display**: On blocked cards, show what they're waiting for

```text
#78 Token Tracking
  BLOCKED by: #75 Session State Schema (In Progress)
              #77 CLI Integration (Ready)
```

**Acceptance Criteria**:

- [ ] Parse dependency labels or issue references
- [ ] Display dependency chain on blocked items
- [ ] Link to dependent issues

### Hub Cleanup (MVP - P0)

Remove deprecated functionality from current Hub implementation.

**Remove**:

- "Parse State" button (will auto-poll)
- "Load from Server" button (replaced by file polling)
- "Load Sample" buttons (no longer needed with real data)
- Broken "Session Summary" tab

**Add**:

- "Return to Hub" button in other playground apps
- Consistent navigation header across playgrounds

**Acceptance Criteria**:

- [ ] Remove deprecated buttons
- [ ] Add return navigation to Worktree Coordinator, Mermaid Designer
- [ ] Implement unified navigation header

### Non-Functional Requirements

**NFR-1**: Hub loads in <2 seconds

**NFR-2**: Polling does not block UI (async updates)

**NFR-3**: Works offline with cached data (LocalStorage)

**NFR-4**: Single-file HTML implementation (consistent with v0.6)

**NFR-5**: Dark/light mode support

**NFR-6**: Keyboard navigation for power users

## Scope

### In Scope (MVP - Phase 1)

- Token budget display with manual refresh
- GitHub issues backlog (P0/P1/P2)
- 10-second polling for workflow state
- 5-stage workflow visualization
- Blocked session detection
- Session identity by milestone/worktree
- Hub cleanup (remove deprecated features)
- "Return to Hub" navigation in other playgrounds

### In Scope (Phase 2 - Kanban)

- Kanban board with 7 lanes
- Card details (title, issue #, session, stage, health)
- Click-to-expand for full details
- Dependency visualization on blocked items
- Research: Evaluate Jira/Plane/GitHub Projects integration

### In Scope (Phase 3 - Session Chat)

- Click card to open chat interface
- Async feedback/clarification capability
- Session notification of new messages

### In Scope (Phase 4 - State Architecture)

- Multi-team state architecture (prevent file conflicts)
- Per-session state files
- Centralized workflow definition
- ADR for state management patterns

### Out of Scope

- Multi-repo support (future research)
- Multi-user access (single-user tool)
- Keyboard shortcuts to start Hub (use command-line or Supervisor)
- Push notifications (polling only for MVP)
- Automated context compaction (manual trigger, documented workflow)

## Dependencies

| Dependency | Description | Status |
|------------|-------------|--------|
| `temp/WORKFLOW_STATE.md` | Current workflow tracking | Exists |
| `temp/SESSION_STATE/` | Per-session state files | NEW - needs creation |
| `gh` CLI | GitHub issues access | Available |
| `/usage` command | Token budget data | Available (manual) |

### New Artifacts Required

#### SESSION_STATE Directory Structure

```text
temp/SESSION_STATE/
  feat--customer-analytics.md    # Session working on customer analytics
  feat--tuva-integration.md      # Session working on Tuva
  main.md                        # Main repo session (if any)
```

#### SESSION_STATE File Format

```yaml
---
session_id: feat--customer-analytics
worktree: /Users/chris/dbt-playground--customer-analytics
branch: feat/customer-analytics
milestone: v0.7-hub-enhancements
stage: BUILD
stage_progress: "3/7 models complete"
blocked: false
blocking_reason: null
last_updated: 2026-01-31T14:30:00
context_usage: 72%
issues_assigned:
  - 35
  - 36
recent_activity:
  - "14:30 - Completed stg_customers model"
  - "14:15 - Started BUILD phase"
---

## Current Focus

Building customer analytics models.

## Decisions Pending

None.

## Recent Completions

- stg_customers
- stg_orders
- int_customer_orders

## Next Actions

- Build fct_customer_orders
- Add tests
```

## Architecture

### Multi-Team State Management

**Challenge**: Multiple sessions updating state concurrently could cause conflicts.

**Proposed Solution**:

1. **Per-Session Files**: Each session writes to its own file in `temp/SESSION_STATE/`
2. **Aggregator**: Hub reads all session files and aggregates view
3. **No Central Lock**: Sessions are independent; Hub is read-only
4. **Conflict Resolution**: Last-write-wins for display (acceptable for polling)

**Alternative Considered**: Single WORKFLOW_STATE.md with sections

- Rejected due to merge conflict risk with multiple writers

**ADR Needed**: Architecture Decision Record for state management patterns

### Data Flow

```text
+-------------------+     +------------------+     +-------------+
| SESSION 1         |     | SESSION 2        |     | SESSION N   |
| (Claude Code)     |     | (Claude Code)    |     | (...)       |
+--------+----------+     +--------+---------+     +------+------+
         |                         |                      |
         v                         v                      v
+--------+----------+     +--------+---------+     +------+------+
| SESSION_STATE/    |     | SESSION_STATE/   |     | SESSION_    |
| session-1.md      |     | session-2.md     |     | STATE/...   |
+--------+----------+     +--------+---------+     +------+------+
         |                         |                      |
         +------------+------------+----------------------+
                      |
                      v
              +-------+--------+
              | WORKFLOW HUB   |
              | (Browser)      |
              | - Polls files  |
              | - Aggregates   |
              | - Displays     |
              +----------------+
```

### Polling Architecture

```text
Hub Browser
    |
    +-- Main Poll (10s) ---> temp/WORKFLOW_STATE.md
    |                        temp/SESSION_STATE/*.md
    |                        temp/AGENT_REPORTS/*/
    |
    +-- Issues Poll (60s) --> gh issue list --json (via server or cache)
    |
    +-- Context Poll (5m) --> Manual refresh button (no auto-poll)
```

## Implementation Phases

### Phase 1: MVP (Target: v0.7.0)

**Priority**: Get visibility working for 2-3 sessions

| Task | Complexity | Priority | Dependencies |
|------|------------|----------|--------------|
| Create SESSION_STATE directory structure | Low | P0 | None |
| Update agents to write SESSION_STATE | Medium | P0 | Directory structure |
| Token budget display (manual refresh) | Low | P0 | None |
| GitHub issues backlog display | Medium | P0 | gh CLI |
| 10-second polling implementation | Medium | P0 | SESSION_STATE files |
| 5-stage workflow visualization | Low | P1 | SESSION_STATE format |
| Blocked session detection | Medium | P1 | SESSION_STATE format |
| Hub cleanup (remove deprecated) | Low | P0 | None |
| "Return to Hub" in other playgrounds | Low | P0 | None |

**Deliverables**:

- Updated `playgrounds/workflow-hub.html`
- `temp/SESSION_STATE/` directory with schema
- Agent updates for SESSION_STATE writing
- Documentation updates

### Phase 2: Kanban Board (Target: v0.7.1)

**Priority**: Visual work management

**Pre-Requisite**: Complete research on existing Kanban solutions

| Task | Complexity | Priority | Dependencies |
|------|------------|----------|--------------|
| Research existing Kanban tools | Medium | P0 | None |
| ADR: Build vs. Integrate decision | Low | P0 | Research |
| Kanban lane implementation | High | P1 | ADR |
| Card component with details | Medium | P1 | Lane implementation |
| Dependency visualization | Medium | P2 | Card component |

**Research Questions**:

- Can GitHub Projects serve our Kanban needs?
- Would Plane or Linear be better fits?
- What would integration look like vs. building custom?

### Phase 3: Session Chat (Target: v0.7.2)

**Priority**: Enable async human-agent communication

| Task | Complexity | Priority | Dependencies |
|------|------------|----------|--------------|
| Chat UI component | Medium | P1 | Kanban cards |
| Message queue mechanism | High | P1 | None |
| Session notification system | High | P2 | Message queue |

**Technical Challenge**: How do Claude sessions receive messages?

- Option A: Poll temp/CHAT/ directory
- Option B: MCP integration
- Option C: GitHub issue comments

### Phase 4: State Architecture Refinement (Target: v0.7.3+)

**Priority**: Scale to 5-6 sessions without issues

| Task | Complexity | Priority | Dependencies |
|------|------------|----------|--------------|
| ADR: Multi-team state architecture | Medium | P0 | Phase 1 learnings |
| Centralized workflow definition | Medium | P1 | ADR |
| Workflow adherence tracking | Medium | P2 | Centralized definition |
| Out-of-order stage detection | Low | P2 | Workflow tracking |

## Success Metrics

| Phase | Metric | Target | Measurement |
|-------|--------|--------|-------------|
| MVP | Session status visibility | <30s to understand all | Observation |
| MVP | Blocked session awareness | <5 min discovery | Timestamp logging |
| MVP | Token budget visibility | Always visible | UI verification |
| Phase 2 | Backlog management | 100% P0/P1 visible | GitHub sync check |
| Phase 3 | Async communication | Messages delivered | End-to-end test |
| Phase 4 | Concurrent sessions | 5-6 without conflict | Stress test |

## Open Questions

1. **Context polling cost**: Is `/usage` command too expensive to poll? May need to stay manual.
   - **Recommendation**: Manual refresh for MVP, evaluate automation later

2. **GitHub API rate limits**: How often can we poll issues?
   - **Recommendation**: 60-second poll for issues, cache aggressively

3. **Session notification**: How does a Claude session know it has a message?
   - **Deferred**: Phase 3 research item

4. **Workflow definition location**: Currently implicit in CLAUDE.md - should we centralize?
   - **Recommendation**: Create explicit `docs/reference/WORKFLOW_STAGES.md`

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| State file conflicts | High | Low | Per-session files, not shared |
| Polling performance | Medium | Medium | Configurable intervals, pause option |
| Kanban scope creep | High | High | Research first, strict MVP scope |
| Session identity confusion | Medium | Medium | Clear naming convention docs |
| Context polling cost | Medium | Medium | Manual refresh for MVP |

## Related Documents

- **Supersedes**: PRD-014 Playground 7 (Workflow Hub) section
- **Depends On**: PRD-016 (Agent Context Management) - SESSION_STATE builds on this
- **GitHub Issues**: TBD (to be created per phase)
- **ADRs Needed**:
  - ADR: Multi-team state architecture
  - ADR: Kanban build vs. integrate

## Next Steps

1. [ ] Create GitHub issue for Phase 1 MVP
2. [ ] Create GitHub issue for Kanban research
3. [ ] Create ADR template for state architecture decision
4. [ ] Update WORKFLOW_STATE.md to reflect new SESSION_STATE pattern
5. [ ] Draft `docs/reference/WORKFLOW_STAGES.md` for centralized workflow definition

---

*PRD Status: Draft - Ready for Review*
*Author: Product Manager*
*Date: 2026-01-31*
