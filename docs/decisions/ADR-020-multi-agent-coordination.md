---
audience: [architect, developer, multi-agent]
priority: high
size: small
dependencies: [ADR-019]
last_updated: 2026-02-04
status: approved
tags: [architecture, debugging, wave3, multi-agent, coordination]
---

# ADR-020: Multi-Agent Coordination Protocol

**Status**: Approved
**Date**: 2026-02-04
**Deciders**: Architect, Planner
**Related Issue**: #226
**Wave 3 Task**: WAVE3-004
**Depends On**: ADR-019 (Debug Session Persistence)

---

## Context

Wave 3 requires support for multiple agents debugging the same system simultaneously. Scenarios include:

1. **Parallel Investigation**: Two agents research different hypotheses concurrently
2. **Specialist Handoff**: Frontend agent hands off to backend agent mid-session
3. **Competitive Debugging**: Alpha/Beta teams debug independently, compare solutions
4. **Escalation**: Junior agent escalates to senior agent without losing context

The Phase 1 Debug protocol assumed single-agent operation:
- No coordination between agents
- No conflict resolution for simultaneous findings
- No audit trail of which agent contributed what

Multi-agent coordination requires solving:
- **Write conflicts**: Two agents writing findings simultaneously
- **Finding attribution**: Which agent discovered what
- **Merge resolution**: Combining multiple agent findings into unified fix
- **Handoff protocol**: Clean context transfer between agents

## Decision

**Separate agent findings into distinct files; merge resolution documented in merge_resolution.md.**

### File Structure (Per Session)

```text
temp/vibe_coding/DEBUG_REPORTS/{session}/
├── session_manifest.md             # Tracks all participating agents
├── agent_primary_findings.md       # Primary agent's findings (Step 1-4)
├── agent_secondary_findings.md     # Secondary agent's findings
├── agent_specialist_findings.md    # Specialist (e.g., security) findings
├── merge_resolution.md             # Unified resolution (created by lead)
└── outcome.md                      # Final fix + LESSONS entry
```

### Agent Findings Template

Each `agent_{role}_findings.md` follows this structure:

```markdown
# Debug Findings: {Agent Role}

**Agent ID**: {unique identifier}
**Joined Session**: {timestamp}
**Focus Area**: {what this agent investigated}

## Reproduction (Step 1)
- Reproduced: Yes/No
- Environment: {details}
- Observation: {what was observed}

## Blast Radius (Step 2)
- Files involved: {list}
- Connected systems: {list}
- Evidence: {logs, traces}

## Findings (Step 3)
{Structured findings per protocol}

## Root Cause Analysis (Step 4)
- Classification: ROOT CAUSE / SYMPTOM
- Reasoning: {explanation}
- Confidence: High/Medium/Low

## Proposed Fix (Step 5)
{If agent proposes a fix}

## Notes for Other Agents
{Context handoff notes}
```

### Merge Resolution Template

```markdown
# Merge Resolution

**Session**: {session_id}
**Lead Agent**: {agent_id}
**Contributing Agents**: {list}
**Resolution Date**: {timestamp}

## Summary of Agent Findings

### Agent 1 ({role})
- Key finding: {summary}
- Classification: {root cause/symptom}
- Proposed fix: {summary}

### Agent 2 ({role})
- Key finding: {summary}
- ...

## Conflicts Identified
{Where agents disagreed and how resolved}

## Unified Resolution
- **Root Cause**: {merged understanding}
- **Fix Strategy**: {combined approach}
- **Files to Modify**: {unified list}

## Implementation Plan
{Ordered steps from merged findings}

## Attribution
| Step | Contributed By |
|------|---------------|
| Reproduction | Agent 1 |
| Root cause identification | Agent 2 |
| Fix proposal | Agent 1 + Agent 2 |
```

### Coordination Protocol

