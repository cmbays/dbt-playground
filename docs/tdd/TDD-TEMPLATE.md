# TDD-[NUMBER]: [Feature Title]

**Status**: Draft | Review | Approved | In Progress | Complete
**Author**: [Name]
**Created**: YYYY-MM-DD
**Updated**: YYYY-MM-DD

**Source PRD**: PRD-XXX
**Related Issue**: #XX
**Architecture Diagram**: TDD-XXX.d2 (if applicable)

---

## Overview

_Brief description of what this TDD covers and the selected approach._

[1-2 paragraphs summarizing the technical approach]

## Technical Approach

### Selected Option

_Description of the chosen implementation approach and why it was selected._

### Alternatives Considered

#### Option A: [Name]
**Approach**: Brief description

**Pros**:
- Pro 1
- Pro 2

**Cons**:
- Con 1
- Con 2

**Complexity**: Low/Medium/High

#### Option B: [Name]
**Approach**: Brief description

**Pros**:
- Pro 1
- Pro 2

**Cons**:
- Con 1
- Con 2

**Complexity**: Low/Medium/High

### Decision Rationale

_Why the selected option was chosen over alternatives._

## Architecture

### Component Diagram

```d2
# D2 diagram here or reference external file
component1 -> component2: relationship
```

### Component Descriptions

| Component | Responsibility |
|-----------|----------------|
| Component 1 | Description |
| Component 2 | Description |

## Data Structures

```javascript
// Key data structures used

const exampleData = {
  id: 'string',
  property: 'type',
};
```

## File Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `path/to/file.html` | Create | New page for feature |
| `path/to/file.js` | Modify | Add new function |
| `css/shared.css` | Modify | Add styles |

## Implementation Sequence

_Ordered steps for implementation._

1. **Step 1**: Description
   - Sub-task a
   - Sub-task b

2. **Step 2**: Description
   - Sub-task a
   - Sub-task b

3. **Step 3**: Description

## API / Interface Design

_If applicable, describe interfaces between components._

### Function Signatures

```javascript
/**
 * Description of function
 * @param {Type} param - Description
 * @returns {Type} Description
 */
function functionName(param) {
  // ...
}
```

## State Management

_How state is managed for this feature._

- Local state: Description
- Persistent state: Description (localStorage, etc.)

## Edge Cases

| Case | Handling |
|------|----------|
| Edge case 1 | How it's handled |
| Edge case 2 | How it's handled |

## Error Handling

| Error Scenario | Handling | User Feedback |
|----------------|----------|---------------|
| Error 1 | How handled | What user sees |
| Error 2 | How handled | What user sees |

## Performance Considerations

- Consideration 1
- Consideration 2

## Accessibility Considerations

- Keyboard navigation: Description
- Screen reader: Description
- Color contrast: Description

## Testing Considerations

_Key areas that need testing._

- Test area 1
- Test area 2
- Test area 3

## Dependencies

_Technical dependencies._

- Uses: `shared.css`, `shared.js`
- Requires: Existing component X
- External: None

## Open Questions

_Unresolved technical questions._

1. Question 1?
2. Question 2?

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| YYYY-MM-DD | Name | Initial draft |
