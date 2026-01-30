# BI Integration Guide - v0.5 Analytics Models

**Last Updated**: 2026-01-30
**Version**: v0.5.0
**Author**: Healthcare Analytics Team

---

## Overview

This guide covers best practices for connecting Business Intelligence (BI) tools to the v0.5 analytics models. The data warehouse follows Kimball dimensional modeling patterns, making it well-suited for traditional BI reporting and ad-hoc analysis.

### Data Model Summary

| Model Type | Count | Description |
|------------|-------|-------------|
| Dimensions | 6 | Patient, Provider, Organization, Payer, Date, Conditions |
| Core Facts | 5 | Encounters, Clinical Events, Patient Summary, Provider Metrics, Cost Analysis |
| Specialized Facts | 1 | Condition Cohorts |
| Aggregate Facts | 2 | Monthly/Yearly Encounters |
| Operational Views | 3 | Active Conditions, Provider Panels, Encounter Summary |

---

## Quick Start

### Connection Details

**Development Environment:**

```text
Database Type: DuckDB
File Path: dbt_project/target/dev.duckdb
Schema: main_staging, main_intermediate, main_marts
```

**Production Considerations:**

- DuckDB is suitable for development and small-scale analytics
- For production BI, consider exporting to PostgreSQL, Snowflake, or BigQuery
- Use dbt's `target` configuration to manage environments

### Connection String Examples

```python
# Python (DuckDB)
import duckdb
conn = duckdb.connect('dbt_project/target/dev.duckdb')

# JDBC (for Tableau, DBeaver)
jdbc:duckdb:/path/to/dev.duckdb
```

---

## Recommended Dashboard Facts

### 1. Patient Outcomes Dashboard

**Primary Fact**: `fct_patient_summary`
**Dimensions**: `dim_patients`, `dim_date`

**Key Metrics:**

- Total patients by year
- Average annual cost per patient
- Encounter counts by age group
- Condition prevalence
- Coverage percentage trends

**Sample Query:**

```sql
select
    d.year_actual
    , count(distinct fps.patient_id) as patient_count
    , round(avg(fps.total_cost), 2) as avg_annual_cost
    , round(avg(fps.encounter_count), 2) as avg_encounters
    , round(avg(fps.condition_count), 2) as avg_conditions
from main_marts.fct_patient_summary fps
join main_marts.dim_date d
    on fps.year_actual = d.year_actual
group by d.year_actual
order by d.year_actual desc
```

### 2. Provider Performance Dashboard

**Primary Fact**: `fct_provider_metrics`
**Dimensions**: `dim_providers`, `dim_organizations`, `dim_date`

**Key Metrics:**

- Monthly encounter volume
- Patients per provider
- Average cost per encounter
- Procedure rates
- Provider efficiency scores

**Sample Query:**

```sql
select
    p.name as provider_name
    , p.specialty
    , o.name as organization_name
    , sum(fpm.encounter_count) as total_encounters
    , sum(fpm.unique_patient_count) as total_patients
    , round(avg(fpm.avg_cost_per_encounter), 2) as avg_cost
from main_marts.fct_provider_metrics fpm
join main_marts.dim_providers p
    on fpm.provider_key = p.provider_key
left join main_marts.dim_organizations o
    on fpm.organization_key = o.organization_key
where fpm.year_actual = 2024
group by 1, 2, 3
order by total_encounters desc
```

### 3. Financial Analysis Dashboard

**Primary Fact**: `fct_cost_analysis`
**Dimensions**: `dim_payers`, `dim_providers`, `dim_date`

**Key Metrics:**

- Total costs by payer
- Payer mix percentages
- Patient responsibility trends
- Cost per encounter class
- Monthly revenue trends

**Sample Query:**

```sql
select
    py.payer_name
    , fca.encounter_class
    , count(*) as encounter_count
    , round(sum(fca.total_cost), 2) as total_cost
    , round(sum(fca.payer_coverage), 2) as payer_coverage
    , round(sum(fca.patient_responsibility), 2) as patient_share
    , round(avg(fca.coverage_pct), 2) as avg_coverage_pct
from main_marts.fct_cost_analysis fca
join main_marts.dim_payers py
    on fca.payer_key = py.payer_key
group by 1, 2
order by total_cost desc
```

### 4. Disease Management Dashboard

**Primary Fact**: `fct_condition_cohorts`
**Dimensions**: `dim_conditions`, `dim_patients`

**Key Metrics:**

- Condition prevalence
- Active vs. resolved conditions
- Chronic condition tracking
- Multi-morbidity analysis
- Cohort sizes for programs

