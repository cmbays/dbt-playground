---
audience: [pm, architect]
priority: medium
size: small
last_updated: 2026-01-28
status: active
tags: [specs, prd, requirements, index]
---

# Product Requirement Documents (PRDs)

This directory contains Product Requirement Documents that define features before development begins.

## Purpose

PRDs capture the "what" and "why" of features:

- Problem being solved
- User benefit
- Acceptance criteria
- Scope boundaries

PRDs do NOT include technical implementation details (those go in TDDs).

## Naming Convention

```
PRD-[NUMBER]-[short-name].md
```

Examples:

- `PRD-001-sample-data-pipeline.md`
- `PRD-002-incremental-models.md`
- `PRD-003-data-quality-tests.md`

## Template

Use `PRD-TEMPLATE.md` for new PRDs.

## PRD Index

| PRD | Title | Status | Epic Issue | Phase |
|-----|-------|--------|------------|-------|
| - | _No PRDs yet_ | - | - | - |

## Related

- [FUTURE_FEATURES.md](FUTURE_FEATURES.md) - Feature ideas backlog
- [../tdd/](../tdd/) - Technical Design Documents

## Workflow

1. PM creates PRD from user requirements
2. PM creates linked GitHub issue
3. PRD reviewed and approved
4. Architect creates TDD from PRD
5. PRD status updated as feature progresses

## Status Values

| Status | Meaning |
|--------|---------|
| Draft | Initial creation, under discussion |
| Approved | Ready for technical design |
| In Development | TDD created, implementation started |
| Complete | Feature shipped |
| Cancelled | Not proceeding |

## Linking

- Link PRD to GitHub issue: `Related Issue: #XX`
- Link PRD to TDD: `Technical Design: TDD-XXX`
- Link in GitHub issue back to PRD: `PRD: docs/specs/PRD-XXX.md`
