---
audience: [multi-agent]
priority: high
size: medium
dependencies: []
last_updated: 2026-01-25
status: active
tags: [reference, structure, organization]
---

# Project Structure

## Directory Overview

```
japanese/
├── index.html                 # Redirect to content/index.html
├── CLAUDE.md                  # Project context for Claude (auto-loaded)
├── README.md                  # Public readme
│
├── content/                   # 🌐 ALL USER-FACING CONTENT
│   ├── index.html            # Main landing page - START HERE
│   │
│   ├── css/                  # Shared stylesheets
│   │   └── shared.css        # Global styles - USED BY ALL PAGES
│   │
│   ├── js/                   # Shared JavaScript
│   │   └── shared.js         # UI utilities - navigation, audio, quizzes
│   │
│   ├── topics/               # Topic-based learning content
│   │   ├── home-life/        # Daily life / home activities
│   │   │   ├── phrases.html
│   │   │   ├── dialogue.html
│   │   │   ├── story.html    # (+ story-morning.html, etc.)
│   │   │   ├── manga.html
│   │   │   ├── quiz.html
│   │   │   └── tips.html
│   │   ├── shopping/         # Shopping scenarios
│   │   ├── restaurant/       # Dining experiences
│   │   └── travel/           # Travel situations
│   │
│   └── kanji/                # 📚 Kanji Study Module (self-contained)
│       ├── index.html        # Kanji study dashboard
│       ├── js/               # Module-specific business logic
│       │   ├── storage.js         # localStorage CRUD, validation
│       │   ├── srs-engine.js      # SM-2 algorithm, stage transitions
│       │   ├── mastery-calculator.js  # JLPT/topic mastery
│       │   └── session-manager.js     # Queue management
│       ├── css/              # Module-specific styles
│       ├── data/             # Kanji metadata
│       │   └── kanji-metadata.js  # 169 kanji with readings/meanings
│       └── test-*.html       # Module test files
│
├── docs/                      # 📄 Development Documentation
│   ├── reference/            # Technical reference docs
│   │   ├── PROJECT_STRUCTURE.md  # This file
│   │   ├── ARCHITECTURE.md
│   │   └── LEARNINGS.md
│   ├── guides/               # How-to guides
│   ├── specs/                # PRDs
│   └── tdd/                  # Technical Design Documents
│
├── temp/                      # 🚧 Working Files (gitignored)
│   ├── v[X.Y]_PLAN.md
│   ├── v[X.Y]_TESTING.md
│   └── [prototype files]
│
├── archive/                   # 📦 Version Snapshots
│   └── v[X.Y]/
│
├── scripts/                   # 🔧 Build & Utility Scripts
│
└── .claude/                   # 🤖 Agent Configuration
    ├── agents/               # Persona definitions
    │   ├── AGENTS.md             # Orchestration guide
    │   ├── git-master.md         # Git operations agent
    │   ├── documenter.md         # Documentation agent
    │   └── [other personas]
    ├── commands/             # Slash commands
    │   ├── commit.md             # /commit - validated commits
    │   ├── branch.md             # /branch - validated branches
    │   ├── deploy.md             # /deploy - version deployment
    │   └── [other commands]
    ├── hooks/                # Pre/post tool hooks
    │   └── pre-bash-check.js     # Git enforcement, safety gates
    ├── rules/                # Coding standards
    │   ├── git-workflow.md       # Git conventions + Agent Git Governance
    │   ├── coding-style.md
    │   └── [other rules]
    └── skills/               # Workflow definitions
        ├── git-operations.md         # Git workflow steps
        ├── worktree-orchestration.md # Parallel development
        ├── deployment-workflow.md
        └── [other skills]
```

---

## Architecture Philosophy

### Two-Layer Content Model

```
Root Level                    → Infrastructure & Configuration
└── content/                  → User-Facing Application
    ├── css/, js/             → Shared presentation utilities
    ├── topics/               → Learning content pages
    └── kanji/                → Self-contained feature module
```

**Why this structure?**

1. **Clean Separation**: User content in `content/`, dev infrastructure at root
2. **Module Isolation**: `kanji/` is self-contained with its own js/ for business logic
3. **Shared Utilities**: `content/css/` and `content/js/` for presentation layer
4. **Future Ready**: New modules (grammar/, vocabulary/) follow same pattern

### Code Organization

