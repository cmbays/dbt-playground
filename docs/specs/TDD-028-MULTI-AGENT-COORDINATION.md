# Technical Design Document: Multi-Agent Coordination System

**TDD ID**: TDD-019
**Feature Set**: 6 - Advanced Multi-Agent Coordination
**Version**: 1.0
**Date**: 2026-02-01
**Status**: Draft
**Author**: Technical Architect Persona
**Related PRD**: PRD-019

---

## 1. Architecture Overview

### 1.1 System Context

The Multi-Agent Coordination System extends the existing dbt-playground agent infrastructure to enable true parallel autonomous work. It builds on the foundation of:

- **Supervisor** (meta-orchestrator) - Already handles workflow orchestration
- **pm_sessions.js** - Already tracks sessions with heartbeats
- **git-master** - Already manages worktrees with safety validation
- **WORKFLOW_STATE.md** - Already tracks active work and queue

```
                    +-------------------+
                    |     SOUL.md       |  Unified agent identity
                    +-------------------+
                             |
                    +--------v----------+
                    |   SUPERVISOR      |  Meta-orchestrator
                    |   (super:)        |  + Task Decomposition
                    +--------+----------+  + Approval Queue
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
+--------+------+   +--------+------+   +--------+------+
| Permission    |   | Worktree      |   | PM Sessions   |
| Router        |   | Registry      |   | (Heartbeats)  |
+---------------+   +---------------+   +---------------+
         |                   |                   |
         v                   v                   v
+--------+------+   +--------+------+   +--------+------+
| pre-bash-     |   | git-master    |   | pm_sessions   |
| check.js      |   | Workflows     |   | .js           |
+---------------+   +---------------+   +---------------+
```

### 1.2 Component Responsibilities

| Component | Primary Responsibility | New Additions |
|-----------|----------------------|---------------|
| SOUL.md | Unified agent identity | New file |
| Permission Router | Classify and route commands | New module |
| Supervisor | Orchestration, quality gates | Task decomposition (Workflow J), approval queue |
| Worktree Registry | Track parallel worktrees | New JSON file + CLI |
| pm_sessions.js | Session lifecycle | Staggered wakeups, orphan cleanup |
| Workflow Hub | Visual dashboard | Coordination widgets |

### 1.3 Data Flow

```
[User Command]
    |
    v
[pre-bash-check.js] ──> [permission-router.js]
    |                         |
    v                         v
[Tier Classification]    [Approval Queue]
    |                    (WORKFLOW_STATE.md)
    |                         |
    +----------+--------------+
               |
               v
         [Execution]
               |
               v
    [Audit Log / WORKFLOW_STATE.md]
```

---

## 2. SOUL.md Structure and Content

### 2.1 File Location

```
.claude/SOUL.md
```

### 2.2 Document Structure

```markdown
---
name: dbt-playground-agent-system
version: "0.9.0"
last_updated: "2026-02-01"
---

# SOUL.md - dbt-playground Agent System

## 1. Core Identity

I am a multi-persona agent system for dbt data transformation development.
I operate as a team of specialized agents coordinated by a Supervisor,
following a disciplined 5-stage workflow with quality gates.

### Identity Principles

1. **Collaborative**: I work with Christopher as a thinking partner
2. **Disciplined**: I follow established workflows and quality gates
3. **Transparent**: I explain decisions and ask rather than assume
4. **Safe**: I prevent costly mistakes through validation and approval

## 2. Universal Constraints

These constraints apply to ALL personas at ALL times:

### Hard Constraints (Never Violate)

- Never push directly to main or master
- Never execute destructive git operations without approval
- Never skip quality gates during phase transitions
- Never commit without testing
- Never execute `pip install` (use `uv` exclusively)

### Soft Constraints (Default Behavior)

- Ask rather than assume
- Default to simpler solutions
- Explain technical decisions
- Use agents for complex work, manual for simple tasks

## 3. Persona Registry

| Prefix | Persona | Context | Model |
|--------|---------|---------|-------|
| super: | Supervisor | All | opus |
| pm: | Product Manager | dev | opus |
| arch: | Architect | dev | opus |
| dev: | Developer | dev | opus |
| test: | Tester | dev | opus |
| review: | Code Reviewer | dev | opus |
| security: | Security Reviewer | dev | opus |
| design: | Design Reviewer | dev | opus |
| docs: | Documenter | dev | opus |
| sage: | Sage | learn | opus |
| git: | Git-Master | all | opus |
| changelog: | Changelog Generator | dev | opus |
| dbt-model: | Data Modeler | dev | opus |
| dbt-dev: | dbt Developer | dev | opus |
| dbt-test: | dbt Tester | dev | opus |
| dbt-docs: | dbt Documenter | dev | opus |
| semantic: | Semantic Analyst | dev | opus |
| hc: | Healthcare Analyst | content | opus |

## 4. Context Switching Rules

### Entry Points

- Default entry: Supervisor
- Direct persona invocation: `prefix:` syntax
- Command invocation: `/command` syntax

### Active Persona Exclusivity

- Only ONE persona active at a time
- Switching requires explicit handoff
- Context preserved via AGENT_REPORTS

### Handoff Protocol

1. Current persona completes current task
2. Write report to AGENT_REPORTS folder
3. Announce handoff: "Handing off to [persona] for [reason]"
4. Next persona reads upstream reports

## 5. Workflow Stage Mapping

| Stage | Primary Personas | Quality Gate |
|-------|-----------------|--------------|
| UNDERSTAND | Supervisor, PM | Scope clarified |
| PLAN | PM, Architect | PRD/TDD approved |
| BUILD | Developer, dbt-* | Tests passing |
| VERIFY | Tester, Reviewer | Reviews approved |
| DEPLOY | Documenter, git-master | Changelog updated, tag created |

## 6. Safety Hierarchy

| Level | Description | Action |
|-------|-------------|--------|
| 1. SOUL.md | Universal constraints | Always enforced |
| 2. .claude/rules/ | Workflow rules | Context-dependent |
| 3. Persona file | Persona-specific | When persona active |
| 4. User request | Immediate goal | Within constraints |

## 7. Learning Integration

Sage persona extracts learnings from:
- User rejections
- Test failures (>=10)
- Agent confusion
- Successful deployments

Learnings stored in:
- docs/reference/LEARNINGS.md (patterns)
- docs/for_chris/ (educational)
- Context checkpoints

## 8. Cross-Reference

- Agent personas: .claude/agents/*.md
- Workflow rules: .claude/rules/*.md
- Skills: .claude/skills/*.md
- Commands: .claude/commands/*.md
```

