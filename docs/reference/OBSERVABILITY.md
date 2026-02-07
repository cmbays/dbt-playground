# Observability Configuration: dbt-playground Debug Protocol

**Version**: 1.0.0
**Created**: 2026-02-04
**Task**: WAVE3-026
**Purpose**: Production-ready observability configuration for Debug Protocol sessions

---

## 1. Monitoring Stack Overview

### 1.1 Stack Components

| Layer | Technology | Version | Purpose | Status |
|-------|-----------|---------|---------|--------|
| **Metrics** | Prometheus | 2.x | Session and step duration metrics | Active |
| **Tracing** | Jaeger | 1.x | Distributed debug session tracing | Active |
| **Logging** | Structured JSON | - | Correlation ID injection, event logging | Active |
| **Visualization** | Grafana | 10.x | Debug Protocol dashboard | Active |
| **Storage** | DuckDB | 1.10.0 | Local metrics persistence | Active |

### 1.2 Configuration Locations

| Component | Config File | Environment Vars |
|-----------|-------------|------------------|
| Tracing | `scripts/lib/observability/tracing.py` | `JAEGER_ENDPOINT`, `TRACE_SAMPLING_RATE` |
| Metrics | `scripts/lib/observability/metrics.py` | `METRICS_PORT`, `OBSERVABILITY_TIER` |
| Logging | `scripts/lib/observability/logger.py` | `LOG_LEVEL` |
| Grafana | `grafana/dashboards/debug-protocol.json` | `GRAFANA_URL` |

### 1.3 Tier Configuration

| Tier | Purpose | Sampling | Output |
|------|---------|----------|--------|
| **Tier 1 (Local)** | Development | 100% | File-based (`temp/traces/`, `temp/metrics/`) |
| **Tier 2 (Staging)** | Small production | 50% | Jaeger + Prometheus |
| **Tier 3 (Production)** | Enterprise scale | 10% | Full observability stack |

```python
from scripts.lib.observability.config import ObservabilityConfig, ObservabilityTier

# Get tier-specific configuration
config = ObservabilityConfig.for_tier(ObservabilityTier.TIER_1_LOCAL)

# Or from environment
config = ObservabilityConfig.from_env()
```

---

## 2. Metrics Registry

### 2.1 Debug Protocol Metrics

| Metric | Type | Labels | Description | Alert Threshold |
|--------|------|--------|-------------|-----------------|
| `debug_sessions_total` | Counter | `severity`, `outcome`, `expedited` | Total debug sessions started | N/A |
| `debug_session_duration_seconds` | Histogram | `severity`, `outcome` | Debug session duration | p95 > 30m |
| `debug_step_duration_seconds` | Histogram | `step_number`, `step_name` | Time spent per protocol step | p95 > 10m |
| `debug_root_cause_total` | Counter | `root_cause_type`, `severity` | Root causes identified by type | N/A |
| `debug_lessons_extracted_total` | Counter | `trigger_type`, `pattern_score_bucket` | Lessons extracted to LESSONS.md | N/A |
| `debug_contract_violations_total` | Counter | `contract_type`, `severity`, `service` | API contract violations | > 5/hour |
| `debug_expedited_path_total` | Counter | `path_type`, `disqualifier` | Expedited vs full path usage | N/A |

### 2.2 Histogram Buckets

**Session Duration** (seconds): `[60, 300, 900, 1800, 3600, 7200]`
- 1 minute, 5 minutes, 15 minutes, 30 minutes, 1 hour, 2 hours

**Step Duration** (seconds): `[10, 30, 60, 120, 300, 600, 1800]`
- 10 seconds to 30 minutes

### 2.3 Usage Example

```python
from scripts.lib.observability.metrics import DebugMetrics, MetricsExporter

# Initialize metrics
metrics = DebugMetrics()

# Record session start
metrics.record_session_start(severity='high', expedited=False)

# Record step duration
metrics.record_step_duration(step_number=1, step_name='Reproduce', duration_seconds=120)

# Record session end
metrics.record_session_end(
    duration_seconds=1800,
    severity='high',
    outcome='resolved',
    root_cause_type='configuration_error'
)

# Export metrics
exporter = MetricsExporter(metrics)
exporter.export()

# Get Prometheus format
print(metrics.to_prometheus())
```

