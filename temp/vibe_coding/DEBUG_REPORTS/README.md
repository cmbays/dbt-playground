---
audience: [architect, developer, debugger, on-call]
priority: high
size: small
status: active
tags: [debug, incident, deployment, validation]
---

# DEBUG_REPORTS Directory

**Created**: 2026-02-04
**Purpose**: Centralized location for debug protocols, incident reports, and deployment validation artifacts.

---

## Contents

| File | Purpose | Task | Status |
|------|---------|------|--------|
| [BACKEND_STRUCTURE_TEMPLATE.md](./BACKEND_STRUCTURE_TEMPLATE.md) | Template for documenting backend architecture | WAVE3-010 | ✅ Complete |
| [DEPLOYMENT_VALIDATION_CHECKLIST.md](./DEPLOYMENT_VALIDATION_CHECKLIST.md) | Pre-deployment quality gates for tier promotions | WAVE3-015 | ✅ Complete |
| [INCIDENT_TEMPLATE.md](./INCIDENT_TEMPLATE.md) | Structured template for production incident response | WAVE3-017 | ✅ Complete |

---

## Usage

### Deployment Validation
Before promoting a project to a higher tier (Local → Staging → Production):

1. Open `DEPLOYMENT_VALIDATION_CHECKLIST.md`
2. Complete all gates for your target tier
3. Document any accepted risks
4. Attach checklist to deployment ticket/PR

### Incident Response
When a production incident occurs:

1. Copy `INCIDENT_TEMPLATE.md` to a new file: `INCIDENT-YYYY-MM-DD-NNN.md`
2. Fill in Header section immediately
3. Document timeline as events occur
4. Complete full RCA after resolution
5. Ensure all postmortem checklist items complete

### Backend Structure Documentation
To understand system dependencies during debugging:

1. Review `BACKEND_STRUCTURE_TEMPLATE.md` sections
2. Reference filled example: `BACKEND_STRUCTURE_DBT_PLAYGROUND.md`
3. Use during Debug Step 2: Blast Radius Research

---

## Wave 3 Tasks

| Task | Deliverable | Status |
|------|-------------|--------|
| WAVE3-001 | DEBUG_REPORTS folder structure | ✅ Complete (P0) |
| WAVE3-010 | BACKEND_STRUCTURE_TEMPLATE.md | ✅ Complete (P1) |
| WAVE3-015 | DEPLOYMENT_VALIDATION_CHECKLIST.md | ✅ Complete (P1) |
| WAVE3-017 | INCIDENT_TEMPLATE.md | ✅ Complete (P1) |

---

## Related Documentation

- [WAVE3_EXECUTIVE_BRIEF.md](../WAVE3_EXECUTIVE_BRIEF.md) - Wave 3 overview
- [WAVE3_PATHWAY_STRATEGY.md](../WAVE3_PATHWAY_STRATEGY.md) - Tier definitions
- [LEARNINGS.md](../../../docs/reference/LEARNINGS.md) - Pattern library
- [CLAUDE.md](../../../CLAUDE.md) - Project context

---

## Future Additions (Planned)

| File | Purpose | Task |
|------|---------|------|
| OBSERVABILITY.md | Observability integration guide | WAVE3-016 |
| BACKEND_STRUCTURE_DBT_PLAYGROUND.md | Filled example for dbt-playground | WAVE3-010 |

---

## Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-02-04 | 1.0.0 | Initial creation with WAVE3-010, 015, 017 deliverables |

---

*Last Updated: 2026-02-04*
