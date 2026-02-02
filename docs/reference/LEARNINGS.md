# Technical Learnings & Patterns

**Purpose**: Quick technical reference for proven patterns, decision frameworks, common pitfalls, and best practices discovered during development.

**Maintenance**: Owned by Sage persona. Updated when patterns are proven in ≥2 real implementations.

**Related Documentation**:

- Executable workflows: `.claude/skills/learned-pattern-*.md`
- Educational narratives: `docs/for_chris/`
- Bug-specific patterns: `docs/standards/TESTING.md#bug-learnings`

---

## Table of Contents

- [Pattern Promotion from ADRs](#pattern-promotion-from-adrs)
  - [Promotion Process](#promotion-process)
  - [Promoted Patterns](#promoted-patterns)
- [Proven Patterns](#proven-patterns)
  - [Agent Orchestration](#agent-orchestration)
    - [Assembly Line Workflow](#pattern-assembly-line-workflow)
    - [Parallel Review Execution](#pattern-parallel-review-execution)
    - [Explicit Agent File Operations](#pattern-explicit-agent-file-operations)
    - [Agent Context Preparation](#pattern-agent-context-preparation)
    - [Agent vs Manual Decision Framework](#pattern-agent-vs-manual-decision-framework)
    - [Context Window Discipline](#pattern-context-window-discipline-for-multi-agent-workflows)
  - [File Operations](#file-operations)
    - [Temp-First File Creation](#pattern-temp-first-file-creation)
  - [Documentation Workflows](#documentation-workflows)
    - [Living vs. Version Documentation](#pattern-living-vs-version-documentation)
- [Decision Frameworks](#decision-frameworks)
  - [When to Create New Files vs. Edit Existing](#when-to-create-new-files-vs-edit-existing)
  - [Workflow Phase Selection](#workflow-phase-selection)
- [Common Pitfalls](#common-pitfalls)
  - [File Path Assumptions](#file-path-assumptions)
  - [Context Loss in Agent Handoffs](#context-loss-in-agent-handoffs)
- [Best Practices](#best-practices)
  - [Version Control](#version-control)
  - [Documentation Standards](#documentation-standards)
  - [When to Create TDDs](#when-to-create-tdds)
- [Phase 1 - SRS Implementation Patterns](#phase-1---srs-implementation-patterns)
  - [Architecture Decisions That Worked](#architecture-decisions-that-worked)
    - [Vertical Slice Module Architecture](#pattern-vertical-slice-module-architecture)
    - [Schema Versioning for localStorage](#pattern-schema-versioning-for-localstorage)
  - [Security Patterns Learned](#security-patterns-learned)
    - [textContent Over innerHTML](#pattern-textcontent-over-innerhtml)
    - [Defensive Null-Checking for localStorage](#pattern-defensive-null-checking-for-localstorage)
    - [Date Parsing in Try-Catch](#pattern-date-parsing-in-try-catch)
  - [JavaScript Defensive Coding Patterns](#javascript-defensive-coding-patterns)
    - [Nullish Coalescing vs Logical OR](#pitfall-nullish-coalescing-vs-logical-or-for-defaults)
    - [Property Name Convention Mismatch](#pitfall-property-name-convention-mismatch)
    - [Browser Module Export Missing](#pitfall-browser-module-export-missing)
    - [Initialization Error Handling](#pattern-initialization-error-handling)
    - [Test Expectations Must Match Implementation](#pattern-test-expectations-must-match-implementation)
  - [Testing Approach Notes](#testing-approach-notes)
    - [Test Files Alongside Source](#pattern-test-files-alongside-source)
    - [Module Validation Before Use](#pattern-module-validation-before-use)
- [Phase 2 - Engagement Layer Patterns](#phase-2---engagement-layer-patterns)
  - [Architecture Patterns](#architecture-patterns)
    - [IIFE Module with Window Export](#pattern-iife-module-with-window-export)
    - [Schema Migration with Version Detection](#pattern-schema-migration-with-version-detection)
  - [Bug Patterns Discovered](#bug-patterns-discovered)
    - [appendChild with String Instead of Node](#bug-appendchild-with-string-instead-of-node)
    - [State Reset in Async Toggle Handler](#bug-state-reset-in-async-toggle-handler)
  - [SVG Visualization Patterns](#svg-visualization-patterns)
    - [SVG Progress Rings with stroke-dasharray](#pattern-svg-progress-rings-with-stroke-dasharray)
    - [CSS Grid for Heatmap Calendar](#pattern-css-grid-for-heatmap-calendar)
- [Workflow Enforcement Patterns](#workflow-enforcement-patterns)
  - [PR-Centric Development with Defense-in-Depth Enforcement](#pattern-pr-centric-development-with-defense-in-depth-enforcement)
  - [Phase Gate Design: Artifacts and State Verification](#pattern-phase-gate-design-artifacts-and-state-verification)
- [dbt Architecture Patterns](#dbt-architecture-patterns)
  - [Three-Layer Model Architecture](#pattern-three-layer-model-architecture)
- [dbt + uv Patterns](#dbt--uv-patterns)
  - [pyproject.toml for dbt Projects](#pattern-pyprojecttoml-for-dbt-projects)
  - [PEP 723 Script Headers](#pattern-pep-723-script-headers)
  - [Version Constraint Selection](#pattern-version-constraint-selection)
  - [Lock File Strategy](#pattern-lock-file-strategy)
- [v0.9 PM Orchestration Patterns](#v09-pm-orchestration-patterns)
  - [Architecture Decisions](#v09-architecture-decisions)
    - [Hybrid Lite Over Complex Infrastructure](#pattern-hybrid-lite-over-complex-infrastructure)
    - [Single Active Session Per Worktree](#pattern-single-active-session-per-worktree)
    - [JSON File as Coordination Layer](#pattern-json-file-as-coordination-layer)
  - [Implementation Patterns](#implementation-patterns)
    - [Atomic File Operations with Locking](#pattern-atomic-file-operations-with-locking)
    - [DRY Abstraction with updateSession Pattern](#pattern-dry-abstraction-with-updatesession-pattern)
    - [Schema Validation with AJV](#pattern-schema-validation-with-ajv)
  - [Testing Strategy Patterns](#testing-strategy-patterns)
    - [Unit Tests for State Machine Operations](#pattern-unit-tests-for-state-machine-operations)
    - [E2E Tests Without Full Integration](#pattern-e2e-tests-without-full-integration)
  - [Multi-Worktree Coordination](#multi-worktree-coordination)
    - [Shared State via Temp Directory](#pattern-shared-state-via-temp-directory)
    - [Cross-Worktree Visibility via API](#pattern-cross-worktree-visibility-via-api)

---

## Pattern Promotion from ADRs

Patterns in this document may originate from Architecture Decision Records (ADRs). When an ADR pattern is validated in 2+ implementations, it becomes a candidate for promotion here.

### Promotion Process

1. **Identification**: Sage reviews completed features for ADR patterns with 2+ implementations
2. **Validation**: Pattern confirmed as reusable (not context-specific)
3. **Promotion**: Pattern added to appropriate LEARNINGS.md section
4. **Cross-Reference**: LEARNINGS entry includes "Validated by: ADR-N" reference
5. **Index Update**: ADR_INDEX.md marks ADR as "Promoted to LEARNINGS.md"

### Promoted Patterns

| Pattern | Source ADR | Validated In | Promoted |
|---------|------------|--------------|----------|
| Three-Layer Model Architecture | [ADR-2](../specs/TDD-001-DBT-PROJECT-ARCHITECTURE.md#adr-2-three-layer-model-architecture) | v0.3 (9 staging), v0.4 (11 models), v0.5 (7 analytics) | 2026-01-31 |
| Hybrid Lite Over Complex Infrastructure | [ADR-001](../decisions/ADR-001-backlog-md-adoption.md), [ADR-002](../decisions/ADR-002-sqlite-state-layer.md) (superseded) | v0.9 PM Orchestration | 2026-02-01 |
| JSON File as Coordination Layer | [TDD-022 ADR-15](../specs/TDD-022-PM-ORCHESTRATION-HYBRID-LITE.md#adr-15-session-tracking-via-json-file) | v0.9 PM Sessions | 2026-02-01 |

---

## Proven Patterns

### Agent Orchestration

_Patterns for effective multi-agent workflows._

#### Pattern: Assembly Line Workflow

**When to apply**: Feature development requiring multiple specialized personas

**Proven in**: v0.1 content migration, v0.2 kanji module

**Description**: Chain specialized personas sequentially, each completing their phase before handoff.

**Process**:

1. PM defines requirements → PRD
2. Architect designs solution → TDD
3. Developer implements → Code
4. Tester verifies → Test results
5. Reviewers validate → Review feedback
6. Documenter archives → Updated docs

**Benefits**:

- Clear separation of concerns
- Reduced context switching
- Quality gates at each phase

**Gotchas**:

- Overhead for small tasks (use manual approach for <3 files)
- Requires discipline to wait for handoffs

**See also**:

- Skill: `.claude/skills/orchestrate-workflow.md`
- FOR_CHRIS: `archive/FOR_CHRIS_docs/agent-orchestration-comparison.md`

---

#### Pattern: Parallel Review Execution

**When to apply**: Post-implementation quality checks

**Proven in**: v0.1 review phase, v0.2 kanji review

**Description**: Run multiple independent review personas simultaneously (Code Reviewer, Design Reviewer, Security Reviewer) to reduce total time.

**Benefits**:

- Faster feedback cycle
- Independent perspectives
- Parallelizable work

**When NOT to use**:

- Reviews have dependencies (sequence them)
- Reviewers need to see each other's feedback

**See also**:

- Command: `/review`

---

#### Pattern: Explicit Agent File Operations

**When to apply**: Delegating tasks to agents that must produce files

**Proven in**: T1.1 schema design, v0.3 agent-based implementations

**Description**: When using Task tool to spawn agents, explicitly specify file deliverables and verification steps. Agents may return content instead of writing files unless instructed otherwise.

**Problem**: Agents spawned via Task tool can use Write/Bash but may choose to return output rather than persist files.

**Solution**:

```markdown
Task: Design the localStorage schema

Deliverables (agent MUST write these files):
1. temp/schema.js - The schema file
2. temp/schema-doc.md - Design documentation

Verification before returning:
- Run: ls -la temp/ (confirm files exist)
- Run: node temp/schema.js (should not error)
- Return paths to created files
```

**Key principles**:

1. **Be explicit about outputs** - List exact file paths
2. **Include verification steps** - Agent confirms files exist
3. **Specify tools to use** - "Use Write tool for X, Bash for Y"
4. **Don't assume** - Some agents prefer returning content

**Benefits**:

- Prevents lost work (agent returns content, doesn't persist)
- Clear success criteria
- Reproducible workflows

**When NOT to use**:

- Manual/direct work (no agent delegation)
- Agent returning content is acceptable (analysis, recommendations)

**See also**:

- FOR_CHRIS: `archive/FOR_CHRIS_docs/agent-orchestration-comparison.md` - Full T1.1 case study
- `.claude/agents/AGENTS.md` - Agent handoff best practices

---

#### Pattern: Agent Context Preparation

**When to apply**: Before delegating work to any agent

**Proven in**: T1.1 schema design, T1.2 SM-2 implementation, v0.3 agent workflows

**Description**: Agents need explicit context to avoid redesigning from scratch or conflicting with existing decisions. Always provide links to relevant docs, previous work, and constraints.

**Problem**: Agent lacks context and produces work that conflicts with existing architecture or repeats previous decisions.

**Solution**:

```javascript
Task({
  prompt: `You are the architect for Task T1.2 (GitHub #14).

  IMPORTANT: First read these files for context:
  1. temp/kanji-storage-schema.js - Schema you'll implement
  2. docs/specs/PRD-001-JLPT-Mastery-Engine.md - Requirements
  3. temp/T1.1-SCHEMA-DESIGN-DOC.md - Previous design decisions

  Your task: Implement SM-2 algorithm based on the schema.

  Deliverables:
  1. kanji/js/srs-engine.js - SM-2 implementation
  2. temp/T1.2-TESTING.md - Test plan

  Use Write tool to create files.`,
  subagent_type: "everything-claude-code:architect"
})
```

**Key elements to provide**:

1. **Role**: "You are the [architect/developer/reviewer]"
2. **Task ID**: Link to GitHub issue for acceptance criteria
3. **Context files**: List files agent should read first
4. **Previous work**: Point to related completed tasks
5. **Constraints**: File naming, dependencies, structure requirements
6. **Deliverables**: Exact file paths to create

**Benefits**:

- Prevents conflicting with existing decisions
- Avoids redesigning from scratch
- Ensures consistency across tasks
- Reduces back-and-forth clarifications

**When NOT to use**:

- Self-contained tasks with no dependencies
- Exploratory research with no constraints

**See also**:

- `.claude/agents/AGENTS.md#agent-handoff-best-practices` - Full handoff protocol
- Pattern: "Explicit Agent File Operations" (deliverables specification)

---

#### Pattern: Agent vs Manual Decision Framework

**When to apply**: Deciding whether to use an agent or work manually

**Proven in**: All versions v0.1-v0.3, T1.1-T1.2 task selection

**Description**: Not every task benefits from agent delegation. Simple tasks are faster and clearer when done manually. Use agents for complexity, manual for simplicity.

**Decision criteria**:

| Task Characteristic | Approach | Reason |
|---------------------|----------|--------|
| < 3 file changes | **Manual** | Agent overhead > benefit |
| Single obvious fix | **Manual** | Faster to just fix it |
| Typo or formatting | **Manual** | Too simple for delegation |
| Complex logic/algorithm | **Agent** | Needs specialized expertise |
| Multi-file architecture | **Agent** | Systematic approach needed |
| Security-sensitive code | **Agent** | Specialized security knowledge |
| Exploratory research | **Agent** | Thorough codebase analysis |

**Examples**:

```markdown
✅ MANUAL:
- Fix typo in README
- Update single CSS rule
- Add console.log for debugging
- Rename variable

✅ AGENT:
- Design authentication architecture
- Implement SM-2 algorithm
- Security audit of API endpoints
- Comprehensive code review
- Explore unfamiliar codebase structure
```

**Rule of thumb**:

- If you can describe the exact change in <2 sentences → Manual
- If you need to say "design," "architect," or "analyze" → Agent

**Benefits of following framework**:

- Faster turnaround on simple tasks
- Better use of agent capabilities on complex work
- Reduced cognitive overhead deciding
- Clearer team communication

**Gotchas**:

- Don't use agents for "quick tweaks" (agent overhead > manual time)
- Don't skip agents for "seems easy" complex logic (bugs likely)

**See also**:

- `.claude/agents/AGENTS.md#when-to-use-agents` - Full agent selection guide
- `.claude/agents/AGENTS.md#agent-selection-guide` - Agent type selection

---

#### Pattern: Context Window Discipline for Multi-Agent Workflows

**When to apply**: Any multi-agent orchestration where agents hand off work

**Proven in**: v0.6 PRD-016 Agent Context Management, Claudie blog post (external validation)

**Description**: Orchestrators should pass file pointers, not content summaries. Sub-agents write to shared folders; downstream agents read directly. This preserves signal fidelity and reduces context window overhead in the orchestrator.

**Problem**: When orchestrators (like Supervisor) relay summarized content between agents:

1. Context window overflow in orchestrator
2. Signal degradation - nuances lost in summarization
3. Information bottleneck - downstream agents get filtered view
4. Repeated context loading across agent invocations

**Solution**: Shared artifact folder pattern

```
temp/AGENT_REPORTS/[feature]/
├── PM_REPORT.md          ← PM writes scope, decisions
├── ARCH_REPORT.md        ← Architect reads PM, writes design
├── TEST_SPEC.md          ← Tester reads ARCH, writes tests
├── DEV_REPORT.md         ← Developer reads all, writes implementation
├── CODE_REVIEW.md        ← Reviewer reads DEV, writes findings
└── SECURITY_REVIEW.md    ← Security reads DEV, writes assessment
```

**Delegation pattern**:

```text
# Instead of:
pm: Create PRD for customer analytics. [includes all context in message]

# Use:
pm: Create PRD for customer analytics.
    - Write PM_REPORT.md to: temp/AGENT_REPORTS/customer-analytics/
    - PRD location: docs/specs/PRD-XXX-CUSTOMER-ANALYTICS.md
```

**Downstream agent pattern**:

```text
arch: Design feature per PRD-XXX.
    - Read: temp/AGENT_REPORTS/customer-analytics/PM_REPORT.md
    - Write: temp/AGENT_REPORTS/customer-analytics/ARCH_REPORT.md
```

**Key principles**:

1. **Orchestrator passes paths, not content**: "Read PM_REPORT.md at [path]"
2. **Each agent writes to shared folder**: Creates permanent artifact
3. **Downstream reads upstream directly**: Full context, no relay loss
4. **Supervisor verifies reports exist**: Phase transition requires artifact

**Benefits**:

- Preserves signal fidelity across handoffs
- Reduces orchestrator context window usage
- Creates audit trail of agent decisions
- Enables session resume via report reading

**When NOT to use**:

- Simple tasks that don't need orchestration
- Single-agent work with no handoffs
- Ad-hoc questions (no workflow state needed)

**See also**:

- PRD: `docs/specs/PRD-016-AGENT-CONTEXT-MANAGEMENT.md`
- TDD: `docs/specs/TDD-016-AGENT-CONTEXT-MANAGEMENT.md`
- Templates: `docs/templates/agent-reports/`
- Pitfall: "Context Loss in Agent Handoffs" (below)

---

### File Operations

_Patterns for safe and effective file manipulation._

#### Pattern: Temp-First File Creation

**When to apply**: Creating or significantly modifying content files

**Proven in**: v0.1 content migration, v0.2 data generation

**Description**: Always create new versions in `temp/` directory first, test thoroughly, then move to final location with approval.

**Process**:

1. Create new file in `temp/[filename]`
2. Test functionality completely
3. Get user approval
4. Archive old version (if exists) to `archive/v[X.Y]/`
5. Move approved file to final location
6. Clean temp (with explicit approval)

**Benefits**:

- No accidental overwrites
- Easy rollback
- Clear approval checkpoint

**Anti-pattern**:

- Direct overwrite of working files
- Skipping temp directory for "small changes"

**See also**:

- CLAUDE.md: File Protection section
- Workflow: Standard Workflow → PROTOTYPE Phase

---

### Documentation Workflows

_Patterns for maintaining accurate, useful documentation._

#### Pattern: Living vs. Version Documentation

**When to apply**: Always - determines where documentation lives

**Proven in**: All versions

**Description**: Separate documentation into two categories with different update patterns.

**Living Docs** (always current):

- `docs/ARCHITECTURE.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/DESIGN_PRINCIPLES.md`
- Update: Whenever patterns change

**Version Docs** (point-in-time):

- `temp/v[X.Y]_PLAN.md`
- `temp/v[X.Y]_TESTING.md`
- Update: During that version only, then archive

**Decision criteria**:

- Will this information change in future versions? → Living doc
- Is this specific to this version's decisions? → Version doc

**See also**:

- CLAUDE.md: Documentation Strategy

---

## Decision Frameworks

### When to Create New Files vs. Edit Existing

**Context**: Deciding whether to modify an existing file or create a new one.

**Decision tree**:

1. **Is this a new topic/feature?**
   - Yes → Create new file with descriptive name
   - No → Continue to step 2

2. **Does the existing file structure support this addition?**
   - Yes → Edit existing file
   - No → Continue to step 3

3. **Would editing make the file too long/complex?**
   - Yes → Split into new files
   - No → Edit existing file

**Examples**:

- New kanji study mode → New file `kanji/index.html`
- Adding kanji to existing data → Edit `kanji/data/kanji-data.js`
- New topic (cooking) → New directory `topics/cooking/`
- Adding dialogue to existing topic → Edit or create based on file length

**Proven in**: v0.1 (topic organization), v0.2 (kanji module separation)

---

### Workflow Phase Selection

**Context**: Determining which workflow phases to execute for a given task.

**Full workflow phases**:

1. UNDERSTAND → 2. PLAN → 3. PROTOTYPE → 4. BUILD → 5. VERIFY → 6. DEPLOY

**Decision criteria**:

| Task Type | Phases | Rationale |
|-----------|--------|-----------|
| New feature (multi-file) | All 6 | Full rigor needed |
| Bug fix (complex) | UNDERSTAND → PLAN → BUILD → VERIFY → DEPLOY | Skip prototype if fix is clear |
| Bug fix (typo) | BUILD → VERIFY | Small, obvious change |
| Documentation update | UNDERSTAND → BUILD → VERIFY | No prototype needed for docs |
| Refactoring | UNDERSTAND → PLAN → PROTOTYPE → BUILD → VERIFY | Prototype to validate approach |

**Rule**: When in doubt, use full workflow. Better safe than sorry.

**See also**:

- `docs/WORKFLOW_EXCEPTIONS.md` - Approved shortcuts
- CLAUDE.md: Standard Workflow section

---

## Common Pitfalls

### File Path Assumptions

**Pitfall**: Assuming file paths without verification

**Symptom**: "File not found" errors, wrong files modified

**Example**:

```javascript
// WRONG - Assumes directory structure
const data = require('../../../data/kanji.json');

// BETTER - Verify path first (use ls/glob)
// Then use confirmed path
```

**Prevention**:

1. Use `ls` to verify parent directory exists before creating nested files
2. Use `glob` to find files by pattern rather than guessing paths
3. Read existing files to understand current structure

**Proven failures**: Early v0.1 migrations, v0.2 data file locations

**See also**:

- `.claude/rules/coding-style.md` - File Organization

---

### Context Loss in Agent Handoffs

**Pitfall**: Losing critical context when switching between agents

**Symptom**: Agent repeats work, misses requirements, asks questions already answered

**Causes**:

- Not reading prior conversation/artifacts
- Insufficient handoff summary
- Missing artifact links

**Prevention**:

1. Each agent reads previous persona's output before starting
2. Handoff includes:
   - Summary of completed work
   - Open questions/blockers
   - Links to artifacts produced
3. Use explicit artifact references (file paths, line numbers)

**Example handoff**:

```markdown
## Handoff to Developer

**Completed**: PRD created in docs/specs/PRD-kanji-filter.md

**Requirements**: JLPT level filter with N5-N2 support

**TDD**: See docs/specs/TDD-kanji-filter.md lines 45-67 for component design

**Blockers**: None

**Next steps**: Implement KanjiFilter component per TDD
```

**Proven failures**: v0.1 assembly line early iterations

**See also**:

- `.claude/agents/AGENTS.md` - Handoff Protocol section

---

## Best Practices

### Version Control

**Practice**: Git tagging for version milestones

**Why**: Creates immutable restore points, enables easy rollback

**How**:

```bash
# After merging version PR
git tag -a v0.3.0 -m "Complete kanji study module"
git push origin v0.3.0
```

**When**:

- After significant feature completion
- At planned version milestones
- Before major refactoring (safety checkpoint)

**Benefits**:

- Easy checkout of specific versions: `git checkout v0.3.0`
- Clear history of releases
- Rollback safety net

**Proven in**: All versions since v0.1

**See also**:

- `.claude/rules/git-workflow.md` - Versioning section

---

### Documentation Standards

**Practice**: Version stamps in modified files

**Why**: Quickly identify file currency and version association

**How**:

```html
<!-- Version: v0.3.0 - Updated: 2026-01-25 -->
```

**Where**:

- Top of HTML files
- Top of CSS files (as comment)
- Top of JavaScript files (as comment)

**Update when**:

- File is modified as part of versioned work
- Not needed for every minor change (use judgment)

**Proven in**: v0.1+ (established as standard)

**See also**:

- `.claude/rules/coding-style.md` - HTML Standards

---

### When to Create TDDs

**Practice**: TDD-First for complex features

**Why**: Prevents ambiguity, enables traceability (Task → TDD Section → PRD → User need), separates "what/why" (PM) from "how" (Architect)

**Create TDDs for**:

- New features with complex logic (SRS algorithms, state machines)
- New data models (schemas, validation rules)
- Features affecting multiple files
- Architectural decisions with trade-offs

**Skip TDDs for**:

- Documentation updates
- Simple UI tweaks (<50 lines)
- Bug fixes (unless architectural)
- Content additions following existing patterns

**Reference pattern**:

```
Task description: "Implement localStorage layer per TDD-001 §2"
(Points to specific section of TDD)
```

**Benefits**:

- No ambiguity for developers ("how" is specified)
- Traceability across artifacts
- Reusability (multiple tasks reference same section)
- Quality gate before implementation

**Proven in**: v0.3 Epic → TDD → Task workflow, PRD-001 → TDD-001 → Tasks #13-23

**See also**:

- `docs/guides/PROJECT_WORKFLOW.md` - Epic → TDD → Task pattern
- Session: `temp/SESSION-2026-01-25-WORKFLOW-OPTIMIZATION.md`

---

## Usage Guidelines

### Adding New Learnings

**Quality bar**:

- ✅ Pattern proven in ≥2 real implementations
- ✅ Real examples from this codebase
- ✅ Clear "when to apply" guidance
- ✅ Cross-references to related docs/skills

**Process**:

1. Sage identifies pattern during session curation
2. Validates pattern meets quality bar
3. Chooses appropriate section (Patterns/Frameworks/Pitfalls/Practices)
4. Writes entry with examples and cross-references
5. Updates this Table of Contents

**Format**:

```markdown
#### Pattern: [Name]

**When to apply**: Context/trigger

**Proven in**: v0.X, v0.Y

**Description**: What it is

**Process/Benefits/Gotchas**: Details

**See also**: Links
```

### Cross-Referencing

**Single-source-of-truth hierarchy**:

1. If pattern is executable workflow → Create skill in `.claude/skills/`
2. If pattern is technical insight → Document here in LEARNINGS.md
3. If pattern has high educational value → Create FOR_CHRIS doc

**Always link between tiers**:

- LEARNINGS → Link to related skills
- FOR_CHRIS → Link to LEARNINGS and skills
- Skills → Reference from LEARNINGS

**Never duplicate** - Use cross-references instead.

---

---

## Phase 1 - SRS Implementation Patterns

_Learnings from the JLPT Mastery Engine Phase 1 implementation (SM-2 algorithm, storage layer, mastery calculations)._

### Architecture Decisions That Worked

#### Pattern: Vertical Slice Module Architecture

**When to apply**: Building self-contained feature modules

**Proven in**: Phase 1 JLPT Mastery Engine (kanji module)

**Description**: Each module is self-contained with clear responsibilities, explicit dependencies, and browser exports via `window.ModuleName` pattern.

**Module structure**:

```
content/kanji/js/
├── srs-engine.js       # SM-2 algorithm (568 lines)
├── storage.js          # localStorage CRUD + validation
├── mastery-calculator.js # JLPT/topic aggregation
└── session-manager.js  # Queue building + session orchestration
```

**Key characteristics**:

1. **Single responsibility**: Each module owns one concern
2. **Explicit dependencies**: JSDoc header lists dependencies
3. **Browser exports**: `window.ModuleName = { ... }` pattern
4. **Graceful fallbacks**: Modules check for dependencies before using

**Example pattern** (from mastery-calculator.js):

```javascript
function getStageMasteryScore(stage) {
  // Try to use srs-engine.js function if available
  if (typeof window !== 'undefined' && window.SRSEngine && window.SRSEngine.getStageMasteryScore) {
    return window.SRSEngine.getStageMasteryScore(stage);
  }
  return STAGE_MASTERY_SCORES[stage] || 0;
}
```

**Benefits**:

- Clear ownership and testability
- Can be loaded independently for testing
- Graceful degradation when dependencies missing

---

#### Pattern: Schema Versioning for localStorage

**When to apply**: Any localStorage persistence that may evolve

**Proven in**: Phase 1 storage.js

**Description**: Include schema version in stored data for future migrations.

**Implementation**:

```javascript
const SCHEMA_VERSION = '1.0.0';  // Semver format

function createDefaultSchema() {
  return {
    version: SCHEMA_VERSION,
    kanji: {},
    settings: { ... },
    stats: { ... },
    metadata: {
      created: new Date().toISOString(),
      last_modified: new Date().toISOString(),
      migration_count: 0
    }
  };
}
```

**Benefits**:

- Enables future data migrations
- Clear audit trail of data age
- Can detect and handle version mismatches

---

### Security Patterns Learned

#### Pattern: textContent Over innerHTML

**When to apply**: All dynamic content rendering

**Proven in**: Phase 1 code review finding

**Problem**: XSS vulnerability from innerHTML with untrusted data.

**Solution**:

```javascript
// DANGEROUS - allows XSS
element.innerHTML = kanji.character;

// SAFE - escapes content
element.textContent = kanji.character;

// SAFE - DOM construction for complex content
const el = document.createElement('ruby');
el.textContent = kanji.character;
const rt = document.createElement('rt');
rt.textContent = kanji.reading;
el.appendChild(rt);
```

**Rule**: Use `textContent` for text, DOM construction for structure. Reserve `innerHTML` only for trusted static content.

---

#### Pattern: Defensive Null-Checking for localStorage

**When to apply**: Any localStorage reads

**Proven in**: Phase 1 storage.js validation layer

**Problem**: Corrupted or tampered localStorage data can crash the app.

**Solution**: Comprehensive validation before use:

```javascript
function loadSchema() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw === null) return null;  // First-time user

    let schema;
    try {
      schema = JSON.parse(raw);
    } catch (e) {
      throw new Error(`Corrupted localStorage: ${e.message}`);
    }

    const validation = validateSchema(schema);
    if (!validation.valid) {
      // Log warnings, throw on critical errors
    }

    return schema;
  } catch (error) {
    console.error('Failed to load schema:', error);
    throw error;
  }
}
```

**Key validation layers**:

1. Null check (first-time user)
2. JSON.parse in try-catch
3. Schema structure validation
4. Field-level validation (types, ranges, enums)

---

#### Pattern: Date Parsing in Try-Catch

**When to apply**: Any date calculations with stored/external data

**Proven in**: Phase 1 streak calculation code review

**Problem**: Invalid date strings cause calculation errors and break the app.

**Solution**:

```javascript
function updateStreak(schema) {
  try {
    const lastDate = new Date(lastStudy);
    const todayDate = new Date(today);

    // Validate date objects
    if (isNaN(lastDate.getTime()) || isNaN(todayDate.getTime())) {
      console.error('Invalid date, resetting streak');
      schema.stats.streak_days = 1;
      return;
    }

    // Safe to proceed with calculation
    const diffDays = Math.floor((todayDate - lastDate) / (24 * 60 * 60 * 1000));
    // ...
  } catch (error) {
    console.error('Error in streak calculation:', error);
    // Reset to safe default
    schema.stats.streak_days = 1;
  }
}
```

**Key principle**: Date operations should never crash the app - always have a fallback.

---

### JavaScript Defensive Coding Patterns

_Bug prevention patterns from Phase 1 browser testing._

#### Pitfall: Nullish Coalescing vs Logical OR for Defaults

**When to apply**: Any code using default values with `||` operator

**Proven in**: Phase 1 JLPT sorting bug (v0.3)

**Problem**: JavaScript's `||` operator treats `0`, `""`, and `false` as falsy, using the fallback even when the value is intentionally zero.

**Bug example**:

```javascript
// JLPT level sort order: N5=0, N4=1, N3=2, N2=3, N1=4
const jlptOrder = { 'N5': 0, 'N4': 1, 'N3': 2, 'N2': 3, 'N1': 4 };

// BUG: N5 kanji (value 0) falls back to 5, sorting last!
const sortValue = jlptOrder[kanji.jlpt_level] || 5;

// FIX: Nullish coalescing only falls back for null/undefined
const sortValue = jlptOrder[kanji.jlpt_level] ?? 5;
```

**Rule**: Use `??` when the default should only apply for `null`/`undefined`. Use `||` when any falsy value should trigger the fallback.

**Quick reference**:

| Operator | Triggers fallback for |
|----------|----------------------|
| `||` | `null`, `undefined`, `0`, `""`, `false`, `NaN` |
| `??` | `null`, `undefined` only |

**See also**: MDN docs on [Nullish coalescing operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)

---

#### Pitfall: Property Name Convention Mismatch

**When to apply**: Multi-module JavaScript with shared interfaces

**Proven in**: Phase 1 dashboard stats bug (v0.3)

**Problem**: Module A uses camelCase properties, Module B returns snake_case - causes silent failures where values are `undefined`.

**Bug example**:

```javascript
// session-manager.js returns snake_case
getQueueStatus() {
  return {
    due_count: queue.due.length,      // snake_case
    new_available: queue.new.length
  };
}

// dashboard.js expected camelCase - BUG!
const status = SessionManager.getQueueStatus();
updateDisplay(status.dueCount);       // undefined - shows 0
updateDisplay(status.newAvailable);   // undefined - shows 0
```

**Prevention strategies**:

1. **Document module interfaces** - JSDoc with exact property names
2. **TypeScript/JSDoc types** - Catch mismatches at "compile" time
3. **Console.log the actual object** - First debugging step
4. **Establish project convention** - Pick one (snake_case or camelCase) and enforce

**Project convention** (for this codebase):

- **Internal JavaScript**: camelCase (`dueCount`, `newAvailable`)
- **Data files/JSON**: snake_case (`jlpt_level`, `stroke_count`)
- **Module interfaces**: Document explicitly in JSDoc header

**Detection checklist**:

- [ ] Values showing as `0`, `undefined`, or `NaN` unexpectedly?
- [ ] Console.log the object - do property names match what you expect?
- [ ] Check both producer and consumer modules for naming convention

---

#### Pitfall: Browser Module Export Missing

**When to apply**: JavaScript modules intended for browser use (not Node.js)

**Proven in**: Phase 1 kanji dashboard (v0.3)

**Problem**: Using `const ModuleName = {...}` does NOT create `window.ModuleName` in browsers. Only `var` at global scope or explicit assignment creates window properties.

**Bug example**:

```javascript
// kanji-metadata.js - BROKEN
const homeLifeKanji = [
  { character: '家', jlpt_level: 'N4' },
  // ...
];
// window.homeLifeKanji is undefined!

// FIX: Explicit window export
const homeLifeKanji = [
  { character: '家', jlpt_level: 'N4' },
  // ...
];
window.homeLifeKanji = homeLifeKanji;  // Now accessible
```

**Prevention strategies**:

1. **Always add explicit exports** for browser modules: `window.ModuleName = ModuleName`
2. **Verify in console**: After loading script, check `window.ModuleName` exists
3. **Use Module pattern with explicit export**:

   ```javascript
   const MyModule = (function() {
     // private code
     return { publicMethod };
   })();
   window.MyModule = MyModule;
   ```

**Detection checklist**:

- [ ] Does the script define variables/objects for other modules to use?
- [ ] Are those variables accessible via `window.varName` in browser console?
- [ ] Does the consuming code check for undefined before using?

**See also**:

- `.claude/skills/learned-pattern-javascript-defensive-coding.md#pattern-4`
- MDN: [var vs let vs const](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/let)

---

#### Pattern: Initialization Error Handling

**When to apply**: Any module initialization code that runs on page load

**Proven in**: Phase 1 dashboard initialization (v0.3)

**Problem**: Initialization errors fail silently without try-catch, making debugging extremely difficult.

**Bug example**:

```javascript
// BROKEN: Silent failure
function loadOrCreateSchema() {
  const schema = Storage.loadSchema();  // If this throws, page breaks silently
  if (!schema) {
    schema = Storage.createDefaultSchema();
  }
  return schema;
}

// FIX: Comprehensive error handling
function loadOrCreateSchema() {
  try {
    console.log('Loading schema...');
    const schema = Storage.loadSchema();

    if (!schema) {
      console.log('No existing schema, creating default...');
      const newSchema = Storage.createDefaultSchema();
      console.log('Created schema:', newSchema);
      return newSchema;
    }

    console.log('Loaded existing schema:', schema);
    return schema;
  } catch (error) {
    console.error('Failed to load/create schema:', error);
    // Provide useful error info, don't just fail silently
    throw error;  // Re-throw for visibility OR return safe default
  }
}
```

**Key principles**:

1. **Log before critical operations**: `console.log('Attempting X...')`
2. **Log success with data**: `console.log('Loaded:', data)`
3. **Catch and log errors with context**: Include function name, operation, and error
4. **Decide: fail or fallback**: Either re-throw for visibility or return safe default

**When to add comprehensive logging**:

- Module initialization
- localStorage operations
- Cross-module calls
- Data parsing (JSON, dates)

**See also**:

- `.claude/skills/learned-pattern-javascript-defensive-coding.md#pattern-5`
- Pattern: "Defensive Null-Checking for localStorage"

---

#### Pattern: Test Expectations Must Match Implementation

**When to apply**: Writing or debugging test assertions

**Proven in**: Phase 1 SRS stage transition test (v0.3)

**Problem**: Test expects wrong value based on incorrect mental model of the implementation.

**Bug example**:

```javascript
// Implementation: AGAIN from guru_1 drops 2 stages
// Stages: apprentice_1(0), apprentice_2(1), apprentice_3(2), apprentice_4(3), guru_1(4)
// guru_1 (index 4) - 2 = index 2 = apprentice_3

// BUG: Test expected apprentice_4 (wrong assumption)
expect(result.stage).toBe('apprentice_4');

// FIX: Correct expectation based on actual indexing
expect(result.stage).toBe('apprentice_3');
```

**Prevention strategies**:

1. **Trace through implementation manually** - Calculate expected value by hand
2. **Test the test** - Verify test fails for wrong reasons initially
3. **Add comments explaining calculation** - Future maintainers understand the math
4. **Use constants from implementation** - `STAGES[STAGES.indexOf('guru_1') - 2]`

**Rule**: When a test fails, verify the expectation is correct before assuming the implementation is wrong.

---

### Testing Approach Notes

#### Pattern: Test Files Alongside Source

**When to apply**: JavaScript modules with testable logic

**Proven in**: Phase 1 module structure

**Description**: Place test files in the same directory as source files for discoverability.

**Structure**:

```
content/kanji/js/
├── srs-engine.js
├── srs-engine.test.js
├── storage.js
├── storage.test.js
└── ...
```

**Benefits**:

- Easy to find tests for any module
- Encourages test writing
- Clear 1:1 mapping

---

#### Pattern: Module Validation Before Use

**When to apply**: Modules with external dependencies

**Proven in**: Phase 1 session-manager.js

**Problem**: Calling undefined module methods causes runtime errors.

**Solution**: Check module availability before use:

```javascript
function processSessionReview(schema, kanji, quality, responseTimeMs) {
  // Validate module is available
  if (typeof window !== 'undefined' && window.SRSEngine && window.SRSEngine.processReview) {
    return window.SRSEngine.processReview(kanji, quality, responseTimeMs);
  } else {
    throw new Error('SRSEngine not available');
  }
}
```

**Pattern variants**:

1. **Throw**: For required dependencies (above)
2. **Fallback**: For optional dependencies (use local implementation)
3. **No-op**: For optional features (skip silently)

---

## Phase 2 - Engagement Layer Patterns

_Learnings from the Phase 2 Engagement Layer implementation (XP/Levels, Streaks, Goals, Dashboard Visualizations)._

### Architecture Patterns

#### Pattern: IIFE Module with Window Export

**When to apply**: Browser-only JavaScript modules that need to be accessed across files

**Proven in**: Phase 2 xp-engine.js, streak-manager.js, goals-manager.js, dashboard-visualizations.js

**Description**: Use IIFE (Immediately Invoked Function Expression) pattern with explicit window export for browser compatibility, plus CommonJS export for Node.js testing.

**Implementation**:

```javascript
const ModuleName = (function() {
  'use strict';

  // Private implementation...

  return {
    // Public API
  };
})();

// Export for browser
if (typeof window !== 'undefined') {
  window.ModuleName = ModuleName;
}

// Export for Node.js testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ModuleName;
}
```

**Benefits**:

- Works in browser without build tools
- Testable in Node.js
- Clear public API
- Encapsulated private state

#### Pattern: Schema Migration with Version Detection

**When to apply**: localStorage schema changes that need backward compatibility

**Proven in**: Phase 2 storage.js (v1.0.0 → v1.1.0)

**Description**: Detect schema version on load, run migrations sequentially, update version stamp.

**Implementation**:

```javascript
function loadSchema() {
  const schema = JSON.parse(localStorage.getItem(KEY));
  if (!schema) return createDefault();

  // Migrate if needed
  if (schema.version === '1.0.0') {
    schema = migrateV1_0_to_V1_1(schema);
  }

  return schema;
}

function migrateV1_0_to_V1_1(schema) {
  // Add new fields with defaults
  schema.stats.xp = schema.stats.xp || { total: 0, level: 1 };
  schema.stats.streak = schema.stats.streak || { current: 0 };
  schema.version = '1.1.0';
  return schema;
}
```

**Benefits**:

- Non-destructive upgrades
- Preserves user data
- Supports skipped versions

### Bug Patterns Discovered

#### Bug: appendChild with String Instead of Node

**Symptom**: `TypeError: Failed to execute 'appendChild' on 'Node': parameter 1 is not of type 'Node'`

**Proven in**: Phase 2 trend line rendering bug

**Root Cause**: Function returns HTML string but code expects DOM Node.

**Fix**: Use `innerHTML` for string markup, `appendChild` only for DOM nodes.

```javascript
// WRONG - createTrendLine returns string
const trendSVG = DashViz.createTrendLine(snapshots);
container.appendChild(trendSVG);  // Error!

// CORRECT
const trendMarkup = DashViz.createTrendLine(snapshots);
container.innerHTML = trendMarkup;
```

**Prevention**: Check JSDoc `@returns` type before using function result.

#### Bug: State Reset in Async Toggle Handler

**Symptom**: Toggle flips back to OFF after async permission request succeeds

**Proven in**: Phase 2 notification toggle bug

**Root Cause**: `updateUI()` reads saved settings (not yet saved) and resets toggle state.

**Fix**: Don't call full UI update in toggle handler; manually update only changed elements.

```javascript
// WRONG
async function handleToggle() {
  const granted = await requestPermission();
  updateUI();  // Resets toggle to saved state!
}

// CORRECT
async function handleToggle() {
  const granted = await requestPermission();
  if (granted) {
    elements.toggle.checked = true;  // Keep checked
    elements.status.textContent = 'Enabled';
  }
}
```

**Prevention**: Trace what UI update functions read vs. what's been saved.

### SVG Visualization Patterns

#### Pattern: SVG Progress Rings with stroke-dasharray

**When to apply**: Circular progress indicators

**Proven in**: Phase 2 topic mastery rings

**Description**: Use SVG circle with `stroke-dasharray` to create partial rings.

**Implementation**:

```javascript
const circumference = 2 * Math.PI * radius;
const offset = circumference * (1 - percentage / 100);

return `
  <circle
    r="${radius}"
    stroke-dasharray="${circumference}"
    stroke-dashoffset="${offset}"
    transform="rotate(-90)"
  />
`;
```

#### Pattern: CSS Grid for Heatmap Calendar

**When to apply**: GitHub-style activity calendars

**Proven in**: Phase 2 study heatmap

**Description**: Use CSS Grid with 7 rows (days) × 53 columns (weeks).

**Implementation**:

```css
.heatmap-grid {
  display: grid;
  grid-template-rows: repeat(7, 12px);
  grid-auto-flow: column;
  gap: 3px;
}
```

---

## Workflow Enforcement Patterns

_Learnings from the v0.5 PR workflow bypass incident and defense-in-depth enforcement design._

### Pattern: PR-Centric Development with Defense-in-Depth Enforcement

**When to apply**: Any project with multi-stage workflows (planning, implementation, review, deploy) where skipping stages has significant consequences

**Proven in**: v0.5 marts-enhancements PR workflow bypass (2026-01-30)

**Description**: Documentation-only workflow enforcement is insufficient. High-stakes workflows need defense-in-depth with multiple enforcement layers that progressively increase difficulty of bypass.

#### The Problem: Document-Only Enforcement Fails

The v0.5 implementation initially committed directly to main instead of the designated feature branch (`feat/marts-enhancements`). This happened despite:

- `V0.5_ORCHESTRATION_SUMMARY.md` explicitly documenting the branch strategy
- `v0.5_PLAN.md` specifying "Create feature branch/worktree and begin model development"
- PRD-015 requiring "draft PR creation at branch/worktree creation"

**Root cause**: The workflow documented the requirement but provided no enforcement mechanism. The phase gate verified document artifacts (PRD exists, TDD exists) but not git state (correct branch, draft PR created).

**Key insight**: Documenting "what should happen" is necessary but insufficient. The workflow assumed correct behavior rather than verifying it.

#### Defense-in-Depth Enforcement Layers

**Layer 1: Persona-Level Verification (Soft Check)**

Add explicit verification step to agent personas that will do implementation work:

```markdown
## Development Flow

1. **VERIFY GIT STATE FIRST**:
   - Run: `git branch --show-current`
   - If on `main`: STOP - invoke `git: create branch feat/[feature-name]`
   - If on feature branch: proceed
```

Benefits: Quick catch during normal workflow, no tooling required
Weakness: Relies on agent compliance, easily skipped under pressure

**Layer 2: Supervisor Phase Gate (Soft Enforcement)**

Add git state to Supervisor's artifact verification matrix:

| Transition | Required Artifacts | Git State Check |
|------------|-------------------|-----------------|
| Tester -> Developer | Test spec exists | `git branch --show-current != main` |
| Developer -> Reviewer | Implementation complete | Draft PR exists for branch |

Benefits: Explicit checkpoint before implementation phase
Weakness: Still soft - can be overridden by operator

**Layer 3: Pre-Commit Hook (Hard Local Enforcement)**

Install git hook that blocks commits to protected branches:

```bash
#!/bin/bash
# .git/hooks/pre-commit
branch=$(git branch --show-current)
if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
    echo "ERROR: Direct commits to main are blocked."
    echo "Create a feature branch first: git checkout -b feat/your-feature"
    exit 1
fi
```

Benefits: Prevents the action at the moment of attempt
Weakness: Local-only, can be bypassed with --no-verify

**Layer 4: Pre-Push Hook (Hard Local Enforcement)**

Block pushes of direct commits to protected branches:

```bash
#!/bin/bash
# .git/hooks/pre-push
while read local_ref local_sha remote_ref remote_sha; do
    if [[ "$remote_ref" == "refs/heads/main" ]]; then
        echo "ERROR: Direct pushes to main are blocked."
        exit 1
    fi
done
```

Benefits: Catches bypass of pre-commit hook
Weakness: Still local, can be bypassed

**Layer 5: GitHub Branch Protection (Hard Remote Enforcement)**

Configure GitHub repository settings:

- Require pull request reviews before merging
- Require status checks to pass
- Include administrators in restrictions
- Block direct pushes to main

Benefits: Enforced at server level, cannot be bypassed locally
Weakness: Requires repository admin access to configure

#### Decision Framework: When to Apply Each Layer

| Layer | Effort | Bypass Difficulty | When to Use |
|-------|--------|-------------------|-------------|
| Persona verification | Low | Easy | Always (baseline) |
| Supervisor phase gate | Low | Medium | Multi-agent workflows |
| Pre-commit hook | Medium | Medium (--no-verify) | Team projects |
| Pre-push hook | Medium | Medium | Remote collaboration |
| Branch protection | Medium | Hard (admin required) | Production projects |

**Rule**: Apply layers progressively based on risk. Solo experiments may need only Layer 1. Production systems need all 5.

#### Implementation Roadmap

**Immediate (v0.5)**:

1. Add branch check to dbt-Developer persona
2. Add git state to Supervisor artifact matrix
3. Update implementation plan templates

**Short-term (v0.6)**:

1. Create and install pre-commit hook
2. Create and install pre-push hook
3. Document hook installation in onboarding

**Long-term (v1.0+)**:

1. Configure GitHub branch protection rules
2. Add CI check for PR branch structure
3. Automate hook installation via setup script

#### Key Learnings

1. **Soft checks are necessary but not sufficient**: They catch honest mistakes but not determined bypasses
2. **Defense-in-depth is not paranoia**: Each layer catches what the previous missed
3. **Local enforcement complements remote enforcement**: Can't always rely on server-side checks
4. **Audit trail matters**: When violations happen, having multiple checkpoints helps identify where the gap occurred
5. **Make correct behavior easier than incorrect**: If creating a branch is friction, violations increase

**See also**:

- Pattern: "Phase Gate Design: Artifacts and State Verification" (below)
- Skill: `.claude/skills/learned-workflow-enforcement.md`
- FOR_CHRIS: `docs/for_chris/UNDERSTANDING_PR_WORKFLOW.md`

---

### Pattern: Phase Gate Design: Artifacts and State Verification

**When to apply**: Designing phase transitions in any multi-stage workflow

**Proven in**: v0.5 PR workflow bypass analysis, Supervisor phase gate design

**Description**: Effective phase gates verify both produced artifacts (documents, code) AND precondition states (git state, environment). Verifying only one creates gaps that enable workflow bypasses.

#### The Anti-Pattern: Artifact-Only Verification

The original Supervisor phase gate verified:

| Transition | Required Artifacts |
|------------|-------------------|
| PM -> Architect | PRD exists |
| Architect -> Tester | TDD exists |
| Tester -> Developer | Test spec exists |
| Developer -> Reviewer | Implementation complete |

**Problem**: This only checks "was the previous step completed?" not "are preconditions for the next step met?"

When transitioning to Developer phase, the gate verified that test specs existed but not that:

- A feature branch was created
- A draft PR was opened
- The working directory was on the correct branch

Result: Implementation began on main instead of the feature branch.

#### The Better Pattern: Artifacts AND State

Phase gates should verify two categories:

**1. Completion Evidence (Backward-Looking)**

Did the previous phase produce expected outputs?

```markdown
| Transition | Required Artifacts |
|------------|-------------------|
| Architect -> Tester | TDD-*.md exists |
```

**2. Precondition State (Forward-Looking)**

Are conditions met for the next phase to succeed?

```markdown
| Transition | Precondition State |
|------------|-------------------|
| Tester -> Developer | Feature branch exists, draft PR created |
```

#### Combined Verification Matrix

| Transition | Artifact Check | State Check | Verification Command |
|------------|----------------|-------------|---------------------|
| PM -> Architect | PRD-*.md exists | None (planning phase) | `ls docs/specs/PRD-*.md` |
| Architect -> Tester | TDD-*.md exists | None | `ls docs/tdd/TDD-*.md` |
| Tester -> Developer | Test spec exists | Branch created, draft PR | `git branch --show-current`, `gh pr list` |
| Developer -> Reviewer | Files created | No uncommitted changes | `git status --porcelain` |
| Reviewer -> Documenter | Reviews approved | No BLOCKER comments | `gh pr reviews` |
| Documenter -> Deploy | CHANGELOG updated | All tests pass | `dbt build --select state:modified` |

#### State Categories to Verify

**Git State**:

- Current branch matches expected (`git branch --show-current`)
- No uncommitted changes for handoff phases (`git status`)
- Remote is synced (`git fetch && git status`)
- PR exists and is correct state (`gh pr view`)

**Environment State**:

- Dependencies installed (`uv sync` succeeded)
- Database accessible (`dbt debug`)
- Required secrets/config present

**Process State**:

- Previous agents completed their phase
- No blocking issues pending
- Stakeholder approvals obtained (if required)

#### Implementing State Verification

**Step 1: Identify preconditions for each phase**

List what must be true before phase can begin:

```markdown
## Developer Phase Preconditions
- [ ] Feature branch created (not main)
- [ ] Branch pushed to origin
- [ ] Draft PR created
- [ ] Test specifications exist
- [ ] No blocking design questions
```

**Step 2: Map preconditions to verifiable checks**

```bash
# Branch check
branch=$(git branch --show-current)
[[ "$branch" != "main" ]] || exit 1

# PR check
gh pr view --json state --jq '.state' | grep -q "OPEN"
```

**Step 3: Add to phase gate verification**

```markdown
## Supervisor: Tester -> Developer Transition

### Artifacts (backward-looking)
- [ ] Test spec exists: `temp/v*_TESTING.md`

### Preconditions (forward-looking)
- [ ] On feature branch: `git branch --show-current` != main
- [ ] Draft PR exists: `gh pr list --head [branch] --state open`
```

**Step 4: Document failure handling**

What happens if precondition fails?

```markdown
If precondition fails:
1. BLOCK transition
2. Report specific failure: "Feature branch not created"
3. Provide fix command: "git: create branch feat/[feature-name]"
4. Do NOT proceed until precondition met
```

#### Decision Points for Phase Gate Design

**When to add state verification**:

- Transition involves environment change (different branch, different service)
- Failure after transition is expensive (hard to undo)
- Multiple actors involved (handoff points)

**When artifact verification is sufficient**:

- Same-context transitions (PM -> Architect, both work on same docs)
- Low-risk phases (can easily redo)
- Solo work (single actor, no handoff)

#### Common State Verification Gaps

| Gap | Symptom | Fix |
|-----|---------|-----|
| No branch check | Commits on main | Add git state to Tester -> Developer |
| No PR check | Work invisible to team | Require draft PR before implementation |
| No sync check | Merge conflicts later | Verify `git fetch && git status` shows synced |
| No environment check | "Works on my machine" | Verify `dbt debug` passes |

#### Key Takeaways

1. **Artifact verification is backward-looking**: "Did previous phase complete?"
2. **State verification is forward-looking**: "Can next phase succeed?"
3. **Both are required for robust phase gates**: One without the other creates gaps
4. **Precondition failures should block, not warn**: Phase gates exist to prevent problems
5. **Each phase transition should have explicit verification criteria**: Document what you check

**See also**:

- Pattern: "PR-Centric Development with Defense-in-Depth Enforcement" (above)
- `.claude/agents/supervisor.md` - Artifact Requirements Matrix
- Skill: `.claude/skills/learned-workflow-enforcement.md`

---

## dbt Architecture Patterns

_Patterns for dbt project structure and model organization._

### Pattern: Three-Layer Model Architecture

**When to apply**: Any dbt project with multiple data transformations

**Validated by**: [ADR-2](../specs/TDD-001-DBT-PROJECT-ARCHITECTURE.md#adr-2-three-layer-model-architecture)

**Proven in**: v0.3 (9 staging models), v0.4 (11 dimensional models), v0.5 (7 analytics models)

**Description**: Organize dbt models into three distinct layers: Staging, Intermediate/Dimensional, and Marts/Analytics. Each layer has a specific purpose and naming convention.

**Layer Structure**:

| Layer | Prefix | Purpose | Example |
|-------|--------|---------|---------|
| Staging | `stg_` | 1:1 with source, light transformations | `stg_synthea__patients` |
| Intermediate | `int_` | Business logic, joins, enrichment | `int_encounters__enriched` |
| Dimensional | `dim_`, `fct_` | Kimball-style facts and dimensions | `dim_patients`, `fct_encounters` |
| Analytics | `fct_`, `v_` | Domain-specific analytics and views | `fct_patient_summary`, `v_active_patients` |

**Key Principles**:

1. **Source isolation**: Only staging models use `source()` macro
2. **Layer dependencies**: Models depend only on same or earlier layers
3. **Naming consistency**: Prefix indicates layer and purpose
4. **Single responsibility**: Each model does one thing well

**Trade-offs**:

| Choice | Benefit | Cost |
|--------|---------|------|
| More files | Clear separation | Navigation overhead |
| Naming conventions | Self-documenting | Learning curve |
| Layer restrictions | Predictable dependencies | Less flexibility |

**Benefits**:

- Easy to understand data flow
- Reusable intermediate models
- Clear testing boundaries
- Consistent onboarding experience

**When NOT to use**:

- Very simple projects (<5 models)
- Ad-hoc analysis work
- Prototype/exploratory work

**See also**:

- TDD-001: Original architecture decision
- ADR_INDEX.md: Full ADR registry

---

## dbt + uv Patterns

_Learnings from modernizing dbt projects with uv-managed Python environments._

### Pattern: pyproject.toml for dbt Projects

**When to apply**: Setting up any new dbt project or migrating from requirements.txt

**Proven in**: dbt-playground v0.2 uv migration

**Description**: dbt projects should use simplified pyproject.toml without build-system configuration since they are not Python libraries.

**Implementation**:

```toml
[project]
name = "your-dbt-project"
version = "0.1.0"
description = "Brief description"
requires-python = ">=3.11"
dependencies = [
    "dbt-duckdb>=1.10.0",
]

[tool.uv]
dev-dependencies = [
    "sqlfluff>=3.0.0",
    "pre-commit>=3.7.0",
]
```

**Key decisions**:

1. **No `[build-system]`**: dbt projects aren't pip-installable libraries
2. **Loose version constraints**: Use `>=1.10.0` not exact pinning (lock file handles exact versions)
3. **Dev tools separate**: Linters in `[tool.uv]` section

**Anti-patterns**:

- Adding `[build-system]` with setuptools/hatchling (unnecessary complexity)
- Exact version pinning like `dbt-duckdb==1.11.2` (version may not exist)
- Mixing production and dev dependencies

---

### Pattern: PEP 723 Script Headers

**When to apply**: Standalone Python scripts that need to be self-documenting or have unique dependencies

**Proven in**: dbt-playground scripts (extract_content.py, insert_shopping_dialogues.py)

**Description**: Use PEP 723 inline script metadata to make scripts self-contained and runnable with `uv run`.

**Implementation for stdlib-only scripts**:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Script docstring."""

import sys
from pathlib import Path
```

**Implementation for scripts with dependencies**:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas>=2.0.0",
#     "requests>=2.31.0",
# ]
# ///
```

**Benefits**:

- Scripts document their own requirements
- `uv run script.py` automatically handles dependencies
- No separate requirements file per script

**Gotchas**:

- Some linters may strip PEP 723 headers (functionality preserved)
- Use `dependencies = []` not omitting the key for stdlib-only

**See also**: Skill: `.claude/skills/learned-pattern-uv-dbt-project-setup.md`

---

### Pattern: Version Constraint Selection

**When to apply**: Choosing version constraints for Python packages in pyproject.toml

**Proven in**: dbt-playground dbt-duckdb version selection

**Description**: Use available package versions with floor constraints, not exact pins.

**Decision framework**:

| Scenario | Constraint | Example |
|----------|------------|---------|
| Stable API needed | Floor constraint | `>=1.10.0` |
| Major version compat | Compatible release | `~=1.10` |
| Exact reproducibility | Lock file | `uv.lock` handles this |
| Latest always | No constraint | `dbt-duckdb` |

**Common gotcha**: dbt adapter versions don't always match dbt-core versions. Example: `dbt-duckdb>=1.11.2` may not exist even if dbt 1.11.2 is out.

**Verification**:

```bash
# Check what versions exist
uv pip index versions dbt-duckdb
```

---

### Pattern: Lock File Strategy

**When to apply**: Deciding whether to commit uv.lock

**Proven in**: dbt-playground reproducibility requirements

**Description**: Commit `uv.lock` for reproducible builds; it ensures identical package versions across all machines.

**Decision matrix**:

| Project Type | Commit Lock? | Reason |
|--------------|--------------|--------|
| Application (dbt project) | **Yes** | Reproducible builds |
| Library (pip-installable) | No | Let consumers resolve |
| Team project | **Yes** | Same versions for all |
| Solo experiment | Optional | Your preference |

**Workflow**:

```bash
# Initial setup
uv sync                    # Creates uv.lock
git add uv.lock           # Commit it

# After adding packages
uv add pandas             # Updates uv.lock
git add uv.lock pyproject.toml
git commit -m "chore: add pandas"

# Updating dependencies
uv sync --upgrade         # Updates uv.lock to latest compatible
```

**Benefits**:

- Reproducible CI/CD
- No "works on my machine" issues
- Clear audit trail of version changes

---

## v0.9 PM Orchestration Patterns

_Learnings from the PM Orchestration Hybrid Lite implementation (session management, multi-worktree coordination, task tracking)._

### v0.9 Architecture Decisions

#### Pattern: Hybrid Lite Over Complex Infrastructure

**When to apply**: Building state management or coordination systems where simplicity trumps features

**Proven in**: v0.9 PM Orchestration (replaced SQLite + sync architecture with JSON + REST API)

**Description**: When evaluating architecture options, prefer solutions that deliver 90% of value with 10% of complexity. Avoid over-engineering for theoretical requirements not yet proven necessary.

**The Decision Journey**:

Original PRD-022 proposed complex architecture:

- Backlog.md with bi-directional sync
- SQLite (9 tables for state database)
- dbt analytics (staging + marts)
- Custom dashboard

After testing Backlog.md, this simplified to:

- Backlog.md (markdown + REST API + MCP)
- PM_SESSIONS.json (simple heartbeat tracker)
- Workflow Hub (3 widgets)

**Result**: 4 hours implementation vs. 2-3 weeks original estimate.

**Decision Criteria for Hybrid Lite**:

1. **Test before committing**: Install and explore the tool before designing around assumptions
2. **Measure real requirements**: Do not build for imagined scale or features
3. **Defer complexity**: Features can be added when proven necessary
4. **Value implementation speed**: Time-to-value matters

**Trade-offs Accepted**:

| Trade-off | Why Acceptable |
|-----------|----------------|
| Non-atomic task claiming | 1-2 concurrent sessions makes race conditions rare |
| 60s vs 30s heartbeat | Does not affect real user experience |
| No SQL analytics | Can parse markdown later if genuinely needed |

**See also**:

- ADR-002: SQLite State Layer (superseded by Hybrid Lite)
- `temp/AGENT_REPORTS/pm-orchestration-backlog/ARCH_DECISION_HYBRID_LITE.md`

---

#### Pattern: Single Active Session Per Worktree

**When to apply**: Multi-session coordination where one actor per context is the common case

**Proven in**: v0.9 PM Sessions implementation (pm_sessions.js lines 256-262)

**Description**: When a new session registers for a worktree that already has an active session, automatically end the previous session rather than allowing multiple.

**Rationale**:

1. **Matches typical workflow**: One Claude Code session per worktree at a time
2. **Simplifies conflict detection**: Only one actor can claim tasks per worktree
3. **Automatic cleanup**: No orphaned sessions accumulate
4. **Clear ownership**: No ambiguity about which session is active

**Consequences**:

- Cannot run multiple test sessions in same worktree (use different worktrees instead)
- Session history shows previous sessions as "ended" not "concurrent"
- Simplifies stale detection (only check one session per worktree)

---

#### Pattern: JSON File as Coordination Layer

**When to apply**: Lightweight cross-process coordination where SQLite is overkill

**Proven in**: v0.9 PM_SESSIONS.json implementation

**Description**: Use a JSON file in a shared directory for simple state coordination between processes. Combine with file locking for safe concurrent access.

**When JSON beats SQLite**:

| Criterion | JSON | SQLite |
|-----------|------|--------|
| Human readable | Yes | No (binary) |
| Query capability | Basic | Full SQL |
| Concurrent writes | With locking | WAL mode |
| Setup required | None | Schema migration |
| Debugging ease | High | Low |

**Decision Matrix**:

- **<100 records**: JSON is likely sufficient
- **Read-heavy, write-light**: JSON works well
- **Need complex queries**: SQLite wins
- **Need transactions**: SQLite wins
- **Debugging ease important**: JSON wins

---

### Implementation Patterns

#### Pattern: Atomic File Operations with Locking

**When to apply**: Any file-based state that may have concurrent readers/writers

**Proven in**: v0.9 pm_sessions.js (lines 124-141, 157-177)

**Description**: Combine temp-file-then-rename pattern for atomicity with file locking for concurrency safety.

**Implementation approach**:

1. **Temp + rename for atomicity**: Write to .tmp file, then rename (POSIX guarantees atomic rename)
2. **File locking for concurrency**: Use proper-lockfile with retry configuration
3. **Always use both together** for file-based state
4. **Release lock in finally** to prevent deadlocks

**Why both patterns**:

| Pattern | Protects Against |
|---------|-----------------|
| Temp + rename | Partial writes, corruption on crash |
| File locking | Concurrent writers clobbering each other |

**Security Review Validated**: Security review confirmed these patterns as best practices.

---

#### Pattern: DRY Abstraction with updateSession Pattern

**When to apply**: Multiple operations that follow read-modify-write pattern on same data structure

**Proven in**: v0.9 pm_sessions.js (lines 185-203, reduced duplication 60%)

**Description**: Extract common read-lock-modify-write pattern into a higher-order function that takes the update logic as a callback.

**Benefits**:

1. **Single point of locking**: Lock logic in one place
2. **Consistent error handling**: Session-not-found handled uniformly
3. **Atomic operations**: Read-modify-write always together
4. **Testable**: Update logic can be tested in isolation

**Code Review Validated**: Code review specifically called out this pattern as "reducing duplication 60%".

---

#### Pattern: Schema Validation with AJV

**When to apply**: Any JSON file that needs structure validation before use

**Proven in**: v0.9 pm_sessions.js (lines 38-66, 105-109)

**Description**: Use AJV (Another JSON Validator) to validate JSON schema before processing. Return safe defaults on validation failure.

**Key principles**:

1. **Use ajv-formats** for date-time, uri, email validation
2. **Define enums explicitly** for status fields
3. **Mark required fields** to catch incomplete data
4. **Return safe defaults** on validation failure (do not throw)
5. **Log validation errors** for debugging

**Security Consideration**: Schema validation prevents malformed data from causing runtime errors.

---

### Testing Strategy Patterns

#### Pattern: Unit Tests for State Machine Operations

**When to apply**: Session lifecycle, status transitions, or any state-based logic

**Proven in**: v0.9 pm_sessions.test.js (40 unit tests covering all state transitions)

**Description**: Treat session management as a state machine and test all valid transitions, edge cases, and invalid operations.

**Test Categories**:

| Category | Tests | What It Validates |
|----------|-------|-------------------|
| Registration | 5 | New session creation, UUID generation |
| Heartbeat | 4 | Timestamp updates, stale recovery |
| Session ending | 3 | Status transition, ended_at timestamp |
| Stale detection | 5 | Threshold timing, status change |
| Task claiming | 6 | Claim, conflict detection, release |
| Cleanup | 2 | Retention period, old session removal |

**Key testing principles**:

1. **Test state transitions explicitly**: active -> stale, stale -> active
2. **Test boundary conditions**: exactly at threshold, one second before/after
3. **Test conflict scenarios**: two sessions claiming same task
4. **Test idempotency**: re-claiming already-claimed task

---

#### Pattern: E2E Tests Without Full Integration

**When to apply**: Validating infrastructure and APIs without requiring full system setup

**Proven in**: v0.9 multi-worktree-visibility.spec.ts (10 tests)

**Description**: E2E tests can verify that the necessary infrastructure and APIs work correctly without requiring complex setup like creating real worktrees.

**Rationale**:

Creating real worktrees during CI runs would pollute the repository, require cleanup, slow down tests, and risk leaving orphaned worktrees.

Instead, tests verify the APIs and infrastructure that enable multi-worktree coordination, without actually creating worktrees.

**Key insight**: Testing the **mechanism** (APIs work, files update correctly) is often more valuable than testing the **integration** (two real worktrees coordinating).

---

### Multi-Worktree Coordination

#### Pattern: Shared State via Temp Directory

**When to apply**: Cross-worktree coordination where state should not be committed to git

**Proven in**: v0.9 PM_SESSIONS.json in temp/ directory

**Description**: Place coordination files in a temp/ directory that is shared across worktrees but not committed to git.

**Key characteristics**:

1. **Gitignored**: temp/ is in .gitignore, state not committed
2. **Shared path**: All worktrees access same file via main repo path
3. **Ephemeral**: State can be regenerated, not critical data
4. **Human readable**: JSON for easy debugging

**Why not git-tracked state**: Session data changes frequently (heartbeats every 60s), would create constant merge conflicts.

**Why not per-worktree state**: Cross-worktree visibility is the goal; each worktree seeing its own state defeats the purpose.

---

#### Pattern: Cross-Worktree Visibility via API

**When to apply**: When worktrees need to see each other's work without git sync

**Proven in**: v0.9 Backlog.md integration with remote_operations: true

**Description**: Use an API server (Backlog.md at localhost:6420) that can scan remote branches, providing visibility across worktrees without requiring git push/pull.

**How it works**:

1. Backlog.md server runs on localhost:6420
2. Server scans remote branches (last 30 days)
3. API returns tasks from all branches
4. Worktrees see each other's tasks via API

**Benefits**:

- No git push required for visibility
- Centralized view of all work
- Browser UI shows consolidated board
- REST API enables programmatic access

---

### Key Takeaways from v0.9 PM Orchestration

**Architecture Decision Patterns**:

1. Test tools before designing around assumptions
2. Defer complexity until proven necessary
3. Single source of truth beats sync

**Implementation Patterns**:

1. Atomic writes + file locking for concurrent access
2. Schema validation on read prevents crashes
3. DRY higher-order functions reduce code

**Testing Patterns**:

1. State machine testing covers all transitions
2. Infrastructure validation without full integration
3. 40 unit + 10 E2E tests provides comprehensive coverage

**Future Implications**:

- What this enables: Additional worktree-aware tools, task-based automation
- Constraints: Backlog.md dependency, JSON file scaling limit (~100 sessions)

---

## Metrics

**Total Patterns**: 44 (as of 2026-02-01)

- Proven Patterns: 8
- Decision Frameworks: 2
- Common Pitfalls: 2
- Best Practices: 3
- Phase 1 SRS Patterns: 11 (Architecture: 2, Security: 3, JavaScript Defensive: 5, Testing: 2)
- Phase 2 Engagement Patterns: 6 (Architecture: 2, Bugs: 2, SVG: 2)
- Workflow Enforcement Patterns: 2 (Defense-in-depth, Phase gate design)
- dbt + uv Patterns: 4 (pyproject.toml, PEP 723, version constraints, lock files)
- v0.9 PM Orchestration Patterns: 10 (Architecture: 3, Implementation: 3, Testing: 2, Multi-Worktree: 2)

**Last Updated**: 2026-02-01 (Added v0.9 PM Orchestration patterns - Hybrid Lite architecture, session management, multi-worktree coordination)

**Related Skills**:

- `.claude/skills/learned-pattern-javascript-defensive-coding.md` - Executable checklist for defensive coding
- `.claude/skills/learned-pattern-browser-testing.md` - Browser testing workflow

**Maintained by**: Sage persona
