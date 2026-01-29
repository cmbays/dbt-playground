# PRD-007: Team Optimizations

**Status**: Draft
**Author**: PM Persona
**Created**: 2026-01-25
**Last Updated**: 2026-01-25

---

## Overview

This PRD establishes an ongoing initiative to optimize the Claude agent team through research, pattern adoption, and continuous improvement. The goal is to maximize agent effectiveness while minimizing context window usage.

## Problem Statement

Our current agent definitions:
1. Lack machine-parseable metadata (no YAML frontmatter)
2. Miss anti-pattern guidance ("Red Flags" sections)
3. Use abstract descriptions instead of concrete code examples
4. Don't leverage learnings from successful open-source configurations

**Impact**: Suboptimal context window usage, slower agent application, missed opportunities to prevent common mistakes.

## Goals

### Primary Goals
1. **Optimize context window usage** - Reduce token burn by 30%+ through frontmatter metadata
2. **Improve agent effectiveness** - Add actionable guidance with concrete examples
3. **Prevent common mistakes** - Add Red Flags/anti-pattern sections
4. **Establish research workflow** - Create repeatable process for learning from external repos

### Non-Goals
- Changing agent responsibilities or handoff protocols
- Adding new agents (separate initiative)
- Modifying skills or commands (future work)

## User Stories

### Agent Users (Developers)
- As a developer, I want agents with concrete code examples so I can apply guidance immediately
- As a developer, I want Red Flags sections so I avoid common mistakes proactively
- As a developer, I want agents that load efficiently so my context window isn't wasted

### System (Claude Code)
- As Claude Code, I want YAML frontmatter so I can parse agent metadata without loading full content
- As Claude Code, I want explicit tool grants so I don't need `allowed_tools` in Task calls
- As Claude Code, I want model specifications so I can select appropriate models per agent

## Solution Overview

### Phase 1: Agent Frontmatter Migration (P1)
Add YAML frontmatter to all 13 agents with:
- `name`: Agent identifier
- `description`: One-line summary for agent selection
- `tools`: Array of granted tools
- `model`: Model specification (opus/sonnet/haiku)

### Phase 2: Content Enhancement (P1)
Enhance priority agents with:
- Red Flags sections (anti-patterns to avoid)
- Concrete code examples (❌/✅ comparisons)
- Project-specific examples (Japanese learning site context)

### Phase 3: Research Framework (P2)
Establish ongoing research capability:
- `/repo-research` skill for external repo analysis
- Research report template and storage
- Pattern for pm:/arch: handoff from research findings

## Scope

### In Scope
| Item | Phase | Priority |
|------|-------|----------|
| YAML frontmatter for all 13 agents | 1 | P1 |
| Red Flags section for architect.md | 2 | P1 |
| Red Flags section for code-reviewer.md | 2 | P1 |
| Red Flags section for security-reviewer.md | 2 | P1 |
| Concrete examples for architect.md | 2 | P1 |
| Concrete examples for code-reviewer.md | 2 | P1 |
| /repo-research skill | 3 | P2 (Complete) |
| Research report template | 3 | P2 (Complete) |

### Out of Scope
- Skills enhancement (future PRD)
- New agent creation (future PRD)
- Hook modifications (future PRD)
- MCP configuration changes (different tech stack)

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Agent frontmatter coverage | 0% | 100% | Count of agents with frontmatter |
| Red Flags coverage | 0% | 50%+ | Priority agents with Red Flags |
| Code examples | ~5 | ~30 | Concrete ❌/✅ examples |
| Research reports | 0 | 1+ | Reports in docs/research/ |

## Technical Approach

### Frontmatter Format
```yaml
---
name: agent-name
description: One-line description for agent selection
tools: ["Read", "Write", "Edit", "Grep", "Glob"]
model: opus
---
```

### Red Flags Format
```markdown
## Red Flags

Watch for these anti-patterns:
- **[Pattern Name]**: Brief description of what to avoid
- **[Pattern Name]**: Brief description of what to avoid
```

### Code Example Format
```markdown
### [Issue Name]

```javascript
// ❌ BAD: Description of problem
badCode();

// ✅ GOOD: Description of solution
goodCode();
```
```

## Implementation Plan

### Milestone 1: Foundation (Sprint 1)
- [ ] T1: Add frontmatter to architect.md (pilot)
- [ ] T2: Verify frontmatter works correctly
- [ ] T3: Add frontmatter to remaining 12 agents
- [ ] T4: Update AGENTS.md with frontmatter documentation

### Milestone 2: Content Enhancement (Sprint 1-2)
- [ ] T5: Add Red Flags to architect.md
- [ ] T6: Add Red Flags to code-reviewer.md
- [ ] T7: Add Red Flags to security-reviewer.md
- [ ] T8: Add concrete examples to architect.md
- [ ] T9: Add concrete examples to code-reviewer.md

### Milestone 3: Documentation (Sprint 2)
- [ ] T10: Document frontmatter pattern in CLAUDE.md
- [ ] T11: Create agent enhancement guide
- [ ] T12: Update agent README with new patterns

## Dependencies

### Completed
- [x] `/repo-research` skill created
- [x] Research report template created
- [x] everything-claude-code research completed

### Required
- None (can proceed immediately)

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Frontmatter not parsed by Claude Code | Low | High | Test with pilot agent first |
| Too much content bloats agents | Medium | Medium | Keep Red Flags concise (~10 items) |
| Inconsistent enhancement quality | Medium | Low | Use templates, review each |

## Research Completed

### everything-claude-code Analysis (2026-01-25)
**Report**: `docs/plans/REPO-RESEARCH-everything-claude-code-2026-01-25.md`

**Key Findings**:
1. YAML frontmatter enables ~30% context savings
2. Red Flags sections prevent common mistakes
3. Concrete code examples improve application speed
4. Project-specific examples show pattern application

**Adoption Recommendations**:
- Critical: YAML frontmatter
- High: Red Flags sections
- High: Concrete code examples
- Medium: Project-specific examples

## Future Research Candidates

| Repository | Focus | Priority |
|------------|-------|----------|
| claude-engineer | Agent patterns | P2 |
| aider | Code modification patterns | P3 |
| cursor-rules | Rules patterns | P3 |

## Appendix

### Agents to Enhance

| Agent | Frontmatter | Red Flags | Examples | Priority |
|-------|-------------|-----------|----------|----------|
| architect.md | Todo | Todo | Todo | P1 |
| code-reviewer.md | Todo | Todo | Todo | P1 |
| security-reviewer.md | Todo | Todo | - | P1 |
| documenter.md | Todo | - | - | P2 |
| developer.md | Todo | - | - | P2 |
| tester.md | Todo | Todo | - | P2 |
| product-manager.md | Todo | - | - | P3 |
| design-reviewer.md | Todo | - | - | P3 |
| sensei.md | Todo | - | - | P3 |
| sage.md | Todo | - | - | P3 |
| git-master.md | Todo | - | - | P3 |
| AGENTS.md | - | - | - | P2 |
| README.md | - | - | - | P3 |

### Related Documents
- Research Report: `docs/plans/REPO-RESEARCH-everything-claude-code-2026-01-25.md`
- Agent Guide: `.claude/agents/AGENTS.md`
- Knowledge Management: `docs/reference/knowledge-management.md`

---

*PRD created by PM persona*
*Version: 1.0*
