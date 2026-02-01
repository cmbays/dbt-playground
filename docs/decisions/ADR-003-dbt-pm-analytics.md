# ADR-003: dbt for PM Analytics

**Status**: Superseded by Hybrid Lite Architecture (2026-02-01)
**Date**: 2026-01-31
**Decision Makers**: Architect, Data Modeler
**Context**: PRD-022, TDD-022 (PM Orchestration System)

> **UPDATE (2026-02-01)**: This decision was **deferred** to future enhancements.
> No SQLite database in Hybrid Lite architecture = no dbt analytics needed for v0.9.
> See:
>
> - ARCH_DECISION_HYBRID_LITE.md for deferral rationale
> - Issue #141 for future consideration
> - PRD-022 Future Enhancements section

---

## Context

The PM Orchestration System generates operational data:

- Session lifecycle events
- Task state transitions
- Agent activity patterns
- Alert history

This data has analytical value:

- **Health monitoring**: Is the project on track?
- **Bottleneck detection**: Where do tasks stall?
- **Productivity insights**: Which agents are most active?
- **Trend analysis**: Are we improving over time?

Question: How should we build analytics on PM state data?

## Decision

**Use dbt to build analytics models on PM state, connecting SQLite via DuckDB ATTACH.**

The analytics layer includes:

- Staging models (`stg_pm_state__*`) for data cleaning
- Intermediate models (`int_pm_state__*`) for metrics
- Analytics marts (`fct_*`, `dim_*`) for dashboards

## Rationale

### Options Considered

| Criterion | dbt Analytics | Custom Python | Metabase/Superset | No Analytics |
|-----------|---------------|---------------|-------------------|--------------|
| Existing Tooling | **Project uses dbt** | New pattern | New tool | N/A |
| Testing | **Data tests** | Unit tests | None | N/A |
| Documentation | **dbt docs** | Manual | Auto-generated | N/A |
| Lineage | **Built-in** | Manual | Limited | N/A |
| Incremental | **Supported** | Manual | Auto | N/A |
| Learning Curve | Low (existing skill) | Low | Medium | None |
| Maintenance | **Same as project** | Separate | External | None |

### Why dbt

1. **Consistency**: Project already uses dbt; no new paradigm
2. **Tested metrics**: Data tests catch issues early
3. **Documented**: dbt docs for metric definitions
4. **Lineage**: Trace metrics to source data
5. **Incremental**: Handle growing data efficiently
6. **Skill leverage**: Team already knows dbt

### Why Not Custom Python

- Separate maintenance burden
- No built-in testing framework
- No automatic documentation
- Loses lineage visibility

### Why Not Metabase/Superset

- External tool to deploy and maintain
- Duplicates logic that could live in dbt
- Adds operational complexity
- Can add later on top of dbt marts

### Why Not Skip Analytics

- Lose visibility into project health
- Manual bottleneck detection
- No productivity insights
- Dashboard would query raw data (slow, fragile)

## Consequences

### Positive

1. **Unified tooling**: Analytics in same framework as data models
2. **Tested metrics**: Catch calculation errors before dashboards
3. **Documentation**: Metric definitions in dbt docs
4. **Lineage**: Trace dashboard numbers to source
5. **Reusable**: dbt models power dashboard, MCP queries, reports

### Negative

1. **More models**: Additional dbt models to maintain
2. **SQLite quirks**: Some DuckDB features may not work with attached SQLite
3. **Coupling**: Analytics depend on PM state schema

### Mitigation

| Negative | Mitigation |
|----------|------------|
| More models | Separate `pm_state` folder; won't clutter main analytics |
| SQLite quirks | Test thoroughly; fallback to COPY if ATTACH issues |
| Schema coupling | Version schema carefully; staging models abstract differences |

## Integration Approach

### DuckDB ATTACH

DuckDB can attach SQLite databases and query them as if they were native:

```sql
-- In dbt on-run-start hook
ATTACH 'pm_state.db' AS pm_state (TYPE sqlite);
```

After attachment, SQLite tables are queryable:

```sql
SELECT * FROM pm_state.main.sessions;
```

### dbt Source Configuration

```yaml
sources:
  - name: pm_state
    database: pm_state
    schema: main
    tables:
      - name: sessions
      - name: tasks
      - name: alerts
      # ...
```

### Model Layer Structure

```
models/
├── staging/pm_state/           # Clean and type
│   ├── _pm_state__sources.yml  # Source definitions
│   ├── _pm_state__models.yml   # Model tests/docs
│   ├── stg_pm_state__sessions.sql
│   ├── stg_pm_state__tasks.sql
│   └── stg_pm_state__alerts.sql
├── intermediate/pm_state/      # Calculate metrics
│   ├── int_pm_state__session_metrics.sql
│   └── int_pm_state__task_flow.sql
└── marts/pm_analytics/         # Dashboard-ready
    ├── dim_project_health.sql
    ├── fct_agent_productivity.sql
    └── fct_task_bottlenecks.sql
```

## Key Metrics

| Metric | Model | Purpose |
|--------|-------|---------|
| Health Score | `dim_project_health` | Single number (0-100) for project status |
| Task Velocity | `fct_task_bottlenecks` | Tasks completed per day/week |
| Cycle Time | `int_pm_state__task_flow` | Time from UNDERSTAND to DEPLOY |
| Agent Activity | `fct_agent_productivity` | Invocations per agent per day |
| Blocked Rate | `dim_project_health` | % of tasks in BLOCKED status |
| Stale Sessions | `dim_project_health` | Sessions without recent heartbeat |

### Health Score Formula

```sql
health_score = greatest(0, 100
    - (stale_sessions * 10)        -- -10 per stale session
    - (blocked_tasks * 5)          -- -5 per blocked task
    - (unack_errors * 15)          -- -15 per unacknowledged error
    - (unack_warnings * 3)         -- -3 per unacknowledged warning
)
```

## Alternatives Not Chosen

### Embedded SQL in Dashboard

- No testing
- Duplicated logic
- Hard to maintain

### Python Analytics Script

- Separate tooling
- No lineage
- Manual documentation

### Separate Analytics Database

- Extra infrastructure
- Sync complexity
- Overkill for volume

## Implementation Notes

1. Add SQLite ATTACH to `dbt_project.yml` on-run-start
2. Create source definition with data tests
3. Build staging models with type casting and cleaning
4. Build intermediate models for metrics
5. Build marts for dashboard consumption
6. Add `pm_state.db` to .gitignore (state, not code)

## Testing Strategy

```yaml
# _pm_state__models.yml
models:
  - name: stg_pm_state__sessions
    columns:
      - name: session_id
        tests:
          - unique
          - not_null
      - name: session_status
        tests:
          - accepted_values:
              values: ['active', 'stale', 'ended']
```

## Related Decisions

- **ADR-001**: Backlog.md for task management
- **ADR-002**: SQLite for state layer (data source for analytics)

## Review Cycle

This decision should be reviewed:

- If analytics volume exceeds SQLite capability
- If real-time dashboards needed (streaming approach)
- If external BI tool adopted

---

**Approval**: Pending (Architect review required)
