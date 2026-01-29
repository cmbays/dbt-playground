# Repository Research Report

> **Repo**: [everything-claude-code](https://github.com/affaan-m/everything-claude-code)
> **Researched**: 2026-01-25
> **Researcher**: Sage persona
> **Focus**: Agent definition patterns, context window optimization, skill structure, design patterns
> **Depth**: Deep

---

## Executive Summary

This repository is a **battle-tested, production-grade Claude Code configuration collection** from an Anthropic hackathon winner with 28.6k stars and 3.4k forks. It provides agents, skills, hooks, commands, rules, and MCP configurations optimized for real-world AI-assisted development.

**Top 3 Takeaways**:
1. **YAML frontmatter in agent definitions** enables machine-parseable metadata for context window optimization
2. **Agents are more operationally actionable** with concrete code examples, anti-patterns ("Red Flags"), and project-specific templates
3. **Skills are modular and hook-triggered** rather than embedded in agents, enabling on-demand loading

**Recommendation**: Adopt YAML frontmatter format for agents, add Red Flags sections, and implement strategic context management.

---

## 1. Repository Overview

### Purpose
Complete Claude Code plugin collection for AI-assisted development. Provides production-ready configurations for agents, skills, hooks, commands, rules, and MCP integrations.

### Technology Stack
| Layer | Technology |
|-------|------------|
| Language | JavaScript (primary), TypeScript |
| Framework | Claude Code CLI |
| Build Tool | N/A (configuration files) |
| Testing | N/A |
| Other | MCP servers, hooks, scripts |

### Project Maturity
- **Stars/Forks**: 28,643 / 3,433
- **Last Updated**: 2026-01-26 (actively maintained)
- **Contributors**: Multiple
- **Maintenance Status**: **Very Active**

### Documentation Quality
- [x] README comprehensive
- [x] Examples provided
- [ ] API documentation (N/A - config files)
- [x] Contributing guidelines
- [x] Two comprehensive guides (shorthand + longform)

**Notes**: Excellent practical documentation with real-world examples from hackathon-winning project.

---

## 2. Project Structure

### Directory Layout
```
everything-claude-code/
├── agents/               # Specialized subagent definitions
│   ├── architect.md
│   ├── planner.md
│   ├── code-reviewer.md
│   ├── security-reviewer.md
│   ├── tdd-guide.md
│   ├── doc-updater.md
│   ├── e2e-runner.md
│   ├── refactor-cleaner.md
│   ├── build-error-resolver.md
│   └── database-reviewer.md
├── skills/               # Workflow definitions (nested directories)
│   ├── tdd-workflow/SKILL.md
│   ├── security-review/SKILL.md
│   ├── continuous-learning/SKILL.md
│   ├── strategic-compact/SKILL.md
│   ├── coding-standards/
│   ├── backend-patterns/
│   ├── frontend-patterns/
│   └── ...
├── commands/             # Slash commands
├── rules/                # Always-enforce guidelines
├── hooks/                # Trigger-based automations
├── scripts/              # Utility scripts
├── mcp-configs/          # MCP server configurations
├── contexts/             # Context configurations
├── tests/                # Test files
└── examples/             # Usage examples
```

### Organization Patterns
- **Agents are flat files** - One `.md` file per agent
- **Skills are directories** - `skill-name/SKILL.md` pattern allows auxiliary files
- **YAML frontmatter everywhere** - Machine-parseable metadata at file start

### Key Observations
- Skills use directory structure for extensibility (can add helper scripts)
- All agents have explicit tool grants in frontmatter
- Model selection (`opus`) declared per agent

### Applicability to Our Project
| Their Pattern | Our Equivalent | Adoption Potential |
|---------------|----------------|-------------------|
| YAML frontmatter | None currently | **High** - Critical for context optimization |
| Flat agent files | Same | Already aligned |
| Skill directories | Flat skill files | **Medium** - Consider for complex skills |
| Explicit tools array | Documented in prose | **High** - Move to frontmatter |

---

## 3. Architecture Patterns

### Pattern 1: YAML Frontmatter for Agents
**What it is**: Structured metadata at file start enabling machine parsing

```yaml
---
name: architect
description: Software architecture specialist for system design...
tools: ["Read", "Grep", "Glob"]
model: opus
---
```

**Where used**: All agent files
**Why it works**:
- Claude Code can extract metadata without loading full content
- Tools are granted automatically when agent invoked
- Model selection happens at agent level, not prompt level
- Description serves as summary for agent selection

**Our applicability**: **Critical** - This is the key optimization we're missing. Claude Code can use frontmatter to:
1. List available agents with descriptions
2. Grant tools without parsing prose
3. Select appropriate model
4. Minimize tokens loaded for agent selection

### Pattern 2: Red Flags / Anti-Patterns Section
**What it is**: Explicit documentation of what NOT to do

```markdown
## Red Flags

Watch for these architectural anti-patterns:
- **Big Ball of Mud**: No clear structure
- **Golden Hammer**: Using same solution for everything
- **Premature Optimization**: Optimizing too early
- **Not Invented Here**: Rejecting existing solutions
- **Analysis Paralysis**: Over-planning, under-building
```

**Where used**: architect.md, code-reviewer.md, tdd-guide.md
**Why it works**: Prevents common mistakes without needing to learn the hard way
**Our applicability**: **High** - Our agents lack explicit anti-pattern guidance

### Pattern 3: Actionable Code Examples
**What it is**: Real code snippets showing correct vs incorrect patterns

```javascript
// ❌ CRITICAL: Hardcoded secrets
const apiKey = "sk-proj-xxxxx"

// ✅ CORRECT: Environment variables
const apiKey = process.env.OPENAI_API_KEY
```

**Where used**: Throughout all agents and skills
**Why it works**: Concrete examples are faster to apply than abstract descriptions
**Our applicability**: **High** - Our agents are more abstract, less actionable

### Pattern 4: Project-Specific Templating
**What it is**: Generic patterns adapted with project-specific examples

```markdown
## Project-Specific Architecture (Example)

### Current Architecture
- **Frontend**: Next.js 15 (Vercel/Cloud Run)
- **Backend**: FastAPI or Express (Cloud Run/Railway)
- **Database**: PostgreSQL (Supabase)
```

**Where used**: architect.md, security-reviewer.md
**Why it works**: Shows how to apply abstract patterns to real projects
**Our applicability**: **High** - We should add Japanese learning site examples

### Pattern 5: Strategic Context Compaction
**What it is**: Manual `/compact` at logical boundaries instead of auto-compaction

```markdown
Strategic compaction at logical boundaries:
- **After exploration, before execution**
- **After completing a milestone**
- **Before major context shifts**
```

**Where used**: `skills/strategic-compact/SKILL.md`
**Why it works**: Preserves important context through task phases
**Our applicability**: **Medium** - Useful for long sessions

### Data Flow
Agents are invoked → YAML frontmatter parsed → Tools granted → Full content loaded → Agent executes → Results returned

### State Management
- No persistent state between invocations
- Skills can use hooks for session tracking
- continuous-learning skill extracts patterns at session end

---

## 4. Feature Analysis

### Feature Inventory

| Feature | Maturity | Quality | Relevance to Us |
|---------|----------|---------|-----------------|
| YAML frontmatter | Complete | High | **Critical** |
| Agent tool grants | Complete | High | **High** |
| Red Flags sections | Complete | High | **High** |
| Code examples | Complete | High | **High** |
| Strategic compact | Complete | Medium | **Medium** |
| Continuous learning | Complete | High | **High** (similar to our Sage) |
| Hook integrations | Complete | High | **Low** (we have hooks) |
| MCP configs | Complete | High | **Low** (different stack) |

### Feature Deep-Dives

#### YAML Frontmatter (Critical Relevance)
**What it does**: Provides machine-parseable metadata for agent selection and configuration

**Implementation approach**:
```yaml
---
name: architect
description: One-line summary for agent selection
tools: ["Read", "Grep", "Glob"]  # Auto-granted when invoked
model: opus                       # Model selection
---

# Full agent content below...
```

**Key files**:
- `agents/architect.md` - Example with all fields
- `agents/code-reviewer.md` - Shows tools array with Bash

**What we can learn**:
- Frontmatter is parsed before content is loaded
- `tools` array eliminates need for `allowed_tools` in Task calls
- `description` enables agent discovery without full content load

**Potential adaptation**:
Add frontmatter to all our agent files:
```yaml
---
name: documenter
description: Documentation specialist maintaining CLAUDE.md, changelog, and living docs
tools: ["Read", "Write", "Edit", "Grep", "Glob"]
model: opus
---
```

#### Code Reviewer Agent (High Relevance)
**What it does**: Reviews code with structured issue categorization

**Implementation approach**:
- Uses git diff to see changes
- Categorizes issues: CRITICAL, HIGH, MEDIUM, LOW
- Provides fix examples for each issue

**Key patterns**:
```markdown
## Review Output Format

For each issue:
```
[CRITICAL] Hardcoded API key
File: src/api/client.ts:42
Issue: API key exposed in source code
Fix: Move to environment variable

const apiKey = "sk-abc123";  // ❌ Bad
const apiKey = process.env.API_KEY;  // ✓ Good
```
```

**What we can learn**:
- Structured issue format with file:line references
- Concrete fix examples, not just descriptions
- Approval criteria clearly defined

---

## 5. Integration Opportunities

### High Priority (Quick Wins)

#### Opportunity 1: Add YAML Frontmatter to All Agents
- **What**: Add `---` frontmatter with name, description, tools, model
- **Value**: ~30% context window savings on agent selection; cleaner tool grants
- **Effort**: Low (template change, apply to 13 agents)
- **Approach**: Direct adoption
- **Risk**: None - additive change

#### Opportunity 2: Add Red Flags Sections
- **What**: Add "Red Flags" / "Anti-Patterns" to architect, code-reviewer, tester
- **Value**: Prevent common mistakes proactively
- **Effort**: Low (add ~20 lines per agent)
- **Approach**: Adapt their patterns to our project context
- **Risk**: None

#### Opportunity 3: Add Concrete Code Examples
- **What**: Add ❌/✅ code comparisons throughout agents
- **Value**: Faster application of guidance
- **Effort**: Medium (requires domain-specific examples)
- **Approach**: Inspiration - create Japanese learning site examples
- **Risk**: Low

### Medium Priority (Planned Features)

#### Opportunity 4: Structured Issue Format for Reviews
- **What**: Standardize review output with [SEVERITY] file:line format
- **Value**: Consistent, actionable review feedback
- **Effort**: Medium
- **Approach**: Adapt their format

#### Opportunity 5: Project-Specific Examples in Agents
- **What**: Add Japanese learning site architecture examples to architect
- **Value**: Shows how abstract patterns apply to our project
- **Effort**: Medium
- **Approach**: Create from scratch using their pattern

#### Opportunity 6: Strategic Compact Awareness
- **What**: Add guidance about when to manually compact
- **Value**: Preserve context during long sessions
- **Effort**: Low
- **Approach**: Document in AGENTS.md or create skill

### Low Priority (Future Consideration)

#### Opportunity 7: Skill Directory Structure
- **What**: Convert skills to `skill-name/SKILL.md` directories
- **Value**: Allows auxiliary scripts/configs per skill
- **Effort**: Medium
- **Approach**: Migration when skills grow complex
- **Risk**: Disrupts current structure

### Not Recommended
| Idea | Why Not |
|------|---------|
| Copy their MCP configs | Different tech stack (we use vanilla JS) |
| Copy database-reviewer | We don't have a database |
| Copy build-error-resolver | We don't have a build system |

---

## 6. Technology Assessment

### Dependencies Worth Noting

| Dependency | Purpose | Our Interest |
|------------|---------|--------------|
| ts-morph | AST analysis for doc generation | Skip (TypeScript-specific) |
| madge | Dependency graph visualization | Evaluate for future |
| DOMPurify | XSS prevention | Already recommended in our security rules |
| Playwright | E2E testing | Evaluate for future |

### Build & Tooling
N/A - Configuration files only, no build process

### Testing Approach
Mentions Jest/Vitest for unit tests, Playwright for E2E. We don't have automated tests yet.

### Performance Considerations
- YAML frontmatter designed for minimal token load
- Skills loaded on-demand via hooks
- Strategic compact for long sessions

### Security Considerations
Their security-reviewer is comprehensive:
- OWASP Top 10 coverage
- Hardcoded secrets detection
- Race condition awareness
- Rate limiting guidance

---

## 7. Risks & Concerns

### Technical Risks
- **Frontmatter compatibility**: Need to verify Claude Code parses our frontmatter
  - *Mitigation*: Test with one agent first before mass migration

### Compatibility Concerns
- Their agents assume TypeScript/Next.js stack
- Some patterns (database queries, API routes) don't apply to our static site

### Maintenance Concerns
- More detailed agents = more to keep updated
- Red Flags sections need project-specific examples

### Licensing
- **License**: MIT
- **Implications**: Free to use, modify, and adapt patterns

---

## 8. Recommendations

### For Product Manager (pm:)

**Feature Opportunities**:
1. **Agent Enhancement Project** - Improve all 13 agents with new patterns
   - Effort estimate: Low (1-2 sessions)
   - Suggested priority: P1

2. **Strategic Context Management** - Add compact guidance for long sessions
   - Effort estimate: Low
   - Suggested priority: P2

**User Stories to Consider**:
- As a developer, I want agents with concrete examples so I can apply guidance faster
- As a maintainer, I want frontmatter metadata so Claude Code loads agents efficiently

**Questions for PM**:
- Should we prioritize all agents equally, or focus on most-used (architect, code-reviewer)?
- Do we want to track token usage before/after to measure optimization?

---

### For Technical Architect (arch:)

**Architecture Recommendations**:
1. **YAML Frontmatter Migration** - Add to all agent files
   - Complexity: Low
   - Files affected: 13 agents

2. **Agent Content Enhancement** - Add Red Flags, code examples, project-specific patterns
   - Complexity: Medium
   - Files affected: architect.md, code-reviewer.md, documenter.md, tester.md

**TDD Candidates**:
- [ ] Agent Frontmatter Migration - Ready for implementation (no TDD needed)
- [ ] Agent Content Enhancement - Create enhancement spec

**Technical Questions**:
- Should `model` field default to `opus` or be explicitly set per agent?
- Should tools be exhaustive or minimal per agent?

---

## 9. Action Items

### Immediate (This Session)
- [x] Generate research report
- [ ] Review with Christopher for approval

### Short-term (Next Sprint)
- [ ] Add YAML frontmatter to all 13 agents
- [ ] Add Red Flags section to architect.md
- [ ] Add Red Flags section to code-reviewer.md
- [ ] Add concrete code examples to security-reviewer.md

### Long-term (Backlog)
- [ ] Add project-specific examples to architect (Japanese learning site)
- [ ] Evaluate strategic compact skill
- [ ] Consider skill directory structure for complex skills

---

## 10. Appendix

### Key File References
| File | Purpose | Notable Code |
|------|---------|--------------|
| `agents/architect.md` | Architecture specialist | Lines 1-5: YAML frontmatter example |
| `agents/code-reviewer.md` | Code review | Lines 20-40: Issue categorization |
| `agents/security-reviewer.md` | Security audit | Lines 100-200: Vulnerability patterns |
| `skills/strategic-compact/SKILL.md` | Context management | Lines 1-30: When to compact |

### Code Snippets

#### YAML Frontmatter Template
```yaml
---
name: agent-name
description: One-line description for agent selection and context optimization
tools: ["Read", "Write", "Edit", "Grep", "Glob"]
model: opus
---

# Agent Name

You are a [role] specializing in [specialty].

## Your Role
...
```

#### Red Flags Section Template
```markdown
## Red Flags

Watch for these anti-patterns:
- **[Anti-pattern Name]**: Brief description
- **[Anti-pattern Name]**: Brief description
```

#### Code Example Template
```markdown
### Issue: [Issue Name]

```javascript
// ❌ BAD: Description of problem
badCode();

// ✅ GOOD: Description of solution
goodCode();
```
```

### External Resources
- [everything-claude-code README](https://github.com/affaan-m/everything-claude-code)
- [Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) - Token optimization section

---

## Handoff

### Status
- [x] Research complete
- [ ] PM review pending
- [ ] Architect review pending
- [ ] Action items assigned

### Next Persona
**Primary**: `arch:` for frontmatter migration implementation
**Secondary**: `pm:` for prioritization of enhancement work

### Handoff Notes
The YAML frontmatter pattern is the highest-impact, lowest-effort improvement. Recommend implementing immediately as it's purely additive and can be done incrementally (one agent at a time).

---

## Comparison Matrix: Their Agents vs. Ours

| Aspect | everything-claude-code | Our Agents | Verdict |
|--------|----------------------|------------|---------|
| **Frontmatter** | YAML with name/desc/tools/model | None | **Adopt theirs** |
| **Length** | 200-400 lines | 100-170 lines | Theirs more comprehensive |
| **Code Examples** | Many, concrete | Few, abstract | **Adopt theirs** |
| **Anti-patterns** | Red Flags sections | None | **Adopt theirs** |
| **Workflow Integration** | Minimal | Detailed handoffs | **Keep ours** |
| **Persona Relationships** | Not documented | Clear (Sage vs Doc) | **Keep ours** |
| **Project Examples** | SaaS platform | None | **Add ours** |
| **Quality Checklists** | Included | Comprehensive | Similar quality |
| **Domain Expertise** | Generic dev | Japanese learning | **Keep ours** |

### Summary Recommendation

**Adopt from them**:
1. YAML frontmatter (critical)
2. Red Flags sections (high value)
3. Concrete code examples (high value)
4. Project-specific examples pattern (medium value)

**Keep our strengths**:
1. Workflow integration with handoffs
2. Persona relationship clarity (Sage vs Documenter)
3. Domain-specific agents (Sensei)
4. Quality checklists with project context

---

*Report generated by Sage persona using repo-research skill*
*Template version: 1.0*
