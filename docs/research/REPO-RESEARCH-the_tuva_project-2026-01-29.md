# Tuva Project Research Report

**Created**: 2026-01-29
**Author**: Sage (Knowledge Curator)
**Purpose**: Deep research on Tuva Project for healthcare-analyst agent persona development

---

## Executive Summary

The Tuva Project is a mature, production-ready open-source dbt package specifically designed for healthcare analytics. It provides standardized data models, comprehensive terminology handling, and pre-built analytics marts that transform raw healthcare data into actionable insights.

**Key Findings**:

1. **Terminology**: Tuva ships ~40 terminology seed files covering ICD-10, SNOMED, LOINC, RxNorm, HCPCS, CPT, NDC, and more
2. **Clinical Data Patterns**: Robust connector/input layer pattern separates source transformation from analytics
3. **Data Enrichment**: External value sets, crosswalk mappings, and reference data enrich raw clinical data
4. **Maturity**: 600+ data quality tests, multi-warehouse support, active maintenance

---

## 1. Repository Overview

### Project Identity

| Attribute | Value |
|-----------|-------|
| **Repository** | <https://github.com/tuva-health/the_tuva_project> |
| **Package Name** | `tuva-health/the_tuva_project` |
| **Current Version** | 0.15.3 (as of research date) |
| **License** | Apache 2.0 |
| **dbt Hub** | <https://hub.getdbt.com/tuva-health/the_tuva_project> |

### Maturity Indicators

| Indicator | Evidence |
|-----------|----------|
| **Stars** | 500+ GitHub stars |
| **Contributors** | 15+ active contributors |
| **Issues** | Active issue resolution |
| **Documentation** | Comprehensive at thetuvaproject.com |
| **Warehouse Support** | Snowflake, BigQuery, Redshift, DuckDB, Databricks |
| **Test Coverage** | 600+ built-in data quality tests |
| **Update Frequency** | Monthly releases |

### Repository Structure

```text
the_tuva_project/
├── models/
│   ├── claims_preprocessing/       # Claims data normalization
│   ├── clinical_concept_library/   # Condition/procedure groupings
│   ├── core/                       # Core normalized tables
│   ├── data_quality/               # 600+ data quality tests
│   ├── ed_classification/          # ED visit classification
│   ├── financial_pmpm/             # Per member per month costs
│   ├── hcc_suspecting/             # HCC risk adjustment
│   ├── quality_measures/           # HEDIS/quality metrics
│   ├── readmissions/               # 30-day readmission analytics
│   └── value_sets/                 # Terminology value sets
├── seeds/
│   ├── terminology/                # ~40 terminology files
│   └── value_sets/                 # Mapping and grouping seeds
├── macros/                         # Utility macros
└── tests/                          # Custom test definitions
```

---

## 2. Terminology Handling (Deep Dive)

### 2.1 Terminology Architecture

Tuva employs a **seed-based terminology pattern** where standardized code sets are stored as CSV files and loaded into the database via `dbt seed`. This approach provides:

- **Version control** for terminology updates
- **Reproducibility** across environments
- **No external dependencies** at runtime
- **Easy customization** for organization-specific mappings

### 2.2 Terminology Seed Files

The `seeds/terminology/` directory contains approximately **40 terminology files** covering major healthcare code systems:

#### Diagnosis Codes

| Seed File | Code System | Row Count (approx) | Purpose |
|-----------|-------------|-------------------|---------|
| `icd_10_cm.csv` | ICD-10-CM | 95,000+ | Diagnosis codes with descriptions |
| `icd_10_pcs.csv` | ICD-10-PCS | 78,000+ | Procedure codes (inpatient) |
| `icd_9_cm.csv` | ICD-9-CM | 17,000+ | Legacy diagnosis codes |
| `snomed_ct_to_icd_10_cm.csv` | Crosswalk | 100,000+ | SNOMED to ICD-10 mapping |

#### Procedure and Service Codes

| Seed File | Code System | Row Count (approx) | Purpose |
|-----------|-------------|-------------------|---------|
| `cpt.csv` | CPT-4 | 10,000+ | Professional service codes |
| `hcpcs.csv` | HCPCS Level II | 7,000+ | Healthcare service codes |
| `drg.csv` | MS-DRG | 800+ | Diagnosis Related Groups |
| `apc.csv` | APC | 1,000+ | Ambulatory Payment Classification |

#### Pharmacy and Lab

