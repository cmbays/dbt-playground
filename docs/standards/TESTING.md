---
audience: [tester, developer]
priority: high
size: small
dependencies: []
last_updated: 2026-01-25
status: active
tags: [standards, testing, quality, tdd]
---

# Testing Framework & Strategy

## Purpose

This document defines our testing approach, documents test-driven development practices, and captures learnings from bugs discovered during development. It should be updated continuously as we refine our testing practices.

## Testing Philosophy

**Core Principle**: Test before deploy, learn from failures, improve the framework.

Our testing approach prioritizes:

1. **Preventing regressions** - Don't break what works
2. **Catching issues early** - Test during BUILD phase, not after DEPLOY
3. **Learning from bugs** - Document root causes and prevention strategies
4. **Incremental improvement** - Testing framework evolves with the project

## Test-Driven Development (TDD) Approach

### For New Features

1. **PLAN Phase**: Define test criteria before writing code
   - What should work when feature is complete?
   - What edge cases exist?
   - How will we verify success?

2. **PROTOTYPE Phase**: Test prototype thoroughly
   - Manual testing of all functionality
   - Cross-browser check (if applicable)
   - Mobile responsiveness check
   - Document any issues found

3. **BUILD Phase**: Test each page as completed
   - Don't wait until all pages are built
   - Verify against prototype behavior
   - Check consistency across pages

4. **VERIFY Phase**: Comprehensive testing
   - Run through complete test checklist
   - Document all results in `temp/v[X.Y]_TESTING.md`
   - Fix issues before DEPLOY

### Test Documentation Format

For each build, create `temp/v[X.Y]_TESTING.md` with:

```markdown
# Version X.Y - Testing Results

## Test Date
[Date]

## Test Environment
- Browser(s): [Chrome, Firefox, Safari, etc.]
- Device(s): [Desktop, Mobile, etc.]
- Screen sizes: [1920x1080, 375x667, etc.]

## Functionality Tests
- [ ] Navigation between pages works
- [ ] All links point to correct destinations
- [ ] Shared CSS loads properly
- [ ] Shared JS loads properly
- [ ] [Feature-specific test]
- [ ] [Feature-specific test]

## Content Tests
- [ ] Japanese text displays correctly
- [ ] Furigana renders properly (if applicable)
- [ ] Audio files play correctly (if applicable)
- [ ] Images load properly (if applicable)

## Interaction Tests
- [ ] Buttons respond to clicks
- [ ] Tense switching works (if applicable)
- [ ] Hint toggles function (if applicable)
- [ ] Quiz interactions work (if applicable)

## Responsive Tests
- [ ] Layout works on desktop (>1024px)
- [ ] Layout works on tablet (768px-1024px)
- [ ] Layout works on mobile (<768px)

## Issues Found
1. [Description of issue]
   - Severity: [Critical/High/Medium/Low]
   - Fix applied: [Yes/No - description]

## Sign-off
- [ ] All critical issues resolved
- [ ] Ready for deployment
```

## Testing Checklist Categories

### 1. Navigation Testing

**Purpose**: Ensure users can move between pages without broken links

Tests:

- Click every navigation button
- Verify correct page loads
- Check back button works
- Verify breadcrumbs (if applicable)
- Test external links open in new tabs (if applicable)

**Bug Prevention**: Navigation breaks are common during refactoring

### 2. Functionality Testing

**Purpose**: Verify all interactive features work as designed

Tests:

- Audio playback (if applicable)
- Hint toggles (if applicable)
- Tense/tab switching (if applicable)
- Quiz submissions and scoring (if applicable)
- Form submissions (if applicable)

**Bug Prevention**: JavaScript errors can silently break functionality

### 3. Content Rendering Testing

**Purpose**: Ensure content displays correctly across devices/browsers

Tests:

- Japanese characters render properly
- Furigana positioning is correct (if applicable)
- Images load and display correctly
- Text is readable (font size, contrast)
- No content overflow or truncation

**Bug Prevention**: Encoding and font issues vary by browser

### 4. Responsive Design Testing

**Purpose**: Verify layout adapts to different screen sizes

Tests:

- Desktop view (>1024px width)
- Tablet view (768px-1024px width)
- Mobile view (<768px width)
- Portrait and landscape orientations
- Touch interactions on mobile

**Bug Prevention**: CSS media queries need explicit testing

### 5. Cross-Browser Testing

**Purpose**: Ensure consistent experience across browsers

Browsers to test:

- Chrome (primary)
- Firefox (secondary)
- Safari (if available)
- Mobile browsers (Chrome mobile, Safari mobile)

**Bug Prevention**: Browser inconsistencies are real, especially with CSS

### 6. Performance Testing

**Purpose**: Ensure pages load quickly and smoothly

Tests:

- Page load time (<3 seconds ideal)
- Smooth animations (no jank)
- Audio loads without delay
- Images optimized (file sizes reasonable)

**Bug Prevention**: Performance degrades gradually without monitoring

## Bug Learnings & Prevention

### Bug Log Format

When bugs are discovered, document them here:

```markdown
### [Date] - [Brief Description]
**Severity**: [Critical/High/Medium/Low]
**Discovered**: [Which phase/how found]
**Root Cause**: [Why did this happen?]
**Fix Applied**: [How was it resolved?]
**Prevention Strategy**: [How to avoid this in the future]
**Test Added**: [What test will catch this in the future?]
```

