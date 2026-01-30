{{
    config(
        materialized='table',
        tags=['analytics', 'marts', 'view']
    )
}}

{#
    Patient Current Conditions View

    Purpose: Current (active) conditions for each patient
    Grain: One row per patient-condition combination where condition is active
    Use cases: Patient panels, disease management dashboards, care gap analysis

    Filters fct_condition_cohorts to only active conditions (no end date).
#}

with condition_cohorts as (
    select
        patient_key
        , patient_id
        , condition_key
        , condition_code
        , condition_description
        , first_diagnosis_date
        , months_with_condition
        , encounter_count
        , is_active
    from {{ ref('fct_condition_cohorts') }}
    where is_active = true
),

final as (
    select
        patient_key
        , patient_id
        , condition_key
        , condition_code
        , condition_description
        , first_diagnosis_date
        , months_with_condition
        , encounter_count
    from condition_cohorts
)

select * from final
