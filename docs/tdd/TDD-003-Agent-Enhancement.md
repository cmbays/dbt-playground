# TDD-003: Agent Enhancement

**Status**: Draft
**Author**: Technical Architect
**Created**: 2026-01-25
**PRD**: [PRD-007-Team-Optimizations](../specs/PRD-007-Team-Optimizations.md)
**Research**: [everything-claude-code analysis](../plans/REPO-RESEARCH-everything-claude-code-2026-01-25.md)

---

## Overview

This TDD defines the technical approach for enhancing all agent files with YAML frontmatter, Red Flags sections, and concrete code examples. The goal is to optimize context window usage and improve agent effectiveness.

## Technical Approach

### Selected Approach: Incremental Enhancement

**Rationale**:
- Low risk: Changes are additive, not destructive
- Testable: Each agent can be validated independently
- Reversible: Frontmatter can be removed if issues arise

**Alternatives Considered**:

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Big bang (all at once) | Fast | High risk, hard to debug | Rejected |
| Incremental (one at a time) | Safe, testable | Slower | **Selected** |
| Generator script | Automated | Over-engineered for 13 files | Rejected |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT FILE STRUCTURE                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐                    │
│  │         YAML FRONTMATTER            │  ← NEW (Phase 1)   │
│  │  ---                                │                    │
│  │  name: agent-name                   │                    │
│  │  description: one-line summary      │                    │
│  │  tools: ["Read", "Write", ...]      │                    │
│  │  model: opus                        │                    │
│  │  ---                                │                    │
│  └─────────────────────────────────────┘                    │
│                                                              │
│  ┌─────────────────────────────────────┐                    │
│  │         EXISTING CONTENT            │  ← PRESERVED       │
│  │  # Role Summary                     │                    │
│  │  ## Core Responsibilities           │                    │
│  │  ## Skill Integration               │                    │
│  │  ## Workflow Integration            │                    │
│  │  ## Constraints                     │                    │
│  │  ## Quality Checklist               │                    │
│  └─────────────────────────────────────┘                    │
│                                                              │
│  ┌─────────────────────────────────────┐                    │
│  │         RED FLAGS SECTION           │  ← NEW (Phase 2)   │
│  │  ## Red Flags                       │                    │
│  │  - Anti-pattern 1                   │                    │
│  │  - Anti-pattern 2                   │                    │
│  └─────────────────────────────────────┘                    │
│                                                              │
│  ┌─────────────────────────────────────┐                    │
│  │         CODE EXAMPLES               │  ← NEW (Phase 2)   │
│  │  ## Common Patterns                 │                    │
│  │  ### Pattern Name                   │                    │
│  │  ❌ Bad example                     │                    │
│  │  ✅ Good example                    │                    │
│  └─────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### Component 1: YAML Frontmatter

**Purpose**: Machine-parseable metadata for agent selection and tool grants

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Agent identifier (kebab-case) |
| `description` | string | Yes | One-line summary for selection UI |
| `tools` | array | Yes | Tools auto-granted when invoked |
| `model` | string | No | Model preference (opus/sonnet/haiku) |

**Constraints**:
- Must be valid YAML
- Must be at file start (before any markdown)
- Description should be < 100 characters

### Component 2: Red Flags Section

**Purpose**: Prevent common mistakes through anti-pattern documentation

**Structure**:
```markdown
## Red Flags

Watch for these anti-patterns:

- **[Pattern Name]**: Brief description of what to avoid and why
- **[Pattern Name]**: Brief description of what to avoid and why
```

**Constraints**:
- 5-15 items per agent (enough to be useful, not overwhelming)
- Each item should be actionable (what to do instead)
- Ordered by severity/frequency

### Component 3: Code Examples

**Purpose**: Concrete guidance through ❌/✅ comparisons

**Structure**:
```markdown
## Common Patterns

### [Pattern Name]

```javascript
// ❌ BAD: Description of problem
badCode();

// ✅ GOOD: Description of solution
goodCode();
```
```

**Constraints**:
- Examples must be project-relevant (Japanese learning site context)
- Include both problem and solution
- Keep examples concise (< 10 lines each)