### 2.4 SLI Metrics (Service Level Indicators)

| SLI | Metric | Target |
|-----|--------|--------|
| **Resolution Rate** | `debug_sessions_total{outcome="resolved"}` / total | > 80% |
| **Time to Resolution** | `debug_session_duration_seconds` p50 | < 30 min |
| **Lesson Extraction** | `debug_lessons_extracted_total` / resolved sessions | > 20% |

---

## 3. Alerting Configuration

### 3.1 Alert Definitions

| Alert Name | Severity | Condition | For | Action |
|------------|----------|-----------|-----|--------|
| `HighDebugSessionDuration` | Warning | `histogram_quantile(0.95, debug_session_duration_seconds) > 3600` | 15m | Review debug protocol adherence |
| `LowResolutionRate` | High | `rate(debug_sessions_total{outcome="resolved"}[1d]) / rate(debug_sessions_total[1d]) < 0.7` | 1h | Escalate to senior engineer |
| `ContractViolationSpike` | Critical | `rate(debug_contract_violations_total[5m]) > 0.1` | 5m | Check API compatibility |
| `ExpediteDisqualification` | Info | `rate(debug_expedited_path_total{path_type="full"}[1h]) > 0.5` | 1h | Review expedited criteria |

### 3.2 Escalation Paths

| Severity | Initial Notify | Escalate After | Channel |
|----------|----------------|----------------|---------|
| Critical | On-call engineer | 15 min | PagerDuty/Slack |
| High | Development team | 30 min | Slack #dev-alerts |
| Warning | Team channel | No escalation | Slack #debug-protocol |
| Info | Dashboard only | No escalation | Grafana |

---

## 4. Dashboard Inventory

### 4.1 Dashboard List

| Dashboard Name | Purpose | File | Update Frequency |
|----------------|---------|------|------------------|
| Debug Protocol Overview | Session metrics, root causes | `grafana/dashboards/debug-protocol.json` | Real-time |

### 4.2 Key Panels

1. **Sessions by Outcome** - Pie chart of resolved/escalated/inconclusive
2. **Session Duration Distribution** - Histogram of debug session lengths
3. **Root Cause Frequency** - Bar chart of root cause categories
4. **Step Bottleneck Analysis** - Heatmap of time per protocol step
5. **Expedited Path Usage** - Gauge showing expedited vs full path ratio
6. **Lessons Extracted** - Counter with trend sparkline
7. **Contract Violations** - Time series with severity breakdown

---

## 5. Tracing Configuration

### 5.1 Service Instrumentation

| Service | Language | Library | Sampling Rate | Status |
|---------|----------|---------|---------------|--------|
| `vibe-code-debug` | Python | Custom (WAVE3-025) | Tier-dependent | Active |

### 5.2 Span Naming Convention

All spans follow the pattern: `vibe-code-debug/{operation}`

| Operation | Span Name | Description |
|-----------|-----------|-------------|
| Session | `vibe-code-debug/debug_session` | Root span for entire session |
| Step 1 | `vibe-code-debug/debug_step_1_reproduce` | Reproduce the bug |
| Step 2 | `vibe-code-debug/debug_step_2_blast_radius` | Assess blast radius |
| Step 3 | `vibe-code-debug/debug_step_3_hypothesis` | Form hypothesis |
| Step 4 | `vibe-code-debug/debug_step_4_root_cause` | Identify root cause |
| Step 5 | `vibe-code-debug/debug_step_5_fix` | Implement fix |
| Step 6 | `vibe-code-debug/debug_step_6_validate` | Validate fix |
| Step 7 | `vibe-code-debug/debug_step_7_document` | Document findings |
| Expedited | `vibe-code-debug/expedited_debug` | Expedited path session |

