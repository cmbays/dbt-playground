# Architecture Overview

## System Architecture

### High-Level Structure

```
┌─────────────────────────────────────────┐
│         index.html (Landing)            │
│    Topic Cards: Home, Shopping, etc.    │
└──────────────┬──────────────────────────┘
               │ (User clicks topic)
               ▼
┌─────────────────────────────────────────┐
│      Topic Folder (e.g., /shopping)     │
│                                         │
│  Pages: phrases, dialogue, story, etc.  │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  Each page links to:             │   │
│  │  - css/shared.css (cached)       │   │
│  │  - js/shared.js (cached)         │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Key Architectural Decisions

**1. Modular Structure**
- Each topic in separate folder (/home, /shopping, /restaurant, /travel)
- Each content type in separate HTML file
- Shared resources (CSS/JS) cached across all pages

**Benefits**:
- Fast page loads (only new HTML downloaded after first visit)
- Easy maintenance (change CSS once, applies everywhere)
- Scalable (add new topics without affecting existing ones)
- Clear organization (files organized by topic and type)

**2. Shared Resources**
- `css/shared.css` - All styling for consistency
- `js/shared.js` - All JavaScript functionality

**Benefits**:
- Consistency across entire site
- Browser caching improves performance
- Single source of truth for styles and behavior
- Changes propagate automatically

**3. Client-Side Interactions**
- No server required (static HTML site)
- All interactivity via JavaScript
- Tense switching, audio, hints handled in browser

**Benefits**:
- Simple deployment (just serve files)
- Fast interactions (no server round-trips)
- Works offline (once loaded)
- Easy to host (GitHub Pages, Netlify, etc.)

---

## File Organization

For complete directory structure and file locations, see **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**.

**Key organizational principles**:
- **Topic-based folders** (/home, /shopping, /restaurant, /travel) - each topic is self-contained
- **Shared resources** (css/, js/) - loaded once, cached across all pages
- **Documentation hierarchy** (docs/, temp/, archive/) - living, version-specific, and historical
- **Work-in-progress isolation** (temp/) - protects production files during development

---

## Component Architecture

### Page Structure (Typical Topic Page)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Topic] - [Content Type]</title>
    <link rel="stylesheet" href="../css/shared.css">
    <!-- Version: v0.X.X - Updated: YYYY-MM-DD -->
</head>
<body>
    <!-- Home icon (fixed position, top-left) -->
    <a href="../index.html" class="home-icon">🏠</a>

    <div class="container">
        <!-- Header (gradient background) -->
        <div class="header">
            <h1>[Topic Title]</h1>
            <p>[Subtitle]</p>
        </div>

        <!-- Navigation (topic selection) -->
        <div class="navigation">
            <button class="nav-btn" onclick="window.location='../home/phrases.html'">
                Home
            </button>
            <button class="nav-btn" onclick="window.location='../shopping/phrases.html'">
                Shopping
            </button>
            <!-- ... more topic buttons -->
        </div>

        <!-- Content area -->
        <div class="content">
            <!-- Section-specific content tabs (if applicable) -->
            <div class="modality-tabs">
                <button class="modality-tab" onclick="window.location='phrases.html'">
                    Phrases
                </button>
                <button class="modality-tab active" onclick="window.location='dialogue.html'">
                    Dialogue
                </button>
                <!-- ... more section buttons -->
            </div>

            <!-- Main content -->
            <div class="scenario-card">
                <!-- Content goes here -->
            </div>
        </div>
    </div>

    <script src="../js/shared.js"></script>
</body>
</html>
```

### CSS Organization (shared.css)

```
1. Reset & Base Styles
   - Box model reset
   - Body fonts, colors, background

2. Layout Components
   - .container (max-width, centering)
   - .header (gradient background)
   - .navigation (flex layout)
   - .content (main content area)

3. Navigation Elements
   - .nav-btn (topic navigation)
   - .modality-tab (section navigation)
   - .tense-btn (tense selection)
   - .home-icon (fixed home button)

4. Content Components
   - .phrase-card
   - .dialogue-exchange
   - .story-content
   - .kanji-card

5. Interactive Elements
   - .audio-btn
   - .hint-btn
   - Hover/active states

6. Responsive Styles
   - @media (max-width: 768px)
   - Mobile adaptations

7. Animations
   - @keyframes fadeIn
   - Transitions
```

