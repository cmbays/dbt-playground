# Learned Skill: Critical Workflow Enforcement with Defense-in-Depth

**Purpose**: Systematic approach to enforcing critical workflows across multi-stage development processes, using defense-in-depth strategy with multiple verification layers.

**Owner**: Supervisor/Architect personas

**Extracted from**: v0.5 PR workflow bypass incident and root cause analysis

**Proven in**: dbt-playground v0.5 marts-enhancements workflow enforcement (2026-01-30)

---

## When to Use

**Trigger conditions**:

- Designing a new multi-stage workflow (planning -> implementation -> review -> deploy)
- Existing workflow has suffered bypasses or violations
- Adding critical phase transitions that should never be skipped
- Integrating multiple agents with handoff points

**Proactive use**:

- Part of workflow design for any new project
- When onboarding team members to existing workflows
- Before major version releases where process matters

---

## Prerequisites

**Required**:

- Understanding of the workflow stages and their dependencies
- Identification of "high-consequence" transitions (where bypass is costly)
- Access to modify agent personas and/or git hooks

**Recommended**:

- Repository admin access (for branch protection)
- Familiarity with git hooks
- Understanding of existing phase gate mechanisms

---

## Process

### Step 1: Map the Workflow and Identify Critical Transitions

**Purpose**: Document the workflow and mark where enforcement is needed

**Questions to answer**:

1. What are the workflow phases?
2. What artifacts does each phase produce?
3. What preconditions must be met before each phase?
4. Which transitions are "high-consequence" (costly to undo)?

**Template**:

```markdown
## Workflow Map: [Workflow Name]

### Phases
1. [Phase 1] -> produces [Artifact 1]
2. [Phase 2] -> produces [Artifact 2]
...

### Critical Transitions (need enforcement)
- [Phase X] -> [Phase Y]: Why critical? [Reason]

### Low-Risk Transitions (documentation sufficient)
- [Phase A] -> [Phase B]: Why low risk? [Reason]
```

**Example from v0.5**:

```markdown
## Workflow Map: PR-Centric Development

### Phases
1. Planning -> produces PRD, TDD
2. Testing Design -> produces Test Spec
3. Implementation -> produces Code
4. Review -> produces Approvals
5. Documentation -> produces CHANGELOG
6. Deploy -> produces Version Tag

### Critical Transitions
- Testing -> Implementation: Must be on feature branch with draft PR
  Why: Commits to wrong branch are costly to fix

- Review -> Documentation: Must have 2+ approvals, no blockers
  Why: Merging without review defeats the purpose

### Low-Risk Transitions
- Planning -> Testing Design: Same context, easy to redo
```

---

### Step 2: Design Verification for Critical Transitions

**Purpose**: Define what gets checked at each critical transition

**For each critical transition, define**:

1. **Artifact verification** (backward-looking): Did previous phase complete?
2. **State verification** (forward-looking): Are preconditions met for next phase?
3. **Verification command**: How to check programmatically?
4. **Failure response**: What happens if check fails?

**Template**:

```markdown
## Transition: [From Phase] -> [To Phase]

### Artifact Verification
- [ ] [Artifact] exists at [path]
- [ ] [Artifact] contains required content

### State Verification
- [ ] [State condition 1]: Command to verify
- [ ] [State condition 2]: Command to verify

### Verification Commands
```bash
# Artifact check
ls [path] || exit 1

# State check
[command] || exit 1
```

### Failure Response

If artifact missing: [action]
If state wrong: [action]

```

**Example from v0.5**:

```markdown
## Transition: Testing -> Implementation

### Artifact Verification
- [ ] Test spec exists: `temp/v*_TESTING.md` or test plan document

### State Verification
- [ ] On feature branch: `git branch --show-current` != main
- [ ] Draft PR exists: `gh pr list --head [branch] --state open`

### Verification Commands
```bash
# Artifact check
ls temp/v*_TESTING.md 2>/dev/null || { echo "Test spec missing"; exit 1; }

