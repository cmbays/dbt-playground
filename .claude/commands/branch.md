# Branch Command

Create a validated git branch through git: with naming convention enforcement.

## Usage

```
/branch [category/]name [--with-pr] [--no-pr]
/branch feat/feature-name
/branch fix/bug-description
/branch feat/new-feature --with-pr "Feature description"
```

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--with-pr` | **ON** | Create draft PR immediately after branch creation |
| `--no-pr` | off | Skip draft PR creation (branch only) |

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

### 4. Draft PR Creation (Default: ON)

When `--with-pr` is enabled (default), git-master creates a draft PR:

```bash
# Create draft PR with scope in description
gh pr create --draft \
  --title "[type]: [brief description]" \
  --body "## Scope

[User-provided description or placeholder]

## Status
- [ ] Implementation in progress
- [ ] Tests passing
- [ ] Ready for review

---
*Draft PR created automatically by git-master*"
```

**Why draft PR at branch creation?**

- Captures development context early
- Makes parallel work visible to team
- PR description becomes source of truth for scope
- Enables cross-session visibility via `gh pr view`

### 5. Post-Creation Logging

- Operation logged to audit trail
- Branch name recorded
- Base commit captured
- PR number recorded (if created)

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

## Branch Lifecycle (PR-First Workflow)

### Creation → Development → Review → Post-Review → Merge → Cleanup

```
1. /branch feat/new-feature         # Creates branch + draft PR
2. /commit "feat: add thing"        # Develop (regular commits)
3. gh pr ready                      # Mark PR ready for review
4. [Multi-agent review via super:]  # Code/Security/Design reviewers
5. [Post-review queue]              # Docs/Sage/PM updates
6. super: APPROVED                  # Supervisor final approval
7. git: merge PR #N                 # Merge (via git-master)
8. [Auto-cleanup]                   # Branch + worktree removed
```

### Draft PR at Creation

The default `--with-pr` flag means:

- Draft PR created immediately with branch
- PR description captures feature scope
- All development visible in PR from start
- Cross-session agents can read PR context via `gh pr view`

## Persona Integration

This command activates the **Git-Master** (`git:`) persona for validated branch creation with naming enforcement and audit logging.

## Related

- [[commit.md]] - Create commits on your branch
- [[../skills/git-operations.md]] - Complete git workflow reference
- [[../rules/git-workflow.md]] - Git standards and conventions
- [[../agents/git-master.md]] - Git-Master persona details
