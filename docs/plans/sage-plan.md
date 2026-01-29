# Implementation Plan: Learning Repository System

**Date**: 2026-01-25
**Feature**: Learning Repository and Knowledge Management System
**Status**: Planning - Updated with PM/Architect Review Recommendations

---

## Executive Summary

Transform the archived FOR_CHRIS documentation into an active "learning repository" system that compounds knowledge over time. This introduces a **Sage persona** to proactively identify patterns, curate session learnings, and extract reusable insights that continuously improve the project.

**Value Proposition:**
- Educational knowledge becomes actionable reference material
- Patterns and learnings compound across sessions
- "What we learned" becomes "what we apply"
- Creates feedback loop for continuous improvement

---

## Current State Analysis

### What EXISTS:
✅ **FOR_CHRIS docs** (archived) - Educational artifacts explaining technical work
✅ **Documenter persona** - Maintains living docs, changelog, CLAUDE.md
✅ **9-persona agent system** - Well-defined roles and workflows
✅ **Documentation structure** - Living docs, version docs, reference docs
✅ **Session learnings** - Captured in `temp/SESSION-*.md` files

### What's MISSING:
❌ **Proactive pattern identification** - No one curates learnings across sessions
❌ **Centralized learning repository** - Knowledge fragmented across locations
❌ **Active FOR_CHRIS.md** - Currently archived, not maintained at root
❌ **Learning extraction workflows** - No systematic process to extract patterns
❌ **Continuous learning skills** - Referenced but not implemented

### Knowledge Fragmentation Map:
```
Current Learning Storage (FRAGMENTED):
├── archive/FOR_CHRIS_docs/ - Historical (2 docs: pm_setup, agent_orchestration)
├── temp/SESSION-*.md - Session notes (risk being cleaned up)
├── docs/TESTING.md#bug-learnings - Bug patterns only
├── .claude/agents/AGENTS.md - Workflow learnings buried in 1155-line doc
└── temp/DOC_OPTIMIZATION_REPORT.md - One-off learnings

Problem: No centralized, actively maintained learning system
```

---

## Proposed Solution

### 1. Create "Sage" Persona

**New 10th Persona**: Sage (Wisdom curator and knowledge organizer)

**Prefix**: `sage:`

**Core Responsibilities:**
1. **Pattern Identification** - Analyze sessions for reusable patterns
2. **Knowledge Consolidation** - Curate learnings from all sources
3. **Learning Repository Management** - Maintain LEARNINGS.md and FOR_CHRIS docs
4. **Cross-Session Memory** - Build institutional knowledge
5. **Skill Extraction** - Extract patterns to `.claude/skills/`

**Why "Sage":**
- Emphasizes **wisdom curation** over mere documentation
- Short, memorable, and distinctive (easy to invoke)
- Suggests **distilling knowledge** into actionable insights
- Focuses on extracting transferable lessons

**Why New Persona vs. Extend Documenter:**
- **Different mindset**: Proactive pattern extraction vs. archival/maintenance
- **Different trigger**: Wisdom curation vs. reactive documentation
- **Different focus**: Cross-session learning vs. version-specific facts
- **Avoids overload**: Documenter already has broad responsibilities

**Role Description**: "Sage extracts and curates learnings from development sessions, transforming project history into institutional wisdom."

### 2. Establish Learning Repository Structure

```
Learning Knowledge Base (CENTRALIZED):

.claude/skills/:
├── learned-pattern-*.md (NEW - Extracted patterns as executable skills)
│   ├── learned-pattern-agent-handoff.md
│   ├── learned-pattern-file-operations.md
│   └── ... (created as patterns identified)
│
├── learning-curation.md (NEW - Curation workflow)
└── continuous-learning.md (NEW - Implement existing reference)

docs/:
├── LEARNINGS.md (NEW - Technical patterns for Claude/implementation)
│   ├── Patterns discovered and proven
│   ├── Common pitfalls and solutions
│   ├── Best practices evolved
│   ├── Decision frameworks
│   └── Cross-references to skills and FOR_CHRIS docs
│
├── TESTING.md#bug-learnings (KEEP - Bug patterns)
│   └── Root causes, fixes, prevention

archive/FOR_CHRIS_docs/ (Educational narratives for Christopher):
├── README.md (INDEX - Lists all FOR_CHRIS docs by topic)
├── agent-orchestration-comparison.md (RENAME from FOR_CHRIS_agent_orchestration.md)
├── github-project-setup.md (RENAME from FOR_CHRIS_pm_setup.md)
├── kanji-module-architecture.md (FUTURE - when kanji module complete)
├── localStorage-schema-design.md (FUTURE - when T1.1 complete)
└── ... (topic-specific educational docs, created as valuable content emerges)

Naming Pattern: [topic-description].md (descriptive, easy to find)
Examples:
  - agent-orchestration-comparison.md
  - kanji-module-architecture.md
  - spaced-repetition-implementation.md
  - testing-framework-evolution.md
```

