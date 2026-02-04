# Frontend Guidelines

**Last Updated**: 2026-02-04
**Status**: Active
**Part of**: Vibe Coding Gap Analysis (#198, Task 2)

---

## Design Philosophy

### Core Principles

1. **Apple Clarity**: Clean typography, generous spacing, obvious hierarchy
2. **Japanese Minimalism (Ma)**: Embrace negative space, let content breathe
3. **Neobrutalist Accents**: Bold borders on interactive elements for tactile feedback
4. **UX-First**: UI should be obvious; if you need to explain it, simplify it

### Anti-Patterns (Avoid)

- Dense layouts with insufficient whitespace
- Competing visual elements
- Decorative elements that don't serve function
- Inconsistent component styling across playgrounds

---

## Architecture

### Hybrid Approach: Shared CSS + Inline Overrides

```
playgrounds/
├── shared/
│   ├── base.css          # CSS variables, reset, typography
│   ├── components.css    # Buttons, cards, modals, tabs
│   └── utilities.css     # Spacing, flex helpers, responsive
├── workflow-hub.html
├── learning-playground.html
└── ...
```

### File Structure

**shared/base.css** - Design tokens and foundation:
- CSS custom properties (colors, spacing, typography)
- CSS reset/normalize
- Base typography styles

**shared/components.css** - Reusable components:
- Buttons (`.btn`, `.btn-primary`, `.btn-sm`)
- Cards (`.card`, `.card-header`, `.card-body`)
- Modals (`.modal-overlay`, `.modal`, `.modal-header`)
- Tabs (`.tab-bar`, `.tab-btn`, `.tab-panel`)

**shared/utilities.css** - Helper classes:
- Spacing (`.mt-1`, `.p-2`, etc.)
- Flexbox (`.flex`, `.items-center`, `.justify-between`)
- Responsive (`.hidden-mobile`, `.stack-mobile`)

### Usage in Playgrounds

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Playground Name</title>

  <!-- Shared styles -->
  <link rel="stylesheet" href="shared/base.css">
  <link rel="stylesheet" href="shared/components.css">
  <link rel="stylesheet" href="shared/utilities.css">

  <!-- Playground-specific overrides -->
  <style>
    /* Only styles unique to this playground */
    .kanban-column { /* ... */ }
  </style>
</head>
```

---

## Color System

### Design Tokens

```css
:root {
  /* Background */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f5f5f5;
  --color-bg-tertiary: #e5e5e5;
  --color-bg-card: #ffffff;

  /* Text */
  --color-text-primary: #1a1a1a;
  --color-text-secondary: #525252;
  --color-text-muted: #737373;
  --color-text-inverse: #ffffff;

  /* Accent */
  --color-accent: #2563eb;
  --color-accent-hover: #1d4ed8;

  /* Status */
  --color-success: #16a34a;
  --color-warning: #ca8a04;
  --color-danger: #dc2626;

  /* Borders */
  --color-border: #e5e5e5;
  --color-border-strong: #1a1a1a;  /* Neobrutalist accent */

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-brutal: 3px 3px 0 var(--color-border-strong);  /* Neobrutalist */
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #1a1a1a;
    --color-bg-secondary: #262626;
    --color-bg-tertiary: #333333;
    --color-bg-card: #262626;

    --color-text-primary: #f5f5f5;
    --color-text-secondary: #a3a3a3;
    --color-text-muted: #737373;
    --color-text-inverse: #1a1a1a;

    --color-border: #404040;
    --color-border-strong: #f5f5f5;

    --shadow-brutal: 3px 3px 0 var(--color-border-strong);
  }
}
```

### Color Usage

| Use Case | Token |
|----------|-------|
| Page background | `--color-bg-primary` |
| Section background | `--color-bg-secondary` |
| Card background | `--color-bg-card` |
| Body text | `--color-text-primary` |
| Secondary text | `--color-text-secondary` |
| Placeholder/hint | `--color-text-muted` |
| Links, CTAs | `--color-accent` |
| Borders | `--color-border` |
| Interactive borders (neobrutalist) | `--color-border-strong` |

---

## Typography

### Font Stack

```css
:root {
  --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
               'Helvetica Neue', Arial, sans-serif;
  --font-mono: 'SF Mono', Monaco, 'Cascadia Code', Consolas,
               'Liberation Mono', monospace;
}
```

### Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| h1 | 2rem (32px) | 600 | 1.2 |
| h2 | 1.5rem (24px) | 600 | 1.3 |
| h3 | 1.25rem (20px) | 600 | 1.4 |
| Body | 1rem (16px) | 400 | 1.5 |
| Small | 0.875rem (14px) | 400 | 1.5 |
| Caption | 0.75rem (12px) | 400 | 1.4 |

### Typography CSS

```css
body {
  font-family: var(--font-body);
  font-size: 1rem;
  line-height: 1.5;
  color: var(--color-text-primary);
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3 {
  font-weight: 600;
  color: var(--color-text-primary);
}

code, pre {
  font-family: var(--font-mono);
  font-size: 0.875em;
}
```

---

## Spacing

### Spacing Scale (8px base)

| Token | Value | Use |
|-------|-------|-----|
| `--space-1` | 0.25rem (4px) | Tight spacing |
| `--space-2` | 0.5rem (8px) | Related elements |
| `--space-3` | 0.75rem (12px) | Component padding |
| `--space-4` | 1rem (16px) | Standard gap |
| `--space-6` | 1.5rem (24px) | Section padding |
| `--space-8` | 2rem (32px) | Large sections |
| `--space-12` | 3rem (48px) | Page sections |

### Spacing Philosophy

**Japanese Minimalism (Ma)**: Use generous spacing. When in doubt, add more space.

```css
/* Too dense - avoid */
.card { padding: 8px; }
.card + .card { margin-top: 8px; }

/* Better - let content breathe */
.card { padding: var(--space-6); }
.card + .card { margin-top: var(--space-4); }
```

---

## Components

### Buttons

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-2) var(--space-4);
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.5;
  border-radius: 6px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
}

/* Neobrutalist interactive accent */
.btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow-brutal);
}

.btn:active {
  transform: translate(0, 0);
  box-shadow: none;
}

.btn-primary {
  background: var(--color-accent);
  color: var(--color-text-inverse);
  border-color: var(--color-border-strong);
}

.btn-secondary {
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  border-color: var(--color-border-strong);
}

.btn-sm {
  padding: var(--space-1) var(--space-3);
  font-size: 0.75rem;
}
```

### Cards

```css
.card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: var(--space-6);
}

/* Neobrutalist card variant */
.card-interactive {
  border: 2px solid var(--color-border-strong);
  transition: all 0.15s ease;
}

.card-interactive:hover {
  transform: translate(-2px, -2px);
  box-shadow: var(--shadow-brutal);
}

.card-header {
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}
```

### Modals

```css
.modal-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
}

.modal-overlay.active {
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: var(--color-bg-card);
  border: 2px solid var(--color-border-strong);
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 85vh;
  overflow: hidden;
  box-shadow: var(--shadow-brutal);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.modal-body {
  padding: var(--space-6);
  overflow-y: auto;
}
```

### Tabs

```css
.tab-bar {
  display: flex;
  gap: var(--space-1);
  border-bottom: 2px solid var(--color-border);
  padding-bottom: 0;
}

.tab-btn {
  padding: var(--space-2) var(--space-4);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: var(--color-text-primary);
}

.tab-btn.active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
}

.tab-panel {
  display: none;
  padding: var(--space-6) 0;
}

.tab-panel.active {
  display: block;
}
```

### Form Inputs

```css
.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: 1rem;
  border: 2px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  transition: all 0.15s ease;
}

.input:hover {
  border-color: var(--color-border-strong);
}

/* Neobrutalist focus state */
.input:focus {
  outline: none;
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-brutal);
}

.input::placeholder {
  color: var(--color-text-muted);
}
```

---

## Accessibility (WCAG AA)

### Focus Indicators

All interactive elements must have visible focus states:

```css
:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* For elements with custom focus styling */
.btn:focus-visible,
.input:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3);
}
```

### Color Contrast

| Combination | Ratio | Status |
|-------------|-------|--------|
| #1a1a1a on #ffffff | 16:1 | ✅ AAA |
| #525252 on #ffffff | 7.4:1 | ✅ AAA |
| #737373 on #ffffff | 4.6:1 | ✅ AA |
| #f5f5f5 on #1a1a1a | 16:1 | ✅ AAA |

### Keyboard Navigation

| Key | Action |
|-----|--------|
| Tab | Move to next focusable element |
| Shift+Tab | Move to previous focusable element |
| Enter | Activate button, submit form |
| Escape | Close modal, cancel action |
| Arrow keys | Navigate within component (tabs, menus) |

### ARIA Requirements

```html
<!-- Modal -->
<div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <h2 id="modal-title">Modal Title</h2>
</div>

<!-- Tabs -->
<div role="tablist">
  <button role="tab" aria-selected="true" aria-controls="panel-1">Tab 1</button>
  <button role="tab" aria-selected="false" aria-controls="panel-2">Tab 2</button>
</div>
<div role="tabpanel" id="panel-1">Content 1</div>
<div role="tabpanel" id="panel-2" hidden>Content 2</div>

<!-- Status messages -->
<div role="status" aria-live="polite">Changes saved</div>
<div role="alert" aria-live="assertive">Error: Invalid input</div>
```

---

## Responsive Design

### Breakpoints

| Name | Width | Target |
|------|-------|--------|
| Mobile | < 640px | Phones |
| Tablet | 640px - 1023px | Tablets, small laptops |
| Desktop | ≥ 1024px | Laptops, desktops |

### Media Queries

```css
/* Mobile-first approach */
.component {
  /* Mobile styles (default) */
  flex-direction: column;
}

@media (min-width: 640px) {
  .component {
    /* Tablet and up */
    flex-direction: row;
  }
}

@media (min-width: 1024px) {
  .component {
    /* Desktop */
    max-width: 1200px;
  }
}
```

### Responsive Utilities

```css
/* Hide on mobile */
@media (max-width: 639px) {
  .hidden-mobile { display: none !important; }
}

/* Stack on mobile */
@media (max-width: 639px) {
  .stack-mobile {
    flex-direction: column !important;
  }
  .stack-mobile > * + * {
    margin-top: var(--space-4);
    margin-left: 0;
  }
}
```

---

## Dark Mode

### Strategy: Auto-Detect

Respect user's system preference via `prefers-color-scheme`. No manual toggle.

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* Override light mode tokens */
  }
}
```

### Testing Dark Mode

**macOS**: System Preferences → Appearance → Dark
**Chrome DevTools**: Elements → Rendering → Emulate prefers-color-scheme: dark

---

## CDN Dependencies

### Approved Libraries

| Library | Version | CDN URL | Purpose |
|---------|---------|---------|---------|
| Mermaid | 10.9.0 | `https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js` | Diagrams |
| Reveal.js | 4.6.0 | `https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.js` | Slides |
| Panzoom | 9.4.3 | `https://cdn.jsdelivr.net/npm/panzoom@9.4.3/+esm` | Zoom/pan |

