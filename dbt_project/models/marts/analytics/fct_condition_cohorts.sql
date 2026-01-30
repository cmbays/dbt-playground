{{
    config(
        materialized='table',
        unique_key='condition_cohort_key',
        tags=['analytics', 'marts', 'fact']
    )
}}

{#
    Patient-Condition Cohort Fact

    Purpose: Patient-condition relationships for disease management and outcomes analysis
    Grain: One row per patient-condition combination (first occurrence)
    Use cases: Disease management, outcomes by condition, cohort analysis

    Aggregates condition occurrences by patient to show:
    - First and last diagnosis dates
    - Duration of condition
    - Number of encounters with the condition
    - Active status (no end date = currently active)
#}

with conditions_source as (
    select
        patient_id
        , encounter_id
        -- cast to varchar for consistent handling (source is BIGINT SNOMED codes)
        , cast(condition_code as varchar) as condition_code
        , condition_description
        , condition_start_date
        , condition_end_date
    from {{ ref('stg_synthea__conditions') }}
    where condition_code is not null
      and patient_id is not null
),

patients as (
    select
        patient_key
        , patient_id
    from {{ ref('dim_patients') }}
    where is_current = true
),

dim_conditions as (
    select
        condition_key
        , condition_code
    from {{ ref('dim_conditions') }}
),

-- aggregate conditions by patient and condition code
condition_windows as (
    select
        patient_id
        , condition_code
        , max(condition_description) as condition_description
        , min(condition_start_date) as first_diagnosis_date
        , max(condition_end_date) as last_diagnosis_date
        , count(distinct encounter_id) as encounter_count
        -- if any occurrence has no end date, condition is considered active
        , count(case when condition_end_date is null then 1 end) > 0 as is_active
    from conditions_source
    group by patient_id, condition_code
),

-- join to dimensions
with_dimensions as (
    select
        cw.patient_id
        , cw.condition_code
        , cw.condition_description
        , cw.first_diagnosis_date
        , cw.last_diagnosis_date
        , cw.encounter_count
        , cw.is_active
        , coalesce(p.patient_key, -1) as patient_key
        , coalesce(dc.condition_key, -1) as condition_key
    from condition_windows as cw
    left join patients as p on cw.patient_id = p.patient_id
    left join dim_conditions as dc on cw.condition_code = dc.condition_code
),

final as (
    select
        -- surrogate key
        md5(cast(patient_id as varchar) || '-' || condition_code) as condition_cohort_key

        -- dimension keys
        , patient_key
        , patient_id
        , condition_key
        , condition_code

        -- condition details
        , condition_description

        -- date dimensions
        , first_diagnosis_date
        , last_diagnosis_date
        , extract(year from first_diagnosis_date) as first_diagnosis_year

        -- measures: duration
        , case
            when last_diagnosis_date is not null and first_diagnosis_date is not null
            then greatest(
                0,
                (extract(year from last_diagnosis_date) - extract(year from first_diagnosis_date)) * 12
                + (extract(month from last_diagnosis_date) - extract(month from first_diagnosis_date))
            )
            else 0
        end as months_with_condition

        -- measures: counts
        , encounter_count

        -- measures: status
        , is_active

        -- metadata
        , current_timestamp as _loaded_at

    from with_dimensions
)

select * from final
