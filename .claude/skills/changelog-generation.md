# Changelog Generation Skill

Automated changelog entry generation from git history using Conventional Commits.

## Overview

This skill automates the creation of CHANGELOG.md entries by parsing git commit history between version tags. It produces Keep a Changelog formatted output grouped by user impact.

## Trigger

Invoke when:

- Preparing a release (`/deploy`)
- Documenter needs changelog update (`docs: update changelog`)
- Checking what changed since last release
- Generating release notes for a PR or tag

## Prerequisites

- Git repository with Conventional Commits
- At least one version tag (or use `--root` for initial)
- `git` CLI available

## Workflow

### Step 1: Determine Range

```bash
# Find the latest tag
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

# If no tags, use root commit
if [ -z "$LATEST_TAG" ]; then
  BASE=$(git rev-list --max-parents=0 HEAD)
else
  BASE=$LATEST_TAG
fi
```

### Step 2: Extract Commits

```bash
# Non-merge commits (actual changes)
git log ${BASE}..HEAD --oneline --no-merges --format="%s"

# Merge commits (for PR numbers)
git log ${BASE}..HEAD --merges --oneline --format="%s"

# Full details including body (for BREAKING CHANGE footers)
git log ${BASE}..HEAD --no-merges --format="COMMIT_START%nHash: %H%nSubject: %s%nBody: %b%nCOMMIT_END"
```

### Step 3: Parse Conventional Commits

Each commit message `type(scope): description` maps to:

| Type | Changelog Section |
|------|-------------------|
| `feat` | **Added** |
| `fix` | **Fixed** |
| `refactor` | **Changed** |
| `style` | **Changed** |
| `perf` | **Changed** |
| `docs` | **Internal** |
| `test` | **Internal** |
| `chore` | **Internal** |
| `!` suffix or `BREAKING CHANGE:` footer | **⚠️ Breaking Changes** |

### Step 4: Group and Format

```markdown
## [X.Y.Z] - YYYY-MM-DD

### ⚠️ Breaking Changes
- **scope**: description (#PR)
  - **Migration**: instructions

### Added
**Scope Group**
- Description (#PR)
- Description (#PR)

### Changed
- **scope**: description (#PR)

### Fixed
- **scope**: description (#PR)

### Internal
- chore/docs/test changes
```

### Step 5: Output

**Draft mode** (default):

```bash
# Write to temp for review
# File: temp/CHANGELOG_DRAFT_vX.Y.Z.md
```

**Apply mode** (with approval):

```bash
# Insert after ## [Unreleased] header in CHANGELOG.md
# Or replace [Unreleased] with versioned header
```

## Usage Examples

### Generate Draft for Next Release

```
changelog: generate entries since v0.4.0
```

### Generate and Apply

```
changelog: generate and apply entries for v0.5.0
```

### Release Notes Only (Condensed)

```
changelog: generate release notes for v0.5.0
```

### Check for Breaking Changes

```
changelog: check breaking changes since v0.4.0
```

## Integration with Deploy

In the deployment workflow, changelog generation slots into the FINALIZE FILES step:

```
PRE-DEPLOY CHECKS
    │
DETERMINE VERSION
    │
ARCHIVE
    │
FINALIZE FILES
    ├─→ Move temp → final
    ├─→ Update version stamps
    └─→ ★ Generate changelog entries ★
        ├─→ Scan git log since last tag
        ├─→ Draft entries
        ├─→ Review/approve
        └─→ Apply to CHANGELOG.md
    │
GIT OPERATIONS (via git-master)
    │
POST-DEPLOY
```

## Curation Guidelines

Automated output should be **reviewed and curated** before applying:

1. **Consolidate**: Group related commits into single entries
2. **Rewrite**: Make descriptions user-facing (not developer shorthand)
3. **Highlight**: Bold the most important changes
4. **Link**: Add PR/issue references
5. **Order**: Most impactful changes first within each section

## Related Documentation

- [[../agents/changelog-generator.md]] - Agent persona
- [[../agents/documenter.md]] - Parent persona
- [[deployment-workflow.md]] - Where this fits in deploy
- [[../rules/git-workflow.md]] - Conventional Commits format
- [[../../CHANGELOG.md]] - Output target
