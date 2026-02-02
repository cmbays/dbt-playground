# Context Checkpoint

**Purpose**: Capture and preserve project context at milestone boundaries, agent handoffs, and critical decision points to prevent context loss during multi-agent workflows and long sessions.

**Owner**: Sage persona

**Invocation**: `sage: checkpoint`, before/after agent handoffs, at milestone boundaries

---

## When to Use

- Before handing off to a different persona (e.g., PM → Architect → Developer)
- After a major decision that future agents need to know about
- At milestone boundaries (version transitions, feature completion)
- When a long session risks losing detail to context compaction
- Before launching multiple parallel agents

**Do NOT use for**:

- Simple single-agent tasks
- Quick fixes or typo corrections
- When context is already well-documented in PRDs/TDDs

---

## Prerequisites

**Required inputs**:

- Understanding of current session state
- Knowledge of what work is in progress or just completed
- Awareness of upcoming agent handoffs or next steps

---

## Process

### Step 1: Assess Current State

**Actions**:

1. Identify the current task and its progress
2. List recent decisions and their rationale
3. Note active blockers or dependencies
4. Check for unresolved questions

---

### Step 2: Write Checkpoint File

**File naming**: `temp/CONTEXT_CHECKPOINT_[YYYY-MM-DD]_[label].md`

**Label examples**: `pre-architect`, `post-kanji-filter`, `milestone-v0.3`, `mid-session`

**Template**:

```markdown
# Context Checkpoint: [Label]

**Date**: YYYY-MM-DD
**Session Phase**: [What was just completed / what's about to start]

---

## Current Task

[1-2 sentences: What is being worked on right now]

## Recent Decisions

- **[Decision]**: [Rationale] (affects: [files/components])
- **[Decision]**: [Rationale] (affects: [files/components])

## Active Blockers

- [Blocker description and what's needed to resolve]

## Work in Progress

| Item | Status | Owner/Persona | Key Files |
|------|--------|---------------|-----------|
| [Task] | [in-progress/blocked/ready] | [persona] | [files] |

## Integration Points

- [Component A] depends on [Component B] via [interface/file]

## Open Questions

- [Question that needs answering before proceeding]

## Next Steps

1. [Immediate next action]
2. [Following action]
3. [Persona recommendation]: [Why this persona should go next]
```

---

### Step 3: Prepare Agent Briefing (Optional)

When the checkpoint is specifically for an agent handoff, create a condensed briefing section at the top of the checkpoint:

**Quick Briefing (<500 tokens)**:

```markdown
## Agent Briefing: [Target Persona]

**Task**: [What this agent needs to do]
**Context**: [Key facts they need to know]
**Decisions already made**: [Don't re-decide these]
**Constraints**: [Boundaries to respect]
**Key files**: [Where to start]
```

---

### Step 4: Prune Old Checkpoints

- Keep the **3 most recent** checkpoints in `temp/`
- Older checkpoints can be deleted (their value is captured in learning digests and LEARNINGS.md)
- Ask for approval before deleting if any checkpoint is <7 days old

---

## Expected Outcomes

**Primary output**: `temp/CONTEXT_CHECKPOINT_[date]_[label].md`

**Quality indicators**:

- Checkpoint is self-contained (readable without prior context)
- Decisions include rationale (not just what, but why)
- Next steps are actionable
- Key files are referenced for quick navigation

---

## Examples

### Example 1: Pre-Architect Handoff

**Invocation**: `sage: checkpoint before switching to architect for spaced repetition design`

**Output**: `temp/CONTEXT_CHECKPOINT_2026-01-27_pre-architect.md`

```markdown
# Context Checkpoint: Pre-Architect

**Date**: 2026-01-27
**Session Phase**: PM completed PRD, handing off to Architect

## Current Task
Design spaced repetition system for kanji study module.

## Recent Decisions
- **Algorithm**: Use SM-2 variant (simpler than SM-5, proven effective) (affects: kanji/js/)
- **Storage**: localStorage for MVP, consider backend later (affects: kanji/js/progress.js)

## Active Blockers
- None

## Work in Progress
| Item | Status | Owner | Key Files |
|------|--------|-------|-----------|
| PRD complete | done | PM | docs/specs/PRD-spaced-repetition.md |
| TDD needed | ready | Architect | docs/specs/TDD-spaced-repetition.md |

## Next Steps
1. Architect: Design data model and algorithm integration
2. Architect: Define localStorage schema
3. Developer: Implement after TDD approval
```

### Example 2: Milestone Checkpoint

**Invocation**: `sage: checkpoint — milestone v0.3 complete`

**Output**: `temp/CONTEXT_CHECKPOINT_2026-01-27_milestone-v0.3.md`

```markdown
# Context Checkpoint: Milestone v0.3

**Date**: 2026-01-27
**Session Phase**: v0.3 complete, planning v0.4

## Current Task
v0.3 shipped. Shopping dialogue page complete with audio.

## Recent Decisions
- **Audio format**: MP3 128kbps (broad compatibility) (affects: topics/*/audio/)
- **Dialogue structure**: JSON data files separate from HTML (affects: all dialogue pages)

## Work in Progress
| Item | Status | Owner | Key Files |
|------|--------|-------|-----------|
| v0.3 tagged | done | Git-Master | v0.3.0 |
| CHANGELOG updated | done | Documenter | CHANGELOG.md |
| Learnings curated | pending | Sage | temp/SESSION-*.md |

## Next Steps
1. Sage: Curate v0.3 learnings
2. PM: Plan v0.4 scope
3. Tag creation confirmed
```

---

## Checklist

Before completing this skill:

- [ ] Current state accurately captured
- [ ] Decisions include rationale
- [ ] Blockers and open questions documented
- [ ] Next steps are actionable with persona recommendations
- [ ] Key files referenced
- [ ] Old checkpoints pruned (keep 3 most recent)

---

## See Also

- `.claude/agents/sage.md` - Sage persona (context management section)
- `.claude/skills/learning-curation.md` - Session learning curation
- `.claude/skills/continuous-learning.md` - Pattern extraction
- `docs/reference/LEARNINGS.md` - Technical patterns repository
