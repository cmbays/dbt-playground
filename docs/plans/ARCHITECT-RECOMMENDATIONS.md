# Architect Recommendations: dbt Project Initialization

**Author**: Technical Architect
**Created**: 2026-01-28
**Related TDD**: TDD-001-DBT-PROJECT-ARCHITECTURE.md

## Executive Summary

After reviewing the initialization plan, the architecture is sound. This document identifies gaps, additional work items, and patterns to establish early for long-term project health.

---

## 1. Additional Models Recommended

### 1.1 Bridge Tables (Missing from Plan)

The plan identifies `careplans.csv` as a "bridge" table but doesn't include implementation details. Bridge tables are critical for many-to-many relationships.

**Recommended Addition**:

```
models/staging/synthea/stg_synthea__careplans.sql
models/marts/core/bridge_patient_careplans.sql
```

**Rationale**: Care plans connect patients to multiple conditions/medications over time. Without this, analytics on care plan effectiveness is limited.

### 1.2 Conformed Dimensions (Consider for Phase 2)

| Dimension | Purpose | Priority |
|-----------|---------|----------|
| `dim_date` | Date analysis, fiscal periods | Medium |
| `dim_time` | Hour-of-day analysis | Low |
| `dim_icd_codes` | Standardized diagnosis lookup | High |
| `dim_procedure_codes` | CPT/procedure standardization | Medium |

**Recommendation**: Start with `dim_icd_codes` as a seed file to establish the pattern.

### 1.3 Aggregate Fact Tables (Phase 2)

| Model | Purpose |
|-------|---------|
| `fct_patient_encounters_daily` | Daily patient activity summary |
| `fct_provider_productivity` | Provider workload metrics |
| `fct_payer_claims_monthly` | Claims analysis by payer/month |

**Recommendation**: Defer to Phase 2, but design schema with aggregation in mind.

---

## 2. Technical Debt Prevention

### 2.1 Establish Jinja Macro Library Early

Create macros for common patterns to prevent copy-paste code:

```
macros/
├── generate_surrogate_key.sql    # Consistent SK generation
├── clean_string.sql              # Standardize string cleaning
├── calculate_age.sql             # Age calculation (years, months)
├── format_icd_code.sql           # ICD-10 code formatting
└── test_helpers/
    └── expect_no_orphan_fks.sql  # Reusable FK test
```

**Priority Macros**:

```sql
-- macros/calculate_age.sql
{% macro calculate_age(birth_date, reference_date) %}
    date_diff('year', {{ birth_date }}, {{ reference_date }})
{% endmacro %}

-- Usage in model:
{{ calculate_age('p.birth_date', 'e.encounter_date') }} as patient_age_at_encounter
```

### 2.2 Source Freshness Configuration

Add freshness checks to catch stale data:

```yaml
# models/staging/synthea/_synthea__sources.yml
sources:
  - name: synthea_raw
    freshness:
      warn_after: {count: 24, period: hour}
      error_after: {count: 48, period: hour}
    loaded_at_field: _loaded_at  # Add this column in staging
```

**Note**: For initial learning, this is optional but establishes good habits.

### 2.3 Version Control for Model Changes

Establish pattern for model versioning early:

```yaml
# When breaking changes are needed:
models:
  - name: dim_patients
    latest_version: 2
    versions:
      - v: 1
        deprecated: true
      - v: 2
```

---

## 3. Patterns to Establish Early

### 3.1 Standardized Metadata Columns

Every model should include:

```sql
select
    -- ... business columns ...

    -- Metadata (always last)
    current_timestamp as _loaded_at,
    '{{ invocation_id }}' as _dbt_invocation_id
from source
```

### 3.2 NULL Handling Convention

Establish project-wide convention:

```sql
-- Option A: Explicit nullif for empty strings (Recommended)
nullif(trim(first_name), '') as first_name,

-- Option B: coalesce for defaults
coalesce(gender, 'Unknown') as gender,
```

**Recommendation**: Use `nullif` in staging, `coalesce` only in marts with documented defaults.

### 3.3 Test Severity Levels

Define when tests should warn vs. error:

```yaml
# Critical tests (fail the build)
data_tests:
  - unique
  - not_null

# Warning tests (log but continue)
data_tests:
  - relationships:
      to: ref('dim_patients')
      field: patient_id
      severity: warn  # Orphan FKs are logged, not failures
```

