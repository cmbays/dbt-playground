# Branch Command

Create a validated git branch through git: with naming convention enforcement.

## Usage

```
/branch [category/]name
/branch feat/feature-name
/branch fix/bug-description
```

## Examples

```
/branch feat/staging-stripe-payments
/branch fix/marts-null-handling
/branch docs/update-architecture
/branch refactor/macros-cleanup
/branch style/model-formatting
```

## Branch Naming Format

### Required Format

```
[category/]descriptive-name
```

### Valid Categories

| Category | Purpose | Example |
|----------|---------|---------|
| `feat/` | New features or content | `feat/shopping-dialogue-page` |
| `fix/` | Bug fixes | `fix/navigation-link-broken` |
| `docs/` | Documentation changes | `docs/update-architecture` |
| `refactor/` | Code restructuring | `refactor/shared-js-cleanup` |
| `style/` | Formatting changes | `style/model-cte-formatting` |
| `chore/` | Maintenance tasks | `chore/update-dependencies` |

### Naming Rules

- **kebab-case**: lowercase with hyphens
- **descriptive**: clear purpose in name
- **concise**: not excessively long
- **no spaces**: use hyphens instead

## Branch Workflow

### 1. Pre-Creation Validation

```
git: validates:
- [ ] Category prefix is valid
- [ ] Name is kebab-case
- [ ] Branch doesn't already exist
- [ ] Currently on main/master (for fresh branch)
```

### 2. Branch Creation

```bash
# git: sets authorization and executes
GIT_MASTER_AUTHORIZED=true git checkout -b [branch-name]
```

### 3. Remote Setup

```bash
# Push and set upstream tracking
GIT_MASTER_AUTHORIZED=true git push -u origin [branch-name]
```

### 4. Post-Creation Logging

- Operation logged to audit trail
- Branch name recorded
- Base commit captured

## Interactive Mode

When invoked without name (`/branch`), git: prompts:

1. **What type of change?** → Determines category
2. **Brief description?** → Determines name
3. **Confirm branch name?** → Final validation

## Validation Rules

### BLOCKED (Exit 1)

- Invalid category prefix
- Non-kebab-case name
- Branch already exists
- Reserved names (main, master, develop)

### WARNED (Proceed with caution)

- Very long branch name (>50 chars)
- Missing category prefix
- Branching from non-main base

### ALLOWED (Proceed)

- Valid category and name format
- Clean working directory
- Branching from main/master

## Quick Branch Patterns

### Feature Development

```
/branch feat/staging-payments-model
/branch feat/marts-customer-analytics
/branch feat/macros-date-utils
```

### Bug Fixes

```
/branch fix/staging-null-dates
/branch fix/marts-metric-calculation
/branch fix/source-freshness-config
```

### Documentation

```
/branch docs/update-readme
/branch docs/add-api-reference
/branch docs/architecture-diagrams
```

### Refactoring

```
/branch refactor/extract-date-macro
/branch refactor/consolidate-staging
/branch refactor/simplify-mart-logic
```

## Error Recovery

### Invalid Category

```
[REJECTED] Invalid branch category: "feature/"

Valid categories: feat/, fix/, docs/, refactor/, style/, chore/
Use: /branch feat/your-feature-name
```

### Branch Exists

```
[REJECTED] Branch already exists: feat/staging-payments

Options:
1. Switch to existing: git checkout feat/staging-payments
2. Delete and recreate: git branch -d feat/staging-payments
3. Use different name: /branch feat/staging-payments-v2
```

### Not on Main

```
[WARNING] Creating branch from feat/other-feature, not main

This may include unmerged changes from feat/other-feature.
Continue? (y/n)
```

## Branch Lifecycle

### Creation → Development → PR → Merge → Cleanup

```
1. /branch feat/new-feature     # Create
2. /commit "feat: add thing"    # Develop
3. gh pr create                 # PR (via git:)
4. gh pr merge                  # Merge (via git:)
5. git branch -d feat/new-feat  # Cleanup (via git:)
```

## Persona Integration

This command activates the **Git-Master** (`git:`) persona for validated branch creation with naming enforcement and audit logging.

## Related

- [[commit.md]] - Create commits on your branch
- [[../skills/git-operations.md]] - Complete git workflow reference
- [[../rules/git-workflow.md]] - Git standards and conventions
- [[../agents/git-master.md]] - Git-Master persona details
