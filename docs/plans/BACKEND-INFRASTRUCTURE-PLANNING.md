# Backend Infrastructure Planning: User Accounts & Persistence (Phase 3+)

## Overview

Plan for building backend infrastructure to support user accounts, progress tracking, and spaced repetition scheduling. This work will unlock:

- Cross-device synchronization
- Personalized learning schedules
- Future premium features (social, analytics)
- Foundation for long-term user retention

**Current Status**: Planning Phase (PM & Architect Review)
**Trigger Point**: When frontend reaches feature maturity (kanji study complete, dashboard stable)
**Target Version**: v1.0.0 or v2.0.0 (requires architecture review)
**Created**: 2026-01-25
**Updated**: 2026-01-25
**Documentation**:

- [PRD-006: Backend Infrastructure Setup](../specs/PRD-006-Backend-Infrastructure-Setup.md)
- [TDD-006: Backend Infrastructure Design](../tdd/TDD-006-Backend-Infrastructure.md)
- [Backend Planning Guide](../reference/BACKEND-PLANNING-GUIDE.md)

---

## Problem & Opportunity

### Current State (v0.2-v0.4)

- ✅ Rich frontend: kanji flashcards, engagement gamification, progress visualization
- ❌ Data lives only in localStorage (lost on device change, cleared on cache flush)
- ❌ No accounts: can't identify users, no progress persistence
- ❌ No scheduling: users manually pick what to study (inefficient)

### Future State (v1.0+)

- ✅ Persistent accounts (signup/login)
- ✅ Server-side progress tracking (sync across devices)
- ✅ Spaced repetition scheduling (SM-2 algorithm or similar)
- ✅ Personalized lesson plans (adapt to user pace)
- ✅ Foundation for premium features

---

## Planning Phases

This is **not immediate work**. It follows a deliberate review process with multiple personas.

### Phase 1: PM Business Planning (1-2 Sessions)

**Owner**: Product Manager persona
**Duration**: 1-2 sessions
**Input**: PRD-006 (skeleton)
**Output**: PRD-006 (approved), GitHub issue, scope definition

**PM Tasks**:

1. Answer critical business questions (see PRD-006 Open Questions):
   - What's MVP scope? (Progress tracking? + Spaced rep?)
   - Authentication approach? (Username/password only? OAuth future?)
   - Data migration strategy? (How to preserve existing localStorage data?)
   - Cost model? (Will there be account limits? Premium tiers?)
   - Rollout strategy? (Mandatory signup? Opt-in? Gradual?)

2. Refine user stories and acceptance criteria
   - Make criteria specific and testable
   - Define success metrics (adoption rate, data integrity, API performance)

3. Create GitHub issue with epic scope
   - Link PRD-006
   - Label: `type:backend`, `status:planning`, `epic`
   - Add to project board

4. Handoff: "PRD is approved, ready for Architect"

**Blockers**: None (this is pure product thinking)

**Approval Stamp**: When complete, PRD-006 gets "Approved By: [PM] On: YYYY-MM-DD"

---

### Phase 2: Architect Technical Research (1-2 Sessions)

**Owner**: Technical Architect persona
**Duration**: 1-2 sessions
**Input**: PRD-006 (approved), TDD-006 (skeleton)
**Output**: TDD-006 (approved with tech recommendations), architecture diagram

**Architect Tasks**:

1. **Research technology options** (4 main paths):
   - **Option A**: Node.js/Express/PostgreSQL/VPS
     - Familiar JS ecosystem, full control, standard approach
     - Research: cost, DevOps burden, scaling limits

   - **Option B**: Python/FastAPI/PostgreSQL/VPS
     - Great for algorithms (spaced rep), different language
     - Research: ecosystem, learning curve, DevOps

   - **Option C**: Serverless (Firebase/Supabase/Next.js Vercel)
     - Minimal ops, auto-scaling, fast time-to-market
     - Research: vendor lock-in, costs at scale, flexibility

   - **Option D**: Next.js API Routes + Vercel
     - Unified stack (frontend+backend same repo), easy deployment
     - Research: API route limitations, cold starts, costs

2. **Complete TDD-006 Alternatives section**
   - For each option: realistic pros/cons, cost estimates, complexity
   - Reference sources (tutorials, documentation, real projects)
   - Compare tradeoffs honestly

3. **Make technology recommendation**
   - Write Decision Rationale section
   - Explain why selected option beats alternatives
   - Call out tradeoffs being accepted (e.g., "Choosing simplicity over infinite scale")

4. **Detail the architecture**
   - Create `TDD-006-architecture.d2` diagram (visual)
   - Finalize database schema (users, progress, reviews)
   - Document API endpoints (HTTP verbs, request/response format)
   - Specify directory structure (`/backend/` organization)

5. **Resolve open technical questions** (TDD-006):
   - Spaced repetition algorithm: SM-2? Anki? Custom?
   - Data migration approach: How to import localStorage to server?
   - Scaling strategy: When does current architecture hit limits?

