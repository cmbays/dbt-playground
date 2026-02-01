# TDD-024: Kanban Workflow Engine

## Overview

**Author**: Technical Architect
**Status**: Draft
**Created**: 2026-02-01
**Updated**: 2026-02-01
**PRD Reference**: PRD-024-KANBAN-WORKFLOW-ENGINE
**Epic**: E20-Kanban-Workflow-Engine

---

## Architecture Overview

The Kanban Workflow Engine adds discipline enforcement to the existing 5-stage
workflow without replacing the current infrastructure. It integrates with:

1. **Backlog.md**: Task storage with extended checklist field
2. **Supervisor Agent**: Transition guard execution
3. **WORKFLOW_STATE.md**: WIP count tracking
4. **Sage Agent**: Learning extraction on violations

### System Context Diagram

```
                                    +-----------------+
                                    |   Human User    |
                                    +--------+--------+
                                             |
                         +-------------------v-------------------+
                         |            Claude Code Session         |
                         |  +-------------+  +----------------+  |
                         |  | Supervisor  |  | /kanban cmds   |  |
                         |  +------+------+  +-------+--------+  |
                         +---------|-----------------|-----------+
                                   |                 |
              +--------------------+-----------------+--------------------+
              |                    |                                      |
              v                    v                                      v
    +---------+-------+   +--------+--------+                   +---------+-------+
    |   Backlog.md    |   | WORKFLOW_STATE  |                   |      Sage       |
    | +-----------+   |   |  +----------+   |                   |  (on skips)     |
    | | Tasks     |   |   |  | WIP      |   |                   +-----------------+
    | | +checklist|   |   |  | Counts   |   |
    | +-----------+   |   |  +----------+   |
    +-----------------+   +-----------------+
```

### Data Flow

```
[User/Agent requests transition]
        |
        v
[Supervisor.transition_task()]
        |
        +---> [Backlog.md API: GET task]
        |             |
        |             v
        |     [Validate checklist]
        |             |
        +---> [Check WIP limits]
        |             |
        |             v
        |     [WORKFLOW_STATE.md: read counts]
        |
        +---> [Execute transition]
                      |
                      +---> [Backlog.md API: PUT task]
                      +---> [WORKFLOW_STATE.md: update counts]
                      +---> [Sage: invoke if skip detected]
```

---

## Per-Ticket Checklist JSON Schema

### Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://dbt-playground/schemas/workflow-checklist.schema.json",
  "title": "WorkflowChecklist",
  "description": "Per-ticket workflow checklist tracking stage progression",
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Reference to Backlog.md task ID"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "When checklist was initialized"
    },
    "stages": {
      "type": "object",
      "properties": {
        "understand": { "$ref": "#/definitions/StageChecklist" },
        "plan": { "$ref": "#/definitions/StageChecklist" },
        "build": { "$ref": "#/definitions/StageChecklist" },
        "verify": { "$ref": "#/definitions/StageChecklist" },
        "deploy": { "$ref": "#/definitions/StageChecklist" }
      },
      "additionalProperties": false
    },
    "compliance": {
      "type": "object",
      "properties": {
        "score": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Calculated compliance score"
        },
        "skips": {
          "type": "array",
          "items": { "$ref": "#/definitions/SkipRecord" },
          "description": "History of skipped stages"
        },
        "bypasses": {
          "type": "array",
          "items": { "$ref": "#/definitions/BypassRecord" },
          "description": "History of authorized bypasses"
        }
      },
      "required": ["score", "skips", "bypasses"]
    }
  },
  "required": ["task_id", "created_at", "stages", "compliance"],
  "definitions": {
    "StageChecklist": {
      "type": "object",
      "properties": {
        "status": {
          "type": "string",
          "enum": ["pending", "in_progress", "complete", "skipped"],
          "description": "Current status of this stage"
        },
        "required_items": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Items required to complete this stage"
        },
        "completed_items": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Items already completed"
        },
        "started_at": {
          "type": ["string", "null"],
          "format": "date-time",
          "description": "When work on this stage began"
        },
        "completed_at": {
          "type": ["string", "null"],
          "format": "date-time",
          "description": "When this stage was completed"
        },
        "agent": {
          "type": ["string", "null"],
          "description": "Agent that worked on this stage"
        }
      },
      "required": ["status", "required_items", "completed_items"]
    },
    "SkipRecord": {
      "type": "object",
      "properties": {
        "from_stage": { "type": "string" },
        "to_stage": { "type": "string" },
        "skipped_stage": { "type": "string" },
        "timestamp": { "type": "string", "format": "date-time" },
        "reason": { "type": ["string", "null"] },
        "learning_extracted": { "type": "boolean" }
      },
      "required": ["from_stage", "to_stage", "skipped_stage", "timestamp"]
    },
    "BypassRecord": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["wip_limit", "checklist_incomplete", "critical_skip"]
        },
        "stage": { "type": "string" },
        "reason": { "type": "string" },
        "authorized_by": { "type": "string" },
        "timestamp": { "type": "string", "format": "date-time" }
      },
      "required": ["type", "stage", "reason", "authorized_by", "timestamp"]
    }
  }
}
```

### Required Items Configuration

Default required items per stage (can be overridden per task):

```yaml
# Default required items per stage
workflow_stage_requirements:
  understand:
    required_items:
      - requirements_clarified
      - acceptance_criteria_defined
    optional_items:
      - blocking_questions_resolved
  plan:
    required_items:
      - branch_created
    optional_items:
      - prd_created
      - tdd_created
      - draft_pr_created
    conditional:
      - item: prd_created
        when: scope_requires_prd
      - item: tdd_created
        when: scope_requires_tdd
  build:
    required_items:
      - tests_written
      - implementation_complete
      - local_tests_pass
    optional_items:
      - dev_report_written
  verify:
    required_items:
      - code_review_approved
      - changelog_updated
      - ci_passing
    optional_items:
      - security_review_approved
    conditional:
      - item: security_review_approved
        when: security_relevant
  deploy:
    required_items:
      - pr_merged
      - docs_updated
    optional_items:
      - learnings_extracted
```

### Example Task with Checklist

```yaml
---
id: TASK-5
title: 'feat(workflow): add Kanban discipline enforcement'
status: BUILD
assignee: [session-abc-123]
created_date: '2026-02-01'
updated_date: '2026-02-01'
labels: [workflow, enhancement]
dependencies: []
priority: high
workflow_checklist:
  stages:
    understand:
      status: complete
      required_items: [requirements_clarified, acceptance_criteria_defined]
      completed_items: [requirements_clarified, acceptance_criteria_defined]
      started_at: '2026-02-01T09:00:00Z'
      completed_at: '2026-02-01T09:30:00Z'
      agent: supervisor
    plan:
      status: complete
      required_items: [branch_created, prd_created, tdd_created]
      completed_items: [branch_created, prd_created, tdd_created]
      started_at: '2026-02-01T09:30:00Z'
      completed_at: '2026-02-01T11:00:00Z'
      agent: architect
    build:
      status: in_progress
      required_items: [tests_written, implementation_complete, local_tests_pass]
      completed_items: [tests_written]
      started_at: '2026-02-01T11:00:00Z'
      completed_at: null
      agent: developer
    verify:
      status: pending
      required_items: [code_review_approved, changelog_updated, ci_passing]
      completed_items: []
      started_at: null
      completed_at: null
      agent: null
    deploy:
      status: pending
      required_items: [pr_merged, docs_updated]
      completed_items: []
      started_at: null
      completed_at: null
      agent: null
  compliance:
    score: 100
    skips: []
    bypasses: []
---

