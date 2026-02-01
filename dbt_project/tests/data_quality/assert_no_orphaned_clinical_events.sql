-- Test: No Orphaned Clinical Events
-- Purpose: Verify all clinical events (conditions, medications, procedures) reference valid encounters
-- Severity: error
-- Returns rows where the encounter_key = -1 (unknown member), indicating orphaned events

with clinical_events_with_missing_encounters as (
    select
        clinical_event_key
        , event_type
        , event_id
        , patient_id
        , encounter_id
        , encounter_key
        , event_start_date
        , description
    from {{ ref('fct_clinical_events') }}
    where encounter_key = -1
      and encounter_id is not null  -- only flag if encounter_id was provided but not found
),

-- additionally check for events with null encounter_id (data quality issue)
events_with_null_encounter_id as (
    select
        clinical_event_key
        , event_type
        , event_id
        , patient_id
        , encounter_id
        , encounter_key
        , event_start_date
        , description
    from {{ ref('fct_clinical_events') }}
    where encounter_id is null
),

violations as (
    select
        clinical_event_key
        , event_type
        , event_id
        , patient_id
        , encounter_id
        , encounter_key
        , event_start_date
        , description
        , 'encounter_not_found' as violation_type
    from clinical_events_with_missing_encounters

    union all

    select
        clinical_event_key
        , event_type
        , event_id
        , patient_id
        , encounter_id
        , encounter_key
        , event_start_date
        , description
        , 'null_encounter_id' as violation_type
    from events_with_null_encounter_id
)

select *
from violations
