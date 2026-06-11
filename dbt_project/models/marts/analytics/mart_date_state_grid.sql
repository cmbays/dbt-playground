{{
    config(
        materialized='table',
        tags=['analytics', 'reporting']
    )
}}

{#
    Dense month x state reporting grid.

    Cross joins every calendar month from dim_date with every non-null
    patient state observed in staging. Left-join sparse activity facts
    against this grid so zero-activity month/state cells render as
    explicit zeros instead of silently disappearing from dashboards.

    The explicit CROSS JOIN inside a CTE doubles as the cute-dbt
    cross-join CTE-edge demo (cute-dbt#64).
#}

with months as (
    select distinct
        year_actual
        , month_actual
        , month_name
    from {{ ref('dim_date') }}
),

states as (
    select distinct state
    from {{ ref('stg_synthea__patients') }}
    where state is not null
),

grid as (
    select
        cast(months.year_actual * 100 + months.month_actual as integer) as month_key
        , months.year_actual
        , months.month_actual
        , months.month_name
        , states.state
    from months
    cross join states
)

select * from grid
