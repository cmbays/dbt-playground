---
title: Workflow Stages
description: Canonical 5-stage workflow definition for Claude Code sessions
version: 1.0
last-updated: 2026-01-31
related:
  - CLAUDE.md
  - docs/reference/PROJECT_STRUCTURE.md
  - .claude/agents/supervisor.md
  - .claude/agents/AGENTS.md
tags: [workflow, reference, orchestration, stages]
---

**Purpose**: This document defines the canonical 5-stage workflow for Claude Code sessions in this project. All development work follows this structure, with the Supervisor agent enforcing quality gates at each transition.

**Key Insight**: The workflow stages represent a universal development lifecycle that maps to the agent assembly line. Each stage has clear entry/exit criteria and designated agent responsibilities.

---

## Table of Contents

1. [Overview](#overview)
2. [The Five Stages](#the-five-stages)
   - [UNDERSTAND](#1-understand)
   - [PLAN](#2-plan)
   - [BUILD](#3-build)
   - [VERIFY](#4-verify)
   - [DEPLOY](#5-deploy)
3. [Stage-to-Agent Mapping](#stage-to-agent-mapping)
4. [Quality Gates](#quality-gates)
5. [Common Pitfalls](#common-pitfalls)
6. [Workflow Exceptions](#workflow-exceptions)
7. [Related Documentation](#related-documentation)

---

## Overview

### The Universal Development Cycle

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  UNDERSTAND  │ →  │     PLAN     │ →  │    BUILD     │ →  │    VERIFY    │ →  │    DEPLOY    │
│              │    │              │    │              │    │              │    │              │
│  Context     │    │  Design      │    │  Implement   │    │  Test        │    │  Release     │
│  Gathering   │    │  Approval    │    │  Execute     │    │  Validate    │    │  Document    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### Why Five Stages?

- **UNDERSTAND**: Prevents building the wrong thing
- **PLAN**: Prevents over-engineering and scope creep
- **BUILD**: Focused implementation with test coverage
- **VERIFY**: Catches issues before release
- **DEPLOY**: Ensures knowledge transfer and documentation

### Stage Enforcement

The Supervisor agent (`super:`) enforces quality gates between stages. Transitions are blocked if required artifacts are missing. See [Quality Gates](#quality-gates) for details.

---

## The Five Stages

### 1. UNDERSTAND

**Purpose**: Gather context, clarify requirements, and align on scope before any design or implementation work begins.

#### Entry Criteria

- User request or GitHub issue received
- Session context available (new or resumed)

#### Activities

| Activity | Tool/Method | Output |
|----------|-------------|--------|
| Read project context | `CLAUDE.md`, architecture docs | Mental model |
| Understand existing patterns | `Grep`, `Glob`, `Read` | Codebase familiarity |
| Clarify requirements | `AskUserQuestion` | Clear acceptance criteria |
| Check for blockers | `temp/WORKFLOW_STATE.md` | Dependency awareness |
| Review related PRDs | `docs/specs/PRD-*.md` | Context from prior work |

#### Exit Criteria

- [ ] Understand what needs to be built
- [ ] Know which files/systems will be affected
- [ ] Clear on acceptance criteria
- [ ] No fundamental questions outstanding

#### Responsible Agents

| Agent | Role in UNDERSTAND |
|-------|-------------------|
| **Supervisor** | Interface layer, clarifying questions |
| **Explore** | Codebase research, pattern discovery |
| **Healthcare Analyst** | Domain context (if healthcare-related) |

#### Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Jumping straight to code | ALWAYS read existing code first |
| Assuming requirements | ASK clarifying questions |
| Missing existing patterns | Use Explore agent for non-trivial research |
| Ignoring related work | Check `docs/specs/` for related PRDs/TDDs |

---

### 2. PLAN

**Purpose**: Design the solution, create artifacts, and get approval before implementation.

#### Entry Criteria

- UNDERSTAND stage complete
- Requirements clarified
- No blocking questions

#### Activities

| Activity | Tool/Method | Output |
|----------|-------------|--------|
| Create PRD (if needed) | PM persona | `docs/specs/PRD-XXX.md` |
| Create TDD | Architect persona | `docs/specs/TDD-XXX.md` |
| Design architecture | `/plan`, diagrams | Architecture decisions |
| Create plan file | Write | `temp/v[X.Y]_PLAN.md` |
| Get user approval | Present plan | Go/No-Go decision |
| Create feature branch | git-master | `feat/feature-name` |

#### Exit Criteria

- [ ] Plan file created (`temp/v[X.Y]_PLAN.md`)
- [ ] User approval received
- [ ] TDD created (for non-trivial work)
- [ ] Feature branch created (not on main)
- [ ] Draft PR created (for visibility)

#### Responsible Agents

| Agent | Role in PLAN |
|-------|-------------|
| **Supervisor** | Orchestrates planning, determines skip flags |
| **PM** | Creates PRD, defines scope |
| **Architect** | Creates TDD, designs system |
| **Data Modeler** | Dimensional model design (dbt) |
| **git-master** | Branch creation |

#### Artifacts Produced

```
docs/specs/PRD-XXX.md        # Product requirements (PM)
docs/specs/TDD-XXX.md        # Technical design (Architect)
temp/v[X.Y]_PLAN.md          # Implementation plan
temp/AGENT_REPORTS/[feature]/
├── PM_REPORT.md             # PM scope decisions
└── ARCH_REPORT.md           # Architect design notes
```

#### Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Over-engineering | Keep solutions simple; solve today's problem |
| Analysis paralysis | Time-box planning; ship incrementally |
| Skipping approval | ALWAYS get user sign-off on non-trivial plans |
| Working on main | Create feature branch BEFORE implementation |

---

### 3. BUILD

**Purpose**: Implement the solution following the approved plan with test coverage.

#### Entry Criteria

- PLAN stage complete with approval
- Feature branch created (verified by Supervisor)
- TDD/plan available for reference

#### Activities

| Activity | Tool/Method | Output |
|----------|-------------|--------|
| Write tests first (TDD) | dbt-tester, tdd-guide | Test files |
| Implement code | Developer agents | Source files |
| Write as you go | Edit, Write | Incremental progress |
| Local validation | `dbt build`, `dbt test` | Passing tests |
| Commit incrementally | git-master `/commit` | Atomic commits |

#### Exit Criteria

- [ ] All planned features implemented
- [ ] Tests written and passing locally
- [ ] Code follows project patterns
- [ ] No obvious bugs or issues
- [ ] DEV_REPORT.md written (tracked features)

#### Responsible Agents

| Agent | Role in BUILD |
|-------|--------------|
| **Developer** | Primary implementation |
| **dbt Developer** | SQL models, Jinja macros |
| **dbt Tester** | Data tests, schema tests |
| **TDD Guide** | Test-first enforcement |
| **git-master** | Commits, branch management |

#### Artifacts Produced

```
models/[layer]/[model].sql   # Implementation files
models/[layer]/schema.yml    # Tests and documentation
temp/AGENT_REPORTS/[feature]/
├── TEST_SPEC.md             # Test plan (Tester)
└── DEV_REPORT.md            # Implementation notes (Developer)
```

#### Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Skipping tests | Write tests FIRST (TDD) |
| Gold-plating | Implement ONLY what's in the plan |
| Big-bang commits | Commit after each logical change |
| Ignoring failures | Fix failing tests before continuing |

---

### 4. VERIFY

**Purpose**: Validate the implementation through testing, review, and quality checks.

#### Entry Criteria

- BUILD stage complete
- Local tests passing
- Implementation ready for review

#### Activities

| Activity | Tool/Method | Output |
|----------|-------------|--------|
| Run full test suite | `dbt build`, `dbt test` | Test results |
| Document test results | Write | `temp/v[X.Y]_TESTING.md` |
| Code review | Code Reviewer | CODE_REVIEW.md |
| Security review | Security Reviewer | SECURITY_REVIEW.md |
| PR review feedback | GitHub PR | Comments/Approvals |

#### Exit Criteria

- [ ] All dbt tests pass
- [ ] Testing documentation complete
- [ ] Code review approved (2+ approvals)
- [ ] No unresolved blocking comments
- [ ] CI checks passing

#### Responsible Agents

| Agent | Role in VERIFY |
|-------|---------------|
| **Supervisor** | Review orchestration, approval tracking |
| **Code Reviewer** | Quality, patterns, bugs |
| **Security Reviewer** | Security vulnerabilities |
| **Design Reviewer** | UI/UX (if applicable) |
| **dbt Tester** | Final test validation |

#### Artifacts Produced

```
temp/v[X.Y]_TESTING.md                    # Test documentation
temp/AGENT_REPORTS/[feature]/
├── CODE_REVIEW.md                        # Review findings
└── SECURITY_REVIEW.md                    # Security assessment
```

#### Quality Gates (Supervisor Enforced)

| Check | Requirement |
|-------|-------------|
| Test pass | `dbt build` succeeds |
| Review approvals | 2+ approvals on PR |
| No blockers | No unresolved `(blocking)` comments |
| CHANGELOG | Updated for feat/fix PRs |
| CI status | All checks passing |

#### Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Skipping review | Code review is ALWAYS required |
| Ignoring warnings | Address all feedback, even "nits" |
| Partial testing | Test the full affected DAG |
| Merging with failures | NEVER merge with failing tests |

---

### 5. DEPLOY

**Purpose**: Release the feature, document learnings, and update project knowledge.

#### Entry Criteria

- VERIFY stage complete
- All approvals received
- CHANGELOG updated

#### Activities

| Activity | Tool/Method | Output |
|----------|-------------|--------|
| Final approval | Supervisor checklist | Merge authorization |
| Merge to main | git-master | Merged PR |
| Update documentation | Documenter | Living docs |
| Extract learnings | Sage | LEARNINGS.md updates |
| Tag version (if applicable) | git-master | Version tag |
| Update WORKFLOW_STATE | Supervisor | Track completed |

#### Exit Criteria

- [ ] PR merged to main
- [ ] Documentation updated
- [ ] CHANGELOG reflects changes
- [ ] Learnings extracted (if applicable)
- [ ] Track marked complete in WORKFLOW_STATE.md

#### Responsible Agents

| Agent | Role in DEPLOY |
|-------|---------------|
| **Supervisor** | Final approval gate, state update |
| **git-master** | Merge, tag operations |
| **Documenter** | Documentation updates |
| **Sage** | Learning extraction |
| **PM** | Issue closure, roadmap update |
| **Changelog Generator** | Automated changelog entries |

#### Artifacts Produced

```
CHANGELOG.md                  # Version history (updated)
docs/reference/LEARNINGS.md   # Patterns and decisions
temp/SESSION_SUMMARY_*.md     # Session documentation
```

#### Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Skipping docs | Documentation is part of the feature |
| No learnings | Invoke Sage on both success and failure |
| Stale roadmap | Update project board status |
| Forgotten cleanup | Remove temp files, close issues |

---

## Stage-to-Agent Mapping

### Assembly Line Flow

```
                    UNDERSTAND           PLAN              BUILD              VERIFY             DEPLOY
                    ──────────────────────────────────────────────────────────────────────────────────────
Supervisor          │ Clarify        │ Orchestrate    │ Monitor        │ Review Queue    │ Final Gate    │
                    ▼                ▼                ▼                ▼                 ▼
PM                  │                │ PRD            │                │                 │ Close Issues  │
                    ▼                ▼                ▼                ▼                 ▼
Architect           │                │ TDD            │                │                 │               │
                    ▼                ▼                ▼                ▼                 ▼
Data Modeler        │                │ Model Design   │                │                 │               │
                    ▼                ▼                ▼                ▼                 ▼
Tester              │                │ Test Plan      │ Test First     │ Validate        │               │
                    ▼                ▼                ▼                ▼                 ▼
Developer           │                │                │ Implement      │                 │               │
                    ▼                ▼                ▼                ▼                 ▼
Code Reviewer       │                │                │                │ Review Code     │               │
                    ▼                ▼                ▼                ▼                 ▼
Security Reviewer   │                │                │                │ Security Audit  │               │
                    ▼                ▼                ▼                ▼                 ▼
Documenter          │                │                │                │                 │ Update Docs   │
                    ▼                ▼                ▼                ▼                 ▼
Sage                │ Context Load   │                │                │                 │ Learn Extract │
                    ▼                ▼                ▼                ▼                 ▼
git-master          │                │ Branch Create  │ Commits        │                 │ Merge & Tag   │
```

### Agent Categories

| Category | Agents | Primary Stages |
|----------|--------|----------------|
| **Orchestration** | Supervisor | All stages (meta-orchestrator) |
| **Planning** | PM, Architect, Data Modeler | PLAN |
| **Implementation** | Developer, dbt Developer | BUILD |
| **Quality** | Tester, Code Reviewer, Security Reviewer | BUILD, VERIFY |
| **Documentation** | Documenter, Sage, Changelog Generator | DEPLOY |
| **Services** | git-master | All (horizontal service) |
| **Domain** | Healthcare Analyst | UNDERSTAND, PLAN |

---

## Quality Gates

The Supervisor enforces quality gates at each stage transition. Transitions are **blocked** if required artifacts are missing.

### Transition Matrix

| From | To | Required Artifacts | Verification |
|------|----|-------------------|--------------|
| START | UNDERSTAND | None | User request clarified |
| UNDERSTAND | PLAN | Clear requirements | No blocking questions |
| PLAN | BUILD | PRD/TDD (if required), Plan approval, Feature branch | `git branch != main` |
| BUILD | VERIFY | Implementation complete, Tests passing | `dbt build` succeeds |
| VERIFY | DEPLOY | 2+ approvals, No blockers, CHANGELOG updated | Supervisor checklist |
| DEPLOY | COMPLETE | PR merged, Docs updated | Track archived |

### Gate Verification Process

```
[Request Transition: BUILD → VERIFY]
    │
    ├─ 1. Check implementation complete
    │      Verify files in expected locations
    │
    ├─ 2. Run test suite
    │      Command: dbt build --select +model_name
    │      Expected: 0 failures
    │
    ├─ 3. Verify DEV_REPORT.md exists
    │      Path: temp/AGENT_REPORTS/[feature]/DEV_REPORT.md
    │
    └─ 4. Decision:
         ├─ All pass → Update WORKFLOW_STATE.md → Proceed to VERIFY
         └─ Any fail → BLOCK → Report specific failures
```

### WORKFLOW_STATE.md Integration

The Supervisor maintains `temp/WORKFLOW_STATE.md` to track stage progression:

```yaml
---
last_updated: 2026-01-31T14:30:00
active_track: feat/customer-analytics
---

## Active Tracks

### Track: feat/customer-analytics (ACTIVE)
- **Stage**: VERIFY
- **Phase**: Code Review
- **Artifacts**:
  - [x] PRD: docs/specs/PRD-004-customer-analytics.md
  - [x] TDD: docs/specs/TDD-004-customer-analytics.md
  - [x] Plan: temp/v0.7_PLAN.md
  - [x] DEV_REPORT: temp/AGENT_REPORTS/customer-analytics/DEV_REPORT.md
  - [ ] CODE_REVIEW: (pending)
- **Blockers**: None
```

---

## Common Pitfalls

### Stage-Level Pitfalls Summary

| Stage | Top Pitfalls | Prevention |
|-------|--------------|------------|
| **UNDERSTAND** | Jumping to code, assuming requirements | Read first, ask questions |
| **PLAN** | Over-engineering, analysis paralysis | Keep simple, time-box |
| **BUILD** | Skipping tests, gold-plating | TDD, stick to plan |
| **VERIFY** | Skipping review, merging with failures | Review required, all tests pass |
| **DEPLOY** | Skipping docs, no learning extraction | Docs are part of feature |

### Cross-Stage Pitfalls

| Pitfall | Stage | Impact | Prevention |
|---------|-------|--------|------------|
| Working on main branch | BUILD | Merge conflicts, blocked PRs | Create branch in PLAN |
| No draft PR | PLAN | Hidden work, no visibility | Create draft PR immediately |
| Scope creep mid-build | BUILD | Delays, over-engineering | Stick to approved plan |
| Insufficient context handoff | All | Agent confusion | Use inter-agent reports |
| Stale WORKFLOW_STATE | All | Session resume failures | Update after each transition |

---

## Workflow Exceptions

Not all work requires the full 5-stage workflow. The Supervisor determines appropriate skip flags.

### Skip Flags

| Flag | Skips | When to Use |
|------|-------|-------------|
| `--skip-prd` | PM phase | Scope already clear from issue |
| `--skip-tdd` | Architect phase | Minor change, obvious implementation |
| `--dev-only` | PM + Architect + Tester | Quick fix, straight to developer |
| `--parallel-review` | Sequential review | Enable parallel code + design review |

### Task Size Guidelines

| Task Size | Workflow | Stages Used |
|-----------|----------|-------------|
| **Trivial** | Manual | None (direct fix) |
| **Small** | `--dev-only` | BUILD → VERIFY |
| **Medium** | `--skip-prd` | UNDERSTAND → PLAN → BUILD → VERIFY → DEPLOY |
| **Large** | Full | All 5 stages |

### Approved Exceptions

Document workflow exceptions in `docs/standards/WORKFLOW_EXCEPTIONS.md` with:

- Reason for exception
- Risk assessment
- Approval

---

## Related Documentation

### Core References

| Document | Relationship |
|----------|--------------|
| [CLAUDE.md](../../CLAUDE.md) | Project context, workflow overview |
| [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) | File organization, development flow |
| [AGENTS.md](../../.claude/agents/AGENTS.md) | Agent orchestration, assembly lines |
| [supervisor.md](../../.claude/agents/supervisor.md) | Quality gates, state management |
| [architect.md](../../.claude/agents/architect.md) | PLAN stage design responsibilities |

### Workflow Standards

| Document | Topic |
|----------|-------|
| [git-workflow.md](../../.claude/rules/git-workflow.md) | Branch naming, commit conventions |
| [testing.md](../../.claude/rules/testing.md) | TDD workflow, test requirements |
| [WORKFLOW_EXCEPTIONS.md](../standards/WORKFLOW_EXCEPTIONS.md) | Approved deviations |

### Templates

| Template | Location |
|----------|----------|
| PM_REPORT | `docs/templates/agent-reports/PM_REPORT.md` |
| ARCH_REPORT | `docs/templates/agent-reports/ARCH_REPORT.md` |
| DEV_REPORT | `docs/templates/agent-reports/DEV_REPORT.md` |
| TEST_SPEC | `docs/templates/agent-reports/TEST_SPEC.md` |
| SESSION_SUMMARY | `docs/templates/agent-reports/SESSION_SUMMARY.md` |

---

*This is a living document. Update as workflow patterns evolve.*
