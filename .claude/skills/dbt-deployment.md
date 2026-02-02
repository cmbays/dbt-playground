# dbt Deployment Skill

Safe deployment workflow for dbt models including compile, run, test, and docs.

## Overview

This skill provides a structured approach to deploying dbt changes to production safely.

## Trigger

Invoke when:

- Deploying new models to production
- Running incremental updates
- Refreshing full tables
- Generating production documentation
- CI/CD pipeline configuration

## Pre-Deployment Checklist

### Code Quality

- [ ] Code review approved
- [ ] All tests pass locally
- [ ] No circular dependencies
- [ ] Incremental logic verified
- [ ] Documentation complete

### Environment

- [ ] Target environment is correct
- [ ] Database credentials valid
- [ ] Sufficient warehouse resources
- [ ] Downstream dependencies notified

## Deployment Workflow

### Phase 1: COMPILE - Verify SQL

```bash
# Compile to verify Jinja templating
dbt compile --target prod

# Review compiled SQL
cat target/compiled/project/models/marts/fct_orders.sql
```

**Verify:**

- No syntax errors
- Correct table references
- Variables resolved correctly
- Macros expanded properly

### Phase 2: RUN - Execute Models

#### Option A: Full Refresh

```bash
# Full refresh of specific model
dbt run --select fct_orders --full-refresh --target prod

# Full refresh of model and descendants
dbt run --select fct_orders+ --full-refresh --target prod
```

#### Option B: Incremental Run

```bash
# Standard incremental run
dbt run --select fct_orders --target prod

# Run upstream dependencies first
dbt run --select +fct_orders --target prod
```

#### Option C: Build (Run + Test)

```bash
# Build runs models then tests
dbt build --select fct_orders --target prod

# Build with fail-fast
dbt build --select fct_orders --target prod --fail-fast
```

### Phase 3: TEST - Validate Quality

```bash
# Run tests on deployed models
dbt test --select fct_orders --target prod

# Run with stored failures for debugging
dbt test --select fct_orders --target prod --store-failures
```

**Critical:** Do not skip testing. Tests catch data quality issues before downstream consumers are affected.

### Phase 4: DOCS - Update Documentation

```bash
# Generate documentation
dbt docs generate --target prod

# Upload to documentation hosting (if configured)
# dbt docs serve --port 8080
```

### Phase 5: VALIDATE - Post-Deployment Checks

```sql
-- Check row counts
select count(*) from prod.fct_orders;

-- Check latest data
select max(updated_at) from prod.fct_orders;

-- Spot check key metrics
select
    date_trunc('day', order_date) as day,
    count(*) as orders,
    sum(total_amount) as revenue
from prod.fct_orders
where order_date >= current_date - 7
group by 1
order by 1 desc;
```

## Deployment Patterns

### Single Model

```bash
dbt build --select model_name --target prod
```

### Model with Upstream

```bash
dbt build --select +model_name --target prod
```

### Model with Downstream

```bash
dbt build --select model_name+ --target prod
```

### Full Lineage

```bash
dbt build --select +model_name+ --target prod
```

### Tag-Based

```bash
# Run all models tagged with 'daily'
dbt build --select tag:daily --target prod
```

### Source-Based

```bash
# Run all models downstream of a source
dbt build --select source:stripe+ --target prod
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: dbt CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  dbt-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dbt
        run: pip install dbt-snowflake

      - name: Run dbt deps
        run: dbt deps

      - name: Run dbt compile
        run: dbt compile --target ci

      - name: Run dbt build (modified models)
        run: |
          dbt build --select state:modified+ \
            --target ci \
            --defer \
            --state ./prod-manifest

      - name: Run dbt docs generate
        run: dbt docs generate --target ci
```

### Slim CI (Modified Models Only)

```bash
# Run only modified models (requires manifest from prod)
dbt build \
  --select state:modified+ \
  --defer \
  --state ./path/to/prod/manifest \
  --target ci
```

## Rollback Procedures

### Immediate Rollback

```bash
# Re-run previous version from git
git checkout HEAD~1 -- models/marts/fct_orders.sql
dbt run --select fct_orders --full-refresh --target prod
```

### Blue-Green Deployment

```sql
-- Swap schemas (Snowflake example)
alter schema prod rename to prod_old;
alter schema prod_new rename to prod;
```

### Point-in-Time Recovery

```sql
-- Use time travel (Snowflake)
create table prod.fct_orders as
select * from prod.fct_orders at (timestamp => '2024-01-15 10:00:00');
```

## Monitoring

### Post-Deployment Checks

```bash
# Check for freshness
dbt source freshness --target prod

# Check model status
dbt run-operation get_last_runs
```

### Alert Configuration

```yaml
# dbt_project.yml
on-run-end:
  - "{{ slack_notification(results) }}"
```

## Deployment Commands Reference

| Command | Purpose |
|---------|---------|
| `dbt compile` | Compile Jinja to SQL |
| `dbt run` | Execute models |
| `dbt test` | Run tests |
| `dbt build` | Run + test |
| `dbt docs generate` | Build docs |
| `dbt source freshness` | Check source freshness |
| `dbt run-operation` | Execute macros |

## Exit Criteria

- [ ] Models compiled without errors
- [ ] Models ran successfully
- [ ] All tests pass
- [ ] Documentation generated
- [ ] Post-deployment validation complete
- [ ] Stakeholders notified

## Emergency Procedures

### Production Issue

1. **Assess Impact**: Who is affected?
2. **Notify**: Alert stakeholders immediately
3. **Rollback**: Revert to last known good state
4. **Investigate**: Root cause analysis
5. **Fix**: Apply correction
6. **Redeploy**: Follow standard deployment
7. **Postmortem**: Document learnings

### Failed Test in Production

1. Check test severity (error vs warn)
2. If error: pause downstream jobs
3. Investigate failed rows
4. Fix source or adjust test
5. Re-run and verify

## Related Documentation

- [[../agents/dbt-developer.md]] - Implementation
- [[../agents/dbt-tester.md]] - Testing
- [[dbt-testing.md]] - Test workflow
- [[dbt-model-development.md]] - Development workflow
- [[deployment-workflow.md]] - General deployment
