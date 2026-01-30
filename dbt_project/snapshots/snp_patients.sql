{% snapshot snp_patients %}
{#
    SCD Type 2 Snapshot for Patient Dimension

    This snapshot tracks historical changes to patient attributes over time.
    When any of the check_cols change, a new record is created with:
    - dbt_valid_from: timestamp when this version became active
    - dbt_valid_to: timestamp when this version was superseded (null if current)
    - dbt_scd_id: unique identifier for each version

    Strategy: 'check' - detect changes in specified columns
    Alternative: 'timestamp' - use a source updated_at column

    Usage:
    - Run snapshots: dbt snapshot
    - Build downstream: dbt run --select dim_patients

    Tracked columns (changes to these create new versions):
    - address, city, state, county, zip_code (location changes)
    - marital_status (life event changes)
    - healthcare_expenses, healthcare_coverage (financial changes)
#}

{{
    config(
        target_schema='snapshots',
        unique_key='patient_id',
        strategy='check',
        check_cols=[
            'address',
            'city',
            'state',
            'county',
            'zip_code',
            'marital_status',
            'healthcare_expenses',
            'healthcare_coverage'
        ],
        invalidate_hard_deletes=true
    )
}}

select
    -- natural key
    patient_id

    -- name attributes (typically don't change, but include for completeness)
    , first_name
    , last_name
    , name_prefix
    , name_suffix
    , maiden_name

    -- demographics (immutable)
    , gender
    , race
    , ethnicity

    -- dates (immutable except death_date)
    , birth_date
    , death_date

    -- location (tracked for changes)
    , address
    , city
    , state
    , county
    , zip_code
    , latitude
    , longitude
    , birth_place

    -- status (tracked for changes)
    , marital_status

    -- financial (tracked for changes)
    , healthcare_expenses
    , healthcare_coverage

    -- identifiers
    , ssn_hash
    , drivers_license
    , passport_number

    -- metadata
    , _loaded_at

from {{ ref('stg_synthea__patients') }}

{% endsnapshot %}
