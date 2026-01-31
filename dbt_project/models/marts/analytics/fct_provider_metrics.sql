{{
    config(
        materialized='table',
        unique_key='provider_metrics_key',
        tags=['analytics', 'marts', 'fact']
    )
}}

{#
    Monthly Provider Metrics Fact

    Purpose: Provider-level utilization and performance metrics
    Grain: One row per provider per calendar month
    Use cases: Provider performance dashboards, utilization trending, quality measures

    Aggregates encounters, patients, procedures, and costs by provider and month.
    Calculates derived metrics like avg cost per encounter and encounters per patient.
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
        , encounter_start_date_key
        , total_claim_cost
        , payer_coverage
        , duration_minutes
        , patient_age_at_encounter
    from {{ ref('fct_encounters') }}
    where provider_key != -1
),

dim_date as (
    select
        date_key
        , year_actual
        , month_actual
    from {{ ref('dim_date') }}
),

procedures as (
    select
        encounter_id
        , count(*) as procedure_count
    from {{ ref('stg_synthea__procedures') }}
    group by encounter_id
),

-- join encounters to date dimension to get year/month
encounters_with_date as (
    select
        e.*
        , d.year_actual
        , d.month_actual
        , cast(d.year_actual as varchar)
            || '-'
            || lpad(cast(d.month_actual as varchar), 2, '0') as year_month_str
        , coalesce(pr.procedure_count, 0) as procedure_count
    from encounters as e
    inner join dim_date as d on e.encounter_start_date_key = d.date_key
    left join procedures as pr on e.encounter_id = pr.encounter_id
    where e.encounter_start_date_key != -1
),

-- aggregate by provider and year-month
provider_month_agg as (
    select
        e.provider_id
        , e.provider_key
        , e.organization_id
        , e.organization_key
        , e.year_actual
        , e.month_actual
        , e.year_month_str

        -- counts
        , count(*) as encounter_count
        , count(distinct e.patient_id) as unique_patient_count

        -- patient metrics
        , avg(e.patient_age_at_encounter) as avg_patient_age

        -- encounter metrics
        , avg(e.duration_minutes) as avg_encounter_duration_minutes

        -- procedure metrics
        , sum(e.procedure_count) as total_procedures

        -- cost metrics
        , sum(e.total_claim_cost) as total_cost
        , sum(e.payer_coverage) as total_payer_coverage

    from encounters_with_date as e
    group by
        e.provider_id
        , e.provider_key
        , e.organization_id
        , e.organization_key
        , e.year_actual
        , e.month_actual
        , e.year_month_str
),

final as (
    select
        -- surrogate key
        md5(cast(provider_id as varchar) || '-' || year_month_str) as provider_metrics_key

        -- dimension keys
        , provider_key
        , provider_id
        , organization_key
        , organization_id

        -- time grain
        , year_actual
        , month_actual
        , year_month_str

        -- measures: counts
        , encounter_count
        , unique_patient_count
        , total_procedures

        -- measures: averages
        , round(avg_patient_age, 2) as avg_patient_age
        , round(avg_encounter_duration_minutes, 2) as avg_encounter_duration_minutes

        -- measures: costs
        , coalesce(total_cost, 0) as total_cost
        , coalesce(total_payer_coverage, 0) as total_payer_coverage

        -- measures: derived ratios
        , case
            when encounter_count > 0
            then round(total_cost / encounter_count, 2)
            else 0
        end as avg_cost_per_encounter

        , case
            when unique_patient_count > 0
            then round(cast(encounter_count as decimal) / unique_patient_count, 2)
            else 0
        end as encounters_per_patient_avg

        -- metadata
        , current_timestamp as _loaded_at

    from provider_month_agg
)

select * from final