| Directory | Purpose | Type of Code |
|-----------|---------|--------------|
| `content/js/shared.js` | UI utilities | Presentation (navigation, audio, hints) |
| `content/css/shared.css` | Global styles | Presentation |
| `content/kanji/js/` | SRS business logic | Domain logic (algorithms, persistence) |
| `content/kanji/data/` | Kanji metadata | Data layer |

---

## For Users

### To Use the Website

1. Open `index.html` (or `content/index.html` directly)
2. Click on a topic card (Home, Shopping, Restaurant, Travel)
3. Navigate between sections (Phrases, Dialogue, Story, etc.)
4. Use audio buttons to hear pronunciation
5. Click hints to see translations

### For Kanji Study (v0.3+)

1. Navigate to `/content/kanji/index.html`
2. Select JLPT level and topic filters
3. Review flashcards using Again/Hard/Good/Easy buttons
4. Track your mastery progress

---

## For Developers

### Key Entry Points

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project context - READ FIRST |
| `content/index.html` | Main landing page |
| `content/css/shared.css` | Global styles |
| `content/js/shared.js` | UI utilities |
| `content/kanji/` | Kanji study module |

### Adding New Topic Content

```
content/topics/[new-topic]/
├── phrases.html
├── dialogue.html
├── story.html
└── ...
```

1. Copy structure from existing topic
2. Update navigation in all topics
3. Add card to `content/index.html`

### Adding New Feature Module

```
content/[new-module]/
├── index.html        # Module entry point
├── js/               # Module-specific business logic
├── css/              # Module-specific styles (optional)
└── data/             # Module data (optional)
```

Follow the kanji module pattern:
- Self-contained with own js/ for domain logic
- Uses shared.css and shared.js for UI utilities
- Independent test files

---

## URL Structure

| URL | Content |
|-----|---------|
| `/` | Redirect to `/content/index.html` |
| `/content/` | Main landing page |
| `/content/topics/home-life/phrases.html` | Topic content |
| `/content/kanji/` | Kanji study module |

---

## Content Organization

### Topic Pages

Each topic in `content/topics/` follows the same structure:

| Page | Purpose |
|------|---------|
| `phrases.html` | Key vocabulary (10-20 phrases) |
| `dialogue.html` | Conversational practice |
| `story.html` | Reading comprehension |
| `manga.html` | Visual storytelling |
| `quiz.html` | Interactive testing |
| `tips.html` | Cultural notes |

**Variants**: `story-morning.html`, `story-groceries.html`, etc.

### Kanji Module

The kanji module (`content/kanji/`) is a **vertical slice**:

```
content/kanji/
├── index.html              # Dashboard UI with engagement features
├── css/
│   └── dashboard.css       # Visualization and widget styles (v0.4.0)
├── js/
│   ├── storage.js          # Persistence layer (schema v1.1.0)
│   ├── srs-engine.js       # SM-2 algorithm
│   ├── mastery-calculator.js # Aggregation
│   ├── session-manager.js  # Queue management
│   ├── xp-engine.js        # XP calculation and levels (v0.4.0)
│   ├── streak-manager.js   # Streak tracking with freezes (v0.4.0)
│   ├── goals-manager.js    # Daily goals and notifications (v0.4.0)
│   └── dashboard-visualizations.js # Heatmap, rings, trend line (v0.4.0)
├── data/
│   └── kanji-metadata.js   # 169 kanji
└── js/test-*.html          # Unit test suites
```

---

## Development Workflow

### Standard Process

```
1. UNDERSTAND → Read CLAUDE.md, docs/
2. PLAN       → Create temp/v[X.Y]_PLAN.md
3. PROTOTYPE  → Build ONE page in temp/
4. BUILD      → Create remaining files
5. VERIFY     → Test, document in temp/v[X.Y]_TESTING.md
6. DEPLOY     → Move to content/, tag version
```

### File Protection Rules

**NEVER**:
- Overwrite content files without backup
- Skip prototype step for new features
- Deploy without testing navigation

**ALWAYS**:
- Work in temp/ first
- Test all links after changes
- Update documentation

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [CLAUDE.md](../../CLAUDE.md) - Project context
- [coding-style.md](../../.claude/rules/coding-style.md) - Standards
- [git-workflow.md](../../.claude/rules/git-workflow.md) - Version control

---

*Last Updated: 2026-01-25*
*Structure: v0.3 - content/ directory reorganization*
