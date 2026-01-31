# Test Specification: [Feature Name]

**Feature**: [feature-name]
**Date**: YYYY-MM-DD
**Author**: Quality Tester

## Test Summary

| Category | Count | Coverage Target |
|----------|-------|-----------------|
| Schema Tests | N | 100% columns |
| Grain Tests | N | All fact tables |
| Referential Tests | N | All FKs |
| Data Quality | N | Key measures |

## Test Matrix

### Schema Tests

| Model | Column | Test | Expected |
|-------|--------|------|----------|
| [model] | [column] | unique | Pass |
| [model] | [column] | not_null | Pass |

### Grain Tests

| Model | Grain Columns | Test Type |
|-------|---------------|-----------|
| [fact] | [col1, col2] | unique_combination |

### Data Quality Tests

| Test Name | Description | Threshold |
|-----------|-------------|-----------|
| [test] | [what it validates] | [pass criteria] |

## Edge Cases Identified

- [edge case 1]: [how tested]
- [edge case 2]: [how tested]

## Test Commands

```bash
# Run all tests for this feature
dbt test --select tag:[feature-name]

# Run specific model tests
dbt test --select [model_name]
```

---

*For Developer: Read all upstream reports, then implement and create DEV_REPORT.md*
