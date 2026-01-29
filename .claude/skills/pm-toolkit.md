# PM Toolkit Skill

## Trigger

Activate when:
- Comparing features for prioritization
- Writing PRD success metrics or acceptance criteria
- Scope questions arise during development
- Creating GitHub issues

## Quick Prioritization Score

Score each criterion 1-3, then sum:

| Criterion | 1 (Low) | 2 (Medium) | 3 (High) |
|-----------|---------|------------|-----------|
| **Learning Science** | Nice-to-have | Supports retention | Proven technique (SRS, active recall) |
| **Engagement** | Minimal interaction | Moderate use | Daily driver feature |
| **Effort** | Week+ of work | Days | Hours |
| **Foundation** | Standalone feature | Enables 1-2 others | Enables 3+ features |

**Interpretation:**
- **8-12**: Build now (current phase)
- **5-7**: Next phase
- **< 5**: Backlog / revisit later

## Feature Hypothesis Format

Use in PRD Success Metrics sections:

```
We believe [feature] will [expected outcome]
because [learning science rationale].
We'll know this works when [observable result].
```

**Example:**
```
We believe SRS-based review scheduling will improve kanji retention
because spaced repetition is proven to strengthen long-term memory.
We'll know this works when users return to review sessions daily.
```

## Scope Creep Guard

Before adding work to the current task, check:

1. **Is it in the PRD/issue?** → If no, stop. Create a new issue instead.
2. **Does current work break without it?** → If no, defer to next phase.
3. **Can it be added later without rework?** → If yes, defer.

If all three say "add it now", update the PRD scope section before proceeding.

## Definition of Done

Project-specific checklist for any feature:

- [ ] Acceptance criteria from PRD/issue met
- [ ] localStorage works (if applicable)
- [ ] Mobile responsive (320px+)
- [ ] Integrates with existing systems (SRS/mastery/XP if relevant)
- [ ] No regression in existing features
- [ ] Living docs updated (ARCHITECTURE.md, PROJECT_STRUCTURE.md)
- [ ] Follows shared.css / shared.js patterns
- [ ] GitHub issue created with labels
- [ ] JLPT level considerations included

## GitHub Issue Template

```markdown
## Problem Statement
What problem does this solve?

## User Benefit
How does this help learners?

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Scope
In scope:
- Item 1

Out of scope:
- Item 1

## Related
- PRD: docs/specs/PRD-xxx.md
- Related issues: #xx
```

## Issue Labels Reference

**Persona**: `persona:pm`, `persona:dev`, `persona:tester`
**Status**: `status:prd`, `status:tdd`, `status:in-dev`, `status:review`
**Type**: `type:feature`, `type:bug`, `type:docs`

## Anti-Patterns

- **Don't create scoring scripts** — the Quick Prioritization Score is a 30-second mental exercise, not a spreadsheet
- **Don't add frameworks beyond the quick score** — RICE, MoSCoW, etc. are overkill for ~20 planned features
- **Don't track unmeasurable metrics** — no analytics exist yet; use observable behavior instead
- **Don't create multiple PRD templates** — one template in `docs/specs/PRD-TEMPLATE.md` is sufficient
- **Don't build stakeholder maps** — solo developer project
