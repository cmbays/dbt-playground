---
name: readiness-checker
tools: Read, Glob, Grep, Bash
model: sonnet
description: Assess capability gaps (knowledge, tools, experience) before committing to work. Returns READY, ADVISORY, RESEARCH_NEEDED, or BLOCKED with detailed gap analysis.
---

# Readiness Check Skill

**Purpose**: Assess capability gaps (knowledge, tools, experience) before committing to work, enabling informed decisions about proceeding, researching, or requesting clarification.

**Owner**: Supervisor persona (auto-invocation), any agent (manual)

**Invocation**: `/readiness-check [task description]` or automatic via Supervisor at new request intake

---

## When to Use

**Automatic Triggers** (Supervisor-managed):

- New feature request received
- After scope clarification, before `/orchestrate`
- When user provides ambiguous or complex requirements

**Manual Triggers**:

- Before committing to unfamiliar work
- When uncertain about tool availability
- Before estimating effort for new integrations
- When onboarding to new domain areas

**Do NOT use for**:

- Simple, well-understood tasks (typo fixes, minor edits)
- Tasks already in progress with validated context
- Pure documentation or research tasks

---

## Assessment Dimensions

The readiness check evaluates three dimensions, each contributing to an overall score:

### 1. Knowledge Assessment (40% weight)

**What to Check**:

- `docs/reference/LEARNINGS.md` - Proven patterns matching the task
- `.claude/skills/` - Existing skills for similar workflows
- `docs/specs/ADR_INDEX.md` - Relevant architecture decisions
- `docs/for_chris/` - Educational materials on the domain
- Prior art in codebase - Similar implementations

**Search Commands**:

```bash
# Search LEARNINGS.md for relevant patterns
grep -i "[keywords]" docs/reference/LEARNINGS.md

# Find related skills
ls .claude/skills/ | grep -i "[domain]"

# Search for prior implementations
grep -r "[pattern]" models/ --include="*.sql"
```

**Scoring Rubric**:

| Condition | Score |
|-----------|-------|
| Multiple proven patterns documented | 36-40 |
| One or more relevant patterns found | 28-35 |
| Related but not exact patterns | 16-27 |
| No relevant patterns found | 0-15 |

---

### 2. Tools Assessment (30% weight)

**What to Check**:

- `pyproject.toml` - Required packages installed
- MCP servers available - External integrations needed
- Environment configuration - Secrets, connections
- CLI tools - Required executables present

**Verification Commands**:

```bash
# Check pyproject.toml for packages
grep -E "dbt|pandas|[package]" pyproject.toml

# Check MCP servers
cat ~/.claude/settings.json | grep -i mcp

# Verify CLI tools
which gh dbt uv

# Check dbt connection
uv run dbt debug --quiet
```

**Scoring Rubric**:

| Condition | Score |
|-----------|-------|
| All required tools present and configured | 27-30 |
| Most tools present, minor config needed | 20-26 |
| Some tools missing, installable | 10-19 |
| Critical tools missing or unavailable | 0-9 |

---

### 3. Experience Assessment (30% weight)

**What to Check**:

- `CHANGELOG.md` - Similar work completed before
- Pattern maturity - How often has this been done
- Novelty level - First-time vs routine work
- Complexity indicators - Multi-agent vs single-agent

**Search Commands**:

```bash
# Check CHANGELOG for similar features
grep -i "[feature-type]" CHANGELOG.md

# Count similar models
ls models/staging/ | wc -l

# Check for related PRs
gh pr list --state merged --search "[keywords]" --limit 5
```

**Scoring Rubric**:

| Condition | Score |
|-----------|-------|
| Routine work with 5+ prior examples | 27-30 |
| Familiar pattern with 2-4 examples | 20-26 |
| Partially novel with 1 example | 10-19 |
| Completely novel, no prior examples | 0-9 |

---

## Workflow Phases

### Phase 1: Scope Extraction

**Input**: Task description from user

**Process**:

1. Parse request for technical requirements
2. Identify domain areas (dbt, Python, integrations)
3. Extract key terms for searching
4. Classify complexity (simple, moderate, complex)

**Output**: Structured scope summary

```markdown
## Scope Summary
- **Domain**: [dbt/python/integration/etc]
- **Key Terms**: [extracted keywords]
- **Complexity**: [simple/moderate/complex]
- **Dependencies**: [identified dependencies]
```

---

### Phase 2: Knowledge Assessment

**Process**:

1. Search LEARNINGS.md for pattern matches
2. Search skills/ for workflow matches
3. Search ADR_INDEX for architectural guidance
4. Search codebase for prior implementations
5. Calculate knowledge score

**Commands**:

