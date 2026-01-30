---
audience: [human, sage]
priority: high
size: large
last_updated: 2026-01-29
status: active
tags: [learning, agents, orchestration, workflow, meta-architecture]
---

# The Supervisor Agent: Lessons in Meta-Orchestration

**Topic**: Building an interface layer that coordinates specialist agents while maintaining state and quality

**Context**: dbt-playground agent system evolution from direct agent invocation to supervised workflows

**Why this matters**: Understanding orchestration patterns helps you design systems where multiple specialized components need to work together coherently, whether that's AI agents, microservices, or human teams.

---

## The Problem We Solved

Before the Supervisor, our agent system had a subtle fragility: **it was stateless between sessions**.

Each time you started a new conversation, you'd have to remember:

- "Where was I in the feature workflow?"
- "Did the PRD get approved?"
- "Which track was I working on?"

And there was no enforcement. You could skip straight from "I have an idea" to "implement it now" without creating the PRD or TDD that would ensure quality. The assembly line was a suggestion, not a guarantee.

The Supervisor changes that. It's the **conductor** who remembers the score, enforces the tempo, and makes sure every section comes in at the right time.

---

## Why a Meta-Orchestrator?

You might ask: "We already have `/orchestrate`. Why add another layer?"

Great question. Here's the key distinction:

| Aspect | `/orchestrate` | Supervisor |
|--------|----------------|------------|
| **Scope** | Single feature, single session | Multiple features, across sessions |
| **Memory** | Stateless | Maintains `WORKFLOW_STATE.md` |
| **Enforcement** | Checkpoint approvals | Active artifact verification |
| **Learning** | None | Invokes Sage on failures/success |

The Supervisor doesn't replace `/orchestrate` - it **wraps** it with persistence and enforcement. Think of it like:

- `/orchestrate` = The assembly line that builds one car
- `Supervisor` = The plant manager who tracks all cars in production, ensures quality at each station, and learns from defects

---

## The State Machine: How the Supervisor Thinks

The Supervisor operates as a state machine. Every interaction follows a decision tree:

### New Request Flow

```
[User Request]
    ↓
"Is this on the roadmap or ad-hoc?"
    ↓
"Does scope need a PRD or is it clear?"
    ↓
"What phases should we skip?"
    ↓
Create/update track in WORKFLOW_STATE.md
    ↓
Delegate to /orchestrate with flags
```

This sequence of clarifying questions prevents the common failure mode of agents diving into implementation before understanding scope.

### The Quality Gate Pattern

Here's where it gets interesting. At each phase transition, the Supervisor performs **active verification**:

```
[Agent says: "PRD complete, ready for architecture"]
    ↓
Supervisor checks: Does docs/specs/PRD-*.md exist?
    ↓
Read file: Is content relevant to this feature?
    ↓
If missing → BLOCK. "Please complete the PRD first."
If present → Update state, proceed.
```

This is different from passive checkpoints ("Are you sure?"). The Supervisor actively looks for the artifact and won't proceed without it.

**Why this matters**: In any workflow system, the weakest point is the handoff. People (and agents) get eager and skip steps. Verification gates prevent this.

---

## Learning from Failures: The Sage Connection

One of the most interesting design decisions was **when to invoke Sage**.

We identified four trigger conditions:

### 1. User Rejection

```
User: "This PRD doesn't capture what I asked for"
Supervisor: *increments rejection counter*
Supervisor: "sage: Extract learnings from rejection..."
```

User rejections are gold. They reveal gaps between what was asked and what was understood. Sage extracts the pattern so future PRDs avoid the same mistake.

### 2. Agent Confusion

When an agent produces wrong artifacts or misunderstands requirements, that's a signal the handoff protocol failed. Sage analyzes what went wrong.

### 3. Test Failures (≥10 in session)

A few test failures are normal. Ten or more in one session? That's a pattern. Maybe the TDD was incomplete, or the implementation approach was flawed. Sage looks for the common thread.

### 4. Successful Deployment

This is the one people forget: **learn from success too**. When a feature ships cleanly, what went right? Sage extracts positive patterns for reinforcement.

The threshold of "≥10 test failures" was chosen deliberately. It's high enough to avoid noise (one flaky test isn't a pattern) but low enough to catch systemic issues early.

