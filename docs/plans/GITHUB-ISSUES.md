# GitHub Issues for dbt-playground Initialization

This document contains all GitHub issues for implementing the dbt project with Synthea healthcare data. Issues are organized by epic and include acceptance criteria for the agent team.

---

## Epic 1: Environment Setup (E1)

### Issue: Install dbt-duckdb adapter

**Epic**: E1-Environment-Setup
**Assignee**: developer
**Labels**: `enhancement`, `setup`, `priority:critical`
**Milestone**: v0.2.0

**Description**:
Install the dbt-duckdb adapter to enable DuckDB as the data warehouse for this project.

**Acceptance Criteria**:

- [ ] `pip install dbt-duckdb` executed successfully
- [ ] `dbt --version` shows dbt-duckdb adapter available
- [ ] Version is >= 1.7.0

**Technical Notes**:

```bash
pip install dbt-duckdb
dbt --version
```

---

### Issue: Create dbt profile configuration

**Epic**: E1-Environment-Setup
**Assignee**: developer
**Labels**: `enhancement`, `setup`, `priority:critical`
**Milestone**: v0.2.0

**Description**:
Create the `~/.dbt/profiles.yml` file with dev and prod targets for DuckDB.

**Acceptance Criteria**:

- [ ] `~/.dbt/profiles.yml` created
- [ ] Profile named `dbt_playground`
- [ ] `dev` target configured with path `./dbt_project/dev.duckdb`
- [ ] `prod` target configured with path `./dbt_project/prod.duckdb`
- [ ] Default target set to `dev`
- [ ] Threads set to 4

**Technical Notes**:
Profile should match the configuration in PRD-001.

---

### Issue: Initialize dbt project structure

**Epic**: E1-Environment-Setup
**Assignee**: dbt-developer
**Labels**: `enhancement`, `setup`, `priority:critical`
**Milestone**: v0.2.0

**Description**:
Initialize the dbt project and configure `dbt_project.yml` with proper model paths and materializations.

**Acceptance Criteria**:

- [ ] `dbt init dbt_project` executed
- [ ] `dbt_project.yml` configured with name `dbt_playground`
- [ ] Profile reference matches profiles.yml
- [ ] Model paths configured for staging, intermediate, marts
- [ ] Materialization defaults set (staging: view, intermediate: view, marts: table)
- [ ] `dbt compile` succeeds

**Technical Notes**:
Follow the configuration specified in PRD-001.

---

### Issue: Configure dbt packages

**Epic**: E1-Environment-Setup
**Assignee**: dbt-developer
**Labels**: `enhancement`, `setup`, `priority:high`
**Milestone**: v0.2.0

**Description**:
Create `packages.yml` with required dbt packages and install them.

**Acceptance Criteria**:

- [ ] `packages.yml` created in `dbt_project/`
- [ ] dbt_utils 1.3.0 included
- [ ] dbt_expectations 0.10.4 included
- [ ] dbt_date 0.10.1 included
- [ ] codegen 0.12.1 included
- [ ] `dbt deps` installs all packages without errors
- [ ] `dbt_packages/` directory populated

---

### Issue: Configure MCP for dbt integration

**Epic**: E1-Environment-Setup
**Assignee**: developer
**Labels**: `enhancement`, `setup`, `mcp`, `priority:high`
**Milestone**: v0.2.0

**Description**:
Update `.mcp.json` to add dbt-mcp server configuration for AI-assisted development.

**Acceptance Criteria**:

- [ ] `.mcp.json` updated with dbt server configuration
- [ ] `DBT_PROJECT_PATH` set to `./dbt_project`
- [ ] `DBT_PROFILES_DIR` set to `~/.dbt`
- [ ] MCP server starts without errors
- [ ] `claude mcp list` shows dbt server

**Technical Notes**:
Follow the configuration in PRD-001.

---

### Issue: Update gitignore for dbt artifacts

**Epic**: E1-Environment-Setup
**Assignee**: developer
**Labels**: `chore`, `setup`, `priority:medium`
**Milestone**: v0.2.0

**Description**:
Update `.gitignore` to exclude dbt build artifacts and sensitive files.

**Acceptance Criteria**:

- [ ] `*.duckdb` added to gitignore
- [ ] `dbt_project/target/` added
- [ ] `dbt_project/dbt_packages/` added
- [ ] `dbt_project/logs/` added
- [ ] `dbt_project/data/` added
- [ ] `profiles.yml` in project directory (if exists) added

---

### Issue: Verify dbt environment setup

**Epic**: E1-Environment-Setup
**Assignee**: dbt-tester
**Labels**: `testing`, `setup`, `priority:critical`
**Milestone**: v0.2.0

**Description**:
Verify complete dbt environment is functional with all components working.

**Acceptance Criteria**:

- [ ] `dbt debug` passes all checks
- [ ] `dbt deps` succeeds
- [ ] `dbt compile` succeeds (may warn about no models)
- [ ] MCP tools respond to basic queries
- [ ] Document any issues found

---

## Epic 2: Data Acquisition (E2)

### Issue: Generate Synthea healthcare data

**Epic**: E2-Data-Acquisition
**Assignee**: developer
**Labels**: `enhancement`, `data`, `priority:critical`
**Milestone**: v0.2.0

**Description**:
Generate 500 synthetic patients using Synthea with CSV export enabled.

**Acceptance Criteria**:

- [ ] Synthea cloned to temp location
- [ ] CSV export enabled in synthea.properties
- [ ] 500 patients generated successfully
- [ ] All expected CSV files created in output directory
- [ ] Document the Synthea version used

**Technical Notes**:

```bash
git clone https://github.com/synthetichealth/synthea.git /tmp/synthea
cd /tmp/synthea
./run_synthea -p 500 --exporter.csv.export true
```

---

### Issue: Copy Synthea data to dbt project

**Epic**: E2-Data-Acquisition
**Assignee**: developer
**Labels**: `enhancement`, `data`, `priority:critical`
**Milestone**: v0.2.0

**Description**:
Copy generated Synthea CSV files to the dbt project data directory.

**Acceptance Criteria**:

- [ ] `dbt_project/data/synthea/` directory created
- [ ] All 9 required CSV files copied:
  - patients.csv
  - encounters.csv
  - conditions.csv
  - medications.csv
  - procedures.csv
  - observations.csv
  - providers.csv
  - organizations.csv
  - payers.csv
- [ ] Files have appropriate permissions (readable)

---

### Issue: Verify Synthea data integrity

**Epic**: E2-Data-Acquisition
**Assignee**: dbt-tester
**Labels**: `testing`, `data`, `priority:high`
**Milestone**: v0.2.0

**Description**:
Verify all Synthea CSV files are readable and have expected structure.

**Acceptance Criteria**:

- [ ] All 9 CSV files readable by DuckDB `read_csv_auto()`
- [ ] Row counts documented for each file
- [ ] Column counts match expected schema
- [ ] No truncated or corrupted files
- [ ] Create verification script/query

**Technical Notes**:

```sql
SELECT 'patients' as table_name, COUNT(*) as rows
FROM read_csv_auto('dbt_project/data/synthea/patients.csv')
-- Union all tables
```

---

### Issue: Create data exploration queries

**Epic**: E2-Data-Acquisition
**Assignee**: data-modeler
**Labels**: `enhancement`, `data`, `documentation`, `priority:medium`
**Milestone**: v0.2.0

