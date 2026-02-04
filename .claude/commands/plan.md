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
   - Identify related existing files and patterns
   - Note any constraints or dependencies

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
   - Extract keywords from current task description (file types, tech stack, function/class names)
   - Read "Topics Index" section from MEMORY_INDEX.md
   - Filter "Recurring Patterns" and "Promotion Candidates" to only show items where:
     - Topic keywords match current task keywords (case-insensitive), OR
     - Pattern score >= 0.7 (high-confidence patterns shown regardless of topic match)
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
   | Condition | Behavior |
   |-----------|----------|
   | File missing | Advisory message, skip gracefully |
   | File empty | Advisory message, skip gracefully |
   | Section missing | Advisory message listing missing sections, skip |
   | Parse error | Silent fallback to no-memory behavior |
   | No relevant patterns | Skip display (no message needed) |

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
