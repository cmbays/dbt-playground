{{
    config(
        materialized='table',
        unique_key='patient_key'
    )
}}

-- depends_on: {{ ref('snp_patients') }}
-- depends_on: {{ ref('stg_synthea__patients') }}

{#
    Patient Dimension with SCD Type 2 History Tracking

    This dimension sources from the snp_patients snapshot, which tracks
    changes to patient attributes over time. Each row represents a
    specific version of a patient's record.

    SCD Type 2 Columns:
    - patient_key: Surrogate key (unique per version)
    - patient_id: Natural key (same across versions)
    - valid_from: When this version became active
    - valid_to: When this version was superseded (null = current)
    - is_current: True for the active version

    To query current patients only:
        WHERE is_current = true

    To query patient state at a point in time:
        WHERE valid_from <= @date AND (valid_to > @date OR valid_to IS NULL)
#}

with snapshot_source as (
    -- source from snapshot for SCD2 history
    -- falls back to staging if snapshot doesn't exist yet
    {% if execute %}
        {% set snapshot_exists = adapter.get_relation(
            database=target.database,
            schema='snapshots',
            identifier='snp_patients'
        ) is not none %}
    {% else %}
        {% set snapshot_exists = false %}
    {% endif %}

    {% if snapshot_exists %}
    select
        patient_id
        , first_name
        , last_name
        , name_prefix
        , name_suffix
        , gender
        , race
        , ethnicity
        , marital_status
        , birth_date
        , death_date
        , address
        , city
        , state
        , county
        , zip_code
        , latitude
        , longitude
        , healthcare_expenses
        , healthcare_coverage
        -- snapshot SCD2 columns
        , dbt_scd_id
        , dbt_valid_from
        , dbt_valid_to
    from {{ ref('snp_patients') }}
    {% else %}
    -- fallback to staging if snapshot hasn't been run yet
    select
        patient_id
        , first_name
        , last_name
        , name_prefix
        , name_suffix
        , gender
        , race
        , ethnicity
        , marital_status
        , birth_date
        , death_date
        , address
        , city
        , state
        , county
        , zip_code
        , latitude
        , longitude
        , healthcare_expenses
        , healthcare_coverage
        -- mock SCD2 columns for initial state
        , patient_id as dbt_scd_id
        , birth_date as dbt_valid_from
        , cast(null as timestamp) as dbt_valid_to
    from {{ ref('stg_synthea__patients') }}
    {% endif %}
),

sequenced as (
    select
        -- surrogate key (unique per version, using dbt_scd_id for ordering)
        row_number() over (order by dbt_scd_id) as patient_key

        -- natural key
        , patient_id

        -- name attributes
        , first_name
        , last_name
        , first_name || ' ' || last_name as full_name
        , name_prefix
        , name_suffix

        -- dates
        , birth_date
        , death_date

        -- derived age (current age or age at death)
        , case
            when death_date is not null
            then date_diff('year', birth_date, death_date)
            else date_diff('year', birth_date, current_date)
        end as age_years

        -- derived flags
        , case when death_date is not null then true else false end as is_deceased

        -- demographics
        , gender
        , race
        , ethnicity
        , marital_status

        -- location
        , address
        , city
        , state
        , county
        , zip_code
        , latitude
        , longitude

        -- financial
        , healthcare_expenses
        , healthcare_coverage

        -- scd type 2 columns from snapshot
        , cast(dbt_valid_from as date) as valid_from
        , cast(dbt_valid_to as date) as valid_to
        , case when dbt_valid_to is null then true else false end as is_current

        -- metadata
        , current_timestamp as _loaded_at

    from snapshot_source
),

-- unknown member for handling missing dimension lookups
unknown_member as (
    select
        -1 as patient_key
        , 'UNKNOWN' as patient_id
        , 'Unknown' as first_name
        , 'Patient' as last_name
        , 'Unknown Patient' as full_name
        , cast(null as varchar) as name_prefix
        , cast(null as varchar) as name_suffix
        , cast(null as date) as birth_date
        , cast(null as date) as death_date
        , cast(null as bigint) as age_years
        , false as is_deceased
        , cast(null as varchar) as gender
        , cast(null as varchar) as race
        , cast(null as varchar) as ethnicity
        , cast(null as varchar) as marital_status
        , cast(null as varchar) as address
        , cast(null as varchar) as city
        , cast(null as varchar) as state
        , cast(null as varchar) as county
        , cast(null as varchar) as zip_code
        , cast(null as double) as latitude
        , cast(null as double) as longitude
        , cast(null as double) as healthcare_expenses
        , cast(null as double) as healthcare_coverage
        , cast('1900-01-01' as date) as valid_from
        , cast(null as date) as valid_to
        , true as is_current
        , current_timestamp as _loaded_at
),

final as (
    select * from unknown_member
    union all
    select * from sequenced
)

select * from final
