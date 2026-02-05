# dbt-debug Command

Debug dbt model failures, test failures, and data quality issues with automatic session tracking and lineage analysis.

## Usage

```
/dbt-debug model <model_name> [--error "error message"]
/dbt-debug test <test_name> [--store-failures]
/dbt-debug freshness <source_name>
/dbt-debug lineage <model_name> [--depth N]
/dbt-debug schema <model_name> [--validate]
```

## Commands

### Debug Model Failure

```
/dbt-debug model stg_synthea__patients
/dbt-debug model fct_encounters --error "column patient_id does not exist"
```

Automatically:
1. Starts debug session with model context
2. Compiles model to inspect SQL
3. Checks upstream dependencies
4. Validates schema against source

Output:

```
dbt Model Debug: stg_synthea__patients
------
Debug Session: DBG-2026-02-05-001

Model Info:
  Type: view
  Schema: synthea
  Materialized: view
  Depends on: source('synthea', 'patients')

Compilation Check:
  Status: PASS
  SQL Path: target/compiled/dbt_playground/models/staging/synthea/stg_synthea__patients.sql

Upstream Status:
  source.synthea.patients: OK (fresh)

Schema Validation:
  Columns defined: 12
  Tests configured: 8

No obvious issues found.

Next Steps:
  1. Check the compiled SQL for logic errors
  2. Run '/dbt-debug lineage stg_synthea__patients' to trace dependencies
  3. Run '/dbt-run build --select stg_synthea__patients' to test

Debug session started. Use '/debug step' to log findings.
```

### Debug Model with Error Context

```
/dbt-debug model int_patient_encounters --error "Binder Error: column encounter_id not found"
```

Output:

```
dbt Model Debug: int_patient_encounters
------
Debug Session: DBG-2026-02-05-002
Error: Binder Error: column encounter_id not found

Analysis:
  [LIKELY ROOT CAUSE] Column reference issue detected

Column Analysis:
  Searching for 'encounter_id' in model...

  Found in model SQL:
    Line 15: encounter_id,
    Line 23: ON p.encounter_id = e.encounter_id

  Upstream columns:
    stg_synthea__encounters: has 'encounter_id' (OK)
    stg_synthea__patients: NO 'encounter_id' column (ISSUE)

Suggested Fix:
  The join on line 23 references encounter_id from stg_synthea__patients,
  but this column doesn't exist in that model.

  Check if you meant to join on patient_id instead, or add encounter_id
  to stg_synthea__patients.

Debug session started. Use '/debug step 3-root_cause' to confirm.
```

### Debug Test Failure

```
/dbt-debug test unique_fct_orders_order_id
/dbt-debug test not_null_stg_patients_patient_id --store-failures
```

Output:

```
dbt Test Debug: not_null_stg_patients_patient_id
------
Debug Session: DBG-2026-02-05-003
Test Type: not_null
Model: stg_patients
Column: patient_id

Test Result: FAIL (12 rows)

Failure Analysis:
  Running test with --store-failures...

  Failed Rows:
  +----+------------+---------------+
  | id | patient_id | source_row_id |
  +----+------------+---------------+
  | 1  | NULL       | row_12345     |
  | 2  | NULL       | row_12346     |
  | 3  | NULL       | row_12347     |
  +----+------------+---------------+
  ... (9 more rows)

  Source Investigation:
  - Source: synthea.patients
  - NULL patient_id found in source data

Root Cause Candidates:
  1. Source data quality issue (NULL IDs in source)
  2. Missing COALESCE/default in staging model
  3. Filtering issue removing valid rows

Suggested Actions:
  1. Check source freshness: /dbt-debug freshness synthea
  2. Add source test for not_null
  3. Filter NULLs in staging: WHERE patient_id IS NOT NULL

Debug session started. Log findings with '/debug step'.
```

### Debug Source Freshness

```
/dbt-debug freshness synthea
/dbt-debug freshness stripe --warn-after 6h
```

Output:

```
dbt Source Freshness: synthea
------
Debug Session: DBG-2026-02-05-004

Source: synthea
Tables Checked: 8

Results:
  +----------------------+------------------+----------+--------+
  | Table                | Last Updated     | Age      | Status |
  +----------------------+------------------+----------+--------+
  | patients             | 2026-02-05 08:00 | 2h       | PASS   |
  | encounters           | 2026-02-05 08:00 | 2h       | PASS   |
  | conditions           | 2026-02-04 20:00 | 14h      | WARN   |
  | medications          | 2026-02-05 08:00 | 2h       | PASS   |
  | observations         | 2026-02-03 12:00 | 46h      | ERROR  |
  +----------------------+------------------+----------+--------+

Issues Found:
  - conditions: 14h old (warn threshold: 12h)
  - observations: 46h old (error threshold: 24h)

Investigation:
  Checking upstream pipeline status...
  - Airflow DAG 'synthea_ingestion': Last run FAILED at 2026-02-04 20:00
  - Error: Connection timeout to source database

Root Cause: Airflow DAG failure blocking data refresh

Suggested Actions:
  1. Check Airflow logs for synthea_ingestion DAG
  2. Verify source database connectivity
  3. Re-run DAG once resolved

Debug session started for freshness investigation.
```

### Analyze Model Lineage

```
/dbt-debug lineage fct_encounters
/dbt-debug lineage dim_patients --depth 3
```

Output:

```
dbt Model Lineage: fct_encounters
------
Debug Session: DBG-2026-02-05-005

Lineage Graph (depth 2):
  source.synthea.encounters
      |
      v
  stg_synthea__encounters
      |
      +---> int_encounter_enriched
      |         |
      |         v
      |     fct_encounters  <-- TARGET
      |
      v
  stg_synthea__patients
      |
      v
  dim_patients

Upstream Models (3):
  - stg_synthea__encounters (view, healthy)
  - stg_synthea__patients (view, healthy)
  - int_encounter_enriched (table, healthy)

Downstream Models (2):
  - mart_utilization (table)
  - rpt_daily_encounters (view)

Test Coverage:
  Model Tests: 5 configured, 5 passing
  Upstream Tests: 12 configured, 12 passing

Schema Contracts:
  - fct_encounters: ENFORCED (contract defined)
  - int_encounter_enriched: NONE (consider adding)

Recommendations:
  1. All upstream healthy - issue likely in fct_encounters itself
  2. Consider adding contract to int_encounter_enriched
  3. Run '/dbt-debug model fct_encounters' for detailed analysis
```

### Validate Schema

```
/dbt-debug schema stg_synthea__patients
/dbt-debug schema fct_orders --validate
```

Output:

```
dbt Schema Validation: stg_synthea__patients
------
Debug Session: DBG-2026-02-05-006

YAML Definition: models/staging/synthea/_synthea__models.yml

Columns Defined: 12
Columns in Model: 14

Discrepancies:
  +------------------+----------+----------+
  | Column           | In YAML  | In Model |
  +------------------+----------+----------+
  | patient_id       | YES      | YES      |
  | first_name       | YES      | YES      |
  | middle_name      | NO       | YES      | <- UNDOCUMENTED
  | last_name        | YES      | YES      |
  | birth_date       | YES      | YES      |
  | death_date       | NO       | YES      | <- UNDOCUMENTED
  | ssn              | YES      | NO       | <- YAML ONLY
  | ...              |          |          |
  +------------------+----------+----------+

Issues:
  - 2 columns in model not documented in YAML
  - 1 column in YAML not found in model (possible rename?)

Test Coverage:
  - patient_id: unique, not_null (OK)
  - birth_date: not_null (OK)
  - middle_name: NO TESTS (add coverage)
  - death_date: NO TESTS (add coverage)

Suggested Actions:
  1. Add middle_name and death_date to YAML
  2. Remove or rename ssn column reference
  3. Add tests for undocumented columns

Run '/dbt-docs generate' after fixing to update documentation.
```

## Workflow Integration

### With /debug Command

