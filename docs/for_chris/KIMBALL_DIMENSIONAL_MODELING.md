# Kimball Dimensional Modeling: Advanced Topics

**Purpose**: Deep dive into dimensional modeling best practices for dbt projects, covering common pitfalls and advanced patterns.

**Last Updated**: 2026-01-28

---

## Table of Contents

1. [Medallion Architecture and Layer Direction](#medallion-architecture-and-layer-direction)
2. [Gold Layer Helper Models](#gold-layer-helper-models)
3. [Fact Table Types](#fact-table-types)
4. [Dimension Table Types](#dimension-table-types)
5. [Slowly Changing Dimensions (SCD)](#slowly-changing-dimensions-scd)
6. [Bridge Tables](#bridge-tables)
7. [Fan Traps](#fan-traps)
8. [Incremental Models](#incremental-models)
9. [Common Anti-Patterns](#common-anti-patterns)

---

## Medallion Architecture and Layer Direction

The medallion architecture organizes data into three layers, each with increasing quality and business value.

```text
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   BRONZE    │───▶│   SILVER    │───▶│    GOLD     │
│   (stg_)    │    │   (int_)    │    │ (fct_/dim_) │
└─────────────┘    └─────────────┘    └─────────────┘
     Raw              Cleaned           Business
   1:1 source        Transformed        Ready
```

### Layer Purposes

| Layer | Prefix | Purpose | Allowed Operations |
|-------|--------|---------|-------------------|
| **Bronze** | `stg_` | Raw data, 1:1 with source | Rename, cast types, filter deletes |
| **Silver** | `int_` | Cleaned, joined, enriched | Business logic, joins, aggregations |
| **Gold** | `fct_`, `dim_` | Business-ready analytics | Final transformations, conformed dims |

### The Cardinal Rule: Never Go Backwards

**Data flows in ONE direction**: Bronze → Silver → Gold

```sql
-- WRONG: Gold model references silver, then gold references that int_
-- Creates backwards dependency risk

fct_orders.sql:
  select * from {{ ref('int_order_enriched') }}  -- OK

int_order_enriched.sql:
  select * from {{ ref('dim_customers') }}  -- WRONG! Gold → Silver

-- RIGHT: Silver references silver or bronze only
int_order_enriched.sql:
  select * from {{ ref('stg_orders') }}
  join {{ ref('stg_customers') }}  -- OK: Bronze sources
```

**Why This Matters**:

1. **Circular Dependencies**: Backwards references can create DAG cycles
2. **Build Order**: dbt may try to build gold before silver
3. **Testing Isolation**: Each layer should be independently testable
4. **Semantic Clarity**: Analysts know gold = production-ready

---

## Gold Layer Helper Models

When gold layer models need shared logic, create **gold layer helpers** instead of adding intermediate models.

### The Problem

```text
Scenario: fct_orders and fct_returns both need exchange rate conversion

WRONG approach:
fct_orders ──┐
             ├──▶ int_exchange_rates ──▶ stg_rates
fct_returns ─┘

Problem: int_ is silver layer, but it's serving gold layer models
This blurs the layer boundaries and creates confusion
```

### The Solution: Gold Layer Helpers

```text
RIGHT approach:
fct_orders ──┐
             ├──▶ _gold__exchange_rates ──▶ stg_rates
fct_returns ─┘

The helper lives IN the gold layer, prefixed with underscore
```

### Naming Conventions

| Pattern | Scope | Example |
|---------|-------|---------|
| `_fct_[model]__[purpose]` | Private to one fact | `_fct_orders__line_calcs` |
| `_dim_[model]__[purpose]` | Private to one dim | `_dim_customers__scd_logic` |
| `_gold__[purpose]` | Shared across gold | `_gold__exchange_rates` |

### Directory Structure

```text
models/
├── staging/              # Bronze (stg_)
│   └── stripe/
│       └── stg_stripe__payments.sql
│
├── intermediate/         # Silver (int_)
│   └── int_orders__enriched.sql
│
└── marts/                # Gold (fct_, dim_, and helpers)
    ├── core/
    │   ├── fct_orders.sql
    │   ├── dim_customers.sql
    │   └── _helpers/
    │       ├── _fct_orders__line_totals.sql
    │       ├── _gold__exchange_rates.sql
    │       └── _gold__date_spine.sql
    │
    └── finance/
        └── mart_monthly_revenue.sql
```

### Best Practices

1. **Underscore Prefix**: Signals "internal use only"
2. **Document Consumers**: Comment which models use this helper
3. **Don't Expose**: Downstream BI tools reference fct_/dim_, never helpers
4. **Materialize Appropriately**: Often `table` for performance

```sql
-- _gold__exchange_rates.sql
-- PURPOSE: Daily exchange rates for multi-currency revenue conversion
-- CONSUMERS: fct_orders, fct_invoices, fct_refunds
-- WARNING: Do NOT reference from int_ layer (silver) - gold only

{{ config(materialized='table') }}

with rates as (
    select
        rate_date,
        from_currency,
        to_currency,
        exchange_rate
    from {{ ref('stg_forex__daily_rates') }}
)

select * from rates
```

---

## Fact Table Types

Fact tables record business events and contain measures (numeric values for aggregation).

### Transaction Facts

**Grain**: One row per atomic business event

```sql
-- fct_orders: One row per order
-- Grain: order_id

select
    order_id,           -- Degenerate dimension
    customer_id,        -- FK to dim_customers
    product_id,         -- FK to dim_products
    order_date_id,      -- FK to dim_date
    quantity,           -- Measure
    unit_price,         -- Measure
    discount_amount,    -- Measure
    total_amount        -- Measure
from ...
```

**Characteristics**:

- Most common fact type
- Additive measures (can sum across all dimensions)
- Sparse (only rows where events occurred)

### Periodic Snapshot Facts

**Grain**: One row per entity per time period

```sql
-- fct_inventory_daily: One row per product per day
-- Grain: product_id + snapshot_date

select
    product_id,
    snapshot_date,
    quantity_on_hand,      -- Semi-additive (sum across products, not dates)
    quantity_reserved,
    reorder_point
from ...
```

**Characteristics**:

- Regular intervals (daily, weekly, monthly)
- Semi-additive measures (can't sum across time)
- Dense (row for every period, even if no change)

### Accumulating Snapshot Facts

**Grain**: One row per lifecycle instance with milestone dates

```sql
-- fct_order_fulfillment: One row per order, updated as it progresses
-- Grain: order_id

select
    order_id,
    order_date,            -- Milestone 1
    payment_date,          -- Milestone 2 (null until paid)
    ship_date,             -- Milestone 3 (null until shipped)
    delivery_date,         -- Milestone 4 (null until delivered)
    days_to_ship,          -- Lag measure
    days_to_deliver        -- Lag measure
from ...
```

**Characteristics**:

- Tracks entity through workflow/lifecycle
- Multiple date columns (milestones)
- Row is updated (not inserted) as milestones occur
- Good for: order fulfillment, loan processing, claims

### Factless Facts

**Grain**: Records events without measures

```sql
-- fct_student_attendance: Who attended which class
-- Grain: student_id + class_id + attendance_date

select
    student_id,
    class_id,
    attendance_date,
    -- No measures! The row existing IS the fact
from ...
```

**Use Cases**:

- Coverage/eligibility (who could buy what)
- Attendance/participation
- Events without numeric values

---

## Dimension Table Types

Dimensions provide context for facts—the "who, what, where, when, why, how."

### Conformed Dimensions

Shared across multiple fact tables for consistent reporting.

```sql
-- dim_customers: Used by fct_orders, fct_returns, fct_support_tickets
-- All facts reference the SAME customer dimension

select
    customer_id,
    customer_name,
    customer_email,
    customer_segment,
    acquisition_channel
from ...
```

**Critical**: Same customer_id must mean the same customer across all facts.

### Role-Playing Dimensions

Same dimension used multiple times in one fact with different meanings.

```sql
-- fct_orders references dim_date THREE ways:
select
    order_id,
    order_date_id,      -- FK to dim_date (when ordered)
    ship_date_id,       -- FK to dim_date (when shipped)
    delivery_date_id    -- FK to dim_date (when delivered)
from ...

-- In BI tool, create three "role" aliases:
-- - Order Date (dim_date as order_date)
-- - Ship Date (dim_date as ship_date)
-- - Delivery Date (dim_date as delivery_date)
```

### Degenerate Dimensions

Dimension attributes stored directly in the fact table (no separate dim table).

```sql
-- fct_order_lines
select
    order_line_id,
    order_id,            -- Degenerate! No dim_orders table
    invoice_number,      -- Degenerate! Just a label
    product_id,          -- FK to dim_products
    quantity,
    amount
from ...
```

**When to Use**:

- Operational codes/numbers with no other attributes
- Would create a useless 1-column dimension
- Example: order number, invoice number, transaction ID

### Junk Dimensions

Combine low-cardinality flags into one dimension to reduce fact table width.

```sql
-- dim_order_flags: Combines boolean flags
-- Instead of 5 flag columns in fct_orders, one FK to this

select
    order_flag_id,       -- Surrogate key
    is_gift,             -- Y/N
    is_rush,             -- Y/N
    is_taxable,          -- Y/N
    is_discounted,       -- Y/N
    requires_signature   -- Y/N
from ...

-- Fact table:
select
    order_id,
    order_flag_id,       -- One FK instead of 5 columns
    ...
from ...
```

**Benefits**:

- Reduces fact table width
- Makes fact table scans faster
- Groups related flags together

### Outrigger Dimensions

A dimension that hangs off another dimension (dimension of a dimension).

```sql
-- dim_customers → dim_geography (outrigger)

-- dim_customers
select
    customer_id,
    customer_name,
    geography_id         -- FK to outrigger
from ...

-- dim_geography (outrigger)
select
    geography_id,
    city,
    state,
    country,
    region
from ...
```

**When to Use**:

- Shared geographic hierarchy
- Reduces redundancy in large dimensions
- Common: geography, organization hierarchy

---

## Slowly Changing Dimensions (SCD)

How to handle dimension attributes that change over time.

### Type 0: Fixed/Immutable

**Behavior**: Never changes

```sql
-- dim_date: Date attributes are fixed
select
    date_id,
    calendar_date,
    day_of_week,      -- Monday is always Monday
    month_name,
    quarter,
    year
from ...
```

### Type 1: Overwrite

**Behavior**: Replace old value with new, no history

```sql
-- Before: customer_email = 'old@email.com'
-- After:  customer_email = 'new@email.com'

-- History is lost
-- Use for: Corrections, unimportant changes
```

### Type 2: Add New Row (Full History)

**Behavior**: Insert new row, mark old row as expired

```sql
-- dim_customers with SCD Type 2

| customer_sk | customer_id | customer_segment | valid_from | valid_to   | is_current |
|-------------|-------------|------------------|------------|------------|------------|
| 1001        | C-123       | Standard         | 2023-01-01 | 2024-06-30 | false      |
| 1002        | C-123       | Premium          | 2024-07-01 | 9999-12-31 | true       |

-- customer_sk: Surrogate key (PK for joins)
-- customer_id: Natural key (business identifier)
-- valid_from/to: Effective date range
-- is_current: Convenience flag
```

**Implementation**:

```sql
-- Joining to SCD Type 2 for point-in-time accuracy
select
    f.order_id,
    d.customer_segment   -- Segment at time of order
from fct_orders f
join dim_customers d
    on f.customer_id = d.customer_id
    and f.order_date between d.valid_from and d.valid_to
```

### Type 3: Add Column (Previous Value)

**Behavior**: Store current and previous value only

```sql
| customer_id | current_segment | previous_segment |
|-------------|-----------------|------------------|
| C-123       | Premium         | Standard         |
```

**Use for**: When you only need "before and after"

### Type 6: Hybrid (1+2+3)

**Behavior**: Combines Type 1, 2, and 3

```sql
| customer_sk | customer_id | current_segment | historical_segment | valid_from | valid_to   | is_current |
|-------------|-------------|-----------------|-------------------|------------|------------|------------|
| 1001        | C-123       | Premium         | Standard          | 2023-01-01 | 2024-06-30 | false      |
| 1002        | C-123       | Premium         | Premium           | 2024-07-01 | 9999-12-31 | true       |

-- current_segment: Type 1 (always current value, even in old rows)
-- historical_segment: What segment was at that point in time
-- valid_from/to, is_current: Type 2 structure
```

---

## Bridge Tables

Bridge tables resolve many-to-many (M:M) relationships in dimensional models.

### Types of Bridge Tables

| Type | Connects | Example |
|------|----------|---------|
| **Dimension-to-Dimension** | Two dimensions | `brg_customer_account` (Customer ↔ Account) |
| **Fact-to-Dimension** | Fact to multi-valued dim | `brg_order_promotion` (Order ↔ Promotions) |
| **Hierarchy Bridge** | Ragged hierarchy | `brg_org_hierarchy` (Employee ↔ Manager chain) |

**Key Insight**: The fact table usually joins to ONE side of the bridge (the "transaction owner"), then the bridge fans out to the other dimension.

### The Problem

```text
Scenario: One customer can have multiple accounts
          One account can have multiple customers
          This is M:M - can't model with simple FK

Customer: Alice ──┬──▶ Account: Joint Savings
                  │
Customer: Bob ────┘

If fct_orders has customer_id, and you want account_id,
you can't add account_id directly (which one?)
```

### Visualizing the Fan-Out

```text
Before Bridge Join (3 fact rows):
┌─────────────┬─────────────┬─────────┐
│ order_id    │ customer_id │ revenue │
├─────────────┼─────────────┼─────────┤
│ 1           │ Alice       │ $100    │
│ 2           │ Bob         │ $50     │
│ 3           │ Alice       │ $75     │
└─────────────┴─────────────┴─────────┘

Bridge Table:
┌─────────────┬────────────┬────────┐
│ customer_id │ account_id │ weight │
├─────────────┼────────────┼────────┤
│ Alice       │ Joint      │ 0.5    │
│ Alice       │ Individual │ 0.5    │  ← Alice has 2 accounts!
│ Bob         │ Joint      │ 1.0    │
└─────────────┴────────────┴────────┘

After Bridge Join (5 rows - FANNED OUT!):
┌─────────────┬─────────────┬─────────┬────────────┬────────┐
│ order_id    │ customer_id │ revenue │ account_id │ weight │
├─────────────┼─────────────┼─────────┼────────────┼────────┤
│ 1           │ Alice       │ $100    │ Joint      │ 0.5    │
│ 1           │ Alice       │ $100    │ Individual │ 0.5    │  ← DUPLICATED!
│ 2           │ Bob         │ $50     │ Joint      │ 1.0    │
│ 3           │ Alice       │ $75     │ Joint      │ 0.5    │
│ 3           │ Alice       │ $75     │ Individual │ 0.5    │  ← DUPLICATED!
└─────────────┴─────────────┴─────────┴────────────┴────────┘

SUM(revenue) = $100 + $100 + $50 + $75 + $75 = $400  ← WRONG! Should be $225
```

### The Solution: Bridge Table

```sql
-- brg_customer_account
-- TYPE: Dimension-to-Dimension Bridge
-- Grain: One row per customer-account assignment

| customer_id | account_id | assignment_weight | is_primary |
|-------------|------------|-------------------|------------|
| Alice       | Joint      | 0.5               | true       |
| Bob         | Joint      | 0.5               | false      |
| Alice       | Individual | 1.0               | false      |
```

### The Double-Counting Trap

Joining through a bridge creates duplicate rows in your fact.

```sql
-- WRONG: This inflates revenue!
select
    a.account_name,
    sum(o.revenue) as total_revenue   -- DOUBLED for joint accounts!
from fct_orders o
join brg_customer_account ca on o.customer_id = ca.customer_id
join dim_accounts a on ca.account_id = a.account_id
group by 1

-- If Alice made a $100 order, it shows as $100 for EACH account she's in
```

### Solutions to Double-Counting

**Option 1: Use Weighting Factor**

```sql
select
    a.account_name,
    sum(o.revenue * ca.assignment_weight) as weighted_revenue  -- Name clearly!
from fct_orders o
join brg_customer_account ca on o.customer_id = ca.customer_id
join dim_accounts a on ca.account_id = a.account_id
group by 1

-- Alice's $100 order → $50 to Joint, $50 to Individual
```

> **End-User Warning**: Weighted allocation works perfectly for **totals**, but can confuse
> end-users viewing **individual line items**. A $100 order showing as $50.00 in a
> detail report looks like a data error. Consider:
>
> - Showing both `gross_revenue` AND `weighted_revenue` columns
> - Adding a tooltip/footnote explaining the allocation
> - Only using weighting in aggregate reports, not detail views

**Option 2: Filter to Primary**

```sql
select
    a.account_name,
    sum(o.revenue) as total_revenue
from fct_orders o
join brg_customer_account ca
    on o.customer_id = ca.customer_id
    and ca.is_primary = true          -- Only primary assignment
join dim_accounts a on ca.account_id = a.account_id
group by 1
```

**Option 3: Aggregate Before Joining**

```sql
with customer_revenue as (
    select customer_id, sum(revenue) as revenue
    from fct_orders
    group by 1
)
select
    a.account_name,
    sum(cr.revenue * ca.assignment_weight) as weighted_revenue
from customer_revenue cr
join brg_customer_account ca on cr.customer_id = ca.customer_id
join dim_accounts a on ca.account_id = a.account_id
group by 1
```

**Option 4: LEFT JOIN to Handle Missing Bridge Entries**

```sql
-- IMPORTANT: If bridge isn't exhaustive, INNER JOIN drops revenue!
select
    coalesce(a.account_name, 'Unassigned') as account_name,
    sum(o.revenue * coalesce(ca.assignment_weight, 1.0)) as weighted_revenue
from fct_orders o
left join brg_customer_account ca on o.customer_id = ca.customer_id
left join dim_accounts a on ca.account_id = a.account_id
group by 1

-- Customers not in bridge → 'Unassigned' with full revenue (weight 1.0)
```

> **Null Handling Warning**: If a `customer_id` exists in `fct_orders` but has no entry
> in `brg_customer_account`, an INNER JOIN silently **drops that revenue entirely**.
> Always verify bridge completeness or use LEFT JOIN with null handling.

### Bridge Table Best Practices

1. **Always include a weight column** (even if all 1.0 initially)
2. **Include is_primary flag** for filtering to single assignment
3. **Comment all bridge joins** to warn about double-counting
4. **Validate weights sum to 1.0** per entity (per customer, all account weights = 1.0)
5. **Test cardinality** in dbt tests
6. **Name weighted columns clearly** (`weighted_revenue` not `revenue`)
7. **Use LEFT JOIN** if bridge isn't guaranteed to be exhaustive
8. **Add referential integrity tests** to prevent orphan assignments

```sql
-- ALWAYS comment bridge table usage
-- BRIDGE JOIN: brg_customer_account (Dim-to-Dim, M:M)
-- Using weighted allocation to avoid double-counting
-- NOTE: LEFT JOIN used because bridge may not cover all customers
left join brg_customer_account ca on o.customer_id = ca.customer_id
```

### Bridge Table dbt Tests

```yaml
# models/marts/brg_customer_account.yml
models:
  - name: brg_customer_account
    description: |
      **Type**: Dimension-to-Dimension Bridge
      **Grain**: One row per customer-account assignment
      **Warning**: Join through this bridge causes fan-out. Use weights!

    tests:
      # Weights must sum to 1.0 per customer
      - dbt_utils.expression_is_true:
          expression: "abs(weight_sum - 1.0) < 0.001"
          config:
            where: "1=1"  # Applied to grouped result
          # Custom SQL needed for this check

    columns:
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
              # Prevents orphan assignments!

      - name: account_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_accounts')
              field: account_id

      - name: assignment_weight
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0 and <= 1"
```

```sql
-- tests/assert_bridge_weights_sum_to_one.sql
-- Singular test: weights per customer must sum to 1.0

with weight_sums as (
    select
        customer_id,
        sum(assignment_weight) as total_weight
    from {{ ref('brg_customer_account') }}
    group by 1
)

select *
from weight_sums
where abs(total_weight - 1.0) > 0.001  -- Allow small float tolerance
```

---

## Fan Traps

Fan traps occur when joins create unintended row multiplication.

### Fan-Out Trap

**Problem**: 1:M join inflates measures

```text
Orders (3 rows) ──JOIN──▶ Order_Lines (10 rows)

If you SUM(order_total) after the join, you count each order
as many times as it has line items!
```

**Solution**: Aggregate before joining, or don't join at all

```sql
-- WRONG
select sum(o.order_total)
from orders o
join order_lines ol on o.order_id = ol.order_id
-- order_total counted once per line item!

-- RIGHT Option 1: Aggregate first
with order_totals as (
    select order_id, order_total from orders
)
select sum(order_total) from order_totals

-- RIGHT Option 2: Use DISTINCT or window functions carefully
```

### Chasm Trap

**Problem**: Two 1:M relationships from same parent create Cartesian product

```text
                    ┌──▶ Order_Lines (5 rows)
Orders (1 row) ────┤
                    └──▶ Shipments (3 rows)

Joining both: 1 × 5 × 3 = 15 rows!
```

**Solution**: Aggregate each relationship separately

```sql
-- WRONG: Chasm trap!
select
    o.order_id,
    sum(ol.line_total) as line_total,    -- Inflated 3x
    sum(s.ship_cost) as ship_cost         -- Inflated 5x
from orders o
join order_lines ol on o.order_id = ol.order_id
join shipments s on o.order_id = s.order_id
group by 1

-- RIGHT: Aggregate separately, then join
with line_totals as (
    select order_id, sum(line_total) as line_total
    from order_lines
    group by 1
),
ship_totals as (
    select order_id, sum(ship_cost) as ship_cost
    from shipments
    group by 1
)
select
    o.order_id,
    lt.line_total,
    st.ship_cost
from orders o
left join line_totals lt on o.order_id = lt.order_id
left join ship_totals st on o.order_id = st.order_id
```

---

## Incremental Models

Incremental models process only new/changed data instead of full table rebuilds.

### Basic Pattern

```sql
{{
  config(
    materialized='incremental',
    unique_key='event_id',
    incremental_strategy='merge'
  )
}}

with source as (
    select * from {{ source('events', 'page_views') }}
    {% if is_incremental() %}
    where event_timestamp > (select max(event_timestamp) from {{ this }})
    {% endif %}
)

select * from source
```

### Common Pitfalls

#### Pitfall 1: Window Functions Need Historical Context

Window functions like LAG, LEAD, running totals reference rows outside the incremental batch.

```sql
-- PROBLEM: LAG looks at previous row, but previous row isn't in batch!
select
    event_id,
    event_timestamp,
    lag(event_timestamp) over (
        partition by user_id
        order by event_timestamp
    ) as prev_event_timestamp
    -- prev_event_timestamp is NULL for first row in batch!
from source
{% if is_incremental() %}
where event_timestamp > (select max(event_timestamp) from {{ this }})
{% endif %}
```

**Solutions**:

```sql
-- Solution 1: Lookback buffer
{% if is_incremental() %}
where event_timestamp >= dateadd(day, -7,
    (select max(event_timestamp) from {{ this }})
)
{% endif %}
-- Then filter out old rows in final select

-- Solution 2: Compute window in non-incremental model
-- Use an int_ model for the window function (full refresh)
-- Incremental model just filters the result

-- Solution 3: Use this model as full_refresh only
{{ config(materialized='table') }}  -- Not incremental
```

#### Pitfall 2: Late-Arriving Data

Data arrives after its timestamp's batch has already run.

```sql
-- Order placed Jan 1, but data arrives Jan 3
-- Jan 2 batch already ran with max(order_date) = Jan 2
-- Jan 1 order is now "late" and won't be picked up!

-- Solution: Use a lookback buffer
{% if is_incremental() %}
where order_date >= dateadd(day, -3, current_date)
  and order_date > (select max(order_date) from {{ this }})
{% endif %}
```

#### Pitfall 3: Updates to Existing Rows

Source row is updated, but update_timestamp wasn't tracked.

```sql
-- Original: order_id=1, status='pending', loaded Jan 1
-- Updated:  order_id=1, status='shipped', loaded Jan 3
-- But order_date is still Jan 1, so it won't be picked up!

-- Solution: Track updated_at separately from business dates
{% if is_incremental() %}
where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
-- AND use merge strategy with unique_key
```

#### Pitfall 4: Deletes Not Handled

Source deletes rows, but incremental model doesn't know.

```sql
-- Options for handling deletes:

-- 1. Soft deletes: Source adds is_deleted flag
{% if is_incremental() %}
where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
-- Merge will update is_deleted=true

-- 2. Full refresh on schedule
-- Run --full-refresh weekly/monthly

-- 3. Compare and delete (advanced)
-- Requires custom macro to identify missing rows
```

### Incremental Strategy Comparison

| Strategy | Use Case | Pros | Cons |
|----------|----------|------|------|
| `append` | Immutable events | Fastest | No updates |
| `merge` | Updates + inserts | Handles updates | Slower, needs unique_key |
| `delete+insert` | Partition replacement | Good for late data | Must define partition |
| `insert_overwrite` | Full partition refresh | Clean partitions | Databricks/Spark only |

---

## Common Anti-Patterns

### 1. Wide Fact Tables

**Anti-pattern**: Denormalizing dimension attributes into facts

```sql
-- BAD: customer_name in fact table
select
    order_id,
    customer_id,
    customer_name,      -- Should be in dim_customers!
    customer_email,     -- Should be in dim_customers!
    order_total
from ...
```

**Why it's bad**: Customer name changes require updating all historical orders.

### 2. Missing Grain Definition

**Anti-pattern**: Undocumented grain leads to duplicate confusion

```sql
-- Is this one row per order, or one row per line item?
-- Nobody knows!
select * from fct_orders
```

**Fix**: Always document grain in model description:

```yaml
models:
  - name: fct_orders
    description: |
      **Grain**: One row per order line item
      **Primary Key**: order_line_id
```

### 3. Business Logic in Staging

**Anti-pattern**: Transformations in stg_ models

```sql
-- stg_orders.sql
-- BAD: Business logic in staging
select
    id as order_id,
    case when status = 1 then 'pending'
         when status = 2 then 'complete'
    end as order_status,           -- Business logic!
    amount * 1.1 as amount_with_tax -- Business logic!
from source
```

**Fix**: Staging is only for rename/cast. Move logic to int_or fct_.

### 4. Circular Dependencies

**Anti-pattern**: A → B → A

```sql
-- model_a.sql
select * from {{ ref('model_b') }}

-- model_b.sql
select * from {{ ref('model_a') }}  -- CIRCULAR!
```

**Fix**: Extract shared logic to a third model.

### 5. Non-Conformed Dimensions

**Anti-pattern**: Same entity modeled differently across facts

```sql
-- fct_orders uses customer_segment from source A
-- fct_returns uses customer_tier from source B
-- Same customer, different segment values!
```

**Fix**: Create one dim_customers, resolve conflicts there.

---

## Quick Reference Checklist

### Model Design

- [ ] Grain is documented (one row per ___)
- [ ] Primary key is defined and tested
- [ ] Layer direction is correct (Bronze → Silver → Gold)
- [ ] No backwards references (Gold → Silver)
- [ ] Helper models use underscore prefix

### Fact Tables

- [ ] Contains FKs and measures only
- [ ] Degenerate dimensions documented
- [ ] Appropriate fact type chosen (transaction/snapshot/accumulating)

### Dimension Tables

- [ ] SCD type chosen and documented
- [ ] Surrogate key for Type 2 SCDs
- [ ] Conformed across related facts
- [ ] Role-playing usage documented

### Bridge Tables

- [ ] Weight column included
- [ ] Primary flag included
- [ ] All joins are commented
- [ ] Tests validate weight sums

### Incremental Models

- [ ] unique_key defined
- [ ] Late-arriving data handled
- [ ] Window functions have lookback buffer
- [ ] Delete strategy documented

---

## Further Reading

- **The Data Warehouse Toolkit** by Ralph Kimball — The definitive guide
- **dbt Best Practices** — docs.getdbt.com/guides/best-practices
- **Dimensional Modeling Techniques** — kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/

---

*This document is part of the dbt-playground learning materials. See also: `.claude/agents/data-modeler.md` and `.claude/agents/dbt-developer.md`.*
