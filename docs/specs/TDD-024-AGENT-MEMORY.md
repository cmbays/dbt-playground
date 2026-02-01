# TDD: Agent Memory & Learning System

**TDD ID**: TDD-XXX (to be assigned)
**Date**: 2026-02-01
**Author**: Technical Architect
**Status**: Draft
**PRD Reference**: PRD-XXX (Agent Memory & Learning System)

---

## 1. Architecture Overview

### Design Philosophy

This system extends the existing Sage-based learning infrastructure with minimal additions. The architecture prioritizes:

1. **Simplicity**: File-based storage, no database
2. **Integration**: Build on existing Sage workflows
3. **Reversibility**: Easy to disable or remove if not valuable
4. **Git-native**: All artifacts tracked in version control

### System Context Diagram

```
+------------------+     +------------------+     +------------------+
|   Developer      |     |   Supervisor     |     |   Sage Agent     |
|   Session        |     |   Agent          |     |                  |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         | Work session           | Phase transitions      | Learning extraction
         |                        |                        |
         v                        v                        v
+--------+------------------------+------------------------+---------+
|                                                                    |
|                         Memory System                              |
|                                                                    |
|  +----------------+  +------------------+  +-------------------+   |
|  | memory/        |  | Sage Workflows   |  | Integration       |   |
|  | YYYY-MM-DD.md  |  | J: Log Session   |  | Points            |   |
|  | MEMORY_INDEX   |  | K: Consolidate   |  | - Session start   |   |
|  +----------------+  +------------------+  | - Session end     |   |
|                                           | - Threshold detect |   |
|                                           +-------------------+   |
|                                                                    |
+--------------------------------------------------------------------+
         |                        |                        |
         v                        v                        v
+--------+---------+     +--------+---------+     +--------+---------+
| LEARNINGS.md     |     | .claude/skills/  |     | WORKFLOW_STATE   |
| (pattern target) |     | (skill target)   |     | (tracking)       |
+------------------+     +------------------+     +------------------+
```

### Component Overview

| Component | Type | Purpose |
|-----------|------|---------|
| `memory/` | Directory | Daily append-only log storage |
| `memory/YYYY-MM-DD.md` | File | Daily session log |
| `memory/MEMORY_INDEX.md` | File | Weekly summary and pattern index |
| Sage Workflow J | Agent workflow | Session logging command |
| Sage Workflow K | Agent workflow | Weekly consolidation |
| `scripts/log-session.py` | Script | CLI logging tool |
| Supervisor integration | Enhancement | Session triggers |
| Session context loader | Function | Bootstrap relevant learnings |

---

## 2. Component Design

### 2.1 Memory Directory Structure

```
dbt-playground/
  |
  +-- memory/                        # NEW: Session memory storage
  |     |
  |     +-- 2026-02-01.md           # Daily log file
  |     +-- 2026-02-02.md           # Each day gets new file
  |     +-- 2026-02-03.md
  |     +-- ...
  |     +-- MEMORY_INDEX.md         # Weekly summary (regenerated)
  |     +-- .gitkeep                # Ensure directory exists in git
  |
  +-- docs/reference/LEARNINGS.md   # EXISTING: Pattern promotion target
  +-- .claude/agents/sage.md        # EXISTING: Extended with new workflows
  +-- .claude/skills/               # EXISTING: Skill extraction target
  +-- temp/WORKFLOW_STATE.md        # EXISTING: Add memory tracking
```

**Directory rules**:

- `memory/` is git-tracked (not in .gitignore)
- Daily files are append-only within the day
- MEMORY_INDEX.md is regenerated (not appended)
- Archive policy: Move logs >90 days to `archive/memory/`

### 2.2 Log Entry Data Structure

#### Markdown Format

```markdown
## [2026-02-01T14:30:00] Task: Implement customer analytics mart

**Outcome**: SUCCESS
**Files Modified**: 5 (models/marts/customer_analytics.sql, ...)

**Key Decisions**:
- Use incremental model: Performance requirement of <5s refresh (affects: marts/)
- Add surrogate key: Consistency with dim_* pattern (affects: customer_analytics.sql)

**Learnings**:
- Incremental models require unique_key configuration for merge strategy
- DuckDB handles incremental differently than Snowflake

**Would Do Differently**:
- Start with test coverage before implementing model logic

**Related**:
- Issue: #142
- PR: #145

---
```

