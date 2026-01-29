# Development Context

Context configuration for development tasks.

## Purpose

Optimizes Claude's behavior for coding, implementation, and technical work.

## When to Use

- Implementing features
- Writing code
- Fixing bugs
- Building UI components
- Working with data

## Active Personas

All coding-focused personas are available:

| Persona | Prefix | Role |
|---------|--------|------|
| Technical Architect | `arch:` | Design, TDD creation |
| Feature Developer | `dev:` | Implementation |
| Quality Tester | `test:` | Testing, verification |
| Code Reviewer | `review:` | Code quality |
| Security Reviewer | `security:` | Security audit |
| Design Reviewer | `design:` | UI/UX review |

## Active Rules

Load these rule files:
- `rules/coding-style.md` - HTML/CSS/JS conventions
- `rules/git-workflow.md` - Version control standards
- `rules/testing.md` - Testing requirements
- `rules/security.md` - Security guidelines

## Active Skills

Available workflows:
- `skills/tdd-workflow.md` - Test-driven development
- `skills/verification-loop.md` - QA verification
- `skills/code-review-workflow.md` - Review process
- `skills/deployment-workflow.md` - Release management

## Commands

Priority commands:
- `/plan` - Implementation planning
- `/tdd` - Test-driven development
- `/review` - Code review
- `/deploy` - Version deployment
- `/orchestrate` - Full workflow

## Hooks

All hooks active:
- Pre-Bash checks
- Pre-Write checks
- Post-Edit checks
- Pre-Stop checks

## Focus Areas

### Code Quality
- Follow patterns in shared.css/shared.js
- Semantic HTML
- Accessible design
- Mobile-first responsive

### Workflow
- Use temp folder for WIP
- Get approval before finalizing
- Test before commit
- Document changes

### Git
- Conventional commits
- Feature branches
- PR reviews
- Version tagging

## Excluded in This Context

- Sensei persona (use content context for Japanese work)
- Documentation-only tasks (use review context)
- Japanese content validation (invoke explicitly if needed)

## Context Switch

Switch to:
- `/context content` - For Japanese content creation
- `/context review` - For review-only tasks

## Example Session

```
[dev context active]

User: Implement JLPT filter for flashcards

Claude (arch:): Let me design the architecture...
[Creates TDD]

Claude (test:): Defining test criteria...
[Creates test spec]

Claude (dev:): Implementing the filter...
[Writes code]

Claude (review:): Reviewing implementation...
[Provides feedback]
```
