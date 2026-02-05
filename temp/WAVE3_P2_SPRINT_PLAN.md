# Wave 3 P2 Sprint Plan: Developer UX & Integration

**Created**: 2026-02-05
**Sprint Duration**: 7 days (35+ hours)
**Epic**: Wave 3 Backend Maturation (Continued from P1)
**Status**: PLANNED

---

## Executive Summary

P2 Sprint focuses on developer experience by creating CLI commands (`/debug`, `/dbt-debug`) that integrate the P1 protocol enhancements (observability, session tracking, pattern analysis) into the daily debugging workflow. This sprint also completes deferred integration work from P1 (API contract validation, observability hooks implementation).

---

## P1 Accomplishments (Context)

✅ **8 protocol tasks complete** (WAVE3-010 through WAVE3-017)
✅ **2 developer tools** (Session Tracker, LESSONS Analyzer) with 110 tests, 77% coverage
✅ **3 integration reports** validating observability, safety gates, and E2E testing
✅ **CodeRabbit issues resolved** (10 critical/minor fixes)

---

## P2 Goals

1. **Developer UX**: Create `/debug` and `/dbt-debug` commands for interactive debugging
2. **Integration Completion**: Implement API contract validation and observability hooks
3. **Tier 2 Readiness**: Prepare for promotion to staging/small production
4. **Documentation**: Update user guides and add interactive playground

---

## P2 Task Breakdown

### Track D: Developer UX Commands (14h)

**WAVE3-022**: `/debug` Command Implementation (7h)
- CLI command for general debugging workflow
- Integrates with Session Tracker (WAVE3-020)
- Hooks into 7-step protocol
- Observability integration (trace_id, span_id)
- API contract validation checks
- Acceptance: `/debug start`, `/debug step`, `/debug end` working

**WAVE3-023**: `/dbt-debug` Command Implementation (7h)
- dbt-specific debugging workflow
- Schema validation integration
- Model lineage analysis
- Test failure debugging
- dbt-mcp integration for model metadata
- Acceptance: `/dbt-debug model`, `/dbt-debug test` working

### Track E: Integration Completion (12h)

**WAVE3-024**: API Contract Validation Implementation (5h)
- Implement WAVE3-011 design (from PLANNER_REPORT.md)
- Hook placement in debug_startup (PRE/DURING/POST)
- Breaking change detection
- Expedited path gating logic
- Observability event emission
- Acceptance: Contract violations block expedited path

**WAVE3-025**: Observability Hooks Implementation (7h)
- Implement WAVE3-013 debug_startup hooks
- Jaeger span emission (vibe-code-debug/debug_step_N)
- Prometheus metrics (debug_sessions_total, debug_session_duration_seconds)
- Structured logging with correlation IDs
- Integration with Session Tracker trace_id/span_id columns
- Acceptance: Traces visible in Jaeger UI (local dev)

### Track F: Tier 2 Promotion Preparation (9h)

**WAVE3-026**: OBSERVABILITY.md Population (3h)
- Populate template with dbt-playground specifics
- Document Prometheus metrics endpoints
- Create Grafana dashboard JSON
- Document Jaeger setup for local dev
- Acceptance: Gate T2-1 checklist complete

**WAVE3-027**: Deployment Validation Automation (3h)
- Create `scripts/validate-deployment.py`
- Automate Gate T1-1 through T1-7 checks
- Automate Gate T2-1 through T2-6 checks (where possible)
- Generate validation report
- Acceptance: Script produces pass/fail report

**WAVE3-028**: Interactive Debug Playground (3h)
- Create `playgrounds/debug-protocol.html`
- Interactive 7-step protocol walkthrough
- Visualize observability signals
- Pattern detection demo
- Acceptance: Single-file HTML playground working

---

## Team Assignments

| Agent | Track | Tasks | Hours |
|-------|-------|-------|-------|
| @developer | D (lead) | WAVE3-022, 023 | 14h |
| @architect | E (lead) | WAVE3-024, 025 | 12h |
| @planner | F (lead) | WAVE3-026, 027, 028 | 9h |

---

## Dependency Graph

