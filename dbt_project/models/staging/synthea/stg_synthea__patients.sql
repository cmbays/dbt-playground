with source as (
    select * from {{ source('synthea_raw', 'patients') }}
),

renamed as (
    select
        -- primary key
        Id as patient_id

        -- demographics
        , FIRST as first_name
        , LAST as last_name
        , PREFIX as name_prefix
        , SUFFIX as name_suffix
        , MAIDEN as maiden_name
        , GENDER as gender
        , RACE as race
        , ETHNICITY as ethnicity
        , MARITAL as marital_status

        -- dates
        , BIRTHDATE as birth_date
        , DEATHDATE as death_date

        -- identifiers (hashed for privacy)
        , md5(SSN) as ssn_hash
        , DRIVERS as drivers_license
        , PASSPORT as passport_number

        -- location
        , BIRTHPLACE as birth_place
        , ADDRESS as address
        , CITY as city
        , STATE as state
        , COUNTY as county
        , ZIP as zip_code
        , LAT as latitude
        , LON as longitude

        -- financial
        , HEALTHCARE_EXPENSES as healthcare_expenses
        , HEALTHCARE_COVERAGE as healthcare_coverage
    from source
),

final as (
    select
        *
        , current_timestamp as _loaded_at
    from renamed
)

select * from final
