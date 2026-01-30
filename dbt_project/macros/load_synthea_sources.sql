{% macro load_synthea_sources() %}
    {#
        Load Synthea CSV files into DuckDB source tables.
        Usage: dbt run-operation load_synthea_sources
    #}
    {% set data_path = 'data/synthea' %}

    {% set tables = [
        'patients',
        'payers',
        'organizations',
        'providers',
        'encounters',
        'conditions',
        'procedures',
        'medications',
        'observations',
        'careplans',
        'allergies',
        'immunizations',
        'devices',
        'imaging_studies',
        'payer_transitions',
        'supplies'
    ] %}

    {% for table in tables %}
        {% set sql %}
            create or replace table main.{{ table }} as
            select * from read_csv_auto('{{ data_path }}/{{ table }}.csv', header=true)
        {% endset %}

        {% do log("Loading " ~ table ~ "...", info=True) %}
        {% do run_query(sql) %}
        {% do log("Loaded " ~ table, info=True) %}
    {% endfor %}

    {% do log("All Synthea sources loaded successfully!", info=True) %}
{% endmacro %}
