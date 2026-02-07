# Architecture Integration Report: Wave 3 P1 Days 5-6

**Feature**: Track A - Protocol Integration (Observability + API Contract Validation)
**Sprint**: Wave 3 P1 Sprint - Days 5-6 Integration & Testing
**Date**: 2026-02-05
**Author**: Technical Architect
**Status**: Integration Verification Complete

---

## Executive Summary

This report documents the integration verification for Days 5-6 of the Wave 3 P1 Sprint. Track A focuses on two areas: (1) verifying the observability hook flow from WAVE3-013 design against the WAVE3-020/021 implementation, and (2) designing the API contract validation integration with the debug protocol and expedited path.

**Key Findings**:
- Observability hook flow is **partially integrated** - event emission exists, but trace/metric instrumentation is deferred to Tier 2
- API contract validation integration design is **complete** - ready for P2 implementation
- No blocking issues for P2 developer UX commands
- Three integration gaps documented with clear P2 resolution paths

---

## 1. Observability Verification

### 1.1 Span Hierarchy Verification

**Design Specification** (OBSERVABILITY_INTEGRATION.md Section 2.1):

```
Debug Session (root span)
|-- Step 1: Reproduce Bug
|-- Step 2: Blast Radius Research
|-- Step 3: Hypothesis Formation (CRITICAL)
|-- Step 4: Root Cause vs Symptom Classification (CRITICAL)
|-- Step 5: Fix Implementation
|-- Step 6: Fix Validation
|-- Step 7: Document & Learn
```

**Implementation Status** (debug_session/tracker.py):

| Component | Designed | Implemented | Status |
|-----------|----------|-------------|--------|
| Session ID generation | `DBG-YYYY-MM-DD-NNN` | `generate_session_id()` in database.py | **Aligned** |
| Protocol phases | 7 steps | `PROTOCOL_PHASES` dict in models.py | **Aligned** |
| Phase naming | `1-reproduce` to `7-prevent` | Matches design | **Aligned** |
| Root span creation | Yes | **No** (deferred) | Tier 2 |
| Step span emission | Yes | **No** (deferred) | Tier 2 |
| Span naming convention | `vibe-code-debug/debug_step_N` | N/A | Tier 2 |

**Protocol Phase Mapping Verification**:

| Design Step | Implementation Phase | Description | Status |
|-------------|---------------------|-------------|--------|
| Step 1: Reproduce Bug | `1-reproduce` | Confirm bug exists reliably | Aligned |
| Step 2: Blast Radius Research | `2-blast_radius` | Identify affected components | Aligned |
| Step 3: Hypothesis Formation | `3-root_cause` | Identify underlying cause | Naming variance |
| Step 4: Root Cause Classification | `4-fix_design` | Design the solution | Purpose variance |
| Step 5: Fix Implementation | `5-implement` | Code the fix | Aligned |
| Step 6: Fix Validation | `6-verify` | Confirm fix works | Aligned |
| Step 7: Document & Learn | `7-prevent` | Add tests/docs to prevent | Aligned |

**Finding**: The Session Tracker (WAVE3-020) does not currently emit Jaeger spans. This is by design - observability tracing is a Tier 2 feature. The architecture is prepared via the hook pattern defined in OBSERVABILITY_INTEGRATION.md Section 2.2.

**Gap: Schema does not include `trace_id`/`span_id` columns**

Specified in WAVE3-013 Section 5.2 but not yet implemented:

```sql
ALTER TABLE debug_sessions ADD COLUMN trace_id VARCHAR;
ALTER TABLE debug_sessions ADD COLUMN span_id VARCHAR;
ALTER TABLE debug_sessions ADD COLUMN observability_enabled BOOLEAN DEFAULT TRUE;

ALTER TABLE debug_steps ADD COLUMN span_id VARCHAR;
ALTER TABLE debug_steps ADD COLUMN metrics_emitted BOOLEAN DEFAULT FALSE;

CREATE INDEX idx_debug_sessions_trace ON debug_sessions(trace_id);
```

**Recommendation**: Add columns to `database.py` SCHEMA_SQL in P2 as part of WAVE3-025 `/debug` command implementation.

---

### 1.2 Metrics Pipeline Validation

**Design Specification** (OBSERVABILITY_INTEGRATION.md Section 3.1):

