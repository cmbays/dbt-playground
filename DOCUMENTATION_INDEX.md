# Documentation Index

**Purpose**: Navigate all documentation efficiently. This is the map to everything documented in the project.

**Last Updated**: 2026-01-25

---

## Documentation Hierarchy

```
Japanese Study Site Documentation
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
|   |   |   |-- verification-loop.md
|   |   |   |-- kanji-content-creation.md
|   |   |   +-- topic-page-creation.md
|   |   |
|   |   +-- .claude/rules/*.md         [STANDARDS to follow]
|   |       |-- coding-style.md
|   |       |-- git-workflow.md
|   |       |-- testing.md
|   |       |-- security.md
|   |       +-- japanese-content.md
|   |
|   +-- docs/README.md                 [DOCS DIRECTORY INDEX + Tagging System]
|   |
|   +-- docs/reference/ARCHITECTURE.md [SYSTEM design]
|   |
|   +-- docs/reference/PROJECT_STRUCTURE.md [FILE organization]
|   |
|   +-- docs/guides/PROJECT_BOARD_GUIDE.md [TASK management]
|   |
|   +-- docs/reference/LEARNINGS.md    [TECHNICAL patterns]
|
+-- docs/                              [Living Documentation]
    |
    |-- README.md                      [Docs index + YAML tagging system]
    |-- DOC_TAGS_MANIFEST.md           [Tagging schema reference]
    |
    |-- guides/                        [How-To Workflows]
    |   |-- PROJECT_WORKFLOW.md        [Epic → TDD → Task pattern]
    |   |-- PROJECT_BOARD_GUIDE.md     [GitHub Projects usage]
    |   +-- CLAUDE_TASK_INTEGRATION.md [Claude task primitives]
    |
    |-- standards/                     [Rules & Conventions]
    |   |-- TESTING.md                 [Testing framework]
    |   |-- CONTENT_STANDARDS.md       [Japanese content]
    |   |-- DESIGN_PRINCIPLES.md       [UI/UX standards]
    |   +-- WORKFLOW_EXCEPTIONS.md     [Approved deviations]
    |
    |-- reference/                     [Technical Documentation]
    |   |-- ARCHITECTURE.md            [System architecture]
    |   |-- PROJECT_STRUCTURE.md       [File organization]
    |   +-- ROADMAP.md                 [Product roadmap]
    |
    |-- specs/                         [Product Requirements]
    |   +-- PRD-*.md
    |
    +-- tdd/                           [Technical Designs]
        +-- TDD-*.md
```

**Note**: For detailed docs/ organization, YAML tagging system, and smart loading patterns, see **[[docs/README.md]]**.

---

## Quick Reference by Task

### "I'm Starting a New Session"