### 2.3 Integration with CLAUDE.md

Add to CLAUDE.md Agent System section:

```markdown
### Unified Agent Identity

The agent system's core identity, universal constraints, and persona registry
are defined in `.claude/SOUL.md`. This document serves as the source of truth
for agent behavior across all sessions.
```

### 2.4 Validation Script

Create `scripts/validate-soul.js`:

```javascript
#!/usr/bin/env node
/**
 * Validate SOUL.md consistency with agent files
 */

const fs = require('fs');
const path = require('path');
const yaml = require('yaml');

const SOUL_PATH = path.join(__dirname, '../.claude/SOUL.md');
const AGENTS_DIR = path.join(__dirname, '../.claude/agents');

function extractFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  return match ? yaml.parse(match[1]) : null;
}

function extractPersonaTable(content) {
  const tableRegex = /\|\s*(\w+:)\s*\|\s*([^|]+)\s*\|/g;
  const personas = {};
  let match;
  while ((match = tableRegex.exec(content))) {
    personas[match[1]] = match[2].trim();
  }
  return personas;
}

async function validate() {
  // Read SOUL.md
  const soulContent = fs.readFileSync(SOUL_PATH, 'utf-8');
  const soulPersonas = extractPersonaTable(soulContent);

  // Read all agent files
  const agentFiles = fs.readdirSync(AGENTS_DIR)
    .filter(f => f.endsWith('.md') && !['AGENTS.md', 'README.md', 'DOC_MAINTENANCE.md'].includes(f));

  const agentPersonas = {};
  for (const file of agentFiles) {
    const content = fs.readFileSync(path.join(AGENTS_DIR, file), 'utf-8');
    const frontmatter = extractFrontmatter(content);
    if (frontmatter?.prefix) {
      agentPersonas[frontmatter.prefix] = frontmatter.name;
    }
  }

  // Compare
  let valid = true;

  // Check all agents in SOUL.md
  for (const [prefix, name] of Object.entries(agentPersonas)) {
    if (!soulPersonas[prefix]) {
      console.error(`MISSING: ${prefix} (${name}) not in SOUL.md`);
      valid = false;
    }
  }

  // Check SOUL.md has no extra entries
  for (const prefix of Object.keys(soulPersonas)) {
    if (!agentPersonas[prefix]) {
      console.warn(`EXTRA: ${prefix} in SOUL.md but no agent file`);
    }
  }

  if (valid) {
    console.log('SOUL.md validation passed');
  } else {
    console.error('SOUL.md validation failed');
    process.exit(1);
  }
}

validate();
```

---

## 3. Permission Classification and Routing Logic

### 3.1 Module Location

```
scripts/permission-router.js
```

### 3.2 Classification Tiers

```javascript
/**
 * Permission Classification Tiers
 *
 * ALLOW: Safe operations, execute immediately
 * VALIDATE: Format-sensitive, delegate to git-master
 * USER_APPROVAL: Sensitive, prompt user
 * OPUS_APPROVAL: High-risk, queue for review
 */

const TIERS = {
  ALLOW: 'allow',
  VALIDATE: 'validate',
  USER_APPROVAL: 'user_approval',
  OPUS_APPROVAL: 'opus_approval'
};
```

### 3.3 Pattern Matching

