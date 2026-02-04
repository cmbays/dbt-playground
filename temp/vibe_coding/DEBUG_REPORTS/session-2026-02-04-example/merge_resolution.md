# Merge Resolution: Orders Page Null Crash

## Session Metadata

| Field | Value |
|-------|-------|
| **Session ID** | session-2026-02-04-example |
| **Merge Coordinator** | agent_backend |
| **Participating Agents** | agent_frontend, agent_backend |
| **Status** | RESOLVED |
| **Merged At** | 2026-02-04 15:30:00 UTC |

---

## Agent Findings Summary

### Agent Frontend

| Finding | Classification | Confidence |
|---------|---------------|------------|
| Crash at orders.js:142 on null.length | Symptom | High |
| Missing null check in displayOrder | Contributing factor | High |
| API returns null for canceled orders | Root cause indicator | High |

**Proposed Fix**: Add `items ?? []` defensive coding

### Agent Backend

| Finding | Classification | Confidence |
|---------|---------------|------------|
| cancelOrder sets items to null | Root cause origin | High |
| API returns raw DB value | Root cause mechanism | High |
| No type contract documented | Contributing factor | Medium |

**Proposed Fix**: Normalize API response + document contract

---

## Consolidated Root Cause

### Root Cause Chain

```
1. cancelOrder() sets items = null in database
         |
         v
2. getOrder() returns raw database value (items: null)
         |
         v
3. Frontend assumes items is always array
         |
         v
4. TypeError: Cannot read properties of null (reading 'length')
```

### Primary Root Cause

**API returns inconsistent type** for items field (array for active orders, null for canceled).

### Secondary Factor

**Frontend lacks defensive coding** for unexpected null values.

---

## Unified Fix Strategy

### Layer 1: API Normalization (Root Cause Fix)

**Owner**: Agent Backend
**Priority**: P0

```javascript
// api/orders.js
async function getOrder(id) {
  const order = await db.orders.findById(id);
  return {
    ...order,
    items: order.items ?? []
  };
}
```

### Layer 2: Frontend Defensive Coding (Defense in Depth)

**Owner**: Agent Frontend
**Priority**: P1

```javascript
// playgrounds/orders.js
const items = order.items ?? [];
renderOrderItems(items);
```

### Layer 3: API Contract Documentation

**Owner**: Agent Backend
**Priority**: P2

Document that `items` is always an array, never null.

---

## Implementation Order

| Step | Action | Owner | Dependency |
|------|--------|-------|------------|
| 1 | Apply API normalization | Agent Backend | None |
| 2 | Apply frontend defensive coding | Agent Frontend | None (can parallel) |
| 3 | Update API documentation | Agent Backend | After step 1 |
| 4 | Verify end-to-end | Both agents | After steps 1-2 |

Steps 1 and 2 can proceed in parallel.

---

## Verification Plan

### API Verification (Agent Backend)

```bash
# Test canceled order
curl http://localhost:3000/api/orders/123
# Expected: { "items": [], "status": "canceled", ... }

# Test active order
curl http://localhost:3000/api/orders/456
# Expected: { "items": [...], "status": "active", ... }
```

### Frontend Verification (Agent Frontend)

1. Open orders page
2. Click on canceled order - should show empty items, no crash
3. Click on active order - should show items normally
4. Check console - no errors

### Integration Verification

- [ ] Canceled order loads without crash
- [ ] Active order displays items correctly
- [ ] No console errors
- [ ] API tests pass
- [ ] Frontend tests pass

---

## LESSONS.md Entry

### Pattern to Document

**Category**: API Design

**Pattern Name**: Consistent Return Types

**Anti-Pattern**:
```javascript
// BAD: Return type varies based on state
return order.status === 'canceled' ? null : order.items;
```

**Correct Pattern**:
```javascript
// GOOD: Always return consistent type
return order.items ?? [];  // Always array
```

**Rule**: API responses should have consistent types regardless of resource state. Use empty collections, not null.

**Reference**: session-2026-02-04-example

---

## Post-Mortem Notes

### What Went Well

- Multi-agent coordination identified both symptom and root cause
- Parallel investigation saved time
- Cross-scope observations caught the full picture

### What Could Improve

- Earlier API contract documentation would have prevented this
- Frontend should have had defensive coding from the start

### Prevention Measures

1. Add API contract validation to CI
2. Add null safety linting rule for frontend
3. Review existing endpoints for similar issues

---

## Sign-Off

| Agent | Approved | Notes |
|-------|----------|-------|
| agent_frontend | Yes | Defensive coding ready |
| agent_backend | Yes | API fix ready |

**Final Status**: Approved for implementation

---

*This is an example merge resolution for documentation purposes*
