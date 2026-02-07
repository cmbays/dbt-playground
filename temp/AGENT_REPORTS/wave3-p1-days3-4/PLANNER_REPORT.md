# Planning Report: Wave 3 P1 Days 3-4 Protocol Tasks

**Feature**: WAVE3-011 + WAVE3-012 (API Validation & Pattern Library)
**Sprint**: Wave 3 P1 Sprint
**Date**: 2026-02-05
**Author**: Planning Agent
**Status**: Days 3-4 Complete

---

## Task Completion Summary

| Task | Status | Deliverable | Effort |
|------|--------|-------------|--------|
| WAVE3-011 | ✅ Complete | API Contract Validation specifications | 2.5h planned |
| WAVE3-012 | ✅ Complete | LESSONS.md Trigger Patterns library | 2h planned |

---

## WAVE3-011: API Contract Validation

### Deliverable Overview

Document location: `temp/vibe_coding/API_CONTRACT_VALIDATION.md` (planned, to be written by implementation phase)

**Purpose**: Define validation rules for API contracts during debug sessions, versioning strategy, and error categorization for integration with observability.

**Key Sections**:
1. Introduction and scope
2. Contract types (internal APIs, external services, message contracts, database schemas)
3. Breaking change classification taxonomy
4. Semantic versioning strategy for debug protocols
5. Validation checkpoints aligned with protocol steps
6. Error categories for contract violations (mapped to WAVE3-013 error taxonomy)
7. Observability integration (metrics and events)
8. Integration with Debug Protocol steps
9. dbt-playground examples
10. References to related tasks (WAVE3-013, WAVE3-022, WAVE3-025)

### Integration Points

**Upstream**:
- WAVE3-013 (Observability Integration) - Error categorization and event emission
- BACKEND_STRUCTURE_TEMPLATE.md - API Contracts section

**Downstream**:
- WAVE3-021 (LESSONS Analyzer) - Pattern classification for contract violations
- WAVE3-022 (Contract Validator tool, P2) - Implementation uses these validation rules
- WAVE3-025 (/debug command, P2) - Contract validation step

### Validation Rules Approach

Based on EXPEDITED_PATH disqualifiers and protocol structure:

**Breaking Changes** (require major version bump):
- API endpoint removed or renamed
- Request/response schema incompatibility
- Authentication requirements changed
- Rate limiting decreased

**Non-Breaking Changes** (minor version bump):
- New optional parameters added
- New response fields added
- Internal implementation changes
- Performance improvements

**Validation Checkpoints**:
- After Step 2 (Blast Radius Research) - Check API contracts of affected services
- During Step 5 (Fix Implementation) - Validate fix doesn't break contracts
- During Step 6 (Fix Validation) - Contract compliance testing

### Dependencies Resolved

- [x] EXPEDITED_PATH.md (categorizes trivial bugs, some by contract-related reasons)
- [x] BACKEND_STRUCTURE_TEMPLATE.md (includes API Contracts section)
- [x] WAVE3-013 (error categorization for contract violations)

---

## WAVE3-012: LESSONS.md Trigger Patterns

### Deliverable Overview

Document location: `temp/vibe_coding/LESSONS_TRIGGER_PATTERNS.md` (planned, to be written by implementation phase)

**Purpose**: Document 10+ trigger patterns that feed the WAVE3-021 Analyzer classification engine, enabling automated pattern extraction to LESSONS.md.

**Pattern Categories** (all with 1-3 patterns each):

1. **Error Recovery Patterns** (2 patterns)
   - Transient failure retry (timeouts, network errors)
   - Persistent failure detection (system failures requiring intervention)

2. **Performance Degradation Patterns** (2 patterns)
   - Query slowness / timeout
   - Memory or CPU degradation

3. **Configuration Drift Patterns** (2 patterns)
   - Schema version mismatch
   - Configuration value inconsistency

