# Repository Research Report

> **Repo**: [Repository Name](https://github.com/owner/repo)
> **Researched**: YYYY-MM-DD
> **Researcher**: Sage persona
> **Focus**: [Primary research question or goal]
> **Depth**: Quick / Standard / Deep

---

## Executive Summary

[2-3 sentence overview of the repository and key findings]

**Top 3 Takeaways**:

1. [Most important finding]
2. [Second most important]
3. [Third most important]

**Recommendation**: [One-line recommendation for our project]

---

## 1. Repository Overview

### Purpose

[What problem does this repo solve? Who is it for?]

### Technology Stack

| Layer | Technology |
|-------|------------|
| Language | |
| Framework | |
| Build Tool | |
| Testing | |
| Other | |

### Project Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Stars | X | High (>5k) / Medium (1k-5k) / Low (<1k) |
| Forks | Y | Active (>500) / Moderate (100-500) / Limited (<100) |
| Last commit | YYYY-MM-DD | Active (<1mo) / Maintained (<6mo) / Stale (>6mo) / Abandoned (>1yr) |
| Issues | X open / Y closed (Z% resolved) | Healthy (>70%) / Concerning (<50%) |
| Contributors | N | Diverse (>50) / Moderate (10-50) / Limited (<10) |
| Version | [version] | [Stability: stable/beta/alpha] |

**Health Assessment**: Thriving / Stable / Stale / Abandoned

**Reasoning**: [Brief explanation of health assessment based on metrics]

### Code Quality Assessment

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| **Testing** | Excellent/Good/Fair/Poor | [Coverage %, test types present] |
| **Documentation** | Excellent/Good/Fair/Poor | [What docs exist] |
| **Maintenance** | Excellent/Good/Fair/Poor | [Commit frequency, issue response] |
| **Architecture** | Excellent/Good/Fair/Poor | [Modularity, patterns used] |
| **Security** | Excellent/Good/Fair/Poor | [Security practices observed] |

**Overall Code Quality**: Excellent / Good / Fair / Poor

**Notes**: [Key observations about code quality]

---

## 2. Project Structure

### Directory Layout

```
repo/
├── [folder]/ - [purpose]
├── [folder]/ - [purpose]
├── [file] - [purpose]
└── ...
```

### Organization Patterns

[Describe how the codebase is organized - by feature, by layer, etc.]

### Key Observations

- [Observation about structure]
- [What works well]
- [What's unusual or noteworthy]

### Applicability to Our Project

| Their Pattern | Our Equivalent | Adoption Potential |
|---------------|----------------|-------------------|
| [pattern] | [our approach] | High/Medium/Low |

---

## 3. Architecture Patterns

### Pattern 1: [Pattern Name]

**What it is**: [Description]
**Where used**: [File/module references]
**Why it works**: [Benefits]
**Pattern type**: Code / Architecture / Workflow / Documentation
**Our applicability**: [How we could use this]

### Pattern 2: [Pattern Name]

**What it is**: [Description]
**Where used**: [File/module references]
**Why it works**: [Benefits]
**Pattern type**: Code / Architecture / Workflow / Documentation
**Our applicability**: [How we could use this]

### Pattern 3: [Pattern Name]

[Continue as needed...]

### Pattern Synthesis (for multi-repo comparison)

**Convergent Patterns** (present in 2+ repos):

- [Pattern X]: Found in [Repo A, Repo B] - Likely industry standard
- [Pattern Y]: Found in [Repo B, Repo C] - Proven approach

**Divergent Patterns** (unique to one repo):

- [Pattern Z]: Only in [Repo A] - Experimental/specialized approach
  - Reason for uniqueness: [Why this repo alone uses it]
  - Evaluation: Worth adopting / Needs more research / Skip

**Best Practices Identified**:

- [Practice 1]: Solves [problem] effectively
- [Practice 2]: Avoids [common pitfall]

**Anti-Patterns Identified**:

- [Anti-pattern 1]: Causes [issue], seen in [Repo X]
- [Anti-pattern 2]: Leads to [problem], refactored away in [Repo Y]

### Data Flow

[Describe how data moves through the application]

### State Management

[How is state handled? What patterns are used?]

---

## 4. Feature Analysis

### Feature Inventory

| Feature | Maturity | Quality | Relevance to Us |
|---------|----------|---------|-----------------|
| [Feature 1] | Complete/Partial/WIP | High/Medium/Low | High/Medium/Low |
| [Feature 2] | | | |
| [Feature 3] | | | |

### Feature Deep-Dives

#### [Feature Name] (High Relevance)

**What it does**: [Description]
**Implementation approach**: [How they built it]
**Key files**:

- `path/to/file.js` - [purpose]
- `path/to/other.js` - [purpose]

**What we can learn**:

- [Learning 1]
- [Learning 2]

**Potential adaptation**:
[How we might implement something similar]

---

## 5. Integration Opportunities

### High Priority (Quick Wins)

#### Opportunity 1: [Name]

- **What**: [Description]
- **Value**: [Why it matters]
- **Effort**: Low / Medium / High
- **Approach**: Direct copy / Adapt / Inspiration only
- **Risk**: [Potential issues]

#### Opportunity 2: [Name]

[Continue format...]

### Medium Priority (Planned Features)

#### Opportunity 3: [Name]

[Continue format...]

### Low Priority (Future Consideration)

#### Opportunity 4: [Name]

[Continue format...]

### Not Recommended

| Idea | Why Not |
|------|---------|
| [Something] | [Reason - too complex, doesn't fit, etc.] |

---

## 6. Technology Assessment

### Dependencies Worth Noting

| Dependency | Purpose | Our Interest |
|------------|---------|--------------|
| [package] | [what it does] | Adopt / Evaluate / Skip |

### Build & Tooling

[Notable build setup, CI/CD, developer experience tools]

### Testing Approach

[How do they test? What coverage? What patterns?]

### Performance Considerations

[Any performance optimizations or concerns noted]

### Security Considerations

[Any security patterns or concerns noted]

---

## 7. Community Insights

### Popular Solutions (in this problem space)

- **[Solution 1]**: X stars, Y forks - [Why it's popular]
- **[Solution 2]**: X stars, Y forks - [Why it's popular]
- **This repo vs. alternatives**: [Comparison]

### Controversial Topics

- **[Topic 1]**: Community split on [approach A vs B]
  - Debate details: [Summary of arguments]
  - Resolution status: Ongoing / Decided / Forked project
- **[Topic 2]**: [Feature X] heavily requested but not implemented
  - Reason: [Why maintainers haven't added it]
  - Workarounds: [How users handle it]

### Expert Opinions

- **Maintainer insights**:
  - [Decision X] made due to [constraint Y] (source: issue #123)
  - Known limitations: [Acknowledged issues]
- **Top contributors recommend**:
  - [Pattern Z] for [use case] (source: PR #456)
- **Community sentiment**:
  - Generally positive about [aspect]
  - Concerns about [aspect]

### Ecosystem Trends

- **Migration patterns**: [Old approach] → [New approach]
  - Reason: [Why the shift]
- **Emerging alternatives**: [New library] gaining traction
  - Difference: [How it compares]
- **Deprecated features**: [Feature] being phased out
  - Migration path: [How to adapt]

### Red Flags

- ⚠️ [Critical issue] unresolved for [timeframe]
- ⚠️ Maintainer burnout signals: [Evidence]
- ⚠️ Breaking changes without migration guides
- ⚠️ Security vulnerabilities: [Status]

**Community Health Score**: Excellent / Good / Fair / Poor

**Notes**: [Overall assessment of community health and activity]

---

## 8. Risks & Concerns

### Technical Risks

- **[Risk 1]**: [Description and mitigation]
- **[Risk 2]**: [Description and mitigation]

### Compatibility Concerns

- [Concern about fitting with our stack/approach]

### Maintenance Concerns

- [Concern about long-term maintenance if adopted]

### Licensing

- **License**: [License type]
- **Implications**: [What this means for us]

---

## 9. Recommendations

### For Product Manager (pm:)

**Feature Opportunities**:

1. **[Feature]** - [User value proposition]
   - Effort estimate: Low/Medium/High
   - Suggested priority: P1/P2/P3

2. **[Feature]** - [User value proposition]
   - Effort estimate: Low/Medium/High
   - Suggested priority: P1/P2/P3

**User Stories to Consider**:

- As a [user], I want [feature] so that [benefit]
- As a [user], I want [feature] so that [benefit]

**Questions for PM**:

- [Question about user needs or priorities]
- [Question about scope or timeline]

---

### For Technical Architect (arch:)

**Architecture Recommendations**:

1. **[Pattern/Approach]** - [Why and how to apply]
   - Complexity: Low/Medium/High
   - Files affected: [estimate]

2. **[Pattern/Approach]** - [Why and how to apply]
   - Complexity: Low/Medium/High
   - Files affected: [estimate]

**TDD Candidates**:

- [ ] [Feature/pattern] - Ready for technical design
- [ ] [Feature/pattern] - Needs more research

**Technical Questions**:

- [Question about implementation approach]
- [Question about tradeoffs]

---

## 10. Action Items

### Immediate (This Sprint)

- [ ] [Action item with owner]
- [ ] [Action item with owner]

### Short-term (Next Sprint)

- [ ] [Action item]
- [ ] [Action item]

### Long-term (Backlog)

- [ ] [Action item]
- [ ] [Action item]

---

## 11. Appendix

### Key File References

| File | Purpose | Notable Code |
|------|---------|--------------|
| `path/to/file` | [purpose] | Lines X-Y: [what's notable] |

### Code Snippets

#### [Snippet Name]

```javascript
// From: path/to/file.js
// Purpose: [why this is notable]

[code snippet]
```

### External Resources

- [Link to relevant docs]
- [Link to related articles]
- [Link to similar projects]

---

## Handoff

### Status

- [x] Research complete
- [ ] PM review pending
- [ ] Architect review pending
- [ ] Action items assigned

### Next Persona

**Primary**: `pm:` for feature prioritization
**Secondary**: `arch:` for technical design

### Handoff Notes

[Any context the next persona should know]

---

*Report generated by Sage persona using repo-research skill*
*Template version: 2.0 - Enhanced with metrics, code quality, community insights, and multi-repo comparison support*
