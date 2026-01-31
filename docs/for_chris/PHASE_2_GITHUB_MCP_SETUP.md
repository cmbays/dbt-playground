# Phase 2: GitHub-MCP Setup Guide

**Status**: READY TO IMPLEMENT
**Date**: 2026-01-31
**Prerequisite**: Phase 1 complete ✅, Phase 1b optional (branch protection)

## Overview

Phase 2 integrates GitHub-MCP (Model Context Protocol) with git-master for automated PR reviews via programmatic GitHub API access.

**Goal**: Enable Code Reviewer and Security Reviewer to post reviews with single git-master request instead of per-call approval friction.

## Installation

### 1. Install GitHub-MCP

```bash
# Option A: Install globally
npm install -g @anthropic-ai/mcp-github

# Option B: Install locally to project
npm install --save-dev @anthropic-ai/mcp-github
```

**Verify installation**:

```bash
which mcp-github  # or npm list -g @anthropic-ai/mcp-github
```

### 2. Configure .mcp.json

Update `.mcp.json` to include GitHub MCP server:

```json
{
  "mcpServers": {
    "dbt": {
      "command": "uvx",
      "args": ["dbt-mcp"],
      "env": {
        "DBT_PROJECT_DIR": "./dbt_project",
        "DBT_PATH": "./.venv/bin/dbt",
        "DBT_PROFILES_DIR": "/Users/cmbays/.dbt"
      }
    },
    "github": {
      "command": "mcp-github",
      "args": [],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### 3. Set GitHub Token

GitHub-MCP requires a GitHub Personal Access Token:

```bash
# Set environment variable
export GITHUB_TOKEN="ghp_your_token_here"

# Or add to ~/.bashrc / ~/.zshrc for persistence
echo 'export GITHUB_TOKEN="ghp_..."' >> ~/.zshrc
```

**Token Requirements**:

- Scopes: `repo`, `pull-requests:write`, `issues:read`
- Create at: <https://github.com/settings/tokens>

### 4. Verify MCP Connection

Test that GitHub-MCP is accessible:

```bash
# Claude Code will automatically load .mcp.json
# Test in Claude Code by asking:
# "Check if GitHub MCP is accessible by listing recent PRs"
```

## Documentation Updates

### 1. Update git-master.md

**Add to Workflow I section**:

```markdown
## Workflow I: PR Review Comments (GitHub-MCP Version)

### MCP-Based Review Posting

With GitHub-MCP configured, git-master can use MCP tools instead of gh CLI:

#### Via Findings File (Recommended)
```bash
git: post-review-from-findings 66 temp/AGENT_REPORTS/[feature]/CODE_REVIEWER_FINDINGS.yaml
```

#### Direct MCP Call

```bash
git: post-review-mcp 66 --verdict approved --message "Looks good!"
```

### MCP vs gh CLI Comparison

| Feature | GitHub-MCP | gh CLI |
|---------|-----------|--------|
| API Access | Direct via MCP | Via command wrapper |
| Approval Required | Per-session auth | GITHUB_TOKEN only |
| Installation | npm install | Pre-installed (usually) |
| Performance | MCP-optimized | Standard |

```

### 2. Update code-reviewer.md

Replace references to `git: pr-comment` with:

```markdown
## Posting Reviews via Git-Master

Reviews are posted using git-master with GitHub-MCP:

**Standard Pattern**:
```bash
git: post-review-from-findings PR_NUMBER path/to/findings.yaml
```

**Example**:

```bash
git: post-review-from-findings 66 temp/AGENT_REPORTS/feature-x/CODE_REVIEWER_FINDINGS.yaml
```

The findings file uses the same YAML format (see git-master.md for template).

```

### 3. Update security-reviewer.md

Apply same changes as code-reviewer.md but reference security findings:

```markdown
# Security Review via GitHub-MCP

Post security findings to PR using git-master:

```bash
git: post-review-from-findings PR_NUMBER temp/AGENT_REPORTS/feature-x/SECURITY_REVIEWER_FINDINGS.yaml
```

```

## Findings File Format (Unchanged)

The YAML findings file format remains the same (documented in git-master.md):

```yaml
pr: 66
reviewer: code-reviewer
verdict: approved  # approved | changes-requested | comment-only

inline:
  - file: "path/to/file.md"
    line: 105
    label: suggestion
    body: "Comment text"

file_level:
  - file: "path/to/file.md"
    label: issue
    body: "File-level feedback"

