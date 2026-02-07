---
audience: [architect, pm, developer]
priority: high
size: large
status: active
tags: [deployment, validation, gates, tier-promotion]
wave3_task: WAVE3-015
---

# Deployment Validation Gates Checklist

**Version**: 1.0.0
**Created**: 2026-02-04
**Task**: WAVE3-015
**Purpose**: Quality gate ensuring bugs are caught before production deployment

---

## Overview

This checklist provides validation gates for tier promotions in the Vibe Code maturation pathway. Each gate must pass before promoting a project to the next tier.

---

## Tier 1 to Tier 2 Gates (Local MVP to Staging/Small Production)

Use this checklist when moving from local development to cloud-hosted staging or small production (10-100 users).

### Gate T1-1: Schema Validation

- [ ] **PASS**: All schema validation checks return expected values

### Gate T1-2: Migration Reversibility

- [ ] **PASS**: All migrations have tested rollback scripts

### Gate T1-3: Data Backup Verification

- [ ] **PASS**: 3+ verified backups exist with tested restore procedure

### Gate T1-4: Documentation Currency

- [ ] README.md - Setup and basic usage
- [ ] CLAUDE.md - Agent configuration (if applicable)
- [ ] docs/runbooks/deployment.md - Deployment procedure
- [ ] docs/runbooks/backup-restore.md - Backup/restore procedure

### Gate T1-5: LESSONS.md Review

- [ ] **PASS**: LESSONS.md reviewed, no blocking patterns unaddressed

### Gate T1-6: Test Coverage

- [ ] **PASS**: Test coverage >= 80%, all tests passing

### Gate T1-7: Security Baseline

- [ ] **PASS**: No hardcoded credentials, security baseline met

---

## Tier 2 to Tier 3 Gates (Staging to Production Scale)

Use this checklist when moving from staging/small production to enterprise scale (100+ users, SLA requirements).

### Gate T2-1: Observability Integration

- [ ] **PASS**: Observability stack configured and verified

### Gate T2-2: Circuit Breakers on External Services

- [ ] **PASS**: Circuit breakers tested and functional

### Gate T2-3: Incident Runbooks

- [ ] docs/runbooks/incident-response.md - General incident procedure
- [ ] docs/runbooks/database-recovery.md - Database failure recovery
- [ ] docs/runbooks/service-restart.md - Application restart procedure
- [ ] docs/runbooks/rollback.md - Deployment rollback procedure
- [ ] docs/runbooks/scaling.md - Scaling procedure

### Gate T2-4: Rollback Plan Tested

- [ ] **PASS**: Rollback plan tested, completes within RTO

### Gate T2-5: Load Testing Verification

| Metric | Target | Actual | Pass |
|--------|--------|--------|------|
| Error rate | < 0.1% | ___% | [ ] |
| p95 latency | < 500ms | ___ms | [ ] |
| p99 latency | < 1s | ___ms | [ ] |
| Throughput | ___ QPS | ___ QPS | [ ] |

### Gate T2-6: SLA Compliance Verification

| Metric | Target | Measured |
|--------|--------|----------|
| Availability | ___% | ___% |
| Response time (p95) | ___ms | ___ms |
| Incident response | ___min | ___min |

- [ ] **PASS**: SLA defined and achievable based on historical data

---

## Pre-Deployment Final Checklist

### 24 Hours Before Deployment
- [ ] All tier gates passed (documented above)
- [ ] Change reviewed and approved by >= 2 engineers
- [ ] On-call engineer identified and notified
- [ ] Deployment window communicated to stakeholders
- [ ] Rollback plan reviewed with team

### Day of Deployment
- [ ] Backup created immediately before deployment
- [ ] Monitoring dashboards open and visible
- [ ] Communication channel ready (Slack, etc.)
- [ ] Runbooks accessible

### Post-Deployment (30 minutes)
- [ ] Health checks passing
- [ ] Error rate within baseline
- [ ] No new errors in Sentry/monitoring
- [ ] Async jobs processing normally

### Post-Deployment (24 hours)
- [ ] Performance baseline comparison
- [ ] No SLA violations
- [ ] Backup completed successfully
- [ ] Deployment log updated

---

## Related Documentation

- [WAVE3_PATHWAY_STRATEGY.md](../WAVE3_PATHWAY_STRATEGY.md) - Tier definitions
- [INCIDENT_TEMPLATE.md](./INCIDENT_TEMPLATE.md) - Production incident format
- [WAVE3_TASK_QUEUE.md](../WAVE3_TASK_QUEUE.md) - Task WAVE3-015

---

*Deployment Validation v1.0.0 | Wave 3 Task: WAVE3-015*
