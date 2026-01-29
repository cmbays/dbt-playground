# Japanese Learning Website 🇯🇵

An interactive Japanese language learning website focused on practical, conversational skills for daily life, shopping, dining, and travel situations.

**Current Level**: Beginner to Elementary (JLPT N5/N4, Duolingo ~40-50)
**Status**: v0.2 (Kanji Study Module) → v0.3 Foundation (In Planning)

---

## 🚀 Quick Start

### For Learners
1. Open `index.html` in your web browser
2. Click a topic card (Home, Shopping, Restaurant, Travel)
3. Explore content types (Phrases, Dialogue, Stories, etc.)
4. Use 🔊 buttons to hear pronunciation
5. Click ? buttons to reveal hints and translations

### For Developers
1. **Start here**: Read `CLAUDE.md` for complete project context
2. **Check roadmap**: See `docs/ROADMAP.md` for current phase and priorities
3. **View tasks**: Browse the [GitHub Project Board](https://github.com/users/cmbays/projects/2)
4. **Learn workflow**: Read `docs/PROJECT_BOARD_GUIDE.md` for contributing
5. **Understand structure**: See `docs/PROJECT_STRUCTURE.md`
6. **Learn architecture**: See `docs/ARCHITECTURE.md`

---

## 📚 Project Overview

### What This Is
A static website (HTML/CSS/JavaScript) for learning Japanese through:
- **Topic-based learning**: Home life, Shopping, Restaurants, Travel
- **Multiple content types**: Phrases, Dialogues, Stories, Manga, Quizzes, Tips
- **Interactive features**: Audio pronunciation, hint system, tense variations
- **Responsive design**: Works on desktop, tablet, and mobile

### Learning Philosophy
- **Practical first**: Real-world scenarios you'll encounter
- **Deep engagement**: Multiple ways to interact with the same content
- **Progressive difficulty**: Present → Past → Future → Advanced
- **Cultural context**: Not just language, but cultural understanding

---

## 🗂️ Project Structure

```
japanese/
├── README.md              # ← You are here
├── CLAUDE.md              # Project context for Claude (developers read this!)
├── index.html             # Landing page - start here for learners
│
├── css/                   # Shared styles
│   └── shared.css         # Single stylesheet for entire site
│
├── js/                    # Shared JavaScript
│   └── shared.js          # All interactive functionality
│
├── topics/                # All learning content (v0.1.0+)
│   ├── home-life/        # Topic: Daily life activities
│   ├── shopping/         # Topic: Shopping scenarios
│   ├── restaurant/       # Topic: Dining experiences
│   └── travel/           # Topic: Travel situations
│       └── [each contains: phrases, dialogue, story, manga, quiz, tips]
│
├── docs/                  # 📄 Documentation
│   ├── ARCHITECTURE.md            # System design
│   ├── PROJECT_STRUCTURE.md       # Complete directory guide
│   ├── DESIGN_PRINCIPLES.md       # UI/UX standards
│   ├── CONTENT_STANDARDS.md       # Japanese content guidelines
│   ├── TESTING.md                 # Testing framework
│   └── WORKFLOW_EXCEPTIONS.md     # Development workflow
│
├── temp/                  # Working files (current development)
├── archive/               # Version snapshots (historical)
└── scripts/               # Build utilities
```

**Complete structure**: See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

---

## 🎓 Content Types

Each topic includes multiple ways to engage with content:

| Content Type | Purpose | Status |
|-------------|---------|--------|
| **Phrases** | Essential vocabulary and expressions | 🚧 Partial |
| **Dialogue** | Conversational practice with back-and-forth exchanges | 🚧 Partial |
| **Story** | Reading comprehension through narratives | 🚧 Partial |
| **Manga** | Visual storytelling with Japanese text | 📋 Planned |
| **Quiz** | Interactive knowledge testing | 📋 Planned |
| **Tips** | Cultural notes and learning guidance | 📋 Planned |

**Tense Variations**: Most content includes Present, Past, Future, and Advanced versions for progressive learning.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **No Backend**: Static site, no server required
- **Browser APIs**: Web Speech API for pronunciation
- **Deployment**: Can be hosted on GitHub Pages, Netlify, Vercel, or any static hosting
- **Development**: No build process required (just edit and refresh!)

---

## 🎯 Current Status

### ✅ v0.2 Completed
- Kanji study module with 169 kanji (N5-N2)
- JLPT level filtering
- Basic flashcard study mode
- Modular architecture (topic folders + shared resources)
- Responsive design (mobile, tablet, desktop)
- Navigation system (topic and section navigation)
- Audio pronunciation system
- Documentation system
- GitHub project infrastructure

### 🚧 v0.3 In Planning (Phase 1 Foundation)
- **Epic #7**: SRS algorithm with mastery tracking (10 tasks)
- **Epic #8**: Study session experience (8 tasks)
- **Epic #9**: Habit formation system (6 tasks)
- See [ROADMAP.md](docs/ROADMAP.md) for details
- Track progress: [Project Board](https://github.com/users/cmbays/projects/2)

### 📋 Future Phases
- v0.4 Engagement: Gamification enhancements
- v0.5 Deep Learning: Mnemonics and radicals
- v0.6 Active Recall: Quiz and audio integration
- See [ROADMAP.md](docs/ROADMAP.md) for full roadmap

---

## 📖 Documentation

### For Users
- **This file**: Overview and quick start
- **index.html**: Just open it and start learning!

### For Developers
Start with these in order:

1. **[CLAUDE.md](CLAUDE.md)** - Complete project context (if working with Claude)
2. **[docs/ROADMAP.md](docs/ROADMAP.md)** - Product roadmap and current phase
3. **[docs/PROJECT_BOARD_GUIDE.md](docs/PROJECT_BOARD_GUIDE.md)** - GitHub project board guide
4. **[docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Where everything is located
5. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and technical decisions
6. **[docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)** - UI/UX standards
7. **[docs/CONTENT_STANDARDS.md](docs/CONTENT_STANDARDS.md)** - Japanese content guidelines
8. **[docs/TESTING.md](docs/TESTING.md)** - Testing framework

### Quick References
- **Workflow**: See "Standard Workflow" in CLAUDE.md (6-phase process)
- **Versioning**: Git tags + semantic versioning (v[MAJOR].[MINOR].[PATCH])
- **File naming**: Lowercase with hyphens (e.g., `story-morning.html`)
- **Working files**: Use `temp/` folder, never overwrite directly

---

## 🎨 Design Principles

- **Consistency**: Shared CSS/JS ensures uniform experience
- **Performance**: Resource caching makes pages load fast
- **Accessibility**: WCAG AA standards, semantic HTML, responsive design
- **Clarity**: Clean visual hierarchy, readable typography
- **Delight**: Subtle animations and polish

**Full design system**: See [docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)

---

## 📝 Content Standards

- **Writing System**: Kanji + Hiragana + Katakana (appropriate mix)
- **Furigana**: Provided for all kanji at N5/N4 levels
- **Romaji**: Available for key phrases (helps absolute beginners)
- **Translations**: Natural English (not word-for-word literal)
- **Audio**: Native or near-native pronunciation
- **Cultural Context**: Notes on customs, etiquette, practical tips

**Complete guidelines**: See [docs/CONTENT_STANDARDS.md](docs/CONTENT_STANDARDS.md)

---

## 🔄 Development Workflow

For developers working on this project:

### Standard 6-Phase Workflow
```
UNDERSTAND → PLAN ✓ → PROTOTYPE ✓ → BUILD → VERIFY → DEPLOY ✓
             (approval)  (approval)                      (approval)
```

1. **UNDERSTAND**: Read docs, review existing content
2. **PLAN**: Create detailed plan, get approval
3. **PROTOTYPE**: Build ONE example, get approval
4. **BUILD**: Apply pattern to remaining pages
5. **VERIFY**: Test everything (navigation, functionality, responsive)
6. **DEPLOY**: Archive old version, deploy new, tag version

**Details**: See "Standard Workflow" section in [CLAUDE.md](CLAUDE.md)

### Critical Rules

**NEVER**:
- Overwrite content files directly (use temp/ folder)
- Skip the prototype step
- Break navigation links
- Deploy without testing

**ALWAYS**:
- Work in temp/ folder first
- Test all navigation after changes
- Get approval at checkpoints
- Version stamp modified files

---

## 🏷️ Versioning

**Format**: Semantic versioning `v[MAJOR].[MINOR].[PATCH]`
- **MAJOR**: Complete topic or significant architectural change
- **MINOR**: New features, new pages, content additions
- **PATCH**: Bug fixes, corrections, small tweaks

**Git Tags** (primary method):
```bash
git tag v0.3.0 -m "Shopping dialogue complete"
git push origin v0.3.0
```

**Archive Retention**: Keep most recent 3 minors + most recent of each major version

---

## 🧪 Testing

Before deploying changes:
- [ ] Navigation works between all pages
- [ ] All links point to correct destinations
- [ ] Shared CSS/JS load properly
- [ ] Responsive on mobile/tablet/desktop
- [ ] Audio pronunciation works
- [ ] Interactive features function correctly
- [ ] Content renders properly (Japanese text, furigana)

**Testing framework**: See [docs/TESTING.md](docs/TESTING.md)

---

## 🤝 Contributing

This is currently a personal learning project, but contributions are welcome!

### Getting Started
1. **Review the roadmap**: See [docs/ROADMAP.md](docs/ROADMAP.md) for current priorities
2. **Check the project board**: [GitHub Project](https://github.com/users/cmbays/projects/2)
3. **Find a task**: Look for issues labeled `status:ready`
4. **Read the guide**: See [docs/PROJECT_BOARD_GUIDE.md](docs/PROJECT_BOARD_GUIDE.md)

### Adding Content
1. Follow patterns from existing pages
2. Use the 6-phase workflow (see CLAUDE.md)
3. Match JLPT N5/N4 difficulty level
4. Include furigana for all kanji
5. Test on multiple devices

### Reporting Issues
- Use GitHub issue templates: Epic, Task, Bug, or Question
- Navigation broken? Let us know which pages
- Content errors? Specify location and correction
- Design issues? Include screenshot and device info

---

## 📜 License

*To be determined - this is currently a personal learning project*

---

## 🙏 Acknowledgments

### Resources Used
- **Dictionaries**: Jisho.org, Tangorin.com
- **Grammar**: Tae Kim's Guide, Imabi.net
- **JLPT Info**: jlpt.jp, JLPT Sensei
- **Cultural Info**: Japan-Guide.com, Tofugu

### Learning Goals
This project serves three purposes:
1. **Japanese Learning**: Create effective study materials
2. **Web Development**: Learn HTML/CSS/JavaScript best practices
3. **Claude Collaboration**: Master effective AI-assisted development

---

## 📬 Contact

*Contact information to be added*

---

## 🗺️ Roadmap

**Full roadmap**: See [docs/ROADMAP.md](docs/ROADMAP.md)

### Current: v0.2 (Kanji Study Module)
- ✅ 169 kanji with metadata
- ✅ JLPT filtering (N5-N2)
- ✅ Basic flashcard study mode

### Next: v0.3 Foundation (Q1 2026)
**Theme**: Build the Learning Engine
- SRS algorithm with SM-2 spaced repetition
- 8-stage mastery tracking (Locked → Burned)
- Study session UI with self-assessment
- Streak counter and habit formation
- **Track**: [GitHub Project Board](https://github.com/users/cmbays/projects/2)

### Future Phases
- **v0.4 Engagement** (Q2 2026): XP, levels, leaderboards
- **v0.5 Deep Learning** (Q2 2026): Mnemonics, radicals, kanji stories
- **v0.6 Active Recall** (Q3 2026): Quiz modes, audio recognition
- **v0.7+ Advanced** (Q3-Q4 2026): Vocabulary, grammar, advanced features

See [docs/ROADMAP.md](docs/ROADMAP.md) for detailed PRDs and milestones.

---

**Ready to learn Japanese?** Open `index.html` and get started! 🚀

**Ready to develop?** Read `CLAUDE.md` for complete context! 💻
