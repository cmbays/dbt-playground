# TDD-001: dbt Project Architecture

## Overview

**Source PRD**: N/A (Infrastructure initialization)
**Author**: Technical Architect
**Status**: Approved
**Created**: 2026-01-28
**Updated**: 2026-01-28

### Summary

This TDD defines the technical architecture for initializing a dbt project with DuckDB and Synthea healthcare data. It validates the architectural decisions in the initialization plan, establishes technical standards for the agent team, and identifies risks and mitigations.

---

## Architecture Decisions

### ADR-1: Database Selection (DuckDB)

**Status**: Approved

**Context**: The project needs a database for analytics development that supports:

- Zero infrastructure overhead for learning environment
- Fast analytical queries
- Native CSV import for Synthea data
- Compatibility with dbt-mcp tooling

**Decision**: Use DuckDB as the primary database.

**Rationale**:

| Criterion | DuckDB | PostgreSQL | SQLite |
|-----------|--------|------------|--------|
| Setup Complexity | None (embedded) | Docker/Install | None |
| Analytical Performance | Excellent (columnar) | Good | Poor |
| CSV Import | Native `read_csv_auto()` | COPY command | Extension |
| dbt Adapter | dbt-duckdb | dbt-postgres | dbt-sqlite |
| MCP Compatibility | Excellent | Good | Limited |
| Production Similarity | Low | High | Very Low |

**Consequences**:

- **Positive**: Immediate productivity, no DevOps overhead, fast iteration
- **Positive**: Direct CSV reading simplifies data loading
- **Negative**: SQL dialect differences from production databases (PostgreSQL)
- **Negative**: Less relevant for production deployment skills
- **Mitigation**: Document DuckDB-specific syntax; plan PostgreSQL phase later

**Verdict**: DuckDB is the correct choice for this learning phase. The zero-infrastructure benefit outweighs production similarity concerns.

---

### ADR-2: Three-Layer Model Architecture

**Status**: Approved

**Context**: dbt projects require a layered architecture for maintainability and clarity.

**Decision**: Adopt staging -> intermediate -> marts architecture (Kimball-inspired).

**Architecture Diagram**:

```
                    ┌─────────────────────────────────────────────────────┐
                    │                   DATA FLOW                         │
                    └─────────────────────────────────────────────────────┘

    ┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │  SOURCE  │     │   STAGING    │     │ INTERMEDIATE │     │    MARTS     │
    │  (CSV)   │────▶│   (stg_)     │────▶│   (int_)     │────▶│  (dim_/fct_) │
    └──────────┘     └──────────────┘     └──────────────┘     └──────────────┘
         │                  │                    │                    │
    Raw Synthea        Clean &            Business Logic         Analytics-
    CSV files         Rename               Enrichment            Ready Tables
                        │                    │                    │
                   - Type casting      - Joins across         - Dimensional
                   - Naming standards    sources                 models
                   - NULL handling     - Calculations         - Fact tables
                   - Source isolation  - Data quality         - Aggregations
```

**Layer Responsibilities**:

| Layer | Prefix | Materialization | Purpose |
|-------|--------|-----------------|---------|
| Staging | `stg_` | View | 1:1 with source, clean and rename |
| Intermediate | `int_` | View | Business logic, joins, enrichment |
| Marts | `dim_`/`fct_` | Table | Analytics-ready, optimized for queries |

**Consequences**:

- **Positive**: Clear separation of concerns
- **Positive**: Industry-standard pattern (Kimball methodology)
- **Positive**: Easier debugging (trace data through layers)
- **Negative**: More files to maintain
- **Mitigation**: Use dbt documentation and lineage graphs

**Verdict**: Correct architecture. The three-layer approach is the dbt community standard.

---

### ADR-3: MCP Integration Strategy

**Status**: Approved with Caveats

**Context**: dbt-mcp enables AI agents to interact with dbt projects.

**Decision**: Integrate dbt-mcp as the primary agent interface.

**Capabilities**:

```
┌─────────────────────────────────────────────────────────────┐
│                    dbt-mcp CAPABILITIES                     │
├──────────────┬──────────────────────────────────────────────┤
│  Discovery   │ get_all_models, get_model_details,          │
│              │ get_lineage, get_columns                    │
├──────────────┼──────────────────────────────────────────────┤
│  Execution   │ build, run, test, seed, docs               │
├──────────────┼──────────────────────────────────────────────┤
│  SQL         │ execute_sql, compile, text_to_sql           │
├──────────────┼──────────────────────────────────────────────┤
│  Generation  │ generate_model_yaml, generate_source,       │
│              │ generate_staging_model                       │
└──────────────┴──────────────────────────────────────────────┘
```

