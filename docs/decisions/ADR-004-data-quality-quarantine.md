# ADR-004: Data Quality Quarantine Pattern with Macros

**Status**: Approved
**Date**: 2026-02-01
**Decision Makers**: Architect, Code Reviewer, Developer
**Context**: v0.8 Phase 5 - Data Quality Enhancement

---

## Context

The dbt project had 2 failing data quality tests:

1. **Encounter timestamp validation** - 1 encounter with end_at < start_at
2. **Medication date validation** - 5 medications with invalid date sequences

Traditional approaches to handle data quality violations:

- **Fail hard**: Tests block deployment (breaks CI/CD)
- **Warn only**: Tests pass but violations are invisible
- **Delete bad data**: Loss of evidence for root cause analysis
- **Manual fixes**: Not scalable, requires human intervention

The project needed a systematic approach to:
- Detect violations at the earliest layer (staging)
- Preserve evidence for investigation
- Filter bad data from downstream analytics
- Monitor data quality health over time

## Decision

**Adopt a macro-based data quality quarantine pattern** that:

1. Flags invalid records at staging with individual validation rules
2. Isolates quarantined records in dedicated intermediate tables
3. Filters quarantined data from all downstream marts
4. Provides analytics summary for monitoring

**Three core macros**:

1. `add_dq_flags(source_cte, validations)` - Adds validation columns
2. `quarantine_filter(enabled=true)` - Generates WHERE clause
3. `generate_quarantine_model(source_model)` - Creates quarantine tables

## Rationale

### Options Considered

| Criterion | Macro Pattern | Inline SQL | dbt Tests Only | External Tool |
|-----------|---------------|------------|----------------|---------------|
| Code Reuse | **Excellent** | Poor | N/A | N/A |
| Debugging | **Individual flags** | Single boolean | No visibility | Good |
| Extensibility | **Easy** | Manual copy | Hard | Vendor lock |
| Performance | Good | **Best** | N/A | External dependency |
| Learning Value | **High** | Medium | Low | Medium |

### Why Macros Over Inline SQL

**Individual validation flags** enable debugging:
```sql
-- Macro approach: See which rule failed
select
    encounter_id,
    valid_encounter_timestamps,  -- false
    no_future_encounter_dates,   -- true
    failed_dq_tests              -- ['valid_encounter_timestamps']
from int_dq_quarantine__encounters
```

vs.

```sql
-- Inline approach: Only know it failed
select encounter_id, is_dq_valid  -- false (but why?)
from stg_encounters
```

**Consistency across entities**: One macro definition ensures all models follow the same pattern.

**Extensibility**: Adding quarantine to a new entity requires ~10 lines:
```sql
with_dq_flags as (
    {{ add_dq_flags(source_cte='renamed', validations={...}) }}
)
```

### Why Not dbt Tests Alone

dbt tests are binary (pass/fail) and don't support:
- Partial failures (some records valid, some invalid)
- Filtering bad data from downstream models
- Aggregating validation failures for analysis

### Why Not External Tool

Tools like Great Expectations or Soda provide rich DQ features but:
- Add external dependencies
- Require separate deployment/maintenance
- Don't integrate natively with dbt DAG
- Overkill for a learning project with 6 violations

## Architecture

### Data Flow

```
STAGING (+DQ Flags)
├─ stg_synthea__encounters
│  ├─ is_dq_valid = true  ──> fct_encounters ──> Analytics
│  └─ is_dq_valid = false ──> int_dq_quarantine__encounters ──> mart_dq_summary
│
└─ stg_synthea__medications
   ├─ is_dq_valid = true  ──> fct_clinical_events ──> Analytics
   └─ is_dq_valid = false ──> int_dq_quarantine__medications ──> mart_dq_summary
```

### Macro Design

**`add_dq_flags()`**:
- Input: source CTE name, dict of {validation_name: sql_condition}
- Output: SELECT with original columns + individual flags + is_dq_valid + failed_dq_tests[]
- Helper macros: `_all_validations_pass()`, `_collect_failed_tests()`

