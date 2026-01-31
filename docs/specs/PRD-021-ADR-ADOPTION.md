# PRD-021: ADR Adoption Initiative

## Overview

**Author**: Product Manager (Claude Code Agent System)
**Status**: Draft
**Created**: 2026-01-31
**Updated**: 2026-01-31

### Problem Statement

Technical decisions in this project are made but not systematically recorded. We have evidence of good decisions (TDD-001 contains embedded ADRs 1-5) but also evidence of decisions lost to conversation history:

1. **Decision Archaeology**: When revisiting past work, we spend time re-discovering why choices were made (e.g., "Why DuckDB over PostgreSQL?" is answered in TDD-001, but "Why metric marts over semantic layer?" requires finding old conversations)

2. **Repeated Debates**: Without recorded decisions, the same trade-offs get re-evaluated. The v0.5.5 semantic layer decision was re-debated because the original rationale was not formally captured.

3. **Onboarding Friction**: New agents (or returning agents with cleared context) lack access to decision history, leading to proposals that conflict with prior decisions.

4. **Pattern Promotion Gap**: Proven decisions should flow to LEARNINGS.md, but there is no systematic trigger. The "Context Window Discipline" pattern made it to LEARNINGS.md; many others did not.

**Validation**: The Architect consultation confirmed that we already practice ADR-like documentation in TDD-001, suggesting the overhead is acceptable when integrated naturally rather than imposed as ceremony.

### Goal

Formalize decision tracking to:

- Reduce decision archaeology time by 80% (decisions findable in <2 minutes)
- Eliminate repeated debates on settled questions
- Create clear pathway from "decision made" to "pattern proven"
- Maintain lightweight overhead that fits existing PRD/TDD workflow

### Reference

- Architect Consultation: Embedded ADRs + centralized index recommended
- Prior Art: TDD-001 ADRs 1-5 (database selection, architecture, MCP, data source, packages)
- Industry Pattern: Lightweight ADRs (Nygard format), decision logs, Y-statements

## User Stories

As a **returning agent** (or Claude session resuming work), I want to find the rationale for past decisions so that I can work within existing constraints without re-debating settled questions.

As an **Architect**, I want a lightweight way to record significant decisions so that the overhead does not discourage documentation but the decisions are findable.

As a **PM**, I want to know what decisions require my input so that I can prioritize stakeholder alignment on consequential choices.

As a **Sage (knowledge curator)**, I want a clear signal for when decisions should become LEARNINGS.md patterns so that proven approaches are systematically captured.

As a **human learner (Chris)**, I want to understand why the project evolved as it did so that I can apply these decision-making patterns to future projects.

As a **future maintainer**, I want to understand historical constraints so that I can safely change decisions when constraints evolve.

## Requirements

### Functional Requirements

#### FR-1: Embedded ADR Format in TDDs

Continue the pattern established in TDD-001: include ADRs inline within TDD documents.

**ADR Template**:

```markdown
### ADR-N: [Decision Title]

**Status**: Proposed | Approved | Superseded by ADR-M

**Context**: What situation requires a decision?

**Decision**: What is the choice made?

**Rationale**: Why this choice over alternatives? (Table format preferred)

**Consequences**:
- **Positive**: [benefits]
- **Negative**: [drawbacks]
- **Mitigation**: [how we address drawbacks]

**Approval**: [Architect | PM + Architect | Human]
```

**Acceptance Criteria**:

- [ ] ADR template documented in TDD-TEMPLATE.md
- [ ] Existing TDD-001 ADRs serve as examples
- [ ] Format supports optional "Superseded by" for decision evolution

#### FR-2: Centralized ADR Index

Create `docs/reference/ADR_INDEX.md` as a discovery mechanism.

**Index Structure**:

```markdown
# ADR Index

| ADR | Title | Status | Location | Approved By | Date |
|-----|-------|--------|----------|-------------|------|
| ADR-1 | Database Selection (DuckDB) | Approved | TDD-001 | Architect | 2026-01-28 |
| ADR-2 | Three-Layer Model Architecture | Approved | TDD-001 | Architect | 2026-01-28 |
```

**Acceptance Criteria**:

- [ ] ADR_INDEX.md created with existing TDD-001 ADRs
- [ ] Index includes location link for quick navigation
- [ ] Format supports filtering by status, approver, topic

#### FR-3: Decision Significance Criteria

Define when a decision warrants an ADR (avoid over-documenting).

**Significance Test** (2+ criteria = ADR warranted):

| Criterion | Description | Example |
|-----------|-------------|---------|
| Reversibility Cost | High effort to undo | Database choice, package adoption |
| Cross-Cutting Impact | Affects multiple features/layers | Naming conventions, error handling pattern |
| Trade-off Significance | Material trade-offs were evaluated | Performance vs. simplicity, vendor choice |
| Constraint Creation | Limits future options | External dependency, API contract |
| External Dependency | Introduces 3rd party reliance | Package version, service integration |

**Acceptance Criteria**:

- [ ] Significance criteria documented in TDD-TEMPLATE.md
- [ ] Architect uses criteria during TDD creation
- [ ] PM can challenge ADR necessity based on criteria

