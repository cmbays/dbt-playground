{{
    config(
        materialized='table',
        unique_key='provider_key'
    )
}}

with providers as (
    select * from {{ ref('stg_synthea__providers') }}
),

organizations as (
    select
        organization_key
        , organization_id
    from {{ ref('dim_organizations') }}
),

sequenced as (
    select
        -- surrogate key (starting from 1, reserving -1 for unknown)
        row_number() over (order by p.provider_id) as provider_key

        -- natural key
        , p.provider_id

        -- organization foreign key
        , o.organization_key
        , p.organization_id

        -- attributes
        , p.provider_name
        , p.gender
        , p.specialty

        -- location
        , p.address
        , p.city
        , p.state
        , p.zip_code
        , p.latitude
        , p.longitude

        -- metrics
        , p.utilization

        -- metadata
        , current_timestamp as _loaded_at

    from providers p
    left join organizations o
        on p.organization_id = o.organization_id
),

-- unknown member for handling missing dimension lookups
unknown_member as (
    select
        -1 as provider_key
        , 'UNKNOWN' as provider_id
        , -1 as organization_key
        , 'UNKNOWN' as organization_id
        , 'Unknown Provider' as provider_name
        , cast(null as varchar) as gender
        , cast(null as varchar) as specialty
        , cast(null as varchar) as address
        , cast(null as varchar) as city
        , cast(null as varchar) as state
        , cast(null as varchar) as zip_code
        , cast(null as double) as latitude
        , cast(null as double) as longitude
        , cast(null as bigint) as utilization
        , current_timestamp as _loaded_at
),

final as (
    select * from unknown_member
    union all
    select * from sequenced
)

select * from final
