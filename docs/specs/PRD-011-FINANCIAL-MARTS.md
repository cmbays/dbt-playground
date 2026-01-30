# PRD-011: Financial Marts

## Overview

**Author**: pm: (Product Manager)
**Status**: Approved
**Created**: 2026-01-29
**Updated**: 2026-01-29
**Epic**: E11
**Version Target**: v1.0.0

### Problem Statement

With both clinical and claims data flowing through Tuva's Input Layer, we can now enable the full suite of Tuva's financial analytics. This represents the culmination of the Tuva integration, delivering PMPM analysis, HCC risk scores, and comprehensive healthcare analytics.

### Goal

Enable Tuva's financial data marts to provide per-member-per-month cost analysis, CMS-HCC risk adjustment scores, and complete healthcare analytics capabilities, marking the project at v1.0.

## User Stories

1. As a healthcare analyst, I want PMPM metrics so that I can analyze cost by service category.
2. As a risk analyst, I want HCC scores so that I can understand population risk profiles.
3. As a data engineer, I want a complete analytics platform so that I can demonstrate full Tuva capabilities.
4. As a learner, I want financial analytics experience so that I can apply this in production environments.

## Requirements

### Functional Requirements

1. **FR-1**: Enable `financial_pmpm` data mart
2. **FR-2**: Enable `cms_hcc` (Hierarchical Condition Categories) data mart
3. **FR-3**: Enable `claims_preprocessing` for encounter grouping
4. **FR-4**: Validate PMPM calculations for correctness
5. **FR-5**: Validate HCC risk scores against expected ranges
6. **FR-6**: Document financial analytics use cases

### Non-Functional Requirements

1. **NFR-1**: Financial calculations must be accurate (verified against sample)
2. **NFR-2**: All marts must build without errors
3. **NFR-3**: Documentation must explain metric interpretation

## Acceptance Criteria

- [ ] Financial PMPM mart builds and calculates costs
- [ ] CMS-HCC mart generates risk adjustment factors
- [ ] Claims preprocessing groups claims into encounters
- [ ] PMPM by service category produces valid results
- [ ] HCC scores fall within expected ranges (0.5 - 5.0 RAF)
- [ ] Sample analytics queries documented and verified
- [ ] Project tagged as v1.0.0

## Scope

### In Scope

- Financial PMPM data mart
- CMS-HCC risk adjustment mart
- Claims preprocessing mart
- Financial analytics documentation
- v1.0 milestone completion

### Out of Scope

- Custom financial reports beyond Tuva
- Dashboard or visualization creation
- Integration with external BI tools

## Data Mart Specifications

### Financial PMPM

| Output | Description |
|--------|-------------|
| `pmpm_summary` | Overall PMPM by time period |
| `pmpm_by_service_category` | PMPM by inpatient, outpatient, professional, pharmacy |
| `pmpm_by_chronic_condition` | PMPM stratified by condition (with member month duplication note) |
| `member_months` | Monthly enrollment counts |

### CMS-HCC

| Output | Description |
|--------|-------------|
| `hcc_conditions` | HCC condition assignments per patient |
| `risk_scores` | RAF (Risk Adjustment Factor) by patient |
| `hcc_demographics` | Demographic factors for risk adjustment |

### Claims Preprocessing

| Output | Description |
|--------|-------------|
| `encounter` | Claims grouped into clinical encounters |
| `encounter_type_mapping` | 15 encounter type classifications |

## Configuration Variables

```yaml
vars:
  # Previously configured
  clinical_input_enabled: true
  claims_input_enabled: true

  # Enable financial marts
  pmpm_enabled: true
  cms_hcc_enabled: true
  claims_preprocessing_enabled: true
```

## Expected Analytics Outputs

### PMPM Analysis

- Total allowed/paid PMPM
- PMPM trends over time
- PMPM by service category
- High-cost member identification

### HCC Risk Scores

- Population-level RAF distribution
- Individual patient risk scores
- HCC condition prevalence
- Risk-stratified cohorts

### Sample Queries

```sql
-- Average PMPM by service category
select
    service_category,
    avg(paid_amount_pmpm) as avg_pmpm
from financial_pmpm.pmpm_by_service_category
group by 1
order by 2 desc;

-- HCC risk distribution
select
    case
        when raf < 1.0 then 'Low Risk'
        when raf < 2.0 then 'Medium Risk'
        else 'High Risk'
    end as risk_tier,
    count(*) as member_count
from cms_hcc.risk_scores
group by 1;
```

## Dependencies

- E10 (Claims Connector) - Claims must be in Tuva format
- E8 (Clinical Marts) - Clinical marts should be operational
- Complete Input Layer (clinical + claims)

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Mart build success | 3/3 marts | `dbt build` completes |
| PMPM calculation | Valid | PMPM values within expected ranges |
| HCC scores | Valid | RAF values between 0.5 - 5.0 |
| Documentation | Complete | Usage guide and sample queries |
| Milestone | v1.0.0 | Project tagged and released |

## v1.0 Milestone Checklist

- [ ] All Tuva clinical marts operational
- [ ] All Tuva financial marts operational
- [ ] Documentation complete
- [ ] CHANGELOG updated
- [ ] Git tag created (v1.0.0)
- [ ] CLAUDE.md updated to reflect completion

## Open Questions

1. What RAF range is expected for synthetic SynPUF data?
2. Should we create summary views for common analytics?
3. Are there specific financial metrics to highlight in documentation?

## Related

- **TDD**: To be created by arch: agent
- **Issue**: See GITHUB-ISSUES.md
- **Dependency**: [PRD-010-CLAIMS-CONNECTOR](./PRD-010-CLAIMS-CONNECTOR.md)
- **Integration Plan**: [TUVA-INTEGRATION-PLAN.md](../plans/TUVA-INTEGRATION-PLAN.md)
