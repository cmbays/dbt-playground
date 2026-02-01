# PRD-024: QA & Testing Enforcement

**PRD Number**: PRD-024
**Title**: QA & Testing Enforcement
**Status**: Draft
**Author**: Product Manager
**Date**: 2026-02-01
**Milestone**: v0.8

---

## 1. Problem Statement

### 1.1 Current State

The dbt-playground project has a mature testing framework (171+ tests) and sophisticated hooks infrastructure, but lacks systematic enforcement of test verification before code review. Current gaps include:

1. **No verification artifact**: TEST_SPEC.md is created before development (test plan), but no artifact captures actual test execution results after implementation.

2. **Manual test execution**: Developers must remember to run tests; no automated triggering on file edits.

3. **No pre-commit validation**: Sessions can end with failing tests in uncommitted changes, leading to broken commits.

4. **Unclear verification responsibility**: dbt-tester creates tests but no dedicated role verifies results before code review.

### 1.2 Impact

| Impact Area | Description |
|-------------|-------------|
| Quality Risk | PRs may reach review with failing tests |
| Audit Trail | No documentation of test execution before merge |
| Workflow Clarity | Unclear who is responsible for verification |
| Feedback Delay | Test failures discovered late in workflow |

### 1.3 Desired State

A systematic QA enforcement workflow that:

- Captures test results in a mandatory artifact (QA_REPORT.md)
- Provides a dedicated role for test verification (qa-reviewer)
- Triggers tests automatically on relevant file edits
- Validates test state before session end
- Maintains advisory (non-blocking) approach to preserve development flow

---

## 2. User Stories

### 2.1 Primary User Stories

**US-1: Developer Test Feedback**
> As a developer, I want immediate feedback when my dbt model edits break tests, so that I can fix issues while context is fresh.

**Acceptance Criteria**:

- [ ] Editing a SQL file in marts layer triggers test execution
- [ ] Test results appear within 15 seconds of edit
- [ ] Failures show clear message with suggested action
- [ ] I can skip auto-testing with a comment flag if needed

---

**US-2: QA Reviewer Verification**
> As a QA reviewer, I want a clear workflow for executing tests and documenting results, so that code reviewers have confidence the implementation works.

**Acceptance Criteria**:

- [ ] I can invoke qa: prefix to start verification
- [ ] Clear guidance on which tests to run
- [ ] QA_REPORT.md template captures all necessary information
- [ ] Verdict section clearly states APPROVED or BLOCKED

---

**US-3: Supervisor Gate Enforcement**
> As a workflow supervisor, I want to block code review until test verification is complete, so that no PR reaches review with unknown test status.

**Acceptance Criteria**:

- [ ] Developer -> Reviewer transition requires QA_REPORT.md
- [ ] Supervisor checks artifact exists before allowing transition
- [ ] Clear error message when artifact is missing
- [ ] Workflow cannot proceed without verification

---

**US-4: Pre-Commit Validation**
> As a developer, I want validation of my dbt changes before ending a session, so that I don't commit broken models.

**Acceptance Criteria**:

- [ ] Stop hook detects uncommitted dbt files
- [ ] Parse validation runs to catch compilation errors
- [ ] Test validation runs on changed models
- [ ] Warnings appear but do not block session end

---

### 2.2 Secondary User Stories

**US-5: Test Skip for WIP**
> As a developer working on incomplete features, I want to skip automatic testing for work-in-progress files, so that known failures don't distract me.

**Acceptance Criteria**:

- [ ] Adding `# no-auto-test` to file skips PostToolUse testing
- [ ] Skip pattern is documented
- [ ] File is still included in Stop hook validation

---

**US-6: Regression Detection**
> As a QA reviewer, I want to verify my changes don't break unrelated tests, so that I catch unexpected side effects.

**Acceptance Criteria**:

- [ ] QA_REPORT.md includes regression check section
- [ ] Guidance to run full test suite provided
- [ ] Unrelated test failures flagged for investigation

