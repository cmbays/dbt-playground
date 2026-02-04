---
audience: [architect, developer, on-call]
priority: high
size: large
status: active
tags: [observability, tracing, metrics, jaeger, prometheus, debug-protocol]
wave3_task: WAVE3-013
---

# Observability Integration for Debug Protocol

**Version**: 1.0.0
**Created**: 2026-02-05
**Task**: WAVE3-013
**Author**: Technical Architect
**Word Count**: ~2,500

---

## Executive Summary

This document defines how the 7-Step Debug Protocol integrates with observability infrastructure (Jaeger, Prometheus, structured logging) to enable production-grade debugging. Observability transforms the Debug protocol from a local troubleshooting tool to a system that can trace issues across distributed services, correlate incidents with historical patterns, and feed learnings back into the compound learning loop.

**Key Integration Points**:
- Debug sessions emit Jaeger spans for tracing
- Protocol steps are instrumented with Prometheus metrics
- Structured logs correlate with session IDs
- LESSONS.md Analyzer (WAVE3-021) consumes observability signals

---

## 1. Observability Signals for Debug Session Tracing

### 1.1 Signal Categories

The Debug protocol produces three categories of observability signals aligned with the three pillars of observability:

| Signal Type | Purpose | Storage | Retention | Tier Availability |
|-------------|---------|---------|-----------|-------------------|
| **Traces** | Track debug flow across steps | Jaeger/Tempo | 7 days | Tier 2+ |
| **Metrics** | Quantify debug patterns | Prometheus | 30 days | Tier 2+ |
| **Logs** | Detailed diagnostic output | Loki/stdout | 14 days | All Tiers |

### 1.2 Critical Signals by Debug Phase

#### Phase 1: Pre-Debug (Symptom Detection)

| Signal | Type | Purpose | Alert Threshold |
|--------|------|---------|-----------------|
| `debug.session.started` | Trace | Session initiation | N/A |
| `debug.symptom.detected` | Log | Capture initial symptoms | N/A |
| `debug.severity.assessed` | Metric | Classify bug severity | Critical triggers page |

#### Phase 2: During Debug (Investigation)

| Signal | Type | Purpose | Alert Threshold |
|--------|------|---------|-----------------|
| `debug.step.{1-7}.started` | Trace | Track protocol phase entry | N/A |
| `debug.step.{1-7}.completed` | Trace | Track protocol phase exit | N/A |
| `debug.step.duration_seconds` | Metric | Time per step | > 30min on Step 3 |
| `debug.hypothesis.formed` | Log | Capture hypotheses | N/A |
| `debug.hypothesis.validated` | Log | Mark hypothesis outcomes | N/A |
| `debug.blast_radius.services` | Metric | Count affected services | > 5 services |
| `debug.expedited_path.taken` | Metric | Track fast-path usage | N/A |

#### Phase 3: Post-Debug (Learning Extraction)

| Signal | Type | Purpose | Alert Threshold |
|--------|------|---------|-----------------|
| `debug.session.completed` | Trace | Session termination | N/A |
| `debug.root_cause.identified` | Log | Capture root cause | N/A |
| `debug.lesson.extracted` | Metric | Count new patterns | N/A |
| `debug.time_to_resolution` | Metric | Measure TTR | > 2 hours |

---

## 2. Instrumenting the 7-Step Protocol

### 2.1 Protocol Step Span Mapping

Each protocol step becomes a Jaeger span with standardized attributes:

```
Debug Session (root span)
├── Step 1: Reproduce Bug
│   ├── symptom_type: string
│   ├── reproducible: boolean
│   └── evidence_path: string
├── Step 2: Blast Radius Research
│   ├── affected_services: string[]
│   ├── api_contracts_checked: int
│   └── schema_version: string
├── Step 3: Hypothesis Formation (CRITICAL)
│   ├── hypothesis_count: int
│   ├── evidence_collected: int
│   └── theories_rejected: int
├── Step 4: Root Cause vs Symptom Classification (CRITICAL)
│   ├── root_cause_validated: boolean
│   ├── contributing_factors: string[]
│   └── misclassification_risk: string
├── Step 5: Fix Implementation
│   ├── fix_type: "code" | "config" | "data"
│   ├── files_changed: int
│   └── rollback_plan: boolean
├── Step 6: Fix Validation
│   ├── tests_passed: boolean
│   ├── regression_risk: string
│   └── verification_method: string
└── Step 7: Document & Learn
    ├── lesson_extracted: boolean
    ├── pattern_score: float
    └── lessons_file_updated: boolean
```

