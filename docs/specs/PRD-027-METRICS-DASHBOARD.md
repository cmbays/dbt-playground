# PRD: Metrics & Dashboard System (Feature Set 5)

**Document ID**: PRD-005
**Version**: 1.1
**Date**: 2026-02-03
**Author**: Product Manager (Planning Team)
**Status**: Approved
**Milestone**: v0.10

---

## 1. Problem Statement

### 1.1 Current State

The dbt-playground project follows a canonical 5-stage workflow (UNDERSTAND, PLAN, BUILD, VERIFY, DEPLOY) enforced by the Supervisor agent. However, there is **no visibility** into:

1. **Workflow Adherence**: Are teams following the workflow correctly? Are phases being skipped?
2. **Agent Performance**: Which agents are most effective? Where do handoffs break down?
3. **Quality Trends**: Are test counts improving over time? Are regressions occurring?
4. **Session Health**: Is the current session stuck? Are there blockers?

### 1.2 Pain Points

| Pain Point | Impact | Frequency |
|------------|--------|-----------|
| Cannot tell if workflow is being followed | Quality issues, rework | Every session |
| No early warning for stuck sessions | Lost productivity | Weekly |
| No visibility into test regressions | Bugs reach production | Monthly |
| Agent handoff failures go unnoticed | Delayed features | Weekly |
| No historical data for learning | Cannot improve process | Ongoing |

### 1.3 Business Impact

Without metrics and dashboards:

- **Learning velocity suffers**: Cannot identify what works and what does not
- **Quality degrades silently**: Regressions go unnoticed until user impact
- **Process improvements are guesswork**: No data to inform workflow changes
- **Session context is lost**: Cannot resume effectively after breaks

---

## 2. User Stories / Use Cases

### 2.1 Primary Personas

| Persona | Description | Key Need |
|---------|-------------|----------|
| **Developer (Chris)** | Primary user learning dbt | Visibility into workflow adherence |
| **Supervisor Agent** | Orchestrates workflow | Data for quality gates |
| **Future Team Member** | Onboards to project | Dashboard for orientation |

### 2.2 User Stories

#### US-001: View Current Session Health

> **As a** developer
> **I want to** see my current session's health at a glance
> **So that** I can identify blockers and take action quickly

**Acceptance Criteria**:

- Dashboard shows current phase and time in phase
- Health pulse score (0-100) displayed prominently
- Adherence score (0-100) displayed with breakdown
- Clear indication if session is stuck or healthy

#### US-002: Track Workflow Adherence

> **As a** developer
> **I want to** track whether I'm following the 5-stage workflow correctly
> **So that** I can improve my process and avoid skipping critical steps

**Acceptance Criteria**:

- Adherence score calculated for each tracked feature
- Penalties visible when phases are skipped or redone
- Phase timeline shows completed vs. remaining phases
- Historical adherence scores viewable

#### US-003: Detect Anomalies Proactively

> **As a** developer
> **I want to** be alerted when something is wrong with my session
> **So that** I can fix issues before they become bigger problems

**Acceptance Criteria**:

- Alert when session is stuck (>30 min no activity)
- Alert when QA phase is skipped
- Alert when tests start failing that previously passed
- Alerts displayed in dashboard with severity levels

#### US-004: Monitor Agent Activity

> **As a** developer
> **I want to** see which agents have been invoked and what they did
> **So that** I can understand the workflow execution and debug issues

**Acceptance Criteria**:

- Agent activity feed shows invocations in chronological order
- Each entry shows agent name, action, and timestamp
- Ability to filter by agent type
- Links to artifacts created by agents

#### US-005: Track Test Quality Over Time

> **As a** developer
> **I want to** see test counts and pass rates over time
> **So that** I can ensure quality is improving, not degrading

**Acceptance Criteria**:

- Test count displayed with trend indicator
- Bug regressions highlighted (tests that were passing now fail)
- Historical chart showing test counts per day
- Ratchet baseline visible (minimum test count)

#### US-006: Resume Sessions with Context

> **As a** developer
> **I want to** resume sessions with full context of where I left off
> **So that** I can continue work without losing momentum

**Acceptance Criteria**:

