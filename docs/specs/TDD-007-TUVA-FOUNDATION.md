# TDD-007: Tuva Foundation Technical Design

## Overview

**Author**: arch: (Architect)
**Status**: Draft
**Created**: 2026-01-29
**PRD Reference**: [PRD-007-TUVA-FOUNDATION](./PRD-007-TUVA-FOUNDATION.md)
**Epic**: E7
**Version Target**: v0.6.0

---

## Executive Summary

This TDD provides detailed technical specifications for integrating the Tuva Project healthcare analytics package into dbt-playground. The implementation creates a connector layer that transforms existing Synthea staging models into Tuva's Clinical Input Layer format.

---

## Architecture Overview

### Data Flow

```text
┌─────────────────────────────────────────────────────────────┐
│                     Raw Data Layer                          │
│   dbt_project/data/synthea/*.csv (16 tables, 471K rows)     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Staging Layer                            │
│   models/staging/synthea/stg_synthea__*.sql (10 models)     │
│   - Existing: patients, encounters, conditions, etc.        │
│   - NEW: stg_synthea__immunizations                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Tuva Connector Layer (NEW)                     │
│   models/intermediate/tuva_connector/int_tuva__*.sql        │
│   - Transforms staging to Tuva Input Layer schema           │
│   - 10 connector models                                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Tuva Input Layer                            │
│   Tuva package reads from connector models via vars         │
│   clinical_input_enabled: true                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                Tuva Data Marts (E8)                         │
│   Chronic Conditions, Readmissions, ED Classification       │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Package Installation

**File**: `dbt_project/packages.yml`

```yaml
packages:
  # Existing packages
  - package: dbt-labs/dbt_utils
    version: 1.3.3

  - package: metaplane/dbt_expectations
    version: 0.10.10

  - package: godatadriven/dbt_date
    version: 0.17.1

  - package: dbt-labs/codegen
    version: 0.14.0

  # NEW: Tuva Project healthcare analytics
  - package: tuva-health/the_tuva_project
    version: 0.15.3
```

**Verification**:

```bash
cd dbt_project
dbt deps
# Expected: Successfully installed 5 packages
```

---

### 2. Configuration Updates

**File**: `dbt_project/dbt_project.yml`

Add to existing configuration:

```yaml
name: 'healthcare_analytics'
version: '0.1.0'
config-version: 2

profile: 'healthcare_analytics'

# ... existing paths ...

# Model configurations by layer
models:
  healthcare_analytics:
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: view
      +schema: intermediate
      # NEW: Tuva connector models
      tuva_connector:
        +tags: ['tuva_connector']
    marts:
      +materialized: table
      +schema: marts

# NEW: Tuva configuration variables
vars:
  # Enable clinical input layer (EHR/clinical data)
  clinical_input_enabled: true

  # Disable claims input layer (no claims data yet)
  claims_input_enabled: false

  # Map Tuva input tables to our connector models
  input_database: '{{ target.database }}'
  input_schema: 'intermediate'

  # Clinical input table references
  patient: "{{ ref('int_tuva__patient') }}"
  encounter: "{{ ref('int_tuva__encounter') }}"
  condition: "{{ ref('int_tuva__condition') }}"
  procedure: "{{ ref('int_tuva__procedure') }}"
  medication: "{{ ref('int_tuva__medication') }}"
  observation: "{{ ref('int_tuva__observation') }}"
  lab_result: "{{ ref('int_tuva__lab_result') }}"
  immunization: "{{ ref('int_tuva__immunization') }}"
  practitioner: "{{ ref('int_tuva__practitioner') }}"
  location: "{{ ref('int_tuva__location') }}"

  # Disable marts for E7 (enable in E8)
  tuva_chronic_conditions_enabled: false
  ed_classification_enabled: false
  readmissions_enabled: false
  data_profiling_enabled: false

# Seed configurations
seeds:
  healthcare_analytics:
    tuva_mappings:
      +schema: seeds