**Description**:
Create exploration queries to understand Synthea data structure and content.

**Acceptance Criteria**:

- [ ] Query to show schema for each table
- [ ] Query to show row counts
- [ ] Query to show sample data
- [ ] Query to show value distributions for key columns
- [ ] Save as `dbt_project/analyses/synthea_exploration.sql`

---

## Epic 3: Staging Layer (E3)

### Issue: Create Synthea source definition

**Epic**: E3-Staging-Layer
**Assignee**: data-modeler
**Labels**: `enhancement`, `staging`, `priority:critical`
**Milestone**: v0.3.0

**Description**:
Create the YAML source definition for Synthea raw data.

**Acceptance Criteria**:

- [ ] `_synthea__sources.yml` created in `models/staging/synthea/`
- [ ] Source named `synthea_raw`
- [ ] All 9 tables defined
- [ ] Primary key columns identified for each table
- [ ] Basic tests on primary keys (unique, not_null)
- [ ] Source descriptions added

---

### Issue: Create stg_synthea__patients model

**Epic**: E3-Staging-Layer
**Assignee**: dbt-developer
**Labels**: `enhancement`, `staging`, `model`, `priority:critical`
**Milestone**: v0.3.0

**Description**:
Create the patients staging model with proper naming and typing.

**Acceptance Criteria**:

- [ ] Model reads from CSV via `read_csv_auto()`
- [ ] All columns renamed to snake_case
- [ ] Primary key: `patient_id`
- [ ] Date columns typed as DATE
- [ ] Decimal columns typed as DECIMAL
- [ ] `_loaded_at` metadata column added
- [ ] Model compiles and runs successfully

**Technical Notes**:
See PRD-003 for column mapping details.

---

### Issue: Create stg_synthea__encounters model

**Epic**: E3-Staging-Layer
**Assignee**: dbt-developer
**Labels**: `enhancement`, `staging`, `model`, `priority:critical`
**Milestone**: v0.3.0

**Description**:
Create the encounters staging model with proper naming and typing.

**Acceptance Criteria**:

- [ ] Model reads from CSV via `read_csv_auto()`
- [ ] All columns renamed to snake_case
- [ ] Primary key: `encounter_id`
- [ ] Timestamp columns typed as TIMESTAMP
- [ ] Foreign keys preserved (patient_id, provider_id, organization_id, payer_id)
- [ ] Cost columns typed as DECIMAL
- [ ] `_loaded_at` metadata column added
- [ ] Model compiles and runs successfully

---

### Issue: Create stg_synthea__conditions model

**Epic**: E3-Staging-Layer
**Assignee**: dbt-developer
**Labels**: `enhancement`, `staging`, `model`, `priority:high`
**Milestone**: v0.3.0

**Description**:
Create the conditions staging model for diagnosis data.

**Acceptance Criteria**:

- [ ] Model reads from CSV
- [ ] All columns renamed to snake_case
- [ ] Date columns properly typed
- [ ] SNOMED codes preserved
- [ ] Patient and encounter linkage maintained
- [ ] `_loaded_at` metadata column added
- [ ] Model compiles and runs successfully

---

### Issue: Create stg_synthea__medications model

**Epic**: E3-Staging-Layer
**Assignee**: dbt-developer
**Labels**: `enhancement`, `staging`, `model`, `priority:high`
**Milestone**: v0.3.0

**Description**:
Create the medications staging model for prescription data.

**Acceptance Criteria**:

- [ ] Model reads from CSV
- [ ] All columns renamed to snake_case
- [ ] Date/timestamp columns typed
- [ ] RxNorm codes preserved
- [ ] Cost columns as DECIMAL
- [ ] `_loaded_at` metadata column added
- [ ] Model compiles and runs successfully

---

### Issue: Create stg_synthea__procedures model

**Epic**: E3-Staging-Layer
**Assignee**: dbt-developer
**Labels**: `enhancement`, `staging`, `model`, `priority:high`
**Milestone**: v0.3.0

**Description**:
Create the procedures staging model.

**Acceptance Criteria**:

- [ ] Model reads from CSV
- [ ] All columns renamed to snake_case
- [ ] SNOMED procedure codes preserved
- [ ] Cost columns as DECIMAL
- [ ] Patient and encounter linkage maintained
- [ ] `_loaded_at` metadata column added
- [ ] Model compiles and runs successfully

---

### Issue: Create stg_synthea__observations model

**Epic**: E3-Staging-Layer
**Assignee**: dbt-developer
**Labels**: `enhancement`, `staging`, `model`, `priority:high`
**Milestone**: v0.3.0

**Description**:
Create the observations staging model for vitals and lab results.

**Acceptance Criteria**:

- [ ] Model reads from CSV
- [ ] All columns renamed to snake_case
- [ ] LOINC codes preserved
- [ ] Observation values preserved (various types)
- [ ] Units column maintained
- [ ] `_loaded_at` metadata column added
- [ ] Model compiles and runs successfully

**Technical Notes**:
This is typically the largest file. Consider view materialization for performance.

---

### Issue: Create stg_synthea__providers model

**Epic**: E3-Staging-Layer
**Assignee**: dbt-developer
**Labels**: `enhancement`, `staging`, `model`, `priority:medium`
**Milestone**: v0.3.0

**Description**:
Create the providers staging model.

**Acceptance Criteria**:

- [ ] Model reads from CSV
- [ ] All columns renamed to snake_case
- [ ] Primary key: `provider_id`
- [ ] Specialty codes preserved
- [ ] Organization linkage maintained
- [ ] `_loaded_at` metadata column added
- [ ] Model compiles and runs successfully

---

### Issue: Create stg_synthea__organizations model

**Epic**: E3-Staging-Layer
**Assignee**: dbt-developer
**Labels**: `enhancement`, `staging`, `model`, `priority:medium`
**Milestone**: v0.3.0

**Description**:
Create the organizations staging model for healthcare facilities.

**Acceptance Criteria**:

- [ ] Model reads from CSV
- [ ] All columns renamed to snake_case
- [ ] Primary key: `organization_id`
- [ ] Address columns standardized
- [ ] Revenue column as DECIMAL
- [ ] `_loaded_at` metadata column added
- [ ] Model compiles and runs successfully

---

### Issue: Create stg_synthea__payers model

**Epic**: E3-Staging-Layer
**Assignee**: dbt-developer
**Labels**: `enhancement`, `staging`, `model`, `priority:medium`
**Milestone**: v0.3.0

**Description**:
Create the payers staging model for insurance data.

**Acceptance Criteria**:

- [ ] Model reads from CSV
- [ ] All columns renamed to snake_case
- [ ] Primary key: `payer_id`
- [ ] Address columns standardized
- [ ] `_loaded_at` metadata column added
- [ ] Model compiles and runs successfully

---

### Issue: Add schema tests to staging models

**Epic**: E3-Staging-Layer
**Assignee**: dbt-tester
**Labels**: `testing`, `staging`, `priority:high`
**Milestone**: v0.3.0

**Description**:
Add schema tests to `_synthea__models.yml` for all staging models.

**Acceptance Criteria**:

- [ ] `_synthea__models.yml` created
- [ ] All 9 models listed with descriptions
- [ ] Primary key columns have `unique` and `not_null` tests
- [ ] Foreign key columns have `not_null` tests where appropriate
- [ ] `dbt test --select staging` passes

