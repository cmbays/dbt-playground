# TDD-023: Workflow Hub Kanban Board

## Overview

**Source PRD**: PRD-023-HUB-KANBAN
**Author**: Technical Architect
**Status**: Draft
**Created**: 2026-01-31
**Updated**: 2026-01-31

### Summary

This document provides the technical design for the Kanban board component within the Workflow Hub. The implementation uses native HTML5 drag-and-drop, CSS Grid for layout, and localStorage for persistence - maintaining the single-file HTML architecture established by existing playgrounds.

### Design Goals

1. **Single-file integration**: Extend workflow-hub.html, not a new file
2. **Native APIs only**: HTML5 drag-and-drop, no external libraries
3. **Consistent patterns**: Follow existing Hub CSS variables and utilities
4. **Offline-first**: localStorage with GitHub sync on load
5. **Accessible**: Keyboard navigation fallback for drag-and-drop

---

## Architecture Decisions

### ADR-12: Native HTML5 Drag-and-Drop

**Status**: Approved

**Context**: The Kanban board requires drag-and-drop functionality to move cards between lanes. Options include external libraries (SortableJS, dnd-kit) or native HTML5 Drag and Drop API.

**Decision**: Use native HTML5 Drag and Drop API.

**Rationale**:

| Criterion | Native API | SortableJS | dnd-kit |
|-----------|------------|------------|---------|
| Bundle Size | 0 KB | 14 KB | 30+ KB |
| Single-file HTML | Yes | CDN required | Not viable |
| Browser Support | All modern | All modern | All modern |
| Touch Support | Limited | Excellent | Excellent |
| Learning Curve | Low | Low | Medium |

**Consequences**:

- **Positive**: Zero dependencies, consistent with playground architecture, full control
- **Negative**: Touch support requires fallback menu, more manual code
- **Mitigation**: Implement "Move to..." dropdown as touch/accessibility fallback

**Approval**: Architect

---

### ADR-13: localStorage Board State Schema

**Status**: Approved

**Context**: Board state (column assignments, card positions) must persist across page reloads. Options: localStorage, IndexedDB, or server-side.

**Decision**: Use localStorage with versioned JSON schema.

**Rationale**:

| Criterion | localStorage | IndexedDB | Server |
|-----------|--------------|-----------|--------|
| Complexity | Low | Medium | High |
| Sync Speed | Instant | Instant | Network |
| Size Limit | 5-10 MB | Unlimited | Unlimited |
| Offline | Yes | Yes | No |
| Cross-device | No | No | Yes |

**Consequences**:

- **Positive**: Simple, instant, offline-capable
- **Negative**: No cross-device sync
- **Mitigation**: v0.9 adds SQLite/Backlog.md for cross-session sync (PRD-022)

**Approval**: Architect

---

## Architecture Overview

### Component Integration

The Kanban board integrates as a new tab/view within the existing Workflow Hub:

