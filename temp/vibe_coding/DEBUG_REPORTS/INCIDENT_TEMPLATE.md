---
audience: [architect, developer, on-call]
priority: high
size: medium
status: active
tags: [incident, postmortem, root-cause-analysis]
wave3_task: WAVE3-017
---

# Incident Report Template

**Version**: 1.0.0
**Created**: 2026-02-04
**Task**: WAVE3-017
**Purpose**: Structured template for production incident response and learning capture

---

## Instructions

Copy this template for each incident. Fill in all sections. Empty sections indicate incomplete incident response.

**Severity Levels**:
| Level | Definition | Response Time | Examples |
|-------|------------|---------------|----------|
| **Critical** | Service down, data loss risk | < 15 min | Database corruption, security breach |
| **High** | Major feature broken, significant user impact | < 1 hour | Authentication failure, payment down |
| **Medium** | Feature degraded, workaround available | < 4 hours | Slow queries, partial data missing |
| **Low** | Minor issue, minimal user impact | < 24 hours | UI glitch, log warning |

---

# Incident Report: INCIDENT-YYYY-MM-DD-NNN

## 1. Header

| Field | Value |
|-------|-------|
| **Title** | [Brief description of incident] |
| **Incident ID** | INCIDENT-YYYY-MM-DD-NNN |
| **Reported Time** | YYYY-MM-DD HH:MM UTC |
| **Resolved Time** | YYYY-MM-DD HH:MM UTC |
| **Duration** | X hours Y minutes |
| **Severity** | Critical / High / Medium / Low |
| **Affected Systems** | [List systems/services] |
| **Affected Users** | [Number or percentage] |
| **Incident Commander** | [Name] |
| **Related Issues** | #NNN, #NNN |

---

## 2. What Happened

### User-Facing Impact
_Describe the impact in plain language that non-technical stakeholders can understand._

### Business Impact
| Impact Type | Measurement |
|-------------|-------------|
| Revenue impact | $X lost / delayed |
| Data impact | X records affected |
| Availability impact | X% downtime |
| User impact | X users affected |

---

## 3. Timeline

| Time (UTC) | Event | Actor |
|------------|-------|-------|
| T+0 | [First symptom reported/detected] | [Who noticed] |
| T+X min | [Alert triggered / User report] | [System/Person] |
| T+X min | [Incident declared] | [Person] |
| T+X min | [Initial diagnosis] | [Team] |
| T+X min | [Root cause identified] | [Person] |
| T+X min | [Fix applied] | [Person] |
| T+X min | [Fix verified] | [Person] |

---

## 4. Root Cause Analysis

### Step 1: Symptom Documentation
_What symptoms were observed?_

### Step 2: Reproduction
- [ ] Reproducible in production
- [ ] Reproducible in staging
- [ ] Reproducible locally
- [ ] Cannot reproduce (intermittent)

### Step 3: Hypothesis Formation (CRITICAL)
_List all hypotheses considered._

| # | Hypothesis | Evidence For | Evidence Against | Status |
|---|------------|--------------|------------------|--------|
| 1 | [Hypothesis] | [Evidence] | [Evidence] | Rejected / Confirmed |

### Step 4: Root Cause vs. Symptom Classification (CRITICAL)

**Symptoms** (effects, not causes):
- [Symptom 1]: [Description]

**Contributing Factors** (made it worse, but not the cause):
- [Factor 1]: [Description]

**ROOT CAUSE** (the actual cause):
> [One clear statement of the root cause]

### Why This Wasn't Caught in Testing

- [ ] No test coverage for this scenario
- [ ] Test environment differs from production
- [ ] Edge case not considered
- [ ] Load/scale not tested
- [ ] Other: [Explanation]

---

## 5. Fix Applied

### Immediate Fix
_What was done to restore service?_

**Verification performed**:
- [ ] Health checks passing
- [ ] Error rate returned to baseline
- [ ] Users confirmed working
- [ ] Monitoring confirmed stable

### Rollback Instructions
_Document how to undo the fix if it causes new issues._

---

## 6. Prevention

### Lessons Extracted
_What did we learn? Add to LESSONS.md._

| Lesson | Category | Added |
|--------|----------|-------|
| [Lesson 1] | [Category] | [ ] Yes |

### Monitoring Improvements
| Alert | Condition | Threshold |
|-------|-----------|-----------|
| [Alert name] | [What triggers] | [Value] |

### Process/Code Changes
| Change | Description | Issue |
|--------|-------------|-------|
| [Change] | [Description] | #NNN |

---

## 7. Postmortem Checklist

### Completeness
- [ ] All timeline events documented
- [ ] Root cause clearly identified
- [ ] Root vs. symptom classified
- [ ] Why not caught answered
- [ ] Fix documented with rollback
- [ ] Prevention items have owners

### Action Items
- [ ] LESSONS.md updated
- [ ] Monitoring alert created
- [ ] Runbook created/updated
- [ ] Follow-up bugs created
- [ ] Team training scheduled

### Communication
- [ ] Stakeholders notified
- [ ] Postmortem shared with team
- [ ] Customer communication sent

### Sign-off
| Role | Name | Date |
|------|------|------|
| Incident Commander | | |
| Engineering Lead | | |

---

## Related Documentation

- [DEPLOYMENT_VALIDATION_CHECKLIST.md](./DEPLOYMENT_VALIDATION_CHECKLIST.md) - Pre-deployment gates
- [LEARNINGS.md](../../../docs/reference/LEARNINGS.md) - Pattern library

---

*Incident Template v1.0.0 | Wave 3 Task: WAVE3-017*
