# TDD-XXX: [Feature Name]

## Overview

**Source PRD**: PRD-XXX
**Author**: [Architect name]
**Status**: Draft | Review | Approved | In Progress | Complete
**Created**: YYYY-MM-DD
**Updated**: YYYY-MM-DD

### Summary

[Brief technical summary of the implementation approach]

## Architecture Decisions

> **When to include ADRs**: Include an ADR for decisions that meet 2+ of the significance criteria below. Not every TDD needs ADRs - only include them for consequential decisions.

### Significance Criteria

Before writing an ADR, verify the decision meets at least 2 of these criteria:

| Criterion | Description | Example |
|-----------|-------------|---------|
| Reversibility Cost | High effort to undo | Database choice, package adoption |
| Cross-Cutting Impact | Affects multiple features/layers | Naming conventions, error handling pattern |
| Trade-off Significance | Material trade-offs were evaluated | Performance vs. simplicity, vendor choice |
| Constraint Creation | Limits future options | External dependency, API contract |
| External Dependency | Introduces 3rd party reliance | Package version, service integration |

**Quick test**: If the decision only affects this feature and is easily changeable later, it probably does not need an ADR.

### ADR-N: [Decision Title]

**Status**: Proposed | Approved | Superseded by ADR-M

**Context**: What situation requires a decision? What constraints exist?

**Decision**: What is the choice made?

**Rationale**:

| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| [Criterion 1] | [Value] | [Value] | [Value] |
| [Criterion 2] | [Value] | [Value] | [Value] |

**Consequences**:

- **Positive**: [Benefits of this decision]
- **Negative**: [Drawbacks or limitations]
- **Mitigation**: [How we address the negatives]

**Approval**: [Architect | PM + Architect | Human]

> **After creating an ADR**: Add an entry to [ADR_INDEX.md](../reference/ADR_INDEX.md)

---

### ADR Examples from TDD-001

<details>
<summary>Example: ADR-1 Database Selection (Low complexity)</summary>

**ADR-1: Database Selection (DuckDB)**

**Status**: Approved

**Context**: The project needs a database for analytics development that supports zero infrastructure overhead, fast analytical queries, and native CSV import.

**Decision**: Use DuckDB as the primary database.

**Rationale**:

| Criterion | DuckDB | PostgreSQL | SQLite |
|-----------|--------|------------|--------|
| Setup Complexity | None (embedded) | Docker/Install | None |
| Analytical Performance | Excellent (columnar) | Good | Poor |
| CSV Import | Native `read_csv_auto()` | COPY command | Extension |

**Consequences**:

- **Positive**: Immediate productivity, no DevOps overhead
- **Negative**: SQL dialect differences from production databases
- **Mitigation**: Document DuckDB-specific syntax; plan PostgreSQL phase later

**Approval**: Architect

</details>

<details>
<summary>Example: ADR-2 Architecture Pattern (Cross-cutting)</summary>

**ADR-2: Three-Layer Model Architecture**

**Status**: Approved

**Context**: dbt projects require a layered architecture for maintainability and clarity.

**Decision**: Adopt staging -> intermediate -> marts architecture (Kimball-inspired).

**Rationale**:

| Layer | Prefix | Materialization | Purpose |
|-------|--------|-----------------|---------|
| Staging | `stg_` | View | 1:1 with source, clean and rename |
| Intermediate | `int_` | View | Business logic, joins, enrichment |
| Marts | `dim_`/`fct_` | Table | Analytics-ready, optimized for queries |

**Consequences**:

- **Positive**: Clear separation of concerns, industry-standard pattern
- **Negative**: More files to maintain
- **Mitigation**: Use dbt documentation and lineage graphs

**Approval**: Architect

</details>

### Approval Chain Reference

| Impact Level | Criteria | Approver | Example |
|--------------|----------|----------|---------|
| High | Irreversible, budget impact, external commitment | Human (Chris) | Cloud service selection, major refactor |
| Medium | Cross-cutting, significant trade-offs | Architect + PM | Package adoption, architecture pattern |
| Low | Single-feature, easily reversible | Architect | Implementation approach, tool choice |

---

## Architecture

### High-Level Design

```
[ASCII diagram or description of architecture]
```

### Components

| Component | Purpose | Location |
|-----------|---------|----------|
| Component 1 | Description | `path/to/file` |

## Implementation Details

### Data Structures

```sql
-- Example schema or data structure
```

### API/Interface Design

```
Function/method signatures and contracts
```

### File Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `path/file.sql` | Create | New model |
| `path/existing.sql` | Modify | Add column |

## Options Analysis

### Option A: [Name]

**Approach**: [Description]

| Pros | Cons |
|------|------|
| Pro 1 | Con 1 |

**Complexity**: Low | Medium | High
**Risk**: Low | Medium | High

### Option B: [Name]

**Approach**: [Description]

| Pros | Cons |
|------|------|
| Pro 1 | Con 1 |

**Complexity**: Low | Medium | High
**Risk**: Low | Medium | High

### Recommendation

[Which option and why]

## Testing Strategy

### Unit Tests

- Test 1: [Description]
- Test 2: [Description]

### Integration Tests

- Test 1: [Description]

### Test Data Requirements

- [What test data is needed]

## Implementation Sequence

1. [ ] Step 1 - [Description]
2. [ ] Step 2 - [Description]
3. [ ] Step 3 - [Description]

## Security Considerations

- [Security consideration 1]
- [Security consideration 2]

## Performance Considerations

- [Performance consideration 1]

## Dependencies

- [Dependency 1]
- [Dependency 2]

## Open Questions

1. [Question 1]
2. [Question 2]

## Related

- **PRD**: [Link to PRD]
- **Issue**: [GitHub issue link]
- **ADR Index**: [docs/reference/ADR_INDEX.md](../reference/ADR_INDEX.md)
- **Diagram**: [Architecture diagram file]
