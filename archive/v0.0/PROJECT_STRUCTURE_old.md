# Japanese Learning App - Project Structure

## 📁 Root Directory Organization

```
japanese/
├── index.html              # Main homepage - START HERE
│
├── css/                    # Stylesheets
│   └── shared.css         # Global styles for all pages
│
├── js/                     # JavaScript
│   └── shared.js          # Interactive features (audio, hints, tense switching)
│
├── shopping/              # Shopping topic (section-based architecture)
│   ├── phrases.html       # Key shopping phrases
│   ├── dialogue.html      # Dialogues (Present/Past/Future/Advanced)
│   ├── story.html         # Stories (to be created)
│   ├── manga.html         # Visual content (to be created)
│   ├── quiz.html          # Interactive quizzes (to be created)
│   └── tips.html          # Cultural tips (to be created)
│
├── docs/                  # 📄 Development documentation
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── TENSE_BUTTONS_FIX.md
│   └── ... (all .md and .txt files)
│
├── scripts/               # 🔧 Python build scripts
│   ├── README.md
│   ├── extract_content.py
│   └── insert_shopping_dialogues.py
│
├── extracted/             # 📦 Temporary extracted content
│   └── shopping-dialogue-*.html
│
└── old_files/             # 🗄️ Legacy monolithic HTML files
    ├── Travel_Scenarios.html
    └── shopping.html
```

## 🎯 For Users

**To use the app:**
1. Open `index.html` in your web browser
2. Click on a topic card (Shopping, Restaurant, etc.)
3. Explore different sections (Phrases, Dialogue, Story, etc.)
4. Click tense tabs to see different difficulty levels

**You don't need:**
- `docs/` - development notes only
- `scripts/` - build tools only
- `extracted/` - temporary files
- `old_files/` - archived versions

## 🛠️ For Developers

**Important folders:**
- `css/` and `js/` - Core styling and functionality
- `shopping/` - Example of new section-based architecture
- `docs/` - Read these for context on design decisions
- `scripts/` - Tools for building content

**Architecture:**
- Two-level navigation: Topics → Sections
- Shared CSS/JS for consistency
- Each section is a separate HTML page
- Tense tabs within dialogue/story pages

## 📊 Current Status

**✅ Complete:**
- Shopping topic structure
- Key phrases section
- Dialogue section (all 4 tenses)
- Tense switching functionality
- Audio playback
- Hint system
- Kanji flashcards

**⏳ To Do:**
- Restaurant, Travel, Hotel, Directions, Emergency, Relationships topics
- Story, Manga, Quiz, Tips sections for Shopping
- Apply section-based architecture to all topics

## 🧹 Recent Cleanup

**Before:** 13 documentation files cluttering root directory
**After:** Clean root with organized subdirectories

All operational files moved to:
- `.md` and `.txt` → `docs/`
- `.py` → `scripts/`
- Old HTML → `old_files/`

**Result:** Clean, professional project structure that's easy to navigate!
