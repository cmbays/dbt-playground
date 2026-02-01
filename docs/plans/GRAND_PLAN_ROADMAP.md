# The Grand Plan: 9-Version Phased Roadmap

## Executive Summary

This plan synthesizes feedback from a council of 5 specialists (Strategic Planner, Risk Analyst, Integration Architect, Metrics Designer, Research Scientist) to create a 9-version roadmap from v0.10 to v1.7 that iteratively builds toward the Grand Plan vision: **self-improving AI teams with competitive benchmarking and evolutionary capabilities**.

**Prerequisite Complete**: v0.8 (Data Quality Excellence) has been merged.

**Critical Constraint**: Grand Plan implementation CANNOT begin until v0.10 features are complete.

**Total Estimated Effort**: 800-1000 hours over 18-24 months

---

## Document References

All council reviews and source documents are in:
`temp/2026_02_01_Discussion/`

| Document | Purpose |
|----------|---------|
| `THE_GRAND_PLAN.md` | Core vision with Gemini/Perplexity feedback |
| `ARCHITECT_REVIEW.md` | Feasibility, incremental path, effort estimates |
| `PM_REVIEW.md` | User stories, MVP definition, prioritization |
| `SAGE_REVIEW.md` | Epistemology, memory architecture, anti-patterns |
| `TESTER_REVIEW.md` | Hypothesis validation, statistical rigor |
| `COUNCIL_STRATEGIC_PLAN.md` | 10-version roadmap details |
| `COUNCIL_RISK_ASSESSMENT.md` | 47 risks with mitigations |
| `COUNCIL_INTEGRATION_ARCHITECTURE.md` | Feature-to-version mapping |
| `COUNCIL_METRICS_FRAMEWORK.md` | Metrics by phase |
| `COUNCIL_RESEARCH_PROTOCOL.md` | Scientific methodology |
| `HOLISTIC_REVIEW.md` | Feature set integration analysis |
| `*_report.md`, `*_plan.md`, `*_PRD.md`, `*_TDD.md` | Individual feature specs |

---

## 9-Version Roadmap Overview

```
PHASE A: FOUNDATION (Current → Apr 2026)
└── v0.10: Agent Orchestration Foundation (110-140h)

PHASE B: TEAM INFRASTRUCTURE (May → Oct 2026)
├── v1.0: Team Identity & Basic Competition (48-72h)
├── v1.1: Common Workspace & Hackathon Prototype (56-70h)
└── v1.2: Benchmarking Infrastructure (63-80h)

PHASE C: BENCHMARKING & COMPETITION (Nov 2026 → Apr 2027)
├── v1.3: Causal Analysis Foundation (100-120h)
├── v1.4: Cross-Pollination & Learning Transfer (80-95h)
└── v1.5: Full Hackathon System (60-75h)

PHASE D: EVOLUTION & SELF-IMPROVEMENT (May → Aug 2027)
├── v1.6: Evolution System Foundation (105-125h)
└── v1.7: Self-Improving AI Teams (110-130h)
```

---

## Phase A: Foundation (v0.10)

### v0.10 - Agent Orchestration Foundation

**Target**: April 30, 2026 | **Effort**: 110-140h

| Feature Set | Deliverables | Effort | Source |
|-------------|--------------|--------|--------|
| FS1: Memory | `memory/` logs, Sage workflows | 14-21h | `agent_memory_plan.md` |
| FS2: Kanban | Per-ticket checklists, WIP limits | 16-24h | `kanban_workflow_plan.md` |
| FS3: QA | QA_REPORT.md, qa-reviewer | 15-20h | `qa_enforcement_plan.md` |
| FS5: Metrics | SQLite schema, adherence scoring | 50-60h | `metrics_dashboard_plan.md` |
| FS7: GitHub | CODEOWNERS, issue-ID naming | 15h | `github_integration_plan.md` |

**Success Criteria**:

- [ ] 100% sessions logged to memory/
- [ ] >85% workflow adherence score
- [ ] 0 deploys without QA artifact
- [ ] Metrics dashboard operational

**GATE**: v0.10 must be complete before Phase B begins.

---

## Phase B: Team Infrastructure (v1.0 - v1.2)

### v1.0 - Team Identity & Basic Competition

**Target**: June 30, 2026 | **Effort**: 48-72h

