# PRD-024: Kanban Workflow Engine

## Overview

**Author**: Product Manager (Claude Code Agent System)
**Status**: Draft
**Created**: 2026-02-01
**Updated**: 2026-02-01
**Version**: v0.9
**Epic**: E20-Kanban-Workflow-Engine
**Related Research**: `temp/2026_02_01_Discussion/kanban_workflow_report.md`

---

## Problem Statement

### Current State

The dbt-playground repository has a well-defined 5-stage workflow (UNDERSTAND, PLAN,
BUILD, VERIFY, DEPLOY) documented in WORKFLOW_STAGES.md and a Supervisor agent that
manages state transitions. However, this workflow lacks **discipline enforcement**:

1. **No WIP Limits**: There is no limit on how many items can be in any stage
   simultaneously. Agents can overload the BUILD stage without capacity checks.

2. **Skippable Stages**: While the Supervisor "checks" for artifacts, there is no
   technical mechanism preventing an agent from bypassing stages. An agent can
   jump from UNDERSTAND directly to DEPLOY.

3. **No Per-Ticket Tracking**: Checklists exist in documentation but are not
   machine-readable or attached to individual tasks. There's no way to verify
   programmatically whether a task followed the proper workflow.

4. **No Compliance Measurement**: We cannot answer "how disciplined is our workflow?"
   There are no metrics tracking workflow adherence over time.

5. **No Audit Trail**: When items skip stages or violate workflow rules, there is
   no historical record to analyze patterns.

### Impact

- **Quality Unpredictability**: Tasks may skip quality gates, resulting in unreviewed
  or untested code reaching deployment
- **Hidden Workflow Violations**: Skipped stages go unnoticed until problems surface
- **Capacity Blindness**: No visibility into whether the team is overloaded
- **Accountability Gaps**: Cannot identify which agents or patterns cause violations
- **Learning Opportunities Lost**: Workflow failures not captured for improvement

### Research Findings

The Technical Architect's research report (2026-02-01) identified:

| Gap | Severity | Impact |
|-----|----------|--------|
| WIP Limits | Medium | Overloaded stages, poor flow |
| Per-Ticket Checklist (JSON) | High | Cannot verify compliance |
| No-Skip Enforcement | High | Quality gates bypassed |
| Compliance Scoring | Medium | Cannot measure discipline |
| Transition Audit Log | Low | Cannot analyze patterns |

---

## Goal

Implement a **Kanban Workflow Engine** that adds discipline enforcement to the
existing 5-stage workflow through:

1. **Per-ticket checklists**: Machine-readable JSON tracking stage progression
2. **Transition guards**: Supervisor-enforced validation before stage changes
3. **WIP limits**: Configurable limits per stage with soft/hard enforcement
4. **Compliance scoring**: Metrics measuring workflow discipline
5. **Skip detection**: Warnings and learning extraction when stages are bypassed

### Success Outcome

- Every tracked task completes all required workflow stages (100% compliance)
- Workflow violations are visible, logged, and extractable for learning
- Agents operate within capacity limits (WIP discipline)
- The team can measure and improve workflow discipline over time

---

## User Stories / Use Cases

### Core Workflow Enforcement

**US-1: Per-Ticket Checklist Tracking**
As a Supervisor agent, I want each task to have a machine-readable checklist so that
I can programmatically verify which stages are complete and which items remain.

**Acceptance Criteria**:

- [ ] Every Backlog.md task has a `workflow_checklist` field
- [ ] Checklist tracks status, required items, and completed items per stage
- [ ] Checklist includes timestamps for when stages started/completed
- [ ] Checklist identifies which agent worked on each stage

**US-2: Transition Guard Validation**
As a Supervisor agent, I want to validate checklist completion before allowing stage
transitions so that incomplete work cannot proceed to the next stage.

**Acceptance Criteria**:

- [ ] Transition from PLAN to BUILD requires all PLAN checklist items complete
- [ ] Transition from BUILD to VERIFY requires all BUILD checklist items complete
- [ ] Missing items result in a BLOCK with specific feedback
- [ ] Validation runs automatically on every transition request

**US-3: Skip Detection and Warning**
As a Supervisor agent, I want to detect when stages are skipped so that violations
are visible and learnings can be extracted.

**Acceptance Criteria**:

- [ ] Skipped stages logged in task checklist compliance section
- [ ] Warning message shown to user on skip detection
- [ ] Sage automatically invoked to extract learnings
- [ ] Skip count tracked for compliance scoring

### WIP Management

**US-4: WIP Count Visibility**
As a human operator, I want to see how many items are in each workflow stage so that
I can understand current capacity utilization.

**Acceptance Criteria**:

- [ ] WIP counts displayed per stage in `/kanban status` command
- [ ] WIP counts visible in WORKFLOW_STATE.md
- [ ] Counts accurate across parallel Claude Code sessions
- [ ] Counts updated in real-time on transitions

