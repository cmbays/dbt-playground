---
audience: [pm, architect]
priority: low
size: small
dependencies: []
last_updated: 2026-01-28
status: active
tags: [specs, backlog, ideas]
---

# Future Features Backlog

Ideas and features for future consideration. Items here are not committed - they represent possibilities to explore.

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

### Data Engineering Skills

- [ ] Dimensional modeling
- [ ] Data quality testing patterns
- [ ] Incremental loading strategies
- [ ] Documentation as code

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

---

*This is a living backlog. Ideas may be added, modified, or removed as the project evolves.*

*Last Updated: 2026-01-28*
