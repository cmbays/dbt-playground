---
audience: [architect, developer, debugger]
priority: high
size: medium
dependencies: [PROJECT_STRUCTURE, ARCHITECTURE]
last_updated: 2026-02-04
status: active
tags: [template, debug, blast-radius, backend]
wave3_task: WAVE3-010
---

# Backend Structure Template

> **Purpose**: Canonical template for documenting backend structure to accelerate blast radius analysis during debugging (Step 2 of the 7-Step Debug Protocol).

## How to Use This Template

1. Copy this template to your project's documentation folder
2. Fill in each section with your project's specifics
3. Update when services, APIs, or schemas change
4. Reference during Debug Step 2: Blast Radius Research

**Time Investment**: 2-4 hours initial setup, 15 min per significant change

---

## 1. Service Map

### Purpose

Document all services and their dependencies to quickly identify what is affected when a component fails or changes.

### Service Registry

| Service | Responsibility | Port | Health Check | Dependencies |
|---------|----------------|------|--------------|--------------|
| [name] | [what it does] | [port] | [endpoint] | [what it calls] |

### Blast Radius Quick Reference

| If This Fails... | These Are Affected |
|------------------|-------------------|
| [Service A] | [Services B, C, ...] |

---

## 2. Database Schema

### Schema Overview

Document tables, relationships, and ownership to identify data dependencies during debugging.

### Table Registry

| Table | Purpose | Primary Key | Owner Service | Row Estimate |
|-------|---------|-------------|---------------|--------------|
| [name] | [description] | [pk column] | [service] | [~count] |

### Schema Versioning

| Version | Date | Migration | Breaking? | Rollback Plan |
|---------|------|-----------|-----------|---------------|
| v1.0.0 | [date] | Initial schema | N/A | N/A |

---

## 3. API Contracts

### Purpose

Document public interfaces with versions to identify breaking changes and consumer impact during debugging.

### API Inventory

| API | Version | Status | Consumers | Deprecation |
|-----|---------|--------|-----------|-------------|
| [name] | v1 | Stable | [who calls it] | N/A |

### Breaking Changes Log

| Date | API | Change | Impact | Migration Guide |
|------|-----|--------|--------|-----------------|
| [date] | [api] | [what changed] | [affected consumers] | [link] |

---

## 4. Message Queues

### Purpose

Document async communication channels to trace event flows during debugging.

### Queue Registry

| Queue/Topic | Purpose | Publisher | Consumer(s) | Retention |
|-------------|---------|-----------|-------------|-----------|
| [name] | [what flows through] | [who writes] | [who reads] | [duration] |

### Message Schema (per queue)

```json
{
  "event_type": "string",
  "payload": { },
  "metadata": {
    "correlation_id": "uuid",
    "timestamp": "iso8601"
  }
}
```

---

## 5. File Organization

### Purpose

Map key files for blast radius analysis. When debugging, know where to look.

### Critical File Map

| Category | Path | Purpose | Change Frequency |
|----------|------|---------|------------------|
| Config | [path] | [what it configures] | Low |
| Entry Point | [path] | [application start] | Low |
| Core Logic | [path/pattern] | [business rules] | Medium |

### Blast Radius by File Category

| File Type | If Changed, Verify... |
|-----------|----------------------|
| Config | All services using that config |
| Schema | Migrations, all queries |
| API Route | All consumers |

---

## 6. Version Matrix

### Purpose

Track API versions, deprecation status, and migration paths for debugging version-related issues.

### Current Versions

| Component | Current | Minimum Supported | Deprecated | EOL Date |
|-----------|---------|-------------------|------------|----------|
| [name] | v1.0 | v1.0 | None | N/A |

### Version Compatibility Matrix

| Client Version | API v1 | Notes |
|----------------|--------|-------|
| SDK 3.x | Yes | Both supported |

---

## Related Documentation

- [DEBUG_PROTOCOL.md](./DEBUG_PROTOCOL.md) - 7-Step Debug Protocol
- [INCIDENT_TEMPLATE.md](./INCIDENT_TEMPLATE.md) - Production incident format

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-02-04 | Initial template (WAVE3-010) | Architect |

---

*Template Version: 1.0.0*
*Wave 3 Task: WAVE3-010*
