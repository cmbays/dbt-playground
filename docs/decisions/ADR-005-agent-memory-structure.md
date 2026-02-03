---
audience: [architect, pm, developer]
priority: high
size: small
dependencies: []
last_updated: 2026-02-02
status: approved
tags: [architecture, v0.10, agent-memory, fs1]
---

# ADR-005: Agent Memory Directory Structure

**Status**: Approved
**Date**: 2026-02-02
**Deciders**: Architect, PM
**Epic**: FS1 Agent Memory & Learning (#143)

## Context

v0.10 introduces an agent memory system (Epic #143) with two types of data:

1. **Session logs** - Detailed, per-developer debugging notes and decisions
2. **Consolidated patterns** - Promoted learnings that appeared 2+ times across sessions

We need to decide:
- Where to place the `memory/` directory (root vs `.claude/memory/`)
- What to track in git vs. ignore

## Decision

**Use root-level `memory/` directory with hybrid git tracking:**

```
dbt-playground/
├── memory/                      # Root level (not nested in .claude/)
│   ├── sessions/                # IGNORED (.gitignore)
│   ├── patterns/                # TRACKED (team learning)
│   ├── codebase/                # TRACKED (project context)
│   └── MEMORY_INDEX.md          # TRACKED (curated index)
├── .claude/                     # Agent configuration (separate)
├── dbt_project/
└── docs/
```

**Git tracking strategy:**
```gitignore
# Ignore private session logs
memory/sessions/

# Track promoted patterns (default behavior)
# memory/patterns/    - TRACKED
# memory/codebase/    - TRACKED
# memory/MEMORY_INDEX.md - TRACKED
```

## Options Considered

### Option 1: Root-level `memory/` (SELECTED)

**Pros:**
- ✅ Simpler `.gitignore` (sessions ignored, rest tracked by default)
- ✅ Shorter paths (`memory/patterns/` vs `.claude/memory/patterns/`)
- ✅ Better discoverability (visible in `ls`, easier to reference)
- ✅ Conceptual clarity: memory is **project knowledge**, not agent configuration
- ✅ Easier backup/migration (portable, not coupled to `.claude/`)
- ✅ Separation of concerns: config (`.claude/`) vs. state (`memory/`)

**Cons:**
- ❌ +1 root directory (minor clutter)
- ❌ Less obvious it's agent-related (mitigated by documentation)

### Option 2: Nested `.claude/memory/`

**Pros:**
- ✅ All agent-related stuff in one place
- ✅ Cleaner root directory

**Cons:**
- ❌ Complex `.gitignore` (must whitelist within ignored `.claude/*`)
- ❌ 20% longer paths (48 chars vs 40 chars)
- ❌ Reduced discoverability (hidden in `.claude/`)
- ❌ Conceptually conflates agent config with agent output
- ❌ Harder to backup/migrate separately

## Rationale

### 1. Memory is Data, Not Configuration

**Agent configuration** (static, defines behavior):
- `.claude/agents/supervisor.md` - How agents behave
- `.claude/commands/commit.md` - What agents can do
- `.claude/hooks/pre-commit.sh` - When agents act

**Memory** (dynamic, project knowledge):
- `memory/patterns/dbt-patterns.md` - What we learned
- `memory/codebase/key-models.md` - What this project does
- `memory/sessions/2026-02-02.md` - How we solved problems

Memory is the **output** of agents, not their **definition**. It belongs with other data/state.

### 2. Analogous to Other Tools

| Tool | Configuration | State/Data |
|------|--------------|------------|
| Git | `.git/config` | `.git/objects/` |
| npm | `.npmrc` | `node_modules/` |
| dbt | `dbt_project.yml` | `target/`, `logs/` |
| **Claude Code** | `.claude/agents/` | `memory/` |

State lives **outside** the config directory.

### 3. Existing .gitignore Pattern

Current `.gitignore` explicitly excludes memory from whitelisted config:

```gitignore
.claude/*                # Ignore ALL
!.claude/agents/         # Whitelist config
!.claude/skills/
...
.claude/memories/        # Explicitly ignore (redundant safety)
```

This shows the intent to **separate memory from agent config**, even if nested.

### 4. Team Discoverability

**Root-level:**
- "Check the `memory/` folder for patterns"
- New developers see it in `ls`
- Clear signal: "This is important project knowledge"

**Nested:**
- "Check `.claude/memory/patterns/`..." (developers skip .claude/)
- Hidden in tool internals
- Less likely to be referenced

## Consequences

### Positive

- ✅ **Simple implementation**: `.gitignore` already updated, works well
- ✅ **Team benefit**: Patterns visible and discoverable
- ✅ **Clear mental model**: Config vs. knowledge separation
- ✅ **Future flexibility**: Easy to backup, share, or migrate patterns

### Negative

- ⚠️ **Root directory count**: +1 top-level directory (acceptable for importance)
- ⚠️ **Requires documentation**: Must explain in CLAUDE.md what `memory/` is

### Neutral

- Memory could move to `.claude/` in the future if organizational needs change
- Decision is reversible with `git mv memory/ .claude/memory/`

## Implementation Notes

### Epic #143 Issues

| Issue | Task | Impact on Directory Structure |
|-------|------|-------------------------------|
| #150 | Create memory/ structure | Implements root-level directory |
| #151 | Session logging (Sage J) | Writes to `memory/sessions/YYYY-MM-DD.md` |
| #153 | Weekly consolidation (Sage K) | Promotes to `memory/patterns/*.md` |
| #163 | Compound learning loop | Reads from `memory/patterns/` at session start |

### File Organization

```
memory/
├── sessions/                    # Private (ignored)
│   ├── 2026-02-02.md           # Daily append-only logs
│   ├── 2026-02-01.md
│   └── .gitkeep                # Track directory structure
│
├── patterns/                    # Tracked (team learning)
│   ├── dbt-patterns.md         # dbt-specific learnings
│   ├── workflow-insights.md    # Process improvements
│   ├── architecture-decisions.md # Design patterns
│   └── troubleshooting.md      # Common issues + solutions
│
├── codebase/                    # Tracked (project context)
│   ├── key-models.md           # Critical models to understand
│   ├── data-quality-rules.md   # DQ thresholds and patterns
│   └── testing-strategy.md     # Test coverage guidelines
│
└── MEMORY_INDEX.md             # Tracked (curated TOC)
```

### Workflow Integration

**Daily (Sage Workflow J - Issue #151):**
```markdown
# memory/sessions/2026-02-02.md
## 14:30 - Add fct_customer_metrics
- Debugged DuckDB window function null handling (30 min)
- Learning: Always use NULLS LAST in ORDER BY
```

**Weekly (Sage Workflow K - Issue #153):**
```markdown
# Sage detects pattern (3 occurrences)
# Creates PR promoting to memory/patterns/dbt-patterns.md:

## DuckDB Window Functions Require NULLS LAST
**Frequency**: 3 sessions
**Solution**: ORDER BY date DESC NULLS LAST
```

**Session Start (Issue #163):**
```markdown
# Agent reads memory/MEMORY_INDEX.md
# Surfaces relevant patterns based on task type
# "Working on dbt models? See memory/patterns/dbt-patterns.md"
```

## Related Decisions

- **ADR-2**: Three-layer model architecture (project structure precedent)
- **ADR-8**: Inter-agent report pattern (temp/AGENT_REPORTS/ for ephemeral)
- **ADR-9**: Backlog.md for task management (git-tracked state)

## References

- [v0.10 Roadmap](../specs/ROADMAP-v0.10.md)
- [PM Report](../../temp/AGENT_REPORTS/v0.10-planning/PM_REPORT.md)
- [Memory Structure Proposal](../../temp/AGENT_REPORTS/v0.10-planning/MEMORY_STRUCTURE_PROPOSAL.md)
- [Epic #143: Agent Memory & Learning](https://github.com/cmbays/dbt-playground/issues/143)

---

**Approved by**: Architect, PM
**Implementation**: v0.10 FS1 (Epic #143, Issues #150-153, #163)