| Metric | Type | Labels | Designed |
|--------|------|--------|----------|
| `debug_sessions_total` | counter | severity, outcome, expedited | Yes |
| `debug_session_duration_seconds` | histogram | severity, outcome | Yes |
| `debug_step_duration_seconds` | histogram | step_number, step_name | Yes |
| `debug_root_cause_total` | counter | root_cause_type, severity | Yes |
| `debug_lessons_extracted_total` | counter | trigger_type, pattern_score_bucket | Yes |

**Implementation Status**:

| Metric | Data Source | Current State |
|--------|-------------|---------------|
| `debug_sessions_total` | `debug_sessions` table | Data available, no Prometheus emission |
| `debug_session_duration_seconds` | `duration_minutes` column | Stored as INTEGER minutes |
| `debug_step_duration_seconds` | Not stored | **Gap** - step timestamps exist |
| `debug_root_cause_total` | `v_session_summary.pattern_category` | View provides categorization |
| `debug_lessons_extracted_total` | Pattern status tracking | Analyzer implements scoring |

**Current Alternative**: The `_emit_event()` method in tracker.py (lines 322-369) writes to `memory/events.jsonl`:

```python
event = {
    'timestamp': datetime.now(UTC).isoformat(),
    'event': 'debug_session_completed',
    'version': '1.0',
    'data': {
        'session_id': session.session_id,
        'duration_minutes': session.duration_minutes,
        'step_count': session.step_count,
        'outcome': session.outcome,
        'root_cause_category': pattern_category,
        'tags': session.tags,
    },
}
```

This provides FS1 correlation but does not support real-time metric querying. Acceptable for Tier 1.

**Metrics Data Available via DuckDB**:

The `v_session_summary` view (database.py lines 64-86) provides pre-categorized data:

```sql
CREATE OR REPLACE VIEW v_session_summary AS
SELECT
    session_id,
    bug_description,
    DATE(start_time) as session_date,
    root_cause,
    outcome,
    duration_minutes,
    step_count,
    tags,
    CASE
        WHEN root_cause ILIKE '%race%' OR root_cause ILIKE '%concurrent%' THEN 'race_condition'
        WHEN root_cause ILIKE '%null%' OR root_cause ILIKE '%none%' THEN 'null_handling'
        WHEN root_cause ILIKE '%timeout%' THEN 'timeout'
        WHEN root_cause ILIKE '%state%' OR root_cause ILIKE '%corrupt%' THEN 'state_management'
        WHEN root_cause ILIKE '%import%' OR root_cause ILIKE '%module%' THEN 'import_error'
        WHEN root_cause ILIKE '%type%' OR root_cause ILIKE '%cast%' THEN 'type_error'
        ELSE 'other'
    END as pattern_category
FROM debug_sessions
WHERE outcome != 'in_progress';
```

**Recommendation**: For Tier 2, implement a Prometheus exporter that queries this view and exposes metrics at `/metrics` endpoint.

---

### 1.3 Error Taxonomy Correlation

**Design Specification** (OBSERVABILITY_INTEGRATION.md Section 4):

```
Error Categories
|-- Infrastructure (network_timeout, connection_refused, dns_resolution_failed, resource_exhausted)
|-- Data (schema_mismatch, constraint_violation, null_reference, data_corruption)
|-- Logic (race_condition, deadlock, off_by_one, state_inconsistency)
|-- API (contract_violation, version_mismatch, auth_failure, rate_limited)
|-- External (third_party_failure, dependency_unavailable, integration_timeout)
```

**Implementation Mapping**:

| Designed Category | Implemented Pattern | v_session_summary Keyword | Coverage |
|-------------------|---------------------|--------------------------|----------|
| Infrastructure.network_timeout | `timeout` | `timeout` | Partial |
| Infrastructure.connection_refused | Not mapped | - | Gap |
| Data.null_reference | `null_handling` | `null`, `none` | Covered |
| Data.schema_mismatch | Not mapped | - | Gap |
| Logic.race_condition | `race_condition` | `race`, `concurrent` | Covered |
| Logic.state_inconsistency | `state_management` | `state`, `corrupt` | Covered |
| Logic.off_by_one | Not mapped | - | Gap |
| API.contract_violation | Not mapped | - | **Critical Gap** |
| API.version_mismatch | Not mapped | - | Gap |
| External.* | Not mapped | - | Gap |

