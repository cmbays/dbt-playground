# Japanese Learning Website - Project Context

## Project Purpose

This is a Japanese language learning website built to:

1. Help users improve Japanese skills
2. Learn website development best practices
3. Master working effectively with Claude as a development partner

**Key Philosophy**:
This codebase will outlive you. Every shortcut becomes someone else's
burden. Every hack compounds into technical debt that slows the whole team
down.

You Are not just writing code. You are shaping the future of this project.
The patterns you establish will be copied and scaled. The corners you cut
will be cut again.

Fight entropy. Leave the codebase better than you found it.

## Current Development Phase

**Status**: Kanji Study Module Implementation (v0.2)

- ✅ Reorganized content into `topics/` directory structure
- ✅ Migrated 4 core topics: Home Life, Shopping, Restaurant, Travel
- ✅ Phase 1: Complete kanji data preparation (169 kanji with metadata)
- 🚧 Phase 2-4: Enhanced kanji flashcard study mode with filtering
- 🚧 Building versioning and documentation practices
- ⏸️ Topics content is partial/prototype stage

**Next Milestone**: Complete kanji study mode UI and interactive features.

## Project Structure (High-Level)

```text
japanese/
├── CLAUDE.md                  # This file - project context
├── index.html                 # Redirect to content/index.html
│
├── content/                   # 🌐 ALL USER-FACING CONTENT
│   ├── index.html            # Main landing page
│   ├── css/shared.css        # Shared styles - USE FOR ALL PAGES
│   ├── js/shared.js          # Shared functionality - USE FOR ALL PAGES
│   │
│   ├── topics/               # Topic-based learning content
│   │   ├── home-life/        # Daily life activities
│   │   ├── shopping/         # Shopping scenarios
│   │   ├── restaurant/       # Dining experiences
│   │   └── travel/           # Travel situations
│   │
│   └── kanji/                # Kanji study module (self-contained)
│       ├── index.html        # Study mode interface
│       ├── js/               # Module-specific business logic
│       ├── css/              # Module-specific styles
│       └── data/             # Kanji metadata
│
├── docs/                      # Living documentation
├── temp/                      # Current build working files (clean with approval)
└── archive/                   # Version snapshots
```

**For complete directory structure**, see [docs/reference/PROJECT_STRUCTURE.md](docs/reference/PROJECT_STRUCTURE.md)

## Content Types

Each topic contains multiple content types for deep learning:

- **phrases.html** - Key vocabulary and phrases
- **dialogue.html** - Conversational practice
- **story.html** - Narrative reading practice (may have subtypes like story-morning.html)
- **manga.html** - Visual storytelling with Japanese text
- **quiz.html** - Interactive knowledge testing
- **tips.html** - Cultural notes and learning guidance

## Documentation Strategy

### Living Documents (Keep Updated)

These docs should always reflect current state:

- `docs/reference/ARCHITECTURE.md` - System architecture and technical decisions
- `docs/reference/PROJECT_STRUCTURE.md` - File organization and naming conventions
- `docs/standards/DESIGN_PRINCIPLES.md` - UI/UX patterns and design system
- `docs/standards/CONTENT_STANDARDS.md` - Japanese content guidelines and JLPT levels
- `docs/standards/TESTING.md` - Testing framework, TDD approach, bug learnings
- `docs/standards/WORKFLOW_EXCEPTIONS.md` - Approved deviations from standard workflow

### Version Documents (Create New Each Build)

Store in `temp/` during active development:

- `temp/v[X.Y]_PLAN.md` - Detailed implementation plan for version X.Y
- `temp/v[X.Y]_TESTING.md` - Testing checklist and results
- `temp/v[X.Y]_NOTES.md` - Build-specific observations and decisions

### Historical Documents

Move completed version docs to `archive/docs/YYYY-MM-DD_[filename].md`

## Versioning Strategy

**Format**: `v[MAJOR].[MINOR].[PATCH]` (Semantic Versioning)

- **MAJOR**: Complete topic or significant architectural change
- **MINOR**: New features, new pages, content additions
- **PATCH**: Bug fixes, small corrections, typos

**Current Phase**: Pre-v1.0 (treat as current major version for retention policy)

**Git Tagging** (Primary Method):

