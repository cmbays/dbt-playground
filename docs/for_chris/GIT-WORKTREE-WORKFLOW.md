---
audience: [human, sage]
priority: high
size: medium
last_updated: 2026-01-29
status: active
tags: [learning, git, workflow, parallel-development, multi-session]
---

# Git Worktrees: Parallel Development for Multi-Session Workflows

**Topic**: Using git worktrees to run multiple Claude Code sessions in parallel, each working on different features without conflicts

**Context**: When you have 3+ Claude Code terminals open, each as a "team" working on separate features, git worktrees provide isolation while sharing the same repository

**Why this matters**: Without worktrees, multiple sessions fight over the same working directory. With worktrees, each session has its own sandbox while sharing commits instantly.

---

## The Problem: One Directory, Many Sessions

Imagine this scenario:

- Terminal 1: Claude is building customer analytics (on `feat/customer-analytics`)
- Terminal 2: Claude is fixing a production bug (on `fix/null-handling`)
- Terminal 3: Claude is writing documentation (on `docs/api-reference`)

Without worktrees, they're all operating on the same directory. When Terminal 2 switches to `fix/null-handling`, it overwrites the uncommitted changes from Terminal 1's work on customer analytics.

You end up with:

- Constant stashing and unstashing
- "Wait, whose changes are these?"
- Lost work when branches switch
- Agents stepping on each other's files

**Worktrees solve this by giving each branch its own directory.**

---

## The Mental Model: Same Brain, Different Hands

Think of your git repository as a brain (the `.git` directory), and worktrees as hands:

```
                 ┌─────────────────────────────────────┐
                 │          .git (the brain)           │
                 │   commits, branches, history        │
                 └──────────────┬──────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Main Repo     │  │   Worktree 1    │  │   Worktree 2    │
│   (main)        │  │ (feat/customer) │  │ (fix/null)      │
│                 │  │                 │  │                 │
│  dbt-playground │  │ ../wt-customer  │  │ ../wt-null-fix  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

All three directories:

- Share the same commit history
- See each other's pushed commits instantly
- Can independently stage, commit, and push
- Have their own working files

**Key insight**: When you commit in one worktree and push, other worktrees can see it with `git fetch`. No merging needed - they share the same repository.

---

## Core Concepts

### What Is a Worktree?

A worktree is a checked-out branch in a separate directory. Each worktree:

- Has its own working directory (files you edit)
- Has its own index (staging area)
- Shares the `.git` database with the main repo
- Is locked to one branch (can't checkout the same branch twice)

### Main Repo vs. Worktree Directories

```
# Main repository (original clone)
~/projects/dbt-playground/
├── .git/                    # The shared brain
├── dbt_project/             # Working files for main
├── docs/
└── ...

# Worktree for customer analytics
~/projects/wt-customer-analytics/
├── .git                     # File pointing to main .git
├── dbt_project/             # Working files for this branch
├── docs/
└── ...
```

The worktree's `.git` is a file (not a directory) that points to the main `.git`:

```bash
$ cat ~/projects/wt-customer-analytics/.git
gitdir: /Users/chris/projects/dbt-playground/.git/worktrees/wt-customer-analytics
```

### Branch Locking: One Branch, One Worktree

Git prevents checking out the same branch in multiple worktrees:

```bash
# In main repo, on feat/customer-analytics
$ cd ~/projects/wt-null-fix
$ git checkout feat/customer-analytics
fatal: 'feat/customer-analytics' is already checked out at '/Users/chris/projects/dbt-playground'
```

This is a feature, not a bug. It prevents two sessions from editing the same branch and creating conflicts.

---

## Essential Commands

### Create a Worktree

```bash
# Create worktree for an existing branch
git worktree add ../wt-customer-analytics feat/customer-analytics

# Create worktree with a new branch (from current HEAD)
git worktree add -b feat/new-feature ../wt-new-feature

# Create worktree with new branch from specific base
git worktree add -b fix/urgent ../wt-urgent main
```

**Naming convention**: Prefix with `wt-` to easily identify worktree directories.

### List Worktrees

```bash
$ git worktree list
/Users/chris/projects/dbt-playground           abc1234 [main]
/Users/chris/projects/wt-customer-analytics    def5678 [feat/customer-analytics]
/Users/chris/projects/wt-null-fix              ghi9012 [fix/null-handling]
```

### Remove a Worktree

```bash
# Remove after merging (clean removal)
git worktree remove ../wt-customer-analytics

