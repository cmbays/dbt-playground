---
audience: [multi-agent, architect, pm]
priority: high
size: small
dependencies: []
last_updated: 2026-01-31
status: active
tags: [reference, decisions, adr, architecture]
---

# ADR Index

## Purpose

This index provides quick discovery of Architecture Decision Records (ADRs) across the project. ADRs document significant technical decisions with their context, rationale, and consequences.

**Goal**: Find the rationale for any past decision in under 2 minutes.

## How to Use This Index

1. **Finding a decision**: Search or browse the table below
2. **Understanding a decision**: Follow the Location link to read the full ADR
3. **Adding a decision**: When writing a TDD, include an ADR section if the decision meets the significance criteria (see TDD-TEMPLATE.md)
4. **Updating this index**: Add a row when creating a new ADR; update status if superseded

## Quick Stats

| Metric | Count |
|--------|-------|
| Total ADRs | 5 |
| Approved | 5 |
| Superseded | 0 |
| Promoted to LEARNINGS.md | 0 |

---

## ADR Registry

| ADR | Title | Status | Location | Approved By | Date | Tags |
|-----|-------|--------|----------|-------------|------|------|
| ADR-1 | Database Selection (DuckDB) | Approved | [TDD-001](../specs/TDD-001-DBT-PROJECT-ARCHITECTURE.md#adr-1-database-selection-duckdb) | Architect | 2026-01-28 | infrastructure, database |
| ADR-2 | Three-Layer Model Architecture | Approved | [TDD-001](../specs/TDD-001-DBT-PROJECT-ARCHITECTURE.md#adr-2-three-layer-model-architecture) | Architect | 2026-01-28 | architecture, dbt |
| ADR-3 | MCP Integration Strategy | Approved | [TDD-001](../specs/TDD-001-DBT-PROJECT-ARCHITECTURE.md#adr-3-mcp-integration-strategy) | Architect | 2026-01-28 | integration, mcp |
| ADR-4 | Synthea as Data Source | Approved | [TDD-001](../specs/TDD-001-DBT-PROJECT-ARCHITECTURE.md#adr-4-synthea-as-data-source) | Architect | 2026-01-28 | data-source |
| ADR-5 | Package Selection | Approved | [TDD-001](../specs/TDD-001-DBT-PROJECT-ARCHITECTURE.md#adr-5-package-selection) | Architect | 2026-01-28 | packages, dbt |

---

## ADR Summary by Category

### Infrastructure & Database

| ADR | Decision | Key Trade-off |
|-----|----------|---------------|
| ADR-1 | DuckDB over PostgreSQL | Zero setup vs production similarity |

### Architecture & Patterns

| ADR | Decision | Key Trade-off |
|-----|----------|---------------|
| ADR-2 | Staging -> Intermediate -> Marts | More files vs clear separation |
| ADR-3 | dbt-mcp as primary agent interface | Natural language vs abstraction overhead |

### Data & Integration

| ADR | Decision | Key Trade-off |
|-----|----------|---------------|
| ADR-4 | Synthea synthetic healthcare data | Free/realistic vs lacking real-world quality issues |
| ADR-5 | Incremental package adoption | Minimal complexity vs delayed capabilities |

---

## Governance

### Significance Criteria

A decision warrants an ADR if it meets 2 or more of these criteria:

| Criterion | Description | Example |
|-----------|-------------|---------|
| Reversibility Cost | High effort to undo | Database choice, package adoption |
| Cross-Cutting Impact | Affects multiple features/layers | Naming conventions, error handling |
| Trade-off Significance | Material trade-offs evaluated | Performance vs simplicity |
| Constraint Creation | Limits future options | External dependency, API contract |
| External Dependency | Introduces 3rd party reliance | Package version, service integration |

### Approval Chain

| Impact Level | Criteria | Approver | Example |
|--------------|----------|----------|---------|
| High | Irreversible, budget impact, external commitment | Human (Chris) | Cloud service selection |
| Medium | Cross-cutting, significant trade-offs | Architect + PM | Package adoption |
| Low | Single-feature, easily reversible | Architect | Implementation approach |

---

## ADR Lifecycle

```text
Proposed --> Approved --> [Active use] --> Superseded (optional)
                |                              |
                +-- Rejected                   +--> New ADR references old
```

### Status Definitions

| Status | Meaning |
|--------|---------|
| Proposed | Under discussion, not yet approved |
| Approved | Decision made and active |
| Superseded | Replaced by a newer ADR (link to replacement) |
| Deprecated | No longer relevant but kept for history |

---

## Future: Pattern Promotion

When an ADR pattern is validated in 2+ implementations, it becomes a candidate for promotion to LEARNINGS.md. The Sage agent reviews completed features for promotion opportunities.

| ADR | Implementations | Promoted? |
|-----|-----------------|-----------|
| ADR-2 (Three-Layer) | All 28 models | Candidate |

---

## Related

- [TDD-TEMPLATE.md](../specs/TDD-TEMPLATE.md) - ADR format and examples
- [LEARNINGS.md](./LEARNINGS.md) - Promoted patterns
- [PRD-021](../specs/PRD-021-ADR-ADOPTION.md) - ADR Adoption Initiative

---

*Created: 2026-01-31 | Maintainer: Architect*
