{{
    config(
        materialized='table',
        unique_key='condition_key',
        tags=['analytics', 'marts', 'dimension']
    )
}}

{#
    Condition Master Dimension

    Sources: ICD/SNOMED condition codes from Synthea
    Grain: One row per unique condition code
    Primary use: Filtering encounters/observations by condition, disease management analysis

    Deduplication: Aggregates from stg_synthea__conditions to get one row per code
    with summary statistics (patient count, encounter count, date ranges).
#}

with conditions_source as (
    select
        -- cast to varchar for consistent handling (source is BIGINT SNOMED codes)
        cast(condition_code as varchar) as condition_code
        , condition_description
        , patient_id
        , encounter_id
        , condition_start_date
        , condition_end_date
    from {{ ref('stg_synthea__conditions') }}
    where condition_code is not null
),

condition_aggregates as (
    select
        condition_code
        , condition_description
        , min(condition_start_date) as first_occurrence_date
        , max(coalesce(condition_end_date, condition_start_date)) as last_occurrence_date
        , count(distinct patient_id) as patient_count
        , count(distinct encounter_id) as encounter_count
    from conditions_source
    group by condition_code, condition_description
),

-- deduplicate in case same code has different descriptions
deduped as (
    select
        condition_code
        , condition_description
        , first_occurrence_date
        , last_occurrence_date
        , patient_count
        , encounter_count
        , row_number() over (
            partition by condition_code
            order by encounter_count desc, condition_description asc
        ) as rn
    from condition_aggregates
),

sequenced as (
    select
        -- surrogate key (starting from 1, reserving -1 for unknown)
        row_number() over (order by condition_code) as condition_key

        -- natural key
        , condition_code

        -- attributes
        , condition_description
        , first_occurrence_date
        , last_occurrence_date

        -- metrics
        , patient_count
        , encounter_count

    from deduped
    where rn = 1
),

-- unknown member for handling missing dimension lookups
unknown_member as (
    select
        -1 as condition_key
        , 'UNKNOWN' as condition_code
        , 'Unknown Condition' as condition_description
        , cast(null as date) as first_occurrence_date
        , cast(null as date) as last_occurrence_date
        , 0 as patient_count
        , 0 as encounter_count
),

final as (
    select
        condition_key
        , condition_code
        , condition_description
        , first_occurrence_date
        , last_occurrence_date
        , patient_count
        , encounter_count
        , current_timestamp as _loaded_at
    from unknown_member

    union all

    select
        condition_key
        , condition_code
        , condition_description
        , first_occurrence_date
        , last_occurrence_date
        , patient_count
        , encounter_count
        , current_timestamp as _loaded_at
    from sequenced
)

select * from final