- Dashboard shows last session state
- Phase timeline shows progress
- Recent agent activity visible
- Active blockers highlighted

---

## 3. Functional Requirements

### 3.1 Adherence Scoring

#### FR-001: Calculate Adherence Score

The system shall calculate an adherence score (0-100) for each tracked feature based on workflow compliance.

**Scoring Formula**:

```
adherence_score = base_points + completion_bonus - penalties

Where:
  base_points = sum(phase_points for each completed phase)
  completion_bonus = 20 if all phases completed in order
  penalties = sum(redo_penalty * redo_count + skip_penalty * skip_count + ...)
```

**Phase Points**:

| Phase | Points | Rationale |
|-------|--------|-----------|
| UNDERSTAND | 10 | Context gathering (foundational but brief) |
| PLAN | 25 | Design work (high value, prevents rework) |
| BUILD | 30 | Implementation (most effort) |
| VERIFY | 20 | Quality assurance (critical for quality) |
| DEPLOY | 15 | Release work (important but smaller scope) |
| **Total** | **100** | Perfect adherence score |

**Penalties**:

| Violation | Penalty | Detection Method |
|-----------|---------|------------------|
| Redo phase (rework) | -5 per redo | `phase.entered` after `phase.exited` for same phase |
| Skip phase | -15 per skip | Missing `phase.entered` event |
| Out-of-order phase | -10 per violation | Sequence check against canonical order |
| Timeout (phase > 2x expected) | -5 per timeout | Duration check against baselines |

#### FR-002: Store Adherence Scores

The system shall persist adherence scores in DuckDB for historical analysis.

> **Note**: Per [ADR-015](../decisions/ADR-015-duckdb-for-fs5-metrics.md), DuckDB was selected over SQLite because it's already in the project (`dbt-duckdb`) and can query JSONL files directly.

**Required Fields**:

- session_id
- feature_name (correlation_id)
- score (0-100)
- base_points
- completion_bonus
- penalties (JSON array of applied penalties)
- calculated_at (timestamp)

### 3.2 Anomaly Detection

#### FR-003: Detect Workflow Anomalies

The system shall detect the following anomalies:

| Anomaly | Detection Logic | Severity | Auto-Resolve |
|---------|-----------------|----------|--------------|
| **Stuck Session** | No events for >30min during BUILD/VERIFY | WARNING | Yes (on next event) |
| **QA Skipping** | DEPLOY without VERIFY events | CRITICAL | No |
| **Phase Timeout** | Phase duration > 2x baseline | WARNING | Yes (on phase exit) |
| **Review Avoidance** | PR merged without approvals | CRITICAL | No |
| **Test Regression** | Passing test now fails | ERROR | Yes (on test fix) |
| **Artifact Missing** | Phase complete without expected artifact | WARNING | Yes (on artifact create) |
| **Agent Loop** | Same agent invoked >5x without progress | WARNING | Yes (on progress) |
| **Orphan Branch** | Branch with no commits for >3 days | INFO | Yes (on commit) |

#### FR-004: Alert on Anomalies

The system shall alert users when anomalies are detected.

**Alert Channels**:

- Console output (when scripts run)
- Dashboard panel (persistent display)
- SQLite storage (for history)

**Alert Format**:

```
[SEVERITY] ANOMALY_TYPE: Description
  Session: <session_id>
  Detected: <timestamp>
  Details: <context>
```

### 3.3 Dashboard Visualization

#### FR-005: Display Current Session Status

The dashboard shall display:

- Active ticket/feature name
- Current phase (UNDERSTAND, PLAN, BUILD, VERIFY, DEPLOY)
- Time in current phase
- Session status (active, stuck, complete)

#### FR-006: Display Scores

The dashboard shall display:

- Adherence score (0-100) with rating (EXCELLENT/GOOD/FAIR/POOR)
- Health pulse score (0-100) with component breakdown
- Test coverage (pass count / total, pass rate)

#### FR-007: Display Phase Timeline

The dashboard shall display a visual timeline of workflow phases:

- Completed phases highlighted
- Current phase indicated
- Duration for each phase shown
- Remaining phases grayed out

#### FR-008: Display Agent Activity Feed

