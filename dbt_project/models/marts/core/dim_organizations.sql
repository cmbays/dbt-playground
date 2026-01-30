{{
    config(
        materialized='table',
        unique_key='organization_key'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__organizations') }}
),

sequenced as (
    select
        -- surrogate key (starting from 1, reserving -1 for unknown)
        row_number() over (order by organization_id) as organization_key

        -- natural key
        , organization_id

        -- attributes
        , organization_name
        , address
        , city
        , state
        , zip_code
        , phone

        -- location
        , latitude
        , longitude

        -- metrics
        , revenue
        , utilization

        -- metadata
        , current_timestamp as _loaded_at

    from source
),

-- unknown member for handling missing dimension lookups
unknown_member as (
    select
        -1 as organization_key
        , 'UNKNOWN' as organization_id
        , 'Unknown Organization' as organization_name
        , cast(null as varchar) as address
        , cast(null as varchar) as city
        , cast(null as varchar) as state
        , cast(null as varchar) as zip_code
        , cast(null as varchar) as phone
        , cast(null as double) as latitude
        , cast(null as double) as longitude
        , cast(null as double) as revenue
        , cast(null as bigint) as utilization
        , current_timestamp as _loaded_at
),

final as (
    select * from unknown_member
    union all
    select * from sequenced
)

select * from final
