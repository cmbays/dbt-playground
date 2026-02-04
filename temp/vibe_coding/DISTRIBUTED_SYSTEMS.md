# Distributed Systems Debugging Guide

**Version**: 1.0
**Created**: 2026-02-04
**Task**: WAVE3-003
**Related**: [x_post_backend.txt](./x_post_backend.txt), [DEBUG_REPORTS](./DEBUG_REPORTS/README.md)

---

## Introduction

This guide extends the 7-step Debug Agent protocol (`x_post_backend.txt`) for debugging bugs in distributed systems. While the core protocol handles monolithic applications excellently, distributed systems introduce unique failure modes that require specialized techniques.

### When to Use This Guide vs Standard Protocol

| Scenario | Use Standard Protocol | Use This Guide |
|----------|----------------------|----------------|
| Single service bug | Yes | No |
| Bug in shared library | Yes | No |
| Request spans 2+ services | No | **Yes** |
| Async job failures | Depends | **Yes** (if cross-service) |
| Data inconsistency across DBs | No | **Yes** |
| Intermittent failures under load | No | **Yes** |
| Timeout cascades | No | **Yes** |
| "It works locally but not in staging" | No | **Yes** |

**Rule of thumb**: If you need logs from more than one service to understand the bug, use this guide.

### Characteristics of Distributed Bugs

Distributed bugs differ from monolith bugs in predictable ways:

| Characteristic | Monolith Bug | Distributed Bug |
|----------------|--------------|-----------------|
| **Reproducibility** | Usually consistent | Often intermittent |
| **Evidence location** | Single log file | Multiple services + queues |
| **Time ordering** | Sequential | Concurrent, possibly out-of-order |
| **State visibility** | Single database | Multiple databases, caches, queues |
| **Failure mode** | All or nothing | Partial failures possible |
| **Root cause** | In your code | Possibly in infrastructure |

### Key Differences from Monolith Debugging

1. **No single source of truth**: State is distributed across services
2. **Network is unreliable**: Timeouts, retries, and partitions are normal
3. **Time is relative**: Clock skew means timestamps are approximate
4. **Partial failure is expected**: Some services succeed while others fail
5. **Eventual consistency means eventual bugs**: Data propagation delays cause issues

---

## Pre-Debug Checklist (New Step 1.5)

Before starting distributed debugging, complete this checklist. Missing any item will significantly slow your investigation.

### Required Before Starting

- [ ] **Identify all services involved in the failing request**
  - List every service the request touches
  - Include async workers, message queues, caches
  - Document the expected flow path

- [ ] **Locate correlation ID / trace ID in system**
  - What header carries the trace ID? (`X-Request-ID`, `X-Correlation-ID`, `traceparent`)
  - Is it propagated through all services?
  - Can you query logs by trace ID?

- [ ] **Verify access to logs from each service**
  - Can you access logs for Service A, B, C...?
  - Do you have the right permissions?
  - Are logs centralized or must you query each service separately?

- [ ] **Check APM/tracing tool availability**
  - Jaeger / Zipkin / Tempo (distributed tracing)
  - DataDog / New Relic / Grafana (APM)
  - CloudWatch / Stackdriver (cloud-native)
  - If no tracing: You will need to correlate logs manually

- [ ] **Document service topology/dependency graph**
  - Draw or reference the service dependency diagram
  - Note which services are synchronous vs asynchronous
  - Identify any message queues, event buses, or caches

### Pre-Debug Checklist Template

```markdown
## Pre-Debug Assessment

**Bug Description**: [one sentence]
**Reported By**: [user/system]
**First Observed**: [timestamp]

### Services Involved

| Service | Role | Has Logs? | Has Tracing? |
|---------|------|-----------|--------------|
| API Gateway | Entry point | Yes | Yes |
| Auth Service | Authentication | Yes | Yes |
| Order Service | Business logic | Yes | Yes |
| Payment Service | External integration | Yes | Partial |
| Notification Worker | Async processing | Yes | No |

### Correlation Strategy

- **Trace ID Header**: X-Request-ID
- **Log Query Method**: Grafana Loki with label filter
- **APM Tool**: Jaeger at http://jaeger.internal:16686

### Service Topology

```
User → API Gateway → Auth Service → Order Service
                                      ↓
                              [RabbitMQ Queue]
                                      ↓
                              Notification Worker → Payment Service
