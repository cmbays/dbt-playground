# Deploy Command

Execute version deployment workflow with proper archiving and tagging.

## Usage

```
/deploy [version] [description]
```

## Examples

```
/deploy v0.3.0 "Complete shopping dialogue page"
/deploy patch "Fix navigation bug"
/deploy minor "Add JLPT filter feature"
```

## Version Determination

| Keyword | Action |
|---------|--------|
| `vX.Y.Z` | Use specified version |
| `major` | Increment major (X+1.0.0) |
| `minor` | Increment minor (X.Y+1.0) |
| `patch` | Increment patch (X.Y.Z+1) |

## Deployment Workflow

### 1. Pre-Deploy Checks

- [ ] All tests pass
- [ ] No uncommitted changes in working files
- [ ] Temp folder reviewed
- [ ] Living docs updated

### 2. Archive Process

```bash
# Following retention policy:
# - Keep most recent of every MAJOR version
# - Keep most recent 3 of current MAJOR version

# Create archive snapshot
mkdir -p archive/v[X.Y]/docs
cp -r docs/*.md archive/v[X.Y]/docs/
```

### 3. Finalize Files

```bash
# Move approved temp files to final locations
mv temp/[approved-files] [final-location]

# Update version comments in modified files
# <!-- Version: vX.Y.Z - Updated: YYYY-MM-DD -->
```

### 4. Git Operations

```bash
# Stage changes
git add [specific files]

# Commit with conventional message
git commit -m "feat(scope): description

Version: vX.Y.Z
Co-Authored-By: Claude <noreply@anthropic.com>"

# Create annotated tag
git tag -a vX.Y.Z -m "Description"

# Push (with confirmation)
git push origin main
git push origin vX.Y.Z
```

### 5. Post-Deploy

- [ ] Verify deployment
- [ ] Update CHANGELOG.md
- [ ] Clean temp/ (with approval)
- [ ] Announce completion

## Deployment Checklist Template

```markdown
## Deployment: v[X.Y.Z]

### Pre-Deploy
- [ ] Tests pass
- [ ] Code reviewed
- [ ] Docs updated
- [ ] Temp files approved

### Archive
- [ ] Created archive/v[X.Y]/
- [ ] Copied docs snapshot
- [ ] Pruned old archives per retention policy

### Deploy
- [ ] Moved temp → final
- [ ] Version stamps updated
- [ ] Git commit created
- [ ] Tag created: v[X.Y.Z]
- [ ] Pushed to remote

### Post-Deploy
- [ ] CHANGELOG updated
- [ ] Temp cleaned (approved)
- [ ] Verified functionality
```

## Rollback

If issues discovered post-deploy:

```bash
# Checkout previous version
git checkout v[previous]

# Or revert specific commit
git revert [commit-hash]
```

## Persona Integration

This command activates the **Documenter** (`docs:`) persona for version management, with verification support from **Quality Tester** (`test:`).
