---
audience: [multi-agent]
priority: high
size: large
dependencies: [PROJECT_STRUCTURE, ARCHITECTURE]
last_updated: 2026-01-25
status: active
tags: [workflow, planning, epic, tdd, task]
---

# Project Workflow Guide

**Purpose**: Document the Epic → TDD → Task breakdown pattern for feature development

**Last Updated**: 2026-01-25

---

## Table of Contents

- [Overview](#overview)
- [Workflow Phases](#workflow-phases)
- [Epic → TDD → Task Pattern](#epic--tdd--task-pattern)
- [Personas and Responsibilities](#personas-and-responsibilities)
- [Claude Task Integration](#claude-task-integration)
- [Real-World Example: PRD-001](#real-world-example-prd-001)
- [When to Skip Phases](#when-to-skip-phases)
- [Best Practices](#best-practices)

---

## Overview

This project follows a **structured workflow** from high-level feature planning to detailed implementation. The workflow ensures:

1. **Clear Requirements**: PM defines "what" and "why" in PRDs
2. **Technical Clarity**: Architect defines "how" in TDDs
3. **Actionable Tasks**: PM/Architect breaks down into implementable chunks
4. **No Developer Guessing**: Every task references a TDD section with complete specs

**Key Principle**: **TDD is the source of truth for implementation**. Developers should never need to guess how to implement something—it's all in the TDD.

---

## Workflow Phases

### Mature Software Team Pattern

```
┌──────────────────────────────────────────────────────────┐
│ 1. PM: Write PRD                                          │
│    Output: docs/specs/PRD-XXX.md                          │
│    Defines: What to build, why it matters, success metrics│
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ 2. PM: Create Epic Issue                                  │
│    Output: GitHub issue (type:epic)                       │
│    Contains: High-level task checklist from PRD           │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ 3. Architect: Create TDD                                  │
│    Output: docs/tdd/TDD-XXX.md                            │
│    Defines: Architecture, algorithms, API contracts       │
│    Contains: Schema design, pseudocode, test strategy     │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ 4. PM/Architect: Break into Tasks                         │
│    Output: GitHub issues (type:task)                      │
│    Each task: References TDD section (e.g., "per §2.1")   │
│    Contains: Acceptance criteria, test plan               │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ 5. Developer: Implement Tasks                             │
│    Output: Working code in kanji/js/, kanji/css/, etc.    │
│    Follows: TDD specifications exactly                    │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ 6. Tester: Verify Implementation                          │
│    Output: Test results, bug reports                      │
│    Validates: Acceptance criteria met, TDD specs followed │
└──────────────────────────────────────────────────────────┘
```

---

## Epic → TDD → Task Pattern

### What is This Pattern?

The Epic → TDD → Task pattern separates **product thinking** (what to build) from **technical thinking** (how to build it) from **execution** (building it).

| Artifact | Owner | Purpose | Audience |
|----------|-------|---------|----------|
| **PRD** | PM | Define feature goals, user stories, success metrics | Stakeholders, team |
| **Epic Issue** | PM | Track high-level progress, coordinate tasks | Team, GitHub board |
| **TDD** | Architect | Define technical implementation, algorithms, APIs | Developers, reviewers |
| **Task Issues** | PM/Arch | Break down work, assign owners, track progress | Developers |

### Why This Pattern?

**Without TDD**:
- Developer sees task: "Implement SM-2 algorithm"
- Developer asks: "What formula? What edge cases? What data structure?"
- Architect has to explain in comments/chat
- Result: Inconsistent implementation, back-and-forth, wasted time

**With TDD**:
- Developer sees task: "Implement SM-2 algorithm per TDD-001 §3"
- Developer reads TDD-001 §3
- TDD has: Complete pseudocode, edge cases, test cases, API contracts
- Result: Developer implements exactly to spec, no ambiguity

---

## Personas and Responsibilities

### Product Manager (PM)

**When**: Start of feature development

**Responsibilities**:
1. Write PRD defining feature goals and acceptance criteria
2. Create Epic issue in GitHub with high-level task list
3. After TDD is created, break Epic into detailed task issues
4. Update task descriptions to reference TDD sections
5. Coordinate task dependencies and priorities

**Artifacts Created**:
- `docs/specs/PRD-XXX.md`
- Epic issue (e.g., #7)
- Task issues (e.g., #13-22)

**Example**: See PRD-001 JLPT Mastery Engine

### Technical Architect (Architect)

**When**: After PRD approval, before implementation

**Responsibilities**:
1. Read PRD and understand requirements
2. Design system architecture and data structures
3. Write TDD with complete specifications:
   - §1: Architecture overview with diagrams
   - §2: Data schema design with rationale
   - §3: Algorithm specifications with pseudocode
   - §4: State machines and transitions
   - §5: Business logic formulas
   - §6: API contracts with function signatures
   - §7: Testing strategy with test cases
4. Answer open questions from PRD
5. Update Epic issue to link to TDD

**Artifacts Created**:
- `docs/tdd/TDD-XXX.md`

**Example**: See TDD-001 JLPT Mastery Engine (35KB, 1450 lines)

### Developer (Developer)

**When**: After TDD is created, tasks are ready

**Responsibilities**:
1. Read TDD section referenced in task
2. Implement code exactly per TDD specifications
3. Write unit tests per TDD §7 test cases
4. Update task status as work progresses
5. Flag ambiguities or errors in TDD immediately

**Artifacts Created**:
- Implementation code (e.g., `kanji/js/srs-engine.js`)
- Unit tests
- PR for review

**Key Rule**: If something is unclear or missing from TDD, **ask Architect before implementing**. Don't guess.

### Quality Tester (Tester)

**When**: After implementation, before PR merge

**Responsibilities**:
1. Run test cases from TDD §7
2. Verify acceptance criteria from task issue
3. Check edge cases and error handling
4. Report bugs with clear reproduction steps
5. Validate against PRD user stories

**Artifacts Created**:
- Test reports
- Bug issues
- Verification sign-off

---

## Claude Task Integration

Claude Code has built-in task primitives (`TaskCreate`, `TaskUpdate`, `TaskList`) that enable **cross-session persistence** and **multi-agent coordination**.

### When to Use Claude Tasks

**Use Claude tasks for**:
- Session-level work breakdown (breaking down GitHub issues into sub-tasks)
- Agent handoffs (PM → Architect → Developer)
- Temporary coordination within a coding session
- Capturing context before session compaction

**Don't use Claude tasks for**:
- Long-term planning (use GitHub issues)
- External visibility (use GitHub issues)
- Milestone tracking (use GitHub issues)

### Integration with GitHub Issues

Claude tasks can **mirror** GitHub structure using metadata:

```javascript
// Example: Create Claude task for Epic
TaskCreate({
  subject: "PRD-001: JLPT Mastery Engine",
  description: "Epic tracking for GitHub #7",
  metadata: {
    github_issue: 7,
    type: "epic",
    epic_id: "PRD-001",
    prd: "docs/specs/PRD-001-JLPT-Mastery-Engine.md"
  }
})

// Example: Create Claude task for implementation
TaskCreate({
  subject: "T1.1 - Implement localStorage layer",
  description: "Implement per TDD-001 §2",
  metadata: {
    github_issue: 13,
    type: "task",
    epic: 7,
    tdd_section: "§2"
  }
})
```

**Benefits**:
- Tasks persist across Claude restarts
- Metadata links to GitHub issues
- Dependencies tracked via `addBlockedBy`
- Cross-session coordination possible

**Metadata Schema**: See `docs/guides/CLAUDE_TASK_INTEGRATION.md` for complete schema

---

## Real-World Example: PRD-001

### PRD-001: JLPT Mastery Engine

**Epic Issue**: #7

**Workflow Timeline**:

1. **PM writes PRD** (2026-01-24)
   - Output: `docs/specs/PRD-001-JLPT-Mastery-Engine.md`
   - Defines: SRS algorithm, mastery stages, JLPT aggregation
   - Open questions: Burned items handling, new card limits

2. **PM creates Epic** (2026-01-24)
   - Output: GitHub issue #7
   - Task list: T1.1 - T1.10 (high-level only)

3. **Architect creates TDD** (2026-01-25)
   - Output: `docs/tdd/TDD-001-JLPT-Mastery-Engine.md` (35KB)
   - §1: 4-layer architecture with data flow diagrams
   - §2: Complete localStorage schema (1032-line reference implementation)
   - §3: SM-2 algorithm with pseudocode
   - §4: 8-stage mastery state machine
   - §5: JLPT/topic aggregation formulas
   - §6: API contracts for 4 modules
   - §7: 42 test cases (unit + integration + edge cases)
   - Answers all PRD open questions

4. **PM updates tasks** (2026-01-25)
   - Updated issues #13-22 with TDD section references
   - Before: "Design localStorage schema"
   - After: "Implement localStorage layer per TDD-001 §2"

5. **Developer implements** (in progress)
   - Reads TDD-001 §2 for schema specifications
   - Implements `storage.js` with exact schema
   - Writes validation per §2.8
   - Tests against §7.2 test cases

### Task Breakdown Example

**Original Task** (before TDD):
```
#13 T1.1 - Design localStorage schema

Description: Design the localStorage schema for per-kanji SRS progress tracking.

Problem: Too vague! What fields? What structure? What validation?
```

**Updated Task** (after TDD):
```
#13 T1.1 - Implement localStorage layer per TDD-001 §2

Description: Implement the localStorage schema per TDD-001 §2.

TDD Reference: TDD-001 §2 (localStorage Schema Design)

Acceptance Criteria:
- [ ] Schema implemented per TDD-001 §2.2 (Root Schema Structure)
- [ ] Per-kanji progress structure matches §2.3
- [ ] Settings structure matches §2.4
- [ ] Stats structure matches §2.5
- [ ] Metadata structure matches §2.6
- [ ] Schema versioning per §2.7
- [ ] Validation rules per §2.8

Reference Implementation: temp/kanji-storage-schema.js (1032 lines)

Key Design Decisions (from §2.3.1):
- Character redundancy for validation
- Fractional intervals (4 hours = 0.167 days)
- History limiting (50 entries max)
```

**Result**: Developer knows exactly what to implement. No ambiguity.

---

## When to Skip Phases

Not every change requires the full workflow. Use judgment:

### Skip PRD When:
- Bug fix (implementation-only change)
- Minor UI tweak (CSS change)
- Documentation update
- Refactoring without behavior change

### Skip TDD When:
- Change is <50 lines
- Pattern already established (e.g., add another page using existing template)
- Trivial implementation (typo fix, comment update)

### Always Do:
- Create GitHub issue (even for small tasks)
- Update CHANGELOG
- Test changes manually
- Get code review

**Rule of Thumb**: If you're unsure whether a task needs a TDD, ask PM or Architect. Better to over-document than under-document.

---

## Best Practices

### For PMs

**Do**:
- Write clear, testable acceptance criteria
- Reference TDD sections in every task
- Keep Epic issues updated with progress
- Adjust priorities based on blockers

**Don't**:
- Create tasks before TDD exists (they'll be too vague)
- Skip linking tasks to TDD sections
- Assume developers know what "implement X" means

### For Architects

**Do**:
- Include complete pseudocode for algorithms
- Provide function signatures with types
- Document edge cases explicitly
- Include test cases in §7
- Answer all open questions from PRD
- Use diagrams (D2 format) for complex flows

**Don't**:
- Leave implementation details ambiguous
- Skip error handling specifications
- Assume "obvious" design decisions
- Write TDD without reading PRD first

### For Developers

**Do**:
- Read entire TDD section before coding
- Follow TDD specs exactly (don't improvise)
- Write tests per TDD §7 test cases
- Flag TDD errors or ambiguities immediately
- Reference TDD section in PR description

**Don't**:
- Guess at implementation details
- Deviate from TDD without architect approval
- Skip edge cases documented in TDD
- Implement before TDD exists

### For Testers

**Do**:
- Run all test cases from TDD §7
- Test edge cases explicitly documented
- Verify acceptance criteria from task
- Report bugs with TDD section reference

**Don't**:
- Skip documented test cases
- Test only happy path
- Approve PRs without checking TDD compliance

---

## Templates

### PRD Template

See: `docs/specs/PRD-001-JLPT-Mastery-Engine.md` as reference

**Sections**:
1. Problem Statement
2. User Benefit
3. Target Users
4. User Stories (prioritized)
5. Acceptance Criteria
6. Scope (in/out)
7. Success Metrics
8. Dependencies
9. Technical Considerations (high-level)
10. Open Questions (for Architect)

### TDD Template

See: `docs/tdd/TDD-001-JLPT-Mastery-Engine.md` as reference

**Sections**:
1. §1: Architecture Overview
2. §2: Data Schema Design
3. §3: Algorithm Specifications
4. §4: State Machines / Business Logic
5. §5: Calculation Formulas
6. §6: API Contracts
7. §7: Testing Strategy

**Principles**:
- Complete specifications (no ambiguity)
- Pseudocode for all algorithms
- Function signatures with types
- Edge cases documented
- Test cases enumerated
- Design decisions explained with rationale

### Task Template

**Format**:
```markdown
**Parent Epic**: #X

**Task ID**: TX.Y

**TDD Reference**: TDD-XXX §Y (Section Name)

## Description
[Action verb] per TDD-XXX §Y. [Brief elaboration].

## Acceptance Criteria
- [ ] [Specific criterion from TDD]
- [ ] [Another criterion]

## Technical Implementation Notes

**Files to create/modify**: [List]

**TDD Pseudocode Reference**: [Section number]

**Function signatures**: [From TDD §6]

## Effort Estimate
[S/M/L]

## Blocked By
[List dependencies]

## Testing Plan
[Reference TDD §7 test cases]
```

---

## Metrics

### Workflow Health Indicators

| Metric | Target | Red Flag |
|--------|--------|----------|
| **Tasks with TDD references** | 100% | <80% |
| **TDD completeness** | All sections filled | Missing §6 or §7 |
| **Implementation time** | 2-3x estimate | >4x estimate (TDD unclear?) |
| **Back-and-forth questions** | <2 per task | >5 per task (TDD incomplete) |
| **Bugs found in review** | <3 per task | >10 per task (TDD misunderstood) |

### Success Stories

**Before Epic → TDD → Task**:
- Developer task: "Implement SRS algorithm" (10 lines)
- Developer implementation: 3 days, 5 clarifying questions, 2 refactors
- Bugs found: 8 (missed edge cases)
- Time to merge: 7 days

**After Epic → TDD → Task**:
- Developer task: "Implement SM-2 algorithm per TDD-001 §3" (200 lines with full spec)
- Developer implementation: 1 day, 0 questions, 0 refactors
- Bugs found: 1 (typo)
- Time to merge: 2 days

**Result**: 3.5x faster, 8x fewer bugs, 0 clarification time

---

## FAQ

### Q: Do I need a TDD for every feature?

**A**: For features >200 lines or with complex logic, yes. For small tweaks, no.

### Q: Who decides if a TDD is needed?

**A**: PM in consultation with Architect. When in doubt, create a TDD.

### Q: What if the TDD is wrong or incomplete?

**A**: Developer flags it immediately. Architect updates TDD. Implementation pauses until TDD is fixed.

### Q: Can I deviate from the TDD if I have a better idea?

**A**: No. Propose the change to Architect, get TDD updated, then implement. Never deviate silently.

### Q: What if there's no TDD section for my task?

**A**: Ask Architect to add it to the TDD before you start. Don't implement without specs.

### Q: How detailed should TDD pseudocode be?

**A**: Detailed enough that a developer can translate it to code without guessing. If you're unsure about an edge case, it should be in the TDD.

---

## Related Documentation

- [CLAUDE_TASK_INTEGRATION.md](CLAUDE_TASK_INTEGRATION.md) - Claude task metadata schema
- [PROJECT_BOARD_GUIDE.md](PROJECT_BOARD_GUIDE.md) - GitHub project board usage
- [ARCHITECTURE.md](../reference/ARCHITECTURE.md) - Overall system architecture
- [.claude/agents/AGENTS.md](../../.claude/agents/AGENTS.md) - Multi-persona orchestration guide

---

**Last Updated**: 2026-01-25 by PM (Claude)

**Changelog**:
- 2026-01-25: Initial version documenting Epic → TDD → Task pattern based on PRD-001/TDD-001 experience

---

*This workflow guide is a living document. Update it as we learn better practices.*