---

### Issue: Document staging models

**Epic**: E3-Staging-Layer
**Assignee**: dbt-documenter
**Labels**: `documentation`, `staging`, `priority:high`
**Milestone**: v0.3.0

**Description**:
Add comprehensive documentation to all staging models.

**Acceptance Criteria**:

- [ ] All 9 models have descriptions
- [ ] All columns have descriptions
- [ ] Source references documented
- [ ] `dbt docs generate` includes all staging models
- [ ] `dbt docs serve` shows documentation site

---

### Issue: Code review staging layer

**Epic**: E3-Staging-Layer
**Assignee**: code-reviewer
**Labels**: `review`, `staging`, `priority:high`
**Milestone**: v0.3.0

**Description**:
Review all staging models for consistency, patterns, and best practices.

**Acceptance Criteria**:

- [ ] Naming conventions consistent across all models
- [ ] Column ordering consistent (PK, attributes, metadata)
- [ ] Data type choices appropriate
- [ ] No unnecessary complexity
- [ ] CTE naming follows conventions
- [ ] Document any recommended improvements

---

## Epic 4: Dimensional Models (E4)

### Issue: Create dim_patients dimension

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `marts`, `dimension`, `priority:critical`
**Milestone**: v0.4.0

**Description**:
Create the patient dimension with demographics, derived attributes, and SCD Type 2 history tracking.

**Acceptance Criteria**:

- [ ] Surrogate key generated (`patient_key`)
- [ ] Natural key preserved (`patient_id`)
- [ ] All demographic attributes included
- [ ] Derived fields: `full_name`, `age_years`, `is_deceased`
- [ ] SCD Type 2 columns: `valid_from`, `valid_to`, `is_current`
- [ ] Initial load sets valid_from = birth_date, valid_to = NULL, is_current = TRUE
- [ ] Materialized as table
- [ ] Tests for unique/not_null on keys
- [ ] Model compiles and runs successfully

**Technical Notes**:
SCD Type 2 enables historical analysis. For initial load, all records are current.

---

### Issue: Create dim_providers dimension

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `marts`, `dimension`, `priority:high`
**Milestone**: v0.4.0

**Description**:
Create the provider dimension with specialty information.

**Acceptance Criteria**:

- [ ] Surrogate key generated (`provider_key`)
- [ ] Natural key preserved (`provider_id`)
- [ ] Specialty information included
- [ ] Organization linkage maintained (`organization_key` FK)
- [ ] Materialized as table
- [ ] Tests for unique/not_null on keys
- [ ] Model compiles and runs successfully

---

### Issue: Create dim_organizations dimension

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `marts`, `dimension`, `priority:high`
**Milestone**: v0.4.0

**Description**:
Create the organizations dimension for healthcare facilities.

**Acceptance Criteria**:

- [ ] Surrogate key generated (`organization_key`)
- [ ] Natural key preserved (`organization_id`)
- [ ] All location attributes included
- [ ] Revenue information included
- [ ] Materialized as table
- [ ] Tests for unique/not_null on keys
- [ ] Model compiles and runs successfully

---

### Issue: Create dim_payers dimension

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `marts`, `dimension`, `priority:high`
**Milestone**: v0.4.0

**Description**:
Create the payers dimension for insurance companies with coverage metrics.

**Acceptance Criteria**:

- [ ] Surrogate key generated (`payer_key`)
- [ ] Natural key preserved (`payer_id`)
- [ ] All payer attributes included (name, address, phone)
- [ ] Coverage metrics included (amount_covered, amount_uncovered)
- [ ] Performance metrics included (covered_encounters, covered_medications, etc.)
- [ ] Derived `coverage_rate` calculated (amount_covered / total)
- [ ] Materialized as table
- [ ] Tests for unique/not_null on keys
- [ ] Model compiles and runs successfully

**Technical Notes**:
Full dimension with all Synthea payer attributes. Supports payer analysis use case.

---

### Issue: Create dim_date dimension

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `marts`, `dimension`, `priority:critical`
**Milestone**: v0.4.0

**Description**:
Create the calendar dimension for time-based analysis.

**Acceptance Criteria**:

- [ ] Date range covers 1909-01-01 to 2025-12-31 (117 years)
- [ ] Date key in YYYYMMDD format
- [ ] Standard calendar attributes (day, week, month, quarter, year)
- [ ] Weekend flag
- [ ] US holiday flags
- [ ] Materialized as table
- [ ] Model compiles and runs successfully

**Technical Notes**:
Use `dbt_date` package for generation. Date range must cover patient births (earliest 1909) through future buffer (2025).

---

### Issue: Create fct_encounters fact table

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `marts`, `fact`, `priority:critical`
**Milestone**: v0.4.0

**Description**:
Create the encounters fact table with all measures and dimension keys.

**Acceptance Criteria**:

- [ ] Surrogate key generated (`encounter_key`)
- [ ] All dimension keys present (patient, provider, organization, payer, date)
- [ ] All measures included (costs, duration)
- [ ] Derived measures calculated (patient_responsibility, duration_minutes)
- [ ] Denormalized patient context (age at encounter)
- [ ] Materialized as table
- [ ] Referential integrity tests added
- [ ] Model compiles and runs successfully

---

### Issue: Create fct_clinical_events fact table

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `marts`, `fact`, `priority:high`
**Milestone**: v0.4.0

**Description**:
Create unified clinical events fact from conditions, medications, and procedures.

**Acceptance Criteria**:

- [ ] Surrogate key generated (`clinical_event_key`)
- [ ] Event type discriminator (CONDITION, MEDICATION, PROCEDURE)
- [ ] Union of conditions, medications, procedures
- [ ] Consistent column mapping across sources
- [ ] Code system preserved (SNOMED, RXNORM)
- [ ] Materialized as table
- [ ] Model compiles and runs successfully

---

### Issue: Create fct_encounters_monthly fact table

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `marts`, `fact`, `aggregate`, `priority:medium`
**Milestone**: v0.4.0

**Description**:
Create monthly aggregate of encounters for time-series analysis and dashboard performance.

**Acceptance Criteria**:

- [ ] Grain: One row per year_month x encounter_class
- [ ] Aggregated encounter count
- [ ] Unique patient count per period
- [ ] Cost summaries (total_claim_cost, payer_coverage, patient_responsibility)
- [ ] Average duration minutes
- [ ] year_month in YYYY-MM format
- [ ] Materialized as table
- [ ] Unique combination test on grain columns
- [ ] Model compiles and runs successfully

**Technical Notes**:
Supports US-2 Encounter Trends use case with pre-aggregated monthly data.

---

### Issue: Create fct_encounters_yearly fact table

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `marts`, `fact`, `aggregate`, `priority:medium`
**Milestone**: v0.4.0

**Description**:
Create yearly aggregate of encounters for annual reporting.

**Acceptance Criteria**:

- [ ] Grain: One row per year x encounter_class
- [ ] Aggregated encounter count
- [ ] Unique patient count per year
- [ ] Cost summaries (total_claim_cost, payer_coverage, patient_responsibility)
- [ ] Average duration minutes
- [ ] Encounters per patient ratio
- [ ] Materialized as table
- [ ] Unique combination test on grain columns
- [ ] Model compiles and runs successfully

