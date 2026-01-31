---
audience: [sage, human]
priority: medium
size: medium
last_updated: 2026-01-31
status: current
tags: [learning, playgrounds, visualization, tools]
---

# Interactive Playground Tools

**Purpose**: This guide explains the philosophy, design, and usage of the interactive playground tools in dbt-playground.

**Why This Exists**: As the project grew, we noticed recurring patterns: questions about data structure, confusion about agent workflows, difficulty coordinating parallel work. Rather than just documenting answers, we built interactive tools that let you explore and discover.

---

## The Story Behind Playgrounds

### The Problem

Picture this scenario: You start a new Claude Code session and want to add a customer analytics feature. You need to:

1. Understand which tables have customer data (Schema Explorer)
2. See what models already exist and their dependencies (Lineage Explorer)
3. Check if another worktree is already working on this (Worktree Coordinator)
4. Design what the dashboard might look like (Dashboard Builder)
5. Understand how the agent workflow will progress (Agent Visualizer)

Before playgrounds, each of these required different tools, commands, or documentation hunting. Now? Five HTML files that answer these questions interactively.

### The Philosophy

**Show, don't tell.** Instead of documentation that describes the data structure, show the actual tables with sample values. Instead of explaining agent workflows, visualize them as they happen.

**Single-file simplicity.** Each playground is one self-contained HTML file. No build step, no dependencies, no server required. Open in a browser and go.

**Progressive disclosure.** Start simple, reveal complexity on demand. The Schema Explorer shows tables first, then columns, then relationships, then code systems.

---

## The Six Playgrounds

### 0. Workflow Hub & Chronicle (Foundation - v0.6-0.7)

**Workflow Hub** (`/playground:hub`) - Central command center providing:

- Quick Resume panel with current branch, phase, health score
- Active Tracks view from WORKFLOW_STATE.md
- Agent Activity timeline showing recent contributions
- Git Worktree summary for parallel session awareness
- Navigation to all other playgrounds

**Workflow Chronicle** (`/playground:chronicle`) - Timeline visualization providing:

- Stratified timeline with Events, Features, Decisions, Bedrock layers
- Agent attribution tracking (who contributed what)
- Health Pulse composite score (0-100)
- Negative Space registry (decisions NOT made)
- JSON export for agent consumption

**Build Order Rationale**: Built as foundation because observability enables everything else. Without visibility into workflow state, other tools operate blind.

### 1. Git Worktree Coordinator (Phase 1 - v0.6.0)

**The Analogy**: Think of git worktrees like separate workbenches in a workshop. Each workbench has its own project, but they all share the same toolbox (git repository). The Coordinator is your workshop map.

**What It Solves**:

- "Is someone else working on this feature?"
- "How many parallel sessions do I have?"
- "Which worktree has uncommitted changes?"
- "Is this branch safe to delete?"

**Key Insight**: Git worktrees are powerful but invisible. You can't see them without running commands. The Coordinator makes parallel work visible at a glance.

**Build Order Rationale**: Built first because parallel development is the foundation for everything else. Without coordination, the other playgrounds could be built in conflicting worktrees.

### 2. Mermaid Diagram Designer (Phase 1.5 - v0.6.0)

**The Analogy**: Technical architecture needs visual communication. The Mermaid Designer is your whiteboard for creating dbt layer diagrams, agent workflows, and ER diagrams.

**What It Solves**:

- "How do I visualize the dbt layer architecture?"
- "Can I create an agent workflow diagram quickly?"
- "How do I share a technical diagram without Figma?"

**Key Features**:

- 6 built-in templates (dbt-layers, agent-workflow, er-healthcare, etc.)
- Zoom/pan with mouse (scroll to zoom, drag to pan)
- Export to Markdown, SVG, PNG, HTML
- Live preview as you edit

**Build Order Rationale**: Built alongside Worktree Coordinator because visual communication is essential for team alignment.

### 3. Agent Orchestration Visualizer (Phase 2 - Planned v0.7.1)

**The Analogy**: The agent system is like a factory assembly line. Each station (PM, Architect, Developer, etc.) does specific work and passes artifacts to the next. The Visualizer is the factory floor monitor showing which station is active and what's moving through.

**What It Solves**:

- "Which agent is working right now?"
- "Why did the workflow stall?"
- "What artifacts exist for this feature?"
- "How do agents hand off to each other?"

**Key Insight**: The `temp/WORKFLOW_STATE.md` file contains workflow state, but it's just text. The Visualizer transforms it into a live diagram with status indicators.

**Build Order Rationale**: Needs WORKFLOW_STATE.md to exist (which the Supervisor creates). Built in Phase 2 after Worktree Coordinator establishes parallel development.

### 4. Healthcare Schema Explorer (Phase 2 - Planned v0.7.1)

**The Analogy**: Synthea data is like a foreign language with its own vocabulary (SNOMED codes), grammar (relationships), and dialects (different table purposes). The Schema Explorer is your phrase book and translator.

**What It Solves**:

- "What columns are in the patients table?"
- "What does a SNOMED code mean?"
- "How do encounters relate to conditions?"
- "What sample values exist in this column?"

**Key Insight**: Healthcare data has two layers of complexity: technical (types, relationships) and domain (clinical codes, medical terminology). The Explorer addresses both.

**Build Order Rationale**: Can be built in parallel with Agent Visualizer since they share no dependencies. Essential for anyone designing dbt models.

### 5. Data Lineage Explorer (Phase 3 - Planned v0.7.2)

