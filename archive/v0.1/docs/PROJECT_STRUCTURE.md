# Project Structure

## Directory Overview

```
japanese/
├── CLAUDE.md                  # Project context for Claude (auto-loaded each session)
├── index.html                 # Landing page - START HERE
│
├── css/                       # Stylesheets
│   └── shared.css            # Global styles - USED BY ALL PAGES
│
├── js/                        # JavaScript
│   └── shared.js             # Interactive features - USED BY ALL PAGES
│
├── home/                      # Topic: Daily life / home activities
│   ├── phrases.html          # Key phrases
│   ├── dialogue.html         # Conversations
│   ├── story.html            # Reading practice (+ story-morning.html, etc.)
│   ├── manga.html            # Visual content
│   ├── quiz.html             # Interactive quizzes
│   └── tips.html             # Cultural notes
│
├── shopping/                  # Topic: Shopping scenarios
│   ├── phrases.html
│   ├── dialogue.html
│   ├── story.html            # (+ story-clothing.html, story-groceries.html, etc.)
│   └── ... (same structure as home/)
│
├── restaurant/                # Topic: Dining experiences
│   ├── phrases.html
│   └── ... (same structure)
│
├── travel/                    # Topic: Travel situations
│   ├── phrases.html
│   ├── story.html            # (+ story-airport.html, story-cycling.html, etc.)
│   └── ... (same structure)
│
├── docs/                      # 📄 Living Documentation
│   ├── ARCHITECTURE.md       # System architecture (current)
│   ├── PROJECT_STRUCTURE.md  # This file
│   ├── DESIGN_PRINCIPLES.md  # UI/UX standards
│   ├── CONTENT_STANDARDS.md  # Japanese content guidelines
│   ├── TESTING.md            # Testing framework & TDD
│   └── WORKFLOW_EXCEPTIONS.md # Approved workflow deviations
│
├── temp/                      # 🚧 Current Build Working Files
│   ├── v[X.Y]_PLAN.md        # Build plan for version X.Y
│   ├── v[X.Y]_TESTING.md     # Test results
│   ├── v[X.Y]_NOTES.md       # Build notes
│   └── [prototype files]     # Work-in-progress content
│
├── archive/                   # 📦 Version Snapshots
│   ├── v0.0/                 # Pre-versioning historical docs
│   │   ├── README.md         # Explanation of archived content
│   │   └── [old docs]        # Historical documentation
│   ├── v0.1/                 # Version 0.1 snapshot
│   │   └── docs/             # Documentation snapshot
│   └── v0.2/                 # Version 0.2 snapshot
│       └── docs/
│
├── scripts/                   # 🔧 Build & Utility Scripts
│   ├── README.md
│   └── [various .py scripts]
│
├── extracted/                 # ⚠️ Temporary Extracted Content
│   └── [extracted HTML]      # (Can be cleaned up periodically)
│
└── old_files/                 # 🗄️ Legacy Monolithic Files
    └── [old HTML files]      # (Keep as reference, not in active use)
```

---

## For Users

### To Use the Website
1. Open `index.html` in your web browser
2. Click on a topic card (Home, Shopping, Restaurant, Travel)
3. Navigate between sections (Phrases, Dialogue, Story, etc.)
4. Use audio buttons to hear pronunciation
5. Click hints to see translations

### You Don't Need These Folders
- `docs/` - Development documentation only
- `temp/` - Work-in-progress files
- `archive/` - Historical versions
- `scripts/` - Development tools
- `extracted/`, `old_files/` - Legacy/temporary files

---

## For Developers

### Important Files & Folders

**Essential Files**:
- `CLAUDE.md` - READ FIRST - Project context that Claude auto-loads
- `index.html` - Landing page
- `css/shared.css` - ALL styling (never duplicate styles)
- `js/shared.js` - ALL JavaScript (never duplicate functions)

**Living Documentation** (`docs/`):
- `ARCHITECTURE.md` - System design and technical decisions
- `PROJECT_STRUCTURE.md` - This file (file organization)
- `DESIGN_PRINCIPLES.md` - UI/UX standards and design system
- `CONTENT_STANDARDS.md` - Japanese content guidelines
- `TESTING.md` - Testing framework and TDD approach
- `WORKFLOW_EXCEPTIONS.md` - Approved workflow deviations

**Working Files** (`temp/`):
- Created during active development
- Version-specific plans, notes, testing docs
- Prototype files for review
- Cleaned with approval after deployment

**Archives** (`archive/`):
- Version snapshots (v0.1, v0.2, etc.)
- Historical documentation
- Retention policy: Keep most recent 3 minors + most recent of each major

---

## Content Organization

### Topic Folders (home, shopping, restaurant, travel)

Each topic follows the same structure:

**Standard Pages**:
1. **phrases.html** - Key vocabulary (10-20 essential phrases)
2. **dialogue.html** - Conversational practice (back-and-forth exchanges)
3. **story.html** - Reading comprehension (narrative practice)
4. **manga.html** - Visual storytelling (to be implemented)
5. **quiz.html** - Interactive testing (to be implemented)
6. **tips.html** - Cultural notes and learning guidance

**Subtypes** (as needed):
- Multiple stories: `story-morning.html`, `story-cooking.html`, etc.
- Specific scenarios: `story-airport.html`, `story-groceries.html`, etc.

### Navigation Structure

**Two-Level Navigation**:
1. **Topic Level** - Switch between topics (Home, Shopping, etc.)
2. **Section Level** - Switch between content types (Phrases, Dialogue, etc.)