**Gap Analysis**:

1. **Infrastructure category** partially covered - only `timeout` mapped
2. **API category** not mapped - critical for WAVE3-011 integration
3. **External category** not mapped - useful for third-party service issues
4. **Data.schema_mismatch** not mapped - important for dbt context

**Expanded Keyword Mapping** (Recommended for P2):

```python
PATTERN_CATEGORIES = {
    # Current mappings
    'race_condition': ['race', 'concurrent', 'thread', 'async'],
    'null_handling': ['null', 'none', 'undefined', 'missing'],
    'state_management': ['state', 'corrupt', 'inconsistent'],
    'timeout': ['timeout'],
    'import_error': ['import', 'module', 'package'],
    'type_error': ['type', 'cast', 'conversion'],

    # Recommended additions for P2
    'infrastructure': ['connection', 'network', 'dns', 'socket', 'resource'],
    'api_contract': ['contract', 'schema', 'version', 'breaking', 'api'],
    'external': ['third.party', 'external', 'vendor', 'integration'],
    'data_quality': ['constraint', 'validation', 'format', 'encoding'],
}
```

---

### 1.4 Integration Points with WAVE3-020/021

**Verified Integration Flow**:

```
[Debug Session Start]
    |
    v
[tracker.start_session()] --> [debug_sessions table]
    |
    v
[tracker.log_step()] --> [debug_steps table]
    |
    v
[tracker.end_session()] --> [events.jsonl] + [database update]
    |
    v
[analyzer.load_sessions()] <-- [v_session_summary view]
    |
    v
[cluster_root_causes()] --> [Pattern objects]
    |
    v
[calculate_score()] --> [Confidence scores]
    |
    v
[classify_pattern()] --> [PROMOTE/CANDIDATE/REVIEW/IGNORE]
```

**Integration Points Verification**:

| Integration | Design | Implementation | Status |
|-------------|--------|----------------|--------|
| Session Tracker -> Events | WAVE3-013 Section 5 | `tracker.py:_emit_event()` | **Working** |
| Events -> LESSONS Analyzer | WAVE3-021 Design | `analyzer.py:load_sessions()` | **Working** |
| Pattern Scoring | FS1 Formula | `scoring.py:calculate_score()` | **Working** |
| Pattern Classification | WAVE3-012 | `scoring.py:classify_pattern()` | **Working** |
| Session Summary View | WAVE3-013 | `database.py:v_session_summary` | **Working** |

**Scoring Algorithm Verification** (scoring.py lines 99-120):

```python
def calculate_score(frequency, days_since_last, sessions):
    """Calculate total pattern score.

    Formula: (Frequency * 0.4) + (Recency * 0.3) + (Consistency * 0.3)
    """
    freq_w = frequency_weight(frequency)
    rec_w = recency_weight(days_since_last)
    cons_w = consistency_weight(sessions)

    return (freq_w * 0.4) + (rec_w * 0.3) + (cons_w * 0.3)
```

This matches OBSERVABILITY_INTEGRATION.md Section 6.2 design exactly.

**Pattern Classification Thresholds** (models.py lines 70-76):

```python
PATTERN_STATUS = {
    'PROMOTE': {'min_score': 0.8, 'min_freq': 3},
    'CANDIDATE': {'min_score': 0.7, 'min_freq': 2},
    'REVIEW': {'min_score': 0.5, 'min_freq': 2},
    'IGNORE': {'min_score': 0.0, 'min_freq': 0},
}
```

Aligns with PLANNER_REPORT.md scoring thresholds.

---

## 2. API Validation Integration Design

### 2.1 Planned Spec Review

From PLANNER_REPORT.md (WAVE3-011 design):

**Contract Types**:
1. Internal APIs (service-to-service)
2. External services (third-party)
3. Message contracts (event schemas)
4. Database schemas

**Validation Checkpoints**:
- After Step 2 (Blast Radius Research) - Check API contracts of affected services
- During Step 5 (Fix Implementation) - Validate fix doesn't break contracts
- During Step 6 (Fix Validation) - Contract compliance testing

