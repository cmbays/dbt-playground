# PRD-007: Tuva Foundation

## Overview

**Author**: pm: (Product Manager)
**Status**: Approved
**Created**: 2026-01-29
**Updated**: 2026-01-29
**Epic**: E7
**Version Target**: v0.6.0

### Problem Statement

The dbt-playground project has 16 Synthea healthcare tables but lacks standardized healthcare analytics capabilities. Building custom analytics from scratch requires significant healthcare domain expertise and development time.

### Goal

Install the Tuva Project dbt package and build a connector layer that transforms Synthea staging models into Tuva's Clinical Input Layer format, enabling pre-built healthcare analytics.

## User Stories

1. As a data engineer, I want to leverage industry-standard healthcare data models so that I can build analytics faster.
2. As a data analyst, I want access to pre-built healthcare analytics so that I can answer clinical questions without building models from scratch.
3. As a learner, I want to understand how healthcare data platforms work so that I can apply these patterns in production environments.

## Requirements

### Functional Requirements

1. **FR-1**: Install `tuva-health/the_tuva_project` package version 0.15.3
2. **FR-2**: Create `stg_synthea__immunizations` staging model (required for Tuva)
3. **FR-3**: Build 10 connector models transforming staging to Tuva Input Layer
4. **FR-4**: Create seed files for terminology mappings (encounter types, LOINC codes)
5. **FR-5**: Configure dbt_project.yml with `clinical_input_enabled: true`
6. **FR-6**: Document all connector models and transformation logic

### Non-Functional Requirements

1. **NFR-1**: Package installation must not conflict with existing packages
2. **NFR-2**: Connector models must build in <60 seconds total
3. **NFR-3**: All models must follow project coding standards

## Acceptance Criteria

- [ ] `dbt deps` installs Tuva package without errors
- [ ] All 10 connector models compile and run successfully
- [ ] `dbt compile --select tuva_health.*` succeeds
- [ ] Schema tests pass for all connector models (unique, not_null on keys)
- [ ] Documentation exists for all connector models

## Scope

### In Scope

- Tuva package installation and configuration
- Clinical Input Layer connector models
- Immunizations staging model
- Encounter type mapping seed
- LOINC code categorization seed

### Out of Scope

- Claims Input Layer (no claims data yet - see E9/E10)
- Tuva data marts (see E8)
- Custom healthcare analytics beyond Tuva

## Connector Model Specifications

| Model | Source | Key Transformations |
|-------|--------|---------------------|
| `int_tuva__patient` | `stg_synthea__patients` | Gender code mapping (M/F to male/female), race code mapping |
| `int_tuva__encounter` | `stg_synthea__encounters` | Encounter class to type mapping |
| `int_tuva__condition` | `stg_synthea__conditions` | Add condition_status derivation |
| `int_tuva__procedure` | `stg_synthea__procedures` | Direct mapping (SNOMED aligned) |
| `int_tuva__medication` | `stg_synthea__medications` | Direct mapping (RxNorm aligned) |
| `int_tuva__observation` | `stg_synthea__observations` | Filter vitals by LOINC code |
| `int_tuva__lab_result` | `stg_synthea__observations` | Filter labs by LOINC code |
| `int_tuva__immunization` | `stg_synthea__immunizations` | Direct mapping (CVX aligned) |
| `int_tuva__practitioner` | `stg_synthea__providers` | Add placeholder NPI |
| `int_tuva__location` | `stg_synthea__organizations` | Map org to location |

## Dependencies

- E5 (Testing & Quality) - Must be complete before starting
- Tuva Project documentation - Reference for Input Layer schema
- Synthea staging models - Must exist for all source tables

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Package install success | 100% | `dbt deps` completes without errors |
| Model compile success | 10/10 models | `dbt compile --select tag:tuva_connector` |
| Test pass rate | 100% | `dbt test --select tag:tuva_connector` |
| Documentation coverage | 100% | All models have descriptions |

## Technical Design (for arch: TDD)

### File Structure

```text
dbt_project/
├── packages.yml                    # Add Tuva package
├── dbt_project.yml                 # Add clinical_input_enabled variable
├── seeds/
│   ├── tuva_mappings/
│   │   ├── encounter_type_mapping.csv
│   │   └── loinc_lab_codes.csv
└── models/
    ├── staging/synthea/
    │   └── stg_synthea__immunizations.sql   # NEW
    └── intermediate/
        └── tuva_connector/
            ├── _tuva_connector__models.yml
            └── int_tuva__*.sql               # 10 models
```

### Configuration Variables

```yaml
vars:
  clinical_input_enabled: true
  claims_input_enabled: false
  patient: "{{ ref('int_tuva__patient') }}"
  encounter: "{{ ref('int_tuva__encounter') }}"
  condition: "{{ ref('int_tuva__condition') }}"
  procedure: "{{ ref('int_tuva__procedure') }}"
  medication: "{{ ref('int_tuva__medication') }}"
  observation: "{{ ref('int_tuva__observation') }}"
  lab_result: "{{ ref('int_tuva__lab_result') }}"
  immunization: "{{ ref('int_tuva__immunization') }}"
  practitioner: "{{ ref('int_tuva__practitioner') }}"
  location: "{{ ref('int_tuva__location') }}"
```

## Open Questions

1. Should we use Tuva's built-in terminology seeds or create custom mappings?
2. What placeholder value should be used for missing NPI in providers?
3. Should observation/lab split use a seed file or hardcoded LOINC categories?

## Related

- **TDD**: [TDD-007-TUVA-FOUNDATION.md](./TDD-007-TUVA-FOUNDATION.md)
- **Issue**: See GITHUB-ISSUES.md
- **Integration Plan**: [TUVA-INTEGRATION-PLAN.md](../plans/TUVA-INTEGRATION-PLAN.md)
