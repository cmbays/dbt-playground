{{
    config(
        materialized='table',
        unique_key='encounter_key'
    )
}}

with encounters as (
    select * from {{ ref('stg_synthea__encounters') }}
    {{ quarantine_filter() }}
),

patients as (
    select
        patient_key
        , patient_id
        , birth_date
    from {{ ref('dim_patients') }}
    where is_current = true
),

providers as (
    select
        provider_key
        , provider_id
    from {{ ref('dim_providers') }}
),

organizations as (
    select
        organization_key
        , organization_id
    from {{ ref('dim_organizations') }}
),

payers as (
    select
        payer_key
        , payer_id
    from {{ ref('dim_payers') }}
),

dim_date as (
    select
        date_key
        , date_actual
    from {{ ref('dim_date') }}
),

final as (
    select
        -- surrogate key
        row_number() over (order by e.encounter_id) as encounter_key

        -- natural key
        , e.encounter_id

        -- dimension keys
        , coalesce(p.patient_key, -1) as patient_key
        , e.patient_id
        , coalesce(pr.provider_key, -1) as provider_key
        , e.provider_id
        , coalesce(o.organization_key, -1) as organization_key
        , e.organization_id
        , coalesce(py.payer_key, -1) as payer_key
        , e.payer_id

        -- date keys
        , coalesce(ds.date_key, -1) as encounter_start_date_key
        , coalesce(de.date_key, -1) as encounter_end_date_key

        -- attributes
        , e.encounter_class
        , e.encounter_code
        , e.encounter_description
        , e.reason_code
        , e.reason_description

        -- timestamps
        , e.encounter_start_at
        , e.encounter_end_at

        -- derived duration
        , date_diff('minute', e.encounter_start_at, e.encounter_end_at) as duration_minutes

        -- costs
        , e.base_encounter_cost
        , e.total_claim_cost
        , e.payer_coverage
        , e.total_claim_cost - coalesce(e.payer_coverage, 0) as patient_responsibility

        -- derived patient context
        , case
            when p.birth_date is not null
            then date_diff('year', p.birth_date, cast(e.encounter_start_at as date))
        end as patient_age_at_encounter

        -- metadata
        , current_timestamp as _loaded_at

    from encounters as e
    left join patients as p on e.patient_id = p.patient_id
    left join providers as pr on e.provider_id = pr.provider_id
    left join organizations as o on e.organization_id = o.organization_id
    left join payers as py on e.payer_id = py.payer_id
    left join dim_date as ds on cast(e.encounter_start_at as date) = ds.date_actual
    left join dim_date as de on cast(e.encounter_end_at as date) = de.date_actual
)

select * from final
