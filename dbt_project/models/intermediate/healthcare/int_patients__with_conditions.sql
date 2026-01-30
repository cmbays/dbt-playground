{{
    config(
        materialized='view'
    )
}}

{#
    Patient condition history with chronic disease flags.

    IMPORTANT: Chronic Condition Detection Limitations
    --------------------------------------------------
    The chronic condition flags (has_diabetes, has_hypertension, has_heart_disease)
    use simplified text matching on condition_description. This is NOT clinical-grade
    detection and should be used for analytics/reporting only, not clinical decisions.

    Detection patterns:
    - Diabetes: description contains 'diabetes'
    - Hypertension: description contains 'hypertension' or 'high blood pressure'
    - Heart disease: description contains 'heart disease', 'cardiac', 'coronary',
                     or 'atrial fibrillation'

    For production clinical use, consider:
    1. Using SNOMED codes instead of text matching
    2. Implementing ICD-10 code mappings
    3. Consulting clinical informaticists for proper condition groupings
    4. Moving patterns to a seed file or reference table for maintainability
#}

with patients as (
    select
        patient_id
    from {{ ref('dim_patients') }}
    where is_current = true
),

conditions as (
    select
        patient_id
        , condition_start_date
        , condition_end_date
        , condition_code
        , condition_description
    from {{ ref('stg_synthea__conditions') }}
),

condition_stats as (
    select
        patient_id
        , count(*) as total_conditions
        , sum(case when condition_end_date is null then 1 else 0 end) as active_conditions
        , min(condition_start_date) as first_condition_date
        , max(condition_start_date) as last_condition_date
    from conditions
    group by patient_id
),

chronic_flags as (
    select
        patient_id
        , max(case
            when lower(condition_description) like '%diabetes%' then 1
            else 0
        end) as has_diabetes
        , max(case
            when lower(condition_description) like '%hypertension%'
                or lower(condition_description) like '%high blood pressure%' then 1
            else 0
        end) as has_hypertension
        , max(case
            when lower(condition_description) like '%heart disease%'
                or lower(condition_description) like '%cardiac%'
                or lower(condition_description) like '%coronary%'
                or lower(condition_description) like '%atrial fibrillation%' then 1
            else 0
        end) as has_heart_disease
    from conditions
    group by patient_id
),

chronic_count as (
    select
        patient_id
        , has_diabetes + has_hypertension + has_heart_disease as chronic_condition_count
    from chronic_flags
),

final as (
    select
        p.patient_id
        , coalesce(cs.total_conditions, 0) as total_conditions
        , coalesce(cs.active_conditions, 0) as active_conditions
        , cs.first_condition_date
        , cs.last_condition_date
        , coalesce(cast(cf.has_diabetes as boolean), false) as has_diabetes
        , coalesce(cast(cf.has_hypertension as boolean), false) as has_hypertension
        , coalesce(cast(cf.has_heart_disease as boolean), false) as has_heart_disease
        , coalesce(cc.chronic_condition_count, 0) as chronic_condition_count
    from patients p
    left join condition_stats cs on p.patient_id = cs.patient_id
    left join chronic_flags cf on p.patient_id = cf.patient_id
    left join chronic_count cc on p.patient_id = cc.patient_id
)

select * from final
