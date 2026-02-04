# TDD-031: Interactive Learning Playground

## Overview

**Source PRD**: (Inline requirements from PM)
**Author**: Technical Architect
**Status**: Draft
**Created**: 2026-02-03
**Updated**: 2026-02-03

### Summary

Design a standalone Interactive Learning Playground that transforms markdown documentation into slide-based presentations with rich interactivity. The system transforms FOR_CHRIS educational docs and Claude Memory logs into navigable, visually delightful learning experiences with interactive diagrams, embedded mock UIs, and extensible widget system.

**Key Architecture Principles**:

1. **Extensibility** - Plugin-based widget system for easy addition of new interactive elements
2. **Interactivity** - Rich interactions beyond static content (tooltips, expand/collapse, clickable elements)
3. **Beauty** - Polished visual design with attention to typography, spacing, and animation
4. **Testability** - Comprehensive testing framework built into architecture from day one

---

## Architecture Decisions

This TDD includes three significant architecture decisions documented as standalone ADRs:

| ADR | Title | Status | Location |
|-----|-------|--------|----------|
| ADR-16 | Rendering Framework Selection | Proposed | [ADR-016](../reference/ADR-016-RENDERING-FRAMEWORK.md) |
| ADR-17 | Markdown Extension Syntax | Proposed | [ADR-017](../reference/ADR-017-MARKDOWN-EXTENSION-SYNTAX.md) |
| ADR-18 | Widget Component System | Proposed | [ADR-018](../reference/ADR-018-WIDGET-COMPONENT-SYSTEM.md) |

**Decision Summary**:

- **ADR-16**: Use reveal.js for slide rendering (CDN-loadable, mature ecosystem)
- **ADR-17**: Use fenced code blocks with `widget:type` syntax for interactive elements
- **ADR-18**: Implement registry-based widget system with handler interface

---

## Architecture

### High-Level Design

```
+------------------------------------------------------------------+
|                    Learning Playground                            |
+------------------------------------------------------------------+
|  +--------------------+  +------------------------------------+   |
|  |   Library Panel    |  |        Presentation View           |   |
|  |                    |  |                                    |   |
|  | [Content Source]   |  |  +------------------------------+  |   |
|  |  FOR_CHRIS / Memory|  |  |       Slide Canvas           |  |   |
|  |                    |  |  |                              |  |   |
|  | [Topic Filter]     |  |  |   +----------------------+   |  |   |
|  |  All / Topic Tags  |  |  |   |  Rendered Content    |   |  |   |
|  |                    |  |  |   |  - Markdown          |   |  |   |
|  | [Deck List]        |  |  |   |  - Widgets           |   |  |   |
|  |  - Doc 1           |  |  |   |  - Interactive Elems |   |  |   |
|  |  - Doc 2           |  |  |   +----------------------+   |  |   |
|  |  - Doc 3 (active)  |  |  |                              |  |   |
|  |                    |  |  |  [Slide Progress: 3 / 12]    |  |   |
|  +--------------------+  |  +------------------------------+  |   |
|                          |                                    |   |
|                          |  [<] [Slide Nav] [>] [Overview]    |   |
|                          +------------------------------------+   |
+------------------------------------------------------------------+
|  [Ask Claude] [Share] [Export]              Health: 92 | v0.9   |
+------------------------------------------------------------------+
```

### Component Architecture

```
                          +-------------------+
                          |   App Container   |
                          +-------------------+
                                   |
          +------------------------+------------------------+
          |                        |                        |
   +------v------+         +------v------+          +------v------+
   | LibraryPanel |         |  SlideViewer |          |  ControlBar  |
   +-------------+         +-------------+          +-------------+
          |                        |                        |
   +------v------+         +------v------+          +------v------+
   |ContentSource|         | SlideCanvas  |          | AskClaude   |
   | TopicFilter |         |   (reveal)   |          | (future P2) |
   | DeckList    |         +------+------+          +-------------+
   +-------------+                |
                          +------v------+
                          |WidgetRegistry|
                          +------+------+
                                 |
        +------------+-----+-----+-----+------------+
        |            |           |           |      |
   +----v---+  +----v---+  +----v---+  +----v---+  +----v---+
   |Diagram |  | Quiz   |  |Mock UI |  | Code   |  |Tooltip |
   | Widget |  | Widget |  | Widget |  | Widget |  | Widget |
   +--------+  +--------+  +--------+  +--------+  +--------+
```

