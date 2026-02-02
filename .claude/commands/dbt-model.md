# dbt-model Command

Create a new dbt model with proper structure, naming, and documentation.

## Usage

```
/dbt-model [layer] [model_name] [source_reference]
/dbt-model staging orders raw.shopify.orders
/dbt-model intermediate orders_joined
/dbt-model fact orders
/dbt-model dimension customers
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `layer` | Yes | Model layer: `staging`, `intermediate`, `fact`, `dimension` |
| `model_name` | Yes | Base name for the model |
| `source_reference` | For staging | Source table reference |

## Examples

### Staging Model

```
/dbt-model staging payments stripe.payments
```

Creates:

- `models/staging/stripe/stg_stripe__payments.sql`
- `models/staging/stripe/_stripe__models.yml` (or appends)

### Intermediate Model

```
/dbt-model intermediate orders_with_customers
```

Creates:

- `models/intermediate/int_orders_with_customers.sql`
- `models/intermediate/_intermediate__models.yml` (or appends)

### Fact Model

```
/dbt-model fact orders
```

Creates:

- `models/marts/fct_orders.sql`
- `models/marts/_marts__models.yml` (or appends)

### Dimension Model

```
/dbt-model dimension customers
```

Creates:

- `models/marts/dim_customers.sql`
- `models/marts/_marts__models.yml` (or appends)

## Generated Templates

### Staging Model

```sql
-- models/staging/stripe/stg_stripe__payments.sql
with source as (
    select * from {{ source('stripe', 'payments') }}
),

renamed as (
    select
        -- Primary Key
        id as payment_id,

        -- Foreign Keys
        customer_id,

        -- Attributes
        status as payment_status,

        -- Measures
        amount / 100.0 as amount,

        -- Timestamps
        created as payment_created_at

    from source
)

select * from renamed
```

### Intermediate Model

```sql
-- models/intermediate/int_orders_with_customers.sql
with orders as (
    select * from {{ ref('stg_shopify__orders') }}
),

customers as (
    select * from {{ ref('stg_shopify__customers') }}
),

joined as (
    select
        orders.*,
        customers.customer_name,
        customers.customer_email
    from orders
    left join customers
        on orders.customer_id = customers.customer_id
)

select * from joined
```

### Fact Model

```sql
-- models/marts/fct_orders.sql
{{
  config(
    materialized='incremental',
    unique_key='order_id'
  )
}}

with source as (
    select * from {{ ref('int_orders_enriched') }}
),

final as (
    select
        -- Keys
        order_id,
        customer_id,
        product_id,

        -- Dimensions
        order_status,
        order_date,

        -- Measures
        quantity,
        amount

    from source
    {% if is_incremental() %}
    where updated_at > (select max(updated_at) from {{ this }})
    {% endif %}
)

select * from final
```

### Dimension Model

```sql
-- models/marts/dim_customers.sql
with source as (
    select * from {{ ref('stg_shopify__customers') }}
),

final as (
    select
        -- Keys
        customer_id,

        -- Attributes
        customer_name,
        customer_email,
        customer_segment,

        -- Flags
        is_active,

        -- Dates
        first_order_date,
        created_at

    from source
)

select * from final
```

## Generated YAML

```yaml
# _models.yml (appended)
models:
  - name: stg_stripe__payments
    description: |
      Staging model for Stripe payments.
      One-to-one with source.

      **Grain**: One row per payment
      **Source**: {{ source('stripe', 'payments') }}
    columns:
      - name: payment_id
        description: Primary key
        tests:
          - unique
          - not_null
```

## Workflow

1. **Parse Arguments**: Determine layer and model type
2. **Check Existing**: Verify model doesn't already exist
3. **Generate SQL**: Create model file from template
4. **Generate YAML**: Create or append schema YAML
5. **Verify**: Compile model to check for errors

## Post-Creation Steps

After model is created:

```bash
# Compile to verify
dbt compile --select [model_name]

# Run model
dbt run --select [model_name]

# Add tests
# (manually add to YAML)

# Run tests
dbt test --select [model_name]
```

## Interactive Mode

When invoked without arguments (`/dbt-model`), prompts for:

1. **Model layer?** → staging, intermediate, fact, dimension
2. **Model name?** → base name
3. **Source?** (if staging) → source.table reference
4. **Materialization?** → table, view, incremental
5. **Incremental key?** (if incremental) → unique key column

## Persona Integration

This command activates the **Data Modeler** (`dbt-model:`) persona for proper model design and naming conventions.

## Related

- [[dbt-test.md]] - Add tests to the model
- [[dbt-run.md]] - Run the model
- [[dbt-docs.md]] - Document the model
- [[../skills/dbt-model-development.md]] - Full development workflow
- [[../agents/data-modeler.md]] - Data Modeler persona
