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
- `PRD-001-vocabulary-quiz.md`
- `PRD-002-progress-tracking.md`
- `PRD-003-audio-playback.md`

## Template

Use `PRD-TEMPLATE.md` for new PRDs.

## PRD Index

| PRD | Title | Status | Epic Issue | Phase |
|-----|-------|--------|------------|-------|
| [PRD-001](PRD-001-JLPT-Mastery-Engine.md) | JLPT Mastery Learning Engine | Complete | [#7](https://github.com/cmbays/japanese-study-site/issues/7) | Phase 1 (v0.3) |
| [PRD-002](PRD-002-Study-Session-Experience.md) | Study Session Experience | Complete | [#8](https://github.com/cmbays/japanese-study-site/issues/8) | Phase 1 (v0.3) |
| [PRD-003](PRD-003-Habit-Formation-System.md) | Habit Formation System | Complete | [#9](https://github.com/cmbays/japanese-study-site/issues/9) | Phase 2 (v0.4) |
| [PRD-004](PRD-004-Claude-Task-GitHub-Integration.md) | Claude Task GitHub Integration | Complete | - | Phase 1 (v0.3) |
| [PRD-005](PRD-005-Progress-Dashboard.md) | Progress Dashboard | Complete | - | Phase 2 (v0.4) |
| [PRD-006](PRD-006-Backend-Infrastructure-Setup.md) | Backend Infrastructure Setup | Draft | - | Future |
| [PRD-007](PRD-007-Team-Optimizations.md) | Team Optimizations | In Development | - | v0.5 |

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
