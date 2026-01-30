with source as (
    select * from {{ source('synthea_raw', 'observations') }}
),

renamed as (
    select
        -- foreign keys
        PATIENT as patient_id
        , ENCOUNTER as encounter_id

        -- timestamp
        , cast(DATE as timestamp) as observation_at

        -- observation details
        , CODE as observation_code
        , DESCRIPTION as observation_description
        , VALUE as observation_value
        , UNITS as units
        , TYPE as observation_type
    from source
),

with_row_number as (
    select
        *
        , row_number() over (
            partition by patient_id, encounter_id, observation_code, observation_at
            order by observation_value, observation_description
        ) as _row_num
    from renamed
),

with_surrogate_key as (
    select
        -- surrogate primary key (includes row_num for true duplicates)
        {{ dbt_utils.generate_surrogate_key(['patient_id', 'encounter_id', 'observation_code', 'observation_at', '_row_num']) }} as observation_id
        , patient_id
        , encounter_id
        , observation_at
        , observation_code
        , observation_description
        , observation_value
        , units
        , observation_type
    from with_row_number
),

final as (
    select
        *
        , current_timestamp as _loaded_at
    from with_surrogate_key
)

select * from final
