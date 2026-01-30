with source as (
    select * from {{ source('synthea_raw', 'payers') }}
),

renamed as (
    select
        -- primary key
        Id as payer_id

        -- attributes
        , NAME as payer_name
        , ADDRESS as address
        , CITY as city
        , STATE_HEADQUARTERED as state
        , ZIP as zip_code
        , PHONE as phone

        -- financial metrics
        , AMOUNT_COVERED as amount_covered
        , AMOUNT_UNCOVERED as amount_uncovered
        , REVENUE as revenue

        -- utilization metrics
        , COVERED_ENCOUNTERS as covered_encounters
        , UNCOVERED_ENCOUNTERS as uncovered_encounters
        , COVERED_MEDICATIONS as covered_medications
        , UNCOVERED_MEDICATIONS as uncovered_medications
        , COVERED_PROCEDURES as covered_procedures
        , UNCOVERED_PROCEDURES as uncovered_procedures
        , COVERED_IMMUNIZATIONS as covered_immunizations
        , UNCOVERED_IMMUNIZATIONS as uncovered_immunizations

        -- member metrics
        , UNIQUE_CUSTOMERS as unique_customers
        , QOLS_AVG as average_quality_of_life_score
        , MEMBER_MONTHS as member_months
    from source
),

final as (
    select
        *
        , current_timestamp as _loaded_at
    from renamed
)

select * from final
