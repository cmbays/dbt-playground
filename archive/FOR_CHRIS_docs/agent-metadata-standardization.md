# For Christopher: Agent Metadata Standardization

**Topic**: Standardizing agent files with YAML frontmatter for better tooling and context optimization

**Created**: 2026-01-25

**Rubric Criteria Met**:
1. Significant architectural decision (YAML frontmatter pattern)
2. Novel pattern (not in existing documentation)
3. Workflow change (validation scripts, agent file structure)
4. High educational value (Agent Orchestration learning goal)

---

## What We Built

This session tackled a deceptively simple question: *How do we make agent files work better for both humans AND machines?*

The answer was YAML frontmatter - a structured metadata block at the top of each agent file that enables:
- **Automatic tool grants** - No more forgetting `allowed_tools` in Task calls
- **Context optimization** - Extract metadata without loading full content
- **Agent selection UI** - Descriptions help choose the right agent
- **Model hints** - Specify preferred model for different workloads

We also added **Red Flags** sections to priority agents (architect, code-reviewer, security-reviewer, tester) and code examples where they add value.

### What Changed

**Before** - Agent files were pure prose:
```markdown
# Technical Architect Persona

## Role Summary
The Technical Architect designs system architecture...
```

**After** - Agent files have machine-parseable headers:
```yaml
---
name: architect
description: System design, TDDs, architecture decisions, pattern consistency
tools: ["Read", "Grep", "Glob", "Write"]
model: opus
---

# Technical Architect Persona

## Role Summary
...
```

---

## Why We Built It This Way

### The Research Phase

Before inventing our own pattern, we researched how other projects handle this. The `everything-claude-code` repository (a well-regarded Claude Code enhancement collection) uses a similar pattern with frontmatter for skills and workflows.

Key insight: **Frontmatter is a well-established pattern in the static site generator world** (Jekyll, Hugo, Astro). It separates metadata from content, allowing tools to process the metadata without parsing the entire document.

### Trade-offs Evaluated

**Option 1: JSON Metadata Files**
- Separate `architect.json` alongside `architect.md`
- Pro: Pure machine-readable
- Con: Two files to maintain, easy to get out of sync
- **Rejected**: Maintenance burden too high

**Option 2: Frontmatter in Markdown**
- Single file, structured header
- Pro: One source of truth, widely understood pattern
- Con: Small token overhead (~20-30 tokens per file)
- **Selected**: Best balance of machine-readability and human-friendliness

**Option 3: External Registry**
- Single `agents-registry.yaml` with all metadata
- Pro: All metadata in one place
- Con: Separated from agent content, defeats co-location principle
- **Rejected**: Violates "keep related things together"

### The "Red Flags" Pattern

We borrowed another pattern from research: **Red Flags sections**. These are anti-patterns specific to each persona's domain:

- **Architect**: "Big Ball of Mud", "Premature Optimization", "God Object"
- **Code Reviewer**: "Incomplete error handling", "Magic numbers", "Copy-paste code"
- **Security Reviewer**: "Hardcoded credentials", "Unvalidated input", "Broken auth"
- **Tester**: "Testing implementation details", "Flaky tests", "No edge cases"

Think of Red Flags as "smell tests" - quick checks that help the agent notice problems without needing detailed rules for every situation.

---

## How It Works

### The Frontmatter Schema

```yaml
---
name: agent-name          # Must match filename (minus .md)
description: One-line summary for agent selection
tools: ["Read", "Write"]  # Auto-granted tools
model: opus               # Model preference hint
---
```

### Field Reference

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Agent identifier, matches filename |
| `description` | Yes | Concise summary (<100 chars) |
| `tools` | Yes | Auto-granted tools when invoked |
| `model` | No | Preferred model (opus/sonnet/haiku) |

### Benefits in Practice

**1. Context Optimization**

When Claude loads agents, it can now:
- Read just the frontmatter to understand what's available
- Load full content only for the selected agent
- Reduce token overhead in multi-agent scenarios

**2. Auto Tool Grants**

Before:
```javascript
Task({
  prompt: "Design the localStorage schema...",
  subagent_type: "architect",
  allowed_tools: ["Write", "Edit", "Read", "Grep", "Glob"]  // Easy to forget!
})
```

After:
```javascript
Task({
  prompt: "Design the localStorage schema...",
  subagent_type: "architect"
  // tools: ["Read", "Grep", "Glob", "Write"] auto-granted from frontmatter
})
```

**3. Agent Selection**

The `description` field enables quick identification:
```
architect: System design, TDDs, architecture decisions, pattern consistency
code-reviewer: Code quality, security, patterns, PR review with detailed feedback
security-reviewer: Security audit, OWASP, authentication, data protection
```

### Validation Scripts

We created two utility scripts to maintain quality:

**`scripts/validate-frontmatter.sh`** - Checks all agent files:
```bash
$ ./scripts/validate-frontmatter.sh

Frontmatter Validation Report - Sun Jan 25 2026
========================================

✅ architect.md - Valid frontmatter
   name: architect
   tools: ["Read", "Grep", "Glob", "Write"]

✅ code-reviewer.md - Valid frontmatter
   name: code-reviewer
   tools: ["Read", "Grep", "Glob", "Bash"]
...

========================================
Summary:
  ✅ Valid:   11
  ⚠️  Invalid: 0
  ❌ Missing: 0
```