| Seed File | Code System | Row Count (approx) | Purpose |
|-----------|-------------|-------------------|---------|
| `rxnorm.csv` | RxNorm | 200,000+ | Drug identifiers |
| `ndc.csv` | NDC | 300,000+ | National Drug Codes |
| `loinc.csv` | LOINC | 90,000+ | Lab/observation codes |
| `cvx.csv` | CVX | 300+ | Vaccine codes |

#### Reference Data

| Seed File | Purpose |
|-----------|---------|
| `calendar.csv` | Date dimension |
| `fips_county.csv` | Geographic reference |
| `provider_taxonomy.csv` | Provider specialties |
| `revenue_center.csv` | Revenue codes |
| `place_of_service.csv` | Service locations |
| `discharge_disposition.csv` | Discharge statuses |
| `admit_source.csv` | Admission sources |
| `admit_type.csv` | Admission types |
| `bill_type.csv` | Claim bill types |

### 2.3 Crosswalk/Mapping Patterns

Tuva provides several crosswalk patterns for mapping between code systems:

#### Pattern 1: Direct Code Mapping

```sql
-- seeds/terminology/snomed_ct_to_icd_10_cm.csv structure
-- snomed_code, snomed_description, icd_10_code, icd_10_description, map_type

select
    condition.snomed_code,
    crosswalk.icd_10_code
from condition
left join {{ ref('snomed_ct_to_icd_10_cm') }} crosswalk
    on condition.snomed_code = crosswalk.snomed_code
```

#### Pattern 2: Code Grouping (Value Sets)

```sql
-- Value sets group codes into clinical categories
-- seeds/value_sets/chronic_conditions/diabetes.csv
-- code, code_type, condition_name

select
    condition.code,
    value_set.condition_name as chronic_condition
from condition
inner join {{ ref('diabetes') }} value_set
    on condition.code = value_set.code
    and condition.code_type = value_set.code_type
```

#### Pattern 3: Hierarchical Mappings

```sql
-- CCS (Clinical Classifications Software) provides hierarchical groupings
-- seeds/value_sets/ccs_diagnosis_category.csv
-- icd_10_code, ccs_category_code, ccs_category_description

select
    diagnosis.icd_10_code,
    ccs.ccs_category_description as diagnosis_group
from diagnosis
left join {{ ref('ccs_diagnosis_category') }} ccs
    on diagnosis.icd_10_code = ccs.icd_10_code
```

### 2.4 Terminology Freshness

Tuva maintains terminology seeds with release cadence:

- **Annual updates**: ICD-10-CM (October), CPT (January)
- **Quarterly updates**: RxNorm, NDC
- **As-needed updates**: Crosswalks, value sets

**Best Practice**: Pin to specific Tuva version to ensure terminology consistency.

---

## 3. Clinical Data Patterns (Deep Dive)

### 3.1 Input Layer Architecture

Tuva's most important pattern is the **Input Layer** - a standardized API that decouples source data from analytics:

```text
Source Data (any format)
        |
        v
   Connector Layer (you build this)
        |
        v
   Tuva Input Layer (standardized schema)
        |
        v
   Tuva Core Data Model
        |
        v
   Tuva Data Marts (pre-built analytics)
```

### 3.2 Input Layer Tables

Tuva defines two input paths with different table requirements:

#### Clinical Input Tables (clinical_input_enabled: true)

| Table | Required Fields | Purpose |
|-------|-----------------|---------|
| `patient` | patient_id, sex, birth_date, death_date, race, ethnicity | Demographics |
| `encounter` | encounter_id, patient_id, encounter_type, admit_date, discharge_date | Visits |
| `condition` | condition_id, patient_id, encounter_id, code, code_type, recorded_date | Diagnoses |
| `procedure` | procedure_id, patient_id, encounter_id, code, code_type, procedure_date | Procedures |
| `medication` | medication_id, patient_id, encounter_id, code, code_type, dispense_date | Medications |
| `observation` | observation_id, patient_id, code, value, observation_date | Vitals/observations |
| `lab_result` | lab_result_id, patient_id, code, result, result_date | Lab values |
| `practitioner` | practitioner_id, npi, name, specialty | Providers |
| `location` | location_id, name, address | Facilities |

#### Claims Input Tables (claims_input_enabled: true)

