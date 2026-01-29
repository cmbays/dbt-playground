# Git Operations Skill

Step-by-step git workflows with validation, executed through git-master.

## Overview

This skill provides validated git operations ensuring safety, format compliance, and audit trails. All git write operations go through git-master for enforcement.

## Trigger

Invoke when:

- Creating branches, commits, tags, or PRs
- Merging or pushing changes
- Any git write operation needed
- User requests `git:` prefixed operation

## Enforcement Layers

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: CLAUDE.md Rules (Social Contract)             │
│  "Agents MUST use git-master for git operations"        │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: pre-bash-check.js Hook (Technical Gate)       │
│  - Blocks git write operations without authorization    │
│  - Checks GIT_MASTER_AUTHORIZED env var                 │
│  - Exit 1 if unauthorized                               │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: Git-Master Agent (Validation + Execution)     │
│  - Validates format before executing                    │
│  - Sets GIT_MASTER_AUTHORIZED=true                      │
│  - Logs all operations to audit trail                   │
└─────────────────────────────────────────────────────────┘
```

## Workflow A: Create Feature Branch

### Input

- Branch name (validated against naming conventions)
- Base branch (default: main)

### Process

```
1. Validate branch name format
   - Must be [category/]kebab-case-name
   - Valid categories: feat/, fix/, docs/, refactor/, style/, chore/

2. Check branch doesn't already exist
   git branch --list [branch-name]

3. Verify clean working directory
   git status --porcelain

4. Create and switch to branch
   GIT_MASTER_AUTHORIZED=true git checkout -b [branch-name]

5. Push and set upstream
   GIT_MASTER_AUTHORIZED=true git push -u origin [branch-name]

6. Log to audit trail
   - Timestamp
   - Branch name
   - Base commit
```

### Output

- Branch created locally and on remote
- Upstream tracking configured
- Audit log updated

## Workflow B: Create Validated Commit

### Input

- Commit message (validated against Conventional Commits)
- Files to stage (specific list, never `git add .`)

### Process

```
1. Validate commit message format
   - Pattern: type(scope): description
   - Valid types: feat, fix, docs, style, refactor, test, chore
   - First line < 72 characters
   - Imperative mood

2. Validate not on protected branch
   current=$(git branch --show-current)
   if [[ "$current" == "main" || "$current" == "master" ]]; then
     REJECT "Cannot commit directly to $current"
   fi

3. Check files for sensitive content
   - No .env files
   - No credentials
   - No large binaries

4. Stage specific files
   GIT_MASTER_AUTHORIZED=true git add [file1] [file2] ...

5. Create commit with HEREDOC
   GIT_MASTER_AUTHORIZED=true git commit -m "$(cat <<'EOF'
   type(scope): description

   Optional body.

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"

6. Log to audit trail
   - Timestamp
   - Commit hash
   - Message summary
   - Files changed
```

### Output

- Commit created with validated message
- Audit log updated

## Workflow C: Create Semantic Version Tag

### Input

- Tag name (validated against semver)
- Tag message/description

### Process

```
1. Validate semantic version format
   - Pattern: vMAJOR.MINOR.PATCH
   - Example: v0.3.0, v1.0.0

2. Check tag doesn't already exist
   git tag --list [tag-name]

3. Create annotated tag
   GIT_MASTER_AUTHORIZED=true git tag -a [tag] -m "[message]"

4. Push tag to remote
   GIT_MASTER_AUTHORIZED=true git push origin [tag]

5. Log to audit trail
```

### Output

- Tag created locally and on remote
- Audit log updated

## Workflow D: Create Pull Request

### Input

- Source branch
- Target branch (default: main)
- PR title (Conventional Commits format)
- PR body (template sections required)

### Process

```
1. Verify branch is pushed to remote
   git ls-remote --heads origin [branch]

2. Validate PR title format
   - Must follow Conventional Commits

3. Validate PR body has required sections
   - ## Summary (1-3 sentences)
   - ## Changes (bullet list)
   - ## Testing (verification steps)
   - ## Related (links)

4. Create PR via gh CLI
   GIT_MASTER_AUTHORIZED=true gh pr create \
     --title "[title]" \
     --body "$(cat <<'EOF'
   ## Summary
   ...

   ## Changes
   ...

   ## Testing
   ...

   ## Related
   ...
   EOF
   )"