**Caveats**:

1. **Version Compatibility**: Verify dbt-mcp version compatibility with dbt-duckdb
2. **Error Handling**: MCP errors may not be as verbose as CLI; maintain fallback
3. **Rate Limiting**: Long-running dbt operations may timeout

**Consequences**:

- **Positive**: Natural language interaction with dbt
- **Positive**: Reduced context switching for agents
- **Negative**: Abstraction may hide useful error details
- **Mitigation**: Always verify via `dbt debug` and direct CLI when debugging

---

### ADR-4: Synthea as Data Source

**Status**: Approved

**Context**: Need realistic healthcare data for learning dimensional modeling.

**Decision**: Use Synthea synthetic healthcare data.

**Rationale**:

- **Free and Open**: No licensing or approval required
- **Realistic Structure**: Follows HL7 FHIR-like patterns
- **Appropriate Scale**: 500 patients provides meaningful data without performance issues
- **Community Support**: Existing dbt examples (Tuva Project) available for reference

**Data Characteristics**:

| Table | Grain | Est. Rows (500 patients) | Key Relationships |
|-------|-------|--------------------------|-------------------|
| patients | patient | 500 | PK: patient_id |
| encounters | encounter | ~5,000 | FK: patient_id, provider_id |
| conditions | diagnosis | ~3,000 | FK: patient_id, encounter_id |
| medications | prescription | ~2,000 | FK: patient_id, encounter_id |
| procedures | procedure | ~1,500 | FK: patient_id, encounter_id |
| observations | observation | ~50,000 | FK: patient_id, encounter_id |
| providers | provider | ~50 | PK: provider_id |
| organizations | organization | ~20 | PK: organization_id |
| payers | payer | ~10 | PK: payer_id |

**Consequences**:

- **Positive**: No data acquisition complexity
- **Positive**: Realistic healthcare domain for learning
- **Negative**: Synthetic data may lack real-world data quality issues
- **Mitigation**: Intentionally introduce data quality scenarios in tests

---

### ADR-5: Package Selection

**Status**: Approved with Prioritization

**Context**: dbt packages extend functionality for testing, utilities, and code generation.

**Decision**: Install packages in priority order:

| Priority | Package | Version | Purpose |
|----------|---------|---------|---------|
| 1 (MVP) | dbt_utils | 1.3.0 | Core utilities (surrogate_key, pivot, etc.) |
| 2 (MVP) | codegen | 0.12.1 | Generate YAML and base models |
| 3 (Quality) | dbt_expectations | 0.10.4 | Advanced data quality tests |
| 4 (Optional) | dbt_date | 0.10.1 | Date dimension generation |

**Installation Order**:

1. Start with `dbt_utils` + `codegen` only
2. Add `dbt_expectations` after basic models work
3. Add `dbt_date` only if building custom dim_date

**Rationale**: Minimize initial complexity. Add packages incrementally.

---

## Technical Standards

### SQL Style Guide

All models must follow these SQL conventions:

#### CTE Structure Pattern

```sql
-- Model: stg_synthea__patients.sql
-- Standard staging model structure

with source as (
    -- First CTE: Always named "source" for raw data
    select * from {{ source('synthea_raw', 'patients') }}
),

renamed as (
    -- Second CTE: Rename and type cast
    select
        -- Primary key first
        id as patient_id,

        -- Group related columns with comments
        -- Demographics
        first as first_name,
        last as last_name,
        cast(birthdate as date) as birth_date,

        -- Metadata column last
        current_timestamp as _loaded_at

    from source
)

-- Final select: Always from last CTE
select * from renamed
```

#### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Staging models | `stg_{source}__{table}` | `stg_synthea__patients` |
| Intermediate models | `int_{entity}__{verb}` | `int_encounters__enriched` |
| Dimension models | `dim_{entity}` | `dim_patients` |
| Fact models | `fct_{event}` | `fct_encounters` |
| Columns (staging) | snake_case, descriptive | `birth_date`, `encounter_id` |
| Primary keys | `{entity}_id` | `patient_id` |
| Foreign keys | `{related_entity}_id` | `provider_id` |
| Timestamps | `{event}_at` or `{event}_timestamp` | `created_at` |
| Metadata | `_{name}` (underscore prefix) | `_loaded_at` |

#### SQL Formatting Rules

