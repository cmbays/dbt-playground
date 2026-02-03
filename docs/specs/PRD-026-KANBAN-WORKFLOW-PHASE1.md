# PRD-026: Kanban Workflow Engine (Phase 1-2)

## Overview

**Author**: Product Manager (Claude Code Agent System)
**Status**: In Progress
**Created**: 2026-02-02
**Updated**: 2026-02-02
**Version**: v0.10
**Epic**: #144 (Kanban Workflow Engine)
**Parent PRD**: PRD-024-KANBAN-WORKFLOW.md

---

## Scope

This PRD covers Phase 1-2 of the Kanban Workflow Engine implementation, focusing on:

1. **Per-ticket checklist JSON schema** (#154)
2. **Transition guards in Supervisor** (#155)
3. **WIP tracking in WORKFLOW_STATE.md** (#164)

Phase 3-4 (compliance scoring, hard WIP limits) are deferred to v1.0.

---

## Problem Statement

The existing 5-stage workflow (UNDERSTAND → PLAN → BUILD → VERIFY → DEPLOY) lacks:

1. **Machine-readable checklists** - Cannot verify stage completion programmatically
2. **Transition enforcement** - Stages can be skipped without detection
3. **WIP visibility** - No tracking of concurrent work items per stage

---

## Goals

### Phase 1: Foundation

- Define JSON schema for per-ticket workflow checklists
- Extend Backlog.md YAML to support checklist field
- Add WIP count tracking to WORKFLOW_STATE.md

### Phase 2: Transition Guards

- Implement transition validation in Supervisor
- Detect and log stage skips
- Soft enforcement (warn but allow) initially

---

## User Stories

### US-1: Per-Ticket Checklist (Issue #154)

**As a** Supervisor agent,
**I want** each task to have a machine-readable checklist,
**So that** I can verify stage completion programmatically.

**Acceptance Criteria**:
- [ ] JSON Schema defined with all 5 stages
- [ ] Each stage tracks: status, required_items, completed_items, timestamps
- [ ] Compliance section tracks skips and bypasses
- [ ] Schema is backward-compatible with existing tasks

### US-2: Transition Guards (Issue #155)

**As a** Supervisor agent,
**I want** to validate transitions before allowing stage changes,
**So that** workflow discipline is enforced.

**Acceptance Criteria**:
- [ ] Guards validate all transitions against allowed matrix
- [ ] Skip detection logs warning and reason
- [ ] Bypass mechanism with explicit reason
- [ ] Soft enforcement (warn, don't block) initially

### US-3: WIP Tracking (Issue #164)

**As a** human operator,
**I want** to see how many items are in each workflow stage,
**So that** I understand capacity utilization.

**Acceptance Criteria**:
- [ ] WIP counts displayed in WORKFLOW_STATE.md
- [ ] Counts updated on stage transitions
- [ ] Warning when approaching configured limits

---

## Technical Approach

### Checklist Schema (v1.0)

```json
{
  "task_id": "TASK-5",
  "created_at": "2026-02-02T12:00:00Z",
  "stages": {
    "understand": { "status": "complete", "started_at": "...", "completed_at": "..." },
    "plan": { "status": "in_progress", "started_at": "..." },
    "build": { "status": "pending" },
    "verify": { "status": "pending" },
    "deploy": { "status": "pending" }
  },
  "compliance": {
    "score": 100,
    "skips": [],
    "bypasses": []
  }
}
```

### Transition Guard Logic

See TDD-025-KANBAN-WORKFLOW.md for pseudocode implementation.

### WIP Tracking Format

```yaml
## WIP Counts
| Stage | Count | Limit | % Used |
|-------|-------|-------|--------|
| UNDERSTAND | 2 | 5 | 40% |
| PLAN | 1 | 3 | 33% |
| BUILD | 2 | 2 | 100% |
| VERIFY | 0 | 3 | 0% |
| DEPLOY | 0 | 2 | 0% |
```

---

## Success Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| Stage skip rate | Unknown | <20% (soft enforcement) |
| Transition logging | 0% | 100% |
| WIP visibility | 0% | 100% |

---

## Timeline

| Phase | Days | Deliverables |
|-------|------|--------------|
| Planning | 1-3 | Gap analysis, interface contract |
| TDD | 4-5 | Test suites (40 tests) |
| Competitive | 6-8 | Alpha/Beta designs, consolidation |
| Development | 9-10 | #154, #155, #164 implemented |
| Review | 11-12 | Code review, 80%+ coverage |
| Testing | 13 | Manual testing |
| Integration | 14 | FS3 sync, PR ready |

**Total**: 14 days (16h effort)

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Backlog.md API | Available | localhost:6420 |
| Supervisor agent | Stable | Modification target |
| WORKFLOW_STATE.md | Exists | Extension target |
| FS3 QA Gates | Planned | Coordination required |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| FS3 conflict in Supervisor | Interface contract by Day 3 |
| Enforcement too rigid | Warn-not-block initially |
| Schema evolution | Version field (v1.0) |

---

## Related Documents

| Document | Relationship |
|----------|--------------|
| PRD-024-KANBAN-WORKFLOW.md | Parent PRD |
| TDD-025-KANBAN-WORKFLOW.md | Technical design |
| FS2_CONTEXT_INDEX.md | Implementation context |

---

*PRD-026 - Kanban Workflow Engine (Phase 1-2)*
*Status: In Progress*
*Author: Product Manager*
