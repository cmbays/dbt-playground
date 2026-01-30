# dbt-playground Project Roadmap

## Project Vision

Transform the dbt-playground into a fully operational dbt learning environment using synthetic healthcare data (Synthea) with DuckDB, enabling AI-assisted data modeling through MCP integration.

## Goals

1. **Learn dbt fundamentals** through hands-on implementation
2. **Practice dimensional modeling** with realistic healthcare data
3. **Enable AI-assisted development** via dbt-mcp integration
4. **Establish data quality patterns** through comprehensive testing
5. **Document learnings** for future reference and skill development

---

## Epics Overview

| Epic | Name | Description | Version Target |
|------|------|-------------|----------------|
| E1 | Environment Setup | DuckDB, dbt-duckdb adapter, profiles, MCP configuration | v0.2.0 |
| E2 | Data Acquisition | Synthea generation, CSV loading, data exploration | v0.2.0 |
| E3 | Staging Layer | 9 staging models with source definitions and basic tests | v0.3.0 |
| E4 | Dimensional Models | Facts, dimensions, intermediate models for analytics | v0.4.0 |
| E5 | Testing & Quality | Comprehensive testing, documentation, data quality monitoring | v0.5.0 |
| E6 | MCP Integration | AI-assisted workflows, agent verification | v0.5.0 |
| E12 | Metric Marts | Standardized metric calculations in SQL mart models | v0.5.5 |
| E7 | Tuva Foundation | Install Tuva package, build clinical connector layer | v0.6.0 |
| E8 | Clinical Marts | Enable chronic conditions, readmissions, ED classification | v0.7.0 |
| E9 | Claims Acquisition | Acquire CMS SynPUF claims data for financial analytics | v0.8.0 |
| E10 | Claims Connector | Build connector for eligibility, medical_claim, pharmacy_claim | v0.9.0 |
| E11 | Financial Marts | Enable PMPM, cost analysis, HCC risk scores | v1.0.0 |

---

## Epic Details

### E1: Environment Setup

**Goal**: Establish a working dbt development environment with DuckDB and MCP tooling.

**PRD**: [PRD-001-ENVIRONMENT-SETUP](../specs/PRD-001-ENVIRONMENT-SETUP.md)

**Scope**:

- Install dbt-duckdb adapter
- Create and configure `~/.dbt/profiles.yml`
- Initialize dbt project structure
- Configure `.mcp.json` for dbt-mcp
- Update `.gitignore` for dbt artifacts

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Profile configuration | developer | architect |
| Project initialization | dbt-developer | - |
| MCP configuration | developer | architect |
| Verification | dbt-tester | - |

**Success Criteria**:

- `dbt debug` passes successfully
- `dbt deps` installs packages
- MCP server responds to queries

**Dependencies**: None (starting point)

---

### E2: Data Acquisition

**Goal**: Generate or obtain Synthea synthetic healthcare data and make it accessible to dbt.

**PRD**: [PRD-002-DATA-ACQUISITION](../specs/PRD-002-DATA-ACQUISITION.md)

**Scope**:

- Generate 500 synthetic patients via Synthea
- Copy CSV files to `dbt_project/data/synthea/`
- Verify CSV structure and row counts
- Create data exploration queries

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Synthea generation | developer | - |
| Data verification | dbt-tester | - |
| Exploration queries | data-modeler | - |

**Success Criteria**:

- All 9+ CSV files present in data directory
- Each file has expected columns
- DuckDB can read all CSVs via `read_csv_auto()`

**Dependencies**: E1 (Environment Setup)

---

### E3: Staging Layer

**Goal**: Create clean, typed staging models for all Synthea source tables with documentation and basic tests.

**PRD**: [PRD-003-STAGING-LAYER](../specs/PRD-003-STAGING-LAYER.md)

**Scope**:

- Create `_synthea__sources.yml` source definition
- Implement 9 staging models:
  - `stg_synthea__patients`
  - `stg_synthea__encounters`
  - `stg_synthea__conditions`
  - `stg_synthea__medications`
  - `stg_synthea__procedures`
  - `stg_synthea__observations`
  - `stg_synthea__providers`
  - `stg_synthea__organizations`
  - `stg_synthea__payers`
