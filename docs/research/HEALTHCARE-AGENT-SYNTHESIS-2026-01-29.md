# Healthcare Agent Synthesis Report

**Created**: 2026-01-29
**Author**: Sage (Knowledge Curator)
**Purpose**: Synthesis of research findings for healthcare-analyst agent persona

---

## Executive Summary

This report synthesizes research from three repositories to inform the design of a `healthcare-analyst` agent persona:

1. **tuva-health/the_tuva_project** - Healthcare dbt patterns, terminology handling
2. **affaan-m/everything-claude-code** - Claude Code agent patterns
3. **anthropics/courses** - Agent specialization patterns

The resulting `healthcare-analyst` agent serves as a domain expert consultant for healthcare data projects, providing terminology guidance, clinical data validation, and data enrichment strategies without directly writing code.

---

## Research Sources Summary

### 1. Tuva Project Findings

**Repository**: <https://github.com/tuva-health/the_tuva_project>

**Key Insights**:

| Finding | Application |
|---------|-------------|
| **Seed-based terminology** | ~40 terminology CSV files for ICD-10, SNOMED, LOINC, RxNorm, CPT, HCPCS |
| **Input Layer pattern** | Standardized connector layer separating source transforms from analytics |
| **code_type field** | Disambiguates code systems across multi-source data |
| **Clinical vs Claims paths** | Different handling for EHR vs payer data |
| **Value set groupings** | 40+ chronic condition categories via curated code sets |
| **600+ data quality tests** | Comprehensive validation patterns |

**Adopted for healthcare-analyst**:

- Complete terminology reference table (code systems, examples, update cadence)
- Clinical vs Claims data comparison matrix
- Data enrichment patterns (descriptions, groupings, crosswalks, reference data)
- External data source catalog

### 2. Everything-claude-code Findings

**Repository**: <https://github.com/affaan-m/everything-claude-code>

**Key Insights**:

| Finding | Application |
|---------|-------------|
| **YAML frontmatter** | Machine-parseable metadata for agent selection |
| **Red Flags sections** | Anti-patterns to watch for in the domain |
| **Handoff protocols** | Clear triggers, inputs, outputs, and handoff conditions |
| **Quality checklists** | Verification items before completing work |
| **Concrete code examples** | Good/bad patterns with visual indicators |

**Adopted for healthcare-analyst**:

- Standard frontmatter structure with tools and model preferences
- Healthcare-specific Red Flags (PHI in logs, code misalignment, etc.)
- Detailed handoff protocol to dbt-dev, dbt-model, dbt-test, semantic
- Domain-specific quality checklist

### 3. Anthropic Patterns Findings

**Repository**: <https://github.com/anthropics/courses>

**Key Insights**:

| Finding | Application |
|---------|-------------|
| **Clear role boundaries** | Explicit scope definition prevents overreach |
| **Tool minimization** | Grant only tools needed for the role |
| **Knowledge vs lookup** | Distinguish embedded knowledge from things to research |
| **Escalation paths** | Clear handoff for implementation and decisions |

**Adopted for healthcare-analyst**:

- Read-only tools (Read, Grep, Glob, WebSearch, WebFetch) - advisory role
- Explicit constraints ("Never write code", "Never make clinical decisions")
- Clear handoff table to implementation agents

---

## Agent Design Decisions

### Role Definition

The healthcare-analyst is a **domain consultant** rather than an **implementer**:

| Responsibility | healthcare-analyst | Implementation Agent |
|----------------|-------------------|---------------------|
| Terminology guidance | **Yes** | No |
| Clinical interpretation | **Yes** | No |
| Data enrichment strategy | **Yes** | No |
| Compliance awareness | **Yes** | No |
| Write SQL code | No | **dbt-developer** |
| Design models | No | **data-modeler** |
| Write tests | No | **dbt-tester** |
| Define metrics | No | **semantic-analyst** |

### Tool Selection

```yaml
tools: ["Read", "Grep", "Glob", "WebSearch", "WebFetch"]
```

**Rationale**:

- `Read`, `Grep`, `Glob`: Access existing codebase and documentation
- `WebSearch`, `WebFetch`: Research terminology updates, CMS guidelines, clinical standards
- **No Write/Edit**: Prevents code changes; advisory role only

### Model Selection

```yaml
model: opus
```

**Rationale**: Healthcare terminology reasoning requires:

- Complex code system relationships
- Nuanced clinical interpretation
- Regulatory compliance awareness
- Deep domain knowledge application

### Prefix Selection

```yaml
prefix: "hc:"
```

**Rationale**: Short, memorable, doesn't conflict with existing prefixes (dbt-model:, dbt-dev:, semantic:, etc.)

---

## Terminology Reference Design

The healthcare-analyst includes comprehensive terminology tables:

### Code Systems Table

| Code System | Full Name | Primary Use | Example |
|-------------|-----------|-------------|---------|
| ICD-10-CM | International Classification of Diseases 10th Rev | Diagnosis | E11.9 |
| SNOMED-CT | Systematized Nomenclature of Medicine | Clinical concepts | 73211009 |
| CPT | Current Procedural Terminology | Professional services | 99213 |
| HCPCS | Healthcare Common Procedure Coding System | Services/equipment | G0008 |
| LOINC | Logical Observation Identifiers Names and Codes | Labs/observations | 2339-0 |
| RxNorm | RxNorm Vocabulary | Drug ingredients | 1049502 |
| NDC | National Drug Codes | Drug packages | 00378-0515-01 |
| CVX | Vaccine Administered | Vaccine types | 140 |