### Data Flow

```
  +------------------+     +-------------------+     +------------------+
  |  Content Source  |---->| Markdown Parser   |---->| Slide Generator  |
  | (docs/for_chris) |     | (with extensions) |     | (reveal.js)      |
  |    or memory/    |     +-------------------+     +------------------+
  +------------------+              |                        |
                                   |                        |
                            +------v------+          +------v------+
                            |Widget Blocks|          |   Slides    |
                            |  Extracted  |          |  Rendered   |
                            +------+------+          +------+------+
                                   |                        |
                                   +----------+-------------+
                                              |
                                       +------v------+
                                       |  DOM Ready  |
                                       +------+------+
                                              |
                                       +------v------+
                                       |Widget Render|
                                       |   Pass      |
                                       +-------------+
```

### Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `learning-playground.html` | Main single-file application | `playgrounds/` |
| `ContentParser` | Parse markdown with widget extensions | Inline JS |
| `WidgetRegistry` | Widget type registration and rendering | Inline JS |
| `SlideGenerator` | Convert parsed content to reveal.js slides | Inline JS |
| `LibraryManager` | Deck navigation and content source toggle | Inline JS |
| `ThemeSystem` | Visual styling and beautification | Inline CSS |
| Individual Widgets | Diagram, Quiz, MockUI, etc. | Inline JS modules |

---

## Implementation Details

### Content Parsing Pipeline

```javascript
class ContentParser {
  constructor() {
    this.widgetPattern = /```widget:(\w+)\n([\s\S]*?)```/g;
    this.tooltipPattern = /<!--tooltip:\s*"([^"]+)"-->/g;
  }

  parse(markdown) {
    const slides = [];
    const widgets = [];

    // Step 1: Extract widget blocks and replace with placeholders
    let processed = markdown.replace(this.widgetPattern, (match, type, content) => {
      const id = `widget-${widgets.length}`;
      widgets.push({
        id,
        type,
        config: this.parseYAML(content)
      });
      return `<div class="widget-placeholder" data-widget-id="${id}"></div>`;
    });

    // Step 2: Process inline tooltips
    processed = processed.replace(this.tooltipPattern, (match, text) => {
      return `<span class="tooltip-trigger" data-tooltip="${text}"></span>`;
    });

    // Step 3: Split into slides (using --- or ## headers)
    const slideDelimiter = /\n---\n|(?=^## )/gm;
    const slideContents = processed.split(slideDelimiter);

    return { slides: slideContents, widgets };
  }

  parseYAML(content) {
    // Simple YAML parser for widget configs
    const lines = content.trim().split('\n');
    const result = {};
    let currentKey = null;
    let multilineValue = [];

    for (const line of lines) {
      if (line.match(/^\w+:/)) {
        if (currentKey && multilineValue.length) {
          result[currentKey] = multilineValue.join('\n');
        }
        const [key, ...valueParts] = line.split(':');
        const value = valueParts.join(':').trim();
        currentKey = key.trim();
        if (value === '|') {
          multilineValue = [];
        } else {
          result[currentKey] = this.parseValue(value);
          currentKey = null;
        }
      } else if (currentKey) {
        multilineValue.push(line.replace(/^  /, ''));
      }
    }

    if (currentKey && multilineValue.length) {
      result[currentKey] = multilineValue.join('\n');
    }

    return result;
  }

  parseValue(value) {
    if (value === 'true') return true;
    if (value === 'false') return false;
    if (!isNaN(value)) return Number(value);
    return value.replace(/^["']|["']$/g, '');
  }
}
```

### Library Management

