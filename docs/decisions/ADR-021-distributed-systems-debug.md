---
audience: [architect, developer, multi-agent]
priority: high
size: medium
dependencies: [ADR-019, ADR-020]
last_updated: 2026-02-04
status: approved
tags: [architecture, debugging, wave3, distributed-systems, observability]
---

# ADR-021: Distributed Systems Debug Scope

**Status**: Approved
**Date**: 2026-02-04
**Deciders**: Architect, Planner
**Related Issue**: #226
**Wave 3 Task**: WAVE3-004
**Depends On**: ADR-019, ADR-020

---

## Context

The Phase 1 Debug Agent protocol assumes monolithic application architecture:
- Single codebase to search
- One database to query
- Synchronous request/response flow
- Local reproduction possible

Modern production systems are distributed:
- **Microservices**: Multiple services with independent deployments
- **Async processing**: Message queues, background jobs, event sourcing
- **Eventual consistency**: State may differ across replicas
- **Network partitions**: Services may be temporarily unreachable

Wave 3 must extend the Debug protocol to handle distributed system bugs, which exhibit unique characteristics:

| Monolith Bug | Distributed Bug |
|--------------|-----------------|
| Single stack trace | Multiple service traces |
| Synchronous flow | Async, out-of-order events |
| Single database | Multiple databases, caches |
| Local reproduction | Requires service mesh |
| Instant state | Eventual consistency window |

Without distributed systems support, the Debug protocol cannot handle:
- Race conditions between services
- Partial failures (one service up, another down)
- Data inconsistency across replicas
- Timeout-induced cascading failures

## Decision

**Extend the Debug protocol with cross-service tracing, timestamp correlation, and state snapshots.**

### Protocol Extensions

#### Extension 1: Cross-Service Trace Collection (Step 2)

Add to Step 2 (Research the Blast Radius):

```markdown
## Step 2 Extension: Distributed Trace Collection

For distributed system bugs, collect traces from ALL involved services:

1. **Identify request ID / correlation ID**
   - Find the unique identifier that links requests across services
   - Common: X-Request-ID, X-Correlation-ID, trace_id

2. **Collect traces from each service**
   - Service A logs: Filter by correlation ID
   - Service B logs: Filter by correlation ID
   - Queue/broker logs: Message ID correlation

3. **Build timeline**
   | Timestamp | Service | Event | Data |
   |-----------|---------|-------|------|
   | T+0ms | API Gateway | Request received | {payload} |
   | T+5ms | Auth Service | Token validated | {user_id} |
   | T+12ms | Order Service | Order created | {order_id} |
   | T+15ms | Queue | Message published | {message_id} |
   | T+50ms | Inventory Service | Stock check | {result} |

4. **Identify gaps**
   - Missing events in timeline = potential failure point
   - Timestamp ordering anomalies = clock skew or race condition
```

#### Extension 2: Timestamp Correlation (Step 3)

Add to Step 3 (Present Findings):

```markdown
## Step 3 Extension: Timestamp Analysis

For distributed bugs, analyze timestamp patterns:

DISTRIBUTED FINDINGS:
- **Timeline anomalies**:
  - Event B occurred before Event A (expected A -> B)
  - Gap of {N}ms between events (expected <{M}ms)
  - Duplicate events at {timestamps}

- **Causality chain**:
  ```
  Service A (T+0) --HTTP--> Service B (T+5) --Queue--> Service C (T+50)
                                                           |
                                                           v
                                              Service D (T+55) [FAILURE]
  ```

- **Clock skew assessment**:
  - Services appear synchronized: Yes/No
  - Maximum observed skew: {N}ms
  - Impact on bug: {assessment}
```

#### Extension 3: State Snapshots (Step 4)

Add to Step 4 (Root Cause Analysis):

```markdown
## Step 4 Extension: Distributed State Analysis

For eventual consistency bugs, capture state snapshots:

STATE SNAPSHOT:
- **Primary database** (Service A): {state at T+N}
- **Read replica** (Service A): {state at T+N}
- **Cache** (Redis): {state at T+N}
- **Service B database**: {state at T+N}

CONSISTENCY ANALYSIS:
- Expected state: {what should be true}
- Actual state: {what was observed}
- Consistency window: {N}ms (time for all systems to converge)
- Bug occurs during: {before/during/after consistency window}

ROOT CAUSE CLASSIFICATION:
- [ ] Race condition (two writes to same resource)
- [ ] Stale read (read before write propagated)
- [ ] Partial failure (some services succeeded, others failed)
- [ ] Timeout cascade (one timeout caused others)
- [ ] Network partition (service unreachable)
```

#### Extension 4: Service Dependency Map

Add to Step 2 findings:

```markdown
## Service Dependency Map

```
[API Gateway]
     |
     v
[Auth Service] -----> [User DB]
     |
     v
[Order Service] ----> [Order DB]
     |                    |
     +---> [Queue] <------+
              |
              v
     [Inventory Service] --> [Inventory DB]
              |
              v
     [Notification Service] --> [Email Provider]
```

Services involved in this bug: [Order Service, Inventory Service]
External dependencies: [Email Provider - 3rd party]
```

### New Evidence Types

Add to evidence collection:

| Evidence Type | Source | Format |
|---------------|--------|--------|
| Distributed trace | Jaeger, Zipkin, X-Ray | JSON export |
| Service logs (correlated) | ELK, CloudWatch | Filtered log bundle |
| Metrics at time of bug | Prometheus, Grafana | Screenshot + query |
| Database state snapshot | pg_dump, mysqldump | SQL or JSON |
| Queue state | RabbitMQ, SQS | Message list + DLQ |
| Network capture | tcpdump, Wireshark | PCAP (if relevant) |

## Rationale

### Why Cross-Service Tracing

1. **Visibility**: Cannot debug what you cannot see
2. **Causality**: Trace shows actual event ordering across services
3. **Industry standard**: OpenTelemetry, Jaeger widely adopted
4. **Root cause isolation**: Narrows from "somewhere in the system" to specific service

### Why Timestamp Correlation

1. **Distributed systems are time-sensitive**: Race conditions depend on timing
2. **Clock skew is real**: Services may have different clock times
3. **Ordering matters**: A -> B -> C failures differ from A -> C -> B
4. **Evidence for root cause**: Timestamps prove causality

### Why State Snapshots

1. **Eventual consistency bugs are common**: Stale reads, partial updates
2. **State divergence is the bug**: Capturing state proves the divergence
3. **Reproduction**: Snapshots enable controlled reproduction
4. **Post-mortem value**: Understand system state at failure time

## Consequences

### Positive

- **Production-ready**: Protocol can handle real distributed system bugs
- **Evidence-based**: Traces and snapshots provide concrete evidence
- **Systematic**: Step-by-step approach for complex bugs
- **Tool-agnostic**: Works with any tracing/logging system

### Negative

- **Higher CPU/disk during debug**: Collecting traces and snapshots is expensive
- **Requires service instrumentation**: Services must emit correlation IDs
- **New failure modes**: Tracing service itself could fail
- **Complexity increase**: Protocol is longer for distributed bugs

### Mitigation

| Negative | Mitigation |
|----------|------------|
| CPU/disk usage | Limit trace collection to bug time window (+/- 5 minutes) |
| Instrumentation required | Document minimum instrumentation for debug-readiness |
| Tracing service failures | Fallback to log correlation if trace unavailable |
| Complexity | Gate on bug type: use extensions only for multi-service bugs |

## Alternatives Considered

### Alternative 1: No Distributed Support (Phase 1 Only)

**Pros**: Simpler protocol
**Cons**: Cannot debug production bugs, limits protocol usefulness
**Rejected**: Wave 3 goal is production readiness

### Alternative 2: Full APM Integration

**Pros**: Comprehensive, real-time, dashboards
**Cons**: Vendor lock-in, cost, overkill for debugging
**Rejected**: APM is for monitoring, not debugging; can use APM data as evidence

### Alternative 3: Chaos Engineering Approach

**Pros**: Proactive bug finding
**Cons**: Different goal (prevention vs diagnosis)
**Rejected**: Complementary but not a substitute for debug protocol

## Implementation Notes

1. **Gate check**: At Step 1, determine if bug is distributed (involves >1 service)
2. **Correlation ID hunt**: First priority is finding the request correlation ID
3. **Timeline tool**: Future enhancement: auto-build timeline from logs
4. **Snapshot script**: Provide template script for state snapshot collection
5. **Evidence folder**: Store all distributed evidence in `evidence/distributed/`

## Related

- [ADR-019: Debug Session Persistence](ADR-019-debug-session-persistence.md) - Evidence storage
- [ADR-020: Multi-Agent Coordination](ADR-020-multi-agent-coordination.md) - Multi-agent findings
- [WAVE3_PATHWAY_STRATEGY.md](../../temp/vibe_coding/WAVE3_PATHWAY_STRATEGY.md) - Tier 2/3 observability
- [WAVE3_PATHWAY_STRATEGY.md](../../temp/vibe_coding/WAVE3_PATHWAY_STRATEGY.md) - Gap analysis
- [x_post_backend.txt](../../temp/vibe_coding/x_post_backend.txt) - Original protocol

---

*Approved as part of Wave 3 Backend Leveling (WAVE3-004)*
