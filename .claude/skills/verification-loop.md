# Verification Loop Skill

Quality assurance verification process for implementations.

## Overview

This skill provides a structured verification loop to ensure implementations meet requirements before approval.

## Trigger

Invoke when:

- Implementation is complete
- Before code review
- After bug fixes
- Pre-deployment checks

## Verification Loop

```
┌─────────────────────────────────────────┐
│           VERIFY                         │
│  ┌─────────────────────────────────┐    │
│  │ 1. Check against requirements   │    │
│  │ 2. Run test suite               │    │
│  │ 3. Manual verification          │    │
│  │ 4. Cross-browser check          │    │
│  │ 5. Accessibility check          │    │
│  └─────────────────────────────────┘    │
│              │                           │
│              ▼                           │
│      All Pass?                           │
│       /    \                             │
│     Yes     No                           │
│      │       │                           │
│      ▼       ▼                           │
│  APPROVE   FIX ──────────┐              │
│      │                   │              │
│      ▼                   │              │
│   DONE        ◄──────────┘              │
└─────────────────────────────────────────┘
```

## Verification Steps

### 1. Requirements Check

- [ ] Review TDD/PRD requirements
- [ ] Confirm all acceptance criteria met
- [ ] Verify no scope creep

### 2. Automated Tests

- [ ] Run test suite (if exists)
- [ ] All tests pass
- [ ] No console errors

### 3. Manual Verification

#### Functional

- [ ] Feature works as specified
- [ ] User interactions correct
- [ ] Error states handled
- [ ] Edge cases work

#### Visual

- [ ] Layout correct
- [ ] Styling consistent
- [ ] No visual regressions
- [ ] Dark mode (if applicable)

#### Navigation

- [ ] Links work
- [ ] Breadcrumbs correct
- [ ] Back button behavior
- [ ] No broken links

### 4. Cross-Browser

| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome | [ ] | [ ] |
| Firefox | [ ] | [ ] |
| Safari | [ ] | [ ] |

### 5. Accessibility

- [ ] Keyboard navigation works
- [ ] Focus states visible
- [ ] Color contrast sufficient
- [ ] Screen reader compatible

### 6. Japanese Content (if applicable)

- [ ] Furigana displays correctly
- [ ] Romaji toggles work
- [ ] Audio plays
- [ ] JLPT level accurate

## Issue Handling

### Found Issue

```markdown
## Issue: [Short Description]

### Severity
- [ ] Critical (blocks deployment)
- [ ] High (must fix)
- [ ] Medium (should fix)
- [ ] Low (nice to fix)

### Details
- Location: [file:line]
- Expected: [behavior]
- Actual: [behavior]
- Steps to reproduce: [list]

### Fix Applied
- [Description of fix]
- Verified: [date/time]
```

### After Fix

- Re-run full verification loop
- Confirm original issue resolved
- Check for regressions

## Verification Report

```markdown
# Verification Report: [Feature] v[X.Y]

## Date
YYYY-MM-DD

## Requirements Check
- TDD: [reference]
- Criteria met: X/Y

## Test Results
- Automated: Pass/Fail (X/Y)
- Manual: Pass/Fail

## Browser Compatibility
| Browser | Status |
|---------|--------|
| Chrome Desktop | Pass |
| Chrome Mobile | Pass |
| Firefox Desktop | Pass |
| Safari Desktop | Pass |

## Accessibility
- Keyboard: Pass
- Focus: Pass
- Contrast: Pass

## Issues Found
- Issue 1: [resolved]
- Issue 2: [resolved]

## Verdict
- [ ] Approved for deployment
- [ ] Needs fixes (see issues)

## Sign-off
Verified by: [date]
```

## Exit Criteria

All of the following must be true:

- [ ] Requirements check passed
- [ ] All tests pass
- [ ] Manual verification complete
- [ ] Cross-browser verified
- [ ] Accessibility checked
- [ ] No blocking issues
- [ ] Documentation updated

## Integration

- **Entry**: After Developer completes implementation
- **Persona**: Quality Tester
- **Exit**: To Code Review or back to Developer

## Quick Verification (Minor Changes)

For small fixes/patches:

- [ ] Feature works
- [ ] No console errors
- [ ] No visual regression
- [ ] No broken links

Skip extended cross-browser/accessibility for trivial changes.