### 5.3 Required Span Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `debug.session_id` | string | Unique session identifier |
| `debug.severity` | string | Bug severity (high/medium/low) |
| `debug.expedited` | boolean | Whether using expedited path |
| `debug.bug_id` | string | Optional bug tracker reference |
| `debug.step.number` | int | Protocol step number (1-7) |
| `debug.step.name` | string | Human-readable step name |
| `debug.findings` | string | What was discovered (truncated) |
| `debug.root_cause` | string | Identified root cause |
| `debug.outcome` | string | Session outcome |
| `debug.lesson_extracted` | boolean | Whether pattern added to LESSONS.md |

### 5.4 Trace Sampling Strategy

| Environment | Sampling Rate | Reason |
|-------------|---------------|--------|
| Development | 100% | Full visibility for debugging |
| Staging | 50% | Balance visibility and storage |
| Production | 10% | Cost optimization |

### 5.5 Local Jaeger Setup

For local development with Jaeger:

```bash
# Run Jaeger all-in-one container
docker run -d --name jaeger \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 14250:14250 \
  -p 14268:14268 \
  -p 14269:14269 \
  jaegertracing/all-in-one:1.54

# Access UI at http://localhost:16686
```

Configure endpoint:

```bash
export OBSERVABILITY_TIER=small_prod
export JAEGER_ENDPOINT=http://localhost:14268/api/traces
```

### 5.6 Usage Example

```python
from scripts.lib.observability.tracing import DebugTracer

# Initialize tracer
tracer = DebugTracer()

# Start session span
context = tracer.start_session_span(
    session_id='debug-2026-02-04-001',
    bug_id='BUG-123',
    severity='high',
    expedited=False
)

# Start step span
step_context = tracer.start_step_span(
    step_number=1,
    step_name='Reproduce',
    parent_context=context
)

# ... do work ...

# End step span
tracer.end_step_span(
    context=step_context,
    findings='Bug reproduced with specific input',
    evidence='temp/evidence/screenshot.png'
)

# End session span
tracer.end_session_span(
    context=context,
    root_cause='Null pointer in validation logic',
    outcome='resolved',
    lesson_extracted=True
)
```

---

## 6. Log Configuration

### 6.1 Structured Log Format

```json
{
  "timestamp": "2026-02-04T10:30:00Z",
  "level": "INFO",
  "service": "vibe-code-debug",
  "logger": "debug_protocol",
  "message": "Debug session started",
  "trace_id": "abc123def456...",
  "span_id": "1234abcd...",
  "session_id": "debug-2026-02-04-001",
  "event": "debug.session.started",
  "severity": "high",
  "bug_description": "API returns 500 on valid input"
}
```

### 6.2 Event Types

| Event | Level | Description |
|-------|-------|-------------|
| `debug.session.started` | INFO | New debug session initiated |
| `debug.session.completed` | INFO | Session ended with outcome |
| `debug.step.N.started` | DEBUG | Protocol step N began |
| `debug.step.N.completed` | DEBUG | Protocol step N finished |
| `debug.symptom.detected` | INFO | New symptom identified |
| `debug.hypothesis.formed` | INFO | Hypothesis created |
| `debug.hypothesis.validated` | INFO | Hypothesis confirmed/rejected |
| `debug.root_cause.identified` | INFO | Root cause found |
| `debug.contract.violation` | WARNING | API contract violated |

### 6.3 Log Retention

| Environment | Retention | Storage |
|-------------|-----------|---------|
| Development | 7 days | Local filesystem |
| Staging | 14 days | Loki/ELK |
| Production | 30 days | Loki/ELK |

### 6.4 Usage Example

```python
from scripts.lib.observability.logger import get_logger

# Get logger
logger = get_logger('debug_protocol')

# Set correlation IDs (from tracer)
logger.set_correlation_ids(
    trace_id=tracer.get_current_trace_id(),
    span_id=tracer.get_current_span_id(),
    session_id='debug-2026-02-04-001'
)

# Log events
logger.session_started(
    session_id='debug-2026-02-04-001',
    bug_description='API returns 500 on valid input',
    severity='high'
)

logger.root_cause_identified(
    session_id='debug-2026-02-04-001',
    root_cause='Null pointer in validation logic',
    category='code_error'
)

logger.session_completed(
    session_id='debug-2026-02-04-001',
    outcome='resolved',
    duration_minutes=25,
    lesson_extracted=True
)
```

