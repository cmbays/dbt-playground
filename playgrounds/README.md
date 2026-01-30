# Interactive Playgrounds

Visual tools for learning, development, and debugging in dbt-playground.

## Available Playgrounds

| Playground | File | Purpose | Status |
|------------|------|---------|--------|
| Worktree Coordinator | `worktree-coordinator.html` | Manage parallel git worktrees | Planned |
| Agent Visualizer | `agent-visualizer.html` | View agent workflows and state | Planned |
| Schema Explorer | `schema-explorer.html` | Browse Synthea healthcare data | Planned |
| Lineage Explorer | `lineage-explorer.html` | Trace dbt data flow | Planned |
| Dashboard Builder | `dashboard-builder.html` | Mock analytics layouts | Planned |

## Quick Start

1. Open any `.html` file in a browser
2. No build step, no dependencies, no server required

## Commands

Access playgrounds via slash commands:

```text
/playground              # List all playgrounds
/playground:worktrees    # Git Worktree Coordinator
/playground:agents       # Agent Visualizer
/playground:schema       # Schema Explorer
/playground:lineage      # Lineage Explorer
/playground:dashboards   # Dashboard Builder
```

## Design Philosophy

- **Single-file HTML**: Each playground is self-contained
- **No dependencies**: Works offline, no npm/pip required
- **Progressive disclosure**: Simple interface, complexity on demand
- **Consistent patterns**: Shared layout, keyboard shortcuts

## Build Order

```text
Phase 1 (v0.6.0): Worktree Coordinator
Phase 2 (v0.6.1): Agent Visualizer, Schema Explorer
Phase 3 (v0.6.2): Lineage Explorer
Phase 4 (v0.6.3): Dashboard Builder
```

## Documentation

- `docs/specs/PRD-014-PLAYGROUND-TOOLS.md` - Full PRD
- `docs/for_chris/PLAYGROUND-TOOLS.md` - Learning guide
- `.claude/commands/playground.md` - Command reference
