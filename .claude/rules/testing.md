# Testing Rules

Standards for testing, verification, and quality assurance.

## Testing Philosophy

- Test early, test often
- Prefer manual verification for UI; automated for logic
- Document test results for version history
- Regression testing after any structural changes

## Test Categories

| Category | Purpose | When to Use |
|----------|---------|-------------|
| **Unit** | Test individual functions | JavaScript logic |
| **Integration** | Test component interactions | Multi-file features |
| **Manual** | Visual/UX verification | All UI changes |
| **Regression** | Ensure no breakage | After any change |
| **Cross-browser** | Browser compatibility | Before deployment |

## Manual Testing Checklist

### HTML/CSS
- [ ] Chrome renders correctly
- [ ] Firefox renders correctly
- [ ] Safari renders correctly
- [ ] Mobile (320px - 767px) works
- [ ] Tablet (768px - 1023px) works
- [ ] Desktop (1024px+) works

### JavaScript
- [ ] No console errors
- [ ] Event handlers work
- [ ] Edge cases handled
- [ ] Error states display correctly
- [ ] localStorage works

### Navigation
- [ ] All internal links work
- [ ] Breadcrumbs correct
- [ ] Back button behavior expected
- [ ] No broken links

### Accessibility
- [ ] Keyboard navigation works
- [ ] Focus states visible
- [ ] Screen reader compatible
- [ ] Color contrast sufficient

### Japanese Content
- [ ] Furigana displays correctly
- [ ] Romaji toggles work
- [ ] Audio plays (if applicable)
- [ ] JLPT level accurate

## Test Documentation

### Location
- Active testing: `temp/v[X.Y]_TESTING.md`
- Archived: `archive/v[X.Y]/docs/TESTING.md`

### Template
```markdown
# Test Results: v[X.Y] - [Feature]

## Date
YYYY-MM-DD

## Summary
[Pass/Fail] - [X/Y checks passing]

## Browser Testing
| Browser | Version | Status | Notes |
|---------|---------|--------|-------|
| Chrome | X.Y | Pass | |
| Firefox | X.Y | Pass | |
| Safari | X.Y | Pass | |

## Responsive Testing
| Breakpoint | Status | Notes |
|------------|--------|-------|
| Mobile (320px) | Pass | |
| Tablet (768px) | Pass | |
| Desktop (1024px) | Pass | |

## Feature Testing
| Feature | Status | Notes |
|---------|--------|-------|
| Feature 1 | Pass | |
| Feature 2 | Pass | |

## Issues Found
- Issue 1: Description (fixed)
- Issue 2: Description (deferred to vX.Y)

## Regression Checks
- [ ] Existing features still work
- [ ] Navigation unchanged
- [ ] No visual regressions

## Sign-Off
Ready for deployment: Yes/No
Tester: [name/date]
```

## TDD Workflow

### Red-Green-Refactor
1. **RED**: Write failing test/define criteria
2. **GREEN**: Implement minimum to pass
3. **REFACTOR**: Clean up, tests still pass

### Test-First for JavaScript
```javascript
// 1. Define expected behavior
describe('filterByLevel', () => {
  test('returns only kanji matching level', () => {
    const kanji = [
      { character: '日', level: 'N5' },
      { character: '語', level: 'N4' }
    ];
    const result = filterByLevel(kanji, 'N5');
    expect(result).toHaveLength(1);
    expect(result[0].character).toBe('日');
  });
});

// 2. Implement function
function filterByLevel(kanji, level) {
  return kanji.filter(k => k.level === level);
}
```

## Edge Cases to Test

### User Input
- Empty input
- Very long input
- Special characters
- Unicode/Japanese characters
- HTML injection attempts

### Data Handling
- Missing data
- Malformed JSON
- Corrupted localStorage
- Network failures (if applicable)

### UI States
- Loading state
- Empty state (no data)
- Error state
- Success state
- Hover/focus states

### Boundaries
- First item
- Last item
- Single item
- Maximum items
- Zero items

## Bug Documentation

### When Found
```markdown
## Bug: [Short Description]

### Environment
- Browser: [name/version]
- Device: [type]
- Date: YYYY-MM-DD

### Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Screenshots
[If applicable]

### Possible Cause
[If known]
```

### After Fixed
Add to `docs/TESTING.md` learning log:
```markdown
## Bug Learnings

### [Bug Title] - vX.Y
- **Root Cause**: [What caused it]
- **Fix**: [How it was fixed]
- **Prevention**: [How to avoid in future]
```

## Performance Testing

### Metrics to Check
- Page load time
- Time to interactive
- JavaScript execution time
- Memory usage (for long sessions)

### Tools
- Browser DevTools (Performance tab)
- Lighthouse audit
- Network throttling tests

## Verification Before Deployment

### Pre-Deploy Checklist
- [ ] All manual tests pass
- [ ] No console errors
- [ ] No broken links
- [ ] Version stamp updated
- [ ] Living docs updated
- [ ] Temp files cleaned (with approval)
- [ ] Git status clean
- [ ] Ready for tagging

## Continuous Testing

### After Every Change
- Visual check in browser
- Console for errors
- Quick navigation test

### Before Every Commit
- Run through feature checklist
- Regression spot-check

### Before Every Release
- Full test suite
- Cross-browser check
- Complete regression test
