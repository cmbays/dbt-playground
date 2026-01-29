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
| _No documents yet_ | - | - |

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