5. Log to audit trail
```

### Output

- PR created with URL
- Audit log updated

## Workflow E: Merge PR with Safety Checks

### Input

- PR number

### Process

```
1. Fetch PR details
   gh pr view [PR#] --json state,reviews,statusCheckRollup

2. Validate merge conditions
   - [ ] All required checks passed
   - [ ] At least one approval (or override)
   - [ ] No merge conflicts
   - [ ] PR title follows format

3. Execute pre-merge checklist (Workflow G)

4. Merge PR
   GIT_MASTER_AUTHORIZED=true gh pr merge [PR#] --merge

5. Cleanup branch
   git branch -d [branch-name]
   GIT_MASTER_AUTHORIZED=true git push origin :[branch-name]

6. Log to audit trail
```

### Output

- PR merged
- Branch cleaned up
- Audit log updated

## Workflow F: Push to Remote

### Input

- Branch name
- Remote (default: origin)

### Process

```
1. Validate not pushing to protected branch without approval
   if [[ "$branch" == "main" ]]; then
     REQUIRE_APPROVAL "Push to main requires explicit approval"
   fi

2. Check for force push attempt
   - BLOCK if --force or -f detected

3. Execute push
   GIT_MASTER_AUTHORIZED=true git push origin [branch]

4. Log to audit trail
```

### Output

- Changes pushed to remote
- Audit log updated

## Workflow G: Pre-Merge Checklist

### Input

- PR number

### Process

```
REQUIRED CHECKS (Block merge if failed):

1. CHANGELOG Updated (for feat/fix PRs)
   - Verify: git diff main...HEAD includes CHANGELOG.md
   - If missing: "CHANGELOG.md must be updated"

2. PR Template Complete
   - All sections have content
   - Title follows Conventional Commits

3. All Required Checks Pass
   - CI/CD passed
   - Reviews approved

4. No Unresolved Comments
   - All review comments resolved or dismissed

RECOMMENDED CHECKS (Warn but allow):

5. Documentation Sync (for PRs >5 files)
   - Prompt: "Did this PR introduce patterns needing doc updates?"

6. Sage Review (for PRs >10 files or labeled 'needs-sage')
   - Prompt: "Suggest Sage review for learnings before merge?"

POST-MERGE ACTIONS (Automatic):

7. Sage Notification
   - If PR >10 files: "sage: review merged PR #XX for learnings"

8. Tag Prompt
   - If merging to main: "Ready to create version tag?"
```

## Validation Reference

### Commit Message Validation

```javascript
// Conventional Commits pattern
const PATTERN = /^(feat|fix|docs|style|refactor|test|chore)(\([a-z0-9-]+\))?!?:\s.+/;

// Validate
function validateCommit(message) {
  const firstLine = message.split('\n')[0];

  if (!PATTERN.test(firstLine)) {
    return { valid: false, error: 'Invalid format' };
  }

  if (firstLine.length > 72) {
    return { valid: false, error: 'First line > 72 chars' };
  }

  return { valid: true };
}
```

### Branch Name Validation

```javascript
// Valid categories
const CATEGORIES = ['feat', 'fix', 'docs', 'refactor', 'style', 'chore'];

// Pattern: category/kebab-case-name
const PATTERN = /^(feat|fix|docs|refactor|style|chore)\/[a-z0-9-]+$/;

function validateBranch(name) {
  return PATTERN.test(name);
}
```

### Semantic Version Validation

```javascript
// Pattern: vMAJOR.MINOR.PATCH
const PATTERN = /^v\d+\.\d+\.\d+$/;

function validateTag(tag) {
  return PATTERN.test(tag);
}
```

## Audit Trail Format

```
# GIT_AUDIT_LOG.txt (gitignored)

[2026-01-25T10:30:00Z] BRANCH_CREATE
  Branch: feat/staging-payments
  Base: main (abc1234)
  User: git-master

[2026-01-25T10:35:00Z] COMMIT
  Hash: def5678
  Message: feat(staging): add Stripe payments model
  Files: 3 changed (+120/-5)
  User: git-master

[2026-01-25T11:00:00Z] PR_CREATE
  Number: #45
  Title: feat(staging): add Stripe payments model
  Branch: feat/staging-payments → main
  User: git-master

[2026-01-25T12:00:00Z] PR_MERGE
  Number: #45
  Method: merge
  User: git-master
```

## Error Messages

### Invalid Commit Message

```
[REJECTED] Commit message invalid

Message: "updated navigation"
Issue: Does not follow Conventional Commits format

Required format: type(scope): description
Valid types: feat, fix, docs, style, refactor, test, chore

Example: fix(nav): correct broken link to home-life
```

### Protected Branch Violation

```
[REJECTED] Cannot commit directly to main

Protected branches require PR workflow:
1. Create feature branch: /branch feat/your-feature
2. Make commits on feature branch
3. Create PR: gh pr create
4. Merge after review
```

### Force Push Blocked

```
[REJECTED] Force push blocked

Command: git push --force origin main
Risk: Rewrites history, may lose work

For emergency override (logged to audit):
git push --force origin main --bypass-git-master
```

## Integration

- **Entry**: Any git write operation request
- **Persona**: Git-Master
- **Exit**: Operation completed with audit log

## Related Documentation

- [[../commands/commit.md]] - Quick commit command
- [[../commands/branch.md]] - Quick branch command
- [[worktree-orchestration.md]] - Parallel development
- [[../rules/git-workflow.md]] - Git standards
- [[../agents/git-master.md]] - Git-Master persona
