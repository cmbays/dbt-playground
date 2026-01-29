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
Create the patient dimension with demographics and derived attributes.

**Acceptance Criteria**:

- [ ] Surrogate key generated (`patient_key`)
- [ ] Natural key preserved (`patient_id`)
- [ ] All demographic attributes included
- [ ] Derived fields: `full_name`, `age_years`, `is_deceased`
- [ ] Materialized as table
- [ ] Tests for unique/not_null on keys
- [ ] Model compiles and runs successfully

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
- [ ] Organization linkage maintained
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

### Issue: Create dim_date dimension

**Epic**: E4-Dimensional-Models
**Assignee**: dbt-developer
**Labels**: `enhancement`, `marts`, `dimension`, `priority:critical`
**Milestone**: v0.4.0

**Description**:
Create the calendar dimension for time-based analysis.

**Acceptance Criteria**:

- [ ] Date range covers 2015-01-01 to 2025-12-31 (or data range)
- [ ] Date key in YYYYMMDD format
- [ ] Standard calendar attributes (day, week, month, quarter, year)
- [ ] Weekend flag
- [ ] US holiday flags (optional)
- [ ] Materialized as table
- [ ] Model compiles and runs successfully

**Technical Notes**:
Consider using `dbt_date` package for generation.

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
- [ ] All dimension keys present (patient, provider, organization, date)
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

- [ ] fct_encounters references valid patient_id in dim_patients
- [ ] fct_encounters references valid provider_id in dim_providers
- [ ] fct_encounters references valid organization_id in dim_organizations
- [ ] fct_encounters references valid date_key in dim_date
- [ ] fct_clinical_events references valid patient_id
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
| Create dim_date dimension | E4 | Critical | dbt-developer |
| Create fct_encounters fact table | E4 | Critical | dbt-developer |
| Create fct_clinical_events fact table | E4 | High | dbt-developer |
| Create int_encounters__enriched intermediate model | E4 | Medium | dbt-developer |
| Create int_patients__with_conditions intermediate model | E4 | Medium | dbt-developer |
| Add referential integrity tests to marts | E4 | High | dbt-tester |
| Document dimensional models | E4 | High | dbt-documenter |
| Code review dimensional models | E4 | High | code-reviewer |

**Total Issues**: 11

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
| `data` | Data-related work |
| `mcp` | MCP integration |
| `quality` | Data quality |
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
*Total Issues: 41*
