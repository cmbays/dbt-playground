# Readiness Check Command

Assess capability gaps (knowledge, tools, experience) before committing to work.

## Usage

```
/readiness-check [task description]
```

## Examples

```
/readiness-check Add dbt_expectations tests to staging models
/readiness-check Implement customer LTV analytics mart
/readiness-check Integrate Tuva clinical data connector
/readiness-check Add Snowflake production deployment
```

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  READINESS CHECK                                            │
│                                                             │
│  1. Scope Extraction                                        │
│     - Parse request for technical requirements              │
│     - Identify domain and complexity                        │
│     - Extract search keywords                               │
│                                                             │
│  2. Knowledge Assessment (40%)                              │
│     - Search LEARNINGS.md for patterns                      │
│     - Check skills/ for workflows                           │
│     - Find prior implementations                            │
│                                                             │
│  3. Tools Assessment (30%)                                  │
│     - Verify packages in pyproject.toml                     │
│     - Check MCP server availability                         │
│     - Validate environment configuration                    │
│                                                             │
│  4. Experience Assessment (30%)                             │
│     - Search CHANGELOG for similar work                     │
│     - Count prior implementations                           │
│     - Assess novelty level                                  │
│                                                             │
│  5. Gap Analysis                                            │
│     - Classify gaps as BLOCKING vs ADVISORY                 │
│     - Calculate composite score                             │
│                                                             │
│  6. Decision                                                │
│     - READY (≥80): Proceed to /orchestrate                  │
│     - ADVISORY (60-79): Proceed with noted gaps             │
│     - RESEARCH_NEEDED (40-59): Research first               │
│     - BLOCKED (<40): Resolve blockers first                 │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: temp/READINESS_CHECK_[feature].md                  │
├─────────────────────────────────────────────────────────────┤
│  INTEGRATION                                                │
│                                                             │
│  Supervisor auto-invokes after scope clarification          │
│  Sage provides gap resolution research if needed            │
└─────────────────────────────────────────────────────────────┘
```

## Score Thresholds

| Score | Status | Next Action |
|-------|--------|-------------|
| 80-100 | READY | Proceed to `/orchestrate` |
| 60-79 | ADVISORY | Proceed with gaps noted |
| 40-59 | RESEARCH_NEEDED | Run `/repo-research` or `sage: research` |
| 0-39 | BLOCKED | Resolve blockers; await user decision |

## Options

| Option | Description |
|--------|-------------|
| `--dimension=knowledge\|tools\|experience` | Check single dimension only |
| `--verbose` | Show all search results |
| `--skip-output` | Don't write artifact file |

## Output

**Report Location**: `temp/READINESS_CHECK_[feature].md`

**Report Sections**:

1. Scope Summary
2. Knowledge Assessment (patterns, skills, prior art)
3. Tools Assessment (packages, MCP, environment)
4. Experience Assessment (CHANGELOG, prior work)
5. Gap Analysis (BLOCKING vs ADVISORY)
6. Recommendations and Next Steps

## Supervisor Integration

The Supervisor automatically runs `/readiness-check` at new request intake:

```
[New Request Received]
    │
    ├─ Clarify scope with user
    │
    ├─ Run /readiness-check [request]
    │
    ├─ READY → /orchestrate [feature]
    ├─ ADVISORY → Note gaps, /orchestrate with caution
    ├─ RESEARCH_NEEDED → Offer /repo-research or sage:
    └─ BLOCKED → Report, await user decision
```

## Gap Resolution

For RESEARCH_NEEDED results, use Sage for gap resolution:

```
sage: resolve gaps for [feature]
```

Sage will:

- Read the readiness check output
- Research identified gaps
- Extract patterns to LEARNINGS.md
- Recommend re-running readiness check

## Related

- `.claude/skills/readiness-check.md` - Full skill definition
- `.claude/agents/supervisor.md` - Supervisor integration
- `.claude/agents/sage.md` - Gap resolution workflow
- `/repo-research` - External repository research
- `/orchestrate` - Feature orchestration
