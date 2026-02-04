---
audience: [architect, developer, multi-agent]
priority: medium
size: small
dependencies: []
last_updated: 2026-02-04
status: approved
tags: [architecture, debugging, wave3, workflow, efficiency]
---

# ADR-022: Expedited Path Gating

**Status**: Approved
**Date**: 2026-02-04
**Deciders**: Architect, Planner
**Related Issue**: #226
**Wave 3 Task**: WAVE3-004

---

## Context

The Phase 1 Debug Agent protocol defines a rigorous 7-step process:

1. Reproduce First
2. Research the Blast Radius
3. Present Findings Before Fixing
4. Root Cause or Symptom?
5. Propose the Fix
6. Implement and Verify
7. Update the Knowledge Base

This rigor is valuable for complex bugs but creates friction for trivial bugs:

| Bug Type | Example | 7-Step Time | Actual Fix Time |
|----------|---------|-------------|-----------------|
| Complex | Race condition in distributed system | 2-4 hours | 1-2 hours |
| Medium | Null pointer in business logic | 30-60 min | 15-30 min |
| **Trivial** | Typo in variable name | **30-60 min** | **2 min** |

For trivial bugs, the protocol overhead (reproduction, blast radius research, formal findings) exceeds the fix time by 10-30x. This creates:

1. **Developer frustration**: Feels bureaucratic for obvious fixes
2. **Time waste**: Protocol steps add no value for simple bugs
3. **Protocol abandonment**: Developers skip protocol entirely, losing rigor for complex bugs

Wave 3 must define when expedited debugging is appropriate without undermining protocol discipline for complex bugs.

## Decision

**Gate expedited path on 4 criteria: single-file, no API contracts, no migrations, no dependencies.**

### Expedited Path Criteria

A bug qualifies for the 3-step expedited path if ALL of the following are true:

| Criterion | Question | Expedited if... |
|-----------|----------|-----------------|
| **Single-file** | Is the bug isolated to one file? | Yes, only one file needs changes |
| **No API contracts** | Does the fix change any API signatures, request/response formats, or public interfaces? | No API changes |
| **No migrations** | Does the fix require database schema changes, data migrations, or config changes? | No migrations |
| **No dependencies** | Does the fix affect other components, services, or downstream consumers? | No dependencies |

### Expedited Path (3 Steps)

If all 4 criteria are met:

```markdown
## Expedited Debug Protocol

### Step E1: Quick Verify
- Confirm bug exists (quick reproduction)
- Confirm single-file scope
- Confirm no API/migration/dependency impact

### Step E2: Fix and Test
- Make the change
- Run relevant tests
- Verify fix locally

### Step E3: Document
- Commit with descriptive message
- Update LESSONS.md if pattern is reusable
- Note: "Expedited fix, single-file typo in {file}"
```

### Decision Tree

```text
Is bug in single file?
├── No → Full 7-step protocol
└── Yes → Does fix change API contracts?
    ├── Yes → Full 7-step protocol
    └── No → Does fix require migrations?
        ├── Yes → Full 7-step protocol
        └── No → Does fix have downstream dependencies?
            ├── Yes → Full 7-step protocol
            └── No → ✅ EXPEDITED PATH (3 steps)
```

### Examples

| Bug | Single-file | No API | No Migration | No Deps | Path |
|-----|-------------|--------|--------------|---------|------|
| Typo in error message | Yes | Yes | Yes | Yes | **Expedited** |
| Missing null check (one function) | Yes | Yes | Yes | Yes | **Expedited** |
| Wrong variable name | Yes | Yes | Yes | Yes | **Expedited** |
| Off-by-one in loop | Yes | Yes | Yes | Yes | **Expedited** |
| API returns wrong status code | Yes | **No** | Yes | Yes | Full |
| Missing column in query | Yes | Yes | **No** | Yes | Full |
| Bug in shared utility | Yes | Yes | Yes | **No** | Full |
| Bug spans 2 files | **No** | Yes | Yes | Yes | Full |
| UI + API fix needed | **No** | **No** | Yes | Yes | Full |

## Rationale

### Why 4 Criteria