```bash
# Pattern search
grep -i "[term1]\|[term2]" docs/reference/LEARNINGS.md
grep -l "[term]" .claude/skills/*.md
grep -r "[pattern]" models/ --include="*.sql" | head -5
```

---

### Phase 3: Tool Assessment

**Process**:

1. Identify required packages from scope
2. Check pyproject.toml for presence
3. Verify MCP servers if needed
4. Check environment configuration
5. Calculate tool score

**Commands**:

```bash
# Package check
grep -E "[package1]|[package2]" pyproject.toml

# MCP check (if integration needed)
cat ~/.claude/settings.json 2>/dev/null | grep -c mcp || echo "0"

# Environment check
env | grep -E "DBT|DATABASE|API" | wc -l
```

---

### Phase 4: Experience Assessment

**Process**:

1. Search CHANGELOG for similar work
2. Count prior implementations
3. Assess novelty level
4. Identify complexity factors
5. Calculate experience score

**Commands**:

```bash
# CHANGELOG search
grep -c -i "[feature-type]" CHANGELOG.md

# Count similar implementations
find models/ -name "*[pattern]*" | wc -l
```

---

### Phase 5: Gap Analysis

**Process**:

1. Compile scores from all dimensions
2. Calculate composite score
3. Identify specific gaps
4. Classify gaps as BLOCKING or ADVISORY

**Gap Classification**:

| Gap Type | Classification | Example |
|----------|----------------|---------|
| Missing critical tool | BLOCKING | No dbt adapter for target database |
| Missing package | ADVISORY | Can install with `uv add` |
| No patterns documented | ADVISORY | Need research, not blocked |
| No prior experience | ADVISORY | Higher effort, not blocked |
| Missing MCP server | BLOCKING (if required) | External API integration |
| Security/compliance unknown | BLOCKING | Needs clarification |

---

### Phase 6: Decision & Output

**Score Thresholds**:

| Score Range | Status | Action |
|-------------|--------|--------|
| 80-100 | READY | Proceed to `/orchestrate` |
| 60-79 | ADVISORY | Note gaps, proceed with caution |
| 40-59 | RESEARCH_NEEDED | Recommend `/repo-research` or `sage:` |
| 0-39 | BLOCKED | Report blockers, await user decision |

**Output Artifact**: `temp/READINESS_CHECK_[feature].md`

---

## Output Artifact Template

```markdown
# Readiness Check: [Feature Name]

**Generated**: [timestamp]
**Status**: [READY | ADVISORY | RESEARCH_NEEDED | BLOCKED]
**Composite Score**: [X]/100

---

## Scope Summary

- **Request**: [original request summary]
- **Domain**: [identified domain]
- **Complexity**: [simple | moderate | complex]
- **Key Terms**: [term1, term2, term3]

---

## Assessment Results

### Knowledge (Weight: 40%)
**Score**: [X]/40

| Check | Result | Notes |
|-------|--------|-------|
| LEARNINGS.md patterns | [X found] | [relevant patterns] |
| Skills available | [X found] | [skill names] |
| ADR guidance | [yes/no] | [ADR references] |
| Prior implementations | [X found] | [file paths] |

**Gaps**:
- [ ] [Gap description] — [BLOCKING/ADVISORY]

### Tools (Weight: 30%)
**Score**: [X]/30

| Check | Result | Notes |
|-------|--------|-------|
| Packages present | [yes/no] | [missing packages] |
| MCP servers | [N/A or status] | [server names] |
| Environment config | [yes/no] | [missing config] |
| CLI tools | [yes/no] | [missing tools] |

**Gaps**:
- [ ] [Gap description] — [BLOCKING/ADVISORY]

### Experience (Weight: 30%)
**Score**: [X]/30

| Check | Result | Notes |
|-------|--------|-------|
| Prior similar work | [X instances] | [CHANGELOG refs] |
| Pattern maturity | [routine/partial/novel] | [assessment] |
| Complexity factors | [list] | [multi-agent, etc] |

**Gaps**:
- [ ] [Gap description] — [BLOCKING/ADVISORY]

---

## Recommendations

### Immediate Actions
1. [Action if READY or ADVISORY]

### Research Needed (if applicable)
- [ ] [Research topic] — `/repo-research [url]` or `sage: [query]`

### Blockers (if applicable)
- [ ] [Blocker description] — Requires: [user decision/tool install/clarification]

---

## Decision

**Status**: [READY | ADVISORY | RESEARCH_NEEDED | BLOCKED]

**Next Step**:
- [READY] Proceed to `/orchestrate [feature]`
- [ADVISORY] Proceed with noted gaps; monitor for issues
- [RESEARCH_NEEDED] Run `/repo-research` or `sage: research` first
- [BLOCKED] Resolve blockers before proceeding; user decision required
```

