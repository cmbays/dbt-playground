---
audience: [architect, developer]
status: approved
epic: E5 - Advanced Metrics & Aggregations
version: 1.0
last_updated: 2026-01-30
---

# TDD-005: Marts Layer Enhancements - Technical Design

## Overview

**Title**: Advanced Analytics Models for Healthcare Domain
**Scope**: 7-11 new models (dim_conditions, 4 fact tables, 3 views)
**Foundation**: Build on v0.4's dimensional architecture
**Patterns**: Kimball methodology, fact grain design, SCD patterns

## Architecture Overview

```
MARTS LAYER - v0.5 Enhancement Architecture
│
├── OPERATIONAL VIEWS (NEW)
│   ├── v_patient_current_conditions
│   │   └── Materialized: Yes | Grain: patient_id
│   ├── v_provider_active_patients
│   │   └── Materialized: Yes | Grain: provider_id
│   └── v_encounter_summary
│       └── Materialized: No (ephemeral)
│
├── ANALYTIC FACTS (NEW)
│   ├── fct_patient_summary
│   │   ├── Grain: patient_id + year_actual
│   │   ├── Measures: 6 (encounters, procedures, conditions, cost, coverage, providers)
│   │   └── Dimensions: 3 (patients, date, payers)
│   │
│   ├── fct_provider_metrics
│   │   ├── Grain: provider_id + year_month
│   │   ├── Measures: 8 (encounters, patients, age, duration, procedures, cost, etc.)
│   │   └── Dimensions: 3 (providers, organizations, date)
│   │
│   ├── fct_condition_cohorts
│   │   ├── Grain: patient_id + condition_code
│   │   ├── Measures: 4 (months, encounters, procedures, cost, is_active)
│   │   └── Dimensions: 4 (patients, conditions, date start, date end)
│   │
│   └── fct_cost_analysis
│       ├── Grain: encounter_id + payer_id + provider_id
│       ├── Measures: 6 (costs, coverage, responsibility, percentages)
│       └── Dimensions: 4 (encounters, payers, providers, date)
│
├── DIMENSIONS (NEW)
│   └── dim_conditions
│       ├── Grain: condition_code (natural key)
│       ├── Attributes: 4 (code, name, category, chronic_flag)
│       └── Source: stg_synthea__conditions (dedup)
│
└── EXISTING (v0.4)
    ├── Core Dimensions: 5 (patients, providers, organizations, payers, date)
    ├── Core Facts: 2 (encounters, clinical_events)
    ├── Aggregate Facts: 2 (monthly, yearly)
    └── Intermediate: 2 (enriched encounters, patients with conditions)
```

## Data Model Specifications

### Dimension: dim_conditions (NEW)

**Purpose**: Master condition dimension for filtering and grouping by condition

**Grain**: One row per unique ICD condition code

**Source**:

```sql
FROM {{ ref('stg_synthea__conditions') }}
WHERE condition_code IS NOT NULL
GROUP BY condition_code, condition_description, ...
```

**Column Specifications**:

| Column | Type | PK | FK | Nullable | Description |
|--------|------|----|----|----------|-------------|
| condition_id | INT | Yes | - | No | Surrogate key (row_number) |
| condition_code | VARCHAR | - | - | No | ICD code (natural key) |
| condition_description | VARCHAR | - | - | No | Full condition name |
| condition_category | VARCHAR | - | - | Yes | Grouping: Acute, Chronic, etc. |
| chronic_flag | BOOLEAN | - | - | No | True if chronic condition |
| is_active | BOOLEAN | - | - | No | True if currently diagnosed |

**Key Relationships**:

- Referenced by: fct_condition_cohorts, fct_clinical_events (v0.4)

**Tests**:

```yaml
- unique: [condition_code]
- not_null: [condition_code, condition_description]
- relationships: fct_condition_cohorts.fk_condition -> condition_id
```

**Documentation**:

```sql
-- Condition master dimension
-- Sources: ICD condition codes from Synthea
-- Primary use: Filtering encounters/observations by condition, disease management analysis
```