**US-5: WIP Limit Warnings**
As a human operator, I want warnings when stages approach capacity so that I can
take action before work gets blocked.

**Acceptance Criteria**:

- [ ] Warning shown when stage reaches 80% of configured limit
- [ ] Warning includes which stage and current count
- [ ] Suggested actions provided (complete existing work, wait, etc.)
- [ ] Warning visible in Workflow Hub

**US-6: WIP Limit Enforcement**
As a Supervisor agent, I want to block new work from entering over-capacity stages
so that work-in-progress remains manageable.

**Acceptance Criteria**:

- [ ] Hard block when stage reaches 100% of configured limit
- [ ] Block message includes current count and limit
- [ ] Bypass mechanism available with authorization and audit
- [ ] Bypass logged to task compliance section

### Compliance Tracking

**US-7: Compliance Score Calculation**
As a Supervisor agent, I want each task to have a compliance score so that workflow
discipline can be measured objectively.

**Acceptance Criteria**:

- [ ] Score = (completed_stages / required_stages) *100 - (skip_count* 10)
- [ ] Score calculated on task completion
- [ ] Score persisted in task checklist
- [ ] Bypass authorizations do not reduce score (tracked separately)

**US-8: Compliance Metrics Display**
As a human operator, I want to see compliance metrics for completed tasks so that
I can understand overall workflow discipline.

**Acceptance Criteria**:

- [ ] Average compliance score displayed in Workflow Hub
- [ ] Per-task compliance visible on Kanban board cards
- [ ] Color coding: Green (>80%), Yellow (60-80%), Red (<60%)
- [ ] Drill-down shows specific skip history

**US-9: Historical Compliance Analysis**
As a human operator, I want to see compliance trends over time so that I can identify
improvement opportunities.

**Acceptance Criteria**:

- [ ] Compliance data retained for completed tasks
- [ ] Weekly/monthly compliance averages calculable
- [ ] Common skip patterns identifiable
- [ ] Sage learnings correlated with compliance data

### Command Interface

**US-10: Kanban Status Command**
As a user, I want a `/kanban status` command so that I can quickly see the current
state of all workflow stages.

**Acceptance Criteria**:

- [ ] Shows count and percentage of WIP limit per stage
- [ ] Lists tasks in each stage with brief info
- [ ] Highlights stages at or near capacity
- [ ] Works from any Claude Code session

**US-11: Kanban Transition Command**
As a Supervisor agent, I want a `/kanban transition [task] [stage]` command so that
I can move tasks with full validation.

**Acceptance Criteria**:

- [ ] Validates checklist completion before transition
- [ ] Checks WIP limits before accepting into new stage
- [ ] Provides clear feedback on success or failure
- [ ] Logs transition to task history

**US-12: Kanban Compliance Command**
As a user, I want a `/kanban compliance [task]` command so that I can see detailed
compliance information for a specific task.

**Acceptance Criteria**:

- [ ] Shows compliance score and calculation breakdown
- [ ] Lists all stages with completion status
- [ ] Shows skip history with timestamps
- [ ] Shows bypass history with authorization details

---

## Functional Requirements

### FR-1: Per-Ticket Workflow Checklist

**Data Structure**:

Each Backlog.md task includes a `workflow_checklist` field containing:

| Field | Type | Description |
|-------|------|-------------|
| stages | object | Per-stage checklist data |
| stages.[stage].status | enum | pending, in_progress, complete, skipped |
| stages.[stage].required_items | array | Items required to complete stage |
| stages.[stage].completed_items | array | Items already completed |
| stages.[stage].started_at | datetime | When stage work began |
| stages.[stage].completed_at | datetime | When stage was marked complete |
| stages.[stage].agent | string | Agent that worked on stage |
| compliance.score | number | Calculated compliance score (0-100) |
| compliance.skips | array | List of skipped stages with metadata |
| compliance.bypasses | array | List of authorized bypasses |

**Required Items Per Stage**:

| Stage | Required Items |
|-------|----------------|
| UNDERSTAND | requirements_clarified, acceptance_criteria_defined |
| PLAN | prd_created (if needed), tdd_created (if needed), branch_created, draft_pr_created |
| BUILD | tests_written, implementation_complete, local_tests_pass, dev_report_written |
| VERIFY | code_review_approved, security_review_approved (if needed), changelog_updated, ci_passing |
| DEPLOY | pr_merged, docs_updated, learnings_extracted (if applicable) |

### FR-2: Transition Guard Logic

**Valid Transitions**:

| From | Valid To | Notes |
|------|----------|-------|
| UNDERSTAND | PLAN, BLOCKED | Cannot skip to BUILD |
| PLAN | BUILD, BLOCKED | Cannot skip to VERIFY |
| BUILD | VERIFY, BLOCKED | Cannot skip to DEPLOY |
| VERIFY | DEPLOY, BLOCKED | Must complete all reviews |
| DEPLOY | (complete) | Terminal state |
| BLOCKED | Any prior stage | Can return to any stage |

**Guard Checks** (in order):

1. Is transition valid? (per matrix above)
2. Is target stage skipping any required stages?
3. Are all required items complete for current stage?
4. Is target stage at WIP capacity?

**Critical Transitions** (hard block on skip):

- PLAN to BUILD
- BUILD to VERIFY

**Non-Critical Transitions** (soft warning on skip):

- UNDERSTAND to PLAN

### FR-3: WIP Limits

**Configuration**:

```yaml
# backlog/config.yml addition
wip_limits:
  understand: 5
  plan: 3
  build: 2
  verify: 3
  deploy: 2
  blocked: 10  # Higher limit for blocked items
```

**Enforcement Levels**:

| Level | Threshold | Behavior |
|-------|-----------|----------|
| Normal | <80% | No action |
| Warning | 80-99% | Warn user, allow transition |
| Hard Limit | 100% | Block transition, require bypass |

**Bypass Mechanism**:

- User can authorize bypass with reason
- Bypass logged to task compliance section
- Does not reduce compliance score
- Audit trail maintained

### FR-4: Compliance Scoring

**Formula**:

```
base_score = (completed_stages / required_stages) * 100
penalty = skip_count * 10
final_score = max(0, base_score - penalty)
```

**Score Interpretation**:

| Score | Rating | Color |
|-------|--------|-------|
| 80-100 | Excellent | Green |
| 60-79 | Acceptable | Yellow |
| 40-59 | Needs Improvement | Orange |
| 0-39 | Poor | Red |

### FR-5: Skip Detection and Learning

**On Skip Detection**:

1. Log skip to task checklist: `compliance.skips[]`
2. Display warning to user
3. Invoke Sage with context:

   ```
   sage: Extract learnings from workflow skip.
   - Task: [task_id]
   - From stage: [from]
   - To stage: [to]
   - Skipped stage: [skipped]
   - Reason given: [reason if any]
   Focus on: Why was skip necessary? How to prevent?
   ```

4. Update compliance score

### FR-6: WORKFLOW_STATE.md Updates

**New Section**:

```yaml
## WIP Counts
| Stage | Count | Limit | % Used |
|-------|-------|-------|--------|
| UNDERSTAND | 2 | 5 | 40% |
| PLAN | 1 | 3 | 33% |
| BUILD | 2 | 2 | 100% |
| VERIFY | 0 | 3 | 0% |
| DEPLOY | 0 | 2 | 0% |
| BLOCKED | 1 | 10 | 10% |
```

---

## Non-Functional Requirements

| ID | Requirement | Target | Rationale |
|----|-------------|--------|-----------|
| NFR-1 | Transition validation latency | <500ms | Must feel responsive |
| NFR-2 | WIP count accuracy | 100% | Critical for enforcement |
| NFR-3 | Cross-session consistency | Eventual (5s) | Backlog.md API refresh |
| NFR-4 | Checklist persistence | Durable | Must survive session restart |
| NFR-5 | Backward compatibility | Full | Existing tasks work without checklist |
| NFR-6 | Configuration flexibility | High | WIP limits configurable per stage |
| NFR-7 | Audit completeness | 100% | All skips and bypasses logged |

---

## Acceptance Criteria

### Phase 1: Foundation (v0.9)

- [ ] AC-1.1: JSON schema validates all test payloads
- [ ] AC-1.2: New Backlog.md tasks created with workflow_checklist field
- [ ] AC-1.3: WORKFLOW_STATE.md displays accurate WIP counts
- [ ] AC-1.4: `/kanban status` command returns expected output
- [ ] AC-1.5: Existing tasks without checklists continue to function

### Phase 2: Transition Guards (v0.9)

- [ ] AC-2.1: PLAN to BUILD transition blocked when checklist incomplete
- [ ] AC-2.2: BUILD to VERIFY transition blocked when checklist incomplete
- [ ] AC-2.3: Skip detection logs warning for non-critical transitions
- [ ] AC-2.4: Sage invoked when skip detected
- [ ] AC-2.5: `/kanban transition` command validates and transitions

### Phase 3: Compliance Scoring (v1.0)

- [ ] AC-3.1: Compliance score calculated correctly per formula
- [ ] AC-3.2: Score displayed in Workflow Hub
- [ ] AC-3.3: Score visible on Kanban board cards
- [ ] AC-3.4: `/kanban compliance` command shows detailed breakdown

### Phase 4: WIP Limits (v1.0)

