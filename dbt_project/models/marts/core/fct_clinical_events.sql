{{
    config(
        materialized='table',
        unique_key='clinical_event_key'
    )
}}

with conditions as (
    select
        condition_id as event_id
        , 'CONDITION' as event_type
        , patient_id
        , encounter_id
        , condition_start_date as event_start_date
        , condition_end_date as event_end_date
        , condition_code as code
        , 'SNOMED-CT' as code_system
        , condition_description as description
        , cast(null as varchar) as reason_code
        , cast(null as varchar) as reason_description
        , cast(null as decimal(18, 2)) as event_cost
    from {{ ref('stg_synthea__conditions') }}
),

medications as (
    select
        medication_id as event_id
        , 'MEDICATION' as event_type
        , patient_id
        , encounter_id
        , cast(medication_start_at as date) as event_start_date
        , cast(medication_end_at as date) as event_end_date
        , medication_code as code
        , 'RXNORM' as code_system
        , medication_description as description
        , reason_code
        , reason_description
        , total_cost as event_cost
    from {{ ref('stg_synthea__medications') }}
),

procedures as (
    select
        procedure_id as event_id
        , 'PROCEDURE' as event_type
        , patient_id
        , encounter_id
        , cast(procedure_at as date) as event_start_date
        , cast(null as date) as event_end_date
        , procedure_code as code
        , 'SNOMED-CT' as code_system
        , procedure_description as description
        , reason_code
        , reason_description
        , base_cost as event_cost
    from {{ ref('stg_synthea__procedures') }}
),

all_events as (
    select * from conditions
    union all
    select * from medications
    union all
    select * from procedures
),

patients as (
    select
        patient_key
        , patient_id
    from {{ ref('dim_patients') }}
    where is_current = true
),

dim_date as (
    select
        date_key
        , date_actual
    from {{ ref('dim_date') }}
),

encounters as (
    select
        encounter_key
        , encounter_id
    from {{ ref('fct_encounters') }}
),

final as (
    select
        -- surrogate key
        row_number() over (order by e.event_id) as clinical_event_key

        -- event identifiers
        , e.event_type
        , e.event_id

        -- dimension keys
        , coalesce(p.patient_key, -1) as patient_key
        , e.patient_id
        , coalesce(enc.encounter_key, -1) as encounter_key
        , e.encounter_id
        , coalesce(d.date_key, -1) as event_date_key

        -- dates
        , e.event_start_date
        , e.event_end_date

        -- code information
        , e.code
        , e.code_system
        , e.description

        -- reason
        , e.reason_code
        , e.reason_description

        -- cost
        , e.event_cost

        -- metadata
        , current_timestamp as _loaded_at

    from all_events e
    left join patients p on e.patient_id = p.patient_id
    left join encounters enc on e.encounter_id = enc.encounter_id
    left join dim_date d on e.event_start_date = d.date_actual
)

select * from final
