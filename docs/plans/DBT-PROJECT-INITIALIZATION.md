# Plan: Initialize dbt Project with Healthcare Data

## Summary

Initialize an operational dbt project using **Synthea synthetic healthcare data** with **DuckDB** as the local database, complete with MCP tooling for AI agent-assisted development.

---

## Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Database** | DuckDB | Zero infrastructure, analytics-optimized, native CSV support, excellent MCP compatibility |
| **Data Source** | Synthea | Free synthetic healthcare data, no approvals, realistic structure, existing dbt integrations |
| **Secondary Reference** | Tuva Project | Study pre-built healthcare dbt patterns after initial setup |

---

## Phase 1: Database Setup (DuckDB)

### 1.1 Install dbt-duckdb Adapter

```bash
pip install dbt-duckdb
```

### 1.2 Create dbt Profile

Create `~/.dbt/profiles.yml`:

```yaml
dbt_playground:
  outputs:
    dev:
      type: duckdb
      path: ./dbt_project/dev.duckdb
      threads: 4
    prod:
      type: duckdb
      path: ./dbt_project/prod.duckdb
      threads: 4
  target: dev
```

**Note**: The `.duckdb` files will be created automatically on first run.

---

## Phase 2: Healthcare Data Acquisition (Synthea)

### 2.1 Option A: Generate Fresh Data (Recommended)

```bash
# Clone Synthea
git clone https://github.com/synthetichealth/synthea.git /tmp/synthea
cd /tmp/synthea

# Enable CSV export (edit src/main/resources/synthea.properties)
# Set: exporter.csv.export = true

# Generate 500 synthetic patients (good learning size)
./run_synthea -p 500 --exporter.csv.export true

# Output will be in /tmp/synthea/output/csv/
```

### 2.2 Option B: Use Pre-Generated Sample

Download sample Synthea CSV files from community sources if Java setup is problematic.

### 2.3 Synthea Data Structure

Key tables for dimensional modeling:

| Table | Type | Description |
|-------|------|-------------|
| `patients.csv` | Dimension | Patient demographics |
| `encounters.csv` | Fact | Healthcare visits/encounters |
| `conditions.csv` | Fact | Diagnoses |
| `medications.csv` | Fact | Prescriptions |
| `procedures.csv` | Fact | Medical procedures |
| `observations.csv` | Fact | Vital signs, lab results |
| `providers.csv` | Dimension | Healthcare providers |
| `organizations.csv` | Dimension | Healthcare facilities |
| `payers.csv` | Dimension | Insurance payers |
| `careplans.csv` | Bridge | Care plan assignments |

---

## Phase 3: dbt Project Initialization

### 3.1 Initialize Project

```bash
cd /Users/cmbays/Documents/claude/dbt-playground
dbt init dbt_project
cd dbt_project
```

### 3.2 Project Structure

```text
dbt_project/
├── dbt_project.yml           # Project configuration
├── packages.yml              # Package dependencies
├── profiles.yml              # (gitignored - use ~/.dbt/)
│
├── seeds/                    # Reference data (small CSVs)
│   └── ref_icd10_codes.csv   # ICD-10 code mappings
│
├── data/                     # Raw Synthea data (gitignored)
│   └── synthea/
│       ├── patients.csv
│       ├── encounters.csv
│       └── ...
│
├── models/
│   ├── staging/              # stg_ models (source cleaning)
│   │   ├── synthea/
│   │   │   ├── _synthea__sources.yml
│   │   │   ├── _synthea__models.yml
│   │   │   ├── stg_synthea__patients.sql
│   │   │   ├── stg_synthea__encounters.sql
│   │   │   ├── stg_synthea__conditions.sql
│   │   │   ├── stg_synthea__medications.sql
│   │   │   ├── stg_synthea__procedures.sql
│   │   │   ├── stg_synthea__observations.sql
│   │   │   ├── stg_synthea__providers.sql
│   │   │   ├── stg_synthea__organizations.sql
│   │   │   └── stg_synthea__payers.sql
│   │   └── README.md
│   │
│   ├── intermediate/         # int_ models (business logic)
│   │   └── healthcare/
│   │       ├── int_encounters__enriched.sql
│   │       └── int_patients__with_conditions.sql
│   │
│   └── marts/                # fct_/dim_ models (analytics)
│       ├── core/
│       │   ├── dim_patients.sql
│       │   ├── dim_providers.sql
│       │   ├── dim_organizations.sql
│       │   ├── dim_date.sql
│       │   ├── fct_encounters.sql
│       │   └── fct_clinical_events.sql
│       └── _core__models.yml
│
├── tests/                    # Custom singular tests
│   └── assert_valid_encounter_dates.sql
│
├── macros/                   # Reusable SQL macros
│   ├── generate_schema_name.sql
│   └── healthcare_utils.sql
│
├── snapshots/                # SCD Type 2 tracking
│   └── scd_patients.sql
│
└── analyses/                 # Ad-hoc queries
    └── patient_cohort_analysis.sql
```

