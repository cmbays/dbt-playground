-- Test: Patient Date Validation
-- Purpose: Verify death_date >= birth_date when death_date is NOT NULL
-- Severity: error
-- Returns rows that violate this constraint (should return 0 rows)

with violations as (
    select
        patient_key
        , patient_id
        , full_name
        , birth_date
        , death_date
    from {{ ref('dim_patients') }}
    where death_date is not null
      and death_date < birth_date
)

select *
from violations
