# Commit Command

Create a validated git commit through git: with Conventional Commits enforcement.

## Usage

```
/commit [message]
/commit "type(scope): description"
```

## Examples

```
/commit "feat(staging): add Stripe payments model"
/commit "fix(marts): correct null handling in dim_customers"
/commit "docs: update CLAUDE.md with git: integration"
/commit  # Interactive mode - will prompt for details
```

## Commit Message Format

### Conventional Commits (Required)

```
type(scope): description

[optional body]

[optional footer]
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Valid Types

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New feature | `feat(staging): add payments model` |
| `fix` | Bug fix | `fix(marts): correct null handling` |
| `docs` | Documentation | `docs: update CLAUDE.md` |
| `style` | Formatting/SQL | `style(models): improve CTE format` |
| `refactor` | Code restructure | `refactor(macros): extract logic` |
| `test` | Tests | `test(staging): add schema tests` |
| `chore` | Maintenance | `chore: update dependencies` |

### Scope (Optional)

Area of codebase: `staging`, `marts`, `macros`, `sources`, etc.

## Commit Workflow

### 1. Pre-Commit Validation

```
git: validates:
- [ ] Message follows Conventional Commits format
- [ ] Type is valid (feat, fix, docs, style, refactor, test, chore)
- [ ] First line < 72 characters
- [ ] Imperative mood ("add" not "added")
- [ ] Not committing to main/master directly
```

### 2. File Staging

```bash
# git: stages SPECIFIC files (never git add .)
git add [specific-files]

# Warning issued if staging:
# - .env files
# - Credentials
# - Large binaries
# - Unintended files
```

### 3. Commit Execution

```bash
# git: sets authorization and executes
GIT_MASTER_AUTHORIZED=true git commit -m "$(cat <<'EOF'
type(scope): description

Optional body with more context.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 4. Post-Commit Logging

- Operation logged to audit trail
- Commit hash recorded
- Timestamp captured

## Interactive Mode

When invoked without message (`/commit`), git: prompts:

1. **What changed?** → Determines type
2. **What area?** → Determines scope
3. **Brief description?** → First line
4. **More context needed?** → Body (optional)
5. **Which files?** → Staging selection

## Validation Rules

### BLOCKED (Exit 1)

- Empty commit message
- Invalid type
- First line > 72 characters
- Direct commit to main/master
- Staging sensitive files without approval

### WARNED (Proceed with caution)

- Past tense in description ("added" → "add")
- Missing Co-Authored-By
- Large number of files
- No body for complex changes

### ALLOWED (Proceed)

- Valid Conventional Commits format
- Specific files staged
- Feature branch target

## Quick Commit Patterns

### Feature Work

```
/commit "feat(staging): add customer events model"
/commit "feat(marts): implement order metrics"
```

### Bug Fixes

```
/commit "fix(staging): handle null dates gracefully"
/commit "fix(marts): correct metric calculation"
```

### Documentation

```
/commit "docs: add git: agent documentation"
/commit "docs(readme): update installation steps"
```

### Refactoring

```
/commit "refactor(shared-js): extract audio player module"
/commit "refactor: consolidate duplicate CSS patterns"
```

## Error Recovery

### Invalid Message Format

```
[REJECTED] Commit message invalid: "updated the thing"

Fix: Use Conventional Commits format
Example: feat(scope): add the thing

Try again with: /commit "feat(scope): add the thing"
```

### Protected Branch

```
[REJECTED] Cannot commit directly to main

Fix: Create feature branch first
Use: /branch feat/your-feature-name
```

## Persona Integration

This command activates the **Git-Master** (`git:`) persona for validated commit creation with format enforcement and audit logging.

## Related

- [[branch.md]] - Create branches before committing
- [[../skills/git-operations.md]] - Complete git workflow reference
- [[../rules/git-workflow.md]] - Git standards and conventions
- [[../agents/git-master.md]] - Git-Master persona details
