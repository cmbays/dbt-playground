{{
    config(
        materialized='table',
        tags=['intermediate', 'quarantine', 'data_quality']
    )
}}

{{ generate_quarantine_model(
    source_model='stg_synthea__encounters',
    description='Encounters quarantined due to data quality violations'
) }}