**Sample Query:**

```sql
select
    dc.condition_description
    , count(distinct fcc.patient_id) as patient_count
    , sum(case when fcc.is_active then 1 else 0 end) as active_patients
    , round(avg(fcc.months_with_condition), 1) as avg_duration_months
from main_marts.fct_condition_cohorts fcc
join main_marts.dim_conditions dc
    on fcc.condition_key = dc.condition_key
group by dc.condition_description
order by patient_count desc
limit 25
```

---

## Dimension Relationships (Star Schema)

```text
                    +----------------+
                    |   dim_date     |
                    +----------------+
                           |
    +----------------+     |     +----------------+
    | dim_patients   |-----+-----| dim_providers  |
    +----------------+     |     +----------------+
           |               |              |
           |       +---------------+      |
           +-------|  FACT TABLES  |------+
                   +---------------+
                          |
    +----------------+    |    +------------------+
    | dim_payers     |----+----| dim_organizations|
    +----------------+         +------------------+
                          |
                   +----------------+
                   | dim_conditions |
                   +----------------+
```

### Key Relationships

| Fact Table | Primary Dimensions | Optional Dimensions |
|------------|-------------------|---------------------|
| fct_patient_summary | dim_patients, dim_date | - |
| fct_provider_metrics | dim_providers, dim_date | dim_organizations |
| fct_cost_analysis | dim_payers, dim_providers | dim_patients, dim_date |
| fct_condition_cohorts | dim_patients, dim_conditions | - |
| fct_encounters | dim_patients, dim_providers | dim_payers, dim_organizations, dim_date |

### Conformed Dimensions

These dimensions are shared across multiple fact tables:

- **dim_patients** - Patient demographics, used in 3+ facts
- **dim_providers** - Provider information, used in 3+ facts
- **dim_date** - Date spine, used for all time-based analysis
- **dim_payers** - Insurance information, used in cost facts

---

## BI Tool-Specific Setup

### Tableau

1. **Connect via DuckDB connector** (Tableau 2023.1+):
   - Select "DuckDB" from connectors
   - Browse to `dev.duckdb` file
   - Select `main_marts` schema

2. **Define relationships**:
   - Start with fact table
   - Join to dimensions on surrogate keys (`*_key` columns)

3. **Recommended data source structure**:

   ```text
   fct_patient_summary (anchor)
   ├── dim_patients (patient_key)
   └── dim_date (year_actual to year_actual)
   ```

### Looker

1. **Create LookML models**:

   ```lookml
   explore: fct_patient_summary {
     join: dim_patients {
       type: left_outer
       sql_on: ${fct_patient_summary.patient_key} = ${dim_patients.patient_key} ;;
       relationship: many_to_one
     }
   }
   ```

2. **Define dimensions and measures in LookML**

### Power BI

1. **Import via ODBC/DirectQuery**:
   - Use DuckDB ODBC driver
   - Import relevant tables

2. **Model view relationships**:
   - Create relationships on `*_key` columns
   - Set cardinality to Many-to-One (fact to dim)

3. **DAX measures example**:

   ```dax
   Total Cost = SUM(fct_patient_summary[total_cost])
   Avg Cost Per Patient = AVERAGE(fct_patient_summary[total_cost])
   ```

### Metabase

1. **Add DuckDB database**:
   - Admin > Databases > Add Database
   - Type: DuckDB
   - Path: `/path/to/dev.duckdb`

2. **Auto-discover tables and relationships**

3. **Create saved questions and dashboards**

### Apache Superset

1. **Add DuckDB connection**:

   ```text
   Database > + Database
   SQLAlchemy URI: duckdb:////path/to/dev.duckdb
   ```

2. **Create datasets from tables**

3. **Build charts and dashboards**

---

## Common Dashboard Patterns

### 1. Executive Summary (KPI Cards)

```sql
-- Total patients, encounters, and costs (current year)
select
    count(distinct patient_id) as total_patients
    , sum(encounter_count) as total_encounters
    , round(sum(total_cost), 2) as total_cost
    , round(avg(payer_coverage_pct), 2) as avg_coverage_pct
from main_marts.fct_patient_summary
where year_actual = extract(year from current_date)
```

### 2. Time Series Trends

```sql
-- Monthly cost trend
select
    year_month_str
    , sum(total_cost) as monthly_cost
    , sum(encounter_count) as monthly_encounters
from main_marts.fct_provider_metrics
group by year_month_str
order by year_month_str
```

### 3. Top-N Analysis

```sql
-- Top 10 conditions by patient count
select
    condition_description
    , patient_count
    , encounter_count
from main_marts.dim_conditions
order by patient_count desc
limit 10
```

