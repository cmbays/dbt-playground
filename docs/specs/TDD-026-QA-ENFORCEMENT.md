# TDD-024: QA & Testing Enforcement

**TDD Number**: TDD-024
**Title**: QA & Testing Enforcement Technical Design
**Status**: Draft
**Author**: Technical Architect
**Date**: 2026-02-01
**Related PRD**: PRD-024

---

## 1. Architecture Overview

### 1.1 System Context

```
                              Development Flow
                                     |
                                     v
    +-----------------+    +-----------------+    +-------------------+
    |  BUILD Stage    |    |  VERIFY Stage   |    |  REVIEW Stage     |
    |  (Developer)    |    |  (qa-reviewer)  |    |  (Code Reviewer)  |
    +-----------------+    +-----------------+    +-------------------+
           |                      |                       |
           v                      v                       v
    DEV_REPORT.md          QA_REPORT.md           CODE_REVIEW.md
           |                      |
           |              +-------+-------+
           |              |               |
           v              v               v
    PostToolUse Hook   dbt test      Stop Hook
    (auto-test)       execution     (validation)
```

### 1.2 Component Overview

| Component | Location | Purpose |
|-----------|----------|---------|
| QA_REPORT.md template | `docs/templates/agent-reports/` | Standardized verification artifact |
| qa-reviewer persona | `.claude/agents/qa-reviewer.md` | Dedicated verification agent |
| /qa command | `.claude/commands/qa.md` | Command shortcut |
| PostToolUse hook | `.claude/hooks/post-edit-check.js` | Auto-test on file edit |
| Stop hook | `.claude/hooks/pre-stop-check.js` | Pre-commit validation |
| Supervisor gate | `.claude/agents/supervisor.md` | Phase transition enforcement |

---

## 2. Hook Configuration Design

### 2.1 hooks.json Structure

The existing hooks.json structure remains unchanged. We enhance the JavaScript handlers:

```json
{
  "$schema": "https://claude.ai/schemas/hooks.json",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/post-edit-check.js \"$TOOL_INPUT\" \"$TOOL_OUTPUT\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/pre-stop-check.js"
          }
        ]
      }
    ]
  }
}
```

### 2.2 Configuration Constants

Add configuration section to hook files:

```javascript
// .claude/hooks/dbt-test-config.js (shared configuration)
const DBT_TEST_CONFIG = {
  // PostToolUse settings
  postToolUse: {
    enabled: true,
    layers: ['marts'],                    // Which layers trigger tests
    timeout: 60000,                       // 60 seconds
    skipPattern: /^--\s*no-auto-test/m,   // SQL comment pattern
    skipPatternYaml: /^#\s*no-auto-test/m, // YAML comment pattern
    excludePaths: [
      '/tests/',
      '_sources.yml',
      '/snapshots/'
    ]
  },

  // Stop hook settings
  stopHook: {
    enabled: true,
    runParse: true,
    runTest: true,
    parseTimeout: 30000,   // 30 seconds
    testTimeout: 120000,   // 120 seconds
    dbtProjectPath: 'dbt_project'
  },

  // Output prefixes
  output: {
    hookPrefix: '[HOOK]',
    warningPrefix: '[HOOK WARNING]',
    errorPrefix: '[HOOK ERROR]',
    notePrefix: '[HOOK NOTE]'
  }
};

module.exports = DBT_TEST_CONFIG;
```

---

## 3. qa-reviewer Persona Definition

### 3.1 Persona File Structure

