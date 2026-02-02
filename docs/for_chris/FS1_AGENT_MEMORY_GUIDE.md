# Agent Memory Guide: Compound Learning in Practice

Welcome to the Agent Memory System! This guide will help you get the most out of session logging and pattern extraction. Think of it as your development journal that gets smarter over time.

---

## What is Agent Memory?

The Agent Memory System captures learnings from your development sessions and surfaces them when they're relevant. Instead of forgetting good ideas or repeating mistakes, the system builds institutional knowledge that compounds over time.

**The core idea**: Every session teaches something. Most of those lessons evaporate when you close your terminal. Agent Memory preserves them, finds patterns, and brings them back when you need them.

---

## Quick Start (5 minutes)

### 1. Log Your First Session

After completing any meaningful work:

```bash
uv run scripts/log-session.py -t "What you worked on"
```

That's it! Your session is now recorded in `memory/2026-02-02.md`.

### 2. Add More Detail (Optional)

For important sessions, add learnings:

```bash
uv run scripts/log-session.py -t "Built customer analytics" -o SUCCESS -i TASK-42
```

Flags:
- `-t "task"` - What you did (required for quick mode)
- `-o PARTIAL` - Outcome (SUCCESS, PARTIAL, FAILURE)
- `-i TASK-42` - Link to Backlog.md task

### 3. See Your Patterns

Run consolidation weekly (or whenever curious):

```bash
uv run scripts/consolidate-memory.py
```

This generates `memory/MEMORY_INDEX.md` with patterns and topics.

---

## Daily Workflow

### When to Log

Log sessions when:
- You finish a significant task
- You learn something you might forget
- You make a decision with rationale worth preserving
- Something fails and you figure out why

### Quick Logging (Most Common)

```bash
# After implementing a feature
uv run scripts/log-session.py -t "Implemented incremental model for orders"

# After debugging
uv run scripts/log-session.py -t "Fixed null handling in dim_customers" -o PARTIAL

# After hitting a wall
uv run scripts/log-session.py -t "Struggled with dbt_expectations syntax" -o FAILURE
```

### Full Logging (Important Sessions)

Run without flags for interactive mode:

```bash
uv run scripts/log-session.py
```

You'll be prompted for:
- Task description
- Outcome
- Decisions (with rationale)
- Learnings
- What you'd do differently
- Related issue/PR

**Tip**: The "What would you do differently?" prompt is the most valuable. It forces reflection.

### Using Sage Commands

If you prefer natural language:

```
sage: log session              # Full interactive
sage: log "Built customer mart" # Quick mode
sage: end session              # Review and log
```

---

## Weekly Workflow

### Running Consolidation

Once a week (Friday afternoon is great):

```bash
uv run scripts/consolidate-memory.py
```

### What You'll See

```
=== Memory Consolidation ===
Directory: /path/to/memory
Period: 7 days

Entries found: 12
Patterns detected: 2
Promotion candidates: 1

Promotion candidates for LEARNINGS.md:
  - Use incremental models for large tables

[OK] Written: memory/MEMORY_INDEX.md
```

### Reading MEMORY_INDEX.md

Open `memory/MEMORY_INDEX.md` to see:

1. **Weekly Summary** - Entries by day and outcome
2. **Recurring Patterns** - Ideas that came up 2+ times
3. **Topics Index** - What you worked on most
4. **Promotion Candidates** - Patterns worth adding to LEARNINGS.md

### Acting on Patterns

When a pattern is marked as CANDIDATE:

1. Review it - Is this actually a reusable insight?
2. If yes, manually add to `docs/reference/LEARNINGS.md`
3. If it's actionable (a process), create a skill file

The system suggests patterns but you decide what sticks.

---

## Tips & Tricks

### 1. Log Failures, Not Just Successes

Failed experiments are often more valuable than successes:

```bash
uv run scripts/log-session.py -t "Tried window functions, too slow" -o FAILURE
```

These appear in the "Failed Experiments" section of MEMORY_INDEX.md.

### 2. Use Task IDs for Correlation

If you're using Backlog.md, always add task IDs:

```bash
uv run scripts/log-session.py -t "Completed analytics mart" -i TASK-15
```

This enables metrics tracking across tasks (coming in FS5).

### 3. Keep Learnings Atomic

Instead of:
```
- Learned a lot about incremental models and testing patterns and dbt config
```

