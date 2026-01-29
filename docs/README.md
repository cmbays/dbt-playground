---
audience: [multi-agent]
priority: high
size: small
dependencies: []
last_updated: 2026-01-28
status: active
tags: [overview, navigation, index]
---

# Documentation Index

**Purpose**: Central navigation for all project documentation

**Last Updated**: 2026-01-25

---

## Quick Navigation

### 📖 Guides (How-To Workflows)
Operational workflows for feature development and coordination.

- **[PROJECT_WORKFLOW.md](guides/PROJECT_WORKFLOW.md)** - Epic → TDD → Task pattern (all personas) [high priority, large]
- **[PROJECT_BOARD_GUIDE.md](guides/PROJECT_BOARD_GUIDE.md)** - GitHub project board usage (PM, Dev) [medium priority]
- **[CLAUDE_TASK_INTEGRATION.md](guides/CLAUDE_TASK_INTEGRATION.md)** - Claude task primitives for cross-session work (PM, Arch) [medium priority]

### 📏 Standards (Rules & Conventions)
Standards all code and content must follow.

- **[TESTING.md](standards/TESTING.md)** - Testing requirements and TDD approach (Tester, Dev) [high priority, small]
- **[CONTENT_STANDARDS.md](standards/CONTENT_STANDARDS.md)** - Japanese content guidelines (Sensei, Dev) [medium priority]
- **[DESIGN_PRINCIPLES.md](standards/DESIGN_PRINCIPLES.md)** - UI/UX standards (Design, Dev) [medium priority]
- **[WORKFLOW_EXCEPTIONS.md](standards/WORKFLOW_EXCEPTIONS.md)** - Approved workflow deviations [low priority, small]

### 📚 Reference (Technical Documentation)
Technical references for system design and architecture.

- **[ARCHITECTURE.md](reference/ARCHITECTURE.md)** - System architecture and technical decisions (Arch, Dev) [high priority]
- **[PROJECT_STRUCTURE.md](reference/PROJECT_STRUCTURE.md)** - File organization and naming (all personas) [high priority]
- **[ROADMAP.md](reference/ROADMAP.md)** - Product roadmap and future plans (PM, Arch) [low priority, large]

### 📋 Specifications
- **[specs/](specs/)** - Product Requirements Documents (PRDs)
- **[tdd/](tdd/)** - Technical Design Documents (TDDs)

### 🗂️ Project Artifacts
- **[plans/](plans/)** - Implementation plans and design discussions
- **[reviews/](reviews/)** - Review artifacts and decisions

---

## Document Tags

All documentation includes YAML frontmatter with metadata tags for intelligent loading by agents. See [DOC_TAGS_MANIFEST.md](DOC_TAGS_MANIFEST.md) for complete tagging schema.

### Tag Schema

```yaml
---
audience: [pm, architect, developer, tester, design, sensei, multi-agent]
priority: high | medium | low
size: small | medium | large  # Token budget: <5K | 5-15K | >15K
dependencies: [other-doc-names]
last_updated: YYYY-MM-DD
status: active | draft | deprecated
tags: [workflow, technical, planning, etc]
---
```

### Smart Loading Patterns

**For Developers**:
```
Load: high priority docs + docs with audience:[developer, multi-agent]
Example: TESTING, ARCHITECTURE, PROJECT_STRUCTURE, relevant TDD sections
Skip: ROADMAP, CONTENT_STANDARDS (unless working on Japanese content)
```

**For PMs**:
```
Load: high priority docs + docs with audience:[pm, multi-agent]
Example: PROJECT_WORKFLOW, PROJECT_BOARD_GUIDE, relevant PRDs
Skip: ARCHITECTURE (unless planning technical work)
```

**For Architects**:
```
Load: high priority docs + technical references
Example: PROJECT_WORKFLOW, ARCHITECTURE, PROJECT_STRUCTURE, relevant PRDs/TDDs
Skip: PROJECT_BOARD_GUIDE (unless managing tasks)
```

---

## Documentation Guidelines

### When to Create New Docs

**Create a new guide when**:
- Establishing a repeatable workflow
- Documenting a multi-persona process
- Creating how-to instructions

**Create a new standard when**:
- Defining rules that code/content must follow
- Establishing conventions
- Setting quality bars

**Create a new reference doc when**:
- Documenting system architecture
- Defining technical specifications
- Creating lookup/reference material

### Document Maintenance

**Living Documents** (update frequently):
- guides/PROJECT_WORKFLOW.md
- reference/ARCHITECTURE.md
- reference/PROJECT_STRUCTURE.md
- standards/*.md

**Version Documents** (create new per version):
- specs/PRD-*.md
- tdd/TDD-*.md
- plans/*.md (in temp/ during active work)

### Cross-References

When referencing other docs:
- Use relative paths: `[ARCHITECTURE](../reference/ARCHITECTURE.md)`
- Link to specific sections: `[TDD-001 §3](../tdd/TDD-001.md#3-sm-2-algorithm-specification)`
- Update links when moving files

---

## Recent Changes

### 2026-01-25: Directory Reorganization + Tagging System
- **Reorganized** docs/ into guides/, standards/, reference/ subdirectories
- **Added** YAML frontmatter tags to all docs for smart agent loading
- **Created** DOC_TAGS_MANIFEST.md documenting tagging schema
- **Updated** cross-references to reflect new structure

### 2026-01-25: Workflow Optimization
- **Created** PROJECT_WORKFLOW.md documenting Epic → TDD → Task pattern
- **Updated** all PRD-001 tasks (#13-22) with TDD section references
- **Established** tagging system for context window management

---

## Related

- **[CLAUDE.md](../CLAUDE.md)** - Main project context for Claude Code
- **[.claude/agents/AGENTS.md](../.claude/agents/AGENTS.md)** - Agent orchestration guide
- **[DOC_TAGS_MANIFEST.md](DOC_TAGS_MANIFEST.md)** - Complete tagging schema reference

---

*This index is automatically maintained. Last updated by PM (Claude) on 2026-01-25.*