```markdown
---
name: qa-reviewer
prefix: "qa:"
description: Test execution, verification gate, QA_REPORT.md creation
tools: ["Read", "Bash", "Grep", "Glob"]
model: opus
---

# QA Reviewer Persona

## Role Summary

The QA Reviewer executes tests, verifies implementations, and creates QA_REPORT.md
to unblock code review. Unlike dbt-tester (who creates tests), the QA Reviewer
executes tests and validates results.

## Core Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Test Execution | Run `dbt test` and `dbt build` commands |
| Result Verification | Verify all tests pass before code review |
| Regression Check | Check for failures in unrelated models |
| Artifact Creation | Create QA_REPORT.md artifact |
| Failure Coordination | Work with Developer to resolve failures |
| Gate Enforcement | Block transition if tests fail |

## Distinction from dbt-tester

| QA Reviewer (qa:) | dbt-tester (dbt-test:) |
|-------------------|------------------------|
| Executes tests | Creates tests |
| Verifies results | Designs test coverage |
| Creates QA_REPORT.md | Creates TEST_SPEC.md |
| Blocks on failures | Documents test plan |
| Runs after development | Runs before development |

## Workflow Position

```

Developer ──> QA Reviewer ──> Code Reviewer
              Creates         Reviews code
              QA_REPORT.md    quality

```

## Standard Workflow

### 1. Receive Feature for Verification

```

qa: verify tests for [feature-name]

```

### 2. Read Upstream Reports

- Read DEV_REPORT.md for implementation summary
- Read TEST_SPEC.md for expected test coverage
- Identify models to test

### 3. Execute Tests

```bash
# Run tests for feature models
dbt test --select tag:[feature-name]

# Or specific model selection
dbt test --select fct_encounters+

# Full build if needed
dbt build --select +[feature-name]+
```

### 4. Check for Regressions

```bash
# Run full test suite
dbt test

# Compare with expected test count
```

### 5. Create QA_REPORT.md

Write to: `temp/AGENT_REPORTS/[feature-name]/QA_REPORT.md`

### 6. Provide Verdict

- APPROVED: All tests pass, proceed to review
- BLOCKED: Failures must be resolved

## Invocation Examples

```text
qa: verify tests for customer-analytics
qa: run full regression check
qa: create QA_REPORT.md for v0.8-phase5
qa: what's the test coverage for fct_encounters?
```

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/qa` | Default verification workflow |
| `/qa run [feature]` | Run tests for specific feature |
| `/qa regression` | Full regression check |
| `/qa report [feature]` | Create QA_REPORT.md |
| `/qa coverage [model]` | Check test coverage |

## Artifacts Produced

| Artifact | Location | When |
|----------|----------|------|
| QA_REPORT.md | `temp/AGENT_REPORTS/[feature]/` | Every verification |
| Test output | Embedded in QA_REPORT.md | Every verification |

## Quality Checklist

### Before Approval

- [ ] All feature tests pass
- [ ] No regressions in unrelated models
- [ ] Test coverage meets TEST_SPEC.md requirements
- [ ] Edge cases from TEST_SPEC.md verified
- [ ] dbt build completes without errors

### QA_REPORT.md Completeness

- [ ] Test execution summary filled
- [ ] dbt test output included
- [ ] Verification checklist completed
- [ ] Edge cases documented
- [ ] Regression check documented
- [ ] Verdict selected (APPROVED/BLOCKED)

## Constraints

- Do NOT create or modify tests (that's dbt-tester's role)
- Do NOT modify model code (that's Developer's role)
- Do NOT skip test execution
- Always document results in QA_REPORT.md
- Always check for regressions
- Block transition if any tests fail

## Coordination with Developer

When tests fail:

1. Document failures in QA_REPORT.md
2. Mark verdict as BLOCKED
3. Provide specific failure details:
   - Test name
   - Model involved
   - Error message
   - Suggested investigation

4. Hand back to Developer with:

   ```
   qa: BLOCKED - 3 test failures detected

   Failures:
   1. unique_fct_encounters_encounter_sk: 5 duplicates
   2. not_null_fct_encounters_patient_id: 12 nulls
   3. assert_encounter_timestamps_valid: 1 violation

   Action: Developer to investigate and fix.
   Re-run: qa: verify tests for [feature] after fixes.
   ```