## Description
Implement Kanban discipline enforcement for the workflow system...
```

---

## Transition Guard Logic

### Pseudocode Implementation

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

class Stage(Enum):
    UNDERSTAND = "understand"
    PLAN = "plan"
    BUILD = "build"
    VERIFY = "verify"
    DEPLOY = "deploy"
    BLOCKED = "blocked"

# Define valid transitions
VALID_TRANSITIONS = {
    Stage.UNDERSTAND: [Stage.PLAN, Stage.BLOCKED],
    Stage.PLAN: [Stage.BUILD, Stage.BLOCKED],
    Stage.BUILD: [Stage.VERIFY, Stage.BLOCKED],
    Stage.VERIFY: [Stage.DEPLOY, Stage.BLOCKED],
    Stage.DEPLOY: [],  # Terminal
    Stage.BLOCKED: [Stage.UNDERSTAND, Stage.PLAN, Stage.BUILD, Stage.VERIFY, Stage.DEPLOY],
}

# Critical transitions that cannot be skipped
CRITICAL_TRANSITIONS = [
    (Stage.PLAN, Stage.BUILD),
    (Stage.BUILD, Stage.VERIFY),
]

@dataclass
class TransitionResult:
    success: bool
    message: str
    warnings: List[str]
    sage_invoked: bool = False

def get_next_stage(current: Stage) -> Optional[Stage]:
    """Get the expected next stage in normal workflow."""
    sequence = [Stage.UNDERSTAND, Stage.PLAN, Stage.BUILD, Stage.VERIFY, Stage.DEPLOY]
    try:
        idx = sequence.index(current)
        return sequence[idx + 1] if idx < len(sequence) - 1 else None
    except ValueError:
        return None

def transition_task(
    task_id: str,
    from_stage: Stage,
    to_stage: Stage,
    bypass_reason: Optional[str] = None
) -> TransitionResult:
    """
    Execute a task transition with full validation.

    Validation Order:
    1. Is transition valid?
    2. Would transition skip a stage?
    3. Is checklist complete for current stage?
    4. Is target stage at WIP capacity?
    """
    warnings = []

    # Load task and checklist
    task = load_task(task_id)
    checklist = task.workflow_checklist

    # 1. Check: Is this a valid transition?
    if to_stage not in VALID_TRANSITIONS.get(from_stage, []):
        return TransitionResult(
            success=False,
            message=f"Invalid transition: {from_stage.value} -> {to_stage.value}",
            warnings=[]
        )

    # 2. Check: Would this skip a stage?
    expected_next = get_next_stage(from_stage)
    if expected_next and to_stage != expected_next and to_stage != Stage.BLOCKED:
        is_critical = (from_stage, to_stage) in CRITICAL_TRANSITIONS

        if is_critical and not bypass_reason:
            return TransitionResult(
                success=False,
                message=f"Critical skip requires bypass authorization. "
                       f"Skipped stage: {expected_next.value}. "
                       f"Use: /kanban bypass {task_id} --reason 'justification'",
                warnings=[]
            )

        # Log the skip
        skip_record = {
            "from_stage": from_stage.value,
            "to_stage": to_stage.value,
            "skipped_stage": expected_next.value,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": bypass_reason,
            "learning_extracted": False
        }
        checklist.compliance.skips.append(skip_record)
        checklist.compliance.score = max(0, checklist.compliance.score - 10)

        # Invoke Sage for learning extraction
        invoke_sage_for_skip(task_id, skip_record)

        if not is_critical:
            warnings.append(
                f"WARNING: Skipped stage {expected_next.value}. "
                f"Compliance score reduced. Sage invoked for learning extraction."
            )

    # 3. Check: Are all required items complete for current stage?
    if from_stage != Stage.BLOCKED:
        stage_checklist = checklist.stages[from_stage.value]
        incomplete = set(stage_checklist.required_items) - set(stage_checklist.completed_items)

        if incomplete and not bypass_reason:
            return TransitionResult(
                success=False,
                message=f"Cannot transition from {from_stage.value}. "
                       f"Incomplete items: {list(incomplete)}",
                warnings=[]
            )

        if incomplete and bypass_reason:
            bypass_record = {
                "type": "checklist_incomplete",
                "stage": from_stage.value,
                "reason": bypass_reason,
                "authorized_by": get_current_user(),
                "timestamp": datetime.utcnow().isoformat()
            }
            checklist.compliance.bypasses.append(bypass_record)
            warnings.append(
                f"Bypass authorized for incomplete checklist. "
                f"Skipped items: {list(incomplete)}"
            )

    # 4. Check: WIP limit for target stage
    if to_stage != Stage.BLOCKED:
        wip_count = count_tasks_in_stage(to_stage)
        wip_limit = get_wip_limit(to_stage)

        if wip_count >= wip_limit:
            if not bypass_reason:
                return TransitionResult(
                    success=False,
                    message=f"WIP limit reached for {to_stage.value} "
                           f"({wip_count}/{wip_limit}). "
                           f"Complete existing work or use bypass.",
                    warnings=[]
                )

            bypass_record = {
                "type": "wip_limit",
                "stage": to_stage.value,
                "reason": bypass_reason,
                "authorized_by": get_current_user(),
                "timestamp": datetime.utcnow().isoformat()
            }
            checklist.compliance.bypasses.append(bypass_record)
            warnings.append(
                f"Bypass authorized for WIP limit. "
                f"Stage {to_stage.value} now at {wip_count + 1}/{wip_limit}."
            )
        elif wip_count >= wip_limit * 0.8:
            warnings.append(
                f"Approaching WIP limit for {to_stage.value} "
                f"({wip_count}/{wip_limit} = {int(wip_count/wip_limit*100)}%)"
            )

    # All checks pass: execute transition
    if from_stage != Stage.BLOCKED:
        stage_checklist = checklist.stages[from_stage.value]
        stage_checklist.status = "complete"
        stage_checklist.completed_at = datetime.utcnow().isoformat()

    task.status = to_stage.value.upper()
    if to_stage != Stage.BLOCKED:
        checklist.stages[to_stage.value].status = "in_progress"
        checklist.stages[to_stage.value].started_at = datetime.utcnow().isoformat()

    # Save and log
    save_task(task)
    update_wip_counts()
    log_transition(task_id, from_stage, to_stage)

    return TransitionResult(
        success=True,
        message=f"Transitioned {task_id} from {from_stage.value} to {to_stage.value}",
        warnings=warnings,
        sage_invoked=len(checklist.compliance.skips) > 0
    )

def invoke_sage_for_skip(task_id: str, skip_record: dict) -> None:
    """Invoke Sage to extract learnings from a workflow skip."""
    sage_prompt = f"""sage: Extract learnings from workflow skip.
- Task: {task_id}
- From stage: {skip_record['from_stage']}
- To stage: {skip_record['to_stage']}
- Skipped stage: {skip_record['skipped_stage']}
- Reason given: {skip_record.get('reason', 'None provided')}

Focus on:
- Why was this skip necessary?
- What process improvement could prevent this?
- Should this be a legitimate workflow exception?

Write findings to temp/AGENT_REPORTS/kanban-workflow/SKIP_LEARNINGS.md
"""
    # Invoke Sage persona (implementation depends on agent framework)
    invoke_agent("sage", sage_prompt)
```

