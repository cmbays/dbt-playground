---
audience: [architect, developer, supervisor]
status: draft
epic: Agent Context Management Enhancements
version: 1.0
last_updated: 2026-01-30
---

# TDD-016: Agent Context Management - Technical Design

## Overview

**Source PRD**: PRD-016-AGENT-CONTEXT-MANAGEMENT.md
**Author**: Technical Architect
**Status**: Draft
**Created**: 2026-01-30
**Updated**: 2026-01-30

### Summary

This TDD defines the technical implementation for inter-agent communication via shared artifacts, session continuity patterns, and agent knowledge documentation. The design focuses on reducing context window overhead in the Supervisor while preserving signal fidelity across agent handoffs.

**Core Principle**: Orchestrators pass file pointers, not content summaries. Sub-agents write to shared folders; downstream agents read directly.

## Architecture Overview

```
INTER-AGENT CONTEXT FLOW (v0.6 Design)

    ┌─────────────────┐
    │   SUPERVISOR    │  Passes file paths, not content summaries
    │    (super:)     │
    └────────┬────────┘
             │
             │  1. Creates feature folder
             │  2. Delegates to agents with folder path
             │  3. Each agent reads upstream reports
             │  4. Each agent writes its own report
             │
    ┌────────┴────────────────────────────────────────────────────────┐
    │                                                                  │
    │   temp/AGENT_REPORTS/[feature]/                                  │
    │   ├── PM_REPORT.md          ← Product Manager writes             │
    │   ├── ARCH_REPORT.md        ← Architect reads PM, writes this    │
    │   ├── TEST_SPEC.md          ← Tester reads ARCH, writes this     │
    │   ├── DEV_REPORT.md         ← Developer reads TEST, writes this  │
    │   ├── CODE_REVIEW.md        ← Reviewer reads DEV, writes this    │
    │   └── SECURITY_REVIEW.md    ← Security reads DEV, writes this    │
    │                                                                  │
    └─────────────────────────────────────────────────────────────────┘

             │
             │  Session boundaries
             ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │   temp/SESSION_SUMMARY_YYYY-MM-DD.md                            │
    │   - Quick Resume section (30-second context recovery)           │
    │   - Decisions made                                               │
    │   - Open questions                                               │
    │   - Agent reports generated                                      │
    └─────────────────────────────────────────────────────────────────┘
```

## Component Specifications

### Component 1: Inter-Agent Reports Structure (FR-1)

**Location**: `temp/AGENT_REPORTS/[feature-name]/`

**Purpose**: Shared artifact folder enabling direct agent-to-agent communication

**Directory Structure**:

```
temp/AGENT_REPORTS/
├── customer-analytics/           # Feature folder (kebab-case)
│   ├── PM_REPORT.md
│   ├── ARCH_REPORT.md
│   ├── TEST_SPEC.md
│   ├── DEV_REPORT.md
│   ├── CODE_REVIEW.md
│   └── SECURITY_REVIEW.md
│
├── order-metrics/                # Another feature
│   ├── PM_REPORT.md
│   └── ...
│
└── README.md                     # Documentation of structure
```

**Naming Convention**:

- Feature folders: `kebab-case` matching branch name (e.g., `feat/customer-analytics` -> `customer-analytics`)
- Report files: `UPPERCASE_UNDERSCORE.md` (consistent with existing WORKFLOW_STATE.md pattern)

**Report Templates**:

See [Templates Section](#templates) for each report template.

### Component 2: Session Summaries (FR-2)

**Location**: `temp/SESSION_SUMMARY_YYYY-MM-DD.md`

**Purpose**: Enable rapid context recovery (target: <60 seconds)

**Naming Convention**: Date-based naming allows multiple summaries per day if needed (append `-N` suffix)

**Generation Trigger**: Explicit user command (not automatic)

**Commands**:

```text
super: end session
super: save session summary
super: checkpoint
```

**Integration with WORKFLOW_STATE.md**:

- SESSION_SUMMARY is a snapshot (point-in-time)
- WORKFLOW_STATE is authoritative (always current)
- SESSION_SUMMARY references WORKFLOW_STATE but doesn't replace it

### Component 3: Job Description Documentation (FR-3)

**Location**: `docs/for_chris/AGENT_JOB_DESCRIPTIONS.md`

**Purpose**: Human-readable agent roles for learning audience

**Content Structure**:

| Section | Content |
|---------|---------|
| Quick Reference Table | Agent -> Human Job Title -> One-Liner |
| Detailed Sections | Each agent with responsibilities, when to invoke, example prompts |
| Decision Tree | "I want to do X" -> Use this agent |

### Component 4: LEARNINGS.md Pattern Entry (FR-4)

**Location**: `docs/reference/LEARNINGS.md` (existing file)

**Section**: New entry under "Agent Orchestration" section

**Pattern Name**: "Context Window Discipline for Multi-Agent Workflows"

### Component 5: Agent Knowledge Consolidation Doc (FR-5)

**Location**: `docs/for_chris/AGENT-KNOWLEDGE-CONSOLIDATION.md`

**Purpose**: Educational document explaining knowledge architecture trade-offs

**Content Outline**:

1. The Problem: Knowledge fragmentation (~51,000 tokens across 51+ files)
2. Case Study: Claudie's evolution (v1 -> v2 -> v3)
3. Trade-offs: Fragmented vs. Consolidated
4. Our Current Architecture: Why it works for now
5. Signs it's time to consolidate
6. Potential consolidation strategies (preview of v0.7)

## Templates

### PM_REPORT.md Template

```markdown
# PM Report: [Feature Name]

**Feature**: [feature-name]
**PRD**: [link to PRD]
**Date**: YYYY-MM-DD
**Author**: Product Manager

## Scope Summary

[2-3 sentence summary of what we're building and why]

## Acceptance Criteria

- [ ] AC-1: [description]
- [ ] AC-2: [description]
- [ ] AC-3: [description]

## Key Decisions Made

| Decision | Rationale |
|----------|-----------|
| [decision] | [why] |

## Out of Scope

- [explicitly excluded item 1]
- [explicitly excluded item 2]

## Open Questions for Architect

- [question 1]
- [question 2]

## Dependencies

- [dependency on other features/systems]

---
*For Architect: Read this report, then create ARCH_REPORT.md*
```

### ARCH_REPORT.md Template

```markdown
# Architecture Report: [Feature Name]

**Feature**: [feature-name]
**TDD**: [link to TDD]
**Date**: YYYY-MM-DD
**Author**: Technical Architect

## Design Summary

[2-3 sentence summary of technical approach]

## Key Design Decisions

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| [decision] | [A, B, C] | [B] | [why B] |

## Components Created/Modified

| Component | Change Type | Purpose |
|-----------|-------------|---------|
| [model.sql] | Create | [description] |

## Integration Points

- Upstream: [what this depends on]
- Downstream: [what depends on this]

## Risks Identified

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [risk] | Low/Med/High | Low/Med/High | [mitigation] |

## Open Questions for Tester

- [testing question 1]
- [testing question 2]

---
*For Tester: Read PM_REPORT.md and this report, then create TEST_SPEC.md*
```

### TEST_SPEC.md Template

```markdown
# Test Specification: [Feature Name]

**Feature**: [feature-name]
**Date**: YYYY-MM-DD
**Author**: Quality Tester

## Test Summary

| Category | Count | Coverage Target |
|----------|-------|-----------------|
| Schema Tests | N | 100% columns |
| Grain Tests | N | All fact tables |
| Referential Tests | N | All FKs |
| Data Quality | N | Key measures |

## Test Matrix

### Schema Tests

| Model | Column | Test | Expected |
|-------|--------|------|----------|
| [model] | [column] | unique | Pass |
| [model] | [column] | not_null | Pass |

### Grain Tests

| Model | Grain Columns | Test Type |
|-------|---------------|-----------|
| [fact] | [col1, col2] | unique_combination |

### Data Quality Tests

| Test Name | Description | Threshold |
|-----------|-------------|-----------|
| [test] | [what it validates] | [pass criteria] |

## Edge Cases Identified

- [edge case 1]: [how tested]
- [edge case 2]: [how tested]

## Test Commands

```bash
# Run all tests for this feature
dbt test --select tag:[feature-name]

# Run specific model tests
dbt test --select [model_name]
```

---
*For Developer: Read all upstream reports, then implement and create DEV_REPORT.md*

```

### DEV_REPORT.md Template

```markdown
# Development Report: [Feature Name]

**Feature**: [feature-name]
**Branch**: [branch-name]
**Date**: YYYY-MM-DD
**Author**: Developer

## Implementation Summary

[2-3 sentence summary of what was implemented]

## Files Changed

| File | Change | Lines | Notes |
|------|--------|-------|-------|
| [path] | Create | +N | [notes] |
| [path] | Modify | +N/-M | [notes] |

## Implementation Decisions

| Decision | Rationale |
|----------|-----------|
| [decision] | [why] |

## Deviations from TDD

| TDD Spec | Actual Implementation | Reason |
|----------|----------------------|--------|
| [spec] | [what was done] | [why different] |

## Blockers Resolved

- [blocker 1]: [how resolved]

## Test Results

```bash
# Command run
dbt build --select [models]

# Results
All N tests passed
```

## Open Issues for Reviewer

- [issue for review 1]
- [issue for review 2]

---
*For Reviewer: Read all upstream reports, review code, then create CODE_REVIEW.md*

```

### CODE_REVIEW.md Template

```markdown
# Code Review Report: [Feature Name]

**Feature**: [feature-name]
**PR**: #[N]
**Date**: YYYY-MM-DD
**Author**: Code Reviewer

## Review Summary

**Verdict**: APPROVED / CHANGES_REQUESTED / BLOCKER

## Checklist

- [ ] Code follows established patterns
- [ ] Tests are comprehensive
- [ ] Documentation is complete
- [ ] No security concerns
- [ ] Performance acceptable

## Findings

### Critical (Must Fix)

_None_ / [list]

### Suggestions (Should Consider)

- [suggestion 1]
- [suggestion 2]

### Positive Notes

- [what was done well]

## Files Reviewed

| File | Status | Notes |
|------|--------|-------|
| [path] | OK / Issue | [notes] |

---
*Verdict: [APPROVED/CHANGES_REQUESTED]*
```

### SECURITY_REVIEW.md Template

```markdown
# Security Review Report: [Feature Name]

**Feature**: [feature-name]
**Date**: YYYY-MM-DD
**Author**: Security Reviewer

## Review Summary

**Risk Level**: LOW / MEDIUM / HIGH / CRITICAL

## Security Checklist

- [ ] No hardcoded credentials
- [ ] PII handled appropriately
- [ ] Input validation present
- [ ] SQL injection prevention
- [ ] Access control verified

## Findings

### Vulnerabilities

| ID | Severity | Description | Recommendation |
|----|----------|-------------|----------------|
| S-1 | [severity] | [description] | [fix] |

### Compliance Notes

- [compliance observation]

## Verdict

**APPROVED** / **BLOCKER**: [reason]

---
*Security review complete*
```

### SESSION_SUMMARY Template

```markdown
# Session Summary: YYYY-MM-DD

## Quick Resume

- **Active Track**: [feature branch name]
- **Last Action**: [what was completed]
- **Next Action**: [what should happen next]
- **Blocking Issues**: [any blockers or "None"]

## Context Snapshot

**Where We Are**:
[1-2 sentences describing current state]

**What Just Happened**:
[Brief summary of session work]

**What's Next**:
[Immediate next steps]

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| [decision] | [why] |

## Open Questions

- [question 1]
- [question 2]

## Agent Reports Generated

| Report | Location |
|--------|----------|
| PM_REPORT | temp/AGENT_REPORTS/[feature]/PM_REPORT.md |
| ARCH_REPORT | temp/AGENT_REPORTS/[feature]/ARCH_REPORT.md |

## Blockers

- [any blockers for next session or "None"]

## WORKFLOW_STATE Reference

See `temp/WORKFLOW_STATE.md` for authoritative track status.

---
*Session ended: HH:MM*
```

## Agent Updates Required

### Supervisor Updates

**File**: `.claude/agents/supervisor.md`

**Changes**:

1. Add Inter-Agent Reports flow to workflow state management
2. Add Session Summary generation workflow
3. Update artifact verification to check for agent reports

**New Section**: Inter-Agent Reports Management

```markdown
## Inter-Agent Reports Management

When starting a new feature workflow:

1. Create feature folder: `temp/AGENT_REPORTS/[feature-name]/`
2. Pass folder path to each agent in delegation
3. Instruct agents to read upstream reports before starting
4. Verify report exists before allowing phase transition

### Folder Creation

On receiving new feature request:
```bash
mkdir -p temp/AGENT_REPORTS/[feature-name]
```

### Delegation Pattern

Instead of:

```text
pm: Create PRD for customer analytics. [includes all context in message]
```

Use:

```text
pm: Create PRD for customer analytics.
    - Write PM_REPORT.md to: temp/AGENT_REPORTS/customer-analytics/
    - PRD location: docs/specs/PRD-XXX-CUSTOMER-ANALYTICS.md
```

### Phase Transition Verification (Updated)

| Transition | Required Artifacts |
|------------|-------------------|
| PM -> Architect | PM_REPORT.md exists in feature folder |
| Architect -> Tester | ARCH_REPORT.md exists in feature folder |
| Tester -> Developer | TEST_SPEC.md exists in feature folder |
| Developer -> Reviewer | DEV_REPORT.md exists in feature folder |

```

### PM Updates

**File**: `.claude/agents/product-manager.md`

**Add Section**: Report Output

```markdown
## Report Output

When working on a feature tracked in AGENT_REPORTS:

1. Write `PM_REPORT.md` to `temp/AGENT_REPORTS/[feature]/`
2. Use template from TDD-016
3. Include "For Architect" handoff section
4. Reference PRD location
```

### Architect Updates

**File**: `.claude/agents/architect.md`

**Add Section**: Report I/O

```markdown
## Report I/O

When working on a feature tracked in AGENT_REPORTS:

1. **Read**: `temp/AGENT_REPORTS/[feature]/PM_REPORT.md`
2. **Write**: `temp/AGENT_REPORTS/[feature]/ARCH_REPORT.md`
3. Use template from TDD-016
4. Include "For Tester" handoff section
```

### Tester Updates

**File**: `.claude/agents/tester.md` (or `dbt-tester.md`)

**Add Section**: Report I/O

```markdown
## Report I/O

When working on a feature tracked in AGENT_REPORTS:

1. **Read**: PM_REPORT.md, ARCH_REPORT.md
2. **Write**: `temp/AGENT_REPORTS/[feature]/TEST_SPEC.md`
3. Use template from TDD-016
```

### Developer Updates

**File**: `.claude/agents/developer.md` (or `dbt-developer.md`)

**Add Section**: Report I/O

```markdown
## Report I/O

When working on a feature tracked in AGENT_REPORTS:

1. **Read**: All upstream reports (PM, ARCH, TEST)
2. **Write**: `temp/AGENT_REPORTS/[feature]/DEV_REPORT.md`
3. Use template from TDD-016
```

### Code Reviewer Updates

**File**: `.claude/agents/code-reviewer.md`

**Add Section**: Report I/O

```markdown
## Report I/O

When working on a feature tracked in AGENT_REPORTS:

1. **Read**: All upstream reports
2. **Write**: `temp/AGENT_REPORTS/[feature]/CODE_REVIEW.md`
3. Post findings to PR AND to report file
```

### Security Reviewer Updates

**File**: `.claude/agents/security-reviewer.md`

**Add Section**: Report I/O

```markdown
## Report I/O

When working on a feature tracked in AGENT_REPORTS:

1. **Read**: DEV_REPORT.md (minimum), all upstream if time permits
2. **Write**: `temp/AGENT_REPORTS/[feature]/SECURITY_REVIEW.md`
```

## Integration Points

### Integration with WORKFLOW_STATE.md

The agent reports folder integrates with existing workflow state:

```yaml
### Track: feat/customer-analytics (ACTIVE)
- **Phase**: DEVELOPMENT
- **Agent Reports**: temp/AGENT_REPORTS/customer-analytics/
  - [x] PM_REPORT.md
  - [x] ARCH_REPORT.md
  - [x] TEST_SPEC.md
  - [ ] DEV_REPORT.md (in progress)
  - [ ] CODE_REVIEW.md
  - [ ] SECURITY_REVIEW.md
```

### Integration with Existing Artifacts

| Artifact | Relationship to Agent Reports |
|----------|------------------------------|
| PRD (docs/specs/) | PM_REPORT.md summarizes and links to PRD |
| TDD (docs/specs/) | ARCH_REPORT.md summarizes and links to TDD |
| Test Plan (temp/) | TEST_SPEC.md may replace or supplement v*_TESTING.md |
| CHANGELOG | Updated based on DEV_REPORT.md |

### Retention Policy

- **During Feature Development**: All reports retained
- **After PR Merge**: Reports cleaned up (preserved in git history via PR)
- **Session Summaries**: Retained for 7 days, then cleaned

## Implementation Sequence

### Phase 1: Foundation (Day 1)

1. [ ] Create `temp/AGENT_REPORTS/README.md` with structure documentation
2. [ ] Create all 6 report templates as standalone files in `docs/templates/`
3. [ ] Create SESSION_SUMMARY template

### Phase 2: Agent Updates (Day 2)

4. [ ] Update `supervisor.md` with Inter-Agent Reports Management section
5. [ ] Update `product-manager.md` with Report Output section
6. [ ] Update `architect.md` with Report I/O section
7. [ ] Update `tester.md` / `dbt-tester.md` with Report I/O section
8. [ ] Update `developer.md` / `dbt-developer.md` with Report I/O section
9. [ ] Update `code-reviewer.md` with Report I/O section
10. [ ] Update `security-reviewer.md` with Report I/O section

### Phase 3: Documentation (Day 3)

11. [ ] Create `docs/for_chris/AGENT_JOB_DESCRIPTIONS.md`
12. [ ] Add pattern entry to `docs/reference/LEARNINGS.md`
13. [ ] Create `docs/for_chris/AGENT-KNOWLEDGE-CONSOLIDATION.md`

### Phase 4: Integration (Day 4)

14. [ ] Update CLAUDE.md with AGENT_REPORTS directory documentation
15. [ ] Update AGENTS.md with inter-agent report workflow
16. [ ] Test workflow with a sample feature

## Testing Strategy

### Manual Testing Workflow

1. **Test Feature Folder Creation**:

   ```bash
   # Create test folder
   mkdir -p temp/AGENT_REPORTS/test-feature

   # Verify structure
   ls temp/AGENT_REPORTS/
   ```

2. **Test Report Generation**:
   - Invoke PM with explicit report output instruction
   - Verify PM_REPORT.md created with correct template
   - Invoke Architect with instruction to read PM_REPORT
   - Verify ARCH_REPORT.md references PM decisions

3. **Test Session Summary**:
   - Run `super: save session summary`
   - Verify SESSION_SUMMARY_YYYY-MM-DD.md created
   - Verify Quick Resume section enables <60 second context recovery

4. **Test Downstream Agent Context**:
   - Start as Developer on feature with all upstream reports
   - Verify Developer can reference PM, ARCH, TEST decisions
   - Verify no context loss compared to Supervisor relay

### Validation Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Report template compliance | Manual review | 100% fields populated |
| Context recovery time | Timed test | <60 seconds |
| Signal preservation | Compare report vs relay | Qualitative improvement |
| Agent adoption | Reports created | 100% for tracked features |

### Test Scenarios

**Scenario 1: Full Workflow with Reports**

```text
1. super: Start new feature "test-context-management"
2. Verify: temp/AGENT_REPORTS/test-context-management/ created
3. pm: Create PRD and PM_REPORT for test feature
4. Verify: PM_REPORT.md exists with correct template
5. arch: Design and create ARCH_REPORT (reads PM_REPORT)
6. Verify: ARCH_REPORT.md references PM decisions
7. Continue through all phases...
```

**Scenario 2: Session Resume with Summary**

```text
1. End session with: super: save session summary
2. Verify: SESSION_SUMMARY_YYYY-MM-DD.md created
3. Start new session
4. Read session summary
5. Measure: Time to understand context
6. Target: <60 seconds
```

**Scenario 3: Cross-Session Continuity**

```text
1. Session A: Complete PM and ARCH phases
2. End Session A with summary
3. Session B: Resume
4. Verify: Tester can read all upstream reports
5. Verify: No context loss from Session A
```

## Security Considerations

- **No PII in Reports**: Reports should reference patient/provider by ID, not names
- **Sensitive Decisions**: Security-relevant decisions in SECURITY_REVIEW.md only
- **Git History**: Reports in temp/ are excluded from permanent history after cleanup

## Performance Considerations

- **File I/O**: Minimal impact (small markdown files)
- **Context Window**: Significant reduction in Supervisor token usage
- **Disk Space**: Negligible (<100KB per feature)

## Dependencies

- Existing agent persona files
- WORKFLOW_STATE.md infrastructure
- temp/ directory structure
- docs/for_chris/ directory

## Open Questions

1. **Report Cleanup Timing**: Should reports be deleted immediately after PR merge, or retained for a grace period?
   - **Recommendation**: Clean after merge (preserved in git history)

2. **Parallel Features**: How to handle multiple active features with reports?
   - **Answer**: Each feature gets its own folder; WORKFLOW_STATE tracks active_track

3. **Partial Workflows**: What if a feature skips phases (e.g., --skip-prd)?
   - **Answer**: Create minimal placeholder report or skip that report file

## Future Enhancements (v0.7+)

- **FR-6**: Handbook Consolidation evaluation (separate TDD)
- **FR-7**: Vector Search over LEARNINGS.md (separate TDD)
- **Automated Summary**: Consider auto-generating session summaries on session end
- **Report Metrics**: Track which reports are most referenced

## Related

- **PRD**: `docs/specs/PRD-016-AGENT-CONTEXT-MANAGEMENT.md`
- **Supervisor**: `.claude/agents/supervisor.md`
- **WORKFLOW_STATE**: `temp/WORKFLOW_STATE.md`
- **LEARNINGS**: `docs/reference/LEARNINGS.md`
- **FOR_CHRIS**: `docs/for_chris/`

---

**Document Version**: 1.0
**Last Updated**: 2026-01-30
**Status**: Draft - Ready for review
