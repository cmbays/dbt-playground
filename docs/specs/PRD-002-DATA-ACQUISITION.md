---
title: Data Acquisition
prd_number: PRD-002
epic: E2-Data-Acquisition
version: 0.2.0
status: draft
author: pm
created: 2026-01-28
last_updated: 2026-01-28
---

## Overview

### Problem Statement

The dbt-playground requires realistic healthcare data to practice dimensional modeling and dbt development. Synthea generates synthetic patient data that mirrors real healthcare data structures without privacy concerns.

### Goal

Generate and load 500 synthetic patient records with associated healthcare encounters, conditions, medications, and other clinical data into the dbt project's data directory for use as source data.

### Success Metrics

- 9+ CSV files present in `dbt_project/data/synthea/`
- Each file readable by DuckDB via `read_csv_auto()`
- Data volume appropriate for learning (500 patients, ~5000+ encounters)
- Data integrity verified (no truncated files, correct column counts)

---

## Requirements

### Functional Requirements

#### FR-1: Synthea Data Generation

**Priority**: P0 (Critical)

Generate synthetic healthcare data using Synthea.

**Acceptance Criteria**:

- [ ] Synthea cloned or downloaded
- [ ] CSV export enabled in configuration
- [ ] 500 patients generated
- [ ] Output CSV files created successfully

**Generation Commands**:

```bash
# Option A: Clone and run Synthea
git clone https://github.com/synthetichealth/synthea.git /tmp/synthea
cd /tmp/synthea

# Enable CSV export (edit synthea.properties)
# Set: exporter.csv.export = true

# Generate 500 patients
./run_synthea -p 500 --exporter.csv.export true

# Output location: /tmp/synthea/output/csv/
```

#### FR-2: Alternative Data Source

**Priority**: P1 (High)

Provide fallback option if Synthea generation fails (Java dependency issues).

**Acceptance Criteria**:

- [ ] Pre-generated CSV sample available
- [ ] Download instructions documented
- [ ] Sample has same structure as generated data

**Fallback Options**:

1. Synthea sample datasets from GitHub releases
2. Pre-generated sample hosted in project releases
3. Reduced dataset (100 patients) for quick testing

#### FR-3: Data Directory Setup

**Priority**: P0 (Critical)

Copy generated CSV files to dbt project data directory.

**Acceptance Criteria**:

- [ ] `dbt_project/data/synthea/` directory created
- [ ] All required CSV files copied
- [ ] Files have appropriate permissions
- [ ] Directory added to `.gitignore`

**Required Files**:

| File | Description | Expected Rows (500 patients) |
|------|-------------|------------------------------|
| `patients.csv` | Patient demographics | ~500 |
| `encounters.csv` | Healthcare visits | ~5,000-10,000 |
| `conditions.csv` | Diagnoses | ~3,000-8,000 |
| `medications.csv` | Prescriptions | ~2,000-5,000 |
| `procedures.csv` | Medical procedures | ~1,000-3,000 |
| `observations.csv` | Vitals, lab results | ~50,000-100,000 |
| `providers.csv` | Healthcare providers | ~50-100 |
| `organizations.csv` | Healthcare facilities | ~10-30 |
| `payers.csv` | Insurance payers | ~10-20 |

#### FR-4: Data Verification

**Priority**: P0 (Critical)

Verify data integrity and structure.

**Acceptance Criteria**:

- [ ] All files have header rows
- [ ] Column counts match expected schema
- [ ] No truncated or corrupted files
- [ ] Files readable by DuckDB

**Verification Query**:

```sql
-- Verify patients.csv readable
SELECT COUNT(*) as row_count, *
FROM read_csv_auto('dbt_project/data/synthea/patients.csv')
LIMIT 5;

-- Verify all files
SELECT
  'patients' as table_name,
  COUNT(*) as rows
FROM read_csv_auto('dbt_project/data/synthea/patients.csv')
UNION ALL
SELECT 'encounters', COUNT(*)
FROM read_csv_auto('dbt_project/data/synthea/encounters.csv')
-- ... etc for all tables
```

#### FR-5: Data Exploration Script

**Priority**: P2 (Medium)

Create exploration queries for understanding data structure.

**Acceptance Criteria**:

- [ ] Script to show table schemas
- [ ] Script to show row counts
- [ ] Script to show sample data
- [ ] Basic statistics for key columns

---

### Non-Functional Requirements

#### NFR-1: Data Privacy

All data must be synthetic with no real patient information.

#### NFR-2: Data Size

Dataset should be small enough for fast iteration (500 patients, <100MB total).

#### NFR-3: Data Freshness

Generation date should be documented for reproducibility.

---

## User Stories

### US-1: Generate Fresh Data

**As a** developer
**I want** to generate fresh Synthea data
**So that** I have a known dataset for testing

**Acceptance Criteria**:

- Clear instructions for Synthea installation
- Commands documented for data generation
- Expected output files listed

### US-2: Use Pre-Generated Data

**As a** developer without Java installed
**I want** to use pre-generated sample data
**So that** I can skip Synthea setup

**Acceptance Criteria**:

- Download link provided
- Sample has same structure as generated
- Instructions for placing files

### US-3: Verify Data Quality

**As a** data engineer
**I want** to verify the data is complete
**So that** I can trust it for model development

