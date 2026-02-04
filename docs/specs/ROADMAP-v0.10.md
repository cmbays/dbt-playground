# v0.10 Roadmap: Agent Orchestration Enhancements

**Milestone**: v0.10
**Target**: April 30, 2026
**Theme**: Agent Memory, Workflow Discipline, Quality Gates, and Observability

## Overview

v0.10 introduces comprehensive agent orchestration improvements enabling self-improving
workflows, strict quality enforcement, and full observability into agent performance.

**Planning Documents**: `temp/2026_02_01_Discussion/` (28 documents)

---

## Feature Sets Summary

| ID | Feature Set | Effort | Value | Priority |
|----|-------------|--------|-------|----------|
| FS1 | Agent Memory & Learning | 14-21h | 9/10 | P1 |
| FS2 | Kanban Workflow Engine | 16-24h | 9/10 | P1 |
| FS3 | QA & Testing Enforcement | 15-20h | 8/10 | P2 |
| FS5 | Metrics & Dashboard | 50-60h | 8/10 | P2 |
| FS7 | GitHub Integration | 15h | 7/10 | P2 |
| **Total** | | **110-140h** | | |

**Deferred to v1.0+**:

- FS6: Multi-Agent Coordination (40-60h) - depends on FS1-5
- FS8: Hackathon System (80-100h) - depends on FS1-7

---

## Phase Structure

### Phase A: Foundation (Weeks 1-2)

Build the memory and workflow discipline foundation.

#### FS1: Agent Memory & Learning System

**Goal**: Enable agents to learn from sessions and compound improvements.

| Task | Description | Est |
|------|-------------|-----|
| FS1.1 | Create `memory/` directory structure | 2h |
| FS1.2 | Implement daily append-only logs (`YYYY-MM-DD.md`) | 4h |
| FS1.3 | Add session-end learning trigger to Sage | 3h |
| FS1.4 | Create weekly consolidation workflow (Workflow K) | 4h |
| FS1.5 | Integrate with compound learning loop | 4h |

**Deliverables**:

- `memory/` directory with daily logs
- Sage Workflow J (session logging)
- Sage Workflow K (weekly consolidation)
- Updated CLAUDE.md documentation

#### FS2: Kanban Workflow Engine (Phase 1-2)

**Goal**: Enforce workflow discipline with per-ticket checklists.

| Task | Description | Est |
|------|-------------|-----|
| FS2.1 | Define per-ticket checklist JSON schema | 2h |
| FS2.2 | Extend Backlog.md YAML for checklist tracking | 3h |
| FS2.3 | Add WIP count tracking to WORKFLOW_STATE.md | 2h |
| FS2.4 | Implement transition guards in Supervisor | 4h |
| FS2.5 | Add skip detection and logging | 3h |
| FS2.6 | Integrate with Sage for learning extraction | 2h |

**Deliverables**:

- Per-ticket checklist in Backlog.md
- Transition guard enforcement
- Skip detection and audit logging

---

### Phase B: Quality & Observability (Weeks 3-5)

Add quality gates and visibility into workflow performance.

#### FS3: QA & Testing Enforcement

**Goal**: Make QA a mandatory gate, not optional step.

| Task | Description | Est |
|------|-------------|-----|
| FS3.1 | Create QA_REPORT.md template | 2h |
| FS3.2 | Define qa-reviewer persona in SOUL.md | 2h |
| FS3.3 | Update Supervisor phase gate for QA artifact | 3h |
| FS3.4 | Create `/qa` command | 3h |
| FS3.5 | Implement PostToolUse advisory hook | 4h |
| FS3.6 | Implement Stop hook validation | 3h |

**Deliverables**:

- QA_REPORT.md template
- qa-reviewer persona
- `/qa` command
- Advisory hooks for testing

#### FS5: Metrics & Dashboard System

**Goal**: Full visibility into workflow adherence and agent performance.

| Task | Description | Est |
|------|-------------|-----|
| FS5.1 | Design SQLite schema for metrics | 4h |
| FS5.2 | Implement event sync script | 6h |
| FS5.3 | Create adherence scoring formula | 4h |
| FS5.4 | Implement outcome metrics collection | 6h |
| FS5.5 | Build anomaly detection rules engine | 8h |
| FS5.6 | Extend Workflow Hub with metrics widgets | 12h |
| FS5.7 | Add agent activity tracking | 6h |
| FS5.8 | Integration testing and polish | 8h |