1. **Single-file**: Multi-file bugs have hidden dependencies; blast radius research is valuable
2. **No API contracts**: API changes affect consumers; need formal review
3. **No migrations**: Data changes are irreversible; need full protocol
4. **No dependencies**: Downstream impact requires blast radius analysis

### Why Strict AND (All Must Pass)

Conservative gating ensures expedited path is truly safe:
- False positive (expedited when shouldn't): Regression risk
- False negative (full when could expedite): Minor time cost

**Decision**: Prefer false negatives (extra protocol time) over false positives (regression risk).

### Why 3 Steps (Not 2 or 4)

| Step Count | Issue |
|------------|-------|
| 1 step | No verification, no documentation |
| 2 steps | Missing either verify or document |
| **3 steps** | Quick verify + fix + document (minimum viable) |
| 4+ steps | Approaches full protocol overhead |

## Consequences

### Positive

- **Reduced friction**: Trivial bugs fixed in minutes, not hours
- **Protocol preservation**: Complex bugs still get full rigor
- **Clear decision rules**: No ambiguity about when to expedite
- **Audit trail**: Expedited fixes still documented in commits

### Negative

- **Some "simple" bugs may need full protocol**: Edge cases where criteria pass but fix is complex
- **Gating adds 1-2 minutes**: Must evaluate 4 criteria before starting
- **Risk of misjudgment**: Developer might think bug is simple when it's not
- **LESSONS.md less detailed**: Expedited fixes have minimal documentation

### Mitigation

| Negative | Mitigation |
|----------|------------|
| Edge cases | If uncertain on any criterion, use full protocol |
| Gating overhead | Criteria check becomes second nature with practice |
| Misjudgment | If fix takes >15 min, escalate to full protocol |
| Less documentation | Require commit message to include expedited reason |

## Alternatives Considered

### Alternative 1: No Expedited Path

**Pros**: Maximum rigor, consistent process
**Cons**: Developer frustration, time waste, protocol abandonment
**Rejected**: Perfect is enemy of good; trivial bugs need trivial process

### Alternative 2: Time-Based Gating (Fix if <5 minutes)

**Pros**: Simple rule
**Cons**: Encourages rushing, no safety criteria, gaming
**Rejected**: Time is outcome, not input; can't know fix time upfront

### Alternative 3: Severity-Based Gating (Low severity = expedited)

**Pros**: Aligns with bug triage
**Cons**: Severity doesn't correlate with complexity; low-severity bug can be complex
**Rejected**: Complexity determines protocol, not business impact

### Alternative 4: Developer Discretion (Trust the developer)

**Pros**: Maximum flexibility
**Cons**: Inconsistent, no accountability, protocol erosion
**Rejected**: Explicit criteria prevent subjective shortcuts

## Implementation Notes

1. **Checklist in DEBUG_REPORTS/**: Add expedited checklist template
2. **Commit format**: `fix(expedited): {description} [single-file, {file}]`
3. **Escalation trigger**: If fix exceeds 15 minutes, stop and switch to full protocol
4. **Metric tracking**: Future: track expedited vs full ratio to tune criteria
5. **Training**: Include examples in onboarding for when to expedite

### Expedited Checklist Template

```markdown
## Expedited Path Checklist

**Bug**: {brief description}
**Date**: {date}

### Gating Criteria

- [ ] Single-file: Bug isolated to `{filename}`
- [ ] No API contracts: Fix does not change public interfaces
- [ ] No migrations: Fix does not require schema/data changes
- [ ] No dependencies: Fix does not affect other components

**All criteria met?** Yes → Proceed with expedited path

### Quick Fix

**Change**: {what was changed}
**Test**: {what was tested}
**Commit**: {commit hash}

### LESSONS Entry (if applicable)

{Optional: pattern to remember}
```

## Related

- [ADR-019: Debug Session Persistence](ADR-019-debug-session-persistence.md) - Full session structure
- [x_post_backend.txt](../../temp/vibe_coding/x_post_backend.txt) - Original 7-step protocol
- [WAVE3_TASK_QUEUE.md](../../temp/vibe_coding/WAVE3_TASK_QUEUE.md) - WAVE3-002 expedited path task

---

*Approved as part of Wave 3 Backend Leveling (WAVE3-004)*