---

### Fact Table: fct_patient_summary (NEW - Annual Grain)

**Purpose**: Annual patient-level snapshots for patient outcomes tracking

**Grain**: ONE row per patient per calendar year

**Pattern**: Conformed dimension fact (dimensions shared with v0.4)

**Column Specifications**:

| Column | Type | Role | Formula/Source | Nullable |
|--------|------|------|-----------------|----------|
| patient_summary_id | INT | Surrogate Key | HASH(patient_id \|\| year_actual) | No |
| fk_patient | INT | Foreign Key | FK to dim_patients | No |
| fk_year_date | INT | Foreign Key | FK to dim_date (year grain) | No |
| fk_payer | INT | Foreign Key | FK to dim_payers | Yes |
| year_actual | INT | Dimension | From dim_date | No |
| patient_age_at_year_end | INT | Dimension | Age calculation | Yes |
| encounter_count | INT | Measure | COUNT(encounters) | No |
| procedure_count | INT | Measure | COUNT(procedures) | No |
| condition_count | INT | Measure | COUNT(DISTINCT conditions) | No |
| total_cost | DECIMAL(15,2) | Measure | SUM(encounter_costs) | No |
| payer_coverage_pct | DECIMAL(5,2) | Measure | SUM(payer_pays) / SUM(total_cost) | Yes |
| unique_providers | INT | Measure | COUNT(DISTINCT providers) | No |
| unique_organizations | INT | Measure | COUNT(DISTINCT organizations) | No |

**Source Logic**:

```sql
WITH patient_year_agg AS (
  SELECT
    patient_id,
    EXTRACT(YEAR FROM encounter_date) as year_actual,
    COUNT(*) as encounter_count,
    SUM(procedure_count) as procedure_count,
    COUNT(DISTINCT condition_id) as condition_count,
    SUM(total_cost) as total_cost,
    SUM(payer_coverage) / SUM(total_cost) as payer_coverage_pct,
    COUNT(DISTINCT provider_id) as unique_providers
  FROM fct_encounters
  GROUP BY patient_id, year_actual
)
SELECT
  MD5(CONCAT(patient_id, year_actual)) as patient_summary_id,
  patient_id as fk_patient,
  year_date_id as fk_year_date,
  ...
FROM patient_year_agg
```

**Key Relationships**:

- fk_patient → dim_patients.patient_id
- fk_year_date → dim_date.date_id (where year_actual = target year)
- fk_payer → dim_payers.payer_id

**Tests**:

```yaml
# Grain tests
- dbt_utils.unique_combination_of_columns:
    combination_of_columns: [fk_patient, year_actual]

# Foreign key tests
- relationships:
    to: ref('dim_patients')
    field: patient_id

# Data quality tests
- dbt_expectations.expect_column_values_to_be_between:
    column_name: encounter_count
    min_value: 0
- dbt_expectations.expect_column_values_to_be_between:
    column_name: total_cost
    min_value: 0
```

**Documentation**:

```
Use case: Patient outcomes tracking, cohort analysis, health trajectory visualization
Example: Top 10 costliest patients by year, patient with most comorbidities, ...
Grain: One row per patient per year (annual snapshot)
Relationship: Join to patients and date dimensions for context
```

---

### Fact Table: fct_provider_metrics (NEW - Monthly Grain)

**Purpose**: Provider-level utilization and quality metrics

**Grain**: ONE row per provider per calendar month

**Column Specifications**:

| Column | Type | Role | Formula | Nullable |
|--------|------|------|---------|----------|
| provider_metrics_id | INT | Surrogate Key | HASH(provider_id \|\| year_month) | No |
| fk_provider | INT | Foreign Key | FK to dim_providers | No |
| fk_organization | INT | Foreign Key | FK to dim_organizations | Yes |
| fk_month_date | INT | Foreign Key | FK to dim_date (month grain) | No |
| year_actual | INT | Dimension | EXTRACT(YEAR from encounter_date) | No |
| month_actual | INT | Dimension | EXTRACT(MONTH from encounter_date) | No |
| encounter_count | INT | Measure | COUNT(*) encounters | No |
| unique_patient_count | INT | Measure | COUNT(DISTINCT patient_id) | No |
| avg_patient_age | DECIMAL(5,2) | Measure | AVG(patient_age) | Yes |
| avg_encounter_duration | DECIMAL(10,2) | Measure | AVG(duration_days) | No |
| total_procedures | INT | Measure | SUM(procedure_count) | No |
| total_cost | DECIMAL(15,2) | Measure | SUM(encounter_costs) | No |
| avg_cost_per_encounter | DECIMAL(12,2) | Measure | total_cost / encounter_count | No |
| encounters_per_patient_avg | DECIMAL(10,2) | Measure | encounter_count / unique_patient_count | No |

**Source Logic**:

```sql
WITH provider_month_agg AS (
  SELECT
    provider_id,
    organization_id,
    EXTRACT(YEAR FROM encounter_date) as year_actual,
    EXTRACT(MONTH FROM encounter_date) as month_actual,
    COUNT(*) as encounter_count,
    COUNT(DISTINCT patient_id) as unique_patient_count,
    AVG(patient_age_at_encounter) as avg_patient_age,
    AVG(encounter_duration) as avg_encounter_duration,
    SUM(procedure_count) as total_procedures,
    SUM(total_cost) as total_cost
  FROM {{ ref('int_encounters__enriched') }}
  GROUP BY provider_id, organization_id, year_actual, month_actual
)
SELECT
  MD5(CONCAT(provider_id, year_actual, month_actual)) as provider_metrics_id,
  ...
  total_cost / encounter_count as avg_cost_per_encounter,
  encounter_count / unique_patient_count as encounters_per_patient_avg
FROM provider_month_agg
```

**Key Relationships**:

- fk_provider → dim_providers.provider_id
- fk_organization → dim_organizations.organization_id
- fk_month_date → dim_date.date_id (where year_month = target)

**Tests**:

```yaml
# Grain tests
- dbt_utils.unique_combination_of_columns:
    combination_of_columns: [fk_provider, year_actual, month_actual]

# Foreign key tests
- relationships:
    to: ref('dim_providers')
    field: provider_id

# Data quality tests
- dbt_expectations.expect_column_values_to_be_between:
    column_name: encounter_count
    min_value: 0
- dbt_expectations.expect_column_values_to_be_between:
    column_name: total_cost
    min_value: 0
```

**Documentation**:

```
Use case: Provider performance dashboards, utilization trending, quality measures
Example: Provider monthly encounter trend, providers by patient count, cost per encounter
Grain: One row per provider per month
```

---

### Fact Table: fct_condition_cohorts (NEW - Patient-Condition Grain)

**Purpose**: Patient-condition relationships for disease management and outcomes analysis

**Grain**: ONE row per patient-condition combination (patient may have condition multiple times, but this is first occurrence)

**Column Specifications**:

| Column | Type | Role | Formula | Nullable |
|--------|------|------|---------|----------|
| condition_cohort_id | INT | Surrogate Key | HASH(patient_id \|\| condition_code) | No |
| fk_patient | INT | Foreign Key | FK to dim_patients | No |
| fk_condition | INT | Foreign Key | FK to dim_conditions | No |
| fk_first_diagnosis_date | INT | Foreign Key | FK to dim_date (first diagnosis) | No |
| fk_last_diagnosis_date | INT | Foreign Key | FK to dim_date (last diagnosis) | Yes |
| condition_code | VARCHAR | Dimension | From dim_conditions | No |
| first_diagnosis_year | INT | Dimension | EXTRACT(YEAR from first_diagnosis) | No |
| months_with_condition | INT | Measure | (last_date - first_date) / 30 | No |
| encounter_count_with_condition | INT | Measure | COUNT encounters during period | No |
| procedure_count_with_condition | INT | Measure | COUNT procedures during period | No |
| total_cost_for_condition | DECIMAL(15,2) | Measure | SUM costs during period | No |
| is_active | BOOLEAN | Measure | CASE WHEN last_date IS NULL THEN TRUE | No |

