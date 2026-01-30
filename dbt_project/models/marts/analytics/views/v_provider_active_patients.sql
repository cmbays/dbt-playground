{{
    config(
        materialized='table',
        tags=['analytics', 'marts', 'view']
    )
}}

{#
    Provider Active Patients View

    Purpose: Active patient count per provider for panel management
    Grain: One row per provider
    Use cases: Provider workload analysis, panel management, capacity planning

    Aggregates patients with active conditions by their most recent provider.
    A patient is attributed to the provider who saw them most recently for an active condition.
#}

with providers as (
    select
        provider_key
        , provider_id
        , provider_name
        , organization_key
        , organization_id
    from {{ ref('dim_providers') }}
    where provider_key != -1
),

-- get current conditions with their most recent encounter
current_conditions as (
    select
        cc.patient_key
        , cc.patient_id
        , cc.condition_key
        , cc.condition_code
    from {{ ref('fct_condition_cohorts') }} as cc
    where cc.is_active = true
),

-- get the most recent encounter per patient to determine their provider
patient_recent_encounters as (
    select
        patient_id
        , provider_key
        , provider_id
        , row_number() over (
            partition by patient_id
            order by encounter_start_at desc
        ) as rn
    from {{ ref('fct_encounters') }}
    where provider_key != -1
),

-- assign patients to their most recent provider
patient_provider_assignment as (
    select
        patient_id
        , provider_key
        , provider_id
    from patient_recent_encounters
    where rn = 1
),

-- join active conditions to provider assignments
active_conditions_by_provider as (
    select
        ppa.provider_key
        , ppa.provider_id
        , cc.patient_id
        , cc.condition_key
    from current_conditions as cc
    inner join patient_provider_assignment as ppa
        on cc.patient_id = ppa.patient_id
),

-- aggregate by provider
provider_summary as (
    select
        provider_key
        , provider_id
        , count(distinct patient_id) as active_patient_count
        , count(*) as total_active_conditions
    from active_conditions_by_provider
    group by provider_key, provider_id
),

final as (
    select
        p.provider_key
        , p.provider_id
        , p.provider_name
        , p.organization_key
        , p.organization_id
        , coalesce(ps.active_patient_count, 0) as active_patient_count
        , coalesce(ps.total_active_conditions, 0) as total_active_conditions
        , case
            when coalesce(ps.active_patient_count, 0) > 0
            then round(
                cast(ps.total_active_conditions as decimal) / ps.active_patient_count,
                2
            )
            else 0
        end as avg_conditions_per_patient
    from providers as p
    left join provider_summary as ps
        on p.provider_key = ps.provider_key
)

select * from final