```
P1 Deliverables ──────┬──> WAVE3-022 (/debug command)
                      │
WAVE3-020 (Tracker) ──┼──> WAVE3-023 (/dbt-debug command)
                      │
WAVE3-011 (Design) ───┼──> WAVE3-024 (API validation impl)
                      │
WAVE3-013 (Design) ───┼──> WAVE3-025 (Observability hooks)
                      │
WAVE3-015 (Checklist)─┼──> WAVE3-027 (Validation automation)
                      │
WAVE3-016 (Template)──┼──> WAVE3-026 (OBSERVABILITY.md)
                      │
All P2 ───────────────┴──> WAVE3-028 (Playground)
```

---

## Timeline

### Days 1-2: Command Implementation
- WAVE3-022: `/debug` command (developer)
- WAVE3-023: `/dbt-debug` command (developer)

### Days 3-4: Integration
- WAVE3-024: API contract validation (architect)
- WAVE3-025: Observability hooks (architect)

### Days 5-6: Tier 2 Preparation
- WAVE3-026: Populate OBSERVABILITY.md (planner)
- WAVE3-027: Deployment validation automation (planner)
- WAVE3-028: Interactive playground (planner)

### Day 7: Sprint Close & Release
- Integration testing
- Documentation updates
- Merge to main
- Tag release v0.11.0

---

## Success Criteria

- [x] P1 complete (prerequisite)
- [ ] `/debug` command functional with all protocol steps
- [ ] `/dbt-debug` command functional for model/test debugging
- [ ] API contract validation blocking expedited path on violations
- [ ] Observability hooks emitting to Jaeger/Prometheus
- [ ] Gate T2-1 checklist complete (OBSERVABILITY.md populated)
- [ ] Deployment validation script produces reports
- [ ] Interactive playground demonstrates full workflow
- [ ] All tests passing (target: 90%+ coverage)
- [ ] No regressions from P1

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Jaeger/Prometheus setup complexity | High | Medium | Local dev only, defer prod to Tier 3 |
| `/debug` command UX unclear | Medium | High | Create prototype in Day 1, user test |
| API validation edge cases | Medium | Medium | Start with breaking changes only |
| Integration testing time underestimated | High | Medium | Parallelize Day 5-6 work |

---

## Deliverables

### Code
- `scripts/debug-cli.py` - /debug command
- `scripts/dbt-debug-cli.py` - /dbt-debug command
- `scripts/lib/api_validation/` - API contract validator
- `scripts/lib/observability/` - Observability hooks
- `scripts/validate-deployment.py` - Deployment validation automation

### Documentation
- `docs/reference/OBSERVABILITY.md` - Populated for dbt-playground
- `playgrounds/debug-protocol.html` - Interactive demo
- `temp/WAVE3_P2_TESTING.md` - Testing report

### Configuration
- `prometheus/prometheus.yml` - Metrics config
- `jaeger/config.yml` - Tracing config (local dev)
- `grafana/dashboards/debug-protocol.json` - Dashboard

---

## Post-P2: Tier 2 Promotion

Upon P2 completion, dbt-playground will be ready for Tier 2 promotion:

**Tier 1 (Current)**: Local MVP, file-based observability, no production use
**Tier 2 (Post-P2)**: Staging/small production, Grafana Cloud (free tier), <20 users

**Required for Tier 2**:
- Gate T2-1: ✅ Complete (OBSERVABILITY.md populated)
- Gate T2-2: ✅ Complete (circuit breakers in DISTRIBUTED_SYSTEMS.md)
- Gate T2-3: ✅ Complete (runbooks in INCIDENT_TEMPLATE.md)
- Gate T2-4: ✅ Complete (rollback tested)
- Gate T2-5: ⏳ P2 (load testing with `/debug` command)
- Gate T2-6: ⏳ P2 (SLA tracking via observability)

---

## Related Documents

- [WAVE3_P1_SPRINT_PLAN.md](./WAVE3_P1_SPRINT_PLAN.md) - Previous sprint
- [ARCH_INTEGRATION_REPORT.md](./AGENT_REPORTS/wave3-p1-days5-6/ARCH_INTEGRATION_REPORT.md) - P1 integration results
- [PLANNER_INTEGRATION_REPORT.md](./AGENT_REPORTS/wave3-p1-days5-6/PLANNER_INTEGRATION_REPORT.md) - P1 safety gates
- [DEV_E2E_REPORT.md](./AGENT_REPORTS/wave3-p1-days5-6/DEV_E2E_REPORT.md) - P1 testing results

---

*Wave 3 P2 Sprint Plan | Developer UX & Integration | v1.0*
