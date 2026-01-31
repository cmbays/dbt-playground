# Repo Research Command

Research an external repository and generate a learnings report for pm: and arch: handoff.

## Usage

```
/repo-research <github-url> [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--depth` | Research depth: `quick`, `standard`, `deep` | `standard` |
| `--focus` | Research question or specialist scope | none |
| `--parallel` | Enable multi-agent specialist research | off (on for deep) |
| `--specialists` | Specific specialists: `architect,security-reviewer,code-reviewer` | all (when parallel) |
| `--council` | Trigger council deliberation after research | off |
| `--skip-handoff` | Generate report without handoff messages | off |

## Examples

```bash
# Standard single-agent research
/repo-research https://github.com/dbt-labs/dbt-core

# Deep research with focus question
/repo-research https://github.com/dbt-labs/dbt-utils --depth=deep --focus="macro patterns"

# Quick evaluation
/repo-research https://github.com/example/dbt-project --depth=quick

# Parallel specialist mode (standard depth)
/repo-research https://github.com/dbt-labs/dbt-core --parallel

# Deep research (parallel is automatic)
/repo-research https://github.com/dbt-labs/dbt-core --depth=deep

# Parallel with specific specialists only
/repo-research https://github.com/owner/repo --parallel --specialists=architect,security-reviewer

# Full workflow with council deliberation
/repo-research https://github.com/owner/repo --depth=deep --council
```

## Workflow

### Standard Mode (Single Agent)

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

### Parallel Mode (Multi-Agent)

```
┌─────────────────────────────────────────────────────────────────┐
│  MASTER SAGE                                                    │
│                                                                 │
│  1. Parse URL → derive repo-name (owner-repo)                   │
│  2. Create artifact folder: temp/AGENT_REPORTS/[repo-name]/     │
│  3. Spawn specialists in parallel:                              │
│                                                                 │
│     ┌─────────────────┬─────────────────┬─────────────────┐    │
│     │   ARCHITECT     │   SECURITY      │   CODE QUALITY  │    │
│     │   --focus=arch  │   --focus=sec   │   --focus=qual  │    │
│     │                 │                 │                 │    │
│     │  • Structure    │  • Dependencies │  • Test coverage│    │
│     │  • Patterns     │  • Vulnerabilty │  • Documentation│    │
│     │  • Data flow    │  • Auth patterns│  • Maintainabil │    │
│     │  • Scalability  │  • Data handling│  • Code standard│    │
│     │                 │                 │                 │    │
│     │  ARCHITECT_     │  SECURITY_      │  QUALITY_       │    │
│     │  FOCUS.md       │  FOCUS.md       │  FOCUS.md       │    │
│     └─────────────────┴─────────────────┴─────────────────┘    │
│                                                                 │
│  4. Wait for specialists to complete                            │
│  5. Read all specialist reports                                 │
│  6. Synthesize master report: RESEARCH_MASTER.md                │
│     - Aggregate metrics and findings                            │
│     - Identify convergent/divergent perspectives                │
│     - Build combined risk matrix                                │
│     - Prioritize recommendations by domain                      │
│                                                                 │
│  7. (Optional) Council handoff if --council                     │
├─────────────────────────────────────────────────────────────────┤
│  OUTPUT: temp/AGENT_REPORTS/[repo-name]/                        │
│          ├── RESEARCH_MASTER.md                                 │
│          ├── ARCHITECT_FOCUS.md                                 │
│          ├── SECURITY_FOCUS.md                                  │
│          └── QUALITY_FOCUS.md                                   │
├─────────────────────────────────────────────────────────────────┤
│  HANDOFF OPTIONS                                                │
│                                                                 │
│  → pm:      Feature opportunities from all perspectives         │
│  → arch:    Architecture patterns with security/quality input   │
│  → council: Full deliberation on diverse specialist findings    │
└─────────────────────────────────────────────────────────────────┘
```

### Depth + Parallel Matrix

| Depth | Default Behavior | Parallel Available | Specialists |
|-------|------------------|-------------------|-------------|
| `quick` | Sage only | No | 0 |
| `standard` | Sage only | Yes (`--parallel`) | 0-2 |
| `deep` | Sage + specialists | Yes (default on) | 3 (full team) |

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

## Options Reference

| Option | Description | Values |
|--------|-------------|--------|
| `--depth` | Research depth | `quick`, `standard`, `deep` |
| `--focus` | Research question or specialist scope | string or `architecture`, `security`, `quality` |
| `--parallel` | Enable multi-agent specialist research | flag |
| `--specialists` | Specific specialists to include | `architect`, `security-reviewer`, `code-reviewer` |
| `--council` | Trigger council deliberation after research | flag |
| `--skip-handoff` | Generate report without handoff messages | flag |

## Output Locations

| Mode | Output Path |
|------|-------------|
| Standard (single-agent) | `docs/research/REPO-RESEARCH-[repo-name]-[date].md` |
| Parallel (multi-agent) | `temp/AGENT_REPORTS/[repo-name]/RESEARCH_MASTER.md` |
| Specialist focus reports | `temp/AGENT_REPORTS/[repo-name]/[ROLE]_FOCUS.md` |
| Council synthesis | `temp/AGENT_REPORTS/[repo-name]/COUNCIL_SYNTHESIS.md` |

## Related

- `.claude/skills/repo-research.md` - Full skill definition
- `.claude/templates/repo-research-report-template.md` - Report template
- `.claude/templates/specialist-focus-template.md` - Specialist focus report template
- `.claude/agents/sage.md` - Sage persona
- `.claude/skills/council.md` - Council skill for deliberation
- `/orchestrate` - For implementing findings
