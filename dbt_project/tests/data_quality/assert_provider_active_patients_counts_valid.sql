-- Test: v_provider_active_patients - Count consistency validation
-- Validates that active_patient_count >= 0 for all providers
-- (0 is valid since view includes all providers via left join)
-- Also validates avg_conditions_per_patient is consistent with counts
-- Returns rows that violate these constraints (should return 0 rows)

select
    provider_key
    , provider_id
    , provider_name
    , active_patient_count
    , total_active_conditions
    , avg_conditions_per_patient
from {{ ref('v_provider_active_patients') }}
where active_patient_count < 0
   or total_active_conditions < 0
   or avg_conditions_per_patient < 0
   -- also check consistency: if active_patient_count > 0, avg should match
   or (
       active_patient_count > 0
       and abs(avg_conditions_per_patient - (cast(total_active_conditions as decimal) / active_patient_count)) > 0.01
   )