6. **Handoff**: "TDD is approved, ready for joint review with PM"

**Blockers**: None (technical research is independent)

**Approval Stamp**: When complete, TDD-006 gets "Approved By: [Architect] On: YYYY-MM-DD"

---

### Phase 3: Joint PM + Architect Review (1 Session)

**Owner**: Both personas together
**Duration**: 30-60 minutes (one focused meeting)
**Input**: PRD-006 (approved), TDD-006 (approved)
**Output**: Final decisions documented, GitHub issue updated, ready for implementation

**Joint Meeting Agenda**:

1. **PRD-006 Review** (10 min)
   - PM walks through approved PRD
   - Architect clarifies tech implications of decisions
   - Agree on MVP scope officially

2. **TDD-006 Review** (20 min)
   - Architect presents technology recommendation
   - Show analysis: top 2 options, cost/scaling comparison
   - Address PM's concerns (will this work for our user base?)

3. **Integration Planning** (15 min)
   - How do frontend and backend work together?
   - Data contracts: what format does API return?
   - Error handling: what if backend is down?

4. **Agent Splitting Decision** (5 min)
   - Review PRD-006 Agent Splitting Strategy section
   - Confirm: When will we create `backend-dev:` persona? (Approved: when backend infrastructure work begins)
   - Boundary: What does each dev own?

5. **Approval & Handoff** (5 min)
   - Both documents get approval stamps (date + names)
   - GitHub issue updated with final decisions
   - Assign owner for next phase

**Outcome**:

- Final decisions locked in
- No more ambiguity for Backend Developer
- Ready to implement

---

### Phase 4: Backend Developer Implementation (Future)

When backend work actually begins:

1. **Backend Developer** claims TDD-006 and implements according to spec
   - Sets up project structure (framework, database)
   - Implements authentication (signup/login)
   - Implements progress API (save/load)
   - Implements spaced rep scheduling service
   - Writes tests throughout

2. **Frontend Developer** extracts API contract from TDD-006
   - Adds login/signup pages
   - Integrates with backend API calls
   - Tests sync flow (save locally → send to server)
   - Tests offline fallback (localStorage as cache)

3. **Both coordinate** on integration
   - API contract is source of truth (TDD-006)
   - Integration tests verify both sides work together
   - Code reviews ensure consistency

4. **Quality gates**
   - Backend tests pass (unit + integration + load)
   - Frontend integration tests pass
   - Data integrity verified (progress syncs correctly)
   - Performance acceptable (API response time < 200ms)

---

## Decision Points & Tradeoffs

These decisions will be made during PM/Architect phases:

### Scope Decision (PM)

**Question**: What's the MVP?

**Options**:

- A) Basic progress tracking only (simpler, faster MVP)
- B) Progress + spaced rep scheduling (more value, more complex)
- C) Progress + spaced rep + social features (ambitious, delays MVP)

**Tradeoff**: MVP speed vs. feature completeness

**Recommendation**: Start with B (tracking + scheduling). Social features are future.

---

### Technology Stack (Architect)

**Question**: Which framework/database/hosting?

**Decision Matrix** (Architect fills this in):

| Axis | Option A | Option B | Option C | Option D |
|------|----------|----------|----------|----------|
| **Framework** | Express.js | FastAPI | Firebase | Next.js |
| **Database** | PostgreSQL | PostgreSQL | Firestore | PostgreSQL |
| **Hosting** | VPS | VPS | Google Cloud | Vercel |
| **Team Familiar?** | ✅ (JS) | ❌ (Python) | ⚠️ (Google) | ✅ (JS) |
| **Cost at 1K users** | $50-100/mo | $50-100/mo | $100-300/mo | $0-50/mo |
| **Cost at 100K users** | $500-1K/mo | $500-1K/mo | $5K+/mo | $1-5K/mo |
| **DevOps Burden** | High | High | Low | Medium |
| **Scaling Complexity** | High | High | Low | Medium |

**Recommendation**: [Architect will make this call]

The decision constrains everything downstream (database schema design, API patterns, deployment workflow).

---

### Agent Splitting (Both)

**Question**: When do we split developer agents?

**Current Decision** ✅ (Already decided):

- **Keep** single `dev:` persona through v0.4
- **Split** `frontend-dev:` + `backend-dev:` when backend infrastructure work begins
- **Trigger**: This document + approved decisions + GitHub issue created

**Boundary**:

- **Frontend Dev**: `content/`, HTML/CSS/JS, client-side integration, localStorage
- **Backend Dev**: `api/` or `backend/`, authentication, database, server-side logic
- **Shared**: Data contracts (API spec), tests, CLAUDE.md patterns

This prevents context-switching burden on single developer as codebase grows.

---

## Critical Success Factors

