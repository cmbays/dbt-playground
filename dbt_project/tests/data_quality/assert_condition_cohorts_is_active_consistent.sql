-- Test: fct_condition_cohorts - is_active consistency validation
-- Validates that is_active = true when there is no end date for any occurrence
-- (i.e., at least one occurrence of the condition has null end_date)
-- This test checks for inconsistencies where is_active doesn't match expectations
--
-- Note: The model logic sets is_active = true when ANY occurrence has null end_date
-- So is_active = false should only happen when ALL occurrences have non-null end_date
--
-- Returns rows that violate consistency rules (should return 0 rows)

-- We check for the impossible state: is_active = false but last_diagnosis_date is NULL
-- This shouldn't happen because last_diagnosis_date being NULL indicates ongoing condition
select
    condition_cohort_key
    , patient_id
    , condition_code
    , first_diagnosis_date
    , last_diagnosis_date
    , is_active
from {{ ref('fct_condition_cohorts') }}
where is_active = false
  and last_diagnosis_date is null
