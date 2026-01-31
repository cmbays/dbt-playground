-- Test: fct_cost_analysis - Cost allocation validation
-- Validates that payer_coverage + patient_responsibility approximately equals total_cost
-- Allows for small rounding differences (0.01)
-- Returns rows that violate this constraint (should return 0 rows)

select
    cost_analysis_key
    , encounter_id
    , total_cost
    , payer_coverage
    , patient_responsibility
    , (payer_coverage + patient_responsibility) as calculated_total
    , abs(total_cost - (payer_coverage + patient_responsibility)) as difference
from {{ ref('fct_cost_analysis') }}
where total_cost > 0
  and abs(total_cost - (payer_coverage + patient_responsibility)) > 0.01
