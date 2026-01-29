# Technical Design Documents (TDDs)

This directory contains Technical Design Documents that specify how features will be implemented.

## Purpose

TDDs translate PRDs into technical specifications:
- Architecture decisions
- Component design
- Data structures
- File changes
- Implementation sequence

TDDs answer "how" based on the PRD's "what" and "why".

## Naming Convention

```
TDD-[NUMBER]-[short-name].md
```

Examples:
- `TDD-001-vocabulary-quiz.md`
- `TDD-002-progress-tracking.md`
- `TDD-003-audio-playback.md`

Architecture diagrams use matching names:
```
TDD-001-vocabulary-quiz.d2
```

## Template

Use `TDD-TEMPLATE.md` for new TDDs.

## TDD Index

| TDD | Title | PRD | Status | Developer |
|-----|-------|-----|--------|-----------|
| _Example_ | _Vocabulary Quiz_ | _PRD-001_ | _In Progress_ | _— _ |

## Workflow

1. Architect receives approved PRD
2. Architect analyzes codebase patterns
3. Architect evaluates implementation options
4. Architect creates TDD with recommended approach
5. TDD reviewed and approved
6. Tester creates test specification from TDD
7. Developer implements from TDD

## Status Values

| Status | Meaning |
|--------|---------|
| Draft | Under design |
| Review | Ready for review |
| Approved | Ready for implementation |
| In Progress | Implementation started |
| Complete | Feature shipped |

## Architecture Diagrams

For complex features, include D2 diagrams:

```d2
# Example component diagram
user -> ui: interacts
ui -> state: updates
state -> storage: persists
```

Save as `TDD-XXX-name.d2` alongside the TDD.

## Option Analysis

When multiple approaches exist, TDDs include option analysis:

| Option | Pros | Cons | Complexity |
|--------|------|------|------------|
| A | ... | ... | Low |
| B | ... | ... | Medium |

With clear recommendation and rationale.

## Linking

- Link TDD to PRD: `Source PRD: PRD-XXX`
- Link TDD to issue: `Related Issue: #XX`
- Link to diagram: `Architecture: TDD-XXX.d2`
