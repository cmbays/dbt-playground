# PRD: Agent Memory & Learning System

**PRD ID**: PRD-XXX (to be assigned)
**Date**: 2026-02-01
**Author**: Product Manager
**Status**: Draft
**Target Milestone**: v0.9

---

## 1. Problem Statement

### Current State

The dbt-playground project has a mature learning infrastructure managed by the Sage agent, including:

- `docs/reference/LEARNINGS.md` with 34 documented patterns
- `.claude/skills/learned-*.md` for executable workflows
- `temp/AGENT_REPORTS/` for per-feature context
- `temp/SESSION_SUMMARY*.md` for ad-hoc session notes

However, three critical gaps prevent systematic compound improvement:

| Gap | Impact |
|-----|--------|
| **No daily session logging** | Sessions cannot be replayed or audited. Pattern detection across sessions is manual. |
| **No automatic session-end triggers** | Learnings are lost if Sage is not explicitly invoked. Manual invocation is inconsistent. |
| **No compound loop automation** | Each session starts from scratch rather than building on recent learnings. |

### Pain Points

1. **Context Loss**: Starting a new session requires manually reconstructing what was learned previously
2. **Pattern Blindness**: Patterns that emerge across multiple sessions go unnoticed until manually reviewed
3. **Inconsistent Capture**: Learning extraction depends on remembering to invoke Sage
4. **No Audit Trail**: Cannot answer "why did we make this decision 3 weeks ago?"

### Opportunity

By adding lightweight daily logging and consolidation workflows, we can:

- Create an audit trail of decisions and learnings
- Surface patterns automatically through weekly review
- Feed relevant context into new sessions
- Measure improvement over time

---

## 2. User Stories / Use Cases

### US-1: Session Logging

**As** a developer working in dbt-playground
**I want** to log key decisions and learnings from my session
**So that** they are preserved for future reference and pattern extraction

**Acceptance Criteria**:

- [ ] Can append a structured entry to today's memory log
- [ ] Entry captures: timestamp, task, outcome, decisions, learnings, would-do-differently
- [ ] Log is git-tracked and searchable
- [ ] Logging takes <30 seconds

### US-2: Session End Capture

**As** a developer ending a significant work session
**I want** to be prompted to capture session learnings
**So that** I don't forget to document valuable insights

**Acceptance Criteria**:

- [ ] Prompt appears at explicit session end or milestone completion
- [ ] Prompt is not intrusive for quick sessions (<5 files changed)
- [ ] Can invoke `sage: end session` manually at any time
- [ ] Captures session summary to memory log

### US-3: Pattern Discovery

**As** the Sage agent
**I want** to scan recent memory logs for recurring patterns
**So that** proven patterns can be promoted to LEARNINGS.md

**Acceptance Criteria**:

- [ ] Weekly consolidation identifies patterns appearing 2+ times
- [ ] Patterns are proposed for LEARNINGS.md promotion (not auto-added)
- [ ] MEMORY_INDEX.md provides searchable summary of weekly learnings
- [ ] False positives are minimal (quality over quantity)

### US-4: Session Context Bootstrap

**As** a developer starting a new session
**I want** to see relevant learnings from recent memory
**So that** I don't repeat mistakes or reinvent solutions

**Acceptance Criteria**:

- [ ] Session start surfaces learnings related to current task
- [ ] Context load takes <30 seconds
- [ ] Irrelevant learnings are filtered out
- [ ] Can opt-out if context is not needed

### US-5: Decision Audit Trail

**As** a project maintainer
**I want** to understand why past decisions were made
**So that** I can evaluate whether to change them

**Acceptance Criteria**:

- [ ] Memory logs capture decision rationale, not just what was done
- [ ] Logs are searchable by keyword and date
- [ ] Can trace from current code back to decision context
- [ ] Retention policy preserves important decisions

---

## 3. Functional Requirements

### FR-1: Memory Directory Structure

```
memory/
  |-- 2026-02-01.md       # Daily append-only log
  |-- 2026-02-02.md       # Each day gets a new file
  |-- ...
  |-- MEMORY_INDEX.md     # Weekly summary and pattern index
```