- Add schema tests (unique, not_null)
- Document all models and columns

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Source definition | data-modeler | - |
| Model design | data-modeler | architect |
| Model implementation | dbt-developer | - |
| Schema tests | dbt-tester | - |
| Documentation | dbt-documenter | - |
| Code review | code-reviewer | - |

**Success Criteria**:

- All 9 staging models compile and run
- `dbt test` passes for staging layer
- All models documented with descriptions
- Consistent naming conventions applied

**Dependencies**: E2 (Data Acquisition)

---

### E4: Dimensional Models

**Goal**: Build dimensional models (facts and dimensions) for healthcare analytics.

**PRD**: [PRD-004-DIMENSIONAL-MODELS](../specs/PRD-004-DIMENSIONAL-MODELS.md)

**Scope**:

**Dimension Models**:

- `dim_patients` - Patient demographics with SCD Type 2 history tracking
- `dim_providers` - Healthcare provider information
- `dim_organizations` - Healthcare facilities
- `dim_payers` - Insurance payer dimension with coverage metrics
- `dim_date` - Calendar dimension (1909-2025) for time-based analysis

**Fact Models**:

- `fct_encounters` - Healthcare visits/encounters
- `fct_clinical_events` - Unified clinical events (conditions, medications, procedures)
- `fct_encounters_monthly` - Monthly aggregate for time-series analysis
- `fct_encounters_yearly` - Yearly aggregate for annual reporting

**Intermediate Models**:

- `int_encounters__enriched` - Encounters with computed fields
- `int_patients__with_conditions` - Patients with condition history

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Dimensional design | data-modeler | architect |
| Dimension implementation | dbt-developer | - |
| Fact implementation | dbt-developer | - |
| Aggregate facts | dbt-developer | - |
| Intermediate models | dbt-developer | data-modeler |
| Testing | dbt-tester | - |
| Documentation | dbt-documenter | - |
| Code review | code-reviewer | - |

**Success Criteria**:

- All 11 dimension, fact, and intermediate models compile and run
- Referential integrity tests pass
- SCD Type 2 correctly implemented on dim_patients
- Aggregate facts have correct grain
- Documentation complete for all marts models
- Query performance acceptable for analytics

**Dependencies**: E3 (Staging Layer)

---

### E5: Testing & Quality

**Goal**: Implement comprehensive testing, documentation site, and data quality monitoring.

**Scope**:

- Add `dbt_expectations` tests for data quality
- Create singular tests for business rules
- Generate and serve dbt docs
- Add source freshness monitoring
- Create README documentation

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| dbt_expectations tests | dbt-tester | - |
| Singular tests | dbt-tester | data-modeler |
| Documentation site | dbt-documenter | - |
| Source freshness | dbt-developer | - |

**Success Criteria**:

- `dbt test` passes all tests
- `dbt docs serve` displays documentation site
- Source freshness configured and monitoring
- All models have 80%+ column documentation

**Dependencies**: E4 (Dimensional Models)

---

### E6: MCP Integration

**Goal**: Verify and optimize AI-assisted dbt development workflows.

**Scope**:

- Test all MCP tools (discovery, SQL, CLI)
- Verify agent workflows (model, test, document)
- Create agent workflow documentation
- Validate semantic layer queries (if applicable)

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| MCP tool testing | developer | dbt-developer |
| Agent workflow verification | sage | all dbt agents |
| Documentation | dbt-documenter | sage |

**Success Criteria**:

- All MCP tools functional
- Agent team can create/test/document models via MCP
- Workflow documented in LEARNINGS.md

**Dependencies**: E5 (Testing & Quality)

---

### E12: Metric Marts Foundation

**Goal**: Build standardized metric marts providing consistent, queryable KPIs for healthcare analytics.

**PRD**: [PRD-012-SEMANTIC-LAYER](../specs/PRD-012-SEMANTIC-LAYER.md)

**Scope**:

- Build `mrt_encounters_summary` metric mart model
- Implement 4-5 core metrics in SQL (total_encounters, total_claims_paid, avg_cost_per_encounter, patient_volume)
- Document metrics with business definitions
- Add reconciliation tests

**Key Considerations**:

- DuckDB has limited MetricFlow query engine support
- **First rollout: Metric marts (SQL models)** - works today with DuckDB
- Full dbt Semantic Layer (YAML definitions + MetricFlow) deferred to future warehouse migration
- See FUTURE_FEATURES.md for warehouse evaluation initiative

**Directory Structure**:

```text
models/
└── marts/
    └── metrics/
        ├── _metrics__models.yml       # Schema with metric definitions
        └── mrt_encounters_summary.sql # Queryable metric mart
```

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Metric definitions | data-modeler | - |
| Metric mart SQL | dbt-developer | - |
| Testing | dbt-tester | - |
| Documentation | dbt-documenter | - |
| Architecture review | architect | - |

**Success Criteria**:

- Metric mart model (`mrt_encounters_summary`) built and tested
- 4-5 core metrics implemented in SQL
- Metrics documented with business descriptions
- Reconciliation tests pass (mart totals match source facts)
- Example queries provided for business users

**GitHub Issues**:

1. Metric Marts Foundation Setup - Create `models/marts/metrics/` directory
2. Encounters Metric Mart - Build mrt_encounters_summary model with 4-5 metrics
3. Metric Documentation - Document metrics and provide example queries

**Dependencies**: E4 (Dimensional Models), E5 (Testing & Quality)

---

### E7: Tuva Foundation

**Goal**: Install the Tuva Project dbt package and build a connector layer to transform Synthea staging models into Tuva's Clinical Input Layer format.

**PRD**: [PRD-007-TUVA-FOUNDATION](../specs/PRD-007-TUVA-FOUNDATION.md)

**Scope**:

- Install `tuva-health/the_tuva_project` package (v0.15.3)
- Add `stg_synthea__immunizations` staging model
- Create 10 connector models (`int_tuva__*`)
- Add seed files for terminology mappings
- Configure `clinical_input_enabled: true`

**Connector Models**:

- `int_tuva__patient` - Patient demographics
- `int_tuva__encounter` - Clinical encounters
- `int_tuva__condition` - Diagnoses/conditions
- `int_tuva__procedure` - Procedures performed
- `int_tuva__medication` - Medications
- `int_tuva__observation` - Vitals and clinical observations
- `int_tuva__lab_result` - Laboratory results
- `int_tuva__immunization` - Vaccinations
- `int_tuva__practitioner` - Healthcare providers
- `int_tuva__location` - Facilities/organizations

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Package installation | dbt-developer | - |
| Connector design | data-modeler | architect |
| Connector implementation | dbt-developer | - |
| Mapping seeds | data-modeler | - |
| Testing | dbt-tester | - |
| Documentation | dbt-documenter | - |

**Success Criteria**:

- Tuva package installs without conflicts
- All 10 connector models compile and run
- `dbt compile --select tuva_health.*` succeeds
- Connector models pass schema tests

**Dependencies**: E5 (Testing & Quality), E12 (Semantic Layer - optional)

---

### E8: Clinical Marts

**Goal**: Enable and validate Tuva's clinical data marts for healthcare analytics.

**PRD**: [PRD-008-CLINICAL-MARTS](../specs/PRD-008-CLINICAL-MARTS.md)

**Scope**:

- Enable chronic conditions data mart
- Enable ED classification data mart
- Enable readmissions data mart
- Enable data profiling/quality mart
- Validate analytics output

**Data Marts to Enable**:

| Mart | Purpose | Key Outputs |
|------|---------|-------------|
| `tuva_chronic_conditions` | 40+ condition groupings | Patient condition cohorts |
| `ed_classification` | Emergency visit categorization | ED utilization metrics |
| `readmissions` | 30-day readmission rates | Readmission patterns |
| `data_profiling` | 600+ data quality tests | Quality reports |

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Mart configuration | dbt-developer | - |
| Output validation | dbt-tester | data-modeler |
| Analytics verification | data-modeler | - |
| Documentation | dbt-documenter | - |

