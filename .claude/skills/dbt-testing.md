# dbt Testing Skill

Comprehensive testing workflow for dbt models including schema tests, singular tests, and source freshness.

## Overview

This skill ensures data quality through systematic testing of all dbt models before production deployment.

## Trigger

Invoke when:

- Adding tests to new models
- Validating data quality rules
- Setting up source freshness monitoring
- Investigating data quality issues
- Pre-deployment validation

## Test Types Reference

| Test Type | Purpose | Location |
|-----------|---------|----------|
| Schema Tests | Column-level validation | `models/*.yml` |
| Singular Tests | Complex business rules | `tests/*.sql` |
| Source Freshness | Data staleness | `sources.yml` |
| Custom Generic | Reusable test logic | `tests/generic/*.sql` |
| Data Tests | Row-level assertions | `tests/data/*.sql` |

## Workflow Steps

### Phase 1: Assess Test Requirements

1. **Identify Critical Columns**
   - Primary keys: `unique`, `not_null`
   - Foreign keys: `relationships`
   - Status fields: `accepted_values`
   - Numeric fields: Range checks

2. **Map Business Rules**
   - What constraints must be true?
   - What edge cases exist?
   - What historical issues occurred?

3. **Create Test Plan**

   ```markdown
   # Test Plan: fct_orders

   ## Schema Tests
   - [ ] order_id: unique, not_null
   - [ ] customer_id: not_null, FK to dim_customers
   - [ ] order_status: accepted_values

   ## Singular Tests
   - [ ] No orphaned line items
   - [ ] Total matches sum of line items
   - [ ] Future dates flagged

   ## Source Freshness
   - [ ] orders source: warn 12h, error 24h
   ```

### Phase 2: Implement Schema Tests

```yaml
# models/marts/orders/_orders__models.yml
version: 2

models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null

      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id

      - name: order_status
        tests:
          - accepted_values:
              values: ['pending', 'completed', 'cancelled', 'refunded']

      - name: order_total
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

### Phase 3: Create Singular Tests

```sql
-- tests/assert_order_totals_match.sql
-- Verify order total equals sum of line items
with order_totals as (
    select
        order_id,
        order_total
    from {{ ref('fct_orders') }}
),

line_item_totals as (
    select
        order_id,
        sum(line_total) as calculated_total
    from {{ ref('fct_order_line_items') }}
    group by 1
)

select
    o.order_id,
    o.order_total,
    l.calculated_total,
    abs(o.order_total - l.calculated_total) as difference
from order_totals o
left join line_item_totals l
    on o.order_id = l.order_id
where abs(o.order_total - coalesce(l.calculated_total, 0)) > 0.01
```

```sql
-- tests/assert_no_future_orders.sql
-- Flag orders with future timestamps
select *
from {{ ref('fct_orders') }}
where order_timestamp > current_timestamp
```

### Phase 4: Configure Source Freshness

```yaml
# models/staging/shopify/_shopify__sources.yml
version: 2

sources:
  - name: shopify
    database: raw
    schema: shopify
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
    loaded_at_field: _fivetran_synced

    tables:
      - name: orders
        description: Shopify orders table
        freshness:
          error_after: {count: 6, period: hour}  # Override

      - name: customers
        freshness: null  # Disable for this table
```

### Phase 5: Create Custom Generic Tests

```sql
-- tests/generic/test_positive.sql
{% test positive(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} < 0

{% endtest %}
```

```sql
-- tests/generic/test_valid_email.sql
{% test valid_email(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} is not null
  and {{ column_name }} not like '%@%.%'

{% endtest %}
```

Usage:

```yaml
columns:
  - name: quantity
    tests:
      - positive

  - name: email
    tests:
      - valid_email
```

### Phase 6: Run and Validate Tests

```bash
# Run all tests
dbt test

# Run tests for specific model
dbt test --select fct_orders

# Run only schema tests
dbt test --select test_type:schema

# Run only singular tests
dbt test --select test_type:singular

# Check source freshness
dbt source freshness

# Run tests with failure details
dbt test --store-failures
```

### Phase 7: Handle Test Failures

1. **Investigate Failure**

   ```bash
   # View failed rows
   dbt test --select fct_orders --store-failures
   # Check audit schema for _dbt_test__audit table
   ```

2. **Determine Severity**

   ```yaml
   columns:
     - name: customer_id
       tests:
         - not_null:
             config:
               severity: error  # Blocks pipeline
         - relationships:
             to: ref('dim_customers')
             field: customer_id
             config:
               severity: warn  # Logs but continues
               warn_if: ">10"
               error_if: ">100"
   ```

3. **Fix or Adjust**
   - Fix data issue at source
   - Adjust test threshold
   - Add where clause to exclude known exceptions

## Test Coverage Checklist

### Staging Models

- [ ] Primary key: unique, not_null
- [ ] Required columns: not_null
- [ ] Types validated (dates, numbers)

### Fact Models

- [ ] Primary key: unique, not_null
- [ ] Foreign keys: relationships
- [ ] Measures: positive where appropriate
- [ ] Dates: not in future

### Dimension Models

- [ ] Primary key: unique, not_null
- [ ] Natural key: unique (for SCD Type 2)
- [ ] Status/category: accepted_values
- [ ] Required attributes: not_null

### Sources

- [ ] Freshness configured
- [ ] Critical tables have error_after
- [ ] Non-critical tables have warn_after

## Artifacts

| Output | Location |
|--------|----------|
| Schema tests | `models/*/[model].yml` |
| Singular tests | `tests/[test_name].sql` |
| Generic tests | `tests/generic/*.sql` |
| Source config | `models/staging/*/_sources.yml` |
| Failed rows | `[target_schema]_dbt_test__audit` |

## Exit Criteria

- [ ] All critical tests pass
- [ ] Warnings reviewed and accepted
- [ ] Source freshness configured
- [ ] Test documentation complete

## Useful dbt Packages

| Package | Tests Provided |
|---------|----------------|
| `dbt_utils` | unique_combination, recency, at_least_one |
| `dbt_expectations` | expect_column_values_to_be_between, etc. |
| `dbt_audit_helper` | compare_queries, compare_relations |

## Related Documentation

- [[../agents/dbt-tester.md]] - Tester persona
- [[dbt-model-development.md]] - Full workflow
- [[dbt-code-review.md]] - Review checklist
- [[dbt-deployment.md]] - Pre-deploy testing