```

### Blockers

- [ ] No access to Payment Service logs (need VPN)
- [ ] Notification Worker has no tracing (will use timestamps)
```

---

## Extended Step 2: Cross-Service Blast Radius

The standard Step 2 ("Research the Blast Radius") focuses on files and functions. For distributed systems, extend this to **services, queues, and state stores**.

### Cross-Service Investigation Process

#### 1. Trace the Request Path

Start with the correlation/trace ID and follow the request through each service:

```bash
# Example: Query Grafana Loki for all services with trace ID
{service=~"api-gateway|auth-service|order-service"} |= "trace-id-abc123"
```

For each service touched:
- Note the timestamp of entry and exit
- Record any errors or warnings
- Capture the request/response payloads if logged

#### 2. Build the Cross-Service Timeline

Create a unified timeline showing events across all services:

```
CROSS-SERVICE TIMELINE

Trace ID: abc123-def456-789
User: user@example.com
Request: POST /orders

Service A (API Gateway) Timeline:
├── T+0ms     : Request received from client
├── T+2ms     : Request validated, forwarding to Auth Service
├── T+15ms    : Auth response received (success)
├── T+18ms    : Forwarding to Order Service
├── T+5015ms  : TIMEOUT waiting for Order Service (5s limit)
└── T+5016ms  : Returned 504 Gateway Timeout to client

Service B (Auth Service) Timeline:
├── T+3ms     : Request received from API Gateway
├── T+8ms     : JWT validated
├── T+10ms    : User lookup complete
└── T+12ms    : Response sent (200 OK)

Service C (Order Service) Timeline:
├── T+20ms    : Request received from API Gateway
├── T+25ms    : Database transaction started
├── T+30ms    : Inventory check initiated
├── T+4500ms  : Inventory service timeout (external dependency)
├── T+4510ms  : Retry #1 to Inventory service
├── T+9000ms  : Retry #1 timeout
└── T+9005ms  : Error logged, but API Gateway already timed out

Queue (RabbitMQ) Timeline:
├── T+N/A     : No message published (Order Service never completed)
└── T+N/A     : Notification Worker never triggered

TIMELINE ANALYSIS:
- Root timeout: Inventory service (external) at T+4500ms
- Cascade: Order Service waited, triggering API Gateway timeout
- Result: Client saw 504, but Order Service kept retrying in background
```

#### 3. Identify Where the Request Fails

Common failure points in distributed systems:

| Failure Point | Symptoms | Evidence |
|---------------|----------|----------|
| **Service boundary** | Timeout or connection error | Error logs at caller, missing entry log at callee |
| **Queue publish** | Message never arrives | No message in queue, or publish error in sender |
| **Queue consume** | Message stuck | Message visible in queue, no consumer log |
| **Database** | Slow query or lock | Long gap in timeline, DB metrics spike |
| **External API** | Timeout or error response | Error log with external URL, no response |
| **Cache** | Stale data served | Cache hit logged, but data is wrong |

#### 4. Map Service Dependencies

Document which services depend on which, and whether dependencies are:
- **Synchronous**: Caller waits for response
- **Asynchronous**: Caller continues, processes response later
- **Fire-and-forget**: Caller does not expect response

```markdown
## Service Dependency Map

| Caller | Callee | Type | Timeout | Retry Policy |
|--------|--------|------|---------|--------------|
| API Gateway | Auth Service | Sync | 2s | None |
| API Gateway | Order Service | Sync | 5s | None |
| Order Service | Inventory API | Sync | 4s | 3 retries, exponential backoff |
| Order Service | RabbitMQ | Async | 1s | 5 retries |
| Notification Worker | Payment Service | Sync | 10s | 3 retries |
```

#### 5. Collect Evidence from Each Service

For each service in the failure path, collect:

```markdown
## Evidence: [Service Name]

**Logs** (filtered by trace ID):
```
2026-02-04T14:30:00.020Z INFO  [order-service] trace=abc123 Received order request
2026-02-04T14:30:00.025Z INFO  [order-service] trace=abc123 Starting inventory check
2026-02-04T14:30:04.500Z ERROR [order-service] trace=abc123 Inventory service timeout after 4500ms
```

**Metrics at time of failure**:
- CPU: 45% (normal)
- Memory: 2.1GB / 4GB (normal)
- Active connections to Inventory: 50 (at limit!)
- Request latency p99: 8500ms (elevated)

**State snapshot**:
- Order record: created_at=T+25ms, status="pending"
- Inventory reservation: not created (timeout before completion)
```

---

## Extended Step 3: Distributed Findings Presentation

The standard Step 3 presents findings before fixing. For distributed systems, include additional dimensions.

### Distributed Findings Template

```markdown
## DISTRIBUTED FINDINGS

**Bug**: [what's broken - observed vs expected behavior]
**Trace ID**: [correlation identifier]
**Time Window**: [start] to [end]
**Services Involved**: [list all]

---

### Timeline Anomalies

Document any events that occurred in unexpected order or with unexpected gaps:

| Anomaly | Description | Significance |
|---------|-------------|--------------|
| Out-of-order events | Event B logged at T+50ms depends on Event A at T+100ms | Suggests clock skew or async race condition |
| Large gap | 2000ms between Event X and Event Y | Possible network delay, GC pause, or blocking call |
| Missing event | Expected log entry not found | Service may have crashed, or log level too high |
| Duplicate events | Same event ID appears twice | Retry logic triggered, possible double-processing |

---

### Causality Chain

Show the actual path the request took, in order:

```
[1] User (browser)
    ↓ POST /api/orders
[2] API Gateway (14:30:00.000)
    ↓ GET /auth/validate (2ms)
[3] Auth Service (14:30:00.003)
    ↓ Response: 200 OK (9ms)
[2] API Gateway (14:30:00.012)
    ↓ POST /orders (sync, 5s timeout)
[4] Order Service (14:30:00.020)
    ↓ GET /inventory/reserve (sync, 4s timeout)
[5] Inventory Service (external)
    ✗ TIMEOUT after 4500ms
[4] Order Service (14:30:04.520)
    ↓ Retry #1...
[2] API Gateway (14:30:05.015)
    ✗ TIMEOUT (5s limit reached)
    ↓ 504 Gateway Timeout to client
```

---

### Clock Skew Assessment

Compare timestamps across services to detect clock drift:

| Service | Timestamp | Skew from Reference |
|---------|-----------|---------------------|
| API Gateway | 2026-02-04T14:30:00.000Z | Reference (0ms) |
| Auth Service | 2026-02-04T14:30:00.003Z | +3ms (acceptable) |
| Order Service | 2026-02-04T14:30:00.020Z | +20ms (acceptable) |
| Inventory Service | 2026-02-04T14:29:59.500Z | -500ms (SKEWED!) |

**Clock Skew Verdict**:
- [ ] All clocks synchronized (skew < 100ms)
- [x] Clock skew detected (Inventory Service 500ms behind)
- [ ] Unable to determine (no overlapping events)

**Impact**: Clock skew of 500ms may cause timestamp-based ordering to fail. Events may appear in wrong order when aggregating logs.

---

### State Snapshots

Capture the state in each service's data store at the moment of the bug:

| Data Store | Service | Key | Value | Expected |
|------------|---------|-----|-------|----------|
| PostgreSQL | Order Service | orders.id=12345 | status="pending" | status="confirmed" |
| PostgreSQL | Order Service | orders.id=12345 | inventory_reserved=false | inventory_reserved=true |
| Redis | API Gateway | session:user123 | {authenticated: true} | (correct) |
| Inventory DB | Inventory Service | item:SKU-001 | quantity=0 | quantity=5 |

**State Inconsistency Detected**:
- Order Service shows order pending, but inventory was never reserved
- Inventory DB shows 0 quantity, but Order Service expected 5 available
- These services have inconsistent views of the world

---

### Queue/Message State

If async processing is involved:

| Queue | Messages Pending | Oldest Message | Consumer Status |
|-------|-----------------|----------------|-----------------|
| order-notifications | 0 | N/A | Idle (no work) |
| payment-requests | 147 | 45 minutes ago | BACKLOGGED |
| email-queue | 3 | 2 minutes ago | Processing normally |

**Queue Analysis**:
- payment-requests queue is backlogged (147 messages, oldest 45 min)
- This suggests Payment Service consumers are slow or failing
- Orders may complete but payments are delayed

---

### Network Conditions

If network issues suspected:

| Route | Latency (p50) | Latency (p99) | Packet Loss |
|-------|---------------|---------------|-------------|
| API Gateway → Auth | 2ms | 8ms | 0% |
| API Gateway → Order | 3ms | 15ms | 0% |
| Order → Inventory (external) | 150ms | 4200ms | 2.3% |

**Network Analysis**:
- Route to Inventory Service shows high p99 latency (4200ms) and packet loss (2.3%)
- This external dependency is unreliable
- Suggests network path or external service degradation
```