#### FR-4: Approval Chain Definition

Establish who approves decisions based on impact level.

| Impact Level | Criteria | Approver | Example |
|--------------|----------|----------|---------|
| High | Irreversible, budget impact, external commitment | Human (Chris) | Cloud service selection, major refactor |
| Medium | Cross-cutting, significant trade-offs | Architect + PM | Package adoption, architecture pattern |
| Low | Single-feature, easily reversible | Architect | Implementation approach, tool choice |

**Acceptance Criteria**:

- [ ] Impact levels documented with examples
- [ ] ADR template includes "Approval" field
- [ ] High-impact decisions surface for human review

#### FR-5: ADR-to-LEARNINGS Pipeline

Create explicit pathway for proven decisions to become patterns.

**Promotion Trigger**: ADR pattern validated in 2+ real implementations.

**Process**:

1. Sage reviews completed features for ADR patterns
2. If pattern applied 2+ times successfully, promote to LEARNINGS.md
3. LEARNINGS.md entry references originating ADRs
4. ADR index notes "Promoted to LEARNINGS.md"

**Acceptance Criteria**:

- [ ] Promotion criteria documented
- [ ] LEARNINGS.md entry template includes "Validated by ADRs" reference
- [ ] Review trigger added to session end workflow

### Non-Functional Requirements

1. **NFR-1**: ADR creation should add <5 minutes to TDD authoring
2. **NFR-2**: ADR lookup should take <2 minutes (index enables discovery)
3. **NFR-3**: Format must be human-readable (not just machine-parseable)
4. **NFR-4**: Works without external tools (markdown only)
5. **NFR-5**: Backward compatible with existing TDD-001 format

## Scope

### In Scope

**Phase 1 (v0.7 - Immediate)**:

- ADR template in TDD-TEMPLATE.md
- ADR_INDEX.md with TDD-001 entries
- Significance criteria documentation
- Approval chain documentation

**Phase 2 (v0.8 - Next Sprint)**:

- ADR-to-LEARNINGS promotion process
- Sage integration for pattern promotion
- Retrospective review of v0.3-v0.6 for missing ADRs

**Phase 3 (v0.9+ - Quarterly)**:

- ADR usage metrics (count, promotion rate)
- Template refinement based on usage
- FOR_CHRIS educational document on decision-making

### Out of Scope

- Standalone ADR directory (embedded in TDDs instead)
- ADR tooling/automation (stay markdown-native)
- Migrating all historical decisions (only significant ones worth archaeology)
- External ADR hosting or publishing

## Dependencies

- TDD-TEMPLATE.md must be updated (Architect)
- LEARNINGS.md must exist and be maintained (Sage)
- Session summary workflow (for promotion trigger)

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Decision discovery time | <2 minutes | Time to find rationale for past decision |
| ADR adoption rate | 100% of new TDDs with significant decisions | ADR_INDEX.md entries |
| Pattern promotion rate | 1+ patterns per quarter | LEARNINGS.md entries citing ADRs |
| Re-debate reduction | 0 repeated debates on indexed decisions | Qualitative (conversation review) |

## Open Questions

1. **Should we backfill ADRs for v0.3-v0.6 decisions?**
   - Recommendation: Only if we are actively re-debating them. Backfill on demand, not proactively.

2. **How do we handle ADRs that span multiple TDDs?**
   - Recommendation: ADR lives in the originating TDD; other TDDs reference it.

3. **What happens when a decision is superseded?**
   - Recommendation: Original ADR status changes to "Superseded by ADR-M"; new ADR explains why.

4. **Should standalone decisions (not tied to a TDD) get ADRs?**
   - Recommendation: Create an "ADR-only" section in ADR_INDEX.md for decisions without TDD context.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ADR location | Embedded in TDDs | Reduces file proliferation; keeps decision near technical context |
| Index format | Markdown table | Simple, no tooling required, sortable in editors |
| Promotion trigger | 2+ implementations | Prevents premature pattern extraction |
| Approval chain | 3 tiers | Balances rigor with velocity |

## Alignment Check

**Does this align with team culture?**

Yes. TDD-001 demonstrates the team already creates ADR-like content naturally. This initiative formalizes discovery (index) without adding ceremony to creation.

**Is the benefit worth the overhead?**

Yes, if we:

- Keep ADRs embedded (no separate files to manage)
- Only require ADRs for significant decisions (2+ criteria)
- Make the index a living document, not a bureaucratic gate

**What could go wrong?**

| Risk | Mitigation |
|------|------------|
| ADR ceremony slows TDD creation | Significance criteria prevents over-documentation |
| Index becomes stale | Architect adds to index as part of TDD completion |
| ADRs not consulted | Session resume checklist includes "review relevant ADRs" |
| Pattern promotion forgotten | Sage reviews at session end |

## Related

- **TDD-001**: Contains ADRs 1-5 as prior art
- **LEARNINGS.md**: Destination for proven patterns
- **TDD-TEMPLATE.md**: Will be updated with ADR section
- **PRD-016**: Agent context management (related workflow)
