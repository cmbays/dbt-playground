# Metrics Database

SQLite database for workflow adherence metrics and anomaly detection.

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

## Files (To Be Created)

- `schema.sql` - Database schema definition
- `migrations/` - Schema migrations
- `metrics.db` - SQLite database (gitignored)

## Related Issues

- #158 - Design SQLite schema for metrics
- #159 - Implement adherence scoring formula
- #160 - Build anomaly detection rules engine
- #167 - Implement event sync script
- #168 - Extend Workflow Hub with metrics widgets
