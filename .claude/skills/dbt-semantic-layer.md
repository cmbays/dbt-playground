# dbt Semantic Layer Skill

Workflow for designing and managing metrics, dimensions, and semantic models.

## Overview

This skill guides the implementation of dbt's Semantic Layer for consistent metric definitions and natural language queries.

## Trigger

Invoke when:

- Defining business metrics
- Creating consistent KPI definitions
- Enabling natural language queries
- Building self-service analytics

## Prerequisites

- dbt version 1.6+ with Semantic Layer support
- MetricFlow integration
- Underlying fact and dimension models

## Workflow Steps

### Phase 1: UNDERSTAND - Define Business Metrics

1. **Gather Requirements**
   - What KPIs does the business track?
   - How are they currently calculated?
   - Who owns the metric definitions?
   - What dimensions are used for analysis?

2. **Document Metric Definitions**

   ```markdown
   # Metric: Revenue

   ## Business Definition
   Total amount of completed orders, excluding refunds and cancellations.

   ## Calculation
   SUM(order_total) WHERE order_status = 'completed'

   ## Dimensions
   - Time: order_date (daily, weekly, monthly)
   - Geography: customer_country, customer_region
   - Product: product_category, product_name
   - Customer: customer_segment

   ## Granularity
   - Lowest: order line item
   - Typical: daily by dimension

   ## Stakeholders
   - Owner: Finance
   - Consumers: Executive, Sales, Marketing
   ```

### Phase 2: MODEL - Create Semantic Model

1. **Define Semantic Model**

   ```yaml
   # models/semantic/orders_semantic.yml
   semantic_models:
     - name: orders
       description: |
         Semantic model for order metrics.
         Based on fct_orders fact table.
       model: ref('fct_orders')

       defaults:
         agg_time_dimension: order_date

       # Entities (join keys)
       entities:
         - name: order
           type: primary
           expr: order_id
         - name: customer
           type: foreign
           expr: customer_id
         - name: product
           type: foreign
           expr: product_id

       # Measures (aggregatable values)
       measures:
         - name: order_total
           description: Sum of order amounts
           agg: sum
           expr: total_amount
           create_metric: true

         - name: order_count
           description: Count of orders
           agg: count
           expr: order_id
           create_metric: true

         - name: unique_customers
           description: Distinct customer count
           agg: count_distinct
           expr: customer_id

       # Dimensions (sliceable attributes)
       dimensions:
         - name: order_date
           type: time
           type_params:
             time_granularity: day
           expr: order_date

         - name: order_status
           type: categorical
           expr: order_status

         - name: customer_segment
           type: categorical
           expr: customer_segment
   ```

### Phase 3: METRICS - Define Derived Metrics

1. **Simple Metrics** (direct from measures)

   ```yaml
   metrics:
     - name: revenue
       description: Total completed order revenue
       type: simple
       type_params:
         measure: order_total
       filter: |
         {{ Dimension('order_status') }} = 'completed'
   ```

2. **Derived Metrics** (calculated from other metrics)

   ```yaml
   metrics:
     - name: average_order_value
       description: Average revenue per order
       type: derived
       type_params:
         expr: revenue / order_count
         metrics:
           - name: revenue
           - name: order_count
   ```

3. **Ratio Metrics**

   ```yaml
   metrics:
     - name: conversion_rate
       description: Orders per unique visitor
       type: ratio
       type_params:
         numerator:
           name: order_count
         denominator:
           name: unique_visitors
   ```

4. **Cumulative Metrics**

   ```yaml
   metrics:
     - name: cumulative_revenue
       description: Running total of revenue
       type: cumulative
       type_params:
         measure: order_total
         window: all_time

     - name: trailing_7d_revenue
       description: Rolling 7-day revenue
       type: cumulative
       type_params:
         measure: order_total
         window: 7
         granularity: day
   ```

### Phase 4: DIMENSIONS - Configure Time and Categorical

1. **Time Dimensions**

   ```yaml
   dimensions:
     - name: order_date
       type: time
       type_params:
         time_granularity: day
       expr: order_date

     - name: order_month
       type: time
       type_params:
         time_granularity: month
       expr: date_trunc('month', order_date)
   ```