**Source Logic**:

```sql
WITH condition_windows AS (
  SELECT
    patient_id,
    condition_code,
    MIN(condition_start_date) as first_diagnosis_date,
    MAX(condition_end_date) as last_diagnosis_date,
    COUNT(*) as encounter_count,
    SUM(procedure_count) as procedure_count,
    SUM(cost) as total_cost
  FROM {{ ref('stg_synthea__conditions') }}
  GROUP BY patient_id, condition_code
)
SELECT
  MD5(CONCAT(patient_id, condition_code)) as condition_cohort_id,
  ...
  CASE WHEN last_diagnosis_date IS NULL THEN TRUE ELSE FALSE END as is_active
FROM condition_windows
```

**Key Relationships**:

- fk_patient → dim_patients.patient_id
- fk_condition → dim_conditions.condition_code
- fk_first_diagnosis_date → dim_date.date_id
- fk_last_diagnosis_date → dim_date.date_id (nullable)

**Tests**:

```yaml
# Grain tests
- dbt_utils.unique_combination_of_columns:
    combination_of_columns: [fk_patient, fk_condition]

# Data quality tests
- dbt_expectations.expect_column_values_to_be_between:
    column_name: months_with_condition
    min_value: 0
- dbt_expectations.expect_column_values_to_be_between:
    column_name: total_cost_for_condition
    min_value: 0
- assert: first_diagnosis_date <= last_diagnosis_date (when both non-null)
```

**Documentation**:

```
Use case: Disease management, outcomes by condition, cohort analysis
Example: Patients with diabetes (count, avg cost, procedures), condition prevalence
Grain: One row per patient-condition combination
Active flag: NULL end_date means currently diagnosed
```

---

### Fact Table: fct_cost_analysis (NEW - Encounter-Payer-Provider Grain)

**Purpose**: Detailed cost breakdown for financial analysis and payer management

**Grain**: ONE row per encounter per payer per provider (supports multi-payer arrangements)

**Column Specifications**:

| Column | Type | Role | Formula | Nullable |
|--------|------|------|---------|----------|
| cost_analysis_id | INT | Surrogate Key | HASH(encounter_id \|\| payer_id \|\| provider_id) | No |
| fk_encounter | INT | Foreign Key | FK to fct_encounters | No |
| fk_payer | INT | Foreign Key | FK to dim_payers | No |
| fk_provider | INT | Foreign Key | FK to dim_providers | No |
| fk_encounter_date | INT | Foreign Key | FK to dim_date | No |
| encounter_id | VARCHAR | Dimension | From source | No |
| year_actual | INT | Dimension | EXTRACT(YEAR from encounter_date) | No |
| total_cost | DECIMAL(15,2) | Measure | Total claim amount | No |
| payer_coverage | DECIMAL(15,2) | Measure | Amount paid by insurance | No |
| patient_responsibility | DECIMAL(15,2) | Measure | Patient copay + coinsurance | No |
| coverage_pct | DECIMAL(5,2) | Measure | payer_coverage / total_cost | No |
| patient_cost_pct | DECIMAL(5,2) | Measure | patient_responsibility / total_cost | No |
| cost_per_procedure | DECIMAL(12,2) | Measure | total_cost / procedure_count | Yes |
| out_of_pocket_pct | DECIMAL(5,2) | Measure | patient_responsibility / total_cost | No |

**Source Logic**:

```sql
WITH encounter_costs AS (
  SELECT
    encounter_id,
    payer_id,
    provider_id,
    encounter_date,
    total_claim_cost,
    insurance_payment,
    patient_copay,
    COUNT(*) over (partition by encounter_id) as procedure_count
  FROM {{ ref('fct_encounters') }}
)
SELECT
  MD5(CONCAT(encounter_id, payer_id, provider_id)) as cost_analysis_id,
  ...
  insurance_payment / total_claim_cost as coverage_pct,
  patient_copay / total_claim_cost as patient_cost_pct
FROM encounter_costs
```