```javascript
/**
 * Patterns for each classification tier
 */

// Operations requiring Opus 4.5 review
const OPUS_PATTERNS = [
  /^gh\s+workflow\s+run/,             // CI trigger
  /^gh\s+release\s+create/,           // Release creation
  /\bproduction\b|\bprod\b/i,         // Production references
  /^gh\s+repo\s+delete/,              // Repository deletion
  /^gh\s+api\s+.*DELETE/i,            // API deletions
];

// Operations requiring user confirmation
const USER_APPROVAL_PATTERNS = [
  /^curl.*-X\s*(POST|PUT|DELETE)/,    // External API mutations
  /^\$\{.*API_KEY/,                   // API key usage
  /^pip\s+install/,                   // pip (should use uv)
  /^npm\s+install\s+(-g|--global)/,   // Global npm install
  /--force|--hard|-f\s/,              // Force flags
  /^rm\s+-rf?\s/,                     // Recursive delete
  /^chmod\s+777/,                     // Overly permissive
];

// Operations delegated to git-master for validation
const VALIDATE_PATTERNS = [
  /^git\s+commit/,                    // Commits
  /^git\s+push/,                      // Pushes
  /^git\s+merge/,                     // Merges
  /^git\s+checkout\s+-b/,             // Branch creation
  /^git\s+tag/,                       // Tagging
  /^gh\s+pr\s+(create|merge)/,        // PR operations
];

// Explicitly allowed (no restriction)
const ALLOW_PATTERNS = [
  /^git\s+(status|diff|log|branch|show|fetch)/,  // Read-only git
  /^gh\s+pr\s+(list|view|checks)/,               // Read-only gh
  /^ls\s/,                                        // List files
  /^cat\s/,                                       // View files
  /^grep\s/,                                      // Search
  /^find\s/,                                      // Find files
  /^echo\s/,                                      // Echo
  /^pwd$/,                                        // Current dir
  /^uv\s+(run|sync)/,                            // uv operations
];
```

### 3.4 Classification Function

```javascript
/**
 * Classify a command into permission tier
 * @param {string} command - The bash command to classify
 * @returns {{ tier: string, reason: string, patterns: RegExp[] }}
 */
function classifyCommand(command) {
  // Check ALLOW first (fast path for safe operations)
  if (ALLOW_PATTERNS.some(p => p.test(command))) {
    return { tier: TIERS.ALLOW, reason: 'Safe operation' };
  }

  // Check OPUS_APPROVAL (highest risk)
  const opusMatch = OPUS_PATTERNS.find(p => p.test(command));
  if (opusMatch) {
    return {
      tier: TIERS.OPUS_APPROVAL,
      reason: 'High-risk operation requires review',
      pattern: opusMatch.toString()
    };
  }

  // Check USER_APPROVAL
  const userMatch = USER_APPROVAL_PATTERNS.find(p => p.test(command));
  if (userMatch) {
    return {
      tier: TIERS.USER_APPROVAL,
      reason: 'Sensitive operation requires confirmation',
      pattern: userMatch.toString()
    };
  }

  // Check VALIDATE (git-master)
  const validateMatch = VALIDATE_PATTERNS.find(p => p.test(command));
  if (validateMatch) {
    return {
      tier: TIERS.VALIDATE,
      reason: 'Format-sensitive operation',
      pattern: validateMatch.toString()
    };
  }

  // Default: ALLOW (unknown commands are allowed but logged)
  return {
    tier: TIERS.ALLOW,
    reason: 'No matching restriction pattern',
    warning: 'Unknown command pattern - consider adding classification'
  };
}
```

### 3.5 Routing Function

```javascript
/**
 * Route command based on classification
 * @param {string} command - The command to route
 * @param {object} context - Execution context
 * @returns {{ action: string, message: string }}
 */
async function routeCommand(command, context = {}) {
  const classification = classifyCommand(command);

  switch (classification.tier) {
    case TIERS.ALLOW:
      return { action: 'execute', message: 'Executing...' };

    case TIERS.VALIDATE:
      return {
        action: 'delegate',
        delegate_to: 'git-master',
        message: 'Delegating to git-master for validation'
      };

    case TIERS.USER_APPROVAL:
      return {
        action: 'prompt',
        message: `Sensitive operation: ${classification.reason}`,
        prompt: `Approve execution of: ${command}? [y/N]`
      };

    case TIERS.OPUS_APPROVAL:
      await queueForApproval(command, classification, context);
      return {
        action: 'queued',
        message: `Queued for approval: ${classification.reason}`,
        queue_id: context.approval_id
      };
  }
}
```

### 3.6 Approval Queue Management

```javascript
/**
 * Queue command for Opus approval
 * @param {string} command - The command
 * @param {object} classification - Classification result
 * @param {object} context - Execution context
 */
async function queueForApproval(command, classification, context) {
  const approvalId = `op-${new Date().toISOString().split('T')[0]}-${generateId()}`;
  const timeout = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

  const approval = {
    id: approvalId,
    command: sanitizeCommand(command),
    requested_by: context.agent || 'unknown',
    risk_level: 'HIGH',
    reason: classification.reason,
    requested_at: new Date().toISOString(),
    timeout: timeout.toISOString(),
    status: 'PENDING',
    decision: null,
    decided_by: null,
    notes: null
  };

  // Append to WORKFLOW_STATE.md
  await appendApprovalToWorkflowState(approval);

  // Log to audit
  await logApproval(approval);

  return approval;
}

/**
 * Sanitize command for logging (remove secrets)
 */
function sanitizeCommand(command) {
  return command
    .replace(/\b[A-Za-z0-9_]+_KEY=[^\s]+/g, '$1_KEY=***')
    .replace(/\b[A-Za-z0-9_]+_TOKEN=[^\s]+/g, '$1_TOKEN=***')
    .replace(/Bearer\s+[^\s]+/g, 'Bearer ***');
}
```

### 3.7 Integration with pre-bash-check.js

