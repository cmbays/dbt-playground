# PRD-010: Claims Connector

## Overview

**Author**: pm: (Product Manager)
**Status**: Approved
**Created**: 2026-01-29
**Updated**: 2026-01-29
**Epic**: E10
**Version Target**: v0.9.0

### Problem Statement

With CMS SynPUF claims data loaded, we need to transform it into Tuva's Claims Input Layer format. This requires staging models and connector models to map Medicare claims structures to Tuva's standardized schema.

### Goal

Build staging and connector models that transform CMS SynPUF data into Tuva's Claims Input Layer (eligibility, medical_claim, pharmacy_claim), enabling financial analytics.

## User Stories

1. As a data engineer, I want claims in Tuva format so that financial marts can run.
2. As a healthcare analyst, I want standardized claims data so that I can compare clinical and financial views.
3. As a learner, I want to understand claims transformation so that I can apply this to real data.

## Requirements

### Functional Requirements

1. **FR-1**: Create staging models for CMS SynPUF tables
2. **FR-2**: Build `int_tuva__eligibility` connector from beneficiary summary
3. **FR-3**: Build `int_tuva__medical_claim` connector from inpatient + outpatient + carrier
4. **FR-4**: Build `int_tuva__pharmacy_claim` connector from PDE
5. **FR-5**: Configure `claims_input_enabled: true`
6. **FR-6**: Pass Tuva's claims validation tests

### Non-Functional Requirements

1. **NFR-1**: Connector models must handle millions of rows efficiently
2. **NFR-2**: Transformations must be documented with business logic
3. **NFR-3**: All models must follow project coding standards

## Acceptance Criteria

- [ ] All staging models for SynPUF tables compile and run
- [ ] Eligibility connector produces valid member spans
- [ ] Medical claim connector unions inpatient + outpatient + carrier
- [ ] Pharmacy claim connector produces valid prescription records
- [ ] `dbt compile --select tuva_health.*` succeeds with claims enabled
- [ ] Tuva claims validation tests pass

## Scope

### In Scope

- Staging models for all SynPUF tables
- Three claims connector models (eligibility, medical_claim, pharmacy_claim)
- Configuration for claims input layer
- Claims-specific schema tests

### Out of Scope

- Financial data marts (see E11)
- Claims preprocessing configuration
- Custom claims analytics

## Staging Model Specifications

| Model | Source | Description |
|-------|--------|-------------|
| `stg_synpuf__beneficiary_summary` | beneficiary_summary_*.csv | Member demographics, coverage |
| `stg_synpuf__inpatient_claims` | inpatient_claims_*.csv | Hospital admissions |
| `stg_synpuf__outpatient_claims` | outpatient_claims_*.csv | Outpatient services |
| `stg_synpuf__carrier_claims` | carrier_claims_*.csv | Physician services |
| `stg_synpuf__pde` | pde_*.csv | Part D prescriptions |

## Connector Model Specifications

### int_tuva__eligibility

| Source Column | Target Column | Transformation |
|---------------|---------------|----------------|
| DESYNPUF_ID | person_id | Direct mapping |
| BENE_BIRTH_DT | birth_date | Date conversion |
| BENE_SEX_IDENT_CD | sex | 1='male', 2='female' |
| BENE_RACE_CD | race | CMS race code mapping |
| SP_STATE_CODE | state | State code lookup |
| BENE_HI_CVRAGE_TOT_MONS | enrollment_start/end | Derive spans |

### int_tuva__medical_claim

| Source | Key Mappings |
|--------|--------------|
| Inpatient | claim_type='institutional', ICD diagnosis/procedure codes |
| Outpatient | claim_type='institutional', ICD diagnosis/procedure codes |
| Carrier | claim_type='professional', HCPCS codes |

### int_tuva__pharmacy_claim

| Source Column | Target Column | Transformation |
|---------------|---------------|----------------|
| DESYNPUF_ID | person_id | Direct mapping |
| PDE_ID | claim_id | Direct mapping |
| SRVC_DT | dispensing_date | Date conversion |
| PROD_SRVC_ID | ndc_code | Direct mapping |
| QTY_DSPNSD_NUM | quantity | Direct mapping |
| DAYS_SUPLY_NUM | days_supply | Direct mapping |
| PTNT_PAY_AMT | paid_amount | Direct mapping |

## File Structure

```text
dbt_project/models/
├── staging/
│   └── cms_synpuf/
│       ├── _cms_synpuf__sources.yml
│       ├── _cms_synpuf__models.yml
│       ├── stg_synpuf__beneficiary_summary.sql
│       ├── stg_synpuf__inpatient_claims.sql
│       ├── stg_synpuf__outpatient_claims.sql
│       ├── stg_synpuf__carrier_claims.sql
│       └── stg_synpuf__pde.sql
└── intermediate/
    └── tuva_connector/
        ├── int_tuva__eligibility.sql      # NEW
        ├── int_tuva__medical_claim.sql    # NEW
        └── int_tuva__pharmacy_claim.sql   # NEW
```

## Dependencies

- E9 (Claims Acquisition) - SynPUF data must be loaded
- E7 (Tuva Foundation) - Clinical connector layer must exist
- Tuva documentation for claims input layer schema

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Staging model success | 5/5 models | All compile and run |
| Connector model success | 3/3 models | All compile and run |
| Tuva validation | Pass | Claims validation tests |
| Documentation | 100% | All models documented |

## Open Questions

1. How to handle multi-year beneficiary files (union vs. separate)?
2. Should carrier claims be split into header/line detail?
3. What default values for missing fields (e.g., rendering_npi)?

## Related

- **TDD**: To be created by arch: agent
- **Issue**: See GITHUB-ISSUES.md
- **Dependency**: [PRD-009-CLAIMS-ACQUISITION](./PRD-009-CLAIMS-ACQUISITION.md)
