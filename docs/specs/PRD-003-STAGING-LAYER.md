---
title: Staging Layer
prd_number: PRD-003
epic: E3-Staging-Layer
version: 0.3.0
status: draft
author: pm
created: 2026-01-28
last_updated: 2026-01-28
---

## Overview

### Problem Statement

Raw Synthea CSV data uses inconsistent naming conventions, uppercase column names, and lacks proper typing. A staging layer is needed to clean, rename, and type-cast source data before business logic is applied.

### Goal

Create 9 staging models that transform raw Synthea CSV data into clean, consistently named, properly typed views that serve as the foundation for dimensional modeling.

### Success Metrics

- All 9 staging models compile and run without errors
- `dbt test` passes for all staging models
- All models have 100% column documentation
- Consistent naming conventions applied (snake_case)
- Primary keys validated as unique and not null

---

## Requirements

### Functional Requirements

#### FR-1: Source Definition

**Priority**: P0 (Critical)

Create YAML source definition for Synthea data.

**Acceptance Criteria**:

- [ ] `_synthea__sources.yml` created in `models/staging/synthea/`
- [ ] All 9 source tables defined
- [ ] Primary key columns identified
- [ ] Basic tests on primary keys (unique, not_null)

**Source Definition Structure**:

```yaml
version: 2

sources:
  - name: synthea_raw
    description: Raw Synthea synthetic healthcare data loaded from CSV files
    schema: main
    tables:
      - name: patients
        description: Patient demographics and identifiers
        columns:
          - name: Id
            description: Unique patient identifier (UUID)
            data_tests:
              - unique
              - not_null
      # ... additional tables
```

#### FR-2: Staging Model - Patients

**Priority**: P0 (Critical)

Create `stg_synthea__patients.sql` to stage patient data.

**Acceptance Criteria**:

- [ ] Reads from CSV via `read_csv_auto()`
- [ ] All columns renamed to snake_case
- [ ] Appropriate data types cast
- [ ] `_loaded_at` metadata column added
- [ ] Documentation complete

**Column Mapping**:

| Source Column | Target Column | Type | Notes |
|---------------|---------------|------|-------|
| Id | patient_id | VARCHAR | Primary key |
| BIRTHDATE | birth_date | DATE | |
| DEATHDATE | death_date | DATE | Nullable |
| SSN | ssn_hash | VARCHAR | Would hash in production |
| FIRST | first_name | VARCHAR | |
| LAST | last_name | VARCHAR | |
| GENDER | gender | VARCHAR | |
| RACE | race | VARCHAR | |
| ETHNICITY | ethnicity | VARCHAR | |
| MARITAL | marital_status | VARCHAR | |
| ADDRESS | address | VARCHAR | |
| CITY | city | VARCHAR | |
| STATE | state | VARCHAR | |
| COUNTY | county | VARCHAR | |
| ZIP | zip_code | VARCHAR | |
| LAT | latitude | DOUBLE | |
| LON | longitude | DOUBLE | |
| HEALTHCARE_EXPENSES | total_healthcare_expenses | DECIMAL | |
| HEALTHCARE_COVERAGE | total_healthcare_coverage | DECIMAL | |

#### FR-3: Staging Model - Encounters

**Priority**: P0 (Critical)

Create `stg_synthea__encounters.sql` to stage encounter data.

**Acceptance Criteria**:

- [ ] All columns renamed to snake_case
- [ ] Timestamps properly typed
- [ ] Foreign keys preserved for joins
- [ ] Encounter class standardized

**Column Mapping**:

| Source Column | Target Column | Type |
|---------------|---------------|------|
| Id | encounter_id | VARCHAR |
| START | start_timestamp | TIMESTAMP |
| STOP | stop_timestamp | TIMESTAMP |
| PATIENT | patient_id | VARCHAR |
| ORGANIZATION | organization_id | VARCHAR |
| PROVIDER | provider_id | VARCHAR |
| PAYER | payer_id | VARCHAR |
| ENCOUNTERCLASS | encounter_class | VARCHAR |
| CODE | encounter_code | VARCHAR |
| DESCRIPTION | encounter_description | VARCHAR |
| BASE_ENCOUNTER_COST | base_encounter_cost | DECIMAL |
| TOTAL_CLAIM_COST | total_claim_cost | DECIMAL |
| PAYER_COVERAGE | payer_coverage | DECIMAL |
| REASONCODE | reason_code | VARCHAR |
| REASONDESCRIPTION | reason_description | VARCHAR |