---

## 3. Functional Requirements

### 3.1 QA_REPORT.md Artifact

**FR-1.1**: System SHALL provide a QA_REPORT.md template in `docs/templates/agent-reports/`.

**FR-1.2**: QA_REPORT.md SHALL include the following sections:

- Test Execution Summary (table: type, passed, failed, skipped)
- dbt Test Output (command executed, full output)
- Verification Checklist
- Edge Cases Verified
- Regressions Checked
- Verdict (APPROVED or BLOCKED)
- Notes

**FR-1.3**: QA_REPORT.md SHALL be written to `temp/AGENT_REPORTS/[feature-name]/QA_REPORT.md`.

**FR-1.4**: Verdict section SHALL use checkbox format:

```markdown
## Verdict
- [ ] **APPROVED** - All tests pass, ready for code review
- [ ] **BLOCKED** - Failures must be resolved
```

---

### 3.2 qa-reviewer Persona

**FR-2.1**: System SHALL provide a qa-reviewer persona in `.claude/agents/qa-reviewer.md`.

**FR-2.2**: qa-reviewer SHALL be invocable via `qa:` prefix.

**FR-2.3**: qa-reviewer SHALL have access to tools: Read, Bash, Grep, Glob.

**FR-2.4**: qa-reviewer core responsibilities SHALL include:

- Execute `dbt test` and `dbt build` commands
- Verify all tests pass before code review
- Check for regressions in unrelated models
- Create QA_REPORT.md artifact
- Coordinate with Developer on failures

**FR-2.5**: qa-reviewer SHALL be distinct from dbt-tester:

| qa-reviewer | dbt-tester |
|-------------|------------|
| Executes tests | Creates tests |
| Creates QA_REPORT.md | Creates TEST_SPEC.md |
| Runs after development | Runs before development |

---

### 3.3 Supervisor Phase Gate

**FR-3.1**: Supervisor SHALL require QA_REPORT.md for Developer -> Reviewer transition.

**FR-3.2**: Supervisor SHALL block transition if QA_REPORT.md is missing.

**FR-3.3**: Supervisor SHALL check artifact exists by path: `temp/AGENT_REPORTS/[feature]/QA_REPORT.md`.

**FR-3.4**: Supervisor error message SHALL be actionable:

```
BLOCKED: QA_REPORT.md not found for [feature-name].
Action: Invoke qa: to run tests and create QA_REPORT.md
```

---

### 3.4 PostToolUse Test Hook

**FR-4.1**: PostToolUse hook SHALL trigger dbt tests when:

- File is in `/dbt_project/` directory
- File ends with `.sql` or `.yml`
- File is NOT in `/tests/` directory
- File is NOT `_sources.yml`
- File is in configured layer (default: marts)

**FR-4.2**: PostToolUse hook SHALL NOT trigger when:

- File contains `# no-auto-test` comment
- File is outside dbt_project
- File is a test file

**FR-4.3**: PostToolUse hook SHALL execute:

```bash
dbt test --select [model_name]+
```

**FR-4.4**: PostToolUse hook SHALL timeout after 60 seconds.

**FR-4.5**: PostToolUse hook SHALL output success message:

```
[HOOK] Tests passed for [model_name] (N tests)
```

**FR-4.6**: PostToolUse hook SHALL output warning on failure:

```
[HOOK WARNING] Test failures detected for [model_name]
Run `dbt test --select [model_name]+` to see details.
```

**FR-4.7**: PostToolUse hook SHALL exit 0 regardless of test result (advisory mode).

---

### 3.5 Stop Hook Validation

**FR-5.1**: Stop hook SHALL detect uncommitted dbt files via `git status --porcelain`.

**FR-5.2**: Stop hook SHALL filter for files in `dbt_project/` ending with `.sql` or `.yml`.

**FR-5.3**: Stop hook SHALL run `dbt parse` with 30-second timeout when dbt files detected.