2. **Categorical Dimensions**

   ```yaml
   dimensions:
     - name: customer_segment
       type: categorical
       expr: customer_segment

     - name: product_category
       type: categorical
       expr: |
         case
           when product_type in ('electronics', 'computers') then 'Tech'
           when product_type in ('clothing', 'shoes') then 'Apparel'
           else 'Other'
         end
   ```

### Phase 5: QUERY - Test and Validate

1. **Query Metrics via CLI**

   ```bash
   # List available metrics
   mf list metrics

   # Query a metric
   mf query --metrics revenue --dimensions order_date --time-start 2024-01-01

   # Query with filter
   mf query --metrics revenue \
     --dimensions customer_segment \
     --where "{{ Dimension('order_status') }} = 'completed'"
   ```

2. **Natural Language Queries** (if dbt-mcp configured)

   ```
   Query: "What was revenue by month in 2024?"

   Generated SQL:
   SELECT
     date_trunc('month', order_date) as order_month,
     sum(total_amount) as revenue
   FROM fct_orders
   WHERE order_status = 'completed'
     AND order_date >= '2024-01-01'
     AND order_date < '2025-01-01'
   GROUP BY 1
   ORDER BY 1
   ```

3. **Validate Against Known Values**

   ```sql
   -- Compare semantic layer result to direct query
   SELECT
     'semantic' as source,
     {{ mf_query('revenue', dimensions=['order_month']) }}
   UNION ALL
   SELECT
     'direct' as source,
     date_trunc('month', order_date) as order_month,
     sum(total_amount) as revenue
   FROM fct_orders
   WHERE order_status = 'completed'
   GROUP BY 1;
   ```

### Phase 6: DOCUMENT - Create Metric Catalog

```yaml
# models/semantic/metrics.yml
metrics:
  - name: revenue
    description: |
      **Business Definition**: Total revenue from completed orders

      **Calculation**: SUM(total_amount) WHERE status = 'completed'

      **Dimensions**:
      - Time: order_date (day, week, month, quarter, year)
      - Customer: customer_segment, customer_country
      - Product: product_category

      **Use Cases**:
      - Executive reporting
      - Sales performance
      - Financial forecasting

      **Caveats**:
      - Excludes refunds and cancellations
      - Currency is USD
```

## Semantic Layer Patterns

### Revenue Metrics

```yaml
measures:
  - name: gross_revenue
    agg: sum
    expr: subtotal_amount

  - name: discount_amount
    agg: sum
    expr: discount_amount

  - name: refund_amount
    agg: sum
    expr: refund_amount

metrics:
  - name: net_revenue
    type: derived
    type_params:
      expr: gross_revenue - discount_amount - refund_amount
```

### Customer Metrics

```yaml
measures:
  - name: unique_customers
    agg: count_distinct
    expr: customer_id

  - name: new_customers
    agg: count_distinct
    expr: "case when is_first_order then customer_id end"

metrics:
  - name: new_customer_rate
    type: derived
    type_params:
      expr: new_customers / unique_customers
```

### Conversion Funnel

```yaml
measures:
  - name: visitors
    agg: count_distinct
    expr: visitor_id

  - name: add_to_cart
    agg: count_distinct
    expr: "case when added_to_cart then visitor_id end"

  - name: purchasers
    agg: count_distinct
    expr: "case when purchased then visitor_id end"

metrics:
  - name: cart_rate
    type: ratio
    type_params:
      numerator: add_to_cart
      denominator: visitors

  - name: purchase_rate
    type: ratio
    type_params:
      numerator: purchasers
      denominator: add_to_cart
```

## Artifacts

| Output | Location |
|--------|----------|
| Semantic models | `models/semantic/*_semantic.yml` |
| Metric definitions | `models/semantic/metrics.yml` |
| Metric catalog | `docs/metrics/` |

## Exit Criteria

- [ ] Semantic models defined
- [ ] Metrics validated against known values
- [ ] Dimensions properly configured
- [ ] Natural language queries work
- [ ] Documentation complete
- [ ] Stakeholder sign-off

## Related Documentation

- [[../agents/semantic-analyst.md]] - Semantic analyst persona
- [[../agents/data-modeler.md]] - Underlying model design
- [[dbt-model-development.md]] - Fact/dimension development
- [[dbt-testing.md]] - Metric testing