### Update Cadence Table

| Terminology | Update Frequency | Effective Date |
|-------------|------------------|----------------|
| ICD-10-CM | Annual | October 1 |
| CPT | Annual | January 1 |
| RxNorm | Monthly | First Monday |
| LOINC | Semi-annual | June, December |

This enables the agent to answer questions like "When do ICD-10 codes update?" or "How often does RxNorm change?"

---

## Red Flags Design

Based on common healthcare data issues from Tuva patterns:

| Red Flag | Description | Consequence |
|----------|-------------|-------------|
| **PHI in Logs** | Patient identifiers in error messages | HIPAA violation risk |
| **Code System Misalignment** | Using SNOMED where ICD-10 expected | Join failures, incorrect results |
| **Missing Null Handling** | Not distinguishing unknown vs absent | Data quality issues |
| **Date Precision Loss** | Timestamps losing timezone/time | Temporal analysis errors |
| **Grain Confusion** | Mixing claim-line with claim-header | Aggregation errors |
| **Hardcoded Clinical Codes** | Codes in SQL, not terminology seeds | Maintenance burden |
| **Ignoring code_type** | Assuming single code system | Incorrect mappings |
| **Crosswalk Ambiguity** | One-to-many without disambiguation | Duplicate records |

---

## Integration with Existing Agents

### Assembly Line Position

```
Healthcare Analyst → Data Modeler → dbt Developer → dbt Tester → Code Reviewer → dbt Documenter
       ↓                  ↓              ↓              ↓              ↓              ↓
  Domain Context      Design SQL    Implement      Add tests      Review        Document
```

### Collaboration Patterns

| Collaborating Agent | healthcare-analyst Provides | healthcare-analyst Receives |
|---------------------|----------------------------|----------------------------|
| **data-modeler** | Terminology guidance, clinical grain definition | Model design questions |
| **dbt-developer** | Code validation, enrichment patterns | Implementation questions |
| **dbt-tester** | Clinical validation rules, data quality expectations | Test strategy questions |
| **semantic-analyst** | Healthcare metric definitions (PMPM, HCC) | Metric design questions |

---

## Future Enhancements

### Potential Additions

1. **FHIR Resource Guidance**: When FHIR data sources are added
2. **Claims Processing Rules**: Deeper CMS billing rules
3. **Risk Adjustment Details**: Expanded HCC/RAF score guidance
4. **Quality Measure Library**: Full HEDIS/NQF measure specifications

### Knowledge Expansion

As the project matures through Epics E7-E11, the healthcare-analyst's knowledge base should expand:

| Epic | New Knowledge Area |
|------|-------------------|
| E7 (Tuva Foundation) | Tuva connector patterns, input layer requirements |
| E8 (Clinical Marts) | Chronic condition groupings, ED classification |
| E9 (Claims Acquisition) | CMS SynPUF structure, Medicare data patterns |
| E10 (Claims Connector) | Claims preprocessing, eligibility handling |
| E11 (Financial Marts) | PMPM calculation, risk adjustment scoring |

---

## Validation Plan

### Test Scenarios

1. **Terminology Query**:
   - Input: `hc: What ICD-10 codes should we map for diabetes conditions?`
   - Expected: Reference to ICD-10 E10-E14 range, mention value sets, suggest Tuva chronic_conditions

2. **Data Enrichment Query**:
   - Input: `hc: How should we enrich patient data with demographic information?`
   - Expected: FIPS codes for geography, suggest reference seeds, mention PHI considerations

3. **Clinical Review Query**:
   - Input: `hc: Review the Tuva connector models for clinical accuracy`
   - Expected: Check code_type usage, validate field mappings, identify missing enrichments

4. **Data Source Query**:
   - Input: `hc: What external data sources would improve our claims analytics?`
   - Expected: NPI registry, CMS reference files, RxNorm updates, suggest acquisition approach

### Success Criteria

- [ ] Agent provides healthcare-specific guidance (not generic dbt advice)
- [ ] Agent correctly identifies terminology systems and their use cases
- [ ] Agent suggests appropriate data enrichment opportunities
- [ ] Agent hands off implementation work to appropriate agents
- [ ] Agent flags PHI/compliance concerns proactively

---

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `.claude/agents/healthcare-analyst.md` | **CREATE** | Full persona definition |
| `.claude/agents/AGENTS.md` | **EDIT** | Add to selection guide and assembly line |
| `docs/plans/ROADMAP.md` | **EDIT** | Add to agent assignments |
| `docs/research/HEALTHCARE-AGENT-SYNTHESIS-2026-01-29.md` | **CREATE** | This synthesis report |
| `temp/TUVA-RESEARCH-REPORT.md` | **REFERENCE** | Source for terminology patterns |

---

## Conclusion

The healthcare-analyst agent fills a critical gap in the agent ecosystem for healthcare data projects. By combining:

1. **Tuva's healthcare expertise** (terminology, clinical patterns)
2. **Everything-claude-code's agent patterns** (frontmatter, red flags, handoffs)
3. **Anthropic's specialization principles** (clear boundaries, tool minimization)

We've created an agent that provides domain expertise without overstepping into implementation, enabling better healthcare data modeling while maintaining clear separation of concerns.

---

*Synthesis completed: 2026-01-29*
*Ready for: Commit via git-master*
