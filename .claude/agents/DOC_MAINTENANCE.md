# Documentation Maintenance Guide

**Purpose**: Detailed protocols for keeping documentation current and consistent across the project.

**Last Updated**: 2026-01-25
**Maintainer**: Documenter and Sage personas

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Update Triggers](#update-triggers)
3. [Update Procedures](#update-procedures)
4. [Wiki-Link Standards](#wiki-link-standards)
5. [Preventing Drift](#preventing-drift)
6. [Consolidation Process](#consolidation-process)
7. [Quality Assurance](#quality-assurance)
8. [Version Control for Docs](#version-control-for-docs)

---

## Core Principles

### 1. Single Source of Truth

Every piece of information should live in ONE authoritative location. Other documents should link, not duplicate.

**Authoritative sources by topic:**

| Topic | Authoritative Document |
|-------|------------------------|
| Agent orchestration | `.claude/agents/AGENTS.md` |
| Agent personas | `.claude/agents/README.md` |
| Reusable workflows | `.claude/skills/*.md` |
| Learned patterns (skills) | `.claude/skills/learned-pattern-*.md` |
| Technical patterns | `docs/reference/LEARNINGS.md` |
| Educational narratives | `archive/FOR_CHRIS_docs/*.md` |
| Bug learnings | `docs/TESTING.md#bug-learnings` |
| Coding standards | `.claude/rules/*.md` |
| Project structure | `docs/PROJECT_STRUCTURE.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| dbt conventions | `docs/CONTENT_STANDARDS.md` |
| UI/UX patterns | `docs/DESIGN_PRINCIPLES.md` |
| Testing approach | `docs/TESTING.md` |
| Task management | `docs/PROJECT_BOARD_GUIDE.md` |
| Product roadmap | `docs/ROADMAP.md` |

### 2. Documentation is Code

- Track changes in git
- Review documentation PRs
- Use meaningful commit messages
- Apply versioning mindset

### 3. Freshness Matters

Outdated documentation is worse than no documentation. Every doc should have:

- "Last Updated" timestamp
- Clear ownership
- Regular review schedule

### 4. Link Over Duplicate

When you need to reference information:

```markdown
# Good - Links to source
See [[docs/ARCHITECTURE.md#caching-strategy]] for caching details.

# Bad - Duplicates content
Caching uses a 1 week TTL for CSS and JS files...
```

### 5. Documenter vs Sage Division of Responsibility

The project uses two personas for documentation maintenance:

**Documenter (`docs:`)** - Reactive, Current State

- **Focus**: Version-specific facts, living documentation
- **Owns**: CHANGELOG, CLAUDE.md, living docs (ARCHITECTURE, PROJECT_STRUCTURE, etc.)
- **Trigger**: Version completion, architecture change, new standards
- **Output**: Current state documentation

**Sage (`sage:`)** - Proactive, Institutional Wisdom

- **Focus**: Cross-session patterns, educational narratives
- **Owns**: LEARNINGS.md, learned-pattern skills, FOR_CHRIS docs
- **Trigger**: Pattern discovered (≥2 uses), bug with root cause, significant session
- **Output**: Reusable patterns, educational documentation

**Both run in parallel** after feature completion. Documenter updates what changed; Sage extracts what was learned.

---

## Update Triggers

### Immediate Update Required

These events require documentation updates in the same PR:

| Event | Documents to Update |
| ------- | --------------------- |
| New file/directory added | `docs/PROJECT_STRUCTURE.md` |
| Architecture change | `docs/ARCHITECTURE.md` |
| New CSS pattern | `docs/DESIGN_PRINCIPLES.md` |
| New content type | `docs/CONTENT_STANDARDS.md` |
| New agent persona | `.claude/agents/README.md`, create `[persona].md` |
| New skill/workflow | `.claude/skills/`, update `README.md` |
| New rule | `.claude/rules/`, update relevant docs |
| Bug fixed with learnings | `docs/TESTING.md` (Bug Learnings section) |
| Breaking change | `CHANGELOG.md`, affected docs |

### Update After Milestone

These updates happen at version deployment:

| Event | Documents to Update |
| ------- | --------------------- |
| Version deployed | `CHANGELOG.md`, archive creation |
| Phase completed | `docs/ROADMAP.md` status |
| Major feature shipped | Sage extracts learnings to LEARNINGS.md, creates FOR_CHRIS doc if rubric met |
| Project board changes | `docs/PROJECT_BOARD_GUIDE.md` |

### Sage-Specific Triggers

These events trigger Sage persona for learning extraction:

| Event | Sage Action |
| ------- | ------------- |
| Pattern observed ≥2 times | Extract to `.claude/skills/learned-pattern-*.md` + LEARNINGS.md |
| Significant session (>5 files OR >50 lines) | Curate `temp/SESSION-*.md`, create learning digest |
| Bug fixed with root cause | Document in `docs/TESTING.md#bug-learnings` + LEARNINGS.md |
| Version milestone with learnings | Apply decision rubric for FOR_CHRIS doc, extract patterns |
| Educational value identified | Create FOR_CHRIS doc if decision rubric met (≥2 criteria) |

### Periodic Review (Monthly)

**Documenter Reviews:**

| Document | Review Focus |
| ---------- | -------------- |
| `CLAUDE.md` | Current status accurate? |
| `docs/ARCHITECTURE.md` | Tech stack current? |
| `docs/ROADMAP.md` | Timelines realistic? |
| All docs | Broken links? |

**Sage Reviews:**

| Document | Review Focus |
| ---------- | -------------- |
| `docs/reference/LEARNINGS.md` | Patterns still accurate? New patterns to add? |
| `archive/FOR_CHRIS_docs/README.md` | Index complete and up-to-date? |
| `temp/SESSION-*.md` files | Valuable sessions to curate? |
| `.claude/skills/learned-pattern-*.md` | Skills still relevant? New patterns to extract? |

---

## Update Procedures

### Standard Documentation Update

```markdown
## Procedure: Update Living Documentation

1. IDENTIFY the authoritative document for your change
   - Check [[DOCUMENTATION_INDEX.md]] if unsure

2. READ the current document state
   - Understand existing structure
   - Note related sections

3. MAKE minimal edits
   - Preserve existing structure
   - Add to appropriate section
   - Don't reorganize unless necessary

4. ADD wiki-links to related docs
   - Link any referenced documents
   - Link from related docs back to yours

5. UPDATE metadata
   - "Last Updated" timestamp
   - Version number if applicable

6. VERIFY
   - All wiki-links work
   - No redundancy introduced
   - Formatting consistent

7. COMMIT with clear message
   - docs: update [doc-name] with [change]
```

### Creating New Documentation

```markdown
## Procedure: Create New Document

1. CONFIRM this document is needed
   - Does authoritative source already exist?
   - Can existing doc be enhanced instead?

2. CHOOSE location based on type:
   - Project-wide info -> docs/
   - Agent/orchestration -> .claude/agents/
   - Reusable workflow -> .claude/skills/
   - Standard/rule -> .claude/rules/
   - Product spec -> docs/specs/
   - Technical design -> docs/tdd/

3. USE consistent structure:
   ```markdown
   # Title

   **Purpose**: One-line description

   **Last Updated**: YYYY-MM-DD
   **Maintainer**: [persona or team]

   ---

   ## Table of Contents (if >100 lines)

   ---

   ## Content Sections...

   ---

   ## Related Documentation

   - [[link1]]
   - [[link2]]
   ```

1. ADD to index documents:
   - Update [[DOCUMENTATION_INDEX.md]]
   - Update parent directory README if applicable
   - Add wiki-links from related docs

2. ANNOUNCE in commit message

```

### Deprecating Documentation

```markdown
## Procedure: Deprecate Document

1. ADD deprecation notice at top:
   ```markdown
   > **DEPRECATED**: This document is no longer maintained.
   > See [[new-authoritative-doc.md]] for current information.
   ```

1. MOVE to archive (if historical value):
   - `archive/docs/YYYY-MM-DD_[filename].md`

2. UPDATE all incoming links:
   - Search for `[[deprecated-doc]]`
   - Replace with link to new doc

3. REMOVE from indexes:
   - Remove from DOCUMENTATION_INDEX.md
   - Remove from directory READMEs

```

### Sage Learning Extraction Procedures

#### Extract Pattern to LEARNINGS.md

```markdown
## Procedure: Extract Pattern to LEARNINGS.md

1. VALIDATE pattern is proven (≥2 uses in practice, not theoretical)

2. CHOOSE appropriate section:
   - Proven Patterns (reusable patterns)
   - Decision Frameworks (when to do X vs Y)
   - Common Pitfalls (mistakes to avoid)
   - Best Practices (standards that emerged)

3. WRITE entry with format:
   ```markdown
   #### Pattern: [Name]

   **When to apply**: [Trigger conditions]

   **Proven in**: [Where used 2+ times]

   **Description**: [What it is]

   **Process/Benefits/Gotchas**: [Details]

   **See also**: [Cross-references]
   ```

4. UPDATE Table of Contents

5. UPDATE metrics at bottom

6. COMMIT with message: `docs(learnings): add [pattern name] pattern`

```

#### Create Learned Pattern Skill

```markdown
## Procedure: Create Learned Pattern Skill

1. VALIDATE pattern is actionable workflow, proven ≥2 times

2. CREATE `.claude/skills/learned-pattern-[name].md`

3. FOLLOW skill format:
   - Description
   - When to Use
   - Process (numbered steps)
   - Expected Outputs
   - Examples

4. ADD cross-reference entry in LEARNINGS.md

5. CONSIDER FOR_CHRIS doc if decision rubric met

6. COMMIT with message: `skill: add learned-pattern-[name]`
```

#### Create FOR_CHRIS Educational Doc

```markdown
## Procedure: Create FOR_CHRIS Educational Doc

1. APPLY decision rubric (≥2 criteria required):
   - [ ] Significant architectural decision
   - [ ] Novel pattern not in existing docs
   - [ ] Workflow changed
   - [ ] Multiple approaches evaluated
   - [ ] High educational value

2. IF rubric met:
   - Copy `.claude/templates/for-chris-doc-template.md`
   - Choose topic-based filename (e.g., `staging-layer-architecture.md`)

3. FILL all sections:
   - What We Built
   - Why We Built It This Way
   - How It Works
   - What I Learned
   - Gotchas & Pitfalls
   - Further Reading

4. INCLUDE concrete code examples

5. ADD cross-references to LEARNINGS.md and skills

6. UPDATE `archive/FOR_CHRIS_docs/README.md` index

7. COMMIT with message: `docs(for-chris): add [topic] educational doc`
```

#### Curate Session Notes

```markdown
## Procedure: Curate Session Notes

1. READ `temp/SESSION-[DATE].md`

2. IDENTIFY reusable patterns vs. one-off learnings

3. APPLY single-source-of-truth hierarchy:
   - Actionable workflows → `.claude/skills/learned-pattern-*.md` (FIRST)
   - Technical patterns → `docs/reference/LEARNINGS.md`
   - Educational narratives (if rubric met) → `archive/FOR_CHRIS_docs/`
   - Bug patterns → `docs/TESTING.md#bug-learnings`

4. CREATE `temp/LEARNING_DIGEST_[DATE].md` summary

5. ARCHIVE or clean session note (with approval)
```

---

## Wiki-Link Standards

### Format

```markdown
[[path/to/file.md]]              # Full document link
[[path/to/file.md#section-id]]   # Section link (heading slug)
[[path/to/file.md|Display Text]] # Custom display text
```

### Section ID Rules

Section IDs are auto-generated from headings:

- Lowercase
- Spaces become hyphens
- Special characters removed

```markdown
## Agent Handoff Best Practices
-> #agent-handoff-best-practices

## For New Agents / Fresh Context Sessions
-> #for-new-agents--fresh-context-sessions
```

### When to Link

**Always link when:**

- Mentioning another document by name
- Describing a process documented elsewhere
- Referencing examples or case studies
- Pointing to related information
- Defining terms explained elsewhere

**Link examples:**

```markdown
# Good
Follow the [[.claude/skills/tdd-workflow.md|TDD workflow]] for this feature.
See [[docs/ARCHITECTURE.md#data-flow]] for how data moves.
The [[.claude/agents/README.md#pm|PM persona]] handles requirements.

# Not as good
Follow the TDD workflow for this feature.
See ARCHITECTURE.md for how data moves.
The PM persona handles requirements.
```

### Link Maintenance

**When moving/renaming documents:**

1. Search for all `[[old-path]]` references
2. Update to `[[new-path]]`
3. Consider leaving redirect note in old location

**Checking for broken links:**

```bash
# Find all wiki-links in project
grep -r '\[\[.*\]\]' --include='*.md' .

# Manual verification recommended for critical docs
```

---

## Preventing Drift

### Common Drift Patterns

| Pattern | Prevention |
|---------|------------|
| Duplicate content | Link to authoritative source |
| Outdated timestamps | Update on every edit |
| Broken links | Verify links on edit |
| Orphaned docs | Keep indexes current |
| Inconsistent style | Follow templates |

### Pre-Commit Checklist

Before committing documentation:

- [ ] "Last Updated" timestamp current
- [ ] All wiki-links verified
- [ ] No content duplicated from authoritative source
- [ ] Spell check passed
- [ ] Formatting consistent
- [ ] Added to appropriate indexes

### Code Review for Docs

Documentation PRs should verify:

- [ ] Information is accurate
- [ ] Placed in correct location
- [ ] Links to related docs
- [ ] Doesn't duplicate existing content
- [ ] Follows document structure template
- [ ] Timestamp updated

---

## Consolidation Process

When you discover redundant information across documents:

### Step 1: Identify Authoritative Source

```markdown
Q: Which document should own this information?
A: Check the topic -> document mapping in Core Principles
```

### Step 2: Compare Content

```markdown
- Read both versions
- Identify which is more complete/accurate
- Note any unique information in each
```

### Step 3: Merge to Authoritative

```markdown
- Enhance authoritative doc with any unique content
- Preserve the best explanation/examples
- Add wiki-links to related concepts
```

### Step 4: Replace Duplicate

```markdown
# Before (in non-authoritative doc)
## Caching Strategy
CSS and JS files are cached for 1 week...
[full explanation]

# After
## Caching Strategy
See [[docs/ARCHITECTURE.md#caching-strategy]] for caching details.
```

### Step 5: Document Consolidation

```markdown
Commit message:
docs: consolidate caching info to ARCHITECTURE.md

- Moved caching details from PROJECT_STRUCTURE.md to ARCHITECTURE.md
- Added wiki-link from PROJECT_STRUCTURE.md
- Enhanced ARCHITECTURE.md with additional context
```

---

## Quality Assurance

### Document Quality Checklist

```markdown
## Quality Checklist: [Document Name]

### Structure
- [ ] Purpose statement at top
- [ ] Table of contents (if >100 lines)
- [ ] Logical section organization
- [ ] Related documentation section

### Content
- [ ] Information is accurate
- [ ] Examples are current
- [ ] No deprecated references
- [ ] Links all work

### Metadata
- [ ] Last Updated is current
- [ ] Maintainer identified
- [ ] In appropriate index

### Style
- [ ] Consistent heading levels
- [ ] Code blocks formatted
- [ ] Tables aligned
- [ ] Lists consistent
```

### Periodic Audit

Monthly documentation audit checklist:

```markdown
## Documentation Audit: [YYYY-MM]

### Accuracy Check
- [ ] CLAUDE.md current status matches reality
- [ ] PROJECT_STRUCTURE.md matches actual files
- [ ] ARCHITECTURE.md reflects current system
- [ ] ROADMAP.md timelines realistic

### Link Verification
- [ ] All wiki-links in CLAUDE.md work
- [ ] All wiki-links in AGENTS.md work
- [ ] Index documents have working links

### Freshness Check
- [ ] All "Last Updated" within 90 days for living docs
- [ ] Archive retention policy applied

### Consistency Check
- [ ] No duplicate content across docs
- [ ] Authoritative sources clearly identified
- [ ] Cross-references bidirectional
```

---

## Version Control for Docs

### Commit Messages for Documentation

Follow conventional commits:

```bash
# Adding documentation
docs: add deployment workflow guide

# Updating documentation
docs(architecture): update caching section

# Fixing documentation
docs: fix broken link in AGENTS.md

# Consolidating documentation
docs: consolidate testing info to TESTING.md
```

### Documentation in PRs

When PRs include documentation:

**PR Description Template:**

```markdown
## Documentation Changes

### Added
- [New document or section]

### Updated
- [Changed document]: [What changed]

### Removed
- [Deprecated document or section]

### Links Affected
- [Any documents that now link differently]
```

### Tagging Documentation Milestones

For major documentation overhauls:

```bash
# Tag significant documentation versions
git tag -a docs-v1.0 -m "Documentation overhaul: agent system complete"
```

---

## Related Documentation

- [[DOCUMENTATION_INDEX.md]] - Complete documentation map
- [[.claude/agents/AGENTS.md]] - Agent orchestration (includes maintenance protocol summary)
- [[.claude/agents/documenter.md]] - Documenter persona definition
- [[.claude/agents/sage.md]] - Sage persona definition
- [[docs/reference/knowledge-management.md]] - Cross-agent knowledge management reference
- [[docs/reference/LEARNINGS.md]] - Technical patterns reference
- [[archive/FOR_CHRIS_docs/README.md]] - Educational docs index
- [[CLAUDE.md#versioning-strategy]] - Project versioning approach
- [[.claude/rules/git-workflow.md]] - Git commit conventions

---

*This document itself should be reviewed and updated whenever documentation practices evolve.*