**Key Changes**:
1. **No active FOR_CHRIS.md at root** - Instead, topic-specific docs in archive/ with clear names
2. **Single Source of Truth Hierarchy** (to prevent duplication):
   - **Skills** (`.claude/skills/learned-pattern-*.md`) = Executable workflows (if pattern is actionable)
   - **LEARNINGS.md** = Quick technical reference + decision frameworks
   - **FOR_CHRIS docs** = Deep-dive educational narratives (cross-reference, don't duplicate)
3. **Archive FOR_CHRIS_docs** is a living directory (not version-specific, updated in place with git history)

### 3. Define Workflows

#### **FOR_CHRIS Doc Decision Rubric**

Create a FOR_CHRIS doc if **≥2 of these criteria** apply:
1. **Significant architectural decision** made with trade-offs evaluated
2. **Novel pattern** not found in existing documentation or resources
3. **Workflow changed** that affects future development approach
4. **Multiple approaches evaluated** with clear winner and rationale
5. **High educational value** for Christopher's stated learning goals

**Quality bar**: Only extract patterns proven in ≥2 real implementations (not theoretical).

---

#### **Workflow A: Session Learning Curation**
```
Trigger: End of significant session with learnings
Input: temp/SESSION-*.md, conversation context
Process:
1. Sage reviews session
2. Identifies reusable patterns vs. one-off learnings
3. Applies single-source-of-truth hierarchy:
   - Actionable workflows → .claude/skills/learned-pattern-*.md (FIRST)
   - Technical patterns → docs/reference/LEARNINGS.md (with cross-refs to skills)
   - Educational narratives (if rubric met) → archive/FOR_CHRIS_docs/ (links to skills/learnings)
4. Creates learning digest in temp/LEARNING_DIGEST_[DATE].md
Output: Updated learning repositories
Note: FOR_CHRIS docs created only when ≥2 decision rubric criteria met
```

#### **Workflow B: Bug Learning Extraction**
```
Trigger: Bug fixed with root cause identified
Input: Bug details, fix description, test results
Process:
1. Sage documents in TESTING.md#bug-learnings
2. Extracts pattern to docs/reference/LEARNINGS.md if applicable
3. Creates topic-specific FOR_CHRIS doc only if decision rubric met
Output: Bug pattern documented for prevention
```

#### **Workflow C: Pattern Discovery**
```
Trigger: Pattern identified across ≥2 sessions/features (proven, not theoretical)
Input: Code examples, workflow observations, decision points
Process:
1. Sage validates pattern (proven ≥2 times in practice)
2. Writes pattern as .claude/skills/learned-pattern-*.md (if actionable)
3. Documents in docs/reference/LEARNINGS.md (with cross-ref to skill)
4. Creates FOR_CHRIS doc only if decision rubric met
Output: Reusable skill available for future use
```

#### **Workflow D: Milestone Learning Documentation**
```
Trigger: Version milestone reached (v0.3, v0.4, etc.) with significant learnings
Input: All learnings from version development
Process:
1. Sage reviews milestone work
2. Apply decision rubric to determine if FOR_CHRIS doc warranted
3. If yes, create topic-specific FOR_CHRIS doc:
   - Example: archive/FOR_CHRIS_docs/kanji-module-architecture.md
   - Engaging narrative explaining what was built, why, and key learnings
   - Cross-references to skills and LEARNINGS.md entries
4. Extract technical patterns to docs/reference/LEARNINGS.md
5. Extract reusable workflows to .claude/skills/
Output: Educational doc preserved, patterns documented for reuse
Note: Not every milestone needs a FOR_CHRIS doc - apply rubric rigorously
```

### 4. Integration with Agent Orchestration

#### **Assembly Line Integration**

**Option 1: Sequential (after Documenter)**
```
PM → Architect → Developer → Tester → Reviewers → Documenter → Sage
```

**Option 2: Parallel (with Documenter)**
```
                                    ┌─→ Documenter (version docs)
PM → ... → Reviewers → (completed) ─┤
                                    └─→ Sage (extract patterns)
```

**Recommendation**: Option 2 (parallel) - both run after feature completion

#### **Handoff Protocol**

**Sage receives from:**
- ALL personas (any can trigger learning capture)
- Documenter (after version docs updated)
- Developer (after experiments/workflow changes)
- Tester (after bugs fixed)

**Sage hands off to:**
- No formal handoff (completes workflow)
- Documenter (if long-term archival needed)

#### **Automated Triggers**

**Built into other personas:**
- **Documenter** → Always notify Sage after version docs updated
- **Developer** → Hand off to Sage after workflow experiments
- **Tester** → Hand off to Sage after bug fix with identified root cause

**Manual invocation:**
- `/sage-review` command for explicit review
- `sage:` prefix for direct invocation

**Session-based:**
- End of significant session (>5 files modified OR >50 lines changed)
- Pattern identified across ≥2 features
- Version milestone reached

### 5. Create New Skills

#### **Skill: continuous-learning.md**
```markdown
# Continuous Learning Skill

Automatically extract reusable patterns from sessions and save as learned skills.

## When to Use
- End of session with new patterns discovered
- After workflow experiments
- When multiple approaches compared

## Process
1. Review session for patterns
2. Validate pattern is proven (not theoretical)
3. Extract to .claude/skills/learned-pattern-*.md
4. Document in docs/reference/LEARNINGS.md
5. Link from FOR_CHRIS.md if educational

## Output
- New skill file in .claude/skills/
- Updated LEARNINGS.md
- Optional FOR_CHRIS.md entry
```

#### **Skill: learning-curation.md**
```markdown
# Learning Curation Skill

Curate session learnings into appropriate repositories.

## When to Use
- End of significant session
- After major feature completion
- When temp/SESSION-*.md files accumulate

## Process
1. Read session notes and conversation
2. Categorize learnings:
   - Technical patterns (docs/reference/LEARNINGS.md)
   - Educational content (FOR_CHRIS.md)
   - Bug patterns (docs/TESTING.md)
   - Reusable workflows (.claude/skills/)
3. Write/update appropriate docs
4. Create learning digest

## Output
- Updated learning repositories
- temp/LEARNING_DIGEST_[DATE].md
```

---

## Implementation Steps

### Phase 1: Foundation (Core Structure)

**Step 1.1: Create Sage Persona**
- File: `.claude/agents/sage.md`
- Content: Full persona definition (responsibilities, triggers, handoffs, constraints, decision rubric)
- Format: Follow existing persona structure (see product-manager.md)
- Prefix: `sage:`
- Include: Role description, FOR_CHRIS doc decision rubric, single-source-of-truth hierarchy

**Step 1.2: Create FOR_CHRIS Template**
- File: `.claude/templates/for-chris-doc-template.md` (NEW)
- Content:
  ```markdown
  # [Topic Title]

  ## What We Built
  [Executive summary - 2-3 sentences of what was accomplished]

  ## Why We Built It This Way
  [Architectural decisions, alternatives considered, trade-offs evaluated]
  [Link to decision rubric criteria that were met]

  ## How It Works
  [Technical deep-dive with code examples]
  [Engaging explanations using analogies where appropriate]

  ## What I Learned
  [Transferable lessons and meta-patterns]
  [What would you do differently? What worked well?]

  ## Gotchas & Pitfalls
  [Common mistakes and how to avoid them]
  [Edge cases discovered during implementation]

  ## Further Reading
  [Cross-references to:]
  - Related LEARNINGS.md entries
  - Extracted skills in .claude/skills/
  - External resources
  ```
- Style guide: Engaging, narrative, use analogies, explain "why"
- **Both educational AND technical content** (engaging explanations + technical deep-dives)
- Purpose: Guide creation of consistent, high-quality FOR_CHRIS docs

**Step 1.3: Create LEARNINGS.md**
- File: `docs/reference/LEARNINGS.md`
- Content:
  - Technical patterns discovered
  - Decision frameworks
  - Common pitfalls and solutions
  - Links to case studies
- Format: Technical but accessible, with examples

**Step 1.4: Create Learning Skills**
- File: `.claude/skills/continuous-learning.md`
- File: `.claude/skills/learning-curation.md`
- Content: Workflow definitions (see section 5 above)

**Step 1.5: Create FOR_CHRIS Index**
- File: `archive/FOR_CHRIS_docs/README.md`
- Content: Index of all FOR_CHRIS docs by topic
- Format: Table with columns: Topic, File, Date Created, Key Concepts
- Note: archive/FOR_CHRIS_docs/ is a living directory (not version-specific)

### Phase 2: Integration (Connect to System)

**Step 2.1: Update Agent System Docs**
- File: `.claude/agents/AGENTS.md`
  - Add Sage to persona table
  - Document integration with assembly line
  - Add workflows (A, B, C, D from above)
  - Update handoff protocols

- File: `.claude/agents/README.md`
  - Add Sage to persona list
  - Define prefix: `sage:`
  - Add example prompts

**Step 2.2: Update Documentation Index**
- File: `DOCUMENTATION_INDEX.md`
  - Add FOR_CHRIS.md to root directory table
  - Add docs/reference/LEARNINGS.md to docs/ table
  - Add learning skills to skills table
  - Add archive/learnings/ to structure
  - Add "Finding Learning Content" section
  - Update maintenance responsibility table

**Step 2.3: Update CLAUDE.md**
- File: `CLAUDE.md`
  - Update "Learning Goals" section to reference active FOR_CHRIS.md
  - Update "Agent Orchestration System" table with Sage
  - Update "Artifact Locations" table with learning files
  - Add note about continuous learning in relevant sections

**Step 2.4: Update Documenter Persona**
- File: `.claude/agents/documenter.md`
  - Add handoff to Sage
  - Clarify division of responsibility (version docs vs. learning patterns)
  - Update artifacts table to exclude FOR_CHRIS.md (now owned by Sage)

### Phase 3: Migration (Move Existing Content)

**Step 3.1: Rename and Organize Existing FOR_CHRIS Docs**
- Rename `archive/FOR_CHRIS_docs/FOR_CHRIS_pm_setup.md` → `github-project-setup.md`
- Rename `archive/FOR_CHRIS_docs/FOR_CHRIS_agent_orchestration.md` → `agent-orchestration-comparison.md`
- Extract from both docs:
  - Evergreen technical patterns → docs/reference/LEARNINGS.md
  - Proven workflow patterns → Consider creating .claude/skills/ if applicable
- Keep renamed docs in archive/FOR_CHRIS_docs/ (topic-based naming makes them easy to find)
- Add index file: `archive/FOR_CHRIS_docs/README.md` listing all FOR_CHRIS docs by topic

**Step 3.2: Curate Top Session Notes** (REDUCED SCOPE)
- Identify top 3 most valuable `temp/SESSION-*.md` files
- Extract proven patterns (≥2 uses) to appropriate locations:
  - Actionable workflows → .claude/skills/
  - Technical patterns → docs/reference/LEARNINGS.md
  - Educational narratives (if rubric met) → archive/FOR_CHRIS_docs/
- Create learning digest for curated sessions
- Defer full session note curation to v0.4+
- Archive or clean up curated temp files per policy

**Step 3.3: Extract One Example Pattern from AGENTS.md** (REDUCED SCOPE)
- Read `.claude/agents/AGENTS.md`
- Extract ONE high-value learning (e.g., T1.1 case study or file operations pattern)
- Create as `.claude/skills/learned-pattern-[example].md`
- Add cross-reference entry in LEARNINGS.md
- Defer full AGENTS.md extraction to Phase 4

### Phase 4: Documentation (Guide Usage)

**Step 4.1: Knowledge Management Documentation**
- Files:
  - `.claude/agents/sage.md` - Operational examples and tips (consolidated)
  - `docs/reference/knowledge-management.md` - Cross-agent knowledge reference
- Content:
  - When/how to invoke Sage (`sage:` prefix, `/sage-review` command)
  - FOR_CHRIS doc decision rubric (≥2 criteria)
  - Single-source-of-truth hierarchy (Skills > LEARNINGS > FOR_CHRIS)
  - Examples of good learning documentation
  - Quality standards for extracted patterns (proven ≥2 times)
  - Topic-based naming guidelines for FOR_CHRIS docs

**Step 4.2: Update DOC_MAINTENANCE.md**
- Add Sage responsibilities
- Define update triggers for learning docs
- Add to maintenance protocol

**Step 4.3: Add Automated Trigger Hook** (OPTIONAL - Future Enhancement)
- Consider adding to `.claude/hooks/PostToolUse.js`
- Check if >5 files modified OR >50 lines changed → Suggest Sage review
- Low priority for initial implementation

**Step 4.4: Extract Full AGENTS.md Patterns** (DEFERRED FROM PHASE 3)
- Extract remaining buried learnings from `.claude/agents/AGENTS.md`
- Create additional learned-pattern skills as appropriate
- Add cross-references to LEARNINGS.md
- Keep high-level overview in AGENTS.md, link to detailed patterns

---

## Critical Files

### Files to CREATE:
1. `.claude/agents/sage.md` - Persona definition (prefix: `sage:`)
2. `.claude/templates/for-chris-doc-template.md` - Template for topic-specific FOR_CHRIS docs
3. `docs/reference/LEARNINGS.md` - Technical patterns for Claude/implementation
4. `.claude/skills/continuous-learning.md` - Learning extraction skill
5. `.claude/skills/learning-curation.md` - Curation workflow
6. `archive/FOR_CHRIS_docs/README.md` - Index of all FOR_CHRIS docs by topic
7. `.claude/skills/learned-pattern-[example].md` - Example learned pattern (from AGENTS.md)

### Files to MODIFY:
1. `.claude/agents/AGENTS.md` - Add Sage integration, workflows, handoff protocols
2. `.claude/agents/README.md` - Add Sage persona to list (prefix: `sage:`)
3. `DOCUMENTATION_INDEX.md` - Add learning repositories and finding guide
4. `CLAUDE.md` - Update learning goals, agent table, artifact locations
5. `.claude/agents/documenter.md` - Add handoff to Sage, clarify responsibilities

### Files to READ (for migration):
1. `archive/FOR_CHRIS_docs/FOR_CHRIS_pm_setup.md` (rename to github-project-setup.md)
2. `archive/FOR_CHRIS_docs/FOR_CHRIS_agent_orchestration.md` (rename to agent-orchestration-comparison.md)
3. `temp/SESSION-*.md` (all session notes)
4. `.claude/agents/AGENTS.md` (extract buried learnings)

### Files to RENAME:
1. `archive/FOR_CHRIS_docs/FOR_CHRIS_pm_setup.md` → `github-project-setup.md`
2. `archive/FOR_CHRIS_docs/FOR_CHRIS_agent_orchestration.md` → `agent-orchestration-comparison.md`

---

## Quality Standards

### FOR_CHRIS Doc Requirements (Topic-Specific Docs in archive/):
- ✅ Topic-based naming: [descriptive-topic].md
- ✅ Engaging, conversational tone (not dry technical)
- ✅ Uses analogies and anecdotes
- ✅ Explains "why" behind decisions
- ✅ Includes concrete code examples (both educational + technical)
- ✅ Extracts transferable meta-lessons
- ✅ Standalone and complete (not dependent on other docs)
- ✅ Links to related documentation (LEARNINGS.md, skills, etc.)
- ✅ Created only when educational value is high

### LEARNINGS.md Requirements:
- ✅ Technical but accessible
- ✅ Proven patterns (not theoretical)
- ✅ Real examples from codebase
- ✅ Clear "when to apply" guidance
- ✅ Links to case studies
- ✅ Categorized by type (patterns, pitfalls, practices)

### Learned Pattern Skill Requirements:
- ✅ Follows `.claude/skills/` format
- ✅ Clear "When to Use" section
- ✅ Step-by-step process
- ✅ Expected outputs defined
- ✅ Examples included
- ✅ Cross-referenced from LEARNINGS.md

---

## Verification Plan

### After Phase 1 (Foundation):
- [ ] Sage persona exists and is complete (prefix: `sage:`)
- [ ] FOR_CHRIS doc template created (.claude/templates/)
- [ ] docs/reference/LEARNINGS.md created with initial content
- [ ] Learning skills created (.claude/skills/)
- [ ] Archive FOR_CHRIS_docs/README.md created as index

### After Phase 2 (Integration):
- [ ] AGENTS.md includes Sage in tables and workflows
- [ ] DOCUMENTATION_INDEX.md shows all learning repositories
- [ ] CLAUDE.md references active learning system
- [ ] Documenter persona updated with handoff to Sage
- [ ] No broken cross-references

### After Phase 3 (Migration):
- [ ] Existing FOR_CHRIS docs renamed with topic-based naming
- [ ] archive/FOR_CHRIS_docs/README.md indexes all docs
- [ ] Technical patterns extracted to docs/reference/LEARNINGS.md from renamed FOR_CHRIS docs
- [ ] Top 3 most valuable session notes curated
- [ ] One example pattern extracted from AGENTS.md
- [ ] Temp files cleaned (with approval)
- [ ] At least one example learned pattern skill exists

### After Phase 4 (Documentation):
- [ ] Clear guidance on using Sage (invoke with `sage:` or `/sage-review`)
- [ ] Sage guide includes decision rubric and single-source-of-truth hierarchy
- [ ] DOC_MAINTENANCE.md includes learning docs
- [ ] Example learned pattern demonstrates quality bar
- [ ] All learning repositories have content
- [ ] Full AGENTS.md pattern extraction completed (deferred from Phase 3)

### Final System Check:
- [ ] Can invoke Sage with `sage:` prefix or `/sage-review` command
- [ ] FOR_CHRIS docs are discoverable by topic, engaging, with educational + technical content
- [ ] archive/FOR_CHRIS_docs/README.md makes docs easy to find
- [ ] LEARNINGS.md contains actionable patterns with cross-references
- [ ] Skills directory contains learned patterns (proven ≥2 times)
- [ ] Single-source-of-truth hierarchy is clear (Skills > LEARNINGS > FOR_CHRIS)
- [ ] Documentation index navigates to all learning content
- [ ] System is self-sustaining (clear triggers and workflows)
- [ ] Template guides creation of new FOR_CHRIS docs
- [ ] Decision rubric prevents over-creation of FOR_CHRIS docs

---

## Success Criteria

**Immediate (v0.3):**
- ✅ Sage persona operational (invoke with `sage:` or `/sage-review`)
- ✅ FOR_CHRIS template guides doc creation (educational + technical content)
- ✅ Existing FOR_CHRIS docs renamed with topic-based naming
- ✅ LEARNINGS.md captures technical patterns with cross-references
- ✅ Single-source-of-truth hierarchy established (Skills > LEARNINGS > FOR_CHRIS)
- ✅ Decision rubric prevents over-documentation
- ✅ System integrated with agent orchestration
- ✅ At least 1 example learned pattern skill exists

**Short-term (v0.4-v0.5):**
- ✅ 3+ learned pattern skills extracted (proven ≥2 times each)
- ✅ 2-3 topic-specific FOR_CHRIS docs created (meeting decision rubric)
- ✅ Session learnings routinely curated (top valuable sessions)
- ✅ Bug learnings systematically extracted
- ✅ Full AGENTS.md pattern extraction completed

**Long-term (v1.0+):**
- ✅ Learning repository is go-to reference
- ✅ Patterns compound across development
- ✅ New contributors learn from curated knowledge
- ✅ "What we learned" actively informs "what we build"

---

## Trade-offs and Considerations

### Pros:
✅ Transforms passive archives into active knowledge
✅ Creates feedback loop for continuous improvement
✅ Makes educational content actionable
✅ Builds institutional memory across sessions
✅ Supports learning goals explicitly

### Cons:
❌ Adds new persona (complexity)
❌ Requires discipline to maintain (another doc to update)
❌ Risk of knowledge duplication across docs
❌ Initial migration effort substantial

### Mitigations:
- Clear division of responsibility (Documenter vs. Sage)
- Defined triggers and workflows (not ad-hoc)
- **Single-source-of-truth hierarchy** prevents duplication (Skills > LEARNINGS > FOR_CHRIS)
- **Decision rubric** prevents over-creation of FOR_CHRIS docs (≥2 criteria required)
- **Quality bar** for patterns (proven ≥2 times in practice)
- Start small, iterate based on value
- **Reduced Phase 3 scope** (top 3 sessions, 1 AGENTS.md pattern) prevents overwhelm
- Cross-references instead of content duplication

### Alternatives Considered:

**1. Extend Documenter instead of new persona**
- Rejected because: Different mindset (reactive vs. proactive), already broad responsibilities, risk of role confusion

**2. Persona name: "Learning Architect" vs. "Sage" vs. "Curator"**
- **"Learning Architect"**: Emphasizes structural/systematic role, parallels Technical Architect
- **"Sage"**: ✅ **CHOSEN** - Shorter, memorable, wisdom-focused, emphasizes distilling knowledge
- **"Curator"**: Balances brevity with clarity but less distinctive
- Decision: "Sage" selected for memorability and focus on wisdom extraction

**3. Active FOR_CHRIS.md at root vs. Topic-specific docs in archive/**
- Active root doc rejected: Becomes long, hard to maintain, risks overwriting
- ✅ **CHOSEN**: Topic-specific docs with descriptive names (easy to find, no overwriting)

---

## Future Enhancements

**v0.4+:**
- Create web interface to browse learning repository
- Tag learnings by topic (agents, testing, architecture, etc.)
- Add search functionality for patterns
- Automatically link learnings to related code

**v1.0+:**
- Use learning repository to onboard new AI agents
- Generate "learning reports" after each version
- Create visualization of pattern evolution
- Export learnings as blog posts or documentation

---

## Decisions Made

### From User Input:
1. **Persona Name**: ✅ **"Sage"** (wisdom curator, shorter/memorable, emphasizes distilling knowledge)
   - Role: "Sage extracts and curates learnings from development sessions"

2. **Prefix**: ✅ **`sage:`** (simple, intuitive, unique)

3. **FOR_CHRIS Doc Structure**: ✅ Archive with descriptive names (topic-based library, not single active doc)
   - Example: `agent-orchestration-comparison.md`, `kanji-module-architecture.md`
   - No active FOR_CHRIS.md at root (reduces maintenance burden)
   - Each doc is standalone and complete

4. **Naming Pattern**: ✅ Topic-based naming (e.g., `github-project-setup.md`, `localStorage-schema-design.md`)
   - Easy to find by topic
   - Descriptive, self-explanatory
   - No overwriting (each topic gets own file)

5. **Content Scope**: ✅ Both educational + technical content (complete learning resource)

6. **Migration Approach**: ✅ Rename existing docs with topic-based names, extract patterns to LEARNINGS.md

### From PM/Architect Review:
7. **Decision Rubric**: ✅ Create FOR_CHRIS doc only if **≥2 criteria** met:
   - Significant architectural decision
   - Novel pattern not in existing docs
   - Workflow changed
   - Multiple approaches evaluated
   - High educational value for Christopher

8. **Single Source of Truth**: ✅ Hierarchy to prevent duplication:
   - **Skills** (`.claude/skills/learned-pattern-*.md`) = Executable workflows
   - **LEARNINGS.md** = Quick technical reference
   - **FOR_CHRIS docs** = Deep-dive narratives (cross-reference, don't duplicate)

9. **Quality Bar**: ✅ Only extract patterns proven **≥2 times** in practice (not theoretical)

10. **Phase 3 Scope Reduction**: ✅ Curate **top 3 session notes** + **1 AGENTS.md pattern** (defer rest to v0.4+)

11. **Template Structure**: ✅ Specified sections (What/Why/How/Learned/Gotchas/Further Reading)

---

**Plan Status**: ✅ **APPROVED** - Updated with PM/Architect review recommendations

**Estimated Effort** (Updated):
- Phase 1 (Foundation): 2-3 hours
- Phase 2 (Integration): 1-2 hours
- Phase 3 (Migration - REDUCED SCOPE): 1-2 hours (top 3 sessions + 1 AGENTS.md pattern)
- Phase 4 (Documentation): 1-2 hours (includes guide + full AGENTS.md extraction)
- **Total**: **5-9 hours** (reduced from 6-10 hours)

**Key Changes from Review**:
- ✅ Persona renamed to "Sage" (`sage:` prefix)
- ✅ Decision rubric added (≥2 criteria for FOR_CHRIS docs)
- ✅ Single-source-of-truth hierarchy defined (Skills > LEARNINGS > FOR_CHRIS)
- ✅ Template structure specified
- ✅ Phase 3 scope reduced (prevents overwhelm)
- ✅ Automated triggers documented
- ✅ Quality bar defined (patterns proven ≥2 times)

**Blocking Questions**: None

**Recommended Next Step**: Start with Phase 1 (Foundation) to create core structure before integration and migration.