Write:
```
- Incremental models need unique_key for merge strategy
- dbt_expectations tests should use column-level thresholds
- DuckDB incremental differs from Snowflake
```

Each learning should be one searchable insight.

### 4. Preview Before Committing

Use dry-run to see what consolidation will find:

```bash
uv run scripts/consolidate-memory.py --dry-run
```

### 5. Search Your Memory

Find past decisions with grep:

```bash
grep -r "incremental" memory/*.md
grep -r "FAILURE" memory/*.md
```

---

## Troubleshooting

### "Could not find project root (CLAUDE.md)"

You're not in the dbt-playground directory. Navigate there first:

```bash
cd /path/to/dbt-playground
```

### No patterns detected after consolidation

You need 2+ similar learnings for pattern detection. Keep logging! After a week or two of regular logging, patterns will emerge.

### Task ID format warning

The expected format is `TASK-N` (e.g., TASK-42). Other formats work but generate a warning:

```
[WARN] Task ID 'issue-42' has unusual format
```

This is just a warning - your entry is still logged.

### Files not auto-detected

Auto-detection uses `git diff HEAD~1`. If you haven't committed recently, no files will be found. That's okay - files are optional.

---

## Examples from Real Sessions

### Example 1: Feature Implementation

```markdown
## [2026-02-02T14:30:00] Task: Built customer analytics mart

**Task ID**: TASK-15
**Outcome**: SUCCESS
**Files Modified**: 3 (models/marts/mart_customer_analytics.sql, ...)

**Key Decisions**:
- Used incremental model: Performance requirement of <5s refresh (affects: marts/)
- Chose surrogate key over natural: Enables SCD Type 2 later (affects: dimensions/)

**Learnings**:
- DuckDB incremental uses 'append' strategy by default, not merge
- Need explicit unique_key even for append strategy

**Would Do Differently**:
- Write tests before implementing (caught 2 bugs manually)

**Related**:
- Issue: #142 | PR: #145
```

### Example 2: Debugging Session

```markdown
## [2026-02-02T16:45:00] Task: Fixed null handling in dim_customers

**Outcome**: PARTIAL
**Files Modified**: 2

**Key Decisions**:
- Added coalesce for all optional fields: Defensive approach for unknown sources

**Learnings**:
- Synthea data has unexpected nulls in phone and email fields
- COALESCE should wrap all non-required fields at staging layer

**Would Do Differently**:
- Check source data quality before building dimensional models
```

### Example 3: Failed Experiment

```markdown
## [2026-02-02T10:00:00] Task: Tried window functions for running totals

**Outcome**: FAILURE
**Files Modified**: 1

**Key Decisions**:
- None (experiment abandoned)

**Learnings**:
- Window functions on 1M+ rows cause memory issues in DuckDB
- Need to pre-aggregate or use incremental approach

**Would Do Differently**:
- Test performance on realistic data volume before implementing
```

---

## How It All Connects

```
Daily Logging                    Weekly Consolidation
     |                                  |
     v                                  v
memory/2026-02-02.md  ------>  memory/MEMORY_INDEX.md
     |                                  |
     v                                  v
Session captured               Patterns identified
     |                                  |
     +----------------------------------+
                    |
                    v
            docs/reference/LEARNINGS.md
                    |
                    v
            Future sessions benefit
```

The compound loop:
1. You log sessions
2. Patterns emerge from repetition
3. Good patterns get promoted to LEARNINGS.md
4. Future sessions start with relevant context
5. You avoid repeating mistakes
6. Loop continues

---

## Command Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `log-session.py -t "task"` | Quick log | `-t "Built marts" -o SUCCESS` |
| `log-session.py` | Full interactive | All fields prompted |
| `consolidate-memory.py` | Weekly patterns | Default: 7 days |
| `consolidate-memory.py --dry-run` | Preview only | No files written |
| `consolidate-memory.py --days 14` | Custom range | Last 14 days |

---

## Next Steps

1. **Start logging today** - Even one entry is better than zero
2. **Make it a habit** - End each significant session with a log
3. **Review weekly** - Run consolidation to see patterns
4. **Promote the good stuff** - Move patterns to LEARNINGS.md

The system gets more valuable the more you use it. Your future self will thank you.

---

*Guide created for FS1: Agent Memory & Learning System*
*Questions? Ask Sage: `sage: help with memory logging`*