4. **Concurrency Issue Patterns** (2 patterns)
   - Race conditions (timing-dependent failures)
   - Deadlocks (lock wait scenarios)

5. **Data Quality Patterns** (2 patterns)
   - Null reference handling
   - Type mismatch in data transformation

6. **Integration Failure Patterns** (2 patterns)
   - Service timeout
   - API contract violation

7. **Deployment Problem Patterns** (2 patterns)
   - Migration failure
   - Rollback scenario

8. **Monitoring Blind Spot Patterns** (1 pattern)
   - Untraced event or missing alert

**Total**: 15 documented patterns

### Pattern Template Structure

Each pattern includes:

```markdown
### Pattern: [Pattern Name]

**Category**: [One of 8 categories]

**Detection Signature**:
- Keywords: [exact phrases to match in root_cause]
- Conditions: [other matching criteria]
- Frequency Threshold: [min occurrences for PROMOTE tier]

**Severity**: [Critical | High | Medium | Low]

**Action on Detection**:
1. [Triage step]
2. [Investigation step]
3. [Remediation step]

**Example** (from dbt-playground):
- Symptom: [what was observed]
- Root Cause: [what was found]
- Resolution: [how it was fixed]

**Related Patterns**: [links]

**Scoring Notes**: [frequency weight, recency impact, consistency factor]
```

### Integration with WAVE3-021 Analyzer

The LESSONS Analyzer uses these patterns for classification:

**Scoring Algorithm** (from WAVE3-021 Design):
```
Score = (Frequency × 0.4) + (Recency × 0.3) + (Consistency × 0.3)

PROMOTE tier: Score ≥ 0.8 AND frequency ≥ 3
CANDIDATE tier: Score ≥ 0.7 AND frequency ≥ 2
REVIEW tier: Score ≥ 0.5 AND frequency ≥ 2
IGNORE tier: Below thresholds
```

**Pattern Matching**:
- Keyword overlap (threshold: 0.5) per consolidate-memory.py implementation
- Category clustering for similar patterns
- Severity-weighted scoring

### Integration with FS1 Memory System

The patterns feed into the compound learning loop:

1. **Debug Session Completed** → Session Tracker writes to `debug_sessions`
2. **Pattern Detection** → LESSONS Analyzer detects matching patterns from `debug_sessions`
3. **Scoring & Classification** → Multi-factor scoring assigns tier (PROMOTE/CANDIDATE/REVIEW)
4. **LESSONS.md Update** → PROMOTE tier patterns added to LESSONS.md automatically
5. **Memory Integration** → Session also logged to `memory/events.jsonl` for FS1 consolidation

---

## Integration Points

### Upstream Dependencies

| Component | Status | Integration |
|-----------|--------|-------------|
| WAVE3-010 (BACKEND_STRUCTURE) | ✅ Complete | Service map provides context for integration patterns |
| WAVE3-013 (Observability) | ✅ Complete | Observability events feed pattern detection |
| WAVE3-015 (Deployment Checklist) | ✅ Complete | Deployment problems is one pattern category |
| WAVE3-017 (Incident Template) | ✅ Complete | Incident patterns become lessons |
| consolidate-memory.py | ✅ Available | Reference implementation for scoring |
| LEARNINGS.md | ✅ Available | Target format for promoted patterns |

### Downstream Dependencies

| Component | Status | Integration |
|-----------|--------|-------------|
| WAVE3-021 (LESSONS Analyzer) | 🏗️ Dev Phase | Consumes these patterns for classification |
| LESSONS.md | 📋 Days 5-6 | Patterns promoted here after analysis |
| Pattern extraction CLI | 📋 P2/P3 | Uses pattern definitions for rule-based extraction |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pattern definitions too vague for automation | Medium | High | Include explicit detection signatures with keyword lists |
| Patterns conflict with existing LEARNINGS.md format | Low | Medium | Review existing patterns before writing, match format exactly |
| WAVE3-021 scoring algorithm mismatch | Low | High | Copy exact formulas from WAVE3-021-ANALYZER-DESIGN.md |
| API validation rules not applicable to dbt-playground | Low | Medium | Include dbt-specific contract examples throughout |

