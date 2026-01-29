---
name: repo-researcher
tools: Read, Write, Edit, Bash, WebFetch, WebSearch, Glob, Grep
model: sonnet
description: Research external repositories to extract architecture patterns, implementation approaches, and integration opportunities for feature planning. Generates structured reports with actionable recommendations.
---

# Repo Research Skill

**Purpose**: Research an external repository and generate a structured learnings report for feature and architecture planning.

**Owner**: Sage persona

**Invocation**: `/repo-research <github-url>` or `sage: research repo <url>`

**Modes**:
- Single repo: `/repo-research <url>`
- Multi-repo comparison: `/repo-research <url1> <url2> <url3> --compare`
- Depth control: `--depth=quick|standard|deep`

---

## When to Use

- Evaluating external libraries/tools for potential integration
- Learning from well-architected open source projects
- Researching competitor implementations
- Gathering patterns from reference implementations
- Technology evaluation for new features

**Do NOT use for**:
- Simple documentation lookups (use WebFetch instead)
- Projects you already understand well
- Quick API reference checks

---

## Prerequisites

**Required inputs**:
- GitHub repository URL (public repos only)
- Research focus or question (optional but recommended)

**Tools needed**:
- `gh` CLI for repo cloning/exploration
- Read/Glob/Grep for codebase analysis
- WebFetch for README and documentation

---

## Process

### Step 1: Repository Overview & Metrics

**Actions**:
1. Clone or fetch repo metadata using `gh repo view <owner/repo> --json stargazerCount,forkCount,pushedAt,openIssues,closedIssues`
2. Extract quantitative metrics:
   - Stars (community interest)
   - Forks (adoption level)
   - Last commit date (maintenance status)
   - Open vs closed issues (project health)
   - Contributors count (community size)
3. Read README.md via WebFetch or gh CLI
4. Identify:
   - Project purpose and scope
   - Technology stack
   - Architecture overview
   - Key features
   - Documentation quality

**Metrics template**:
| Metric | Value | Assessment |
|--------|-------|------------|
| Stars | X | High (>5k) / Medium (1k-5k) / Low (<1k) |
| Forks | Y | Active (>500) / Moderate (100-500) / Limited (<100) |
| Last commit | YYYY-MM-DD | Active (<1mo) / Maintained (<6mo) / Stale (>6mo) / Abandoned (>1yr) |
| Issues | X open / Y closed (Z% resolved) | Healthy (>70%) / Concerning (<50%) |
| Contributors | N | Diverse (>50) / Moderate (10-50) / Limited (<10) |

**Health assessment rubric**:
- **Thriving**: Active commits, high stars, healthy issue resolution, diverse contributors
- **Stable**: Regular maintenance, moderate adoption, responsive to issues
- **Stale**: Infrequent updates, low activity, but still functional
- **Abandoned**: No recent commits, unresolved issues piling up

**Output**: Quantitative health assessment + qualitative overview

---

### Step 2: Structure Analysis

**Actions**:
1. Examine directory structure: `gh api repos/<owner>/<repo>/contents`
2. Identify architectural patterns:
   - Folder organization
   - Separation of concerns
   - Module boundaries
   - Configuration approach
3. Note naming conventions and file organization

**Questions to answer**:
- How is the codebase organized?
- What patterns are used for separation?
- How are shared resources managed?
- What's the build/tooling setup?

**Output**: Structural patterns and organization insights

---

### Step 3: Feature Inventory & Code Quality

**Actions**:
1. List major features from README/docs
2. Explore implementation of key features
3. Note:
   - User-facing features
   - Developer experience features
   - Infrastructure/tooling features
4. Assess feature maturity and code quality

**Code Quality Assessment**:

Evaluate across these dimensions (rate as excellent/good/fair/poor):

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| **Testing** | | Unit tests? Integration tests? E2E tests? Coverage reports? |
| **Documentation** | | README quality? API docs? Code comments? Examples? |
| **Maintenance** | | Recent commits? Active PRs? Responsive to issues? |
| **Architecture** | | Clear separation of concerns? Modular? Scalable patterns? |
| **Security** | | Dependency scanning? Security policy? Vulnerability handling? |

**Quality Rubric**:
- **Excellent**: 80%+ test coverage, comprehensive docs, weekly commits, security scanning
- **Good**: 50%+ coverage, good README + API docs, monthly commits, some security practices
- **Fair**: Some tests, basic README, quarterly commits, minimal security
- **Poor**: No tests, sparse docs, abandoned or rarely updated

**Output**: Feature list with implementation notes + code quality assessment

