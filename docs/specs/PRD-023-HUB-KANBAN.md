# PRD-023: Workflow Hub Kanban Board

## Overview

**Author**: Product Manager (Claude Code Agent System)
**Status**: Draft
**Created**: 2026-01-31
**Updated**: 2026-01-31
**Version**: v0.7.2
**Epic**: E19-Multi-Session-Orchestration
**GitHub Issue**: #110

### Problem Statement

The Workflow Hub v0.7.0 provides session visibility but lacks a visual task management interface. Users must switch to GitHub to see their issue backlog, understand priorities, and track work through PM stages. There's no way to:

1. **Visualize workflow stages**: See issues move through Backlog → Grooming → Ready → In Progress → Review → Done
2. **Identify blocked work**: Quickly spot blocked items and their reasons
3. **Launch sessions contextually**: Start Claude Code sessions directly from blocked/ready issues
4. **Track subtask progress**: See session task completion within each issue

### Goal

Implement a 7-lane Kanban board within the Workflow Hub that displays GitHub issues as draggable cards with:

- Visual PM workflow stages (lanes)
- 5-stage development phase indicators (on cards)
- Session integration with `--from-pr` launch capability
- Context health visibility for active sessions
- Smart archiving for completed items

**Success Outcome**: Users can manage their entire issue workflow from a single interface, launching Claude sessions directly from the board.

---

## User Stories

### Core Board Experience

**US-1: GitHub Issues as Cards**
As a project manager, I want GitHub issues displayed as Kanban cards so that I have a single source of truth for work items.

**US-2: Seven-Lane Workflow Board**
As a workflow participant, I want a 7-lane Kanban board (Backlog, Grooming, Ready, In Progress, In Review, Blocked, Done) so that I can see where each issue is in the PM process.

**US-3: Drag-and-Drop Movement**
As a board user, I want to drag cards between lanes so that I can update issue status quickly.

### Card Information

**US-4: Workflow Phase Indicator**
As a human operator, I want each card to show its current development phase (UNDERSTAND/PLAN/BUILD/VERIFY/DEPLOY) so that I understand progress within each lane.

**US-5: Priority and Type Icons**
As a user scanning the board, I want priority (P0/P1/P2) and type (bug/feature) shown as Jira-style icons so that I can quickly identify critical items.

**US-6: Mini-Timeline Progress**
As a board viewer, I want a compact progress indicator on each card showing subtask completion so that I can see progress at a glance.

**US-7: GitHub Labels as Tags**
As a board user, I want to see 2-3 relevant GitHub labels on each card so that I understand the issue's domain.

### Session Integration

**US-8: Start Session Button**
As a human operator, I want a button to launch a Claude Code session for blocked/ready cards so that I can quickly unblock work or start development.

**US-9: Context Health Display**
As a human operator, I want context health (token usage) prominently shown on cards when yellow/orange/red so that I know when sessions need cleanup.

**US-10: Expanded Card View**
As a user investigating an issue, I want to click a card and see full details including checklist, session log, and blocking reasons so that I understand the full context.

### Board Management

**US-11: Smart Done Archiving**
As a board user, I want the Done lane to auto-manage old cards (card limit with fade) so that the board stays clean while showing recent progress.

---

## Requirements

### Functional Requirements

#### FR-1: Board Layout

**Seven Lanes**:

| Lane | Purpose | Color Accent |
|------|---------|--------------|
| Backlog | Ungroomed issues | Gray |
| Grooming | Being refined | Blue |
| Ready | Ready for dev | Green |
| In Progress | Actively worked | Cyan |
| In Review | PR submitted | Purple |
| Blocked | Waiting on blocker | Red |
| Done | Completed | Dark Gray |

**Acceptance Criteria**:

- [ ] Horizontal scroll for all 7 lanes
- [ ] Lane headers show card count
- [ ] CSS Grid layout with 320px column width
- [ ] Responsive: Desktop shows all, tablet shows 4-5 + scroll

#### FR-2: Card Design

**Card Structure**:

```text
┌─────────────────────────────────┐
│ [Type] #94          [P1] [🔴]  │ ← Issue #, Priority, Health (if warn)
│ Add customer analytics tracking │ ← Title (2 lines max)
├─────────────────────────────────┤
│ ○○○●●●● 4/7         [BUILD]    │ ← Progress dots + Phase badge
│ [feat] [analytics]             │ ← Labels (2-3 max)
└─────────────────────────────────┘
```

