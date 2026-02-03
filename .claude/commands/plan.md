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
   - Check if `memory/MEMORY_INDEX.md` exists
   - If present, extract relevant context:
     - "Recurring Patterns" section - proven patterns to consider
     - "Promotion Candidates" section - patterns nearing proven status
   - Display relevant learnings to inform planning:

   ```
   [Memory Bootstrap]
   Recent learnings that may inform this plan:

   Recurring Patterns:
   - [pattern summary] (score: X.XX)

   Promotion Candidates:
   - [ ] [candidate description]

   Consider these patterns when designing the implementation approach.
   ```

   - Note: This is advisory context, not requirements
   - Skip this step if memory/MEMORY_INDEX.md doesn't exist

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
