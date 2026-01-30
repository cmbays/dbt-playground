with source as (
    select * from {{ source('synthea_raw', 'providers') }}
),

renamed as (
    select
        -- primary key
        Id as provider_id

        -- foreign key
        , ORGANIZATION as organization_id

        -- attributes
        , NAME as provider_name
        , GENDER as gender
        , SPECIALITY as specialty

        -- location
        , ADDRESS as address
        , CITY as city
        , STATE as state
        , ZIP as zip_code
        , LAT as latitude
        , LON as longitude

        -- metrics
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
