# dbt Source Onboarding Skill

Workflow for adding new data sources to the dbt project.

## Overview

This skill guides the process of onboarding new data sources, from discovery through staging model creation.

## Trigger

Invoke when:

- New data source available in warehouse
- Integrating new third-party data
- Adding internal system data
- Expanding to new schemas

## Workflow Steps

### Phase 1: DISCOVER - Understand the Source

1. **Identify Source Location**

   ```sql
   -- Find available tables
   show tables in database raw;
   show tables in schema raw.stripe;

   -- Or use information_schema
   select table_name, row_count
   from information_schema.tables
   where table_schema = 'stripe';
   ```

2. **Explore Table Structure**

   ```sql
   -- Get column info
   describe table raw.stripe.payments;

   -- Sample data
   select * from raw.stripe.payments limit 100;
   ```

3. **Document Findings**

   ```markdown
   # Source Discovery: Stripe

   ## Tables Found
   | Table | Rows | Key Columns | Notes |
   |-------|------|-------------|-------|
   | payments | 1.2M | id, customer_id | Main fact |
   | customers | 50K | id, email | Customer dim |
   | subscriptions | 30K | id, customer_id | Subscription data |

   ## Data Quality Notes
   - payments.id is unique
   - Some null customer_ids (guest payments)
   - created column is timestamp
   ```

### Phase 2: DEFINE - Create Source Configuration

1. **Create Source YAML**

   ```yaml
   # models/staging/stripe/_stripe__sources.yml
   version: 2

   sources:
     - name: stripe
       description: |
         Stripe payment data synced via Fivetran.
         Updates every 6 hours.

         **Owner**: Finance Team
         **Contact**: #data-stripe in Slack
       database: raw
       schema: stripe

       freshness:
         warn_after: {count: 12, period: hour}
         error_after: {count: 24, period: hour}
       loaded_at_field: _fivetran_synced

       tables:
         - name: payments
           description: |
             Individual payment transactions including
             charges, refunds, and disputes.
           columns:
             - name: id
               description: Primary key from Stripe
             - name: customer_id
               description: FK to customers table
             - name: amount
               description: Amount in cents
             - name: currency
               description: ISO currency code
             - name: created
               description: Payment creation timestamp

         - name: customers
           description: Stripe customer records
           columns:
             - name: id
               description: Primary key
             - name: email
               description: Customer email
   ```

2. **Test Source Connection**

   ```bash
   # Compile to verify source exists
   dbt compile --select source:stripe

   # Check freshness
   dbt source freshness --select source:stripe
   ```

### Phase 3: STAGE - Create Staging Models

1. **Use dbt-mcp to Generate** (if available)

   ```bash
   # Generate staging model scaffold
   dbt run-operation generate_staging_model \
     --args '{"source_name": "stripe", "table_name": "payments"}'
   ```

2. **Or Create Manually**

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
           currency,

           -- Measures (convert cents to dollars)
           amount / 100.0 as amount,

           -- Timestamps
           created as payment_created_at,
           _fivetran_synced as synced_at

       from source
   )

   select * from renamed
   ```

3. **Create Staging Schema YAML**

   ```yaml
   # models/staging/stripe/stg_stripe__payments.yml
   version: 2

   models:
     - name: stg_stripe__payments
       description: |
         Staging model for Stripe payments.
         One-to-one with source, with column renaming
         and type casting only.

         **Source**: `{{ source('stripe', 'payments') }}`
         **Grain**: One row per payment attempt
       columns:
         - name: payment_id
           description: Primary key from Stripe
           tests:
             - unique
             - not_null

         - name: customer_id
           description: FK to Stripe customer

         - name: amount
           description: Payment amount in USD (converted from cents)
           tests:
             - not_null
   ```

### Phase 4: VALIDATE - Test and Verify

1. **Run Staging Model**

   ```bash
   dbt run --select stg_stripe__payments
   ```

2. **Run Tests**

   ```bash
   dbt test --select stg_stripe__payments
   ```

3. **Verify Data Quality**

   ```sql
   -- Check row counts match source
   select
       (select count(*) from {{ source('stripe', 'payments') }}) as source_count,
       (select count(*) from {{ ref('stg_stripe__payments') }}) as staging_count;

   -- Check for nulls in critical columns
   select
       count(*) as total,
       count(payment_id) as with_payment_id,
       count(customer_id) as with_customer_id
   from {{ ref('stg_stripe__payments') }};
   ```

### Phase 5: DOCUMENT - Complete Documentation

1. **Update Source Documentation**
   - Add all columns to source YAML
   - Document data quality issues
   - Note business context

2. **Create Data Dictionary Entry**

   ```markdown
   # Stripe Data Source

   ## Overview
   Payment processing data from Stripe.

   ## Tables
   - `stg_stripe__payments`: Individual transactions
   - `stg_stripe__customers`: Customer records
   - `stg_stripe__subscriptions`: Recurring billing

   ## Known Issues
   - Guest payments have null customer_id
   - Historical data before 2020 may be incomplete

   ## Refresh Schedule
   - Synced every 6 hours via Fivetran
   - Freshness warning: 12 hours
   - Freshness error: 24 hours
   ```

## Directory Structure

```
models/
└── staging/
    └── stripe/
        ├── _stripe__sources.yml     # Source definition
        ├── _stripe__models.yml      # Model documentation
        ├── stg_stripe__payments.sql
        ├── stg_stripe__customers.sql
        └── stg_stripe__subscriptions.sql
```

## Staging Model Conventions

| Column Type | Source | Staging |
|-------------|--------|---------|
| Primary Key | `id` | `[table]_id` |
| Foreign Key | `customer_id` | `customer_id` |
| Status | `status` | `[context]_status` |
| Amount (cents) | `amount` | `amount` (converted) |
| Timestamp | `created` | `[context]_created_at` |
| Boolean | `is_active` | `is_active` |

## Artifacts

| Output | Location |
|--------|----------|
| Source YAML | `models/staging/[source]/_[source]__sources.yml` |
| Model YAML | `models/staging/[source]/_[source]__models.yml` |
| SQL files | `models/staging/[source]/stg_[source]__[table].sql` |
| Data dictionary | `docs/data-sources/[source].md` |

## Exit Criteria

- [ ] Source YAML created and valid
- [ ] Source freshness configured
- [ ] Staging models created for key tables
- [ ] Tests pass
- [ ] Documentation complete
- [ ] Team notified of new source

## Related Documentation

- [[../agents/data-modeler.md]] - Model design
- [[../agents/dbt-developer.md]] - Implementation
- [[dbt-model-development.md]] - Full development workflow
- [[dbt-testing.md]] - Testing workflow
