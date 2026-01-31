---
title: Workflow Hub v0.7 MVP - Multi-Session Orchestration Command Center
prd_number: PRD-019
epic: E19-Multi-Session-Orchestration
epic_issue: 85
version: 0.7.0
status: approved
author: pm
created: 2026-01-31
last_updated: 2026-01-31
supersedes: PRD-014 (Playground 7: Workflow Hub section)
---

# PRD-019: Workflow Hub v0.7 MVP

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

### MVP Goals

| Goal | Metric | Target |
|------|--------|--------|
| Session visibility | Time to understand all session status | <30 seconds |
| Blocker discovery | Time from blocked to human awareness | <5 minutes (with 10s polling) |
| Context health | Token budget visibility | Always visible |
| Backlog integration | GitHub issues visible in tool | 100% of P0/P1 issues displayed |

---

## User Stories (MVP)

### US-1: Token Budget Visibility (P0)

**As a** human operator managing multiple Claude Code sessions,
**I want to** see the token budget for each active session,
**So that** I know when to trigger context cleanup before a session fails.

**Acceptance Criteria:**

- [ ] Display token usage as percentage and absolute numbers (e.g., "72% - 144K / 200K")
- [ ] Color-code by threshold: Green (<60%), Yellow (60-80%), Red (>80%)
- [ ] Manual refresh button per session
- [ ] Configurable warning threshold (default: 80%)

### US-2: GitHub Issues Backlog (P0)

**As a** human operator,
**I want to** see my GitHub issues backlog grouped by priority (P0/P1/P2),
**So that** I can assign work to sessions without switching to GitHub.

**Acceptance Criteria:**

- [ ] Fetch issues via `gh issue list --json`
- [ ] Group by priority label (P0 Critical, P1 High, P2 Medium)
- [ ] Show issue #, title, and relevant labels
- [ ] Limit display to top 10 items with "Show all" expansion
- [ ] Click issue to open in GitHub

### US-3: Real-Time Polling (P0)

**As a** human operator,
**I want to** the Hub to poll for updates every 10 seconds,
**So that** I see near-real-time status without manual refresh.

**Acceptance Criteria:**

- [ ] Poll `temp/SESSION_STATE/*.md` files on 10-second interval
- [ ] Display "Last updated: Xs ago" timestamp
- [ ] Pause/resume polling toggle button
- [ ] Configurable polling interval in settings (5-60 seconds)

### US-4: Workflow Stage Tracking (P0)

**As a** human operator,
**I want to** see which workflow stage (UNDERSTAND/PLAN/BUILD/VERIFY/DEPLOY) each session is in,
**So that** I understand progress at a glance.

**Acceptance Criteria:**

- [ ] Display 5-stage pipeline per session with visual indicator
- [ ] Highlight current stage with distinct styling
- [ ] Show sub-task progress when available (e.g., "model 3 of 7")
- [ ] Completed stages show checkmark

### US-5: Blocked Session Detection (P0)

**As a** human operator,
**I want to** blocked sessions displayed prominently with their blocking reason,
**So that** I can quickly unblock them.

**Acceptance Criteria:**

- [ ] Parse `blocked: true` flag from SESSION_STATE files
- [ ] Display blocking reason prominently
- [ ] Show time waiting (e.g., "Blocked for 15 minutes")
- [ ] Blocked sessions appear in dedicated "BLOCKED" section at top
- [ ] Action buttons: [View Details]

### US-6: Hub UI Cleanup (P0)

**As a** user of the Workflow Hub,
**I want to** a clean interface without deprecated features,
**So that** I'm not confused by non-functional buttons.

**Acceptance Criteria:**

- [ ] Remove "Parse State" button (replaced by auto-poll)
- [ ] Remove "Load from Server" button (replaced by file polling)
- [ ] Remove "Load Sample" buttons
- [ ] Remove broken "Session Summary" tab
- [ ] Add "Return to Hub" button in Worktree Coordinator
- [ ] Add "Return to Hub" button in Mermaid Designer

---

## Technical Requirements

### FR-1: Token Budget Display

**Data Source**: Manual input via refresh button (MVP). Future: `/usage` CLI command.

**Display Format:**

```text
Session: feat/customer-analytics
Context: [=======---] 72% (144K / 200K tokens)
Status: Healthy (under 80%)
```

**Thresholds:**

| Level | Range | Color | Action |
|-------|-------|-------|--------|
| Healthy | <60% | Green | None |
| Warning | 60-80% | Yellow | Monitor |
| Critical | >80% | Red | Trigger cleanup |

