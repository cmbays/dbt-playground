-- Test: No Future Dates Validation
-- Purpose: Comprehensive check for future dates across all critical date columns
-- Severity: warn (Phase 2 already covers this via individual column tests)
-- Returns rows where any date is > current_date (should return 0 rows)

{{
    config(
        severity = 'warn'
    )
}}

with staging_patients_violations as (
    select
        'stg_synthea__patients' as source_model
        , patient_id as record_id
        , 'birth_date' as column_name
        , birth_date as date_value
    from {{ ref('stg_synthea__patients') }}
    where birth_date > current_date

    union all

    select
        'stg_synthea__patients' as source_model
        , patient_id as record_id
        , 'death_date' as column_name
        , death_date as date_value
    from {{ ref('stg_synthea__patients') }}
    where death_date > current_date
),

staging_encounters_violations as (
    select
        'stg_synthea__encounters' as source_model
        , encounter_id as record_id
        , 'encounter_start_at' as column_name
        , cast(encounter_start_at as date) as date_value
    from {{ ref('stg_synthea__encounters') }}
    where cast(encounter_start_at as date) > current_date

    union all

    select
        'stg_synthea__encounters' as source_model
        , encounter_id as record_id
        , 'encounter_end_at' as column_name
        , cast(encounter_end_at as date) as date_value
    from {{ ref('stg_synthea__encounters') }}
    where cast(encounter_end_at as date) > current_date
),

staging_conditions_violations as (
    select
        'stg_synthea__conditions' as source_model
        , condition_id as record_id
        , 'condition_start_date' as column_name
        , condition_start_date as date_value
    from {{ ref('stg_synthea__conditions') }}
    where condition_start_date > current_date

    union all

    select
        'stg_synthea__conditions' as source_model
        , condition_id as record_id
        , 'condition_end_date' as column_name
        , condition_end_date as date_value
    from {{ ref('stg_synthea__conditions') }}
    where condition_end_date > current_date
),

staging_medications_violations as (
    select
        'stg_synthea__medications' as source_model
        , medication_id as record_id
        , 'medication_start_at' as column_name
        , cast(medication_start_at as date) as date_value
    from {{ ref('stg_synthea__medications') }}
    where cast(medication_start_at as date) > current_date
),

staging_procedures_violations as (
    select
        'stg_synthea__procedures' as source_model
        , procedure_id as record_id
        , 'procedure_at' as column_name
        , cast(procedure_at as date) as date_value
    from {{ ref('stg_synthea__procedures') }}
    where cast(procedure_at as date) > current_date
),

staging_observations_violations as (
    select
        'stg_synthea__observations' as source_model
        , observation_id as record_id
        , 'observation_at' as column_name
        , cast(observation_at as date) as date_value
    from {{ ref('stg_synthea__observations') }}
    where cast(observation_at as date) > current_date
),

dim_patients_violations as (
    select
        'dim_patients' as source_model
        , cast(patient_key as varchar) as record_id
        , 'valid_from' as column_name
        , valid_from as date_value
    from {{ ref('dim_patients') }}
    where valid_from > current_date
      and patient_key != -1  -- exclude unknown member

    union all

    select
        'dim_patients' as source_model
        , cast(patient_key as varchar) as record_id
        , 'valid_to' as column_name
        , valid_to as date_value
    from {{ ref('dim_patients') }}
    where valid_to > current_date
      and patient_key != -1  -- exclude unknown member
),

fct_clinical_events_violations as (
    select
        'fct_clinical_events' as source_model
        , cast(clinical_event_key as varchar) as record_id
        , 'event_start_date' as column_name
        , event_start_date as date_value
    from {{ ref('fct_clinical_events') }}
    where event_start_date > current_date

    union all

    select
        'fct_clinical_events' as source_model
        , cast(clinical_event_key as varchar) as record_id
        , 'event_end_date' as column_name
        , event_end_date as date_value
    from {{ ref('fct_clinical_events') }}
    where event_end_date > current_date
),

all_violations as (
    select * from staging_patients_violations
    union all
    select * from staging_encounters_violations
    union all
    select * from staging_conditions_violations
    union all
    select * from staging_medications_violations
    union all
    select * from staging_procedures_violations
    union all
    select * from staging_observations_violations
    union all
    select * from dim_patients_violations
    union all
    select * from fct_clinical_events_violations
)

select *
from all_violations