### 3.4 Model Contracts (dbt 1.5+)

For critical marts, consider model contracts:

```yaml
models:
  - name: fct_encounters
    config:
      contract:
        enforced: true
    columns:
      - name: encounter_id
        data_type: varchar
      - name: total_claim_cost
        data_type: decimal(10,2)
```

**Recommendation**: Defer contracts until core models stabilize.

---

## 4. Integration Points to Consider

### 4.1 CI/CD for dbt

Establish GitHub Actions workflow early:

```yaml
# .github/workflows/dbt-ci.yml
name: dbt CI

on:
  pull_request:
    paths:
      - 'dbt_project/**'

jobs:
  dbt-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install dbt-duckdb
      - name: dbt deps
        run: cd dbt_project && dbt deps
      - name: dbt compile
        run: cd dbt_project && dbt compile
      - name: dbt test
        run: cd dbt_project && dbt test --select staging
```

**Priority**: Medium (add after MVP works locally)

### 4.2 Pre-commit Hooks for SQL

Consider SQLFluff for SQL linting:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 3.0.0
    hooks:
      - id: sqlfluff-lint
        args: [--dialect, duckdb]
      - id: sqlfluff-fix
        args: [--dialect, duckdb]
```

**Priority**: Low (nice-to-have for consistency)

### 4.3 dbt Cloud / Elementary Integration

For production-grade observability:

| Tool | Purpose | When to Add |
|------|---------|-------------|
| Elementary | Data observability, anomaly detection | Phase 2 |
| dbt Cloud | Scheduling, IDE, docs hosting | If scaling beyond local |
| Great Expectations | Advanced data quality | If dbt_expectations insufficient |

---

## 5. Git Workflow for Model Development

### 5.1 Branch Naming for dbt

Extend existing conventions:

```
feat/model-{layer}-{entity}     # feat/model-staging-patients
fix/model-{name}-{issue}        # fix/model-fct-encounters-null-cost
docs/model-{name}               # docs/model-dim-patients
test/model-{name}               # test/model-stg-observations
```

### 5.2 Commit Message Scope

Add dbt-specific scopes:

```
feat(models/staging): add stg_synthea__patients
fix(models/marts): handle null payer_id in fct_encounters
test(models): add uniqueness tests for all staging models
docs(models): add column descriptions for dim_patients
```

### 5.3 PR Checklist for Model Changes

```markdown
## Model Change Checklist

### Before Merge
- [ ] `dbt compile` passes
- [ ] `dbt run --select <model>+` succeeds
- [ ] `dbt test --select <model>` passes
- [ ] Model YAML has description
- [ ] Key columns documented
- [ ] No hardcoded values (use vars or macros)

### For New Models
- [ ] Follows naming convention
- [ ] Added to appropriate layer
- [ ] Has uniqueness test on PK
- [ ] Foreign keys have relationship tests

### For Schema Changes
- [ ] Downstream models checked
- [ ] Version bump if breaking change
- [ ] Migration plan documented
```

---

## 6. Learning Opportunities

### 6.1 Intentional Complexity Scenarios

To maximize learning, introduce these scenarios:

| Scenario | How to Implement | Learning |
|----------|------------------|----------|
| Late-arriving facts | Add encounter with future date, then backfill | Incremental models |
| SCD Type 2 | Patient address changes | Snapshot functionality |
| Data quality issue | Introduce duplicate patient IDs | Testing importance |
| Schema evolution | Add new column to source | Handling source changes |

### 6.2 Tuva Project Reference

After MVP, study Tuva Project patterns:

```bash
# Clone for reference (don't install as package initially)
git clone https://github.com/tuva-health/tuva.git /tmp/tuva-reference

# Key patterns to study:
# - Claims data marts
# - Quality measures
# - Terminology standardization
```

**Recommendation**: Reference Tuva after core models work, before building advanced analytics.

---

## 7. Risk Mitigations Not in Original Plan

### 7.1 Database Backup Strategy

DuckDB files are single files that can be easily lost:

```bash
# Add to scripts/backup_db.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp dbt_project/dev.duckdb dbt_project/backups/dev_${DATE}.duckdb