```javascript
class LibraryManager {
  constructor() {
    this.contentSources = {
      'for_chris': {
        label: 'Learning Docs',
        pattern: 'docs/for_chris/*.md',
        topicExtractor: this.extractTopicsFromFrontmatter
      },
      'memory': {
        label: 'Claude Memory',
        pattern: 'memory/*.md',
        topicExtractor: this.extractTopicsFromContent
      }
    };
    this.currentSource = 'for_chris';
    this.decks = [];
  }

  async loadDeckList(source) {
    const manifest = this.getManifest(source);
    this.decks = manifest.map(entry => ({
      ...entry,
      topics: this.contentSources[source].topicExtractor(entry)
    }));
    return this.decks;
  }

  extractTopicsFromFrontmatter(entry) {
    const frontmatter = entry.content.match(/^---\n([\s\S]*?)\n---/);
    if (frontmatter) {
      const tagsMatch = frontmatter[1].match(/tags:\s*\[(.*?)\]/);
      if (tagsMatch) {
        return tagsMatch[1].split(',').map(t => t.trim().replace(/['"]/g, ''));
      }
    }
    return [];
  }

  extractTopicsFromContent(entry) {
    const topics = [];
    if (entry.content.includes('incremental')) topics.push('incremental');
    if (entry.content.includes('test')) topics.push('testing');
    if (entry.content.includes('model')) topics.push('modeling');
    return topics;
  }

  filterByTopic(topic) {
    if (!topic) return this.decks;
    return this.decks.filter(deck => deck.topics.includes(topic));
  }

  getAllTopics() {
    const topics = new Set();
    this.decks.forEach(deck => deck.topics.forEach(t => topics.add(t)));
    return Array.from(topics).sort();
  }
}
```

### Theme System (Beauty Focus)

```css
/* Learning Playground Theme System
   Priority: Visual delight, not utilitarian */

:root {
  /* Primary palette - Warm, inviting learning environment */
  --lp-bg-primary: #fdfcfb;
  --lp-bg-secondary: #f7f5f3;
  --lp-bg-card: #ffffff;
  --lp-bg-code: #1e1e2e;

  /* Accent colors - Educational, trustworthy */
  --lp-accent-primary: #6366f1;     /* Indigo - learning */
  --lp-accent-secondary: #8b5cf6;   /* Purple - insight */
  --lp-accent-success: #22c55e;     /* Green - achievement */
  --lp-accent-warning: #f59e0b;     /* Amber - attention */

  /* Typography */
  --lp-font-display: 'Inter', -apple-system, sans-serif;
  --lp-font-body: 'Source Sans Pro', -apple-system, sans-serif;
  --lp-font-code: 'JetBrains Mono', 'Fira Code', monospace;

  /* Spacing scale */
  --lp-space-xs: 0.25rem;
  --lp-space-sm: 0.5rem;
  --lp-space-md: 1rem;
  --lp-space-lg: 1.5rem;
  --lp-space-xl: 2rem;
  --lp-space-2xl: 3rem;

  /* Animation */
  --lp-transition-fast: 150ms ease;
  --lp-transition-normal: 300ms ease;
  --lp-transition-slow: 500ms ease;

  /* Shadows - Soft, layered */
  --lp-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --lp-shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --lp-shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.12);

  /* Border radius - Friendly, approachable */
  --lp-radius-sm: 0.375rem;
  --lp-radius-md: 0.5rem;
  --lp-radius-lg: 0.75rem;
  --lp-radius-xl: 1rem;
}

/* Dark mode - Cozy, not harsh */
@media (prefers-color-scheme: dark) {
  :root {
    --lp-bg-primary: #1a1a2e;
    --lp-bg-secondary: #16162a;
    --lp-bg-card: #222240;
    --lp-bg-code: #0d0d1a;
  }
}

/* Typography refinements */
.lp-slide h1 {
  font-family: var(--lp-font-display);
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
  background: linear-gradient(135deg, var(--lp-accent-primary), var(--lp-accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.lp-slide h2 {
  font-family: var(--lp-font-display);
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--lp-accent-primary);
  margin-bottom: var(--lp-space-lg);
}

.lp-slide p {
  font-family: var(--lp-font-body);
  font-size: 1.125rem;
  line-height: 1.7;
  color: var(--text-secondary);
  max-width: 65ch; /* Optimal reading width */
}

/* Widget containers */
.lp-widget {
  background: var(--lp-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--lp-radius-lg);
  padding: var(--lp-space-lg);
  margin: var(--lp-space-lg) 0;
  box-shadow: var(--lp-shadow-md);
  transition: var(--lp-transition-normal);
}

.lp-widget:hover {
  box-shadow: var(--lp-shadow-lg);
  transform: translateY(-2px);
}

/* Interactive element styling */
.lp-tooltip-trigger {
  border-bottom: 2px dotted var(--lp-accent-primary);
  cursor: help;
  transition: var(--lp-transition-fast);
}

.lp-tooltip-trigger:hover {
  background: rgba(99, 102, 241, 0.1);
  border-bottom-style: solid;
}

/* Quiz widget specific */
.lp-quiz-option {
  display: flex;
  align-items: center;
  gap: var(--lp-space-md);
  padding: var(--lp-space-md);
  border: 2px solid var(--border-color);
  border-radius: var(--lp-radius-md);
  margin-bottom: var(--lp-space-sm);
  cursor: pointer;
  transition: var(--lp-transition-fast);
}

.lp-quiz-option:hover {
  border-color: var(--lp-accent-primary);
  background: rgba(99, 102, 241, 0.05);
}

.lp-quiz-option.correct {
  border-color: var(--lp-accent-success);
  background: rgba(34, 197, 94, 0.1);
}

/* Progress indicator */
.lp-progress {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--lp-bg-secondary);
}

.lp-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--lp-accent-primary), var(--lp-accent-secondary));
  transition: width var(--lp-transition-normal);
}
```

