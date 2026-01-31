# Interactive Playgrounds

Visual tools for learning, development, and debugging in dbt-playground.

## Available Playgrounds

| Playground | File | Purpose | Status |
|------------|------|---------|--------|
| Workflow Hub | `workflow-hub.html` | Central command center, session resume | **v0.6.0** |
| Workflow Chronicle | `workflow-chronicle.html` | Stratified timeline, health pulse, agent export | **v0.7.0** |
| Worktree Coordinator | `worktree-coordinator.html` | Manage parallel git worktrees | **v0.6.0** |
| Mermaid Designer | `mermaid-designer.html` | Create and export Mermaid diagrams | **v0.6.0** |
| Agent Visualizer | `agent-visualizer.html` | View agent workflows and state | Planned (v0.7.1) |
| Schema Explorer | `schema-explorer.html` | Browse Synthea healthcare data | Planned (v0.7.1) |
| Lineage Explorer | `lineage-explorer.html` | Trace dbt data flow | Planned (v0.7.2) |
| Dashboard Builder | `dashboard-builder.html` | Mock analytics layouts | Planned (v0.7.3) |

## Quick Start

1. Open any `.html` file in a browser
2. No build step, no dependencies, no server required

### Workflow Hub

The central command center for dbt-playground:

1. Open `workflow-hub.html` in a browser
2. Paste data from `temp/WORKFLOW_STATE.md` or `temp/SESSION_SUMMARY_*.md`
3. See Quick Resume, Active Tracks, and Agent Activity

**Features**:

- Quick Resume panel for session continuity
- Active Tracks view from WORKFLOW_STATE.md
- Agent Activity timeline
- Git Worktree summary
- Navigation to all other playgrounds

### Worktree Coordinator

Visualize and manage git worktrees for parallel development:

1. Open `worktree-coordinator.html` in a browser
2. Run the provided command in your terminal
3. Paste the output to see your worktrees displayed

**Features**:

- Worktree dashboard with status cards
- Branch, PR, and ahead/behind status
- Copy commands for common operations
- Keyboard shortcuts (R: refresh, ?: help)

### Workflow Chronicle

Stratified timeline visualization with health pulse and agent export:

1. Open `workflow-chronicle.html` in a browser
2. Run `uv run scripts/generate-chronicle-data.py` to populate data
3. View commits, branches, and bedrock layers

**Features**:

- Glance panel with branch, phase, health, agent stats
- Stratified timeline (Surface/Features/Decisions/Bedrock layers)
- Agent contribution tracking (Co-Authored-By)
- JSON export for agent consumption (`?format=json`)

**CLI Companions**:

```bash
uv run scripts/workflow-timeline.py    # Git-based timeline
uv run scripts/workflow-glance.py      # 3-second health check
uv run scripts/compute-health-pulse.py # Composite health score
uv run scripts/check-negative-space.py # Query rejected decisions
```

### Mermaid Designer

Create diagrams with live preview and multiple export options:

1. Open `mermaid-designer.html` in a browser
2. Type Mermaid code in the editor
3. See live preview as you type

**Features**:

- Live Mermaid rendering with 400ms debounce
- 6 built-in templates (dbt layers, agent workflow, ER diagram, etc.)
- Export to Markdown, SVG, PNG, or standalone HTML
- Save diagrams to browser localStorage
- Dark mode support

## Commands

Access playgrounds via slash commands:

```text
/playground              # Open Workflow Hub (default entry point)
/playground:hub          # Workflow Hub explicitly
/playground:chronicle    # Workflow Chronicle (stratified timeline)
/playground:worktrees    # Git Worktree Coordinator
/playground:mermaid      # Mermaid Diagram Designer
/playground:agents       # Agent Visualizer (planned)
/playground:schema       # Schema Explorer (planned)
/playground:lineage      # Lineage Explorer (planned)
/playground:dashboards   # Dashboard Builder (planned)
```

## Design Philosophy

- **Single-file HTML**: Each playground is self-contained
- **No dependencies**: Works offline (Mermaid loads from CDN)
- **Progressive disclosure**: Simple interface, complexity on demand
- **Consistent patterns**: Shared layout, keyboard shortcuts, dark mode

## Keyboard Shortcuts

All playgrounds share these shortcuts:

| Key | Action |
|-----|--------|
| `?` | Show help |
| `Esc` | Close modals |
| `R` | Refresh (Worktree Coordinator) |
| `Ctrl+Enter` | Render (Mermaid Designer) |
| `Ctrl+S` | Save (Mermaid Designer) |

## Build Order

```text
Phase 1 (v0.6.0): Workflow Hub, Worktree Coordinator, Mermaid Designer  <-- Complete
Phase 2 (v0.7.0): Workflow Chronicle (stratified timeline)              <-- Complete
Phase 3 (v0.7.1): Agent Visualizer, Schema Explorer
Phase 4 (v0.7.2): Lineage Explorer
Phase 5 (v0.7.3): Dashboard Builder
```

## Documentation

- `docs/specs/PRD-014-PLAYGROUND-TOOLS.md` - Full PRD
- `docs/specs/TDD-014-PLAYGROUND-TOOLS.md` - Technical design
- `docs/for_chris/PLAYGROUND-TOOLS.md` - Learning guide
- `.claude/commands/playground.md` - Command reference
