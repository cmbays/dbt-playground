---
audience: [pm, architect]
priority: medium
size: small
last_updated: 2026-01-30
status: active
tags: [specs, prd, requirements, index]
---

# Product Requirement Documents (PRDs) and Technical Design Documents (TDDs)

This directory contains both Product Requirement Documents (PRDs) that define features before development, and Technical Design Documents (TDDs) that specify how features will be implemented.

## Purpose

**PRDs** capture the "what" and "why" of features:

- Problem being solved
- User benefit
- Acceptance criteria
- Scope boundaries

**TDDs** capture the "how" of features:

- Architecture decisions
- Component design
- Data structures
- Implementation sequence

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

| PRD | Title | Status | Version |
|-----|-------|--------|---------|
| PRD-001 | Environment Setup | Complete | v0.1 |
| PRD-002 | Data Acquisition | Complete | v0.2 |
| PRD-003 | Staging Layer | Complete | v0.3 |
| PRD-004 | Dimensional Models | Complete | v0.4 |
| PRD-005 | Marts Enhancements | Complete | v0.5 |
| PRD-014 | Playground Tools | Complete | v0.6 |
| PRD-016 | Agent Context Management | Approved | v0.7 |
| PRD-007 | Tuva Foundation | Draft | Future |
| PRD-008 | Clinical Marts | Draft | Future |
| PRD-009 | Claims Acquisition | Draft | Future |
| PRD-010 | Claims Connector | Draft | Future |
| PRD-011 | Financial Marts | Draft | Future |
| PRD-012 | Semantic Layer | Draft | Future |
| PRD-013 | Git Worktree Workflow | Complete | v0.6 |
| PRD-015 | Workflow Enhancement | Draft | Future |

## TDD Index

| TDD | Title | Status | PRD |
|-----|-------|--------|-----|
| TDD-001 | dbt Project Architecture | Complete | - |
| TDD-004 | Dimensional Models | Complete | PRD-004 |
| TDD-005 | Marts Enhancements | Complete | PRD-005 |
| TDD-007 | Tuva Foundation | Draft | PRD-007 |
| TDD-014 | Playground Tools | Complete | PRD-014 |
| TDD-016 | Agent Context Management | Complete | PRD-016 |

## Related

- [FUTURE_FEATURES.md](FUTURE_FEATURES.md) - Feature ideas backlog
- [TDD-TEMPLATE.md](TDD-TEMPLATE.md) - Technical Design Document template

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
