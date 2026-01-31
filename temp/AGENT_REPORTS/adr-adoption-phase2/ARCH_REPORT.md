# Architect Report: ADR Adoption Phase 2

**Feature**: ADR-to-LEARNINGS Promotion Workflow
**PRD Reference**: PRD-021-ADR-ADOPTION.md (FR-5)
**Issue**: #108
**PR**: #109
**Date**: 2026-01-31
**Author**: Technical Architect (Claude Code Agent)

---

## Design Overview

Phase 2 establishes the pathway for proven ADR patterns to flow into LEARNINGS.md, creating a sustainable knowledge extraction pipeline.

### Architecture Principles

1. **Minimal Ceremony**: Promotion happens as part of existing Sage workflows, not as separate bureaucracy
2. **Evidence-Based**: 2+ implementations required before promotion (already in PRD-021)
3. **Audit Trail**: ADR_INDEX tracks promotion status; LEARNINGS.md references source ADRs
4. **Session Integration**: ADR review becomes part of session resume, not a separate step

---

## Implementation Design

### 1. LEARNINGS.md Pattern Promotion Section

**Location**: Add after line ~15 (after "Related Documentation" section)

**Content Structure**:

```markdown
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
| Three-Layer Model Architecture | ADR-2 | v0.3, v0.4, v0.5 | 2026-01-31 |
```

### 2. Sage Persona Workflow H

**Location**: Add after Workflow G (PR Learning Extraction) in `.claude/agents/sage.md`

**Content**:

```markdown
### Workflow H: ADR Pattern Promotion Review

Trigger: Session end OR explicit invocation with `sage: review ADRs for promotion`
Input: ADR_INDEX.md, feature implementation history

Process:
1. Scan ADR_INDEX.md for ADRs with "Approved" status
2. For each ADR, check if pattern appears in 2+ implementations:
   - Search codebase for pattern usage
   - Review CHANGELOG for feature mentions
   - Check temp/v*.md plans for pattern references
3. If 2+ implementations found:
   - Draft LEARNINGS.md entry with "Validated by: ADR-N"
   - Update ADR_INDEX.md "Promoted to" column
   - Log promotion in temp/LEARNING_DIGEST_[DATE].md
4. Report findings to Supervisor

Output: Promoted patterns added to LEARNINGS.md, ADR_INDEX.md updated
```

### 3. Historical ADR Backfill

**Approach**: Create `docs/specs/TDD-HISTORICAL.md` with minimal ADR sections

**Structure**:

```markdown
# TDD-HISTORICAL: Retrospective Architecture Decisions

Historical ADRs reconstructed from v0.3-v0.6 development.

## ADR-6: PR-Centric Development Workflow (v0.5)

**Status**: Approved (Historical)
**Context**: Need for better visibility into work-in-progress...
...

## ADR-7: Single-File Playground Architecture (v0.6)
...

## ADR-8: Inter-Agent Report Pattern (v0.6)
...
```

**ADR_INDEX.md Update**:

| ADR | Title | Status | Location | Approved By | Date | Tags |
|-----|-------|--------|----------|-------------|------|------|
| ADR-6 | PR-Centric Development Workflow | Approved (Historical) | TDD-HISTORICAL | Architect | 2026-01-30 | workflow |
| ADR-7 | Single-File Playground Architecture | Approved (Historical) | TDD-HISTORICAL | Architect | 2026-01-31 | architecture |
| ADR-8 | Inter-Agent Report Pattern | Approved (Historical) | TDD-HISTORICAL | Architect | 2026-01-31 | workflow, agents |

### 4. SESSION_SUMMARY Template Update

**Location**: `docs/templates/agent-reports/SESSION_SUMMARY.md`

**Add after "Open Questions" section**:

```markdown
## ADR Review

### ADRs Consulted This Session
- [ADR-N] - [reason consulted]

### ADR Candidates Identified
- [potential decision] - [meets N significance criteria]

### Promotion Candidates
- [ADR-N] - [implementation count: N]
```

---

## File Change Summary

| File | Action | Scope |
|------|--------|-------|
| `docs/reference/LEARNINGS.md` | EDIT | Add Pattern Promotion section (~30 lines) |
| `.claude/agents/sage.md` | EDIT | Add Workflow H (~25 lines) |
| `docs/specs/TDD-HISTORICAL.md` | CREATE | Historical ADRs 6-8 (~100 lines) |
| `docs/reference/ADR_INDEX.md` | EDIT | Add ADRs 6-8, update Quick Stats, add Promoted column |
| `docs/templates/agent-reports/SESSION_SUMMARY.md` | EDIT | Add ADR Review section (~15 lines) |

**Estimated Total**: ~170 lines across 5 files

---

## Trade-offs Considered

| Decision | Choice | Alternative | Rationale |
|----------|--------|-------------|-----------|
| Historical ADR location | TDD-HISTORICAL.md | Individual TDD files | Single file reduces clutter; historical ADRs don't need full TDD structure |
| Promotion tracking | ADR_INDEX.md column | Separate tracking file | Keeps all ADR metadata in one place |
| Session integration | SESSION_SUMMARY section | Separate ADR review template | Reduces template proliferation; keeps session context unified |

---

## Open Technical Questions

All resolved during design:

| Question | Resolution |
|----------|------------|
| How to mark historical vs. contemporary ADRs? | Add "(Historical)" suffix to Status |
| Should promotion be automated? | No - keep Sage-driven for judgment on context-specificity |
| How to handle ADR supersession? | Original ADR stays in index with "Superseded by" status |

---

## Validation Approach

1. **LEARNINGS.md**: Verify ADR-2 promotion entry is well-formed
2. **Sage Persona**: Verify YAML frontmatter remains valid
3. **TDD-HISTORICAL**: Verify ADR format matches TDD-001 examples
4. **ADR_INDEX.md**: Verify table formatting and link validity
5. **SESSION_SUMMARY**: Verify template renders correctly

---

## Recommendation

**PROCEED** with implementation. Design is complete and aligns with PRD-021 Phase 2 scope.

**Next Agent**: Developer (to implement the 5 file changes)

---

*Report generated: 2026-01-31*
