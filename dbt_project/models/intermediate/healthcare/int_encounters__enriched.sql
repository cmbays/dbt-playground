{{
    config(
        materialized='view'
    )
}}

with encounters as (
    select
        encounter_id
    from {{ ref('fct_encounters') }}
),

conditions as (
    select
        encounter_id
        , count(*) as condition_count
        , cast(0 as decimal(18, 2)) as total_condition_cost
    from {{ ref('stg_synthea__conditions') }}
    group by encounter_id
),

medications as (
    select
        encounter_id
        , count(*) as medication_count
        , coalesce(sum(total_cost), 0) as total_medication_cost
    from {{ ref('stg_synthea__medications') }}
    {{ quarantine_filter() }}
    group by encounter_id
),

procedures as (
    select
        encounter_id
        , count(*) as procedure_count
        , coalesce(sum(base_cost), 0) as total_procedure_cost
    from {{ ref('stg_synthea__procedures') }}
    group by encounter_id
),

final as (
    select
        e.encounter_id
        , coalesce(c.condition_count, 0) as condition_count
        , coalesce(m.medication_count, 0) as medication_count
        , coalesce(p.procedure_count, 0) as procedure_count
        , coalesce(c.condition_count, 0)
            + coalesce(m.medication_count, 0)
            + coalesce(p.procedure_count, 0) as total_event_count
        , coalesce(c.total_condition_cost, 0) as total_condition_cost
        , coalesce(m.total_medication_cost, 0) as total_medication_cost
        , coalesce(p.total_procedure_cost, 0) as total_procedure_cost
        , coalesce(c.total_condition_cost, 0)
            + coalesce(m.total_medication_cost, 0)
            + coalesce(p.total_procedure_cost, 0) as total_event_cost
    from encounters as e
    left join conditions as c on e.encounter_id = c.encounter_id
    left join medications as m on e.encounter_id = m.encounter_id
    left join procedures as p on e.encounter_id = p.encounter_id
)

select * from final