**`quarantine_filter()`**:
- Input: enabled (bool), field_name (string)
- Output: `WHERE is_dq_valid = true`
- Toggleable for debugging

**`generate_quarantine_model()`**:
- Input: source_model (string), description (string)
- Output: Complete SQL selecting `WHERE is_dq_valid = false`
- Auto-applies quarantine tags

### Validation Strategy

**Staging layer validations**:
- Timestamp/date sequence rules (end >= start)
- Future date checks (start <= current)
- Historical plausibility (dates after 1900)
- Null handling (end can be null, but if present must be valid)

**Why at staging**: Earliest detection point, before any transformations or joins.

## Consequences

### Positive

1. **Zero test failures**: All 425 tests pass (was 405 PASS, 2 ERROR)
2. **Visibility preserved**: Quarantined records in dedicated tables for investigation
3. **Code reuse**: 3 macros eliminate ~100 lines of duplicated logic
4. **Extensibility**: Pattern ready for conditions, procedures, observations
5. **Monitoring**: `mart_dq_summary` tracks quarantine rates over time
6. **Debugging**: Individual validation flags show exact failure reason
7. **Clean analytics**: Downstream marts guaranteed valid data only

### Negative

1. **Mild over-engineering**: 3 macros for 2 entities is slightly ahead of need
2. **DuckDB-specific**: `list_value()` and `filter()` syntax not portable
3. **Build time increase**: +20% (2.0s → 2.4s for full build)
4. **Learning curve**: Team must understand macro abstraction

### Mitigation

| Negative | Mitigation |
|----------|------------|
| Over-engineering | Justified by extensibility need; well-documented |
| DuckDB-specific | Acceptable for single-DB learning project |
| Build time | 20% increase well below 30% threshold |
| Learning curve | Macro README.md with examples; reusable pattern |

## Metrics

### Before Implementation
- Models: 28
- Tests: 405 PASS, 2 ERROR, 3 WARN
- Quarantined records: None (invisible)

### After Implementation
- Models: 31 (+3 quarantine tables)
- Tests: 423 PASS, 0 ERROR, 2 WARN (+18 tests)
- Quarantined records: 6 (1 encounter, 5 medications)
- Quarantine rate: 0.006% (6 / 96,335 total records)

### Code Metrics
- Macros created: 3 (~70 lines total)
- Files created: 8
- Files modified: 8
- Line savings: ~60% reduction vs. inline approach

## Alternatives Not Chosen

### Option A: Inline Validation (Simpler)

**Approach**: Single `is_dq_valid` boolean in staging models, no macros.

```sql
-- Inline example
select
    *,
    (encounter_end_at >= encounter_start_at
     and encounter_start_at <= current_timestamp) as is_dq_valid
from renamed
```

