# Product Requirements Document: Multi-Agent Coordination System

**PRD ID**: PRD-019
**Feature Set**: 6 - Advanced Multi-Agent Coordination
**Version**: 1.0
**Date**: 2026-02-01
**Status**: Draft
**Author**: Product Manager Persona
**Target Milestone**: v0.9 (Mar 31, 2026)

---

## 1. Problem Statement

### 1.1 Current State

The dbt-playground project has developed a sophisticated multi-agent system with 21 personas, a Supervisor meta-orchestrator, PM session management with heartbeats, and git worktree orchestration. However, several coordination gaps limit the system's ability to enable true parallel autonomous work:

1. **No unified agent identity**: 21 separate persona files lack a consolidated "soul" document defining universal constraints and identity
2. **No formal permission routing**: High-risk operations (releases, CI triggers) execute without Opus 4.5 oversight
3. **Manual coordination overhead**: Task decomposition is conversational, not algorithmic
4. **Resource contention risk**: Multiple worktrees may wake simultaneously, causing resource spikes
5. **Limited worktree tracking**: No structured registry correlating worktrees to sessions and PRs

### 1.2 Impact

| Pain Point | Impact | Affected Users |
|------------|--------|----------------|
| No permission routing | High-risk ops may execute unsafely | All agents, Christopher |
| Manual task decomposition | Complex features take longer | Supervisor, PM |
| Resource contention | System slowdowns during parallel work | All parallel sessions |
| No worktree registry | Orphan worktrees, lost context | git-master, Supervisor |
| No unified identity | Inconsistent agent behavior | All personas |

### 1.3 Success Vision

After implementation, the dbt-playground agent system will:

- Have a single source of truth for agent identity and constraints (SOUL.md)
- Route high-risk operations through formal approval before execution
- Decompose complex features into parallelizable subtasks algorithmically
- Distribute heartbeat wakeups to prevent resource spikes
- Track all worktrees in a structured registry with session correlation
- Enable 2-3x throughput improvement for complex features

---

## 2. User Stories and Use Cases

### 2.1 Primary User Stories

#### US-1: As Christopher, I want high-risk operations to require approval so that costly mistakes are prevented

**Acceptance Criteria**:

- AC-1.1: Operations matching OPUS_APPROVAL patterns are blocked until approved
- AC-1.2: Blocked operations display clear reason and escalation path
- AC-1.3: Approval decisions are logged with timestamp and rationale
- AC-1.4: Approved operations execute normally after approval
- AC-1.5: Timeout after 10 minutes escalates to user notification

#### US-2: As the Supervisor, I want formal task decomposition so that complex features can be parallelized

**Acceptance Criteria**:

- AC-2.1: Requests >10 files trigger formal decomposition
- AC-2.2: Decomposition produces subtasks with owners, inputs, outputs
- AC-2.3: Subtasks form a DAG (no cycles)
- AC-2.4: Dependencies between subtasks are explicit
- AC-2.5: Subtasks can be assigned to available worktrees

#### US-3: As git-master, I want a worktree registry so that I can track parallel work and prevent conflicts

**Acceptance Criteria**:

- AC-3.1: WORKTREE_REGISTRY.json tracks all active worktrees
- AC-3.2: Registry includes PR number, session ID, status, files affected
- AC-3.3: Registry validates against schema on write
- AC-3.4: Conflict detection warns before overlapping file modifications
- AC-3.5: Registry updates on worktree create/remove/merge

#### US-4: As a parallel session, I want staggered heartbeats so that resource contention is minimized

**Acceptance Criteria**:

- AC-4.1: Heartbeat timing includes session-based offset
- AC-4.2: Offset distributes heartbeats evenly across interval
- AC-4.3: Stagger is deterministic (same session = same offset)
- AC-4.4: Existing heartbeat functionality unchanged
- AC-4.5: Configuration flag to enable/disable staggering

#### US-5: As an agent, I want SOUL.md so that universal constraints are consistent across sessions

**Acceptance Criteria**:

- AC-5.1: SOUL.md synthesizes all 21 persona identities
- AC-5.2: Universal constraints listed (never push to main, etc.)
- AC-5.3: Persona activation triggers documented
- AC-5.4: Context switching rules explicit
- AC-5.5: SOUL.md referenced from CLAUDE.md

### 2.2 Secondary User Stories

#### US-6: As Christopher, I want orphan cleanup so that stale worktrees don't accumulate

**Acceptance Criteria**:

- AC-6.1: Cron job detects worktrees without active sessions
- AC-6.2: Orphans logged but not auto-deleted (safety)
- AC-6.3: Cleanup command available for manual removal
- AC-6.4: Workflow Hub displays orphan status

#### US-7: As a user, I want Workflow Hub widgets so that coordination state is visible

