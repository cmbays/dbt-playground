with source as (
    select * from {{ source('synthea_raw', 'procedures') }}
),

renamed as (
    select
        -- foreign keys
        PATIENT as patient_id
        , ENCOUNTER as encounter_id

        -- timestamp
        , cast(DATE as timestamp) as procedure_at

        -- procedure details
        , CODE as procedure_code
        , DESCRIPTION as procedure_description
        , BASE_COST as base_cost

        -- reason for procedure
        , REASONCODE as reason_code
        , REASONDESCRIPTION as reason_description
    from source
),

with_surrogate_key as (
    select
        -- surrogate primary key (no natural key exists)
        {{ dbt_utils.generate_surrogate_key(['patient_id', 'encounter_id', 'procedure_code', 'procedure_at']) }} as procedure_id
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
