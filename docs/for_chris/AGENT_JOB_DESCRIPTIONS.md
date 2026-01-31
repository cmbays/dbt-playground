# Agent Job Descriptions

A plain-language guide to understanding what each agent does in our system.

## Quick Reference

| Agent | Human Job Title | One-Line Description |
|-------|-----------------|----------------------|
| supervisor | Project Coordinator | Makes sure nothing falls through the cracks between sessions |
| sage | Knowledge Librarian | Remembers what worked so we don't reinvent the wheel |
| git-master | Release Manager | Guards the codebase - no one commits without approval |
| pm | Product Manager | Defines what to build and why it matters |
| architect | Technical Architect | Designs how pieces fit together |
| dbt-developer | Data Engineer | Writes the SQL that transforms data |
| dbt-tester | QA Engineer | Makes sure the data is correct and complete |
| code-reviewer | Code Reviewer | Catches bugs and ensures code quality |
| security-reviewer | Security Analyst | Identifies vulnerabilities and risks |
| documenter | Technical Writer | Keeps documentation current and clear |
| data-modeler | Data Modeler | Designs the structure of dimensional models |

## Detailed Roles

### Supervisor (super:)

**Human Equivalent**: Project Coordinator / Scrum Master

**What They Do**:

- Opens each session asking "what are we working on today?"
- Keeps track of work-in-progress across sessions
- Makes sure each step is complete before moving to the next
- Queues urgent work without derailing current tasks
- Triggers learning extraction when things go right or wrong

**When to Invoke**:

- Starting a new work session: `super: starting new session`
- Resuming previous work: `super: resume`
- Checking status: `super: what's the current state?`
- Queueing urgent work: `super: queue fix for null handling bug`

**Example Prompts**:

```text
super: I'm starting a new session. What are we working on today?
super: Resume where we left off
super: What's in the queue?
```

---

### Sage (sage:)

**Human Equivalent**: Knowledge Manager / Lessons Learned Specialist

**What They Do**:

- Captures patterns that worked well
- Documents mistakes to avoid repeating
- Curates reusable solutions
- Extracts learnings from completed work

**When to Invoke**:

- After completing a difficult task
- When something failed unexpectedly
- When you discover a reusable pattern
- Before starting work similar to past projects

**Example Prompts**:

```text
sage: What did we learn from the last mart implementation?
sage: Extract learnings from this debugging session
sage: Is there a pattern for handling null values?
```

---

### Git-Master (git:)

**Human Equivalent**: Release Manager / Version Control Guardian

**Agent Type**: **Horizontal** (service agent used by all other agents, not a vertical workflow phase)

**What They Do**:

- Creates branches with proper naming
- Commits changes with good messages
- Creates and manages pull requests
- Enforces branch protection rules
- Prevents accidental destructive operations

**Core Principle**: *If we don't record what happened properly, we won't remember, and we won't improve.*

**Git-Centric Workflow**:

Git-master enforces a workflow where context lives in git and artifacts, not in session hand-offs:

| Practice | Why It Matters |
|----------|----------------|
| Open PRs early | All work visible in GitHub |
| Reviewers read from git | Not from session summaries |
| Post comments on PRs | Creates permanent record |
| Commit artifacts to repo | Enables cross-session learning |

**When to Invoke**:

- Creating a new branch: `git: create branch feat/new-feature`
- Committing changes: `/commit` or `git: commit these changes`
- Creating a PR: `git: create PR for this branch`

**Example Prompts**:

```text
git: create branch feat/customer-analytics
git: commit the staging model changes
git: what's the status of our branches?
```

---

### Product Manager (pm:)

**Human Equivalent**: Product Owner / Business Analyst

**What They Do**:

- Clarifies requirements and scope
- Writes Product Requirement Documents (PRDs)
- Creates GitHub issues
- Prioritizes features
- Defines acceptance criteria

**When to Invoke**:

- New feature idea: `pm: I want to add customer analytics`
- Clarifying scope: `pm: what should v0.4 include?`
- Creating issues: `pm: create an issue for this bug`

**Example Prompts**:

```text
pm: I want to add a customer analytics mart
pm: What's the priority for order metrics improvements?
pm: Scope out what v0.4 should include
```

---

### Technical Architect (arch:)

**Human Equivalent**: Systems Architect / Tech Lead

**What They Do**:

- Translates PRDs into technical designs
- Creates Technical Design Documents (TDDs)
- Evaluates implementation options
- Identifies risks and dependencies
- Ensures patterns are consistent

**When to Invoke**:

- Planning a new feature: `arch: design the architecture for...`
- Evaluating approaches: `arch: what's the best approach for...`
- Understanding structure: `arch: how does the current system handle...`

**Example Prompts**:

```text
arch: design the architecture for a customer analytics mart
arch: what's the best approach for incremental models?
arch: create a TDD for the order metrics feature
```

---

### dbt Developer (dbt-dev:)

**Human Equivalent**: Data Engineer / SQL Developer

**What They Do**:

- Implements SQL models from designs
- Writes efficient transformations
- Creates Jinja macros
- Handles incremental logic
- Optimizes query performance

**When to Invoke**:

- Implementing models: `dbt-dev: implement the stg_stripe__payments model`
- Adding features: `dbt-dev: add incremental logic to fct_orders`
- Creating macros: `dbt-dev: create a macro for currency conversion`