### FR-2: GitHub Issues Backlog

**Data Source**: `gh issue list --json number,title,labels,state --state open`

**Display Format:**

```text
BACKLOG (15 issues)

P0 - Critical (2)
  #78 Workflow Hub token tracking
  #79 Fix broken pagination

P1 - High (5)
  #35 Add dbt_expectations tests
  #36 Singular tests for business rules
  ...

[Show P2...] (8 more)
```

**Polling**: Every 60 seconds (separate from main 10s poll due to API cost).

### FR-3: SESSION_STATE File Format

Sessions write their state to `temp/SESSION_STATE/{session-id}.md`:

```yaml
---
session_id: feat--customer-analytics
worktree: /Users/chris/dbt-playground--customer-analytics
branch: feat/customer-analytics
stage: BUILD
stage_progress: "3/7 models complete"
blocked: false
blocking_reason: null
last_updated: 2026-01-31T14:30:00
context_usage: 72
issues_assigned:
  - 35
  - 36
---

## Current Focus

Building customer analytics models.

## Decisions Pending

None.
```

### FR-4: Polling Architecture

```text
Hub Browser
    |
    +-- Main Poll (10s) ---> temp/SESSION_STATE/*.md
    |
    +-- Issues Poll (60s) --> gh issue list (cached)
    |
    +-- Context Poll -------> Manual refresh button only (MVP)
```

---

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Hub loads in | <2 seconds |
| NFR-2 | Polling does not block UI | Async updates |
| NFR-3 | Works offline with cached data | LocalStorage |
| NFR-4 | Single-file HTML implementation | Consistent with v0.6 |
| NFR-5 | Dark/light mode support | Theme toggle |

---

## MVP Scope

### In Scope

- Token budget display with manual refresh
- GitHub issues backlog (P0/P1/P2)
- 10-second polling for workflow state
- 5-stage workflow visualization
- Blocked session detection
- Session identity by worktree/branch
- Hub cleanup (remove deprecated features)
- "Return to Hub" navigation in other playgrounds

### Out of Scope (Future Phases)

| Item | Phase | Issue |
|------|-------|-------|
| Kanban board with lanes | Phase 2 (v0.7.1) | #86 |
| Click-to-expand card details | Phase 2 | #86 |
| Dependency visualization | Phase 2 | - |
| Session chat/feedback | Phase 3 (v0.7.2) | TBD |
| Auto context compaction | Phase 4 | TBD |
| Multi-team state architecture ADR | Phase 4 | TBD |

---

## Dependencies

| Dependency | Description | Status |
|------------|-------------|--------|
| `temp/SESSION_STATE/` | Per-session state files | NEW - needs creation |
| `gh` CLI | GitHub issues access | Available |
| Workflow Hub v0.6 | Existing HTML implementation | Available |

---

## Implementation Tasks

| # | Task | Complexity | Priority |
|---|------|------------|----------|
| 1 | Create `temp/SESSION_STATE/` directory structure | Low | P0 |
| 2 | Define SESSION_STATE file schema | Low | P0 |
| 3 | Hub cleanup: remove deprecated buttons | Low | P0 |
| 4 | Add "Return to Hub" to other playgrounds | Low | P0 |
| 5 | Token budget display component | Medium | P0 |
| 6 | GitHub issues backlog component | Medium | P0 |
| 7 | 10-second polling implementation | Medium | P0 |
| 8 | 5-stage workflow visualization | Low | P0 |
| 9 | Blocked session detection UI | Medium | P0 |
| 10 | Update agents to write SESSION_STATE | Medium | P0 |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Session status visibility | <30s to understand all | Observation |
| Blocked session awareness | <5 min discovery | Timestamp logging |
| Token budget visibility | Always visible | UI verification |
| Backlog integration | 100% P0/P1 visible | GitHub sync check |

---

## Open Questions for Architect

1. **Session state writing**: Should agents write SESSION_STATE automatically, or via explicit command?
2. **Polling file access**: Can browser JavaScript read local files, or do we need a tiny server?
3. **State conflicts**: If two sessions share a worktree (rare), how to handle?
4. **Token API**: Best way to get `/usage` data into Hub?

---

## Related Documents

- **Epic Issue**: #85 (GitHub)
- **Research Issue**: #86 (Kanban evaluation)
- **Supersedes**: PRD-014 Playground 7 (Workflow Hub section)
- **Foundation**: PRD-016 (Agent Context Management)

---

*PRD Status: Approved for MVP Development*
*Author: Product Manager*
*Date: 2026-01-31*
