# TDD-006: Backend Infrastructure Design & Architecture

**Status**: Draft (Ready for Architect Review & Iteration)
**Author**: Claude Code (Initial Framework)
**Created**: 2026-01-25
**Updated**: 2026-01-25

**Source PRD**: PRD-006
**Related Issue**: [Linked from PRD-006]
**Architecture Diagram**: TDD-006-architecture.d2 (to be created)

---

## Overview

This TDD defines the technical approach for building backend infrastructure to support persistent user accounts, progress tracking, and spaced repetition scheduling. It explores multiple technology stack options and documents the selection rationale.

**Status**: Framework only. Architect should:
1. Research actual technology options
2. Complete Option A/B/C comparisons
3. Make recommendation with clear rationale
4. Document final architecture design

---

## Technical Approach

### Design Goals (Non-Negotiable)

- **Developer Velocity**: Can one backend dev + one frontend dev work independently?
- **Operational Simplicity**: Easy to deploy, monitor, backup
- **Scalability**: Can handle 1K-10K active users without major refactoring
- **Maintainability**: Code patterns consistent with existing project philosophy ("Leave it better than you found it")
- **Cost Efficiency**: Won't break the budget for small/medium user base

### Technology Stack Decision

**Three main axes to decide:**

1. **Backend Framework**: Node.js/Express vs. Python/FastAPI vs. Go vs. Rust?
2. **Database**: PostgreSQL vs. MongoDB vs. Firebase vs. something else?
3. **Deployment**: Self-hosted (VPS) vs. Cloud Platform (AWS/Vercel/Railway)?

Each choice has deep implications for developer experience, scaling, and cost.

---

## Alternative Approaches

**NOTE: Architect should flesh these out with real research and options.**

### Option A: Node.js + Express + PostgreSQL + Self-Hosted VPS

**Approach**: Stick with JavaScript ecosystem; Express API server with PostgreSQL database; deploy to cloud VPS (DigitalOcean, Linode, or similar).

**Pros**:
- Same language as frontend (shared libraries, consistent patterns)
- Mature ecosystem (Express, TypeORM, Jest)
- Full control over infrastructure
- Reasonable ops complexity
- Cost-effective for small scale

**Cons**:
- Must manage database backups and monitoring yourself
- Learning ops/DevOps if not familiar
- Horizontal scaling requires load balancer setup
- Server maintenance burden

**Complexity**: Medium

**Cost Estimate**: $5-20/month (VPS) + time for DevOps

### Option B: Python/FastAPI + PostgreSQL + Self-Hosted

**Approach**: Python backend (separate from JS frontend) with FastAPI web framework; PostgreSQL database; VPS deployment.

**Pros**:
- Python great for data science/scheduling algorithms
- FastAPI is extremely fast and developer-friendly
- Async-first (good for I/O-heavy work like API calls)
- Excellent data validation with Pydantic

**Cons**:
- New language for frontend team (lower velocity initially)
- Python runtime/dependency management overhead
- Less overlap with existing JavaScript project

**Complexity**: Medium-High

**Cost Estimate**: $5-20/month (VPS) + ramp-up time

### Option C: Serverless (Firebase/Supabase) + Managed Database

**Approach**: Serverless functions + managed database; minimal infrastructure management.

**Pros**:
- Zero infrastructure to manage (Firebase Realtime DB handles it)
- Pay-per-use (cheap for small scale)
- Built-in authentication (can use Firebase Auth)
- Auto-scaling
- Fast time-to-market

**Cons**:
- Vendor lock-in (Firebase is Google)
- Less flexibility for custom algorithms (spaced repetition)
- Can become expensive at scale
- Limited database flexibility

**Complexity**: Low

**Cost Estimate**: $0-50/month (free tier covers startup)

### Option D: Next.js API Routes + PostgreSQL + Vercel

**Approach**: Unified full-stack with Next.js API routes; PostgreSQL; deploy to Vercel (serverless frontend + function-based backend).

**Pros**:
- Single codebase (frontend + backend in same repo)
- Already familiar with Next.js if using it
- Automatic deployment CI/CD
- Easy to share types between frontend and backend
- Vercel scales automatically

**Cons**:
- API routes not ideal for complex business logic
- Database connection pooling required (adds complexity)
- Cold start latency for functions
- Lock-in to Vercel

**Complexity**: Medium

**Cost Estimate**: $0 free tier, scales to $100+/month

---

### Decision Rationale (PLACEHOLDER)

**Architect**: Fill this in after analyzing options above.

- **Selected Option**: [A/B/C/D or hybrid]
- **Why This Option**:
  - Aligns with [Team skills/constraints]
  - Best balance of [developer velocity / cost / scaling]
  - Enables [future features like X/Y]