**Rules**:

- One file per day, named `YYYY-MM-DD.md`
- Files are append-only (entries added, never removed during day)
- Files are git-tracked (not in .gitignore)
- MEMORY_INDEX.md regenerated weekly

### FR-2: Log Entry Format

Each entry follows a standardized format:

```markdown
## [YYYY-MM-DDTHH:MM:SS] Task: [Brief task description]

**Outcome**: SUCCESS | FAILURE | PARTIAL
**Files Modified**: [count] | [list if <5]

**Key Decisions**:
- [Decision]: [Rationale] (affects: [components])

**Learnings**:
- [What we learned]

**Would Do Differently**:
- [If anything]

**Related**:
- Issue: #[number] | PR: #[number] | None

---
```

### FR-3: Logging Commands

| Command | Behavior |
|---------|----------|
| `sage: log session` | Append entry to today's log via interactive prompt |
| `sage: log "[task]"` | Quick log with auto-filled defaults |
| `scripts/log-session.py` | CLI script for programmatic logging |

### FR-4: Session End Triggers

| Trigger | Condition | Action |
|---------|-----------|--------|
| Explicit end | User says "ending session" or similar | Prompt for learning capture |
| Milestone completion | Version deployed or major feature done | Sage suggests review |
| Threshold reached | >5 files modified OR >50 lines changed | Soft prompt at next pause |
| Manual | `sage: end session` | Full session review workflow |

### FR-5: Weekly Consolidation