### Supervisor Integration

Add to `.claude/agents/supervisor.md`:

```markdown
## Kanban Transition Guard (NEW)

Before any phase transition, the Supervisor validates the transition using Kanban
workflow rules.

### Transition Validation Flow

[Phase Transition Requested]
    |
    +-- 1. Load task workflow_checklist from Backlog.md
    |
    +-- 2. Validate transition using transition_task() logic:
    |       - Is transition valid?
    |       - Would it skip a stage?
    |       - Is checklist complete?
    |       - Is target at WIP capacity?
    |
    +-- 3. On validation failure:
    |       - BLOCK transition
    |       - Report specific reason to user
    |       - Offer bypass option if applicable
    |
    +-- 4. On validation success:
    |       - Execute transition
    |       - Update task status in Backlog.md
    |       - Update WIP counts in WORKFLOW_STATE.md
    |       - Display any warnings
    |
    +-- 5. On skip detection:
            - Log to compliance.skips
            - Invoke Sage for learning
            - Update compliance score

### Checklist Item Marking

When artifacts are created, Supervisor marks checklist items complete:

| Artifact Created | Checklist Item |
|-----------------|----------------|
| docs/specs/PRD-*.md | prd_created |
| docs/specs/TDD-*.md | tdd_created |
| Feature branch created | branch_created |
| Draft PR created | draft_pr_created |
| Tests in models/*/schema.yml | tests_written |
| Model files created | implementation_complete |
| `dbt build` passes | local_tests_pass |
| Review approved | code_review_approved |
| CHANGELOG.md updated | changelog_updated |
| CI checks pass | ci_passing |
| PR merged | pr_merged |
| Docs updated | docs_updated |

### Checklist Update API

def mark_checklist_item(task_id: str, stage: str, item: str) -> None:
    task = load_task(task_id)
    checklist = task.workflow_checklist
    stage_list = checklist.stages[stage]

    if item not in stage_list.completed_items:
        stage_list.completed_items.append(item)
        save_task(task)
        log_checklist_update(task_id, stage, item)
```

