{{
    config(
        materialized='table',
        unique_key='date_key'
    )
}}

{#
    Calendar dimension covering 1909-01-01 to 2025-12-31.

    Note on date_key: Uses YYYYMMDD integer format. Valid range is years 0001-2147483
    (integer max 2,147,483,647). Safe for all practical date ranges.

    Note on day_of_week: dbt_date uses US convention (Sunday=1, Saturday=7),
    NOT ISO 8601 (Monday=1). Weekend and holiday logic accounts for this.
#}

with date_spine as (
    {{ dbt_date.get_date_dimension('1909-01-01', '2025-12-31') }}
),

final as (
    select
        -- surrogate key (YYYYMMDD format, valid for years up to 2147483)
        cast(year_number * 10000 + month_of_year * 100 + day_of_month as integer) as date_key

        -- actual date
        , date_day as date_actual

        -- day attributes (dbt_date convention: Sunday=1, Monday=2, ..., Saturday=7)
        , day_of_week
        , day_of_week_name as day_name
        , day_of_week_name_short as day_name_short
        , day_of_month
        , day_of_year

        -- week attributes
        , week_of_year

        -- month attributes
        , month_of_year as month_actual
        , month_name
        , month_name_short

        -- quarter attributes
        , quarter_of_year as quarter_actual
        , 'Q' || cast(quarter_of_year as varchar) as quarter_name

        -- year attributes
        , year_number as year_actual

        -- flags (Sunday=1, Saturday=7 in dbt_date convention)
        , case when day_of_week in (1, 7) then true else false end as is_weekend

        -- us holidays (basic implementation, not comprehensive)
        -- uses dbt_date convention: Sunday=1, Monday=2, Thursday=5, Saturday=7
        , case
            when month_of_year = 1 and day_of_month = 1 then true  -- new year's day
            when month_of_year = 7 and day_of_month = 4 then true  -- independence day
            when month_of_year = 12 and day_of_month = 25 then true  -- christmas
            when month_of_year = 11 and day_of_week = 5
                and day_of_month between 22 and 28 then true  -- thanksgiving (4th thursday)
            when month_of_year = 1 and day_of_week = 2
                and day_of_month between 15 and 21 then true  -- mlk day (3rd monday)
            when month_of_year = 2 and day_of_week = 2
                and day_of_month between 15 and 21 then true  -- presidents day (3rd monday)
            when month_of_year = 5 and day_of_week = 2
                and day_of_month between 25 and 31 then true  -- memorial day (last monday)
            when month_of_year = 9 and day_of_week = 2
                and day_of_month between 1 and 7 then true  -- labor day (1st monday)
            when month_of_year = 11 and day_of_month = 11 then true  -- veterans day
            else false
        end as is_us_holiday

        , case
            when month_of_year = 1 and day_of_month = 1 then 'New Year''s Day'
            when month_of_year = 7 and day_of_month = 4 then 'Independence Day'
            when month_of_year = 12 and day_of_month = 25 then 'Christmas Day'
            when month_of_year = 11 and day_of_week = 5
                and day_of_month between 22 and 28 then 'Thanksgiving'
            when month_of_year = 1 and day_of_week = 2
                and day_of_month between 15 and 21 then 'Martin Luther King Jr. Day'
            when month_of_year = 2 and day_of_week = 2
                and day_of_month between 15 and 21 then 'Presidents Day'
            when month_of_year = 5 and day_of_week = 2
                and day_of_month between 25 and 31 then 'Memorial Day'
            when month_of_year = 9 and day_of_week = 2
                and day_of_month between 1 and 7 then 'Labor Day'
            when month_of_year = 11 and day_of_month = 11 then 'Veterans Day'
            else null
        end as holiday_name

    from date_spine
)

select * from final