| Input | Process | Output |
|-------|---------|--------|
| memory/*.md from past 7 days | Sage scans for patterns | MEMORY_INDEX.md updated |
| Patterns appearing 2+ times | Propose LEARNINGS.md additions | Promotion candidates list |
| Failed experiments | Extract negative learnings | "What to avoid" section |

**Consolidation triggers**:

- Manual: `sage: consolidate week`
- Future: Automatic weekly (configurable)

### FR-6: Session Start Context

At session start, if memory entries exist:

1. Load entries from past 7 days
2. Filter by relevance to stated task (if provided)
3. Surface top 3-5 relevant learnings
4. Display as "Recent Context" (not blocking)

**Relevance scoring** (simple keyword match initially):

- Task keywords match entry task description
- File paths match affected components
- Issue/PR numbers match

---

## 4. Non-Functional Requirements

### NFR-1: Performance

| Operation | Target | Rationale |
|-----------|--------|-----------|
| Log entry append | <5 seconds | Must be fast to encourage usage |
| Session start context load | <30 seconds | Should not slow down work |
| Weekly consolidation | <2 minutes | Acceptable for batch process |
| Keyword search in memory | <10 seconds | Reasonable for grep-based search |

### NFR-2: Storage

| Metric | Estimate | Policy |
|--------|----------|--------|
| Daily log size | ~2-5 KB | Based on 3-5 entries per day |
| Weekly storage | ~10-25 KB | 5 days * 5 KB |
| Monthly storage | ~40-100 KB | Acceptable for git tracking |
| Retention | 90 days active | Archive older logs manually |

**Storage growth mitigation**:

- Logs are text files (compress well in git)
- No binary or attachment storage
- Manual archive for logs >90 days old

### NFR-3: Reliability

| Requirement | Implementation |
|-------------|----------------|
| No data loss | Append-only writes, git versioned |
| Recovery from corruption | Git history provides backup |
| Graceful degradation | Missing memory/ does not break workflows |
| Partial availability | Individual log failures don't affect others |

### NFR-4: Usability

| Requirement | Implementation |
|-------------|----------------|
| Low friction logging | Single command or script |
| Non-intrusive prompts | Only at explicit session boundaries |
| Opt-out available | Can skip memory capture |
| Clear documentation | Usage in CLAUDE.md |

### NFR-5: Maintainability

| Requirement | Implementation |
|-------------|----------------|
| Extend existing infrastructure | Build on Sage agent, not parallel system |
| Simple file format | Markdown, no custom parsers needed |
| No external dependencies | File-based, no database or service |
| Standard patterns | PEP 723 scripts, existing skill format |

---

## 5. Acceptance Criteria

### Phase 1: Daily Logging (MVP)

- [ ] `memory/` directory exists and is git-tracked
- [ ] Can append entry via `sage: log session`
- [ ] Can append entry via `scripts/log-session.py`
- [ ] Log entry format follows specification
- [ ] CLAUDE.md documents memory/ usage

### Phase 2: Session End Triggers

- [ ] Supervisor prompts for capture at explicit session end
- [ ] `sage: end session` works as documented
- [ ] Threshold-based prompts appear for significant sessions
- [ ] Prompts are not intrusive for quick sessions

### Phase 3: Weekly Consolidation

- [ ] `sage: consolidate week` scans past 7 days
- [ ] Patterns appearing 2+ times are identified
- [ ] MEMORY_INDEX.md is generated
- [ ] Promotion candidates are proposed (not auto-committed)

### Phase 4: Compound Loop

- [ ] Session start loads relevant context from memory
- [ ] Context is filtered by task relevance
- [ ] WORKFLOW_STATE tracks memory entry status
- [ ] Measurable improvement in session continuity

### Overall Success Criteria

| Metric | Target | Timeframe |
|--------|--------|-----------|
| Memory entries created | >80% of significant sessions | After 30 days |
| Pattern promotions | 2-3 per month | Ongoing |
| Session startup satisfaction | "Context helpful" feedback | User survey |
| Repeated mistakes | Decreasing trend | Track in memory |

---

## 6. Out of Scope

### Explicitly NOT Building

| Item | Reason |
|------|--------|
| Vector database | Overkill for project scale; file-based is sufficient |
| Automatic LEARNINGS.md updates | Quality requires human review |
| Per-ticket LEARNINGS.md files | AGENT_REPORTS/ already serves this need |
| Real-time memory sync | Append-only batch is sufficient |
| External memory frameworks | Adds complexity without clear benefit |
| Semantic search | Keyword search is sufficient initially |
| Memory API service | File-based approach requires no API |
| Cross-repo memory | Single repo scope only |
| Automatic log rotation | Manual archive is acceptable |
| BI/analytics on memory | Simple metrics are sufficient |

### Deferred to Future Versions

| Item | Target Version | Trigger |
|------|----------------|---------|
| Automated weekly consolidation | v0.9.1 | If manual consolidation proves valuable |
| Semantic search (embeddings) | v1.0+ | If keyword search is insufficient |
| Memory dashboard visualization | v1.0+ | If memory volume grows significantly |
| Cross-session dependency tracking | v1.0+ | If workflow complexity increases |

---

## 7. Dependencies

### Prerequisites

| Dependency | Status | Required For |
|------------|--------|--------------|
| v0.8 complete | In progress | Phase 1 start |
| Sage agent functional | Complete | All phases |
| LEARNINGS.md exists | Complete | Phase 3 promotion |
| PEP 723 script pattern | Established | scripts/log-session.py |

### Technical Dependencies

| Component | Dependency | Integration Point |
|-----------|------------|-------------------|
| Sage agent | Write tool | Appending log entries |
| Supervisor | Prompt logic | Session end triggers |
| WORKFLOW_STATE | State tracking | Memory entry status |
| scripts/ | uv, PEP 723 | CLI logging script |

### No External Dependencies

This feature intentionally avoids external dependencies:

- No database (SQLite, DuckDB for memory)
- No vector store (ChromaDB, Pinecone)
- No external services (APIs, cloud storage)
- No additional Python packages

---

## 8. Risks and Mitigations

### R1: Low Adoption

**Risk**: Users find logging too tedious and skip it

**Probability**: Medium | **Impact**: High

**Mitigations**:

1. Make logging very fast (<30 seconds)
2. Provide quick-log command for minimal entries
3. Session-end prompts as gentle reminders
4. Demonstrate value through context bootstrapping

### R2: Noise Over Signal

**Risk**: Logs fill with low-value entries, obscuring useful patterns

**Probability**: Medium | **Impact**: Medium

**Mitigations**:

1. Structured format guides valuable entries
2. "Would do differently" forces reflection
3. Consolidation filters for recurring patterns only
4. Human review before LEARNINGS.md promotion

### R3: Scope Creep

**Risk**: Feature grows beyond minimal viable memory

**Probability**: Medium | **Impact**: Medium

**Mitigations**:

1. Explicit "what NOT to build" list
2. Phase gates require validation before advancing
3. Out of scope documented upfront
4. Review after Phase 1 before continuing

### R4: Integration Complexity

**Risk**: Memory system conflicts with existing Sage workflows

**Probability**: Low | **Impact**: Medium

**Mitigations**:

1. Extend existing Sage workflows, not replace
2. Memory is additive (new workflows J, K)
3. No changes to existing LEARNINGS.md process
4. Separate directory avoids conflicts

---

## 9. Success Metrics

### Leading Indicators (Early Validation)

| Metric | Target | When |
|--------|--------|------|
| First log entry created | Success | Day 1 |
| 5 consecutive days with entries | Adoption | Week 1 |
| First pattern identified | Value proof | Week 2 |
| Context bootstrap used | Loop closure | Week 3 |

### Lagging Indicators (Long-term Value)

| Metric | Target | When |
|--------|--------|------|
| Memory entry coverage | >80% of sessions | Month 1+ |
| Pattern promotions | 2-3/month | Month 2+ |
| Repeated mistakes | Decreasing trend | Month 2+ |
| Session resume time | Faster than before | Month 1+ |

### Qualitative Feedback

Collect during regular use:

- "Was the session context helpful?" (Y/N)
- "Did memory help avoid a repeat mistake?" (Y/N)
- "Is logging worth the time?" (Y/N)

---

## 10. Open Questions

### Q1: Retention Policy

**Question**: How long should memory logs be retained active vs. archived?

**Options**:

- A: 30 days active, then archive
- B: 90 days active, then archive (recommended)
- C: Indefinite active, manual archive
- D: Auto-delete after 180 days

**Recommendation**: Option B - 90 days provides sufficient context for most work, manual archive preserves valuable history.

### Q2: Automation Level

**Question**: Should weekly consolidation run automatically or on-demand?

**Options**:

- A: Always manual (`sage: consolidate week`)
- B: Auto on Monday with manual override (recommended for v0.9.1)
- C: Configurable cron-style schedule

**Recommendation**: Option A for v0.9 (validate value first), Option B for v0.9.1 if manual proves useful.

### Q3: Context Surfacing

**Question**: How prominent should session-start context be?

**Options**:

- A: Blocking (must acknowledge before proceeding)
- B: Prominent but dismissible (recommended)
- C: Subtle notification
- D: Opt-in only

**Recommendation**: Option B - Value comes from seeing context, but should not impede work.

---

## 11. Appendix

### A: Comparison to Research Report Recommendations

| Research Recommendation | PRD Alignment |
|------------------------|---------------|
| Daily append-only logs | FR-1, FR-2 |
| Session end triggers | FR-4 |
| Weekly consolidation | FR-5 |
| Compound loop | FR-6 |
| File-based approach | NFR-5 |
| No vector database | Out of Scope |
| Build on Sage | All phases |

### B: Existing Infrastructure Reuse

| Existing Component | How Reused |
|-------------------|------------|
| Sage agent | Extended with Workflows J, K |
| LEARNINGS.md | Promotion target for patterns |
| .claude/skills/ | May extract new skills |
| Supervisor | Session end prompts |
| WORKFLOW_STATE | Memory entry tracking |
| PEP 723 scripts | log-session.py pattern |

### C: Related Documents

| Document | Purpose |
|----------|---------|
| `agent_memory_report.md` | Research findings |
| `agent_memory_plan.md` | Implementation plan |
| `agent_memory_TDD.md` | Technical design |
| `.claude/agents/sage.md` | Sage agent definition |
| `docs/reference/LEARNINGS.md` | Pattern repository |

---

*PRD prepared by Product Manager persona*
*Review date: 2026-02-01*