### 2.2 Observability Hook Architecture

```python
from typing import Callable, List
from dataclasses import dataclass
from enum import Enum

class DebugPhase(Enum):
    PRE_DEBUG = "pre_debug"
    DURING_DEBUG = "during_debug"
    POST_DEBUG = "post_debug"

@dataclass
class ObservabilityHook:
    phase: DebugPhase
    name: str
    callback: Callable
    priority: int = 100

class DebugStartup:
    """Centralized debug session initialization with observability."""

    def __init__(self):
        self.hooks: dict[DebugPhase, List[ObservabilityHook]] = {
            DebugPhase.PRE_DEBUG: [],
            DebugPhase.DURING_DEBUG: [],
            DebugPhase.POST_DEBUG: [],
        }
        self._register_default_hooks()

    def _register_default_hooks(self):
        """Register built-in observability hooks."""
        # PRE_DEBUG hooks
        self.register_hook(DebugPhase.PRE_DEBUG, "initialize_tracer", self._init_tracer, priority=10)
        self.register_hook(DebugPhase.PRE_DEBUG, "setup_metrics", self._setup_metrics, priority=20)

        # POST_DEBUG hooks
        self.register_hook(DebugPhase.POST_DEBUG, "emit_session_metrics", self._emit_session_metrics, priority=10)
        self.register_hook(DebugPhase.POST_DEBUG, "trigger_lessons_analysis", self._trigger_lessons_analysis, priority=100)
```

---

## 3. Metrics for Incident Pattern Detection

### 3.1 Core Debug Metrics (Prometheus)

```yaml
metrics:
  - name: debug_sessions_total
    type: counter
    labels: [severity, outcome, expedited]
    description: Total debug sessions started

  - name: debug_session_duration_seconds
    type: histogram
    buckets: [60, 300, 900, 1800, 3600, 7200]
    labels: [severity, outcome]
    description: Debug session duration

  - name: debug_step_duration_seconds
    type: histogram
    buckets: [10, 30, 60, 120, 300, 600, 1800]
    labels: [step_number, step_name]
    description: Time spent per protocol step

  - name: debug_root_cause_total
    type: counter
    labels: [root_cause_type, severity]
    description: Root causes identified by type

  - name: debug_lessons_extracted_total
    type: counter
    labels: [trigger_type, pattern_score_bucket]
    description: Lessons extracted to LESSONS.md
```

### 3.2 Incident Correlation Metrics

| Metric | Purpose |
|--------|---------|
| `debug_root_cause_total` | Identify recurring root causes |
| `debug_session_duration_seconds` | Find long-running debug sessions |
| `debug_step_duration_seconds` | Identify bottleneck steps |
| `debug_expedited_vs_full` | Measure protocol efficiency |

---

## 4. Error Categorization for Incident Correlation

### 4.1 Error Taxonomy

```
Error Categories
├── Infrastructure
│   ├── network_timeout
│   ├── connection_refused
│   ├── dns_resolution_failed
│   └── resource_exhausted
├── Data
│   ├── schema_mismatch
│   ├── constraint_violation
│   ├── null_reference
│   └── data_corruption
├── Logic
│   ├── race_condition
│   ├── deadlock
│   ├── off_by_one
│   └── state_inconsistency
├── API
│   ├── contract_violation
│   ├── version_mismatch
│   ├── auth_failure
│   └── rate_limited
└── External
    ├── third_party_failure
    ├── dependency_unavailable
    └── integration_timeout
```

### 4.2 Incident Severity Correlation

| Error Category | Default Severity | Escalation Trigger |
|----------------|------------------|-------------------|
| Infrastructure.resource_exhausted | Critical | Immediate |
| Data.data_corruption | Critical | Immediate |
| API.contract_violation | High | > 3 occurrences/hour |
| Logic.race_condition | High | > 1 occurrence |
| Logic.off_by_one | Medium | > 10 occurrences/day |
| External.third_party_failure | Low | External to us |

---

## 5. Integration with WAVE3-020 (Session Tracker)

### 5.1 Data Flow

```
Debug Session Start
        │
        ├─── Traces (Jaeger spans) → Jaeger/Tempo (7 day retain)
        ├─── Metrics (Prometheus) → Prometheus (30 day retain)
        └─── Logs (structured JSON) → Loki/stdout (14 day retain)
```

### 5.2 Session Tracker Schema Extension