**Success Criteria**:

- All enabled marts build successfully
- Chronic conditions groupings populated for patients
- Data quality tests pass (>95% pass rate)
- Analytics queries return valid results

**Dependencies**: E7 (Tuva Foundation)

---

### E9: Claims Acquisition

**Goal**: Acquire synthetic claims data (CMS SynPUF) to unlock Tuva's financial analytics capabilities.

**PRD**: [PRD-009-CLAIMS-ACQUISITION](../specs/PRD-009-CLAIMS-ACQUISITION.md)

**Scope**:

- Download CMS Synthetic Public Use Files (SynPUF)
- Load beneficiary summary data
- Load inpatient/outpatient/carrier claims
- Load prescription drug events
- Verify data structure and quality

**Data Sources**:

| CMS SynPUF File | Target Tuva Table | Description |
|-----------------|-------------------|-------------|
| Beneficiary Summary | `eligibility` | 2M Medicare beneficiaries |
| Inpatient Claims | `medical_claim` | Hospital admissions |
| Outpatient Claims | `medical_claim` | Outpatient services |
| Carrier Claims | `medical_claim` | Physician services |
| PDE (Part D) | `pharmacy_claim` | Prescription drugs |

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Data download | developer | - |
| Data loading | dbt-developer | - |
| Source definition | data-modeler | - |
| Data verification | dbt-tester | - |

**Success Criteria**:

- All SynPUF files downloaded and accessible
- DuckDB can read all claims CSVs
- Source definitions created
- Row counts verified

**Dependencies**: E8 (Clinical Marts)

---

### E10: Claims Connector

**Goal**: Build connector layer to transform CMS SynPUF data into Tuva's Claims Input Layer format.

**PRD**: [PRD-010-CLAIMS-CONNECTOR](../specs/PRD-010-CLAIMS-CONNECTOR.md)

**Scope**:

- Create staging models for SynPUF tables
- Build `eligibility` connector model
- Build `medical_claim` connector model
- Build `pharmacy_claim` connector model
- Configure `claims_input_enabled: true`

**Connector Models**:

- `int_tuva__eligibility` - From beneficiary summary
- `int_tuva__medical_claim` - From inpatient + outpatient + carrier
- `int_tuva__pharmacy_claim` - From prescription drug events

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Staging models | dbt-developer | - |
| Connector design | data-modeler | architect |
| Connector implementation | dbt-developer | - |
| Testing | dbt-tester | - |
| Documentation | dbt-documenter | - |

**Success Criteria**:

- All claims connector models compile and run
- Claims data passes Tuva validation tests
- `dbt compile --select tuva_health.*` succeeds with claims enabled

**Dependencies**: E9 (Claims Acquisition)

---

### E11: Financial Marts

**Goal**: Enable Tuva's financial analytics data marts for cost and risk analysis.

**PRD**: [PRD-011-FINANCIAL-MARTS](../specs/PRD-011-FINANCIAL-MARTS.md)

**Scope**:

- Enable Financial PMPM data mart
- Enable CMS-HCC risk adjustment mart
- Enable claims preprocessing
- Validate financial analytics output

**Data Marts to Enable**:

| Mart | Purpose | Key Outputs |
|------|---------|-------------|
| `financial_pmpm` | Per member per month cost | Cost by service category |
| `cms_hcc` | Risk adjustment scores | RAF scores, HCC conditions |
| `claims_preprocessing` | Encounter grouping | Claim encounter types |

**Agent Assignments**:

| Task | Primary Agent | Supporting |
|------|---------------|------------|
| Mart configuration | dbt-developer | - |
| Financial validation | dbt-tester | data-modeler |
| Analytics verification | data-modeler | - |
| Documentation | dbt-documenter | - |

**Success Criteria**:

- PMPM metrics calculated correctly
- HCC risk scores generated
- Cost analysis queries return valid results
- Project reaches v1.0 milestone

**Dependencies**: E10 (Claims Connector)

---

## Milestones

### M1: v0.2.0 - Foundation

**Target**: Week 1

**Scope**: Epics E1 + E2

**Deliverables**:

- Working dbt environment with DuckDB
- Synthea data loaded and accessible
- MCP configuration in place
- `dbt debug` passes

**Success Metrics**:

- [ ] `dbt debug` shows successful connection
- [ ] `dbt compile` completes without errors
- [ ] All 9 Synthea CSVs present and readable
- [ ] MCP server responds to health check

---

### M2: v0.3.0 - Staging Complete

**Target**: Week 2

**Scope**: Epic E3

**Deliverables**:

- All 9 staging models implemented
- Source definitions complete
- Basic schema tests passing
- Model documentation in place

**Success Metrics**:

- [ ] `dbt run --select staging` completes
- [ ] `dbt test --select staging` passes
- [ ] All staging models have descriptions
- [ ] Naming conventions consistent (`stg_synthea__*`)

---

### M3: v0.4.0 - Analytics Ready

**Target**: Week 3

**Scope**: Epic E4

**Deliverables**:

- 5 dimension models (patients, providers, organizations, payers, date)
- 4 fact models (encounters, clinical_events, monthly, yearly aggregates)
- 2 intermediate models for complex logic
- Referential integrity tests
- SCD Type 2 on dim_patients

**Success Metrics**:

- [ ] `dbt run` completes for all 11 models
- [ ] `dbt test` passes all tests including referential integrity
- [ ] dim_date covers 1909-01-01 to 2025-12-31
- [ ] dim_patients has valid_from, valid_to, is_current columns
- [ ] Aggregate facts have correct grain (year_month x class, year x class)
- [ ] Lineage graph shows proper dependencies
- [ ] Query performance meets expectations (<1 sec for typical queries)

---

### M4: v0.5.0 - Production Quality

**Target**: Week 4

**Scope**: Epics E5 + E6

**Deliverables**:

- Comprehensive test suite
- Documentation site generated
- MCP integration verified
- Agent workflows documented

**Success Metrics**:

- [ ] `dbt test` runs 50+ tests
- [ ] `dbt docs serve` shows complete documentation
- [ ] All MCP tools functional
- [ ] LEARNINGS.md updated with patterns

---

### M4.5: v0.5.5 - Metric Marts

**Target**: Week 4-5

**Scope**: Epic E12

**Deliverables**:

- Metric mart model (`mrt_encounters_summary`)
- 4-5 core metrics implemented in SQL
- Metric documentation with business definitions
- Reconciliation tests

**Success Metrics**:

- [ ] `models/marts/metrics/` directory created
- [ ] `mrt_encounters_summary` model built and passing tests
- [ ] 4-5 metrics: total_encounters, total_claims_paid, avg_cost_per_encounter, patient_volume, avg_duration
- [ ] Metrics documented with business descriptions and example queries

---

### M5: v0.6.0 - Tuva Foundation

**Target**: Week 5-6

**Scope**: Epic E7

**Deliverables**:

- Tuva package installed and configured
- 10 clinical connector models built
- Immunizations staging model added
- Terminology mapping seeds created

**Success Metrics**:

- [ ] `dbt deps` installs Tuva without conflicts
- [ ] `dbt build --select tag:tuva_connector` completes
- [ ] `dbt compile --select tuva_health.*` succeeds
- [ ] All connector models have documentation

---

### M6: v0.7.0 - Clinical Analytics

**Target**: Week 7-8

**Scope**: Epic E8

**Deliverables**:

- Chronic conditions mart enabled
- ED classification mart enabled
- Readmissions mart enabled
- Data quality reports generated

**Success Metrics**:

- [ ] Chronic condition groupings for 1,172 patients
- [ ] ED visits properly classified
- [ ] 30-day readmission rates calculated
- [ ] Data quality >95% pass rate

---

### M7: v0.8.0 - Claims Ready

**Target**: Week 9-10

**Scope**: Epics E9 + E10

**Deliverables**:

- CMS SynPUF data acquired and loaded
- Claims staging models created
- Claims connector models built
- Claims input layer validated

**Success Metrics**:

- [ ] 2M beneficiary records loaded
- [ ] Medical claims accessible via source()
- [ ] Pharmacy claims accessible via source()
- [ ] Tuva claims validation passes

