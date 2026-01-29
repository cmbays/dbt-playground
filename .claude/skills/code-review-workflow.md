# Code Review Workflow Skill

Structured code review process for quality assurance.

## Overview

This skill provides a consistent code review process ensuring quality, security, and adherence to project standards.

## Trigger

Invoke when:

- Implementation complete and verified
- Pull request created
- Code changes ready for review
- Pre-merge verification needed

## Review Process

### Phase 1: Context Gathering

1. **Understand the Change**
   - Read PR description / commit messages
   - Review TDD/PRD if available
   - Understand the goal

2. **Identify Scope**
   - Which files changed?
   - What type of change? (feat/fix/refactor)
   - How extensive?

### Phase 2: Code Analysis

#### Correctness Review

- [ ] Logic is sound
- [ ] Edge cases handled
- [ ] No off-by-one errors
- [ ] Correct data types
- [ ] Error handling present

#### Security Review

- [ ] No XSS vulnerabilities
- [ ] Input validated
- [ ] Output encoded
- [ ] No sensitive data exposed
- [ ] External resources secured

#### Pattern Adherence

- [ ] Uses shared.css/shared.js
- [ ] Follows naming conventions
- [ ] Consistent with existing code
- [ ] No unnecessary departures

#### Quality Check

- [ ] Code is readable
- [ ] Functions are focused
- [ ] No unnecessary complexity
- [ ] Appropriate comments
- [ ] No dead code

#### Performance

- [ ] No obvious inefficiencies
- [ ] Reasonable time complexity
- [ ] No memory leaks
- [ ] Efficient DOM operations

### Phase 3: Documentation

Generate review report with categorized findings.

## Issue Categories

| Prefix | Meaning | Blocks Approval |
|--------|---------|-----------------|
| `[BLOCKER]` | Must fix | Yes |
| `[BUG]` | Incorrect behavior | Yes |
| `[SECURITY]` | Security vulnerability | Yes |
| `[SUGGESTION]` | Improvement idea | No |
| `[QUESTION]` | Needs clarification | Depends |
| `[NITPICK]` | Minor preference | No |
| `[PRAISE]` | Good work | No |

## Review Report Template

```markdown
## Code Review: [Feature/PR]

### Summary
[1-2 sentence overall assessment]

### Review Scope
- Files: [count]
- Lines changed: [+X/-Y]
- Type: [feat/fix/refactor]

---

### Blockers
Must fix before approval:
- [ ] `[BLOCKER]` Description (file:line)

### Bugs
Incorrect behavior:
- [ ] `[BUG]` Description (file:line)

### Security Issues
Vulnerabilities found:
- [ ] `[SECURITY]` Description (file:line)

### Suggestions
Optional improvements:
- `[SUGGESTION]` Description

### Questions
Need clarification:
- `[QUESTION]` Question text

### What's Good
Positive observations:
- `[PRAISE]` Good practice observed

---

### Verdict
- [ ] **Approved** - No issues
- [ ] **Approved with suggestions** - Optional fixes
- [ ] **Changes requested** - Must address blockers/bugs

### Checklist
- [ ] Meets requirements
- [ ] Follows patterns
- [ ] Security reviewed
- [ ] No regressions expected
```

## Common Issues

### HTML

- Missing semantic elements
- Broken navigation links
- Missing accessibility attributes
- Incorrect file paths
- Missing version comment

### CSS

- Not using custom properties
- Inline styles (should be in shared.css)
- Missing responsive styles
- Specificity issues
- Unused styles

### JavaScript

- Uncaught exceptions
- Missing error handling
- Not using shared.js functions
- Global variable pollution
- innerHTML with unsanitized data

### Japanese Content

- Missing furigana
- Incorrect romanization
- Unnatural phrasing
- Missing audio handling

## Review Response

### For Authors

When receiving review:

1. Address all blockers/bugs
2. Respond to questions
3. Consider suggestions
4. Thank reviewer for feedback

### Re-Review After Fixes

- Verify blockers resolved
- Check no new issues introduced
- Update verdict

## Quick Review (Minor Changes)

For trivial changes (typos, formatting):

- [ ] Change is correct
- [ ] No side effects
- [ ] Patterns followed

Can skip extensive security/performance review.

## Integration

- **Entry**: After Verification Loop passes
- **Persona**: Code Reviewer
- **Parallel**: Design Reviewer, Security Reviewer (optional)
- **Exit**: To Documenter (approved) or Developer (changes needed)

## Skill Invocation

Can be combined with built-in:

- `/code-review` for PR reviews
- `/feature-dev:code-reviewer` for detailed analysis

## Exit Criteria

Review complete when:

- [ ] All files examined
- [ ] All issues documented
- [ ] Verdict rendered
- [ ] Handoff clear

---

## Related Documentation

- [[../agents/AGENTS.md#code-review]] - When to use code review agents
- [[../rules/coding-style.md]] - Code standards to check against
- [[../rules/security.md]] - Security checklist
- [[deployment-workflow.md]] - Next step after review approval
- [[tdd-workflow.md]] - Previous step in pipeline