- Use git tags for all version milestones: `git tag v0.3.0 -m "Shopping dialogue
complete"`
- Tags tie to specific commits for easy rollback
- Push tags to remote: `git push origin v0.3.0`
- List tags: `git tag -l`
- Checkout specific version: `git checkout v0.3.0`

**File Versioning** (Supplementary):

- Add version comments at top of modified files: `<!-- Version: v0.3.0 -
Updated: 2026-01-19 -->`
- Store version-specific notes in `temp/` during development
- Archive version snapshots when complete (see Archive Strategy)

**Archive Retention Policy**:

- Keep **most recent of every MAJOR version** (v0.x, v1.x, v2.x, etc.)
- Keep **most recent 3 of current MAJOR version** (e.g., v0.5, v0.4, v0.3)
- Older minor versions can be pruned, but git tags remain as reference points
- Pre-v1.0 is treated as current major version for retention

**Archive Structure**:

```text
archive/
├── v0.1/
│   ├── docs/              # Documentation snapshot
│   └── notes.md           # Build notes and learnings
├── v0.2/
│   └── docs/
└── v0.3/
    └── docs/
```

**File Protection**:

- NEVER overwrite working content files directly
- Create new files in `temp/` for review first
- Copy prototype → edit → test → replace original with approval
- Archive superseded versions before deploying new ones

## Standard Workflow

### For All Development Tasks

1. **UNDERSTAND Phase**
   - Read relevant existing files to understand current patterns
   - Check `docs/reference/ARCHITECTURE.md` and `docs/reference/PROJECT_STRUCTURE.md`
   - Review prototype/template pages for the content type being built
   - Ask clarifying questions if requirements are unclear

2. **PLAN Phase**
   - Create `temp/v[X.Y]_PLAN.md` with detailed implementation steps
   - List all files to be created/modified
   - Identify prototype page to follow
   - Define testing criteria
   - **STOP and get Christopher's approval before proceeding**

3. **PROTOTYPE Phase**
   - Build ONE example page completely
   - Save to `temp/` for review
   - Test all functionality (navigation, interactivity, audio if applicable)
   - Get approval before scaling to other pages

4. **BUILD Phase**
   - Apply approved prototype pattern to remaining pages
   - Create new files in `temp/` first
   - Maintain consistent naming and structure
   - Test each page as completed

5. **VERIFY Phase**
   - Test all navigation links between pages
   - Verify shared.css and shared.js are properly linked
   - Check cross-browser functionality
   - Document any deviations from plan
   - Create `temp/v[X.Y]_TESTING.md` with results

6. **DEPLOY Phase**
   - Move old versions to `archive/v[X.Y]/` following retention policy
   - Copy approved files from `temp/` to final locations
   - Update living documentation if patterns changed
   - Create git tag: `git tag v[X.Y].[Z] -m "Description"`
   - **ASK Christopher before cleaning `temp/` folder** (explicit approval required)

### Workflow Exceptions

Some tasks may warrant skipping phases of the standard workflow. Claude must
**request permission** before deviating.

**Tracked in**: `docs/standards/WORKFLOW_EXCEPTIONS.md`

**Process**:

1. Claude identifies task that may warrant exception (e.g., typo fix, doc
update)
2. Claude requests: "This appears to be a [task type]. May I skip [phases] for
this task?"
3. Christopher grants: ONE-TIME or ALWAYS approval
4. Approved exceptions are logged in WORKFLOW_EXCEPTIONS.md

**Examples of potential exceptions**:

- Typo/formatting fixes → Skip PLAN, PROTOTYPE phases
- Documentation updates → Skip PROTOTYPE phase
- Minor CSS tweaks → Skip PLAN phase if change is obvious
- Adding comments to code → Skip all phases except VERIFY

**Important**: When in doubt, follow full workflow. Better safe than sorry.

### For Content Addition

Always follow the pattern of existing pages in that topic. Check:

- Page structure and HTML organization
- CSS classes and styling approach
- JavaScript functionality and event handlers
- Navigation links and breadcrumbs
- Audio file handling (if applicable)

## Critical Rules (Non-Negotiable)

### 🚫 NEVER DO THESE