---

### M8: v1.0.0 - Full Analytics Platform

**Target**: Week 11-12

**Scope**: Epic E11

**Deliverables**:

- Financial PMPM mart enabled
- CMS-HCC risk scores calculated
- Complete healthcare analytics platform
- Project at v1.0 milestone

**Success Metrics**:

- [ ] PMPM metrics by service category
- [ ] HCC risk adjustment scores generated
- [ ] Full Tuva mart suite operational
- [ ] Project documented as v1.0 complete

---

## Dependency Graph

```text
E1 Environment Setup
    |
    v
E2 Data Acquisition
    |
    v
E3 Staging Layer
    |
    v
E4 Dimensional Models
    |
    +-------------+
    v             v
E5 Testing    E6 MCP Integration
    |             |
    +------+------+
           v
      v0.5.0 Complete
           |
           v
    E12 Semantic Layer
           |
      v0.5.5 Complete
           |
           v
    E7 Tuva Foundation
           |
           v
    E8 Clinical Marts
           |
      v0.7.0 Complete
           |
           v
    E9 Claims Acquisition
           |
           v
    E10 Claims Connector
           |
           v
    E11 Financial Marts
           |
           v
      v1.0.0 Complete
```

---

## Agent Team Assignments

### Primary Responsibilities

| Agent | Primary Areas | Epic Focus |
|-------|---------------|------------|
| **data-modeler** | Model design, naming, relationships, metric definitions | E3, E4, E7, E8, E10, E12 |
| **dbt-developer** | SQL implementation, Jinja, optimization | E1, E3, E4, E7, E8, E10, E11, E12 |
| **dbt-tester** | Schema tests, singular tests, freshness | E2, E3, E4, E5, E7, E8, E10, E11, E12 |
| **dbt-documenter** | Model docs, column descriptions, site | E3, E4, E5, E7, E8, E12 |
| **developer** | Environment, MCP, scripts, data download | E1, E2, E6, E9 |
| **architect** | Design decisions, technical direction | E1, E4, E7, E10, E12 |
| **code-reviewer** | Code quality, patterns, standards | E3, E4, E7 |
| **sage** | Learning extraction, pattern documentation | E6, E11 |

### Assembly Line for dbt Models

```text
For each model:

1. data-modeler  -> Design model (grain, columns, relationships)
2. dbt-developer -> Implement SQL with Jinja
3. dbt-tester    -> Add schema and singular tests
4. code-reviewer -> Review for patterns and quality
5. dbt-documenter -> Add descriptions and examples
```

---

## Risk Mitigation

| Risk | Mitigation | Owner |
|------|------------|-------|
| Synthea Java dependency | Provide pre-generated CSV option | developer |
| DuckDB path issues | Document absolute path requirements | architect |
| MCP compatibility | Test early in E1, have fallback workflow | developer |
| Data quality issues | Validate CSVs before model development | dbt-tester |
| Scope creep | PRDs define clear boundaries per epic | pm (this role) |
| Tuva package conflicts | Test in isolation branch before merge | dbt-developer |
| Terminology mapping gaps | Use Tuva's built-in terminology seeds | data-modeler |
| Large observation table (299K rows) | Consider incremental materialization | architect |
| CMS SynPUF data size | Document storage requirements, subset if needed | developer |
| MetricFlow DuckDB limitations | Metric marts now; full semantic layer after warehouse migration | architect |

---

## Related Documentation

- [Implementation Plan](./DBT-PROJECT-INITIALIZATION.md) - Detailed technical plan
- [GitHub Issues](./GITHUB-ISSUES.md) - Actionable work items
- [Architecture](../reference/ARCHITECTURE.md) - System design
- [Agent Guide](../../.claude/agents/AGENTS.md) - Agent orchestration
- [Tuva Integration Plan](./TUVA-INTEGRATION-PLAN.md) - Tuva package integration details
- [Semantic Layer PRD](../specs/PRD-012-SEMANTIC-LAYER.md) - Semantic layer requirements

---

*Last Updated: 2026-01-29*
*Status: Active Planning*
