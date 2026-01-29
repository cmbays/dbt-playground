# Git Workflow Rules

Standards for version control, branching, commits, and releases.

## Workflow: GitHub Flow

This project uses **GitHub Flow** (simple, not Git Flow):

```text
main (always deployable)
  │
  ├── feat/add-model ──→ PR ──→ merge ──→ delete branch
  ├── fix/broken-test ──→ PR ──→ merge ──→ delete branch
  ├── docs/update-readme ──→ PR ──→ merge ──→ delete branch
  │
  └── tag v0.2.0 (when milestone reached)
```

**Key principles:**

- `main` is always deployable
- All work on feature branches
- Merge via PR (or direct for tiny changes)
- Delete branches after merge
- Tag releases directly on main
- No `develop` or `release/` branches

## Branch Naming

### Format

`[category/]descriptive-name`

### Categories

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feat/` | New features or content | `feat/add-patients-model` |
| `fix/` | Bug fixes | `fix/broken-test` |
| `docs/` | Documentation changes | `docs/update-architecture` |
| `refactor/` | Code restructuring | `refactor/cleanup-staging` |
| `style/` | CSS/styling changes | `style/format-sql` |
| `chore/` | Maintenance tasks | `chore/update-dependencies` |

### Guidelines

- Use kebab-case (lowercase with hyphens)
- Be descriptive but concise
- Include issue number if applicable: `fix/nav-bug-#12`

## Commit Messages

### Format (Conventional Commits)

```
type(scope): description

[optional body]

[optional footer]
```

### Types

| Type | Purpose |
|------|---------|
| `feat` | New feature or content |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, CSS (no logic change) |
| `refactor` | Code restructuring |
| `test` | Adding or updating tests |
| `chore` | Maintenance, dependencies |

### Scope (Optional)

Area of codebase: `shopping`, `kanji`, `shared-css`, `nav`

### Examples

```
feat(restaurant): add dialogue page with audio support
fix(nav): correct broken link to home-life index
docs: update CLAUDE.md with development conventions
style(flashcards): improve hover state transitions
refactor(shared-js): extract audio player into function
chore: update .gitignore for temp files
```

### Guidelines

- Use imperative mood ("add" not "added")
- Keep first line under 72 characters
- Add body for complex changes
- Reference issues: `fix(nav): resolve broken link (#12)`

## Pull Requests

### Title Format

Same as commit messages: `type(scope): description`

### Description Template

```markdown
## Summary
Brief description (1-3 sentences)

## Changes
- Bullet list of changes
- Include files added/modified
- Note breaking changes

## Testing
- How was this tested?
- What should reviewers verify?

## Related
- Links to issues, PRs, documentation
- Reference to prototype/design
```

## Versioning

### Semantic Versioning

`vMAJOR.MINOR.PATCH`

| Component | When to Increment |
|-----------|-------------------|
| MAJOR | Complete topic or major architecture change |
| MINOR | New features, pages, content additions |
| PATCH | Bug fixes, small corrections, typos |

### Git Tags

```bash
# Create annotated tag
git tag -a v0.3.0 -m "Complete shopping dialogue page"

# Push tag
git push origin v0.3.0

# List tags
git tag -l

# View tag details
git show v0.3.0
```

### When to Tag

- After merging significant PRs
- At version milestones
- Before major refactoring (restore point)

### When NOT to Tag

Not every merge requires a version bump. These accumulate in `[Unreleased]`:

| Change Type | Version Bump? | Example |
|-------------|---------------|---------|
| New feature | MINOR | Adding staging models |
| Bug fix | PATCH | Fixing broken test |
| Docs only | No | Updating README |
| Chores | No | Dependency updates |
| Refactors | No (usually) | Code cleanup |
| Style/format | No | SQL formatting |

**Rule**: Tag when there's meaningful user-facing change or milestone completion.

## Branch Hygiene

### Delete After Merge

Always delete branches after merging to keep the repo tidy:

```bash
# Delete local branch
git branch -d feat/my-feature

# Delete remote branch
git push origin --delete feat/my-feature

# Prune stale remote tracking branches
git fetch --prune
```

### GitHub Auto-Delete

Enable "Automatically delete head branches" in repo settings to auto-cleanup after PR merge.

### Periodic Cleanup

```bash
# List merged branches (safe to delete)
git branch --merged main

# Delete all merged local branches except main
git branch --merged main | grep -v "main" | xargs git branch -d
```