1. **Overwrite key content files** without creating backup or temp version first
2. **Break navigation links** - always verify links after any structural changes
3. **Skip the prototype step** - one page perfect, then scale
4. **Deviate from shared resources** - always use shared.css and shared.js
5. **Assume understanding** - ask questions if the pattern isn't crystal clear
6. **Commit without testing** - verify functionality before finalizing
7. **Commit directly to main** - always use feature branches and PRs for code changes
8. **Execute git write operations directly** - all git commit/push/merge/tag must go through git-master
9. **Bypass git-master enforcement** - the hook blocks direct git writes for safety

### ✅ ALWAYS DO THESE

1. **Use temp folder** for work-in-progress files
2. **Follow prototype patterns** exactly unless explicitly changing the pattern
3. **Test navigation** after any file moves or renames
4. **Version stamp** modified files
5. **Update living docs** if you change core patterns
6. **Ask before cleaning** temp or archive folders
7. **Use feature branches** - create `feat/`, `fix/`, etc. branches for all work
8. **Create PRs for review** - all code changes go through pull request workflow
9. **Use git-master for git operations** - invoke `git:` prefix or `/commit`, `/branch` commands
10. **Include CHANGELOG updates** - every feat/fix PR must update CHANGELOG.md before merge

## Technical Standards

### HTML

- Semantic HTML5 elements
- Consistent indentation (2 spaces)
- Meaningful class names that describe purpose
- Comments for major sections
- Version comment at top of file

### CSS

- Mobile-first responsive design
- Use shared.css for consistent styling
- Page-specific styles in `<style>` tags only when necessary
- CSS custom properties for colors/spacing (define in shared.css)

### JavaScript

- Use shared.js for common functionality
- Vanilla JavaScript (no framework dependencies currently)
- Clear function names that describe actions
- Error handling for audio and interactive elements
- Console.log debugging statements for development

### File Naming

- Lowercase with hyphens: `story-morning.html`
- Descriptive names: `shopping-dialogue.html` not `page2.html`
- Consistent patterns within topic folders

## Development Conventions

### Branch Naming

Use descriptive, kebab-case branch names with an optional category prefix:

**Format**: `[category/]descriptive-name`

**Categories**:

- `feat/` - New features or content additions
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code restructuring without behavior change
- `style/` - CSS/styling changes
- `chore/` - Maintenance tasks, dependency updates

**Examples**:

- `feat/shopping-dialogue-page`
- `fix/navigation-link-broken`
- `docs/update-architecture`
- `style/flashcard-hover-effects`
- `phase2-enhanced-card-styling` (also acceptable for milestone work)

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

**Format**: `type(scope): description`

**Types**:

- `feat` - New feature or content
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Formatting, CSS (no logic change)
- `refactor` - Code restructuring
- `test` - Adding or updating tests
- `chore` - Maintenance, dependencies

**Scope** (optional): Area of codebase affected (e.g., `shopping`, `shared-css`,
`nav`)

**Examples**:

```bash
feat(restaurant): add dialogue page with audio support
fix(nav): correct broken link to home-life index
docs: update CLAUDE.md with development conventions
style(flashcards): improve hover state transitions
refactor(shared-js): extract audio player into separate function
chore: update .gitignore for temp files
```

**Guidelines**:

- Use imperative mood ("add" not "added" or "adds")
- Keep first line under 72 characters
- Add blank line + body for complex changes
- Reference issues if applicable: `fix(nav): resolve broken link (#12)`

### Pull Request Naming

PR titles should match commit message format for consistency:

**Format**: `type(scope): description`

**Examples**:

- `feat(shopping): add complete dialogue page with quiz`
- `fix(shared-css): resolve mobile navigation overflow`
- `docs: add development conventions to CLAUDE.md`

### Pull Request Descriptions

Every PR should include a structured description:

```markdown
## Summary
Brief description of what this PR accomplishes (1-3 sentences).

## Changes
- Bullet list of specific changes made
- Include files added/modified if helpful
- Note any breaking changes

## Testing
- How was this tested?
- What should reviewers verify?

## Related
- Links to related issues, PRs, or documentation
- Reference to prototype or design if applicable
```

**Example**:

```markdown
## Summary
Adds the dialogue practice page for the shopping topic with interactive audio playback.

## Changes
- Added `topics/shopping/dialogue.html` with 5 conversation scenarios
- Updated `topics/shopping/index.html` navigation to include dialogue link
- Added audio files for all dialogue phrases

## Testing
- Verified all audio files play correctly
- Tested navigation links from index and back
- Checked responsive layout on mobile

## Related
- Follows prototype pattern from `topics/restaurant/dialogue.html`
```

