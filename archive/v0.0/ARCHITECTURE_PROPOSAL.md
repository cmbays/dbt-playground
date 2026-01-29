# Architecture Proposal: Section-Based vs Tab-Based

## Current Situation

**Problem:** You're seeing only key phrases when opening shopping.html, but the dialogue content is in the file.

**Likely Cause:** Either:
1. File sync issue between VM and your local folder
2. Browser cache showing old version
3. Tab-switching JavaScript not working as expected

## Your Architecture Suggestion

Instead of having everything in one shopping.html with tabs, have separate pages:

```
shopping/
├── index.html (or phrases.html)     ← Key phrases (default)
├── dialogue.html                     ← Dialogue with tense tabs
├── story.html                        ← Stories with tense tabs
├── manga.html                        ← Manga sections
├── quiz.html                         ← Quizzes
└── tips.html                         ← Cultural tips
```

## Architecture Comparison

### Option A: Current (Single Page with Tabs)

```
shopping.html (one file)
├── Navigation tabs: Phrases | Dialogue | Story | Manga | Quiz | Tips
├── Phrases section (active by default)
├── Dialogue section (hidden)
│   └── Tense tabs: Present | Past | Future | Advanced
├── Story section (hidden)
│   └── Tense tabs: Present | Past | Future | Advanced
└── etc.
```

**Pros:**
- Single file to manage
- No page reloads when switching sections
- All content loads at once

**Cons:**
- Large file size (80KB+)
- All content loads even if not needed
- Harder to debug which section has issues
- Tab JavaScript must work perfectly

### Option B: Your Suggestion (Separate Pages)

```
shopping/
├── phrases.html          → Key phrases with hints
├── dialogue.html         → Dialogues with tense tabs within
├── story.html           → Stories with tense tabs within
├── manga.html           → Manga content
├── quiz.html            → Quiz questions
└── tips.html            → Cultural tips

Each file includes navigation to other sections
```

**Pros:**
- Smaller individual files (15-25KB each)
- Only load what you need
- Easier to debug and maintain
- Clear separation of content types
- Can work on sections independently

**Cons:**
- Page reload when switching sections
- Navigation must be in every file
- Slightly more files to manage

## Recommended: Hybrid Option C

```
shopping/
├── index.html              → Overview/entry point
├── phrases.html           → Key phrases (standalone)
├── dialogue.html          → ALL dialogues with tense tabs
├── story.html             → ALL stories with tense tabs
├── manga.html             → Manga content
├── quiz.html              → Quizzes
└── tips.html              → Cultural tips
```

**Why this is better:**
1. **Clear URLs**: `shopping/dialogue.html` tells you exactly what you're viewing
2. **Tense tabs stay**: Within dialogue.html, you still have Present/Past/Future/Advanced tabs
3. **Smaller files**: Each file 15-30KB instead of 80KB+
4. **Easy debugging**: If dialogue doesn't work, you know it's dialogue.html
5. **Faster loading**: Only load the section you need
6. **Better organization**: Each file has one clear purpose

## Structure Example

### shopping/dialogue.html
```html
<nav class="section-nav">
  <a href="phrases.html">Phrases</a>
  <a href="dialogue.html" class="active">Dialogue</a>
  <a href="story.html">Story</a>
  <a href="manga.html">Manga</a>
  <a href="quiz.html">Quiz</a>
  <a href="tips.html">Tips</a>
</nav>

<div class="tense-selector">
  <button class="active">Present</button>
  <button>Past</button>
  <button>Future</button>
  <button>Advanced</button>
</div>

<div id="dialogue-present" class="active">
  [Present tense dialogue content]
</div>

<div id="dialogue-past">
  [Past tense dialogue content]
</div>
<!-- etc -->
```

## Implementation Plan

### Phase 1: Create Structure
1. Create shopping/ subdirectory
2. Split current shopping.html into separate files
3. Add section navigation to each file
4. Test all links and navigation

### Phase 2: Populate Content
1. phrases.html gets key phrases section
2. dialogue.html gets all 4 dialogues with tense tabs
3. story.html gets all 4 stories with tense tabs
4. tips.html gets cultural tips
5. manga.html and quiz.html remain placeholders

### Phase 3: Apply to All Topics
1. Repeat structure for restaurant/
2. Repeat structure for travel/
3. Repeat structure for other topics

## File Organization

```
japanese/
├── index.html                    ← Main landing page
│
├── shopping/
│   ├── index.html               ← Shopping overview (or phrases.html)
│   ├── dialogue.html            ← 4 dialogues with tense tabs
│   ├── story.html              ← 4 stories with tense tabs
│   ├── manga.html              ← Manga content
│   ├── quiz.html               ← Quizzes
│   └── tips.html               ← Cultural tips
│
├── restaurant/
│   ├── index.html
│   ├── dialogue.html
│   ├── story.html
│   └── ...
│
├── travel/
│   └── ...
│
├── css/
│   └── shared.css
│
└── js/
    └── shared.js
```

## Navigation Flow

```
Main Index Page
    ↓
Shopping Overview (shopping/index.html)
    ↓
Section Navigation Bar:
    → Phrases
    → Dialogue [Has tense tabs: Present|Past|Future|Advanced]
    → Story [Has tense tabs: Present|Past|Future|Advanced]
    → Manga
    → Quiz
    → Tips
```

## Benefits of This Approach

1. **Matches your expectation**: Key phrases works standalone, dialogue has tense tabs
2. **Better performance**: Load only what's needed (15KB vs 80KB)
3. **Easier debugging**: Know exactly which file has the issue
4. **Clearer URLs**: `shopping/dialogue.html` vs `shopping.html?tab=dialogue`
5. **Independent work**: Can work on story section without affecting dialogue
6. **Better organization**: Each file has single, clear purpose
7. **Scalability**: Easy to add new sections (e.g., vocabulary.html)

## Quick Implementation

Would you like me to:

**Option 1:** Fix the current single-page architecture
- Debug why you're only seeing key phrases
- Ensure tab switching works properly
- Stay with current single-file approach

**Option 2:** Implement the new architecture (recommended)
- Create shopping/ subdirectory
- Split into separate section files (phrases, dialogue, story, etc.)
- Each section file has its own tense tabs where appropriate
- Better organization and performance

## Your Feedback Needed

1. Do you prefer **single page with tabs** (current) or **separate files per section** (proposed)?
2. If separate files, should the entry point be `shopping/index.html` or `shopping/phrases.html`?
3. Should all topics follow the same structure, or just shopping for now?

Let me know your preference and I'll implement it!
