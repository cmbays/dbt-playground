---
audience: [sage, human]
priority: low
size: small
last_updated: 2026-01-28
status: active
tags: [learning, educational, narratives, index]
---

# FOR_CHRIS Educational Documents

**Purpose**: Topic-specific narratives explaining architectural decisions, learnings, and development patterns in an engaging, educational format.

**Audience**: Christopher (project owner) for learning and future reference.

**Maintenance**: Created by Sage persona when decision rubric is met.

---

## Decision Rubric

Create a FOR_CHRIS doc when ≥2 of these criteria are met:

1. **Architectural decision** - Major design choice with tradeoffs
2. **Novel pattern** - First-time use of a technique
3. **Workflow change** - Process modification
4. **Multiple approaches evaluated** - Options analysis worth preserving
5. **High educational value** - Explains "why" not just "what"

---

## Document Index

| Document | Topic | Date |
|----------|-------|------|
| [UNDERSTANDING_PR_WORKFLOW.md](UNDERSTANDING_PR_WORKFLOW.md) | PR-first development philosophy and defense-in-depth enforcement | 2026-01-30 |
| [PLAYGROUND-TOOLS.md](PLAYGROUND-TOOLS.md) | Interactive visual tools for learning | 2026-01-29 |
| [GIT-WORKTREE-WORKFLOW.md](GIT-WORKTREE-WORKFLOW.md) | Parallel development with git worktrees | 2026-01-29 |
| [SUPERVISOR_ORCHESTRATION.md](SUPERVISOR_ORCHESTRATION.md) | Meta-orchestration and multi-track workflows | 2026-01-29 |
| [UV_PYTHON_MODERNIZATION.md](UV_PYTHON_MODERNIZATION.md) | Python/uv dependency management for dbt | 2026-01-29 |
| [PROJECT_ONBOARDING.md](PROJECT_ONBOARDING.md) | Project setup, workflow, roadmap | 2026-01-29 |
| [KIMBALL_DIMENSIONAL_MODELING.md](KIMBALL_DIMENSIONAL_MODELING.md) | Dimensional modeling principles | 2026-01-28 |

---

## Document Format

Each FOR_CHRIS doc should:

- Tell a story (not just list facts)
- Explain the "why" behind decisions
- Include analogies for complex concepts
- Show tradeoffs considered
- Reference related technical docs

See `.claude/templates/for-chris-doc-template.md` for the template.

---

## Related

- `docs/reference/LEARNINGS.md` - Technical patterns (quick reference)
- `.claude/skills/learned-pattern-*.md` - Executable workflows
- `.claude/agents/sage.md` - Sage persona (creates these docs)