---

## Integration Points

### Supervisor Integration

The Supervisor invokes `/readiness-check` automatically:

```
[After Scope Clarification]
    │
    ├─ Run /readiness-check [request]
    │
    ├─ READY (≥80) → Proceed to /orchestrate
    ├─ ADVISORY (60-79) → Note gaps, proceed with caution
    ├─ RESEARCH_NEEDED (40-59) → Offer /repo-research or sage:
    └─ BLOCKED (<40) → Report blockers, await user decision
```

### Sage Integration

For RESEARCH_NEEDED results, Sage can perform gap resolution:

```
sage: resolve gaps for [feature]
    - Read: temp/READINESS_CHECK_[feature].md
    - Research identified gaps
    - Update LEARNINGS.md with findings
    - Re-assess readiness
```

### WORKFLOW_STATE.md Recording

When readiness check completes, Supervisor records result:

```yaml
### Track: feat/example-feature (ACTIVE)
- **Readiness Check**: 2026-01-31T10:00:00Z
- **Readiness Score**: 75/100 (ADVISORY)
- **Gaps Noted**: Missing dbt_expectations patterns
```

---

## Examples

### Example 1: READY Path

**Request**: "Add unique test to existing staging model"

**Assessment**:

- Knowledge: 38/40 (many testing patterns in LEARNINGS.md)
- Tools: 30/30 (all dbt tools present)
- Experience: 28/30 (100+ tests already exist)
- **Total: 96/100 — READY**

**Output**: Proceed to orchestrate immediately.

---

### Example 2: ADVISORY Path

**Request**: "Add dbt_expectations tests to staging models"

**Assessment**:

- Knowledge: 25/40 (dbt testing patterns exist, dbt_expectations not documented)
- Tools: 22/30 (dbt_expectations not in pyproject.toml but installable)
- Experience: 15/30 (no prior dbt_expectations usage)
- **Total: 62/100 — ADVISORY**

**Gaps**:

- [ ] dbt_expectations not installed — ADVISORY (installable)
- [ ] No documented patterns for dbt_expectations — ADVISORY (can research)

**Output**: Proceed with gaps noted; recommend installing package first.

---

### Example 3: RESEARCH_NEEDED Path

**Request**: "Implement Tuva clinical data mart integration"

**Assessment**:

- Knowledge: 15/40 (no Tuva patterns documented)
- Tools: 20/30 (healthcare connectors not configured)
- Experience: 8/30 (no prior Tuva work)
- **Total: 43/100 — RESEARCH_NEEDED**

**Gaps**:

- [ ] No Tuva patterns in LEARNINGS.md — ADVISORY
- [ ] Healthcare connector MCP not configured — BLOCKING (if required)
- [ ] No prior Tuva implementations — ADVISORY

**Output**: Recommend `/repo-research https://github.com/tuva-health/tuva` first.

---

### Example 4: BLOCKED Path

**Request**: "Add Snowflake connector for production deployment"

**Assessment**:

- Knowledge: 20/40 (some Snowflake patterns exist)
- Tools: 5/30 (dbt-snowflake not installed, no credentials)
- Experience: 10/30 (no Snowflake usage in project)
- **Total: 35/100 — BLOCKED**

**Gaps**:

- [ ] dbt-snowflake adapter not installed — BLOCKING
- [ ] Snowflake credentials not configured — BLOCKING
- [ ] No Snowflake account provisioned — BLOCKING

**Output**: Cannot proceed. User must provision Snowflake and configure credentials.

---

## Command-Line Options

```
/readiness-check [task description]
    --dimension=knowledge|tools|experience  # Check single dimension only
    --verbose                               # Show all search results
    --skip-output                          # Don't write artifact file
```

---

## Checklist

Before completing readiness check:

- [ ] Scope extracted from request
- [ ] Knowledge assessment completed (LEARNINGS, skills, prior art)
- [ ] Tools assessment completed (packages, MCP, environment)
- [ ] Experience assessment completed (CHANGELOG, prior work)
- [ ] Gaps classified as BLOCKING or ADVISORY
- [ ] Composite score calculated
- [ ] Status determined (READY/ADVISORY/RESEARCH_NEEDED/BLOCKED)
- [ ] Artifact written to `temp/READINESS_CHECK_[feature].md`
- [ ] Handoff to Supervisor or next action recommended

---

## See Also

- `.claude/commands/readiness-check.md` - Command reference
- `.claude/agents/supervisor.md` - Supervisor integration
- `.claude/agents/sage.md` - Gap resolution research
- `.claude/skills/repo-research.md` - External repository research
- `docs/reference/LEARNINGS.md` - Pattern reference
