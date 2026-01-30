-- Test: v_patient_current_conditions - All rows should be active conditions
-- This view should only contain active (current) conditions
-- Since the view filters by is_active = true, this is a sanity check
-- Returns rows that are not active (should return 0 rows)

select
    v.patient_key
    , v.patient_id
    , v.condition_key
    , v.condition_code
from {{ ref('v_patient_current_conditions') }} as v
inner join {{ ref('fct_condition_cohorts') }} as f
    on v.patient_id = f.patient_id
    and v.condition_code = f.condition_code
where f.is_active = false