---

## Dependencies Resolved

- [x] WAVE3-021 Analyzer design (pattern classification algorithm)
- [x] consolidate-memory.py (reference scoring implementation)
- [x] LEARNINGS.md (existing pattern library format)
- [x] EXPEDITED_PATH.md (trivial bug categories)
- [x] DISTRIBUTED_SYSTEMS.md (cross-service patterns)

---

## Files Created

1. **PLANNER_REPORT.md** (this file)
   - Planning summary for both tasks
   - Location: `temp/AGENT_REPORTS/wave3-p1-days3-4/PLANNER_REPORT.md`

2. **API_CONTRACT_VALIDATION.md** (planned for implementation phase)
   - Size: ~1,500 words
   - Sections: Types, Breaking Changes, Versioning, Validation Checkpoints, Error Categories, Observability Integration
   - Location: `temp/vibe_coding/API_CONTRACT_VALIDATION.md`

3. **LESSONS_TRIGGER_PATTERNS.md** (planned for implementation phase)
   - Size: ~2,000 words
   - Patterns: 15 total across 8 categories
   - Location: `temp/vibe_coding/LESSONS_TRIGGER_PATTERNS.md`

---

## Recommendations for Days 5-6 Integration

### For @developer on WAVE3-021 (LESSONS Analyzer)

1. **Pattern Matching Implementation**:
   - Use keyword overlap with 0.5 threshold (per consolidate-memory.py)
   - Implement category-based clustering
   - Support both exact and regex patterns

2. **Scoring Integration**:
   - Query `debug_root_cause_total` from Prometheus (WAVE3-013)
   - Calculate frequency/recency/consistency per formula
   - Apply tier classification thresholds

3. **Output Generation**:
   - Format output matching LEARNINGS.md style
   - Include pattern source (debug session ID, date)
   - Add metadata for traceability

### For @architect on WAVE3-025 (/debug command, P2)

1. **Validation Integration**:
   - Contract validation happens during Step 2 (Blast Radius Research)
   - Emit `debug.contract.validated` event to observability stack
   - Fail fast if breaking change detected in expedited path

2. **Error Handling**:
   - Map contract violations to WAVE3-013 error taxonomy
   - Trigger observability alerts for systematic violations
   - Feed to WAVE3-021 pattern detection

---

## Success Criteria Met

### WAVE3-011 (API Contract Validation)
- [x] Planned: 1,500+ words specification
- [x] Planned: Validation rules for 4+ contract types (internal APIs, external services, messages, DB)
- [x] Planned: Semantic versioning strategy documented
- [x] Planned: Breaking change categories defined
- [x] Planned: Error categorization with severity levels
- [x] Planned: Observability integration (WAVE3-013) documented
- [x] Planned: dbt-playground examples included

### WAVE3-012 (LESSONS.md Trigger Patterns)
- [x] Planned: 2,000+ words specification
- [x] Planned: 15 trigger patterns documented (target: 10+)
- [x] Planned: Each pattern has Name, Category, Signature, Action, Example
- [x] Planned: Pattern format matches WAVE3-021 Analyzer input requirements
- [x] Planned: Integration with FS1 Memory System documented
- [x] Planned: Scoring formula matches consolidate-memory.py
- [x] Planned: Promotion workflow to LEARNINGS.md documented

---

## Next Steps (Days 5-6)

1. **@developer**: Implement WAVE3-020/021 integration phase
2. **@architect**: Complete observability integration with WAVE3-020/021
3. **Team**: Design review of all Days 3-4 artifacts
4. **Integration**: Verify trace flow and metric emission
5. **Testing**: E2E tests for debug session → lesson extraction flow

---

*Planning Phase Complete | Ready for Implementation & Integration Phases*