---

### Issue: Create int_encounters__enriched intermediate model

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `intermediate`, `priority:medium`
**Milestone**: v0.4.0

**Description**:
Create intermediate model with pre-computed encounter enrichments.

**Acceptance Criteria**:

- [ ] Condition count per encounter
- [ ] Medication count per encounter
- [ ] Procedure count per encounter
- [ ] Total event cost per encounter
- [ ] Model compiles and runs successfully

---

### Issue: Create int_patients__with_conditions intermediate model

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `intermediate`, `priority:medium`
**Milestone**: v0.4.0

**Description**:
Create intermediate model with patient condition history.

**Acceptance Criteria**:

- [ ] Total condition count per patient
- [ ] First diagnosis date
- [ ] Active conditions list (array or comma-separated)
- [ ] Chronic condition flags (diabetes, hypertension, heart disease)
- [ ] Model compiles and runs successfully

---

### Issue: Add referential integrity tests to marts

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-tester
**Labels**: `testing`, `marts`, `priority:high`
**Milestone**: v0.4.0

**Description**:
Add referential integrity tests between facts and dimensions.

**Acceptance Criteria**:

- [ ] fct_encounters references valid patient_id in dim_patients (where is_current = true)
- [ ] fct_encounters references valid provider_id in dim_providers
- [ ] fct_encounters references valid organization_id in dim_organizations
- [ ] fct_encounters references valid payer_id in dim_payers
- [ ] fct_encounters references valid date_key in dim_date
- [ ] fct_clinical_events references valid patient_id
- [ ] Aggregate facts reference valid date ranges
- [ ] `dbt test --select marts` passes

---

### Issue: Document dimensional models

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-documenter
**Labels**: `documentation`, `marts`, `priority:high`
**Milestone**: v0.4.0

**Description**:
Add comprehensive documentation to all dimensional models.

**Acceptance Criteria**:

- [ ] `_core__models.yml` created with all models
- [ ] `_healthcare__models.yml` created for intermediate models
- [ ] All models have descriptions explaining grain
- [ ] All columns have descriptions
- [ ] Example queries added to model descriptions
- [ ] `dbt docs generate` includes all marts models

---

### Issue: Code review dimensional models

**Epic**: E4-Dimensional-Models
**Assignee**: code-reviewer
**Labels**: `review`, `marts`, `priority:high`
**Milestone**: v0.4.0

**Description**:
Review all dimensional models for patterns and best practices.

**Acceptance Criteria**:

- [ ] Kimball methodology followed correctly
- [ ] Surrogate keys generated deterministically
- [ ] Naming conventions consistent
- [ ] No unnecessary denormalization
- [ ] SCD Type 2 implementation correct
- [ ] Aggregate fact grains are correct
- [ ] Query performance acceptable
- [ ] Document any recommended improvements

---

## Epic 5: Testing & Quality (E5)

### Issue: Add dbt_expectations data quality tests

**Epic**: E5-Testing-Quality
**Assignee**: dbt-tester
**Labels**: `testing`, `quality`, `priority:high`
**Milestone**: v0.5.0

**Description**:
Add comprehensive data quality tests using dbt_expectations package.

**Acceptance Criteria**:

- [ ] Date range tests (no future dates where inappropriate)
- [ ] Value range tests (costs are positive)
- [ ] String pattern tests (ZIP codes, codes)
- [ ] Null percentage tests
- [ ] Row count tests (minimum expected rows)
- [ ] Tests documented in YAML files

---

### Issue: Create singular tests for business rules

**Epic**: E5-Testing-Quality
**Assignee**: dbt-tester
**Labels**: `testing`, `quality`, `priority:medium`
**Milestone**: v0.5.0

**Description**:
Create custom singular tests for healthcare business rules.

**Acceptance Criteria**:

- [ ] Test: encounter stop_timestamp >= start_timestamp
- [ ] Test: patient death_date >= birth_date (if applicable)
- [ ] Test: no orphaned clinical events (all have valid encounters)
- [ ] Tests stored in `tests/` directory
- [ ] All tests pass

---

### Issue: Generate and deploy dbt documentation site

**Epic**: E5-Testing-Quality
**Assignee**: dbt-documenter
**Labels**: `documentation`, `quality`, `priority:high`
**Milestone**: v0.5.0

**Description**:
Generate complete dbt documentation and verify coverage.

**Acceptance Criteria**:

- [ ] `dbt docs generate` succeeds
- [ ] `dbt docs serve` displays site
- [ ] All models visible in lineage graph
- [ ] 80%+ column documentation coverage
- [ ] Example queries included where helpful
- [ ] Document how to serve docs locally

---

## Epic 6: MCP Integration (E6)

### Issue: Test MCP discovery tools

**Epic**: E6-MCP-Integration
**Assignee**: developer
**Labels**: `testing`, `mcp`, `priority:high`
**Milestone**: v0.5.0

**Description**:
Verify MCP discovery tools work correctly with the dbt project.

**Acceptance Criteria**:

- [ ] `get_all_models` returns all models
- [ ] `get_model_details` returns correct information
- [ ] `get_lineage` shows dependencies
- [ ] `get_columns` returns column information
- [ ] Document any issues found

---

### Issue: Test MCP SQL execution tools

**Epic**: E6-MCP-Integration
**Assignee**: dbt-developer
**Labels**: `testing`, `mcp`, `priority:high`
**Milestone**: v0.5.0

**Description**:
Verify MCP SQL tools work correctly.

**Acceptance Criteria**:

- [ ] `execute_sql` runs queries successfully
- [ ] `compile` returns compiled SQL
- [ ] `text_to_sql` generates valid SQL (if applicable)
- [ ] Results return in expected format
- [ ] Document any issues found

---

### Issue: Document agent workflow with MCP

**Epic**: E6-MCP-Integration
**Assignee**: sage
**Labels**: `documentation`, `mcp`, `priority:medium`
**Milestone**: v0.5.0

**Description**:
Document how agents should use MCP tools for dbt development.

**Acceptance Criteria**:

- [ ] Common MCP tool usage documented
- [ ] Example workflows for creating models
- [ ] Example workflows for testing models
- [ ] Troubleshooting guide for MCP issues
- [ ] Update LEARNINGS.md with patterns discovered

---

## Epic 7: Tuva Foundation (E7)

### Issue: Install Tuva Project dbt package

**Epic**: E7-Tuva-Foundation
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `priority:critical`
**Milestone**: v0.6.0

**Description**:
Install the Tuva Project dbt package to enable healthcare analytics.

**Acceptance Criteria**:

- [ ] Add `tuva-health/the_tuva_project` version 0.15.3 to packages.yml
- [ ] `dbt deps` installs package without conflicts
- [ ] No version conflicts with existing packages
- [ ] Document any configuration requirements

---

### Issue: Create stg_synthea__immunizations staging model

**Epic**: E7-Tuva-Foundation
**Assignee**: dbt-developer
**Labels**: `enhancement`, `staging`, `tuva`, `priority:high`
**Milestone**: v0.6.0

**Description**:
Create immunizations staging model required for Tuva's immunization input table.

**Acceptance Criteria**:

- [ ] Model reads from immunizations CSV
- [ ] All columns renamed to snake_case
- [ ] CVX codes preserved
- [ ] Patient and encounter linkage maintained
- [ ] `_loaded_at` metadata column added
- [ ] Model compiles and runs successfully