---

## Extended Step 4: Root Cause Analysis for Distributed Bugs

The standard Step 4 asks "Root cause or symptom?" For distributed systems, we add a failure category classification.

### Distributed Failure Categories

| Category | Symptoms | Common Causes | Example |
|----------|----------|---------------|---------|
| **Race Condition** | Events arrive out of order; state is inconsistent; bug is intermittent | Missing locks, no idempotency, async timing | Two services update same record; last write wins randomly |
| **Partial Failure** | Some services succeeded, others failed; system in inconsistent state | No distributed transaction, missing compensation | Payment processed but order not confirmed |
| **Timeout Cascade** | One timeout triggers others; multiple services fail together | Insufficient timeout budgets, no circuit breakers | Service A waits 30s for B, B waits 30s for C, all timeout |
| **Stale Read** | Code reads old value; decision based on outdated data | Cache not invalidated, read replica lag | User sees "5 in stock" but checkout fails (actually 0) |
| **Network Partition** | Services cannot communicate; system makes conflicting decisions | Network failure, DNS issues, firewall rules | Service A thinks B is down, processes locally; B is actually up |
| **Clock Skew** | Timestamps out of order; time-based logic fails | NTP not configured, VM clock drift | "Created before modified" check fails due to clock difference |
| **Queue Backlog** | Messages pile up; processing falls behind; timeouts increase | Slow consumers, spike in traffic, consumer crash | 100k pending messages; new orders wait hours |
| **Resource Exhaustion** | Connections refused, OOM errors, CPU throttling | Connection pool full, memory leak, unbounded queues | Database rejects connections; all 100 pool slots in use |

### Distributed Root Cause Classification Template

```markdown
## ROOT CAUSE ANALYSIS (Distributed)

**Bug Type**: [Race Condition / Partial Failure / Timeout Cascade / Stale Read / Network Partition / Clock Skew / Queue Backlog / Resource Exhaustion]

**Failure Mechanism**:

1. **Trigger**: [What initiated the failure]
   - Service: [name]
   - Action: [what it tried to do]
   - Result: [what happened instead]

2. **Propagation**: [How the failure spread]
   - Service A: [received timeout from Service B]
   - Service B: [was waiting on Service C]
   - Service C: [connection pool exhausted]

3. **Impact**: [What the user experienced]
   - Visible error: [504 Gateway Timeout]
   - Data state: [Order created but not confirmed]
   - Recovery: [Manual intervention required / Auto-recovered / Data loss]

**Evidence Supporting Classification**:

| Evidence | What It Shows | Confidence |
|----------|---------------|------------|
| Timeline gap of 4500ms | Timeout waiting for Inventory | High |
| Connection pool at 50/50 | Resource exhaustion | High |
| Retry logs x3 | Timeout cascade in progress | Medium |
| Order status "pending" after user saw error | Partial failure | High |

**Confidence Level**: High / Medium / Low

**Reasoning**: [Why you believe this is the root cause, not a symptom]

**Alternative Hypotheses Considered**:

| Hypothesis | Why Rejected |
|------------|--------------|
| Database deadlock | No lock wait logs found |
| Code bug in Order Service | Same code worked 1000x before failure |
| DNS failure | DNS resolution logs show success |

**Likelihood of Recurrence**: Common / Occasional / Rare

**Reasoning**: [Why this is likely or unlikely to happen again]
```