### File Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `playgrounds/learning-playground.html` | Create | Main single-file application |
| `docs/for_chris/*.md` | Modify | Add widget blocks to existing docs (optional) |
| `docs/reference/ADR_INDEX.md` | Modify | Add ADR-16, ADR-17, ADR-18 entries |
| `docs/reference/ADR-016-RENDERING-FRAMEWORK.md` | Create | reveal.js decision |
| `docs/reference/ADR-017-MARKDOWN-EXTENSION-SYNTAX.md` | Create | Widget syntax decision |
| `docs/reference/ADR-018-WIDGET-COMPONENT-SYSTEM.md` | Create | Registry pattern decision |
| `CLAUDE.md` | Modify | Add Learning Playground to playgrounds table |

---

## Options Analysis

### Option A: Custom HTML/JS (No Framework)

**Approach**: Build slide rendering from scratch using vanilla JS and CSS.

| Pros | Cons |
|------|------|
| Full control over every aspect | Significant development time |
| No external dependencies | Must implement navigation, gestures, keyboard |
| Perfectly aligned with existing patterns | Reinventing the wheel |
| Smallest possible bundle | Quality risk (animations, accessibility) |

**Complexity**: High
**Risk**: Medium (time sink, quality concerns)

### Option B: reveal.js + Custom Widgets (Recommended)

**Approach**: Use reveal.js for slide mechanics, build custom widget system on top.

| Pros | Cons |
|------|------|
| Proven slide mechanics | External dependency (CDN) |
| Beautiful defaults | Learning reveal.js API |
| Focus effort on unique value (widgets) | Some constraints on customization |
| Mobile/touch support built-in | Bundle size (~200KB) |
| Active community, good docs | |

**Complexity**: Medium
**Risk**: Low (mature ecosystem)

### Option C: Slidev (Vue-based)

**Approach**: Use Slidev framework designed for developer presentations.

| Pros | Cons |
|------|------|
| Developer-focused features | Requires build step |
| Vue component ecosystem | Breaks single-file pattern |
| Excellent code highlighting | Heavier dependency chain |
| Live coding support | Learning Vue ecosystem |

**Complexity**: Medium-High
**Risk**: Medium (architectural mismatch)

### Recommendation

**Option B: reveal.js + Custom Widgets**

Rationale:

1. Leverages proven slide mechanics - focus effort on unique value (interactivity)
2. CDN loading preserves single-file pattern
3. Extensive documentation and community support
4. Beautiful themes reduce design burden
5. Plugin system aligns with widget extensibility goal

---

## Testing Strategy

### Unit Tests

The testing framework is built into the architecture with a dedicated test mode.

