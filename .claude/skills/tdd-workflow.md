# TDD Workflow Skill

Test-driven development workflow for feature implementation.

## Overview

This skill implements the Red-Green-Refactor cycle for developing features with tests first.

## Trigger

Invoke when:

- Implementing new JavaScript functionality
- Adding interactive features
- Building components with complex logic

## Workflow Steps

### Phase 1: RED - Define Failing Tests

1. **Clarify Requirements**
   - What should this feature do?
   - What are the inputs and outputs?
   - What edge cases exist?

2. **Write Test Specification**
   Create `temp/v[X.Y]_TESTING.md`:

   ```markdown
   # Test Specification: [Feature]

   ## Acceptance Criteria
   - [ ] Criterion 1
   - [ ] Criterion 2

   ## Unit Tests
   - [ ] Test case 1: [description]
   - [ ] Test case 2: [description]

   ## Edge Cases
   - [ ] Edge case 1: [description]
   - [ ] Edge case 2: [description]

   ## Manual Verification
   - [ ] Visual check 1
   - [ ] Interaction check 1
   ```

3. **Create Test Scaffolding** (for JS)

   ```javascript
   // temp/[feature].test.js
   describe('[Feature Name]', () => {
     test('should [expected behavior]', () => {
       // Arrange
       const input = ...;

       // Act
       const result = functionUnderTest(input);

       // Assert
       expect(result).toBe(expected);
     });

     test('should handle edge case', () => {
       // Edge case testing
     });
   });
   ```

### Phase 2: GREEN - Implement Minimum Solution

1. **Write Minimum Code**
   - Only enough to pass tests
   - Don't optimize yet
   - Don't add extra features

2. **Verify Tests Pass**
   - Run test suite
   - All defined criteria met
   - No regressions

3. **Manual Verification**
   - Check in browser
   - Test user interactions
   - Verify visual output

### Phase 3: REFACTOR - Improve Quality

1. **Clean Up Code**
   - Remove duplication
   - Improve naming
   - Add necessary comments
   - Extract functions if needed

2. **Verify Tests Still Pass**
   - Same behavior
   - No regressions
   - Performance acceptable

3. **Document**
   - Update test spec with results
   - Note any deviations
   - Record learnings

## Artifacts

| Output | Location |
|--------|----------|
| Test specification | `temp/v[X.Y]_TESTING.md` |
| Test code (if applicable) | `temp/[feature].test.js` |
| Implementation | `temp/` → final location |
| Test results | Appended to test spec |

## Exit Criteria

- [ ] All tests pass
- [ ] Edge cases handled
- [ ] Code reviewed and clean
- [ ] Documentation updated
- [ ] Ready for deployment

## Integration

- **Entry**: After TDD created by Architect
- **Persona**: Quality Tester + Developer
- **Exit**: To Code Review

## Example

```
User: Implement JLPT filter for kanji cards

TDD Phase 1 (RED):
- Define: filterByLevel(kanji[], level) returns filtered array
- Test: N5 filter returns only N5 kanji
- Test: Empty array returns empty
- Test: Invalid level returns all

TDD Phase 2 (GREEN):
- Implement filterByLevel function
- Pass all tests
- Verify in browser

TDD Phase 3 (REFACTOR):
- Extract level validation
- Add JSDoc comments
- Confirm tests still pass
```

---

## Related Documentation

- [[../../docs/TESTING.md]] - Project testing framework and bug learnings
- [[../rules/testing.md]] - Testing requirements and standards
- [[../agents/AGENTS.md]] - Agent orchestration and when to use TDD
- [[code-review-workflow.md]] - Next step after TDD complete
- [[verification-loop.md]] - QA verification process