**Breaking Change Categories**:
- API endpoint removed or renamed (Critical)
- Request/response schema incompatibility (High)
- Authentication requirements changed (High)
- Rate limiting decreased (Medium)

### 2.2 Integration Design

**Hook Placement in debug_startup**:

Based on OBSERVABILITY_INTEGRATION.md Section 2.2 hook architecture:

```python
class DebugPhase(Enum):
    PRE_DEBUG = "pre_debug"
    DURING_DEBUG = "during_debug"
    POST_DEBUG = "post_debug"
```

**API Validation Hook Registration**:

```python
class DebugStartup:
    def _register_default_hooks(self):
        # PRE_DEBUG hooks
        self.register_hook(DebugPhase.PRE_DEBUG, "initialize_tracer", self._init_tracer, priority=10)
        self.register_hook(DebugPhase.PRE_DEBUG, "setup_metrics", self._setup_metrics, priority=20)
        self.register_hook(DebugPhase.PRE_DEBUG, "load_contract_specs", self._load_contracts, priority=30)

        # DURING_DEBUG hooks (contract validation)
        self.register_hook(DebugPhase.DURING_DEBUG, "validate_api_contracts", self._validate_contracts, priority=50)
        self.register_hook(DebugPhase.DURING_DEBUG, "check_fix_contract_impact", self._check_fix_impact, priority=60)

        # POST_DEBUG hooks
        self.register_hook(DebugPhase.POST_DEBUG, "emit_session_metrics", self._emit_session_metrics, priority=10)
        self.register_hook(DebugPhase.POST_DEBUG, "check_contract_compliance", self._check_compliance, priority=20)
        self.register_hook(DebugPhase.POST_DEBUG, "trigger_lessons_analysis", self._trigger_lessons_analysis, priority=100)
```

**When Contract Validation Runs**:

| Phase | Hook | Purpose | Fail Behavior |
|-------|------|---------|---------------|
| PRE_DEBUG | `load_contract_specs` | Load API schemas from spec files | Warning only |
| DURING_DEBUG (Step 2) | `validate_api_contracts` | Check affected services' contracts | Add to blast radius |
| DURING_DEBUG (Step 5) | `check_fix_contract_impact` | Validate fix doesn't break contracts | Block if breaking |
| POST_DEBUG (Step 6) | `check_contract_compliance` | Final contract validation | Log violation |

### 2.3 Contract Violation Observability Events

**Event Schema**:

```json
{
  "timestamp": "2026-02-05T10:30:00Z",
  "event": "api_contract_violation",
  "version": "1.0",
  "data": {
    "session_id": "DBG-2026-02-05-001",
    "violation_type": "breaking_change",
    "contract_name": "UserService.getUser",
    "expected_schema": "v2.0.0",
    "actual_schema": "v1.9.0",
    "severity": "high",
    "step": "5-implement",
    "affected_services": ["UserService", "AuthService"],
    "expedited_disqualified": true
  }
}
```

**Breaking Change Categories** (from PLANNER_REPORT.md):

| Category | Severity | Example | Expedited Path Impact |
|----------|----------|---------|----------------------|
| Endpoint removed/renamed | Critical | `DELETE /users/:id` removed | **Disqualified** |
| Schema incompatibility | High | Response field type changed | **Disqualified** |
| Auth requirements changed | High | New API key required | **Disqualified** |
| Rate limiting decreased | Medium | From 1000/min to 100/min | Warning |
| New optional parameters | Low | Added `?include_deleted=true` | None |

### 2.4 Expedited Path Gating

**Current Disqualifiers** (from EXPEDITED_PATH.md Section 3):

1. Multi-file changes
2. Database migration required
3. **API contract changes** (target for integration)
4. Upstream/downstream dependencies
5. New dependencies required
6. Security-sensitive code
7. Uncertain root cause
8. Environment-specific behavior

**New Disqualifier Logic**:

```python
def is_expedited_path_allowed(session_context: dict) -> tuple[bool, str]:
    """Check if expedited path is allowed for this debug session.

    Returns:
        (allowed: bool, reason: str) - Reason is empty if allowed
    """
    # Existing disqualifier checks...

    # NEW: Contract validation check
    if session_context.get('api_contracts_affected'):
        contracts = session_context['api_contracts_affected']
        for contract in contracts:
            if contract.get('change_type') == 'breaking':
                return (False, f"Breaking API contract change: {contract['name']}")

    return (True, "")
```