#### FR-4: Staging Model - Conditions

**Priority**: P0 (Critical)

Create `stg_synthea__conditions.sql` to stage diagnosis data.

**Acceptance Criteria**:

- [ ] All columns renamed
- [ ] Date columns properly typed
- [ ] SNOMED codes preserved
- [ ] Patient and encounter linkage maintained

#### FR-5: Staging Model - Medications

**Priority**: P0 (Critical)

Create `stg_synthea__medications.sql` to stage prescription data.

**Acceptance Criteria**:

- [ ] All columns renamed
- [ ] Date/timestamp columns typed
- [ ] Cost columns as DECIMAL
- [ ] RxNorm codes preserved

#### FR-6: Staging Model - Procedures

**Priority**: P0 (Critical)

Create `stg_synthea__procedures.sql` to stage procedure data.

**Acceptance Criteria**:

- [ ] All columns renamed
- [ ] Procedure codes (SNOMED) preserved
- [ ] Cost columns as DECIMAL
- [ ] Patient and encounter linkage maintained

#### FR-7: Staging Model - Observations

**Priority**: P0 (Critical)

Create `stg_synthea__observations.sql` to stage vitals and lab results.

**Acceptance Criteria**:

- [ ] All columns renamed
- [ ] Observation values preserved (various types)
- [ ] LOINC codes preserved
- [ ] Units column maintained

#### FR-8: Staging Model - Providers

**Priority**: P1 (High)

Create `stg_synthea__providers.sql` to stage provider data.

**Acceptance Criteria**:

- [ ] All columns renamed
- [ ] Specialty codes preserved
- [ ] Organization linkage maintained

#### FR-9: Staging Model - Organizations

**Priority**: P1 (High)

Create `stg_synthea__organizations.sql` to stage facility data.

**Acceptance Criteria**:

- [ ] All columns renamed
- [ ] Address columns standardized
- [ ] Revenue column as DECIMAL

#### FR-10: Staging Model - Payers

**Priority**: P1 (High)

Create `stg_synthea__payers.sql` to stage insurance data.

**Acceptance Criteria**:

- [ ] All columns renamed
- [ ] Address columns standardized

#### FR-11: Model Documentation

**Priority**: P1 (High)

Create comprehensive model documentation.

**Acceptance Criteria**:

- [ ] `_synthea__models.yml` created
- [ ] All 9 models documented with descriptions
- [ ] All columns documented
- [ ] Schema tests defined (unique, not_null on PKs)

---

### Non-Functional Requirements

#### NFR-1: Consistent Naming

All staging models must follow `stg_synthea__[entity]` naming convention.

#### NFR-2: Materialization

Staging models should be materialized as views for development speed.

#### NFR-3: Idempotency

Models must be idempotent - running multiple times produces same result.

---

## User Stories

### US-1: Clean Source Data

**As a** data engineer
**I want** staging models that clean raw CSV data
**So that** downstream models have consistent, typed inputs

**Acceptance Criteria**:

- Column names are snake_case
- Data types are appropriate
- Nulls handled consistently

### US-2: Document Data Lineage

**As a** data analyst
**I want** to see where staging data comes from
**So that** I can trace data quality issues

**Acceptance Criteria**:

- Source references use `source()` macro
- Column descriptions explain transformations
- Lineage visible in dbt docs

### US-3: Test Data Quality

**As a** data engineer
**I want** tests on staging models
**So that** I catch data quality issues early

**Acceptance Criteria**:

- Primary keys tested for uniqueness
- Required columns tested for not_null
- Tests run as part of CI

---

## Technical Specifications

### Model Template

