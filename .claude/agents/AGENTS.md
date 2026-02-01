# Agent Orchestration Guide

**Purpose**: This guide ensures smooth agent orchestration and handoff across sessions by documenting best practices, common pitfalls, and when to use which approach.

**Last Updated**: 2026-01-30
**Status**: Living Document

---

## Quick Reference

### When to Use Agents

| Task Type | Approach | Agent | Reason |
| ----------- | ---------- | ------- | -------- |
| Architecture design | **Agent** | `everything-claude-code:architect` | Specialized expertise, thorough analysis |
| Complex algorithms | **Agent** | `everything-claude-code:architect` | Need deep technical review |
| Feature implementation | **Agent** | `feature-dev:code-architect` → Developer | Structured workflow |
| Code review | **Agent** | `everything-claude-code:code-reviewer` | Objective quality checks |
| Security review | **Agent** | `everything-claude-code:security-reviewer` | Specialized security knowledge |
| Documentation | **Agent** | `everything-claude-code:doc-updater` | Structured, thorough docs |
| Typo fix | **Manual** | Direct | Too simple for agent overhead |
| Small CSS tweak | **Manual** | Direct | Quick, obvious change |
| Exploratory research | **Agent** | `Explore` | Thorough codebase analysis |
| Readiness assessment | **Skill** | `/readiness-check` | Assess gaps before new work |
| dbt model design | **Agent** | `data-modeler` | Dimensional modeling expertise |
| dbt implementation | **Agent** | `dbt-developer` | SQL/Jinja best practices |
| dbt testing | **Agent** | `dbt-tester` | Data quality validation |
| dbt documentation | **Agent** | `dbt-documenter` | Model/column descriptions |
| Metrics/semantic layer | **Agent** | `semantic-analyst` | KPI definitions, natural language |
| Healthcare terminology | **Agent** | `healthcare-analyst` | Clinical codes, data enrichment, compliance |

### Critical Rule: Be Explicit About File Operations

**❌ Don't:**

```javascript
Task({
  prompt: "Design the staging model schema for customer data",
  subagent_type: "everything-claude-code:architect"
})
```

**✅ Do:**

```javascript
Task({
  prompt: "Design the staging model schema for customer data.

  DELIVERABLES (must write to disk):
  1. temp/stg-customers-design.sql - Complete model implementation
  2. temp/T1.1-SCHEMA-DESIGN-DOC.md - Design documentation

  Use the Write tool to create these files.",
  subagent_type: "everything-claude-code:architect",
  allowed_tools: ["Write", "Edit", "Read", "Grep", "Glob"]
})
```

---

## Table of Contents