---

## Data Structures

### Frontmatter Schema

```yaml
---
# Required fields
name: string          # kebab-case identifier
description: string   # one-line summary (< 100 chars)
tools: string[]       # tool names from Claude Code toolset

# Optional fields
model: string         # "opus" | "sonnet" | "haiku" (default: opus)
---
```

### Tool Names Reference

Available tools for `tools` array:
```javascript
const AVAILABLE_TOOLS = [
  "Read",       // Read files
  "Write",      // Write new files
  "Edit",       // Edit existing files
  "Grep",       // Search file contents
  "Glob",       // Find files by pattern
  "Bash",       // Execute commands
  "WebFetch",   // Fetch web content
  "WebSearch",  // Search web
  "Task",       // Spawn subagents
];
```

### Agent Tool Recommendations

| Agent | Recommended Tools |
|-------|-------------------|
| architect | Read, Grep, Glob, Write |
| code-reviewer | Read, Grep, Glob, Bash |
| security-reviewer | Read, Write, Edit, Bash, Grep, Glob |
| documenter | Read, Write, Edit, Grep, Glob |
| developer | Read, Write, Edit, Bash, Grep, Glob |
| tester | Read, Bash, Grep, Glob |
| product-manager | Read, Write, Grep, Glob |
| design-reviewer | Read, Grep, Glob |
| sensei | Read, Write, Grep, Glob |
| sage | Read, Write, Grep, Glob |
| git-master | Read, Bash, Grep, Glob |

---

## File Changes

| File | Change Type | Description | Priority |
|------|-------------|-------------|----------|
| `.claude/agents/architect.md` | Modify | Add frontmatter, Red Flags, examples | P1 (pilot) |
| `.claude/agents/code-reviewer.md` | Modify | Add frontmatter, Red Flags, examples | P1 |
| `.claude/agents/security-reviewer.md` | Modify | Add frontmatter, Red Flags | P1 |
| `.claude/agents/documenter.md` | Modify | Add frontmatter | P2 |
| `.claude/agents/developer.md` | Modify | Add frontmatter | P2 |
| `.claude/agents/tester.md` | Modify | Add frontmatter, Red Flags | P2 |
| `.claude/agents/product-manager.md` | Modify | Add frontmatter | P3 |
| `.claude/agents/design-reviewer.md` | Modify | Add frontmatter | P3 |
| `.claude/agents/sensei.md` | Modify | Add frontmatter | P3 |
| `.claude/agents/sage.md` | Modify | Add frontmatter | P3 |
| `.claude/agents/git-master.md` | Modify | Add frontmatter | P3 |
| `.claude/agents/AGENTS.md` | Modify | Document frontmatter pattern | P2 |
| `CLAUDE.md` | Modify | Add agent frontmatter section | P2 |

---

## Implementation Sequence

### Phase 1: Pilot (architect.md)

**Goal**: Validate frontmatter works correctly before mass migration

```
Step 1.1: Add frontmatter to architect.md
Step 1.2: Verify parsing (test Task call without allowed_tools)
Step 1.3: Add Red Flags section (10 architecture anti-patterns)
Step 1.4: Add 5 code examples (design patterns)
Step 1.5: Test agent invocation end-to-end
```

**Validation Criteria**:
- [ ] Frontmatter is valid YAML
- [ ] Agent can be invoked without explicit tool grants
- [ ] Description appears in agent selection
- [ ] No regression in agent behavior

### Phase 2: Frontmatter Migration (remaining agents)

**Goal**: Add frontmatter to all remaining agents

```
Step 2.1: code-reviewer.md (with Red Flags, examples)
Step 2.2: security-reviewer.md (with Red Flags)
Step 2.3: documenter.md
Step 2.4: developer.md
Step 2.5: tester.md (with Red Flags)
Step 2.6: product-manager.md
Step 2.7: design-reviewer.md
Step 2.8: sensei.md
Step 2.9: sage.md
Step 2.10: git-master.md
```

### Phase 3: Documentation

**Goal**: Update documentation to reflect new patterns

