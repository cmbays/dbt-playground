# QA Command

Run QA tests and produce QA_REPORT.md for deployment readiness.

## Usage

```
/qa [selector]
/qa --check
/qa --summary
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `selector` | No | dbt model selector (default: current feature models) |
| `--check` | No | Validate existing QA_REPORT.md without running tests |
| `--summary` | No | Show current QA status and adherence metrics |
| `--force` | No | Re-run even if report exists |
| `--no-sign-off` | No | Produce report but don't check sign-off box |

## Examples

### Run QA for Current Feature

```
/qa
```

Executes full QA workflow:

1. Determines feature from current branch
2. Runs `dbt build --select +{models}+`
3. Collects test results
4. Produces `temp/AGENT_REPORTS/{feature}/QA_REPORT.md`
5. Reports summary

Output:

```
╔══════════════════════════════════════╗
║           QA REPORT SUMMARY          ║
╚══════════════════════════════════════╝

Feature: customer-analytics
Branch: feat/customer-analytics

Test Results:
  ✓ dbt Build:     12 models OK
  ✓ Schema Tests:  45 passed, 0 failed
  ✓ Singular Tests: 3 passed, 0 failed

Issues Found: 0

Sign-off Status: ✓ Ready for deployment

Report: temp/AGENT_REPORTS/customer-analytics/QA_REPORT.md
```

### Run QA for Specific Models

```
/qa stg_patients+
```

Tests `stg_patients` and all downstream models:

```bash
dbt build --select stg_patients+
```

### Run QA with Upstream Dependencies

```
/qa +dim_customers
```

Tests `dim_customers` and all upstream dependencies:

```bash
dbt build --select +dim_customers
```

### Validate Existing Report

```
/qa --check
```

Validates QA_REPORT.md without running tests:

```
Checking QA Report: temp/AGENT_REPORTS/customer-analytics/QA_REPORT.md

Sections:
  ✓ Test Summary
  ✓ Test Execution
  ✓ Issues Found
  ✓ Sign-off

Sign-off Status: ✓ QA Complete checked

Result: VALID - Ready for VERIFY → DEPLOY transition
```

### Show QA Summary

```
/qa --summary
```

Shows current QA status and team adherence:

```
╔══════════════════════════════════════╗
║           QA STATUS SUMMARY          ║
╚══════════════════════════════════════╝

Current Feature: customer-analytics
QA Report: ✓ Exists, complete, signed off

Team Adherence:
  Total Transitions: 25
  With QA Report: 18 (72%)
  Skipped: 7 (28%)

Adherence Rate: 72%
Trend: ↑ Improving (+5% this week)

💡 Tip: Run /qa before requesting DEPLOY
```

## QA Workflow

### What /qa Does

```
[/qa invoked]
    │
    ├─ 1. Resolve feature name
    │   └─ Extract from branch: feat/X → X
    │
    ├─ 2. Determine test selector
    │   ├─ If argument provided: use as selector
    │   └─ If no argument: detect changed models
    │
    ├─ 3. Create AGENT_REPORTS folder
    │   └─ mkdir -p temp/AGENT_REPORTS/{feature}/
    │
    ├─ 4. Run dbt tests
    │   └─ dbt build --select {selector}
    │
    ├─ 5. Parse results
    │   └─ Extract pass/fail/skip counts
    │
    ├─ 6. Document issues
    │   └─ Record any failures with details
    │
    ├─ 7. Produce QA_REPORT.md
    │   └─ Use template, populate with results
    │
    ├─ 8. Determine sign-off
    │   ├─ All pass → Check "QA Complete"
    │   └─ Failures → Leave unchecked
    │
    └─ 9. Report summary to user
```

### QA Report Location

```
temp/AGENT_REPORTS/{feature}/QA_REPORT.md
```

Where `{feature}` is extracted from the branch name:

- `feat/customer-analytics` → `customer-analytics`
- `fix/null-handling` → `null-handling`

## Test Execution

### Default Selector Logic

When no selector is provided:

1. Get current branch name
2. Find models modified in this branch vs main
3. Build selector: `+{model1}+ +{model2}+`

### dbt Commands Used

| Scenario | Command |
|----------|---------|
| Full build + test | `dbt build --select {selector}` |
| Test only | `dbt test --select {selector}` |
| Downstream | `dbt build --select {model}+` |
| Upstream | `dbt build --select +{model}` |

## Output Files

### QA_REPORT.md

Created at: `temp/AGENT_REPORTS/{feature}/QA_REPORT.md`

Template: `docs/templates/agent-reports/QA_REPORT.md`

Contains:

- Test Summary (counts by category)
- Test Execution (commands and output)
- Issues Found (failures with details)
- Sign-off (checklist and approval)

### Metrics Log

Appended to: `temp/QA_METRICS_LOG.jsonl`

```json
{"timestamp": "2026-02-02T15:30:00Z", "feature": "customer-analytics", "event_type": "qa_completed", "passed": 48, "failed": 0}
```

## Flags Reference

| Flag | Description |
|------|-------------|
| `--check` | Validate existing report only |
| `--summary` | Show status and adherence metrics |
| `--force` | Re-run even if report exists |
| `--no-sign-off` | Produce report but don't check sign-off box |

## Integration

### With Supervisor

The Supervisor checks for QA_REPORT.md during VERIFY → DEPLOY transition:

```
super: Ready to deploy
→ Checking QA gate...
→ QA_REPORT.md found: ✓
→ Sign-off status: ✓ QA Complete
→ Proceeding to DEPLOY
```

### With qa-reviewer Persona

This command activates the **qa-reviewer** (`qa:`) persona for comprehensive QA orchestration.

### With Workflow State

QA results are recorded in WORKFLOW_STATE.md:

```yaml
### Track: feat/customer-analytics (ACTIVE)
- **QA Gate**:
  - **Status**: PASS
  - **Report**: temp/AGENT_REPORTS/customer-analytics/QA_REPORT.md
  - **Signed Off**: Yes
```

## Error Handling

### Test Failures

If tests fail, /qa still produces QA_REPORT.md but:

- Documents failures in "Issues Found" section
- Does NOT check "QA Complete" box
- Reports clear next steps

```
⚠️ QA completed with failures

Test Results:
  ✓ dbt Build:     12 models OK
  ✗ Schema Tests:  43 passed, 2 failed
  ✓ Singular Tests: 3 passed, 0 failed

Issues Found: 2
  1. [ERROR] not_null_stg_patients_patient_id (stg_patients)
  2. [ERROR] unique_dim_providers_provider_id (dim_providers)

Sign-off Status: ✗ Not ready for deployment

Next Steps:
  1. Fix failing tests
  2. Run /qa again
  3. Request VERIFY → DEPLOY when all pass
```

### Build Failures

If dbt build fails:

```
❌ QA blocked by build failure

Build Error:
  Model: int_patient_encounters
  Error: Compilation Error - column 'patient_id' does not exist

QA cannot proceed until build succeeds.

Next Steps:
  1. Fix the build error
  2. Run /qa again
```

## Quick Reference

| Command | Action |
|---------|--------|
| `/qa` | Full QA for current feature |
| `/qa model+` | QA specific model + downstream |
| `/qa --check` | Validate existing report |
| `/qa --summary` | Show adherence metrics |

## Related

- [[../agents/qa-reviewer.md]] - qa-reviewer persona
- [[../agents/supervisor.md]] - QA gate integration
- [[dbt-test.md]] - Add/run dbt tests
- [[dbt-run.md]] - Build models
