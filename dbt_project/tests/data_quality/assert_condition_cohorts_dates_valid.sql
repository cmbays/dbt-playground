-- Test: fct_condition_cohorts - Date order validation
-- Validates that first_diagnosis_date <= last_diagnosis_date when both are non-null
-- Returns rows that violate this constraint (should return 0 rows)

select
    condition_cohort_key
    , patient_id
    , condition_code
    , first_diagnosis_date
    , last_diagnosis_date
from {{ ref('fct_condition_cohorts') }}
where last_diagnosis_date is not null
  and first_diagnosis_date > last_diagnosis_date
