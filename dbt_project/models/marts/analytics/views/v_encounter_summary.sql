{{
    config(
        materialized='ephemeral',
        tags=['analytics', 'marts', 'view']
    )
}}

{#
    Encounter Summary View (Ephemeral)

    Purpose: Enriched encounter view with dimension attributes
    Materialization: Ephemeral (not persisted) - used as a building block
    Use cases: Ad-hoc queries, building blocks for other models, BI tool queries

    Joins fct_encounters with all dimension tables to provide a denormalized
    view with human-readable names instead of just keys.
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
        , encounter_start_at
        , encounter_class
        , encounter_description
        , total_claim_cost
        , payer_coverage
        , patient_responsibility
        , duration_minutes
    from {{ ref('fct_encounters') }}
),

patients as (
    select
        patient_key
        , full_name as patient_name
    from {{ ref('dim_patients') }}
    where is_current = true
),

providers as (
    select
        provider_key
        , provider_name
    from {{ ref('dim_providers') }}
),

organizations as (
    select
        organization_key
        , organization_name
    from {{ ref('dim_organizations') }}
),

payers as (
    select
        payer_key
        , payer_name
    from {{ ref('dim_payers') }}
),

final as (
    select
        -- identifiers
        e.encounter_id
        , cast(e.encounter_start_at as date) as encounter_date

        -- patient
        , e.patient_id
        , coalesce(p.patient_name, 'Unknown Patient') as patient_name

        -- provider
        , e.provider_id
        , coalesce(pr.provider_name, 'Unknown Provider') as provider_name

        -- organization
        , e.organization_id
        , coalesce(o.organization_name, 'Unknown Organization') as organization_name

        -- payer
        , e.payer_id
        , coalesce(py.payer_name, 'Unknown Payer') as payer_name

        -- encounter details
        , e.encounter_class
        , e.encounter_description
        , e.duration_minutes

        -- costs
        , coalesce(e.total_claim_cost, 0) as total_cost
        , coalesce(e.payer_coverage, 0) as payer_coverage
        , coalesce(e.patient_responsibility, 0) as patient_responsibility

    from encounters as e
    left join patients as p on e.patient_key = p.patient_key
    left join providers as pr on e.provider_key = pr.provider_key
    left join organizations as o on e.organization_key = o.organization_key
    left join payers as py on e.payer_key = py.payer_key
)

select * from final