1. **[[CLAUDE.md]]** - Current project state, critical rules
2. **[[.claude/agents/AGENTS.md#for-new-agents--fresh-context-sessions]]** - Onboarding checklist
3. **[[docs/guides/PROJECT_BOARD_GUIDE.md]]** - Active tasks
4. **[[docs/README.md]]** - Documentation navigation

### "I Need to Implement a Feature"

1. **[[docs/guides/PROJECT_WORKFLOW.md]]** - Epic → TDD → Task pattern
2. **[[docs/specs/]]** - Find the PRD for requirements
3. **[[docs/tdd/]]** - Find the TDD for specifications
4. **[[.claude/agents/AGENTS.md#assembly-line-workflows]]** - Follow the workflow
5. **[[.claude/skills/tdd-workflow.md]]** - TDD process
6. **[[.claude/rules/coding-style.md]]** - Code standards
7. **[[docs/standards/TESTING.md]]** - Testing requirements

### "I Need to Review Code"

1. **[[.claude/skills/code-review-workflow.md]]** - Review process
2. **[[.claude/rules/security.md]]** - Security checklist
3. **[[.claude/agents/AGENTS.md#code-review]]** - Agent usage
4. **[[docs/standards/DESIGN_PRINCIPLES.md]]** - UI/UX standards

### "I Need to Deploy a Version"

1. **[[.claude/skills/deployment-workflow.md]]** - Full deployment process
2. **[[.claude/rules/git-workflow.md]]** - Git standards
3. **[[CLAUDE.md#versioning-strategy]]** - Version numbering
4. **[[docs/standards/TESTING.md]]** - Verification checklist

### "I Need to Create Japanese Content"

1. **[[docs/standards/CONTENT_STANDARDS.md]]** - Content guidelines
2. **[[.claude/rules/japanese-content.md]]** - Technical standards
3. **[[.claude/skills/kanji-content-creation.md]]** - Kanji workflow
4. **[[docs/standards/DESIGN_PRINCIPLES.md]]** - UI/UX patterns

### "I Need to Update Documentation"

1. **[[.claude/agents/AGENTS.md#documentation-maintenance-protocol]]** - Maintenance guide
2. **[[docs/reference/PROJECT_STRUCTURE.md]]** - Where files go
3. **[[docs/README.md]]** - Docs directory organization
4. **[[DOCUMENTATION_INDEX.md]]** - This file (complete map)

### "I Need to Understand the Architecture"

1. **[[docs/reference/ARCHITECTURE.md]]** - System design
2. **[[docs/reference/PROJECT_STRUCTURE.md]]** - File organization
3. **[[docs/standards/DESIGN_PRINCIPLES.md]]** - UI/UX patterns
4. **[[docs/tdd/]]** - Technical design documents

### "I Need to Track Tasks"

1. **[[docs/guides/PROJECT_BOARD_GUIDE.md]]** - GitHub Projects usage
2. **[[docs/guides/CLAUDE_TASK_INTEGRATION.md]]** - Claude task primitives
3. **[[docs/reference/ROADMAP.md]]** - Product phases
4. **[[CLAUDE.md#agent-orchestration-system]]** - Personas for tasks

### "I Need to Understand YAML Tagging"

1. **[[docs/README.md]]** - Documentation index with tagging overview
2. **[[docs/DOC_TAGS_MANIFEST.md]]** - Complete tagging schema
3. **[[docs/guides/PROJECT_WORKFLOW.md]]** - Epic → TDD → Task pattern using tags

### "I Need to Find Learning Content"

1. **[[archive/FOR_CHRIS_docs/README.md]]** - Index of educational docs
2. **[[docs/reference/LEARNINGS.md]]** - Technical patterns and decision frameworks
3. **[[.claude/skills/learned-pattern-*.md]]** - Extracted workflow patterns
4. **[[.claude/agents/sage.md]]** - Learning curation system
5. **[[.claude/skills/learning-curation.md]]** - How to curate learnings

### "I Need to Extract Learnings from a Session"

1. **[[.claude/skills/learning-curation.md]]** - Full curation process
2. **[[.claude/skills/continuous-learning.md]]** - Pattern extraction workflow
3. **[[.claude/agents/sage.md]]** - Sage persona workflows
4. **[[archive/FOR_CHRIS_docs/README.md]]** - Decision rubric for FOR_CHRIS docs

---

## Document Purposes

### Root Directory

| Document | Purpose | Primary Audience | Links |
|----------|---------|------------------|-------|
| **[[CLAUDE.md]]** | Complete project context, auto-loaded by Claude | Claude (every session) | → [[.claude/agents/AGENTS.md]], [[docs/README.md]] |
| **[[DOCUMENTATION_INDEX.md]]** | Navigation map (this file) | Everyone | → [[docs/README.md]] |
| **[[CHANGELOG.md]]** | Version history | Everyone | ← [[.claude/rules/git-workflow.md]] |
| **[[README.md]]** | Project overview for humans | New contributors | → [[CLAUDE.md]] |

### docs/ Directory

**See [[docs/README.md]] for detailed organization, YAML tagging system, and smart loading patterns.**

#### guides/ (How-To Workflows)

| Document | Purpose | Primary Audience | Tags |
|----------|---------|------------------|------|
| **[[docs/guides/PROJECT_WORKFLOW.md]]** | Epic → TDD → Task pattern | Multi-agent | `audience: multi-agent, priority: high, size: large` |
| **[[docs/guides/PROJECT_BOARD_GUIDE.md]]** | GitHub Projects usage guide | PM, Developer | `audience: pm/developer, priority: medium` |
| **[[docs/guides/CLAUDE_TASK_INTEGRATION.md]]** | Claude task primitives | PM, Architect | `audience: pm/architect, priority: medium, size: large` |

#### standards/ (Rules & Conventions)

| Document | Purpose | Primary Audience | Tags |
|----------|---------|------------------|------|
| **[[docs/standards/TESTING.md]]** | Testing framework, TDD approach | Tester, Developer | `audience: tester/developer, priority: high, size: small` |
| **[[docs/standards/CONTENT_STANDARDS.md]]** | Japanese content guidelines | Sensei, Developer | `audience: sensei/developer, priority: medium` |
| **[[docs/standards/DESIGN_PRINCIPLES.md]]** | UI/UX standards, design system | Design, Developer | `audience: design/developer, priority: medium` |
| **[[docs/standards/WORKFLOW_EXCEPTIONS.md]]** | Approved workflow deviations | Multi-agent | `audience: multi-agent, priority: low, size: small` |

#### reference/ (Technical Documentation)

| Document | Purpose | Primary Audience | Tags |
|----------|---------|------------------|------|
| **[[docs/reference/ARCHITECTURE.md]]** | System design, technical decisions | Architect, Developer | `audience: architect/developer, priority: high` |
| **[[docs/reference/PROJECT_STRUCTURE.md]]** | File organization, naming conventions | Multi-agent | `audience: multi-agent, priority: high` |
| **[[docs/reference/ROADMAP.md]]** | Product roadmap, phase planning | PM, Architect | `audience: pm/architect, priority: low, size: large` |

#### Other

| Document | Purpose | Primary Audience |
|----------|---------|------------------|
| **[[docs/README.md]]** | Documentation index + YAML tagging system | All agents |
| **[[docs/DOC_TAGS_MANIFEST.md]]** | Tagging schema reference | All agents |
| **[[docs/specs/]]** | Product Requirements Documents (PRDs) | PM, Architect, Multi-agent |
| **[[docs/tdd/]]** | Technical Design Documents (TDDs) | Architect, Developer, Tester |
| **[[docs/reference/LEARNINGS.md]]** | Technical patterns, decision frameworks, common pitfalls | Sage, All agents |

### .claude/agents/ Directory

| Document | Purpose | Primary Audience | Links |
|----------|---------|------------------|-------|
| **[[.claude/agents/AGENTS.md]]** | Agent orchestration guide, best practices | All agents | → [[CLAUDE.md]], [[.claude/skills/]], [[docs/guides/PROJECT_BOARD_GUIDE.md]] |
| **[[.claude/agents/README.md]]** | Persona definitions, invocation methods | All agents | ← [[.claude/agents/AGENTS.md]] |
| **[[.claude/agents/sage.md]]** | Sage persona - Learning curation | Sage | → [[docs/reference/LEARNINGS.md]], [[archive/FOR_CHRIS_docs/]] |
| **[persona].md** | Individual persona role definition | Specific persona | ← [[.claude/agents/README.md]] |

### .claude/skills/ Directory

| Document | Purpose | Primary Audience | Links |
|----------|---------|------------------|-------|
| **[[.claude/skills/tdd-workflow.md]]** | Test-driven development process | Developer, Tester | ← [[docs/standards/TESTING.md]] |
| **[[.claude/skills/code-review-workflow.md]]** | Code review process | Reviewer | → [[.claude/rules/security.md]] |
| **[[.claude/skills/deployment-workflow.md]]** | Release management | Documenter | → [[.claude/rules/git-workflow.md]] |
| **[[.claude/skills/verification-loop.md]]** | QA verification | Tester | → [[docs/standards/TESTING.md]] |
| **[[.claude/skills/kanji-content-creation.md]]** | Kanji data workflow | Content creator | → [[docs/standards/CONTENT_STANDARDS.md]] |
| **[[.claude/skills/topic-page-creation.md]]** | Topic page workflow | Developer | → [[docs/standards/DESIGN_PRINCIPLES.md]] |
| **[[.claude/skills/continuous-learning.md]]** | Pattern extraction to skills | Sage | → [[docs/reference/LEARNINGS.md]] |
| **[[.claude/skills/learning-curation.md]]** | Session learning curation | Sage | → [[docs/reference/LEARNINGS.md]], [[archive/FOR_CHRIS_docs/]] |
| **[[.claude/skills/learned-pattern-*.md]]** | Extracted workflow patterns | Sage, All agents | ← [[docs/reference/LEARNINGS.md]] |

### .claude/rules/ Directory

| Document | Purpose | Primary Audience | Links |
|----------|---------|------------------|-------|
| **[[.claude/rules/coding-style.md]]** | HTML/CSS/JS conventions | Developer | ← [[CLAUDE.md]] |
| **[[.claude/rules/git-workflow.md]]** | Version control standards | Everyone | ← [[CLAUDE.md]] |
| **[[.claude/rules/testing.md]]** | Testing requirements | Tester, Developer | → [[docs/standards/TESTING.md]] |
| **[[.claude/rules/security.md]]** | Security guidelines | Security Reviewer | → [[docs/reference/ARCHITECTURE.md]] |
| **[[.claude/rules/japanese-content.md]]** | JLPT/content standards | Sensei, Content creator | → [[docs/standards/CONTENT_STANDARDS.md]] |

### .claude/contexts/ Directory

| Document | Purpose | Primary Audience |
|----------|---------|------------------|
| **dev.md** | Development context configuration | Developer |
| **review.md** | Review context configuration | Reviewer |
| **content.md** | Content context configuration | Content creator |

### archive/FOR_CHRIS_docs/ Directory (Learning Repository)

| Document | Purpose | Primary Audience | Links |
|----------|---------|------------------|-------|
| **[[archive/FOR_CHRIS_docs/README.md]]** | Index of educational docs | Christopher, Sage | → [[.claude/templates/for-chris-doc-template.md]] |
| **[[archive/FOR_CHRIS_docs/agent-orchestration-comparison.md]]** | Agent system design decisions | Christopher | → [[docs/reference/LEARNINGS.md]], [[.claude/agents/AGENTS.md]] |
| **[[archive/FOR_CHRIS_docs/github-project-setup.md]]** | GitHub Projects integration | Christopher | → [[docs/guides/PROJECT_BOARD_GUIDE.md]] |
| **[topic].md** | Topic-specific educational narratives | Christopher | ← [[.claude/agents/sage.md]] |

### .claude/templates/ Directory

| Document | Purpose | Primary Audience | Links |
|----------|---------|------------------|-------|
| **[[.claude/templates/for-chris-doc-template.md]]** | Template for FOR_CHRIS docs | Sage | → [[archive/FOR_CHRIS_docs/]] |

---

## Documentation Lifecycle

### Living Documents (Always Current)

These documents reflect the current state and should be updated continuously:

- **[[CLAUDE.md]]** - Project context
- **[[docs/README.md]]** - Documentation index + tagging
- **[[docs/reference/ARCHITECTURE.md]]** - System design
- **[[docs/reference/PROJECT_STRUCTURE.md]]** - File organization
- **[[docs/standards/DESIGN_PRINCIPLES.md]]** - UI/UX standards
- **[[docs/standards/CONTENT_STANDARDS.md]]** - Content guidelines
- **[[docs/standards/TESTING.md]]** - Testing framework
- **[[.claude/agents/AGENTS.md]]** - Agent guide

**Update trigger**: Any relevant code change

### Version Documents (Per-Release)

These documents are created for each version and archived:

- `temp/v[X.Y]_PLAN.md` - Build plan
- `temp/v[X.Y]_TESTING.md` - Test results
- `temp/v[X.Y]_NOTES.md` - Build notes

**Lifecycle**: Created in `temp/` → Deployed → Archived in `archive/v[X.Y]/`

### Reference Documents (Occasional Updates)

These documents change less frequently:

- **[[docs/reference/ROADMAP.md]]** - Phase planning
- **[[docs/guides/PROJECT_BOARD_GUIDE.md]]** - GitHub usage
- **[[docs/guides/PROJECT_WORKFLOW.md]]** - Epic → TDD → Task pattern
- **[[.claude/rules/]]** - Standards
- **[[.claude/skills/]]** - Workflows

**Update trigger**: New patterns, process changes, phase completion

---

## Cross-Reference Map

Shows which documents reference each other. Use for impact analysis when updating.

```
CLAUDE.md
  -> docs/README.md
  -> docs/reference/ARCHITECTURE.md
  -> docs/reference/PROJECT_STRUCTURE.md
  -> .claude/agents/AGENTS.md
  -> .claude/agents/README.md
  -> .claude/skills/*.md
  -> .claude/rules/*.md
  -> docs/standards/WORKFLOW_EXCEPTIONS.md

.claude/agents/AGENTS.md
  -> CLAUDE.md
  -> .claude/agents/README.md
  -> .claude/skills/*.md
  -> .claude/rules/*.md
  -> docs/guides/PROJECT_BOARD_GUIDE.md
  -> docs/guides/PROJECT_WORKFLOW.md
  -> docs/reference/LEARNINGS.md

docs/README.md
  -> DOC_TAGS_MANIFEST.md
  -> docs/guides/*.md
  -> docs/standards/*.md
  -> docs/reference/*.md

docs/guides/PROJECT_WORKFLOW.md
  -> docs/reference/PROJECT_STRUCTURE.md
  -> docs/reference/ARCHITECTURE.md
  -> docs/guides/CLAUDE_TASK_INTEGRATION.md
  -> docs/guides/PROJECT_BOARD_GUIDE.md
  -> .claude/agents/AGENTS.md

docs/reference/ARCHITECTURE.md
  -> docs/reference/PROJECT_STRUCTURE.md
  -> docs/standards/DESIGN_PRINCIPLES.md

docs/reference/PROJECT_STRUCTURE.md
  -> CLAUDE.md
  -> docs/reference/ARCHITECTURE.md

docs/standards/TESTING.md
  -> .claude/skills/tdd-workflow.md
  -> .claude/skills/verification-loop.md
  -> .claude/rules/testing.md

docs/guides/PROJECT_BOARD_GUIDE.md
  -> docs/reference/ROADMAP.md
  -> docs/guides/CLAUDE_TASK_INTEGRATION.md
  -> docs/specs/
```

---

## Finding Information

### By Keyword

| Looking For | Document |
|-------------|----------|
| **JLPT levels** | [[docs/standards/CONTENT_STANDARDS.md]], [[.claude/rules/japanese-content.md]] |
| **Furigana** | [[docs/standards/CONTENT_STANDARDS.md#furigana-standards]] |
| **localStorage** | [[docs/reference/ARCHITECTURE.md]], [[.claude/rules/security.md]] |
| **CSS variables** | [[docs/standards/DESIGN_PRINCIPLES.md#color-palette]] |
| **Semantic versioning** | [[CLAUDE.md#versioning-strategy]], [[.claude/rules/git-workflow.md]] |
| **SM-2 algorithm** | [[docs/specs/PRD-001-JLPT-Mastery-Engine.md]], [[docs/tdd/TDD-001-JLPT-Mastery-Engine.md]] |
| **Mastery stages** | [[docs/reference/ROADMAP.md#sprint-3-mastery-tracking-system]], [[docs/tdd/TDD-001-JLPT-Mastery-Engine.md]] |
| **Streaks** | [[docs/reference/ROADMAP.md#sprint-4-streak-system-mvp]] |
| **Agent handoff** | [[.claude/agents/AGENTS.md#agent-handoff-best-practices]] |
| **Persona prefixes** | [[.claude/agents/README.md]] |
| **Code review** | [[.claude/skills/code-review-workflow.md]] |
| **Deployment** | [[.claude/skills/deployment-workflow.md]] |
| **Epic → TDD → Task** | [[docs/guides/PROJECT_WORKFLOW.md]] |
| **YAML tagging** | [[docs/README.md]], [[docs/DOC_TAGS_MANIFEST.md]] |
| **Token budgets** | [[docs/DOC_TAGS_MANIFEST.md#context-window-budget-guidelines]] |
| **Smart loading** | [[docs/README.md#smart-loading-patterns]], [[docs/DOC_TAGS_MANIFEST.md#agent-loading-strategies]] |
| **Learning patterns** | [[docs/reference/LEARNINGS.md]], [[archive/FOR_CHRIS_docs/]] |
| **Sage persona** | [[.claude/agents/sage.md]] |
| **FOR_CHRIS docs** | [[archive/FOR_CHRIS_docs/README.md]] |
| **Pattern extraction** | [[.claude/skills/continuous-learning.md]] |
| **Learning curation** | [[.claude/skills/learning-curation.md]] |

### By Question

| Question | Answer Location |
|----------|-----------------|
| "What's the current project status?" | [[CLAUDE.md#current-development-phase]] |
| "Where should I put new files?" | [[docs/reference/PROJECT_STRUCTURE.md]] |
| "What code style should I use?" | [[.claude/rules/coding-style.md]] |
| "How do I create a new page?" | [[.claude/skills/topic-page-creation.md]] |
| "What agent should I use?" | [[.claude/agents/AGENTS.md#agent-selection-guide]] |
| "How do I track my task?" | [[docs/guides/PROJECT_BOARD_GUIDE.md]] |
| "What's planned for v0.4?" | [[docs/reference/ROADMAP.md#phase-2-engagement-layer-v04]] |
| "How do I create a TDD?" | [[docs/guides/PROJECT_WORKFLOW.md]], [[docs/tdd/TDD-001-JLPT-Mastery-Engine.md]] (example) |
| "What docs should I load for my persona?" | [[docs/README.md#smart-loading-patterns]] |
| "How do I organize documentation?" | [[docs/README.md]], [[docs/reference/PROJECT_STRUCTURE.md]] |
| "What's the Epic → TDD → Task pattern?" | [[docs/guides/PROJECT_WORKFLOW.md]] |
| "How do I extract learnings from a session?" | [[.claude/skills/learning-curation.md]] |
| "When should I create a FOR_CHRIS doc?" | [[.claude/agents/sage.md#decision-framework]], [[archive/FOR_CHRIS_docs/README.md]] |
| "Where do I document patterns?" | [[docs/reference/LEARNINGS.md]] |
| "How do I invoke Sage?" | [[.claude/agents/sage.md]], [[.claude/agents/README.md]] |

---

## Maintenance Responsibility

| Document Area | Primary Maintainer | Update Frequency |
|---------------|-------------------|------------------|
| [[CLAUDE.md]] | Documenter | Each version |
| [[docs/README.md]] | Documenter | When docs/ structure changes |
| [[docs/guides/]] | PM / Architect | When workflows change |
| [[docs/standards/]] | Architect / Sensei | When standards change |
| [[docs/reference/]] | Architect | When architecture/roadmap changes |
| [[.claude/agents/]] | Documenter | When agent system changes |
| [[.claude/skills/]] | Relevant persona | When workflow changes |
| [[.claude/rules/]] | Architect | When standards change |
| [[docs/specs/]] | PM | When requirements change |
| [[docs/tdd/]] | Architect | When designs change |
| [[docs/reference/LEARNINGS.md]] | Sage | When patterns proven ≥2 times |
| [[archive/FOR_CHRIS_docs/]] | Sage | When decision rubric met (≥2 criteria) |
| [[.claude/skills/learned-pattern-*.md]] | Sage | When actionable patterns identified |

---

## Navigation Tips

### For New Agents
1. Start with **[[CLAUDE.md]]** (auto-loaded)
2. Check **[[.claude/agents/AGENTS.md]]** for orchestration guide
3. Review **[[docs/README.md]]** for documentation organization
4. Load docs based on your **[[docs/README.md#smart-loading-patterns]]** persona pattern

### For Christopher
1. **[[CLAUDE.md]]** - Check current project state
2. **[[docs/reference/LEARNINGS.md]]** - Technical patterns and learnings
3. **[[docs/guides/PROJECT_BOARD_GUIDE.md]]** - Active tasks
4. **[[docs/reference/ROADMAP.md]]** - Product roadmap

### For Documentation Updates
1. Check **[[docs/reference/PROJECT_STRUCTURE.md]]** for file locations
2. Update living documents immediately
3. Reference **[[docs/README.md]]** for organization
4. Add YAML frontmatter per **[[docs/DOC_TAGS_MANIFEST.md]]**
5. Update cross-references in this file

---

*This index should be updated whenever new documentation is added or documentation structure changes.*

**Last major update**: 2026-01-25 (docs/ reorganization + YAML tagging system)