---

## Compliance Scoring Algorithm

### Score Calculation

```python
def calculate_compliance_score(checklist: WorkflowChecklist) -> float:
    """
    Calculate compliance score for a task.

    Formula:
    - Base score: (completed_stages / required_stages) * 100
    - Skip penalty: -10 points per skipped stage
    - Minimum score: 0
    - Maximum score: 100

    Bypasses are tracked but do not affect score (authorized exceptions).
    """

    required_stages = ["understand", "plan", "build", "verify", "deploy"]
    completed_stages = [
        s for s in required_stages
        if checklist.stages[s].status == "complete"
    ]

    base_score = (len(completed_stages) / len(required_stages)) * 100
    skip_penalty = len(checklist.compliance.skips) * 10

    final_score = max(0, base_score - skip_penalty)

    return round(final_score, 1)

def get_compliance_breakdown(checklist: WorkflowChecklist) -> dict:
    """Get detailed compliance breakdown for display."""

    required_stages = ["understand", "plan", "build", "verify", "deploy"]
    completed_count = sum(
        1 for s in required_stages
        if checklist.stages[s].status == "complete"
    )

    return {
        "score": checklist.compliance.score,
        "rating": get_rating(checklist.compliance.score),
        "stages": {
            "required": len(required_stages),
            "completed": completed_count,
            "percentage": round(completed_count / len(required_stages) * 100, 1)
        },
        "penalties": {
            "skip_count": len(checklist.compliance.skips),
            "skip_penalty": len(checklist.compliance.skips) * 10
        },
        "bypasses": {
            "count": len(checklist.compliance.bypasses),
            "types": [b["type"] for b in checklist.compliance.bypasses]
        },
        "calculation": f"({completed_count}/5 * 100) - ({len(checklist.compliance.skips)} * 10) = {checklist.compliance.score}"
    }

def get_rating(score: float) -> str:
    """Convert score to rating label."""
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "acceptable"
    elif score >= 40:
        return "needs_improvement"
    else:
        return "poor"
```

### Score Update Triggers

| Event | Score Action |
|-------|--------------|
| Stage completed | Recalculate base score |
| Stage skipped | Subtract 10 points |
| Bypass authorized | No change (tracked separately) |
| Task completed | Final score persisted |

---

## Integration with Existing Supervisor and Backlog.md

### Backlog.md API Integration

The Kanban engine uses the existing Backlog.md REST API:

```python
import requests
from typing import Optional

BACKLOG_API = "http://localhost:6420/api"

def load_task(task_id: str) -> Task:
    """Load task from Backlog.md API."""
    response = requests.get(f"{BACKLOG_API}/tasks/{task_id}")
    response.raise_for_status()
    return Task.from_dict(response.json())

def save_task(task: Task) -> None:
    """Save task to Backlog.md API."""
    response = requests.put(
        f"{BACKLOG_API}/tasks/{task.id}",
        json=task.to_dict(),
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()

def get_tasks_by_status(status: str) -> list:
    """Get all tasks with a specific status."""
    response = requests.get(f"{BACKLOG_API}/tasks")
    response.raise_for_status()
    return [t for t in response.json() if t.get("status") == status]

def count_tasks_in_stage(stage: Stage) -> int:
    """Count tasks currently in a stage."""
    status_map = {
        Stage.UNDERSTAND: "UNDERSTAND",
        Stage.PLAN: "PLAN",
        Stage.BUILD: "BUILD",
        Stage.VERIFY: "VERIFY",
        Stage.DEPLOY: "DEPLOY",
        Stage.BLOCKED: "BLOCKED",
    }
    tasks = get_tasks_by_status(status_map[stage])
    return len(tasks)
```

### WORKFLOW_STATE.md Integration

Add WIP counts section to state file:

```markdown
---
last_updated: 2026-02-01T12:00:00Z
active_track: feat/kanban-workflow
session_id: abc-123
---

## WIP Counts

| Stage | Count | Limit | Used | Status |
|-------|-------|-------|------|--------|
| UNDERSTAND | 2 | 5 | 40% | Normal |
| PLAN | 1 | 3 | 33% | Normal |
| BUILD | 2 | 2 | 100% | At Limit |
| VERIFY | 0 | 3 | 0% | Normal |
| DEPLOY | 0 | 2 | 0% | Normal |
| BLOCKED | 1 | 10 | 10% | Normal |

**Last WIP Update**: 2026-02-01T12:00:00Z

## Active Track
...
```

### WIP Count Update Logic

```python
def update_wip_counts() -> None:
    """Update WIP counts in WORKFLOW_STATE.md."""
    wip_data = {}
    wip_limits = get_wip_limits()  # From backlog/config.yml

    for stage in Stage:
        if stage == Stage.BLOCKED:
            continue
        count = count_tasks_in_stage(stage)
        limit = wip_limits.get(stage.value, 999)
        percentage = int(count / limit * 100) if limit > 0 else 0
        status = "At Limit" if percentage >= 100 else "Warning" if percentage >= 80 else "Normal"

        wip_data[stage.value] = {
            "count": count,
            "limit": limit,
            "percentage": percentage,
            "status": status
        }

    # Write to WORKFLOW_STATE.md
    update_workflow_state_wip_section(wip_data)
```

### Config.yml Extension

```yaml
# backlog/config.yml
project_name: "dbt-playground"
default_status: "UNDERSTAND"
statuses: ["UNDERSTAND", "PLAN", "BUILD", "VERIFY", "DEPLOY", "BLOCKED"]

# NEW: WIP Limits
wip_limits:
  understand: 5
  plan: 3
  build: 2
  verify: 3
  deploy: 2
  blocked: 10

# NEW: Enforcement Configuration
kanban_enforcement:
  enabled: true
  mode: "soft"  # soft = warnings, hard = blocks
  critical_transitions:
    - ["PLAN", "BUILD"]
    - ["BUILD", "VERIFY"]
  skip_penalty: 10
  require_bypass_for_critical: true
```

---

## Implementation Sequence

### Phase 1: Foundation (Week 1)

```
Day 1-2: Schema Design
├── Create workflow-checklist.schema.json
├── Add JSON Schema to docs/schemas/
├── Create test fixtures (valid/invalid)
└── Validate schema with ajv

Day 3-4: Backlog.md Integration
├── Test workflow_checklist field in task YAML
├── Verify API accepts checklist field
├── Create task template with default checklist
└── Migration: add empty checklist to existing tasks

Day 5: WORKFLOW_STATE.md Updates
├── Add WIP counts section to state file
├── Implement update_wip_counts() function
├── Test cross-session accuracy
└── Document state file changes
```

### Phase 2: Transition Guards (Week 2)

```
Day 1-2: Core Logic
├── Implement transition_task() function
├── Add to Supervisor agent
├── Unit tests for validation logic
└── Integration tests with Backlog.md

Day 3: Skip Detection
├── Implement skip detection logic
├── Sage integration for learning extraction
├── Skip logging to compliance.skips
└── Compliance score updates

Day 4-5: Commands
├── Create /kanban status command
├── Create /kanban transition command
├── Test command outputs
└── Documentation
```

### Phase 3: Compliance Scoring (Week 3)

```
Day 1-2: Scoring Implementation
├── Implement calculate_compliance_score()
├── Add score to task completion flow
├── Create /kanban compliance command
└── Unit tests for scoring

Day 3-4: Workflow Hub Integration
├── Add compliance widget to Hub
├── Display score on Kanban cards
├── Color coding implementation
└── Drill-down modal for details

Day 5: Refinement
├── Historical data structure
├── Aggregate metrics calculation
└── Documentation updates
```

### Phase 4: WIP Limits (Week 4)

```
Day 1-2: Configuration
├── Add wip_limits to config.yml
├── Implement get_wip_limits()
├── Config validation
└── Default limits

Day 3-4: Enforcement
├── Warning threshold (80%)
├── Hard block (100%)
├── Bypass mechanism
├── Audit trail logging

Day 5: Visualization
├── WIP indicators on Kanban lanes
├── Warning colors/icons
├── End-to-end testing
└── Documentation
```