# Keep last 5 backups
cd dbt_project/backups && ls -t | tail -n +6 | xargs rm -f
```

### 7.2 Sample Data Fallback

If Synthea generation fails, provide alternative:

1. Create minimal CSV samples in `seeds/sample/`
2. Document download link for pre-generated data
3. Add script to fetch sample data

```bash
# scripts/fetch_sample_data.sh
#!/bin/bash
# Fallback if Synthea generation fails
curl -L "https://example.com/synthea-sample-500.zip" -o /tmp/synthea.zip
unzip /tmp/synthea.zip -d dbt_project/data/synthea/
```

### 7.3 MCP Timeout Handling

Document expected timeouts and workarounds:

```markdown
## MCP Timeout Reference

| Operation | Expected Time | Timeout Risk |
|-----------|---------------|--------------|
| dbt compile | <5s | Low |
| dbt run (staging) | <30s | Low |
| dbt run (all) | 1-2min | Medium |
| dbt docs generate | 30s-1min | Medium |

If timeout occurs, run via CLI directly.
```

---

## 8. Immediate Next Steps (Prioritized)

### Priority 1: Environment Setup (Day 1)

1. Install dbt-duckdb: `pip install dbt-duckdb`
2. Create profiles.yml in ~/.dbt/
3. Verify with `dbt debug`

### Priority 2: Data Acquisition (Day 1)

1. Generate Synthea data OR download sample
2. Place in dbt_project/data/synthea/
3. Verify CSV structure matches expected

### Priority 3: Project Scaffold (Day 1-2)

1. Run `dbt init dbt_project`
2. Configure dbt_project.yml per plan
3. Create directory structure
4. Install packages (dbt deps)

### Priority 4: First Model (Day 2)

1. Create source definition
2. Implement stg_synthea__patients
3. Add tests
4. Run and verify

### Priority 5: MCP Integration (Day 2-3)

1. Update .mcp.json
2. Verify dbt-mcp connection
3. Test basic MCP commands
4. Document any issues

---

## 9. Success Metrics

Track these to measure project health:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Model test coverage | 100% PK tests | `dbt test` output |
| Documentation coverage | 100% models described | dbt docs review |
| Build time | <2 min full run | `dbt run` timing |
| Test pass rate | 100% | CI/CD reporting |
| Agent task success | >90% | Manual tracking |

---

## Appendix: File Checklist

### Files to Create (in order)

```
[ ] ~/.dbt/profiles.yml                              # Database connection
[ ] dbt_project/dbt_project.yml                      # Project config
[ ] dbt_project/packages.yml                         # Package dependencies
[ ] .mcp.json                                        # MCP configuration
[ ] dbt_project/data/synthea/*.csv                   # Raw data
[ ] dbt_project/models/staging/synthea/_synthea__sources.yml
[ ] dbt_project/models/staging/synthea/_synthea__models.yml
[ ] dbt_project/models/staging/synthea/stg_synthea__patients.sql
[ ] dbt_project/models/staging/synthea/stg_synthea__encounters.sql
[ ] dbt_project/models/staging/synthea/stg_synthea__conditions.sql
[ ] dbt_project/models/staging/synthea/stg_synthea__medications.sql
[ ] dbt_project/models/staging/synthea/stg_synthea__procedures.sql
[ ] dbt_project/models/staging/synthea/stg_synthea__observations.sql
[ ] dbt_project/models/staging/synthea/stg_synthea__providers.sql
[ ] dbt_project/models/staging/synthea/stg_synthea__organizations.sql
[ ] dbt_project/models/staging/synthea/stg_synthea__payers.sql
[ ] dbt_project/models/marts/core/_core__models.yml
[ ] dbt_project/models/marts/core/dim_patients.sql
[ ] dbt_project/models/marts/core/dim_providers.sql
[ ] dbt_project/models/marts/core/fct_encounters.sql
```

### Files to Modify

```
[ ] .gitignore                                       # Add dbt artifacts
[ ] CLAUDE.md                                        # Update project status
[ ] docs/reference/PROJECT_STRUCTURE.md              # Add dbt structure
[ ] docs/reference/ARCHITECTURE.md                   # Update with dbt details
```

---

*This document should be reviewed and updated after MVP completion to capture learnings.*
