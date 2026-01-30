---
audience: [human, sage]
priority: high
size: large
last_updated: 2026-01-30
status: active
tags: [learning, workflow, git, pr, enforcement, defense-in-depth]
---

# Understanding PR-First Development: Why It Matters and How We Enforce It

**Topic**: The philosophy behind PR-centric development and the defense-in-depth enforcement strategy that prevents workflow bypasses

**Context**: During v0.5 development, an initial commit was made directly to main instead of the feature branch. This incident revealed systemic gaps in our workflow enforcement and led to a comprehensive defense-in-depth strategy.

**Why this matters**: Understanding *why* PR-first matters helps you appreciate *why* we enforce it at multiple layers. It's not bureaucracy - it's quality protection with an audit trail.

---

## The Story of the v0.5 Bypass

Let me tell you what happened, because the story illustrates the problem better than any abstract explanation.

We had just completed planning for v0.5 - the marts layer enhancements. Everything was documented:

- `v0.5_PLAN.md` specified the feature branch: `feat/marts-enhancements`
- `V0.5_ORCHESTRATION_SUMMARY.md` listed "Create Git Worktree" as step 1
- `PRD-015` explicitly required "draft PR creation at branch/worktree creation"

Three different documents, all saying the same thing: **create a feature branch before implementing**.

And yet, when the Developer agent started implementing the first model, it committed directly to main.

Why? Because nobody *verified* the branch was created. The documents said what *should* happen, but the workflow didn't check that it *did* happen.

The Supervisor's phase gate checked: "Does the test spec exist?" Yes. "Does the TDD exist?" Yes. "Ready for implementation!" But it never asked: "Are we on the right branch?"

This is the difference between **documentation** and **enforcement**.

---

## Why PR-First Development Matters

Before we talk about enforcement, let's understand why we care about working on branches with draft PRs in the first place.

### 1. Visibility: Everyone Sees What's In Progress

When you create a draft PR at the start of work:

- Team members can see what features are being developed
- Cross-session agents can use `gh pr view` to understand context
- Work-in-progress is visible even if not complete
- No "submarine features" that suddenly surface at merge time

### 2. Audit Trail: Git History Tells a Story

Every commit on a feature branch is part of the PR history:

- Reviewers can see how the code evolved
- Decisions are captured in commit messages
- If something breaks, you can trace when it was introduced
- The merge commit links the PR to main

### 3. Review-Ready: Work Is Always Reviewable

With changes on a branch:

- Reviewers can comment on code at any point
- You can request early feedback before feature is complete
- Security reviewer, code reviewer, design reviewer - all can work from the same PR
- Draft status signals "not ready to merge" while still enabling discussion

### 4. Revertable: Mistakes Stay Contained

If something goes wrong:

- The entire feature can be reverted by reverting the merge commit
- Main is never polluted with half-done work
- Broken features don't block other work
- You can abandon a branch without cleaning up main

### 5. Parallel Work: Multiple Features at Once

With branches and worktrees:

- Different agents can work on different features simultaneously
- Changes don't conflict until merge time
- Each feature is isolated during development
- Merge conflicts are resolved once, at the end

---

## The Defense-in-Depth Strategy

So we agree PR-first is valuable. Now how do we ensure it actually happens?

The insight from the v0.5 incident is that **single-layer enforcement is fragile**. If your only protection is a document that says "create a branch," and someone doesn't read it (or an agent doesn't check it), the violation happens.

Defense-in-depth means placing enforcement at multiple layers, each progressively harder to bypass:

```
Layer 5: GitHub Branch Protection ────────── [Cannot bypass without admin]
    │
Layer 4: Pre-Push Hook ───────────────────── [Blocks push to main]
    │
Layer 3: Pre-Commit Hook ─────────────────── [Blocks commit to main]
    │
Layer 2: Supervisor Phase Gate ───────────── [Checks before implementation]
    │
Layer 1: Persona Verification ────────────── [Agent self-checks]
    │
    └──→ Workflow starts
```

Each layer catches what the previous layer missed.

### Layer 1: Persona Verification (Soft Check)

The agent doing implementation now has explicit instructions:

```markdown
## Development Flow

1. **VERIFY GIT STATE FIRST**:
   - Run: `git branch --show-current`
   - If on `main`: STOP - invoke `git: create branch feat/[feature-name]`
   - If on feature branch: proceed
```

**What it catches**: Honest mistakes by agents following instructions
**What it misses**: Agents that skip the step or operators that bypass the agent

### Layer 2: Supervisor Phase Gate (Soft Enforcement)

The Supervisor now verifies git state before allowing transitions:

| Transition | Git State Check |
|------------|-----------------|
| Tester -> Developer | Branch is not main |
| Developer -> Reviewer | Draft PR exists |

**What it catches**: Attempts to transition without proper setup
**What it misses**: Direct invocation of Developer without going through Supervisor

### Layer 3: Pre-Commit Hook (Hard Local)

A git hook that runs before every commit:

```bash
#!/bin/bash
branch=$(git branch --show-current)
if [ "$branch" = "main" ]; then
    echo "ERROR: Direct commits to main are blocked."
    exit 1
fi
```