---

## Testing Strategy

### Unit Tests

| Test Suite | Focus | Coverage Target |
|------------|-------|-----------------|
| schema_validation | JSON schema validation | 100% |
| transition_guard | Transition logic | 100% |
| compliance_scoring | Score calculation | 100% |
| wip_limits | Limit checking | 100% |

### Example Test Cases

```python
# test_transition_guard.py

def test_valid_transition_succeeds():
    """UNDERSTAND -> PLAN should succeed with complete checklist."""
    task = create_task_with_checklist(stage="UNDERSTAND", items_complete=True)
    result = transition_task(task.id, Stage.UNDERSTAND, Stage.PLAN)
    assert result.success
    assert "PLAN" in result.message

def test_invalid_transition_blocked():
    """UNDERSTAND -> BUILD should fail (skips PLAN)."""
    task = create_task_with_checklist(stage="UNDERSTAND")
    result = transition_task(task.id, Stage.UNDERSTAND, Stage.BUILD)
    assert not result.success
    assert "skip" in result.message.lower()

def test_incomplete_checklist_blocked():
    """Transition blocked when checklist incomplete."""
    task = create_task_with_checklist(stage="BUILD", items_complete=False)
    result = transition_task(task.id, Stage.BUILD, Stage.VERIFY)
    assert not result.success
    assert "incomplete" in result.message.lower()

def test_wip_limit_blocked():
    """Transition blocked when target at capacity."""
    set_wip_count(Stage.BUILD, 2)  # At limit
    set_wip_limit(Stage.BUILD, 2)

    task = create_task_with_checklist(stage="PLAN", items_complete=True)
    result = transition_task(task.id, Stage.PLAN, Stage.BUILD)
    assert not result.success
    assert "WIP limit" in result.message

def test_bypass_allows_wip_limit():
    """Bypass authorization allows exceeding WIP limit."""
    set_wip_count(Stage.BUILD, 2)
    set_wip_limit(Stage.BUILD, 2)

    task = create_task_with_checklist(stage="PLAN", items_complete=True)
    result = transition_task(
        task.id, Stage.PLAN, Stage.BUILD,
        bypass_reason="Critical hotfix required"
    )
    assert result.success
    assert len(result.warnings) > 0

def test_skip_invokes_sage():
    """Skip detection should invoke Sage."""
    task = create_task_with_checklist(stage="UNDERSTAND")
    result = transition_task(
        task.id, Stage.UNDERSTAND, Stage.BUILD,
        bypass_reason="Emergency"
    )
    assert result.sage_invoked

def test_compliance_score_calculation():
    """Compliance score calculated correctly."""
    checklist = create_checklist(
        completed_stages=3,
        skips=1
    )
    score = calculate_compliance_score(checklist)
    # (3/5 * 100) - (1 * 10) = 60 - 10 = 50
    assert score == 50
```

### Integration Tests

| Test | Description | Setup |
|------|-------------|-------|
| E2E Transition Flow | Full transition with API | Backlog.md server running |
| Cross-Session WIP | WIP accuracy across sessions | Two terminals |
| Sage Integration | Learning extraction on skip | Sage agent available |
| Hub Display | Compliance in UI | Hub server running |

### Test Data

Create fixtures in `tests/fixtures/kanban/`:

```
tests/fixtures/kanban/
├── valid_checklist.yaml      # Complete valid checklist
├── incomplete_checklist.yaml # Checklist with missing items
├── skipped_checklist.yaml    # Checklist with skip history
└── task_states/
    ├── understand_complete.yaml
    ├── plan_in_progress.yaml
    ├── build_blocked.yaml
    └── verify_approved.yaml
```

---

## Architecture Decision Records

### ADR-K1: Checklist Storage Location

**Status**: Proposed

**Context**: The workflow checklist data needs to be stored persistently and accessed
across Claude Code sessions.

**Options**:

1. **Backlog.md task file** - Inline with task YAML frontmatter
2. **Separate JSON file** - Per-task JSON in `backlog/checklists/`
3. **WORKFLOW_STATE.md** - Inline with workflow state