#### JSON Schema (for script validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["timestamp", "task", "outcome"],
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "task": {
      "type": "string",
      "maxLength": 200
    },
    "outcome": {
      "type": "string",
      "enum": ["SUCCESS", "FAILURE", "PARTIAL"]
    },
    "files_modified": {
      "type": "integer",
      "minimum": 0
    },
    "files_list": {
      "type": "array",
      "items": { "type": "string" }
    },
    "decisions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "decision": { "type": "string" },
          "rationale": { "type": "string" },
          "affects": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "learnings": {
      "type": "array",
      "items": { "type": "string" }
    },
    "would_do_differently": {
      "type": "array",
      "items": { "type": "string" }
    },
    "related": {
      "type": "object",
      "properties": {
        "issue": { "type": "string" },
        "pr": { "type": "string" }
      }
    }
  }
}
```

### 2.3 MEMORY_INDEX.md Structure

```markdown
# Memory Index

**Generated**: 2026-02-07T00:00:00
**Period**: 2026-02-01 to 2026-02-07
**Total Entries**: 15

---

## Weekly Summary

| Day | Entries | Outcomes | Top Topics |
|-----|---------|----------|------------|
| Mon | 3 | 2 SUCCESS, 1 PARTIAL | marts, testing |
| Tue | 2 | 2 SUCCESS | staging, sources |
| Wed | 4 | 3 SUCCESS, 1 FAILURE | macros, incremental |
| Thu | 3 | 3 SUCCESS | documentation |
| Fri | 3 | 2 SUCCESS, 1 PARTIAL | deployment, ci |

---

## Recurring Patterns (2+ occurrences)

### Pattern: Incremental Model Configuration
**Occurrences**: 3 (Mon, Wed, Wed)
**Summary**: unique_key required for proper merge behavior
**Promotion Status**: CANDIDATE for LEARNINGS.md

### Pattern: Test-First Development
**Occurrences**: 2 (Mon, Thu)
**Summary**: "Would do differently" entries mention test coverage
**Promotion Status**: REVIEW - reinforces existing pattern

---

## Topics Index

| Topic | Count | Days |
|-------|-------|------|
| marts | 5 | Mon, Tue, Wed |
| testing | 4 | Mon, Thu, Fri |
| macros | 3 | Wed |
| staging | 2 | Tue |

---

## Failed Experiments

| Day | Task | Failure Reason | Learning |
|-----|------|----------------|----------|
| Wed | Macro for audit columns | Jinja parsing error | Escape braces in macros |

---

## Related Issues/PRs

| Type | Number | Tasks |
|------|--------|-------|
| Issue | #142 | Customer analytics (Mon) |
| Issue | #145 | Incremental testing (Wed) |
| PR | #147 | Marts deployment (Fri) |
```

### 2.4 Sage Workflow J: Session Logging

**Addition to `.claude/agents/sage.md`**:

```markdown
### Workflow J: Session Logging

```

Trigger: Manual invocation `sage: log session` or `sage: log "[task]"`
Input: Session context, modified files, user input

Process:

1. Determine today's log file: memory/YYYY-MM-DD.md
2. If quick log (`sage: log "[task]"`):
   - Auto-fill timestamp, outcome=SUCCESS, files from git status
   - Prompt only for decisions and learnings
3. If full log (`sage: log session`):
   - Interactive prompts for all fields
   - Suggest decisions based on recent commits
4. Validate entry format against schema
5. Append entry to daily log file
6. Confirm entry written

Output: Entry appended to memory/YYYY-MM-DD.md

```

**Example invocations**:

```text
sage: log session
sage: log "Implemented customer analytics mart"
sage: log "Fixed incremental model bug" --outcome PARTIAL
```

**Interactive prompt flow**:

```
sage: log session

[Sage] Starting session log entry...

Task description: [user input or suggest from recent commits]
Outcome (SUCCESS/FAILURE/PARTIAL): [user input, default SUCCESS]
Files modified: [auto-detect from git status, confirm]

Key decisions made this session:
1. [user input]
2. [user input or 'done']

What did you learn?
1. [user input]
2. [user input or 'done']

What would you do differently?
1. [user input or 'none']

Related issue/PR: [user input or 'none']

[Sage] Entry logged to memory/2026-02-01.md
```

### 2.5 Sage Workflow K: Weekly Consolidation

**Addition to `.claude/agents/sage.md`**:

```markdown
### Workflow K: Weekly Consolidation

```