### Root Cause vs Symptom in Distributed Systems

In distributed systems, distinguishing root cause from symptom is harder because failures cascade:

```
Root Cause:          Symptom 1:           Symptom 2:           Symptom 3:
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Inventory   │      │ Order       │      │ API Gateway │      │ User sees   │
│ Service     │ ───→ │ Service     │ ───→ │ times out   │ ───→ │ 504 error   │
│ times out   │      │ times out   │      │             │      │             │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
     ↑
 Fix HERE              Fixing here          Fixing here         Fixing here
 (root cause)          (incomplete)         (bandaid)           (user-facing only)
```

**Ask yourself**:
- If I fix this, will the upstream services stop failing?
- Is this service failing because of its own bug, or because a dependency failed?
- Would adding a retry here fix the problem, or just delay the same failure?

---

## Extended Steps 5-7: Implementing Fixes for Distributed Bugs

### Extended Step 5: Propose Fix for Distributed Bugs

When proposing fixes for distributed systems, consider these patterns:

#### Idempotency Patterns

Ensure operations can be safely retried:

```javascript
// BAD: Non-idempotent - creates duplicate orders on retry
async function createOrder(userId, items) {
  const order = await db.orders.create({ userId, items });
  return order;
}

// GOOD: Idempotent - uses client-provided idempotency key
async function createOrder(userId, items, idempotencyKey) {
  // Check if this request was already processed
  const existing = await db.orders.findByIdempotencyKey(idempotencyKey);
  if (existing) {
    return existing; // Return same result as before
  }

  const order = await db.orders.create({
    userId,
    items,
    idempotencyKey
  });
  return order;
}
```

#### Compensation Transactions (Saga Pattern)

Undo partial failures:

```javascript
// Saga: Order creation with compensation
async function createOrderSaga(orderData) {
  const saga = new Saga();

  try {
    // Step 1: Reserve inventory
    const reservation = await inventoryService.reserve(orderData.items);
    saga.addCompensation(() => inventoryService.release(reservation.id));

    // Step 2: Charge payment
    const payment = await paymentService.charge(orderData.payment);
    saga.addCompensation(() => paymentService.refund(payment.id));

    // Step 3: Create order record
    const order = await orderService.create(orderData);
    saga.addCompensation(() => orderService.cancel(order.id));

    // Step 4: Send confirmation
    await notificationService.sendConfirmation(order);
    // No compensation needed - notifications are fire-and-forget

    return order;

  } catch (error) {
    // Something failed - run all compensations in reverse order
    await saga.compensate();
    throw new OrderCreationFailed(error);
  }
}
```

#### Circuit Breaker Pattern

Prevent cascade failures:

```javascript
const circuitBreaker = new CircuitBreaker({
  failureThreshold: 5,    // Open after 5 failures
  resetTimeout: 30000,    // Try again after 30s
  timeout: 4000           // Individual call timeout
});

async function callInventoryService(items) {
  return circuitBreaker.execute(async () => {
    return await inventoryService.reserve(items);
  }).catch(error => {
    if (error instanceof CircuitOpenError) {
      // Circuit is open - fail fast with degraded response
      logger.warn('Inventory service circuit open, using fallback');
      return { status: 'pending_verification', items };
    }
    throw error;
  });
}
```

#### Eventual Consistency Patterns

Accept that data will be consistent "eventually":

```javascript
// Instead of synchronous consistency check:
// BAD: Fails if inventory service is slow
const available = await inventoryService.checkAvailable(items);
if (!available) throw new OutOfStockError();

// GOOD: Optimistic approach with async reconciliation
const order = await orderService.create({
  ...orderData,
  status: 'pending_inventory_check'
});

// Async worker will verify and update status
await queue.publish('inventory-check', { orderId: order.id, items });

// Return immediately - status will update when verified
return order;
```

### Extended Step 6: Test Distributed Fixes

Standard testing is insufficient for distributed systems. Add these validation techniques:

#### Chaos Engineering Validation

Intentionally inject failures to verify fix works:

```yaml
# Litmus chaos experiment: Kill Inventory Service pod
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: inventory-pod-kill
spec:
  appinfo:
    appns: production
    applabel: "app=inventory-service"
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-kill
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "60"  # Kill pod for 60 seconds
            - name: CHAOS_INTERVAL
              value: "10"  # Every 10 seconds
```

**Expected result**: Order Service should handle Inventory Service unavailability gracefully (circuit breaker opens, fallback used, no 500 errors to users).

#### Load Testing Under Failure

Verify fix works under concurrent load:

```javascript
// k6 load test with failure injection
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    normal_load: {
      executor: 'constant-vus',
      vus: 100,
      duration: '10m',
    },
    failure_injection: {
      executor: 'shared-iterations',
      vus: 1,
      iterations: 1,
      startTime: '2m',  // Start failure at 2 minutes
      exec: 'injectFailure',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],  // Less than 1% errors
    http_req_duration: ['p(95)<500'],
  },
};

export default function() {
  const res = http.post('https://api.example.com/orders', orderPayload);
  check(res, {
    'status is 200 or 202': (r) => r.status === 200 || r.status === 202,
  });
}

export function injectFailure() {
  // Call internal endpoint to trigger chaos
  http.post('https://chaos.internal/inject', {
    target: 'inventory-service',
    type: 'network-delay',
    duration: '5m',
    delay: '5000ms',
  });
}
```

#### Staged Rollout

Test in production gradually:

```yaml
# Kubernetes canary deployment
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: order-service
spec:
  strategy:
    canary:
      steps:
        # Deploy to 5% of traffic first
        - setWeight: 5
        - pause: { duration: 10m }
        # Check error rate
        - analysis:
            templates:
              - templateName: error-rate
            args:
              - name: service
                value: order-service
        # If healthy, proceed to 25%
        - setWeight: 25
        - pause: { duration: 30m }
        - analysis:
            templates:
              - templateName: error-rate
        # Full rollout
        - setWeight: 100
```

#### Multi-Service Integration Testing

Test the entire flow, not just individual services:

```javascript
// Integration test: Full order flow with all services
describe('Order Creation Flow', () => {
  beforeAll(async () => {
    // Start all services in test containers
    await testContainers.startAll([
      'api-gateway',
      'auth-service',
      'order-service',
      'inventory-service',
      'payment-service',
      'rabbitmq',
      'postgres'
    ]);
  });

  it('should handle inventory service timeout gracefully', async () => {
    // Inject 5s delay into inventory service
    await inventoryService.injectDelay(5000);

    const response = await apiGateway.post('/orders', orderPayload);

    // Should return 202 Accepted (async processing)
    expect(response.status).toBe(202);
    expect(response.body.status).toBe('pending_inventory_check');

    // Order should still be created
    const order = await orderService.getOrder(response.body.orderId);
    expect(order).toBeDefined();
    expect(order.status).toBe('pending_inventory_check');
  });

  it('should complete order when inventory service recovers', async () => {
    // Remove delay
    await inventoryService.removeDelay();

    // Wait for async processing
    await waitFor(async () => {
      const order = await orderService.getOrder(orderId);
      return order.status === 'confirmed';
    }, { timeout: 30000 });

    const order = await orderService.getOrder(orderId);
    expect(order.status).toBe('confirmed');
    expect(order.inventoryReserved).toBe(true);
  });
});
```

### Extended Step 7: Document Distributed Patterns

After fixing a distributed bug, document more than just the fix. Capture the pattern.

#### Update LESSONS.md with Distributed Pattern

```markdown
## Distributed System Lessons

### LESSON: Timeout Cascade from External Dependencies

**Pattern**: When an external service (Inventory) times out, the calling service (Order) waits, which causes its caller (API Gateway) to wait, creating a cascade of timeouts.

**Symptoms**:
- Multiple services timeout within seconds of each other
- Logs show "waiting for response" in multiple services
- Users see 504 Gateway Timeout

**Root Cause**: Missing circuit breaker + insufficient timeout budgets

**Prevention**:
1. Implement circuit breaker on all external calls
2. Set timeout budget: each hop gets fraction of total (e.g., 5s total = 2s per hop max)
3. Add fallback behavior when circuit opens
4. Monitor circuit state in dashboards

**Related Debug Session**: session-2026-02-04-143022
```