pr_summary: |
  Overall assessment of the PR...
```

## Testing Phase 2 Integration

### 1. Create Test PR

```bash
git checkout -b test/phase2-mcp-test
echo "# Test PR for Phase 2" >> README.md
git add README.md
git commit -m "test(phase2): verify GitHub-MCP integration"
git push -u origin test/phase2-mcp-test
gh pr create --title "test(phase2): verify GitHub-MCP integration" \
  --body "Testing Phase 2 GitHub-MCP review posting"
```

### 2. Create Findings File

Create `temp/AGENT_REPORTS/phase2-test/CODE_REVIEWER_FINDINGS.yaml`:

```yaml
pr: REPLACE_WITH_PR_NUMBER
reviewer: code-reviewer
verdict: approved
summary: "Test review via GitHub-MCP"

inline:
  - file: "README.md"
    line: 1
    label: praise
    body: "praise: Good test setup!"

pr_summary: |
  This is a test PR for GitHub-MCP integration.
  Everything looks good. GitHub-MCP is working!
```

### 3. Post Review via Git-Master

```bash
git: post-review-from-findings PR_NUMBER temp/AGENT_REPORTS/phase2-test/CODE_REVIEWER_FINDINGS.yaml
```

**Expected Result**:

- Review posted to PR within 2 minutes
- Inline comment visible on README.md:1
- PR summary comment appears
- No additional approval prompts

### 4. Verify Success

```bash
gh pr view PR_NUMBER --json reviews
gh pr view PR_NUMBER  # Check comments
```

## Troubleshooting

### GitHub-MCP Not Found

```
Error: GitHub-MCP not installed
```

**Fix**:

```bash
npm install -g @anthropic-ai/mcp-github
```

### Token Issues

```
Error: GITHUB_TOKEN not found or invalid
```

**Fix**:

```bash
export GITHUB_TOKEN="ghp_your_token"
# Verify: echo $GITHUB_TOKEN
```

### MCP Connection Failed

```
Error: Cannot connect to GitHub MCP server
```

**Fix**:

1. Check `.mcp.json` syntax (must be valid JSON)
2. Verify GitHub-MCP is installed
3. Verify GITHUB_TOKEN is set and valid
4. Check network connectivity

### Review Not Posted

```
Error: POST /repos/{owner}/{repo}/pulls/{pr}/reviews failed
```

**Causes**:

- PR number is invalid
- GITHUB_TOKEN lacks `pull-requests:write` scope
- File path in findings doesn't exist
- Line number out of range

**Fix**:

- Verify PR number: `gh pr view N`
- Check token scopes
- Verify findings file path
- Check line numbers in diff

## Phase 2 Completion Checklist

- [ ] GitHub-MCP installed globally or locally
- [ ] `.mcp.json` updated with GitHub server config
- [ ] `GITHUB_TOKEN` environment variable set
- [ ] `GITHUB_TOKEN` has required scopes (repo, pull-requests:write)
- [ ] git-master.md updated with GitHub-MCP workflows
- [ ] code-reviewer.md updated with MCP routing
- [ ] security-reviewer.md updated with MCP routing
- [ ] Test PR created and verified
- [ ] Inline comments posted successfully
- [ ] PR summary posted successfully
- [ ] All tests passing with GitHub-MCP enabled

## Phase 2 Success Metrics

- ✅ Reviews posted in <2 minutes after git-master request
- ✅ No per-call approval friction (single git-master invocation)
- ✅ Reviews visible in GitHub PR timeline with file:line anchors
- ✅ Both inline and PR summary comments working
- ✅ Multiple reviewers can post independently

## When Phase 2 is Complete

After Phase 2:

- Code Reviewer can post reviews: `git: post-review-from-findings PR_NUMBER [findings]`
- Security Reviewer can post reviews: Same pattern
- git-master routes all reviews through GitHub-MCP
- Findings file format is standardized and documented
- No manual approval needed per review (only initial git-master auth)

## References

- [GitHub MCP Documentation](https://github.com/anthropics/anthropic-sdk-python/blob/main/examples/mcp/github.py)
- [git-master.md Workflow I](../.claude/agents/git-master.md#workflow-i-pr-review-comments)
- [GitHub Personal Access Tokens](https://github.com/settings/tokens)
- [Phase 2 Implementation Plan](../temp/archive/v0.7-design/IMPLEMENTATION_PLAN_v0.7.md)
