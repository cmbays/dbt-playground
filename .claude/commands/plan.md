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
/plan Add JLPT level filtering to vocabulary display
```

Would create a plan covering:
- Data structure changes
- UI filter component
- JavaScript filter logic
- localStorage persistence
- Testing approach

## Persona Integration

This command activates the **Technical Architect** (`arch:`) persona for planning, with consultation from **Product Manager** (`pm:`) for requirements clarification.