```sql
ALTER TABLE debug_sessions ADD COLUMN trace_id VARCHAR;
ALTER TABLE debug_sessions ADD COLUMN span_id VARCHAR;
ALTER TABLE debug_sessions ADD COLUMN observability_enabled BOOLEAN DEFAULT TRUE;

ALTER TABLE debug_steps ADD COLUMN span_id VARCHAR;
ALTER TABLE debug_steps ADD COLUMN metrics_emitted BOOLEAN DEFAULT FALSE;

CREATE INDEX idx_debug_sessions_trace ON debug_sessions(trace_id);
```

---

## 6. Integration with WAVE3-021 (LESSONS Analyzer)

### 6.1 Observability Signals for Pattern Extraction

| Signal Source | What Analyzer Extracts |
|---------------|------------------------|
| Jaeger traces | Step duration anomalies |
| Prometheus metrics | Recurring root causes |
| Structured logs | Hypothesis validation rates |
| Session Tracker | Fix effectiveness |

### 6.2 Pattern Detection Algorithm

```python
class LessonsAnalyzer:
    def detect_recurring_patterns(self, lookback_days: int = 30) -> list:
        """Identify patterns meeting extraction threshold."""
        patterns = []

        # Query recurring root causes from Prometheus
        root_cause_query = f"""
            sum by (root_cause_type) (
                increase(debug_root_cause_total[{lookback_days}d])
            ) > 2
        """
        recurring_causes = self.prometheus.query(root_cause_query)

        for cause in recurring_causes:
            patterns.append({
                "type": "recurring_root_cause",
                "name": cause["metric"]["root_cause_type"],
                "frequency": cause["value"],
                "score": self.calculate_pattern_score(cause),
            })

        return sorted(patterns, key=lambda p: p["score"], reverse=True)
```

---

## 7. Jaeger Span Patterns

### 7.1 Span Naming Convention

```
vibe-code-debug/debug_session
vibe-code-debug/debug_step_1_reproduce
vibe-code-debug/debug_step_2_blast_radius
vibe-code-debug/debug_step_3_hypothesis
vibe-code-debug/debug_step_4_root_cause
vibe-code-debug/debug_step_5_fix
vibe-code-debug/debug_step_6_validate
vibe-code-debug/debug_step_7_document
vibe-code-debug/expedited_debug
```

### 7.2 Span Attribute Standards

| Attribute | Type | Description | Required |
|-----------|------|-------------|----------|
| `debug.session_id` | string | Unique session identifier | Yes |
| `debug.bug_id` | string | Bug tracker reference | Yes |
| `debug.severity` | string | critical/high/medium/low | Yes |
| `debug.step.number` | int | Protocol step (1-7) | Yes (steps) |
| `debug.step.name` | string | Human-readable step name | Yes (steps) |
| `debug.expedited` | boolean | Using expedited path | Yes |
| `debug.root_cause` | string | Identified root cause | No |
| `debug.fix_applied` | string | Description of fix | No |
| `debug.lesson_extracted` | boolean | Pattern added to LESSONS | No |

---

## 8. Cost Considerations by Tier

### 8.1 Tier 1 (Local MVP): Zero Cost
- Traces: In-memory / file export
- Metrics: Local Prometheus or none
- Logs: stdout / file

### 8.2 Tier 2 (Small Production): $20-100/month
- Traces: Grafana Cloud (free tier)
- Metrics: Grafana Cloud (free tier)
- Logs: Grafana Loki (free tier)

### 8.3 Tier 3 (Production Scale): $200-1000/month
- Traces: Grafana Tempo (paid)
- Metrics: Prometheus + Grafana
- Logs: Grafana Loki (paid)

---

## Related Documentation

- [BACKEND_STRUCTURE_TEMPLATE.md](./DEBUG_REPORTS/BACKEND_STRUCTURE_TEMPLATE.md) - Service map for blast radius
- [DEPLOYMENT_VALIDATION_CHECKLIST.md](./DEBUG_REPORTS/DEPLOYMENT_VALIDATION_CHECKLIST.md) - Gate T2-1 observability requirement
- [INCIDENT_TEMPLATE.md](./DEBUG_REPORTS/INCIDENT_TEMPLATE.md) - Incident correlation
- [OBSERVABILITY.md](./DEBUG_REPORTS/OBSERVABILITY.md) - Observability setup template (WAVE3-016)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-02-05 | Initial observability integration spec (WAVE3-013) | Architect |

---

*Observability Integration v1.0.0 | Wave 3 Task: WAVE3-013*
