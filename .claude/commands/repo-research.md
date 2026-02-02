# Repo Research Command

Research an external repository and generate a learnings report for pm: and arch: handoff.

## Usage

```
/repo-research <github-url> [--depth=quick|standard|deep] [--focus="research question"]
```

## Examples

```
/repo-research https://github.com/dbt-labs/dbt-core
/repo-research https://github.com/dbt-labs/dbt-utils --depth=deep --focus="macro patterns"
/repo-research https://github.com/example/dbt-project --depth=quick
```

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  SAGE PERSONA                                               │
│                                                             │
│  1. Repository Overview                                     │
│     - Fetch repo metadata and README                        │
│     - Identify purpose, stack, maturity                     │
│                                                             │
│  2. Structure Analysis                                      │
│     - Directory organization                                │
│     - Architecture patterns                                 │
│     - Naming conventions                                    │
│                                                             │
│  3. Feature Inventory                                       │
│     - List major features                                   │
│     - Assess implementation quality                         │
│     - Note relevance to our project                         │
│                                                             │
│  4. Pattern Extraction                                      │
│     - Code patterns                                         │
│     - Architecture patterns                                 │
│     - Workflow patterns                                     │
│                                                             │
│  5. Integration Assessment                                  │
│     - Identify adoption opportunities                       │
│     - Assess complexity and risks                           │
│     - Prioritize recommendations                            │
│                                                             │
│  6. Generate Report                                         │
│     - Use standardized template                             │
│     - Include actionable recommendations                    │
│     - Prepare handoff messages                              │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: docs/research/REPO-RESEARCH-[name]-[date].md       │
├─────────────────────────────────────────────────────────────┤
│  HANDOFF OPTIONS                                            │
│                                                             │
│  → pm:   Feature opportunities, user value, priorities      │
│  → arch: Architecture patterns, technical decisions, TDDs   │
└─────────────────────────────────────────────────────────────┘
```

## Depth Levels

| Level | Scope | Best For |
|-------|-------|----------|
| `quick` | README + structure | Initial evaluation |
| `standard` | Full analysis | Feature planning |
| `deep` | Code walkthrough | Implementation prep |

Default: `standard`

## Output

**Report Location**: `docs/research/REPO-RESEARCH-[repo-name]-[YYYY-MM-DD].md`

**Report Sections**:

1. Executive Summary
2. Repository Overview
3. Project Structure
4. Architecture Patterns
5. Feature Analysis
6. Integration Opportunities
7. Technology Assessment
8. Risks & Concerns
9. Recommendations (for PM and Architect)
10. Action Items

## Handoff Protocol

After research completes, Sage provides handoff messages for:

**Product Manager (pm:)**

- Feature opportunities with user value
- Priority recommendations
- Questions for scope decisions

**Technical Architect (arch:)**

- Architecture patterns to consider
- TDD candidates
- Technical concerns and tradeoffs

## Options

| Option | Description |
|--------|-------------|
| `--depth` | Research depth: quick, standard, deep |
| `--focus` | Specific research question or area |
| `--skip-handoff` | Generate report without handoff messages |

## Related

- `.claude/skills/repo-research.md` - Full skill definition
- `.claude/templates/repo-research-report-template.md` - Report template
- `.claude/agents/sage.md` - Sage persona
- `/orchestrate` - For implementing findings