---

### Issue: Create encounter type mapping seed

**Epic**: E7-Tuva-Foundation
**Assignee**: data-modeler
**Labels**: `enhancement`, `tuva`, `seeds`, `priority:high`
**Milestone**: v0.6.0

**Description**:
Create seed file mapping Synthea encounter classes to Tuva encounter types.

**Acceptance Criteria**:

- [ ] `encounter_type_mapping.csv` created in seeds/tuva_mappings/
- [ ] Maps: ambulatory, wellness, urgentcare, emergency, inpatient, outpatient
- [ ] Tuva types: outpatient, inpatient, emergency, etc.
- [ ] `dbt seed` loads mapping successfully

---

### Issue: Create LOINC lab codes seed

**Epic**: E7-Tuva-Foundation
**Assignee**: data-modeler
**Labels**: `enhancement`, `tuva`, `seeds`, `priority:high`
**Milestone**: v0.6.0

**Description**:
Create seed file categorizing LOINC codes as vitals vs laboratory results.

**Acceptance Criteria**:

- [ ] `loinc_lab_codes.csv` created in seeds/tuva_mappings/
- [ ] Common vital sign LOINC codes categorized
- [ ] Lab result LOINC codes identified
- [ ] `dbt seed` loads categorization successfully

---

### Issue: Create int_tuva__patient connector model

**Epic**: E7-Tuva-Foundation
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `connector`, `priority:critical`
**Milestone**: v0.6.0

**Description**:
Create connector model transforming stg_synthea__patients to Tuva patient format.

**Acceptance Criteria**:

- [ ] Gender mapped (M to male, F to female)
- [ ] Race codes mapped to CDC standards
- [ ] data_source column added ('synthea')
- [ ] All required Tuva columns present
- [ ] Model compiles and runs successfully

---

### Issue: Create int_tuva__encounter connector model

**Epic**: E7-Tuva-Foundation
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `connector`, `priority:critical`
**Milestone**: v0.6.0

**Description**:
Create connector model transforming stg_synthea__encounters to Tuva encounter format.

**Acceptance Criteria**:

- [ ] Encounter class mapped to Tuva types using seed
- [ ] All required Tuva columns present
- [ ] data_source column added
- [ ] Model compiles and runs successfully

---

### Issue: Create remaining clinical connector models

**Epic**: E7-Tuva-Foundation
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `connector`, `priority:high`
**Milestone**: v0.6.0

**Description**:
Create connector models for condition, procedure, medication, observation, lab_result, immunization, practitioner, and location.

**Acceptance Criteria**:

- [ ] int_tuva__condition maps from stg_synthea__conditions
- [ ] int_tuva__procedure maps from stg_synthea__procedures
- [ ] int_tuva__medication maps from stg_synthea__medications
- [ ] int_tuva__observation filters vitals from observations
- [ ] int_tuva__lab_result filters labs from observations
- [ ] int_tuva__immunization maps from stg_synthea__immunizations
- [ ] int_tuva__practitioner maps from stg_synthea__providers
- [ ] int_tuva__location maps from stg_synthea__organizations
- [ ] All models compile and run successfully

---

### Issue: Configure Tuva clinical input layer

**Epic**: E7-Tuva-Foundation
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `config`, `priority:critical`
**Milestone**: v0.6.0

**Description**:
Configure dbt_project.yml to enable Tuva's clinical input layer.

**Acceptance Criteria**:

- [ ] clinical_input_enabled: true set in vars
- [ ] claims_input_enabled: false set in vars
- [ ] All input table refs point to connector models
- [ ] `dbt compile --select tuva_health.*` succeeds

---

### Issue: Add tests to Tuva connector models

**Epic**: E7-Tuva-Foundation
**Assignee**: dbt-tester
**Labels**: `testing`, `tuva`, `priority:high`
**Milestone**: v0.6.0

**Description**:
Add schema tests to all Tuva connector models.

**Acceptance Criteria**:

- [ ] `_tuva_connector__models.yml` created
- [ ] Primary keys have unique/not_null tests
- [ ] Foreign keys validated
- [ ] `dbt test --select tag:tuva_connector` passes

---

### Issue: Document Tuva connector models

**Epic**: E7-Tuva-Foundation
**Assignee**: dbt-documenter
**Labels**: `documentation`, `tuva`, `priority:high`
**Milestone**: v0.6.0

**Description**:
Document all Tuva connector models with transformation logic.

**Acceptance Criteria**:

- [ ] All connector models have descriptions
- [ ] Transformation logic documented
- [ ] Source-to-target mapping documented
- [ ] `dbt docs generate` includes connector models

---

## Epic 8: Clinical Marts (E8)

### Issue: Enable chronic conditions data mart

**Epic**: E8-Clinical-Marts
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `marts`, `priority:critical`
**Milestone**: v0.7.0

**Description**:
Enable and validate Tuva's chronic conditions data mart.

**Acceptance Criteria**:

- [ ] tuva_chronic_conditions_enabled: true configured
- [ ] Mart builds successfully
- [ ] Condition groupings populated for patients with conditions
- [ ] ~40 condition groups available

---

### Issue: Enable ED classification data mart

**Epic**: E8-Clinical-Marts
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `marts`, `priority:high`
**Milestone**: v0.7.0

**Description**:
Enable and validate Tuva's ED classification data mart.

**Acceptance Criteria**:

- [ ] ed_classification_enabled: true configured
- [ ] Mart builds successfully
- [ ] Emergency encounters properly classified
- [ ] Avoidable ED visits identified

---

### Issue: Enable readmissions data mart

**Epic**: E8-Clinical-Marts
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `marts`, `priority:high`
**Milestone**: v0.7.0

**Description**:
Enable and validate Tuva's readmissions data mart.

**Acceptance Criteria**:

- [ ] readmissions_enabled: true configured
- [ ] Mart builds successfully
- [ ] Index admissions identified
- [ ] 30-day readmission flags calculated

---

### Issue: Enable data profiling mart

**Epic**: E8-Clinical-Marts
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `quality`, `priority:high`
**Milestone**: v0.7.0

**Description**:
Enable Tuva's data profiling for data quality validation.

**Acceptance Criteria**:

- [ ] data_profiling_enabled: true configured
- [ ] Profiling runs successfully
- [ ] Quality report generated
- [ ] Pass rate documented (target: >95%)

---

### Issue: Validate clinical mart outputs

**Epic**: E8-Clinical-Marts
**Assignee**: dbt-tester
**Labels**: `testing`, `tuva`, `priority:critical`
**Milestone**: v0.7.0

**Description**:
Validate all clinical mart outputs for correctness.

**Acceptance Criteria**:

- [ ] Chronic condition groupings cover all patients with conditions
- [ ] ED classifications are reasonable for data
- [ ] Readmission rates within expected ranges
- [ ] Data quality tests pass (>95%)
- [ ] Sample analytics queries verified

---

### Issue: Document clinical mart usage

**Epic**: E8-Clinical-Marts
**Assignee**: dbt-documenter
**Labels**: `documentation`, `tuva`, `priority:high`
**Milestone**: v0.7.0

**Description**:
Document how to use Tuva clinical marts for analytics.

**Acceptance Criteria**:

- [ ] Chronic conditions usage guide
- [ ] ED classification interpretation
- [ ] Readmissions analysis examples
- [ ] Sample SQL queries documented

---

## Epic 9: Claims Acquisition (E9)

### Issue: Research and document CMS SynPUF data

**Epic**: E9-Claims-Acquisition
**Assignee**: developer
**Labels**: `research`, `data`, `tuva`, `priority:critical`
**Milestone**: v0.8.0

**Description**:
Research CMS SynPUF data structure and document acquisition plan.

**Acceptance Criteria**:

- [ ] CMS SynPUF documentation reviewed
- [ ] File formats and structures documented
- [ ] Storage requirements estimated
- [ ] Download procedure documented

---

### Issue: Download CMS SynPUF data files

**Epic**: E9-Claims-Acquisition
**Assignee**: developer
**Labels**: `enhancement`, `data`, `tuva`, `priority:critical`
**Milestone**: v0.8.0

**Description**:
Download CMS Synthetic Public Use Files for claims analytics.

**Acceptance Criteria**:

- [ ] Beneficiary summary files downloaded
- [ ] Inpatient claims files downloaded
- [ ] Outpatient claims files downloaded
- [ ] Carrier claims files downloaded
- [ ] PDE (Part D) files downloaded
- [ ] Files stored in dbt_project/data/cms_synpuf/

---

### Issue: Create CMS SynPUF source definitions

**Epic**: E9-Claims-Acquisition
**Assignee**: data-modeler
**Labels**: `enhancement`, `staging`, `tuva`, `priority:high`
**Milestone**: v0.8.0

**Description**:
Create source definitions for all CMS SynPUF tables.

**Acceptance Criteria**:

- [ ] `_cms_synpuf__sources.yml` created
- [ ] All SynPUF tables defined
- [ ] Column descriptions added
- [ ] Basic tests on primary keys

---

### Issue: Verify CMS SynPUF data integrity

**Epic**: E9-Claims-Acquisition
**Assignee**: dbt-tester
**Labels**: `testing`, `data`, `tuva`, `priority:high`
**Milestone**: v0.8.0

**Description**:
Verify all SynPUF files are readable and have expected structure.

**Acceptance Criteria**:

- [ ] All files readable by DuckDB
- [ ] Row counts documented
- [ ] Column counts match CMS documentation
- [ ] No corrupted files

---

## Epic 10: Claims Connector (E10)

### Issue: Create CMS SynPUF staging models

**Epic**: E10-Claims-Connector
**Assignee**: dbt-developer
**Labels**: `enhancement`, `staging`, `tuva`, `priority:critical`
**Milestone**: v0.9.0

**Description**:
Create staging models for all CMS SynPUF tables.

**Acceptance Criteria**:

- [ ] stg_synpuf__beneficiary_summary created
- [ ] stg_synpuf__inpatient_claims created
- [ ] stg_synpuf__outpatient_claims created
- [ ] stg_synpuf__carrier_claims created
- [ ] stg_synpuf__pde created
- [ ] All models compile and run

---

### Issue: Create int_tuva__eligibility connector

**Epic**: E10-Claims-Connector
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `connector`, `priority:critical`
**Milestone**: v0.9.0

**Description**:
Create connector model transforming beneficiary summary to Tuva eligibility.

**Acceptance Criteria**:

- [ ] Member spans derived from coverage months
- [ ] Demographics mapped correctly
- [ ] All required Tuva columns present
- [ ] Model compiles and runs successfully

---

### Issue: Create int_tuva__medical_claim connector

**Epic**: E10-Claims-Connector
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `connector`, `priority:critical`
**Milestone**: v0.9.0

**Description**:
Create connector model unioning inpatient, outpatient, and carrier claims.

**Acceptance Criteria**:

- [ ] Inpatient claims mapped with claim_type='institutional'
- [ ] Outpatient claims mapped with claim_type='institutional'
- [ ] Carrier claims mapped with claim_type='professional'
- [ ] All required Tuva columns present
- [ ] Model compiles and runs successfully

---

### Issue: Create int_tuva__pharmacy_claim connector

**Epic**: E10-Claims-Connector
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `connector`, `priority:critical`
**Milestone**: v0.9.0

**Description**:
Create connector model transforming PDE to Tuva pharmacy claims.

**Acceptance Criteria**:

- [ ] NDC codes preserved
- [ ] Days supply and quantity mapped
- [ ] Payment amounts mapped
- [ ] All required Tuva columns present
- [ ] Model compiles and runs successfully

---

### Issue: Configure Tuva claims input layer

**Epic**: E10-Claims-Connector
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `config`, `priority:critical`
**Milestone**: v0.9.0

**Description**:
Configure dbt_project.yml to enable Tuva's claims input layer.

**Acceptance Criteria**:

- [ ] claims_input_enabled: true set in vars
- [ ] Eligibility, medical_claim, pharmacy_claim refs configured
- [ ] `dbt compile --select tuva_health.*` succeeds with claims
- [ ] Tuva claims validation tests pass

---

### Issue: Test claims connector models

**Epic**: E10-Claims-Connector
**Assignee**: dbt-tester
**Labels**: `testing`, `tuva`, `priority:high`
**Milestone**: v0.9.0

**Description**:
Add tests and validate claims connector models.

**Acceptance Criteria**:

- [ ] Schema tests on all connector models
- [ ] Tuva validation tests pass
- [ ] Referential integrity verified
- [ ] `dbt test` passes for claims connectors

---

## Epic 11: Financial Marts (E11)

### Issue: Enable Financial PMPM data mart

**Epic**: E11-Financial-Marts
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `marts`, `priority:critical`
**Milestone**: v1.0.0

**Description**:
Enable and validate Tuva's Financial PMPM data mart.

**Acceptance Criteria**:

- [ ] pmpm_enabled: true configured
- [ ] Mart builds successfully
- [ ] PMPM by service category calculated
- [ ] Member months accurate

---

### Issue: Enable CMS-HCC risk adjustment mart

**Epic**: E11-Financial-Marts
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `marts`, `priority:critical`
**Milestone**: v1.0.0

**Description**:
Enable and validate Tuva's CMS-HCC risk adjustment data mart.

**Acceptance Criteria**:

- [ ] cms_hcc_enabled: true configured
- [ ] Mart builds successfully
- [ ] HCC conditions assigned
- [ ] RAF scores calculated

---

### Issue: Enable claims preprocessing

**Epic**: E11-Financial-Marts
**Assignee**: dbt-developer
**Labels**: `enhancement`, `tuva`, `marts`, `priority:high`
**Milestone**: v1.0.0

**Description**:
Enable Tuva's claims preprocessing for encounter grouping.

**Acceptance Criteria**:

- [ ] claims_preprocessing_enabled: true configured
- [ ] Claims grouped into encounters
- [ ] Encounter types assigned
- [ ] Mart builds successfully

---

### Issue: Validate financial mart outputs

**Epic**: E11-Financial-Marts
**Assignee**: dbt-tester
**Labels**: `testing`, `tuva`, `priority:critical`
**Milestone**: v1.0.0

**Description**:
Validate all financial mart outputs for correctness.

**Acceptance Criteria**:

- [ ] PMPM values within expected ranges
- [ ] HCC scores between 0.5 - 5.0 RAF
- [ ] All financial tests pass
- [ ] Sample analytics queries verified

