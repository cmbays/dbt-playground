# ADR-015: DuckDB for FS5 Metrics Database

**Date**: 2026-02-03
**Status**: Approved
**Approvers**: Architect, Supervisor
**Tags**: infrastructure, database, metrics, fs5

---

## Context

FS5 Metrics & Dashboard (Epic #146) requires a database for:

1. Storing adherence scores and their breakdowns
2. Tracking detected anomalies
3. Aggregating daily metrics
4. Serving dashboard queries

The original PRD-027 specified SQLite for this purpose, citing:
- Standard library availability
- Simple file-based storage
- SQL queryability for analytics
- WAL mode for data integrity

However, during FS5 implementation planning, the team identified an alternative approach.

## Decision

**Use DuckDB instead of SQLite for the FS5 Metrics database.**

### Key Factors

| Factor | SQLite | DuckDB | Winner |
|--------|--------|--------|--------|
| Already in project | No | Yes (`dbt-duckdb>=1.10.0`) | DuckDB |
| Query JSONL directly | No (requires ETL) | Yes (`read_json_auto()`) | DuckDB |
| Analytics performance | Row-based | Columnar | DuckDB |
| dbt integration | Separate engine | Same engine | DuckDB |
| Tech stack complexity | +1 technology | No change | DuckDB |

### Architecture Change

**Before (SQLite approach)**:

```
JSONL Files → Sync Script (ETL) → SQLite → Dashboard
```

**After (DuckDB approach)**:

```
JSONL Files → DuckDB Views (direct query) → Dashboard
```

The DuckDB approach eliminates the sync script entirely by using views that query JSONL files directly via `read_json_auto()`.

## Consequences

### Positive

1. **Reduced complexity**: No sync script to maintain (~20 hours saved)
2. **Real-time data**: Views always show current JSONL content
3. **Unified tooling**: Same database engine as dbt models
4. **No new dependencies**: DuckDB already installed
5. **Better analytics**: Columnar storage optimized for aggregations

### Negative

1. **No triggers**: DuckDB doesn't support triggers; application-layer logic required for `updated_at` timestamps and cascading updates
2. **Less ubiquitous**: SQLite is more widely known, but team is already using DuckDB
3. **Browser access**: Dashboard cannot query DuckDB directly; pre-generated JSON export required

### Neutral

1. **MVCC vs WAL**: DuckDB uses MVCC which provides similar data integrity guarantees to SQLite's WAL mode
2. **File locking**: Both require consideration for concurrent access; DuckDB handles this internally

## Alternatives Considered

### Alternative 1: SQLite (Original Plan)

**Pros**: Standard library, triggers, ubiquitous knowledge
**Cons**: Adds another database technology, requires sync script
**Rejected**: Complexity outweighs benefits when DuckDB already exists

### Alternative 2: Hybrid (SQLite + DuckDB)

**Pros**: Could use SQLite for writes, ATTACH to DuckDB for analytics
**Cons**: Adds complexity, two databases to maintain
**Rejected**: Unnecessary complexity

### Alternative 3: Pure File-Based (No Database)

**Pros**: Simplest approach
**Cons**: Complex queries become unwieldy, no aggregation support
**Rejected**: Metrics require SQL-level query capabilities

## Implementation Notes

1. Database location: `database/metrics/metrics.duckdb`
2. Schema: Views over JSONL + tables for computed data
3. Dashboard: Pre-generated JSON with polling
4. Testing: Temporary DuckDB databases in pytest fixtures

## Related

- [ADR-1: Database Selection (DuckDB)](../specs/TDD-001-DBT-PROJECT-ARCHITECTURE.md#adr-1-database-selection-duckdb) - Original DuckDB selection for dbt
- [ADR-10: SQLite for Cross-Session State](ADR-002-sqlite-state-layer.md) - Superseded PM state layer
- [PRD-027: Metrics & Dashboard](../specs/PRD-027-METRICS-DASHBOARD.md) - Original specification
- [DUCKDB_MIGRATION_REVIEW.md](../../temp/AGENT_REPORTS/fs5-metrics-dashboard/DUCKDB_MIGRATION_REVIEW.md) - Full analysis

---

*Approved by Architect on 2026-02-03*
*This ADR supersedes SQLite references in PRD-027 for FS5 implementation*
