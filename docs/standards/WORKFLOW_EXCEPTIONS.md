---
audience: [multi-agent]
priority: low
size: small
dependencies: [PROJECT_WORKFLOW]
last_updated: 2026-01-25
status: active
tags: [workflow, exceptions, reference]
---

# Workflow Exceptions - Approved Deviations

This document tracks approved exceptions to the standard 6-phase workflow (UNDERSTAND → PLAN → PROTOTYPE → BUILD → VERIFY → DEPLOY).

## Purpose

Some tasks are simple enough that following the full workflow creates unnecessary overhead. This document tracks which task types have been granted exceptions and which workflow phases can be skipped.

## Approval Types

- **ONE-TIME**: Approved for a specific instance only
- **ALWAYS**: Approved for all instances of this task type going forward

## Current Approved Exceptions

### ALWAYS Approved

*None yet - will be populated as patterns emerge*

### ONE-TIME Approved

*None yet - will be logged as they occur*

## How to Request Exception

Claude should request exception with this format:

```
This appears to be a [task type: e.g., "typo fix", "documentation update"].
May I skip the [PLAN/PROTOTYPE/etc.] phase(s) for this task?

Reasoning: [brief explanation of why exception makes sense]
```

## Example Exception Criteria

Tasks that might warrant exceptions:

| Task Type | Skip Phases | Reasoning |
|-----------|-------------|-----------|
| Typo/spelling fix | PLAN, PROTOTYPE | Change is obvious, low risk |
| Documentation update | PROTOTYPE | No user-facing functionality |
| Adding code comments | PLAN, PROTOTYPE | No functionality change |
| Minor CSS tweaks | PLAN (sometimes) | If change is isolated and obvious |
| Archiving old files | PLAN, PROTOTYPE | File organization task |

**Important**: When in doubt, Claude should follow the full workflow.

## Log Format

When an exception is granted, log it here:

```markdown
### [Date] - [Task Type] - [Approval Type]
**Task**: [Brief description]
**Phases Skipped**: [List phases]
**Granted By**: Christopher
**Reasoning**: [Why exception was appropriate]
```

---

*Last Updated: 2026-01-19*