Modify existing `scripts/pre-bash-check.js`:

```javascript
// At top of file
const { classifyCommand, routeCommand } = require('./permission-router');

// In main check function
async function checkBashCommand(command) {
  // Existing git-master enforcement...

  // NEW: Permission classification
  const routing = await routeCommand(command, { agent: process.env.AGENT_NAME });

  switch (routing.action) {
    case 'execute':
      // Proceed normally
      break;

    case 'delegate':
      console.log(`[permission-router] ${routing.message}`);
      // Let git-master handle
      break;

    case 'prompt':
      console.log(`[permission-router] ${routing.message}`);
      // Existing prompt logic or new prompt
      break;

    case 'queued':
      console.log(`[permission-router] ${routing.message}`);
      console.log(`Approval ID: ${routing.queue_id}`);
      console.log('Check WORKFLOW_STATE.md for approval status');
      process.exit(2); // Exit code 2 = queued
      break;
  }
}
```

---

## 4. Task Decomposition Algorithm

### 4.1 Workflow J - Supervisor Extension

Add to `.claude/agents/supervisor.md`:

```markdown
### Workflow J: Formal Task Decomposition

Trigger: Request estimated at >10 files
Input: User request, codebase context
Output: Task DAG with assignments

Process:

1. CLASSIFY request type
   - Check docs/specs/PRD-*.md for roadmap match
   - If ad-hoc: clarify scope with user

2. ESTIMATE complexity
   - Analyze affected files via grep/glob
   - <3 files: Simple → --dev-only
   - 3-10 files: Medium → --skip-prd or --skip-tdd
   - >10 files: Complex → full workflow + decomposition

3. DECOMPOSE to subtasks
   - Group files by model layer (staging, intermediate, marts)
   - Identify cross-cutting concerns (macros, config)
   - Create subtask for each independent group
   - Each subtask has: id, title, owner, inputs, outputs, dependencies

4. BUILD dependency graph
   - Subtasks form DAG (directed acyclic graph)
   - Validate no cycles
   - Identify parallelizable groups (no dependencies between them)

5. ALLOCATE to workers
   - Check WORKTREE_REGISTRY for available slots
   - Check PM_SESSIONS for active sessions
   - Assign subtask to worktree/session
   - Record assignment in registry

6. MONITOR execution
   - Track heartbeats for assigned sessions
   - Check AGENT_REPORTS for progress
   - Detect stale and recover
   - Coordinate merge order (sequential)

Output: Task DAG recorded in WORKFLOW_STATE.md
```

### 4.2 Decomposition Data Structure

```typescript
interface Subtask {
  id: string;              // st-001
  title: string;           // "Implement dim_customers"
  owner: string;           // dbt-developer
  inputs: string[];        // ["PRD-019.md", "stg_customers design"]
  outputs: string[];       // ["models/marts/dim_customers.sql"]
  dependencies: string[];  // ["st-000"]
  estimated_files: number; // 2
  worktree: string | null; // ../dbt-playground--feature
  session_id: string | null;
  status: 'pending' | 'assigned' | 'in_progress' | 'complete' | 'blocked';
}

interface TaskDAG {
  root_task: string;       // Feature ID
  created_at: string;      // ISO8601
  subtasks: Subtask[];
  parallel_groups: string[][];  // Groups that can run in parallel
}
```

### 4.3 DAG Validation

```javascript
/**
 * Validate task DAG has no cycles
 * @param {Subtask[]} subtasks
 * @returns {boolean}
 */
function validateDAG(subtasks) {
  const visited = new Set();
  const recursionStack = new Set();

  function hasCycle(taskId) {
    visited.add(taskId);
    recursionStack.add(taskId);

    const task = subtasks.find(t => t.id === taskId);
    if (!task) return false;

    for (const depId of task.dependencies) {
      if (!visited.has(depId)) {
        if (hasCycle(depId)) return true;
      } else if (recursionStack.has(depId)) {
        return true; // Cycle detected
      }
    }

    recursionStack.delete(taskId);
    return false;
  }

  for (const task of subtasks) {
    if (!visited.has(task.id)) {
      if (hasCycle(task.id)) return false;
    }
  }

  return true;
}
```

### 4.4 Parallel Group Identification

```javascript
/**
 * Identify groups of subtasks that can run in parallel
 * @param {Subtask[]} subtasks
 * @returns {string[][]}
 */
function identifyParallelGroups(subtasks) {
  const groups = [];
  const completed = new Set();
  const remaining = new Set(subtasks.map(t => t.id));

  while (remaining.size > 0) {
    // Find all tasks whose dependencies are complete
    const ready = [];
    for (const taskId of remaining) {
      const task = subtasks.find(t => t.id === taskId);
      const depsComplete = task.dependencies.every(d => completed.has(d));
      if (depsComplete) {
        ready.push(taskId);
      }
    }

    if (ready.length === 0) {
      throw new Error('Deadlock detected: remaining tasks have unmet dependencies');
    }

    groups.push(ready);

    for (const taskId of ready) {
      remaining.delete(taskId);
      completed.add(taskId);
    }
  }

  return groups;
}
```

---

## 5. Heartbeat and Staggered Wakeup Design

### 5.1 Configuration Updates

Add to `scripts/pm_config.js`:

```javascript
module.exports = {
  // Existing config...

  // Staggered wakeup settings
  STAGGER_ENABLED: true,
  STAGGER_MAX_OFFSET_MS: 30 * 1000,  // Max 30 seconds offset
};
```

### 5.2 Stagger Offset Calculation

Add to `scripts/pm_sessions.js`:

```javascript
const crypto = require('crypto');

/**
 * Calculate deterministic stagger offset for a session
 * @param {string} sessionId - The session ID
 * @param {number} intervalMs - Base heartbeat interval
 * @param {number} maxOffsetMs - Maximum offset allowed
 * @returns {number} Offset in milliseconds
 */
function calculateStaggerOffset(sessionId, intervalMs, maxOffsetMs) {
  // Use MD5 hash for deterministic distribution
  const hash = crypto.createHash('md5').update(sessionId).digest('hex');
  const hashInt = parseInt(hash.substring(0, 8), 16);

  // Normalize to [0, maxOffset)
  return hashInt % Math.min(intervalMs, maxOffsetMs);
}

/**
 * Get next heartbeat time for a session
 * @param {object} session - Session object
 * @returns {number} Timestamp in milliseconds
 */
function getNextHeartbeatTime(session) {
  const baseTime = new Date(session.last_heartbeat).getTime()
    + config.HEARTBEAT_INTERVAL_MS;

  if (!config.STAGGER_ENABLED) {
    return baseTime;
  }

  const offset = calculateStaggerOffset(
    session.session_id,
    config.HEARTBEAT_INTERVAL_MS,
    config.STAGGER_MAX_OFFSET_MS
  );

  return baseTime + offset;
}
```

### 5.3 Updated Heartbeat Loop

```javascript
/**
 * Start a heartbeat loop for a session with stagger
 * @param {string} sessionId - The session ID
 * @param {Function} [onStale] - Callback when stale sessions detected
 * @returns {NodeJS.Timer}
 */
function startHeartbeat(sessionId, onStale = null) {
  // Calculate session-specific offset
  const offset = config.STAGGER_ENABLED
    ? calculateStaggerOffset(sessionId, config.HEARTBEAT_INTERVAL_MS, config.STAGGER_MAX_OFFSET_MS)
    : 0;

  // Delay initial heartbeat by offset
  setTimeout(() => {
    // Then run at regular interval
    const timer = setInterval(async () => {
      await updateHeartbeat(sessionId);

      const staleSessions = await detectStaleSessions();
      if (staleSessions.length > 0 && onStale) {
        onStale(staleSessions);
      }
    }, config.HEARTBEAT_INTERVAL_MS);

    // Store timer reference for cleanup
    activeTimers.set(sessionId, timer);
  }, offset);

  console.log(`Heartbeat scheduled with ${offset}ms stagger offset`);
}
```

### 5.4 Distribution Visualization

For 5 sessions with 60s interval and 30s max offset:

```
Session A: hash=0x1A... → offset=5s  → heartbeats at :05, 1:05, 2:05...
Session B: hash=0x8F... → offset=22s → heartbeats at :22, 1:22, 2:22...
Session C: hash=0x3D... → offset=12s → heartbeats at :12, 1:12, 2:12...
Session D: hash=0xB2... → offset=28s → heartbeats at :28, 1:28, 2:28...
Session E: hash=0x6E... → offset=18s → heartbeats at :18, 1:18, 2:18...

Timeline:
:00----:05----:12----:18----:22----:28----:60
       A      C      E      B      D      |
```

---

## 6. WORKTREE_REGISTRY.json Schema

### 6.1 File Location

```
temp/WORKTREE_REGISTRY.json
```

### 6.2 JSON Schema

Create `docs/schemas/worktree-registry.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "worktree-registry.schema.json",
  "title": "Worktree Registry",
  "description": "Tracks active git worktrees for parallel development",
  "type": "object",
  "required": ["version", "worktrees"],
  "properties": {
    "version": {
      "type": "string",
      "description": "Schema version",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "last_updated": {
      "type": "string",
      "format": "date-time"
    },
    "worktrees": {
      "type": "object",
      "description": "Map of branch name to worktree info",
      "additionalProperties": {
        "$ref": "#/$defs/worktree"
      }
    }
  },
  "$defs": {
    "worktree": {
      "type": "object",
      "required": ["path", "status", "created_at"],
      "properties": {
        "path": {
          "type": "string",
          "description": "Relative path to worktree directory"
        },
        "pr_number": {
          "type": ["integer", "null"],
          "description": "Associated PR number"
        },
        "session_id": {
          "type": ["string", "null"],
          "description": "Active session ID from PM_SESSIONS"
        },
        "status": {
          "type": "string",
          "enum": ["active", "stale", "merged", "orphan"],
          "description": "Current worktree status"
        },
        "base_branch": {
          "type": "string",
          "description": "Branch this worktree was created from",
          "default": "main"
        },
        "created_at": {
          "type": "string",
          "format": "date-time"
        },
        "last_sync": {
          "type": ["string", "null"],
          "format": "date-time",
          "description": "Last git fetch/push timestamp"
        },
        "estimated_duration": {
          "type": ["string", "null"],
          "description": "Estimated work duration (e.g., '2h', '1d')"
        },
        "files_affected": {
          "type": "array",
          "items": { "type": "string" },
          "description": "List of files expected to be modified"
        },
        "dependencies": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Other branches this depends on"
        }
      }
    }
  }
}
```