### 3.3 dbt_project.yml Configuration

```yaml
name: 'dbt_playground'
version: '0.1.0'
config-version: 2

profile: 'dbt_playground'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

clean-targets:
  - "target"
  - "dbt_packages"

models:
  dbt_playground:
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: view
      +schema: intermediate
    marts:
      +materialized: table
      +schema: marts
```

---

## Phase 4: Package Installation

### 4.1 packages.yml

```yaml
packages:
  # Core utilities - essential macros and tests
  - package: dbt-labs/dbt_utils
    version: 1.3.0

  # Data quality testing framework
  - package: calogica/dbt_expectations
    version: 0.10.4

  # Date/time utilities (for dim_date)
  - package: calogica/dbt_date
    version: 0.10.1

  # Code generation helpers
  - package: dbt-labs/codegen
    version: 0.12.1
```

### 4.2 Install Packages

```bash
dbt deps
```

---

## Phase 5: MCP Configuration

### 5.1 Update .mcp.json

Update `/Users/cmbays/Documents/claude/dbt-playground/.mcp.json`:

```json
{
  "mcpServers": {
    "dbt": {
      "command": "uvx",
      "args": ["dbt-mcp"],
      "env": {
        "DBT_PROJECT_PATH": "./dbt_project",
        "DBT_PROFILES_DIR": "~/.dbt"
      }
    }
  }
}
```

### 5.2 Install dbt-mcp

```bash
pip install dbt-mcp
# Or use uvx (no installation needed)
uvx dbt-mcp --help
```

### 5.3 Available MCP Tools

Once configured, agents will have access to:

| Category | Tools |
|----------|-------|
| **Discovery** | `get_all_models`, `get_model_details`, `get_lineage`, `get_columns` |
| **SQL** | `execute_sql`, `text_to_sql`, `compile` |
| **CLI** | `build`, `run`, `test`, `docs`, `seed` |
| **Code Gen** | `generate_model_yaml`, `generate_source`, `generate_staging_model` |
| **Semantic** | `list_metrics`, `query_metrics`, `get_dimensions` |

---

## Phase 6: Initial Model Implementation

### 6.1 Source Definition

Create `models/staging/synthea/_synthea__sources.yml`:

```yaml
version: 2

sources:
  - name: synthea_raw
    description: Raw Synthea synthetic healthcare data
    schema: main
    tables:
      - name: patients
        description: Patient demographics
        columns:
          - name: Id
            description: Unique patient identifier (UUID)
            data_tests:
              - unique
              - not_null
      - name: encounters
        description: Healthcare encounters/visits
        columns:
          - name: Id
            data_tests:
              - unique
              - not_null
      - name: conditions
      - name: medications
      - name: procedures
      - name: observations
      - name: providers
      - name: organizations
      - name: payers
```

### 6.2 Sample Staging Model

Create `models/staging/synthea/stg_synthea__patients.sql`:

```sql
with source as (
    select * from read_csv_auto('data/synthea/patients.csv')
),

renamed as (
    select
        -- Primary key
        Id as patient_id,

        -- Demographics
        FIRST as first_name,
        LAST as last_name,
        BIRTHDATE as birth_date,
        DEATHDATE as death_date,
        SSN as ssn_hash,  -- Would hash in production
        GENDER as gender,
        RACE as race,
        ETHNICITY as ethnicity,
        MARITAL as marital_status,

        -- Location
        ADDRESS as address,
        CITY as city,
        STATE as state,
        COUNTY as county,
        ZIP as zip_code,
        LAT as latitude,
        LON as longitude,

        -- Healthcare
        HEALTHCARE_EXPENSES as total_healthcare_expenses,
        HEALTHCARE_COVERAGE as total_healthcare_coverage,

        -- Metadata
        current_timestamp as _loaded_at

    from source
)

select * from renamed
```

### 6.3 Sample Fact Model

Create `models/marts/core/fct_encounters.sql`:

```sql
{{
  config(
    materialized='table',
    unique_key='encounter_id'
  )
}}

with encounters as (
    select * from {{ ref('stg_synthea__encounters') }}
),

patients as (
    select * from {{ ref('stg_synthea__patients') }}
),

final as (
    select
        -- Keys
        e.encounter_id,
        e.patient_id,
        e.provider_id,
        e.organization_id,
        e.payer_id,

        -- Date keys (for dim_date joins)
        cast(e.start_timestamp as date) as encounter_date_key,

        -- Encounter details
        e.encounter_class,
        e.encounter_code,
        e.encounter_description,
        e.reason_code,
        e.reason_description,

        -- Timestamps
        e.start_timestamp,
        e.stop_timestamp,

        -- Measures
        e.base_encounter_cost,
        e.total_claim_cost,
        e.payer_coverage,
        e.total_claim_cost - e.payer_coverage as patient_responsibility,
        timestampdiff('minute', e.start_timestamp, e.stop_timestamp) as duration_minutes,

        -- Patient context (denormalized for performance)
        p.birth_date as patient_birth_date,
        date_diff('year', p.birth_date, cast(e.start_timestamp as date)) as patient_age_at_encounter,
        p.gender as patient_gender,

        -- Metadata
        current_timestamp as _loaded_at

    from encounters e
    left join patients p on e.patient_id = p.patient_id
)

select * from final
```

---

## Phase 7: Data Loading Strategy

### 7.1 DuckDB Native CSV Loading

DuckDB can read CSVs directly in SQL (no separate load step):

```sql
-- In any model, reference CSV directly
select * from read_csv_auto('data/synthea/patients.csv')
```

### 7.2 For Larger Datasets

Create a loading script `scripts/load_synthea.py`:

```python
import duckdb

con = duckdb.connect('dbt_project/dev.duckdb')

# Load each Synthea table
tables = ['patients', 'encounters', 'conditions', 'medications',
          'procedures', 'observations', 'providers', 'organizations', 'payers']

for table in tables:
    con.execute(f"""
        CREATE OR REPLACE TABLE raw_{table} AS
        SELECT * FROM read_csv_auto('data/synthea/{table}.csv')
    """)
    print(f"Loaded {table}")

con.close()
```

---

## Phase 8: Verification & Testing

### 8.1 Verify dbt Setup

```bash
cd dbt_project

# Check connection
dbt debug

# Install packages
dbt deps

# Compile models (no execution)
dbt compile

# Run staging models
dbt run --select staging

# Run all models
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

### 8.2 Verify MCP Integration

```bash
# List available MCP servers
claude mcp list

# Test dbt-mcp connection
# (In Claude Code, the dbt tools should be available)
```

### 8.3 Agent Workflow Test

Test the full agent workflow:

1. `dbt-model: design a patient cohort analysis model`
2. `dbt-dev: implement the cohort model`
3. `dbt-test: add data quality tests`
4. `dbt-docs: document the new model`

---

## Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `dbt_project/dbt_project.yml` | Project configuration |
| `dbt_project/packages.yml` | Package dependencies |
| `dbt_project/models/staging/synthea/_synthea__sources.yml` | Source definitions |
| `dbt_project/models/staging/synthea/stg_synthea__*.sql` | 9 staging models |
| `dbt_project/models/marts/core/dim_*.sql` | 4 dimension models |
| `dbt_project/models/marts/core/fct_*.sql` | 2 fact models |
| `dbt_project/models/marts/core/_core__models.yml` | Model documentation |
| `scripts/load_synthea.py` | Data loading script |
| `scripts/generate_synthea.sh` | Synthea generation script |

### Modified Files

| File | Change |
|------|--------|
| `.mcp.json` | Add dbt-mcp configuration |
| `.gitignore` | Add `dbt_project/data/`, `*.duckdb`, `dbt_project/target/` |
| `CLAUDE.md` | Update project status and structure |

---

## Implementation Order

1. **Environment Setup**
   - Install dbt-duckdb
   - Create ~/.dbt/profiles.yml
   - Update .mcp.json

2. **Data Acquisition**
   - Generate or download Synthea data
   - Place CSVs in dbt_project/data/synthea/

3. **Project Initialization**
   - Run `dbt init dbt_project`
   - Configure dbt_project.yml
   - Create packages.yml and run `dbt deps`

4. **Staging Layer**
   - Create source definitions
   - Implement 9 staging models
   - Add basic tests

5. **Marts Layer**
   - Create dimension models (dim_patients, dim_providers, dim_date)
   - Create fact models (fct_encounters, fct_clinical_events)
   - Add documentation

6. **Verification**
   - Run full dbt pipeline
   - Test MCP integration
   - Verify agent workflows

---

## Success Criteria

- [ ] `dbt debug` passes successfully
- [ ] `dbt run` completes without errors
- [ ] `dbt test` passes all tests
- [ ] `dbt docs serve` shows documentation site
- [ ] MCP tools accessible in Claude Code
- [ ] Agents can interact with dbt project via MCP
- [ ] Healthcare data follows dimensional modeling patterns

---

## Future Enhancements (Post-MVP)

- Add Tuva Project package for claims analytics patterns
- Implement SCD Type 2 for patient dimension
- Add source freshness monitoring
- Create semantic layer metrics
- Build healthcare-specific macros (ICD code parsing, age calculations)
- Add dbt_expectations tests for data quality
