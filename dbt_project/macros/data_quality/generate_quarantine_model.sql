{#
    Generate a complete quarantine model that isolates invalid records.

    Creates a model that selects only records with is_dq_valid = false from a source staging model.
    This allows data quality issues to be investigated without polluting downstream marts.

    Parameters:
        source_model (string): Name of the staging model to quarantine from
        description (string): Optional description for the quarantine table

    Returns:
        Complete SQL SELECT statement for quarantine model

    Example:
        {{ config(materialized='table', tags=['quarantine', 'data_quality']) }}

        {{ generate_quarantine_model(
            source_model='stg_synthea__encounters',
            description='Encounters quarantined due to data quality violations'
        ) }}

        -- Generates:
        -- -- Encounters quarantined due to data quality violations
        -- select * from {{ ref('stg_synthea__encounters') }}
        -- where is_dq_valid = false
#}

{% macro generate_quarantine_model(source_model, description='') %}
{% if description %}
-- {{ description }}
{% endif %}
select * from {{ ref(source_model) }}
where is_dq_valid = false
{% endmacro %}
