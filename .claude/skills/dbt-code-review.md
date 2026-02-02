# dbt Code Review Skill

dbt-specific code review checklist and best practices.

## Overview

This skill provides a comprehensive review checklist for dbt models, ensuring code quality, performance, and adherence to best practices.

## Trigger

Invoke when:

- Reviewing dbt model PRs
- Auditing existing dbt code
- Pre-deployment quality check
- Onboarding new dbt developers

## Review Categories

### 1. Model Structure

| Check | Pass | Fail |
|-------|------|------|
| Uses CTEs, not subqueries | `with cte as (...)` | `select * from (select...)` |
| Final CTE is `final` | `select * from final` | Unclear final output |
| CTE names are descriptive | `with customers as` | `with a as` |
| One model per file | Single select | Multiple creates |
| Model in correct directory | `staging/`, `marts/` | Wrong layer |

### 2. Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Staging | `stg_[source]__[table]` | `stg_stripe__payments` |
| Intermediate | `int_[entity]__[verb]` | `int_orders__pivoted` |
| Fact | `fct_[process]` | `fct_orders` |
| Dimension | `dim_[entity]` | `dim_customers` |
| Column | `snake_case` | `customer_id` |
| Boolean | `is_` or `has_` prefix | `is_active`, `has_subscription` |
| Date | `_date` suffix | `order_date` |
| Timestamp | `_at` suffix | `created_at` |
| ID | `_id` suffix | `customer_id` |

### 3. SQL Best Practices

```sql
-- ✅ GOOD: Explicit column selection
select
    order_id,
    customer_id,
    total_amount
from source

-- ❌ BAD: Select star in production models
select *
from source
```

```sql
-- ✅ GOOD: Consistent formatting
select
    order_id,
    customer_id,
    sum(amount) as total_amount
from orders
group by 1, 2

-- ❌ BAD: Inconsistent formatting
SELECT order_id, customer_id,
SUM(amount) as total_amount FROM orders GROUP BY 1,2
```

```sql
-- ✅ GOOD: Explicit null handling
select
    coalesce(customer_name, 'Unknown') as customer_name,
    nullif(status, '') as status
from customers

-- ❌ BAD: Implicit null behavior
select
    customer_name,  -- Could be null
    status          -- Empty string treated as value
from customers
```

### 4. Dependencies

| Check | Correct | Incorrect |
|-------|---------|-----------|
| Uses ref() | `{{ ref('model') }}` | `schema.model` |
| Uses source() | `{{ source('src', 'tbl') }}` | `raw.table` |
| No circular deps | Linear DAG | A → B → A |
| Correct layer order | stg → int → fct/dim | fct → stg |

### 5. Incremental Models

```sql
-- ✅ GOOD: Proper incremental pattern
{{
  config(
    materialized='incremental',
    unique_key='event_id',
    incremental_strategy='merge'
  )
}}

with source as (
    select * from {{ source('events', 'clicks') }}
    {% if is_incremental() %}
    where event_timestamp > (
        select max(event_timestamp) from {{ this }}
    )
    {% endif %}
)
```

Checklist:

- [ ] `unique_key` is defined
- [ ] `incremental_strategy` is appropriate
- [ ] `is_incremental()` filter is correct
- [ ] Handles late-arriving data
- [ ] Full refresh still works

### 6. Testing

| Requirement | Check |
|-------------|-------|
| Primary key tested | `unique`, `not_null` |
| Foreign keys tested | `relationships` |
| Status fields tested | `accepted_values` |
| Complex rules tested | Singular tests exist |
| Source freshness | Configured where applicable |

### 7. Documentation

| Element | Required |
|---------|----------|
| Model description | Yes |
| Column descriptions | Yes for key columns |
| Grain documented | Yes for facts |
| Primary key documented | Yes |
| Update frequency | Yes for incremental |

### 8. Performance

```sql
-- ✅ GOOD: Filter early
with filtered_source as (
    select *
    from source
    where order_date >= '2024-01-01'
),
joined as (
    select * from filtered_source
    join other_table...
)

-- ❌ BAD: Filter late
with joined as (
    select *
    from source
    join other_table...
)
select *
from joined
where order_date >= '2024-01-01'
```

Checklist:

- [ ] Filters applied early
- [ ] Joins are necessary
- [ ] No cross joins (unless intended)
- [ ] Aggregations are efficient
- [ ] Incremental for large tables

### 9. Security

| Check | Status |
|-------|--------|
| No PII in column names | |
| Sensitive data masked | |
| No hardcoded credentials | |
| Access controls documented | |

## Review Workflow

### Quick Review (< 100 lines)

1. Check naming conventions
2. Verify ref() and source() usage
3. Check for tests
4. Verify documentation exists

### Standard Review

1. All quick review items
2. Review SQL logic
3. Check incremental pattern (if applicable)
4. Verify test coverage
5. Review performance considerations

### Deep Review (Major Changes)

1. All standard review items
2. Trace data lineage
3. Check downstream impact
4. Review with business stakeholders
5. Performance test with production data

## Review Comment Template

```markdown
## dbt Code Review: [Model Name]

### Summary
[Overall assessment]

### Naming & Structure
- [ ] Follows naming conventions
- [ ] CTEs are well-organized
- [ ] Model in correct layer

### SQL Quality
- [ ] No select *
- [ ] Explicit null handling
- [ ] Efficient joins

### Dependencies
- [ ] Uses ref() and source()
- [ ] No circular dependencies
- [ ] Correct layer order

### Testing
- [ ] Primary key tested
- [ ] Foreign keys tested
- [ ] Critical rules covered

### Documentation
- [ ] Model description
- [ ] Column descriptions
- [ ] Grain documented

### Issues Found
1. [Issue description] - [Severity]

### Suggestions
1. [Optional improvement]

### Verdict
- [ ] Approved
- [ ] Approved with suggestions
- [ ] Changes requested
```

## Common Review Findings

| Finding | Severity | Fix |
|---------|----------|-----|
| Missing unique test on PK | 🔴 High | Add test |
| Select * in mart | 🔴 High | List columns |
| No model description | 🟡 Medium | Add description |
| Hardcoded date | 🟡 Medium | Use variable |
| Missing relationship test | 🟡 Medium | Add test |
| CTE named `a`, `b`, `c` | 🟢 Low | Use descriptive names |
| Inconsistent casing | 🟢 Low | Standardize |

## Exit Criteria

- [ ] All high-severity issues resolved
- [ ] Medium-severity issues addressed or accepted
- [ ] Tests pass
- [ ] Documentation complete

## Related Documentation

- [[../agents/code-reviewer.md]] - Code reviewer persona
- [[dbt-testing.md]] - Testing workflow
- [[dbt-model-development.md]] - Development workflow
- [[../rules/coding-style.md]] - General coding standards