```javascript
// Test harness embedded in learning-playground.html
class LPTestHarness {
  constructor() {
    this.tests = [];
    this.results = [];
  }

  describe(name, fn) {
    this.tests.push({ name, fn, type: 'suite' });
  }

  it(name, fn) {
    this.tests.push({ name, fn, type: 'test' });
  }

  async run() {
    for (const test of this.tests) {
      try {
        await test.fn();
        this.results.push({ name: test.name, status: 'pass' });
      } catch (error) {
        this.results.push({ name: test.name, status: 'fail', error: error.message });
      }
    }
    return this.results;
  }
}

// Example tests
harness.describe('ContentParser', () => {
  harness.it('should extract widget blocks', () => {
    const parser = new ContentParser();
    const markdown = '# Title\n\n```widget:diagram\ntype: mermaid\n```';
    const { widgets } = parser.parse(markdown);
    assert(widgets.length === 1);
    assert(widgets[0].type === 'diagram');
  });

  harness.it('should split slides on horizontal rule', () => {
    const parser = new ContentParser();
    const markdown = '# Slide 1\n\n---\n\n# Slide 2';
    const { slides } = parser.parse(markdown);
    assert(slides.length === 2);
  });
});

harness.describe('WidgetRegistry', () => {
  harness.it('should register and render widgets', async () => {
    WidgetRegistry.register('test-widget', {
      render(config, container) {
        container.innerHTML = `<div class="test">${config.value}</div>`;
      }
    });
    const container = document.createElement('div');
    await WidgetRegistry.render('test-widget', { value: 'hello' }, container);
    assert(container.innerHTML.includes('hello'));
  });

  harness.it('should gracefully handle unknown widget types', async () => {
    const container = document.createElement('div');
    await WidgetRegistry.render('nonexistent', { foo: 'bar' }, container);
    assert(container.querySelector('.widget-fallback'));
  });
});
```

### Integration Tests

| Test | Description | Validation |
|------|-------------|------------|
| Full deck load | Load a FOR_CHRIS doc as slides | All slides render, widgets functional |
| Navigation | Keyboard and click navigation | Correct slide transitions |
| Widget rendering | All widget types render | No console errors, correct output |
| Content source toggle | Switch between FOR_CHRIS and Memory | Deck list updates, content loads |
| Topic filtering | Filter by topic tag | Only matching decks shown |
| Dark mode | Theme switch | All colors update, no contrast issues |

### Visual Regression Testing

```javascript
class VisualTester {
  async captureSlide(slideIndex) {
    Reveal.slide(slideIndex);
    await new Promise(resolve => setTimeout(resolve, 500));
    const canvas = await html2canvas(document.querySelector('.reveal'));
    return canvas.toDataURL();
  }

  async compareSnapshots(baseline, current) {
    // Pixel-by-pixel comparison, return diff percentage
  }
}
```

### Test Mode Activation

```javascript
// Activate test mode via URL parameter
if (new URLSearchParams(location.search).get('test') === 'true') {
  harness.run().then(results => harness.renderResults());
}
```

---

## Implementation Sequence

### Phase 1: Foundation (P0 - MVP)

1. [ ] Create `learning-playground.html` with basic structure
2. [ ] Implement ContentParser with widget extraction
3. [ ] Integrate reveal.js via CDN
4. [ ] Implement basic slide generation from markdown
5. [ ] Create WidgetRegistry framework
6. [ ] Implement Diagram widget (Mermaid support)
7. [ ] Implement Code widget with syntax highlighting
8. [ ] Library panel with deck list (hardcoded manifest initially)
9. [ ] Basic navigation controls
10. [ ] Apply theme system (beautiful defaults)

### Phase 2: Interactivity (P1)

11. [ ] Implement Tooltip widget (inline definitions)
12. [ ] Implement Expandable widget (collapsible sections)
13. [ ] Add diagram interactivity (tooltips, click handlers)
14. [ ] Content source toggle (FOR_CHRIS / Memory)
15. [ ] Topic extraction and filtering
16. [ ] Slide overview mode
17. [ ] Keyboard shortcuts panel

### Phase 3: Advanced Widgets (P2)

18. [ ] Implement Quiz widget with feedback
19. [ ] Implement MockUI widget framework
20. [ ] Implement Terminal widget (type-along)
21. [ ] Implement Comparison widget (slider/toggle)
22. [ ] "Ask Claude" integration placeholder
23. [ ] Live playground sandboxes (iframe-based)

### Phase 4: Polish and Testing (P3)

24. [ ] Embedded test harness
25. [ ] Visual regression baseline
26. [ ] Performance optimization (lazy loading)
27. [ ] Accessibility audit and fixes
28. [ ] Mobile responsiveness refinement
29. [ ] Export functionality (PDF, standalone HTML)
30. [ ] Documentation and examples

---

## Security Considerations

1. **XSS Prevention**: Sanitize markdown content before rendering
   - Use DOMPurify for HTML sanitization
   - Escape widget config values before DOM insertion

2. **CDN Integrity**: Use SRI (Subresource Integrity) hashes for CDN scripts
   ```html
   <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.js"
           integrity="sha384-..." crossorigin="anonymous"></script>
   ```