**Decision**: **Option 1 - Backlog.md task file**

**Rationale**:

- Single source of truth for task data
- No additional file management
- Backlog.md API handles persistence
- Natural extension of existing task schema

**Consequences**:

- Backlog.md must accept custom fields (verified: yes)
- Task YAML may become larger
- Browser UI may not display checklist (acceptable)

### ADR-K2: Enforcement Mode

**Status**: Proposed

**Context**: How strictly should workflow violations be enforced?

**Options**:

1. **Hard enforcement** - Block all violations
2. **Soft enforcement** - Warn but allow
3. **Graduated enforcement** - Start soft, move to hard

**Decision**: **Option 3 - Graduated enforcement**

**Rationale**:

- Allows learning period without friction
- Can tighten as patterns stabilize
- Bypass mechanism provides escape valve
- Matches project's learning-first philosophy

**Consequences**:

- Configuration needed for enforcement mode
- Must track when to graduate
- Some violations may slip through initially

---

## Performance Considerations

### Response Time Targets

| Operation | Target | Implementation |
|-----------|--------|----------------|
| Transition validation | <500ms | In-memory validation, async API calls |
| WIP count update | <200ms | Batch updates, caching |
| Compliance calculation | <100ms | Simple arithmetic |
| Schema validation | <50ms | Compiled JSON Schema |

### Optimization Strategies

1. **Cache WIP counts** - Refresh on transition, poll every 30s
2. **Batch API calls** - Load all tasks once per validation
3. **Lazy checklist loading** - Only load when needed
4. **Async Sage invocation** - Don't block transition for learning

---

## Monitoring and Observability

### Metrics to Track

| Metric | Collection Point | Purpose |
|--------|-----------------|---------|
| Transition success rate | transition_task() | Workflow health |
| Skip frequency | compliance.skips | Process improvement |
| Bypass usage | compliance.bypasses | Exception patterns |
| WIP utilization | wip_counts | Capacity planning |
| Compliance scores | task completion | Discipline measurement |

### Logging

```python
import logging

logger = logging.getLogger("kanban")

def log_transition(task_id: str, from_stage: Stage, to_stage: Stage, result: TransitionResult):
    logger.info(
        f"TRANSITION: {task_id} {from_stage.value} -> {to_stage.value} "
        f"success={result.success} warnings={len(result.warnings)}"
    )
    if not result.success:
        logger.warning(f"TRANSITION_BLOCKED: {task_id} - {result.message}")

def log_skip(task_id: str, skip_record: dict):
    logger.warning(
        f"SKIP_DETECTED: {task_id} {skip_record['from_stage']} -> {skip_record['to_stage']} "
        f"skipped={skip_record['skipped_stage']} reason={skip_record.get('reason', 'none')}"
    )

def log_bypass(task_id: str, bypass_record: dict):
    logger.info(
        f"BYPASS_AUTHORIZED: {task_id} type={bypass_record['type']} "
        f"stage={bypass_record['stage']} by={bypass_record['authorized_by']}"
    )
```

---

## Related Documents

| Document | Relationship |
|----------|--------------|
| `temp/2026_02_01_Discussion/kanban_workflow_report.md` | Research foundation |
| `temp/2026_02_01_Discussion/kanban_workflow_plan.md` | Implementation plan |
| `temp/2026_02_01_Discussion/kanban_workflow_PRD.md` | Product requirements |
| `docs/reference/WORKFLOW_STAGES.md` | Current workflow definition |
| `.claude/agents/supervisor.md` | Supervisor implementation |
| `backlog/config.yml` | Configuration file |

---

## Open Questions

| # | Question | Status | Decision |
|---|----------|--------|----------|
| 1 | Should bypass require Chris's explicit approval? | Open | Consider role-based bypass |
| 2 | How to handle retroactive checklist for existing tasks? | Open | Default to "migrated" status |
| 3 | Should compliance scores affect PR merge? | Deferred | Not for v1.0 |
| 4 | Integration with GitHub Projects API? | Deferred | Build-first approach |

---

*TDD Status: Draft - Ready for Review*
*Author: Technical Architect*
*Date: 2026-02-01*