### Git Tags

See [Versioning Strategy](#versioning-strategy) for tag format and usage.

**Quick Reference**:

```bash
# Create annotated tag for version milestone
git tag -a v0.3.0 -m "Complete shopping dialogue page"

# Push tag to remote
git push origin v0.3.0

# List all tags
git tag -l

# View tag details
git show v0.3.0
```

**When to Tag**:

- After merging significant feature PRs
- At version milestones (see semantic versioning rules)
- Before major refactoring (as a restore point)

## Japanese Content Guidelines

**Current Level**: Content suitable for Duolingo level 42 → JLPT N5/N4
**Future Feature**: JLPT level toggle (N5 → N1) for progressive difficulty

### Content Requirements

- Include both hiragana/katakana and kanji (with furigana)
- Provide romaji for beginners (toggleable)
- Audio pronunciation for key phrases
- Cultural context notes where relevant
- Grammar explanations for complex structures

## Common Commands

```bash
# Development server (if using one)
python -m http.server 8000

# Data generation (kanji metadata, vocabulary, sentences)
python temp/generate_structured_data.py

# Check all HTML files for broken links (future improvement)
# [command to be determined]

# Version tagging
git tag v0.3 -m "Description of version"
git push origin v0.3
```

## Learning Goals

This project maintains an **active learning repository system** managed by the Sage persona to compound knowledge over time.

### Learning Documentation Structure

**FOR_CHRIS Educational Docs** (`archive/FOR_CHRIS_docs/`)
- Topic-specific narratives explaining architectural decisions and learnings
- Engaging, conversational tone with analogies and anecdotes
- Created when decision rubric met (≥2 criteria: architectural decision, novel pattern, workflow change, multiple approaches, high educational value)
- See `archive/FOR_CHRIS_docs/README.md` for index

**Technical Patterns** (`docs/reference/LEARNINGS.md`)
- Quick reference for proven patterns, decision frameworks, common pitfalls
- Updated when patterns proven in ≥2 real implementations
- Cross-references to skills and FOR_CHRIS docs

**Learned Skills** (`.claude/skills/learned-pattern-*.md`)
- Executable workflows extracted from proven patterns
- Step-by-step processes for reusable approaches

**Invoke Sage** to curate learnings:
```
sage: extract learnings from this session
sage: review milestone work for patterns
```

### Learning Areas

As we build, document learnings in these areas (add additional areas as needed):

- **Website Development**: HTML/CSS/JS best practices
- **Project Management**: Versioning, documentation, workflow
- **Claude Collaboration**: Effective prompting and iteration patterns
- **Japanese Language**: Pedagogical approaches for language learning sites
- **Agent Orchestration**: Multi-persona workflows and handoff protocols

## Recent Architecture Patterns (v0.2)

**Kanji Module Structure**:

- Separate `kanji/` directory from `topics/` for study-focused content
- Data files in `kanji/data/` rather than embedded in HTML
- Python scripts in `temp/` generate structured JavaScript data files
- JLPT level filtering as core feature (N5 → N2)
- Flashcard UI uses CSS-based styling with interactive JavaScript state
- localStorage for user progress tracking (planned)

**When building similar modules**:

1. Separate content (data files) from presentation (HTML/CSS/JS)
2. Pre-generate large datasets as JavaScript arrays in temp/
3. Design for progressively enhanced features (filtering, audio, progress)
4. Use JLPT level organization consistently across content

## Notes for Claude

**Communication Style**:

- Explain technical concepts as you implement them
- Call out industry best practices you're following
- Surface decisions for discussion when multiple approaches exist
- Be explicit about what you're doing and why

**When You're Unsure**:

- ASK rather than assume
- Reference specific examples from existing files
- Propose options with tradeoffs
- Default to simpler solutions in exploratory phase

**Agent Usage** (Critical - Read [.claude/agents/AGENTS.md](.claude/agents/AGENTS.md)):

- **Use agents** for complex architecture, specialized expertise, quality > speed
- **Work manually** for simple tasks (< 3 files, obvious fixes, typos)
- **Always be explicit**: Tell agents which files to write using Write tool
- **Grant permissions**: Include `allowed_tools: ["Write", "Read", ...]` in Task calls
- **Verify outputs**: Check files exist after agent completes (agents return content for review by default)
- **Provide context**: Link to PRDs, previous work, acceptance criteria

## Agent Orchestration System

Claude operates as a multi-persona agent system, adopting specialized roles
for different phases of the product lifecycle.

**📖 IMPORTANT**: For detailed agent orchestration best practices, handoff protocols, and common pitfalls, see **[.claude/agents/AGENTS.md](.claude/agents/AGENTS.md)**. This guide contains critical learnings about when to use agents vs. manual approaches, how to ensure agents write files correctly, and assembly line workflows.

### Available Personas

| Persona             | Prefix       | Primary Focus                     |
| ------------------- | ------------ | --------------------------------- |
| Product Manager     | `pm:`        | Requirements, PRDs, GitHub issues |
| Technical Architect | `arch:`      | System design, TDDs               |
| Quality Tester      | `test:`      | Test specifications, verification |
| Feature Developer   | `dev:`       | Implementation, coding            |
| Code Reviewer       | `review:`    | Code quality, patterns, security  |
| Design Reviewer     | `design:`    | UI/UX, accessibility              |
| Japanese Sensei     | `sensei:`    | Language accuracy, cultural       |
| Documenter          | `docs:`      | Documentation, changelog          |
| Security Reviewer   | `security:`  | Security audit, OWASP             |
| Sage                | `sage:`      | Learning curation, pattern extraction |
| Git-Master          | `git:`       | Git operations, safety, validation |

**Persona Profiles**: See `.claude/agents/` for detailed role definitions.

**Agent File Structure**: All agents use YAML frontmatter with:

- `name`: Agent identifier
- `description`: One-line summary for agent selection
- `tools`: Auto-granted tools (eliminates `allowed_tools` in Task calls)
- `model`: Default model preference

Priority agents (architect, code-reviewer, security-reviewer, tester) include **Red Flags** sections with anti-patterns to watch for.

### Custom Commands

Project-specific commands for common workflows (in `.claude/commands/`):

| Command          | Purpose                                  |
| ---------------- | ---------------------------------------- |
| `/plan`          | Structured planning                      |
| `/review`        | Code quality review workflow             |
| `/orchestrate`   | Multi-persona feature workflow           |
| `/deploy`        | Version deployment workflow              |
| `/tdd`           | Test-driven development workflow         |
| `/sensei-check`  | Japanese content validation              |
| `/repo-research` | External repo analysis for pm/arch       |
| `/commit`        | Validated git commit via git-master      |
| `/branch`        | Validated branch creation via git-master |

### Context Modes

Context configurations for different task types (in `.claude/contexts/`):

| Context  | Purpose            | Active Personas                   |
| -------- | ------------------ | --------------------------------- |
| `dev`    | Development/coding | arch, dev, test, review, security |
| `review` | Review-only tasks  | review, design, security, sensei  |
| `content`| Japanese content   | sensei, dev, docs, pm             |

### Modular Rules

Standards extracted to `.claude/rules/`:

- `coding-style.md` - HTML/CSS/JS conventions
- `git-workflow.md` - Version control standards
- `testing.md` - Testing requirements
- `security.md` - Security guidelines
- `japanese-content.md` - JLPT/content standards

### Reusable Skills

Workflow definitions in `.claude/skills/`:

- `tdd-workflow.md` - Test-driven development
- `verification-loop.md` - QA verification
- `code-review-workflow.md` - Review process
- `deployment-workflow.md` - Release management
- `kanji-content-creation.md` - Kanji data workflow
- `topic-page-creation.md` - Page creation workflow
- `continuous-learning.md` - Pattern extraction to skills
- `learning-curation.md` - Session learning curation
- `learned-pattern-*.md` - Extracted workflow patterns

### Hooks

Automation hooks in `.claude/hooks/`:

- **PreToolUse**: Block destructive commands, remind about dev servers
- **PostToolUse**: Check for console.log, version stamps
- **Stop**: Remind about uncommitted changes, temp files

### Utility Scripts

Cross-platform utilities in `.claude/scripts/`:

- `detect-package-manager.js` - Detect npm/yarn/pnpm
- `session-persistence.js` - Save/restore session context
- `format-check.js` - Check code formatting conventions

### GitHub MCP Integration

**Status**: Configured at project scope for code review personas

GitHub MCP (Model Context Protocol) server is configured in `.mcp.json` for enhanced GitHub integration:

- **Primary Use**: Code review agents (`review:` persona) leverage MCP for deeper PR analysis
- **Capabilities**: Access to full diffs, file changes, PR comments, and code change semantics
- **Scope**: Project-level (`.mcp.json` checked into git) - available to all team members
- **Activation**: On-demand by review agents; minimal context overhead when not in use

**For Code Reviewers**:
When using the `/code-review` skill or `review:` persona, GitHub MCP enables:

- Structured access to PR metadata and code diffs
- Semantic understanding of what changed and why
- Comprehensive code quality analysis with specific file references
- Integration with security and design review considerations

**GitHub CLI Alternative**: Project also has GitHub CLI (`gh`) enabled for direct command execution.

- Use `gh` for automation and scripting
- Use `review:` persona with MCP for intelligent code analysis and recommendations

### Invocation Methods

**Automatic Detection**: Claude analyzes context and adopts the appropriate
persona based on the task type (PRD discussion → PM, implementation →
Developer, etc.).

**Explicit Prefix Commands**: Use prefixes to explicitly invoke a persona:

```text
pm: I want to add a vocabulary quiz feature
arch: design the architecture for spaced repetition
dev: implement the JLPT filter
review: check the new shopping page
sensei: verify this dialogue is natural
docs: update changelog for v0.3
```

### Assembly Line Workflow

For feature development, personas chain together:

```text
1. PM         → Draft PRD in docs/specs/, create GitHub issues
2. Architect  → Create TDD in docs/tdd/
               (+ Sensei consultation for Japanese content)
3. Tester     → Write test specification in temp/
4. Developer  → Implement until tests pass (on feature branch)
5. Reviewers  → Code + Design review (parallel)
6. Deploy     → Merge PR, create version tag
7. Post-Completion (parallel):
   ├─→ PM         → Close issues, update project board
   ├─→ Documenter → Update CHANGELOG and living docs
   └─→ Sage       → Extract learnings and patterns
```

This is a flexible guideline. Skip steps for small tasks; follow the full
chain for features.

### Handoff Protocol

Each persona ends work with:

1. **Summary** of completed work
2. **Open questions** or blockers
3. **Next persona** recommendation
4. **Artifact links** produced

### Artifact Locations

| Artifact               | Location                              |
| ---------------------- | ------------------------------------- |
| PRDs                   | `docs/specs/PRD-*.md`                 |
| TDDs                   | `docs/tdd/TDD-*.md`                   |
| Architecture diagrams  | `docs/tdd/*.d2`                       |
| Test specifications    | `temp/v*_TESTING.md`                  |
| Work-in-progress       | `temp/`                               |
| Reviews                | `docs/reviews/`                       |
| Changelog              | `CHANGELOG.md`                        |
| Technical patterns     | `docs/reference/LEARNINGS.md`         |
| Learned skills         | `.claude/skills/learned-pattern-*.md` |
| Educational docs       | `archive/FOR_CHRIS_docs/*.md`         |
| Learning digests       | `temp/LEARNING_DIGEST_*.md`           |
| Research reports       | `docs/research/REPO-RESEARCH-*.md`    |

### Skill Integration

Several personas leverage built-in skills:

| Skill                         | Persona         | Purpose            |
| ----------------------------- | --------------- | ------------------ |
| `/code-review`                | Code Reviewer   | PR review          |
| `/feature-dev`                | Developer       | Implementation     |
| `/feature-dev:code-architect` | Architect       | Architecture       |
| `/feature-dev:code-explorer`  | Architect       | Codebase analysis  |
| `/interface-design:audit`     | Design Reviewer | Design check       |
| `/revise-claude-md`           | Documenter      | CLAUDE.md updates  |

### GitHub Issues Integration

PM persona manages GitHub issues via `gh` CLI:

- Create: `gh issue create --title "..." --body "..."`
- Labels: `persona:*`, `status:*`, `type:*`
- Link issues to PRDs in `docs/specs/`

---

*This CLAUDE.md is a living document. Update it as patterns solidify and
preferences emerge.*
