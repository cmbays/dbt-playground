# Plan Command

Activate structured planning mode for implementation tasks.

## Usage

```
/plan [feature or task description]
```

## Workflow

When this command is invoked:

1. **Understand Current State**
   - Read relevant documentation (CLAUDE.md, PROJECT_STRUCTURE.md, ARCHITECTURE.md)
   - Read [TECH_STACK.md](../../docs/reference/TECH_STACK.md) for technology constraints
   - Identify related existing files and patterns
   - Note any constraints or dependencies

1.1 **Interrogation Phase** (Mandatory for `feat`, optional for others)

   Before making assumptions, systematically ask clarifying questions. This surfaces hidden requirements and prevents rework.

   **Enforcement by Task Type**:

   | Type | Interrogation |
   |------|--------------|
   | `feat` | **Mandatory** - Must complete before planning |
   | `fix` | Optional - Ask if scope unclear |
   | `docs` | Optional - Ask if audience unclear |
   | `chore` | Skip - Proceed directly |

   **Question Categories**:

   *Users & Scope*:
   - Who will use this feature? (humans, agents, both)
   - What's explicitly IN scope for this task?
   - What's explicitly OUT of scope? (prevents scope creep)
   - Is this a complete feature or a vertical slice of something larger?

   *Data & Dependencies*:
   - What data/inputs does this need?
   - What existing code/models does this depend on?
   - What will depend on this once complete?
   - Are there external dependencies (APIs, libraries, services)?

   *Error Handling & Edge Cases*:
   - What can go wrong? (list failure modes)
   - How should errors be handled? (fail fast, graceful degradation, retry)
   - What are the edge cases? (empty data, invalid input, timeout)
   - Is there a rollback strategy needed?

   *Technical Constraints*:
   - Performance requirements? (response time, data volume)
   - Security considerations? (auth, input validation, PII)
   - Compatibility requirements? (mobile, dark mode, accessibility)

   **Interrogation Output**:

   Document answers in the plan file under "## Requirements Clarification":

   ```markdown
   ## Requirements Clarification

   ### Users & Scope
   - **Users**: [who uses this]
   - **In Scope**: [explicit inclusions]
   - **Out of Scope**: [explicit exclusions]

   ### Data & Dependencies
   - **Inputs**: [data/inputs needed]
   - **Depends On**: [existing code/models]
   - **Depended On By**: [downstream consumers]

   ### Error Handling
   - **Failure Modes**: [what can go wrong]
   - **Strategy**: [how to handle]

   ### Constraints
   - **Performance**: [requirements]
   - **Security**: [considerations]
   ```

   **Skip Conditions**:

   - User says "skip interrogation" or "proceed"
   - Task type is `chore`
   - All questions already answered in task description