**Acceptance Criteria**:

- AC-7.1: Session Grid widget shows all active sessions
- AC-7.2: Worktree Map widget visualizes assignments
- AC-7.3: Permission Queue widget displays pending approvals
- AC-7.4: Widgets update automatically (polling)

---

## 3. Functional Requirements

### 3.1 SOUL.md - Unified Agent Identity

#### FR-1.1: Structure

SOUL.md shall include:

```markdown
# SOUL.md - dbt-playground Agent System

## Core Identity
I am a multi-persona agent system for dbt development...

## Universal Constraints
- Never push directly to main
- All git operations via git-master
- Quality gates are non-negotiable
- Ask rather than assume
- Default to simpler solutions

## Persona Registry
| Prefix | Persona | Activates When |
|--------|---------|----------------|
| super: | Supervisor | Session orchestration |
| pm: | Product Manager | Requirements work |
| arch: | Architect | Design decisions |
...

## Context Switching Rules
- Only one persona active at a time
- Supervisor is default entry point
- Explicit handoff required between personas
```

#### FR-1.2: Validation

- SOUL.md shall pass YAML frontmatter validation if frontmatter is included
- Persona registry shall match .claude/agents/*.md files
- Constraint list shall be consistent with .claude/rules/*.md

### 3.2 Permission Classification and Routing

#### FR-2.1: Classification Tiers

| Tier | Description | Action |
|------|-------------|--------|
| ALLOW | Safe operations (read, grep, status) | Execute immediately |
| VALIDATE | Format-sensitive (commits, PRs) | git-master validates |
| USER_APPROVAL | Sensitive (package installs, force) | Prompt user |
| OPUS_APPROVAL | High-risk (releases, CI, production) | Queue for review |

#### FR-2.2: Pattern Matching

```javascript
const OPUS_REQUIRED = [
  /gh workflow run/,           // CI trigger
  /gh release create/,         // Release creation
  /production|prod/i,          // Production references
];

const USER_APPROVAL = [
  /^curl.*-X\s*(POST|PUT|DELETE)/,  // External API mutations
  /^\$\{.*API_KEY/,                  // API key usage
  /^pip install/,                    // Package installation
  /^npm install/,                    // Package installation
  /--force|--hard|-f\s/,             // Force flags
];
```

#### FR-2.3: Approval Queue

Pending approvals stored in WORKFLOW_STATE.md:

```yaml
## Pending Approvals

### Approval: op-2026-02-01-001 (PENDING)
- Operation: `gh release create v0.8.0`
- Requested by: Documenter
- Risk level: HIGH
- Reason: Production release
- Requested at: 2026-02-01T14:30:00Z
- Timeout: 2026-02-01T14:40:00Z

Decision: [APPROVE | DENY | MODIFY]
Decided by: ___
Notes: ___
```

#### FR-2.4: Escalation Flow

```
[Command Received]
    |
    +-- permission-router.js classifies
    |
    +-- ALLOW → Execute immediately
    |
    +-- VALIDATE → Delegate to git-master
    |
    +-- USER_APPROVAL → Prompt: "Approve [command]? [y/N]"
    |     |
    |     +-- User approves → Execute with log
    |     +-- User denies → Abort with message
    |
    +-- OPUS_APPROVAL → Add to approval queue
          |
          +-- Log pending approval
          +-- Notify user of pending queue
          +-- Wait for explicit approval
          +-- Timeout after 10 minutes → Escalate
```

### 3.3 Task Decomposition Algorithm

#### FR-3.1: Workflow J - Formal Task Decomposition

```
Input: User Request
Output: Task Tree (DAG)

Algorithm:
1. CLASSIFY request type
   - On roadmap? Check docs/specs/PRD-*.md
   - Ad-hoc? Clarify scope

2. ESTIMATE complexity
   - < 3 files: Simple (--dev-only)
   - 3-10 files: Medium (--skip-prd or --skip-tdd)
   - > 10 files: Complex (full workflow, decomposition)

3. DECOMPOSE to subtasks
   - Each subtask has: owner, inputs, outputs, dependencies
   - DAG structure (no cycles)
   - Independent subtasks can parallelize

4. ALLOCATE to workers
   - Check worktree availability in WORKTREE_REGISTRY
   - Check task conflicts in PM_SESSIONS
   - Assign session to subtask

5. MONITOR execution
   - Heartbeat tracking
   - Progress via AGENT_REPORTS
   - Stale detection and recovery
```

#### FR-3.2: Subtask Schema

```json
{
  "subtask_id": "st-001",
  "title": "Implement dim_customers",
  "owner": "dbt-developer",
  "inputs": ["PRD-019.md", "stg_customers design"],
  "outputs": ["models/marts/dim_customers.sql", "schema.yml"],
  "dependencies": ["st-000"],
  "estimated_files": 2,
  "worktree": null,
  "session_id": null,
  "status": "pending"
}
```

### 3.4 Staggered Wakeup System

#### FR-4.1: Offset Calculation

```javascript
function calculateStaggerOffset(session_id, interval_ms) {
  // Deterministic hash-based offset
  const hash = crypto.createHash('md5').update(session_id).digest('hex');
  const hashInt = parseInt(hash.substring(0, 8), 16);
  return hashInt % interval_ms;
}
```

#### FR-4.2: Heartbeat Timing

```javascript
function getNextHeartbeatTime(session, config) {
  const stagger = config.STAGGER_ENABLED
    ? calculateStaggerOffset(session.session_id, config.HEARTBEAT_INTERVAL_MS)
    : 0;

  return new Date(session.last_heartbeat).getTime()
    + config.HEARTBEAT_INTERVAL_MS
    + stagger;
}
```

#### FR-4.3: Configuration

```javascript
// pm_config.js additions
STAGGER_ENABLED: true,
STAGGER_MAX_OFFSET_MS: 30 * 1000,  // Max 30s offset
```

### 3.5 WORKTREE_REGISTRY.json

#### FR-5.1: Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "version": { "type": "string" },
    "last_updated": { "type": "string", "format": "date-time" },
    "worktrees": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["path", "status", "created_at"],
        "properties": {
          "path": { "type": "string" },
          "pr_number": { "type": ["integer", "null"] },
          "session_id": { "type": ["string", "null"] },
          "status": { "enum": ["active", "stale", "merged", "orphan"] },
          "base_branch": { "type": "string" },
          "created_at": { "type": "string", "format": "date-time" },
          "last_sync": { "type": ["string", "null"], "format": "date-time" },
          "estimated_duration": { "type": ["string", "null"] },
          "files_affected": { "type": "array", "items": { "type": "string" } },
          "dependencies": { "type": "array", "items": { "type": "string" } }
        }
      }
    }
  }
}
```

#### FR-5.2: Registry Operations

| Operation | Trigger | Action |
|-----------|---------|--------|
| Create | Worktree created | Add entry with status=active |
| Update | Session heartbeat | Update last_sync |
| Merge | PR merged | Set status=merged, trigger cleanup |
| Orphan | No session for 5min | Set status=orphan |
| Remove | Cleanup executed | Delete entry |

### 3.6 Orphan Detection and Cleanup

#### FR-6.1: Detection Logic

```javascript
async function detectOrphans(registry, sessions) {
  const orphans = [];

  for (const [branch, worktree] of Object.entries(registry.worktrees)) {
    if (worktree.status !== 'active') continue;

    // Check if session exists and is active
    const session = sessions.find(s =>
      s.session_id === worktree.session_id &&
      s.status === 'active'
    );

    if (!session) {
      orphans.push({ branch, worktree, reason: 'no_active_session' });
    }
  }

  return orphans;
}
```

#### FR-6.2: Cleanup Protocol

- Orphans are **logged but not auto-deleted** (safety)
- Manual cleanup: `node scripts/worktree-registry.js cleanup <branch>`
- Cleanup removes worktree directory and registry entry
- Cleanup requires user confirmation for branches with uncommitted changes

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| Permission classification | <10ms | Time to classify command |
| Heartbeat update | <100ms | Time to update PM_SESSIONS.json |
| Registry validation | <50ms | Time to validate against schema |
| Orphan detection | <500ms | Time to scan all worktrees |
| Workflow Hub refresh | <2s | Time to load coordination widgets |

### 4.2 Reliability

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| Heartbeat delivery | 99.9% | Heartbeats not dropped |
| Registry consistency | 100% | No orphan entries without worktrees |
| Approval queue durability | 100% | No approvals lost on crash |
| Session recovery | <30s | Time to recover stale session |

### 4.3 Security

| Requirement | Implementation |
|-------------|----------------|
| Permission escalation | OPUS_APPROVAL for high-risk ops |
| Audit trail | All operations logged with timestamp |
| No secrets in logs | Sanitize API keys, tokens from logs |
| Approval authentication | User must explicitly approve |

### 4.4 Resource Limits

| Resource | Limit | Enforcement |
|----------|-------|-------------|
| Concurrent worktrees | 5 | Warn at 4, block at 5 |
| Session heartbeat interval | 60s | Minimum enforced |
| Approval timeout | 10 minutes | Auto-escalate after timeout |
| Registry file size | 1MB | Warn if exceeded |

### 4.5 Compatibility

| Requirement | Implementation |
|-------------|----------------|
| Backward compatible | Existing pm_sessions.js continues to work |
| Node.js version | 18+ (already required) |
| Platform | macOS, Linux (per project) |
| Git version | 2.20+ (worktree features) |

---

## 5. Acceptance Criteria Summary

### 5.1 Phase A: Foundation

- [ ] SOUL.md exists at `.claude/SOUL.md`
- [ ] SOUL.md includes all 21 personas
- [ ] SOUL.md referenced from CLAUDE.md
- [ ] permission-router.js classifies commands correctly
- [ ] OPUS_APPROVAL operations are blocked
- [ ] Staggered wakeups distribute heartbeats evenly
- [ ] Configuration flag controls stagger behavior

### 5.2 Phase B: Coordination

- [ ] Workflow J documented in supervisor.md
- [ ] Decomposition produces valid DAG
- [ ] WORKTREE_REGISTRY.json validates against schema
- [ ] Registry CLI provides create/update/remove/list
- [ ] Orphan detection works correctly
- [ ] Cron setup documented

### 5.3 Phase C: Integration

- [ ] Approval queue persists in WORKFLOW_STATE.md
- [ ] Approvals logged with decision and rationale
- [ ] Workflow Hub Session Grid widget works
- [ ] Workflow Hub Worktree Map widget works
- [ ] Workflow Hub Permission Queue widget works
- [ ] Parallel development documented
- [ ] End-to-end workflow tested

---

## 6. Out of Scope

### 6.1 Deferred to v1.0

| Feature | Reason |
|---------|--------|
| AGENT_CARD.json generation | External integration not needed yet |
| Automated worktree spawning via API | Requires process management complexity |
| MCP approval gateway server | Hook-based approach sufficient |
| Cross-repository coordination | Single repo focus for now |
| Vector store for context memory | File-based AGENT_REPORTS sufficient |

### 6.2 Explicitly Excluded

| Feature | Reason |
|---------|--------|
| Real-time WebSocket updates | Polling sufficient for current scale |
| Distributed session management | Single machine operation |
| Automated conflict resolution | Requires human judgment |
| AI-based task decomposition | Algorithm-based decomposition first |

---

## 7. Dependencies

### 7.1 Internal Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| pre-bash-check.js | Active | Low - extend existing |
| pm_sessions.js | Active | Low - minor additions |
| pm_config.js | Active | Low - configuration only |
| supervisor.md | Active | Low - documentation update |
| git-master.md | Active | Low - integrate registry |
| WORKFLOW_STATE.md | Active | Low - add section |

### 7.2 External Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| Node.js 18+ | Available | None |
| gh CLI | Available | None |
| System crontab | Available | None |
| Ajv (JSON schema) | Installed | None |

---

## 8. Risks and Mitigations

### 8.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Permission false positives | Medium | High | Comprehensive test suite, allowlist |
| Registry corruption | Low | Medium | Atomic writes, schema validation |
| Stagger clock skew | Low | Low | Server timestamps, tolerance |

### 8.2 Process Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SOUL.md maintenance drift | Medium | Medium | Validation script, pre-commit |
| Approval queue delays | Low | Medium | Timeout escalation |
| Orphan accumulation | Medium | Low | Cron cleanup, Hub visibility |

---

## 9. Success Metrics

### 9.1 Quantitative

| Metric | Baseline | Target |
|--------|----------|--------|
| Parallel throughput | 1x | 2-3x |
| Session recovery time | Minutes | <30s |
| Permission incidents | Unknown | 0 critical |
| Context loss on resume | Frequent | Rare |
| Orphan worktrees | Unknown | 0 persistent |

### 9.2 Qualitative

- Developer Experience: Complex features feel parallelizable
- Safety: High-risk operations require explicit approval
- Visibility: Coordination state visible in Workflow Hub
- Reliability: Sessions recover automatically
- Documentation: Clear guide for parallel development

---

## 10. Appendices

### A. Related Documents

| Document | Purpose |
|----------|---------|
| [Research Report](./multi_agent_coordination_report.md) | Technical analysis |
| [Implementation Plan](./multi_agent_coordination_plan.md) | Phased rollout |
| [TDD](./multi_agent_coordination_TDD.md) | Technical design |
| [CLAUDE.md](/CLAUDE.md) | Project context |
| [supervisor.md](/.claude/agents/supervisor.md) | Supervisor persona |
| [pm_sessions.js](/scripts/pm_sessions.js) | Session management |

### B. Glossary

| Term | Definition |
|------|------------|
| SOUL.md | Unified agent identity document |
| Permission tier | Classification level for command safety |
| Staggered wakeup | Offset heartbeat timing to distribute load |
| Worktree registry | JSON file tracking active worktrees |
| Orphan worktree | Worktree without active session |
| Task decomposition | Breaking complex work into subtasks |

### C. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-01 | PM Persona | Initial draft |

---

**Document Status**: Draft
**Next Review**: 2026-02-03
**Approvals Required**: Christopher (Product Owner)
