{{
    config(
        materialized='table',
        tags=['analytics', 'data_quality']
    )
}}

with encounter_metrics as (
    select
        'encounters' as entity_type
        , count(*) filter (where is_dq_valid = false) as quarantined_count
        , count(*) as total_count
        , round(100.0 * count(*) filter (where is_dq_valid = false) / count(*), 2) as quarantine_rate_pct
        , count(*) filter (where not valid_encounter_timestamps) as failed_valid_encounter_timestamps
        , count(*) filter (where not no_future_encounter_dates) as failed_no_future_encounter_dates
        , count(*) filter (where not end_after_1900) as failed_end_after_1900
        , count(*) filter (where not start_after_1900) as failed_start_after_1900
    from {{ ref('stg_synthea__encounters') }}
),

medication_metrics as (
    select
        'medications' as entity_type
        , count(*) filter (where is_dq_valid = false) as quarantined_count
        , count(*) as total_count
        , round(100.0 * count(*) filter (where is_dq_valid = false) / count(*), 2) as quarantine_rate_pct
        , count(*) filter (where not valid_medication_dates) as failed_valid_medication_dates
        , count(*) filter (where not no_future_medication_dates) as failed_no_future_medication_dates
        , count(*) filter (where not start_after_1900) as failed_start_after_1900
        , count(*) filter (where not end_after_1900_if_present) as failed_end_after_1900_if_present
    from {{ ref('stg_synthea__medications') }}
),

combined_metrics as (
    select
        entity_type
        , quarantined_count
        , total_count
        , quarantine_rate_pct
        , failed_valid_encounter_timestamps as failed_timestamp_validations
        , failed_no_future_encounter_dates as failed_future_date_validations
        , failed_end_after_1900 as failed_historical_end_validations
        , failed_start_after_1900 as failed_historical_start_validations
    from encounter_metrics

    union all

    select
        entity_type
        , quarantined_count
        , total_count
        , quarantine_rate_pct
        , failed_valid_medication_dates as failed_timestamp_validations
        , failed_no_future_medication_dates as failed_future_date_validations
        , failed_end_after_1900_if_present as failed_historical_end_validations
        , failed_start_after_1900 as failed_historical_start_validations
    from medication_metrics
)

select
    entity_type
    , quarantined_count
    , total_count
    , quarantine_rate_pct
    , failed_timestamp_validations
    , failed_future_date_validations
    , failed_historical_end_validations
    , failed_historical_start_validations
    , current_timestamp as _generated_at
from combined_metrics
order by entity_type