# Force remove (if uncommitted changes)
git worktree remove --force ../wt-customer-analytics

# Clean up stale worktree entries (if directory was deleted manually)
git worktree prune
```

### Move a Worktree

```bash
# Rename or relocate
git worktree move ../wt-old-name ../wt-new-name
```

---

## Workflow with Claude Code

### Starting a New Track

When you want to start a parallel work stream:

```bash
# 1. Create branch and worktree together
cd ~/projects/dbt-playground
git worktree add -b feat/order-metrics ../wt-order-metrics main

# 2. Create draft PR immediately (so work is tracked)
cd ../wt-order-metrics
gh pr create --draft --title "feat: add order metrics" --body "WIP"

# 3. Open new terminal in that directory
# (or tell Claude which directory to work in)
```

### Which Terminal Works Where

Assign each terminal a clear purpose:

| Terminal | Directory | Branch | Purpose |
|----------|-----------|--------|---------|
| 1 | `dbt-playground` | `main` | Coordination, merges, releases |
| 2 | `wt-customer-analytics` | `feat/customer-analytics` | Customer analytics feature |
| 3 | `wt-order-metrics` | `feat/order-metrics` | Order metrics feature |
| 4 | `wt-hotfix` | `fix/urgent` | Production hotfixes |

### How Claude Knows Where It Is

Claude Code automatically detects its working directory. At the start of each session, verify:

```bash
# Claude should report this
pwd
# → /Users/chris/projects/wt-customer-analytics

git branch --show-current
# → feat/customer-analytics
```

**Tip**: Include context at session start:

```
You are working in the customer-analytics worktree.
Focus: Building the dim_customers and fct_orders marts.
Branch: feat/customer-analytics
```

### Committing and Pushing from Worktrees

Works exactly like normal git:

```bash
# In worktree directory
git add .
git commit -m "feat(marts): add dim_customers model"
git push origin feat/customer-analytics
```

Other worktrees see the pushed commits after `git fetch`:

```bash
# In a different worktree
git fetch
git log origin/feat/customer-analytics --oneline -3
```

### Merging and Cleanup

When a feature is complete:

```bash
# 1. Merge PR (via GitHub or CLI)
gh pr merge feat/customer-analytics --squash

# 2. Switch to main repo
cd ~/projects/dbt-playground

# 3. Update main
git checkout main
git pull

# 4. Remove the worktree
git worktree remove ../wt-customer-analytics

# 5. Delete the branch (if not auto-deleted by merge)
git branch -d feat/customer-analytics
```

---

## Common Scenarios

### "I want to start a new feature while v0.4 is in progress"

```bash
# From main repo
cd ~/projects/dbt-playground

# Create worktree from main (not from v0.4 branch)
git worktree add -b feat/new-thing ../wt-new-thing main

# Now you have:
# - wt-new-thing: clean slate from main
# - dbt-playground: still on feat/v0.4-work
```

### "I need to hotfix main while other work continues"

```bash
# Create hotfix worktree
git worktree add -b fix/production-bug ../wt-hotfix main

# Work in hotfix terminal
cd ../wt-hotfix
# ... fix the bug ...
git commit -am "fix: resolve null handling in staging"
git push origin fix/production-bug

# Merge quickly, then cleanup
gh pr create --title "fix: production null handling" --body "Urgent fix"
gh pr merge --squash
git worktree remove ../wt-hotfix
```

Other worktrees are unaffected and continue their work.

### "Two features need to merge - which goes first?"

Consider dependencies:

1. **Independent features**: Merge in any order
2. **Feature B depends on Feature A**: Merge A first, then rebase B on main before merging

```bash
# After merging feature A
cd ../wt-feature-b
git fetch
git rebase origin/main
# Resolve any conflicts
git push --force-with-lease
```

### "I'm done with a track - how to clean up"

Full cleanup checklist:

```bash
# 1. Ensure all changes committed and pushed
cd ../wt-feature-x
git status  # Should be clean
git push

# 2. Merge the PR
gh pr merge --squash

# 3. Go to main repo
cd ~/projects/dbt-playground

# 4. Update main
git pull origin main

# 5. Remove worktree
git worktree remove ../wt-feature-x

