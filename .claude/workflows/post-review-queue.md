# Post-Review Queue Workflow

This workflow defines the agent queue that runs after a PR receives 2+ approvals.

## Purpose

Ensure documentation, learning extraction, and project management updates happen **before merge**, captured in the PR's git history.

## Trigger Conditions

The post-review queue starts when ALL conditions are met:

1. PR has 2+ `APPROVED` reviews
2. No `CHANGES_REQUESTED` reviews outstanding
3. No unresolved `[BLOCKER]` comments
4. PR is not in draft state

## Queue Sequence

```
┌─────────────────────────────────────────────────────────────┐
│                    POST-REVIEW QUEUE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. DOCUMENTER (docs:)                    [REQUIRED]        │
│     └─ Update CHANGELOG.md                                  │
│     └─ Update relevant docs if patterns changed             │
│     └─ Commit to PR branch                                  │
│                                                             │
│  2. SAGE (sage:)                          [CONDITIONAL]     │
│     └─ Review PR for extractable learnings                  │
│     └─ Apply decision rubric                                │
│     └─ Commit doc updates to PR branch (if any)             │
│     └─ Skip if: PR is trivial fix (<10 lines)               │
│                                                             │
│  3. PM (pm:)                              [CONDITIONAL]     │
│     └─ Link PR to related GitHub issues                     │
│     └─ Update issue status                                  │
│     └─ Close issues if PR resolves them                     │
│     └─ Skip if: No related issues                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Agent Invocation Templates

### 1. Documenter

```
docs: Update CHANGELOG for PR #[N] on branch [branch-name]

Context:
- PR title: [title]
- PR type: [feat/fix/docs/etc]
- Summary: [1-2 sentences]

Tasks:
1. Add entry to CHANGELOG.md under appropriate section
2. Update any docs affected by this PR
3. Commit changes to [branch-name] with message:
   "docs: update changelog for PR #[N]"
4. Push to origin
```

### 2. Sage

```
sage: Review PR #[N] for learnings

Context:
- PR scope: [brief description]
- Files changed: [count]
- Key changes: [summary]

Tasks:
1. Read PR diff and discussion
2. Apply decision rubric (≥2 criteria for FOR_CHRIS doc)
3. Extract patterns to LEARNINGS.md if proven
4. If doc updates needed, commit to [branch-name]:
   "docs(sage): extract learnings from PR #[N]"
5. Report findings to Supervisor
```

### 3. PM

```
pm: Update issues for PR #[N]

Context:
- Related issues: #[X], #[Y]
- PR resolves: [yes/no]

Tasks:
1. Add PR link to related issues
2. Update issue status (if applicable)
3. Close issues that this PR resolves (use: gh issue close X --comment "...")
4. Report completion to Supervisor
```

## Queue Execution Rules

### Sequencing

- Agents run **sequentially**, not in parallel
- Each agent must complete before next starts
- This ensures commits don't conflict

### Commit Rules

| Agent | Commit Message Format | Files Allowed |
|-------|----------------------|---------------|
| Documenter | `docs: ...` | CHANGELOG.md, docs/*.md |
| Sage | `docs(sage): ...` | docs/reference/LEARNINGS.md, docs/for_chris/*.md |
| PM | `chore(pm): ...` | None (uses gh CLI only) |

### Branch Targeting

- All commits go to the **PR's feature branch**
- Never commit to main during post-review queue
- Use `git checkout [branch-name]` before any git operations

### Error Handling

If an agent fails:

1. Supervisor logs the failure
2. Queue pauses
3. Supervisor reports: "Post-review queue paused at [agent]: [error]"
4. User can fix and resume: "super: resume post-review queue for PR #N"

### Skip Conditions

| Agent | Skip When |
|-------|-----------|
| Documenter | Never (always required for feat/fix) |
| Sage | PR is trivial (<10 lines), no patterns to extract |
| PM | No related issues linked |

## Verification Commands

### Check Queue Readiness

```bash
# Verify 2+ approvals
gh pr view N --json reviews --jq '[.reviews[] | select(.state=="APPROVED")] | length'
# Expected: ≥2

# Verify no blockers
gh pr view N --json reviews --jq '[.reviews[] | select(.state=="CHANGES_REQUESTED")] | length'
# Expected: 0

# Verify not draft
gh pr view N --json isDraft --jq '.isDraft'
# Expected: false
```

### Verify Queue Completion

```bash
# Check CHANGELOG was updated
gh pr diff N --name-only | grep "CHANGELOG.md"

# Check commits added by queue
gh pr view N --json commits --jq '.commits[-3:] | .[].messageHeadline'
# Should show docs: and docs(sage): commits if applicable
```

## Supervisor Orchestration

The Supervisor manages the queue through these steps:

```
super: [PR #N reaches 2+ approvals]

1. Announce: "Post-review queue starting for PR #N"

2. Run Documenter:
   └─ "docs: Update CHANGELOG for PR #N on branch feat/xyz"
   └─ Wait for completion
   └─ Verify commit: "Documenter committed CHANGELOG update"

3. Evaluate Sage need:
   └─ If PR >10 lines and contains patterns:
      └─ "sage: Review PR #N for learnings"
      └─ Wait for completion
   └─ Else: "Sage skipped (trivial PR)"

4. Evaluate PM need:
   └─ If related issues exist:
      └─ "pm: Update issues for PR #N"
      └─ Wait for completion
   └─ Else: "PM skipped (no related issues)"

5. Announce: "Post-review queue complete for PR #N"
   └─ Proceed to Final Approval Gate
```

## Integration Points

### With Supervisor

- Supervisor triggers queue after approval threshold met
- Supervisor monitors each agent's completion
- Supervisor proceeds to final approval after queue complete

### With Git-Master

- Git-master executes actual commit/push operations
- Queue agents delegate git operations: `git: commit -m "docs: ..."`
- Git-master validates commit format

### With GitHub

- All comments and reviews visible in PR history
- Queue commits appear in PR's commit list
- Final merged PR contains complete history

## Example Complete Flow

```
PR #42: feat/customer-analytics
├── Implementation commits (by Developer)
├── Code Review comment (by Code Reviewer)
├── Security Review approval (by Security Reviewer)
├── Code Review approval (by Code Reviewer)
├── [2+ approvals reached]
├── docs: update changelog for PR #42 (by Documenter)
├── docs(sage): extract learnings from PR #42 (by Sage)
├── [PM updates issue #38]
├── [Supervisor Final Approval]
└── Merge to main
```

All context preserved in git history and GitHub PR.