**Key Relationships**:

- fk_encounter → fct_encounters.encounter_id
- fk_payer → dim_payers.payer_id
- fk_provider → dim_providers.provider_id
- fk_encounter_date → dim_date.date_id

**Tests**:

```yaml
# Grain tests
- dbt_utils.unique_combination_of_columns:
    combination_of_columns: [fk_encounter, fk_payer, fk_provider]

# Data quality tests
- dbt_expectations.expect_column_values_to_be_between:
    column_name: total_cost
    min_value: 0
- dbt_expectations.expect_column_values_to_be_between:
    column_name: coverage_pct
    min_value: 0
    max_value: 100
- assert: total_cost = payer_coverage + patient_responsibility
```

**Documentation**:

```
Use case: Financial analysis, payer contract optimization, cost allocation
Example: Average cost per encounter by payer, patient cost burden by provider
Grain: One row per encounter-payer-provider
Costs: Always non-negative, coverage + responsibility = total
```

---

### Views (NEW - Operational)

**v_patient_current_conditions** (TABLE)

```sql
SELECT
  fk_patient,
  fk_condition,
  condition_code,
  first_diagnosis_date,
  months_with_condition
FROM {{ ref('fct_condition_cohorts') }}
WHERE is_active = TRUE
```

**v_provider_active_patients** (TABLE)

```sql
SELECT
  fk_provider,
  COUNT(DISTINCT fk_patient) as active_patient_count
FROM {{ ref('fct_condition_cohorts') }}
WHERE is_active = TRUE
  AND first_diagnosis_year = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY fk_provider
```

**v_encounter_summary** (EPHEMERAL)

```sql
SELECT
  e.encounter_id,
  e.encounter_date,
  p.patient_name,
  pr.provider_name,
  o.organization_name,
  cc.condition_code,
  e.total_cost
FROM {{ ref('fct_encounters') }} e
LEFT JOIN {{ ref('dim_patients') }} p ON e.fk_patient = p.patient_id
LEFT JOIN {{ ref('dim_providers') }} pr ON e.fk_provider = pr.provider_id
LEFT JOIN {{ ref('dim_organizations') }} o ON e.fk_organization = o.organization_id
LEFT JOIN {{ ref('fct_condition_cohorts') }} cc ON e.fk_patient = cc.fk_patient
```

## Test Specifications

### Test Matrix

| Model | Test Type | Count | Examples |
|-------|-----------|-------|----------|
| dim_conditions | Schema | 3 | unique(code), not_null(name, description) |
| fct_patient_summary | Grain | 1 | unique(patient, year) |
| | References | 3 | FK to patients, date, payers |
| | Quality | 4 | counts ≥0, cost ≥0, coverage %∈[0,100], providers ≥1 |
| fct_provider_metrics | Grain | 1 | unique(provider, year, month) |
| | References | 3 | FK to providers, orgs, date |
| | Quality | 4 | counts ≥0, cost ≥0, avg values valid |
| fct_condition_cohorts | Grain | 1 | unique(patient, condition) |
| | References | 4 | FK to patients, conditions, dates (both) |
| | Quality | 4 | months ≥0, cost ≥0, dates logical |
| fct_cost_analysis | Grain | 1 | unique(encounter, payer, provider) |
| | References | 4 | FK to encounters, payers, providers, date |
| | Quality | 5 | costs ≥0, coverage ≤100%, cost totals correct |

### Testing Example: fct_patient_summary

```yaml
models:
  - name: fct_patient_summary
    description: Annual patient aggregations for outcomes tracking

    columns:
      - name: patient_summary_id
        description: Surrogate key
        tests:
          - not_null
          - unique

      - name: fk_patient
        description: Foreign key to dim_patients
        tests:
          - not_null
          - relationships:
              to: ref('dim_patients')
              field: patient_id

      - name: encounter_count
        description: Number of encounters in year
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 10000  # reasonable upper bound

      - name: total_cost
        description: Total cost for year
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 10000000  # 10M reasonable max

tests:
  - name: grain_patient_year
    sql: |
      WITH grain_test AS (
        SELECT fk_patient, year_actual, COUNT(*) as cnt
        FROM {{ ref('fct_patient_summary') }}
        GROUP BY fk_patient, year_actual
      )
      SELECT * FROM grain_test WHERE cnt > 1
```