```text
┌──────────────────────────────────────────────────────────────┐
│                      Workflow Hub Header                      │
│  [Sessions] [Kanban] [Issues]                    [Settings]  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ...    │
│  │ Backlog  │ │ Grooming │ │  Ready   │ │In Progress│        │
│  │   (5)    │ │   (2)    │ │   (3)    │ │   (1)    │        │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤        │
│  │ ┌──────┐ │ │ ┌──────┐ │ │ ┌──────┐ │ │ ┌──────┐ │        │
│  │ │Card 1│ │ │ │Card 3│ │ │ │Card 5│ │ │ │Card 8│ │        │
│  │ └──────┘ │ │ └──────┘ │ │ └──────┘ │ │ └──────┘ │        │
│  │ ┌──────┐ │ │ ┌──────┐ │ │ ┌──────┐ │ │          │        │
│  │ │Card 2│ │ │ │Card 4│ │ │ │Card 6│ │ │          │        │
│  │ └──────┘ │ │ └──────┘ │ │ └──────┘ │ │          │        │
│  │   ...    │ │          │ │ ┌──────┐ │ │          │        │
│  │          │ │          │ │ │Card 7│ │ │          │        │
│  │          │ │          │ │ └──────┘ │ │          │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│                     ← Horizontal Scroll →                    │
├──────────────────────────────────────────────────────────────┤
│                      Status Bar / Footer                     │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

```text
                    ┌─────────────────┐
                    │   Page Load     │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │   localStorage  │           │   gh issue list │
    │  (board-state)  │           │    (async)      │
    └────────┬────────┘           └────────┬────────┘
             │                             │
             ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │ Restore column  │           │ Merge new issues│
    │  positions      │           │ into cards      │
    └────────┬────────┘           └────────┬────────┘
             │                             │
             └──────────────┬──────────────┘
                            ▼
                  ┌─────────────────┐
                  │   Render Board  │
                  └────────┬────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │ Drag/Drop  │   │ Card Click │   │ Start Sess │
   │   Event    │   │   Event    │   │   Button   │
   └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
         │                │                │
         ▼                ▼                ▼
   ┌────────────┐   ┌────────────┐   ┌────────────┐
   │ Update     │   │ Show Modal │   │ Copy cmd   │
   │ localStorage│   │            │   │ to clipboard│
   └────────────┘   └────────────┘   └────────────┘
```

---

## Implementation Details

### Data Structures

#### Board State Schema (localStorage)

```javascript
// Key: 'workflow-hub-kanban'
const boardState = {
  version: 1,
  lastUpdated: "2026-01-31T12:00:00Z",
  lastGitHubSync: "2026-01-31T12:00:00Z",

  // Column order and card assignments
  columns: {
    "backlog": ["card-35", "card-36", "card-40"],
    "grooming": ["card-78"],
    "ready": ["card-94", "card-95"],
    "in-progress": ["card-110"],
    "in-review": [],
    "blocked": ["card-86"],
    "done": ["card-92", "card-93", "card-91"]
  },

  // Card data keyed by id
  cards: {
    "card-94": {
      issueNumber: 94,
      title: "Add customer analytics tracking",
      type: "enhancement",       // bug | enhancement | docs | chore
      priority: "P1",            // P0 | P1 | P2 | P3
      labels: ["feat", "analytics", "v0.7.2"],
      phase: "BUILD",            // UNDERSTAND | PLAN | BUILD | VERIFY | DEPLOY
      subtasksDone: 4,
      subtasksTotal: 7,
      assignee: "Chris",
      prNumber: 112,             // Linked PR, if any
      prStatus: "open",          // open | draft | merged | closed
      sessionId: null,           // Active Claude session, if any
      contextHealth: null,       // 0-100, null if no active session
      blockedReason: null,
      blockedSince: null,        // ISO timestamp
      completedAt: null,         // ISO timestamp
      url: "https://github.com/cmbays/dbt-playground/issues/94"
    }
  },

  // Board settings
  settings: {
    doneCardLimit: 10,
    autoArchiveDays: 7,
    showArchived: false
  }
};
```

#### Column Configuration

```javascript
const COLUMNS = [
  { id: 'backlog',     label: 'Backlog',     color: '#6b7280', icon: '📋' },
  { id: 'grooming',    label: 'Grooming',    color: '#3b82f6', icon: '✏️' },
  { id: 'ready',       label: 'Ready',       color: '#22c55e', icon: '✅' },
  { id: 'in-progress', label: 'In Progress', color: '#06b6d4', icon: '🔄' },
  { id: 'in-review',   label: 'In Review',   color: '#8b5cf6', icon: '👀' },
  { id: 'blocked',     label: 'Blocked',     color: '#ef4444', icon: '🚫' },
  { id: 'done',        label: 'Done',        color: '#374151', icon: '🎉' }
];

const TYPE_ICONS = {
  'bug': '🐛',
  'enhancement': '⭐',
  'docs': '📝',
  'chore': '🔧',
  'default': '📌'
};