**Acceptance Criteria**:

- Verification queries provided
- Expected row counts documented
- Data quality checks available

---

## Technical Specifications

### Synthea Data Schema

#### patients.csv

| Column | Type | Description |
|--------|------|-------------|
| Id | UUID | Unique patient identifier |
| BIRTHDATE | DATE | Date of birth |
| DEATHDATE | DATE | Date of death (if applicable) |
| SSN | STRING | Social security number |
| DRIVERS | STRING | Driver's license |
| PASSPORT | STRING | Passport number |
| PREFIX | STRING | Name prefix |
| FIRST | STRING | First name |
| LAST | STRING | Last name |
| SUFFIX | STRING | Name suffix |
| MAIDEN | STRING | Maiden name |
| MARITAL | STRING | Marital status |
| RACE | STRING | Race |
| ETHNICITY | STRING | Ethnicity |
| GENDER | STRING | Gender |
| BIRTHPLACE | STRING | Place of birth |
| ADDRESS | STRING | Street address |
| CITY | STRING | City |
| STATE | STRING | State |
| COUNTY | STRING | County |
| ZIP | STRING | ZIP code |
| LAT | FLOAT | Latitude |
| LON | FLOAT | Longitude |
| HEALTHCARE_EXPENSES | FLOAT | Total expenses |
| HEALTHCARE_COVERAGE | FLOAT | Total coverage |

#### encounters.csv

| Column | Type | Description |
|--------|------|-------------|
| Id | UUID | Unique encounter identifier |
| START | TIMESTAMP | Encounter start time |
| STOP | TIMESTAMP | Encounter end time |
| PATIENT | UUID | FK to patients.Id |
| ORGANIZATION | UUID | FK to organizations.Id |
| PROVIDER | UUID | FK to providers.Id |
| PAYER | UUID | FK to payers.Id |
| ENCOUNTERCLASS | STRING | Type (ambulatory, inpatient, etc.) |
| CODE | STRING | SNOMED code |
| DESCRIPTION | STRING | Encounter description |
| BASE_ENCOUNTER_COST | FLOAT | Base cost |
| TOTAL_CLAIM_COST | FLOAT | Total billed |
| PAYER_COVERAGE | FLOAT | Amount covered by payer |
| REASONCODE | STRING | Reason SNOMED code |
| REASONDESCRIPTION | STRING | Reason description |

*(Additional table schemas available in Synthea documentation)*

### Data Loading Strategy

DuckDB can read CSV files directly without loading:

```sql
-- Direct CSV query (no load step needed)
SELECT * FROM read_csv_auto('data/synthea/patients.csv');
```

For larger datasets, pre-load into DuckDB:

```python
import duckdb

con = duckdb.connect('dbt_project/dev.duckdb')

tables = ['patients', 'encounters', 'conditions', 'medications',
          'procedures', 'observations', 'providers', 'organizations', 'payers']

for table in tables:
    con.execute(f"""
        CREATE OR REPLACE TABLE raw_{table} AS
        SELECT * FROM read_csv_auto('data/synthea/{table}.csv')
    """)
    print(f"Loaded {table}")

con.close()
```

---

## Implementation Notes

### Prerequisites

- Java 11+ (for Synthea generation)
- 1GB+ disk space for generation
- dbt project initialized (from PRD-001)

### Generation Tips

1. **Memory**: Synthea may need `-Xmx4g` for 500+ patients
2. **Time**: Generation takes 5-15 minutes for 500 patients
3. **State**: Specify state for location data: `./run_synthea California -p 500`

### File Size Expectations

| File | Approximate Size |
|------|------------------|
| patients.csv | ~200KB |
| encounters.csv | ~2-5MB |
| conditions.csv | ~500KB-1MB |
| medications.csv | ~500KB-1MB |
| procedures.csv | ~200KB-500KB |
| observations.csv | ~20-50MB |
| providers.csv | ~20KB |
| organizations.csv | ~5KB |
| payers.csv | ~2KB |

---

## Agent Assignment

| Task | Agent | Notes |
|------|-------|-------|
| Synthea generation | developer | Java/CLI operations |
| Data copy/setup | developer | File system operations |
| Verification queries | dbt-tester | DuckDB query validation |
| Schema documentation | data-modeler | Understanding data structure |
| Exploration script | dbt-developer | Create analysis queries |

---

## Dependencies

### Upstream

- PRD-001: Environment Setup (dbt project must exist)

### Downstream

- PRD-003: Staging Layer (requires source data)

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Java not installed | Medium | Medium | Provide pre-generated sample |
| Synthea version incompatibility | Low | Low | Document tested version |
| Large file sizes | Low | Low | Limit to 500 patients |
| Corrupted CSV files | Medium | Low | Verification script |

---

## Open Questions

1. Should we commit a small sample dataset for quick-start?
2. What state should be used for Synthea generation (affects address data)?
3. Should we generate additional modules (immunizations, allergies)?

---

## References

- [Synthea Documentation](https://github.com/synthetichealth/synthea/wiki)
- [Synthea CSV Export](https://github.com/synthetichealth/synthea/wiki/CSV-File-Data-Dictionary)
- [DuckDB CSV Import](https://duckdb.org/docs/data/csv/overview)

---

*PRD Status: Draft - Ready for Review*
