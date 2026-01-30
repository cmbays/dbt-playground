# Playground Commands

Interactive visual tools for learning and development.

## Usage

```
/playground              # List all playgrounds with status
/playground:worktrees    # Git Worktree Coordinator
/playground:agents       # Agent Orchestration Visualizer
/playground:schema       # Healthcare Schema Explorer
/playground:lineage      # Data Lineage Explorer
/playground:dashboards   # Dashboard Mockup Builder
```

## Available Playgrounds

### /playground:worktrees - Git Worktree Coordinator

**Purpose**: Manage parallel Claude Code sessions with git worktrees.

**Features**:

- View all worktrees with branch, status, and PR info
- Detect conflicts before they happen
- Quick actions: create, remove, fetch, prune
- Session tracking across worktrees

**When to Use**:

- Starting parallel development on multiple features
- Checking status of all active work
- Before creating a new worktree
- After merging PRs (cleanup)

**Launch**: Opens `playgrounds/worktree-coordinator.html`

---

### /playground:agents - Agent Orchestration Visualizer

**Purpose**: Understand and debug agent workflows.

**Features**:

- Workflow diagram from WORKFLOW_STATE.md
- Execution timeline with timestamps
- Agent dependency graph
- State inspector and editor

**When to Use**:

- Learning how agent orchestration works
- Debugging failed or stalled workflows
- Explaining workflows to new contributors
- Monitoring active `/orchestrate` execution

**Launch**: Opens `playgrounds/agent-visualizer.html`

---

### /playground:schema - Healthcare Schema Explorer

**Purpose**: Browse Synthea data structure interactively.

**Features**:

- Table browser with row counts
- Column details with sample values
- Foreign key relationship map
- Healthcare code system reference (SNOMED, ICD-10, etc.)

**When to Use**:

- Designing new dbt models
- Understanding Synthea data patterns
- Finding the right column for a query
- Learning healthcare terminology

**Launch**: Opens `playgrounds/schema-explorer.html`

---

### /playground:lineage - Data Lineage Explorer

**Purpose**: Trace data flow through the dbt DAG.

**Features**:

- Interactive DAG viewer
- Upstream/downstream analysis
- Impact analysis for changes
- Lineage diff between git refs

**When to Use**:

- Understanding model dependencies
- Before modifying existing models
- During PR review (impact check)
- Debugging data quality issues

**Launch**: Opens `playgrounds/lineage-explorer.html`

---

### /playground:dashboards - Dashboard Mockup Builder

**Purpose**: Design analytics dashboards visually.

**Features**:

- Drag-and-drop layout builder
- Metric definition interface
- Healthcare KPI templates
- Export to PNG, Markdown, JSON

**When to Use**:

- Planning new analytics features
- Communicating requirements to stakeholders
- Defining metrics before implementation
- Creating PRD visualizations

**Launch**: Opens `playgrounds/dashboard-builder.html`

---

## Implementation Status

| Playground | Status | Version |
|------------|--------|---------|
| Worktree Coordinator | Planned | v0.6.0 |
| Agent Visualizer | Planned | v0.6.1 |
| Schema Explorer | Planned | v0.6.1 |
| Lineage Explorer | Planned | v0.6.2 |
| Dashboard Builder | Planned | v0.6.3 |

## File Locations

```text
playgrounds/
├── worktree-coordinator.html   # Phase 1
├── agent-visualizer.html       # Phase 2
├── schema-explorer.html        # Phase 2
├── lineage-explorer.html       # Phase 3
└── dashboard-builder.html      # Phase 4
```

## Agent Suggestions

Agents should suggest relevant playgrounds contextually:

| Agent | Suggests | When |
|-------|----------|------|
| Supervisor | Worktree Coordinator | Creating parallel work tracks |
| Supervisor | Agent Visualizer | Explaining workflow phases |
| Data Modeler | Schema Explorer | Designing new models |
| dbt Developer | Lineage Explorer | Understanding dependencies |
| Semantic Analyst | Dashboard Builder | Defining metrics |
| Healthcare Analyst | Schema Explorer | Healthcare terminology questions |

## Related

- `docs/specs/PRD-014-PLAYGROUND-TOOLS.md` - Full PRD
- `docs/for_chris/PLAYGROUND-TOOLS.md` - Learning guide
- `CLAUDE.md` - Project context