---

### Step 4: Pattern Extraction & Synthesis

**Actions**:
1. Identify reusable patterns:
   - Code patterns (components, utilities, abstractions)
   - Architecture patterns (data flow, state management)
   - Workflow patterns (testing, deployment, CI/CD)
   - Documentation patterns
2. Evaluate pattern quality (proven? well-documented?)
3. Assess applicability to our project

**For single repo research**:
- Extract patterns as documented above
- Note innovative approaches
- Identify potential adaptation needs

**For multi-repo comparison mode** (`--compare`):
1. **Convergent patterns** (present in 2+ repos):
   - Likely industry standards or best practices
   - High confidence for adoption
   - Example: All 3 repos use CSS custom properties for theming
2. **Divergent patterns** (unique to 1 repo):
   - Niche solutions or experimental approaches
   - Requires deeper evaluation before adoption
   - Example: Only Repo A uses Web Workers for processing
3. **Best practices** (patterns solving common problems well):
   - Look for patterns with good docs and community praise
   - Check for patterns that avoid known pitfalls
4. **Anti-patterns** (patterns causing issues across repos):
   - Note patterns mentioned in issues/complaints
   - Patterns that were refactored away in later versions

**Synthesis questions**:
- What patterns appear in 2+ repos? → Likely proven approaches
- What patterns are unique to 1 repo? → Experimental or specialized
- Which patterns solve [our specific problem] best?
- Which patterns should we avoid? → Known issues or complexity

**Output**: Catalog of extractable patterns + cross-repo synthesis (if comparing)

---

### Step 5: Technology Assessment

**Actions**:
1. List dependencies and tools used
2. Evaluate:
   - Technology choices and rationale (if documented)
   - Dependency health (maintenance, security)
   - Compatibility with our stack
3. Note any innovative or unfamiliar technologies

**Output**: Technology stack analysis

---

### Step 6: Integration Opportunities

**Actions**:
1. Identify features/patterns applicable to our project
2. Assess integration complexity:
   - Direct adoption (copy pattern)
   - Adaptation needed (modify for our context)
   - Inspiration only (learn concept, build our own)
3. Note potential risks or concerns
4. Prioritize by value and effort

**Output**: Prioritized integration recommendations

---

### Step 7: Community Insights

**Actions**:
1. Gather community intelligence from:
   - Issue discussions (common requests, pain points)
   - Pull request conversations (design decisions)
   - GitHub Discussions or forums
   - Release notes and changelogs
2. Identify patterns in community feedback

**Community Insights Template**:

**Popular solutions** (most adopted in this space):
- [Solution 1] - X stars, Y forks, [adoption indicators]
- [Solution 2] - X stars, Y forks, [adoption indicators]

**Controversial topics** (debated in issues/discussions):
- [Topic 1]: Community split on [approach A vs B]
- [Topic 2]: [Feature X] heavily requested but not implemented due to [reason]

**Expert opinions** (maintainer comments, notable contributors):
- Maintainer notes [decision X] made due to [constraint Y]
- Top contributor recommends [pattern Z] for [use case]
- Known limitations acknowledged: [limitation with explanation]

**Ecosystem trends**:
- Migration patterns: [old approach] → [new approach]
- Emerging alternatives: [new library] gaining traction
- Deprecated features: [feature] being phased out

**Red flags** (potential concerns):
- Unresolved critical issues open for >6 months
- Maintainer burnout signals (slow response times)
- Breaking changes without migration guides
- Security vulnerabilities not addressed promptly

**Output**: Community intelligence summary

---

### Step 8: Generate Report

**Actions**:
1. Use template: `.claude/templates/repo-research-report-template.md`
2. Fill all sections with findings
3. Include specific file/code references
4. Write actionable recommendations
5. Save to:
   - Single repo: `docs/research/REPO-RESEARCH-[repo-name]-[date].md`
   - Multi-repo: `docs/research/REPO-COMPARISON-[topic]-[date].md`

**For multi-repo comparison**, also create:
- Individual reports for each repo (optional, for depth)
- Comparison table with key metrics side-by-side
- Synthesis section with best-of-breed recommendations

**Output**: Complete research report(s)

---

## Handoff Protocol

### To Product Manager (pm:)

**What PM needs**:
- Feature opportunities (what could we build?)
- User value propositions (why would users want this?)
- Competitive analysis (how does this compare?)
- Priority recommendations

