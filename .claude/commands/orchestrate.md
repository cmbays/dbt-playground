# Orchestrate Command

Execute multi-persona workflow for feature development.

## Usage

```
/orchestrate [feature request or issue]
```

## Example

```
/orchestrate Add customer analytics mart with order metrics
```

## Assembly Line Workflow

This command initiates a sequential persona chain:

```
┌─────────────────────────────────────────────────────────────┐
│  1. PRODUCT MANAGER (pm:)                                   │
│     - Clarify requirements                                  │
│     - Create PRD in docs/specs/                             │
│     - Define acceptance criteria                            │
├─────────────────────────────────────────────────────────────┤
│  2. TECHNICAL ARCHITECT (arch:)                             │
│     - Design system architecture                            │
│     - Create TDD in docs/tdd/                               │
│     - Identify implementation approach                      │
│     - Consult data-modeler: for dimensional modeling needs  │
├─────────────────────────────────────────────────────────────┤
│  3. QUALITY TESTER (test:)                                  │
│     - Write test specification                              │
│     - Define verification criteria                          │
│     - Create temp/v*_TESTING.md                             │
├─────────────────────────────────────────────────────────────┤
│  4. FEATURE DEVELOPER (dev:)                                │
│     - Implement per TDD                                     │
│     - Work in temp/ first                                   │
│     - Verify tests pass                                     │
├─────────────────────────────────────────────────────────────┤
│  5. REVIEWERS (review: + design:)                           │
│     - Code quality review                                   │
│     - Design/UX review                                      │
│     - Can run in parallel                                   │
├─────────────────────────────────────────────────────────────┤
│  6. DOCUMENTER (docs:)                                      │
│     - Update CHANGELOG                                      │
│     - Update living documentation                           │
│     - Archive version artifacts                             │
└─────────────────────────────────────────────────────────────┘
```

## Handoff Protocol

At each stage transition, output:

1. **Summary**: What was completed
2. **Artifacts**: Files created/modified
3. **Open Questions**: Unresolved items
4. **Next Persona**: Recommended handoff
5. **Blockers**: Issues preventing progress

## Checkpoint Approvals

The workflow pauses for user approval at:

- After PRD (before architecture)
- After TDD (before implementation)
- After implementation (before reviews)
- After reviews (before documentation)

## Skip Options

For smaller tasks, phases can be skipped:

```
/orchestrate --skip-prd Add order status filter to marts
/orchestrate --dev-only Fix null handling in dim_customers
```

## Artifact Locations

| Phase | Output Location |
|-------|-----------------|
| PRD | `docs/specs/PRD-*.md` |
| TDD | `docs/tdd/TDD-*.md` |
| Test Spec | `temp/v*_TESTING.md` |
| Implementation | `temp/` then final location |
| Reviews | `docs/reviews/` or inline |
| Changelog | `CHANGELOG.md` |

## Persona Integration

Orchestrate coordinates all personas according to the assembly line defined in CLAUDE.md's Agent Orchestration System section.