# State check
branch=$(git branch --show-current)
[[ "$branch" != "main" ]] || { echo "Not on feature branch"; exit 1; }
```

### Failure Response

If artifact missing: Request Tester to complete test spec
If state wrong: Request git-master to create feature branch

```

---

### Step 3: Implement Defense-in-Depth Layers

**Purpose**: Add multiple enforcement layers for critical transitions

**Layer 1: Persona-Level Verification (Soft Check)**

Add verification step to relevant agent personas.

```markdown
# In [agent].md

## Pre-Execution Verification

Before starting work, verify:
1. Run: `[verification command]`
2. If [condition fails]: STOP - [remediation action]
3. If [condition passes]: proceed

DO NOT SKIP THIS STEP.
```

**Layer 2: Supervisor Phase Gate (Soft Enforcement)**

Add state verification to Supervisor's transition matrix.

```markdown
# In supervisor.md, Artifact Requirements Matrix

| Transition | Required Artifacts | State Verification |
|------------|-------------------|-------------------|
| [Phase A] -> [Phase B] | [artifact exists] | [state command returns OK] |
```

**Layer 3: Git Hooks (Hard Local Enforcement)**

Create hook scripts that block violations.

**Pre-commit hook template**:

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Purpose: Prevent commits to protected branches

branch=$(git branch --show-current)

# Block commits to protected branches
protected_branches=("main" "master" "production")
for protected in "${protected_branches[@]}"; do
    if [ "$branch" = "$protected" ]; then
        echo "ERROR: Direct commits to $protected are blocked."
        echo "Create a feature branch: git checkout -b feat/your-feature"
        exit 1
    fi
done

exit 0
```

**Pre-push hook template**:

```bash
#!/bin/bash
# .git/hooks/pre-push
# Purpose: Prevent pushes to protected branches

protected_branches=("main" "master" "production")

while read local_ref local_sha remote_ref remote_sha; do
    for protected in "${protected_branches[@]}"; do
        if [[ "$remote_ref" == "refs/heads/$protected" ]]; then
            echo "ERROR: Direct pushes to $protected are blocked."
            echo "Create a PR instead."
            exit 1
        fi
    done
done

exit 0
```

**Layer 4: Branch Protection (Hard Remote Enforcement)**

Configure repository settings (if you have admin access):

```markdown
## Branch Protection Configuration

Branch: main

- [x] Require pull request reviews before merging
  - Required approving reviews: 2
- [x] Require status checks to pass before merging
- [x] Require branches to be up to date before merging
- [x] Include administrators
- [x] Restrict who can push to matching branches
  - Only allow: [no direct pushes]
```

---

### Step 4: Document Hook Installation

**Purpose**: Ensure hooks are installed consistently

Create or update onboarding documentation:

```markdown
## Git Hooks Installation

This project uses git hooks for workflow enforcement.

### Automatic Installation (recommended)

```bash
# Run setup script
./scripts/setup-hooks.sh
```

### Manual Installation

```bash
# Copy hooks to git directory
cp .github/hooks/* .git/hooks/
chmod +x .git/hooks/*
```

### Verification

```bash
# Verify hooks are installed
ls -la .git/hooks/
# Should see: pre-commit, pre-push
```

```

---

### Step 5: Create Setup Script

**Purpose**: Automate hook installation for new contributors

```bash
#!/bin/bash
# scripts/setup-hooks.sh
# Purpose: Install git hooks for workflow enforcement

HOOK_SOURCE=".github/hooks"
HOOK_TARGET=".git/hooks"

echo "Installing git hooks for workflow enforcement..."

# Create hooks directory if needed
mkdir -p "$HOOK_TARGET"