`/dbt-debug` automatically starts a debug session:

```
/dbt-debug model stg_patients
  -> Starts session: DBG-2026-02-05-001
  -> Tags: dbt, model, stg_patients

# Continue with standard debug workflow
/debug step 3-root_cause "Missing join condition"
/debug end "Missing join" --time 20m
```

### With /qa Command

Debug failures found during QA:

```
/qa stg_patients+
  -> Test failures found

/dbt-debug test not_null_stg_patients_patient_id
  -> Investigates and logs to same session
```

### With Session Tracker

All dbt debug sessions are tracked:

```
/debug history --tags dbt
  -> Shows all dbt-related debug sessions

lessons-analyzer.py extract --category dbt
  -> Extracts dbt-specific patterns
```

## dbt-MCP Integration

When dbt-MCP is available, enhanced analysis:

| Feature | Without MCP | With MCP |
|---------|-------------|----------|
| Lineage | YAML parsing | Live manifest query |
| Compilation | `dbt compile` | Direct SQL access |
| Schema | YAML parsing | Catalog query |
| Run Status | Log parsing | Real-time status |

## Flags Reference

| Flag | Description | Default |
|------|-------------|---------|
| `--error` | Error message context | none |
| `--store-failures` | Store failed test rows | false |
| `--depth` | Lineage depth | 2 |
| `--validate` | Run validation checks | false |
| `--warn-after` | Freshness warn threshold | per-source |
| `--format` | Output format (table, json, mermaid) | table |
| `--select` | dbt selector syntax | none |

## Protocol Mapping for dbt Issues

| Issue Type | Suggested Protocol Path |
|------------|------------------------|
| Compilation Error | 1-reproduce -> 3-root_cause -> 5-implement -> 6-verify |
| Test Failure | 1-reproduce -> 2-blast_radius -> 3-root_cause -> 5-implement -> 6-verify -> 7-prevent |
| Freshness Issue | 1-reproduce -> 2-blast_radius -> 3-root_cause (often external) |
| Schema Drift | 2-blast_radius -> 4-fix_design -> 5-implement -> 7-prevent |

## Examples

### Quick Test Debug

```
# Test fails in CI
/dbt-debug test not_null_dim_customers_customer_id --store-failures

# Review failures
# Fix identified: source data issue

/debug step 3-root_cause "Source data contains orphaned records"
/debug end "Source data quality" --time 15m
```

### Model Compilation Debug

```
# Model fails to compile
/dbt-debug model int_patient_timeline --error "column does not exist"

# Command shows likely column mismatch
/debug step 3-root_cause "Column renamed in upstream model"
/debug step 5-implement "Updated reference to new column name"

/dbt-run build --select int_patient_timeline
# Success

/debug end "Column rename not propagated" --time 10m
```

### Complex Lineage Investigation

```
# mart_utilization producing wrong numbers
/dbt-debug lineage mart_utilization --depth 3

# Trace shows fct_encounters upstream
/dbt-debug model fct_encounters

# Find issue in intermediate
/dbt-debug schema int_encounter_enriched --validate

# Fix found
/debug step 3-root_cause "Duplicate rows from missing distinct"
/debug end "Missing DISTINCT in int_encounter_enriched" --time 45m
```

## Error Categories

Common dbt error patterns tracked by the analyzer:

| Category | Examples | Typical Root Cause |
|----------|----------|-------------------|
| schema_mismatch | Column not found | Upstream change not propagated |
| test_failure | Unique constraint violated | Data quality issue |
| freshness_error | Source stale | Pipeline/ETL failure |
| compilation_error | Jinja syntax error | Template issue |
| runtime_error | Query timeout | Performance/data volume |

## Related

- [[debug.md]] - General debug command
- [[dbt-run.md]] - Run dbt models
- [[dbt-test.md]] - Run dbt tests
- [[qa.md]] - QA workflow
- [[../agents/dbt-developer.md]] - dbt Developer persona
- [[../agents/debug-agent.md]] - Debug Agent persona
