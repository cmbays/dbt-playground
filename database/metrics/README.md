# Metrics Database

DuckDB database for workflow adherence metrics and anomaly detection.

**Epic**: #146 (Metrics & Dashboard System)
**Status**: In Development

## Schema (Planned)

| Table | Purpose |
|-------|---------|
| sessions | Workflow session tracking |
| phase_transitions | Phase entries/exits |
| test_results | dbt test outcomes |
| agent_invocations | Agent activity |
| daily_metrics | Aggregated daily metrics |
| anomalies | Detected violations |
| pr_metrics | GitHub PR data |

## Files by Issue & Sprint Track

| File | Issue | Track | Purpose |
|------|-------|-------|---------|
| `schema/metrics-schema.sql` | #158 | α | Core DuckDB schema (sessions, transitions, invocations) |
| `schema/live-views.sql` | #158 | α | Unified views for dashboard queries |
| `migrations/` | #167 | β | Schema migrations and versioning |
| `sync/` | #167 | β | Event sync scripts from memory/events.jsonl |
| `metrics.db` | #159 | γ | DuckDB database file (gitignored) |
| `daily_metrics` table | #159 | γ | Aggregated adherence scores by day |
| `anomalies` table | #160 | δ | Detected workflow violations |
| `anomaly-rules.yml` | #160 | δ | Rule configuration for anomaly detection |
| Dashboard widgets | #168 | ε | Workflow Hub metrics integration |

### Sprint Tracks

| Track | Focus | Issues |
|-------|-------|--------|
| **α** (Alpha) | Schema Design | #158 |
| **β** (Beta) | Event Sync & Migrations | #167 |
| **γ** (Gamma) | Adherence Scoring | #159 |
| **δ** (Delta) | Anomaly Detection | #160 |
| **ε** (Epsilon) | Dashboard Widgets | #168 |

## Related Issues

- #158 - Design DuckDB schema for metrics
- #159 - Implement adherence scoring formula
- #160 - Build anomaly detection rules engine
- #167 - Implement event sync script
- #168 - Extend Workflow Hub with metrics widgets
