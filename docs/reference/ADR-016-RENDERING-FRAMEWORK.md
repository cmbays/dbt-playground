# ADR-016: Rendering Framework Selection

## Status

**Accepted**

## Context

The Interactive Learning Playground needs to render markdown documentation as interactive slide-based presentations. The rendering solution must:

1. **Integrate with single-file HTML pattern** - Existing playgrounds are self-contained HTML files
2. **Support custom interactive widgets** - Beyond standard markdown (diagrams, quizzes, mock UIs)
3. **Be visually beautiful** - Not utilitarian; polished, delightful experience
4. **Be extensible** - Easy to add new widget types without modifying core
5. **Support mobile/touch** - Responsive, gesture-friendly navigation
6. **Have reasonable performance** - Fast initial load, smooth transitions

### Options Considered

1. **Custom HTML/JS** - Build everything from scratch
2. **reveal.js** - Mature presentation framework with CDN availability
3. **Slidev** - Vue-based developer presentation tool
4. **Marp** - Markdown-to-slides converter
5. **impress.js** - CSS3-powered presentations

## Decision

Use **reveal.js** as the slide rendering engine with a custom widget layer built on top.

## Rationale

### Comparison Matrix

| Criterion | Custom HTML/JS | reveal.js | Slidev | Marp | impress.js |
|-----------|----------------|-----------|--------|------|------------|
| Single-file capable | Yes (complex) | Yes (CDN) | No (build) | Yes (limited) | Yes (CDN) |
| Markdown support | Manual parsing | Built-in plugin | Built-in | Native | Limited |
| Plugin system | Build from scratch | Mature ecosystem | Vue components | Limited | Limited |
| Visual quality | Full control | Excellent themes | Excellent | Basic | Excellent |
| Touch/mobile | Manual | Built-in | Good | Good | Poor |
| Learning curve | High | Low | Medium | Low | Medium |
| Extensibility | Unlimited | Good API | Vue-based | Limited | Limited |
| CDN availability | N/A | Yes (jsdelivr) | No | No | Yes |
| Community/docs | N/A | Excellent | Good | Good | Fair |
| Bundle size | Minimal | ~200KB | ~500KB+ | ~50KB | ~50KB |

### Why reveal.js

1. **CDN Loading Preserves Single-File Pattern**

   ```html
   <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.js"></script>
   <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.css">
   ```

   No build step required. The playground remains a single HTML file that works by double-clicking.

2. **Mature Plugin Ecosystem**
   - Markdown plugin for content parsing
   - Highlight.js plugin for code syntax highlighting
   - Notes plugin for speaker notes
   - Zoom plugin for diagram inspection
   - Math plugin if needed for formulas

3. **Beautiful Built-in Themes**

   reveal.js ships with professional themes (black, white, league, beige, sky, night, serif, simple, solarized) that can be customized via CSS variables. This reduces our design burden.

4. **Comprehensive Navigation**
   - Keyboard shortcuts (arrows, space, escape for overview)
   - Touch gestures (swipe)
   - Mouse wheel support
   - URL fragment navigation (shareable slide links)
   - Overview mode (bird's eye view)

5. **API for Programmatic Control**

   ```javascript
   // Navigate programmatically
   Reveal.slide(2, 1); // Go to slide 2, vertical slide 1

   // Listen for events
   Reveal.on('slidechanged', event => {
     // Trigger widget rendering
   });

   // Get state
   const { indexh, indexv } = Reveal.getState();
   ```

   This API is essential for integrating our widget system.

6. **Responsive by Default**

   Scales slides to fit viewport automatically. Works on mobile without additional effort.

### Why Not Custom HTML/JS

Building from scratch would require implementing:

- Slide transitions and animations
- Keyboard navigation
- Touch gesture handling
- Overview mode
- URL fragment routing
- Responsive scaling
- Accessibility features

This represents significant development time with quality risk. reveal.js has solved these problems over 10+ years.

### Why Not Slidev

Slidev is excellent but:

- Requires Node.js build step
- Vue.js dependency (learning curve, weight)
- Cannot produce single-file HTML without bundling
- Overkill for our use case (we do not need live coding features)

### Why Not Marp

Marp is lightweight but:

- Limited interactivity (static slides)
- No plugin system for custom widgets
- Cannot add click handlers or dynamic content easily

## Consequences

### Positive

- **Fast development**: Focus on unique value (widgets) rather than slide mechanics
- **Proven quality**: Animations, accessibility, and mobile support battle-tested
- **Easy onboarding**: Developers familiar with reveal.js can contribute immediately
- **Beautiful defaults**: Professional appearance with minimal styling effort
- **Future flexibility**: Large plugin ecosystem if we need additional features

### Negative

- **External dependency**: Requires CDN access (or bundling for offline)
- **Bundle size**: ~200KB for reveal.js + plugins (acceptable for modern connections)
- **Some constraints**: Cannot completely customize transition behavior

### Mitigation

1. **CDN Dependency**
   - Use CDN with integrity hashes for security
   - Document offline bundling option for air-gapped environments
   - Use `<script>` fallback pattern:
     ```html
     <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.js"
             onerror="alert('CDN unavailable. Please check network connection.')">
     </script>
     ```

2. **Bundle Size**
   - Lazy-load mermaid and other heavy plugins
   - Use minified CDN versions
   - Accept trade-off: 200KB is reasonable for the functionality gained

3. **Customization Constraints**
   - reveal.js is highly customizable via CSS and config
   - Can override any behavior via event listeners
   - If truly blocked, can fork (MIT license)

## Implementation Notes

### Basic Integration

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/theme/white.css">
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <section>Slide 1</section>
      <section>Slide 2</section>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.js"></script>
  <script>
    Reveal.initialize({
      hash: true,
      plugins: []
    });
  </script>
</body>
</html>
```

### Widget Integration Point

```javascript
Reveal.on('ready', event => {
  // Initial widget render for first slide
  renderWidgetsInSlide(event.currentSlide);
});

Reveal.on('slidechanged', event => {
  // Render widgets when slide changes (lazy loading)
  renderWidgetsInSlide(event.currentSlide);
});
```

### Configuration Options

```javascript
Reveal.initialize({
  // Navigation
  hash: true,           // URL fragments for sharing
  history: true,        // Browser back/forward

  // Display
  width: 1280,          // Slide width
  height: 720,          // Slide height
  margin: 0.1,          // Margin around slides
  minScale: 0.2,        // Minimum zoom
  maxScale: 2.0,        // Maximum zoom

  // Behavior
  center: true,         // Vertical centering
  progress: true,       // Progress bar
  controls: true,       // Navigation arrows
  keyboard: true,       // Keyboard navigation
  touch: true,          // Touch gestures
  overview: true,       // Overview mode (Esc)

  // Appearance
  transition: 'slide',  // none/fade/slide/convex/concave/zoom
  backgroundTransition: 'fade'
});
```

## Related

- **TDD**: [TDD-031-LEARNING-PLAYGROUND.md](../specs/TDD-031-LEARNING-PLAYGROUND.md)
- **ADR-17**: [Markdown Extension Syntax](ADR-017-MARKDOWN-EXTENSION-SYNTAX.md)
- **ADR-18**: [Widget Component System](ADR-018-WIDGET-COMPONENT-SYSTEM.md)
- **reveal.js Documentation**: https://revealjs.com/
- **reveal.js GitHub**: https://github.com/hakimel/reveal.js

## Approval

- **Decision Level**: Low (single-feature, external dependency)
- **Approver**: Architect
- **Date**: 2026-02-04
