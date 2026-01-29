# Coding Style Rules

Standards for HTML, CSS, and JavaScript in this project.

## HTML Standards

### Structure

- Use semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`)
- Consistent 2-space indentation
- Comments for major sections: `<!-- Navigation -->`, `<!-- Main Content -->`
- Version comment at top: `<!-- Version: vX.Y.Z - Updated: YYYY-MM-DD -->`

### Naming

- Lowercase with hyphens for IDs and classes: `flashcard-container`, `jlpt-filter`
- Meaningful names that describe purpose, not appearance: `primary-action` not `blue-button`

### Accessibility

- All images have `alt` attributes
- Form inputs have associated `<label>` elements
- Interactive elements are keyboard accessible
- Color is not the only indicator of state
- Proper heading hierarchy (h1 → h2 → h3)

### Links

- External links use `target="_blank" rel="noopener noreferrer"`
- Internal navigation verified after any structural changes
- Breadcrumbs for nested pages

## CSS Standards

### Organization

- Use `css/shared.css` for all shared styles
- Page-specific styles in `<style>` tags only when necessary
- Custom properties (CSS variables) defined in shared.css

### Custom Properties

```css
:root {
  /* Colors */
  --color-primary: #...;
  --color-secondary: #...;
  --color-background: #...;
  --color-text: #...;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 2rem;
  --spacing-xl: 4rem;

  /* Typography */
  --font-family-base: ...;
  --font-family-japanese: ...;
  --font-size-base: 1rem;
}
```

### Responsive Design

- Mobile-first approach
- Breakpoints:
  - Small: 320px - 767px
  - Medium: 768px - 1023px
  - Large: 1024px+
- Use `rem` units for typography, `em` for component spacing
- Flexible layouts with flexbox/grid

### Naming Convention (BEM-inspired)

```css
.component { }
.component__element { }
.component--modifier { }

/* Examples */
.flashcard { }
.flashcard__front { }
.flashcard__back { }
.flashcard--flipped { }
```

## JavaScript Standards

### Organization

- Use `js/shared.js` for common functionality
- Page-specific scripts in `<script>` tags or dedicated files
- Vanilla JavaScript only (no frameworks currently)

### Naming

- camelCase for variables and functions: `filterByLevel`, `currentCard`
- PascalCase for classes/constructors: `FlashcardManager`
- UPPER_SNAKE_CASE for constants: `MAX_CARDS`, `JLPT_LEVELS`
- Descriptive names that describe action: `handleFilterChange`, `renderCard`

### Functions

- Clear function names that describe actions
- Single responsibility per function
- JSDoc comments for public functions:

```javascript
/**
 * Filters kanji array by JLPT level
 * @param {Array} kanji - Array of kanji objects
 * @param {string} level - JLPT level (N5-N1)
 * @returns {Array} Filtered kanji array
 */
function filterByLevel(kanji, level) { }
```

### Error Handling

- Try/catch for JSON parsing, audio loading, external resources
- Graceful degradation for missing features
- User-friendly error messages (not technical jargon)

### DOM Manipulation

- Prefer `textContent` over `innerHTML` for text
- Sanitize any dynamic HTML content
- Cache DOM references for repeated access
- Use event delegation where appropriate

### State Management

- localStorage for user preferences and progress
- Validate stored data before use
- Clear naming for storage keys: `jlpt-filter-level`, `flashcard-progress`

## File Organization

### Naming

- Lowercase with hyphens: `story-morning.html`, `kanji-data.js`
- Descriptive names: `shopping-dialogue.html` not `page2.html`
- Consistent patterns within directories

### Directory Structure

```
topics/[topic-name]/
├── index.html
├── phrases.html
├── dialogue.html
├── story.html
├── manga.html
├── quiz.html
└── tips.html
```

## Comments

### When to Comment

- Complex logic that isn't self-evident
- Workarounds with explanation
- TODO items with context
- Version information

### When NOT to Comment

- Self-explanatory code
- Every function (only public/complex ones)
- Removed code (delete it, don't comment out)

### Format

```javascript
// Single line for brief notes

/*
 * Multi-line for longer explanations
 * that need more context
 */

// TODO: Description of what needs to be done
// FIXME: Description of known issue
```

## Code Quality

### Avoid

- Global variables (use closures or modules)
- Magic numbers (use named constants)
- Deep nesting (refactor to functions)
- Copy-paste code (extract to functions)
- Over-engineering for hypothetical futures

### Prefer

- Small, focused functions
- Early returns to reduce nesting
- Descriptive variable names over comments
- Existing patterns from shared resources