Each staging model follows this pattern:

```sql
-- models/staging/synthea/stg_synthea__[entity].sql

with source as (
    select * from read_csv_auto('data/synthea/[entity].csv')
),

renamed as (
    select
        -- Primary key
        Id as [entity]_id,

        -- Attributes (rename to snake_case)
        COLUMN_NAME as column_name,

        -- Type conversions
        cast(DATE_COLUMN as date) as date_column,
        cast(DECIMAL_COLUMN as decimal(18,2)) as decimal_column,

        -- Metadata
        current_timestamp as _loaded_at

    from source
)

select * from renamed
```

### Directory Structure

```text
models/staging/synthea/
├── _synthea__sources.yml      # Source definitions
├── _synthea__models.yml       # Model documentation
├── stg_synthea__patients.sql
├── stg_synthea__encounters.sql
├── stg_synthea__conditions.sql
├── stg_synthea__medications.sql
├── stg_synthea__procedures.sql
├── stg_synthea__observations.sql
├── stg_synthea__providers.sql
├── stg_synthea__organizations.sql
└── stg_synthea__payers.sql
```

### Testing Strategy

**Schema Tests** (in `_synthea__models.yml`):

```yaml
models:
  - name: stg_synthea__patients
    columns:
      - name: patient_id
        data_tests:
          - unique
          - not_null
      - name: birth_date
        data_tests:
          - not_null
```

**Data Tests** (future):

- Date range validation (no future birth dates)
- Referential integrity (encounters reference valid patients)
- Value range checks (costs are positive)

---

## Implementation Notes

### DuckDB CSV Reading

DuckDB's `read_csv_auto()` automatically infers types. Override when needed:

```sql
-- Explicit type specification if auto-detect fails
select * from read_csv(
    'data/synthea/patients.csv',
    header = true,
    columns = {
        'Id': 'VARCHAR',
        'BIRTHDATE': 'DATE',
        ...
    }
)
```

### Handling Large Files

`observations.csv` can be very large. Consider:

1. Using view materialization (no duplication)
2. Adding `limit` during development
3. Partitioning in marts layer if needed

### Null Handling

Synthea uses empty strings for nulls. Handle with:

```sql
nullif(trim(COLUMN_NAME), '') as column_name
```

---

## Agent Assignment

| Task | Agent | Notes |
|------|-------|-------|
| Source definition | data-modeler | YAML structure and tests |
| Model design | data-modeler | Column mapping decisions |
| patients model | dbt-developer | First model, establish pattern |
| encounters model | dbt-developer | Complex with FKs |
| conditions model | dbt-developer | |
| medications model | dbt-developer | |
| procedures model | dbt-developer | |
| observations model | dbt-developer | Large file handling |
| providers model | dbt-developer | |
| organizations model | dbt-developer | |
| payers model | dbt-developer | |
| Schema tests | dbt-tester | Add to models.yml |
| Documentation | dbt-documenter | Column descriptions |
| Code review | code-reviewer | Pattern consistency |

---

## Dependencies

### Upstream

- PRD-001: Environment Setup (dbt must be configured)
- PRD-002: Data Acquisition (CSV files must exist)

### Downstream

- PRD-004: Dimensional Models (consumes staging models)

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| CSV schema changes | High | Low | Document expected schema |
| Large observation file | Medium | Medium | Use views, test with sample |
| Inconsistent nulls | Medium | Medium | Standardize null handling |
| Type inference errors | Medium | Medium | Explicit casts where needed |

---

## Open Questions

1. Should we add `_source_file` column for lineage tracking?
2. Should staging models filter obviously invalid records?
3. Should we create a codegen script for repetitive model creation?

---

## References

- [dbt Staging Best Practices](https://docs.getdbt.com/guides/best-practices/how-we-structure/2-staging)
- [Synthea Data Dictionary](https://github.com/synthetichealth/synthea/wiki/CSV-File-Data-Dictionary)
- [DuckDB CSV Documentation](https://duckdb.org/docs/data/csv/overview)

---

*PRD Status: Draft - Ready for Review*