```

### 3.2 Frontmatter Specification

```yaml
---
name: qa-reviewer
prefix: "qa:"
description: Test execution, verification gate, QA_REPORT.md creation
tools: ["Read", "Bash", "Grep", "Glob"]
model: opus
---
```

---

## 4. QA_REPORT.md Template Structure

### 4.1 Template File

Location: `docs/templates/agent-reports/QA_REPORT.md`

```markdown
# QA Report: [Feature Name]

**Feature**: [feature-name]
**Date**: YYYY-MM-DD
**Author**: QA Reviewer
**Status**: PENDING | APPROVED | BLOCKED

---

## Test Execution Summary

| Test Type | Passed | Failed | Warned | Skipped | Total |
|-----------|--------|--------|--------|---------|-------|
| Schema tests | 0 | 0 | 0 | 0 | 0 |
| Singular tests | 0 | 0 | 0 | 0 | 0 |
| dbt_expectations | 0 | 0 | 0 | 0 | 0 |
| **Total** | 0 | 0 | 0 | 0 | 0 |

**Test Pass Rate**: 0% (0/0)

---

## dbt Test Output

### Command Executed

```bash
dbt test --select tag:[feature-name]
```

### Execution Time

- Started: HH:MM:SS
- Completed: HH:MM:SS
- Duration: X.Xs

### Full Output

```
[Paste full dbt test output here]
```

---

## Verification Checklist

### Test Execution

- [ ] All schema tests pass
- [ ] All singular tests pass
- [ ] All dbt_expectations tests pass
- [ ] No warnings on critical models

### Build Verification

- [ ] `dbt build` completes without errors
- [ ] All models materialize correctly
- [ ] Row counts are reasonable

### Coverage Check

- [ ] TEST_SPEC.md requirements met
- [ ] Primary keys tested (unique + not_null)
- [ ] Foreign keys tested (relationships)
- [ ] Business rules validated

---

## Edge Cases Verified

Based on TEST_SPEC.md edge cases:

| Edge Case | Test Method | Result |
|-----------|-------------|--------|
| [edge case 1] | [how tested] | PASS/FAIL |
| [edge case 2] | [how tested] | PASS/FAIL |

---

## Regression Check

### Full Suite Execution

```bash
dbt test
```

### Results

- **Total Tests**: N
- **Passed**: N
- **Failed**: 0
- **Unrelated Failures**: 0

### Notes

[Any observations about test suite health]

---

## Verdict

Select one:

- [ ] **APPROVED** - All tests pass, ready for code review
- [ ] **BLOCKED** - Failures must be resolved (see below)

### If BLOCKED

**Failure Summary**:

| Test | Model | Error | Severity |
|------|-------|-------|----------|
| [test_name] | [model] | [error] | ERROR/WARN |

**Recommended Actions**:

1. [Action 1]
2. [Action 2]

**Hand-off**: Return to Developer for fixes.

---

## Notes

[Any additional observations, warnings, or follow-up items]

---

*QA Report generated by qa-reviewer*
*For Code Reviewer: Proceed with review if verdict is APPROVED*

```

### 4.2 Template Sections Explanation

| Section | Purpose | Required |
|---------|---------|----------|
| Test Execution Summary | Quick overview of results | Yes |
| dbt Test Output | Full command output for audit | Yes |
| Verification Checklist | Structured validation steps | Yes |
| Edge Cases Verified | TEST_SPEC.md traceability | Yes |
| Regression Check | Ensure no side effects | Yes |
| Verdict | Clear APPROVED/BLOCKED decision | Yes |
| Notes | Additional context | Optional |

---

## 5. Integration with Existing TEST_SPEC.md Workflow

### 5.1 Workflow Timeline

```

PLAN Stage                    BUILD Stage                   VERIFY Stage
    |                             |                             |
    v                             v                             v
dbt-tester                   Developer                    qa-reviewer
    |                             |                             |
    v                             v                             v
TEST_SPEC.md              Implementation              QA_REPORT.md
(test plan)                (code + tests)           (test execution)
    |                             |                             |
    |-------- References -------->|                             |
    |                             |-------- Verifies ---------->|