### Current Bug Learnings

#### 2026-01-25 - Property Name Convention Mismatch (Bug 1)

**Severity**: High (silent failure, shows wrong data)
**Discovered**: Browser testing - dashboard showed all zeros
**Root Cause**: Dashboard used camelCase (`dueCount`, `newAvailable`) but SessionManager returned snake_case (`due_count`, `new_available`). Property access returned `undefined`, which displayed as `0`.
**Fix Applied**: Changed dashboard to use snake_case property names matching the API
**Prevention Strategy**:

1. Document module interfaces with exact property names in JSDoc
2. Console.log the actual object to see property names before assuming
3. Establish project convention and enforce consistently
**Test Added**: Check that property names match between producer and consumer modules

---

#### 2026-01-25 - Falsy Zero in Sorting (Bug 2)

**Severity**: Medium (incorrect sort order)
**Discovered**: Browser testing - N5 kanji sorted last instead of first
**Root Cause**: `jlptOrder[a.jlpt_level] || 5` treated N5's sort value of `0` as falsy, falling back to `5`. JavaScript `||` treats `0`, `""`, and `false` as falsy.
**Fix Applied**: Changed to `?? 5` (nullish coalescing) which only falls back for `null`/`undefined`
**Prevention Strategy**:

1. Use `??` when default should only apply for null/undefined
2. Use `||` only when any falsy value should trigger fallback
3. Code review checklist: check all `||` operators with defaults
**Test Added**: Verify JLPT N5 (value 0) sorts before N4 (value 1)

---

#### 2026-01-25 - Incorrect Test Expectation (Bug 3)

**Severity**: Low (false test failure)
**Discovered**: Test verification - test expected wrong stage after AGAIN response
**Root Cause**: Test expected `apprentice_4` for AGAIN from `guru_1` but implementation correctly returns `apprentice_3` (drops 2 stages: index 4 - 2 = index 2)
**Fix Applied**: Updated test expectation to match correct implementation behavior
**Prevention Strategy**:

1. Trace through implementation manually to calculate expected values
2. When test fails, verify expectation is correct before assuming implementation is wrong
3. Add comments explaining non-obvious expected values
**Test Added**: N/A (fixed existing test)

---

#### 2026-01-25 - Missing Window Export for Browser (Bug 4)

**Severity**: Critical (module completely inaccessible)
**Discovered**: Browser testing - dashboard couldn't find kanji data
**Root Cause**: `const homeLifeKanji = [...]` doesn't create `window.homeLifeKanji`. JavaScript `const` at file scope does not become a window property - only `var` or explicit assignment does.
**Fix Applied**: Added explicit `window.homeLifeKanji = homeLifeKanji` export
**Prevention Strategy**:

1. Always add explicit window exports for browser modules
2. Verify in console that `window.ModuleName` exists after loading
3. Use the revealing module pattern with explicit export
**Test Added**: Check `window.ModuleName` exists for all modules in console

---

#### 2026-01-25 - Missing Error Handling in Initialization (Bug 5)

**Severity**: High (silent failure, hard to diagnose)
**Discovered**: Browser testing - page loaded but features broken, no console errors
**Root Cause**: No try-catch around initialization, errors failed silently
**Fix Applied**: Added comprehensive error handling with console.log tracing at each step
**Prevention Strategy**:

1. Wrap initialization in try-catch
2. Add console.log before critical operations
3. Log success with data after operations complete
4. Catch and log errors with full context
**Test Added**: Verify console shows initialization trace on page load

---

## Common Testing Pitfalls to Avoid

1. **Testing only in one browser** - Always test in multiple browsers
2. **Testing only on desktop** - Mobile usage is significant
3. **Skipping edge cases** - What happens if audio fails to load?
4. **Assuming links work** - Always click through navigation manually
5. **Not testing after "small changes"** - Small changes can have big impacts
6. **Testing in isolation** - Test the full user flow, not just one feature

## Testing Tools & Commands

### Manual Testing Checklist

Located in: `temp/v[X.Y]_TESTING.md` (create for each version)

### Browser DevTools

- Console: Check for JavaScript errors
- Network tab: Verify all resources load
- Device toolbar: Test responsive design
- Lighthouse: Performance and accessibility audits

### Local Server

```bash
# Run local server for testing
python -m http.server 8000
# Then open: http://localhost:8000
```

### Future Automated Testing

*As project matures, consider:*

- HTML validation (W3C validator)
- Link checking automation
- Screenshot regression testing
- Accessibility testing tools

## Continuous Improvement

This testing framework should evolve. After each version:

1. Review what bugs were caught (or missed)
2. Update test checklists with new tests
3. Document new bug learnings
4. Refine prevention strategies
5. Improve TDD process

**Goal**: Each version should be more robust than the last, with fewer bugs making it to deployment.

---

## Related Documentation

- [[../.claude/skills/tdd-workflow.md]] - Detailed TDD workflow for implementation
- [[../.claude/skills/verification-loop.md]] - QA verification process
- [[../.claude/rules/testing.md]] - Testing standards and requirements
- [[../CLAUDE.md#standard-workflow]] - Where testing fits in development workflow
- [[../.claude/agents/AGENTS.md#verification-checklist]] - Agent verification checklist

---

*Last Updated: 2026-01-25*
*Next Review: After v0.4 deployment*
