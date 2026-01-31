# TDD-014: Interactive Playground Tools

## Overview

**Source PRD**: PRD-014-PLAYGROUND-TOOLS
**Author**: Technical Architect
**Status**: Draft
**Created**: 2026-01-31
**Updated**: 2026-01-31

### Summary

This document provides the technical design for Phase 1 of the Interactive Playground Tools: the **Git Worktree Coordinator** and **Mermaid Diagram Designer**.

### Design Goals

1. **Single-file HTML**: Each playground is self-contained, no build step
2. **No external dependencies at runtime**: Libraries embedded or loaded from CDN
3. **Consistent UI patterns**: Shared layout, keyboard shortcuts, styling
4. **Progressive disclosure**: Simple first, complexity on demand
5. **Offline-capable**: Core features work without network

---

## Architecture Overview

### File Structure

```text
playgrounds/
├── README.md                        # Index of all playgrounds
├── worktree-coordinator.html        # Phase 1: Git worktree management
├── mermaid-designer.html            # Phase 1: Diagram creation
├── agent-visualizer.html            # Phase 2 (planned)
├── schema-explorer.html             # Phase 2 (planned)
├── lineage-explorer.html            # Phase 3 (planned)
└── dashboard-builder.html           # Phase 4 (planned)
```

### Shared Component Pattern

Each playground follows this HTML structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Playground Name] - dbt-playground</title>
  <style>
    /* Embedded CSS - shared base + playground-specific */
  </style>
</head>
<body>
  <header class="playground-header">
    <h1>[Playground Name]</h1>
    <div class="header-actions">
      <button id="refresh-btn">Refresh</button>
      <button id="help-btn">Help</button>
    </div>
  </header>

  <main class="playground-main">
    <!-- Playground-specific content -->
  </main>

  <footer class="playground-footer">
    <span class="status"></span>
    <span class="keyboard-hints">R: Refresh | ?: Help | Esc: Close</span>
  </footer>

  <script>
    /* Embedded JavaScript - shared utilities + playground-specific */
  </script>
</body>
</html>
```

### Shared CSS Variables

```css
:root {
  /* Colors - Light Mode */
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --bg-tertiary: #e8e8e8;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --text-muted: #999999;
  --accent-primary: #2563eb;
  --accent-success: #16a34a;
  --accent-warning: #ca8a04;
  --accent-danger: #dc2626;
  --border-color: #e5e5e5;

  /* Typography */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
  --font-size-xl: 1.5rem;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Layout */
  --header-height: 60px;
  --footer-height: 40px;
  --sidebar-width: 280px;
  --max-content-width: 1400px;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #1a1a1a;
    --bg-secondary: #262626;
    --bg-tertiary: #333333;
    --text-primary: #f5f5f5;
    --text-secondary: #a3a3a3;
    --text-muted: #737373;
    --border-color: #404040;
  }
}
```

### Shared JavaScript Utilities

```javascript
// Keyboard shortcut handler
const KeyboardShortcuts = {
  handlers: {},

  register(key, callback, description) {
    this.handlers[key.toLowerCase()] = { callback, description };
  },

  init() {
    document.addEventListener('keydown', (e) => {
      // Ignore if typing in input
      if (e.target.matches('input, textarea, [contenteditable]')) return;

      const key = e.key.toLowerCase();
      const handler = this.handlers[key];
      if (handler) {
        e.preventDefault();
        handler.callback();
      }
    });
  },

  getHelp() {
    return Object.entries(this.handlers)
      .map(([key, { description }]) => `${key.toUpperCase()}: ${description}`)
      .join('\n');
  }
};

// Status bar helper
const StatusBar = {
  element: null,

  init(selector = '.status') {
    this.element = document.querySelector(selector);
  },

  set(message, type = 'info') {
    if (!this.element) return;
    this.element.textContent = message;
    this.element.className = `status status-${type}`;
  },

  success(message) { this.set(message, 'success'); },
  error(message) { this.set(message, 'error'); },
  warning(message) { this.set(message, 'warning'); },
  info(message) { this.set(message, 'info'); }
};

// Local storage helper
const Storage = {
  prefix: 'dbt-playground-',

  get(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(this.prefix + key);
      return item ? JSON.parse(item) : defaultValue;
    } catch {
      return defaultValue;
    }
  },

  set(key, value) {
    try {
      localStorage.setItem(this.prefix + key, JSON.stringify(value));
    } catch (e) {
      console.warn('Storage.set failed:', e);
    }
  },

  remove(key) {
    localStorage.removeItem(this.prefix + key);
  }
};

