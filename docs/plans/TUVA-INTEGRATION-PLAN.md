# Tuva Project Integration Plan

**Created**: 2026-01-29
**Personas**: pm: (product research), arch: (architecture), dbt-model: (data modeling)
**Status**: APPROVED

---

## Executive Summary

The [Tuva Project](https://github.com/tuva-health/tuva) is an open-source dbt package for healthcare analytics that provides pre-built data marts, terminology sets, and 600+ data quality tests. It's an excellent fit for dbt-playground because:

1. **Synthea Compatibility**: Our 16 Synthea tables map well to Tuva's Clinical Input Layer
2. **DuckDB Support**: Tuva supports DuckDB (our adapter)
3. **Learning Value**: Exposes industry-standard healthcare analytics patterns
4. **Acceleration**: Provides chronic conditions, quality measures, and readmission analytics out-of-the-box

---

## Tuva Project Overview

### What It Provides

| Component | Description |
|-----------|-------------|
| **Input Layer** | Standardized API for claims and clinical data |
| **Core Data Model** | Unified healthcare data structure |
| **Data Marts** | Pre-built analytics (chronic conditions, quality measures, readmissions) |
| **Terminology Sets** | ICD-10, SNOMED, LOINC, RxNorm code sets |
| **Data Quality** | 600+ built-in validation tests |

### Data Marts (Clinical-Compatible)

| Data Mart | Works with Clinical Data? | Value |
|-----------|---------------------------|-------|
| **Chronic Conditions** | YES | 40+ condition groupings from diagnosis codes |
| **ED Classification** | YES | Emergency visit categorization |
| **Readmissions** | YES | 30-day hospital readmission rates |
| **Data Quality Intelligence** | YES | 600+ validation tests |
| **Quality Measures** | PARTIAL | Some HEDIS measures work |
| Financial PMPM | NO | Requires claims data |
| CMS-HCCs | NO | Requires claims data |

---

## Synthea to Tuva Mapping

### Table-Level Mapping

| Synthea Table | Tuva Input Table | Mapping Quality | Notes |
|---------------|------------------|-----------------|-------|
| `patients` | `patient` | HIGH | Minor gender/race code mapping |
| `encounters` | `encounter` | HIGH | Encounter class translation needed |
| `conditions` | `condition` | HIGH | SNOMED codes align |
| `procedures` | `procedure` | HIGH | SNOMED codes align |
| `medications` | `medication` | HIGH | RxNorm codes align |
| `observations` | `observation` | MEDIUM | Split vitals from labs |
| `observations` | `lab_result` | MEDIUM | Filter by LOINC code type |
| `immunizations` | `immunization` | HIGH | CVX codes align |
| `providers` | `practitioner` | HIGH | NPI not in Synthea |
| `organizations` | `location` | MEDIUM | Granularity difference |

### Tables Without Tuva Mapping

These Synthea tables have no Tuva equivalent (keep in staging for custom analytics):

- `allergies` (598 rows)
- `careplans` (3,484 rows)
- `devices` (79 rows)
- `imaging_studies` (856 rows)
- `payer_transitions` (3,802 rows)
- `supplies` (1 row)
- `payers` (11 rows)

### Key Transformation Requirements

1. **Add `stg_synthea__immunizations`** - Required for Tuva (defer to v0.6)
2. **Observation/Lab Split** - Filter `observations` by LOINC code to separate vitals from labs
3. **Encounter Type Mapping** - Synthea (`ambulatory`, `wellness`) to Tuva (`outpatient`, `inpatient`)
4. **Gender/Race Codes** - Map `M/F` to `male/female`, race codes to CDC standards
5. **Add `data_source` Column** - Constant 'synthea' for lineage tracking

---

## Recommended Architecture

### Connector Approach

```text
Synthea Raw Data (16 tables)
        |
        v
Synthea Staging Layer (stg_synthea__*)
        |
        v
Tuva Connector Layer (int_tuva__*)  <-- NEW: Transform to Tuva format
        |
        v
Tuva Input Layer refs
        |
        v
Tuva Data Marts (auto-generated)
```

### Why This Approach

1. **Preserves Existing Work** - Staging models remain unchanged
2. **Clean Separation** - Connector layer handles all Tuva-specific transforms
3. **Reusability** - Staging models still serve custom dimensional models (E4)
4. **Maintainability** - Tuva updates don't break staging layer

---

## Implementation Plan

### Phase 1: Tuva Foundation (v0.6)

**Scope**: Install Tuva package, build connector layer

```text
dbt_project/
├── packages.yml                    # Add tuva-health/the_tuva_project
├── dbt_project.yml                 # Add clinical_input_enabled: true
├── seeds/
│   ├── encounter_type_mapping.csv  # Synthea -> Tuva encounter types
│   └── loinc_lab_codes.csv         # LOINC codes for lab filtering
└── models/
    └── intermediate/
        └── tuva_connector/
            ├── _tuva_connector__models.yml
            ├── int_tuva__patient.sql
            ├── int_tuva__encounter.sql
            ├── int_tuva__condition.sql
            ├── int_tuva__procedure.sql
            ├── int_tuva__medication.sql
            ├── int_tuva__observation.sql
            ├── int_tuva__lab_result.sql
            ├── int_tuva__immunization.sql
            ├── int_tuva__practitioner.sql
            └── int_tuva__location.sql
```

**packages.yml Addition**:

```yaml
  - package: tuva-health/the_tuva_project
    version: 0.15.3
```

**dbt_project.yml Addition**:

```yaml
vars:
  clinical_input_enabled: true
  claims_input_enabled: false

  # Point Tuva to connector models
  patient: "{{ ref('int_tuva__patient') }}"
  encounter: "{{ ref('int_tuva__encounter') }}"
  condition: "{{ ref('int_tuva__condition') }}"
  # ... etc
```

### Phase 2: Clinical Marts (v0.7)

**Scope**: Enable and validate Tuva data marts

```yaml
vars:
  tuva_chronic_conditions_enabled: true
  ed_classification_enabled: true
  readmissions_enabled: true
  data_profiling_enabled: true
```

**Deliverables**:

- Chronic condition groupings for 1,172 patients
- ED visit classification for emergency encounters
- 30-day readmission analysis
- Data quality report with 600+ tests

### Phase 3: Claims Acquisition (v0.8)

**Scope**: Acquire claims data to unlock financial analytics

**Recommended Source**: CMS Synthetic Public Use Files (SynPUF)

- 2 million Medicare beneficiaries
- Inpatient, outpatient, carrier, and Part D claims
- Realistic distribution patterns from real Medicare data
- **Free and public domain**

### Phase 4: Claims Connector (v0.9)

**Scope**: Build connector for claims data

- `eligibility` table from beneficiary summary
- `medical_claim` from inpatient + outpatient + carrier claims
- `pharmacy_claim` from prescription drug events

### Phase 5: Financial Marts (v1.0)

**Scope**: Enable financial analytics

- PMPM (Per Member Per Month) cost analysis
- CMS-HCC risk adjustment scores
- Drug spend and adherence metrics

---

## Extended Roadmap

| Version | Epic | Focus |
|---------|------|-------|
| v0.3 | E3 | Staging (current plan - 9 models) |
| v0.4 | E4 | Dimensional Models (custom facts/dims) |
| v0.5 | E5+E6 | Testing & MCP Integration |
| **v0.6** | **E7** | **Tuva Foundation** (clinical connector) |
| **v0.7** | **E8** | **Clinical Marts** (chronic conditions, readmissions, ED) |
| **v0.8** | **E9** | **Claims Acquisition** (CMS SynPUF) |
| **v0.9** | **E10** | **Claims Connector** (eligibility, medical_claim, pharmacy_claim) |
| **v1.0** | **E11** | **Financial Marts** (PMPM, cost analysis, HCCs) |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| dbt version mismatch | Tuva requires 1.9.x+, we have 1.11.2 | Compatible - no action |
| Terminology mapping gaps | Some SNOMED codes may not map | Use Tuva's terminology seeds |
| Large observation table | 299K rows may slow builds | Consider incremental materialization |
| Learning curve | Tuva conventions differ from our patterns | Study Tuva docs, start with one mart |
| Package conflicts | May conflict with existing packages | Test in isolation branch first |

---

## Verification Plan

### Foundation Verification (v0.6)

```bash
# Install packages
dbt deps

# Build connector models
dbt build --select tag:tuva_connector

# Verify Tuva can read inputs
dbt compile --select tuva_health.*
```

### Marts Verification (v0.7)

```bash
# Build chronic conditions mart
dbt build --select +chronic_conditions

# Check condition groupings
dbt show --select chronic_conditions.chronic_conditions --limit 20

# Run data quality
dbt test --select tuva_health.*
```

---

## Sources

- [Tuva Project GitHub](https://github.com/tuva-health/tuva)
- [Tuva Documentation](https://thetuvaproject.com/getting-started/overview)
- [Tuva Input Layer](https://thetuvaproject.com/input-layer)
- [Tuva Data Marts](https://thetuvaproject.com/data-marts/overview)
- [Tuva dbt Hub](https://hub.getdbt.com/tuva-health/the_tuva_project/latest/)
- [Tuva Connector Template](https://github.com/tuva-health/connector_template)
- [CMS Synthetic PUF](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files)

---

*Approved: 2026-01-29*