---

## Multi-Track Management: Juggling Features

Real work isn't sequential. You're working on customer analytics, then a production bug comes in, then the PM asks about that other feature.

The Supervisor handles this with **track management**:

```markdown
## Active Tracks

### Track: feat/customer-analytics (ACTIVE)
- Phase: ARCHITECTURE
- Status: In Progress

### Track: fix/null-handling (QUEUED)
- Priority: High (queued interrupt)
- Reason: Production bug
```

Key principle: **Never switch mid-phase**. If you're in the middle of implementing, the urgent bug goes in the queue and waits until implementation completes.

Why? Context switching mid-task is expensive. Half-done work is harder to resume than work you finished then moved away from.

---

## The Interface Layer Philosophy

The Supervisor embodies a specific philosophy: **clarify before delegating**.

Instead of:

```
User: "Add customer analytics"
Agent: *immediately starts writing code*
```

It's:

```
User: "Add customer analytics"
Supervisor: "Is this on the roadmap, or an ad-hoc request?"
Supervisor: "Does this need a full PRD, or is scope already clear?"
Supervisor: "Should we skip any phases?"
User: "It's on the roadmap, PRD exists already, full workflow"
Supervisor: "Starting architecture phase..."
```

These questions take 30 seconds but save hours of rework from misunderstanding scope.

---

## Architectural Diagram

Here's how the Supervisor relates to existing agents:

```
                    ┌─────────────────┐
                    │   SUPERVISOR    │  ← Interface + State + Verification
                    │    (super:)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │ /orchestrate│  │    Sage     │  │ Git-Master  │
    │ (assembly)  │  │ (learning)  │  │ (git ops)   │
    └──────┬──────┘  └─────────────┘  └─────────────┘
           │
    ┌──────┴──────┐
    │  PM → Arch  │
    │  → Dev → ...│
    └─────────────┘
```

The Supervisor sits above the assembly line but doesn't replace it. You can still:

- Use `pm:` directly for quick PRD work
- Use `arch:` directly for architecture questions
- Use `/orchestrate` directly for one-off features

The Supervisor adds value when you want **continuity, enforcement, and learning**.

---

## Key Learnings

### 1. State Files > Memory

Relying on conversation context for state is fragile. A markdown file (`WORKFLOW_STATE.md`) that the agent reads on session start is robust.

### 2. Verification > Trust

"Did you create the PRD?" is weaker than "Let me check if docs/specs/PRD-*.md exists." Active verification catches mistakes passive questions miss.

### 3. Queuing > Switching

When urgent work arrives, queue it rather than immediately switching. Context switches are expensive; queued work can be planned.

### 4. Learn from Both Failure and Success

Most learning systems focus on failure. But patterns that work should be extracted and reinforced too.

### 5. Clarify Before Delegating

Every minute spent on clarifying questions saves ten minutes of rework. The interface layer exists to ask the questions humans forget to.

---

## Applying This Beyond Agents

The Supervisor pattern isn't unique to AI agents. It applies anywhere you have:

- **Multiple specialized workers** (human or automated)
- **Multi-step processes** with handoffs
- **Quality requirements** that can't rely on honor system
- **Work that spans multiple sessions**

Examples:

- **DevOps pipelines**: A "supervisor" service that tracks deployments across stages, enforces gates, and learns from failures
- **Document review workflows**: Track where documents are in approval, verify required sections exist, queue revision requests
- **Sprint management**: Track features through planning → design → implementation → review, enforce definition of done

The meta-orchestration pattern is widely applicable.

---

## What's Next

The Supervisor is v1. Future enhancements might include:

- **Metrics dashboard**: How long do features spend in each phase?
- **Automated blocker detection**: If a track hasn't moved in 3 days, surface it
- **Cross-repository awareness**: Track work across multiple projects

But those are refinements. The core pattern - state + verification + learning + queuing - is solid.

---

## Related Reading

- [[../../.claude/agents/supervisor.md]] - Full persona definition
- [[../../.claude/agents/AGENTS.md]] - Agent orchestration guide
- [[../../.claude/agents/sage.md]] - Learning extraction patterns

---

*The best orchestration systems are invisible when they work. You only notice them when something goes wrong - and by then, they've already caught it.*
