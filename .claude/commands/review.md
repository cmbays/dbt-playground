# Review Command

Perform comprehensive code review with structured feedback.

## Usage

```
/review [file, folder, or PR reference]
```

## Examples

```
/review topics/shopping/dialogue.html
/review kanji/
/review #12
/review (reviews staged changes)
```

## Review Process

1. **Gather Context**
   - Read the file(s) to review
   - Check TDD/PRD if available
   - Review related files for pattern consistency

2. **Analyze Code**
   Run through review checklist:
   - [ ] **Correctness**: Logic errors, edge cases
   - [ ] **Security**: XSS, injection, unsafe operations
   - [ ] **Patterns**: Follows shared.css/js conventions
   - [ ] **Structure**: Semantic HTML, proper organization
   - [ ] **Performance**: Unnecessary operations, reflows
   - [ ] **Accessibility**: Keyboard nav, screen readers
   - [ ] **Japanese Content**: Furigana, romanization accuracy

3. **Generate Report**
   Create structured review with categorized findings

## Review Report Format

```markdown
## Code Review: [Target]

### Summary
[Overall assessment]

### Blockers (Must Fix)
- [ ] [BLOCKER] Issue description (file:line)

### Bugs
- [ ] [BUG] Issue description (file:line)

### Security Issues
- [ ] [SECURITY] Issue description (file:line)

### Suggestions
- [SUGGESTION] Improvement idea
- [SUGGESTION] Another idea

### What's Working Well
- [PRAISE] Good pattern usage
- [PRAISE] Clean implementation

### Verdict
- [ ] Approved
- [ ] Approved with suggestions
- [ ] Changes requested (blockers exist)
```

## Issue Prefixes

| Prefix | Meaning | Action Required |
|--------|---------|-----------------|
| `[BLOCKER]` | Must fix before approval | Yes, critical |
| `[BUG]` | Incorrect behavior | Yes |
| `[SECURITY]` | Security vulnerability | Yes, urgent |
| `[SUGGESTION]` | Improvement idea | Optional |
| `[QUESTION]` | Needs clarification | Response needed |
| `[NITPICK]` | Minor style preference | Optional |
| `[PRAISE]` | Good work worth noting | None |

## Persona Integration

This command activates the **Code Reviewer** (`review:`) persona, with optional consultation from:

- **Design Reviewer** (`design:`) for UI/UX issues
- **Japanese Sensei** (`sensei:`) for content accuracy

## Skill Integration

May invoke:

- `/code-review` for PR reviews
- `/feature-dev:code-reviewer` for implementation analysis