```
Step 3.1: Update AGENTS.md with frontmatter documentation
Step 3.2: Update CLAUDE.md agent section
Step 3.3: Create agent authoring guide (optional)
```

---

## Detailed Specifications

### Architect Red Flags

```markdown
## Red Flags

Watch for these architecture anti-patterns:

- **Big Ball of Mud**: No clear structure or module boundaries. Everything depends on everything.
- **Golden Hammer**: Using the same solution for every problem regardless of fit.
- **Premature Optimization**: Optimizing before measuring. Build first, optimize measured bottlenecks.
- **Not Invented Here**: Rejecting existing solutions without evaluation. Use proven patterns.
- **Analysis Paralysis**: Over-planning without building. Ship incrementally.
- **Magic Numbers**: Hardcoded values without explanation. Use named constants.
- **God Object**: One module/function doing everything. Split responsibilities.
- **Tight Coupling**: Components too dependent on each other. Use clear interfaces.
- **Leaky Abstractions**: Implementation details bleeding through interfaces.
- **Over-Engineering**: Building for hypothetical futures. Solve today's problem.
```

### Code Reviewer Red Flags

```markdown
## Red Flags

Watch for these code quality anti-patterns:

- **Swallowed Exceptions**: Catch blocks that do nothing. At minimum, log errors.
- **Magic Strings**: String literals repeated without constants.
- **Deep Nesting**: More than 3-4 levels of nesting. Refactor to functions.
- **Long Functions**: Functions > 50 lines. Break into focused units.
- **Commented Out Code**: Dead code left in. Delete it, git remembers.
- **console.log Debugging**: Debug statements left in production code.
- **Global State**: Mutable globals. Use closures or modules.
- **innerHTML with User Input**: XSS vulnerability. Use textContent.
- **Missing Error Handling**: Assume operations can fail. Add try-catch.
- **Copy-Paste Code**: Duplicated logic. Extract to shared function.
```

### Security Reviewer Red Flags

```markdown
## Red Flags

Watch for these security anti-patterns:

- **Hardcoded Secrets**: API keys, passwords in source. Use environment variables.
- **innerHTML with Untrusted Data**: XSS vulnerability. Sanitize or use textContent.
- **eval() Usage**: Code injection risk. Never eval user input.
- **Missing Input Validation**: Trust no input. Validate at boundaries.
- **Storing Sensitive Data in localStorage**: Can be accessed by XSS. Minimize storage.
- **HTTP for Sensitive Operations**: Use HTTPS only for auth/data.
- **Missing CORS Configuration**: Cross-origin issues. Configure explicitly.
- **SQL/NoSQL Injection**: String concatenation in queries. Use parameterized queries.
- **Missing Rate Limiting**: DoS vulnerability on public endpoints.
- **Outdated Dependencies**: Known CVEs. Keep dependencies updated.
```

### Architect Code Examples

```markdown
## Common Patterns

### Module Export Pattern

```javascript
// ❌ BAD: const doesn't create window property
const KanjiModule = { ... };
// Other scripts can't access KanjiModule

// ✅ GOOD: Explicit window assignment for browser modules
const KanjiModule = { ... };
window.KanjiModule = KanjiModule;
```

### Default Value Pattern

```javascript
// ❌ BAD: || treats 0 as falsy
const count = userCount || 10;  // 0 becomes 10!

// ✅ GOOD: ?? only replaces null/undefined
const count = userCount ?? 10;  // 0 stays 0
```

### Data Structure Naming

```javascript
// ❌ BAD: Inconsistent naming across module boundary
// Module A returns: { due_count: 5, review_count: 3 }
// Module B expects: { dueCount: 5, reviewCount: 3 }

// ✅ GOOD: Consistent naming convention
// Document the convention: "All module interfaces use camelCase"
// API returns: { dueCount: 5, reviewCount: 3 }
```

### Initialization Error Handling

```javascript
// ❌ BAD: Silent failure, wrong data displayed
function init() {
  const data = loadData();
  renderUI(data);  // If loadData fails, undefined rendered
}

