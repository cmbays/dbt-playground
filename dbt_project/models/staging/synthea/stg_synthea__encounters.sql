with source as (
    select * from {{ source('synthea_raw', 'encounters') }}
),

renamed as (
    select
        -- primary key
        Id as encounter_id

        -- foreign keys
        , PATIENT as patient_id
        , ORGANIZATION as organization_id
        , PROVIDER as provider_id
        , PAYER as payer_id

        -- timestamps
        , cast(START as timestamp) as encounter_start_at
        , cast(STOP as timestamp) as encounter_end_at

        -- attributes
        , ENCOUNTERCLASS as encounter_class
        , CODE as encounter_code
        , DESCRIPTION as encounter_description

        -- costs
        , BASE_ENCOUNTER_COST as base_encounter_cost
        , TOTAL_CLAIM_COST as total_claim_cost
        , PAYER_COVERAGE as payer_coverage

        -- reason for visit
        , REASONCODE as reason_code
        , REASONDESCRIPTION as reason_description
    from source
),

final as (
    select
        *
        , current_timestamp as _loaded_at
    from renamed
)

select * from final
