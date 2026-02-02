# dbt Model Development Skill

End-to-end workflow for designing, implementing, testing, and documenting dbt models.

## Overview

This skill guides the complete lifecycle of dbt model development from initial design through documentation.

## Trigger

Invoke when:

- Creating new dbt models (staging, intermediate, fact, dimension)
- Adding new data sources to the warehouse
- Building analytics tables for business users
- Implementing incremental models

## Workflow Steps

### Phase 1: DESIGN - Model Architecture

**Persona**: Data Modeler (`dbt-model:`)

1. **Understand Requirements**
   - What business question does this answer?
   - What is the grain of the model?
   - What sources are needed?
   - What downstream uses are expected?

2. **Design Model Structure**

   ```yaml
   # temp/model-design.yml
   model_name: fct_orders
   layer: marts
   grain: one row per order line item
   primary_key: order_line_id
   materialization: incremental

   sources:
     - stg_shopify__orders
     - stg_shopify__line_items
     - dim_customers

   columns:
     - name: order_line_id
       type: string
       tests: [unique, not_null]
     - name: customer_id
       type: string
       tests: [not_null, relationships]
   ```

3. **Define Dependencies**
   - Map upstream models/sources
   - Identify downstream consumers
   - Check for circular dependencies

### Phase 2: IMPLEMENT - Write SQL

**Persona**: dbt Developer (`dbt-dev:`)

1. **Create Staging Model** (if new source)

   ```sql
   -- models/staging/shopify/stg_shopify__orders.sql
   with source as (
       select * from {{ source('shopify', 'orders') }}
   ),

   renamed as (
       select
           id as order_id,
           customer_id,
           total_price as total_amount,
           created_at as order_timestamp
       from source
   )

   select * from renamed
   ```

2. **Implement Core Model**

   ```sql
   -- models/marts/fct_orders.sql
   {{
     config(
       materialized='incremental',
       unique_key='order_line_id'
     )
   }}

   with orders as (
       select * from {{ ref('stg_shopify__orders') }}
   ),

   line_items as (
       select * from {{ ref('stg_shopify__line_items') }}
   ),

   joined as (
       select
           li.line_item_id as order_line_id,
           o.order_id,
           o.customer_id,
           li.product_id,
           li.quantity,
           li.price
       from orders o
       inner join line_items li
           on o.order_id = li.order_id
       {% if is_incremental() %}
       where o.order_timestamp > (
           select max(order_timestamp) from {{ this }}
       )
       {% endif %}
   )

   select * from joined
   ```

3. **Compile and Verify**

   ```bash
   dbt compile --select fct_orders
   dbt run --select fct_orders
   ```

### Phase 3: TEST - Validate Quality

**Persona**: dbt Tester (`dbt-test:`)

1. **Add Schema Tests**

   ```yaml
   # models/marts/fct_orders.yml
   models:
     - name: fct_orders
       description: Order line items fact table
       columns:
         - name: order_line_id
           tests:
             - unique
             - not_null
         - name: customer_id
           tests:
             - not_null
             - relationships:
                 to: ref('dim_customers')
                 field: customer_id
   ```

2. **Create Singular Tests** (for complex rules)

   ```sql
   -- tests/assert_positive_quantities.sql
   select *
   from {{ ref('fct_orders') }}
   where quantity <= 0
   ```

3. **Run Tests**

   ```bash
   dbt test --select fct_orders
   ```

### Phase 4: DOCUMENT - Write Descriptions

**Persona**: dbt Documenter (`dbt-docs:`)

1. **Add Model Description**

   ```yaml
   models:
     - name: fct_orders
       description: |
         **Grain**: One row per order line item
         **Primary Key**: `order_line_id`
         **Update Frequency**: Hourly incremental

         Order line items with customer and product context.

         **Key Joins**:
         - `dim_customers` via `customer_id`
         - `dim_products` via `product_id`
   ```

2. **Add Column Descriptions**

   ```yaml
   columns:
     - name: order_line_id
       description: |
         Unique identifier for the line item.
         Concatenation of order_id and line_number.
   ```

3. **Generate Docs**

   ```bash
   dbt docs generate
   dbt docs serve
   ```

### Phase 5: REVIEW - Quality Check

**Persona**: Code Reviewer (`review:`)

Apply dbt code review checklist:

- [ ] Uses `ref()` and `source()` exclusively
- [ ] CTEs are well-named and logical
- [ ] Follows naming conventions
- [ ] Tests cover primary key
- [ ] Documentation is complete
- [ ] Incremental logic is correct

### Phase 6: DEPLOY - Production Release

**Persona**: Git-Master (`git:`)

1. Create feature branch
2. Commit changes
3. Create PR with dbt CI checks
4. Merge after approval
5. Tag release if significant

## Artifacts

| Output | Location |
|--------|----------|
| Model design | `temp/model-design.yml` |
| SQL model | `models/[layer]/[model].sql` |
| Schema YAML | `models/[layer]/[model].yml` |
| Singular tests | `tests/[test_name].sql` |

## Exit Criteria

- [ ] Model runs without errors
- [ ] All tests pass
- [ ] Documentation is complete
- [ ] Code review approved
- [ ] PR merged

## Integration

- **Entry**: After PRD or ad-hoc request
- **Personas**: Data Modeler → dbt Developer → dbt Tester → dbt Documenter → Code Reviewer
- **Exit**: To production deployment

## Example

```
User: Create a model for customer lifetime value

dbt-model: Design CLV model with grain per customer
→ Output: Model design with measures and dimensions

dbt-dev: Implement dim_customer_ltv model
→ Output: SQL model with aggregations

dbt-test: Add tests for CLV calculations
→ Output: Schema tests and validation queries

dbt-docs: Document model and columns
→ Output: Complete YAML documentation

review: Check dbt best practices
→ Output: Approval or change requests
```

## Related Documentation

- [[../agents/data-modeler.md]] - Model design
- [[../agents/dbt-developer.md]] - Implementation
- [[../agents/dbt-tester.md]] - Testing
- [[../agents/dbt-documenter.md]] - Documentation
- [[dbt-testing.md]] - Testing workflow
- [[dbt-deployment.md]] - Deployment workflow
