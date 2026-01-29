# PRD-006: Backend Infrastructure Setup & Agent Splitting Strategy

**Status**: Draft (Ready for PM Review & Iteration)
**Author**: Claude Code (Initial Framework)
**Created**: 2026-01-25
**Updated**: 2026-01-25

**Related Issue**: [CREATE GitHub issue for this PRD]
**Technical Design**: TDD-006 (to be completed by Architect)

---

## Problem Statement

Currently, the Japanese Learning Website is a static frontend with client-side state management. As the project scales beyond Kanji study modules to include:
- Multi-user accounts and progress tracking
- Spaced repetition scheduling (personalized to each learner)
- Synchronized learning state across devices
- Social/leaderboard features
- Advanced analytics for learner pathways

...the codebase will need a backend API to manage persistent, server-side data.

Additionally, the single `dev:` persona will eventually become a bottleneck when frontend and backend work diverges significantly. We need a documented decision point for when to split developer agents.

## User Benefit

- **Learners**: Cross-device sync, personalized scheduling, progress preservation
- **Project**: Foundation for premium features (accounts, social, advanced metrics)
- **Development Team**: Clearer separation of concerns, parallel development

## Target Users

- Returning learners who want accounts and progress tracking
- Eventually: premium tier users with spaced repetition
- Future: social features and learner communities

## JLPT Level Considerations

| Level | Considerations |
|-------|----------------|
| N5-N4 | Core audience; backend sync needed for consistent experience |
| N3+ | Advanced learners benefit from personalized scheduling |

---

## User Stories

1. As a returning learner, I want my progress saved to an account so that I can resume learning on any device.
2. As a regular studier, I want the system to schedule kanji review based on spaced repetition so that I learn more efficiently.
3. As a project maintainer, I want clear separation between frontend and backend development so that teams can work in parallel.

## Acceptance Criteria

**NOTE**: These are placeholder; PM should refine based on actual feature priorities.

- [ ] AC-1: Backend API server running (Node.js/Express/Next.js - TBD)
- [ ] AC-2: User authentication system (signup, login, JWT/session - TBD)
- [ ] AC-3: Progress data persists server-side and syncs with frontend
- [ ] AC-4: Spaced repetition algorithm runs server-side with configurable intervals
- [ ] AC-5: Frontend can fetch personalized lesson plans from backend
- [ ] AC-6: Agent splitting strategy documented and ready for implementation

---

## Scope

### In Scope
- Backend framework selection and setup (see TDD-006 for tech choices)
- User authentication system (basic credentials; OAuth TBD for future)
- Progress tracking API (read/write learner state)
- Spaced repetition scheduling service (core algorithm)
- Database schema for users, progress, kanji metadata
- API documentation and testing

### Out of Scope
- Premium payment processing (future)
- Social features (leaderboards, messaging - future)
- Advanced analytics dashboard (future)
- Mobile app (native iOS/Android - future)
- Multi-language support beyond Japanese content (future)

### Future Considerations
- OAuth/SSO integration (Google, GitHub)
- Offline-first sync (service workers, CouchDB-style replication)
- Analytics pipeline (user behavior, learning outcomes)
- Admin dashboard for content management
- Webhook integrations for third-party tools

---

## Content Requirements

**Not applicable** - this is infrastructure, not content. However:
- Backend must support JLPT level filtering (inherit from frontend)
- Progress tracking must store per-level achievements
- API responses must include furigana, romaji, audio URLs (inherit frontend standards)

---

## Success Metrics

- [ ] **Reliability**: 99.9% API uptime in production
- [ ] **Performance**: API responses < 200ms for typical queries
- [ ] **Adoption**: ≥50% of users sign up for accounts within 3 months of launch
- [ ] **Data Integrity**: Zero data loss; automated backups working
- [ ] **Development**: Frontend and backend teams can work in parallel without blocking

---

## Dependencies

_What must exist before backend work can begin._

- [ ] Final technology stack decision (Node.js? Python? Rust? - see TDD-006)
- [ ] Database platform decision (PostgreSQL? MongoDB? - see TDD-006)
- [ ] Hosting/deployment strategy (self-hosted? AWS? Vercel? - see TDD-006)
- [ ] Current frontend architecture stable enough to define API contracts
- [ ] Existing kanji/vocabulary/progress data structures finalized

---

## Open Questions

**PM should resolve these before handoff to Architect:**

1. **MVP Scope**: Do we start with basic progress tracking + spaced repetition, or just progress tracking?
2. **Authentication**: Usernames/passwords only, or OAuth from day one? (Impacts complexity)
3. **Data Migration**: How do we migrate existing localStorage data to server?
4. **Rollout Strategy**: Opt-in accounts? Force migration? Gradual?
5. **Cost Model**: Will there be free tier limitations on account count? (Affects architecture)
6. **Social Features**: Do we reserve database schema for future social/leaderboard features now?

---

## Agent Splitting Strategy

**CRITICAL DECISION**: This PRD documents the *trigger point* for splitting the developer agent.

### When to Split

Backend infrastructure work should trigger agent splitting when:
- A dedicated backend service is needed (not just static site generation)
- Frontend and backend work diverge technologically (JavaScript UI vs. API framework)
- Team benefits from parallel development (2+ developers)

### How to Split

At the time of backend implementation:

1. **Create `backend-dev:` persona** (see `.claude/agents/AGENTS.md` for profile)
   - Responsible for: API design, database queries, authentication, server logic
   - Tools: Backend framework (Node, Python, etc.), database client, API testing
   - Focus: `api/`, `backend/`, database schemas

2. **Keep `frontend-dev:` persona focused** on:
   - HTML/CSS/JavaScript in `content/`
   - Client-side state management
   - API integration (calling backend endpoints)
   - Data visualization and UX

3. **Establish Integration Boundary**
   - API contracts defined in `docs/API.md` (shared by both)
   - Frontend integration tests verify API usage
   - Backend tests verify contract compliance
   - Weekly sync between personas (or per-PR review)

### Handoff Protocol at Split Time

When backend work begins:
1. **Architect** finalizes API specification in TDD-006
2. **Product Manager** approves backend MVP scope
3. **Code Reviewer** establishes backend testing standards
4. **Frontend Dev** extracts what API calls are needed
5. **Backend Dev** implements backend according to spec
6. **Both devs** coordinate on integration and testing

---

## Related Architecture Decisions

### Current Frontend Architecture (Documented)
- Static HTML + CSS + vanilla JavaScript
- Client-side localStorage for progress
- Python scripts (in `temp/`) generate data files
- No runtime dependencies or framework

### Future Backend Architecture (To Be Decided)
- Framework: Express? FastAPI? Hono? (TDD-006)
- Database: PostgreSQL? MongoDB? (TDD-006)
- Hosting: Self-hosted? Cloud platform? (TDD-006)
- Authentication: JWT? Sessions? (TDD-006)

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-25 | Claude Code | Initial framework - ready for PM review and completion |

---

## Next Steps for PM

1. **Resolve Open Questions** section above
2. **Define MVP Scope**: What's in first version vs. future?
3. **Prioritize Dependencies**: Which tech stack decisions matter most?
4. **Create GitHub Issue**: Link this PRD to tracking issue
5. **Notify Architect**: Hand off to TDD-006 after PRD approval
6. **Schedule Review**: Set time for PM + Architect to review both documents together

---

## For Future Reference

**Next Person**: When you continue this work, start with the Open Questions section. PM should have filled those in during their review phase.
