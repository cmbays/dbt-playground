{#
    Add data quality validation flags to a CTE.

    Parameters:
        source_cte (string): Name of the CTE to validate
        validations (dict): Dictionary of validation_name: sql_condition pairs

    Returns:
        SQL SELECT statement with:
        - All original columns from source_cte
        - Individual validation flags (boolean) for each validation
        - is_dq_valid (boolean): True if all validations pass
        - failed_dq_tests (varchar[]): Array of failed validation names

    Example:
        {{ add_dq_flags(
            source_cte='renamed',
            validations={
                'valid_timestamps': 'end_at >= start_at',
                'no_future_dates': 'start_at <= current_timestamp'
            }
        ) }}
#}

{% macro add_dq_flags(source_cte, validations) %}
    select
        *

        -- individual validation flags
        {% for validation_name, condition in validations.items() %}
        , ({{ condition }}) as {{ validation_name }}
        {% endfor %}

        -- overall validity flag
        , {{ _all_validations_pass(validations) }} as is_dq_valid

        -- array of failed test names
        , {{ _collect_failed_tests(validations) }} as failed_dq_tests

    from {{ source_cte }}
{% endmacro %}

{#
    Helper macro: Generate AND clause for all validations
#}
{% macro _all_validations_pass(validations) %}
    (
        {% for validation_name, condition in validations.items() %}
        ({{ condition }})
        {% if not loop.last %} and {% endif %}
        {% endfor %}
    )
{% endmacro %}

{#
    Helper macro: Collect failed test names into array
#}
{% macro _collect_failed_tests(validations) %}
    list_value(
        {% for validation_name, condition in validations.items() %}
        case when not ({{ condition }}) then '{{ validation_name }}' else null end
        {% if not loop.last %}, {% endif %}
        {% endfor %}
    )
{% endmacro %}