const PRIORITY_STYLES = {
  'P0': { icon: '🔥', color: '#dc2626', label: 'Critical' },
  'P1': { icon: '🔴', color: '#f97316', label: 'High' },
  'P2': { icon: '🟡', color: '#eab308', label: 'Medium' },
  'P3': { icon: '⚪', color: '#9ca3af', label: 'Low' }
};

const PHASE_BADGES = {
  'UNDERSTAND': { label: 'UNDERSTAND', color: '#6b7280' },
  'PLAN':       { label: 'PLAN',       color: '#3b82f6' },
  'BUILD':      { label: 'BUILD',      color: '#22c55e' },
  'VERIFY':     { label: 'VERIFY',     color: '#f59e0b' },
  'DEPLOY':     { label: 'DEPLOY',     color: '#8b5cf6' }
};
```

### CSS Architecture

#### New CSS Variables (add to existing :root)

```css
:root {
  /* Kanban-specific variables */
  --kanban-column-width: 320px;
  --kanban-column-min-height: 400px;
  --kanban-card-gap: 0.75rem;
  --kanban-header-height: 48px;

  /* Health indicator colors */
  --health-green: #22c55e;
  --health-yellow: #eab308;
  --health-orange: #f97316;
  --health-red: #dc2626;
}
```

#### Kanban Board Layout

```css
/* Board viewport with horizontal scroll */
.kanban-viewport {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 1rem;
}

.kanban-board {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: var(--kanban-column-width);
  gap: 1rem;
  width: fit-content;
  min-width: 100%;
  height: calc(100vh - var(--header-height) - var(--footer-height) - 2rem);
}

/* Individual column */
.kanban-column {
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border-radius: 8px;
  min-height: var(--kanban-column-min-height);
}

.kanban-column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  background: inherit;
  border-radius: 8px 8px 0 0;
}

.kanban-column-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
}

.kanban-column-count {
  background: var(--bg-tertiary);
  padding: 0.125rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.kanban-column-cards {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: var(--kanban-card-gap);
}

/* Drop zone highlight */
.kanban-column.drag-over {
  background: rgba(37, 99, 235, 0.05);
}

.kanban-column.drag-over .kanban-column-cards {
  outline: 2px dashed var(--accent-primary);
  outline-offset: -4px;
}
```

#### Card Styling

```css
/* Card base */
.kanban-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-left: 4px solid transparent;
  border-radius: 6px;
  padding: 0.75rem;
  cursor: grab;
  transition: all 0.15s ease;
  position: relative;
}

.kanban-card:hover {
  box-shadow: var(--shadow);
  transform: translateY(-2px);
  border-left-color: var(--accent-primary);
}

.kanban-card:active {
  cursor: grabbing;
}

.kanban-card.dragging {
  opacity: 0.5;
  transform: rotate(3deg);
}

/* Card header row */
.kanban-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.kanban-card-id {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.kanban-card-id .type-icon {
  font-size: 0.875rem;
}

.kanban-card-indicators {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.priority-icon {
  font-size: 0.875rem;
}

.health-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: none;  /* Only show when not green */
}

.health-indicator.warning { display: block; background: var(--health-yellow); }
.health-indicator.danger { display: block; background: var(--health-orange); }
.health-indicator.critical {
  display: block;
  background: var(--health-red);
  animation: pulse 1.5s infinite;
}

/* Card title */
.kanban-card-title {
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

/* Card footer row */
.kanban-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
}

.kanban-card-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
}

.progress-dots {
  display: flex;
  gap: 2px;
}

.progress-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--bg-tertiary);
}

.progress-dot.completed {
  background: var(--accent-success);
}