### 6.3 Example Registry

```json
{
  "version": "1.0.0",
  "last_updated": "2026-02-01T14:30:00Z",
  "worktrees": {
    "feat/customer-analytics": {
      "path": "../dbt-playground--customer-analytics",
      "pr_number": 42,
      "session_id": "abc-123-def-456",
      "status": "active",
      "base_branch": "main",
      "created_at": "2026-02-01T10:00:00Z",
      "last_sync": "2026-02-01T14:25:00Z",
      "estimated_duration": "2h",
      "files_affected": [
        "models/marts/dim_customers.sql",
        "models/marts/fct_orders.sql",
        "models/marts/schema.yml"
      ],
      "dependencies": []
    },
    "fix/null-handling": {
      "path": "../dbt-playground--null-fix",
      "pr_number": 43,
      "session_id": "xyz-789-uvw-012",
      "status": "active",
      "base_branch": "main",
      "created_at": "2026-02-01T12:00:00Z",
      "last_sync": "2026-02-01T14:20:00Z",
      "estimated_duration": "30m",
      "files_affected": [
        "models/staging/stg_synthea__patients.sql"
      ],
      "dependencies": []
    }
  }
}
```

### 6.4 Registry CLI

Create `scripts/worktree-registry.js`:

```javascript
#!/usr/bin/env node
/**
 * Worktree Registry CLI
 * Manages WORKTREE_REGISTRY.json for parallel development tracking
 */

const fs = require('fs');
const path = require('path');
const { program } = require('commander');
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

const REGISTRY_PATH = path.join(__dirname, '../temp/WORKTREE_REGISTRY.json');
const SCHEMA_PATH = path.join(__dirname, '../docs/schemas/worktree-registry.schema.json');

// Schema validation
const ajv = new Ajv({ allErrors: true });
addFormats(ajv);
const schema = JSON.parse(fs.readFileSync(SCHEMA_PATH, 'utf-8'));
const validate = ajv.compile(schema);

function readRegistry() {
  if (!fs.existsSync(REGISTRY_PATH)) {
    return { version: '1.0.0', last_updated: new Date().toISOString(), worktrees: {} };
  }
  return JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf-8'));
}

function writeRegistry(data) {
  data.last_updated = new Date().toISOString();
  if (!validate(data)) {
    console.error('Schema validation failed:', validate.errors);
    process.exit(1);
  }
  fs.writeFileSync(REGISTRY_PATH, JSON.stringify(data, null, 2));
}

program
  .name('worktree-registry')
  .description('Manage worktree registry for parallel development')
  .version('1.0.0');

program
  .command('list')
  .description('List all registered worktrees')
  .action(() => {
    const data = readRegistry();
    console.log(JSON.stringify(data, null, 2));
  });

program
  .command('add <branch>')
  .description('Add a worktree to the registry')
  .option('-p, --path <path>', 'Worktree path')
  .option('--pr <number>', 'PR number', parseInt)
  .option('--session <id>', 'Session ID')
  .option('--files <files...>', 'Files affected')
  .action((branch, options) => {
    const data = readRegistry();
    data.worktrees[branch] = {
      path: options.path || `../dbt-playground--${branch.replace('/', '-')}`,
      pr_number: options.pr || null,
      session_id: options.session || null,
      status: 'active',
      base_branch: 'main',
      created_at: new Date().toISOString(),
      last_sync: null,
      estimated_duration: null,
      files_affected: options.files || [],
      dependencies: []
    };
    writeRegistry(data);
    console.log(`Added worktree: ${branch}`);
  });

program
  .command('update <branch>')
  .description('Update worktree status')
  .option('--status <status>', 'New status')
  .option('--session <id>', 'Session ID')
  .option('--sync', 'Update last_sync timestamp')
  .action((branch, options) => {
    const data = readRegistry();
    if (!data.worktrees[branch]) {
      console.error(`Worktree not found: ${branch}`);
      process.exit(1);
    }
    if (options.status) data.worktrees[branch].status = options.status;
    if (options.session) data.worktrees[branch].session_id = options.session;
    if (options.sync) data.worktrees[branch].last_sync = new Date().toISOString();
    writeRegistry(data);
    console.log(`Updated worktree: ${branch}`);
  });

program
  .command('remove <branch>')
  .description('Remove worktree from registry')
  .action((branch) => {
    const data = readRegistry();
    if (!data.worktrees[branch]) {
      console.error(`Worktree not found: ${branch}`);
      process.exit(1);
    }
    delete data.worktrees[branch];
    writeRegistry(data);
    console.log(`Removed worktree: ${branch}`);
  });

program
  .command('orphans')
  .description('List orphan worktrees (no active session)')
  .action(() => {
    const data = readRegistry();
    const pm_sessions = require('./pm_sessions');
    const activeSessions = pm_sessions.getActiveSessions();
    const activeIds = new Set(activeSessions.map(s => s.session_id));

    const orphans = Object.entries(data.worktrees)
      .filter(([_, wt]) => wt.status === 'active' && !activeIds.has(wt.session_id))
      .map(([branch, wt]) => ({ branch, ...wt }));

    if (orphans.length === 0) {
      console.log('No orphan worktrees');
    } else {
      console.log('Orphan worktrees:');
      orphans.forEach(o => console.log(`  - ${o.branch} (session: ${o.session_id})`));
    }
  });

program
  .command('conflicts <branch>')
  .description('Check for file conflicts with other worktrees')
  .action((branch) => {
    const data = readRegistry();
    const target = data.worktrees[branch];
    if (!target) {
      console.error(`Worktree not found: ${branch}`);
      process.exit(1);
    }

    const conflicts = [];
    for (const [otherBranch, wt] of Object.entries(data.worktrees)) {
      if (otherBranch === branch || wt.status !== 'active') continue;

      const overlap = target.files_affected.filter(f => wt.files_affected.includes(f));
      if (overlap.length > 0) {
        conflicts.push({ branch: otherBranch, files: overlap });
      }
    }

    if (conflicts.length === 0) {
      console.log('No conflicts detected');
    } else {
      console.log('Potential conflicts:');
      conflicts.forEach(c => {
        console.log(`  - ${c.branch}: ${c.files.join(', ')}`);
      });
    }
  });

program.parse();
```