## Integration Patterns

### Conformed Dimensions

All new facts use existing dimensions from v0.4:

- **dim_patients** ← fct_patient_summary, fct_condition_cohorts
- **dim_providers** ← fct_provider_metrics, fct_cost_analysis
- **dim_organizations** ← fct_provider_metrics
- **dim_payers** ← fct_patient_summary, fct_cost_analysis
- **dim_date** ← All facts (multiple dates/grains)
- **dim_conditions** (NEW) ← fct_condition_cohorts, fct_clinical_events

### Grain Compatibility

| Fact A | Fact B | Compatible? | Join Pattern |
|--------|--------|-------------|--------------|
| fct_patient_summary | fct_condition_cohorts | Yes | ON patient_id + year range |
| fct_provider_metrics | fct_cost_analysis | Yes | ON provider_id + date |
| fct_encounters (v0.4) | fct_cost_analysis | Yes | ON encounter_id (1:M) |

### Source Integration

- **stg_conditions** → dim_conditions (1:M dedup to 1:1)
- **stg_encounters** + **fct_encounters** → all fact tables (aggregation)
- **int_encounters__enriched** → fct_provider_metrics (pre-enriched source)

## Performance Considerations

### Materialization Strategy

| Model | Type | Strategy | Rationale |
|-------|------|----------|-----------|
| dim_conditions | TABLE | Full refresh | Small, stable dimension |
| fct_patient_summary | TABLE | Full refresh | Annual grain, full rebuild acceptable |
| fct_provider_metrics | TABLE | Incremental (v0.6) | Large table, monthly updates |
| fct_condition_cohorts | TABLE | Full refresh | Medium size, needed for views |
| fct_cost_analysis | TABLE | Incremental (v0.6) | Large table, only new encounters |
| v_* views | VIEW/TABLE | Materialized view | Dashboard performance |

### Query Performance Targets

- dim_conditions lookups: <100ms (small table)
- fct_patient_summary year aggregations: <500ms
- fct_provider_metrics month-over-month: <1s
- v_patient_current_conditions: <500ms (materialized)

## SQL Patterns & Templates

### CTE Pattern for Aggregates

```sql
WITH grain_agg AS (
  SELECT
    group_by_keys,
    measure_col,
    COUNT(*) as count_measure,
    SUM(amount) as sum_measure,
    AVG(amount) as avg_measure
  FROM source_table
  WHERE filter_conditions
  GROUP BY group_by_keys
),
add_dimensions AS (
  SELECT
    ga.*,
    d.dimension_name
  FROM grain_agg ga
  LEFT JOIN dim d ON ga.dim_key = d.key
)
SELECT * FROM add_dimensions
```

### Grain Validation Test

```sql
SELECT
  {{ grain_columns | join(', ') }},
  COUNT(*) as grain_count
FROM {{ ref('fact_table') }}
GROUP BY {{ grain_columns | join(', ') }}
HAVING COUNT(*) > 1
```

### Cost Validation Test

```sql
SELECT *
FROM {{ ref('fct_cost_analysis') }}
WHERE NOT (
  ABS(total_cost - (payer_coverage + patient_responsibility)) < 0.01
)
```

## References

- **PRD-005-MARTS-ENHANCEMENTS.md** - Requirements document
- **v0.4_PLAN.md** - v0.4 implementation patterns
- **DBT_CODING_STANDARDS.md** - SQL and YAML formatting standards
- **KIMBALL_REFERENCE.md** - Dimensional modeling guide

---

**Document Version**: 1.0
**Last Updated**: 2026-01-30
**Status**: Approved for implementation
