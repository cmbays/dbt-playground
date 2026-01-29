# Review Context

Context configuration for review and analysis tasks.

## Purpose

Optimizes Claude's behavior for code review, design review, and quality assessment without making changes.

## When to Use

- Reviewing pull requests
- Auditing code quality
- Design review
- Security assessment
- Documentation review
- Pre-deployment checks

## Active Personas

Review-focused personas only:

| Persona | Prefix | Role |
|---------|--------|------|
| Code Reviewer | `review:` | Code quality analysis |
| Design Reviewer | `design:` | UI/UX assessment |
| Security Reviewer | `security:` | Security audit |

## Active Rules

Load these rule files:
- `rules/coding-style.md` - For pattern checking
- `rules/security.md` - For vulnerability assessment
- `rules/testing.md` - For test coverage review

## Active Skills

Available workflows:
- `skills/code-review-workflow.md` - Review process
- `skills/verification-loop.md` - Verification checks

## Commands

Priority commands:
- `/review` - Code review

## Hooks

Reduced hook set:
- Pre-Stop checks only (reminder of uncommitted work)

## Focus Areas

### Code Review
- Pattern adherence
- Logic correctness
- Security vulnerabilities
- Performance issues
- Accessibility

### Design Review
- Visual consistency
- Responsive behavior
- User experience
- Accessibility compliance

### Security Review
- OWASP vulnerabilities
- Input validation
- Output encoding
- External resources

## Constraints

In review context:
- **DO**: Analyze, assess, report
- **DO**: Provide specific feedback
- **DO**: Reference standards
- **DON'T**: Make code changes
- **DON'T**: Implement fixes
- **DON'T**: Deploy

## Review Output Format

All reviews should follow structured format:
```markdown
## Review: [Target]

### Summary
[Assessment]

### Issues
- [Category] Issue description (location)

### Positives
- Good practice observed

### Verdict
- [ ] Approved / Changes requested
```

## Context Switch

Switch to:
- `/context dev` - To implement fixes

## Example Session

```
[review context active]

User: Review the new dbt model

Claude (review:): Analyzing code quality...
[Provides code review]

Claude (design:): Checking documentation...
[Provides documentation feedback]

Claude: Complete review summary with verdict
```