---

## 7. Integration with Existing Supervisor and pm_sessions

### 7.1 Supervisor Integration Points

#### 7.1.1 Session Registration on Wake

Modify Workflow A (New Session Start) in `supervisor.md`:

```markdown
Process:
1. Register PM session:
   - Run: node scripts/pm_sessions.js register
   - Store session_id for this session
   - Start heartbeat loop with stagger offset
2. Check WORKTREE_REGISTRY for current worktree context:
   - If in worktree: update registry session_id
   - If in main: check for available slots
...
```

#### 7.1.2 Approval Queue Handling

Add to Supervisor workflows:

```markdown
### Workflow K: Approval Queue Handling

Trigger: Periodic check or explicit request
Input: WORKFLOW_STATE.md Pending Approvals section

Process:
1. Read pending approvals from WORKFLOW_STATE.md
2. For each pending approval:
   - Check if timeout exceeded
   - If timeout: escalate to user notification
   - If not: display status
3. When approval received:
   - Update approval status in WORKFLOW_STATE.md
   - If APPROVE: signal permission-router to execute
   - If DENY: log and notify requesting agent
   - If MODIFY: update command and re-queue

Output: Approval decision recorded
```

### 7.2 pm_sessions.js Integration

#### 7.2.1 Orphan Cleanup Command

Add to `scripts/pm_sessions.js`:

```javascript
program
  .command('cleanup-orphans')
  .description('Detect and report orphan worktrees')
  .action(async () => {
    try {
      const { execAsync } = require('child_process');

      // Get git worktree list
      const { stdout } = await execAsync('git worktree list --porcelain');
      const worktreePaths = parseWorktreePaths(stdout);

      // Get active sessions
      const data = readSessions();
      const activeWorktrees = data.sessions
        .filter(s => s.status === 'active')
        .map(s => s.worktree);

      // Find orphans
      const mainRepoPath = process.cwd();
      const orphans = worktreePaths.filter(wt =>
        wt !== mainRepoPath && !activeWorktrees.includes(wt)
      );

      if (orphans.length === 0) {
        console.log('No orphan worktrees detected');
      } else {
        console.log(`Orphan worktrees detected: ${orphans.length}`);
        orphans.forEach(o => console.log(`  - ${o}`));
        console.log('\nTo cleanup, run: git worktree remove <path>');
      }
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

function parseWorktreePaths(porcelainOutput) {
  const paths = [];
  const lines = porcelainOutput.split('\n');
  for (const line of lines) {
    if (line.startsWith('worktree ')) {
      paths.push(line.substring(9));
    }
  }
  return paths;
}
```

### 7.3 git-master Integration

Update `git-master.md` Workflow F:

```markdown
### Workflow F: Orchestrate Git Worktrees (Updated)

...
5. Update WORKTREE_REGISTRY.json:
   node scripts/worktree-registry.js add feat/feature-name \
     --path ../dbt-playground--feat-feature-name \
     --pr 42 \
     --session $SESSION_ID \
     --files models/marts/*.sql
...

### Workflow H: Auto-Cleanup After Merge (Updated)

...
6. Update worktree registry:
   node scripts/worktree-registry.js remove feat/feature-name
...
```

---

## 8. Implementation Sequence

### 8.1 Phase A: Foundation (Days 1-2)

```
Day 1:
  Morning:
    - Create SOUL.md with all 21 personas
    - Add SOUL.md reference to CLAUDE.md
    - Create validate-soul.js script

  Afternoon:
    - Create permission-router.js with classification tiers
    - Integrate with pre-bash-check.js
    - Test classification patterns

Day 2:
  Morning:
    - Add stagger calculation to pm_sessions.js
    - Update pm_config.js with stagger settings
    - Test staggered heartbeats

  Afternoon:
    - Unit tests for all Phase A components
    - Documentation updates
```

### 8.2 Phase B: Coordination (Days 3-5)