1. **Lowercase keywords**: `select`, `from`, `where` (not `SELECT`, `FROM`)
2. **Trailing commas**: Place commas at end of lines
3. **One column per line**: In select statements
4. **Indentation**: 4 spaces
5. **Line length**: Max 100 characters
6. **CTE naming**: Lowercase, descriptive (`source`, `renamed`, `filtered`)

#### DuckDB-Specific Patterns

```sql
-- CSV reading (DuckDB-specific)
select * from read_csv_auto('path/to/file.csv')

-- Date functions (verify compatibility)
date_diff('year', start_date, end_date)  -- DuckDB syntax
-- vs PostgreSQL: date_part('year', age(end_date, start_date))

-- Type casting
cast(column as date)  -- Standard SQL, works in DuckDB
column::date          -- PostgreSQL shorthand, may not work
```

**Important**: Document all DuckDB-specific SQL in model descriptions for future PostgreSQL migration.

---

### Testing Strategy

#### Required Tests by Layer

| Layer | Required Tests | Optional Tests |
|-------|----------------|----------------|
| Staging | `unique`, `not_null` on PKs | `accepted_values` for enums |
| Intermediate | Referential integrity | Row count validation |
| Marts | All of above + business rules | Freshness, distribution |

#### Test File Organization

```yaml
# models/staging/synthea/_synthea__models.yml
version: 2

models:
  - name: stg_synthea__patients
    description: Cleaned patient demographics from Synthea
    columns:
      - name: patient_id
        description: Unique patient identifier (UUID)
        data_tests:
          - unique
          - not_null
      - name: gender
        data_tests:
          - accepted_values:
              values: ['M', 'F']
```

#### Test Categories

1. **Schema Tests** (in YAML): `unique`, `not_null`, `accepted_values`, `relationships`
2. **Generic Tests** (from packages): `dbt_utils.unique_combination_of_columns`
3. **Singular Tests** (in `/tests/`): Custom SQL assertions

#### Minimum Test Coverage

- Every staging model: PK uniqueness and not null
- Every fact table: FK relationships to dimensions
- Every dimension: SCD validation (if applicable)

---

### Documentation Requirements

#### Model Description Template

Every model YAML entry must include:

```yaml
models:
  - name: model_name
    description: |
      **Purpose**: What this model provides
      **Grain**: One row per [entity]
      **Update Frequency**: [How often refreshed]
      **Owner**: [Agent/team responsible]

      ## Business Context
      [Why this model exists, what questions it answers]

      ## Key Assumptions
      - Assumption 1
      - Assumption 2
```

#### Column Documentation

At minimum, document:

- All primary keys
- All foreign keys
- Any calculated fields (with formula)
- Any columns with business logic

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| DuckDB SQL dialect incompatibility with future PostgreSQL | Medium | Medium | Document DuckDB-specific syntax; create compatibility layer |
| Synthea data generation fails (Java issues) | Medium | Low | Provide pre-generated sample data download option |
| dbt-mcp version conflicts | Low | High | Pin package versions; test integration before agent workflows |
| Large observation table performance | Low | Medium | Add materialization hints; consider incremental models |
| Agent generates invalid SQL | Medium | Low | Always run `dbt compile` before `dbt run`; validate in MCP |
| Loss of data between sessions (DuckDB file) | Low | High | Document database file location; add to gitignore with sample |

---

## Agent Team Guidelines

### For data-modeler (Dimensional Design)

**Responsibilities**:

- Design dimensional models following Kimball methodology
- Define grain for each fact table
- Identify slowly changing dimensions
- Create entity relationship diagrams

**Constraints**:

- Must use approved naming conventions (see SQL Style Guide)
- Must document business keys vs surrogate keys
- Must specify SCD type for each dimension (Type 1 or Type 2)

**Checklist before handoff**:

- [ ] Grain clearly defined
- [ ] All relationships documented
- [ ] Naming follows conventions
- [ ] ERD diagram created (optional but recommended)

---

### For dbt-developer (Implementation)

**Responsibilities**:

- Implement models following TDD pattern
- Write SQL following style guide
- Add required tests
- Create model documentation

**Workflow**:

```
1. Receive model design from data-modeler
2. Create staging model first (1:1 with source)
3. Run `dbt compile` to verify syntax
4. Run `dbt run --select model_name` to build
5. Add tests in YAML
6. Run `dbt test --select model_name`
7. Document in YAML
8. Verify lineage with `dbt docs generate`
```

**MCP Tool Usage**:

```
# Use these dbt-mcp tools:
- generate_staging_model: Create initial staging model
- compile: Verify SQL before running
- run: Build the model
- test: Run data tests
- get_lineage: Verify dependencies
```

**Constraints**:

- Never skip `dbt compile` before `dbt run`
- Always add tests before marking complete
- Document all columns, not just keys

---

### For dbt-tester (Quality Assurance)

**Responsibilities**:

- Review test coverage
- Add advanced data quality tests (dbt_expectations)
- Create singular tests for business rules
- Validate data after model runs

**Test Types to Consider**:

```yaml
# Basic tests (always include)
- unique
- not_null
- relationships

# Advanced tests (add as needed)
- dbt_expectations.expect_column_values_to_be_between
- dbt_expectations.expect_column_values_to_match_regex
- dbt_expectations.expect_table_row_count_to_be_between
```

**Constraints**:

- Every staging model needs PK tests
- Every fact table needs FK relationship tests
- Document test failures with clear error messages

---

### For dbt-documenter (Documentation)

**Responsibilities**:

- Ensure all models have descriptions
- Ensure all columns are documented
- Create and maintain the dbt docs site
- Document business context and usage

**Workflow**:

```
1. Run `dbt docs generate` after model changes
2. Review generated documentation site
3. Add missing descriptions
4. Add business context to key models
5. Verify lineage graph is accurate
```

**Constraints**:

- Use markdown in descriptions for formatting
- Include grain in every model description
- Document owner/responsible party

---

## Implementation Sequence

1. [x] **Phase 1: Environment Setup**
   - Install dbt-duckdb adapter
   - Configure profiles.yml
   - Update .mcp.json for dbt-mcp

2. [ ] **Phase 2: Data Acquisition**
   - Generate Synthea data (500 patients)
   - Place CSVs in dbt_project/data/synthea/
   - Verify file structure

3. [ ] **Phase 3: Project Initialization**
   - Run `dbt init dbt_project`
   - Configure dbt_project.yml
   - Install packages (dbt deps)
   - Verify with `dbt debug`

4. [ ] **Phase 4: Staging Layer**
   - Create source definitions
   - Implement 9 staging models
   - Add PK/FK tests
   - Run `dbt run --select staging`

5. [ ] **Phase 5: Marts Layer**
   - Create dim_patients
   - Create dim_providers
   - Create dim_date (optional)
   - Create fct_encounters
   - Add relationship tests

6. [ ] **Phase 6: Verification**
   - Run full `dbt run`
   - Run full `dbt test`
   - Generate and review docs
   - Test MCP integration

---

## Security Considerations

Even with synthetic data, establish good security patterns:

1. **Gitignore Sensitive Items**:

   ```gitignore
   # Database files
   *.duckdb
   *.duckdb.wal

   # Raw data
   dbt_project/data/

   # dbt artifacts
   dbt_project/target/
   dbt_project/logs/
   dbt_project/dbt_packages/

   # Profile with credentials
   dbt_project/profiles.yml
   ```

2. **PII Handling Pattern**: Even in synthetic data, treat SSN/names as PII:

   ```sql
   -- In staging models, prepare for production patterns
   ssn as ssn_masked,  -- In production: md5(ssn) or hash
   ```

3. **No Credentials in Code**: Use environment variables or profiles.yml (gitignored)

---

## Performance Considerations

1. **Materialization Strategy**:
   - Views for staging/intermediate (fast iteration)
   - Tables for marts (query performance)

2. **Observation Table**: 50K+ rows may need:
   - Incremental materialization
   - Partitioning by date
   - Careful join strategies

3. **Model Ordering**: Use `dbt run --select staging+ --exclude intermediate` for faster iteration

---

## Open Questions

1. **dim_date implementation**: Should we use dbt_date package or create custom?
   - Recommendation: Start without, add if needed for reporting

2. **Incremental models**: Should we implement for observations table now?
   - Recommendation: Defer until performance issues arise

3. **Source freshness**: Should we configure freshness checks?
   - Recommendation: Add after MVP, when refresh patterns are established

4. **Semantic layer**: Should we define metrics in the semantic layer?
   - Recommendation: Phase 2 enhancement after core models work

---

## Related

- **Plan**: `docs/plans/DBT-PROJECT-INITIALIZATION.md`
- **Architecture Recommendations**: `docs/plans/ARCHITECT-RECOMMENDATIONS.md`
- **Project Structure**: `docs/reference/PROJECT_STRUCTURE.md`
- **Testing Standards**: `docs/standards/TESTING.md`

---

*Last Updated: 2026-01-28*