Trigger: Manual invocation `sage: consolidate week` or automated weekly
Input: memory/*.md files from past 7 days

Process:

1. Scan memory/ for files in date range
2. Parse all entries into structured data
3. Identify patterns:
   - Same decision rationale appearing 2+ times
   - Same learning appearing 2+ times
   - Same "would do differently" appearing 2+ times
4. Generate MEMORY_INDEX.md:
   - Weekly summary table
   - Recurring patterns section
   - Topics index
   - Failed experiments summary
5. For each promotion candidate:
   - Check if pattern already in LEARNINGS.md
   - If not, add to "Promotion Candidates" section
6. Report findings to user

Output: Updated memory/MEMORY_INDEX.md, promotion candidates listed

```

**Pattern detection algorithm** (simple text matching):

```python
def find_recurring_patterns(entries: list[Entry]) -> list[Pattern]:
    """Identify patterns appearing 2+ times across entries."""

    # Extract all learnings, decisions, would-do-differently
    all_items = []
    for entry in entries:
        all_items.extend([(entry.date, 'learning', l) for l in entry.learnings])
        all_items.extend([(entry.date, 'decision', d.rationale) for d in entry.decisions])
        all_items.extend([(entry.date, 'improve', w) for w in entry.would_do_differently])

    # Simple fuzzy grouping (keyword overlap > 50%)
    patterns = []
    used = set()

    for i, (date1, type1, text1) in enumerate(all_items):
        if i in used:
            continue

        similar = [(date1, text1)]
        for j, (date2, type2, text2) in enumerate(all_items[i+1:], i+1):
            if j in used or type2 != type1:
                continue
            if keyword_overlap(text1, text2) > 0.5:
                similar.append((date2, text2))
                used.add(j)

        if len(similar) >= 2:
            patterns.append(Pattern(
                type=type1,
                occurrences=similar,
                count=len(similar),
                summary=summarize_pattern(similar)
            ))

    return patterns
```

### 2.6 Session Logging Script

**File**: `scripts/log-session.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Session logging script for Agent Memory System.

Usage:
    uv run scripts/log-session.py                    # Interactive mode
    uv run scripts/log-session.py --task "Task"      # Quick mode
    uv run scripts/log-session.py --help             # Show help
"""

import argparse
import subprocess
from datetime import datetime
from pathlib import Path


def get_memory_dir() -> Path:
    """Get memory directory path, creating if needed."""
    # Find project root (directory containing CLAUDE.md)
    cwd = Path.cwd()
    while cwd != cwd.parent:
        if (cwd / 'CLAUDE.md').exists():
            memory_dir = cwd / 'memory'
            memory_dir.mkdir(exist_ok=True)
            return memory_dir
        cwd = cwd.parent
    raise FileNotFoundError("Could not find project root (CLAUDE.md)")


def get_today_log() -> Path:
    """Get path to today's log file."""
    memory_dir = get_memory_dir()
    today = datetime.now().strftime('%Y-%m-%d')
    return memory_dir / f'{today}.md'


def get_modified_files() -> list[str]:
    """Get list of modified files from git status."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1'],
            capture_output=True, text=True
        )
        return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except Exception:
        return []


def prompt_input(prompt: str, default: str = '') -> str:
    """Prompt for input with optional default."""
    if default:
        value = input(f'{prompt} [{default}]: ').strip()
        return value if value else default
    return input(f'{prompt}: ').strip()


def prompt_list(prompt: str) -> list[str]:
    """Prompt for a list of items."""
    print(f'{prompt} (enter empty line when done):')
    items = []
    while True:
        item = input(f'  {len(items) + 1}. ').strip()
        if not item:
            break
        items.append(item)
    return items


def format_entry(
    task: str,
    outcome: str,
    files: list[str],
    decisions: list[tuple[str, str, str]],
    learnings: list[str],
    improvements: list[str],
    issue: str,
    pr: str
) -> str:
    """Format a memory log entry as markdown."""
    timestamp = datetime.now().isoformat(timespec='seconds')

    lines = [
        f'## [{timestamp}] Task: {task}',
        '',
        f'**Outcome**: {outcome}',
    ]

    if files:
        if len(files) <= 5:
            lines.append(f'**Files Modified**: {len(files)} ({", ".join(files)})')
        else:
            lines.append(f'**Files Modified**: {len(files)}')

    lines.append('')
    lines.append('**Key Decisions**:')
    if decisions:
        for decision, rationale, affects in decisions:
            lines.append(f'- {decision}: {rationale} (affects: {affects})')
    else:
        lines.append('- None documented')

    lines.append('')
    lines.append('**Learnings**:')
    if learnings:
        for learning in learnings:
            lines.append(f'- {learning}')
    else:
        lines.append('- None documented')

    lines.append('')
    lines.append('**Would Do Differently**:')
    if improvements:
        for improvement in improvements:
            lines.append(f'- {improvement}')
    else:
        lines.append('- Nothing noted')

    lines.append('')
    lines.append('**Related**:')
    related_parts = []
    if issue:
        related_parts.append(f'Issue: #{issue}')
    if pr:
        related_parts.append(f'PR: #{pr}')
    if related_parts:
        lines.append(f'- {" | ".join(related_parts)}')
    else:
        lines.append('- None')

    lines.append('')
    lines.append('---')
    lines.append('')

    return '\n'.join(lines)


def interactive_mode() -> str:
    """Collect entry data interactively."""
    print('\n=== Session Log Entry ===\n')

    task = prompt_input('Task description')
    outcome = prompt_input('Outcome', 'SUCCESS').upper()
    if outcome not in ['SUCCESS', 'FAILURE', 'PARTIAL']:
        outcome = 'SUCCESS'

    files = get_modified_files()
    if files:
        print(f'\nDetected {len(files)} modified files:')
        for f in files[:5]:
            print(f'  - {f}')
        if len(files) > 5:
            print(f'  ... and {len(files) - 5} more')
        if input('Use these files? [Y/n]: ').strip().lower() == 'n':
            files = []

    print()
    decisions = []
    print('Key decisions (format: decision | rationale | affects):')
    while True:
        decision_input = input(f'  {len(decisions) + 1}. ').strip()
        if not decision_input:
            break
        parts = [p.strip() for p in decision_input.split('|')]
        if len(parts) >= 2:
            decision = parts[0]
            rationale = parts[1]
            affects = parts[2] if len(parts) > 2 else 'unspecified'
            decisions.append((decision, rationale, affects))
        else:
            decisions.append((decision_input, 'No rationale provided', 'unspecified'))

    learnings = prompt_list('\nLearnings')
    improvements = prompt_list('\nWould do differently')

    issue = prompt_input('\nRelated issue number (or empty)')
    pr = prompt_input('Related PR number (or empty)')

    return format_entry(task, outcome, files, decisions, learnings, improvements, issue, pr)


def quick_mode(task: str, outcome: str = 'SUCCESS') -> str:
    """Generate entry with minimal prompts."""
    files = get_modified_files()
    return format_entry(
        task=task,
        outcome=outcome,
        files=files,
        decisions=[],
        learnings=[],
        improvements=[],
        issue='',
        pr=''
    )


def main():
    parser = argparse.ArgumentParser(description='Log session entry to memory')
    parser.add_argument('--task', '-t', help='Task description (quick mode)')
    parser.add_argument('--outcome', '-o', default='SUCCESS',
                       choices=['SUCCESS', 'FAILURE', 'PARTIAL'],
                       help='Task outcome')
    args = parser.parse_args()

    if args.task:
        entry = quick_mode(args.task, args.outcome)
    else:
        entry = interactive_mode()

    log_file = get_today_log()

    # Append to file
    with open(log_file, 'a') as f:
        f.write(entry)

    print(f'\n✓ Entry logged to {log_file}')


if __name__ == '__main__':
    main()
```

### 2.7 Supervisor Integration Points

**Enhancements to Supervisor agent for session triggers**:

```markdown
## Session End Detection (Enhancement to supervisor.md)

### Trigger Points

1. **Explicit End Statement**
   - User says: "ending session", "done for today", "wrapping up"
   - Response: "Would you like to capture session learnings? (sage: log session)"

2. **Milestone Completion**
   - After version tag created
   - After PR merged
   - Response: Prompt for session/milestone learning capture

3. **Threshold Detection**
   - Condition: >5 files modified since session start
   - OR: >50 lines changed in dbt/Python files
   - Response: Soft suggestion at next natural pause

### Detection Logic

```python
def check_session_logging_needed() -> bool:
    """Check if session warrants logging prompt."""

    # Check for explicit session end
    if user_intent_is_session_end():
        return True

    # Check for milestone
    if recent_version_tag() or recent_pr_merge():
        return True

    # Check thresholds
    files_changed = count_modified_files_since_session_start()
    lines_changed = count_lines_changed_since_session_start()

    if files_changed > 5 or lines_changed > 50:
        return True

    return False
```

### Non-Intrusive Prompting

Prompts should:

- Appear at natural pauses (after task completion, not mid-work)
- Be dismissible with single word ("skip", "later", "no")
- Not repeat within same session after dismissal
- Include quick-log option for minimal effort

```

### 2.8 Session Context Loader

**Function for loading relevant context at session start**:

```python
def load_session_context(task_description: str | None = None, days: int = 7) -> str:
    """
    Load relevant learnings from memory for session start.

    Args:
        task_description: Optional task context for relevance filtering
        days: Number of days to look back (default 7)

    Returns:
        Formatted context string for display
    """
    memory_dir = get_memory_dir()

    # Get recent log files
    cutoff = datetime.now() - timedelta(days=days)
    log_files = sorted(memory_dir.glob('????-??-??.md'))
    recent_files = [f for f in log_files if parse_date(f.stem) >= cutoff.date()]

    if not recent_files:
        return "No recent memory entries found."

    # Parse all entries
    entries = []
    for log_file in recent_files:
        entries.extend(parse_log_file(log_file))

    # Filter by relevance if task provided
    if task_description:
        task_keywords = extract_keywords(task_description)
        entries = [e for e in entries if keyword_overlap(e.keywords, task_keywords) > 0.2]

    # Sort by relevance and recency
    entries.sort(key=lambda e: (e.relevance_score, e.timestamp), reverse=True)

    # Take top 5
    top_entries = entries[:5]

    if not top_entries:
        return "No relevant learnings found for this task."

    # Format output
    lines = [
        "## Recent Context",
        "",
        f"Found {len(top_entries)} relevant entries from past {days} days:",
        ""
    ]

    for entry in top_entries:
        lines.append(f"### {entry.date}: {entry.task}")
        lines.append(f"**Outcome**: {entry.outcome}")
        if entry.learnings:
            lines.append("**Learnings**:")
            for learning in entry.learnings[:3]:  # Limit to 3
                lines.append(f"- {learning}")
        lines.append("")

    return '\n'.join(lines)
```

---

## 3. Data Structures

### 3.1 Memory Entry (Parsed)

```python
@dataclass
class MemoryEntry:
    """Parsed memory log entry."""
    timestamp: datetime
    task: str
    outcome: Literal['SUCCESS', 'FAILURE', 'PARTIAL']
    files_modified: int
    files_list: list[str]
    decisions: list[Decision]
    learnings: list[str]
    would_do_differently: list[str]
    related_issue: str | None
    related_pr: str | None

    # Computed
    date: date  # Extract from timestamp
    keywords: set[str]  # Extract from task + learnings
    relevance_score: float  # Set during filtering


@dataclass
class Decision:
    """A key decision with rationale."""
    decision: str
    rationale: str
    affects: list[str]
```

### 3.2 Pattern (Identified)

```python
@dataclass
class Pattern:
    """A recurring pattern identified during consolidation."""
    type: Literal['learning', 'decision', 'improvement']
    occurrences: list[tuple[date, str]]  # (date, text) pairs
    count: int
    summary: str
    promotion_status: Literal['CANDIDATE', 'REVIEW', 'EXISTS', 'REJECTED']
```

### 3.3 Memory Index

```python
@dataclass
class MemoryIndex:
    """Weekly memory index structure."""
    generated: datetime
    period_start: date
    period_end: date
    total_entries: int

    daily_summary: list[DailySummary]
    recurring_patterns: list[Pattern]
    topics_index: dict[str, TopicEntry]
    failed_experiments: list[FailedExperiment]
    related_items: list[RelatedItem]


@dataclass
class DailySummary:
    day: date
    day_name: str
    entry_count: int
    outcomes: dict[str, int]  # {'SUCCESS': 2, 'FAILURE': 1}
    top_topics: list[str]
```

---

## 4. Integration Points with Existing Sage Agent

### 4.1 New Workflows Summary

| Workflow | Trigger | Input | Output |
|----------|---------|-------|--------|
| J: Session Logging | `sage: log session` | User input, git state | memory/YYYY-MM-DD.md entry |
| K: Weekly Consolidation | `sage: consolidate week` | memory/*.md (7 days) | MEMORY_INDEX.md, promotion candidates |

### 4.2 Sage Agent File Modifications

**File**: `.claude/agents/sage.md`

**Additions**:

1. Workflow J definition (section 2.4)
2. Workflow K definition (section 2.5)
3. Update trigger conditions table
4. Update artifacts produced table

**Example trigger conditions update**:

```markdown
### Sage Trigger Conditions (Updated)

Sage extracts learnings when:

| Trigger | Condition | Automatic? |
|---------|-----------|------------|
| User request | `sage: log session` | Manual |
| User request | `sage: consolidate week` | Manual |
| Session end | Supervisor detects end | Semi-auto |
| ... (existing triggers) | ... | ... |
```

### 4.3 Existing Workflow Compatibility

The new workflows are **additive** and do not modify existing Sage workflows:

| Existing Workflow | Impact |
|-------------------|--------|
| A: Session Learning Curation | Unchanged - can still use temp/SESSION-*.md |
| B: Bug Learning Extraction | Unchanged |
| C: Pattern Discovery | Unchanged - but K can feed candidates |
| D: Milestone Learning Documentation | Unchanged |
| E: Context Checkpoint | Unchanged |
| F: Agent Briefing Preparation | Unchanged - can use memory/ as source |
| G: PR Learning Extraction | Unchanged |
| H: ADR Pattern Promotion Review | Unchanged |
| I: Gap Resolution Research | Unchanged |

### 4.4 Cross-Workflow Integration

```
Session Work
     |
     v
[Workflow J: Log Session] --> memory/YYYY-MM-DD.md
     |
     v (weekly)
[Workflow K: Consolidate] --> MEMORY_INDEX.md
     |                             |
     +-- Promotion candidates -----+
     |
     v
[Workflow C: Pattern Discovery] <-- feeds from MEMORY_INDEX patterns
     |
     v
LEARNINGS.md (if pattern meets quality bar)
```

---

## 5. Implementation Sequence

### Phase 1: Foundation (Week 1, Days 1-3)

| Task | Deliverable | Depends On |
|------|-------------|------------|
| 1.1 | Create `memory/` directory with .gitkeep | None |
| 1.2 | Create log entry format template | 1.1 |
| 1.3 | Implement `scripts/log-session.py` | 1.2 |
| 1.4 | Add Sage Workflow J to `sage.md` | 1.2 |
| 1.5 | Test logging via script and Sage | 1.3, 1.4 |
| 1.6 | Document in CLAUDE.md | 1.5 |

### Phase 2: Triggers (Week 1, Days 4-5)

| Task | Deliverable | Depends On |
|------|-------------|------------|
| 2.1 | Add session end detection to Supervisor | Phase 1 |
| 2.2 | Add threshold detection logic | Phase 1 |
| 2.3 | Implement non-intrusive prompting | 2.1, 2.2 |
| 2.4 | Test trigger scenarios | 2.3 |

### Phase 3: Consolidation (Week 2, Days 1-3)

| Task | Deliverable | Depends On |
|------|-------------|------------|
| 3.1 | Implement log file parser | Phase 1 |
| 3.2 | Implement pattern detection algorithm | 3.1 |
| 3.3 | Implement MEMORY_INDEX.md generator | 3.2 |
| 3.4 | Add Sage Workflow K to `sage.md` | 3.3 |
| 3.5 | Test consolidation with sample data | 3.4 |

### Phase 4: Compound Loop (Week 2, Days 4-5 + Week 3)

| Task | Deliverable | Depends On |
|------|-------------|------------|
| 4.1 | Implement session context loader | Phase 1 |
| 4.2 | Add relevance filtering | 4.1 |
| 4.3 | Integrate with session start | 4.2 |
| 4.4 | Add memory entry tracking to WORKFLOW_STATE | Phase 1 |
| 4.5 | End-to-end testing | All above |

---

## 6. Testing Strategy

### 6.1 Unit Tests

| Component | Test Cases |
|-----------|------------|
| Log entry formatting | Valid format, edge cases (empty fields, special chars) |
| Log file parsing | Single entry, multiple entries, malformed entries |
| Pattern detection | 0 patterns, 1 pattern, multiple patterns |
| Keyword extraction | Stop words, technical terms, empty input |
| Date handling | Various formats, invalid dates |

### 6.2 Integration Tests

| Scenario | Expected Outcome |
|----------|------------------|
| Log entry via script | Entry appears in memory/YYYY-MM-DD.md |
| Log entry via Sage | Entry appears in memory/YYYY-MM-DD.md |
| Weekly consolidation | MEMORY_INDEX.md generated with correct content |
| Session context load | Relevant entries surfaced |
| Threshold trigger | Prompt appears after >5 files modified |

### 6.3 End-to-End Tests

| Scenario | Steps | Expected |
|----------|-------|----------|
| Full logging cycle | Work -> Log -> Consolidate -> Promote | Pattern reaches LEARNINGS.md |
| Session continuity | Day 1: Log learning. Day 2: Start session | Day 1 learning surfaced |
| Pattern detection accuracy | Create 3 similar entries | Pattern identified with count=3 |

### 6.4 Manual Testing Checklist

- [ ] Create first memory entry via script
- [ ] Create memory entry via Sage command
- [ ] Verify entry format matches specification
- [ ] Run weekly consolidation with 5+ entries
- [ ] Verify MEMORY_INDEX.md is correct
- [ ] Start new session and verify context loading
- [ ] Trigger threshold-based prompt
- [ ] Dismiss prompt and verify no repeat

---

## 7. Rollback Plan

### Rollback Scenarios

| Scenario | Trigger | Action |
|----------|---------|--------|
| Feature not valuable | User feedback after 30 days | Archive memory/, remove workflows |
| Performance issues | Context load >60 seconds | Disable context loader |
| Storage concerns | memory/ exceeds 1MB | Aggressive archiving |
| Integration conflicts | Sage errors | Remove new workflows, keep memory/ |

### Rollback Procedure

1. **Disable context loading** (immediate):
   - Remove session start integration
   - Memory/ remains for manual reference

2. **Disable triggers** (same day):
   - Remove Supervisor integration
   - Keep manual logging available

3. **Archive memory system** (end of trial):
   - Move memory/ to archive/memory/
   - Remove Workflows J, K from Sage
   - Update CLAUDE.md documentation

### Data Preservation

- Memory entries are never deleted automatically
- Rollback preserves all logged data in archive/
- Can be re-enabled later without data loss

---

## 8. Security Considerations

### Data Sensitivity

| Data Type | Sensitivity | Handling |
|-----------|-------------|----------|
| Task descriptions | Low | May contain project details |
| Decisions/rationale | Low | May reference architecture |
| File paths | Low | Relative to project |
| Issue/PR numbers | Low | Public GitHub data |

### Recommendations

1. **No PII in logs**: Task descriptions should not include personal data
2. **No credentials**: Never log API keys, tokens, or passwords
3. **Relative paths only**: Use relative paths, not absolute
4. **Review before commit**: Memory entries are git-tracked

### Access Control

- Memory files inherit project access control
- No additional authentication needed
- Standard git permissions apply

---

## 9. Appendices

### A: File Format Examples

**Empty day log** (memory/2026-02-01.md):

```markdown
# Session Memory: 2026-02-01

No entries logged for this date.
```

**Single entry day log**:

```markdown
# Session Memory: 2026-02-01

## [2026-02-01T09:30:00] Task: Set up memory system

**Outcome**: SUCCESS
**Files Modified**: 4

**Key Decisions**:
- Use markdown format: Human readable and git-friendly (affects: memory/)

**Learnings**:
- PEP 723 scripts work well for standalone tools

**Would Do Differently**:
- Nothing noted

**Related**:
- Issue: #150

---
```

### B: Error Handling

| Error | Handling |
|-------|----------|
| memory/ doesn't exist | Create automatically |
| Log file locked | Retry 3x, then warn user |
| Parse error in log | Skip malformed entry, log warning |
| Pattern detection timeout | Return partial results |

### C: Configuration Options (Future)

```yaml
# .claude/config/memory.yaml (future)
memory:
  retention_days: 90
  auto_consolidate: weekly
  context_days: 7
  max_context_entries: 5
  relevance_threshold: 0.2
```

### D: Related Documents

| Document | Purpose |
|----------|---------|
| `agent_memory_report.md` | Research findings |
| `agent_memory_plan.md` | Implementation plan |
| `agent_memory_PRD.md` | Product requirements |
| `.claude/agents/sage.md` | Sage agent (to be extended) |
| `.claude/skills/learning-curation.md` | Existing learning workflow |
| `.claude/skills/context-checkpoint.md` | Existing context management |

---

*TDD prepared by Technical Architect persona*
*Review date: 2026-02-01*
