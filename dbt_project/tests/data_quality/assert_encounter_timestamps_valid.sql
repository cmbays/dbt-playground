-- Test: Encounter Timestamp Validation
-- Purpose: Verify encounter_end_at >= encounter_start_at for all encounters
-- Severity: error
-- Returns rows that violate this constraint (should return 0 rows)

with violations as (
    select
        encounter_key
        , encounter_id
        , patient_id
        , encounter_start_at
        , encounter_end_at
        , encounter_class
    from {{ ref('fct_encounters') }}
    where encounter_end_at < encounter_start_at
)

select *
from violations