**Integration with Step 2 (Blast Radius Research)**:

```python
def blast_radius_research(session_id: str) -> BlastRadiusResult:
    """Step 2 of debug protocol - identify affected components.

    Includes API contract analysis for expedited path gating.
    """
    result = BlastRadiusResult()

    # Existing: Find affected files and services
    result.affected_files = find_affected_files()
    result.affected_services = trace_service_dependencies()

    # NEW: Analyze API contracts
    result.api_contracts = analyze_api_contracts(result.affected_services)

    # NEW: Check for breaking changes
    for contract in result.api_contracts:
        if is_breaking_change(contract):
            result.expedited_path_blocked = True
            result.expedited_block_reason = f"Breaking change in {contract.name}"

            # Emit observability event
            emit_event('api_contract_violation', {
                'session_id': session_id,
                'violation_type': 'potential_breaking_change',
                'contract_name': contract.name,
                'step': '2-blast_radius',
            })

    return result
```

### 2.5 Integration with Error Taxonomy

**Mapping Contract Violations to WAVE3-013 Error Categories**:

| Contract Violation | Error Category | Error Subtype |
|--------------------|----------------|---------------|
| Schema mismatch | Data | schema_mismatch |
| Version mismatch | API | version_mismatch |
| Auth failure | API | auth_failure |
| Rate limited | API | rate_limited |
| Endpoint removed | API | contract_violation |
| Breaking change detected | API | contract_violation |

**Incident Severity Correlation** (from OBSERVABILITY_INTEGRATION.md Section 4.2):

| Error Category | Default Severity | Escalation Trigger |
|----------------|------------------|-------------------|
| API.contract_violation | **High** | > 3 occurrences/hour |
| API.version_mismatch | **Medium** | > 5 occurrences/day |
| API.auth_failure | **High** | > 1 occurrence |
| API.rate_limited | **Low** | External factor |

---

## 3. Integration Risks

### 3.1 Gaps Between Design and Implementation

| Gap | Severity | Impact | Mitigation |
|-----|----------|--------|------------|
| No trace_id/span_id columns | Low | Cannot link sessions to Jaeger traces | Add columns in P2 schema migration |
| Limited error taxonomy coverage | Medium | Some root causes not categorized | Expand keyword mapping in P2 |
| No Prometheus metrics emission | Low | No real-time monitoring | Acceptable for Tier 1 |
| API contract validation not implemented | Medium | No automated contract checking | Design complete, implement in P2 |

### 3.2 Missing Observability Signals

| Signal | Designed | Implemented | Priority |
|--------|----------|-------------|----------|
| Session start trace | Yes | No | P2 |
| Step duration metrics | Yes | No | P2 |
| Contract violation events | Yes | No | P2 |
| Pattern extraction metrics | Yes | No | P3 |
| Expedited path tracking | Yes | No | P2 |

### 3.3 Contract Validation Edge Cases

| Edge Case | Handling | Notes |
|-----------|----------|-------|
| Contract spec file not found | Warning, continue debugging | Most dbt-playground code |
| Multiple contract versions active | Compare against latest stable | Conservative approach |
| Partial schema match | Flag as potential issue | Don't auto-disqualify |
| Internal API without spec | Skip validation, log warning | Document gap |

---

## 4. Recommendations for P2

### 4.1 `/debug` Command Observability Integration

When implementing WAVE3-025 (`/debug` command):

1. **Schema migration** - Add observability columns:
   ```sql
   ALTER TABLE debug_sessions ADD COLUMN trace_id VARCHAR;
   ALTER TABLE debug_sessions ADD COLUMN span_id VARCHAR;
   ALTER TABLE debug_sessions ADD COLUMN observability_enabled BOOLEAN DEFAULT TRUE;
   ALTER TABLE debug_sessions ADD COLUMN expedited BOOLEAN DEFAULT FALSE;
   ```

2. **Initialize tracer on session start**:
   ```python
   tracer = trace.get_tracer("vibe-code-debug")
   with tracer.start_as_current_span("debug_session") as span:
       span.set_attribute("debug.session_id", session_id)
       span.set_attribute("debug.severity", severity)
   ```