.phase-badge {
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Card labels */
.kanban-card-labels {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.label-tag {
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.625rem;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

/* Blocked card styling */
.kanban-card.blocked {
  border-left-color: var(--accent-danger);
  background: rgba(239, 68, 68, 0.02);
}

.blocked-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  font-size: 1rem;
}

.blocked-time {
  font-size: 0.625rem;
  color: var(--accent-danger);
  margin-top: 0.25rem;
}
```

### JavaScript Implementation

#### Core Board Class

```javascript
class KanbanBoard {
  constructor() {
    this.state = this.loadState();
    this.selectedCard = null;
    this.init();
  }

  // State Management
  loadState() {
    const saved = localStorage.getItem('workflow-hub-kanban');
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed.version === 1) return parsed;
    }
    return this.getDefaultState();
  }

  saveState() {
    this.state.lastUpdated = new Date().toISOString();
    localStorage.setItem('workflow-hub-kanban', JSON.stringify(this.state));
  }

  getDefaultState() {
    return {
      version: 1,
      lastUpdated: new Date().toISOString(),
      lastGitHubSync: null,
      columns: {
        'backlog': [], 'grooming': [], 'ready': [],
        'in-progress': [], 'in-review': [], 'blocked': [], 'done': []
      },
      cards: {},
      settings: { doneCardLimit: 10, autoArchiveDays: 7, showArchived: false }
    };
  }

  // Initialization
  init() {
    this.render();
    this.initDragDrop();
    this.initKeyboard();
    this.syncGitHubIssues();
  }

  // Drag and Drop
  initDragDrop() {
    // Card drag events
    document.addEventListener('dragstart', (e) => {
      const card = e.target.closest('.kanban-card');
      if (!card) return;

      card.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', card.dataset.cardId);
    });

    document.addEventListener('dragend', (e) => {
      const card = e.target.closest('.kanban-card');
      if (card) card.classList.remove('dragging');
      document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
    });

    // Column drop events
    document.addEventListener('dragover', (e) => {
      const column = e.target.closest('.kanban-column');
      if (!column) return;

      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';

      // Remove previous highlights
      document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
      column.classList.add('drag-over');
    });

    document.addEventListener('drop', (e) => {
      const column = e.target.closest('.kanban-column');
      if (!column) return;

      e.preventDefault();
      const cardId = e.dataTransfer.getData('text/plain');
      const targetColumn = column.dataset.columnId;

      this.moveCard(cardId, targetColumn);
      column.classList.remove('drag-over');
    });
  }

  moveCard(cardId, targetColumn) {
    // Remove from current column
    for (const col of Object.keys(this.state.columns)) {
      const idx = this.state.columns[col].indexOf(cardId);
      if (idx !== -1) {
        this.state.columns[col].splice(idx, 1);
        break;
      }
    }

    // Add to target column
    this.state.columns[targetColumn].push(cardId);

    // Update blocked state if moving to/from blocked
    const card = this.state.cards[cardId];
    if (targetColumn === 'blocked' && !card.blockedSince) {
      card.blockedSince = new Date().toISOString();
    } else if (targetColumn !== 'blocked') {
      card.blockedSince = null;
      card.blockedReason = null;
    }

    // Update completed state
    if (targetColumn === 'done' && !card.completedAt) {
      card.completedAt = new Date().toISOString();
    } else if (targetColumn !== 'done') {
      card.completedAt = null;
    }

    this.saveState();
    this.render();
  }

  // Keyboard Navigation
  initKeyboard() {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.modalOpen) {
        this.closeModal();
      }
    });
  }

  // GitHub Sync
  async syncGitHubIssues() {
    try {
      const response = await fetch('/api/github-issues');
      if (!response.ok) throw new Error('GitHub sync failed');

      const issues = await response.json();
      this.mergeIssues(issues);
      this.state.lastGitHubSync = new Date().toISOString();
      this.saveState();
      this.render();
    } catch (err) {
      console.warn('GitHub sync unavailable:', err.message);
    }
  }

  mergeIssues(issues) {
    for (const issue of issues) {
      const cardId = `card-${issue.number}`;

      // Create or update card
      this.state.cards[cardId] = {
        ...this.state.cards[cardId],
        issueNumber: issue.number,
        title: issue.title,
        type: this.extractType(issue.labels),
        priority: this.extractPriority(issue.labels),
        labels: issue.labels.map(l => l.name).filter(l => !l.match(/^P[0-3]$/) && !['bug', 'enhancement', 'docs'].includes(l)),
        url: issue.html_url
      };

      // Add to backlog if new
      if (!this.findCardColumn(cardId)) {
        this.state.columns.backlog.push(cardId);
      }
    }
  }

  extractType(labels) {
    const types = labels.map(l => l.name);
    if (types.includes('bug')) return 'bug';
    if (types.includes('enhancement')) return 'enhancement';
    if (types.includes('docs') || types.includes('documentation')) return 'docs';
    return 'chore';
  }

  extractPriority(labels) {
    const priorities = ['P0', 'P1', 'P2', 'P3'];
    for (const p of priorities) {
      if (labels.some(l => l.name === p)) return p;
    }
    return 'P2'; // Default
  }

  findCardColumn(cardId) {
    for (const [col, cards] of Object.entries(this.state.columns)) {
      if (cards.includes(cardId)) return col;
    }
    return null;
  }

  // Rendering
  render() {
    const container = document.getElementById('kanban-board');
    if (!container) return;

    container.innerHTML = COLUMNS.map(col => this.renderColumn(col)).join('');
  }

  renderColumn(column) {
    const cards = this.state.columns[column.id] || [];
    const visibleCards = column.id === 'done'
      ? this.getVisibleDoneCards(cards)
      : cards;

    return `
      <div class="kanban-column" data-column-id="${column.id}">
        <div class="kanban-column-header">
          <div class="kanban-column-title">
            <span>${column.icon}</span>
            <span>${column.label}</span>
          </div>
          <span class="kanban-column-count">${cards.length}</span>
        </div>
        <div class="kanban-column-cards">
          ${visibleCards.map(cardId => this.renderCard(cardId)).join('')}
          ${column.id === 'done' && cards.length > visibleCards.length
            ? `<button class="show-archived-btn" onclick="kanbanBoard.toggleShowArchived()">
                 Show ${cards.length - visibleCards.length} more
               </button>`
            : ''
          }
        </div>
      </div>
    `;
  }

  renderCard(cardId) {
    const card = this.state.cards[cardId];
    if (!card) return '';

    const isBlocked = this.findCardColumn(cardId) === 'blocked';
    const typeIcon = TYPE_ICONS[card.type] || TYPE_ICONS.default;
    const priority = PRIORITY_STYLES[card.priority] || PRIORITY_STYLES.P2;
    const phase = card.phase ? PHASE_BADGES[card.phase] : null;

    return `
      <div class="kanban-card ${isBlocked ? 'blocked' : ''}"
           data-card-id="${cardId}"
           draggable="true"
           onclick="kanbanBoard.openCard('${cardId}')">
        ${isBlocked ? '<span class="blocked-badge">🚫</span>' : ''}

        <div class="kanban-card-header">
          <span class="kanban-card-id">
            <span class="type-icon">${typeIcon}</span>
            #${card.issueNumber}
          </span>
          <div class="kanban-card-indicators">
            <span class="priority-icon" title="${priority.label}">${priority.icon}</span>
            ${this.renderHealthIndicator(card.contextHealth)}
          </div>
        </div>

        <div class="kanban-card-title">${this.escapeHtml(card.title)}</div>

        <div class="kanban-card-footer">
          ${this.renderProgress(card)}
          ${phase ? `<span class="phase-badge" style="background: ${phase.color}; color: white">${phase.label}</span>` : ''}
        </div>

        ${card.labels?.length ? `
          <div class="kanban-card-labels">
            ${card.labels.slice(0, 3).map(l => `<span class="label-tag">${l}</span>`).join('')}
          </div>
        ` : ''}

        ${isBlocked && card.blockedSince ? `
          <div class="blocked-time">⏱️ Blocked ${this.formatBlockedTime(card.blockedSince)}</div>
        ` : ''}
      </div>
    `;
  }

  renderHealthIndicator(health) {
    if (health == null || health < 60) return '';
    const level = health >= 90 ? 'critical' : health >= 80 ? 'danger' : 'warning';
    return `<span class="health-indicator ${level}" title="${health}% context used"></span>`;
  }

  renderProgress(card) {
    if (!card.subtasksTotal) return '';
    const done = card.subtasksDone || 0;
    const total = card.subtasksTotal;

    const dots = Array.from({ length: Math.min(total, 7) }, (_, i) =>
      `<span class="progress-dot ${i < done ? 'completed' : ''}"></span>`
    ).join('');

    return `
      <div class="kanban-card-progress">
        <span class="progress-dots">${dots}</span>
        <span>${done}/${total}</span>
      </div>
    `;
  }

  getVisibleDoneCards(cards) {
    if (this.state.settings.showArchived) return cards;
    return cards.slice(-this.state.settings.doneCardLimit);
  }

  formatBlockedTime(since) {
    const days = Math.floor((Date.now() - new Date(since)) / (1000 * 60 * 60 * 24));
    if (days === 0) return 'today';
    if (days === 1) return '1 day';
    return `${days} days`;
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Card Modal
  openCard(cardId) {
    const card = this.state.cards[cardId];
    if (!card) return;

    this.selectedCard = cardId;
    // Show modal with full card details
    // Implementation in next section
  }

  toggleShowArchived() {
    this.state.settings.showArchived = !this.state.settings.showArchived;
    this.saveState();
    this.render();
  }
}