---

### Issue: Document financial analytics

**Epic**: E11-Financial-Marts
**Assignee**: dbt-documenter
**Labels**: `documentation`, `tuva`, `priority:high`
**Milestone**: v1.0.0

**Description**:
Document how to use Tuva financial marts for analytics.

**Acceptance Criteria**:

- [ ] PMPM analysis guide
- [ ] HCC risk score interpretation
- [ ] Cost analysis examples
- [ ] Sample SQL queries documented

---

### Issue: Complete v1.0 milestone

**Epic**: E11-Financial-Marts
**Assignee**: developer
**Labels**: `milestone`, `release`, `priority:critical`
**Milestone**: v1.0.0

**Description**:
Finalize v1.0 release with complete Tuva integration.

**Acceptance Criteria**:

- [ ] All Tuva clinical marts operational
- [ ] All Tuva financial marts operational
- [ ] Documentation complete
- [ ] CHANGELOG updated
- [ ] Git tag v1.0.0 created
- [ ] CLAUDE.md updated to reflect completion

---

## Epic 12: Developer Experience - Git Worktrees (E12)

### Issue: Set up git worktree workflow infrastructure

**Epic**: E12-Developer-Experience
**Assignee**: developer
**Labels**: `enhancement`, `workflow`, `priority:critical`
**Milestone**: v0.4.1

**Description**:
Establish git worktree conventions and workflow for parallel Claude Code sessions. Each session ("team") can work in isolation without branch conflicts.

**Acceptance Criteria**:

- [ ] Worktree naming convention documented: `dbt-playground-{track}`
- [ ] Worktree directory location: sibling to main repo (`../dbt-playground-{track}/`)
- [ ] Branch naming tied to worktree: `feat/{track}-{feature}` or `feat/{track}`
- [ ] Track names defined (tuva, marts, docs, infra, fix)
- [ ] Workflow tested with at least 2 concurrent worktrees
- [ ] No interference between worktrees confirmed

**Technical Notes**:

```bash
# Create worktree
git worktree add ../dbt-playground-tuva -b feat/tuva-connectors main

# List worktrees
git worktree list

# Remove worktree after PR merge
git worktree remove ../dbt-playground-tuva
```

---

### Issue: Update CLAUDE.md with worktree guidance

**Epic**: E12-Developer-Experience
**Assignee**: developer
**Labels**: `documentation`, `workflow`, `priority:high`
**Milestone**: v0.4.1

**Description**:
Add a section to CLAUDE.md explaining how to work with git worktrees for parallel development.

**Acceptance Criteria**:

- [ ] New "Git Worktrees" section in CLAUDE.md
- [ ] Worktree naming convention documented
- [ ] Commands for creating worktrees documented
- [ ] Commands for checking current worktree/branch
- [ ] Commands for cleanup after PR merge
- [ ] Guidance on draft PR creation at worktree setup
- [ ] Note about commit-per-model granularity

**Content to Include**:

```markdown
## Git Worktrees (Parallel Development)

When running multiple Claude Code sessions, each session should operate in its own git worktree.

### Creating a Worktree
git worktree add ../dbt-playground-{track} -b feat/{track}-{feature} main

### Check Current Context
git worktree list
pwd  # Verify which worktree you're in

### After PR Merge
git worktree remove ../dbt-playground-{track}
git branch -d feat/{track}-{feature}
```

---

### Issue: Create FOR_CHRIS learning doc on worktrees

**Epic**: E12-Developer-Experience
**Assignee**: sage
**Labels**: `documentation`, `learning`, `priority:high`
**Milestone**: v0.4.1

**Description**:
Create a learning document in docs/for_chris/ explaining git worktrees for parallel development.

**Acceptance Criteria**:

- [ ] `docs/for_chris/GIT_WORKTREES.md` created
- [ ] Explains what git worktrees are and why they matter
- [ ] Covers the problem (parallel sessions conflict) and solution
- [ ] Step-by-step guide for creating worktrees
- [ ] Visual diagram of worktree structure
- [ ] Commands reference for common operations
- [ ] Best practices (max 3-4 concurrent, cleanup after merge)
- [ ] Troubleshooting section

**Structure**:

```markdown
# Git Worktrees for Parallel Development

## Why Worktrees?
- Problem: Multiple Claude sessions share one directory
- Solution: Each session gets its own worktree

## Quick Reference
| Action | Command |
|--------|---------|
| Create worktree | git worktree add ... |
| List worktrees | git worktree list |
| Remove worktree | git worktree remove ... |

## Step-by-Step Guide
...

## Best Practices
...
```

---

### Issue: Update supervisor/orchestrate to be worktree-aware

**Epic**: E12-Developer-Experience
**Assignee**: developer
**Labels**: `enhancement`, `agents`, `priority:medium`
**Milestone**: v0.4.1

**Description**:
Update the supervisor agent documentation to understand and work with multiple worktrees.

**Acceptance Criteria**:

- [ ] Supervisor persona docs updated with worktree awareness
- [ ] Can identify which worktree/branch a session is in
- [ ] Can list active worktrees and their assigned features
- [ ] Can recommend which worktree to use for a task
- [ ] Prevents conflicting assignments (same feature in multiple worktrees)
- [ ] `/orchestrate` command acknowledges worktree context

**Technical Notes**:

```bash
# Supervisor can use these commands to understand context
git worktree list
git branch --show-current
pwd
```

---

## Summary by Milestone

### v0.2.0 - Foundation (E1 + E2)

| Issue | Epic | Priority | Assignee |
|-------|------|----------|----------|
| Install dbt-duckdb adapter | E1 | Critical | developer |
| Create dbt profile configuration | E1 | Critical | developer |
| Initialize dbt project structure | E1 | Critical | dbt-developer |
| Configure dbt packages | E1 | High | dbt-developer |
| Configure MCP for dbt integration | E1 | High | developer |
| Update gitignore for dbt artifacts | E1 | Medium | developer |
| Verify dbt environment setup | E1 | Critical | dbt-tester |
| Generate Synthea healthcare data | E2 | Critical | developer |
| Copy Synthea data to dbt project | E2 | Critical | developer |
| Verify Synthea data integrity | E2 | High | dbt-tester |
| Create data exploration queries | E2 | Medium | data-modeler |

**Total Issues**: 11

### v0.3.0 - Staging Complete (E3)

| Issue | Epic | Priority | Assignee |
|-------|------|----------|----------|
| Create Synthea source definition | E3 | Critical | data-modeler |
| Create stg_synthea__patients model | E3 | Critical | dbt-developer |
| Create stg_synthea__encounters model | E3 | Critical | dbt-developer |
| Create stg_synthea__conditions model | E3 | High | dbt-developer |
| Create stg_synthea__medications model | E3 | High | dbt-developer |
| Create stg_synthea__procedures model | E3 | High | dbt-developer |
| Create stg_synthea__observations model | E3 | High | dbt-developer |
| Create stg_synthea__providers model | E3 | Medium | dbt-developer |
| Create stg_synthea__organizations model | E3 | Medium | dbt-developer |
| Create stg_synthea__payers model | E3 | Medium | dbt-developer |
| Add schema tests to staging models | E3 | High | dbt-tester |
| Document staging models | E3 | High | dbt-documenter |
| Code review staging layer | E3 | High | code-reviewer |