**Example Prompts**:

```text
dbt-dev: implement the stg_stripe__payments model
dbt-dev: fix the null handling in dim_customers
dbt-dev: optimize the int_orders__joined model
```

---

### dbt Tester (dbt-test:)

**Human Equivalent**: QA Engineer / Data Quality Analyst

**What They Do**:

- Defines schema tests for models
- Creates singular tests for business rules
- Configures source freshness monitoring
- Validates data quality constraints
- Monitors test coverage

**When to Invoke**:

- Adding tests: `dbt-test: add schema tests to stg_stripe__payments`
- Complex validation: `dbt-test: create a singular test for orphaned orders`
- Coverage review: `dbt-test: review test coverage for the orders mart`

**Example Prompts**:

```text
dbt-test: add schema tests to stg_stripe__payments
dbt-test: create a singular test for orphaned orders
dbt-test: configure source freshness for Shopify data
```

---

### Code Reviewer (review:)

**Human Equivalent**: Senior Developer / Code Quality Lead

**What They Do**:

- Reviews code for bugs and logic errors
- Checks adherence to project conventions
- Identifies maintainability issues
- Provides constructive feedback
- Approves or requests changes

**When to Invoke**:

- PR review: `/review --pr 42`
- Local review: `review: check the new staging model`
- Pattern review: `review: verify this follows our patterns`

**Example Prompts**:

```text
review: check the new staging model implementation
review: --pr 42 (posts review to GitHub)
review: audit the customer dimension for problems
```

---

### Security Reviewer (security:)

**Human Equivalent**: Security Analyst / AppSec Engineer

**What They Do**:

- Identifies security vulnerabilities
- Checks for OWASP Top 10 issues
- Evaluates data handling security
- Assesses third-party risks
- Provides remediation guidance

**When to Invoke**:

- Security audit: `security: review the new model for PII exposure`
- PR security: `security: --pr 42`
- Specific concerns: `security: check for SQL injection risks`

**Example Prompts**:

```text
security: review the new staging model implementation
security: check for PII exposure in mart models
security: audit database connection handling
```

---

### Documenter (docs:)

**Human Equivalent**: Technical Writer / Documentation Specialist

**What They Do**:

- Keeps documentation current
- Updates CHANGELOG
- Generates dbt docs
- Maintains README files
- Creates educational content

**When to Invoke**:

- After feature completion: `docs: update CHANGELOG for PR #42`
- Documentation updates: `docs: update the README`
- dbt docs: `docs: regenerate dbt documentation`

**Example Prompts**:

```text
docs: update CHANGELOG for the new mart feature
docs: regenerate dbt documentation
docs: add usage examples to the README
```

---

### Data Modeler (dbt-model:)

**Human Equivalent**: Data Architect / Dimensional Modeler

**What They Do**:

- Designs dimensional model structure
- Defines naming conventions
- Maps relationships between entities
- Designs fact and dimension tables
- Applies Kimball methodology

**When to Invoke**:

- Designing models: `dbt-model: design the customer dimension`
- Relationship mapping: `dbt-model: map the order-customer relationship`
- Grain definition: `dbt-model: define the grain for fct_orders`

**Example Prompts**:

```text
dbt-model: design the customer dimension with SCD Type 2
dbt-model: what's the right grain for the orders fact table?
dbt-model: create a model design for claims processing
```

---

## Decision Tree: Which Agent Do I Need?

**"I want to..."**

| Goal | Agent | Example |
|------|-------|---------|
| Start or resume work | Supervisor | `super: resume` |
| Define what to build | PM | `pm: scope out the new feature` |
| Design how to build it | Architect | `arch: design the architecture` |
| Plan model structure | Data Modeler | `dbt-model: design the dimension` |
| Write the SQL | dbt Developer | `dbt-dev: implement the model` |
| Add tests | dbt Tester | `dbt-test: add tests` |
| Review code quality | Code Reviewer | `/review --pr N` |
| Check security | Security Reviewer | `security: audit for risks` |
| Update docs | Documenter | `docs: update CHANGELOG` |
| Commit changes | Git-Master | `/commit` |
| Learn from experience | Sage | `sage: extract learnings` |

---

## How Agents Work Together

```
User Request
     │
     ▼
[Supervisor] ──── Clarifies scope, creates track
     │
     ▼
[PM] ──────────── Writes PRD, creates PM_REPORT
     │
     ▼
[Architect] ───── Reads PM_REPORT, writes TDD, creates ARCH_REPORT
     │
     ▼
[Data Modeler] ── Designs dimensional model
     │
     ▼
[dbt Tester] ──── Reads reports, writes TEST_SPEC
     │
     ▼
[dbt Developer] ─ Reads all reports, implements, writes DEV_REPORT
     │
     ▼
[Code Reviewer] ─ Reviews, writes CODE_REVIEW
     │
     ▼
[Documenter] ──── Updates docs, CHANGELOG
     │
     ▼
[Git-Master] ──── Commits, creates PR, merges
     │
     ▼
[Sage] ────────── Extracts learnings
```

---

## Related

- [Supervisor Orchestration](SUPERVISOR_ORCHESTRATION.md) - Full supervisor workflow
- [PR Workflow](UNDERSTANDING_PR_WORKFLOW.md) - Git and PR process
- [Agent System](.claude/agents/AGENTS.md) - Technical agent documentation
