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

with_dq_flags as (
    {{ add_dq_flags(
        source_cte='renamed',
        validations={
            'valid_encounter_timestamps': 'encounter_end_at >= encounter_start_at',
            'no_future_encounter_dates': 'encounter_start_at <= current_timestamp',
            'end_after_1900': 'encounter_end_at >= timestamp \'1900-01-01\'',
            'start_after_1900': 'encounter_start_at >= timestamp \'1900-01-01\''
        }
    ) }}
),

final as (
    select
        *
        , current_timestamp as _loaded_at
    from with_dq_flags
)

select * from final