**Why not chosen**:
- No individual validation flags (harder debugging)
- No `failed_dq_tests` array (can't aggregate failure reasons)
- Duplicated logic across models
- Less valuable for learning project

### Option C: dbt-expectations Only

**Approach**: Use dbt_expectations tests with custom failure handling.

**Why not chosen**:
- Tests are post-materialization (too late to filter)
- No built-in quarantine table generation
- Can't filter based on test results in downstream models
- Requires complex custom schema tests

### External DQ Tools (Great Expectations, Soda, Monte Carlo)

**Why not chosen**:
- External dependencies and setup complexity
- Separate deployment pipeline
- Not deeply integrated with dbt DAG
- Overkill for 6 violations in learning project

## Implementation Notes

### Files Created

**Macros** (`macros/data_quality/`):
- `add_dq_flags.sql` - Core validation macro
- `quarantine_filter.sql` - WHERE clause generator
- `generate_quarantine_model.sql` - Quarantine table generator
- `README.md` - Usage documentation

**Models** (`models/intermediate/quarantine/`):
- `int_dq_quarantine__encounters.sql`
- `int_dq_quarantine__medications.sql`
- `_quarantine__models.yml` - Schema documentation

**Analytics** (`models/marts/analytics/`):
- `mart_dq_summary.sql` - DQ monitoring table

### Files Modified

**Staging models**:
- `stg_synthea__encounters.sql` - Added `with_dq_flags` CTE
- `stg_synthea__medications.sql` - Added `with_dq_flags` CTE

**Downstream models**:
- `fct_encounters.sql` - Applied `{{ quarantine_filter() }}`
- `fct_clinical_events.sql` - Applied filter + valid_encounters CTE
- `int_encounters__enriched.sql` - Applied filter

### Usage Pattern

**Step 1**: Add DQ flags to staging
```sql
with_dq_flags as (
    {{ add_dq_flags(
        source_cte='renamed',
        validations={
            'valid_timestamps': 'end_at >= start_at',
            'no_future_dates': 'start_at <= current_timestamp'
        }
    ) }}
)
```

**Step 2**: Create quarantine table
```sql
{{ config(materialized='table', tags=['quarantine', 'data_quality']) }}
{{ generate_quarantine_model(source_model='stg_my_entity') }}
```

**Step 3**: Filter in downstream
```sql
with entities as (
    select * from {{ ref('stg_my_entity') }}
    {{ quarantine_filter() }}
)
```

## DuckDB-Specific Features

This implementation uses DuckDB-specific syntax:

**Array construction**:
```sql
-- DuckDB
list_value(case when not valid then 'rule_name' else null end, ...)

-- Snowflake equivalent
ARRAY_CONSTRUCT(case when not valid then 'rule_name' else null end, ...)

-- BigQuery equivalent
[case when not valid then 'rule_name' else null end, ...]
```

**Conditional aggregation**:
```sql
-- DuckDB
count(*) filter (where is_dq_valid = false)

-- Standard SQL
sum(case when is_dq_valid = false then 1 else 0 end)
```

For multi-database portability, these would need adapter-specific implementations.

## Monitoring & Alerting

### Quarantine Rate Threshold

**Recommendation**: Alert if `quarantine_rate_pct > 1%`

**Current state** (v0.8):
- Encounters: 0.00% (1 / 53,346)
- Medications: 0.01% (5 / 42,989)
- Both well below threshold ✅

### Metrics to Track

1. **Quarantine trend**: Track `mart_dq_summary` over time
2. **Failed validation breakdown**: Use `failed_dq_tests` for root cause
3. **Entity-level rates**: Monitor each entity type separately
4. **Alert on spikes**: >10x increase in quarantine rate

### Example Queries

**Quarantine summary**:
```sql
select * from {{ ref('mart_dq_summary') }}
order by quarantine_rate_pct desc
```

**Failed validation distribution**:
```sql
select
    unnest(failed_dq_tests) as failed_validation,
    count(*) as failure_count
from {{ ref('int_dq_quarantine__encounters') }}
group by 1
order by 2 desc
```

**Quarantine details**:
```sql
select
    encounter_id,
    encounter_start_at,
    encounter_end_at,
    failed_dq_tests
from {{ ref('int_dq_quarantine__encounters') }}
```

## Related Decisions

- **DBT_TESTING_STANDARDS.md** - General testing philosophy
- **ADR-003** - dbt for PM analytics (could consume DQ metrics)

## Review Cycle

This decision should be reviewed:

- After extending to 3+ additional entities (assess macro ROI)
- If quarantine rate exceeds 1% (may need auto-remediation)
- If migrating to multi-database setup (portability concerns)
- After 6 months of production use

## Future Enhancements (Out of Scope for v0.8)

1. **Auto-remediation**: Macros to fix common violations (trim whitespace, coalesce nulls)
2. **Historical tracking**: SCD Type 2 for quarantine trend analysis
3. **Alert integration**: Email/Slack when quarantine rate exceeds threshold
4. **Dashboard**: Quarantine metrics in BI tool
5. **Multi-database support**: Adapter-specific macro implementations
6. **Sampling**: For large datasets, quarantine sample instead of full set

---

**Approval**: Approved (Code Reviewer, Architect, Developer)
**Implementation Date**: 2026-02-01
**Review Date**: 2026-08-01 (6 months)