**`scripts/count-agent-tokens.sh`** - Monitors context budget:
```bash
$ ./scripts/count-agent-tokens.sh

Agent Token Count Report - Sun Jan 25 2026
================================

architect.md                        10594 chars  ~2648 tokens
code-reviewer.md                     9200 chars  ~2300 tokens
...

================================
TOTAL (agents only)                 67632 chars  ~16908 tokens
```

---

## What I Learned

### 1. Research Before Inventing

The impulse is often to design something new. But frontmatter is a 15-year-old pattern from Jekyll (2008). It's battle-tested, widely understood, and has tooling support.

**Meta-lesson**: Before solving a problem, check if someone already solved it well.

### 2. Co-location Beats Separation

Keeping metadata IN the agent file (rather than separate registry) means:
- One file to edit when making changes
- Version control tracks everything together
- No sync issues between files

**Meta-lesson**: When things change together, store them together.

### 3. Progressive Enhancement

We added frontmatter to ALL 11 agents, but only added Red Flags to 4 priority agents. Why?

- Frontmatter is low-effort, high-value (quick to add, immediate benefits)
- Red Flags require domain expertise (need to think through anti-patterns)
- Better to have 4 excellent Red Flags sections than 11 mediocre ones

**Meta-lesson**: Don't let perfect be the enemy of good. Ship value incrementally.

### 4. Validation Scripts as Documentation

The validation script isn't just a quality check - it's **executable documentation**. Reading it tells you:
- What fields are required (name, description, tools)
- Which files are considered agents (not AGENTS.md, README.md, DOC_MAINTENANCE.md)
- What valid frontmatter looks like

**Meta-lesson**: Code that validates is also code that documents.

### 5. Token Budgets Matter

Adding ~30 tokens of frontmatter per agent seems trivial. But with 11 agents, that's 330 tokens. If all agents are loaded, that's context we're spending.

The frontmatter enables SELECTIVE loading - read metadata first, load full content only when needed. This is actually a token SAVINGS over naive "load everything" approaches.

**Meta-lesson**: Small optimizations compound across scale.

---

## Gotchas & Pitfalls

### 1. YAML Syntax is Unforgiving

```yaml
# ❌ Will break
tools: [Read, Write]  # Missing quotes

# ✅ Correct
tools: ["Read", "Write"]  # Quoted strings
```

The validation script catches this, but it's easy to mess up manually.

### 2. Name Must Match Filename

If `architect.md` has `name: tech-architect`, something's wrong. The validation script could be extended to check this, but currently it's a manual responsibility.

### 3. Don't Over-Engineer Frontmatter

It's tempting to add more fields:
```yaml
---
name: architect
description: ...
tools: [...]
model: opus
version: 1.0.0        # Is this useful?
author: Claude        # Who cares?
last_updated: 2026-01-25  # git already tracks this
---
```

Only add fields that serve a purpose. Metadata is code - it has maintenance cost.

### 4. Red Flags Aren't Exhaustive

The Red Flags sections are conversation starters, not complete anti-pattern catalogs. They help the agent notice obvious problems, but domain expertise still matters.

---

## The Bigger Picture

This work is part of a larger pattern: **treating agent definitions as first-class artifacts**.

Agent files aren't just prompts - they're:
- **Configuration** (what tools to use)
- **Documentation** (what the agent does)
- **Workflow** (when to invoke, what to produce)
- **Quality gates** (red flags to watch for)

The frontmatter pattern makes this explicit. An agent file is now structured data with human-readable content, not just prose.

This sets us up for future enhancements:
- Automatic agent selection based on task type
- Context budget management (load only what fits)
- Agent composition (combining capabilities)
- Testing agent behaviors (given input, expect output)

---

## Files Changed

| File | Change |
|------|--------|
| `.claude/agents/*.md` (11 files) | Added YAML frontmatter |
| `.claude/agents/architect.md` | Added Red Flags, Code Examples |
| `.claude/agents/code-reviewer.md` | Added Red Flags, Code Examples |
| `.claude/agents/security-reviewer.md` | Added Red Flags |
| `.claude/agents/tester.md` | Added Red Flags |
| `.claude/agents/AGENTS.md` | Documented frontmatter schema |
| `scripts/validate-frontmatter.sh` | New validation script |
| `scripts/count-agent-tokens.sh` | New token counting script |
| `CLAUDE.md` | Updated agent orchestration section |

---

## Related Documentation

- **[AGENTS.md](/.claude/agents/AGENTS.md)** - Full agent orchestration guide with frontmatter reference
- **[agent-orchestration-comparison.md](./agent-orchestration-comparison.md)** - When to use agents vs. manual approach
- **[LEARNINGS.md](/docs/reference/LEARNINGS.md)** - Technical patterns and decision frameworks

---

*Document created: 2026-01-25*
*Author: Sage (Claude)*
