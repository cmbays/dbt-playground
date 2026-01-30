# Review Command

Perform comprehensive code review with structured feedback.

## Usage

```
/review [file, folder, or PR reference]
/review --pr N                    # Post review directly to GitHub PR
/review --pr N --security         # Include security review
```

## Flags

| Flag | Description |
|------|-------------|
| `--pr N` | Post review comments directly to GitHub PR #N |
| `--security` | Include security review (requires --pr) |
| `--design` | Include design review (requires --pr) |

## Examples

```
/review models/staging/stripe/        # Local review output
/review models/marts/                 # Local review output
/review #12                           # Local review of PR #12
/review --pr 42                       # Post review to GitHub PR #42
/review --pr 42 --security            # Post code + security review
/review (reviews staged changes)      # Local review of staged changes
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
   - [ ] **dbt Patterns**: Naming conventions, CTE structure

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
- **Data Modeler** (`dbt-model:`) for dimensional modeling accuracy
- **Security Reviewer** (`security:`) for security-focused analysis

## Skill Integration

May invoke:

- `/code-review` for PR reviews
- `/feature-dev:code-reviewer` for implementation analysis

---

## PR Review Mode (--pr flag)

When using `--pr N`, the review is posted directly to GitHub instead of local output.

### PR Review Workflow

```
1. Fetch PR details: gh pr view N --json title,body,files
2. Fetch PR diff: gh pr diff N
3. Run review checklist against changes
4. Post inline comments for line-specific issues
5. Post summary review with verdict
6. Set review status (approve/request-changes/comment)
```

### Inline Comments

Line-specific issues are posted as inline comments on the PR:

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments \
  -f body="[BLOCKER] Missing null handling" \
  -f path="models/staging/stg_orders.sql" \
  -f line=42
```

### Summary Review

A summary review is posted with the final verdict:

```bash
# Approve (no blockers)
gh pr review N --approve --body "## Code Review Summary..."

# Request changes (blockers exist)
gh pr review N --request-changes --body "## Code Review Summary..."

# Comment only (suggestions only)
gh pr review N --comment --body "## Code Review Summary..."
```

### Multi-Reviewer Flow

When Supervisor orchestrates reviews:

1. `/review --pr N` posts Code Review
2. `/review --pr N --security` posts Security Review (if flagged)
3. `/review --pr N --design` posts Design Review (if flagged)
4. Each review appears as separate GitHub review
5. Supervisor monitors for 2+ approvals

### Benefits of PR Review Mode

- **Audit trail**: All feedback captured in PR history
- **Cross-session visibility**: Other agents can see feedback via `gh pr view`
- **GitHub integration**: Uses native review system (approve/request-changes)
- **Iteration tracking**: Subsequent reviews show as new reviews