### Version Policy

Lock to specific minor versions (e.g., `@10.9.0` not `@10`) to prevent breaking changes.

---

## File Checklist for New Playgrounds

```markdown
- [ ] Links shared CSS files (base.css, components.css, utilities.css)
- [ ] Has `<meta name="viewport">` for responsive
- [ ] Has `lang="en"` on `<html>`
- [ ] Uses design tokens (no hardcoded colors)
- [ ] Has visible focus states on all interactive elements
- [ ] Modals have ARIA attributes
- [ ] Works at 640px width (mobile)
- [ ] Dark mode tested
- [ ] No console errors
```

---

## Migration Guide

### For Existing Playgrounds

1. **Create shared/ directory** with base.css, components.css, utilities.css
2. **Extract common styles** from workflow-hub.html (most complete)
3. **Update each playground**:
   - Add `<link>` to shared CSS files
   - Remove duplicated styles
   - Keep only playground-specific overrides
4. **Add mobile breakpoints** to playgrounds that lack them
5. **Add focus indicators** to all interactive elements
6. **Test** dark mode and mobile views

### Estimated Effort

| Phase | Hours |
|-------|-------|
| Create shared CSS | 4-6h |
| Migrate 6 playgrounds | 6-12h |
| Add mobile support | 3-4h |
| Add accessibility | 2-3h |
| **Total** | **15-25h** |

---

## Version History

| Date | Change |
|------|--------|
| 2026-02-04 | Initial guidelines created |

---

## Related Documents

- [TECH_STACK.md](./TECH_STACK.md) - Technology versions including CDN deps
- [PLAYGROUND_AUDIT.md](../../temp/PLAYGROUND_AUDIT.md) - Baseline audit data
- [DESIGN_PRINCIPLES.md](../standards/DESIGN_PRINCIPLES.md) - General design standards
