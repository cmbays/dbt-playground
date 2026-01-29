# Review Artifacts

This directory contains review documentation and artifacts from code and design reviews.

## Purpose

Capture review feedback and decisions:
- Code review summaries
- Design review reports
- Review checklists
- Approval records

## Review Types

### Code Review
Performed by: Code Reviewer (`review:` prefix)
Focus: Code quality, patterns, security, maintainability

### Design Review
Performed by: Design Reviewer (`design:` prefix)
Focus: UI/UX, accessibility, visual consistency

### Content Review
Performed by: Japanese Sensei (`sensei:` prefix)
Focus: Language accuracy, cultural appropriateness, pedagogy

## Naming Convention

```
[YYYY-MM-DD]-[type]-[feature-name].md
```

Examples:
- `2025-01-24-code-flashcard-flip.md`
- `2025-01-24-design-kanji-filter.md`
- `2025-01-24-content-shopping-dialogue.md`

## When to Create Review Artifacts

Create formal review documents for:
- Major feature implementations
- Significant bug fixes
- Architecture changes
- Content additions

Minor reviews can be captured in:
- PR comments
- Commit messages
- Issue comments

## Review Index

| Date | Type | Feature | Reviewer | Outcome |
|------|------|---------|----------|---------|
| _Example_ | _Code_ | _Flashcard Flip_ | _Code Reviewer_ | _Approved_ |

## Review Workflow

1. Developer completes implementation
2. Tester verifies tests pass
3. Code Reviewer performs code review
4. Design Reviewer performs design review (parallel)
5. Sensei reviews content (if applicable)
6. Issues addressed or documented
7. Reviewers approve
8. Documenter updates changelog

## Review Outcomes

| Outcome | Meaning | Next Step |
|---------|---------|-----------|
| Approved | Ready to merge/deploy | Proceed to Documenter |
| Approved with suggestions | Can proceed, optional improvements | Note for future |
| Changes requested | Must address before proceeding | Return to Developer |
| Blocked | Critical issue found | Discuss resolution |

## Templates

### Quick Code Review
```markdown
## Code Review: [Feature]
**Date**: YYYY-MM-DD
**Reviewer**: Code Reviewer

### Summary
Brief assessment

### Issues Found
- [ ] Issue 1
- [ ] Issue 2

### Verdict: Approved / Changes Requested
```

### Quick Design Review
```markdown
## Design Review: [Feature]
**Date**: YYYY-MM-DD
**Reviewer**: Design Reviewer

### Summary
Brief assessment

### Accessibility
- [ ] Check 1
- [ ] Check 2

### Responsive
- [ ] Mobile
- [ ] Tablet
- [ ] Desktop

### Verdict: Approved / Changes Requested
```
