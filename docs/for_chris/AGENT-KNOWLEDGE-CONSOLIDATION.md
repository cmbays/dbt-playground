# Agent Knowledge Consolidation

Understanding trade-offs in how we structure agent knowledge, with lessons from others who've tried different approaches.

## The Problem: Knowledge Fragmentation

Our current agent system has knowledge spread across many files:

```
.claude/
├── agents/       # 20+ persona files
├── skills/       # 23 skill files
├── commands/     # 16 command files
└── rules/        # 4 rule files
```

**Total potential context**: ~51,000 tokens if all were loaded.

This isn't necessarily bad! But it's worth understanding why this architecture emerged and when it might need to change.

## Case Study: Claudie's Evolution

A team building an AI project manager (Claudie) went through three architectural iterations. Their journey is instructive.

### v1: Massive Single File

**What they did**: One huge `CLAUDIE.md` file with everything - persona, workflows, tools, patterns.

**What happened**:

- ✅ Single source of truth
- ✅ Easy to find anything
- ❌ Context window overflow
- ❌ Loaded irrelevant content for every task
- ❌ Expensive per-query (paying for tokens not needed)

**Result**: Worked initially, but as the system grew, they hit context limits and performance issues.

### v2: Fragmented Files

**What they did**: Split into many specialized files (exactly what we have now).

```
docs/
├── personas/
├── workflows/
├── tools/
└── patterns/
```

**What happened**:

- ✅ Only load what's needed
- ✅ Clear separation of concerns
- ❌ "Amnesia" - agents forgot related context
- ❌ Inconsistent behavior across sessions
- ❌ Hard to maintain coherent system behavior

**Result**: Better efficiency, but agents lost the holistic understanding.

### v3: Tiered Handbook (Their Solution)

**What they did**: Consolidated into layered handbooks with a "foundation" always loaded.

```
HANDBOOK_FOUNDATION.md    # Always loaded (core rules, workflow)
HANDBOOK_ENGINEERING.md   # Loaded for code tasks
HANDBOOK_PM.md            # Loaded for PM tasks
personas/                 # Minimal persona deltas
```

**What happened**:

- ✅ Shared context always present
- ✅ Specialized knowledge on-demand
- ✅ Consistent behavior (foundation always loaded)
- ✅ Reduced token cost (no duplication)

**Key insight**: The "foundation" layer eliminated the amnesia problem by ensuring core patterns were always available.

**Additional insight for our project**: PM should create project management artifacts (PRDs, milestones, issues, tasks) that enable evaluation of team improvement over time. These artifacts provide the data needed to answer "are we getting better?" and identify patterns in what works vs. what doesn't.

## Our Current Architecture

We use v2 (fragmented files) with some v3 elements:

**v3-like elements we have**:

- `CLAUDE.md` as foundation (always loaded)
- `.claude/rules/` as shared rules (loaded by context)
- Cross-references between files

**v2 elements we have**:

- Many separate persona files
- Separate skill files
- Separate command files

### Why Our v2 Works (For Now)

1. **Project size**: We're still small enough that fragmentation isn't painful
2. **Clear persona boundaries**: Each agent has distinct responsibilities
3. **CLAUDE.md as glue**: Core context provides coherence
4. **Learning orientation**: We're learning dbt, not optimizing for production

### Signs It May Need to Change

Watch for these symptoms:

| Symptom | What It Means |
|---------|---------------|
| Agents forget established patterns | Foundation layer too thin |
| Duplicated content across files | Need consolidation |
| Inconsistent behavior | Missing shared context |
| Context overflow errors | Too much being loaded |
| "Which file has X?" confusion | Need better organization |

## Trade-offs: Fragmented vs. Consolidated

### Fragmented (Current)

**Pros**:

- Load only what's needed
- Easy to update single concern
- Clear ownership
- Lower per-query cost

**Cons**:

- Risk of inconsistency
- Cross-cutting concerns scattered
- May miss related context
- Harder to maintain coherence

### Consolidated

**Pros**:

- Consistent behavior
- All context available
- Easier to ensure coverage
- Single source of truth

**Cons**:

- Higher per-query cost
- May load irrelevant content
- Harder to update (affects everything)
- Risk of context overflow

### The Middle Ground (Tiered)

**Pros**:

- Foundation ensures consistency
- Layers add specialization
- Balanced token usage
- Clear loading rules

**Cons**:

- More complex architecture
- Need to maintain layer boundaries
- Migration effort

## When to Consolidate

Consider consolidation when:

1. **Agents lose context frequently** - They should know established patterns
2. **You're duplicating content** - Same pattern in multiple files
3. **Behavior is inconsistent** - Different sessions produce different styles
4. **Token budget allows** - You have room for larger foundation
5. **Patterns are stable** - Content won't change frequently

**Not yet time if**:

- Everything is working smoothly
- Project is still learning/experimenting phase
- Clear persona boundaries are working
- No duplication detected

## Potential Consolidation Strategy (v0.7+)

If we decide to consolidate, here's a potential approach:

### Step 1: Measure Current State

```bash
# Count tokens per file
wc -w .claude/agents/*.md .claude/skills/*.md
```

### Step 2: Identify Common Content

Look for repeated content across files:

- Shared coding standards
- Common workflow steps
- Repeated constraint lists
- Duplicated patterns

### Step 3: Design Tiered Structure

```
.claude/
  handbook/
    FOUNDATION.md      # Always loaded (core workflow, rules)
    DBT_LAYER.md       # dbt-specific operations
    REVIEW_LAYER.md    # Review and quality operations
    ORCHESTRATION.md   # Supervisor and coordination
  personas/            # Minimal persona deltas only
```

### Step 4: Migration

1. Extract common content to handbook layers
2. Reduce persona files to unique deltas
3. Update loading rules
4. Test consistency

### Step 5: Validate

- Verify consistent behavior across sessions
- Check token usage improvement
- Confirm no functionality lost

## Our Recommendation

**For now**: Stay with current architecture (v2 with v3 elements)

**Reasons**:

1. We're in learning phase - experimentation is good
2. No consolidation pain points yet
3. Clear persona boundaries working well
4. CLAUDE.md provides adequate foundation

**Revisit when**:

- We complete v1.0 milestone
- Agents start forgetting established patterns
- Maintenance burden increases
- Token usage becomes problematic

## Key Takeaways

1. **There's no perfect architecture** - Each has trade-offs
2. **Context window is the constraint** - All decisions flow from this
3. **Foundation layer is key** - Ensures consistency across agents
4. **Consolidate based on pain** - Don't optimize prematurely
5. **Measure before changing** - Know current token usage

## Related

- [Agent Job Descriptions](AGENT_JOB_DESCRIPTIONS.md) - What each agent does
- [Supervisor Orchestration](SUPERVISOR_ORCHESTRATION.md) - How agents coordinate
- [LEARNINGS.md](../reference/LEARNINGS.md) - Pattern: Context Window Discipline
- [PRD-016](../specs/PRD-016-AGENT-CONTEXT-MANAGEMENT.md) - Agent context management

---

*This document captures learnings for future architectural decisions. Revisit at v0.7+ milestone.*
