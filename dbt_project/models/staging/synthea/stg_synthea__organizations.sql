with source as (
    select * from {{ source('synthea_raw', 'organizations') }}
),

renamed as (
    select
        -- primary key
        Id as organization_id

        -- attributes
        , NAME as organization_name
        , ADDRESS as address
        , CITY as city
        , STATE as state
        , ZIP as zip_code
        , PHONE as phone

        -- location
        , LAT as latitude
        , LON as longitude

        -- metrics
        , REVENUE as revenue
        , UTILIZATION as utilization
    from source
),

final as (
    select
        *
        , current_timestamp as _loaded_at
    from renamed
)

select * from final