| Deliverable | Description | Source |
|-------------|-------------|--------|
| SOUL.md | Unified agent identity | `multi_agent_coordination_plan.md` |
| Team Directory | `.claude/teams/{id}/` structure | `ARCHITECT_REVIEW.md` |
| TEAM_SOUL.md | Philosophy template | `ARCHITECT_REVIEW.md` |
| WIP Enforcement | Hard limits in Supervisor | FS2 Phases 3-4 |

**Success Criteria**:

- [ ] 2 teams operate independently
- [ ] Team-local memory persists across sessions
- [ ] Teams have distinct philosophies documented

**Hypothesis Tested**: H1 - Persistent memory improves performance

### v1.1 - Common Workspace & Hackathon Prototype

**Target**: August 31, 2026 | **Effort**: 56-70h

| Deliverable | Description | Source |
|-------------|-------------|--------|
| `shared/` Directory | Common workspace structure | `ARCHITECT_REVIEW.md` |
| Event Log | Shared workspace write audit | `ARCHITECT_REVIEW.md` |
| Scout Agent | Cross-team pattern observer | `SAGE_REVIEW.md` |
| Hackathon MVP | 2 teams, 3 reviewers | `hackathon_system_plan.md` |

**Success Criteria**:

- [ ] Teams share learnings via common workspace
- [ ] No state leakage between team workspaces
- [ ] Prototype hackathon completes successfully

### v1.2 - Benchmarking Infrastructure

**Target**: October 31, 2026 | **Effort**: 63-80h

| Deliverable | Description | Source |
|-------------|-------------|--------|
| Benchmark Schema | YAML task definitions | `TESTER_REVIEW.md` |
| Council of 7 | Full reviewer rotation | `hackathon_system_plan.md` |
| Results Archive | `shared/benchmarks/` | `ARCHITECT_REVIEW.md` |
| Token Tracking | Per-team efficiency metrics | `PM_REVIEW.md` |

**Success Criteria**:

- [ ] Benchmark reliability r > 0.80
- [ ] Council inter-rater reliability > 0.70
- [ ] 30+ benchmark cycles logged

**Hypothesis Tested**: H2 - Team identity affects approach quality

---

## Phase C: Benchmarking & Competition (v1.3 - v1.5)

### v1.3 - Causal Analysis Foundation

**Target**: December 31, 2026 | **Effort**: 100-120h

| Deliverable | Description | Source |
|-------------|-------------|--------|
| Memory State Diff | Before/after comparison | `ARCHITECT_REVIEW.md` |
| Commit Impact Analysis | Correlate commits with scores | `SAGE_REVIEW.md` |
| Sage Chronicler Mode | Longitudinal causality tracking | `SAGE_REVIEW.md` |
| Confidence Tiers | Observed→Replicated→Validated→Established | `SAGE_REVIEW.md` |

**Success Criteria**:

- [ ] System identifies patterns correlated with success (p < 0.05)
- [ ] Confidence intervals on all causal claims
- [ ] At least 1 pattern promoted through full validation

**Hypothesis Tested**: H3 - Competition accelerates improvement

### v1.4 - Cross-Pollination & Learning Transfer

**Target**: February 28, 2027 | **Effort**: 80-95h

| Deliverable | Description | Source |
|-------------|-------------|--------|
| Scout Agent Full | Philosophy-filtered adoption | `SAGE_REVIEW.md` |
| Pattern Provenance | Track origin and adaptations | `SAGE_REVIEW.md` |
| Diversity Metrics | Philosophy diversity tracking | `SAGE_REVIEW.md` |

**Success Criteria**:

- [ ] Cross-pollination success rate >50%
- [ ] Diversity metrics show no convergence trend
- [ ] Pattern provenance fully tracked

**Hypothesis Tested**: H4 - Cross-pollination spreads good patterns

### v1.5 - Full Hackathon System

**Target**: April 30, 2027 | **Effort**: 60-75h

| Deliverable | Description | Source |
|-------------|-------------|--------|
| `/hackathon` Full | 3+ teams, 4-hour duration | `hackathon_system_plan.md` |
| Tournament Mode | Multi-round competitions | NEW |
| Results Archive | `docs/hackathons/` | `hackathon_system_plan.md` |