1.5 **Bootstrap from Session Memory** (when available)

   **File Check:**
   - Check if `memory/MEMORY_INDEX.md` exists
   - If missing: Display advisory and skip gracefully

   ```
   [Memory Bootstrap] No memory index found (memory/MEMORY_INDEX.md missing). Skipping.
   ```

   **Section Validation:**
   - Required sections: "Recurring Patterns", "Promotion Candidates", "Topics Index"
   - If any section is missing or empty:

   ```
   [Memory Bootstrap] Memory index incomplete (missing: {section names}). Skipping.
   ```

   - If parse error occurs: Fall back to no-memory behavior silently

   **Relevance Filtering:**

   *Keyword Extraction from Task Description:*
   - Tokenize: Split on non-alphanumeric characters, lowercase all tokens
   - Remove stopwords: "the", "a", "an", "is", "to", "for", "of", "in", "on", "with"
   - Extract file extensions: Match pattern `\.[a-z0-9]+` (e.g., ".sql", ".py", ".md")
   - Identify tech-stack terms via whitelist: "python", "sql", "dbt", "react", "typescript", "javascript", "yaml", "json", "markdown", "git", "sqlite", "postgres"

   *Topics Index Structure* (from `memory/MEMORY_INDEX.md`):

   ```markdown
   ## Topics Index

   | Topic | Count |
   |-------|-------|
   | incremental | 3 |
   | models | 2 |
   | python | 1 |
   ```

   Parse as key-value pairs: topic name → occurrence count.

   *Recurring Patterns Structure*:

   ```markdown
   ## Recurring Patterns (2+ occurrences)

   ### Pattern 1: [Summary]
   **Occurrences**: N (dates)
   **Summary**: [description]
   **Score**: X.XX
   ```

   Extract: summary, score, and infer topics from summary keywords.

   *Matching Logic:*
   - For each pattern, extract keywords from its summary using same tokenization
   - Match if: (task keywords ∩ pattern keywords) is non-empty, OR score >= 0.7
   - Filter "Promotion Candidates" similarly by matching candidate text keywords

   - If no relevant patterns found after filtering: Skip display

   **Display Format** (only if relevant patterns found):

   ```
   [Memory Bootstrap]
   Relevant learnings for this task (filtered by topic match):

   Recurring Patterns:
   - [pattern summary] (score: X.XX, topics: topic1, topic2)

   Promotion Candidates:
   - [ ] [candidate description]

   Consider these patterns when designing the implementation approach.
   (Advisory context only - not requirements)
   ```

   **Error Handling Summary:**

   | Condition | User-Facing Behavior | Event Emitted |
   |-----------|---------------------|---------------|
   | File missing | Advisory message, skip gracefully | `memory_bootstrap_skip` (reason: "file_missing") |
   | File empty | Advisory message, skip gracefully | `memory_bootstrap_skip` (reason: "file_empty") |
   | Section missing | Advisory message listing missing sections, skip | `memory_bootstrap_skip` (reason: "section_missing", missing_sections[]) |
   | Parse error | Silent fallback to no-memory behavior (no user message) | `memory_bootstrap_error` (error_message, error_code?) |
   | No relevant patterns | Skip display (no message needed) | `memory_bootstrap_skip` (reason: "no_relevant_patterns") |

   All conditions emit events to `events.jsonl` for operator visibility, even when user-facing behavior is silent.

   **Metrics Instrumentation:**

   Emit events to `events.jsonl` at repo root for FS5 metrics aggregation:

   | Event Type | When | Payload Schema |
   |------------|------|----------------|
   | `memory_bootstrap_success` | Patterns found and displayed | `{timestamp, plan_id, pattern_count, topics_matched[], file_path}` |
   | `memory_bootstrap_skip` | Bootstrap skipped | `{timestamp, plan_id, reason: "file_missing" | "file_empty" | "section_missing" | "no_relevant_patterns", missing_sections[]?}` |
   | `memory_bootstrap_error` | Parse or read error | `{timestamp, plan_id, error_message, error_code?}` |

   *Example event:*

   ```json
   {"event": "memory_bootstrap_success", "timestamp": "2026-02-04T01:00:00Z", "plan_id": "plan-feat-x", "pattern_count": 2, "topics_matched": ["sql", "incremental"], "file_path": "memory/MEMORY_INDEX.md"}
   ```

   *Event file locations:*

   | File | Consumer | Purpose |
   |------|----------|---------|
   | `events.jsonl` (repo root) | FS5 metrics dashboard | Primary aggregation target for all agent events |
   | `memory/events.jsonl` | Sage consolidation | Session logging events for weekly pattern extraction |

   Memory bootstrap events are written to `events.jsonl` at repo root. Session logging events (from `sage: log session`) continue to write to `memory/events.jsonl` for backward compatibility with Sage Workflow K.

   This enables FS5 to track adoption rates, missing-section frequency, and matching effectiveness.

2. **Create Implementation Plan**
   - Create `temp/v[X.Y]_PLAN.md` with:
     - Feature summary
     - Files to create/modify
     - Implementation steps
     - Testing criteria
     - Rollback considerations

3. **Request Approval**
   - Present plan summary to user
   - Wait for explicit approval before proceeding

## Plan Document Template

```markdown
# Implementation Plan: [Feature Name]

## Version
Target: v[X.Y]

## Summary
[1-2 sentence description]

## Requirements Clarification

### Users & Scope
- **Users**: [who uses this - humans, agents, both]
- **In Scope**: [explicit inclusions]
- **Out of Scope**: [explicit exclusions]

### Data & Dependencies
- **Inputs**: [data/inputs needed]
- **Depends On**: [existing code/models]
- **Depended On By**: [downstream consumers]

### Error Handling
- **Failure Modes**: [what can go wrong]
- **Strategy**: [fail fast / graceful degradation / retry]

### Constraints
- **Performance**: [requirements if any]
- **Security**: [considerations if any]
- **Compatibility**: [mobile, dark mode, accessibility]

## Prerequisites
- [ ] Dependency 1
- [ ] Dependency 2

## Files to Create
| File | Purpose |
|------|---------|
| path/to/file.ext | Description |

## Files to Modify
| File | Changes |
|------|---------|
| path/to/file.ext | Description |

## Implementation Steps
1. Step 1
2. Step 2
3. Step 3

## Testing Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Rollback Plan
If issues arise:
1. Revert step
2. Revert step

## Questions for Review
- Any clarification needed?
```

## Example

```
/plan Add customer lifetime value metrics to the marts layer
```

Would create a plan covering:

- Data model changes
- Required staging sources
- Intermediate model logic
- Mart model structure
- Testing approach

## Persona Integration

This command activates the **Technical Architect** (`arch:`) persona for planning, with consultation from **Product Manager** (`pm:`) for requirements clarification.