### 4. Distribution Analysis

```sql
-- Cost distribution by encounter class
select
    encounter_class
    , count(*) as encounter_count
    , round(avg(total_cost), 2) as avg_cost
    , round(sum(total_cost), 2) as total_cost
from main_marts.fct_cost_analysis
group by encounter_class
order by total_cost desc
```

### 5. Cohort Comparison

```sql
-- Age group comparison
select
    case
        when patient_age_at_year_end < 18 then '0-17'
        when patient_age_at_year_end < 35 then '18-34'
        when patient_age_at_year_end < 50 then '35-49'
        when patient_age_at_year_end < 65 then '50-64'
        else '65+'
    end as age_group
    , count(distinct patient_id) as patients
    , round(avg(total_cost), 2) as avg_cost
from main_marts.fct_patient_summary
where year_actual = 2024
group by 1
order by 1
```

---

## Performance Optimization Tips

### 1. Pre-Aggregation

Use aggregate fact tables for high-level dashboards:

- `fct_encounters_monthly` - Monthly aggregates
- `fct_encounters_yearly` - Annual aggregates

### 2. Materialized Views

The following are already materialized as tables:

- `v_patient_current_conditions` - Active conditions only
- `v_provider_active_patients` - Provider panel summaries

### 3. Indexing Strategy

For production databases, add indexes on:

- All surrogate keys (`*_key` columns)
- Foreign key columns
- Common filter columns (year_actual, encounter_class)

### 4. Query Best Practices

- Use surrogate keys for joins (faster than natural keys)
- Filter early in CTEs
- Limit result sets for exploration
- Use aggregate tables when possible

### 5. Incremental Refresh

For large datasets, consider:

- Partition by date
- Use incremental models in dbt
- Schedule off-peak refreshes

---

## Data Quality Considerations

### Known Characteristics

1. **Synthea synthetic data**: All data is generated, not real patient data
2. **Date range**: Data spans multiple decades (Synthea default)
3. **Null handling**: Some columns allow nulls (documented in YAML)

### Validation Queries

```sql
-- Check row counts
select 'fct_patient_summary' as model, count(*) as rows from main_marts.fct_patient_summary
union all
select 'fct_provider_metrics', count(*) from main_marts.fct_provider_metrics
union all
select 'fct_cost_analysis', count(*) from main_marts.fct_cost_analysis
union all
select 'fct_condition_cohorts', count(*) from main_marts.fct_condition_cohorts;

-- Check date range
select
    min(encounter_date) as earliest_date
    , max(encounter_date) as latest_date
from main_marts.fct_cost_analysis;
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Missing data | Models not built | Run `dbt build` |
| Slow queries | Large fact scans | Use aggregate tables or add filters |
| Join failures | Null keys | Check for null foreign keys |
| Incorrect totals | Duplicate joins | Review cardinality and relationships |

### Support Resources

- **dbt Documentation**: `dbt docs serve` (after `dbt docs generate`)
- **Model YAML**: See `_analytics__models.yml` for schema details
- **Test Results**: All 91 tests passing validates data quality

---

## Appendix: Model Reference

### Fact Tables

| Model | Grain | Row Count | Key Columns |
|-------|-------|-----------|-------------|
| fct_patient_summary | patient + year | 21,343 | patient_summary_key, patient_key |
| fct_provider_metrics | provider + month | 33,463 | provider_metrics_key, provider_key |
| fct_cost_analysis | encounter | 53,346 | cost_analysis_key, encounter_key |
| fct_condition_cohorts | patient + condition | 7,165 | condition_cohort_key, patient_key, condition_key |

### Dimension Tables

| Model | Grain | Row Count | Primary Key |
|-------|-------|-----------|-------------|
| dim_patients | patient | 1,171 | patient_key |
| dim_providers | provider | 5,855 | provider_key |
| dim_organizations | organization | 1,119 | organization_key |
| dim_payers | payer | 10 | payer_key |
| dim_conditions | condition_code | 130 | condition_key |
| dim_date | calendar_date | 36,525 | date_key |

### Operational Views

| Model | Grain | Row Count | Description |
|-------|-------|-----------|-------------|
| v_patient_current_conditions | patient + condition | 3,811 | Active conditions only |
| v_provider_active_patients | provider | 5,855 | Provider panel summaries |
| v_encounter_summary | encounter | ephemeral | Enriched encounter view |

---

**Document Version**: 1.0
**Last Updated**: 2026-01-30
**Compatible With**: dbt 1.11.2+, DuckDB 1.10.0+