3. **Wrap each step in a span**:
   ```python
   with tracer.start_as_current_span(f"debug_step_{step_number}") as step_span:
       step_span.set_attribute("debug.step.name", phase_name)
       # ... step logic
   ```

4. **Store trace context in database**:
   ```python
   session.trace_id = span.get_span_context().trace_id
   session.span_id = span.get_span_context().span_id
   ```

### 4.2 Contract Validation Automation

For P2 WAVE3-022 (Contract Validator tool):

1. **Schema discovery**: Scan for OpenAPI/AsyncAPI specs in repository
2. **Change detection**: Compare current schema against baseline
3. **Breaking change detection**: Apply semantic versioning rules
4. **Integration**: Hook into Step 2 (research) and Step 6 (validation)
5. **dbt contracts**: Detect column renames, type changes, removed columns

### 4.3 Dashboard Requirements

For P2 observability dashboard:

| Panel | Metrics | Purpose |
|-------|---------|---------|
| Active Sessions | `debug_sessions_total{outcome="in_progress"}` | Current debugging load |
| Time to Resolution | `debug_session_duration_seconds` p50, p95 | Efficiency tracking |
| Root Cause Distribution | `debug_root_cause_total` by category | Pattern identification |
| Step Bottlenecks | `debug_step_duration_seconds` by step | Protocol optimization |
| Contract Violations | `api_contract_violations_total` | API health |
| Expedited Path Usage | `debug_sessions_total{expedited="true"}` / total | Protocol efficiency |

---

## 5. Success Metrics Verification

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| All observability signal types verified | 3 (traces, metrics, logs) | 1 (events/logs) | **Partial** - Tier 1 appropriate |
| API validation integration designed | Complete | Complete | **Pass** |
| No blocking issues for P2 | 0 | 0 | **Pass** |
| Integration report ready | Day 7 | Day 5 | **Pass** |

---

## 6. Files Referenced

| File | Purpose | Key Sections |
|------|---------|--------------|
| `temp/vibe_coding/OBSERVABILITY_INTEGRATION.md` | Design spec | Section 2.1, 3, 4, 5 |
| `temp/vibe_coding/EXPEDITED_PATH.md` | Disqualifier criteria | Section 3 |
| `scripts/lib/debug_session/tracker.py` | Session lifecycle | `_emit_event()` |
| `scripts/lib/debug_session/database.py` | Schema, views | `v_session_summary` |
| `scripts/lib/debug_session/models.py` | Data models | `PROTOCOL_PHASES`, `PATTERN_STATUS` |
| `scripts/lib/lessons_analyzer/scoring.py` | Pattern scoring | `calculate_score()` |
| `scripts/lib/lessons_analyzer/analyzer.py` | Pattern extraction | `load_sessions()` |
| `temp/AGENT_REPORTS/wave3-p1-days3-4/PLANNER_REPORT.md` | WAVE3-011 design | API validation rules |
| `temp/AGENT_REPORTS/wave3-p1-days3-4/ARCH_REPORT.md` | Days 3-4 architecture | Observability integration |
| `temp/AGENT_REPORTS/wave3-p1-days3-4/DEV_REPORT.md` | Implementation details | CLI commands, test coverage |

---

## 7. Handoff Notes

### For P2 Developer (WAVE3-025 `/debug` command)

1. **Schema migration**: Add `trace_id`, `span_id`, `observability_enabled`, `expedited` columns
2. **Hook integration**: Use `DebugStartup` class pattern from OBSERVABILITY_INTEGRATION.md
3. **Event types**: Extend `_emit_event()` to support contract violation events
4. **Testing**: Add integration tests for trace correlation

### For P2 Architect (WAVE3-022 Contract Validator)

1. **Spec format**: Support OpenAPI 3.x and AsyncAPI 2.x
2. **Change detection**: Implement semantic diff algorithm
3. **Integration points**: Hook into Step 2 (research) and Step 6 (validation)
4. **Observability**: Emit `api_contract_violation` events

### For Day 7 Sprint Close

1. All Track A verification tasks complete
2. Three integration gaps documented with P2 resolution paths
3. API validation design ready for implementation
4. No blockers for P2 developer UX commands

---

*Integration Verification Complete | Ready for Day 7 Sprint Close and P2 Planning*