### JavaScript Organization (shared.js)

```javascript
// 1. Navigation Functions
function showScenario(id) { ... }
function showModality(scenario, modality) { ... }
function showTense(scenario, modality, tense) { ... }

// 2. Interactive Features
function speak(text, button) { ... }        // Audio pronunciation
function toggleHint(btn) { ... }            // Show/hide hints
function toggleKanji(card) { ... }          // Flip kanji cards

// 3. Quiz System (when implemented)
function checkQuiz(el, correct, quizId) { ... }
function updateScore() { ... }

// 4. Initialization
function initializePage() { ... }
document.addEventListener('DOMContentLoaded', initializePage);
```

---

## Data Flow

### Initial Page Load

```
1. Browser requests index.html
2. Loads css/shared.css (cached for future)
3. Loads js/shared.js (cached for future)
4. Displays topic cards
```

### Navigation to Topic Page

```
1. User clicks topic card
2. Browser navigates to /[topic]/phrases.html
3. Uses CACHED css/shared.css (no download!)
4. Uses CACHED js/shared.js (no download!)
5. Only downloads new HTML (~15-25KB)
```

**Result**: Subsequent pages load 80-90% faster due to caching

### User Interactions

```
1. User clicks button (e.g., audio, hint, tense)
2. JavaScript function called
3. DOM manipulation (show/hide, style changes)
4. Feedback to user (animation, sound, etc.)
5. No page reload required (all client-side)
```

---

## Performance Characteristics

### File Sizes
```
index.html:        ~12KB
Topic page HTML:   ~15-25KB
css/shared.css:    ~15KB (cached)
js/shared.js:      ~10KB (cached)
```

### Load Times (typical)
```
First visit:       ~50KB total (index + CSS + JS)
Second page:       ~20KB (just HTML, CSS/JS cached)
Third page:        ~20KB (just HTML, CSS/JS cached)
```

### Caching Strategy
```
HTML:   No cache (always fresh content)
CSS:    1 week cache (update with version changes)
JS:     1 week cache (update with version changes)
Audio:  1 month cache (rarely changes)
```

---

## Scalability

### Adding New Topics
```
1. Create new folder: /[topic-name]/
2. Copy template pages from existing topic
3. Update content (keep structure identical)
4. Add topic card to index.html
5. Update navigation in shared template
6. Test navigation links
```

### Adding New Content Types
```
1. Create new page type (e.g., grammar.html)
2. Follow existing page structure
3. Add to all topic folders
4. Update section navigation
5. Test across all topics
```

### Adding New Features
```
1. Add functionality to shared.js
2. Available to all pages immediately
3. Update relevant pages to use new feature
4. Test across topics
```

---

## Technology Stack

### Frontend
- **HTML5**: Semantic markup, ruby tags for furigana
- **CSS3**: Flexbox, Grid, gradients, animations, media queries
- **JavaScript (ES6+)**: DOM manipulation, Web Speech API, event handling

### No Backend Required
- Static site (HTML/CSS/JS only)
- No database needed
- No server-side processing
- Content embedded in HTML

### Browser APIs Used
- **Web Speech API**: Text-to-speech for pronunciation
- **LocalStorage**: Potential future use for progress tracking
- **Service Workers**: Potential future use for offline support

---

## Future Architectural Considerations

### Potential Enhancements
1. **Dynamic Content Loading**: Fetch content from JSON files
2. **State Management**: Track user progress across sessions
3. **Offline Support**: Service workers for offline learning
4. **Backend Integration**: Optional server for progress sync
5. **API Integration**: Dictionary API, translation API

### Maintaining Simplicity
- Start simple, add complexity only when needed
- Keep static approach unless clear benefit to dynamic
- Prioritize learning content over technical complexity

---

## Architectural Principles

1. **Keep It Simple**: Static site architecture is sufficient for current needs
2. **Consistency**: Shared resources ensure uniform experience
3. **Performance**: Caching and small file sizes prioritize speed
4. **Scalability**: Topic-based organization grows easily
5. **Maintainability**: Changes in one place propagate everywhere
6. **Accessibility**: Semantic HTML, WCAG standards, responsive design

---

*Last Updated: 2026-01-19*
*Next Review: After first complete topic finalized*
