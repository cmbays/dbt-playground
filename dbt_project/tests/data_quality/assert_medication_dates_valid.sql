-- Test: Medication Date Validation (Stretch Goal)
-- Purpose: Verify medication_end_at >= medication_start_at where end date exists
-- Severity: error
-- Returns rows that violate this constraint (should return 0 rows)

with medications_from_clinical_events as (
    select
        clinical_event_key
        , event_id as medication_id
        , patient_id
        , encounter_id
        , event_start_date as medication_start_date
        , event_end_date as medication_end_date
        , description as medication_description
    from {{ ref('fct_clinical_events') }}
    where event_type = 'MEDICATION'
),

violations as (
    select
        clinical_event_key
        , medication_id
        , patient_id
        , encounter_id
        , medication_start_date
        , medication_end_date
        , medication_description
    from medications_from_clinical_events
    where medication_end_date is not null
      and medication_end_date < medication_start_date
)

select *
from violations