# Copy each hook
for hook in "$HOOK_SOURCE"/*; do
    if [ -f "$hook" ]; then
        hookname=$(basename "$hook")
        cp "$hook" "$HOOK_TARGET/$hookname"
        chmod +x "$HOOK_TARGET/$hookname"
        echo "  Installed: $hookname"
    fi
done

echo "Done. Git hooks installed successfully."
```

---

### Step 6: Test the Enforcement Layers

**Purpose**: Verify each layer works correctly

**Test checklist**:

```markdown
## Enforcement Layer Testing

### Layer 1: Persona Verification
- [ ] Agent correctly checks state before starting work
- [ ] Agent correctly blocks when state is wrong
- [ ] Agent provides clear remediation guidance

### Layer 2: Supervisor Phase Gate
- [ ] Supervisor verifies artifacts at transition
- [ ] Supervisor verifies state at transition
- [ ] Supervisor blocks transition when verification fails
- [ ] Supervisor provides clear failure message

### Layer 3: Pre-Commit Hook
- [ ] Commit to main is blocked with clear error
- [ ] Commit to feature branch succeeds
- [ ] Error message includes remediation guidance
- [ ] Hook can be bypassed with --no-verify (intentional escape hatch)

### Layer 4: Pre-Push Hook
- [ ] Push to main is blocked with clear error
- [ ] Push to feature branch succeeds
- [ ] Error message includes remediation guidance

### Layer 5: Branch Protection (if configured)
- [ ] Direct push to main rejected by GitHub
- [ ] PR merge without required reviews blocked
- [ ] Status checks required before merge
```

---

## Common Workflows After Setup

### Adding a New Protected Transition

```markdown
1. Identify the transition and why it needs protection
2. Add artifact + state verification to Supervisor
3. If high-risk, add hook enforcement
4. Update documentation
5. Test all layers
```

### Debugging Enforcement Failures

```markdown
1. Identify which layer caught the violation
2. If Layer 1 (persona): Agent may have skipped verification step
3. If Layer 2 (supervisor): Check WORKFLOW_STATE.md for context
4. If Layer 3/4 (hooks): Check hook installation
5. If Layer 5 (branch protection): Check repository settings
```

### Updating Enforcement Rules

```markdown
1. Update Supervisor phase gate matrix
2. Update hook scripts if needed
3. Update persona verification steps
4. Communicate changes to team
5. Update onboarding documentation
```

---

## Decision Framework

### When to Add Each Layer

| Layer | Add When | Skip When |
|-------|----------|-----------|
| Persona verification | Always for critical transitions | Never skip |
| Supervisor phase gate | Multi-agent workflows | Single-agent work |
| Pre-commit hook | Team projects, high-risk branches | Solo experiments |
| Pre-push hook | Remote collaboration | Local-only work |
| Branch protection | Production repositories | Personal forks |

### How Much Enforcement is Enough?

| Risk Level | Recommended Layers |
|------------|-------------------|
| Low (experiments, spikes) | Layer 1 + 2 |
| Medium (team projects) | Layer 1 + 2 + 3 |
| High (production, releases) | All 5 layers |

---

## Troubleshooting

### "Hook not running"

**Symptom**: Commits/pushes succeed when they should be blocked

**Causes**:

1. Hook not installed (check `.git/hooks/`)
2. Hook not executable (`chmod +x .git/hooks/pre-commit`)
3. Hook has syntax error (test with `bash -x .git/hooks/pre-commit`)

**Fix**: Reinstall hooks with setup script

### "False positives blocking valid work"

**Symptom**: Legitimate work blocked by enforcement

**Causes**:

1. Enforcement rule too strict
2. Edge case not considered
3. Workflow changed but enforcement not updated

**Fix**: Review and update enforcement rules, add exceptions if needed

### "Enforcement bypassed"

**Symptom**: Violation occurred despite enforcement layers

**Root cause questions**:

1. Which layer should have caught it?
2. Was that layer installed/configured?
3. Was there a bypass flag used (e.g., --no-verify)?

**Fix**: Strengthen the layer that failed, add redundant layer if needed

---

## See Also

- `docs/reference/LEARNINGS.md#workflow-enforcement-patterns` - Technical patterns
- `docs/for_chris/UNDERSTANDING_PR_WORKFLOW.md` - Educational context
- `.claude/agents/supervisor.md` - Phase gate implementation
- `temp/ROOT_CAUSE_ANALYSIS_v0.5_BYPASS.md` - Original incident analysis