- **Rejected Alternatives**:
  - Why not [Option]?
  - Why not [Option]?

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│         Learner Devices (Browsers)              │
│  ┌──────────────────────────────────────────┐   │
│  │  Frontend (HTML/CSS/JS)                  │   │
│  │  ├─ Kanji Study UI                       │   │
│  │  ├─ Progress Display                     │   │
│  │  └─ localStorage (session cache)         │   │
│  └──────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────┘
                   │ HTTPS API calls
                   ▼
┌─────────────────────────────────────────────────┐
│        Backend API Server Layer                 │
│  ┌──────────────────────────────────────────┐   │
│  │  Express/FastAPI/Next.js                 │   │
│  │  ├─ /api/auth/* (login, signup)          │   │
│  │  ├─ /api/progress/* (save/load state)    │   │
│  │  ├─ /api/schedule/* (spaced rep)         │   │
│  │  ├─ /api/kanji/* (content delivery)      │   │
│  │  └─ /api/health (monitoring)             │   │
│  └──────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────┘
                   │ SQL queries
                   ▼
┌─────────────────────────────────────────────────┐
│      Data Layer (PostgreSQL/MongoDB)            │
│  ┌──────────────────────────────────────────┐   │
│  │  Users Table/Collection                  │   │
│  │  Progress Table/Collection                │   │
│  │  Kanji Metadata Table/Collection          │   │
│  │  Review History Table/Collection          │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

**D2 Diagram**: To be created in `TDD-006-architecture.d2`

### Component Descriptions

| Component | Responsibility | Tech |
|-----------|----------------|------|
| Frontend | User interface, local state, API calls | Vanilla JS / Next.js |
| API Gateway | Route requests, auth middleware, error handling | Express/FastAPI/Next |
| Auth Service | User signup, login, JWT/session validation | Passport.js / FastAPI |
| Progress Service | Save/load learning progress | ORM (TypeORM/SQLAlchemy) |
| Scheduling Service | Calculate spaced rep intervals | Custom algorithm |
| Database | Persistent storage | PostgreSQL/MongoDB |

---

## Data Structures

### Key Entities (Preliminary)

```javascript
// User
{
  id: 'uuid',
  username: 'string',
  email: 'string',
  passwordHash: 'string',
  createdAt: 'timestamp',
  preferences: {
    jlptLevel: 'N5|N4|N3|N2|N1',
    dailyGoal: 'number',
    notificationsEnabled: 'boolean'
  }
}

// Progress
{
  id: 'uuid',
  userId: 'uuid',
  kanjiId: 'string', // e.g., '日'
  status: 'new|learning|reviewing|mastered',
  reviewHistory: [
    {
      reviewedAt: 'timestamp',
      correct: 'boolean',
      interval: 'number' // days until next review
    }
  ],
  nextReviewDate: 'timestamp'
}

// Review Schedule (Output)
{
  userId: 'uuid',
  todayCards: [kanjiId, ...], // Due today
  upcomingCards: [kanjiId, ...], // Due in next 7 days
  masteredCards: [kanjiId, ...] // Already mastered
}
```

---

## File Changes (Preliminary)

| File/Directory | Change Type | Description |
|---|---|---|
| `backend/` | Create | New directory for backend code |
| `backend/src/server.ts` | Create | Express/FastAPI entry point |
| `backend/src/routes/auth.ts` | Create | Authentication endpoints |
| `backend/src/routes/progress.ts` | Create | Progress tracking endpoints |
| `backend/src/routes/schedule.ts` | Create | Spaced rep scheduling |
| `backend/src/models/` | Create | Database models/schemas |
| `backend/src/services/` | Create | Business logic (algorithms) |
| `backend/test/` | Create | Backend tests (unit + integration) |
| `backend/Dockerfile` | Create | Container definition |
| `backend/.env.example` | Create | Environment variables template |
| `docs/API.md` | Create | API documentation |
| `docs/tdd/TDD-006-architecture.d2` | Create | Architecture diagram |

---

## API Design (Placeholder)

**Architect**: Detail this out after tech stack is chosen.

### Authentication Endpoints

```
POST /api/auth/signup
  Body: { username, email, password }
  Returns: { userId, token }

POST /api/auth/login
  Body: { email, password }
  Returns: { userId, token }

POST /api/auth/refresh
  Body: { refreshToken }
  Returns: { accessToken }
```

### Progress Endpoints

```
GET /api/progress/:userId
  Returns: { progress: [...] } (all user progress)

POST /api/progress/:userId/record
  Body: { kanjiId, correct: boolean }
  Returns: { nextReviewDate, interval }

GET /api/progress/:userId/schedule
  Returns: { todayCards, upcomingCards, masteredCards }
```

---

## Implementation Sequence

**Note**: This is a placeholder. Architect should refine after tech stack decision.

1. **Foundation**
   - Set up project structure (package.json, TypeScript config, linting)
   - Configure database connection and migrations
   - Set up testing framework

2. **Authentication**
   - Implement user signup/login
   - JWT or session-based auth
   - Password hashing (bcrypt)

3. **Progress Tracking**
   - Database schema for users and progress
   - Save progress endpoint
   - Load progress endpoint

4. **Spaced Repetition Algorithm**
   - Implement core algorithm (SM-2 or similar)
   - Calculate review schedules
   - Endpoint to get today's cards

5. **Integration & Testing**
   - Frontend integration (API calls work)
   - Full test coverage (unit + integration + E2E)
   - Load testing (can handle expected traffic)

6. **Deployment**
   - Database backup strategy
   - Monitoring and alerting
   - CI/CD pipeline
   - Documentation

---

## State Management

- **Session State**: JWT token in localStorage (frontend)
- **Persistent State**: User account, progress history in database (backend)
- **Sync Strategy**: Frontend calls API to save after each review, fetches latest schedule on session start

---

## Error Handling

| Scenario | Handling | User Feedback |
|----------|----------|---------------|
| Invalid credentials | Return 401 | "Username or password incorrect" |
| User not found | Return 404 | "No account found" |
| Database connection failure | Return 500 with retry | "Server error. Please try again." |
| Malformed request | Return 400 | "Invalid request format" |
| Network timeout | Retry with exponential backoff | "Connection lost. Retrying..." |

---

## Performance Targets

- [ ] API response time < 200ms (p95)
- [ ] Database queries optimized with indexes
- [ ] JWT validation < 5ms
- [ ] Support 100+ concurrent users (with VPS)
- [ ] Support 1K+ concurrent users (with serverless/auto-scaling)

---

## Security Considerations

**See** `.claude/rules/security.md` for general rules. Backend-specific:

- [ ] All passwords hashed with bcrypt (cost factor 12)
- [ ] SQL injection prevention (parameterized queries, ORM)
- [ ] Rate limiting on auth endpoints (prevent brute force)
- [ ] CORS configured correctly (frontend domain only)
- [ ] Environment variables for secrets (no hardcoded keys)
- [ ] HTTPS enforced (TLS certificate)
- [ ] Input validation on all endpoints
- [ ] Database backups automated and tested

---

## Testing Strategy

### Unit Tests
- Spaced rep algorithm correctness
- Password hashing functions
- Data validation logic

### Integration Tests
- Full auth flow (signup → login → authenticated request)
- Progress save and load
- Schedule calculation with progress history

### E2E Tests
- Frontend calls backend API
- Data persists across page reload
- Multi-device sync (if supported)

### Load Tests
- Can handle 100+ concurrent users
- Database performance under load
- Memory/CPU utilization acceptable

---

## Dependencies

- **External Libraries**: TBD by selected framework (Express, FastAPI, etc.)
- **Infrastructure**: PostgreSQL / MongoDB (managed or self-hosted)
- **Services**: Email (if password reset needed), SMS (if 2FA added)
- **Frontend**: Must call API endpoints (documented in API.md)

---

## Open Questions

**Architect should research and resolve:**

1. **Tech Stack**:
   - Which framework (Express? FastAPI? Next.js? Go?)
   - Which database (PostgreSQL? MongoDB? Firebase?)
   - Which hosting (VPS? Vercel? AWS? Heroku?)

2. **Spaced Repetition**:
   - SM-2 algorithm? Anki algorithm? Custom?
   - Review intervals: 1, 3, 7, 14, 30 days? (Configurable?)
   - How to handle user skipping reviews?

3. **Data Migration**:
   - How to preserve existing localStorage progress when user signs up?
   - Gradual migration or one-time import?

4. **Scaling**:
   - At what point does self-hosted become unmaintainable?
   - Monitoring/alerting strategy?

5. **Future Features**:
   - Should database schema be designed for leaderboards, social features now?
   - Should API anticipate OAuth, 2FA, email verification?

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-25 | Claude Code | Initial framework - ready for Architect review and completion |

---

## Next Steps for Architect

1. **Research Technology Options**
   - Compare frameworks (Express vs. FastAPI vs. others)
   - Compare databases (PostgreSQL vs. MongoDB vs. Firebase)
   - Compare hosting (VPS vs. Vercel vs. AWS)
   - Document each option with real trade-offs

2. **Make Recommendation**
   - Fill in Option A/B/C comparisons with research
   - Write decision rationale
   - Reference past learnings from project

3. **Detail Architecture**
   - Create architecture diagram (TDD-006-architecture.d2)
   - Finalize data structures
   - Detail API endpoints

4. **Resolve Open Questions**
   - Spaced rep algorithm choice
   - Data migration strategy
   - Scaling plan

5. **Schedule Review**
   - Set time for PM + Architect to review both PRD-006 and TDD-006 together
   - Plan handoff to Backend Developer when approved

---

## For Future Reference

**Next Person**: Start with "Alternative Approaches" section. Architect should have filled these in with real research.
