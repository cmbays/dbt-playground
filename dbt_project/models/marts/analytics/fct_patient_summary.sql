{{
    config(
        materialized='table',
        unique_key='patient_summary_key',
        tags=['analytics', 'marts', 'fact']
    )
}}

{#
    Annual Patient Summary Fact

    Purpose: Patient-level annual snapshots for outcomes tracking
    Grain: One row per patient per calendar year
    Use cases: Patient outcomes, annual cost summaries, cohort analysis

    Aggregates encounters, procedures, conditions, and costs by patient and year.
    Joins to dimensions for foreign key lookups.
#}

with encounters as (
    select
        encounter_key
        , encounter_id
        , patient_key
        , patient_id
        , provider_key
        , provider_id
        , organization_key
        , organization_id
        , payer_key
        , payer_id
        , encounter_start_date_key
        , encounter_class
        , total_claim_cost
        , payer_coverage
        , patient_responsibility
        , patient_age_at_encounter
        , encounter_start_at
    from {{ ref('fct_encounters') }}
    where patient_key != -1
),

dim_date as (
    select
        date_key
        , year_actual
    from {{ ref('dim_date') }}
),

procedures as (
    select
        encounter_id
        , count(*) as procedure_count
    from {{ ref('stg_synthea__procedures') }}
    group by encounter_id
),

conditions as (
    select
        patient_id
        , condition_code
        , extract(year from condition_start_date) as condition_year
    from {{ ref('stg_synthea__conditions') }}
),

-- join encounters to date dimension to get year
encounters_with_year as (
    select
        e.*
        , d.year_actual
        , coalesce(pr.procedure_count, 0) as procedure_count
    from encounters as e
    inner join dim_date as d on e.encounter_start_date_key = d.date_key
    left join procedures as pr on e.encounter_id = pr.encounter_id
    where e.encounter_start_date_key != -1
),

-- count distinct conditions per patient per year
conditions_per_patient_year as (
    select
        patient_id
        , condition_year as year_actual
        , count(distinct condition_code) as condition_count
    from conditions
    group by patient_id, condition_year
),

-- aggregate by patient and year
patient_year_agg as (
    select
        e.patient_id
        , e.year_actual
        , max(e.patient_key) as patient_key
        , count(*) as encounter_count
        , sum(e.procedure_count) as procedure_count
        , sum(e.total_claim_cost) as total_cost
        , sum(e.payer_coverage) as payer_coverage
        , sum(e.patient_responsibility) as patient_responsibility
        , count(distinct e.provider_id) as unique_providers
        , count(distinct e.organization_id) as unique_organizations
        , max(e.patient_age_at_encounter) as patient_age_at_year_end
    from encounters_with_year as e
    group by e.patient_id, e.year_actual
),

-- join condition counts
with_conditions as (
    select
        pya.*
        , coalesce(c.condition_count, 0) as condition_count
    from patient_year_agg as pya
    left join conditions_per_patient_year as c
        on pya.patient_id = c.patient_id
        and pya.year_actual = c.year_actual
),

final as (
    select
        -- surrogate key
        md5(cast(patient_id as varchar) || '-' || cast(year_actual as varchar)) as patient_summary_key

        -- dimension keys
        , patient_key
        , patient_id

        -- time grain
        , year_actual

        -- patient context
        , patient_age_at_year_end

        -- measures: counts
        , encounter_count
        , procedure_count
        , condition_count
        , unique_providers
        , unique_organizations

        -- measures: costs
        , coalesce(total_cost, 0) as total_cost
        , coalesce(payer_coverage, 0) as payer_coverage
        , coalesce(patient_responsibility, 0) as patient_responsibility

        -- measures: ratios
        , case
            when total_cost > 0
            then round(payer_coverage / total_cost * 100, 2)
        end as payer_coverage_pct

        -- metadata
        , current_timestamp as _loaded_at

    from with_conditions
)

select * from final