#### Add Runbook for Similar Bugs

```markdown
# Runbook: Timeout Cascade Investigation

## Trigger
- Multiple 504 errors across services
- Alerts for "elevated latency" from 2+ services simultaneously

## Quick Diagnosis

1. Check APM for slow traces:
   ```
   Query: service.name:* AND duration:>5000ms
   Group by: service.name
   ```

2. Identify the bottom of the cascade (slowest service):
   ```
   Sort traces by duration DESC
   Find the service with longest "waiting for child span"
   ```

3. Check circuit breaker states:
   ```bash
   curl http://order-service.internal/actuator/circuitbreakers
   ```

## Resolution Steps

1. If circuit is OPEN: Dependency is failing, circuit is protecting system
   - Check dependency health
   - Wait for circuit to half-open and test

2. If circuit is CLOSED but requests slow: Circuit threshold not reached yet
   - Consider lowering threshold
   - Check if dependency is degraded (slow but not failing)

3. If no circuit breaker: Immediate action needed
   - Enable maintenance mode on affected endpoint
   - Deploy circuit breaker configuration
   - Gradually restore traffic

## Escalation

- If cascade affects >50% of requests: Page on-call SRE
- If data inconsistency detected: Page database team
```

#### Update Architecture Diagrams

If the bug revealed a missing dependency or incorrect flow:

```markdown
## Architecture Update (Post-Incident)

**Before** (what we thought):
```
Order Service → Inventory Service (sync, 5s timeout)
```

**After** (what we learned):
```
Order Service → Inventory Service (sync, 5s timeout)
                    ↓
              [Circuit Breaker]
                    ↓
              Fallback: Queue for async verification
```

**Change**: Added circuit breaker with async fallback. Orders now created optimistically; inventory verified asynchronously.
```

---

## Quick Reference: Distributed Debugging Checklist

Use this checklist when debugging any distributed system bug:

### Phase 1: Prepare (Step 1.5)

- [ ] Identified all services in request path
- [ ] Have correlation/trace ID
- [ ] Can access logs from all services
- [ ] Know the service topology
- [ ] Understand sync vs async boundaries

### Phase 2: Investigate (Step 2 Extended)

- [ ] Built cross-service timeline
- [ ] Identified exact failure point
- [ ] Collected evidence from each service
- [ ] Checked queue states (if async)
- [ ] Assessed clock skew

### Phase 3: Analyze (Steps 3-4 Extended)

- [ ] Presented distributed findings
- [ ] Identified timeline anomalies
- [ ] Mapped causality chain
- [ ] Captured state snapshots
- [ ] Classified failure type (8 categories)
- [ ] Confirmed root cause vs symptom

### Phase 4: Fix (Steps 5-7 Extended)

- [ ] Proposed fix with appropriate pattern:
  - [ ] Idempotency (for retries)
  - [ ] Compensation/Saga (for partial failure)
  - [ ] Circuit breaker (for cascades)
  - [ ] Eventual consistency (for stale reads)
- [ ] Tested with chaos engineering
- [ ] Tested under load
- [ ] Used staged rollout
- [ ] Updated LESSONS.md with pattern
- [ ] Created/updated runbook
- [ ] Updated architecture diagram if needed

---

## References

- **Original Protocol**: [x_post_backend.txt](./x_post_backend.txt) - 7-step Debug Agent
- **Multi-Agent Coordination**: [DEBUG_REPORTS/README.md](./DEBUG_REPORTS/README.md) - Session management
- **Wave 3 Context**: [WAVE3_EXECUTIVE_BRIEF.md](./WAVE3_EXECUTIVE_BRIEF.md) - Strategic overview
- **Tier Architecture**: [WAVE3_PATHWAY_STRATEGY.md](./WAVE3_PATHWAY_STRATEGY.md) - Infrastructure tiers
- **Task Definition**: WAVE3-003 in [WAVE3_TASK_QUEUE.md](./WAVE3_TASK_QUEUE.md)

---

**Word Count**: ~3,800 words

*Created: 2026-02-04 | WAVE3-003 | Technical Architect*