**Deliverables**:

- SQLite metrics database
- Adherence scoring
- Anomaly detection (8 rules)
- Workflow Hub metrics dashboard

#### FS7: GitHub Integration Enhancements

**Goal**: Better traceability and code ownership.

| Task | Description | Est |
|------|-------------|-----|
| FS7.1 | Create CODEOWNERS file | 2h |
| FS7.2 | Implement issue-ID task file naming | 3h |
| FS7.3 | Add PRD-to-Issue traceability metadata | 3h |
| FS7.4 | Create task file sync workflow | 4h |
| FS7.5 | Configure branch protection rules | 3h |

**Deliverables**:

- CODEOWNERS file
- Issue-ID task naming convention
- Task file sync workflow
- Branch protection configuration

---

## Dependency Graph

```
Phase A (Foundation)
    FS1: Memory ──────────┐
    FS2: Kanban P1-2 ─────┤
                          │
                          v
Phase B (Quality & Observability)
    FS3: QA ──────────────┤
    FS5: Metrics ─────────┤
    FS7: GitHub ──────────┘ (can run in parallel)
                          │
                          v
v1.0 (Future)
    FS2: Kanban P3-4
    FS6: Multi-Agent Coordination
                          │
                          v
v1.1+ (Future)
    FS8: Hackathon System
```

---

## GitHub Issues

### Epic Issues

| Issue | Title | Labels |
|-------|-------|--------|
| #143 | epic(v0.10): Agent Memory & Learning System | type:epic, P1 |
| #144 | epic(v0.10): Kanban Workflow Engine | type:epic, P1 |
| #145 | epic(v0.10): QA & Testing Enforcement | type:epic, P2 |
| #146 | epic(v0.10): Metrics & Dashboard System | type:epic, P2 |
| #147 | epic(v0.10): GitHub Integration Enhancements | type:epic, P2 |

### Future Milestones

| Issue | Title | Target |
|-------|-------|--------|
| #148 | epic(v1.0): Multi-Agent Coordination System | v1.0 |
| #149 | epic(v1.1+): Hackathon System | v1.1+ |

### Implementation Issues

#### FS1: Agent Memory (#143)

- #150 - Create memory/ directory structure
- #151 - Implement daily append-only session logs
- #152 - Add Sage Workflow J (session logging)
- #153 - Add Sage Workflow K (weekly consolidation)
- #163 - Integrate compound learning loop

#### FS2: Kanban Workflow (#144)

- #154 - Define per-ticket checklist JSON schema
- #155 - Implement transition guards in Supervisor
- #164 - Add WIP tracking to WORKFLOW_STATE.md

#### FS3: QA Enforcement (#145)

- #156 - Create QA_REPORT.md template
- #157 - Define qa-reviewer persona
- #165 - Update Supervisor phase gate for QA artifact
- #166 - Create /qa command

#### FS5: Metrics Dashboard (#146)

- #158 - Design SQLite schema for metrics
- #159 - Implement adherence scoring formula
- #160 - Build anomaly detection rules engine
- #167 - Implement event sync script
- #168 - Extend Workflow Hub with metrics widgets

#### FS7: GitHub Integration (#147)

- #161 - Create CODEOWNERS file
- #162 - Implement issue-ID task file naming
- #169 - Add PRD-to-Issue traceability metadata
- #170 - Create task file sync workflow

### Planning Documents

| Feature Set | PRD | TDD |
|-------------|-----|-----|
| Agent Memory | [PRD-024](./PRD-024-AGENT-MEMORY.md) | [TDD-024](./TDD-024-AGENT-MEMORY.md) |
| Kanban Workflow | [PRD-025](./PRD-025-KANBAN-WORKFLOW.md) | [TDD-025](./TDD-025-KANBAN-WORKFLOW.md) |
| QA Enforcement | [PRD-026](./PRD-026-QA-ENFORCEMENT.md) | [TDD-026](./TDD-026-QA-ENFORCEMENT.md) |
| Metrics Dashboard | [PRD-027](./PRD-027-METRICS-DASHBOARD.md) | [TDD-027](./TDD-027-METRICS-DASHBOARD.md) |
| GitHub Integration | [PRD-029](./PRD-029-GITHUB-INTEGRATION.md) | [TDD-029](./TDD-029-GITHUB-INTEGRATION.md) |
| Multi-Agent Coord (v1.0) | [PRD-028](./PRD-028-MULTI-AGENT-COORDINATION.md) | [TDD-028](./TDD-028-MULTI-AGENT-COORDINATION.md) |
| Hackathon (v1.1+) | [PRD-030](./PRD-030-HACKATHON-SYSTEM.md) | [TDD-030](./TDD-030-HACKATHON-SYSTEM.md) |

