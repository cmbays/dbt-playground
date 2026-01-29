# TDD Command

Execute test-driven development workflow.

## Usage

```
/tdd [feature or component to implement]
```

## Examples

```
/tdd staging model for Stripe payments
/tdd customer dimension with order history
/tdd incremental model error handling
```

## TDD Workflow

### Phase 1: RED (Write Failing Tests)

1. **Define Acceptance Criteria**
   - What should this feature do?
   - What are the expected inputs/outputs?
   - What edge cases exist?

2. **Write Test Specification**
   Create `temp/v[X.Y]_TESTING.md`:

   ```markdown
   # Test Specification: [Feature]

   ## Unit Tests
   - [ ] Test 1: Description
   - [ ] Test 2: Description

   ## Integration Tests
   - [ ] Test 1: Description

   ## Manual Verification
   - [ ] Check 1: Description
   - [ ] Check 2: Description
   ```

3. **Create Test Scaffolding**
   For JavaScript features:

   ```javascript
   // temp/[feature].test.js
   describe('[Feature]', () => {
     test('should [expected behavior]', () => {
       // Test implementation
     });
   });
   ```

### Phase 2: GREEN (Make Tests Pass)

1. **Implement Minimum Code**
   - Write just enough to pass tests
   - Work in `temp/` first
   - Don't optimize yet

2. **Run Tests**
   - Verify all tests pass
   - Document any failures
   - Fix issues iteratively

3. **Manual Verification**
   - Test in browser
   - Check responsive behavior
   - Verify accessibility

### Phase 3: REFACTOR (Improve Code)

1. **Clean Up Implementation**
   - Remove duplication
   - Improve naming
   - Add necessary comments

2. **Verify Tests Still Pass**
   - No regressions
   - Same behavior, cleaner code

3. **Document Final State**
   - Update test spec with results
   - Note any deviations

## Test Categories

| Category | Purpose | Example |
|----------|---------|---------|
| **Schema** | Test column properties | Primary key is unique and not null |
| **Data** | Test business rules | Order totals are non-negative |
| **Singular** | Custom validation | No orphaned records exist |
| **Regression** | Ensure no breaks | Existing models still work |

## Testing Checklist

### For HTML/CSS

- [ ] Renders correctly in Chrome
- [ ] Renders correctly in Firefox
- [ ] Renders correctly in Safari
- [ ] Mobile responsive (320px - 768px)
- [ ] Tablet responsive (768px - 1024px)
- [ ] Desktop layout (1024px+)
- [ ] Dark mode (if applicable)

### For JavaScript

- [ ] No console errors
- [ ] Event handlers work
- [ ] Edge cases handled
- [ ] Error states handled
- [ ] Performance acceptable

### For dbt Models

- [ ] Primary keys are unique
- [ ] Foreign keys have valid references
- [ ] Null handling is explicit
- [ ] Column names follow conventions

## Test Documentation Template

```markdown
# Test Results: v[X.Y] - [Feature]

## Date
YYYY-MM-DD

## Summary
[Pass/Fail] - [X/Y tests passing]

## Test Results

### Unit Tests
| Test | Status | Notes |
|------|--------|-------|
| Test 1 | Pass | |
| Test 2 | Pass | |

### Integration Tests
| Test | Status | Notes |
|------|--------|-------|
| Test 1 | Pass | |

### Manual Verification
| Check | Status | Notes |
|-------|--------|-------|
| Chrome | Pass | |
| Mobile | Pass | |

## Issues Found
- Issue 1: Description (fixed)
- Issue 2: Description (deferred)

## Sign-Off
Ready for review: Yes/No
```

## Persona Integration

This command activates the **Quality Tester** (`test:`) persona in collaboration with **Feature Developer** (`dev:`) for the implementation phases.

## Skill Integration

May invoke:

- `/feature-dev` for guided implementation
