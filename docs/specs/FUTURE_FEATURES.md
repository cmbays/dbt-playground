---
audience: [pm, architect]
priority: low
size: small
dependencies: []
last_updated: 2026-01-29
status: active
tags: [specs, backlog, ideas]
---

# Future Features Backlog

Ideas and features for future consideration. Items here are not committed - they represent possibilities to explore.

## Metric Marts (Promoted to PRD-012)

The metrics foundation feature has been promoted to active planning. See [PRD-012-SEMANTIC-LAYER](./PRD-012-SEMANTIC-LAYER.md) for full requirements.

### Summary

| Feature | Description | Status | Target |
|---------|-------------|--------|--------|
| Metric marts | Queryable SQL models with standardized metrics | Planned | v0.5.5 |
| Core metrics | 4-5 metrics (total_encounters, claims_paid, etc.) | Planned | v0.5.5 |
| Full dbt Semantic Layer | YAML semantic models + MetricFlow | Deferred | Post-warehouse migration |

### Key Considerations

- **DuckDB Limitation**: MetricFlow query engine has limited DuckDB support
- **First Rollout**: Metric marts (SQL models) - works today
- **Prerequisites**: Stable dimensional models (E4), comprehensive testing (E5)
- **Future**: Full semantic layer when we migrate to supported warehouse

---

## Warehouse Evaluation for Semantic Layer

**Status**: Future Consideration

When the project matures beyond learning/prototyping, evaluate data warehouse solutions that fully support dbt Semantic Layer (MetricFlow).

### Candidates to Evaluate

| Warehouse | MetricFlow Support | Cost Model | Notes |
|-----------|-------------------|------------|-------|
| Snowflake | Full | Usage-based | Enterprise standard, excellent dbt integration |
| BigQuery | Full | Usage-based | Good for GCP shops, serverless |
| Databricks | Full | Usage-based | Good for ML/AI workloads |
| PostgreSQL | Partial | Self-hosted | Lower cost, some limitations |
| MotherDuck | TBD | Usage-based | Cloud DuckDB - may add MetricFlow support |

### Evaluation Criteria

- MetricFlow query engine support
- dbt Cloud integration (optional)
- Cost for learning/small workloads
- Migration effort from DuckDB
- BI tool integration options

### When to Evaluate

- After v1.0 milestone complete
- When BI tool integration becomes a requirement
- When dataset size exceeds DuckDB performance limits

### Future Expansion Ideas (Post-Migration)

| Feature | Description | Complexity | Priority |
|---------|-------------|------------|----------|
| YAML semantic models | Define semantic models in YAML | Medium | High |
| MetricFlow queries | `dbt sl query` commands | Low | High |
| Patient semantic model | Define patient-level metrics | Medium | Medium |
| Clinical events metrics | Condition/medication/procedure counts | Medium | Low |
| BI tool integration | Tableau, Looker, etc. via semantic layer | High | Medium |

---

## Data Modeling Features

### Sample Data Domains

| Feature | Description | Complexity | Priority |
|---------|-------------|------------|----------|
| E-commerce dataset | Orders, customers, products, payments | Medium | High |
| SaaS metrics | Users, events, subscriptions, MRR | Medium | Medium |
| Financial data | Transactions, accounts, categories | Low | Low |
| Marketing analytics | Campaigns, conversions, attribution | High | Low |

### Model Patterns

| Feature | Description | Complexity | Priority |
|---------|-------------|------------|----------|
| Incremental models | Handle large datasets efficiently | Medium | High |
| Snapshots (SCD2) | Track historical changes | Medium | High |
| Slowly changing dims | Multiple SCD strategies | High | Medium |
| Semi-structured data | JSON/VARIANT handling | Medium | Medium |

## dbt Advanced Features

### Macros & Jinja

| Feature | Description | Complexity | Priority |
|---------|-------------|------------|----------|
| Generic test macros | Reusable data quality tests | Low | High |
| Model generator macro | Generate models from metadata | Medium | Medium |
| Audit columns macro | Standard audit fields | Low | High |
| Dynamic SQL macro | Flexible query building | Medium | Low |

### Testing & Quality

| Feature | Description | Complexity | Priority |
|---------|-------------|------------|----------|
| Custom schema tests | Domain-specific validations | Medium | High |
| Data freshness checks | Source monitoring | Low | High |
| Row count trending | Anomaly detection | Medium | Medium |
| Column-level lineage | Impact analysis | High | Low |

## Integration Features

### Database Connections

| Feature | Description | Complexity | Priority |
|---------|-------------|------------|----------|
| DuckDB local | Fast local development | Low | High |
| PostgreSQL | Standard relational database | Low | Medium |
| BigQuery | Cloud data warehouse | Medium | Low |
| Snowflake | Enterprise data warehouse | Medium | Low |

### Tooling

| Feature | Description | Complexity | Priority |
|---------|-------------|------------|----------|
| dbt-mcp integration | AI-assisted development | Medium | High |
| Pre-commit hooks | Code quality automation | Low | Medium |
| SQLFluff linting | SQL style enforcement | Low | Medium |
| dbt docs hosting | Documentation site | Low | Low |

## Learning Objectives

### dbt Skills

- [ ] Model types (table, view, incremental, ephemeral)
- [ ] ref() and source() functions
- [ ] Jinja templating basics
- [ ] Custom schema configuration
- [ ] Environment handling (dev/prod)
- [ ] Metric mart patterns
- [ ] Semantic layer concepts (future)

### Data Engineering Skills

- [ ] Dimensional modeling
- [ ] Data quality testing patterns
- [ ] Incremental loading strategies
- [ ] Documentation as code
- [ ] Metric governance

### AI-Assisted Development

- [ ] dbt-mcp query assistance
- [ ] Model generation prompts
- [ ] Test generation patterns
- [ ] Documentation generation

---

## How to Use This Document

1. **Add ideas**: Any feature idea can be added here
2. **Prioritize**: PM reviews and sets priorities periodically
3. **Promote to PRD**: High-priority items become PRDs when ready
4. **Archive**: Completed or rejected items moved to archive

## Promotion Criteria

Move to PRD when:

- Clear user benefit identified
- Technical feasibility assessed
- Fits current phase goals
- Resources available

## Recently Promoted

| Feature | PRD | Date | Version |
|---------|-----|------|---------|
| Metric Marts Foundation | PRD-012 | 2026-01-29 | v0.5.5 |

---

*This is a living backlog. Ideas may be added, modified, or removed as the project evolves.*

*Last Updated: 2026-01-29*
