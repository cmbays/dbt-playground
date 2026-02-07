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
│     - Create TDD in docs/specs/                               │
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
│  4.5. CODERABBIT AI (auto:)  ◄─ PRE-REVIEW GATE            │
│       - Pattern detection & quality analysis                │
│       - Security scanning                                   │
│       - Test coverage gaps                                  │
│       - dbt-specific checks                                 │
│       → Saves findings to CODERABBIT_REVIEW.md              │
│       → Dev iterates on findings before human review        │
├─────────────────────────────────────────────────────────────┤
│  5. REVIEWERS (review: + design:)                           │
│     - Code quality review (architecture focus)              │
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
- After implementation (before CodeRabbit review)
- After CodeRabbit review (developer iterates, then manual review)
- After manual reviews (before documentation)

## CodeRabbit Pre-Review Gate (Phase 4.5)

After implementation is complete and tests pass, CodeRabbit AI automatically runs before manual reviews.

### What CodeRabbit Checks

- **Patterns & Anti-patterns**: Detects common code smells, violations of dbt conventions
- **Test Coverage**: Identifies gaps in test coverage
- **Security Issues**: Scans for potential vulnerabilities, injection risks
- **dbt-Specific**: Model naming, documentation completeness, testing best practices
- **Performance**: Queries that could be optimized, unnecessary complexity

### Developer Iteration Loop

```
1. Developer completes implementation
   └─ All tests pass locally

2. Orchestrate triggers CodeRabbit (automatic)
   └─ Findings saved to CODERABBIT_REVIEW.md

3. Developer reviews findings
   └─ Iterates on code (patterns, tests, security)
   └─ Re-runs local tests
   └─ Can re-trigger CodeRabbit if desired

4. Developer signals readiness
   └─ Proceeds to manual review phase (review: + design:)

5. Manual reviewers focus on
   └─ Architecture & design decisions
   └─ Business logic & requirements
   └─ PR strategy & modularity
```

### Opting Out

CodeRabbit can be disabled for specific features:

```
/orchestrate --skip-coderabbit Add quick hotfix to production
```

This is only recommended for truly urgent fixes that will be cleaned up in follow-up PRs.

## Skip Options

For smaller tasks, phases can be skipped:

```
/orchestrate --skip-prd Add order status filter to marts
/orchestrate --skip-coderabbit Quick production hotfix
/orchestrate --dev-only Fix null handling in dim_customers
```

## Artifact Locations

| Phase | Output Location |
|-------|-----------------|
| PRD | `docs/specs/PRD-*.md` |
| TDD | `docs/specs/TDD-*.md` |
| Test Spec | `temp/v*_TESTING.md` |
| Implementation | `temp/` then final location |
| CodeRabbit Review | `temp/AGENT_REPORTS/[feature]/CODERABBIT_REVIEW.md` |
| Manual Reviews | `temp/AGENT_REPORTS/[feature]/CODE_REVIEW.md` |
| Changelog | `CHANGELOG.md` |

## Persona Integration

Orchestrate coordinates all personas according to the assembly line defined in CLAUDE.md's Agent Orchestration System section.
