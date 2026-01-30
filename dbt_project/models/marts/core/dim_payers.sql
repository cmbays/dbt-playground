{{
    config(
        materialized='table',
        unique_key='payer_key'
    )
}}

with source as (
    select * from {{ ref('stg_synthea__payers') }}
),

sequenced as (
    select
        -- surrogate key (starting from 1, reserving -1 for unknown)
        row_number() over (order by payer_id) as payer_key

        -- natural key
        , payer_id

        -- attributes
        , payer_name
        , address
        , city
        , state
        , zip_code
        , phone

        -- financial metrics
        , amount_covered
        , amount_uncovered
        , revenue

        -- utilization metrics
        , covered_encounters
        , uncovered_encounters
        , covered_medications
        , uncovered_medications
        , covered_procedures
        , uncovered_procedures
        , covered_immunizations
        , uncovered_immunizations

        -- member metrics
        , unique_customers
        , average_quality_of_life_score
        , member_months

        -- derived metrics
        , case
            when (amount_covered + amount_uncovered) > 0
            then amount_covered / (amount_covered + amount_uncovered)
            else 0
        end as coverage_rate

        -- metadata
        , current_timestamp as _loaded_at

    from source
),

-- unknown member for handling missing dimension lookups
unknown_member as (
    select
        -1 as payer_key
        , 'UNKNOWN' as payer_id
        , 'Unknown Payer' as payer_name
        , cast(null as varchar) as address
        , cast(null as varchar) as city
        , cast(null as varchar) as state
        , cast(null as varchar) as zip_code
        , cast(null as varchar) as phone
        , cast(null as double) as amount_covered
        , cast(null as double) as amount_uncovered
        , cast(null as double) as revenue
        , cast(null as bigint) as covered_encounters
        , cast(null as bigint) as uncovered_encounters
        , cast(null as bigint) as covered_medications
        , cast(null as bigint) as uncovered_medications
        , cast(null as bigint) as covered_procedures
        , cast(null as bigint) as uncovered_procedures
        , cast(null as bigint) as covered_immunizations
        , cast(null as bigint) as uncovered_immunizations
        , cast(null as bigint) as unique_customers
        , cast(null as double) as average_quality_of_life_score
        , cast(null as bigint) as member_months
        , cast(null as double) as coverage_rate
        , current_timestamp as _loaded_at
),

final as (
    select * from unknown_member
    union all
    select * from sequenced
)

select * from final