- [ ] AC-4.1: WIP limits configurable in backlog/config.yml
- [ ] AC-4.2: Warning shown at 80% capacity
- [ ] AC-4.3: Hard block at 100% capacity
- [ ] AC-4.4: Bypass mechanism functional with audit trail
- [ ] AC-4.5: Visual indicators on Kanban board lanes

---

## Out of Scope

| Item | Reason | Future Consideration |
|------|--------|---------------------|
| Pull-based work allocation | Complexity; not needed for v1.0 | v1.1+ if needed |
| Transition audit log database | Backlog.md sufficient | v1.1+ if analytics needed |
| Automated stale detection | Separate feature | PM Orchestration v0.9 |
| Real-time compliance dashboards | Metrics overkill for current scale | v1.1+ |
| Multi-repo WIP tracking | Single repo focus | v2.0 |
| External Kanban tool integration | Build-first approach | v1.1+ if requested |
| AI-based skip prediction | Research needed | Future consideration |
| Gamification (badges, leaderboards) | Not aligned with learning goals | Not planned |

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Backlog.md v1.35+ | Software | Installed |
| PM Orchestration Phase 3 | Feature | 90% complete |
| Supervisor agent | Infrastructure | Stable |
| Sage integration | Feature | Stable |
| Workflow Hub v0.7.2 | Feature | In progress |
| WORKFLOW_STAGES.md | Documentation | Complete |

---

## Success Metrics

| Metric | Baseline | Phase 2 Target | Phase 4 Target |
|--------|----------|----------------|----------------|
| Stage skip rate | Unknown (estimated >30%) | <20% | <5% |
| Average compliance score | N/A | >70% | >85% |
| WIP violations | Not tracked | Visible | <5% |
| Transition enforcement rate | 0% | 100% critical | 100% all |
| Learning extraction rate (on skips) | 0% | 100% | 100% |
| Bypass usage rate | N/A | Tracked | <10% |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Backlog.md doesn't support custom fields | Low | High | Test early; fallback to parallel JSON |
| Enforcement too rigid | Medium | Medium | Bypass mechanism with audit |
| Adoption friction | Medium | Low | Start soft, graduate to hard |
| Cross-session race conditions | Low | Medium | Use Backlog.md API as source of truth |
| Complexity creep | Medium | Medium | Strict scope control; defer to future |

---

## Related Documents

| Document | Relationship |
|----------|--------------|
| `temp/2026_02_01_Discussion/kanban_workflow_report.md` | Research foundation |
| `temp/2026_02_01_Discussion/kanban_workflow_plan.md` | Implementation plan |
| `temp/2026_02_01_Discussion/kanban_workflow_TDD.md` | Technical design |
| `docs/reference/WORKFLOW_STAGES.md` | Current workflow definition |
| `.claude/agents/supervisor.md` | Supervisor enforcement logic |
| `docs/specs/PRD-023-HUB-KANBAN.md` | Kanban board visualization |
| `docs/specs/PRD-022-PM-ORCHESTRATION.md` | PM orchestration architecture |

---

## Appendix A: User Flow Diagrams

### Transition Guard Flow

```
[Agent requests transition: BUILD -> VERIFY]
    |
    v
[Supervisor receives request]
    |
    +-- Is transition valid? (per matrix)
    |       |
    |       +-- No --> BLOCK: "Invalid transition"
    |       |
    |       +-- Yes --> Continue
    |
    +-- Any stages skipped?
    |       |
    |       +-- Yes (critical) --> BLOCK: "Cannot skip [stage]"
    |       |
    |       +-- Yes (non-critical) --> WARN, invoke Sage, continue
    |       |
    |       +-- No --> Continue
    |
    +-- Checklist complete for BUILD?
    |       |
    |       +-- No --> BLOCK: "Incomplete: [items]"
    |       |
    |       +-- Yes --> Continue
    |
    +-- VERIFY at WIP capacity?
    |       |
    |       +-- Yes --> BLOCK: "WIP limit reached (3/3)"
    |       |          (offer bypass option)
    |       |
    |       +-- No --> Continue
    |
    +-- Execute transition
            |
            +-- Update task status
            +-- Update checklist timestamps
            +-- Update WIP counts
            +-- Log transition
            +-- Return SUCCESS
```

### Skip Detection Flow

```
[Skip detected: UNDERSTAND -> BUILD (skipped PLAN)]
    |
    v
[Log to task.compliance.skips]
    |
    +-- { from: "UNDERSTAND", to: "BUILD", skipped: "PLAN", timestamp, reason }
    |
    v
[Display warning to user]
    |
    v
[Invoke Sage]
    |
    +-- sage: Extract learnings from workflow skip...
    |
    v
[Update compliance score]
    |
    +-- penalty = skip_count * 10
    +-- new_score = base_score - penalty
    |
    v
[Continue with transition if non-critical]
```

---

*PRD Status: Draft - Ready for Review*
*Author: Product Manager*
*Date: 2026-02-01*
