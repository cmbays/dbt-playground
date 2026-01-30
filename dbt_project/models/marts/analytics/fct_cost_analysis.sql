{{
    config(
        materialized='table',
        unique_key='cost_analysis_key',
        tags=['analytics', 'marts', 'fact']
    )
}}

{#
    Encounter Cost Analysis Fact

    Purpose: Detailed cost breakdown for financial analysis and payer management
    Grain: One row per encounter (simplified from original spec)
    Use cases: Financial analysis, payer contract optimization, cost allocation

    Provides cost breakdown including:
    - Total cost, payer coverage, patient responsibility
    - Coverage percentages
    - Cost per procedure
#}

with encounters as (
    select
        encounter_key
        , encounter_id
        , patient_key
        , patient_id
        , payer_key
        , payer_id
        , provider_key
        , provider_id
        , encounter_start_date_key
        , encounter_class
        , total_claim_cost
        , payer_coverage
        , patient_responsibility
        , encounter_start_at
    from {{ ref('fct_encounters') }}
),

dim_date as (
    select
        date_key
        , date_actual
        , year_actual
    from {{ ref('dim_date') }}
),

procedures as (
    select
        encounter_id
        , count(*) as procedure_count
        , sum(base_cost) as procedure_cost
    from {{ ref('stg_synthea__procedures') }}
    group by encounter_id
),

-- join encounters to date and procedures
encounters_enriched as (
    select
        e.encounter_key
        , e.encounter_id
        , e.patient_key
        , e.patient_id
        , e.payer_key
        , e.payer_id
        , e.provider_key
        , e.provider_id
        , e.encounter_start_date_key
        , e.encounter_class
        , coalesce(e.total_claim_cost, 0) as total_cost
        , coalesce(e.payer_coverage, 0) as payer_coverage
        , coalesce(e.patient_responsibility, 0) as patient_responsibility
        , d.date_actual as encounter_date
        , d.year_actual
        , coalesce(p.procedure_count, 0) as procedure_count
        , p.procedure_cost
    from encounters as e
    left join dim_date as d on e.encounter_start_date_key = d.date_key
    left join procedures as p on e.encounter_id = p.encounter_id
),

final as (
    select
        -- surrogate key
        md5(encounter_id) as cost_analysis_key

        -- encounter reference
        , encounter_key
        , encounter_id

        -- dimension keys
        , patient_key
        , patient_id
        , payer_key
        , payer_id
        , provider_key
        , provider_id

        -- date dimensions
        , encounter_start_date_key as encounter_date_key
        , encounter_date
        , year_actual

        -- encounter details
        , encounter_class

        -- measures: costs
        , total_cost
        , payer_coverage
        , patient_responsibility

        -- measures: percentages
        , case
            when total_cost > 0
            then round(payer_coverage / total_cost * 100, 2)
            else 0
        end as coverage_pct

        , case
            when total_cost > 0
            then round(patient_responsibility / total_cost * 100, 2)
            else 0
        end as patient_cost_pct

        -- measures: procedure costs
        , procedure_count
        , case
            when procedure_count > 0
            then round(total_cost / procedure_count, 2)
        end as cost_per_procedure

        -- metadata
        , current_timestamp as _loaded_at

    from encounters_enriched
)

select * from final
