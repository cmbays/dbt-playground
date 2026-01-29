# Visualization Layer Roadmap

## Purpose

Long-term plan to expose healthcare analytics data through dashboards, visualizations, and engaging narratives using open source solutions.

---

## Executive Summary

We recommend **Lightdash** as the primary BI tool due to its native dbt integration, open source nature, and semantic layer support. Alternatives are evaluated below.

---

## Tool Evaluation

### Tier 1: dbt-Native (Recommended)

#### Lightdash (Recommended)

**Why**: Built specifically for dbt teams. Defines metrics once in dbt, serves everywhere.

| Aspect | Details |
|--------|---------|
| **License** | MIT Open Source |
| **dbt Integration** | Native - reads dbt models, metrics, and documentation directly |
| **Deployment** | Self-hosted (Docker) or Cloud |
| **Best For** | Teams already using dbt who want consistent metrics |

**Pros**:

- Metrics defined in YAML (single source of truth)
- Automatic joins based on dbt relationships
- Self-service exploration for analysts
- Slack integration for alerts

**Cons**:

- Smaller community than Superset/Metabase
- Less mature visualization library

**Setup Effort**: Low (docker-compose with dbt connection)

---

### Tier 2: General Purpose BI

#### Apache Superset

**Why**: Most powerful open source BI. Extensive chart library.

| Aspect | Details |
|--------|---------|
| **License** | Apache 2.0 |
| **dbt Integration** | Via database connection (query dbt models) |
| **Deployment** | Self-hosted (Docker/K8s) |
| **Best For** | Large organizations needing flexibility |

**Pros**:

- 50+ visualization types
- SQL Lab for ad-hoc queries
- Role-based access control
- Dashboard embedding

**Cons**:

- No native dbt integration (metrics not synced)
- Higher complexity to deploy
- Steeper learning curve

**Setup Effort**: Medium

---

#### Metabase

**Why**: Most user-friendly. Great for non-technical users.

| Aspect | Details |
|--------|---------|
| **License** | AGPL (Open Source) |
| **dbt Integration** | Via database connection |
| **Deployment** | Self-hosted or Cloud |
| **Best For** | Business users self-service |

**Pros**:

- Intuitive question builder
- Beautiful default visualizations
- Easy embedding
- Good documentation

**Cons**:

- Limited SQL customization
- No dbt metric sync
- AGPL license restrictions

**Setup Effort**: Low

---

### Tier 3: Headless/API-First

#### Cube.dev

**Why**: Semantic layer API. Build custom frontends.

| Aspect | Details |
|--------|---------|
| **License** | MIT (core), Proprietary (cloud) |
| **dbt Integration** | Can sync with dbt schema |
| **Best For** | Custom embedded analytics |

**Pros**:

- API-first design
- Pre-aggregations for performance
- GraphQL support
- Headless architecture

**Cons**:

- Requires frontend development
- More complex architecture

---

## Recommendation Matrix

| Use Case | Recommended Tool |
|----------|-----------------|
| dbt-native metrics governance | **Lightdash** |
| Complex ad-hoc exploration | Apache Superset |
| Non-technical business users | Metabase |
| Embedded analytics in custom app | Cube.dev |
| Real-time operational dashboards | Grafana + Superset |

---

## Implementation Phases

### Phase 1: Foundation (v0.2)

- [ ] Complete dbt staging and marts layers
- [ ] Define key metrics in dbt YAML
- [ ] Set up development DuckDB database

### Phase 2: BI Tool Setup (v0.3)

- [ ] Deploy Lightdash via Docker
- [ ] Connect to DuckDB
- [ ] Import dbt project
- [ ] Verify metrics and dimensions

### Phase 3: Dashboard Development (v0.4)

- [ ] Create executive summary dashboard
- [ ] Build patient analytics dashboard
- [ ] Build provider performance dashboard
- [ ] Build encounter analysis dashboard

