# Agent Orchestration System

**Purpose**: Persona definitions and invocation methods for the agent orchestration system.

**Last Updated**: 2026-01-25

For detailed orchestration best practices, see [[AGENTS.md]].

---

## Overview

The agent system provides specialized personas for different aspects of development. Claude automatically detects context and adopts the appropriate persona, or you can explicitly invoke one using prefix commands.

## Available Personas

| Persona | Prefix | File | Primary Focus |
|---------|--------|------|---------------|
| Product Manager | `pm:` | `product-manager.md` | Requirements, PRDs, GitHub issues |
| Technical Architect | `arch:` | `architect.md` | System design, TDDs, architecture |
| Quality Tester | `test:` | `tester.md` | Test specs, verification |
| Feature Developer | `dev:` | `developer.md` | Implementation |
| Code Reviewer | `review:` | `code-reviewer.md` | Code quality, patterns |
| Design Reviewer | `design:` | `design-reviewer.md` | UI/UX, accessibility |
| Japanese Sensei | `sensei:` | `sensei.md` | Language accuracy, culture |
| Documenter | `docs:` | `documenter.md` | Documentation, changelog |
| Security Reviewer | `security:` | `security-reviewer.md` | Security audit, OWASP |
| Sage | `sage:` | `sage.md` | Learning curation, pattern extraction |
| Changelog Generator | `changelog:` | `changelog-generator.md` | Automated changelog, release notes |

## Assembly Line Workflow

For feature development, personas chain together:

```
1. PM         → Draft PRD in docs/specs/
2. Architect  → Create TDD in docs/tdd/
               (+ Sensei consultation for Japanese content)
3. Tester     → Write test specification
4. Developer  → Implement until tests pass
5. Reviewers  → Code + Design review (parallel)
6. Post-Completion (parallel):
   ├─→ Documenter → Update changelog and docs
   └─→ Sage       → Extract learnings and patterns
```

## Invocation Methods

### Automatic Detection
Claude analyzes context and adopts appropriate persona:
- PRD/requirements discussion → PM
- Technical design questions → Architect
- Implementation tasks → Developer
- Review requests → Code/Design Reviewer
- Japanese content → Sensei

### Explicit Prefix Commands
Use prefixes to explicitly invoke a persona:
```
pm: I want to add a vocabulary quiz feature
arch: design the architecture for spaced repetition
test: create test spec for flashcard flip
dev: implement the JLPT filter
review: check the new shopping page
design: audit the kanji cards for accessibility
sensei: verify this dialogue is natural
docs: update changelog for v0.3
sage: extract learnings from this session
```

## Handoff Protocol

Each persona ends work with:
1. **Summary** of completed work
2. **Open questions** or blockers
3. **Next persona** recommendation
4. **Artifact links** produced

## Artifact Locations

| Artifact Type | Location |
|---------------|----------|
| PRDs | `docs/specs/PRD-*.md` |
| TDDs | `docs/tdd/TDD-*.md` |
| Architecture diagrams | `docs/tdd/*.d2` |
| Test specifications | `temp/v*_TESTING.md` |
| Work-in-progress code | `temp/` |
| Changelog | `CHANGELOG.md` |
| Review artifacts | `docs/reviews/` |
| Technical patterns | `docs/reference/LEARNINGS.md` |
| Learned skills | `.claude/skills/learned-pattern-*.md` |
| Educational docs | `archive/FOR_CHRIS_docs/*.md` |
| Learning digests | `temp/LEARNING_DIGEST_*.md` |

## Skill Integration

Several personas leverage built-in skills:

| Skill | Persona(s) | Purpose |
|-------|------------|---------|
| `/code-review` | Code Reviewer | PR review |
| `/feature-dev` | Developer | Guided implementation |
| `/feature-dev:code-architect` | Architect | Architecture design |
| `/feature-dev:code-explorer` | Architect | Codebase analysis |
| `/feature-dev:code-reviewer` | Code Reviewer | Quality analysis |
| `/interface-design:audit` | Design Reviewer | Design system check |
| `/revise-claude-md` | Documenter | CLAUDE.md updates |
| `/claude-md-improver` | Documenter | CLAUDE.md audits |
| `changelog-generation` | Changelog Generator, Documenter | Automated changelog from git history |
| `code-simplifier` (plugin) | Architect, Developer, Code Reviewer, Refactor-Cleaner | Identify over-complexity, reduce token burn |

**Note**: For token optimization and code simplification strategies, see [[AGENTS.md#token-optimization--code-simplification]].

## Custom Commands

Project-specific commands in `.claude/commands/`:

| Command | Purpose |
|---------|---------|
| `/plan` | Structured implementation planning |
| `/review` | Code quality review workflow |
| `/orchestrate` | Multi-persona feature workflow |
| `/deploy` | Version deployment workflow |
| `/tdd` | Test-driven development workflow |
| `/sensei-check` | Japanese content validation |

## Context Modes

Context configurations in `.claude/contexts/`:

| Context | Purpose | Active Personas |
|---------|---------|-----------------|
| `dev` | Development/coding | arch, dev, test, review, security, design |
| `review` | Review-only tasks | review, design, security, sensei |
| `content` | Japanese content | sensei, dev, docs, pm |

## Rules

Modular rules in `.claude/rules/`:
- `coding-style.md` - HTML/CSS/JS conventions
- `git-workflow.md` - Version control standards
- `testing.md` - Testing requirements
- `security.md` - Security guidelines
- `japanese-content.md` - JLPT/content standards

## Skills

Reusable workflows in `.claude/skills/`:
- `tdd-workflow.md` - Test-driven development
- `verification-loop.md` - QA verification
- `code-review-workflow.md` - Review process
- `deployment-workflow.md` - Release management
- `kanji-content-creation.md` - Kanji data workflow
- `topic-page-creation.md` - Page creation workflow
- `continuous-learning.md` - Pattern extraction to skills
- `learning-curation.md` - Session learning curation
- `changelog-generation.md` - Automated changelog from git history
- `learned-pattern-*.md` - Extracted workflow patterns

## Adding New Personas

To add a new persona:
1. Create `[persona-name].md` in this directory
2. Follow the standard structure (see existing files)
3. Define workflow integration points
4. Update this README
5. Update [[../../CLAUDE.md]] agent section

---

## Related Documentation

- [[AGENTS.md]] - Agent orchestration best practices, handoff protocols
- [[DOC_MAINTENANCE.md]] - Documentation maintenance for Documenter persona
- [[../../CLAUDE.md]] - Project context, workflow overview
- [[../../DOCUMENTATION_INDEX.md]] - Complete documentation map
- [[../skills/]] - Reusable workflows for personas
- [[../rules/]] - Standards for personas to enforce
- [[../contexts/]] - Context configurations for task types