The dashboard shall display a chronological feed of agent invocations:

- Agent name
- Action/task description
- Timestamp
- Outcome (success/failure/redo)
- Link to created artifacts (if any)

#### FR-009: Display Anomaly Alerts

The dashboard shall display active anomalies:

- Severity indicator (color-coded)
- Anomaly type
- Description
- Detected timestamp
- Dismiss/acknowledge action

### 3.4 Data Persistence

#### FR-010: Store Events in JSONL

The system shall continue storing events in `temp/WORKFLOW_HISTORY/events.jsonl` for:

- Append-only audit trail
- Human-readable format
- Simple event capture

#### FR-011: Query Events via DuckDB Views

The system shall query events directly from JSONL files using DuckDB views:

- Complex queries via SQL
- Aggregations via DuckDB analytics
- Dashboard data via pre-generated JSON
- Historical analysis via unified event view

**Query Mechanism**:

- DuckDB `read_json_auto()` for direct JSONL access
- Views transform events to canonical format
- No sync script required (real-time data)
- Optional: Export to JSON for dashboard consumption

#### FR-012: Capture Test Results

The system shall capture test results from dbt runs:

- Total tests
- Passed tests
- Failed tests
- Warned tests
- Test names (for regression detection)

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| Dashboard load time | <2 seconds | Responsive user experience |
| DuckDB query time | <100ms | Fast dashboard updates |
| View query time | <500ms for unified events | Direct JSONL querying |
| Anomaly detection time | <500ms | Near-real-time alerting |

### 4.2 Storage

| Requirement | Target | Rationale |
|-------------|--------|-----------|
| DuckDB database size | <50MB | Reasonable disk usage |
| Events.jsonl growth | ~1MB/month | Sustainable growth |
| Archive policy | 30 days active, then archive | Balance history vs. size |

### 4.3 Queryability

| Requirement | Description |
|-------------|-------------|
| SQL access | All metrics queryable via standard SQL |
| dbt compatibility | Same DuckDB engine as dbt models |
| Export | JSON export for external analysis |

### 4.4 Reliability

| Requirement | Description |
|-------------|-------------|
| Offline operation | All features work without network |
| Graceful degradation | Dashboard works even if metrics incomplete |
| Data integrity | No data loss on crash (DuckDB MVCC) |

### 4.5 Extensibility

| Requirement | Description |
|-------------|-------------|
| New anomaly rules | Addable via YAML configuration |
| New event types | Extendable event schema |
| New metrics | SQL views for custom metrics |

---

## 5. Acceptance Criteria

### 5.1 Feature-Level Acceptance

| Feature | Acceptance Criteria |
|---------|---------------------|
| Adherence Scoring | Score calculated correctly for 20 test sessions with known outcomes |
| Anomaly Detection | 8 rules implemented, >90% detection rate on injected violations |
| Dashboard | All widgets functional, load time <2 seconds, responsive design |
| Data Persistence | Events sync correctly, no data loss, incremental sync working |
| Integration | Supervisor shows metrics summary on session start |

### 5.2 End-to-End Acceptance

1. **New Session Flow**:
   - Start new session
   - Dashboard shows initial state (no score, no phases)
   - Begin work, phases tracked
   - Adherence score updates
   - Anomalies detected if violations occur

2. **Resume Session Flow**:
   - Resume existing session
   - Dashboard shows previous state
   - Phase timeline shows progress
   - Adherence score reflects history

3. **Anomaly Detection Flow**:
   - Introduce violation (e.g., skip VERIFY)
   - Anomaly detected within 1 minute
   - Alert displayed in dashboard
   - Alert logged to DuckDB

---

## 6. Out of Scope

The following are explicitly out of scope for v0.9:

| Item | Rationale | Future Consideration |
|------|-----------|---------------------|
| **Predictive analytics** | Requires historical data | v1.1+ |
| **Multi-repo metrics** | Single repo focus for v0.9 | v1.0+ |
| **External dashboards** | Local-first philosophy | v1.0+ if needed |
| **Real-time streaming** | Polling sufficient for current use | v1.1+ |
| **User authentication** | Single-user project | Not planned |
| **Cloud storage** | Local-only storage | Not planned |
| **A/B testing agents** | Requires more data | v1.1+ |
| **Agent optimization recommendations** | Requires ML | v1.1+ |
| **Cross-session correlation** | Complex analysis | v1.0+ |