**Example User Flow**:
```
index.html
  ↓ (click "Shopping")
shopping/phrases.html
  ↓ (click "Dialogue" tab)
shopping/dialogue.html
  ↓ (click "Home" nav button)
home/phrases.html
```

---

## Development Status

### ✅ Completed
- Modular architecture (topic folders + shared resources)
- Shared CSS/JS system
- Navigation structure
- Basic content types (phrases, dialogue, story)
- Tense switching functionality
- Audio playback system
- Hint system
- Responsive design

### 🚧 In Progress (Pre-v1.0)
- Home topic (partially complete)
- Shopping topic (partially complete)
- Restaurant topic (just started)
- Travel topic (partially complete)
- Documentation system
- Testing framework
- Versioning workflow

### 📋 To Do
- Complete one full topic as template
- Implement manga pages
- Implement quiz pages
- Implement tips pages
- Apply template to remaining topics
- JLPT level toggle feature
- Furigana/romaji toggle features
- Progress tracking
- Audio file optimization

---

## File Naming Conventions

### HTML Files
```
Format: [content-type].html or [content-type]-[subtype].html

Examples:
phrases.html
dialogue.html
story.html
story-morning.html
story-groceries.html
```

**Rules**:
- Lowercase only
- Hyphens (not underscores) for multi-word names
- Descriptive subtypes when needed
- Consistent across all topics

### Version Documents
```
Format: v[X.Y]_[TYPE].md

Examples:
temp/v0.3_PLAN.md
temp/v0.3_TESTING.md
temp/v0.3_NOTES.md
```

### Archive Folders
```
Format: v[MAJOR].[MINOR] or v[MAJOR].[MINOR].[PATCH]

Examples:
archive/v0.0/    (pre-versioning)
archive/v0.1/
archive/v0.2/
archive/v1.0/
```

---

## Version Control

### Git Tags (Primary Versioning)
```bash
# Tag a new version
git tag v0.3.0 -m "Shopping dialogue complete"

# Push tags to remote
git push origin v0.3.0

# List all tags
git tag -l

# Checkout specific version
git checkout v0.3.0
```

### Archive Folders (Supplementary)
- Store documentation snapshots
- Keep non-git-tracked files
- Reference materials for each version
- Follow retention policy (most recent 3 minors + most recent major)

---

## Workflow Integration

### Standard Development Workflow

```
1. UNDERSTAND
   ↓ Read: CLAUDE.md, ARCHITECTURE.md, existing content

2. PLAN
   ↓ Create: temp/v[X.Y]_PLAN.md
   ↓ Get approval from Christopher

3. PROTOTYPE
   ↓ Build: ONE page in temp/
   ↓ Get approval from Christopher

4. BUILD
   ↓ Create: Remaining pages in temp/

5. VERIFY
   ↓ Test: Navigation, functionality, responsive
   ↓ Document: temp/v[X.Y]_TESTING.md

6. DEPLOY
   ↓ Archive: Old version to archive/v[X.Y]/
   ↓ Move: Approved files from temp/ to final location
   ↓ Tag: git tag v[X.Y].[Z]
   ↓ Clean: temp/ folder (with approval)
```

### File Protection Rules

**NEVER**:
- Overwrite content files directly
- Skip the temp/ folder for new content
- Deploy without testing navigation
- Clean temp/ without asking

**ALWAYS**:
- Work in temp/ first
- Get approval before deployment
- Test all links after structural changes
- Archive superseded versions
- Update version comments in files

---

## Folder Cleanup Guidelines

### temp/ Folder
- **Purpose**: Active development workspace
- **Cleanup**: After successful deployment (with approval)
- **Retention**: Only current build files
- **Ask Before**: Always request permission to clean

### archive/ Folder
- **Purpose**: Version snapshots
- **Retention Policy**:
  - Keep most recent of every MAJOR version
  - Keep most recent 3 of current MAJOR version
  - Pre-v1.0 treated as current major
- **Cleanup**: Based on retention policy (with approval)

### extracted/ Folder
- **Purpose**: Temporary content extraction
- **Cleanup**: Can be cleaned periodically (low priority)
- **Retention**: None (all temporary)

### old_files/ Folder
- **Purpose**: Legacy reference files
- **Retention**: Keep for now (reference during migration)
- **Future**: May archive once migration fully complete

---

## Adding New Content

### New Topic
```
1. Create folder: /[topic-name]/
2. Copy structure from existing topic (e.g., shopping/)
3. Update content (keep HTML structure identical)
4. Add topic card to index.html
5. Update navigation buttons in pages
6. Test all navigation links
7. Document in version notes
```

### New Content Type
```
1. Create in one topic: /home/newtype.html
2. Follow existing page structure
3. Get approval (prototype approach)
4. Create in all other topics
5. Update section navigation
6. Test navigation across all topics
7. Update docs if new pattern introduced
```

### New Page Variant (e.g., story-airport.html)
```
1. Copy similar page as template
2. Update content
3. Keep structure consistent
4. Update navigation if needed
5. Test links
```

---

## Common Paths

**For Claude**:
- Start every session: Auto-read `CLAUDE.md`
- Check architecture: `docs/ARCHITECTURE.md`
- Check standards: `docs/DESIGN_PRINCIPLES.md`, `docs/CONTENT_STANDARDS.md`
- Work area: `temp/`

**For Christopher**:
- Entry point: `index.html`
- Review prototypes: `temp/[files]`
- Review docs: `docs/`
- Check versions: `archive/`

**For Both**:
- Reference point: `CLAUDE.md`
- Testing checklist: `docs/TESTING.md`
- Workflow rules: `CLAUDE.md` (Standard Workflow section)

---

*Last Updated: 2026-01-19*
*Next Review: After completing documentation system setup*