```

### 5.2 Artifact Relationship

| Artifact | Created By | Stage | Purpose |
|----------|------------|-------|---------|
| TEST_SPEC.md | dbt-tester | PLAN | Define what to test |
| DEV_REPORT.md | Developer | BUILD | Document implementation |
| QA_REPORT.md | qa-reviewer | VERIFY | Verify tests pass |

### 5.3 TEST_SPEC.md to QA_REPORT.md Traceability

qa-reviewer reads TEST_SPEC.md to verify:

1. **Test Coverage**: Are all tests in TEST_SPEC.md implemented?
2. **Edge Cases**: Are edge cases from TEST_SPEC.md verified?
3. **Test Categories**: Does test execution match planned categories?

Example verification in QA_REPORT.md:

```markdown
## Coverage Check

Per TEST_SPEC.md requirements:

| Requirement | Status |
|-------------|--------|
| Primary key unique + not_null | VERIFIED |
| Foreign key relationships | VERIFIED |
| Date range validation | VERIFIED |
| Business rule: no future dates | VERIFIED |
```

---

## 6. Implementation Sequence

### 6.1 Phase 1: Templates & Documentation (Days 1-2)

```
Step 1.1: Create QA_REPORT.md template
  File: docs/templates/agent-reports/QA_REPORT.md
  Content: Full template as specified in Section 4.1

Step 1.2: Update supervisor.md phase gates
  File: .claude/agents/supervisor.md
  Change: Add QA_REPORT.md to transition matrix

Step 1.3: Document QA workflow
  File: docs/reference/QA_WORKFLOW.md
  Content: Reference guide for QA enforcement
```

### 6.2 Phase 2: qa-reviewer Persona (Days 3-5)

```
Step 2.1: Create qa-reviewer persona
  File: .claude/agents/qa-reviewer.md
  Content: Full persona as specified in Section 3.1

Step 2.2: Create /qa command
  File: .claude/commands/qa.md
  Content: Command shortcut definition

Step 2.3: Update AGENTS.md
  File: .claude/agents/AGENTS.md
  Changes:
    - Add qa-reviewer to agent selection guide
    - Update assembly line workflows
    - Add QA workflow section

Step 2.4: Verify qa: prefix works
  Test: qa: hello
  Expected: qa-reviewer responds
```

### 6.3 Phase 3: Hook Enhancement (Days 6-9)

```
Step 3.1: Create shared configuration
  File: .claude/hooks/dbt-test-config.js
  Content: Configuration as specified in Section 2.2

Step 3.2: Enhance PostToolUse hook
  File: .claude/hooks/post-edit-check.js
  Changes:
    - Add dbt file detection
    - Add test execution logic
    - Add timeout handling
    - Add skip pattern detection

Step 3.3: Enhance Stop hook
  File: .claude/hooks/pre-stop-check.js
  Changes:
    - Add dbt file detection in git status
    - Add dbt parse execution
    - Add dbt test execution
    - Add timeout handling

Step 3.4: Test hooks
  Tests:
    - Edit marts SQL, verify test triggers
    - Add # no-auto-test, verify skip
    - Create uncommitted dbt file, stop session
    - Verify parse and test validation runs
```

### 6.4 Phase 4: Validation (Days 9-10)

```
Step 4.1: End-to-end workflow test
  Scenario: Full feature development with QA gate

Step 4.2: Performance validation
  Measure: PostToolUse overhead, Stop hook overhead

Step 4.3: Documentation updates
  Files:
    - CLAUDE.md (add QA workflow reference)
    - CHANGELOG.md (add v0.8 QA features)
    - docs/for_chris/QA_ENFORCEMENT_GUIDE.md (educational)