# 6. Delete remote branch (if not auto-deleted)
git push origin --delete feat/feature-x

# 7. Prune any stale references
git worktree prune
git fetch --prune
```

---

## Tips for Working with Claude

### Tell Claude Which Worktree at Session Start

Include context in your initial prompt:

```
Working in: ~/projects/wt-customer-analytics
Branch: feat/customer-analytics
Task: Build dim_customers dimension model

The main dbt-playground repo is at ~/projects/dbt-playground.
```

### Use Supervisor Status to See All Tracks

```
super: status
```

This shows all active workflow tracks, which often map to worktrees.

### How Claude Can Detect Worktree Context

Claude Code sees the working directory automatically:

```bash
# Claude can run this to orient itself
git worktree list
pwd
git branch --show-current
```

If you switch terminals, remind Claude:

```
Now working in wt-order-metrics worktree (feat/order-metrics branch).
```

---

## Gotchas and Pitfalls

### Can't Checkout Same Branch in Two Worktrees

```bash
# This will fail if feat/x is checked out elsewhere
git checkout feat/x
# fatal: 'feat/x' is already checked out at '/path/to/other/worktree'
```

**Solution**: Each parallel track needs its own branch. Plan branch names ahead.

### Need to Push for Other Worktrees to See Commits

Worktrees share the git database but not uncommitted changes:

```bash
# Worktree A commits locally
git commit -m "add feature"

# Worktree B cannot see this until A pushes
# In Worktree A:
git push

# In Worktree B:
git fetch
git log origin/feat/a --oneline
```

**Pattern**: Commit early, push often. Especially at natural breakpoints.

### Worktrees and Node Modules / Python Venvs

Each worktree has its own working directory, so dependencies need installing:

```bash
# In each new worktree
cd ../wt-new-feature
uv sync                  # Python dependencies
npm install              # Node dependencies (if any)
```

These are separate installs but use the same lockfiles.

### Absolute vs. Relative Paths in Scripts

Scripts should use paths relative to the project root, not absolute paths. This ensures they work in any worktree.

```bash
# Good: relative to project root
dbt run --project-dir ./dbt_project

# Bad: hardcoded absolute path
dbt run --project-dir /Users/chris/projects/dbt-playground/dbt_project
```

### Don't Delete Worktree Directories Manually

Always use `git worktree remove`:

```bash
# Wrong
rm -rf ../wt-old-feature

# Right
git worktree remove ../wt-old-feature
```

If you do delete manually, run `git worktree prune` to clean up stale entries.

---

## Directory Layout Recommendation

Keep worktrees as siblings to the main repo:

```
~/projects/
├── dbt-playground/              # Main repo (main branch)
├── wt-customer-analytics/       # Worktree (feat/customer-analytics)
├── wt-order-metrics/            # Worktree (feat/order-metrics)
└── wt-hotfix/                   # Worktree (fix/urgent)
```

Benefits:

- Easy to `cd ../wt-*` between worktrees
- All project work in one parent directory
- Clear visual separation
- `wt-` prefix makes worktrees obvious

---

## Quick Reference Card

```bash
# Create worktree with new branch
git worktree add -b feat/name ../wt-name main

# Create worktree for existing branch
git worktree add ../wt-name existing-branch

# List all worktrees
git worktree list

# Remove worktree (clean)
git worktree remove ../wt-name

# Remove worktree (force, uncommitted changes)
git worktree remove --force ../wt-name

# Clean up stale entries
git worktree prune

# See which branch each worktree has
git worktree list --porcelain
```

---

## Key Takeaways

1. **Worktrees = Parallel Sandboxes**: Same git brain, different working hands
2. **One Branch Per Worktree**: Git enforces this to prevent conflicts
3. **Push to Share**: Worktrees share commits through the remote
4. **Clean Up After Merge**: Remove worktree, prune, delete branch
5. **Context at Session Start**: Tell Claude which worktree it's in

---

## Related Reading

- [Supervisor Orchestration](./SUPERVISOR_ORCHESTRATION.md) - Multi-track workflow management
- [Git Workflow Rules](../../.claude/rules/git-workflow.md) - Branch naming and commit conventions
- [Git Documentation: git-worktree](https://git-scm.com/docs/git-worktree) - Official reference

---

*The best parallel workflows are the ones where each track forgets the others exist - until it's time to merge.*
