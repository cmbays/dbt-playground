# dbt-docs Command

Generate, serve, and manage dbt documentation.

## Usage

```
/dbt-docs [action]
/dbt-docs generate
/dbt-docs serve
/dbt-docs audit
/dbt-docs add [model_name]
```

## Actions

| Action | Description |
|--------|-------------|
| `generate` | Build documentation site |
| `serve` | Serve docs locally |
| `audit` | Check documentation coverage |
| `add` | Add documentation to model |

## Examples

### Generate Documentation

```
/dbt-docs generate
```

Executes:

```bash
dbt docs generate
```

Output:

```
Generating dbt documentation...

✓ Parsed 45 models
✓ Parsed 12 sources
✓ Parsed 89 tests
✓ Generated catalog.json
✓ Generated manifest.json

Documentation available at: target/

Serve locally with: /dbt-docs serve
```

### Serve Documentation

```
/dbt-docs serve
```

Executes:

```bash
dbt docs serve --port 8080
```

Output:

```
Serving dbt docs at http://localhost:8080

Press Ctrl+C to stop

Features:
- Model lineage DAG
- Column-level documentation
- Test coverage
- Source freshness
```

### Audit Documentation Coverage

```
/dbt-docs audit
```

Output:

```
Documentation Coverage Audit

Models: 45 total
├── With description: 38 (84%)
├── Missing description: 7 (16%)
└── Columns documented: 72%

Missing Model Descriptions:
- int_orders_temp
- stg_legacy__users
- fct_events_v2
...

Columns Missing Descriptions:
- fct_orders.shipping_address_id
- dim_customers.legacy_id
...

Recommendations:
1. Add descriptions to 7 models
2. Document 45 columns
3. Add grain to 3 fact tables
```

### Add Documentation to Model

```
/dbt-docs add fct_orders
```

Interactive mode:

```
Adding documentation to fct_orders

Current description: [empty]

Model description:
> Order transactions at the line item level

Grain (one row per...):
> order line item

Primary key:
> order_line_id

Update frequency:
> Hourly incremental

Columns to document:
1. order_id - Unique order identifier
2. customer_id - FK to dim_customers
3. product_id - FK to dim_products
...

Generated YAML:

models:
  - name: fct_orders
    description: |
      **Grain**: One row per order line item
      **Primary Key**: `order_line_id`
      **Update Frequency**: Hourly incremental

      Order transactions at the line item level.
    columns:
      - name: order_id
        description: Unique order identifier
      - name: customer_id
        description: FK to dim_customers
      ...

Write to models/marts/_marts__models.yml? [Y/n]:
```

## Documentation Templates

### Fact Model

```yaml
description: |
  **Grain**: One row per [grain]
  **Primary Key**: `[key]`
  **Update Frequency**: [schedule]

  [Business description]

  **Key Joins**:
  - [dimension] via [column]
  - [dimension] via [column]

  **Metrics Derived**:
  - [metric name]
```

### Dimension Model

```yaml
description: |
  **Grain**: One row per [entity]
  **Primary Key**: `[key]`
  **SCD Type**: [1/2/none]

  [Business description]

  **Key Attributes**:
  - [attribute 1]
  - [attribute 2]
```

### Staging Model

```yaml
description: |
  Staging model for [source description].
  One-to-one with source, with column renaming
  and type casting only.

  **Source**: `{{ source('[source]', '[table]') }}`
  **Grain**: One row per [grain]
```

### Source Table

```yaml
description: |
  [Business description]

  **Owner**: [team]
  **Contact**: [slack channel or email]
  **Update Frequency**: [schedule]
```

## Best Practices

### Model Descriptions

- Start with grain definition
- Include primary key
- Document update frequency
- List key relationships
- Add business context

### Column Descriptions

- Explain business meaning
- Note source of data
- Document transformations
- Flag nullable columns
- Include units (USD, seconds, etc.)

### Source Descriptions

- Include data owner
- Add contact information
- Document known issues
- Note freshness expectations

## Generated Files

| File | Location | Purpose |
|------|----------|---------|
| `catalog.json` | `target/` | Column metadata |
| `manifest.json` | `target/` | Model dependencies |
| `index.html` | `target/` | Documentation site |
| `run_results.json` | `target/` | Last run status |

## Persona Integration

This command activates the **dbt Documenter** (`dbt-docs:`) persona for comprehensive documentation.

## Related

- [[dbt-model.md]] - Create models to document
- [[dbt-test.md]] - Tests appear in docs
- [[../skills/dbt-model-development.md]] - Development workflow
- [[../agents/dbt-documenter.md]] - dbt Documenter persona