**Handoff message**:
```
sage: → pm:

Research complete for [repo-name].

**Key Feature Opportunities**:
1. [Feature 1] - [User value]
2. [Feature 2] - [User value]

**Report**: docs/research/REPO-RESEARCH-[repo-name]-[date].md

**Recommended next steps**:
- Review Section 5 (Integration Opportunities) for PRD candidates
- Consider [specific feature] for [reason]

**Questions for PM consideration**:
- [Question about priorities/scope]
```

### To Technical Architect (arch:)

**What Architect needs**:
- Architecture patterns (how did they solve X?)
- Technical decisions (what tradeoffs did they make?)
- Implementation approaches (how could we adopt this?)
- Risk assessment (what could go wrong?)

**Handoff message**:
```
sage: → arch:

Research complete for [repo-name].

**Key Architecture Patterns**:
1. [Pattern 1] - [Applicability to our project]
2. [Pattern 2] - [Applicability to our project]

**Report**: docs/research/REPO-RESEARCH-[repo-name]-[date].md

**Recommended for TDD consideration**:
- [Pattern/approach] could address [our challenge]
- See Section 3 (Architecture Patterns) for details

**Technical concerns**:
- [Concern about compatibility/complexity]
```

---

## Expected Outcomes

**Primary output**:
- `docs/research/REPO-RESEARCH-[repo-name]-[date].md`

**Quality indicators**:
- [ ] All template sections completed
- [ ] Specific code/file references included
- [ ] Recommendations are actionable
- [ ] Integration complexity assessed
- [ ] Risks identified
- [ ] Handoff messages prepared

---

## Research Modes

### Single Repository Research
```
/repo-research <url> [--depth=quick|standard|deep]
```

Standard workflow: Steps 1-8 for one repository

---

### Multi-Repository Comparison
```
/repo-research <url1> <url2> <url3> --compare [--depth=quick|standard|deep]
```

**Process**:
1. Research each repo individually (Steps 1-6 for each)
2. Skip Step 7 (Community Insights) for individual repos
3. **Comparative Analysis** (replaces Step 7):
   - Create side-by-side metrics comparison table
   - Identify common patterns across repos (convergent)
   - Note unique approaches per repo (divergent)
   - Synthesize "best of breed" recommendations
4. Generate comparison report (Step 8)

**Comparison Report Structure**:
```markdown
# Repository Comparison: [Topic/Category]

## Executive Summary
[Which repo is best for what use case]

## Metrics Comparison
| Metric | Repo 1 | Repo 2 | Repo 3 |
|--------|--------|--------|--------|
| Stars | X | Y | Z |
| Maintenance | Active | Stale | Active |
| Test Coverage | 85% | 40% | None |
| Documentation | Excellent | Good | Fair |

## Feature Matrix
| Feature | Repo 1 | Repo 2 | Repo 3 |
|---------|--------|--------|--------|
| Feature A | ✅ | ✅ | ❌ |
| Feature B | ✅ | ❌ | ✅ |

## Pattern Analysis
### Convergent Patterns (2+ repos)
- Pattern X: All repos use [approach]
- Pattern Y: 2/3 repos implement [solution]

### Divergent Patterns (unique approaches)
- Repo 1: [unique approach A]
- Repo 2: [unique approach B]

## Recommendations
### Use Repo 1 if:
- [Criteria/use case]

### Use Repo 2 if:
- [Criteria/use case]

### Use Repo 3 if:
- [Criteria/use case]

### Best of Breed:
- Adopt [pattern from Repo 1]
- Combine with [approach from Repo 2]
- Avoid [anti-pattern from Repo 3]
```

---

## Depth Levels

### Quick Scan (15-20 min equivalent)
- README analysis
- Metrics extraction (Step 1)
- Directory structure review
- Top 3 features identified
- High-level quality assessment
- Quick recommendations

### Standard Research (30-45 min equivalent)
- Full process (Steps 1-8)
- Key files examined
- Patterns documented
- Code quality assessed
- Community insights gathered
- Integration plan drafted

### Deep Dive (60+ min equivalent)
- Standard + code walkthrough of key features
- Dependency analysis
- Performance/security considerations
- Detailed implementation notes
- Example code extraction
- Risk assessment

Specify depth: `/repo-research <url> --depth=quick|standard|deep`

---

## Examples

### Example 1: Single Repo Research (UI Component Library)

```
sage: research repo https://github.com/example/component-lib

Focus: How do they handle theming and accessibility?
```

**Metrics extracted**:
- Stars: 12.5k (High interest)
- Last commit: 2 days ago (Active)
- Issues: 45 open / 890 closed (95% resolved - Healthy)
- Test coverage: 87% (Excellent)