// ✅ GOOD: Explicit error handling
function init() {
  try {
    const data = loadData();
    if (!data) throw new Error('No data loaded');
    renderUI(data);
  } catch (error) {
    console.error('Init failed:', error);
    renderErrorState();
  }
}
```

### State Immutability

```javascript
// ❌ BAD: Mutating shared state
function updateProgress(state, newProgress) {
  state.progress = newProgress;  // Mutates original!
  return state;
}

// ✅ GOOD: Return new object
function updateProgress(state, newProgress) {
  return { ...state, progress: newProgress };
}
```
```

---

## Edge Cases

### Edge Case 1: Empty Tools Array
**Scenario**: Agent with no tool grants
**Handling**: Use empty array `tools: []` - agent runs read-only

### Edge Case 2: Invalid YAML
**Scenario**: Malformed frontmatter
**Handling**: Claude Code falls back to loading full content, logs warning

### Edge Case 3: Missing Frontmatter
**Scenario**: Agent file without frontmatter (migration incomplete)
**Handling**: Backward compatible - works as before, just no optimization

### Edge Case 4: Description Too Long
**Scenario**: Description > 100 characters
**Handling**: Truncate in UI, full description in file

---

## Testing Considerations

### Validation Tests (Manual)

1. **Frontmatter Parsing**
   - Create test agent with frontmatter
   - Invoke via Task tool without `allowed_tools`
   - Verify tools are granted automatically

2. **Agent Discovery**
   - List available agents
   - Verify description appears correctly
   - Check model selection works

3. **Regression Testing**
   - Invoke each enhanced agent
   - Verify existing functionality unchanged
   - Check handoff protocols still work

### Checklist Per Agent

- [ ] Frontmatter is valid YAML (use linter)
- [ ] `name` matches file name (without .md)
- [ ] `description` is concise and accurate
- [ ] `tools` array matches agent needs
- [ ] Existing content preserved
- [ ] No markdown rendering issues
- [ ] Agent invocable without errors

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Frontmatter not parsed | Low | High | Pilot with one agent first |
| YAML syntax errors | Medium | Low | Use YAML linter |
| Breaking existing agents | Low | High | Test each agent after change |
| Inconsistent enhancement | Medium | Medium | Use templates, review |

---

## Success Criteria

### Phase 1 Complete When:
- [ ] architect.md has valid frontmatter
- [ ] Frontmatter parsing verified working
- [ ] Red Flags section added (10 items)
- [ ] Code examples added (5 examples)
- [ ] No regression in architect functionality

### Phase 2 Complete When:
- [ ] All 11 agents have frontmatter
- [ ] Priority agents have Red Flags (architect, code-reviewer, security-reviewer, tester)
- [ ] Priority agents have examples (architect, code-reviewer)

### Phase 3 Complete When:
- [ ] AGENTS.md documents frontmatter pattern
- [ ] CLAUDE.md updated with agent section
- [ ] All changes committed and merged

---

## Appendix

### Frontmatter Template

```yaml
---
name: agent-name
description: One-line description for agent selection and context optimization
tools: ["Read", "Write", "Edit", "Grep", "Glob"]
model: opus
---

# Agent Name Persona

## Role Summary
...
```

### Red Flags Section Template

```markdown
## Red Flags

Watch for these anti-patterns:

- **[Pattern Name]**: Brief description of what to avoid. [What to do instead].
- **[Pattern Name]**: Brief description of what to avoid. [What to do instead].
- **[Pattern Name]**: Brief description of what to avoid. [What to do instead].
```

### Code Example Template

```markdown
## Common Patterns

### [Pattern Category]

```javascript
// ❌ BAD: Description of the problem
problematicCode();

// ✅ GOOD: Description of the solution
correctCode();
```

**Why**: Brief explanation of why the good pattern is better.
```

---

## Related Documents

- PRD: [PRD-007-Team-Optimizations](../specs/PRD-007-Team-Optimizations.md)
- Research: [everything-claude-code analysis](../plans/REPO-RESEARCH-everything-claude-code-2026-01-25.md)
- Agents: [.claude/agents/AGENTS.md](../../.claude/agents/AGENTS.md)
- GitHub Issues: #60, #61, #62, #63

---

*TDD created by Technical Architect persona*
*Version: 1.0*
