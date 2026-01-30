with source as (
    select * from {{ source('synthea_raw', 'conditions') }}
),

renamed as (
    select
        -- foreign keys
        PATIENT as patient_id
        , ENCOUNTER as encounter_id

        -- dates
        , START as condition_start_date
        , STOP as condition_end_date

        -- condition details
        , CODE as condition_code
        , DESCRIPTION as condition_description
    from source
),

with_surrogate_key as (
    select
        -- surrogate primary key (no natural key exists)
        {{ dbt_utils.generate_surrogate_key(['patient_id', 'encounter_id', 'condition_code', 'condition_start_date']) }} as condition_id
        , *
    from renamed
),

final as (
    select
        *
        , current_timestamp as _loaded_at
    from with_surrogate_key
)

select * from final