**Report highlights**:
- CSS custom properties for theming
- ARIA attributes on all interactive components
- Keyboard navigation patterns
- Storybook for documentation

**Community insights**:
- Highly requested: Dark mode support (in progress)
- Maintainer notes performance prioritized over feature count

**Handoff to arch:**:
- Theme system pattern applicable to our flashcard styling
- Accessibility patterns for quiz interactions

---

### Example 2: Single Repo Research (Learning App)

```
/repo-research https://github.com/example/language-learner --depth=deep

Focus: Spaced repetition implementation and progress tracking
```

**Metrics extracted**:
- Stars: 3.2k (Medium interest)
- Forks: 450 (Moderate adoption)
- Last commit: 3 months ago (Maintained)
- Contributors: 23 (Moderate)

**Report highlights**:
- SM-2 algorithm implementation
- localStorage schema for progress
- Statistics visualization approach
- Gamification patterns

**Code quality**:
- Testing: Good (60% coverage, unit + integration tests)
- Documentation: Excellent (detailed README, API docs, examples)
- Architecture: Good (modular, clear separation)

**Handoff to pm:**:
- Spaced repetition as v1.0 feature candidate
- Progress dashboard inspiration

---

### Example 3: Multi-Repo Comparison (Flashcard Libraries)

```
/repo-research https://github.com/lib-a/flashcards https://github.com/lib-b/cards https://github.com/lib-c/memorize --compare
```

**Comparison highlights**:

| Metric | Lib A | Lib B | Lib C |
|--------|-------|-------|-------|
| Stars | 8k | 2k | 500 |
| Maintenance | Active | Stale | Active |
| Test Coverage | 90% | None | 45% |
| Documentation | Excellent | Fair | Good |

**Convergent patterns** (all 3 repos):
- Card flip animation using CSS transforms
- Keyboard shortcuts (Space = flip, Arrow = next/prev)

**Divergent patterns**:
- Lib A: Web Workers for spaced repetition calculation (unique)
- Lib B: Canvas-based rendering (unique, but abandoned)
- Lib C: Vue.js component (framework-specific)

**Recommendation**:
- **Use Lib A** for production (best maintained, excellent tests/docs)
- **Adopt pattern from Lib C**: Progress bar visualization is superior
- **Avoid Lib B approach**: Canvas rendering adds complexity without benefit

---

## Common Pitfalls

### Pitfall 1: Shallow Analysis
**Symptom**: Report only summarizes README
**Solution**: Actually explore code, not just docs

### Pitfall 2: Missing Context
**Symptom**: Patterns extracted without understanding constraints
**Solution**: Note why decisions were made, not just what

### Pitfall 3: Over-Engineering Recommendations
**Symptom**: Suggesting complex patterns for simple needs
**Solution**: Match recommendation complexity to our actual needs

### Pitfall 4: No Actionable Items
**Symptom**: Interesting findings but no clear next steps
**Solution**: Every section should connect to "what we could do"

---

## Checklist

### Single Repository Research

Before completing research:

- [ ] Repo overview captured (Step 1)
- [ ] Quantitative metrics extracted and assessed
- [ ] Structure analyzed (Step 2)
- [ ] Key features inventoried (Step 3)
- [ ] Code quality evaluated across 5 dimensions
- [ ] Patterns extracted (Step 4)
- [ ] Technologies assessed (Step 5)
- [ ] Integration opportunities identified (Step 6)
- [ ] Community insights gathered (Step 7)
- [ ] Report generated using template (Step 8)
- [ ] PM handoff message prepared
- [ ] Architect handoff message prepared
- [ ] Report saved to docs/research/

### Multi-Repository Comparison

Before completing comparison:

- [ ] All individual repos researched (Steps 1-6 each)
- [ ] Metrics comparison table created
- [ ] Feature matrix completed
- [ ] Convergent patterns identified (2+ repos)
- [ ] Divergent patterns noted (unique approaches)
- [ ] Best practices synthesized
- [ ] Anti-patterns identified
- [ ] Use case recommendations written (which repo for what)
- [ ] Best-of-breed recommendations provided
- [ ] Comparison report saved to docs/research/
- [ ] Individual repo reports saved (optional)
- [ ] Handoff messages prepared

---

## See Also

- `.claude/templates/repo-research-report-template.md` - Report template
- `.claude/agents/sage.md` - Sage persona definition
- `.claude/skills/learning-curation.md` - For post-research pattern extraction
- `docs/specs/` - Where PM creates PRDs from findings
- `docs/tdd/` - Where Architect creates TDDs from findings
