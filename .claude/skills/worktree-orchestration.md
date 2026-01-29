# Worktree Orchestration Skill

Git worktree management for parallel development with conflict prevention.

## Overview

This skill enables parallel development using git worktrees while preventing conflicts through shared file detection and coordination protocols.

## Trigger

Invoke when:
- Multiple features need parallel development
- Long-running feature shouldn't block other work
- Need isolated environments for different branches
- User requests worktree setup

## What Are Worktrees?

Git worktrees allow multiple working directories from a single repository:

```
Main Repository
├── japanese-study-site/           # Main worktree (main branch)
├── japanese-study-site-feat-a/    # Worktree for feat/feature-a
└── japanese-study-site-feat-b/    # Worktree for feat/feature-b
```

Each worktree has its own:
- Working directory
- Checked out branch
- Staging area

But shares:
- Git objects database
- Remote configuration
- Hooks

## When to Use Worktrees

### USE Worktrees When:

| Scenario | Reason |
|----------|--------|
| Two independent topics | No shared files, parallel safe |
| Long-running feature | Don't block other work |
| Parallel kanji data updates | Data files isolated |
| A/B testing implementations | Compare approaches |
| Review while developing | Keep review context separate |

### DON'T Use Worktrees When:

| Contraindication | Reason | Alternative |
|------------------|--------|-------------|
| Quick tasks (<15 min) | Setup overhead exceeds benefit | Branch switch |
| Shared file modifications | Merge conflicts likely | Sequential development |
| Storage constraints | Each worktree duplicates files | Monitor disk space |
| Same files across worktrees | High conflict risk | Designate primary |

## Worktree Decision Matrix

```
Is task < 15 minutes?
├── YES → Use branch switch, skip worktree
└── NO → Continue

Do features modify shared files?
├── YES → Sequential development or coordinate
└── NO → Continue

Is disk space constrained?
├── YES → Monitor usage, limit worktrees
└── NO → Continue

Are features truly independent?
├── YES → Create worktrees
└── NO → Plan coordination strategy
```

## High-Risk Shared Files (This Project)

These files should NOT be modified in parallel worktrees:

```
content/css/shared.css    # Global styles - central dependency
content/js/shared.js      # Global JavaScript - central dependency
CLAUDE.md                 # Project instructions - must stay in sync
.claude/rules/*.md        # Agent rules - coordination needed
.claude/agents/*.md       # Agent personas - coordination needed
docs/ARCHITECTURE.md      # Living documentation - single source
CHANGELOG.md              # Release history - single source
```

### Shared File Detection

Before creating worktrees, git-master analyzes each feature's scope:

```
git-master: setup worktrees for feat/a and feat/b

[ANALYZING] Feature scopes for conflict detection...

feat/a modifies:
  - topics/shopping/dialogue.html
  - topics/shopping/quiz.html

feat/b modifies:
  - topics/restaurant/story.html
  - topics/restaurant/tips.html

[RESULT] No shared file conflicts detected.
         Safe to proceed with parallel worktrees.
```

### Conflict Warning Example

```
git-master: setup worktrees for feat/a and feat/b

[ANALYZING] Feature scopes for conflict detection...

feat/a modifies:
  - content/css/shared.css    ⚠️ SHARED
  - topics/shopping/dialogue.html

feat/b modifies:
  - content/css/shared.css    ⚠️ SHARED
  - topics/restaurant/story.html

[WARNING] Both features modify shared.css

Options:
1. Sequential: Complete feat/a first, then feat/b
2. Coordinate: Designate one worktree as primary for shared.css
3. Override: Proceed with awareness (merge conflicts likely)

Choose [1/2/3]:
```

## Worktree Workflow

### Phase 1: Planning

```
1. List features for parallel development
2. Analyze each feature's file scope
3. Check for shared file conflicts
4. Get user approval if conflicts detected
```

### Phase 2: Creation

```bash
# Create worktree directories
git worktree add ../japanese-study-site-feat-a feat/feature-a
git worktree add ../japanese-study-site-feat-b feat/feature-b

# Verify creation
git worktree list
```

### Phase 3: Registry

Create worktree registry for tracking:

```json
// temp/WORKTREE_REGISTRY.json (gitignored)
{
  "created": "2026-01-25T10:00:00Z",
  "worktrees": [
    {
      "path": "../japanese-study-site-feat-a",
      "branch": "feat/feature-a",
      "status": "active",
      "owner": "developer-1",
      "scope": ["topics/shopping/*"],
      "created": "2026-01-25T10:00:00Z"
    },
    {
      "path": "../japanese-study-site-feat-b",
      "branch": "feat/feature-b",
      "status": "active",
      "owner": "developer-2",
      "scope": ["topics/restaurant/*"],
      "created": "2026-01-25T10:00:00Z"
    }
  ],
  "shared_files_locked": [],
  "conflicts_detected": []
}
```

### Phase 4: Development

Work proceeds in each worktree independently:

```bash
# In worktree A
cd ../japanese-study-site-feat-a
# Make changes, commit, push

# In worktree B
cd ../japanese-study-site-feat-b
# Make changes, commit, push
```

### Phase 5: Cleanup

After features are merged:

```bash
# Remove worktrees
git worktree remove ../japanese-study-site-feat-a
git worktree remove ../japanese-study-site-feat-b

# Prune stale references
git worktree prune

# Update registry
# Remove entries from WORKTREE_REGISTRY.json
```

## Commands Reference

### Create Worktree
```bash
# From existing branch
git worktree add <path> <branch>

# Create new branch
git worktree add -b <new-branch> <path> <base-branch>
```

### List Worktrees
```bash
git worktree list
```

### Remove Worktree
```bash
# Clean removal
git worktree remove <path>

# Force removal (if dirty)
git worktree remove --force <path>
```

### Prune Stale References
```bash
git worktree prune
```

## Coordination Protocols

### Protocol 1: Shared File Lock

When one worktree needs to modify a shared file:

```
1. Announce: "Locking shared.css for feat/a"
2. Update registry: Add to shared_files_locked
3. Other worktrees: Cannot modify that file
4. Complete work: Merge feat/a
5. Release: Remove from shared_files_locked
```

### Protocol 2: Sequential Sections

For large shared files with distinct sections:

```
1. Define sections: "feat/a owns .flashcard-*, feat/b owns .quiz-*"
2. Document in registry
3. Each worktree only modifies their section
4. Merge order doesn't matter
```

### Protocol 3: Rebase Coordination

Keep worktrees current with main:

```bash
# In each worktree periodically
git fetch origin main
git rebase origin/main

# Or for feature branches
git pull --rebase origin main
```

## Troubleshooting

### Error: Branch Already Checked Out

```
fatal: 'feat/a' is already checked out at '/path/to/other/worktree'
```

**Solution**: Each branch can only be checked out in one worktree.

### Error: Worktree Locked

```
fatal: working tree '/path' is locked
```

**Solution**:
```bash
git worktree unlock /path
# or remove lock file
rm /path/.git/worktrees/name/locked
```

### Stale Worktree

If worktree directory was deleted manually:

```bash
git worktree prune
```

## Best Practices

### 1. Limit Active Worktrees
- 2-3 maximum recommended
- Each consumes disk space
- Context switching overhead

### 2. Clear Naming
```
../project-feat-shopping-quiz    # Clear purpose
../project-wt1                    # Unclear
```

### 3. Regular Sync
- Rebase worktrees from main weekly
- Prevents large merge conflicts later

### 4. Clean Exit
- Always `git worktree remove`, don't just delete
- Run `git worktree prune` periodically

### 5. Document Ownership
- Registry shows who owns what
- Prevents accidental conflicts

## Integration with Git-Master

Git-master orchestrates worktrees through Workflow F:

```
git-master: setup worktrees for feat/a and feat/b

1. Validate branch names
2. Analyze file scope conflicts
3. Get approval if needed
4. Create worktrees
5. Update registry
6. Assign ownership
7. Log to audit trail
```

## Related Documentation

- [[git-operations.md]] - Core git workflows
- [[../commands/branch.md]] - Branch creation
- [[../agents/git-master.md]] - Git-Master persona
- [[../rules/git-workflow.md]] - Git standards