1. **Session Join**: Agent writes entry to `session_manifest.md` agents section
2. **Isolation**: Each agent writes ONLY to their own findings file
3. **No Cross-Write**: Agents do not modify each other's findings files
4. **Merge Trigger**: When all agents complete Step 5 OR lead agent initiates
5. **Lead Selection**: First agent to join is default lead; can be reassigned
6. **Merge Authority**: Only lead agent creates `merge_resolution.md`
7. **Outcome Write**: Lead agent writes `outcome.md` after merge

## Rationale

### Why Separate Files Per Agent

| Approach | Pros | Cons |
|----------|------|------|
| Single shared file | Simple | Merge conflicts, lost attribution |
| Separate files | No conflicts, clear attribution | More files, requires merge step |
| Database with locks | Concurrent writes | Complexity, not Git-native |

**Decision**: Separate files eliminate merge conflicts and preserve attribution, which outweighs the additional merge step.

### Why Explicit Merge Step

1. **Quality gate**: Merge forces review of all findings before fix
2. **Conflict resolution**: Disagreements must be explicitly resolved
3. **Audit trail**: Clear record of how unified fix was derived
4. **Attribution preservation**: Each agent's contribution is traceable

### Why Lead Agent Authority

1. **Single point of decision**: Avoids deadlock on conflicts
2. **Accountability**: One agent responsible for final resolution
3. **Simplicity**: No voting or consensus protocol needed
4. **Flexibility**: Lead can delegate merge to specialist if appropriate

## Consequences

### Positive

- **No write conflicts**: Each agent has exclusive write space
- **Clear audit trail**: Every finding attributed to specific agent
- **Parallel work**: Agents can investigate simultaneously
- **Forensic value**: Post-incident review shows full investigation path
- **Flexible handoff**: Any agent can join/leave session cleanly

### Negative

- **Manual merge required**: Lead agent must synthesize findings
- **Post-session cleanup needed**: Multiple files per session
- **Coordination overhead**: Agents must check session_manifest for others
- **Lead bottleneck**: Merge waits for lead agent availability

### Mitigation

| Negative | Mitigation |
|----------|------------|
| Manual merge | Merge template reduces cognitive load; future: auto-merge tool |
| Cleanup | Session archival script bundles all files |
| Coordination overhead | Session status visible in `.active_sessions/` symlinks |
| Lead bottleneck | Lead can delegate merge; escalation path in metadata |

## Alternatives Considered

### Alternative 1: Single Shared Document with Sections

**Pros**: Simpler structure, fewer files
**Cons**: Merge conflicts, attribution unclear, concurrent edit issues
**Rejected**: Does not solve core multi-agent write conflict problem

### Alternative 2: Real-Time Collaboration (Google Docs Style)

**Pros**: No merge step, live collaboration
**Cons**: Requires external service, not filesystem-based, complex
**Rejected**: Over-engineering for Tier 1; violates local-first principle

### Alternative 3: Message Queue Between Agents

**Pros**: Async communication, event-driven
**Cons**: Infrastructure overhead, complex state management
**Rejected**: Overkill for debugging coordination; better suited for production systems

## Implementation Notes

1. **Join protocol**: Agent checks `session_manifest.md`, adds self to agents section
2. **Naming convention**: `agent_{role}_findings.md` where role is human-readable
3. **Completion signal**: Agent sets `status: complete` in their metadata entry
4. **Merge trigger**: Lead polls for all agents complete OR manual trigger
5. **Conflict format**: Use diff-style blocks in `merge_resolution.md` for disagreements
6. **Archive**: After outcome, session folder moved to `DEBUG_REPORTS/archive/`

## Related

- [ADR-019: Debug Session Persistence](ADR-019-debug-session-persistence.md) - Session folder structure
- [ADR-008: Inter-Agent Report Pattern](../specs/TDD-HISTORICAL.md#adr-8-inter-agent-report-pattern) - Report conventions
- [WAVE3_EXECUTIVE_BRIEF.md](../../temp/vibe_coding/WAVE3_EXECUTIVE_BRIEF.md) - Multi-agent gap analysis
- [x_post_backend.txt](../../temp/vibe_coding/x_post_backend.txt) - Original single-agent protocol

---

*Approved as part of Wave 3 Backend Leveling (WAVE3-004)*