// Clipboard helper
const Clipboard = {
  async copy(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      return true;
    }
  }
};
```

---

## Playground 1: Git Worktree Coordinator

### Purpose

Visualize and manage git worktrees with conflict prevention and session awareness.

### Data Sources

| Source | Command | Format | Refresh |
|--------|---------|--------|---------|
| Worktree list | `git worktree list --porcelain` | Text (parsed) | On demand |
| Branch status | `git status --porcelain` | Text (parsed) | On demand |
| PR status | `gh pr list --json` | JSON | On demand |
| Remote status | `git fetch --dry-run` | Text | On demand |

### UI Layout

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  GIT WORKTREE COORDINATOR                           [Refresh] [Help] [New]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ MAIN REPOSITORY                                              [Clean]  │  │
│  │ /Users/chris/dbt-playground                                           │  │
│  │ Branch: main | Ahead: 0 | Behind: 0 | Last commit: 2h ago            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ACTIVE WORKTREES (2)                                                       │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ dbt-playground--customer-analytics                      [3 modified]  │  │
│  │ Branch: feat/customer-analytics                                       │  │
│  │ PR: #42 (Draft) "feat: add customer analytics"                       │  │
│  │ Behind main: 2 commits                                                │  │
│  │ [View] [Diff] [Commit] [Push] [Delete]                               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ dbt-playground--tuva                                          [Clean]  │  │
│  │ Branch: feat/tuva-integration                                         │  │
│  │ PR: #45 (Open) "feat: integrate Tuva Project"                        │  │
│  │ Up to date with main                                                  │  │
│  │ [View] [Delete]                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  2 worktrees | 3 modified files | Last refresh: just now        R:Refresh  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Model

```javascript
// Worktree data structure
const WorktreeData = {
  mainRepo: {
    path: '/Users/chris/dbt-playground',
    branch: 'main',
    isMain: true,
    status: {
      modified: 0,
      staged: 0,
      untracked: 0
    },
    remote: {
      ahead: 0,
      behind: 0
    },
    lastCommit: {
      hash: 'abc1234',
      message: 'feat: add analytics models',
      time: '2h ago'
    }
  },
  worktrees: [
    {
      path: '/Users/chris/dbt-playground--customer-analytics',
      name: 'dbt-playground--customer-analytics',
      branch: 'feat/customer-analytics',
      isMain: false,
      status: {
        modified: 3,
        staged: 0,
        untracked: 1
      },
      remote: {
        ahead: 1,
        behind: 2
      },
      pr: {
        number: 42,
        title: 'feat: add customer analytics',
        state: 'DRAFT',
        url: 'https://github.com/...'
      },
      lastCommit: {
        hash: 'def5678',
        message: 'wip: customer model',
        time: '30m ago'
      }
    }
  ]
};
```

### Key Functions

```javascript
// Parse git worktree list --porcelain output
function parseWorktreeList(output) {
  const worktrees = [];
  const blocks = output.trim().split('\n\n');

  for (const block of blocks) {
    const lines = block.split('\n');
    const worktree = {};

    for (const line of lines) {
      if (line.startsWith('worktree ')) {
        worktree.path = line.substring(9);
      } else if (line.startsWith('HEAD ')) {
        worktree.head = line.substring(5);
      } else if (line.startsWith('branch ')) {
        worktree.branch = line.substring(7).replace('refs/heads/', '');
      } else if (line === 'bare') {
        worktree.bare = true;
      }
    }

    if (worktree.path) {
      worktrees.push(worktree);
    }
  }

  return worktrees;
}

// Get status for a worktree
async function getWorktreeStatus(path) {
  // In browser context, this would need to call out to a local script
  // For now, we provide mock data or a manual refresh button
}

// Conflict detection
function detectConflicts(worktrees) {
  const conflicts = [];
  const branches = new Map();

  for (const wt of worktrees) {
    if (branches.has(wt.branch)) {
      conflicts.push({
        type: 'duplicate-branch',
        branch: wt.branch,
        worktrees: [branches.get(wt.branch), wt.path]
      });
    }
    branches.set(wt.branch, wt.path);
  }

  return conflicts;
}
```

### Browser Limitations

Since this runs in a browser, we cannot directly execute git commands. Options:

1. **Manual Paste Mode**: User runs command, pastes output into textarea
2. **Local Script Bridge**: Python script that serves data via localhost
3. **File Watcher**: Script writes JSON, playground reads it

**Recommended for v0.6.0**: Manual paste mode with helpful command hints.

```html
<div class="data-input-panel">
  <p>Run this command and paste the output below:</p>
  <code>git worktree list --porcelain && git status -sb</code>
  <button onclick="copyCommand()">Copy Command</button>
  <textarea id="git-output" placeholder="Paste git output here..."></textarea>
  <button onclick="parseAndDisplay()">Parse</button>
</div>
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| R | Refresh data |
| N | New worktree dialog |
| ? | Show help |
| Esc | Close dialogs |
| 1-9 | Select worktree by index |

---

