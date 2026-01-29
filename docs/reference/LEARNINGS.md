# Technical Learnings & Patterns

**Purpose**: Quick technical reference for proven patterns, decision frameworks, common pitfalls, and best practices discovered during development.

**Maintenance**: Owned by Sage persona. Updated when patterns are proven in ≥2 real implementations.

**Related Documentation**:

- Executable workflows: `.claude/skills/learned-pattern-*.md`
- Educational narratives: `docs/for_chris/`
- Bug-specific patterns: `docs/standards/TESTING.md#bug-learnings`

---

## Table of Contents

- [Proven Patterns](#proven-patterns)
  - [Agent Orchestration](#agent-orchestration)
    - [Assembly Line Workflow](#pattern-assembly-line-workflow)
    - [Parallel Review Execution](#pattern-parallel-review-execution)
    - [Explicit Agent File Operations](#pattern-explicit-agent-file-operations)
    - [Agent Context Preparation](#pattern-agent-context-preparation)
    - [Agent vs Manual Decision Framework](#pattern-agent-vs-manual-decision-framework)
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

**TDD**: See docs/tdd/TDD-kanji-filter.md lines 45-67 for component design

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

## Metrics

**Total Patterns**: 27 (as of 2026-01-25)

- Proven Patterns: 7
- Decision Frameworks: 2
- Common Pitfalls: 2
- Best Practices: 3
- Phase 1 SRS Patterns: 11 (Architecture: 2, Security: 3, JavaScript Defensive: 5, Testing: 2)
- Phase 2 Engagement Patterns: 6 (Architecture: 2, Bugs: 2, SVG: 2)

**Last Updated**: 2026-01-25 (Added Phase 2 Engagement Layer patterns: IIFE module export, schema migration, appendChild bug, async toggle state bug, SVG progress rings, CSS grid heatmap)

**Related Skills**:

- `.claude/skills/learned-pattern-javascript-defensive-coding.md` - Executable checklist for defensive coding
- `.claude/skills/learned-pattern-browser-testing.md` - Browser testing workflow

**Maintained by**: Sage persona
