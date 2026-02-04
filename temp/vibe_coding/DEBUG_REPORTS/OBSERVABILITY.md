---
audience: [architect, developer, devops, on-call]
priority: high
size: large
status: active
tags: [observability, monitoring, metrics, tracing, alerting, template]
wave3_task: WAVE3-016
---

# OBSERVABILITY.md Template

**Version**: 1.0.0
**Created**: 2026-02-05
**Task**: WAVE3-016
**Purpose**: Standard template for documenting observability setup in backend services
**Word Count**: ~1,800

---

## How to Use This Template

1. Copy this template to your project's documentation folder
2. Fill in each section with your project's observability configuration
3. Update when monitoring, alerts, or dashboards change
4. Reference during incident response and debugging (integrates with INCIDENT_TEMPLATE.md)
5. Required for Tier 2 promotion (Gate T2-1 in DEPLOYMENT_VALIDATION_CHECKLIST.md)

**Time Investment**: 3-4 hours initial setup, 30 min per significant change

---

# Observability Configuration: {Project Name}

## 1. Monitoring Stack Overview

### 1.1 Stack Components

| Layer | Technology | Version | Purpose | Status |
|-------|-----------|---------|---------|--------|
| **Metrics** | [Prometheus/Datadog/CloudWatch] | [version] | System and application metrics | [Active/Planned] |
| **Tracing** | [Jaeger/Tempo/X-Ray] | [version] | Distributed request tracing | [Active/Planned] |
| **Logging** | [Loki/ELK/CloudWatch Logs] | [version] | Centralized log aggregation | [Active/Planned] |
| **Visualization** | [Grafana/Kibana/CloudWatch] | [version] | Dashboards and exploration | [Active/Planned] |
| **Alerting** | [PagerDuty/OpsGenie/Slack] | [version] | Incident notification | [Active/Planned] |

### 1.2 Configuration Locations

| Component | Config File | Environment Vars |
|-----------|-------------|------------------|
| Prometheus | `prometheus/prometheus.yml` | `PROMETHEUS_URL` |
| Jaeger | `jaeger/config.yml` | `JAEGER_AGENT_HOST` |
| Grafana | `grafana/dashboards/*.json` | `GRAFANA_URL` |

---

## 2. Metrics Registry

### 2.1 System Metrics (Per Service)

| Metric | Type | Labels | Description | Alert Threshold |
|--------|------|--------|-------------|-----------------|
| `process_cpu_seconds_total` | Counter | `service` | CPU usage | > 80% sustained |
| `process_resident_memory_bytes` | Gauge | `service` | Memory usage | > 90% of limit |
| `http_requests_total` | Counter | `service, method, status` | Request count | N/A |
| `http_request_duration_seconds` | Histogram | `service, method` | Request latency | p95 > 500ms |
| `db_connections_active` | Gauge | `service, database` | Active DB connections | > 80% pool |

### 2.2 SLI Metrics (Service Level Indicators)

| SLI | Metric | Target |
|-----|--------|--------|
| **Availability** | `http_requests_total{status!~"5.."}` | 99.9% |
| **Latency** | `http_request_duration_seconds` p95 | < 500ms |
| **Throughput** | `http_requests_total` | > 100/min |

---

## 3. Alerting Configuration

### 3.1 Alert Definitions

| Alert Name | Severity | Condition | For |
|------------|----------|-----------|-----|
| `HighErrorRate` | Critical | `rate(http_requests_total{status=~"5.."}[5m]) > 0.01` | 5m |
| `HighLatency` | High | `histogram_quantile(0.95, http_request_duration_seconds) > 1` | 10m |
| `DatabaseDown` | Critical | `up{job="database"} == 0` | 1m |
| `DiskSpaceLow` | Warning | `disk_free_bytes / disk_total_bytes < 0.1` | 15m |

### 3.2 Escalation Paths

| Severity | Initial Notify | Escalate After |
|----------|----------------|----------------|
| Critical | On-call engineer | 15 min |
| High | On-call engineer | 30 min |
| Warning | Slack channel | No escalation |