---

## 7. Dependencies

### 7.1 Internal Dependencies

| Dependency | Description | Status |
|------------|-------------|--------|
| `compute-health-pulse.py` | Base scoring engine | Exists |
| `events.jsonl` | Event storage | Exists |
| `event-schema.json` | Event schema | Exists, needs extension |
| `workflow-chronicle.html` | Base visualization | Exists, will extend |
| `capture-event.py` | Event capture | Exists |
| v0.8 completion | Test baselines, DQ foundation | In progress |

### 7.2 External Dependencies

| Dependency | Description | Risk |
|------------|-------------|------|
| DuckDB | Persistence layer (via dbt-duckdb) | None (already installed) |
| GitHub API | PR metrics | Low (rate limits) |
| Rich library | Console output | None (already installed) |

---

## 8. Success Metrics

### 8.1 Adoption Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dashboard usage | Daily | Check access logs (if tracked) |
| Anomaly acknowledgment | >80% | Anomalies dismissed vs. ignored |
| Score improvement | Upward trend | Weekly adherence score average |

### 8.2 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Adherence score accuracy | >95% | Manual validation of 20 sessions |
| Anomaly detection rate | >90% | Inject known violations |
| False positive rate | <10% | Count spurious alerts |

### 8.3 Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dashboard load time | <2 seconds | Browser dev tools |
| Query response time | <100ms | SQLite profiling |
| Sync time | <1 second | Script timing |

---

## 9. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Over-instrumentation burden | Medium | Medium | Lean event schema, auto-capture |
| Dashboard complexity | Medium | Medium | Design review before build |
| Scope creep | Medium | High | Strict adherence to PRD |
| Performance issues | Low | Medium | Profile early, optimize late |
| Data privacy concerns | Low | Low | All data local, no PII |

---

## 10. Timeline

| Phase | Duration | Target Completion |
|-------|----------|-------------------|
| Phase 1: Foundation | 1 week | Week of Mar 3, 2026 |
| Phase 2: Metrics Collection | 1 week | Week of Mar 10, 2026 |
| Phase 3: Anomaly Detection | 1 week | Week of Mar 17, 2026 |
| Phase 4: Dashboard Extension | 1 week | Week of Mar 24, 2026 |
| Phase 5: Polish & Documentation | 1 week | Week of Mar 31, 2026 |

**Target Milestone**: v0.9 - March 31, 2026

---

## 11. Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| **Adherence Score** | 0-100 measure of workflow compliance |
| **Health Pulse** | 0-100 composite score of session health |
| **Anomaly** | Detected workflow violation or issue |
| **Phase** | Stage in 5-stage workflow (UNDERSTAND, PLAN, BUILD, VERIFY, DEPLOY) |
| **Session** | Continuous period of work on a feature |
| **Ratchet** | Quality baseline that can only increase |

### B. Related Documents

| Document | Location |
|----------|----------|
| Research Report | `temp/2026_02_01_Discussion/metrics_dashboard_report.md` |
| Implementation Plan | `temp/2026_02_01_Discussion/metrics_dashboard_plan.md` |
| TDD | `temp/2026_02_01_Discussion/metrics_dashboard_TDD.md` |
| Workflow Stages | `docs/reference/WORKFLOW_STAGES.md` |
| Event Schema | `temp/WORKFLOW_HISTORY/schema/event-schema.json` |

### C. Open Questions

1. **Q**: Should anomaly rules be configurable per-project or global?
   **A**: Start with global, evaluate per-project in v1.0.

2. **Q**: How long should historical data be retained?
   **A**: 30 days active, archive older data.

3. **Q**: Should dashboard auto-refresh or manual refresh?
   **A**: Auto-refresh every 30 seconds with manual refresh button.

### D. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-01 | Initial PRD creation |
| 1.1 | 2026-02-03 | Updated to use DuckDB instead of SQLite per ADR-015. Changed FR-011 from sync script to JSONL views. |

---

*PRD complete. Ready for TDD creation and implementation.*