**What it catches**: Any attempt to commit to main, regardless of workflow path
**What it misses**: Can be bypassed with `git commit --no-verify`

### Layer 4: Pre-Push Hook (Hard Local)

Blocks pushes to protected branches:

```bash
#!/bin/bash
while read local_ref local_sha remote_ref remote_sha; do
    if [[ "$remote_ref" == "refs/heads/main" ]]; then
        echo "ERROR: Direct pushes to main are blocked."
        exit 1
    fi
done
```

**What it catches**: Pushes to main even if commit hook was bypassed
**What it misses**: Can also be bypassed, and doesn't help if hook not installed

### Layer 5: GitHub Branch Protection (Hard Remote)

Server-side enforcement that cannot be bypassed locally:

- Require pull request reviews before merging
- Block direct pushes to main (even from admins if configured)
- Require status checks to pass

**What it catches**: Everything that makes it to the server
**What it misses**: Nothing - this is the final line of defense

---

## Why Multiple Layers Instead of Just One Strong Layer?

You might ask: "If GitHub branch protection catches everything, why bother with the other layers?"

Great question. Here's the answer:

### 1. Fast Feedback Beats Late Feedback

If you commit to main locally and only discover the error when you push (Layer 4 or 5), you've already done the work. You need to:

1. Understand why the push failed
2. Create a branch retroactively
3. Cherry-pick or recommit your work
4. Clean up main

But if Layer 1 (persona) or Layer 2 (Supervisor) catches it, you haven't even started. The fix is just "create a branch."

**Principle**: Catch errors as early as possible to minimize rework.

### 2. Layers Provide Redundancy

No single enforcement mechanism is perfect:

- Personas can be bypassed by direct commands
- Supervisors can be skipped with `--dev-only` flag
- Hooks can be bypassed with `--no-verify`
- Branch protection can be misconfigured

With multiple layers, the question isn't "what if one fails?" but "can all of them fail simultaneously?" That's much less likely.

### 3. Different Contexts Need Different Enforcement

Not every project needs all five layers:

- **Solo experiments**: Layer 1 + 2 may be enough
- **Team projects**: Add Layer 3 + 4 for git hooks
- **Production systems**: All 5 layers including branch protection

Defense-in-depth scales with risk.

### 4. Audit Trail for Post-Mortems

If a violation does occur, multiple layers help answer: "Where did the process break down?"

- If Layer 1 failed: Agent didn't follow its instructions
- If Layer 2 failed: Supervisor was bypassed
- If Layer 3 failed: Hook wasn't installed or was bypassed
- If Layer 4 failed: Same as Layer 3
- If Layer 5 failed: Branch protection not configured

Each layer is a checkpoint for investigation.

---

## The Bigger Picture: Workflow Enforcement as Systems Design

The v0.5 incident taught us something important that applies beyond git workflows:

**Documenting correct behavior is necessary but not sufficient for ensuring it happens.**

This applies to:

- **Code review requirements**: Documented in guidelines, enforced by required reviews
- **Testing requirements**: Documented in standards, enforced by CI checks
- **Security requirements**: Documented in policies, enforced by scanners and gates
- **Deployment procedures**: Documented in runbooks, enforced by approval workflows

In each case, the pattern is the same:

1. Document what should happen (the policy)
2. Add soft checks that remind (persona/supervisor layer)
3. Add hard checks that prevent (hooks/CI layer)
4. Add server-side enforcement (platform-level controls)

The v0.5 bypass was a learning moment that showed us our workflow was at stage 1 only. Now we're building toward all four stages.

---

## Practical Application: What This Means for You

### If You're Starting New Work

1. **Use `/branch` or `git: create branch`**: These commands now create a draft PR automatically
2. **Verify before implementing**: Quick check - `git branch --show-current`
3. **Trust the Supervisor**: If it blocks your transition, there's a reason

### If You See an Enforcement Error

1. **Don't bypass it**: The error is protecting you from future pain
2. **Fix the underlying issue**: Create the branch, create the PR, whatever's missing
3. **Report if it's a false positive**: Maybe our enforcement needs tuning

### If You're Designing Workflows

1. **Ask "what enforces this?"** for each requirement
2. **Add verification, not just documentation**
3. **Design for failure**: What happens if one layer fails?
4. **Make correct behavior easier than incorrect**: Reduce friction for the right path

---

## Summary: The Philosophy in One Sentence

**Write down what should happen, then add layers of enforcement to make sure it does, progressively harder to bypass, with early feedback preferred over late.**

This is defense-in-depth applied to workflow, and it's how mature engineering organizations prevent categories of errors rather than individual mistakes.

---

## Related Reading

- **Technical patterns**: `docs/reference/LEARNINGS.md#workflow-enforcement-patterns`
- **Executable skill**: `.claude/skills/learned-workflow-enforcement.md`
- **Supervisor details**: `.claude/agents/supervisor.md` (phase gates)
- **Git workflow rules**: `.claude/rules/git-workflow.md`
- **Root cause analysis**: `temp/ROOT_CAUSE_ANALYSIS_v0.5_BYPASS.md`

---

*The best process is invisible when followed and impossible to bypass when not.*