3. **Iframe Sandboxing**: For live playground sandboxes, use restrictive sandbox
   ```html
   <iframe sandbox="allow-scripts" srcdoc="..."></iframe>
   ```

4. **No External Data Fetch**: All content is local files, no API calls to untrusted sources

---

## Performance Considerations

1. **Lazy Widget Loading**: Only render widgets when slide becomes visible
   ```javascript
   Reveal.on('slidechanged', event => {
     const widgets = event.currentSlide.querySelectorAll('.widget-placeholder');
     widgets.forEach(placeholder => {
       if (!placeholder.dataset.rendered) {
         renderWidget(placeholder);
         placeholder.dataset.rendered = 'true';
       }
     });
   });
   ```

2. **Mermaid Diagram Caching**: Cache rendered SVGs in memory

3. **Content Chunking**: For large decks, only parse visible slides + neighbors

4. **Animation Performance**: Use `transform` and `opacity` for animations (GPU-accelerated)

---

## Dependencies

### External (CDN-loaded)

| Dependency | Version | Purpose | Size |
|------------|---------|---------|------|
| reveal.js | 4.6.x | Slide framework | ~150KB |
| reveal.js markdown plugin | 4.6.x | Markdown parsing | ~20KB |
| reveal.js highlight plugin | 4.6.x | Code highlighting | ~30KB |
| mermaid | 10.x | Diagram rendering | ~200KB (lazy) |
| DOMPurify | 3.x | XSS prevention | ~15KB |

---

## Open Questions

1. **Content Manifest**: How should the deck list be populated in single-file HTML?
   - Option A: Hardcode manifest in JS (recommended initially)
   - Option B: Fetch from a small JSON file
   - Option C: Use File System Access API (limited browser support)

2. **Memory Log Parsing**: How to structure memory logs as coherent slides?
   - Daily logs may not have natural slide boundaries
   - Need heuristics for splitting (by entry? by theme?)

3. **Ask Claude Integration**: What API/mechanism for P2 feature?
   - Requires Claude API key (security concern in browser)
   - Could use a local proxy or defer to desktop app integration

4. **Offline Support**: Should the playground work fully offline?
   - Would require bundling CDN dependencies
   - Increases file size significantly

---

## Related

- **ADR-16**: [Rendering Framework Selection](../reference/ADR-016-RENDERING-FRAMEWORK.md)
- **ADR-17**: [Markdown Extension Syntax](../reference/ADR-017-MARKDOWN-EXTENSION-SYNTAX.md)
- **ADR-18**: [Widget Component System](../reference/ADR-018-WIDGET-COMPONENT-SYSTEM.md)
- **ADR Index**: [docs/reference/ADR_INDEX.md](../reference/ADR_INDEX.md)
- **Existing Playgrounds**: [docs/for_chris/PLAYGROUND-TOOLS.md](../for_chris/PLAYGROUND-TOOLS.md)
- **reveal.js Docs**: https://revealjs.com/
- **Mermaid Docs**: https://mermaid.js.org/

---

## Appendix A: Widget Handler Template

```javascript
// Template for creating new widget types
const NewWidget = {
  type: 'new-widget',

  // Required: Render the widget
  async render(config, container) {
    container.innerHTML = `
      <div class="lp-widget lp-widget-${this.type}">
        <!-- Widget content here -->
      </div>
    `;
    this.attachListeners(container);
  },

  // Optional: Clean up when widget is destroyed
  destroy(container) {
    // Remove event listeners, clear timers, etc.
  },

  // Optional: Get current widget state
  getState(container) {
    return { /* Serializable state */ };
  },

  // Optional: Restore widget state
  setState(container, state) {
    // Apply state to widget
  },

  // Internal helpers
  attachListeners(container) {
    // Event binding
  }
};

// Register the widget
WidgetRegistry.register('new-widget', NewWidget);
```

---

## Appendix B: Sample Widget-Enhanced Document

```markdown
---
tags: [dbt, modeling, architecture]
title: Three-Layer Architecture
---

# Three-Layer dbt Architecture

Understanding the Bronze-Silver-Gold pattern.

---

## The Layers

Data flows through three transformation stages.

Each layer has a specific purpose<!--tooltip: "This is called separation of concerns"-->.

---

## Knowledge Check

(Quiz widget would test understanding of layer purposes)

---

## Try It Yourself

(Terminal widget would show dbt commands to run)
```
