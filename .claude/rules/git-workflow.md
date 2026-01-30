# Git Workflow Rules

GitHub Flow with git-master agent enforcement.

## Workflow

```text
main (always deployable)
  └── feat/add-model ──→ PR ──→ merge ──→ delete branch
```

- `main` is always deployable
- All work on feature branches
- All changes merge via PR (never push directly to main)
- Tag releases on main

## Branch Naming

`[category/]descriptive-name`

| Prefix | Purpose |
|--------|---------|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `docs/` | Documentation |
| `refactor/` | Code restructuring |
| `chore/` | Maintenance |

## Commit Messages (Conventional Commits)

`type(scope): description`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

```bash
feat(staging): add stg_stripe__payments model
fix(marts): correct null handling in dim_customers
```

## Git-Master Enforcement

All git write operations go through git-master agent for safety.

| Command | Purpose |
|---------|---------|
| `/commit` | Create validated commit |
| `/branch` | Create validated branch |
| `git: [request]` | General git operation |

### Blocked Operations

Direct git writes are blocked by hook:

```bash
# BLOCKED - use git: prefix instead
git commit -m "..."
git push origin main
```

### Protected Operations (Need Explicit Approval)

- `git push --force`
- `git reset --hard`
- Force push to main/master
- `gh pr merge` without review

## Git Worktrees (Parallel Sessions)

Git worktrees enable multiple Claude Code sessions to work simultaneously on different features without conflicts.

### Worktree Creation

All worktree operations go through git-master:

```bash
git: create worktree for feat/customer-analytics
```

Git-master will:

1. Create branch from main
2. Create worktree directory as sibling (`../dbt-playground--customer-analytics`)
3. Push branch to origin
4. Create draft PR for visibility

### Worktree Rules

| Rule | Enforcement |
|------|-------------|
| One branch per worktree | Git enforces (cannot checkout same branch in two places) |
| Push after each commit | Other worktrees see changes via `git fetch` |
| Clean up after merge | `git worktree remove`, then delete branch |

### Directory Convention

Worktrees are siblings to the main repo:

```text
~/projects/
├── dbt-playground/                    # Main repo
├── dbt-playground--customer-analytics/ # Worktree
└── dbt-playground--tuva/               # Worktree
```

### Draft PR Workflow

```bash
# At worktree creation, create draft PR immediately
cd ../dbt-playground--feat-x
git push -u origin feat/x
gh pr create --draft --title "feat: description" --body "WIP scope"
```

This ensures all parallel work is visible in GitHub.

## Versioning

`vMAJOR.MINOR.PATCH` (Semantic Versioning)

- MAJOR: Architecture change
- MINOR: New features
- PATCH: Bug fixes

Tag when there's meaningful user-facing change.