1. **PM answers all business questions** before Architect starts
   - Scope ambiguity → technical churn → wasted work
   - Must be resolved upfront

2. **Architect makes clear technology recommendation** with research
   - Not "multiple options are equally valid"
   - "Option A is best because X, Y, Z; we're accepting tradeoff Z"

3. **API contract is locked before implementation**
   - Frontend and backend work independently
   - Contract is source of truth (not code, not good intentions)
   - Changes go through formal API review

4. **Data migration is tested thoroughly**
   - Existing users' localStorage → server progress
   - Zero data loss is non-negotiable
   - Test with real data, real users

5. **Agent split happens cleanly**
   - Clear boundary definitions
   - Independent development paths
   - Regular sync points (PR reviews, integration tests)

---

## Timeline Estimate

| Phase | Owner | Duration | Status |
|-------|-------|----------|--------|
| **Phase 1** | PM | 1-2 sessions | Not started |
| **Phase 2** | Architect | 1-2 sessions | Not started |
| **Phase 3** | PM + Arch | 1 session | Not started |
| **Phase 4** | Backend Dev + Front Dev | 4-8 weeks | Future (after approval) |

**Total Planning**: 3-5 sessions spread across multiple Claude conversations
**Total Implementation**: 4-8 weeks (estimate; depends on tech stack complexity)

Note: No time estimates for individual sessions—focus on completion criteria instead.

---

## When to Start This Work

### Prerequisites (Must Be Met First)

- [ ] Kanji study module stable (v0.3+)
- [ ] Engagement layer complete (v0.4, XP/levels/goals)
- [ ] Frontend architecture patterns solidified
- [ ] Team ready to add backend complexity

### Trigger Events

- User requests: "I want my progress saved between devices"
- Project milestone: Kanji module feature-complete, ready to scale
- Business need: Need user accounts for premium features or analytics

### Not Starting This Work If

- Kanji study still has critical bugs
- Engagement features are still in flux
- Team is at capacity with frontend work
- Business requirements are still unclear

---

## Documentation References

**For detailed planning guidance**, see:

1. **[PRD-006: Backend Infrastructure Setup](../specs/PRD-006-Backend-Infrastructure-Setup.md)**
   - Product requirements, user stories, acceptance criteria
   - Open questions for PM to answer
   - Agent splitting strategy

2. **[TDD-006: Backend Infrastructure Design](../tdd/TDD-006-Backend-Infrastructure.md)**
   - Technology options (Node vs. Python vs. Serverless vs. Next.js)
   - Architecture design (components, data flow)
   - API specification (endpoints, request/response)
   - Database schema
   - Implementation sequence

3. **[Backend Planning Guide](../reference/BACKEND-PLANNING-GUIDE.md)**
   - Step-by-step workflow for PM → Architect → Joint Review
   - Checklist of what needs to be filled in
   - Common pitfalls and how to avoid them
   - Success criteria for completion

4. **[CLAUDE.md: Agent Orchestration System](../../CLAUDE.md#agent-orchestration-system)**
   - How personas work together
   - `pm:`, `arch:`, `dev:` definitions
   - When to split agents

---

## Next Steps

**For PM (when ready to start)**:

1. Read `PRD-006-Backend-Infrastructure-Setup.md` top-to-bottom
2. Answer the 6 questions in "Open Questions" section
3. Refine acceptance criteria (make them specific)
4. Create GitHub issue linking PRD-006
5. Notify Architect: "PRD approved, ready for TDD work"

**For Architect (when PM done)**:

1. Read `TDD-006-Backend-Infrastructure.md` top-to-bottom
2. Research each technology option (Node/Python/Firebase/Next.js)
3. Complete "Alternative Approaches" with real findings
4. Write "Decision Rationale" recommending one option
5. Detail API design and database schema
6. Create architecture diagram (TDD-006-architecture.d2)
7. Notify PM: "TDD approved, ready for joint review"

**For Joint Review (when both done)**:

1. Use BACKEND-PLANNING-GUIDE Phase 3 section
2. 30-minute focused meeting covering:
   - PRD approval + MVP scope confirmation
   - TDD approval + tech stack ratification
   - Integration planning + API contract alignment
   - Agent splitting confirmation
3. Add approval stamps to both documents
4. Update GitHub issue with final decisions
5. Ready to hand off to Backend Developer

---

## Questions?

If anything is unclear:

- Check the detailed PRD-006, TDD-006 documents
- Read BACKEND-PLANNING-GUIDE for workflow details
- Reference CLAUDE.md for persona definitions
- Ask! These documents are living; they improve with questions.

---

## Related Documentation

- **ROADMAP.md**: Long-term product roadmap (check Phase 3+ plans)
- **CHANGELOG.md**: Version history and features
- **PHASE2-ENGAGEMENT-LAYER.md**: Current phase work (v0.4)
- **CLAUDE.md**: Project philosophy, agent system, workflow standards