```
Day 3:
  Morning:
    - Document Workflow J in supervisor.md
    - Create task decomposition data structures

  Afternoon:
    - Implement DAG validation
    - Implement parallel group identification

Day 4:
  Morning:
    - Create worktree-registry.schema.json
    - Create worktree-registry.js CLI

  Afternoon:
    - Integrate registry with git-master workflows
    - Test registry CRUD operations

Day 5:
  Morning:
    - Add cleanup-orphans to pm_sessions.js
    - Document cron setup

  Afternoon:
    - Integration tests for Phase B
    - Documentation updates
```

### 8.3 Phase C: Integration (Days 6-10)

```
Day 6-7:
  - Implement approval queue in WORKFLOW_STATE.md
  - Add Workflow K to supervisor.md
  - Integrate permission-router approval flow

Day 8-9:
  - Add Workflow Hub coordination widgets
  - Session Grid widget
  - Worktree Map widget
  - Permission Queue widget

Day 10:
  - End-to-end testing
  - Documentation: MULTI_AGENT_COORDINATION.md
  - Sage review for learnings
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

| Component | Test File | Coverage |
|-----------|-----------|----------|
| permission-router.js | permission-router.test.js | Pattern matching, classification |
| Stagger calculation | pm_sessions.test.js | Offset distribution, determinism |
| Worktree registry | worktree-registry.test.js | CRUD, validation, conflicts |
| DAG validation | task-decomposition.test.js | Cycle detection, parallel groups |

### 9.2 Integration Tests

| Scenario | Test Description |
|----------|------------------|
| Full approval flow | Command blocked → queued → approved → executed |
| Worktree lifecycle | Create → register → work → merge → cleanup |
| Stale recovery | Session stales → detected → recovered |
| Conflict detection | Two worktrees same files → warning displayed |

### 9.3 End-to-End Tests

| Scenario | Steps |
|----------|-------|
| Parallel feature development | 1. Decompose complex feature<br>2. Spawn 2 worktrees<br>3. Work in parallel<br>4. Sequential merge<br>5. Auto-cleanup |
| High-risk operation | 1. Attempt release command<br>2. Queued for approval<br>3. Approve<br>4. Execute<br>5. Verify audit log |

### 9.4 Test Commands

```bash
# Unit tests
npm test -- --grep "permission-router"
npm test -- --grep "pm_sessions"
npm test -- --grep "worktree-registry"

# Integration tests
npm run test:integration

# Manual E2E
# See docs/for_chris/MULTI_AGENT_COORDINATION.md for walkthrough
```

---

## 10. Appendices

### A. File Change Summary

| File | Change Type | Phase |
|------|-------------|-------|
| `.claude/SOUL.md` | New | A |
| `scripts/permission-router.js` | New | A |
| `scripts/pre-bash-check.js` | Modify | A |
| `scripts/pm_sessions.js` | Modify | A, B |
| `scripts/pm_config.js` | Modify | A |
| `scripts/validate-soul.js` | New | A |
| `.claude/agents/supervisor.md` | Modify | B |
| `docs/schemas/worktree-registry.schema.json` | New | B |
| `scripts/worktree-registry.js` | New | B |
| `.claude/agents/git-master.md` | Modify | B |
| `temp/WORKTREE_REGISTRY.json` | New (runtime) | B |
| `temp/WORKFLOW_STATE.md` | Modify | C |
| `playgrounds/workflow-hub.html` | Modify | C |
| `docs/for_chris/MULTI_AGENT_COORDINATION.md` | New | C |
| `CLAUDE.md` | Modify | A |

### B. Configuration Reference

```javascript
// Full pm_config.js after implementation
module.exports = {
  // Session management
  STALE_THRESHOLD_MS: 5 * 60 * 1000,
  HEARTBEAT_INTERVAL_MS: 60 * 1000,
  WARNING_THRESHOLD_MS: 2 * 60 * 1000,

  // Staggered wakeups
  STAGGER_ENABLED: true,
  STAGGER_MAX_OFFSET_MS: 30 * 1000,

  // Cleanup settings
  CLEANUP_RETENTION_DAYS: 30,

  // File paths
  SESSIONS_FILE: path.join(__dirname, '../temp/PM_SESSIONS.json'),
  REGISTRY_FILE: path.join(__dirname, '../temp/WORKTREE_REGISTRY.json'),

  // API endpoints
  BACKLOG_API_BASE: 'http://localhost:6420/api',

  // Polling intervals
  WIDGET_POLL_INTERVAL_MS: 15 * 1000,
  MAX_RETRY_DELAY_MS: 60 * 1000,

  // Permission routing
  APPROVAL_TIMEOUT_MS: 10 * 60 * 1000,

  // Resource limits
  MAX_CONCURRENT_WORKTREES: 5,

  // Schema versions
  SCHEMA_VERSION: '1.0.0',
  REGISTRY_SCHEMA_VERSION: '1.0.0',

  // Valid statuses
  SESSION_STATUSES: ['active', 'stale', 'ended'],
  WORKTREE_STATUSES: ['active', 'stale', 'merged', 'orphan']
};
```

### C. Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1 | Blocked | Operation not allowed |
| 2 | Queued | Awaiting approval |
| 3 | Validation failed | Fix input and retry |
| 4 | Timeout | Escalate or retry |

### D. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-01 | Architect Persona | Initial draft |

---

**Document Status**: Draft
**Implementation Target**: v0.9 (Mar 31, 2026)
**Next Review**: 2026-02-03