Additional planning artifacts in `temp/2026_02_01_Discussion/`:

- Research reports (`*_report.md`)
- Implementation plans (`*_plan.md`)

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Memory Logs | 100% sessions logged | Daily log file count |
| Workflow Adherence | >85% compliance score | Metrics dashboard |
| QA Gate Enforcement | 0 deploys without QA | Phase transition audit |
| Test Coverage | >80% on new code | dbt test count |
| Dashboard Uptime | 100% availability | Workflow Hub loads |
| Skip Rate | <5% stage skips | Compliance scoring |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep | Medium | High | Strict phase boundaries |
| Metrics schema churn | Medium | Medium | Lock schema after FS5.1 |
| Hook performance | Low | Medium | Advisory mode, <500ms |
| Breaking Backlog.md | Low | High | Backward-compatible extensions |

---

## Parallel Track: Vibe Coding Documentation Gap Closure

**Status**: Queued for post-Phase-B execution
**Epic**: #198 (Vibe Coding Gap Analysis)
**Timing**: After FS5 (Metrics) or concurrent with Phase B development

### Purpose

Close documentation and frontend design gaps identified from "Vibe Coding" X post analysis. This is complementary to v0.10 agent orchestration work and strengthens documentation foundations.

### Task Breakdown (4 Sprints)

| Priority | Sprint | Tasks | Effort | Issues |
|----------|--------|-------|--------|--------|
| P1 | Sprint 1 | TECH_STACK.md, DEPLOY_CHECKLIST.md | 3-5h | #201, #202 |
| P2 | Sprint 2 | Playground Audit, FRONTEND_GUIDELINES.md | 6-9h | #205, #203 |
| P2 | Sprint 3 | Task Decomposition, /plan Enhancement | 5-7h | #204, #206 |
| P3 | Sprint 4 | Learning Playground | 8-12h | #207 |

**Total Effort**: 23-31 hours

### Key Dependencies

- **After Phase A/B**: No blocking dependencies; can run in parallel
- **Supports FS2 Kanban**: Task Decomposition (#204) directly supports workflow discipline
- **Supports FS3 QA**: DEPLOY_CHECKLIST (#202) documents quality gates

### Interview-Based Approach

Each task includes a **structured interview** (20-45 min) to capture user perspective on function, design, and intent before implementation. See [VIBE-CODING-GAP-ANALYSIS.md](./VIBE-CODING-GAP-ANALYSIS.md) Part 5 for interview framework and sample questions.

### Deliverables

| Task | Document | Type | Impact |
|------|----------|------|--------|
| #201 | TECH_STACK.md | Reference | Version strategy, dependency documentation |
| #202 | DEPLOY_CHECKLIST.md | Standard | Pre-deploy quality gates |
| #203 | FRONTEND_GUIDELINES.md | Reference | Design consistency (6+ playgrounds) |
| #204 | LEARNINGS.md additions | Pattern | Task decomposition methodology |
| #205 | PLAYGROUND_AUDIT.md | Artifact | Design audit and remediation roadmap |
| #206 | /plan command enhancement | Tool | Better requirement interrogation |
| #207 | learning-hub.html | Playground | Interactive concept learning |

---

## Related Documents

- [UPDATED_IDEAS.md](../../temp/2026_02_01_Discussion/UPDATED_IDEAS.md) - Original feature organization
- [HOLISTIC_REVIEW.md](../../temp/2026_02_01_Discussion/HOLISTIC_REVIEW.md) - Cross-cutting analysis
- [v0.8 Roadmap](./ROADMAP-v0.8.md) - Current milestone (data quality)
- [FUTURE_FEATURES.md](./FUTURE_FEATURES.md) - Deferred features backlog
- [VIBE-CODING-GAP-ANALYSIS.md](./VIBE-CODING-GAP-ANALYSIS.md) - Detailed analysis and interview questions

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-04 | Added Vibe Coding Documentation Gap Closure track (7 issues: #201-#207) |
| 2026-02-01 | Initial v0.10 roadmap created from planning session |
