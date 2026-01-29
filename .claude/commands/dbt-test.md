# dbt-test Command

Add or run tests for dbt models.

## Usage

```
/dbt-test [model_name] [test_type]
/dbt-test stg_stripe__payments schema
/dbt-test fct_orders singular
/dbt-test fct_orders run
/dbt-test --all
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `model_name` | Yes | Model to test |
| `test_type` | No | `schema`, `singular`, `run`, or `all` (default: `run`) |

## Examples

### Add Schema Tests

```
/dbt-test stg_stripe__payments schema
```

Opens interactive mode to add tests:

1. **Primary key column?** → payment_id
2. **Add unique test?** → Yes
3. **Add not_null test?** → Yes
4. **Foreign key columns?** → customer_id
5. **FK references?** → dim_customers.customer_id
6. **Categorical columns?** → payment_status
7. **Accepted values?** → pending, completed, failed, refunded

Generates:

```yaml
models:
  - name: stg_stripe__payments
    columns:
      - name: payment_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: payment_status
        tests:
          - accepted_values:
              values: ['pending', 'completed', 'failed', 'refunded']
```

### Create Singular Test

```
/dbt-test fct_orders singular
```

Prompts for:

1. **Test name?** → assert_order_totals_match
2. **Test description?** → Verify order totals match sum of line items
3. **Failing condition?** → (guides through SQL)

Creates:

```sql
-- tests/assert_order_totals_match.sql
-- Verify order totals match sum of line items
with order_totals as (
    select order_id, total_amount
    from {{ ref('fct_orders') }}
),

line_totals as (
    select order_id, sum(line_amount) as calculated
    from {{ ref('fct_order_lines') }}
    group by 1
)

select
    o.order_id,
    o.total_amount,
    l.calculated,
    abs(o.total_amount - l.calculated) as difference
from order_totals o
left join line_totals l on o.order_id = l.order_id
where abs(o.total_amount - coalesce(l.calculated, 0)) > 0.01
```

### Run Tests

```
/dbt-test fct_orders run
```

Executes:

```bash
dbt test --select fct_orders
```

Shows:

```
Running tests for fct_orders...

✓ unique_fct_orders_order_id
✓ not_null_fct_orders_order_id
✓ relationships_fct_orders_customer_id
✓ accepted_values_fct_orders_status

4 tests passed, 0 failed
```

### Run All Tests

```
/dbt-test --all
```

Executes:

```bash
dbt test
```

## Test Types Reference

### Built-in Schema Tests

| Test | Purpose | Example |
|------|---------|---------|
| `unique` | No duplicates | Primary keys |
| `not_null` | No nulls | Required fields |
| `accepted_values` | Value in list | Status fields |
| `relationships` | FK exists | Dimension joins |

### dbt_utils Tests

| Test | Purpose |
|------|---------|
| `unique_combination_of_columns` | Composite primary key |
| `expression_is_true` | Custom expression |
| `recency` | Data freshness |
| `at_least_one` | Column has values |

### Custom Tests

```sql
-- tests/generic/test_positive.sql
{% test positive(model, column_name) %}
select *
from {{ model }}
where {{ column_name }} < 0
{% endtest %}
```

## Workflow

### Adding Tests

1. Identify testable requirements
2. Add schema tests for columns
3. Create singular tests for business rules
4. Run tests to verify
5. Adjust severity levels

### Debugging Failures

```bash
# Run with stored failures
dbt test --select model_name --store-failures

# Check failed rows
select * from [schema]_dbt_test__audit.unique_model_column;
```

## Test Severity

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
```

## Quick Test Patterns

### Primary Key

```yaml
- name: order_id
  tests:
    - unique
    - not_null
```

### Foreign Key

```yaml
- name: customer_id
  tests:
    - relationships:
        to: ref('dim_customers')
        field: customer_id
```

### Status Field

```yaml
- name: status
  tests:
    - accepted_values:
        values: ['active', 'inactive', 'pending']
```

### Numeric Range

```yaml
- name: quantity
  tests:
    - dbt_utils.expression_is_true:
        expression: ">= 0"
```

## Persona Integration

This command activates the **dbt Tester** (`dbt-test:`) persona for comprehensive test design and data quality validation.

## Related

- [[dbt-model.md]] - Create models to test
- [[dbt-run.md]] - Run models before testing
- [[../skills/dbt-testing.md]] - Testing workflow
- [[../agents/dbt-tester.md]] - dbt Tester persona
