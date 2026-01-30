{{
    config(
        materialized='table',
        unique_key=['year_month', 'encounter_class']
    )
}}

with encounters as (
    select
        encounter_id
        , patient_id
        , encounter_start_date_key
        , encounter_class
        , total_claim_cost
        , payer_coverage
        , patient_responsibility
        , duration_minutes
    from {{ ref('fct_encounters') }}
),

dim_date as (
    select
        date_key
        , year_actual
        , month_actual
    from {{ ref('dim_date') }}
),

encounters_with_date as (
    select
        e.*
        , d.year_actual
        , d.month_actual
        , cast(d.year_actual as varchar) || '-' ||
            lpad(cast(d.month_actual as varchar), 2, '0') as year_month
    from encounters e
    inner join dim_date d on e.encounter_start_date_key = d.date_key
    where e.encounter_start_date_key != -1
),

final as (
    select
        year_month
        , year_actual
        , month_actual
        , encounter_class
        , count(*) as encounter_count
        , count(distinct patient_id) as unique_patients
        , sum(total_claim_cost) as total_claim_cost
        , sum(payer_coverage) as total_payer_coverage
        , sum(patient_responsibility) as total_patient_responsibility
        , avg(duration_minutes) as avg_duration_minutes
        , current_timestamp as _loaded_at
    from encounters_with_date
    group by year_month, year_actual, month_actual, encounter_class
)

select * from final
