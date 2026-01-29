# Agent Orchestration Guide

**Purpose**: This guide ensures smooth agent orchestration and handoff across sessions by documenting best practices, common pitfalls, and when to use which approach.

**Last Updated**: 2026-01-25
**Status**: Living Document

---

## Quick Reference

### When to Use Agents

| Task Type | Approach | Agent | Reason |
| ----------- | ---------- | ------- | -------- |
| Architecture design | **Agent** | `everything-claude-code:architect` | Specialized expertise, thorough analysis |
| Complex algorithms | **Agent** | `everything-claude-code:architect` | Need deep technical review |
| Feature implementation | **Agent** | `feature-dev:code-architect` → Developer | Structured workflow |
| Code review | **Agent** | `everything-claude-code:code-reviewer` | Objective quality checks |
| Security review | **Agent** | `everything-claude-code:security-reviewer` | Specialized security knowledge |
| Documentation | **Agent** | `everything-claude-code:doc-updater` | Structured, thorough docs |
| Typo fix | **Manual** | Direct | Too simple for agent overhead |
| Small CSS tweak | **Manual** | Direct | Quick, obvious change |
| Exploratory research | **Agent** | `Explore` | Thorough codebase analysis |

### Critical Rule: Be Explicit About File Operations

**❌ Don't:**

```javascript
Task({
  prompt: "Design the localStorage schema for kanji progress",
  subagent_type: "everything-claude-code:architect"
})
```

**✅ Do:**

```javascript
Task({
  prompt: "Design the localStorage schema for kanji progress.

  DELIVERABLES (must write to disk):
  1. temp/kanji-storage-schema.js - Complete implementation
  2. temp/T1.1-SCHEMA-DESIGN-DOC.md - Design documentation

  Use the Write tool to create these files.",
  subagent_type: "everything-claude-code:architect",
  allowed_tools: ["Write", "Edit", "Read", "Grep", "Glob"]
})
```

---

## Table of Contents

