# PRD-009: Claims Acquisition

## Overview

**Author**: pm: (Product Manager)
**Status**: Approved
**Created**: 2026-01-29
**Updated**: 2026-01-29
**Epic**: E9
**Version Target**: v0.8.0

### Problem Statement

Tuva's financial analytics (PMPM, cost analysis, HCC risk scores) require claims data. The current Synthea dataset is clinical-only. To unlock the full potential of the Tuva Project, we need to acquire synthetic claims data.

### Goal

Acquire and load CMS Synthetic Public Use Files (SynPUF) to provide medical claims, pharmacy claims, and eligibility data for financial analytics.

## User Stories

1. As a data engineer, I want claims data so that I can enable Tuva's financial analytics.
2. As a healthcare analyst, I want realistic Medicare claims so that I can learn claims analytics patterns.
3. As a learner, I want exposure to claims data structures so that I understand healthcare billing.

## Requirements

### Functional Requirements

1. **FR-1**: Download CMS SynPUF beneficiary summary files
2. **FR-2**: Download CMS SynPUF inpatient claims files
3. **FR-3**: Download CMS SynPUF outpatient claims files
4. **FR-4**: Download CMS SynPUF carrier claims files
5. **FR-5**: Download CMS SynPUF prescription drug event (PDE) files
6. **FR-6**: Load all files into DuckDB-accessible location
7. **FR-7**: Create source definitions for all claims tables

### Non-Functional Requirements

1. **NFR-1**: Data must be public domain (no licensing issues)
2. **NFR-2**: Storage requirements must be documented
3. **NFR-3**: Data loading must be reproducible via scripts

## Acceptance Criteria

- [ ] All SynPUF files downloaded and stored in `dbt_project/data/cms_synpuf/`
- [ ] DuckDB can read all CSV files via `read_csv_auto()`
- [ ] Source definitions created in `_cms_synpuf__sources.yml`
- [ ] Row counts verified against CMS documentation
- [ ] Data dictionary documented

## Scope

### In Scope

- CMS SynPUF Sample 1 (or subset if storage constrained)
- Beneficiary, inpatient, outpatient, carrier, and PDE files
- Source definitions and basic validation
- Download scripts for reproducibility

### Out of Scope

- Full 2M beneficiary dataset (use sample if storage limited)
- Claims connector models (see E10)
- Financial analytics (see E11)

## CMS SynPUF File Specifications

| File | Description | Rows (Sample 1) | Target Table |
|------|-------------|-----------------|--------------|
| Beneficiary Summary | Demographics, coverage | ~116K | `eligibility` input |
| Inpatient Claims | Hospital admissions | ~66K | `medical_claim` input |
| Outpatient Claims | Outpatient services | ~790K | `medical_claim` input |
| Carrier Claims | Physician services | ~2.8M | `medical_claim` input |
| PDE (Part D) | Prescription drugs | ~3.1M | `pharmacy_claim` input |

**Source**: [CMS SynPUF](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files)

## Data Storage Structure

```text
dbt_project/data/
├── synthea/                        # Existing clinical data
└── cms_synpuf/                     # NEW: Claims data
    ├── beneficiary_summary_2008.csv
    ├── beneficiary_summary_2009.csv
    ├── beneficiary_summary_2010.csv
    ├── inpatient_claims_2008.csv
    ├── inpatient_claims_2009.csv
    ├── outpatient_claims_2008.csv
    ├── outpatient_claims_2009.csv
    ├── carrier_claims_2008.csv
    ├── carrier_claims_2009.csv
    └── pde_2008.csv
```

## Dependencies

- E8 (Clinical Marts) - Should be validated before adding complexity
- Internet access for CMS data download
- Sufficient disk space (~2-5 GB for sample)

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Files downloaded | 100% | All specified files present |
| DuckDB accessibility | 100% | `read_csv_auto()` succeeds for all |
| Source definitions | Complete | All tables defined with tests |
| Data validation | Pass | Row counts match CMS specs |

## Alternative Data Sources

If CMS SynPUF is too large or complex, consider:

| Alternative | Size | Pros | Cons |
|-------------|------|------|------|
| Tuva Demo Data | 1K patients | Pre-formatted for Tuva | Small sample |
| OpenClaims | Varies | Community-maintained | Less realistic |
| Subset SynPUF | 10-20K beneficiaries | Manageable size | Manual subsetting |

## Open Questions

1. Should we use full SynPUF Sample 1 or create a smaller subset?
2. How do we handle multi-year beneficiary files?
3. Should we create a download/setup script for reproducibility?

## Related

- **TDD**: To be created by arch: agent
- **Issue**: See GITHUB-ISSUES.md
- **Dependency**: [PRD-008-CLINICAL-MARTS](./PRD-008-CLINICAL-MARTS.md)