**Total Issues**: 13

### v0.4.0 - Analytics Ready (E4)

| Issue | Epic | Priority | Assignee |
|-------|------|----------|----------|
| Create dim_patients dimension | E4 | Critical | dbt-developer |
| Create dim_providers dimension | E4 | High | dbt-developer |
| Create dim_organizations dimension | E4 | High | dbt-developer |
| Create dim_payers dimension | E4 | High | dbt-developer |
| Create dim_date dimension | E4 | Critical | dbt-developer |
| Create fct_encounters fact table | E4 | Critical | dbt-developer |
| Create fct_clinical_events fact table | E4 | High | dbt-developer |
| Create fct_encounters_monthly fact table | E4 | Medium | dbt-developer |
| Create fct_encounters_yearly fact table | E4 | Medium | dbt-developer |
| Create int_encounters__enriched intermediate model | E4 | Medium | dbt-developer |
| Create int_patients__with_conditions intermediate model | E4 | Medium | dbt-developer |
| Add referential integrity tests to marts | E4 | High | dbt-tester |
| Document dimensional models | E4 | High | dbt-documenter |
| Code review dimensional models | E4 | High | code-reviewer |

**Total Issues**: 14

### v0.4.1 - Developer Experience (E12)

| Issue | Epic | Priority | Assignee |
|-------|------|----------|----------|
| Set up git worktree workflow infrastructure | E12 | Critical | developer |
| Update CLAUDE.md with worktree guidance | E12 | High | developer |
| Create FOR_CHRIS learning doc on worktrees | E12 | High | sage |
| Update supervisor/orchestrate to be worktree-aware | E12 | Medium | developer |

**Total Issues**: 4

### v0.5.0 - Production Quality (E5 + E6)

| Issue | Epic | Priority | Assignee |
|-------|------|----------|----------|
| Add dbt_expectations data quality tests | E5 | High | dbt-tester |
| Create singular tests for business rules | E5 | Medium | dbt-tester |
| Generate and deploy dbt documentation site | E5 | High | dbt-documenter |
| Test MCP discovery tools | E6 | High | developer |
| Test MCP SQL execution tools | E6 | High | dbt-developer |
| Document agent workflow with MCP | E6 | Medium | sage |

**Total Issues**: 6

---

### v0.6.0 - Tuva Foundation (E7)

| Issue | Epic | Priority | Assignee |
|-------|------|----------|----------|
| Install Tuva Project dbt package | E7 | Critical | dbt-developer |
| Create stg_synthea__immunizations staging model | E7 | High | dbt-developer |
| Create encounter type mapping seed | E7 | High | data-modeler |
| Create LOINC lab codes seed | E7 | High | data-modeler |
| Create int_tuva__patient connector model | E7 | Critical | dbt-developer |
| Create int_tuva__encounter connector model | E7 | Critical | dbt-developer |
| Create remaining clinical connector models | E7 | High | dbt-developer |
| Configure Tuva clinical input layer | E7 | Critical | dbt-developer |
| Add tests to Tuva connector models | E7 | High | dbt-tester |
| Document Tuva connector models | E7 | High | dbt-documenter |

**Total Issues**: 10

---

### v0.7.0 - Clinical Analytics (E8)

| Issue | Epic | Priority | Assignee |
|-------|------|----------|----------|
| Enable chronic conditions data mart | E8 | Critical | dbt-developer |
| Enable ED classification data mart | E8 | High | dbt-developer |
| Enable readmissions data mart | E8 | High | dbt-developer |
| Enable data profiling mart | E8 | High | dbt-developer |
| Validate clinical mart outputs | E8 | Critical | dbt-tester |
| Document clinical mart usage | E8 | High | dbt-documenter |

**Total Issues**: 6

---

### v0.8.0 - Claims Ready (E9)

| Issue | Epic | Priority | Assignee |
|-------|------|----------|----------|
| Research and document CMS SynPUF data | E9 | Critical | developer |
| Download CMS SynPUF data files | E9 | Critical | developer |
| Create CMS SynPUF source definitions | E9 | High | data-modeler |
| Verify CMS SynPUF data integrity | E9 | High | dbt-tester |

**Total Issues**: 4

---

### v0.9.0 - Claims Connector (E10)

| Issue | Epic | Priority | Assignee |
|-------|------|----------|----------|
| Create CMS SynPUF staging models | E10 | Critical | dbt-developer |
| Create int_tuva__eligibility connector | E10 | Critical | dbt-developer |
| Create int_tuva__medical_claim connector | E10 | Critical | dbt-developer |
| Create int_tuva__pharmacy_claim connector | E10 | Critical | dbt-developer |
| Configure Tuva claims input layer | E10 | Critical | dbt-developer |
| Test claims connector models | E10 | High | dbt-tester |

**Total Issues**: 6

---

### v1.0.0 - Full Analytics Platform (E11)

| Issue | Epic | Priority | Assignee |
|-------|------|----------|----------|
| Enable Financial PMPM data mart | E11 | Critical | dbt-developer |
| Enable CMS-HCC risk adjustment mart | E11 | Critical | dbt-developer |
| Enable claims preprocessing | E11 | High | dbt-developer |
| Validate financial mart outputs | E11 | Critical | dbt-tester |
| Document financial analytics | E11 | High | dbt-documenter |
| Complete v1.0 milestone | E11 | Critical | developer |

**Total Issues**: 6

---

## Labels Reference

| Label | Purpose |
|-------|---------|
| `enhancement` | New feature or capability |
| `chore` | Maintenance task |
| `testing` | Testing-related work |
| `documentation` | Documentation updates |
| `review` | Code review task |
| `setup` | Environment/configuration |
| `staging` | Staging layer models |
| `marts` | Marts layer models |
| `intermediate` | Intermediate models |
| `dimension` | Dimension tables |
| `fact` | Fact tables |
| `aggregate` | Aggregate fact tables |
| `data` | Data-related work |
| `mcp` | MCP integration |
| `quality` | Data quality |
| `tuva` | Tuva Project integration |
| `connector` | Tuva connector models |
| `seeds` | Seed file work |
| `config` | Configuration changes |
| `research` | Research/discovery work |
| `milestone` | Milestone completion |
| `release` | Release-related work |
| `workflow` | Developer workflow improvements |
| `agents` | Agent system updates |
| `learning` | Learning documentation |
| `priority:critical` | Must have for milestone |
| `priority:high` | Should have for milestone |
| `priority:medium` | Nice to have |

---

## Creating Issues

To create these issues in GitHub, use the `gh` CLI:

```bash
# Example: Create first issue
gh issue create \
  --title "Install dbt-duckdb adapter" \
  --label "enhancement,setup,priority:critical" \
  --milestone "v0.2.0" \
  --body "**Epic**: E1-Environment-Setup
**Assignee**: developer

**Description**:
Install the dbt-duckdb adapter to enable DuckDB as the data warehouse.

**Acceptance Criteria**:
- [ ] pip install dbt-duckdb executed successfully
- [ ] dbt --version shows dbt-duckdb adapter available
- [ ] Version is >= 1.7.0"
```

Or use the GitHub web interface to create issues manually.

---

*Document Created: 2026-01-28*
*Document Updated: 2026-01-29*
*Total Issues: 80 (44 original + 32 Tuva integration + 4 Developer Experience)*
