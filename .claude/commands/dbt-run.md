# dbt-run Command

Execute dbt commands safely with validation and logging.

## Usage

```
/dbt-run [command] [options]
/dbt-run build --select model_name
/dbt-run run --select +model_name+
/dbt-run test --select model_name
/dbt-run compile --select model_name
```

## Commands

| Command | Description |
|---------|-------------|
| `run` | Execute model SQL |
| `build` | Run + test models |
| `test` | Run tests only |
| `compile` | Compile Jinja to SQL |
| `seed` | Load seed files |
| `snapshot` | Run snapshots |
| `source` | Check source freshness |
| `docs` | Generate documentation |

## Selection Options

| Option | Description | Example |
|--------|-------------|---------|
| `--select` | Select specific models | `--select fct_orders` |
| `+model` | Model and upstream | `--select +fct_orders` |
| `model+` | Model and downstream | `--select fct_orders+` |
| `+model+` | Full lineage | `--select +fct_orders+` |
| `tag:` | Models with tag | `--select tag:daily` |
| `source:` | From source | `--select source:stripe+` |
| `state:modified` | Changed models | `--select state:modified` |

## Examples

### Build Single Model

```
/dbt-run build --select fct_orders
```

Executes:

```bash
dbt build --select fct_orders
```

### Build with Upstream

```
/dbt-run build --select +fct_orders
```

Runs all dependencies first, then fct_orders.

### Full Refresh

```
/dbt-run run --select fct_orders --full-refresh
```

Rebuilds incremental model from scratch.

### Run Tests

```
/dbt-run test --select fct_orders
```

Runs only tests, no model execution.

### Compile Only

```
/dbt-run compile --select fct_orders
```

Compiles Jinja to SQL without executing.

### Check Source Freshness

```
/dbt-run source freshness --select source:stripe
```

Checks if sources are fresh.

### Generate Docs

```
/dbt-run docs generate
```

Generates documentation site.

## Pre-Run Validation

Before executing, the command validates:

1. **Target Environment**: Confirms dev/prod target
2. **Model Exists**: Verifies model is valid
3. **Dependencies**: Checks upstream models exist
4. **Permissions**: Confirms database access

## Execution Workflow

```
1. Parse command and options
2. Validate model selection
3. Confirm target environment
4. Execute dbt command
5. Report results
6. Log execution
```

## Output Format

```
/dbt-run build --select fct_orders

Target: dev
Models: fct_orders (1 model)
Upstream: +fct_orders (3 models)

Running dbt build...

[Run]
✓ stg_shopify__orders (view) .............. [SUCCESS in 1.2s]
✓ stg_shopify__customers (view) ........... [SUCCESS in 0.8s]
✓ fct_orders (incremental) ................ [SUCCESS in 3.4s]

[Test]
✓ unique_fct_orders_order_id .............. [PASS]
✓ not_null_fct_orders_order_id ............ [PASS]
✓ relationships_fct_orders_customer_id .... [PASS]

Summary:
  3 models ran successfully
  3 tests passed
  Total time: 5.4s
```

## Error Handling

### Compilation Error

```
/dbt-run build --select fct_orders

✗ Compilation Error
  Model 'fct_orders' references undefined model 'stg_missing'

  Fix: Create the missing model or update the reference
```

### Test Failure

```
/dbt-run build --select fct_orders

[Run]
✓ fct_orders (incremental) ................ [SUCCESS in 3.4s]

[Test]
✓ unique_fct_orders_order_id .............. [PASS]
✗ not_null_fct_orders_customer_id ......... [FAIL]
  Got 15 results, configured to fail if != 0

  View failed rows:
  dbt test --select fct_orders --store-failures
```

### Runtime Error

```
/dbt-run build --select fct_orders

✗ Database Error
  Timeout executing query for fct_orders

  Suggestions:
  - Check query complexity
  - Consider incremental materialization
  - Add partition filters
```

## Advanced Options

### Fail Fast

```
/dbt-run build --select fct_orders+ --fail-fast
```

Stops on first failure.

### Threads

```
/dbt-run build --select tag:daily --threads 4
```

Parallel execution.

### Target

```
/dbt-run build --select fct_orders --target prod
```

Specifies environment.

### Defer

```
/dbt-run build --select state:modified --defer --state ./prod-manifest
```

Uses production for unmodified models.

## Interactive Mode

When invoked without arguments (`/dbt-run`), prompts for:

1. **Command?** → build, run, test, compile
2. **Model selection?** → model name or pattern
3. **Include upstream?** → Yes/No
4. **Include downstream?** → Yes/No
5. **Full refresh?** (if incremental) → Yes/No

## Safety Checks

### Production Target

```
/dbt-run build --select fct_orders --target prod

⚠️  You are targeting PRODUCTION

  Target: prod
  Models: fct_orders

  Type 'yes' to confirm: _
```

### Full Refresh Warning

```
/dbt-run run --select fct_orders --full-refresh

⚠️  Full refresh will rebuild the entire table

  Model: fct_orders
  Current rows: 1,234,567
  Estimated time: ~15 minutes

  Continue? [y/N]: _
```

## Persona Integration

This command uses the **dbt Developer** (`dbt-dev:`) persona for execution and error diagnosis.

## Related

- [[dbt-model.md]] - Create models to run
- [[dbt-test.md]] - Test models after running
- [[dbt-docs.md]] - Generate documentation
- [[../skills/dbt-deployment.md]] - Deployment workflow
- [[../agents/dbt-developer.md]] - dbt Developer persona
