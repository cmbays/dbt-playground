# PRD-008: Clinical Marts

## Overview

**Author**: pm: (Product Manager)
**Status**: Approved
**Created**: 2026-01-29
**Updated**: 2026-01-29
**Epic**: E8
**Version Target**: v0.7.0

### Problem Statement

With the Tuva connector layer in place, the project can leverage Tuva's pre-built clinical data marts. These marts provide industry-standard healthcare analytics that would take significant time to build from scratch.

### Goal

Enable and validate Tuva's clinical data marts to provide chronic condition groupings, ED visit classification, readmission analysis, and data quality intelligence for our Synthea patient population.

## User Stories

1. As a data analyst, I want chronic condition groupings so that I can analyze patient cohorts by disease.
2. As a healthcare analyst, I want ED classification so that I can understand emergency utilization patterns.
3. As a quality analyst, I want readmission metrics so that I can identify care quality issues.
4. As a data engineer, I want data quality reports so that I can validate data integrity.

## Requirements

### Functional Requirements

1. **FR-1**: Enable `tuva_chronic_conditions` data mart
2. **FR-2**: Enable `ed_classification` data mart
3. **FR-3**: Enable `readmissions` data mart
4. **FR-4**: Enable `data_profiling` data mart
5. **FR-5**: Validate analytics outputs for correctness
6. **FR-6**: Document mart usage and interpretation

### Non-Functional Requirements

1. **NFR-1**: Data marts must build without errors
2. **NFR-2**: Data quality test pass rate must exceed 95%
3. **NFR-3**: Chronic condition groupings must cover 100% of patients with conditions

## Acceptance Criteria

- [ ] Chronic conditions mart builds and populates groupings
- [ ] ED classification correctly categorizes emergency encounters
- [ ] Readmissions mart calculates 30-day readmission rates
- [ ] Data profiling generates quality report
- [ ] All enabled marts pass Tuva's built-in tests
- [ ] Sample analytics queries documented and verified

## Scope

### In Scope

- Enabling clinical-compatible data marts
- Validating mart outputs
- Documenting analytics use cases
- Creating sample queries

### Out of Scope

- Financial data marts (PMPM, HCCs) - require claims data
- Custom analytics beyond Tuva marts
- Dashboard or visualization creation

## Data Mart Specifications

| Mart | Configuration Variable | Key Outputs |
|------|------------------------|-------------|
| Chronic Conditions | `tuva_chronic_conditions_enabled: true` | ~40 condition groups per patient |
| ED Classification | `ed_classification_enabled: true` | ED visit categories (avoidable, etc.) |
| Readmissions | `readmissions_enabled: true` | 30-day readmission flags, rates |
| Data Profiling | `data_profiling_enabled: true` | 600+ data quality test results |

## Expected Analytics Outputs

### Chronic Conditions

- Patient-level condition groupings
- Condition prevalence by population
- Multi-morbidity analysis capability

### ED Classification

- ED visits categorized by acuity
- Potentially avoidable ED visits flagged
- ED utilization patterns

### Readmissions

- Index admissions identified
- 30-day readmission flags
- Readmission rates by condition

### Data Quality

- Field-level quality metrics
- Completeness scores
- Consistency validation

## Dependencies

- E7 (Tuva Foundation) - Connector layer must be complete
- Clinical data in Input Layer format
- Tuva package terminology seeds

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Mart build success | 4/4 marts | `dbt build` completes |
| Patient coverage | 100% | All patients with conditions have groupings |
| Data quality pass rate | >95% | Data profiling test results |
| Readmission calculation | Valid | Rates within expected ranges |

## Open Questions

1. What is the expected chronic condition distribution for synthetic data?
2. Should we create a summary dashboard for mart outputs?
3. Are there specific quality measures to prioritize?

## Related

- **TDD**: To be created by arch: agent
- **Issue**: See GITHUB-ISSUES.md
- **Dependency**: [PRD-007-TUVA-FOUNDATION](./PRD-007-TUVA-FOUNDATION.md)