**The Analogy**: A dbt project is like a river system. Sources are springs, staging models are tributaries, and marts are the main river. The Lineage Explorer lets you trace water (data) from any point upstream or downstream.

**What It Solves**:

- "What sources feed this model?"
- "If I change this model, what breaks?"
- "Why is this column here?"
- "How did the DAG change in this PR?"

**Key Insight**: dbt docs already provides lineage, but requires `dbt docs generate` and `serve`. The Explorer parses `manifest.json` directly for instant, contextual lineage.

**Build Order Rationale**: Needs dbt models to exist (intermediate and marts). Built after Schema Explorer since understanding source data comes before understanding transformations.

### 6. Dashboard Mockup Builder (Phase 4 - Planned v0.7.3)

**The Analogy**: Before building a house, architects create mockups. Before building dashboards, analysts should mockup layouts. The Builder is your analytics sketchpad.

**What It Solves**:

- "What metrics do stakeholders actually want?"
- "How should KPIs be arranged?"
- "What dimensions enable slicing?"
- "Does this design make sense before we build it?"

**Key Insight**: Most analytics projects fail not from bad code, but from misunderstood requirements. Visual mockups force alignment before implementation.

**Build Order Rationale**: Last because it benefits from all other playgrounds. Uses Schema Explorer for column selection, Lineage Explorer for metric sources.

---

## Technical Architecture

### Why Single-File HTML?

**Pros**:

- No build step (open and use)
- No dependencies (no npm, no Python)
- Portable (email it, put it anywhere)
- Version-controlled (diff-able)
- Self-documenting (all code visible)

**Cons**:

- Limited interactivity (no backend)
- Larger file size (inlined dependencies)
- Harder to share components

**Tradeoff Decision**: For developer tools, simplicity wins. The playgrounds are meant for individual use, not production deployment.

### Data Sources

| Playground | Primary Data Source | Update Frequency |
|------------|---------------------|------------------|
| Worktree Coordinator | `git worktree list`, `gh pr list` | On demand (refresh) |
| Agent Visualizer | `temp/WORKFLOW_STATE.md` | Real-time (file watch) |
| Schema Explorer | DuckDB queries, `sources.yml` | On data reload |
| Lineage Explorer | `target/manifest.json` | After `dbt compile` |
| Dashboard Builder | User input | User-driven |

### Shared Patterns

All playgrounds share:

1. **Layout**: Header with title, main content area, status bar
2. **Refresh**: Manual refresh button (no auto-refresh to save resources)
3. **Export**: Copy/download results in useful formats
4. **Keyboard**: Consistent shortcuts (R=refresh, Esc=close modal)

---

## Usage Patterns

### Daily Workflow

```text
Morning:
1. /playground:worktrees  -> Check status of parallel work
2. /playground:agents     -> See where each track left off

During Development:
3. /playground:schema     -> Find columns for new model
4. /playground:lineage    -> Check impact before changes

Before PR:
5. /playground:lineage --diff main  -> Show lineage changes
```

### Onboarding Pattern

New contributor? Walk through in order:

1. **Schema Explorer**: Understand the source data
2. **Lineage Explorer**: See how data transforms
3. **Agent Visualizer**: Learn the workflow
4. **Worktree Coordinator**: Set up parallel work
5. **Dashboard Builder**: Plan your feature

### Debugging Pattern

Something wrong? Use playgrounds to diagnose:

| Symptom | Playground | What to Check |
|---------|------------|---------------|
| Workflow stuck | Agent Visualizer | Which phase, what's blocked |
| Wrong data | Lineage Explorer | Upstream dependencies |
| Unknown column | Schema Explorer | Column details, FK relationships |
| Merge conflict | Worktree Coordinator | Conflicting branches |

---

## Design Decisions

### Why Not Use dbt Docs?

dbt docs is excellent but:

- Requires `dbt docs generate` and `dbt docs serve`
- Full project scope (not focused on current work)
- No integration with agent system
- No worktree awareness

Our playgrounds complement dbt docs, not replace it.

### Why Not Use VS Code Extensions?

We considered VS Code extensions but:

- Not everyone uses VS Code
- Extensions require installation and updates
- Harder to share and version control
- Our HTML approach works everywhere

### Why HTML Instead of Terminal UI?

Terminal UIs (blessed, ink) were considered but:

- Harder to visualize relationships
- Limited color/styling
- No mouse interaction
- HTML is more accessible

For simple tools (Worktree Coordinator), terminal UI would work. For complex tools (Lineage Explorer), HTML is essential.

---

## Future Enhancements

**v0.7+**:

- Playground synchronization (Lineage shows model, Schema shows columns)
- Shared component library (DRY across playgrounds)
- Real-time updates via file watching
- Dark mode toggle

**v1.0+**:

- VS Code sidebar integration
- Team sharing (read-only hosted versions)
- Playground plugins for custom tools

---

## Related Documentation

- [PRD-014-PLAYGROUND-TOOLS.md](../specs/PRD-014-PLAYGROUND-TOOLS.md) - Full PRD with detailed features
- [CLAUDE.md](../../CLAUDE.md) - Project context with playgrounds section
- [playground.md](../../.claude/commands/playground.md) - Command reference
- [GIT-WORKTREE-WORKFLOW.md](./GIT-WORKTREE-WORKFLOW.md) - Worktree concepts

---

*This document was created as part of the v0.6 playground implementation. See WORKFLOW_STATE.md for current build status.*
