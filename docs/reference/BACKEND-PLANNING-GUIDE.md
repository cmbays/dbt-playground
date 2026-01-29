# Backend Infrastructure Planning Guide

**Purpose**: Guide PM and Architect personas through reviewing and improving the backend infrastructure plan.

**Status**: Initial framework ready for iteration
**Created**: 2026-01-25

---

## Overview

Two documents have been created to plan backend infrastructure and agent splitting:

1. **PRD-006**: Backend Infrastructure Setup (Product Requirements)
2. **TDD-006**: Backend Infrastructure Design (Technical Design)

These documents are intentionally incomplete frameworks. PM and Architect personas should collaborate to:
- Research actual technology options
- Fill in decision rationale
- Resolve open questions
- Create a finalized, actionable plan

---

## Collaboration Workflow

### Phase 1: PM Review of PRD-006 (Product Manager)

**Time**: 1-2 sessions

**PM Tasks**:

1. **Resolve Business Questions**
   - What's the MVP scope? (Basic progress tracking only? + Spaced rep?)
   - Authentication approach? (Username/password? OAuth later?)
   - Data migration strategy? (How to migrate existing localStorage data?)
   - Cost model? (Will there be account limits?)

2. **Refine User Stories**
   - Are the user stories in PRD-006 correct?
   - Should we add more (social features, analytics)?
   - Are JLPT level considerations complete?

3. **Finalize Acceptance Criteria**
   - Current criteria are placeholders; make them specific
   - Define "done" measurably
   - Link to tech decisions that will be made in TDD

4. **Create GitHub Issue**
   - Link PRD-006 to a GitHub issue for tracking
   - Add labels: `type:backend`, `status:planning`
   - Link to this guide

5. **Note for Architect**
   - When PRD is approved, add section: "PM Approved On: YYYY-MM-DD"
   - Document any constraints PM discovered (budget, timeline, user expectations)

### Phase 2: Architect Research & TDD-006 (Architect/Technical Architect)

**Time**: 1-2 sessions

**Architect Tasks**:

1. **Research Technology Options**
   - Option A: Node.js/Express/PostgreSQL/VPS
     - Find 2-3 real examples of similar projects
     - Research cost, scaling limits, DevOps complexity
   - Option B: Python/FastAPI/PostgreSQL/VPS
     - Same research; compare with Option A
   - Option C: Serverless (Firebase/Supabase)
     - Cost analysis, scaling behavior, vendor lock-in implications
   - Option D: Next.js API Routes + Vercel
     - API route best practices, cold start latency, cost at scale

2. **Flesh Out Options in TDD-006**
   - Replace placeholder "Pros" and "Cons" with real findings
   - Add complexity assessment
   - Include cost estimates (research actual pricing)
   - Reference where you found the information

3. **Make a Recommendation**
   - Fill "Decision Rationale" section
   - Explain why selected option beats others
   - Call out tradeoffs being accepted
   - Reference project philosophy: "Leave it better than you found it"

4. **Detail the Architecture**
   - Create `TDD-006-architecture.d2` file with D2 diagram
   - Finalize data structures (schema)
   - Detail API endpoints (HTTP verbs, request/response bodies)
   - Specify file structure for new `backend/` directory

5. **Resolve Open Questions**
   - Spaced rep algorithm: Research SM-2 vs. Anki vs. Leitner
   - Make recommendation with rationale
   - Data migration: Propose specific strategy
   - Scaling: At what point does architecture need rework?

6. **Document Integration Points**
   - How does frontend call backend?
   - How does backend maintain consistency with frontend data formats?
   - What existing patterns should backend adopt?

### Phase 3: Joint Review (PM + Architect)

**Time**: 1 session (30-60 min)

**Participants**: PM and Architect personas (or Christopher if real humans)

**Agenda**:

1. **PRD Review** (10 min)
   - PM walks through approved PRD and open questions
   - Architect clarifies technical implications
   - Agree on MVP scope

2. **TDD Review** (20 min)
   - Architect presents technology recommendation
   - Show cost/scaling analysis for top 2 options
   - Discuss DevOps burden (who maintains this?)

3. **Integration Planning** (15 min)
   - How does this unlock future features?
   - What data models need to be stable?
   - Agent splitting: When exactly does this happen?

4. **Approval & Handoff** (5 min)
   - Add approval stamps to both documents
   - Document any decisions made during review
   - Assign owner for next phase (Backend Developer)

### Phase 4: Developer Implementation (Future)

When backend work begins:

1. **Backend Developer** claims TDD-006 and implements according to spec
2. **Frontend Developer** extracts API contract from TDD-006
3. **Both coordinate** on integration and testing
4. **Code Reviewer** establishes backend testing standards

---

## Document Sections Requiring Completion

### PRD-006 Completion Checklist

- [ ] **Problem Statement**: Verified correct?
- [ ] **Open Questions** (Lines ~110-122): PM should answer or defer
  - MVP Scope
  - Authentication approach
  - Data migration
  - Rollout strategy
  - Cost model
  - Social features schema
- [ ] **Acceptance Criteria** (Lines ~76-84): Make specific and measurable
- [ ] **Success Metrics** (Lines ~95-103): Refine to be observable
- [ ] **Dependencies** (Lines ~104-111): Finalize and reorder by criticality
- [ ] **Revision History**: Add entry when PM completes review

### TDD-006 Completion Checklist

