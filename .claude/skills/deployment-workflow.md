# Deployment Workflow Skill

Version deployment and release management process.

## Overview

This skill manages the deployment of approved changes, including archiving, versioning, and documentation updates.

## Trigger

Invoke when:
- Code review approved
- Version milestone reached
- Ready for release
- User requests deployment

## Deployment Workflow

```
┌─────────────────────────────────────────┐
│  PRE-DEPLOY CHECKS                       │
│  - All tests pass                        │
│  - Code review approved                  │
│  - No blocking issues                    │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  DETERMINE VERSION                       │
│  - Analyze changes                       │
│  - Apply semver rules                    │
│  - Set version number                    │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  ARCHIVE                                 │
│  - Create archive/vX.Y/                  │
│  - Copy docs snapshot                    │
│  - Apply retention policy                │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  FINALIZE FILES                          │
│  - Move temp → final                     │
│  - Update version stamps                 │
│  - Update CHANGELOG                      │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  GIT OPERATIONS                          │
│  - Stage specific files                  │
│  - Commit with message                   │
│  - Create tag                            │
│  - Push (with approval)                  │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  POST-DEPLOY                             │
│  - Verify deployment                     │
│  - Clean temp (with approval)            │
│  - Update living docs                    │
│  - Announce completion                   │
└─────────────────────────────────────────┘
```

## Version Determination

### Semantic Versioning
| Change Type | Version Increment | Example |
|-------------|-------------------|---------|
| Major architecture change | MAJOR (X.0.0) | v1.0.0 → v2.0.0 |
| New feature, new page | MINOR (X.Y.0) | v0.2.0 → v0.3.0 |
| Bug fix, typo, tweak | PATCH (X.Y.Z) | v0.2.0 → v0.2.1 |

### Decision Guide
```
Is this a breaking change or complete topic?
  YES → MAJOR
  NO  → Continue

Is this a new feature or content addition?
  YES → MINOR
  NO  → Continue

Is this a bug fix or correction?
  YES → PATCH
```

## Archive Process

### Create Archive
```bash
# Create version archive directory
mkdir -p archive/v[X.Y]/docs

# Copy documentation snapshot
cp docs/ARCHITECTURE.md archive/v[X.Y]/docs/
cp docs/PROJECT_STRUCTURE.md archive/v[X.Y]/docs/
cp docs/DESIGN_PRINCIPLES.md archive/v[X.Y]/docs/

# Add build notes
echo "# v[X.Y] Notes\n\nDeployed: YYYY-MM-DD\n\n## Changes\n- Change 1\n- Change 2" > archive/v[X.Y]/notes.md
```

### Retention Policy
- Keep most recent of every MAJOR version (v0.x, v1.x, v2.x)
- Keep most recent 3 of current MAJOR version
- Pre-v1.0 treated as current major for retention

### Prune Old Archives
```bash
# Example: If deploying v0.5, keep v0.5, v0.4, v0.3
# Remove v0.2 and earlier (but keep git tags)
rm -rf archive/v0.2
```

## File Finalization

### Move Approved Files
```bash
# Move from temp to final locations
mv temp/[approved-file] [final-location]

# Example
mv temp/shopping-dialogue.html topics/shopping/dialogue.html
```

### Update Version Stamps
Add to top of modified HTML files:
```html
<!-- Version: vX.Y.Z - Updated: YYYY-MM-DD -->
```

### Update CHANGELOG

**Automated** (preferred): Invoke the changelog-generator agent to scan git history:
```
changelog: generate entries since v[PREVIOUS_TAG]
```
This produces a draft in `temp/CHANGELOG_DRAFT_vX.Y.Z.md` for review. After curation, apply to CHANGELOG.md.

**Manual** (fallback): Write entries directly in Keep a Changelog format:
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Feature 1
- Feature 2

### Changed
- Change 1

### Fixed
- Bug fix 1
```

See [[changelog-generation.md]] for the full automated workflow.

## Git Operations (via Git-Master)

All git operations go through git-master for validation and audit logging.

### Stage and Commit
```bash
# Use git: prefix for validated commits
git: commit my changes with message "feat(shopping): add complete dialogue page"

# Or use /commit command
/commit "feat(shopping): add complete dialogue page"
```

Git-master will:
- Stage specific files (never `git add .`)
- Validate Conventional Commits format
- Add Co-Authored-By automatically
- Log to audit trail

### Tag
```bash
git: create tag v0.3.0 "Complete shopping dialogue page"
```

### Push (Requires Approval)
```bash
git: push to origin main
git: push tag v0.3.0
```

### Direct Commands (Blocked by Hook)
Direct git write commands are blocked by `pre-bash-check.js`:
```bash
# These will be BLOCKED:
git commit -m "..."    # Use git: commit instead
git push origin main   # Use git: push instead
git tag -a v0.3.0      # Use git: create tag instead
```

## Deployment Checklist

```markdown
## Deployment: v[X.Y.Z]

### Pre-Deploy
- [ ] All tests pass
- [ ] Code review approved
- [ ] No blocking issues
- [ ] Version determined

### Archive
- [ ] Created archive/v[X.Y]/
- [ ] Docs snapshot copied
- [ ] Retention policy applied
- [ ] Old archives pruned

### Finalize
- [ ] Temp files moved to final location
- [ ] Version stamps updated
- [ ] CHANGELOG updated
- [ ] Living docs updated

### Git
- [ ] Specific files staged
- [ ] Commit message follows convention
- [ ] Tag created: v[X.Y.Z]
- [ ] Pushed to remote (approved)

### Post-Deploy
- [ ] Functionality verified
- [ ] No regressions
- [ ] Temp cleaned (approved)
- [ ] Completion announced
```

## Rollback Procedure

If issues discovered post-deploy:

### Quick Rollback
```bash
# Checkout previous version
git checkout v[previous]
```

### Revert Commit
```bash
# Create revert commit
git revert [commit-hash]
git push
```

### Tag Note
```bash
# Add note to problematic tag
git tag -a v[X.Y.Z]-bad -m "Known issues - see v[X.Y.Z+1]"
```

## Integration

- **Entry**: After Code Review approval
- **Persona**: Documenter
- **Exit**: Project continues at new version

## Exit Criteria

Deployment complete when:
- [ ] All checklist items done
- [ ] Version tagged and pushed
- [ ] CHANGELOG updated
- [ ] Team notified
- [ ] Verified working

---

## Related Documentation

- [[../../CLAUDE.md#versioning-strategy]] - Semantic versioning rules
- [[../rules/git-workflow.md]] - Git commit and tag standards
- [[../agents/AGENTS.md#assembly-line-workflows]] - Where deployment fits in workflow
- [[code-review-workflow.md]] - Previous step in pipeline
- [[../agents/DOC_MAINTENANCE.md]] - Post-deploy documentation updates