1. [Agent File Structure](#agent-file-structure)
2. [Core Principles](#core-principles)
3. [Agent Handoff Best Practices](#agent-handoff-best-practices)
4. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
5. [Agent Selection Guide](#agent-selection-guide)
6. [Token Optimization & Code Simplification](#token-optimization--code-simplification)
7. [Assembly Line Workflows](#assembly-line-workflows)
8. [Verification Checklist](#verification-checklist)
9. [Examples from T1.1 Case Study](#examples-from-t11-case-study)
10. [Related Documentation](#related-documentation)

---

## Agent File Structure

All agent files use YAML frontmatter for machine-parseable metadata, enabling context optimization and automatic tool grants.

### Frontmatter Schema

```yaml
---
name: agent-name          # Matches filename (without .md)
description: One-line summary for agent selection UI
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: opus               # Default model (opus/sonnet/haiku)
---
```

### Field Reference

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Agent identifier, matches filename |
| `description` | Yes | Concise summary (<100 chars) for selection |
| `tools` | Yes | Auto-granted tools when agent invoked |
| `model` | No | Default model preference |

### Benefits

1. **Context Optimization**: Metadata can be extracted without loading full agent content
2. **Auto Tool Grants**: Tools array eliminates need for `allowed_tools` in Task calls
3. **Agent Selection**: Description enables quick identification of right agent for task
4. **Model Hints**: Preferred model for agent's workload type

### Enhanced Sections

Priority agents include additional guidance sections:

| Section | Purpose | Agents |
|---------|---------|--------|
| **Red Flags** | Anti-patterns to watch for | architect, code-reviewer, security-reviewer, tester |
| **Common Patterns** | Code examples with ❌/✅ | architect, code-reviewer |

### Example Usage

When frontmatter includes tools, Task calls become simpler:

```javascript
// ❌ Old pattern (manual tool grants)
Task({
  prompt: "Review the authentication code...",
  subagent_type: "code-reviewer",
  allowed_tools: ["Read", "Grep", "Glob", "Bash"]  // Had to specify
})

// ✅ New pattern (auto-granted from frontmatter)
Task({
  prompt: "Review the authentication code...",
  subagent_type: "code-reviewer"
  // Tools auto-granted: ["Read", "Grep", "Glob", "Bash"]
})
```

### Validation

Run frontmatter validation to ensure all agents have valid metadata:

```bash
bash scripts/validate-frontmatter.sh
```

---

## Core Principles

### Principle 1: Agents Return Content for Review

**Key Insight**: Agents are designed to **return content in their response** rather than automatically writing files. This is a safety feature.

**Why This Matters**:

- Prevents agents from modifying codebase without oversight
- Allows review before committing changes
- Gives control over where files are created

**Action**: Always explicitly instruct agents to **write files to disk** if that's what you want.

### Principle 2: Explicit Deliverables

**Bad (Vague)**:
> "Design the authentication system"

**Good (Explicit)**:
> "Design the authentication system. Write these files:
>
> 1. `temp/auth-schema.js` - Schema definition
> 2. `temp/AUTH_DESIGN.md` - Design document
> 3. `temp/auth-api.js` - API interface
> Use the Write tool for each file."

### Principle 3: Grant Necessary Tools

**With Frontmatter (Preferred)**: Agent files with YAML frontmatter auto-grant tools specified in the `tools` array. No `allowed_tools` needed in Task calls.

**Without Frontmatter (Legacy)**: Grant file operation permissions explicitly:

```javascript
Task({
  allowed_tools: ["Write", "Edit", "Read", "Grep", "Glob", "Bash"],
  // ... other params
})
```

**Common tool needs by role**:

| Role | Tools | Auto-Granted? |
|------|-------|---------------|
| **Architect** | Write, Read, Grep, Glob | ✅ Yes |
| **Developer** | Write, Edit, Read, Bash, Grep, Glob | ✅ Yes |
| **Code Reviewer** | Read, Grep, Glob, Bash | ✅ Yes |
| **Security Reviewer** | Read, Write, Edit, Bash, Grep, Glob | ✅ Yes |
| **Tester** | Read, Bash, Grep, Glob | ✅ Yes |
| **Documenter** | Read, Write, Edit, Grep, Glob | ✅ Yes |

**Note**: All 11 project agents now have frontmatter with auto-granted tools.

### Principle 4: Verify Agent Output

After agent completes, **always verify** deliverables:

```javascript
// Check if files were created
Bash({ command: "ls -lh temp/kanji-storage-schema.js" })

// If file doesn't exist, agent returned content in response
// Extract content manually or re-run agent with explicit instructions
```

---

## Agent Handoff Best Practices

### 1. Pre-Handoff: Prepare Context

Before calling an agent, ensure they have access to:

- **PRDs**: Link to relevant spec in `docs/specs/`
- **Task details**: GitHub issue number and acceptance criteria
- **Related work**: Point to similar completed tasks
- **Constraints**: File naming, structure, dependencies

**Example**:

```javascript
Task({
  prompt: `You are the architect for Task T1.2 (GitHub #14).

  Context:
  - PRD: docs/specs/PRD-001-JLPT-Mastery-Engine.md
  - Previous task: T1.1 (schema design) completed
  - Schema file: temp/kanji-storage-schema.js

  Your task: Implement SM-2 algorithm based on the schema.

  Deliverables:
  1. kanji/js/srs-engine.js - SM-2 implementation
  2. temp/T1.2-TESTING.md - Test plan

  Use Write tool to create files.`,
  subagent_type: "everything-claude-code:architect"
})
```

### 2. During Handoff: Clear Instructions

Structure your agent prompt with:

1. **Role**: "You are the [architect/developer/reviewer]"
2. **Context**: Links to relevant docs, previous work
3. **Task**: Specific objective from GitHub issue
4. **Deliverables**: Exact files to create with paths
5. **Tools**: Mention tools to use (Write, Edit, etc.)
6. **Constraints**: File conventions, dependencies, limits

### 3. Post-Handoff: Verification

```javascript
// 1. Check agent completed
TaskOutput({ task_id: "agent_id" })

// 2. Verify files exist
Bash({ command: "ls -lh temp/*.js temp/*.md" })

// 3. Validate content
Read({ file_path: "temp/kanji-storage-schema.js" })

// 4. If missing, extract from agent response
// (See "Common Pitfalls" section)
```

### 4. Handoff to Next Agent

When chaining agents (assembly line), include:

- **Previous agent's output**: Links to files created
- **Next steps**: What this agent should build on
- **Dependencies**: What to read first

**Example**:

```javascript
// After Architect completes schema design...
Task({
  prompt: `You are the Developer implementing T1.2.

  Build on previous work:
  - Schema: temp/kanji-storage-schema.js (read this first)
  - Design doc: temp/T1.1-SCHEMA-DESIGN-DOC.md

  Your task: Implement SM-2 algorithm using the schema.

  Deliverables:
  1. kanji/js/srs-engine.js - Implementation
  2. kanji/js/srs-engine.test.js - Unit tests

  Use Write tool for new files.`,
  subagent_type: "feature-dev",
  allowed_tools: ["Write", "Read", "Bash"]
})
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Agent Returns Content Instead of Writing Files

**Symptom**: Agent response includes complete code, but `ls temp/` shows files don't exist.

**Root Cause**: Agent wasn't explicitly told to write files, or lacked Write permission.

**Solution**:

1. Extract content from agent response
2. Write files manually using Write tool
3. For future: Add explicit "Use Write tool" instruction

**Example Fix**:

```javascript
// After realizing agent didn't write files
Write({
  file_path: "temp/kanji-storage-schema.js",
  content: `/* extract from agent response */`
})
```

**Prevention**:

- Always include "Use the Write tool to create these files" in prompt
- Grant `allowed_tools: ["Write", ...]`
- Verify files exist after agent completes

### Pitfall 2: Agent Lacks Context from Previous Work

**Symptom**: Agent designs something from scratch that conflicts with existing decisions.

**Root Cause**: Agent didn't read previous work or wasn't told where to find it.

**Solution**:

```javascript
Task({
  prompt: `IMPORTANT: First read these files for context:
  1. temp/kanji-storage-schema.js - Schema you'll implement
  2. docs/specs/PRD-001-JLPT-Mastery-Engine.md - Requirements

  Then implement... [rest of task]`,
  subagent_type: "feature-dev"
})
```

### Pitfall 3: Agent Over-Engineers Simple Task

**Symptom**: Agent produces 500 lines for a 10-line fix.

**Root Cause**: Used specialized agent for simple task.

**Solution**: Don't use agents for trivial tasks. Direct implementation is faster and simpler.

**Rule of Thumb**:

- **< 3 file changes**: Manual
- **Single obvious fix**: Manual
- **Complex logic/architecture**: Agent

### Pitfall 4: Unclear Acceptance Criteria

**Symptom**: Agent delivers something different from what was needed.

**Root Cause**: Prompt didn't include specific acceptance criteria from GitHub issue.

**Solution**:

```javascript
Task({
  prompt: `Task T1.2 from GitHub issue #14.

  Acceptance Criteria (from issue):
  - [ ] Function calculates correct interval for repetitions 0, 1, 2+
  - [ ] Ease factor adjusts based on quality rating (0-5)
  - [ ] Quality < 3 resets repetitions to 0
  - [ ] Returns next review date

  Implement SM-2 algorithm meeting ALL criteria above.`,
  subagent_type: "feature-dev"
})
```

### Pitfall 5: Agent Can't Find Files

**Symptom**: Agent says "file not found" for files that exist.

**Root Cause**: Relative paths from agent's execution context differ.

**Solution**: Use absolute paths or project-relative paths:

```javascript
// ❌ Relative (may fail)
"Read ../temp/schema.js"

// ✅ Absolute or project-relative
"Read /Users/cmbays/Documents/claude/japanese-study-site/temp/schema.js"
"Read temp/schema.js (from project root)"
```

---

## Agent Selection Guide

### Architecture & Design

**Agent**: `everything-claude-code:architect`

**When to use**:

- Designing system architecture
- Technical decision documents (TDDs)
- Database schema design
- API interface design
- Evaluating architectural trade-offs

**Example**:

```javascript
Task({
  description: "Design authentication architecture",
  prompt: "Design OAuth 2.0 authentication system...",
  subagent_type: "everything-claude-code:architect",
  allowed_tools: ["Write", "Read", "Grep", "Glob"]
})
```

**Deliverables**: Design docs, architecture diagrams, schemas

### Feature Implementation

**Agent**: `feature-dev:code-architect` → `feature-dev` developer

**When to use**:

- Building new features
- Multi-file implementations
- Complex business logic
- Following existing patterns

**Example**:

```javascript
// Step 1: Architecture
Task({
  description: "Plan flashcard feature",
  prompt: "Analyze codebase and design flashcard system...",
  subagent_type: "feature-dev:code-architect"
})

// Step 2: Implementation
Task({
  description: "Implement flashcard feature",
  prompt: "Build flashcard system per architecture...",
  subagent_type: "feature-dev"
})
```

### Code Review

**Agent**: `everything-claude-code:code-reviewer`

**When to use**:

- After completing implementation
- Before merging PRs
- Checking for bugs, security issues
- Verifying best practices

**Example**:

```javascript
Task({
  description: "Review authentication code",
  prompt: "Review kanji/js/srs-engine.js for bugs, security, quality...",
  subagent_type: "everything-claude-code:code-reviewer",
  allowed_tools: ["Read", "Grep", "Glob"]
})
```

**Deliverables**: Review report, suggested fixes

### Security Review

**Agent**: `everything-claude-code:security-reviewer`

**When to use**:

- Authentication/authorization code
- User input handling
- API endpoints
- Data storage logic
- Before deploying sensitive features

**Example**:

```javascript
Task({
  description: "Security audit localStorage schema",
  prompt: "Review temp/kanji-storage-schema.js for security vulnerabilities...",
  subagent_type: "everything-claude-code:security-reviewer"
})
```

### Testing

**Agent**: `everything-claude-code:tdd-guide` or `everything-claude-code:e2e-runner`

**When to use**:

- Writing unit tests
- Creating E2E test suites
- Verifying test coverage
- TDD workflow enforcement

**Example**:

```javascript
Task({
  description: "Write SM-2 algorithm tests",
  prompt: "Create unit tests for kanji/js/srs-engine.js...",
  subagent_type: "everything-claude-code:tdd-guide"
})
```

### Documentation

**Agent**: `everything-claude-code:doc-updater`

**When to use**:

- Updating codemaps
- Writing technical documentation
- Creating API reference
- Maintaining living docs

**Example**:

```javascript
Task({
  description: "Update architecture docs",
  prompt: "Update docs/ARCHITECTURE.md with new SRS engine...",
  subagent_type: "everything-claude-code:doc-updater"
})
```

### Codebase Exploration

**Agent**: `Explore`

**When to use**:

- Understanding unfamiliar codebase
- Finding files by pattern
- Researching implementation details
- Tracing execution paths

**Example**:

```javascript
Task({
  description: "Find all kanji data files",
  prompt: "Search for all files containing kanji data and explain structure...",
  subagent_type: "Explore",
  model: "haiku" // Fast for exploration
})
```

### Changelog Generation (Horizontal Service)

**Agent**: Changelog Generator (`changelog:` prefix)

Changelog Generator is a **horizontal service agent** — invoked by the Documenter or Deploy workflow to automate changelog entries from git history.

**When to use**:

- Generating changelog entries for a release
- Creating release notes for tags or PRs
- Checking for breaking changes since last tag
- Any time CHANGELOG.md needs updating from git history

**How it works**:

```
┌─────────────────────────────────────────────────────────┐
│  Documenter or /deploy workflow                         │
│  "Generate changelog for v0.5.0"                        │
└────────────────────────┬────────────────────────────────┘
                         │ Delegates to
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Changelog Generator                                    │
│  - Scans git log between tags                           │
│  - Parses Conventional Commits                          │
│  - Categorizes by impact (Breaking/Added/Fixed/etc)     │
│  - Outputs draft to temp/ for review                    │
└─────────────────────────────────────────────────────────┘
```

**Example**:

```javascript
Task({
  description: "Generate changelog since v0.4.0",
  prompt: `Generate changelog entries for v0.5.0.
  Base: v0.4.0, Head: HEAD.
  Write draft to temp/CHANGELOG_DRAFT_v0.5.0.md`,
  subagent_type: "changelog-generator"
})
```

**See**: [[changelog-generator.md]] for full persona details, [[../skills/changelog-generation.md]] for workflow.

### Git Operations (Horizontal Service)

**Agent**: Git-Master (`git:` prefix)

Git-Master is a **horizontal service agent** - unlike vertical agents that own specific workflow phases, Git-Master is invoked by ANY agent needing git operations.

**When to use**:

- Creating branches, commits, tags
- Creating or merging pull requests
- Any git write operation
- All agents delegate git work to git-master

**How it works**:

```
┌─────────────────────────────────────────────────────────┐
│  Any Agent (Developer, Documenter, etc.)                │
│  "I need to commit these changes"                       │
└────────────────────────┬────────────────────────────────┘
                         │ Delegates to
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Git-Master                                             │
│  - Validates format (Conventional Commits)              │
│  - Checks safety rules                                  │
│  - Executes with GIT_MASTER_AUTHORIZED=true             │
│  - Logs to audit trail                                  │
└─────────────────────────────────────────────────────────┘
```

**Commands**:

- `/commit` - Create validated commit
- `/branch` - Create validated branch

**Example**:

```javascript
// From any agent workflow
"git: commit my changes with message 'feat(kanji): add filter'"
"git: create branch feat/new-feature"
"git: create PR for current branch"
```

**Enforcement**:

- `pre-bash-check.js` BLOCKS direct git write operations
- Only git-master can set `GIT_MASTER_AUTHORIZED=true`
- All operations logged to audit trail

**See**: [[git-master.md]] for full persona details, [[../skills/git-operations.md]] for workflows.

---

## Token Optimization & Code Simplification

This section addresses reducing AI token burn-rate and context window usage through strategic use of simplification and cleanup agents.

**Philosophy**: The project's principle of "right amount of complexity is minimum needed" extends to token efficiency. Every unnecessary line of code burns tokens during review, testing, and future maintenance.

### Code-Simplifier Plugin Integration

The `code-simplifier` plugin helps identify and eliminate unnecessary complexity before it enters the codebase.

**When to Activate**:

- During code review (catch over-engineering)
- During architecture phase (design simply from start)
- During refactoring passes (batch cleanup)
- Before major releases (reduce baseline complexity)

### Agent Skill Matrix: Token-Optimized Tools

| Agent | Primary Tools | Add for Simplification | Use case |
|-------|---------------|------------------------|----------|
| **Architect** | Write, Read, Grep, Glob | **code-simplifier** | Design minimal from start |
| **Developer** | Write, Edit, Read, Bash | **code-simplifier** | Validate minimal implementation |
| **Code Reviewer** | Read, Grep, Glob | **code-simplifier** | Catch over-engineering before merge |
| **Refactor-Cleaner** | Write, Edit, Read, Bash, Grep, Glob | **code-simplifier** | Batch consolidation & cleanup |
| **Security Reviewer** | Read, Grep, Glob | *optional* | Identify security complexity |
| **Tester** | Read, Bash, Grep | *optional* | Identify test duplication |

### Token Burn Reduction Pipeline

```
Design Phase       Arch with code-simplifier
                   └─→ Simple, lean design
                       │
Implementation      Dev with code-simplifier
                   └─→ Minimal code
                       │
Review Phase        Code Reviewer + code-simplifier
                   └─→ Block over-complex PRs
                       │
Cleanup Phase       Refactor-Cleaner quarterly
                   └─→ Consolidate patterns, remove duplication
```

### Using Code-Simplifier with Agents

#### 1. Architect: Design for Simplicity

```javascript
Task({
  description: "Design kanji filtering system",
  prompt: `Design the kanji filtering architecture.

  IMPORTANT: Use code-simplifier to evaluate design complexity:
  - Identify unnecessary layers or abstraction
  - Validate that each component is truly needed
  - Suggest minimal implementation patterns

  DELIVERABLES:
  1. temp/kanji-filter-design.md - Design document
  2. temp/kanji-filter-schema.js - Data structure

  Use Write tool.`,
  subagent_type: "everything-claude-code:architect",
  allowed_tools: ["Write", "Read", "Grep", "Glob", "code-simplifier"]
})
```

**Expected Output**: Lean design without premature abstraction.

#### 2. Developer: Implement Minimally

```javascript
Task({
  description: "Implement kanji filtering",
  prompt: `Implement kanji filtering per design in temp/kanji-filter-design.md.

  Use code-simplifier to:
  - Ensure no unnecessary functions or helpers
  - Validate implementation matches minimal design
  - Flag any over-engineering detected

  DELIVERABLES:
  1. kanji/js/filters.js - Implementation
  2. kanji/js/filters.test.js - Tests

  Use Write tool.`,
  subagent_type: "feature-dev",
  allowed_tools: ["Write", "Edit", "Read", "Bash", "code-simplifier"]
})
```

**Expected Output**: Implementation with no unnecessary complexity.

#### 3. Code Reviewer: Enforce Simplicity Gate

```javascript
Task({
  description: "Review kanji implementation for complexity",
  prompt: `Review kanji/js/filters.js using code-simplifier:
  - Flag any functions that could be consolidated
  - Identify unnecessary abstractions
  - Check for code duplication
  - Validate test coverage is proportional to complexity

  Report findings and recommend simplifications.`,
  subagent_type: "everything-claude-code:code-reviewer",
  allowed_tools: ["Read", "Grep", "Glob", "code-simplifier"]
})
```

**Expected Output**: Review report with simplification recommendations. PR must address critical complexity flags before merge.

#### 4. Refactor-Cleaner: Batch Consolidation

**Frequency**: Quarterly or after 3+ features land

```javascript
Task({
  description: "Quarterly code simplification and consolidation",
  prompt: `Analyze entire codebase for simplification opportunities:

  Use code-simplifier to identify:
  - Duplicate patterns across topics/
  - Unused functions or exports
  - Over-engineered components
  - Opportunities for consolidation

  Create consolidation plan with:
  1. Priority ranking (impact/effort)
  2. Before/after token cost analysis
  3. Risk assessment for each consolidation

  DELIVERABLE:
  - temp/CONSOLIDATION_PLAN.md - Detailed plan

  Do NOT implement yet, only analyze and plan.`,
  subagent_type: "everything-claude-code:refactor-cleaner",
  allowed_tools: ["Read", "Grep", "Glob", "code-simplifier"]
})
```

**Expected Output**: Strategic consolidation plan. Review plan before execution to prioritize highest-ROI simplifications.

### Metrics: Token Burn Baseline

Track these metrics to validate improvement:

| Metric | Measurement | Target |
|--------|-------------|--------|
| **Lines per Feature** | Total lines / feature count | Decrease trend |
| **Complexity Flags** | code-simplifier issues per PR | ↓ 50% YoY |
| **Dead Code** | Unused functions/exports | < 2% of codebase |
| **Duplication Ratio** | Similar patterns / total code | < 5% |
| **Test:Code Ratio** | Test lines / implementation lines | 0.8-1.2x |

### Agent Token Metrics (Current)

All 11 agents with YAML frontmatter:

| Category | Count | ~Tokens |
|----------|-------|---------|
| Agent files | 11 | ~18,587 |
| With Red Flags | 4 | architect, code-reviewer, security-reviewer, tester |
| With Code Examples | 2 | architect, code-reviewer |

**Frontmatter ROI**: ~20-30 tokens saved per Task call (no `allowed_tools` needed)

Run `bash scripts/count-agent-tokens.sh` to measure current state.

### Implementation Strategy

**Phase 1: Immediate (This Sprint)**
- Add code-simplifier to Code Reviewer's tool set
- Run code-simplifier on all incoming PRs
- Document findings in review comments

**Phase 2: Standard (Next 2 Sprints)**
- Add code-simplifier to Architect (design phase)
- Add code-simplifier to Developer (implementation)
- Create quarterly Refactor-Cleaner task

**Phase 3: Optimization (Month 2+)**
- Analyze token savings from Phase 1-2
- Adjust agent skill matrix based on learnings
- Document patterns that increased/decreased complexity

---

## Assembly Line Workflows

### Standard Feature Development Pipeline

```
PM → Architect → Developer → Tester → Reviewer → Documenter
```

#### **1. PM: Define Requirements**

- Create PRD in `docs/specs/`
- Create GitHub issue with acceptance criteria
- Link PRD to issue

#### **2. Architect: Design System**

```javascript
Task({
  prompt: "Design [feature] architecture based on PRD...",
  subagent_type: "everything-claude-code:architect"
})
```

**Output**: TDD, schema, API design

#### **3. Developer: Implement**

```javascript
Task({
  prompt: "Implement [feature] per TDD in docs/tdd/...",
  subagent_type: "feature-dev"
})
```

**Output**: Implementation files, initial tests

#### **4. Tester: Verify**

```javascript
Task({
  prompt: "Test [feature] implementation per acceptance criteria...",
  subagent_type: "everything-claude-code:tdd-guide"
})
```

**Output**: Test results, test coverage report

#### **5. Reviewer: Quality Check**

```javascript
Task({
  prompt: "Review [feature] code for quality, security, performance...",
  subagent_type: "everything-claude-code:code-reviewer"
})
```

**Output**: Review report, improvement suggestions

#### **6. Documenter: Update Docs**

```javascript
Task({
  prompt: "Update docs with [feature] details...",
  subagent_type: "everything-claude-code:doc-updater"
})
```

**Output**: Updated living docs, codemaps

#### **6b. Changelog Generator: Automated Changelog**

Invoked by Documenter during step 6 or by `/deploy`:

```javascript
Task({
  description: "Generate changelog for release",
  prompt: "Generate changelog entries since last tag. Write to temp/CHANGELOG_DRAFT.md",
  subagent_type: "changelog-generator"
})
```

**Output**: Draft changelog entries for review and curation

### Expedited Pipeline (Simple Features)

```
Architect → Developer → Reviewer
```

Skip PM (use GitHub issue as spec) and Tester (developer writes tests).

### Bug Fix Pipeline

`Explorer → Developer → Tester → Reviewer`

1. **Explorer**: Understand bug context
2. **Developer**: Fix with tests
3. **Tester**: Verify fix
4. **Reviewer**: Check for regressions

---

## Verification Checklist

After any agent completes, verify:

### ✅ Files Created

```bash
# Check expected deliverables exist
ls -lh temp/*.js temp/*.md

# If missing, check agent response for content
```

### ✅ Content Quality

```bash
# Read key files
cat temp/kanji-storage-schema.js | head -50

# Check for:
# - Proper structure
# - Comments/documentation
# - No placeholder/TODO code
```

### ✅ Acceptance Criteria Met

Compare agent output to GitHub issue acceptance criteria:

- [ ] All checkboxes addressed
- [ ] Technical requirements met
- [ ] Edge cases handled

### ✅ Integration Points

- [ ] Follows existing code patterns
- [ ] Compatible with adjacent systems
- [ ] Doesn't break existing functionality

### ✅ Documentation

- [ ] Code comments present
- [ ] Design docs created
- [ ] Usage examples included
- [ ] Edge cases documented

---

## Examples from T1.1 Case Study

### What Went Wrong (First Attempt)

**Agent call**:

```javascript
Task({
  description: "Design localStorage schema architecture",
  prompt: "Design the localStorage schema for kanji SRS progress tracking...",
  subagent_type: "everything-claude-code:architect"
})
```

**Result**: Agent returned complete code in response but didn't write files.

**Why**: No explicit "write files" instruction, no Write tool granted.

### What Went Right (Corrected)

**Agent call** (what should have been):

```javascript
Task({
  description: "Design localStorage schema architecture",
  prompt: `Design the localStorage schema for kanji SRS progress tracking.

  DELIVERABLES (write to disk):
  1. temp/kanji-storage-schema.js - Complete schema implementation
  2. temp/T1.1-SCHEMA-DESIGN-DOC.md - Comprehensive design document

  Use the Write tool to create both files.`,
  subagent_type: "everything-claude-code:architect",
  allowed_tools: ["Write", "Read", "Grep", "Glob"]
})
```

**Result**: Agent would have created files directly.

### Quality Comparison Results

**Manual approach** (543 lines):

- Basic constants
- Simple validation
- 2 helper functions
- Works but minimal

**Agent approach** (1032 lines):

- Immutable constants (`Object.freeze()`)
- 8 helper functions
- CJK Unicode validation
- Browser + Node.js compatibility
- Future-proofing (client_id, streak_start_date)
- 87% more code, better quality

**Lesson**: Agent orchestration produces higher quality for complex tasks, but requires explicit instructions.

---

## Related Documentation

### Core Documentation

- [[CLAUDE.md]] - Project instructions and agent orchestration overview
- [[.claude/agents/README.md]] - Agent persona definitions
- [[.claude/skills/README.md]] - Reusable workflow skills
- [[.claude/contexts/README.md]] - Context configurations

### Workflows

- [[docs/WORKFLOW_EXCEPTIONS.md]] - Approved deviations from standard workflow
- [[.claude/skills/tdd-workflow.md]] - Test-driven development process
- [[.claude/skills/code-review-workflow.md]] - Code review process
- [[.claude/skills/deployment-workflow.md]] - Release management

### Standards

- [[.claude/rules/coding-style.md]] - Code conventions
- [[.claude/rules/git-workflow.md]] - Version control standards
- [[.claude/rules/testing.md]] - Testing requirements
- [[.claude/rules/security.md]] - Security guidelines

### Case Studies

- [[archive/FOR_CHRIS_docs/agent-orchestration-comparison.md]] - T1.1 manual vs agent comparison
- [[docs/reviews/]] - Past code reviews
- [[docs/tdd/]] - Technical design documents

### GitHub Integration

- [[docs/PROJECT_BOARD_GUIDE.md]] - GitHub Projects workflow
- [[.github/ISSUE_TEMPLATE/]] - Issue templates
- [[.github/PULL_REQUEST_TEMPLATE.md]] - PR template

---

## Quick Tips

### 🎯 Golden Rules

1. **Be explicit**: Tell agents exactly which files to write
2. **Grant tools**: Include `allowed_tools: ["Write", "Read", ...]`
3. **Verify output**: Check files exist after agent completes
4. **Provide context**: Link to PRDs, previous work, related docs
5. **Simple tasks**: Do manually, don't over-engineer with agents

### 🚫 Common Mistakes

1. Vague instructions: "Design the thing" → No files created
2. No tool permissions: Agent can't write files
3. Wrong agent: Using architect for simple bug fix
4. Missing context: Agent designs incompatible solution
5. No verification: Assuming files were created

### ✨ Success Pattern

```javascript
// 1. Prepare context
const prd = "docs/specs/PRD-001.md";
const relatedWork = "temp/previous-task-output.js";

// 2. Call agent with explicit instructions
Task({
  description: "Design authentication system",
  prompt: `You are the Architect for Task T2.5 (GitHub #25).

  Context:
  - PRD: ${prd}
  - Related: ${relatedWork}

  Design OAuth 2.0 authentication system.

  DELIVERABLES (write using Write tool):
  1. temp/auth-schema.js - Database schema
  2. temp/auth-api.js - API interface
  3. temp/AUTH_DESIGN.md - Design document

  Include security considerations, edge cases, and examples.`,
  subagent_type: "everything-claude-code:architect",
  allowed_tools: ["Write", "Read", "Grep", "Glob"]
});

// 3. Verify deliverables
Bash({ command: "ls -lh temp/auth-*" });

// 4. Read and validate
Read({ file_path: "temp/AUTH_DESIGN.md" });

// 5. Proceed to next agent if needed
Task({
  description: "Implement authentication",
  prompt: `Implement auth system per design in temp/AUTH_DESIGN.md...`,
  subagent_type: "feature-dev"
});
```

---

## For New Agents / Fresh Context Sessions

Start here on every new session to quickly orient yourself:

### Essential Reading (Do First)

1. **[[CLAUDE.md]]** - Project context, current phase, critical rules
   - Current status: Kanji Study Module (v0.2)
   - Key workflow: UNDERSTAND -> PLAN -> PROTOTYPE -> BUILD -> VERIFY -> DEPLOY
   - Critical: Never overwrite content files directly

2. **This file (AGENTS.md)** - How to work effectively with the system
   - Agent selection guide
   - Handoff best practices
   - Common pitfalls to avoid

3. **[[docs/PROJECT_BOARD_GUIDE.md]]** - Active tasks and priorities
   - Check "In Progress" column
   - Identify blockers
   - Claim ready tasks

### Role-Specific Reading (Based on Task)

1. **[[.claude/agents/README.md]]** - Your role/persona definition
   - Review your persona's responsibilities
   - Understand handoff expectations
   - Check skill integrations

2. **[[docs/reference/LEARNINGS.md]]** - Technical patterns and decisions
   - Contains proven patterns with real examples
   - Documents decision frameworks
   - Quick reference for common approaches

### Quick Context Checklist

```markdown
- [ ] Read CLAUDE.md (project state)
- [ ] Reviewed active tasks in GitHub Projects
- [ ] Identified my persona for this task
- [ ] Checked for related PRDs in docs/specs/
- [ ] Located any previous work in temp/
```

---

## Documentation Maintenance Protocol

Agents are responsible for keeping documentation current. Follow these protocols to prevent documentation drift.

### When to Update Documentation

| Event | Update These Docs |
|-------|-------------------|
| New feature implemented | ARCHITECTURE.md, relevant skills/*.md |
| New workflow discovered | AGENTS.md, WORKFLOW_EXCEPTIONS.md |
| Bug fixed with learnings | TESTING.md (Bug Learnings section) |
| PRD completed | docs/specs/ (move from draft to approved) |
| TDD completed | docs/tdd/, link from PRD |
| Version deployed | CHANGELOG.md, living docs timestamps |
| Pattern changed | DESIGN_PRINCIPLES.md or CONTENT_STANDARDS.md |
| New persona needed | .claude/agents/README.md, create persona file |

### Documentation Update Workflow

```
1. IDENTIFY which doc(s) need updating
2. READ current state to understand context
3. EDIT with minimal changes (preserve existing structure)
4. ADD wiki-links to related documentation
5. UPDATE "Last Updated" timestamp
6. VERIFY no broken wiki-links created
```

### Cross-Referencing Guidelines

**Always add wiki-links when:**

- Mentioning another document's content
- Referencing a related workflow or skill
- Describing integration with another system
- Pointing to examples or case studies

**Wiki-link format:**

```markdown
[[path/to/file.md]]           # Link to entire file
[[path/to/file.md#section]]   # Link to specific section
```

**Good cross-references:**

```markdown
See [[.claude/skills/tdd-workflow.md]] for testing approach.
Architecture decisions are documented in [[docs/ARCHITECTURE.md#key-architectural-decisions]].
```

### Avoiding Redundancy

**Before adding information, check:**

1. Does this already exist in another doc?
2. If yes, link to it instead of duplicating
3. If the other doc is incomplete, enhance IT rather than creating new content

**Authoritative sources:**

| Topic | Authoritative Document |
| ------- | ------------------------ |
| Agent orchestration | `.claude/agents/AGENTS.md` (this file) |
| Agent personas | `.claude/agents/README.md` |
| Reusable workflows | `.claude/skills/*.md` |
| Coding standards | `.claude/rules/*.md` |
| Project structure | `docs/PROJECT_STRUCTURE.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Japanese content | `docs/CONTENT_STANDARDS.md` |
| UI/UX patterns | `docs/DESIGN_PRINCIPLES.md` |
| Testing approach | `docs/TESTING.md` |
| Task management | `docs/PROJECT_BOARD_GUIDE.md` |

### When Discovering Redundancy

```markdown
1. Identify which document should be authoritative
2. Keep detailed content in authoritative source
3. Replace duplicate with wiki-link: "See [[authoritative.md#section]]"
4. Note consolidation in commit message
```

### Documentation Quality Checklist

Before committing documentation changes:

- [ ] Purpose statement clear at top
- [ ] Table of contents for docs > 100 lines
- [ ] "Last Updated" timestamp current
- [ ] Wiki-links to related docs
- [ ] No broken internal links
- [ ] No redundant content (link instead)
- [ ] Examples are current and working

---

## Related Documentation

### Core Project Documentation

| Document | Purpose | When to Reference |
| ---------- | --------- | ------------------- |
| [[CLAUDE.md]] | Project context, rules, workflows | Every session start |
| [[docs/ARCHITECTURE.md]] | System design, technical decisions | Implementation work |
| [[docs/PROJECT_STRUCTURE.md]] | File organization, naming | Finding/creating files |
| [[docs/DESIGN_PRINCIPLES.md]] | UI/UX standards | Frontend work |
| [[docs/CONTENT_STANDARDS.md]] | Japanese content guidelines | Content creation |
| [[docs/TESTING.md]] | Testing framework, TDD | Verification work |

### Agent System Documentation

| Document | Purpose | When to Reference |
|----------|---------|-------------------|
| [[.claude/agents/README.md]] | Persona definitions | Understanding roles |
| [[.claude/skills/tdd-workflow.md]] | Test-driven development | Implementing features |
| [[.claude/skills/code-review-workflow.md]] | Review process | PR reviews |
| [[.claude/skills/deployment-workflow.md]] | Release management | Version deployment |
| [[.claude/rules/coding-style.md]] | Code conventions | Writing code |
| [[.claude/rules/git-workflow.md]] | Git practices | Version control |
| [[.claude/rules/security.md]] | Security guidelines | Security review |

### Project Management

| Document | Purpose | When to Reference |
|----------|---------|-------------------|
| [[docs/ROADMAP.md]] | Product roadmap, phases | Planning work |
| [[docs/PROJECT_BOARD_GUIDE.md]] | GitHub Projects usage | Task management |
| [[docs/WORKFLOW_EXCEPTIONS.md]] | Approved deviations | Skipping phases |
| [[docs/reference/LEARNINGS.md]] | Patterns, comparisons | Understanding decisions |

### Artifact Locations Summary

| Artifact Type | Location | Managed By |
|---------------|----------|------------|
| PRDs | `docs/specs/PRD-*.md` | PM persona |
| TDDs | `docs/tdd/TDD-*.md` | Architect persona |
| Test specs | `temp/v*_TESTING.md` | Tester persona |
| Build plans | `temp/v*_PLAN.md` | Any persona |
| Work in progress | `temp/` | Developer persona |
| Reviews | `docs/reviews/` | Reviewer personas |
| Version archives | `archive/v*/` | Documenter persona |

---

**Remember**: The goal isn't to always use agents. The goal is to **know when agents add value** and how to use them effectively when they do.

Documentation is code for humans. Keep it current, keep it linked, keep it useful.