**FR-5.4**: Stop hook SHALL run `dbt test --select [models]` with 120-second timeout.

**FR-5.5**: Stop hook SHALL output validation summary:

```
[HOOK] N uncommitted dbt files - running validation...
[HOOK] dbt parse: OK
[HOOK] dbt test: OK (M tests passed)
```

**FR-5.6**: Stop hook SHALL output warning on failure:

```
[HOOK WARNING] Some tests failed. Review before committing.
```

**FR-5.7**: Stop hook SHALL exit 0 regardless of validation result (advisory mode).

---

### 3.6 /qa Command

**FR-6.1**: System SHALL provide `/qa` command shortcut in `.claude/commands/qa.md`.

**FR-6.2**: /qa command SHALL support operations:

- `/qa` - Default: run tests for current feature, create QA_REPORT.md
- `/qa run [feature-name]` - Run tests for specific feature
- `/qa regression` - Check for regressions (full test suite)
- `/qa report [feature-name]` - Generate QA_REPORT.md only
- `/qa coverage [model-name]` - Check test coverage for model

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-1.1**: PostToolUse hook overhead SHALL be less than 15 seconds per edit.

**NFR-1.2**: Stop hook overhead SHALL be less than 30 seconds at session end.

**NFR-1.3**: Hook timeouts SHALL be configurable.

### 4.2 Reliability

**NFR-2.1**: Hooks SHALL NOT block operations under any circumstance.

**NFR-2.2**: Hooks SHALL handle execution errors gracefully (try/catch, exit 0).

**NFR-2.3**: Hooks SHALL function when dbt is unavailable (skip with warning).

### 4.3 Usability

**NFR-3.1**: Error messages SHALL be actionable (include suggested command).

**NFR-3.2**: Warning messages SHALL be distinguishable from errors.

**NFR-3.3**: Skip patterns SHALL be documented and easy to use.

### 4.4 Maintainability

**NFR-4.1**: Hook configuration SHALL be centralizable (future config file support).

**NFR-4.2**: Layer selection SHALL be configurable without code changes.

**NFR-4.3**: Timeout values SHALL be adjustable via constants.

### 4.5 Observability

**NFR-5.1**: All hook executions SHALL output to stderr with [HOOK] prefix.

**NFR-5.2**: Test execution time SHALL be included in success messages.

**NFR-5.3**: QA_REPORT.md SHALL include execution timestamps.

---

## 5. Acceptance Criteria

### 5.1 Must Have (P0)

- [ ] QA_REPORT.md template created with all required sections
- [ ] qa-reviewer persona operational with qa: prefix
- [ ] Supervisor blocks Developer -> Reviewer without QA_REPORT.md
- [ ] PostToolUse hook triggers tests for marts SQL files
- [ ] Stop hook validates uncommitted dbt files
- [ ] All hooks are non-blocking (exit 0)
- [ ] /qa command shortcut functional

### 5.2 Should Have (P1)

- [ ] Skip pattern (`# no-auto-test`) recognized
- [ ] Configurable timeout values
- [ ] Performance within specified limits
- [ ] Educational documentation created
- [ ] CHANGELOG updated

### 5.3 Nice to Have (P2)

- [ ] Layer selection configurable via config file
- [ ] Test result caching to reduce repeated executions
- [ ] Workflow Hub integration for QA status display

---

## 6. Out of Scope

### 6.1 Explicitly Excluded

| Item | Reason | Future Milestone |
|------|--------|------------------|
| CI test enforcement | Significant complexity | v0.9 |
| Blocking hook mode | Would disrupt workflow | v0.9 (optional) |
| Test result dashboard | Requires UI work | v0.9 |
| Great Expectations integration | Enterprise tooling | v1.0 |
| Automated quarantine from failures | Depends on Phase 5 | v0.9 |

### 6.2 Deferred Decisions

1. **CI PR blocking**: Whether failing tests should block PR merge (v0.9 decision)
2. **Hook configuration file**: Format and location of config.json (v0.9)
3. **Historical trend tracking**: How to store and visualize test trends (v0.9)