**Acceptance Criteria**:

- [ ] Type icon: Bug (🐛), Feature (⭐), Docs (📝), Chore (🔧)
- [ ] Priority icon: P0 (🔥), P1 (🔴), P2 (🟡), P3 (⚪)
- [ ] Phase badge showing current workflow stage
- [ ] Progress as dots or "N/M" format
- [ ] 2-3 labels maximum displayed

#### FR-3: Drag-and-Drop

**Native HTML5 Drag-and-Drop**:

- [ ] Cards draggable between lanes
- [ ] Visual feedback: opacity change, cursor:grabbing
- [ ] Drop zone highlight on dragover
- [ ] Fallback: "Move to..." dropdown menu for accessibility

**Persistence**:

- [ ] Lane state saved to localStorage on drop
- [ ] Board state reloads on page refresh

#### FR-4: Expanded Card Modal

**Triggered by**: Card click

**Modal Contents**:

- [ ] Full issue title and description
- [ ] Subtask checklist with progress bar
- [ ] Session log snippet (last 3-5 entries)
- [ ] Blocking reason (if blocked)
- [ ] Time waiting indicator (e.g., "Blocked 2 days")
- [ ] Linked PR status
- [ ] "Start Session" button

#### FR-5: Session Launch

**Start Session Button**:

- [ ] Visible on Blocked and Ready cards
- [ ] Visible in expanded card modal
- [ ] Generates command: `claude --from-pr <PR#>`
- [ ] Copies command to clipboard
- [ ] Options dropdown for context level:
  - Full PR history (default)
  - Agent reports only
  - Issue description + blocker

#### FR-6: Context Health Indicator

**Display Rules**:

| Health Level | Visibility | Style |
|--------------|------------|-------|
| Green (<60%) | Hover/expand only | Subtle |
| Yellow (60-80%) | Always visible | Yellow dot |
| Orange (80-90%) | Always visible | Orange dot |
| Red (>90%) | Always visible | Red dot, pulse |

**Acceptance Criteria**:

- [ ] Health indicator positioned in card header
- [ ] Only shown for cards with active sessions
- [ ] Tooltip shows "72% (144K / 200K tokens)"

#### FR-7: Done Lane Management

**Smart Archiving**:

- [ ] Show last 10 completed cards by default
- [ ] Older cards fade with reduced opacity
- [ ] "Show N more" link for archived items
- [ ] Click any Done card to expand details

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Single-file HTML implementation | Consistent with playgrounds |
| NFR-2 | localStorage persistence | Offline-capable |
| NFR-3 | No external dependencies | Vanilla JS/CSS only |
| NFR-4 | Page load time | <2 seconds |
| NFR-5 | Drag-drop latency | <100ms visual feedback |
| NFR-6 | Accessible keyboard navigation | Tab + Enter fallback |

---

## Technical Design

### Data Model

```javascript
const boardState = {
  version: 1,
  lastUpdated: "2026-01-31T12:00:00Z",
  columns: {
    backlog: ["card-35", "card-36"],
    grooming: [],
    ready: ["card-94"],
    "in-progress": ["card-110"],
    "in-review": [],
    blocked: ["card-86"],
    done: ["card-92", "card-93"]
  },
  cards: {
    "card-94": {
      id: 94,
      title: "Add customer analytics tracking",
      type: "enhancement",
      priority: "P1",
      labels: ["feat", "analytics"],
      phase: "BUILD",
      subtasksDone: 4,
      subtasksTotal: 7,
      assignee: "Chris",
      sessionId: null,
      contextHealth: null,
      blockedReason: null,
      blockedSince: null,
      completedAt: null
    }
  },
  settings: {
    doneCardLimit: 10,
    autoArchiveDays: 7
  }
};
```

### Architecture

```text
┌──────────────────────────────────────────────────┐
│                 Workflow Hub                      │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │ Sessions   │ │ Kanban     │ │ Issues     │   │
│  │ Panel      │ │ Board      │ │ Backlog    │   │
│  └────────────┘ └────────────┘ └────────────┘   │
│         │              │              │          │
│         └──────────────┴──────────────┘          │
│                        │                         │
│              ┌─────────▼─────────┐               │
│              │    localStorage    │               │
│              │   (board-state)   │               │
│              └───────────────────┘               │
│                        │                         │
│              ┌─────────▼─────────┐               │
│              │    gh CLI sync    │               │
│              │  (on page load)   │               │
│              └───────────────────┘               │
└──────────────────────────────────────────────────┘
```