---

## 4. Dashboard Inventory

### 4.1 Dashboard List

| Dashboard Name | Purpose | Update Frequency | Owner |
|----------------|---------|------------------|-------|
| Service Overview | High-level health | Real-time | Platform team |
| Request Performance | Latency analysis | Real-time | Backend team |
| Database Health | Query monitoring | Real-time | DBA team |
| Error Analysis | Error rates | Real-time | Backend team |
| Debug Protocol | Debug session metrics | Daily | Debug team |

---

## 5. Incident Runbooks

### 5.1 Runbook Index

| Runbook | Alert Triggered By | Link |
|---------|-------------------|------|
| High Error Rate | `HighErrorRate` | `docs/runbooks/high-error-rate.md` |
| Database Recovery | `DatabaseDown` | `docs/runbooks/database-recovery.md` |
| Service Restart | Manual | `docs/runbooks/service-restart.md` |
| Rollback Procedure | Manual | `docs/runbooks/rollback.md` |

---

## 6. Tracing Configuration

### 6.1 Service Instrumentation

| Service | Language | Library | Sampling Rate | Status |
|---------|----------|---------|---------------|--------|
| [Service A] | Python | opentelemetry-python | 10% (prod) | Active |
| [Service B] | Node.js | @opentelemetry/node | 10% (prod) | Active |

### 6.2 Trace Sampling Strategy

| Environment | Sampling Rate | Reason |
|-------------|---------------|--------|
| Development | 100% | Full visibility for debugging |
| Staging | 50% | Balance visibility and cost |
| Production | 10% | Cost optimization |

---

## 7. Log Configuration

### 7.1 Structured Log Format

```json
{
  "timestamp": "2026-02-05T10:30:00Z",
  "level": "INFO",
  "service": "api-gateway",
  "trace_id": "abc123",
  "message": "Request processed",
  "duration_ms": 45
}
```

### 7.2 Log Retention

| Environment | Retention | Storage |
|-------------|-----------|---------|
| Development | 7 days | Local |
| Staging | 14 days | Loki (free tier) |
| Production | 30 days | Loki (paid) |

---

## 8. Cost Estimation

### 8.1 Tier 2 (Small Production) Costs

| Component | Monthly Cost |
|-----------|--------------|
| Metrics | $0-50 |
| Traces | $0-50 |
| Logs | $0-50 |
| **Total** | **$0-150** |

### 8.2 Tier 3 (Production Scale) Costs

| Component | Monthly Cost |
|-----------|--------------|
| Metrics | $50-200 |
| Traces | $100-300 |
| Logs | $100-300 |
| **Total** | **$250-800** |

---

## 9. Verification Checklist (Gate T2-1)

- [ ] Prometheus/metrics endpoint exposed on all services
- [ ] SLI metrics defined and collecting
- [ ] Grafana dashboards created
- [ ] Jaeger/Tempo receiving traces
- [ ] Sampling rate appropriate for tier
- [ ] Structured JSON logging configured
- [ ] Logs aggregating in central location
- [ ] Critical alerts configured and tested
- [ ] Escalation paths documented
- [ ] Service overview dashboard exists

---

## Related Documentation

- [BACKEND_STRUCTURE_TEMPLATE.md](./BACKEND_STRUCTURE_TEMPLATE.md) - Service inventory
- [DEPLOYMENT_VALIDATION_CHECKLIST.md](./DEPLOYMENT_VALIDATION_CHECKLIST.md) - Gate T2-1 requirement
- [INCIDENT_TEMPLATE.md](./INCIDENT_TEMPLATE.md) - Incident response using observability
- [OBSERVABILITY_INTEGRATION.md](../OBSERVABILITY_INTEGRATION.md) - Debug protocol integration

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-02-05 | Initial template (WAVE3-016) | Architect |

---

*Observability Template v1.0.0 | Wave 3 Task: WAVE3-016*