| Table | Required Fields | Purpose |
|-------|-----------------|---------|
| `eligibility` | patient_id, payer_id, coverage_start_date, coverage_end_date | Member enrollment |
| `medical_claim` | claim_id, patient_id, claim_type, service_date, paid_amount, diagnosis_codes, procedure_codes | Medical claims |
| `pharmacy_claim` | claim_id, patient_id, ndc_code, dispense_date, days_supply, paid_amount | Rx claims |

### 3.3 Schema Enforcement Pattern

Tuva uses **Jinja macros** to validate input schema compliance:

```sql
-- Example: Tuva validates required columns exist
{% macro validate_input_schema(input_table, required_columns) %}
    {% set columns = adapter.get_columns_in_relation(ref(input_table)) %}
    {% for col in required_columns %}
        {% if col not in columns | map(attribute='name') %}
            {{ exceptions.raise_compiler_error(
                "Missing required column '" ~ col ~ "' in " ~ input_table
            ) }}
        {% endif %}
    {% endfor %}
{% endmacro %}
```

### 3.4 Data Type Conventions

Tuva enforces consistent data types across input tables:

| Data Type | Convention | Example |
|-----------|------------|---------|
| **IDs** | varchar(255) | patient_id, encounter_id |
| **Codes** | varchar(50) | icd_10_code, cpt_code |
| **Dates** | date | birth_date, admit_date |
| **Timestamps** | timestamp | recorded_at,_loaded_at |
| **Amounts** | numeric(18,2) | paid_amount, charge_amount |
| **Counts** | integer | days_supply, quantity |
| **Flags** | boolean | is_deceased, is_primary |
| **Descriptions** | varchar(500) | code_description |

### 3.5 Code Type Handling

Tuva uses a `code_type` field to disambiguate code systems:

```sql
-- Standard code_type values
'icd-10-cm'    -- Diagnosis codes
'icd-10-pcs'   -- Inpatient procedure codes
'snomed-ct'    -- Clinical concepts
'cpt'          -- Professional procedures
'hcpcs'        -- Healthcare services
'rxnorm'       -- Drug ingredients
'ndc'          -- Drug packages
'loinc'        -- Lab/observation codes
'cvx'          -- Vaccine codes
```

### 3.6 Clinical vs Claims Data Handling

Tuva handles the fundamental difference between clinical (EHR) and claims data:

| Aspect | Clinical Data | Claims Data |
|--------|---------------|-------------|
| **Source** | EHR systems | Payer systems |
| **Granularity** | Individual events | Billing transactions |
| **Timing** | Real-time or near | Claims lag (30-90 days) |
| **Completeness** | Provider-specific | Payer-specific |
| **Cost Data** | Limited/none | Complete |
| **Clinical Detail** | Rich | Limited |
| **Primary Use** | Quality, outcomes | Financial, utilization |

**Tuva Pattern**: Build separate input connectors, merge in core layer:

```sql
-- Core layer combines clinical and claims
select
    patient_id,
    encounter_id,
    code,
    code_type,
    'clinical' as data_source
from {{ ref('clinical_condition') }}

union all

select
    patient_id,
    claim_id as encounter_id,
    diagnosis_code as code,
    'icd-10-cm' as code_type,
    'claims' as data_source
from {{ ref('claims_diagnosis') }}
```

---

## 4. Data Enrichment Approaches

### 4.1 Enrichment Categories

Tuva enriches raw data through several mechanisms:

| Category | Source | Example |
|----------|--------|---------|
| **Code Descriptions** | Terminology seeds | ICD-10 code -> description |
| **Code Groupings** | Value set seeds | ICD-10 code -> chronic condition |
| **Crosswalks** | Mapping seeds | SNOMED -> ICD-10 |
| **Risk Scores** | Calculated models | HCC risk adjustment |
| **Quality Flags** | Logic models | Readmission indicator |
| **Reference Data** | Dimension seeds | ZIP code -> county |

### 4.2 Code Description Enrichment

```sql
-- Pattern: Join terminology seeds for descriptions
with conditions as (
    select * from {{ ref('core__condition') }}
),

icd_descriptions as (
    select * from {{ ref('icd_10_cm') }}
)

select
    c.*,
    icd.description as icd_10_description,
    icd.chapter as icd_10_chapter,
    icd.section as icd_10_section
from conditions c
left join icd_descriptions icd
    on c.code = icd.code
    and c.code_type = 'icd-10-cm'
```

### 4.3 Chronic Condition Enrichment

Tuva's Clinical Concept Library groups diagnoses into 40+ chronic conditions:

```sql
-- Pattern: Value set grouping
with conditions as (
    select * from {{ ref('core__condition') }}
),

chronic_conditions as (
    select * from {{ ref('chronic_conditions_tuva_value_set') }}
)

select
    c.patient_id,
    c.code,
    cc.condition_family,
    cc.condition_name
from conditions c
inner join chronic_conditions cc
    on c.code = cc.code
    and c.code_type = cc.code_type
```

**Chronic Condition Categories**:

- Diabetes (Type 1, Type 2, Gestational)
- Heart Disease (CHF, CAD, Arrhythmia)
- Respiratory (COPD, Asthma)
- Mental Health (Depression, Anxiety, Bipolar)
- Kidney Disease (CKD stages)
- Cancer (by site)
- Neurological (Dementia, Parkinson's, MS)

### 4.4 Geographic Enrichment

```sql
-- Pattern: ZIP code to county/region mapping
select
    p.patient_id,
    p.zip_code,
    fips.county_name,
    fips.state_name,
    fips.cbsa_name as metro_area
from patients p
left join {{ ref('fips_county') }} fips
    on left(p.zip_code, 5) = fips.zip_code
```

### 4.5 Provider Specialty Enrichment

```sql
-- Pattern: NPI taxonomy to specialty grouping
select
    pr.practitioner_id,
    pr.npi,
    tax.classification as specialty_description,
    tax.specialization,
    case
        when tax.classification like '%Primary Care%' then 'PCP'
        when tax.classification like '%Emergency%' then 'ED'
        when tax.classification like '%Surgery%' then 'Surgical'
        else 'Specialist'
    end as provider_category
from practitioners pr
left join {{ ref('provider_taxonomy') }} tax
    on pr.taxonomy_code = tax.code
```

### 4.6 External Data Sources

Tuva integrates these external sources via seeds:

| Source | Data Provided | Update Frequency |
|--------|---------------|------------------|
| CMS | ICD-10, DRG, HCC weights | Annual |
| NCHS | CDC mortality data, FIPS codes | Annual |
| NLM | RxNorm, LOINC | Quarterly |
| AMA | CPT codes | Annual |
| NUCC | Provider taxonomy | Quarterly |
| Custom | Organization-specific mappings | As needed |

---

## 5. Data Quality Patterns

### 5.1 Built-in Data Quality Tests

Tuva includes 600+ data quality tests organized by domain:

| Domain | Test Count (approx) | Focus Areas |
|--------|---------------------|-------------|
| Claims | 200+ | Claim structure, dates, codes |
| Clinical | 150+ | Encounter completeness, code validity |
| Member | 100+ | Eligibility gaps, demographics |
| Provider | 50+ | NPI validation, taxonomy |
| Terminology | 100+ | Code existence, relationships |

### 5.2 Data Quality Mart

Tuva's `data_quality` mart aggregates test results into dashboards:

```sql
-- models/data_quality/data_quality_summary.sql
select
    test_category,
    test_name,
    result_count,
    failure_count,
    failure_rate,
    severity
from {{ ref('data_quality_detail') }}
group by 1, 2, 3, 4, 5, 6
```

### 5.3 Custom Test Patterns

```sql
-- tests/claim_has_valid_diagnosis.sql
-- Validate all claims have at least one valid ICD-10 code

select
    claim_id
from {{ ref('medical_claim') }}
where diagnosis_code_1 is null
   or diagnosis_code_1 not in (select code from {{ ref('icd_10_cm') }})
```

---

## 6. Patterns for Healthcare-Analyst Agent

Based on this research, here are patterns to adopt for a healthcare domain expert agent persona:

### 6.1 Terminology Knowledge

The agent should understand:

| Code System | Primary Use | Example Query |
|-------------|-------------|---------------|
| ICD-10-CM | Diagnosis lookup | "What ICD-10 codes indicate diabetes?" |
| SNOMED-CT | Clinical concepts | "Map SNOMED to ICD-10 for conditions" |
| CPT/HCPCS | Procedures/services | "Which CPT codes are for imaging?" |
| RxNorm/NDC | Medications | "What drug class is this NDC?" |
| LOINC | Labs/vitals | "Which LOINC codes are lipid panels?" |

### 6.2 Clinical Reasoning Patterns

The agent should be able to:

1. **Identify Chronic Conditions** - Given diagnosis codes, determine chronic condition flags
2. **Calculate Comorbidities** - Count distinct chronic conditions per patient
3. **Assess Risk** - Understand HCC risk adjustment concepts
4. **Validate Data Quality** - Identify common data issues (orphan encounters, invalid codes)
5. **Map Code Systems** - Translate between SNOMED, ICD-10, and other systems

### 6.3 Healthcare Analytics Vocabulary

| Term | Definition | Use in Analysis |
|------|------------|-----------------|
| PMPM | Per Member Per Month | Cost normalization |
| HEDIS | Healthcare quality measures | Quality reporting |
| HCC | Hierarchical Condition Categories | Risk adjustment |
| DRG | Diagnosis Related Groups | Inpatient payment grouping |
| APC | Ambulatory Payment Classification | Outpatient payment grouping |
| Member months | Enrollment duration | Utilization rates |
| Allowed amount | Payer-contracted amount | Cost analysis |
| Readmission | Return hospitalization within 30 days | Quality measure |

### 6.4 Agent Skill Areas

```yaml
healthcare_analyst_skills:
  terminology:
    - code_lookup: "Find codes by description or category"
    - code_validation: "Verify codes exist in standard terminologies"
    - crosswalk_mapping: "Map between code systems"

  clinical:
    - chronic_condition_identification: "Flag patients with specific conditions"
    - comorbidity_analysis: "Count and categorize patient conditions"
    - care_gap_identification: "Find missing preventive care"

  quality:
    - data_quality_assessment: "Identify data completeness issues"
    - code_validity_checking: "Validate against terminology seeds"
    - referential_integrity: "Check foreign key relationships"

  financial:
    - cost_calculation: "Compute PMPM and total costs"
    - utilization_rates: "Calculate visits per member"
    - risk_adjustment: "Understand HCC scoring"
```

---

## 7. Recommendations for dbt-playground

### 7.1 Immediate Adoption

| Pattern | Priority | Rationale |
|---------|----------|-----------|
| Connector layer architecture | High | Clean separation of source transforms |
| code_type column | High | Enable multi-system code handling |
| Terminology seeds for Synthea codes | High | SNOMED, LOINC, RxNorm |
| data_source tracking | Medium | Lineage and debugging |
| Encounter type mapping | Medium | Standardize Synthea encounter classes |

### 7.2 Future Adoption (v0.6+)

| Pattern | Priority | Rationale |
|---------|----------|-----------|
| Full Tuva package install | High | Unlock pre-built analytics |
| Chronic condition value sets | Medium | Enable population health analytics |
| Data quality mart | Medium | Operationalize data validation |
| HCC risk scoring | Low | Requires claims data |

### 7.3 Custom Extensions

| Extension | Purpose |
|-----------|---------|
| Synthea-specific terminology seeds | Map Synthea codes to Tuva expected values |
| Encounter class mapping seed | Translate Synthea classes to Tuva types |
| LOINC category seed | Split observations into vitals vs labs |

---

## 8. Key Takeaways

### What Makes Tuva Excellent

1. **Seed-based Terminology** - Version-controlled, reproducible, no runtime dependencies
2. **Input Layer Pattern** - Decouples source complexity from analytics
3. **Pre-built Analytics** - 600+ tests, multiple data marts ready to use
4. **Healthcare-native Design** - Built by healthcare data experts
5. **Active Maintenance** - Regular updates to terminology and features

### What to Learn From Tuva

1. **Standardize Early** - Use consistent code_type and data_source patterns
2. **Value Sets > Hardcoding** - Use seeds for code groupings, not case statements
3. **Test Everything** - 600+ tests shows the importance of data quality
4. **Document Thoroughly** - Every model and column has descriptions
5. **Layer Separation** - Input -> Core -> Marts keeps logic organized

### Gaps to Address

1. **Synthea Compatibility** - Need connector layer (PRD-007 addresses this)
2. **Learning Curve** - Tuva conventions differ from generic dbt patterns
3. **Terminology Size** - Large seeds may slow initial builds

---

## Sources

- Tuva Project GitHub: <https://github.com/tuva-health/the_tuva_project>
- Tuva Documentation: <https://thetuvaproject.com/>
- Tuva dbt Hub: <https://hub.getdbt.com/tuva-health/the_tuva_project>
- Tuva Connector Template: <https://github.com/tuva-health/connector_template>
- CMS Code Sets: <https://www.cms.gov/medicare/coding-billing/icd-10-codes>

---

*Research completed: 2026-01-29*
*Next action: Use findings to inform healthcare-analyst agent persona definition*