```

---

### 3. Seed File Specifications

#### 3.1 Encounter Type Mapping

**File**: `dbt_project/seeds/tuva_mappings/encounter_type_mapping.csv`

```csv
synthea_encounter_class,tuva_encounter_type,tuva_encounter_type_description
ambulatory,outpatient,Outpatient visit
wellness,outpatient,Wellness/preventive visit
outpatient,outpatient,Outpatient visit
urgentcare,emergency,Urgent care visit
emergency,emergency,Emergency department visit
inpatient,inpatient,Inpatient hospitalization
hospice,skilled nursing facility,Hospice care
home,home health,Home health visit
snf,skilled nursing facility,Skilled nursing facility
virtual,telehealth,Virtual/telehealth visit
```

**Rationale**: Synthea uses encounter classes that need mapping to Tuva's standardized encounter types for proper analytics categorization.

#### 3.2 LOINC Category Mapping

**File**: `dbt_project/seeds/tuva_mappings/loinc_category_mapping.csv`

```csv
loinc_code,category,description
8867-4,vital,Heart rate
8310-5,vital,Body temperature
8462-4,vital,Diastolic blood pressure
8480-6,vital,Systolic blood pressure
9279-1,vital,Respiratory rate
29463-7,vital,Body weight
8302-2,vital,Body height
39156-5,vital,Body mass index
59408-5,vital,Oxygen saturation
72166-2,vital,Tobacco smoking status
2708-6,lab,Oxygen saturation in arterial blood
2571-8,lab,Triglycerides
2093-3,lab,Cholesterol total
2085-9,lab,HDL cholesterol
2089-1,lab,LDL cholesterol
4548-4,lab,Hemoglobin A1c
6299-2,lab,Urea nitrogen
2160-0,lab,Creatinine
1751-7,lab,Albumin
1920-8,lab,AST
1742-6,lab,ALT
718-7,lab,Hemoglobin
26515-7,lab,Platelets
26464-8,lab,Leukocytes
```

**Rationale**: Synthea's observations table contains both vital signs and lab results. This mapping enables splitting into separate Tuva input tables.

---

### 4. Staging Model Addition

#### 4.1 stg_synthea__immunizations

**File**: `dbt_project/models/staging/synthea/stg_synthea__immunizations.sql`

```sql
with source as (
    select * from {{ source('synthea_raw', 'immunizations') }}
),

renamed as (
    select
        -- foreign keys
        PATIENT as patient_id
        , ENCOUNTER as encounter_id

        -- timestamp
        , cast(DATE as timestamp) as administered_at

        -- immunization details
        , CODE as cvx_code
        , DESCRIPTION as vaccine_description

        -- cost
        , BASE_COST as base_cost
    from source
),

with_surrogate_key as (
    select
        -- surrogate primary key
        {{ dbt_utils.generate_surrogate_key(['patient_id', 'encounter_id', 'cvx_code', 'administered_at']) }} as immunization_id
        , *
    from renamed
),

final as (
    select
        *
        , current_timestamp as _loaded_at
    from with_surrogate_key
)