// Initialize on page load
let kanbanBoard;
document.addEventListener('DOMContentLoaded', () => {
  kanbanBoard = new KanbanBoard();
});
```

#### Card Modal Component

```javascript
// Add to KanbanBoard class
openCard(cardId) {
  const card = this.state.cards[cardId];
  if (!card) return;

  this.selectedCard = cardId;
  this.modalOpen = true;

  const column = this.findCardColumn(cardId);
  const isBlocked = column === 'blocked';

  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.id = 'card-modal';
  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <div class="modal-title">
          <span class="type-icon">${TYPE_ICONS[card.type] || TYPE_ICONS.default}</span>
          <span>#${card.issueNumber}</span>
          <span class="priority-badge" style="color: ${PRIORITY_STYLES[card.priority].color}">
            ${PRIORITY_STYLES[card.priority].icon} ${card.priority}
          </span>
        </div>
        <button class="modal-close" onclick="kanbanBoard.closeModal()">×</button>
      </div>

      <h2 class="modal-card-title">${this.escapeHtml(card.title)}</h2>

      <div class="modal-section">
        <h3>Status</h3>
        <div class="status-row">
          <span>Lane: <strong>${COLUMNS.find(c => c.id === column)?.label}</strong></span>
          ${card.phase ? `<span>Phase: <span class="phase-badge" style="background: ${PHASE_BADGES[card.phase].color}; color: white">${card.phase}</span></span>` : ''}
        </div>
      </div>

      ${card.subtasksTotal ? `
        <div class="modal-section">
          <h3>Progress</h3>
          <div class="progress-bar-container">
            <div class="progress-bar" style="width: ${(card.subtasksDone / card.subtasksTotal) * 100}%"></div>
          </div>
          <span class="progress-text">${card.subtasksDone} of ${card.subtasksTotal} subtasks complete</span>
        </div>
      ` : ''}

      ${isBlocked ? `
        <div class="modal-section blocked-section">
          <h3>🚫 Blocked</h3>
          <p><strong>Reason:</strong> ${card.blockedReason || 'No reason specified'}</p>
          <p><strong>Duration:</strong> ${this.formatBlockedTime(card.blockedSince)}</p>
        </div>
      ` : ''}

      ${card.sessionId ? `
        <div class="modal-section">
          <h3>Active Session</h3>
          <p>Session: ${card.sessionId}</p>
          <p>Context: ${card.contextHealth}% used</p>
        </div>
      ` : ''}

      <div class="modal-actions">
        ${!card.sessionId && (isBlocked || column === 'ready') ? `
          <button class="btn btn-primary" onclick="kanbanBoard.startSession('${cardId}')">
            ▶️ Start Session
          </button>
        ` : ''}
        <a href="${card.url}" target="_blank" class="btn btn-secondary">
          View on GitHub ↗
        </a>
        <div class="move-dropdown">
          <button class="btn btn-secondary">Move to...</button>
          <div class="dropdown-content">
            ${COLUMNS.filter(c => c.id !== column).map(c => `
              <button onclick="kanbanBoard.moveCard('${cardId}', '${c.id}'); kanbanBoard.closeModal();">
                ${c.icon} ${c.label}
              </button>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) this.closeModal();
  });
}

closeModal() {
  const modal = document.getElementById('card-modal');
  if (modal) modal.remove();
  this.modalOpen = false;
  this.selectedCard = null;
}

startSession(cardId) {
  const card = this.state.cards[cardId];
  if (!card) return;

  let command;
  if (card.prNumber) {
    command = `claude --from-pr ${card.prNumber}`;
  } else {
    command = `claude --from-issue ${card.issueNumber}`;
  }

  // Copy to clipboard
  navigator.clipboard.writeText(command).then(() => {
    this.showToast(`Copied: ${command}`);
  });

  this.closeModal();
}

showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}
```

---

## Testing Strategy

### Unit Tests

Since this is a single-file HTML implementation, testing is done via browser developer tools and manual verification.

**Test Cases**:

1. **Board Load**
   - Verify localStorage state loads correctly
   - Verify empty state creates default structure
   - Verify migration from older schema versions

2. **Drag and Drop**
   - Card moves between columns on drop
   - State persists after move
   - Blocked timestamp sets when moving to Blocked lane
   - Completed timestamp sets when moving to Done lane

3. **Card Rendering**
   - Type icons render correctly for each type
   - Priority icons match priority level
   - Health indicator shows only for yellow/orange/red
   - Progress dots render correctly
   - Labels truncate to 3 maximum

4. **Modal**
   - Opens on card click
   - Closes on X button, Escape key, or backdrop click
   - Start Session copies correct command
   - Move dropdown moves card to selected lane

5. **GitHub Sync**
   - New issues added to Backlog
   - Existing cards update with GitHub data
   - Labels extracted correctly

### Integration Tests

**Test Scenarios**:

1. **Full Workflow**
   - Create issue in GitHub → appears in Hub Backlog
   - Drag to In Progress → timestamp updates
   - Drag to Blocked → blocked indicator appears
   - Drag to Done → card archives correctly

2. **Session Integration**
   - Start Session generates correct command
   - Active session shows context health
   - Session end clears session from card

### Test Data

Use sample data in localStorage for development:

```javascript
// Add to console for testing
localStorage.setItem('workflow-hub-kanban', JSON.stringify({
  version: 1,
  lastUpdated: new Date().toISOString(),
  columns: {
    'backlog': ['card-35', 'card-36'],
    'in-progress': ['card-110'],
    'blocked': ['card-86'],
    'done': ['card-92']
  },
  cards: {
    'card-35': { issueNumber: 35, title: 'Add dbt_expectations tests', type: 'enhancement', priority: 'P1', phase: 'PLAN', subtasksDone: 2, subtasksTotal: 5 },
    'card-36': { issueNumber: 36, title: 'Singular tests for business rules', type: 'enhancement', priority: 'P2' },
    'card-110': { issueNumber: 110, title: 'Kanban board implementation', type: 'enhancement', priority: 'P1', phase: 'BUILD', subtasksDone: 8, subtasksTotal: 17, prNumber: 115 },
    'card-86': { issueNumber: 86, title: 'Research Kanban solutions', type: 'docs', priority: 'P2', blockedReason: 'Superseded by v0.9 decision', blockedSince: '2026-01-30T10:00:00Z' },
    'card-92': { issueNumber: 92, title: 'Issue Creation CLI', type: 'enhancement', priority: 'P1', completedAt: '2026-01-29T15:00:00Z' }
  },
  settings: { doneCardLimit: 10, autoArchiveDays: 7, showArchived: false }
}));
location.reload();
```

---

## Implementation Sequence

### Phase 1: Board Foundation (Est. ~3 hours)

- [ ] **1.1** Add Kanban tab to Hub header navigation
- [ ] **1.2** Create CSS Grid layout for 7 columns
- [ ] **1.3** Implement column rendering with headers
- [ ] **1.4** Implement card rendering with basic info (title, #, type icon)
- [ ] **1.5** Add localStorage persistence layer

### Phase 2: Drag and Drop (Est. ~2 hours)

- [ ] **2.1** Implement dragstart/dragend on cards
- [ ] **2.2** Implement dragover/drop on columns
- [ ] **2.3** Add visual feedback (opacity, drop zone highlight)
- [ ] **2.4** Persist column changes to localStorage

### Phase 3: Card Details (Est. ~2 hours)

- [ ] **3.1** Add priority icons and phase badges
- [ ] **3.2** Add progress dots component
- [ ] **3.3** Add health indicator (warning/danger/critical states)
- [ ] **3.4** Add labels display (max 3)
- [ ] **3.5** Add blocked card styling with time indicator

### Phase 4: Modal and Actions (Est. ~2 hours)

- [ ] **4.1** Implement card modal with full details
- [ ] **4.2** Add "Start Session" button with clipboard copy
- [ ] **4.3** Add "Move to..." dropdown for accessibility
- [ ] **4.4** Add GitHub link button
- [ ] **4.5** Add Escape key to close modal

### Phase 5: GitHub Sync (Est. ~1 hour)

- [ ] **5.1** Add `/api/github-issues` endpoint to Hub server
- [ ] **5.2** Implement issue merge logic
- [ ] **5.3** Add sync status indicator in header

### Phase 6: Polish (Est. ~2 hours)

- [ ] **6.1** Done lane archiving with "Show more" button
- [ ] **6.2** Responsive adjustments for tablet
- [ ] **6.3** Dark mode verification
- [ ] **6.4** Toast notifications for actions
- [ ] **6.5** Keyboard shortcuts help

**Total Estimate**: ~12 hours

---

## Security Considerations

- **No sensitive data**: Board state contains only issue metadata, no credentials
- **localStorage only**: No server-side storage of board state
- **GitHub API**: Read-only access via existing `gh` CLI authentication
- **XSS prevention**: All user content escaped via `textContent` before rendering

---

## Performance Considerations

- **Render optimization**: Only re-render changed columns on state update
- **Debounced saves**: Batch localStorage writes during rapid drag operations
- **Lazy modal**: Modal DOM created on-demand, not pre-rendered
- **Card limit**: Done lane limits visible cards to prevent DOM bloat

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| workflow-hub.html | File to extend | Exists |
| CSS Variables | Shared styling | Defined in Hub |
| GitHub CLI | Issue data | Available |
| SESSION_STATE | Session linking | Defined in PRD-019 |

---

## Open Questions

| # | Question | Status | Decision |
|---|----------|--------|----------|
| 1 | Should we add WIP limits per column? | Deferred | v0.8+ enhancement |
| 2 | How to handle very long card titles? | Resolved | Truncate to 2 lines with ellipsis |
| 3 | Should Done cards link to merged PRs? | Resolved | Yes, show PR link if available |

---

## Related

- **PRD**: [PRD-023-HUB-KANBAN.md](./PRD-023-HUB-KANBAN.md)
- **Research**: `temp/AGENT_REPORTS/hub-kanban-v072/RESEARCH_REPORT.md`
- **User Stories**: `temp/AGENT_REPORTS/hub-kanban-v072/PM_USER_STORIES.md`
- **ADR Index**: [ADR_INDEX.md](../reference/ADR_INDEX.md)
- **GitHub Issue**: [#110](https://github.com/cmbays/dbt-playground/issues/110)
- **Parent TDD**: [TDD-014-PLAYGROUND-TOOLS.md](./TDD-014-PLAYGROUND-TOOLS.md)
