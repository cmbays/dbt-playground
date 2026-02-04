# Debug Session Report: [Bug Title]

## Session Metadata

| Field | Value |
|-------|-------|
| **Session ID** | session-YYYY-MM-DD-HHmmss |
| **Agent Name** | [your-agent-name] |
| **Status** | IN_PROGRESS / COMPLETE / BLOCKED |
| **Started** | YYYY-MM-DD HH:mm:ss UTC |
| **Ended** | YYYY-MM-DD HH:mm:ss UTC |
| **Duration** | Xh Ym |

## Bug Reference

| Field | Value |
|-------|-------|
| **Original Report** | [Issue #N / LESSONS.md reference / user report] |
| **Severity** | Critical / High / Medium / Low |
| **Affected Area** | [component/feature/file] |
| **Environment** | [Tier 1 / Tier 2 / Tier 3] |

## Investigation Scope

**My Focus Area**: [Frontend / Backend / Data / Infrastructure]

**Explicitly NOT investigating**:
- [area 1 - handled by Agent X]
- [area 2 - out of scope]

---

## Reproduction

### Steps to Reproduce

1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Behavior

[What should happen]

### Actual Behavior

[What actually happens]

### Reproduction Confirmed

- [ ] I can reproduce this bug
- [ ] Reproduction rate: [100% / intermittent / specific conditions]
- [ ] Environment: [local / staging / production]

---

## Investigation Log

### HH:MM - [Action Taken]

**What I checked**: [description]

**What I found**: [observation]

**Conclusion**: [interpretation]

---

### HH:MM - [Next Action]

**What I checked**: [description]

**What I found**: [observation]

**Conclusion**: [interpretation]

---

## Findings

### Evidence Collected

| Evidence | Location | Relevance |
|----------|----------|-----------|
| [error message] | [file:line] | [why it matters] |
| [log entry] | [log file] | [what it indicates] |
| [behavior] | [UI/API] | [symptom vs cause] |

### Files Involved

| File | Role in Bug | Change Needed? |
|------|-------------|----------------|
| [file1.js] | [triggers error] | Yes / No / Unknown |
| [file2.sql] | [data source] | Yes / No / Unknown |

### Connected Systems

- **Upstream**: [what feeds into this]
- **Downstream**: [what this affects]
- **Shared dependencies**: [common libraries/data]

---

## Root Cause Analysis

### Classification

- [ ] **ROOT CAUSE**: Fixing this will resolve the bug permanently
- [ ] **SYMPTOM**: This is a visible effect of a deeper issue

### If Root Cause

**Root cause identified**: [description]

**Why this is root cause**:
- [reasoning 1]
- [reasoning 2]

**Confidence level**: High / Medium / Low

### If Symptom

**Visible symptom**: [what appears broken]

**Deeper issue**: [what actually needs fixing]

**Why treating symptom is insufficient**:
- [consequence 1]
- [consequence 2]

**Recommendation**: Investigate [X] to find root cause

---

## Proposed Fix

### Files to Modify

| File | Change | Risk Level |
|------|--------|------------|
| [file] | [specific change] | Low / Med / High |

### Files NOT Being Touched

| File | Reason |
|------|--------|
| [file] | [why intentionally left alone] |

### Implementation Notes

```
[code snippet or pseudocode showing fix approach]
```

### Verification Plan

1. [How to verify fix works]
2. [How to verify no regressions]
3. [Edge cases to test]

---

## Cross-Scope Observations

### For Other Agents

**For Agent [Name]** (if applicable):
- [observation that may affect their scope]
- [question or concern]

### Dependencies Discovered

- [Agent X] needs to complete [task] before my fix can work
- My finding affects [Agent Y]'s investigation at [specific point]

---

## Summary

### Final Diagnosis

[2-3 sentence summary of what you found]

### Recommendation

- [ ] **FIX**: Ready to implement fix
- [ ] **DEFER**: Needs more investigation by [agent/area]
- [ ] **MERGE**: Combine findings with other agents first
- [ ] **ESCALATE**: Beyond current scope, needs [expertise/access]

### Blockers

[List any blockers preventing completion]

---

## Post-Fix (Complete After Implementation)

### Changes Made

| File | Change | Why |
|------|--------|-----|
| [file] | [what changed] | [reasoning] |

### Verification Results

- [ ] Original reproduction steps no longer trigger bug
- [ ] Related functionality still works
- [ ] No new errors in logs
- [ ] Tests pass

### LESSONS.md Update

- [ ] Pattern documented in LESSONS.md
- [ ] Entry reference: [LESSONS.md section]

---

*Template version: 1.0 | WAVE3-001*