select * from final
```

---

### 5. Connector Model Specifications

All connector models follow this structure:

```text
models/intermediate/tuva_connector/
├── _tuva_connector__models.yml    # Documentation and tests
├── int_tuva__patient.sql
├── int_tuva__encounter.sql
├── int_tuva__condition.sql
├── int_tuva__procedure.sql
├── int_tuva__medication.sql
├── int_tuva__observation.sql
├── int_tuva__lab_result.sql
├── int_tuva__immunization.sql
├── int_tuva__practitioner.sql
└── int_tuva__location.sql
```

#### 5.1 int_tuva__patient

**Purpose**: Transform patient demographics to Tuva patient schema.

```sql
{{
    config(
        tags=['tuva_connector', 'clinical_input'],
        materialized='view'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__patients') }}
),

transformed as (
    select
        -- Required fields
        patient_id as patient_id
        , patient_id as person_id  -- Tuva uses person_id as primary identifier

        -- Demographics
        , first_name
        , last_name
        , case
            when gender = 'M' then 'male'
            when gender = 'F' then 'female'
            else 'unknown'
          end as sex
        , birth_date
        , death_date

        -- Race mapping (Synthea uses text, Tuva expects standardized codes)
        , case race
            when 'white' then 'white'
            when 'black' then 'black'
            when 'asian' then 'asian'
            when 'native' then 'american indian or alaska native'
            when 'hawaiian' then 'native hawaiian or other pacific islander'
            when 'other' then 'other'
            else 'unknown'
          end as race

        , case ethnicity
            when 'hispanic' then 'hispanic'
            when 'nonhispanic' then 'not hispanic'
            else 'unknown'
          end as ethnicity

        -- Location
        , address as address
        , city
        , state
        , zip_code as zip_code
        , latitude
        , longitude

        -- Data source tracking
        , 'synthea' as data_source

    from source
)

select * from transformed
```

#### 5.2 int_tuva__encounter

**Purpose**: Transform encounters with type mapping via seed.

```sql
{{
    config(
        tags=['tuva_connector', 'clinical_input'],
        materialized='view'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__encounters') }}
),

encounter_mapping as (
    select * from {{ ref('encounter_type_mapping') }}
),

transformed as (
    select
        -- Keys
        enc.encounter_id
        , enc.patient_id as person_id
        , enc.patient_id

        -- Encounter details
        , coalesce(map.tuva_encounter_type, 'other') as encounter_type
        , enc.encounter_class as encounter_class_source
        , enc.encounter_code
        , enc.encounter_description

        -- Timestamps
        , cast(enc.encounter_start_at as date) as encounter_start_date
        , cast(enc.encounter_end_at as date) as encounter_end_date
        , enc.encounter_start_at as admit_datetime
        , enc.encounter_end_at as discharge_datetime

        -- Provider and facility
        , enc.provider_id as attending_provider_id
        , enc.organization_id as facility_id

        -- Financials
        , enc.total_claim_cost as total_cost
        , enc.payer_coverage as paid_amount

        -- Reason
        , enc.reason_code as primary_diagnosis_code
        , enc.reason_description as primary_diagnosis_description

        -- Data source
        , 'synthea' as data_source

    from source enc
    left join encounter_mapping map
        on lower(enc.encounter_class) = lower(map.synthea_encounter_class)
)

select * from transformed
```

#### 5.3 int_tuva__condition

**Purpose**: Transform conditions with status derivation.

```sql
{{
    config(
        tags=['tuva_connector', 'clinical_input'],
        materialized='view'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__conditions') }}
),

transformed as (
    select
        -- Keys
        condition_id
        , patient_id as person_id
        , patient_id
        , encounter_id

        -- Condition details
        , condition_code as code
        , 'snomed-ct' as code_type  -- Synthea uses SNOMED
        , condition_description as description

        -- Dates
        , cast(condition_start_date as date) as condition_date
        , cast(condition_start_date as date) as onset_date
        , cast(condition_end_date as date) as resolved_date

        -- Derived status
        , case
            when condition_end_date is not null then 'resolved'
            else 'active'
          end as condition_status

        -- Data source
        , 'synthea' as data_source

    from source
)

select * from transformed
```

#### 5.4 int_tuva__procedure

**Purpose**: Transform procedures (SNOMED codes align directly).

```sql
{{
    config(
        tags=['tuva_connector', 'clinical_input'],
        materialized='view'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__procedures') }}
),

transformed as (
    select
        -- Keys
        procedure_id
        , patient_id as person_id
        , patient_id
        , encounter_id

        -- Procedure details
        , procedure_code as code
        , 'snomed-ct' as code_type  -- Synthea uses SNOMED
        , procedure_description as description

        -- Date
        , cast(procedure_date as date) as procedure_date

        -- Cost
        , base_cost

        -- Data source
        , 'synthea' as data_source

    from source
)

select * from transformed
```

#### 5.5 int_tuva__medication

**Purpose**: Transform medications (RxNorm codes align directly).

```sql
{{
    config(
        tags=['tuva_connector', 'clinical_input'],
        materialized='view'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__medications') }}
),

transformed as (
    select
        -- Keys
        medication_id
        , patient_id as person_id
        , patient_id
        , encounter_id

        -- Medication details
        , medication_code as code
        , 'rxnorm' as code_type  -- Synthea uses RxNorm
        , medication_description as description

        -- Dates
        , cast(medication_start_at as date) as start_date
        , cast(medication_stop_at as date) as end_date

        -- Derived status
        , case
            when medication_stop_at is not null then 'stopped'
            else 'active'
          end as status

        -- Cost
        , base_cost
        , total_cost

        -- Data source
        , 'synthea' as data_source

    from source
)

select * from transformed
```

#### 5.6 int_tuva__observation

**Purpose**: Filter observations to vitals only using LOINC mapping.

```sql
{{
    config(
        tags=['tuva_connector', 'clinical_input'],
        materialized='view'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__observations') }}
),

loinc_mapping as (
    select * from {{ ref('loinc_category_mapping') }}
    where category = 'vital'
),

-- Filter to vital signs only
vitals_only as (
    select obs.*
    from source obs
    inner join loinc_mapping loinc
        on obs.observation_code = loinc.loinc_code
),

transformed as (
    select
        -- Keys
        observation_id
        , patient_id as person_id
        , patient_id
        , encounter_id

        -- Observation details
        , observation_code as code
        , 'loinc' as code_type
        , observation_description as description

        -- Value
        , observation_value as value
        , units as unit

        -- Timestamp
        , observation_at as observation_datetime
        , cast(observation_at as date) as observation_date

        -- Data source
        , 'synthea' as data_source

    from vitals_only
)

select * from transformed
```

#### 5.7 int_tuva__lab_result

**Purpose**: Filter observations to lab results only using LOINC mapping.

```sql
{{
    config(
        tags=['tuva_connector', 'clinical_input'],
        materialized='view'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__observations') }}
),

loinc_mapping as (
    select * from {{ ref('loinc_category_mapping') }}
    where category = 'lab'
),

-- Filter to lab results only
labs_only as (
    select obs.*
    from source obs
    inner join loinc_mapping loinc
        on obs.observation_code = loinc.loinc_code
),

transformed as (
    select
        -- Keys
        observation_id as lab_result_id
        , patient_id as person_id
        , patient_id
        , encounter_id

        -- Lab details
        , observation_code as code
        , 'loinc' as code_type
        , observation_description as description

        -- Result
        , observation_value as result_value
        , units as unit

        -- Timestamp
        , observation_at as result_datetime
        , cast(observation_at as date) as result_date

        -- Status (lab results are typically final)
        , 'final' as status

        -- Data source
        , 'synthea' as data_source

    from labs_only
)

select * from transformed
```

#### 5.8 int_tuva__immunization

**Purpose**: Transform immunizations (CVX codes align directly).

```sql
{{
    config(
        tags=['tuva_connector', 'clinical_input'],
        materialized='view'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__immunizations') }}
),

transformed as (
    select
        -- Keys
        immunization_id
        , patient_id as person_id
        , patient_id
        , encounter_id

        -- Immunization details
        , cvx_code as code
        , 'cvx' as code_type  -- Synthea uses CVX
        , vaccine_description as description

        -- Date
        , cast(administered_at as date) as immunization_date
        , administered_at as immunization_datetime

        -- Status (administered immunizations are complete)
        , 'completed' as status

        -- Data source
        , 'synthea' as data_source

    from source
)

select * from transformed
```

#### 5.9 int_tuva__practitioner

**Purpose**: Transform providers to practitioners.

```sql
{{
    config(
        tags=['tuva_connector', 'clinical_input'],
        materialized='view'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__providers') }}
),

transformed as (
    select
        -- Keys
        provider_id as practitioner_id
        , provider_id

        -- Name
        , provider_name as name

        -- Identifiers
        -- Note: Synthea doesn't include NPI, using placeholder
        , null as npi

        -- Specialty
        , provider_specialty as specialty

        -- Organization link
        , organization_id as facility_id

        -- Location
        , provider_address as address
        , provider_city as city
        , provider_state as state
        , provider_zip as zip_code

        -- Data source
        , 'synthea' as data_source

    from source
)

select * from transformed
```

#### 5.10 int_tuva__location

**Purpose**: Transform organizations to locations.

```sql
{{
    config(
        tags=['tuva_connector', 'clinical_input'],
        materialized='view'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__organizations') }}
),

transformed as (
    select
        -- Keys
        organization_id as location_id
        , organization_id as facility_id

        -- Name
        , organization_name as name

        -- Identifiers
        -- Note: Synthea doesn't include NPI, using placeholder
        , null as npi

        -- Location details
        , organization_address as address
        , organization_city as city
        , organization_state as state
        , organization_zip as zip_code
        , latitude
        , longitude

        -- Data source
        , 'synthea' as data_source

    from source
)

select * from transformed
```

---

### 6. YAML Configuration

**File**: `dbt_project/models/intermediate/tuva_connector/_tuva_connector__models.yml`

```yaml
version: 2

models:
  - name: int_tuva__patient
    description: >
      Transforms Synthea patient demographics to Tuva patient input layer format.
      Maps gender codes (M/F to male/female) and standardizes race/ethnicity values.
    columns:
      - name: patient_id
        description: Unique patient identifier (from Synthea)
        data_tests:
          - unique
          - not_null
      - name: person_id
        description: Tuva person identifier (same as patient_id for single-source)
        data_tests:
          - unique
          - not_null
      - name: sex
        description: Standardized sex (male, female, unknown)
        data_tests:
          - accepted_values:
              values: ['male', 'female', 'unknown']
      - name: data_source
        description: Source system identifier
        data_tests:
          - accepted_values:
              values: ['synthea']

  - name: int_tuva__encounter
    description: >
      Transforms Synthea encounters to Tuva encounter input layer format.
      Uses encounter_type_mapping seed to translate encounter classes.
    columns:
      - name: encounter_id
        description: Unique encounter identifier
        data_tests:
          - unique
          - not_null
      - name: person_id
        description: Patient identifier
        data_tests:
          - not_null
          - relationships:
              to: ref('int_tuva__patient')
              field: person_id
      - name: encounter_type
        description: Standardized Tuva encounter type
        data_tests:
          - not_null

  - name: int_tuva__condition
    description: >
      Transforms Synthea conditions to Tuva condition input layer format.
      Derives condition_status from presence of end date.
    columns:
      - name: condition_id
        description: Unique condition identifier (surrogate key)
        data_tests:
          - unique
          - not_null
      - name: person_id
        description: Patient identifier
        data_tests:
          - not_null
      - name: condition_status
        description: Derived status (active or resolved)
        data_tests:
          - accepted_values:
              values: ['active', 'resolved']

  - name: int_tuva__procedure
    description: >
      Transforms Synthea procedures to Tuva procedure input layer format.
      SNOMED codes pass through directly.
    columns:
      - name: procedure_id
        description: Unique procedure identifier (surrogate key)
        data_tests:
          - unique
          - not_null
      - name: person_id
        description: Patient identifier
        data_tests:
          - not_null

  - name: int_tuva__medication
    description: >
      Transforms Synthea medications to Tuva medication input layer format.
      RxNorm codes pass through directly.
    columns:
      - name: medication_id
        description: Unique medication identifier (surrogate key)
        data_tests:
          - unique
          - not_null
      - name: person_id
        description: Patient identifier
        data_tests:
          - not_null

  - name: int_tuva__observation
    description: >
      Filters Synthea observations to vital signs only using LOINC mapping.
      Lab results are routed to int_tuva__lab_result instead.
    columns:
      - name: observation_id
        description: Unique observation identifier (surrogate key)
        data_tests:
          - unique
          - not_null
      - name: person_id
        description: Patient identifier
        data_tests:
          - not_null

  - name: int_tuva__lab_result
    description: >
      Filters Synthea observations to laboratory results only using LOINC mapping.
      Vital signs are routed to int_tuva__observation instead.
    columns:
      - name: lab_result_id
        description: Unique lab result identifier (surrogate key)
        data_tests:
          - unique
          - not_null
      - name: person_id
        description: Patient identifier
        data_tests:
          - not_null

  - name: int_tuva__immunization
    description: >
      Transforms Synthea immunizations to Tuva immunization input layer format.
      CVX codes pass through directly.
    columns:
      - name: immunization_id
        description: Unique immunization identifier (surrogate key)
        data_tests:
          - unique
          - not_null
      - name: person_id
        description: Patient identifier
        data_tests:
          - not_null

  - name: int_tuva__practitioner
    description: >
      Transforms Synthea providers to Tuva practitioner input layer format.
      Note: NPI is null as Synthea doesn't include this identifier.
    columns:
      - name: practitioner_id
        description: Unique practitioner identifier
        data_tests:
          - unique
          - not_null

  - name: int_tuva__location
    description: >
      Transforms Synthea organizations to Tuva location input layer format.
      Note: NPI is null as Synthea doesn't include this identifier.
    columns:
      - name: location_id
        description: Unique location identifier
        data_tests:
          - unique
          - not_null
```

---

## Implementation Order

### Phase 1: Foundation (Day 1)

1. Update `packages.yml` with Tuva package
2. Run `dbt deps` to install
3. Verify no conflicts

### Phase 2: Seeds (Day 1)

1. Create `seeds/tuva_mappings/` directory
2. Create `encounter_type_mapping.csv`
3. Create `loinc_category_mapping.csv`
4. Run `dbt seed`

### Phase 3: Staging Addition (Day 1)

1. Create `stg_synthea__immunizations.sql`
2. Add to `_synthea__models.yml`
3. Run `dbt build --select stg_synthea__immunizations`

### Phase 4: Connector Models (Days 2-3)

Build in dependency order:

1. `int_tuva__patient` (no dependencies)
2. `int_tuva__location` (no dependencies)
3. `int_tuva__practitioner` (no dependencies)
4. `int_tuva__encounter` (depends on mapping seed)
5. `int_tuva__condition` (depends on patient)
6. `int_tuva__procedure` (depends on patient)
7. `int_tuva__medication` (depends on patient)
8. `int_tuva__observation` (depends on patient, LOINC seed)
9. `int_tuva__lab_result` (depends on patient, LOINC seed)
10. `int_tuva__immunization` (depends on patient)

### Phase 5: Configuration (Day 3)

1. Update `dbt_project.yml` with Tuva vars
2. Run `dbt compile --select tuva_health.*`
3. Verify compilation succeeds

### Phase 6: Testing (Day 4)

1. Create `_tuva_connector__models.yml`
2. Run `dbt test --select tag:tuva_connector`
3. Fix any failures

---

## Testing Strategy

### Unit Tests (dbt tests)

| Test Type | Coverage |
|-----------|----------|
| `unique` | All primary keys |
| `not_null` | All primary keys, person_id |
| `accepted_values` | sex, condition_status, data_source |
| `relationships` | person_id to patient |

### Integration Tests

```bash
# Full connector layer build
dbt build --select tag:tuva_connector

# Verify Tuva can compile against connectors
dbt compile --select tuva_health.*

# Row count verification
dbt show --select int_tuva__patient --limit 5
dbt show --select int_tuva__encounter --limit 5
```

### Validation Queries

```sql
-- Verify patient count matches
select
    'staging' as layer, count(*) as patients
from {{ ref('stg_synthea__patients') }}
union all
select
    'connector' as layer, count(*) as patients
from {{ ref('int_tuva__patient') }};

-- Verify observation split
select
    'total_obs' as category, count(*) as cnt
from {{ ref('stg_synthea__observations') }}
union all
select
    'vitals' as category, count(*) as cnt
from {{ ref('int_tuva__observation') }}
union all
select
    'labs' as category, count(*) as cnt
from {{ ref('int_tuva__lab_result') }};
```

---

## Risk Mitigation

| Risk | Mitigation | Status |
|------|------------|--------|
| Package version conflict | Test in isolation branch first | Planned |
| Missing LOINC codes | Start with common codes, extend as needed | Mitigated |
| Tuva schema changes | Pin to specific version (0.15.3) | Mitigated |
| Performance on observations | Use view materialization, index if needed | Planned |

---

## Open Questions Resolution

| Question | Resolution |
|----------|------------|
| Use Tuva's terminology seeds or custom? | Use custom seeds for Synthea-specific mappings |
| Placeholder for missing NPI? | Use `null` - Tuva handles missing values |
| Observation/lab split method? | Use seed file with LOINC categories |

---

## Verification Checklist

- [ ] `dbt deps` installs Tuva without errors
- [ ] `dbt seed` loads mapping files
- [ ] `dbt build --select stg_synthea__immunizations` succeeds
- [ ] `dbt build --select tag:tuva_connector` succeeds (10 models)
- [ ] `dbt test --select tag:tuva_connector` passes
- [ ] `dbt compile --select tuva_health.*` succeeds
- [ ] Documentation exists for all connector models
- [ ] Row counts verified between staging and connectors

---

## Related Documents

- **PRD**: [PRD-007-TUVA-FOUNDATION](./PRD-007-TUVA-FOUNDATION.md)
- **Integration Plan**: [TUVA-INTEGRATION-PLAN](../plans/TUVA-INTEGRATION-PLAN.md)
- **Coding Standards**: [DBT_CODING_STANDARDS](../reference/DBT_CODING_STANDARDS.md)

---

*Created: 2026-01-29*
*Author: arch: (Architect)*