---

## 7. Dependencies

### 7.1 Technical Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| Hooks infrastructure (.claude/hooks/) | Operational | Low |
| dbt test suite (171+ tests) | Operational | Low |
| Agent reports pattern (temp/AGENT_REPORTS/) | Operational | Low |
| Supervisor phase gates | Operational | Low |

### 7.2 Workflow Dependencies

| Dependency | Description |
|------------|-------------|
| v0.7.0 completion | GitHub Project Management complete |
| Phase 5 (Quarantine) | QA workflow compatible with quarantine pattern |

---

## 8. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Hook slows development | Medium | Medium | Advisory mode, timeouts, skip patterns |
| Developer annoyance | Medium | Low | Clear documentation, easy skip |
| False positive warnings | Medium | Low | Selective layer testing, clear messages |
| Timeout on large suites | Medium | Low | Configurable timeout, model-specific testing |

---

## 9. Success Metrics

### 9.1 Adoption Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Features with QA_REPORT.md | 100% | Count artifacts per feature |
| qa-reviewer invocations | Tracked | Log qa: prefix usage |
| Skip pattern usage | <10% of files | Count # no-auto-test occurrences |

### 9.2 Quality Metrics

| Metric | Before | After Target |
|--------|--------|--------------|
| PRs with unknown test status | Unknown | 0% |
| Test failures caught pre-review | Delayed | Immediate |
| Regression detection | Manual | Automated |

### 9.3 Performance Metrics

| Metric | Target | Max Acceptable |
|--------|--------|----------------|
| PostToolUse overhead | 5-10s | 15s |
| Stop hook overhead | 10-20s | 30s |

---

## 10. User Experience

### 10.1 Developer Workflow

```
1. Developer completes implementation
2. Developer runs: dbt build --select [feature]+
3. Tests pass locally
4. Developer creates DEV_REPORT.md
5. Supervisor: "Ready for QA verification"
6. Developer invokes: qa: verify tests for [feature]
7. qa-reviewer runs tests, creates QA_REPORT.md
8. Supervisor: "QA_REPORT.md found, proceeding to code review"
9. Code reviewer receives PR with verified test status
```

### 10.2 Error Experience

**Missing QA_REPORT.md**:

```
super: Ready for code review

BLOCKED: QA_REPORT.md not found for feat/customer-analytics.

Next steps:
1. Run: qa: verify tests for customer-analytics
2. Ensure all tests pass
3. QA_REPORT.md will be created automatically
4. Resume: super: ready for code review
```

**Test Failure During Edit**:

```
[HOOK WARNING] Test failures detected for fct_encounters
Run `dbt test --select fct_encounters+` to see details.

Note: This is advisory only. Fix failures before committing.
```

---

## 11. Glossary

| Term | Definition |
|------|------------|
| QA_REPORT.md | Artifact documenting test execution results and verification status |
| qa-reviewer | Agent persona responsible for test verification |
| Advisory mode | Hooks warn but do not block operations |
| PostToolUse hook | Hook that executes after Write/Edit tool calls |
| Stop hook | Hook that executes when Claude session ends |
| Phase gate | Checkpoint where Supervisor verifies artifacts before transition |

---

## 12. References

- Research Report: `temp/2026_02_01_Discussion/qa_enforcement_report.md`
- Hooks Infrastructure: `.claude/hooks/hooks.json`
- Existing Agent Reports: `docs/templates/agent-reports/`
- Testing Standards: `docs/reference/DBT_TESTING_STANDARDS.md`
- Supervisor Workflow: `.claude/agents/supervisor.md`

---

## 13. Approval

| Role | Name | Date | Status |
|------|------|------|--------|
| Product Manager | - | 2026-02-01 | Draft |
| Technical Architect | - | - | Pending |
| Project Lead | - | - | Pending |

---

*Document Status: Draft*
*Last Updated: 2026-02-01*