## Protected Operations

### NEVER Do Without Explicit Approval

- `git push --force` or `git push -f`
- `git reset --hard`
- `git checkout .` or `git restore .`
- `git clean -f`
- `git branch -D`
- Force push to main/master

### Always Get Approval For

- Rebasing shared branches
- Amending pushed commits
- Deleting branches with unmerged work
- Resetting to previous commits

## Workflow

### Feature Development

```bash
# Create feature branch
git checkout -b feat/feature-name

# Make changes, commit incrementally
git add [specific files]
git commit -m "feat(scope): description"

# Push branch
git push -u origin feat/feature-name

# Create PR for review
gh pr create --title "feat(scope): description" --body "..."
```

### Bug Fixes

```bash
git checkout -b fix/bug-description
# Fix the bug
git add [files]
git commit -m "fix(scope): description"
git push -u origin fix/bug-description
gh pr create
```

### Commit Hygiene

- Commit frequently with clear messages
- Each commit should be a logical unit
- Don't commit broken code
- Don't commit large unrelated changes together

## Archive Retention

### Policy

- Keep most recent of every MAJOR version
- Keep most recent 3 of current MAJOR version
- Pre-v1.0 treated as current major for retention

### Archive Process

```bash
# Before deploying new version
mkdir -p archive/v0.3/docs
cp docs/*.md archive/v0.3/docs/

# Prune old archives per policy
# (Keep v0.5, v0.4, v0.3 if current major is v0)
```

## Safety Checks

### Before Committing

- [ ] Run tests (if applicable)
- [ ] Check `git status` for unexpected files
- [ ] Review `git diff` for unintended changes
- [ ] Verify no sensitive data in changes

### Before Pushing

- [ ] Commits have clear messages
- [ ] No debug code left in
- [ ] Documentation updated if needed

### Before Merging

- [ ] PR approved by reviewer
- [ ] All checks pass
- [ ] Conflicts resolved properly
- [ ] Version tag planned

## Agent Git Governance

### Git-Master Enforcement

All git write operations in this project are managed through the Git-Master agent (`git:` prefix) for safety, validation, and audit trails.

### Enforcement Layers

```
Layer 1: CLAUDE.md Rules
├── "Agents MUST use git: for git operations"
│
Layer 2: pre-bash-check.js Hook
├── BLOCKS git write operations without authorization
├── Checks GIT_MASTER_AUTHORIZED env var
├── Exit 1 if unauthorized
│
Layer 3: Git-Master Agent
├── Validates format (Conventional Commits, branch names)
├── Sets GIT_MASTER_AUTHORIZED=true
└── Logs all operations to audit trail
```

### Commands

| Command | Purpose |
|---------|---------|
| `/commit` | Create validated commit |
| `/branch` | Create validated branch |
| `git: [request]` | General git operation |

### Examples

```bash
# Branch creation
git: create branch feat/new-feature

# Commit
git: commit my changes with message "feat(kanji): add filter"
# Or use command
/commit "feat(kanji): add filter"

# Tag creation
git: create tag v0.3.0 "Description"

# PR creation
git: create PR for current branch

# Merge
git: merge PR #44
```

### What Gets Blocked

Direct git write commands are blocked by the hook:

```bash
# BLOCKED - use git: prefix instead
git commit -m "..."
git push origin main
git tag -a v0.3.0 -m "..."
git checkout -b feat/something
gh pr create
gh pr merge
```

### Bypass (Emergency Only)

For emergencies, add `--bypass-git-master` flag (logged to audit):

```bash
git commit -m "emergency fix" --bypass-git-master
```

**Warning**: Bypass usage is logged. Use only when git-master is unavailable.

### Audit Trail

All git-master operations logged to `temp/GIT_AUDIT_LOG.txt` (gitignored):

```
[2026-01-25T10:30:00Z] BRANCH_CREATE
  Branch: feat/kanji-filter
  Base: main (abc1234)

[2026-01-25T10:35:00Z] COMMIT
  Hash: def5678
  Message: feat(kanji): add JLPT filtering
  Files: 3 changed
```

### Related

- [[../agents/git-master.md]] - Git-Master persona
- [[../skills/git-operations.md]] - Detailed workflows
- [[../commands/commit.md]] - Commit command
- [[../commands/branch.md]] - Branch command