1. [Agent File Structure](#agent-file-structure)
2. [Core Principles](#core-principles)
3. [Agent Handoff Best Practices](#agent-handoff-best-practices)
4. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
5. [Agent Selection Guide](#agent-selection-guide)
6. [Token Optimization & Code Simplification](#token-optimization--code-simplification)
7. [Assembly Line Workflows](#assembly-line-workflows)
8. [Verification Checklist](#verification-checklist)
9. [Examples from T1.1 Case Study](#examples-from-t11-case-study)
10. [Related Documentation](#related-documentation)

---

## Agent File Structure

All agent files use YAML frontmatter for machine-parseable metadata, enabling context optimization and automatic tool grants.

### Frontmatter Schema

```yaml
---
name: agent-name          # Matches filename (without .md)
prefix: "name:"           # Invocation prefix (e.g., "arch:", "pm:")
description: One-line summary for agent selection UI
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: opus               # Default model (opus/sonnet/haiku)
---
```

### Field Reference

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Agent identifier, matches filename |
| `prefix` | Yes | Invocation prefix for queuing agent (e.g., "arch:", "pm:") |
| `description` | Yes | Concise summary (<100 chars) for selection |
| `tools` | Yes | Auto-granted tools when agent invoked |
| `model` | No | Default model preference |

### Benefits

1. **Context Optimization**: Metadata can be extracted without loading full agent content
2. **Auto Tool Grants**: Tools array eliminates need for `allowed_tools` in Task calls
3. **Agent Selection**: Description enables quick identification of right agent for task
4. **Model Hints**: Preferred model for agent's workload type

### Enhanced Sections

Priority agents include additional guidance sections:

| Section | Purpose | Agents |
|---------|---------|--------|
| **Red Flags** | Anti-patterns to watch for | architect, code-reviewer, security-reviewer, tester |
| **Common Patterns** | Code examples with ❌/✅ | architect, code-reviewer |

### Example Usage

When frontmatter includes tools, Task calls become simpler:

```javascript
// ❌ Old pattern (manual tool grants)
Task({
  prompt: "Review the authentication code...",
  subagent_type: "code-reviewer",
  allowed_tools: ["Read", "Grep", "Glob", "Bash"]  // Had to specify
})

// ✅ New pattern (auto-granted from frontmatter)
Task({
  prompt: "Review the authentication code...",
  subagent_type: "code-reviewer"
  // Tools auto-granted: ["Read", "Grep", "Glob", "Bash"]
})
```

### Validation

Run frontmatter validation to ensure all agents have valid metadata:

```bash
bash scripts/validate-frontmatter.sh
```

---

## Core Principles

### Principle 1: Agents Return Content for Review

**Key Insight**: Agents are designed to **return content in their response** rather than automatically writing files. This is a safety feature.

**Why This Matters**:

- Prevents agents from modifying codebase without oversight
- Allows review before committing changes
- Gives control over where files are created

**Action**: Always explicitly instruct agents to **write files to disk** if that's what you want.

### Principle 2: Explicit Deliverables

**Bad (Vague)**:
> "Design the authentication system"

**Good (Explicit)**:
> "Design the authentication system. Write these files:
>
> 1. `temp/auth-schema.js` - Schema definition
> 2. `temp/AUTH_DESIGN.md` - Design document
> 3. `temp/auth-api.js` - API interface
> Use the Write tool for each file."

### Principle 3: Grant Necessary Tools

**With Frontmatter (Preferred)**: Agent files with YAML frontmatter auto-grant tools specified in the `tools` array. No `allowed_tools` needed in Task calls.

**Without Frontmatter (Legacy)**: Grant file operation permissions explicitly:

```javascript
Task({
  allowed_tools: ["Write", "Edit", "Read", "Grep", "Glob", "Bash"],
  // ... other params
})
```

**Common tool needs by role**:

| Role | Tools | Auto-Granted? |
|------|-------|---------------|
| **Architect** | Write, Read, Grep, Glob | ✅ Yes |
| **Developer** | Write, Edit, Read, Bash, Grep, Glob | ✅ Yes |
| **Code Reviewer** | Read, Grep, Glob, Bash | ✅ Yes |
| **Security Reviewer** | Read, Write, Edit, Bash, Grep, Glob | ✅ Yes |
| **Tester** | Read, Bash, Grep, Glob | ✅ Yes |
| **Documenter** | Read, Write, Edit, Grep, Glob | ✅ Yes |

**Note**: All 11 project agents now have frontmatter with auto-granted tools.

### Principle 4: Verify Agent Output

After agent completes, **always verify** deliverables:

```javascript
// Check if files were created
Bash({ command: "ls -lh temp/stg-customers-design.sql" })

// If file doesn't exist, agent returned content in response
// Extract content manually or re-run agent with explicit instructions
```

---

## Agent Handoff Best Practices

### 1. Pre-Handoff: Prepare Context

Before calling an agent, ensure they have access to:

- **PRDs**: Link to relevant spec in `docs/specs/`
- **Task details**: GitHub issue number and acceptance criteria
- **Related work**: Point to similar completed tasks
- **Constraints**: File naming, structure, dependencies

**Example**:

```javascript
Task({
  prompt: `You are the architect for Task T1.2 (GitHub #14).

  Context:
  - PRD: docs/specs/PRD-001-Customer-Analytics.md
  - Previous task: T1.1 (schema design) completed
  - Schema file: temp/stg-customers-design.sql

  Your task: Design the dimensional model for customer analytics.

  Deliverables:
  1. models/marts/dim_customers.sql - Dimension model
  2. temp/T1.2-TESTING.md - Test plan

  Use Write tool to create files.`,
  subagent_type: "everything-claude-code:architect"
})
```

### 2. During Handoff: Clear Instructions

Structure your agent prompt with:

1. **Role**: "You are the [architect/developer/reviewer]"
2. **Context**: Links to relevant docs, previous work
3. **Task**: Specific objective from GitHub issue
4. **Deliverables**: Exact files to create with paths
5. **Tools**: Mention tools to use (Write, Edit, etc.)
6. **Constraints**: File conventions, dependencies, limits

### 3. Post-Handoff: Verification

```javascript
// 1. Check agent completed
TaskOutput({ task_id: "agent_id" })

// 2. Verify files exist
Bash({ command: "ls -lh temp/*.sql temp/*.md" })

// 3. Validate content
Read({ file_path: "temp/stg-customers-design.sql" })

// 4. If missing, extract from agent response
// (See "Common Pitfalls" section)
```

### 4. Handoff to Next Agent

When chaining agents (assembly line), include:

- **Previous agent's output**: Links to files created
- **Next steps**: What this agent should build on
- **Dependencies**: What to read first

**Example**:

```javascript
// After Architect completes schema design...
Task({
  prompt: `You are the Developer implementing T1.2.

  Build on previous work:
  - Schema: temp/stg-customers-design.sql (read this first)
  - Design doc: temp/T1.1-SCHEMA-DESIGN-DOC.md

  Your task: Implement the customer dimension model.

  Deliverables:
  1. models/marts/dim_customers.sql - Implementation
  2. models/marts/schema.yml - Tests and documentation

  Use Write tool for new files.`,
  subagent_type: "feature-dev",
  allowed_tools: ["Write", "Read", "Bash"]
})
```

---

## Inter-Agent Reports (v0.6+)

For multi-agent workflows, agents communicate via shared artifact folders instead of relying on orchestrator relay.

### Report Structure

```
temp/AGENT_REPORTS/[feature-name]/
├── PM_REPORT.md          # Product Manager scope and decisions
├── ARCH_REPORT.md        # Architect design and trade-offs
├── TEST_SPEC.md          # Tester coverage and test plan
├── DEV_REPORT.md         # Developer implementation notes
├── CODE_REVIEW.md        # Code reviewer findings
└── SECURITY_REVIEW.md    # Security reviewer assessment
```

### Workflow

1. **Supervisor creates folder** for new feature
2. **Each agent reads upstream** reports before starting
3. **Each agent writes** their report to the folder
4. **Supervisor verifies** reports exist before phase transitions

### Delegation Pattern

```text
# Instead of passing content through Supervisor:
pm: Create PRD for customer analytics.
    - Write PM_REPORT.md to: temp/AGENT_REPORTS/customer-analytics/
    - PRD location: docs/specs/PRD-XXX-CUSTOMER-ANALYTICS.md

# Downstream agent reads directly:
arch: Design feature per PRD-XXX.
    - Read: temp/AGENT_REPORTS/customer-analytics/PM_REPORT.md
    - Write: temp/AGENT_REPORTS/customer-analytics/ARCH_REPORT.md
```

### Benefits

- **Preserved signal fidelity**: No context loss from orchestrator summarization
- **Reduced orchestrator overhead**: Supervisor passes paths, not content
- **Audit trail**: Full record of agent decisions
- **Session continuity**: Reports enable quick resume

### Templates

See `docs/templates/agent-reports/` for all report templates.

**Related**: [[docs/specs/PRD-016-AGENT-CONTEXT-MANAGEMENT.md]] for full design.

---

## Context Management (v0.6+)

Context management ensures agents have the information they need across sessions and handoffs. The Sage agent manages context checkpoints and briefings.

### Context Checkpoint Workflow

When handing off between sessions or before complex agent work:

```
1. CHECKPOINT: Sage creates CONTEXT_CHECKPOINT_*.md with:
   - Current phase and active track
   - Key decisions made
   - Artifacts completed
   - Blockers or open questions

2. HANDOFF: Next session or agent reads checkpoint first

3. BRIEFING: Sage can prepare agent-specific briefings:
   - Filtered context relevant to agent's role
   - Pointers to key files (not full content)
   - Open questions requiring attention
```

### When to Create Checkpoints

| Trigger | Action |
|---------|--------|
| End of session | Supervisor requests checkpoint from Sage |
| Before complex handoff | Checkpoint current state |
| Context window near limit | Checkpoint to preserve context |
| Major phase transition | Checkpoint completed phase |

### Context Tiers

| Tier | Content | When Loaded |
|------|---------|-------------|
| **Quick** | Branch, phase, health score, last commit | Always (via Workflow Hub) |
| **Full** | Active artifacts, decisions, blockers | On session resume |
| **Archived** | Historical decisions, completed tracks | On demand |

### Checkpoint File Format

```markdown
# Context Checkpoint - [Feature Name]
Generated: [timestamp]

## Current State
- Branch: feat/xyz
- Phase: DEVELOPMENT
- Health: 93/100

## Key Decisions
1. [Decision with rationale]

## Completed Artifacts
- [x] PRD: docs/specs/PRD-XXX.md
- [x] ARCH_REPORT: temp/AGENT_REPORTS/xyz/

## Open Items
- [ ] Blocker description

## Pointers (Read These First)
- PM_REPORT.md for scope
- ARCH_REPORT.md for design
```

**See**: [[sage.md]] Section 11.3 for full checkpoint workflow.

---

## Agent Communication Patterns (v0.6+)

Agents communicate via three distinct mechanisms. Choose based on the communication need.

### Communication Method Comparison

| Method | Managed By | Use When | Persistence |
|--------|------------|----------|-------------|
| **Inter-Agent Reports** | Agents write, Supervisor verifies | Structured phase outputs | Feature folder |
| **WORKFLOW_STATE.md** | Supervisor | Track status, phases, queue | Single file |
| **Context Checkpoints** | Sage | Session handoffs, complex context | Per-checkpoint file |

### Decision Tree: Which Method?

```
Is this a structured phase deliverable?
├── YES → Inter-Agent Reports (PM_REPORT, ARCH_REPORT, etc.)
└── NO → Is this workflow status or phase tracking?
    ├── YES → WORKFLOW_STATE.md
    └── NO → Is this context preservation for handoff?
        ├── YES → Context Checkpoint (via Sage)
        └── NO → Direct agent-to-agent (future consideration)
```

### Inter-Agent Reports (Folder-Based)

**Best for**: Structured outputs that downstream agents need to read.

```
temp/AGENT_REPORTS/[feature]/
├── PM_REPORT.md      # PM writes, Architect reads
├── ARCH_REPORT.md    # Architect writes, Dev reads
├── TEST_SPEC.md      # Tester writes, Dev reads
└── ...
```

**Pattern**: Orchestrator passes file path, not content. Agent reads directly.

### WORKFLOW_STATE.md (Supervisor-Managed)

**Best for**: Tracking active work, phases, and multi-track coordination.

```yaml
active_track: feat/customer-analytics
phase: DEVELOPMENT
artifacts:
  - [x] PRD
  - [ ] TDD
queue:
  - fix/null-handling (urgent)
```

**Pattern**: Only Supervisor writes. All agents can read for context.

### Context Checkpoints (Sage-Managed)

**Best for**: Preserving rich context across sessions or context window limits.

**Pattern**: Sage creates on demand or at session end. Next session loads for quick resume.

---

## Workflow Visualization (v0.7+)

The Workflow Chronicle provides visual observability into agent workflows.

### Available Tools

| Tool | Purpose | Command |
|------|---------|---------|
| Workflow Hub | Central command center | `/playground:hub` |
| Workflow Chronicle | Timeline visualization | `/playground:chronicle` |
| Workflow Glance | 3-second terminal check | `uv run scripts/workflow-glance.py` |

### Workflow Chronicle Features

The Chronicle playground (`playgrounds/workflow-chronicle.html`) provides:

1. **Stratified Timeline**: Events, Features, Decisions, Bedrock layers
2. **Agent Tracking**: Who contributed what (via Co-Authored-By)
3. **Health Pulse**: Composite 0-100 score based on git metrics
4. **Negative Space**: Registry of decisions NOT made (NEGATIVE_SPACE.yaml)
5. **JSON Export**: Structured data for agent consumption

### CLI Companions

```bash
# Quick health check (3-second terminal view)
uv run scripts/workflow-glance.py

# Full timeline with agent attribution
uv run scripts/workflow-timeline.py

# Compute health score
uv run scripts/compute-health-pulse.py

# Query rejected decisions
uv run scripts/check-negative-space.py
```

### Integration with Supervisor

Supervisor can use Chronicle data to:

- Report health score in status updates
- Identify stalled features (no commits)
- Verify phase transitions have artifacts
- Trigger Sage when patterns indicate learning opportunity

**See**: [[playgrounds/README.md]] for full playground documentation.

---

## Common Pitfalls & Solutions

### Pitfall 1: Agent Returns Content Instead of Writing Files

**Symptom**: Agent response includes complete code, but `ls temp/` shows files don't exist.

**Root Cause**: Agent wasn't explicitly told to write files, or lacked Write permission.

**Solution**:

1. Extract content from agent response
2. Write files manually using Write tool
3. For future: Add explicit "Use Write tool" instruction

**Example Fix**:

```javascript
// After realizing agent didn't write files
Write({
  file_path: "temp/stg-customers-design.sql",
  content: `/* extract from agent response */`
})
```

**Prevention**:

- Always include "Use the Write tool to create these files" in prompt
- Grant `allowed_tools: ["Write", ...]`
- Verify files exist after agent completes

### Pitfall 2: Agent Lacks Context from Previous Work

**Symptom**: Agent designs something from scratch that conflicts with existing decisions.

**Root Cause**: Agent didn't read previous work or wasn't told where to find it.

**Solution**:

```javascript
Task({
  prompt: `IMPORTANT: First read these files for context:
  1. temp/stg-customers-design.sql - Schema you'll implement
  2. docs/specs/PRD-001-Customer-Analytics.md - Requirements

  Then implement... [rest of task]`,
  subagent_type: "feature-dev"
})
```

### Pitfall 3: Agent Over-Engineers Simple Task

**Symptom**: Agent produces 500 lines for a 10-line fix.

**Root Cause**: Used specialized agent for simple task.

**Solution**: Don't use agents for trivial tasks. Direct implementation is faster and simpler.

**Rule of Thumb**:

- **< 3 file changes**: Manual
- **Single obvious fix**: Manual
- **Complex logic/architecture**: Agent

### Pitfall 4: Unclear Acceptance Criteria

**Symptom**: Agent delivers something different from what was needed.

**Root Cause**: Prompt didn't include specific acceptance criteria from GitHub issue.

**Solution**:

```javascript
Task({
  prompt: `Task T1.2 from GitHub issue #14.

  Acceptance Criteria (from issue):
  - [ ] Staging model extracts all required columns
  - [ ] Primary key is unique and not null
  - [ ] Foreign key relationships are tested
  - [ ] Column descriptions are documented

  Implement staging model meeting ALL criteria above.`,
  subagent_type: "feature-dev"
})
```

### Pitfall 5: Agent Can't Find Files

**Symptom**: Agent says "file not found" for files that exist.

**Root Cause**: Relative paths from agent's execution context differ.

**Solution**: Use absolute paths or project-relative paths:

```javascript
// ❌ Relative (may fail)
"Read ../temp/schema.sql"

// ✅ Absolute or project-relative
"Read /Users/cmbays/Documents/claude/dbt-playground/temp/schema.sql"
"Read temp/schema.sql (from project root)"
```

---

## Agent Selection Guide

### Architecture & Design

**Agent**: `everything-claude-code:architect`

**When to use**:

- Designing system architecture
- Technical decision documents (TDDs)
- Database schema design
- API interface design
- Evaluating architectural trade-offs

**Example**:

```javascript
Task({
  description: "Design authentication architecture",
  prompt: "Design OAuth 2.0 authentication system...",
  subagent_type: "everything-claude-code:architect",
  allowed_tools: ["Write", "Read", "Grep", "Glob"]
})
```

**Deliverables**: Design docs, architecture diagrams, schemas

### Feature Implementation

**Agent**: `feature-dev:code-architect` → `feature-dev` developer

**When to use**:

- Building new features
- Multi-file implementations
- Complex business logic
- Following existing patterns

**Example**:

```javascript
// Step 1: Architecture
Task({
  description: "Plan customer analytics mart",
  prompt: "Analyze codebase and design customer mart models...",
  subagent_type: "feature-dev:code-architect"
})

// Step 2: Implementation
Task({
  description: "Implement customer analytics mart",
  prompt: "Build customer mart per architecture...",
  subagent_type: "feature-dev"
})
```

### Code Review

**Agent**: `everything-claude-code:code-reviewer`

**When to use**:

- After completing implementation
- Before merging PRs
- Checking for bugs, security issues
- Verifying best practices

**Example**:

```javascript
Task({
  description: "Review staging model code",
  prompt: "Review models/staging/stg_stripe__payments.sql for quality, patterns...",
  subagent_type: "everything-claude-code:code-reviewer",
  allowed_tools: ["Read", "Grep", "Glob"]
})
```

**Deliverables**: Review report, suggested fixes

### Security Review

**Agent**: `everything-claude-code:security-reviewer`

**When to use**:

- Authentication/authorization code
- User input handling
- API endpoints
- Data storage logic
- Before deploying sensitive features

**Example**:

```javascript
Task({
  description: "Security audit data model",
  prompt: "Review models/marts/fct_orders.sql for security vulnerabilities...",
  subagent_type: "everything-claude-code:security-reviewer"
})
```

### Testing

**Agent**: `everything-claude-code:tdd-guide` or `everything-claude-code:e2e-runner`

**When to use**:

- Writing unit tests
- Creating E2E test suites
- Verifying test coverage
- TDD workflow enforcement

**Example**:

```javascript
Task({
  description: "Write model tests",
  prompt: "Create schema tests for models/marts/fct_orders.sql...",
  subagent_type: "everything-claude-code:tdd-guide"
})
```

### Documentation

**Agent**: `everything-claude-code:doc-updater`

**When to use**:

- Updating codemaps
- Writing technical documentation
- Creating API reference
- Maintaining living docs

**Example**:

```javascript
Task({
  description: "Update architecture docs",
  prompt: "Update docs/ARCHITECTURE.md with new data mart design...",
  subagent_type: "everything-claude-code:doc-updater"
})
```

### Codebase Exploration

**Agent**: `Explore`

**When to use**:

- Understanding unfamiliar codebase
- Finding files by pattern
- Researching implementation details
- Tracing execution paths

**Example**:

```javascript
Task({
  description: "Find all staging models",
  prompt: "Search for all staging models and explain their structure...",
  subagent_type: "Explore",
  model: "haiku" // Fast for exploration
})
```

### Changelog Generation (Horizontal Service)

**Agent**: Changelog Generator (`changelog:` prefix)

Changelog Generator is a **horizontal service agent** — invoked by the Documenter or Deploy workflow to automate changelog entries from git history.

**When to use**:

- Generating changelog entries for a release
- Creating release notes for tags or PRs
- Checking for breaking changes since last tag
- Any time CHANGELOG.md needs updating from git history

**How it works**:

```
┌─────────────────────────────────────────────────────────┐
│  Documenter or /deploy workflow                         │
│  "Generate changelog for v0.5.0"                        │
└────────────────────────┬────────────────────────────────┘
                         │ Delegates to
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Changelog Generator                                    │
│  - Scans git log between tags                           │
│  - Parses Conventional Commits                          │
│  - Categorizes by impact (Breaking/Added/Fixed/etc)     │
│  - Outputs draft to temp/ for review                    │
└─────────────────────────────────────────────────────────┘
```

**Example**:

```javascript
Task({
  description: "Generate changelog since v0.4.0",
  prompt: `Generate changelog entries for v0.5.0.
  Base: v0.4.0, Head: HEAD.
  Write draft to temp/CHANGELOG_DRAFT_v0.5.0.md`,
  subagent_type: "changelog-generator"
})
```

**See**: [[changelog-generator.md]] for full persona details, [[../skills/changelog-generation.md]] for workflow.

### Git Operations (Horizontal Service)

**Agent**: Git-Master (`git:` prefix)

Git-Master is a **horizontal service agent** - unlike vertical agents that own specific workflow phases, Git-Master is invoked by ANY agent needing git operations.

**When to use**:

- Creating branches, commits, tags
- Creating or merging pull requests
- Any git write operation
- All agents delegate git work to git-master

**How it works**:

```
┌─────────────────────────────────────────────────────────┐
│  Any Agent (Developer, Documenter, etc.)                │
│  "I need to commit these changes"                       │
└────────────────────────┬────────────────────────────────┘
                         │ Delegates to
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Git-Master                                             │
│  - Validates format (Conventional Commits)              │
│  - Checks safety rules                                  │
│  - Executes with GIT_MASTER_AUTHORIZED=true             │
│  - Logs to audit trail                                  │
└─────────────────────────────────────────────────────────┘
```

**Commands**:

- `/commit` - Create validated commit
- `/branch` - Create validated branch

**Example**:

```javascript
// From any agent workflow
"git: commit my changes with message 'feat(orders): add order status filter'"
"git: create branch feat/new-feature"
"git: create PR for current branch"
```

**Enforcement**:

- `pre-bash-check.js` BLOCKS direct git write operations
- Only git-master can set `GIT_MASTER_AUTHORIZED=true`
- All operations logged to audit trail

**See**: [[git-master.md]] for full persona details, [[../skills/git-operations.md]] for workflows.

### Workflow Supervisor (Meta-Orchestrator)

**Agent**: Supervisor (`super:` prefix)

The Supervisor is the **meta-orchestrator** - it serves as the primary interface layer between the human and specialist agents, wrapping `/orchestrate` with verification and state management.

**When to use**:

- Starting a new work session
- Resuming work from a previous session
- Managing multiple parallel work tracks
- Handling urgent interrupts during active work
- Ensuring quality gates are enforced

**How it works**:

```
┌─────────────────────────────────────────────────────────┐
│  User Request                                           │
│  "Add customer analytics mart"                          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  SUPERVISOR (super:)                                    │
│  - Asks clarifying questions                            │
│  - Determines /orchestrate flags                        │
│  - Creates/updates temp/WORKFLOW_STATE.md               │
│  - Enforces artifact verification at phase gates        │
│  - Invokes Sage on failures/deployments                 │
└────────────────────────┬────────────────────────────────┘
                         │ Delegates to
                         ▼
┌─────────────────────────────────────────────────────────┐
│  /orchestrate [feature] [flags]                         │
│  PM → Arch → Tester → Dev → Review → Docs               │
└─────────────────────────────────────────────────────────┘
```

**Key Capabilities**:

| Capability | Description |
|------------|-------------|
| Interface Layer | Clarifies scope before delegating |
| Quality Gates | Blocks transitions if artifacts missing |
| State Management | Maintains `temp/WORKFLOW_STATE.md` |
| Sage Coordination | Triggers learning extraction |
| Multi-Track | Manages parallel features and queue |

**Commands**:

- `/supervisor` - Wake up for new/resumed session
- `super: resume` - Resume from state file
- `super: status` - Show all track status
- `super: queue [feature]` - Add to interrupt queue

**Sage Trigger Conditions**:

| Trigger | Action |
|---------|--------|
| User rejection | Invoke Sage for learning |
| ≥10 test failures | Invoke Sage for patterns |
| Agent confusion | Invoke Sage for clarification gaps |
| Successful deployment | Invoke Sage for positive patterns |

**State File** (`temp/WORKFLOW_STATE.md`):

```yaml
---
last_updated: 2026-01-29T14:30:00
active_track: feat/customer-analytics
---

## Active Tracks
### Track: feat/customer-analytics (ACTIVE)
- Phase: ARCHITECTURE
- Artifacts:
  - [x] PRD: docs/specs/PRD-004-customer-analytics.md
  - [ ] TDD: (pending)
```

**Relationship to Other Agents**:

```
                    ┌─────────────────┐
                    │   SUPERVISOR    │  ← Meta-orchestrator
                    │    (super:)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │ /orchestrate│  │    Sage     │  │ Git-Master  │
    │ (assembly)  │  │ (learning)  │  │ (git ops)   │
    └─────────────┘  └─────────────┘  └─────────────┘
```

**Multi-Worktree Support**:

Supervisor can manage multiple parallel work tracks across git worktrees:

- Each worktree = isolated Claude Code session
- Supervisor tracks all active worktrees via `git worktree list`
- Routes tasks to appropriate worktree/session
- `super: status` shows all active tracks including worktree locations

See [[docs/for_chris/GIT-WORKTREE-WORKFLOW.md]] for worktree workflow details.

**See**: [[supervisor.md]] for full persona details, [[../commands/supervisor.md]] for command usage.

### dbt Development Agents

The dbt agents form a specialized pipeline for data modeling, transformation, and analytics development.

#### Data Modeler (`dbt-model:`)

Designs dbt models following dimensional modeling best practices.

**When to use**:

- Designing staging, intermediate, fact, and dimension models
- Establishing naming conventions
- Defining model relationships and grain
- Creating source definitions

**Example**:

```
dbt-model: design a dimensional model for customer orders
dbt-model: create staging layer for Stripe payment data
```

**See**: [[data-modeler.md]] for full persona details.

#### dbt Developer (`dbt-dev:`)

Implements SQL models, macros, and incremental strategies.

**When to use**:

- Implementing model SQL from designs
- Writing Jinja macros
- Optimizing query performance
- Implementing incremental logic

**Example**:

```
dbt-dev: implement the stg_stripe__payments model
dbt-dev: add incremental logic to fct_orders
```

**See**: [[dbt-developer.md]] for full persona details.

#### dbt Tester (`dbt-test:`)

Ensures data quality through comprehensive testing.

**When to use**:

- Adding schema tests to models
- Creating singular tests for business rules
- Configuring source freshness
- Validating data quality

**Example**:

```
dbt-test: add schema tests to stg_stripe__payments
dbt-test: create singular test for orphaned orders
```

**See**: [[dbt-tester.md]] for full persona details.

#### dbt Documenter (`dbt-docs:`)

Maintains model and column documentation.

**When to use**:

- Writing model descriptions
- Documenting columns
- Generating dbt docs site
- Auditing documentation coverage

**Example**:

```
dbt-docs: document the orders mart models
dbt-docs: generate and serve dbt docs
```

**See**: [[dbt-documenter.md]] for full persona details.

#### Semantic Analyst (`semantic:`)

Designs and manages the dbt Semantic Layer.

**When to use**:

- Defining metrics and dimensions
- Enabling natural language queries
- Creating consistent KPI definitions
- Building semantic models

**Example**:

```
semantic: define revenue metrics for orders
semantic: query "revenue by month for 2024"
```

**See**: [[semantic-analyst.md]] for full persona details.

#### Healthcare Analyst (`hc:`)

Domain expert for healthcare terminology, clinical data patterns, and data enrichment.

**When to use**:

- Questions about healthcare code systems (ICD-10, SNOMED, CPT, LOINC, RxNorm)
- Clinical data validation guidance
- Data enrichment strategies (external sources, crosswalks)
- Tuva integration consulting
- HIPAA/compliance considerations

**Example**:

```
hc: What ICD-10 codes should we map for diabetes conditions?
hc: How should we enrich patient data with demographic information?
hc: Review the Tuva connector models for clinical accuracy
```

**See**: [[healthcare-analyst.md]] for full persona details.

### dbt Assembly Line

For dbt model development, agents chain together:

```
Healthcare Analyst → Data Modeler → dbt Developer → dbt Tester → Code Reviewer → dbt Documenter
       ↓                  ↓              ↓              ↓              ↓              ↓
  Domain Context      Design SQL    Implement      Add tests      Review        Document
```

**Commands** (see `.claude/commands/` for details):

| Command | Purpose | Agent/Skill |
|---------|---------|-------------|
| `/readiness-check` | Assess capability gaps before work | Supervisor + Skill |
| `/dbt-model` | Create new models | Data Modeler |
| `/dbt-test` | Add/run tests | dbt Tester |
| `/dbt-run` | Execute dbt commands | dbt Developer |
| `/dbt-docs` | Generate documentation | dbt Documenter |
| `/dbt-query` | Natural language queries | Semantic Analyst |

**Skills**:

- `dbt-model-development` - End-to-end workflow
- `dbt-testing` - Comprehensive testing
- `dbt-code-review` - dbt-specific review
- `dbt-deployment` - Safe deployment
- `dbt-source-onboarding` - New sources
- `dbt-semantic-layer` - Metrics design

---

## Token Optimization & Code Simplification

This section addresses reducing AI token burn-rate and context window usage through strategic use of simplification and cleanup agents.

**Philosophy**: The project's principle of "right amount of complexity is minimum needed" extends to token efficiency. Every unnecessary line of code burns tokens during review, testing, and future maintenance.

### Code-Simplifier Plugin Integration

The `code-simplifier` plugin helps identify and eliminate unnecessary complexity before it enters the codebase.

**When to Activate**:

- During code review (catch over-engineering)
- During architecture phase (design simply from start)
- During refactoring passes (batch cleanup)
- Before major releases (reduce baseline complexity)

### Agent Skill Matrix: Token-Optimized Tools

| Agent | Primary Tools | Add for Simplification | Use case |
|-------|---------------|------------------------|----------|
| **Architect** | Write, Read, Grep, Glob | **code-simplifier** | Design minimal from start |
| **Developer** | Write, Edit, Read, Bash | **code-simplifier** | Validate minimal implementation |
| **Code Reviewer** | Read, Grep, Glob | **code-simplifier** | Catch over-engineering before merge |
| **Refactor-Cleaner** | Write, Edit, Read, Bash, Grep, Glob | **code-simplifier** | Batch consolidation & cleanup |
| **Security Reviewer** | Read, Grep, Glob | *optional* | Identify security complexity |
| **Tester** | Read, Bash, Grep | *optional* | Identify test duplication |

### Token Burn Reduction Pipeline

```
Design Phase       Arch with code-simplifier
                   └─→ Simple, lean design
                       │
Implementation      Dev with code-simplifier
                   └─→ Minimal code
                       │
Review Phase        Code Reviewer + code-simplifier
                   └─→ Block over-complex PRs
                       │
Cleanup Phase       Refactor-Cleaner quarterly
                   └─→ Consolidate patterns, remove duplication
```

### Using Code-Simplifier with Agents

#### 1. Architect: Design for Simplicity

```javascript
Task({
  description: "Design order filtering system",
  prompt: `Design the order filtering architecture.

  IMPORTANT: Use code-simplifier to evaluate design complexity:
  - Identify unnecessary layers or abstraction
  - Validate that each component is truly needed
  - Suggest minimal implementation patterns

  DELIVERABLES:
  1. temp/order-filter-design.md - Design document
  2. temp/int_orders__filtered.sql - Intermediate model

  Use Write tool.`,
  subagent_type: "everything-claude-code:architect",
  allowed_tools: ["Write", "Read", "Grep", "Glob", "code-simplifier"]
})
```

**Expected Output**: Lean design without premature abstraction.

#### 2. Developer: Implement Minimally

```javascript
Task({
  description: "Implement order filtering",
  prompt: `Implement order filtering per design in temp/order-filter-design.md.

  Use code-simplifier to:
  - Ensure no unnecessary CTEs or helpers
  - Validate implementation matches minimal design
  - Flag any over-engineering detected

  DELIVERABLES:
  1. models/intermediate/int_orders__filtered.sql - Implementation
  2. models/intermediate/schema.yml - Tests

  Use Write tool.`,
  subagent_type: "feature-dev",
  allowed_tools: ["Write", "Edit", "Read", "Bash", "code-simplifier"]
})
```

**Expected Output**: Implementation with no unnecessary complexity.

#### 3. Code Reviewer: Enforce Simplicity Gate

```javascript
Task({
  description: "Review order filtering for complexity",
  prompt: `Review models/intermediate/int_orders__filtered.sql using code-simplifier:
  - Flag any functions that could be consolidated
  - Identify unnecessary abstractions
  - Check for code duplication
  - Validate test coverage is proportional to complexity

  Report findings and recommend simplifications.`,
  subagent_type: "everything-claude-code:code-reviewer",
  allowed_tools: ["Read", "Grep", "Glob", "code-simplifier"]
})
```

**Expected Output**: Review report with simplification recommendations. PR must address critical complexity flags before merge.

#### 4. Refactor-Cleaner: Batch Consolidation

**Frequency**: Quarterly or after 3+ features land

```javascript
Task({
  description: "Quarterly code simplification and consolidation",
  prompt: `Analyze entire codebase for simplification opportunities:

  Use code-simplifier to identify:
  - Duplicate patterns across topics/
  - Unused functions or exports
  - Over-engineered components
  - Opportunities for consolidation

  Create consolidation plan with:
  1. Priority ranking (impact/effort)
  2. Before/after token cost analysis
  3. Risk assessment for each consolidation

  DELIVERABLE:
  - temp/CONSOLIDATION_PLAN.md - Detailed plan

  Do NOT implement yet, only analyze and plan.`,
  subagent_type: "everything-claude-code:refactor-cleaner",
  allowed_tools: ["Read", "Grep", "Glob", "code-simplifier"]
})
```

**Expected Output**: Strategic consolidation plan. Review plan before execution to prioritize highest-ROI simplifications.

### Metrics: Token Burn Baseline

Track these metrics to validate improvement:

| Metric | Measurement | Target |
|--------|-------------|--------|
| **Lines per Feature** | Total lines / feature count | Decrease trend |
| **Complexity Flags** | code-simplifier issues per PR | ↓ 50% YoY |
| **Dead Code** | Unused functions/exports | < 2% of codebase |
| **Duplication Ratio** | Similar patterns / total code | < 5% |
| **Test:Code Ratio** | Test lines / implementation lines | 0.8-1.2x |

### Agent Token Metrics (Current)

All 11 agents with YAML frontmatter:

| Category | Count | ~Tokens |
|----------|-------|---------|
| Agent files | 11 | ~18,587 |
| With Red Flags | 4 | architect, code-reviewer, security-reviewer, tester |
| With Code Examples | 2 | architect, code-reviewer |

**Frontmatter ROI**: ~20-30 tokens saved per Task call (no `allowed_tools` needed)

Run `bash scripts/count-agent-tokens.sh` to measure current state.

### Implementation Strategy

**Phase 1: Immediate (This Sprint)**

- Add code-simplifier to Code Reviewer's tool set
- Run code-simplifier on all incoming PRs
- Document findings in review comments

**Phase 2: Standard (Next 2 Sprints)**

- Add code-simplifier to Architect (design phase)
- Add code-simplifier to Developer (implementation)
- Create quarterly Refactor-Cleaner task

**Phase 3: Optimization (Month 2+)**

- Analyze token savings from Phase 1-2
- Adjust agent skill matrix based on learnings
- Document patterns that increased/decreased complexity

---

## Assembly Line Workflows

The agent assembly line maps to the canonical 5-stage workflow (UNDERSTAND → PLAN → BUILD → VERIFY → DEPLOY). See [WORKFLOW_STAGES.md](../../docs/reference/WORKFLOW_STAGES.md) for complete stage definitions and quality gates.

### Standard Feature Development Pipeline

```
PM → Architect → Developer → Tester → Reviewer → Documenter
```

#### **1. PM: Define Requirements**

- Create PRD in `docs/specs/`
- Create GitHub issue with acceptance criteria
- Link PRD to issue

#### **2. Architect: Design System**

```javascript
Task({
  prompt: "Design [feature] architecture based on PRD...",
  subagent_type: "everything-claude-code:architect"
})
```

**Output**: TDD, schema, API design

#### **3. Developer: Implement**

```javascript
Task({
  prompt: "Implement [feature] per TDD in docs/specs/...",
  subagent_type: "feature-dev"
})
```

**Output**: Implementation files, initial tests

#### **4. Tester: Verify**

```javascript
Task({
  prompt: "Test [feature] implementation per acceptance criteria...",
  subagent_type: "everything-claude-code:tdd-guide"
})
```

**Output**: Test results, test coverage report

#### **5. Reviewer: Quality Check**

```javascript
Task({
  prompt: "Review [feature] code for quality, security, performance...",
  subagent_type: "everything-claude-code:code-reviewer"
})
```

**Output**: Review report, improvement suggestions

#### **6. Documenter: Update Docs**

```javascript
Task({
  prompt: "Update docs with [feature] details...",
  subagent_type: "everything-claude-code:doc-updater"
})
```

**Output**: Updated living docs, codemaps

#### **6b. Changelog Generator: Automated Changelog**

Invoked by Documenter during step 6 or by `/deploy`:

```javascript
Task({
  description: "Generate changelog for release",
  prompt: "Generate changelog entries since last tag. Write to temp/CHANGELOG_DRAFT.md",
  subagent_type: "changelog-generator"
})
```

**Output**: Draft changelog entries for review and curation

### Expedited Pipeline (Simple Features)

```
Architect → Developer → Reviewer
```

Skip PM (use GitHub issue as spec) and Tester (developer writes tests).

### Bug Fix Pipeline

`Explorer → Developer → Tester → Reviewer`

1. **Explorer**: Understand bug context
2. **Developer**: Fix with tests
3. **Tester**: Verify fix
4. **Reviewer**: Check for regressions

---

## Verification Checklist

After any agent completes, verify:

### ✅ Files Created

```bash
# Check expected deliverables exist
ls -lh temp/*.js temp/*.md

# If missing, check agent response for content
```

### ✅ Content Quality

```bash
# Read key files
cat temp/stg-customers-design.sql | head -50

# Check for:
# - Proper structure
# - Comments/documentation
# - No placeholder/TODO code
```

### ✅ Acceptance Criteria Met

Compare agent output to GitHub issue acceptance criteria:

- [ ] All checkboxes addressed
- [ ] Technical requirements met
- [ ] Edge cases handled

### ✅ Integration Points

- [ ] Follows existing code patterns
- [ ] Compatible with adjacent systems
- [ ] Doesn't break existing functionality

### ✅ Documentation

- [ ] Code comments present
- [ ] Design docs created
- [ ] Usage examples included
- [ ] Edge cases documented

---

## Examples from T1.1 Case Study

### What Went Wrong (First Attempt)

**Agent call**:

```javascript
Task({
  description: "Design localStorage schema architecture",
  prompt: "Design the staging model schema for customer data...",
  subagent_type: "everything-claude-code:architect"
})
```

**Result**: Agent returned complete code in response but didn't write files.

**Why**: No explicit "write files" instruction, no Write tool granted.

### What Went Right (Corrected)

**Agent call** (what should have been):

```javascript
Task({
  description: "Design localStorage schema architecture",
  prompt: `Design the staging model schema for customer data.

  DELIVERABLES (write to disk):
  1. temp/stg-customers-design.sql - Complete schema implementation
  2. temp/T1.1-SCHEMA-DESIGN-DOC.md - Comprehensive design document

  Use the Write tool to create both files.`,
  subagent_type: "everything-claude-code:architect",
  allowed_tools: ["Write", "Read", "Grep", "Glob"]
})
```

**Result**: Agent would have created files directly.

### Quality Comparison Results

**Manual approach** (543 lines):

- Basic constants
- Simple validation
- 2 helper functions
- Works but minimal

**Agent approach** (1032 lines):

- Immutable constants (`Object.freeze()`)
- 8 helper functions
- CJK Unicode validation
- Browser + Node.js compatibility
- Future-proofing (client_id, streak_start_date)
- 87% more code, better quality

**Lesson**: Agent orchestration produces higher quality for complex tasks, but requires explicit instructions.

---

## Related Documentation

### Core Documentation

- [[CLAUDE.md]] - Project instructions and agent orchestration overview
- [[.claude/agents/README.md]] - Agent persona definitions
- [[.claude/skills/README.md]] - Reusable workflow skills
- [[.claude/contexts/README.md]] - Context configurations

### Workflows

- [[docs/WORKFLOW_EXCEPTIONS.md]] - Approved deviations from standard workflow
- [[.claude/skills/tdd-workflow.md]] - Test-driven development process
- [[.claude/skills/code-review-workflow.md]] - Code review process
- [[.claude/skills/deployment-workflow.md]] - Release management

### Standards

- [[.claude/rules/coding-style.md]] - Code conventions
- [[.claude/rules/git-workflow.md]] - Version control standards
- [[.claude/rules/testing.md]] - Testing requirements
- [[.claude/rules/security.md]] - Security guidelines

### Case Studies

- [[docs/for_chris/]] - Educational narratives and case studies
- [[docs/reviews/]] - Past code reviews
- [[docs/specs/]] - Technical design documents

### GitHub Integration

- [[docs/PROJECT_BOARD_GUIDE.md]] - GitHub Projects workflow
- [[.github/ISSUE_TEMPLATE/]] - Issue templates
- [[.github/PULL_REQUEST_TEMPLATE.md]] - PR template

---

## Quick Tips

### 🎯 Golden Rules

1. **Be explicit**: Tell agents exactly which files to write
2. **Grant tools**: Include `allowed_tools: ["Write", "Read", ...]`
3. **Verify output**: Check files exist after agent completes
4. **Provide context**: Link to PRDs, previous work, related docs
5. **Simple tasks**: Do manually, don't over-engineer with agents

### 🚫 Common Mistakes

1. Vague instructions: "Design the thing" → No files created
2. No tool permissions: Agent can't write files
3. Wrong agent: Using architect for simple bug fix
4. Missing context: Agent designs incompatible solution
5. No verification: Assuming files were created

### ✨ Success Pattern

```javascript
// 1. Prepare context
const prd = "docs/specs/PRD-001.md";
const relatedWork = "temp/previous-task-output.js";

// 2. Call agent with explicit instructions
Task({
  description: "Design authentication system",
  prompt: `You are the Architect for Task T2.5 (GitHub #25).

  Context:
  - PRD: ${prd}
  - Related: ${relatedWork}

  Design OAuth 2.0 authentication system.

  DELIVERABLES (write using Write tool):
  1. temp/auth-schema.js - Database schema
  2. temp/auth-api.js - API interface
  3. temp/AUTH_DESIGN.md - Design document

  Include security considerations, edge cases, and examples.`,
  subagent_type: "everything-claude-code:architect",
  allowed_tools: ["Write", "Read", "Grep", "Glob"]
});

// 3. Verify deliverables
Bash({ command: "ls -lh temp/auth-*" });

// 4. Read and validate
Read({ file_path: "temp/AUTH_DESIGN.md" });

// 5. Proceed to next agent if needed
Task({
  description: "Implement authentication",
  prompt: `Implement auth system per design in temp/AUTH_DESIGN.md...`,
  subagent_type: "feature-dev"
});
```

---

## For New Agents / Fresh Context Sessions

Start here on every new session to quickly orient yourself:

### Essential Reading (Do First)

1. **[[CLAUDE.md]]** - Project context, current phase, critical rules
   - Current status: Analytics Layer Complete (v0.6.0)
   - Key workflow: UNDERSTAND → PLAN → BUILD → VERIFY → DEPLOY (see [[docs/reference/WORKFLOW_STAGES.md]])
   - Critical: Use git-master for all git operations

2. **This file (AGENTS.md)** - How to work effectively with the system
   - Agent selection guide
   - Handoff best practices
   - Common pitfalls to avoid

3. **[[docs/PROJECT_BOARD_GUIDE.md]]** - Active tasks and priorities
   - Check "In Progress" column
   - Identify blockers
   - Claim ready tasks

### Role-Specific Reading (Based on Task)

1. **[[.claude/agents/README.md]]** - Your role/persona definition
   - Review your persona's responsibilities
   - Understand handoff expectations
   - Check skill integrations

2. **[[docs/reference/LEARNINGS.md]]** - Technical patterns and decisions
   - Contains proven patterns with real examples
   - Documents decision frameworks
   - Quick reference for common approaches

### Quick Context Checklist

```markdown
- [ ] Read CLAUDE.md (project state)
- [ ] Reviewed active tasks in GitHub Projects
- [ ] Identified my persona for this task
- [ ] Checked for related PRDs in docs/specs/
- [ ] Located any previous work in temp/
```

---

## Documentation Maintenance Protocol

Agents are responsible for keeping documentation current. Follow these protocols to prevent documentation drift.

### When to Update Documentation

| Event | Update These Docs |
|-------|-------------------|
| New feature implemented | ARCHITECTURE.md, relevant skills/*.md |
| New workflow discovered | AGENTS.md, WORKFLOW_EXCEPTIONS.md |
| Bug fixed with learnings | TESTING.md (Bug Learnings section) |
| PRD completed | docs/specs/ (move from draft to approved) |
| TDD completed | docs/specs/, link from PRD |
| Version deployed | CHANGELOG.md, living docs timestamps |
| Pattern changed | DESIGN_PRINCIPLES.md or CONTENT_STANDARDS.md |
| New persona needed | .claude/agents/README.md, create persona file |

### Documentation Update Workflow

```
1. IDENTIFY which doc(s) need updating
2. READ current state to understand context
3. EDIT with minimal changes (preserve existing structure)
4. ADD wiki-links to related documentation
5. UPDATE "Last Updated" timestamp
6. VERIFY no broken wiki-links created
```

### Cross-Referencing Guidelines

**Always add wiki-links when:**

- Mentioning another document's content
- Referencing a related workflow or skill
- Describing integration with another system
- Pointing to examples or case studies

**Wiki-link format:**

```markdown
[[path/to/file.md]]           # Link to entire file
[[path/to/file.md#section]]   # Link to specific section
```

**Good cross-references:**

```markdown
See [[.claude/skills/tdd-workflow.md]] for testing approach.
Architecture decisions are documented in [[docs/ARCHITECTURE.md#key-architectural-decisions]].
```

### Avoiding Redundancy

**Before adding information, check:**

1. Does this already exist in another doc?
2. If yes, link to it instead of duplicating
3. If the other doc is incomplete, enhance IT rather than creating new content

**Authoritative sources:**

| Topic | Authoritative Document |
| ------- | ------------------------ |
| Agent orchestration | `.claude/agents/AGENTS.md` (this file) |
| Agent personas | `.claude/agents/README.md` |
| Reusable workflows | `.claude/skills/*.md` |
| Coding standards | `.claude/rules/*.md` |
| Project structure | `docs/PROJECT_STRUCTURE.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| dbt conventions | `docs/CONTENT_STANDARDS.md` |
| UI/UX patterns | `docs/DESIGN_PRINCIPLES.md` |
| Testing approach | `docs/TESTING.md` |
| Task management | `docs/PROJECT_BOARD_GUIDE.md` |

### When Discovering Redundancy

```markdown
1. Identify which document should be authoritative
2. Keep detailed content in authoritative source
3. Replace duplicate with wiki-link: "See [[authoritative.md#section]]"
4. Note consolidation in commit message
```

### Documentation Quality Checklist

Before committing documentation changes:

- [ ] Purpose statement clear at top
- [ ] Table of contents for docs > 100 lines
- [ ] "Last Updated" timestamp current
- [ ] Wiki-links to related docs
- [ ] No broken internal links
- [ ] No redundant content (link instead)
- [ ] Examples are current and working

---

## Related Documentation

### Core Project Documentation

| Document | Purpose | When to Reference |
| ---------- | --------- | ------------------- |
| [[CLAUDE.md]] | Project context, rules, workflows | Every session start |
| [[docs/ARCHITECTURE.md]] | System design, technical decisions | Implementation work |
| [[docs/PROJECT_STRUCTURE.md]] | File organization, naming | Finding/creating files |
| [[docs/DESIGN_PRINCIPLES.md]] | UI/UX standards | Frontend work |
| [[docs/CONTENT_STANDARDS.md]] | dbt naming conventions | Model creation |
| [[docs/TESTING.md]] | Testing framework, TDD | Verification work |

### Agent System Documentation

| Document | Purpose | When to Reference |
|----------|---------|-------------------|
| [[.claude/agents/README.md]] | Persona definitions | Understanding roles |
| [[.claude/skills/tdd-workflow.md]] | Test-driven development | Implementing features |
| [[.claude/skills/code-review-workflow.md]] | Review process | PR reviews |
| [[.claude/skills/deployment-workflow.md]] | Release management | Version deployment |
| [[.claude/rules/coding-style.md]] | Code conventions | Writing code |
| [[.claude/rules/git-workflow.md]] | Git practices | Version control |
| [[.claude/rules/security.md]] | Security guidelines | Security review |

### Project Management

| Document | Purpose | When to Reference |
|----------|---------|-------------------|
| [[docs/ROADMAP.md]] | Product roadmap, phases | Planning work |
| [[docs/PROJECT_BOARD_GUIDE.md]] | GitHub Projects usage | Task management |
| [[docs/WORKFLOW_EXCEPTIONS.md]] | Approved deviations | Skipping phases |
| [[docs/reference/LEARNINGS.md]] | Patterns, comparisons | Understanding decisions |

### Artifact Locations Summary

| Artifact Type | Location | Managed By |
|---------------|----------|------------|
| PRDs | `docs/specs/PRD-*.md` | PM persona |
| TDDs | `docs/specs/TDD-*.md` | Architect persona |
| Agent Reports | `temp/AGENT_REPORTS/[feature]/` | All agents |
| Session Summaries | `temp/SESSION_SUMMARY_*.md` | Supervisor |
| Test specs | `temp/v*_TESTING.md` | Tester persona |
| Build plans | `temp/v*_PLAN.md` | Any persona |
| Work in progress | `temp/` | Developer persona |
| Reviews | `docs/reviews/` | Reviewer personas |
| Educational docs | `docs/for_chris/` | Sage persona |
| Report Templates | `docs/templates/agent-reports/` | Documenter |

---

**Remember**: The goal isn't to always use agents. The goal is to **know when agents add value** and how to use them effectively when they do.

Documentation is code for humans. Keep it current, keep it linked, keep it useful.