## Playground 2: Mermaid Diagram Designer

### Purpose

Create, edit, and export Mermaid diagrams with live preview and templates.

### External Dependencies

| Library | Version | Purpose | CDN |
|---------|---------|---------|-----|
| Mermaid.js | 10.x | Diagram rendering | esm.sh or cdnjs |

### UI Layout

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  MERMAID DIAGRAM DESIGNER                    [Templates] [Export] [Help]    │
├────────────────────────────────────┬────────────────────────────────────────┤
│                                    │                                        │
│  CODE EDITOR                       │  LIVE PREVIEW                          │
│  ─────────────                     │  ────────────                          │
│  flowchart TD                      │                                        │
│    A[Staging] --> B[Intermediate]  │    ┌─────────┐                         │
│    B --> C[Marts]                  │    │ Staging │                         │
│    C --> D[Analytics]              │    └────┬────┘                         │
│                                    │         │                              │
│                                    │    ┌────▼────────┐                     │
│                                    │    │Intermediate │                     │
│                                    │    └────┬────────┘                     │
│                                    │         │                              │
│                                    │    ┌────▼────┐                         │
│                                    │    │  Marts  │                         │
│                                    │    └────┬────┘                         │
│                                    │         │                              │
│                                    │    ┌────▼─────┐                        │
│                                    │    │Analytics │                        │
│                                    │    └──────────┘                        │
│                                    │                                        │
├────────────────────────────────────┴────────────────────────────────────────┤
│  Type: Flowchart | Nodes: 4 | Valid: Yes                         ?:Help     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Model