**Success Criteria**:

- [ ] 3+ teams complete parallel development
- [ ] 7 reviewers provide consistent scoring
- [ ] Tournament mode runs 3+ rounds

---

## Phase D: Evolution & Self-Improvement (v1.6 - v1.7)

### v1.6 - Evolution System Foundation

**Target**: June 30, 2027 | **Effort**: 105-125h

| Deliverable | Description | Source |
|-------------|-------------|--------|
| Philosophy Seeding | Spawn team from template | `ARCHITECT_REVIEW.md` |
| Skill Injection | Controlled capability mutations | `THE_GRAND_PLAN.md` |
| Chaos Monkey | Periodic stress tests | `THE_GRAND_PLAN.md` |
| Rollback Checkpoints | Pre-mutation snapshots | `TESTER_REVIEW.md` |

**Success Criteria**:

- [ ] Can spawn new team from philosophy seed
- [ ] Mutations measurably impact performance
- [ ] Rollback successfully restores team state

### v1.7 - Self-Improving AI Teams (GRAND PLAN COMPLETE)

**Target**: August 31, 2027 | **Effort**: 110-130h

| Deliverable | Description | Source |
|-------------|-------------|--------|
| Autonomous Loop | Teams optimize themselves | `THE_GRAND_PLAN.md` |
| Safety Bounds | Limits on autonomous action | NEW |
| Reproducibility Package | External validation materials | `TESTER_REVIEW.md` |
| Longitudinal Report | 6+ months evolution data | NEW |

**Success Criteria**:

- [ ] Teams show statistically significant improvement (p < 0.05)
- [ ] At least 3 causal links validated
- [ ] Token efficiency improves >20% from baseline
- [ ] Zero catastrophic failures
- [ ] External party replicates findings

**Hypothesis Tested**: H5 - Teams genuinely self-improve over time

---

## Top 5 Risks (from Council Risk Assessment)

| Risk | Phase | Mitigation |
|------|-------|------------|
| Complexity cascade | All | Aggressive simplicity, layer boundaries |
| Runaway token costs | v1.3+ | Token budgets, circuit breakers |
| Causal attribution errors | v1.3+ | Counterfactual testing, confidence tiers |
| Goodhart's Law gaming | v1.2+ | Hidden benchmarks, multi-dimensional scores |
| Monoculture convergence | v1.4+ | Philosophy anchoring, diversity metrics |

---

## Governance Checkpoints

| Transition | Gate Criteria | Reviewers |
|------------|---------------|-----------|
| v0.10 → v1.0 | All 5 feature sets operational | Architect + PM |
| v1.2 → v1.3 | Benchmark reliability > 0.80, 30+ cycles | Tester + Sage |
| v1.5 → v1.6 | Causal analysis validated, diversity preserved | Sage + PM |
| v1.7 Complete | External validation, zero catastrophic failures | Full Council |

---

## Immediate Next Steps

1. **Begin v0.10 implementation** - FS1 (Memory) is the keystone
2. **Write user stories** (per PM Review) - Before v1.0 implementation
3. **Establish metrics baseline** (per Metrics Framework) - Before v1.0

---

## Verification

To verify this plan is progressing correctly:

1. **v0.10 Gate**: Run `uv run dbt build` - all tests pass, `memory/` directory exists
2. **v1.0 Gate**: 2 teams can complete same benchmark independently
3. **v1.2 Gate**: Benchmark scores have r > 0.80 reliability
4. **v1.5 Gate**: Tournament produces winner with documented methodology
5. **v1.7 Gate**: External researcher replicates improvement findings

---

## Files to Create/Modify

### Phase A (v0.10)

- `memory/` directory structure
- `temp/metrics.db` SQLite database
- `.claude/agents/qa-reviewer.md` new persona
- `scripts/compute-adherence.py` new script

### Phase B (v1.0-v1.2)

- `.claude/SOUL.md` unified identity
- `.claude/teams/` directory structure
- `shared/` common workspace
- `shared/benchmarks/` results archive

### Phase C-D (v1.3-v1.7)

- Causal analysis engine
- Evolution/mutation system
- Reproducibility package

---

*Plan created: 2026-02-01*
*Council: Strategic Planner, Risk Analyst, Integration Architect, Metrics Designer, Research Scientist*
