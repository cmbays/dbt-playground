---
name: specialist-focus-report
type: template
skill: repo-research
---

# Specialist Focus Report: [Focus Area]

> **Repo**: [Repository Name](https://github.com/owner/repo)
> **Specialist**: [architect | security-reviewer | code-reviewer]
> **Focus**: [architecture | security | quality]
> **Researched**: YYYY-MM-DD
> **Parent Research**: temp/AGENT_REPORTS/[repo-name]/RESEARCH_MASTER.md

---

## Executive Summary

[2-3 sentence overview of findings from this specialist's perspective]

**Top 3 Findings**:

1. [Most important finding in this focus area]
2. [Second most important]
3. [Third most important]

**Risk Level**: Low / Medium / High / Critical

---

## Focus Area Analysis

### Architecture Focus (`--focus=architecture`)

> Use this section if specialist is `architect`

#### Structure Assessment

| Aspect | Rating | Evidence |
|--------|--------|----------|
| Modularity | Excellent/Good/Fair/Poor | [Evidence] |
| Separation of Concerns | Excellent/Good/Fair/Poor | [Evidence] |
| Scalability Patterns | Excellent/Good/Fair/Poor | [Evidence] |
| Data Flow Clarity | Excellent/Good/Fair/Poor | [Evidence] |

#### Key Patterns Identified

##### Pattern 1: [Pattern Name]

- **What**: [Description]
- **Where**: [File/module references]
- **Applicability**: High/Medium/Low
- **Adoption complexity**: Low/Medium/High

##### Pattern 2: [Pattern Name]

[Continue as needed...]

#### Data Flow Analysis

[Describe how data moves through the system]

#### Scalability Considerations

[Assessment of how the architecture handles growth]

---

### Security Focus (`--focus=security`)

> Use this section if specialist is `security-reviewer`

#### Security Assessment

| Aspect | Rating | Evidence |
|--------|--------|----------|
| Dependency Security | Excellent/Good/Fair/Poor | [Evidence] |
| Authentication Patterns | Excellent/Good/Fair/Poor | [Evidence] |
| Data Handling | Excellent/Good/Fair/Poor | [Evidence] |
| Input Validation | Excellent/Good/Fair/Poor | [Evidence] |
| Secrets Management | Excellent/Good/Fair/Poor | [Evidence] |

#### Dependency Audit

| Dependency | Version | Known Vulnerabilities | Risk |
|------------|---------|----------------------|------|
| [package] | [version] | [CVE or "None"] | Low/Med/High |

#### Vulnerability Findings

##### Finding 1: [Vulnerability Type]

- **Severity**: Critical/High/Medium/Low
- **Location**: [File/module]
- **Description**: [What the issue is]
- **Recommendation**: [How to address]

##### Finding 2: [Vulnerability Type]

[Continue as needed...]

#### Security Patterns (Good Practices)

- [Pattern 1]: [What they do well]
- [Pattern 2]: [What they do well]

#### Security Concerns

- [Concern 1]: [Description and risk]
- [Concern 2]: [Description and risk]

---

### Quality Focus (`--focus=quality`)

> Use this section if specialist is `code-reviewer`

#### Quality Assessment

| Aspect | Rating | Evidence |
|--------|--------|----------|
| Test Coverage | Excellent/Good/Fair/Poor | [Coverage % if available] |
| Documentation | Excellent/Good/Fair/Poor | [What docs exist] |
| Code Standards | Excellent/Good/Fair/Poor | [Linting, formatting] |
| Maintainability | Excellent/Good/Fair/Poor | [Code complexity, clarity] |
| Technical Debt | Low/Medium/High | [Evidence of debt] |

#### Testing Analysis

| Test Type | Present | Coverage | Quality |
|-----------|---------|----------|---------|
| Unit Tests | Yes/No | X% | Excellent/Good/Fair/Poor |
| Integration Tests | Yes/No | X% | Excellent/Good/Fair/Poor |
| E2E Tests | Yes/No | X% | Excellent/Good/Fair/Poor |

#### Documentation Assessment

- **README**: Excellent/Good/Fair/Poor - [Notes]
- **API Docs**: Excellent/Good/Fair/Poor - [Notes]
- **Code Comments**: Excellent/Good/Fair/Poor - [Notes]
- **Examples**: Excellent/Good/Fair/Poor - [Notes]

#### Maintainability Findings

##### Finding 1: [Area]

- **Assessment**: [Description]
- **Impact**: High/Medium/Low
- **Recommendation**: [What to do]

##### Finding 2: [Area]

[Continue as needed...]

#### Technical Debt Inventory

| Debt Item | Severity | Estimated Effort | Priority |
|-----------|----------|------------------|----------|
| [Item 1] | High/Med/Low | Low/Med/High | P1/P2/P3 |

---

## Risks Identified

| Risk | Likelihood | Impact | Focus Area | Mitigation |
|------|------------|--------|------------|------------|
| [Risk 1] | Low/Med/High | Low/Med/High | [arch/sec/qual] | [Mitigation] |
| [Risk 2] | Low/Med/High | Low/Med/High | [arch/sec/qual] | [Mitigation] |

---

## Recommendations

### For Master Report Synthesis

**Key findings to include**:

1. [Finding 1 - critical for synthesis]
2. [Finding 2 - important context]
3. [Finding 3 - notable observation]

**Divergent perspectives** (may conflict with other specialists):

- [Area where this specialist's view may differ]
- [Reason for potential disagreement]

**Questions for council deliberation** (if `--council`):

- [Question 1 requiring multi-perspective discussion]
- [Question 2 requiring trade-off analysis]

### Integration Recommendations

| Recommendation | Priority | Complexity | Dependencies |
|----------------|----------|------------|--------------|
| [Recommendation 1] | P1/P2/P3 | Low/Med/High | [What it depends on] |
| [Recommendation 2] | P1/P2/P3 | Low/Med/High | [What it depends on] |

---

## Appendix

### Key File References

| File | Purpose | Notable Finding |
|------|---------|-----------------|
| `path/to/file` | [purpose] | [what was found] |

### Evidence Snippets

#### [Snippet Name]

```
// From: path/to/file
// Relevant to: [finding]

[code or config snippet]
```

---

## Handoff

**Status**: Complete

**Next Step**: Master Sage synthesis (RESEARCH_MASTER.md)

**Specialist Notes**:

[Any additional context for the master report author]

---

*Report generated by [specialist role] specialist using repo-research skill with --focus=[focus]*