### Integration Points

1. **GitHub Issues**: `gh issue list --json` on page load
2. **SESSION_STATE Files**: Poll for session-linked cards
3. **Future (v0.9)**: Backlog.md via MCP for task management

---

## Scope

### In Scope (v0.7.2)

- 7-lane Kanban board with horizontal scroll
- Card design with type/priority icons and phase badges
- Native HTML5 drag-and-drop
- localStorage persistence
- Expanded card modal with details
- "Start Session" button with clipboard copy
- Context health indicators
- Smart Done lane with card limits

### Out of Scope (Future)

| Item | Target Version | Notes |
|------|---------------|-------|
| Backlog.md integration | v0.9 | PRD-022 defines MCP approach |
| SQLite state database | v0.9 | Real-time cross-session state |
| Session chat/feedback | v0.7.3 | #111 |
| GitHub issue sync (write) | v0.8+ | Currently read-only |
| WIP limits per lane | v0.8+ | Future enhancement |
| Swimlanes (grouped rows) | v0.8+ | Priority or assignee grouping |

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Workflow Hub v0.7.0 | Foundation | Complete |
| `gh` CLI | GitHub data | Available |
| SESSION_STATE format | Session data | Defined in PRD-019 |
| localStorage API | Browser | Built-in |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Board load time | <2 seconds | Page load performance |
| Drag-drop latency | <100ms | Visual feedback timing |
| Session launch time | <5 seconds | Click to command copied |
| Issues visible | 100% of open issues | Sync verification |
| Blocked visibility | 100% | All blocked items in Blocked lane |

---

## Implementation Tasks

### Phase 1: Board Foundation (MVP)

| # | Task | Complexity | Priority |
|---|------|------------|----------|
| 1 | Create 7-lane CSS Grid layout | Medium | P0 |
| 2 | Implement card component with icons | Medium | P0 |
| 3 | Add native HTML5 drag-and-drop | Medium | P0 |
| 4 | Implement localStorage persistence | Low | P0 |
| 5 | Add GitHub issue sync on load | Medium | P0 |

### Phase 2: Card Details

| # | Task | Complexity | Priority |
|---|------|------------|----------|
| 6 | Implement expanded card modal | Medium | P0 |
| 7 | Add phase badge component | Low | P0 |
| 8 | Add progress indicator (dots) | Low | P1 |
| 9 | Add context health indicator | Low | P1 |

### Phase 3: Session Integration

| # | Task | Complexity | Priority |
|---|------|------------|----------|
| 10 | Add "Start Session" button | Low | P0 |
| 11 | Implement clipboard copy for command | Low | P0 |
| 12 | Add context options dropdown | Medium | P1 |
| 13 | Link SESSION_STATE to cards | Medium | P1 |

### Phase 4: Polish

| # | Task | Complexity | Priority |
|---|------|------------|----------|
| 14 | Implement Done lane archiving | Low | P1 |
| 15 | Add keyboard navigation fallback | Medium | P2 |
| 16 | Responsive tablet/mobile layout | Medium | P2 |
| 17 | Add "Move to" dropdown menu | Low | P2 |

---

## Open Questions

| # | Question | Status | Decision |
|---|----------|--------|----------|
| 1 | Should we update GitHub labels on lane change? | Deferred | Read-only for v0.7.2; write in v0.8+ |
| 2 | How to handle multi-repo boards? | Deferred | Single repo for v0.7.2 |
| 3 | Should Done cards link to PRs? | Resolved | Yes, show PR link if available |

---

## Related Documents

- **Research Report**: `temp/AGENT_REPORTS/hub-kanban-v072/RESEARCH_REPORT.md`
- **User Stories**: `temp/AGENT_REPORTS/hub-kanban-v072/PM_USER_STORIES.md`
- **Parent PRD**: PRD-019 (Workflow Hub v0.7 MVP)
- **Future Architecture**: PRD-022 (PM Orchestration - v0.9)
- **Implementation Issue**: [#110](https://github.com/cmbays/dbt-playground/issues/110)
- **Research Issue**: [#86](https://github.com/cmbays/dbt-playground/issues/86) (superseded)

---

*PRD Status: Draft - Ready for Review*
*Author: Product Manager*
*Date: 2026-01-31*
