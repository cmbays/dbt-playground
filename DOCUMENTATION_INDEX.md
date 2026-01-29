# Documentation Index

**Purpose**: Navigate all documentation efficiently. This is the map to everything documented in the project.

**Last Updated**: 2026-01-28

---

## Documentation Hierarchy

```
dbt-playground Documentation
|
+-- CLAUDE.md                          [START HERE - Project Context]
|   |
|   +-- .claude/agents/AGENTS.md       [HOW to work - Agent Orchestration]
|   |   |
|   |   +-- .claude/agents/README.md   [WHO does what - Persona Definitions]
|   |   |
|   |   +-- .claude/skills/*.md        [WHAT to do - Reusable Workflows]
|   |   |   |-- tdd-workflow.md
|   |   |   |-- code-review-workflow.md
|   |   |   |-- deployment-workflow.md
|   |   |   +-- verification-loop.md
|   |   |
|   |   +-- .claude/rules/*.md         [STANDARDS to follow]
|   |       |-- coding-style.md
|   |       |-- git-workflow.md
|   |       |-- testing.md
|   |       +-- security.md
|   |
|   +-- docs/README.md                 [DOCS DIRECTORY INDEX]
|   |
|   +-- docs/reference/ARCHITECTURE.md [SYSTEM design]
|   |
|   +-- docs/reference/PROJECT_STRUCTURE.md [FILE organization]
|   |
|   +-- docs/reference/LEARNINGS.md    [TECHNICAL patterns]
|
+-- docs/                              [Living Documentation]
    |
    |-- README.md                      [Docs index]
    |
    |-- guides/                        [How-To Workflows]
    |   |-- PROJECT_WORKFLOW.md        [Epic → TDD → Task pattern]
    |   |-- PROJECT_BOARD_GUIDE.md     [GitHub Projects usage]
    |   +-- CLAUDE_TASK_INTEGRATION.md [Task system integration]
    |
    |-- standards/                     [Rules & Conventions]
    |   |-- TESTING.md                 [Testing framework]
    |   |-- DESIGN_PRINCIPLES.md       [UI/UX standards]
    |   +-- WORKFLOW_EXCEPTIONS.md     [Approved deviations]
    |
    |-- reference/                     [Technical Documentation]
    |   |-- ARCHITECTURE.md            [System architecture]
    |   +-- PROJECT_STRUCTURE.md       [File organization]
    |
    |-- specs/                         [Product Requirements]
    |   +-- PRD-*.md
    |
    +-- tdd/                           [Technical Designs]
        +-- TDD-*.md
```

---

## Quick Reference by Task

### "I'm Starting a New Session"

1. **[[CLAUDE.md]]** - Current project state, critical rules
2. **[[.claude/agents/AGENTS.md]]** - Agent orchestration guide
3. **[[docs/guides/PROJECT_BOARD_GUIDE.md]]** - Active tasks

### "I Need to Implement a Feature"

1. **[[docs/guides/PROJECT_WORKFLOW.md]]** - Epic → TDD → Task pattern
2. **[[docs/specs/]]** - Find the PRD for requirements
3. **[[docs/tdd/]]** - Find the TDD for specifications
4. **[[.claude/skills/tdd-workflow.md]]** - TDD process
5. **[[.claude/rules/coding-style.md]]** - Code standards

### "I Need to Review Code"

1. **[[.claude/skills/code-review-workflow.md]]** - Review process
2. **[[.claude/rules/security.md]]** - Security checklist
3. **[[docs/standards/DESIGN_PRINCIPLES.md]]** - UI/UX standards

### "I Need to Deploy a Version"

1. **[[.claude/skills/deployment-workflow.md]]** - Full deployment process
2. **[[.claude/rules/git-workflow.md]]** - Git standards
3. **[[CLAUDE.md#versioning-strategy]]** - Version numbering

### "I Need to Update Documentation"

1. **[[.claude/agents/AGENTS.md]]** - Maintenance guide
2. **[[docs/reference/PROJECT_STRUCTURE.md]]** - Where files go
3. **[[DOCUMENTATION_INDEX.md]]** - This file

### "I Need to Understand the Architecture"

1. **[[docs/reference/ARCHITECTURE.md]]** - System design
2. **[[docs/reference/PROJECT_STRUCTURE.md]]** - File organization

---

## Document Purposes

### Root Directory

| Document | Purpose | Primary Audience |
|----------|---------|------------------|
| **[[CLAUDE.md]]** | Complete project context | Claude (every session) |
| **[[DOCUMENTATION_INDEX.md]]** | Navigation map (this file) | Everyone |
| **[[CHANGELOG.md]]** | Version history | Everyone |
| **[[README.md]]** | Project overview | New contributors |

### .claude/ Directory

| Document | Purpose | Primary Audience |
|----------|---------|------------------|
| **[[.claude/agents/AGENTS.md]]** | Agent orchestration guide | All agents |
| **[[.claude/agents/README.md]]** | Persona definitions | All agents |
| **[[.claude/skills/*.md]]** | Reusable workflows | Relevant personas |
| **[[.claude/rules/*.md]]** | Coding standards | All developers |

### docs/ Directory

| Document | Purpose | Primary Audience |
|----------|---------|------------------|
| **[[docs/reference/ARCHITECTURE.md]]** | System architecture | Architect, Developer |
| **[[docs/reference/PROJECT_STRUCTURE.md]]** | File organization | Multi-agent |
| **[[docs/guides/PROJECT_WORKFLOW.md]]** | Epic → TDD → Task | Multi-agent |
| **[[docs/standards/TESTING.md]]** | Testing framework | Tester, Developer |

---

## Navigation Tips

### For New Agents
1. Start with **[[CLAUDE.md]]** (auto-loaded)
2. Check **[[.claude/agents/AGENTS.md]]** for orchestration guide
3. Review **[[docs/README.md]]** for documentation organization

### For Documentation Updates
1. Check **[[docs/reference/PROJECT_STRUCTURE.md]]** for file locations
2. Update living documents immediately
3. Update cross-references in this file

---

*This index should be updated whenever new documentation is added or documentation structure changes.*

**Last major update**: 2026-01-28 (rebrand to dbt-playground)