```

---

## 7. PostToolUse Hook Implementation

### 7.1 Enhanced post-edit-check.js

```javascript
#!/usr/bin/env node
/**
 * Post-Edit Hook: Quality checks after file modifications
 * Enhanced with dbt test triggering for QA enforcement
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const DBT_TEST_CONFIG = {
  enabled: true,
  layers: ['marts'],
  timeout: 60000,
  skipPatternSql: /^--\s*no-auto-test/m,
  skipPatternYaml: /^#\s*no-auto-test/m,
  excludePaths: ['/tests/', '_sources.yml', '/snapshots/'],
  dbtProjectPath: 'dbt_project'
};

const input = process.argv[2];
const output = process.argv[3];

try {
  const toolInput = JSON.parse(input || '{}');
  const filePath = toolInput.file_path || '';
  const fileName = path.basename(filePath);

  // === EXISTING CHECKS (JS/HTML files) ===
  if (filePath.match(/\.(js|html)$/)) {
    // Skip temp and test files
    if (!filePath.includes('/temp/') &&
        !filePath.includes('.test.') &&
        !filePath.includes('.spec.')) {

      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');

        // Check for console.log in JS files
        if (filePath.endsWith('.js')) {
          const consoleLogCount = (content.match(/console\.log/g) || []).length;
          if (consoleLogCount > 3) {
            console.error(`[HOOK NOTE] Found ${consoleLogCount} console.log statements in ${fileName}`);
          }
        }

        // Check for TODO/FIXME comments
        const todoCount = (content.match(/TODO|FIXME|HACK|XXX/g) || []).length;
        if (todoCount > 0) {
          console.error(`[HOOK NOTE] Found ${todoCount} TODO/FIXME comments in ${fileName}`);
        }
      }
    }
  }

  // === NEW: dbt AUTO-TEST LOGIC ===
  if (DBT_TEST_CONFIG.enabled &&
      filePath.includes(`/${DBT_TEST_CONFIG.dbtProjectPath}/`) &&
      (filePath.endsWith('.sql') || filePath.endsWith('.yml'))) {

    // Check exclude paths
    const isExcluded = DBT_TEST_CONFIG.excludePaths.some(
      excludePath => filePath.includes(excludePath)
    );

    if (!isExcluded) {
      // Check layer (only test configured layers)
      const isConfiguredLayer = DBT_TEST_CONFIG.layers.some(
        layer => filePath.includes(`/${layer}/`)
      );

      if (isConfiguredLayer) {
        // Check for skip pattern
        if (fs.existsSync(filePath)) {
          const content = fs.readFileSync(filePath, 'utf8');
          const skipPattern = filePath.endsWith('.sql')
            ? DBT_TEST_CONFIG.skipPatternSql
            : DBT_TEST_CONFIG.skipPatternYaml;

          if (skipPattern.test(content)) {
            console.error(`[HOOK NOTE] Skipping auto-test for ${fileName} (no-auto-test flag)`);
          } else {
            // Extract model name
            const modelName = path.basename(filePath, path.extname(filePath));

            // Skip YAML config files
            if (!modelName.startsWith('_')) {
              console.error(`[HOOK] Running dbt tests for ${modelName}...`);

              try {
                const startTime = Date.now();
                const testCmd = `cd ${DBT_TEST_CONFIG.dbtProjectPath} && uv run dbt test --select ${modelName}+`;

                const testOutput = execSync(testCmd, {
                  encoding: 'utf8',
                  timeout: DBT_TEST_CONFIG.timeout,
                  stdio: ['pipe', 'pipe', 'pipe']
                });

                const duration = ((Date.now() - startTime) / 1000).toFixed(1);

                // Count tests from output
                const passMatch = testOutput.match(/(\d+) of (\d+) PASS/);
                const testCount = passMatch ? passMatch[2] : 'N';

                if (testOutput.includes('ERROR') || testOutput.includes('FAIL')) {
                  console.error(`[HOOK WARNING] Test failures detected for ${modelName}`);
                  console.error(`Run \`dbt test --select ${modelName}+\` to see details.`);
                } else {
                  console.error(`[HOOK] Tests passed for ${modelName} (${testCount} tests, ${duration}s)`);
                }
              } catch (testError) {
                if (testError.killed) {
                  console.error(`[HOOK WARNING] Test timeout (${DBT_TEST_CONFIG.timeout/1000}s) for ${modelName}`);
                } else {
                  console.error(`[HOOK WARNING] Test execution failed for ${modelName}`);
                  console.error(`Run \`dbt test --select ${modelName}+\` manually.`);
                }
              }
            }
          }
        }
      }
    }
  }

  process.exit(0);
} catch (error) {
  console.error(`[HOOK ERROR] ${error.message}`);
  process.exit(0);  // Non-blocking
}
```

### 7.2 Key Implementation Details

| Feature | Implementation |
|---------|----------------|
| Layer filtering | Check if path includes `/marts/` |
| Skip pattern | Regex match at file start |
| Timeout | execSync timeout option |
| Model extraction | path.basename without extension |
| Test selection | `--select model+` for downstream |
| Non-blocking | Always exit 0 |

---

## 8. Stop Hook Implementation

### 8.1 Enhanced pre-stop-check.js

```javascript
#!/usr/bin/env node
/**
 * Pre-Stop Hook: Final checks before Claude stops working
 * Enhanced with dbt validation for uncommitted changes
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const DBT_STOP_CONFIG = {
  enabled: true,
  runParse: true,
  runTest: true,
  parseTimeout: 30000,
  testTimeout: 120000,
  dbtProjectPath: 'dbt_project'
};

try {
  // === EXISTING: Check for uncommitted changes ===
  let changedDbtFiles = [];

  try {
    const gitStatus = execSync('git status --porcelain', { encoding: 'utf8' });
    if (gitStatus.trim()) {
      const changedFiles = gitStatus.trim().split('\n');
      console.error(`[HOOK REMINDER] ${changedFiles.length} uncommitted changes detected`);

      // Filter for dbt files
      changedDbtFiles = changedFiles
        .map(line => line.substring(3).trim())  // Remove git status prefix
        .filter(f =>
          f.includes(DBT_STOP_CONFIG.dbtProjectPath) &&
          (f.endsWith('.sql') || f.endsWith('.yml'))
        );
    }
  } catch (e) {
    // Not a git repo or git not available
  }

  // === NEW: dbt VALIDATION FOR UNCOMMITTED FILES ===
  if (DBT_STOP_CONFIG.enabled && changedDbtFiles.length > 0) {
    console.error(`[HOOK] ${changedDbtFiles.length} uncommitted dbt files - running validation...`);

    // Step 1: Run dbt parse
    if (DBT_STOP_CONFIG.runParse) {
      try {
        execSync(`cd ${DBT_STOP_CONFIG.dbtProjectPath} && uv run dbt parse`, {
          encoding: 'utf8',
          timeout: DBT_STOP_CONFIG.parseTimeout,
          stdio: ['pipe', 'pipe', 'pipe']
        });
        console.error('[HOOK] dbt parse: OK');
      } catch (parseError) {
        console.error('[HOOK WARNING] dbt parse failed - models may have errors');
        console.error('Run `dbt parse` to see compilation errors.');
      }
    }

    // Step 2: Run dbt test on changed models
    if (DBT_STOP_CONFIG.runTest) {
      // Extract model names from changed SQL files
      const models = changedDbtFiles
        .filter(f => f.endsWith('.sql'))
        .map(f => path.basename(f, '.sql'))
        .filter(m => !m.startsWith('_'));  // Exclude YAML config files

      if (models.length > 0) {
        const selector = models.join(' ');
        try {
          const startTime = Date.now();
          const testOutput = execSync(
            `cd ${DBT_STOP_CONFIG.dbtProjectPath} && uv run dbt test --select ${selector}`,
            {
              encoding: 'utf8',
              timeout: DBT_STOP_CONFIG.testTimeout,
              stdio: ['pipe', 'pipe', 'pipe']
            }
          );

          const duration = ((Date.now() - startTime) / 1000).toFixed(1);

          // Count tests
          const passMatch = testOutput.match(/(\d+) of (\d+) PASS/);
          const testCount = passMatch ? passMatch[1] : '?';

          if (testOutput.includes('ERROR') || testOutput.includes('FAIL')) {
            console.error('[HOOK WARNING] Some tests failed. Review before committing.');
          } else {
            console.error(`[HOOK] dbt test: OK (${testCount} tests passed, ${duration}s)`);
          }
        } catch (testError) {
          if (testError.killed) {
            console.error(`[HOOK WARNING] Test timeout (${DBT_STOP_CONFIG.testTimeout/1000}s)`);
          } else {
            console.error('[HOOK WARNING] Some tests failed. Review before committing.');
          }
        }
      } else {
        console.error('[HOOK] No SQL models to test (only YAML changes)');
      }
    }
  }

  // === EXISTING: Check temp folder ===
  const tempDir = path.join(process.cwd(), 'temp');
  if (fs.existsSync(tempDir)) {
    const tempFiles = fs.readdirSync(tempDir).filter(f => !f.startsWith('.'));
    if (tempFiles.length > 0) {
      console.error(`[HOOK REMINDER] ${tempFiles.length} files in temp/ folder`);
      console.error('Review temp/ contents before ending session.');
    }
  }

  process.exit(0);
} catch (error) {
  console.error(`[HOOK ERROR] ${error.message}`);
  process.exit(0);  // Non-blocking
}
```

### 8.2 Key Implementation Details

| Feature | Implementation |
|---------|----------------|
| File detection | git status --porcelain filtered for dbt_project |
| Parse validation | dbt parse with 30s timeout |
| Test execution | dbt test --select with model names |
| Model extraction | basename from changed .sql files |
| Non-blocking | Always exit 0 |

---

## 9. Testing Strategy

### 9.1 Unit Tests

| Test | File | Scenario | Expected |
|------|------|----------|----------|
| PostToolUse skip | post-edit-check.js | File with # no-auto-test | Skip message, no test run |
| PostToolUse trigger | post-edit-check.js | Marts SQL file | Test execution, result message |
| PostToolUse exclude | post-edit-check.js | Tests directory file | No test run |
| PostToolUse timeout | post-edit-check.js | Large model | Timeout warning |
| Stop parse | pre-stop-check.js | Uncommitted SQL | Parse validation runs |
| Stop test | pre-stop-check.js | Uncommitted SQL | Test validation runs |
| Stop no dbt | pre-stop-check.js | No dbt changes | Skip dbt validation |

### 9.2 Integration Tests

| Test | Scenario | Steps | Expected |
|------|----------|-------|----------|
| Full QA workflow | Feature verification | 1. Complete implementation 2. Invoke qa: 3. Check QA_REPORT.md | QA_REPORT.md created |
| Supervisor gate | Missing QA_REPORT | 1. Request review 2. No QA_REPORT.md | Transition blocked |
| PostToolUse integration | Edit marts model | 1. Edit fct_encounters.sql 2. Save | Tests run, result shown |
| Stop integration | End with uncommitted | 1. Edit SQL 2. Stop session | Parse + test validation |

### 9.3 Performance Tests

| Test | Measurement | Target |
|------|-------------|--------|
| PostToolUse overhead | Time from save to hook complete | <15s |
| Stop overhead | Time from stop to hook complete | <30s |
| Timeout behavior | Large model test | Timeout warning appears |

---

## 10. Error Handling

### 10.1 PostToolUse Error Scenarios

| Scenario | Handling | Output |
|----------|----------|--------|
| dbt not installed | Catch execSync error | `[HOOK WARNING] dbt not available` |
| Test timeout | Check error.killed | `[HOOK WARNING] Test timeout (60s)` |
| Test failure | Check output for FAIL | `[HOOK WARNING] Test failures detected` |
| File read error | Catch fs.readFileSync | `[HOOK ERROR] Cannot read file` |
| Parse error | Catch JSON.parse | `[HOOK ERROR] Invalid input` |

### 10.2 Stop Hook Error Scenarios

| Scenario | Handling | Output |
|----------|----------|--------|
| Not git repo | Catch execSync error | Silent skip |
| dbt parse fails | Catch error | `[HOOK WARNING] dbt parse failed` |
| dbt test fails | Catch error | `[HOOK WARNING] Some tests failed` |
| Timeout | Check error.killed | `[HOOK WARNING] Test timeout` |

### 10.3 Recovery Patterns

All hooks use non-blocking recovery:

```javascript
try {
  // Hook logic
} catch (error) {
  console.error(`[HOOK ERROR] ${error.message}`);
  process.exit(0);  // Always exit 0, never block
}
```

---

## 11. Future Enhancements

### 11.1 v0.9 Considerations

| Enhancement | Description |
|-------------|-------------|
| Config file | `.claude/hooks/config.json` for settings |
| Blocking mode | Optional `mode: blocking` for strict enforcement |
| Test caching | Skip re-test if file unchanged since last test |
| Parallel testing | Run tests in parallel for multiple models |

### 11.2 v1.0 Considerations

| Enhancement | Description |
|-------------|-------------|
| CI integration | GitHub Actions dbt test enforcement |
| Dashboard | Workflow Hub test status widget |
| Trend tracking | Historical test pass rates |
| Quarantine link | Auto-route failures to quarantine |

---

## 12. File Manifest

### 12.1 Files to Create

| File | Purpose |
|------|---------|
| `docs/templates/agent-reports/QA_REPORT.md` | QA report template |
| `.claude/agents/qa-reviewer.md` | qa-reviewer persona |
| `.claude/commands/qa.md` | /qa command shortcut |
| `docs/reference/QA_WORKFLOW.md` | Reference documentation |
| `docs/for_chris/QA_ENFORCEMENT_GUIDE.md` | Educational guide |

### 12.2 Files to Modify

| File | Changes |
|------|---------|
| `.claude/hooks/post-edit-check.js` | Add dbt test triggering |
| `.claude/hooks/pre-stop-check.js` | Add dbt validation |
| `.claude/agents/supervisor.md` | Add QA gate to phase matrix |
| `.claude/agents/AGENTS.md` | Add qa-reviewer, update workflows |
| `CLAUDE.md` | Add QA workflow reference |
| `CHANGELOG.md` | Add v0.8 QA features |

---

## 13. Appendix: /qa Command Definition

### 13.1 Command File

Location: `.claude/commands/qa.md`

```markdown
# /qa Command

Invoke the qa-reviewer agent for test verification.

## Usage

```

/qa                           # Default: run tests, create QA_REPORT.md
/qa run [feature-name]        # Run tests for specific feature
/qa regression                # Full regression check
/qa report [feature-name]     # Generate QA_REPORT.md only
/qa coverage [model-name]     # Check test coverage for model

```

## Default Behavior

When invoked without arguments, /qa:

1. Reads current feature from WORKFLOW_STATE.md
2. Runs `dbt test --select tag:[feature]` or infers models
3. Checks for regressions with `dbt test`
4. Creates QA_REPORT.md in temp/AGENT_REPORTS/[feature]/
5. Reports verdict (APPROVED/BLOCKED)

## Examples

```

/qa
> Running verification for feat/customer-analytics...
> Tests: 15 pass, 0 fail
> Regressions: 0
> QA_REPORT.md created: temp/AGENT_REPORTS/customer-analytics/QA_REPORT.md
> Verdict: APPROVED

/qa run order-metrics
> Running tests for order-metrics...
> Tests: 8 pass, 2 fail
> Verdict: BLOCKED - see failures below

/qa coverage fct_encounters
> Test coverage for fct_encounters:
>
> - Schema tests: 12
> - Singular tests: 2
> - dbt_expectations: 5
> Total: 19 tests
>
```

## Related

- qa-reviewer persona: `.claude/agents/qa-reviewer.md`
- QA_REPORT template: `docs/templates/agent-reports/QA_REPORT.md`
- Supervisor gates: `.claude/agents/supervisor.md`
```

---

*Document Status: Draft*
*Last Updated: 2026-02-01*
*For Developer: Implement in sequence per Section 6*
