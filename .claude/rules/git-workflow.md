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

## Versioning

`vMAJOR.MINOR.PATCH` (Semantic Versioning)

- MAJOR: Architecture change
- MINOR: New features
- PATCH: Bug fixes

Tag when there's meaningful user-facing change.
