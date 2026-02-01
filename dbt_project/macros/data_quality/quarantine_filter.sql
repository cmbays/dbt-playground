{#
    Generate WHERE clause to filter out quarantined records.

    Ensures only records that pass data quality validations flow through to downstream models.

    Parameters:
        enabled (bool): Whether to apply the filter (default: true)
        field_name (string): Name of the validity flag field (default: 'is_dq_valid')

    Returns:
        SQL WHERE clause filtering to valid records only

    Example:
        select * from {{ ref('stg_synthea__encounters') }}
        {{ quarantine_filter() }}

        -- Generates:
        -- where is_dq_valid = true
#}

{% macro quarantine_filter(enabled=true, field_name='is_dq_valid') %}
    {% if enabled %}
    where {{ field_name }} = true
    {% endif %}
{% endmacro %}