---

## 7. Integration with Debug Protocol

### 7.1 Automatic Instrumentation

The observability hooks module (`scripts/lib/observability/hooks.py`) provides automatic instrumentation:

```python
from scripts.lib.observability.hooks import instrument_debug_session

# Wrap your debug session
@instrument_debug_session(severity='high')
def debug_api_error():
    # Your debug logic here
    pass
```

### 7.2 Memory System Integration

Metrics are emitted to `memory/events.jsonl` for compound learning:

```json
{"timestamp": "2026-02-04T10:30:00Z", "type": "debug_session", "outcome": "resolved", "duration_minutes": 25}
```

### 7.3 DuckDB Storage (ADR-015)

Debug session data stored in DuckDB for local analytics:

```sql
-- Query session metrics
SELECT
    date_trunc('day', started_at) as day,
    outcome,
    COUNT(*) as sessions,
    AVG(duration_seconds) / 60 as avg_minutes
FROM debug_sessions
GROUP BY 1, 2
ORDER BY 1 DESC;
```

---

## 8. Cost Estimation

### 8.1 Tier 1 (Local Development)

| Component | Monthly Cost |
|-----------|--------------|
| File storage | $0 |
| DuckDB | $0 |
| **Total** | **$0** |

### 8.2 Tier 2 (Small Production)

| Component | Monthly Cost |
|-----------|--------------|
| Jaeger (self-hosted) | $0-20 |
| Prometheus (self-hosted) | $0-20 |
| Grafana (self-hosted) | $0 |
| **Total** | **$0-40** |

### 8.3 Tier 3 (Production Scale)

| Component | Monthly Cost |
|-----------|--------------|
| Grafana Cloud (traces) | $50-200 |
| Grafana Cloud (metrics) | $50-200 |
| Grafana Cloud (logs) | $50-200 |
| **Total** | **$150-600** |

---

## 9. Verification Checklist (Gate T2-1)

- [x] Metrics endpoint exposed (`scripts/lib/observability/metrics.py`)
- [x] SLI metrics defined and collecting
- [x] Grafana dashboard created (`grafana/dashboards/debug-protocol.json`)
- [x] Jaeger/tracing receiving traces (file-based for Tier 1)
- [x] Sampling rate appropriate for tier
- [x] Structured JSON logging configured
- [x] Logs include correlation IDs (trace_id, span_id, session_id)
- [x] Debug protocol events logged
- [ ] Critical alerts configured and tested (Tier 2+)
- [ ] Escalation paths documented (Tier 2+)
- [x] Service overview dashboard exists

---

## 10. Quick Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OBSERVABILITY_TIER` | `local` | Deployment tier (local/small_prod/production) |
| `JAEGER_ENDPOINT` | None | Jaeger HTTP endpoint for traces |
| `TRACE_SAMPLING_RATE` | 1.0 | Sampling rate (0.0-1.0) |
| `METRICS_PORT` | 8000 | Prometheus metrics port |
| `LOG_LEVEL` | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |

### File Locations (Tier 1)

| Artifact | Location |
|----------|----------|
| Traces | `temp/traces/trace_*.json` |
| Metrics | `temp/metrics/metrics_*.prom` |
| Debug sessions | `database/debug_sessions/debug_sessions.duckdb` |
| Memory events | `memory/events.jsonl` |

---

## Related Documentation

- [DEPLOYMENT_VALIDATION_CHECKLIST.md](../../temp/DEBUG_REPORTS/DEPLOYMENT_VALIDATION_CHECKLIST.md) - Gate T2-1 requirement
- [OBSERVABILITY_INTEGRATION.md](../../temp/vibe_coding/OBSERVABILITY_INTEGRATION.md) - Debug protocol integration design
- [ADR-015](../../docs/decisions/ADR-015-duckdb-for-metrics.md) - DuckDB for metrics storage

---

*Observability Configuration v1.0.0 | Wave 3 Task: WAVE3-026*