- [ ] **Alternative Approaches** (Lines ~55-125): Research and document real options
  - Fill in actual frameworks/databases for each option
  - Research real cost estimates
  - Document actual tradeoffs discovered
- [ ] **Decision Rationale** (Lines ~128-141): Which option? Why?
- [ ] **Architecture Diagram**: Create `TDD-006-architecture.d2`
- [ ] **Data Structures** (Lines ~195-245): Finalize database schema
- [ ] **API Design** (Lines ~260-290): Complete endpoint specifications
- [ ] **Implementation Sequence** (Lines ~292-320): Refine with realistic ordering
- [ ] **Open Questions** (Lines ~347-365): Architect research and resolve
- [ ] **Revision History**: Add entry when Architect completes review

---

## Key Decision Points

### Technology Stack Axes (Architect)

**Framework**:
- Node.js/Express (familiar to frontend team)
- Python/FastAPI (great for algorithms, different language)
- Go (fast, compiled, unfamiliar)
- Rust (extremely safe, steep learning curve)

**Decision Criteria**:
- Team's existing language skills
- Ecosystem maturity
- DevOps simplicity
- Performance needs

**Cost Impact**: Minimal (same hosting cost)
**Learning Curve Impact**: High (team skills vs. new language)

---

**Database**:
- PostgreSQL (relational, robust, industry standard)
- MongoDB (document-based, more flexible schema)
- Firebase (fully managed, easiest to operate)

**Decision Criteria**:
- Data structure complexity
- Scaling plan
- Backup/recovery importance
- DevOps overhead tolerance

**Cost Impact**: Low-Medium (Firebase could be expensive at scale)
**DevOps Impact**: High (self-hosted needs backups, monitoring)

---

**Hosting**:
- VPS (DigitalOcean, Linode): $5-20/month
- Vercel/Railway: $0-50/month
- AWS/GCP: Pay-per-use, can scale to $1000+

**Decision Criteria**:
- Expected user count
- DevOps skills available
- Cost tolerance
- Scaling needs

**Cost Impact**: High (can range 10x)
**DevOps Impact**: High (self-hosted needs monitoring)

---

### Agent Splitting Decision (PM/Architect)

**Trigger**: When backend infrastructure work begins

**Impact**: Creates separate `backend-dev:` persona

**Decision**: Already made (see PRD-006 Agent Splitting Strategy section)

---

## Common Pitfalls & How to Avoid

### Pitfall 1: Over-Engineering for Scale
**How it happens**: Choosing Kubernetes/microservices for MVP
**Prevention**: Start simple (VPS + PostgreSQL), scale when needed
**Guidance**: Architect should recommend what supports 1K-10K users, not 1M

### Pitfall 2: Technology Churn
**How it happens**: Rewriting backend in different language mid-project
**Prevention**: Research thoroughly before selection, commit to choice
**Guidance**: Architect should document why alternatives were rejected

### Pitfall 3: Incomplete Data Migration
**How it happens**: Users sign up, localStorage data is lost
**Prevention**: Design migration strategy in advance, test thoroughly
**Guidance**: PRD-006 should answer data migration question clearly

### Pitfall 4: Agent Splitting Too Early
**How it happens**: Splitting dev team before backend is needed
**Prevention**: This guide documents trigger point (infrastructure decision made)
**Guidance**: Don't split until there's actual backend code to write

### Pitfall 5: API Contract Drift
**How it happens**: Frontend and backend disagree on API format
**Prevention**: Document API spec in TDD-006 before implementation starts
**Guidance**: Make API spec the contract; code should follow spec, not vice-versa

---

## For Future Sessions

If you're continuing this work:

1. **Check document status**: Are PRD-006 and TDD-006 still marked "Draft"?
2. **Read Open Questions**: These are the decision points that block progress
3. **Follow the workflow**: PM review → Architect research → Joint decision
4. **Document decisions**: Always update the revision history sections
5. **Create GitHub issue**: Link documents to tracking issue

---

## Quick Reference: What Gets Decided When?

| Decision | Owner | When | Documented In |
|----------|-------|------|----------------|
| MVP scope (features) | PM | Phase 1 | PRD-006 Open Questions |
| Technology stack | Architect | Phase 2 | TDD-006 Decision Rationale |
| API design | Architect | Phase 2 | TDD-006 API Design |
| Cost budget | PM | Phase 1 | PRD-006 Dependencies |
| Agent split timing | Both | Phase 3 | PRD-006 Agent Splitting Strategy |
| Data migration approach | Architect | Phase 2 | TDD-006 Implementation Sequence |

---

## Success Criteria

When both documents are ready for handoff to Backend Developer:

- [ ] PRD-006 approved by PM (section "Approved On: DATE" added)
- [ ] All Open Questions in PRD-006 answered (or explicitly deferred to future)
- [ ] TDD-006 approved by Architect (section "Approved On: DATE" added)
- [ ] Technology stack selected with clear rationale
- [ ] API design documented and reviewed
- [ ] Database schema finalized
- [ ] Architecture diagram exists (TDD-006-architecture.d2)
- [ ] GitHub issue created linking both documents
- [ ] Backend Developer persona can start work without ambiguity

---

## Questions?

If either document is unclear:
1. Check the CLAUDE.md for persona definitions
2. Check the git history for similar decisions (architecture decisions in past)
3. Reference the PRD templates and TDD templates in same directories

Remember: This is a living document. Update it as the process evolves.