### Phase 4: Engagement Features (v0.5)

- [ ] Add drill-down capabilities
- [ ] Create scheduled reports
- [ ] Set up Slack alerts for anomalies
- [ ] Build "story" mode for narratives

### Phase 5: Production (v1.0)

- [ ] Deploy to production infrastructure
- [ ] Configure authentication (SSO)
- [ ] Set up row-level security
- [ ] Performance optimization

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Lightdash  │  │  Notebooks  │  │  Evidence   │         │
│  │ (Dashboards)│  │  (Analysis) │  │(Narratives) │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
├──────────────────────────┼──────────────────────────────────┤
│                    Semantic Layer                            │
│  ┌───────────────────────┴───────────────────────┐         │
│  │           dbt Metrics + Exposures             │         │
│  │  (dim_patients, fct_encounters, metrics.yml)  │         │
│  └───────────────────────┬───────────────────────┘         │
│                          │                                  │
├──────────────────────────┼──────────────────────────────────┤
│                    Data Layer                               │
│  ┌───────────────────────┴───────────────────────┐         │
│  │              DuckDB / PostgreSQL              │         │
│  │         (marts.dim_*, marts.fct_*)           │         │
│  └───────────────────────┬───────────────────────┘         │
│                          │                                  │
├──────────────────────────┼──────────────────────────────────┤
│                    Source Layer                             │
│  ┌───────────────────────┴───────────────────────┐         │
│  │           Synthea CSV (Healthcare Data)       │         │
│  └───────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## dbt Exposures Configuration

When visualization layer is added, define exposures in dbt:

```yaml
# models/exposures.yml
version: 2

exposures:
  - name: executive_dashboard
    type: dashboard
    maturity: high
    url: https://lightdash.local/dashboard/executive
    description: >
      Executive summary of healthcare analytics including
      patient volumes, encounter trends, and provider metrics.

    depends_on:
      - ref('fct_encounters')
      - ref('dim_patients')
      - ref('dim_providers')

    owner:
      name: Analytics Team
      email: analytics@healthcare.local

  - name: patient_cohort_analysis
    type: analysis
    maturity: medium
    url: https://lightdash.local/explore/patients
    description: Self-service patient cohort exploration

    depends_on:
      - ref('dim_patients')
      - ref('fct_clinical_events')
```

---

## Evidence.dev for Narratives

For "engaging narratives" requirement, consider [Evidence.dev](https://evidence.dev):

- Markdown-based reporting
- SQL embedded in documents
- Auto-generated charts from queries
- Git-based version control
- Static site deployment

```markdown
<!-- Example Evidence report -->
# Healthcare Executive Report

```sql patient_trend
select
  date_trunc('month', encounter_date) as month,
  count(*) as encounters
from fct_encounters
group by 1
order by 1
```

Patient encounters have {patient_trend[patient_trend.length-1].encounters > patient_trend[0].encounters ? 'increased' : 'decreased'} over the past year.

<LineChart data={patient_trend} x=month y=encounters />
```

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Dashboard load time | < 3 seconds | Lightdash metrics |
| User adoption | 80% of analysts | Weekly active users |
| Self-service ratio | 70% | Questions without eng help |
| Data freshness | < 1 hour | Source freshness tests |

---

## Resources

- [Lightdash Docs](https://docs.lightdash.com/)
- [Apache Superset Docs](https://superset.apache.org/)
- [Metabase Docs](https://www.metabase.com/docs/)
- [Evidence.dev](https://evidence.dev/)
- [dbt Exposures](https://docs.getdbt.com/docs/build/exposures)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-29 | Recommend Lightdash | Native dbt integration, open source, good UX |
| 2026-01-29 | Consider Evidence for narratives | Markdown-based, great for storytelling |
| 2026-01-29 | Phase implementation | Build foundation first, then visualizations |

---

*Last Updated: 2026-01-29*
