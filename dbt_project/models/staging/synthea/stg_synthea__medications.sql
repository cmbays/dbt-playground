with source as (
    select * from {{ source('synthea_raw', 'medications') }}
),

renamed as (
    select
        -- foreign keys
        PATIENT as patient_id
        , PAYER as payer_id
        , ENCOUNTER as encounter_id

        -- timestamps
        , cast(START as timestamp) as medication_start_at
        , cast(STOP as timestamp) as medication_end_at

        -- medication details
        , CODE as medication_code
        , DESCRIPTION as medication_description

        -- costs
        , BASE_COST as base_cost
        , PAYER_COVERAGE as payer_coverage
        , DISPENSES as dispenses
        , TOTALCOST as total_cost

        -- reason for medication
        , REASONCODE as reason_code
        , REASONDESCRIPTION as reason_description
    from source
),

with_row_number as (
    select
        *
        , row_number() over (
            partition by patient_id, encounter_id, medication_code, medication_start_at
            order by medication_end_at nulls last, total_cost desc
        ) as _row_num
    from renamed
),

with_surrogate_key as (
    select
        -- surrogate primary key (includes row_num for true duplicates)
        {{ dbt_utils.generate_surrogate_key(['patient_id', 'encounter_id', 'medication_code', 'medication_start_at', '_row_num']) }} as medication_id
        , patient_id
        , payer_id
        , encounter_id
        , medication_start_at
        , medication_end_at
        , medication_code
        , medication_description
        , base_cost
        , payer_coverage
        , dispenses
        , total_cost
        , reason_code
        , reason_description
    from with_row_number
),

final as (
    select
        *
        , current_timestamp as _loaded_at
    from with_surrogate_key
)

select * from final