```javascript
const DiagramState = {
  current: {
    id: 'diagram-1',
    name: 'dbt-layers',
    type: 'flowchart',
    code: 'flowchart TD\n  A[Staging] --> B[Marts]',
    created: '2026-01-31T10:00:00Z',
    modified: '2026-01-31T10:30:00Z'
  },
  library: [
    { id: 'diagram-1', name: 'dbt-layers', type: 'flowchart' },
    { id: 'diagram-2', name: 'agent-workflow', type: 'flowchart' }
  ],
  templates: {
    'dbt-layers': {
      name: 'dbt Layer Architecture',
      type: 'flowchart',
      code: `flowchart TD
    subgraph Sources
        S1[Raw Data]
    end
    subgraph Staging
        STG1[stg_model]
    end
    subgraph Intermediate
        INT1[int_model]
    end
    subgraph Marts
        FCT1[fct_model]
        DIM1[dim_model]
    end
    S1 --> STG1
    STG1 --> INT1
    INT1 --> FCT1
    INT1 --> DIM1`
    },
    'agent-workflow': {
      name: 'Agent Orchestration',
      type: 'flowchart',
      code: `flowchart LR
    USER([User]) --> SUP[Supervisor]
    SUP --> PM[Product Manager]
    PM --> ARCH[Architect]
    ARCH --> DEV[Developer]
    DEV --> TEST[Tester]
    TEST --> DOC[Documenter]
    DOC --> DONE([Complete])`
    },
    'er-diagram': {
      name: 'Entity Relationship',
      type: 'erDiagram',
      code: `erDiagram
    PATIENT ||--o{ ENCOUNTER : has
    ENCOUNTER ||--o{ CONDITION : has
    ENCOUNTER ||--o{ MEDICATION : has
    PROVIDER ||--o{ ENCOUNTER : performs`
    }
  }
};
```

### Key Functions

```javascript
// Initialize Mermaid
async function initMermaid() {
  await import('https://esm.sh/mermaid@10');
  mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
    flowchart: { htmlLabels: true }
  });
}

// Render diagram
async function renderDiagram(code, container) {
  try {
    const { svg } = await mermaid.render('diagram', code);
    container.innerHTML = svg;
    return { valid: true };
  } catch (error) {
    container.innerHTML = `<pre class="error">${error.message}</pre>`;
    return { valid: false, error: error.message };
  }
}

// Debounced render on input
const debouncedRender = debounce(async () => {
  const code = editor.value;
  const result = await renderDiagram(code, previewContainer);
  StatusBar.set(result.valid ? 'Diagram valid' : `Error: ${result.error}`,
                result.valid ? 'success' : 'error');
}, 300);

// Export to SVG
function exportSVG() {
  const svg = previewContainer.querySelector('svg');
  if (!svg) return;

  const svgData = new XMLSerializer().serializeToString(svg);
  const blob = new Blob([svgData], { type: 'image/svg+xml' });
  downloadBlob(blob, `${DiagramState.current.name}.svg`);
}

// Export to Markdown
function exportMarkdown() {
  const code = editor.value;
  const markdown = '```mermaid\n' + code + '\n```';
  Clipboard.copy(markdown);
  StatusBar.success('Markdown copied to clipboard');
}

// Export to PNG (requires canvas)
async function exportPNG() {
  const svg = previewContainer.querySelector('svg');
  if (!svg) return;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const img = new Image();

  const svgData = new XMLSerializer().serializeToString(svg);
  const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(svgBlob);

  img.onload = () => {
    canvas.width = img.width * 2;  // 2x for retina
    canvas.height = img.height * 2;
    ctx.scale(2, 2);
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);

    canvas.toBlob((blob) => {
      downloadBlob(blob, `${DiagramState.current.name}.png`);
      URL.revokeObjectURL(url);
    }, 'image/png');
  };

  img.src = url;
}

// Download helper
function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
```

### Template Library

Templates are embedded in the HTML for offline use:

| Template | Type | Description |
|----------|------|-------------|
| dbt-layers | flowchart | dbt staging/intermediate/marts flow |
| agent-workflow | flowchart | Agent orchestration sequence |
| er-synthea | erDiagram | Synthea entity relationships |
| healthcare-events | sequence | Clinical event timeline |
| git-workflow | flowchart | Git branching strategy |
| data-pipeline | flowchart | ETL/ELT pipeline |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+Enter | Render diagram |
| Ctrl+S | Save to library |
| Ctrl+E | Export menu |
| Ctrl+T | Templates menu |
| Ctrl+/ | Toggle comment |
| ? | Show help |

### Persistence

Diagrams are stored in localStorage:

```javascript
// Save diagram to library
function saveDiagram() {
  const library = Storage.get('mermaid-library', []);
  const existing = library.findIndex(d => d.id === DiagramState.current.id);

  if (existing >= 0) {
    library[existing] = DiagramState.current;
  } else {
    library.push(DiagramState.current);
  }

  Storage.set('mermaid-library', library);
  StatusBar.success('Diagram saved');
}

// Load library
function loadLibrary() {
  const library = Storage.get('mermaid-library', []);
  DiagramState.library = library;
  renderLibraryPanel();
}
```

---

## Testing Strategy

### Manual Testing Checklist

#### Worktree Coordinator

- [ ] Displays worktree list correctly
- [ ] Shows modified file counts
- [ ] Displays PR status when available
- [ ] Shows ahead/behind status
- [ ] Keyboard shortcuts work
- [ ] Help panel displays
- [ ] Dark mode works
- [ ] Copy command button works

#### Mermaid Designer

- [ ] Live preview updates on typing
- [ ] All diagram types render (flowchart, ER, sequence, class)
- [ ] Templates load correctly
- [ ] Export to Markdown works
- [ ] Export to SVG works
- [ ] Export to PNG works
- [ ] Save to library works
- [ ] Load from library works
- [ ] Dark mode works
- [ ] Error messages display for invalid syntax

### Browser Compatibility

Target browsers:

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Accessibility

- [ ] All interactive elements are keyboard accessible
- [ ] Focus states are visible
- [ ] Color contrast meets WCAG AA
- [ ] Screen reader labels on buttons

---

## Implementation Plan

### Phase 1a: Worktree Coordinator (4-6 hours)

1. Create HTML skeleton with shared styles
2. Implement manual paste mode for git data
3. Parse worktree list output
4. Display worktree cards
5. Add keyboard shortcuts
6. Add help panel
7. Test and refine

### Phase 1b: Mermaid Designer (6-8 hours)

1. Create HTML skeleton with split-pane layout
2. Integrate Mermaid.js from CDN
3. Implement live preview with debounce
4. Add template library
5. Implement export functions (MD, SVG, PNG)
6. Add diagram save/load with localStorage
7. Add keyboard shortcuts
8. Test and refine

### Shared Work

1. Document shared CSS/JS patterns
2. Update playgrounds/README.md
3. Test in multiple browsers
4. Add to CHANGELOG

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Mermaid.js CDN unavailable | High | Bundle fallback, document offline mode |
| Browser localStorage limits | Low | Warn on storage near limit |
| Git output parsing edge cases | Medium | Handle common formats, show raw on parse fail |
| Dark mode SVG rendering | Low | Test mermaid themes in dark mode |

---

## Future Enhancements (Post v0.6.0)

1. **Local server bridge**: Python/Node script for real git integration
2. **Mermaid live collaboration**: WebSocket sync between users
3. **Diagram version history**: Git-style versioning in localStorage
4. **VS Code extension**: Port playgrounds to VS Code webviews
5. **Real-time worktree monitoring**: File watcher for status updates

---

## References

- [PRD-014-PLAYGROUND-TOOLS.md](PRD-014-PLAYGROUND-TOOLS.md)
- [Mermaid.js Documentation](https://mermaid.js.org/)
- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [GitHub CLI Documentation](https://cli.github.com/manual/)

---

*TDD Status: Draft - Ready for Implementation*
