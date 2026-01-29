# Design Principles & UI/UX Standards

## Purpose

This document defines the visual and interaction design standards for the Japanese learning website. All pages should follow these principles for consistency and professional appearance.

---

## Design Philosophy

**Core Values**:
1. **Clarity** - Content should be easy to read and understand
2. **Consistency** - Similar elements look and behave the same way across pages
3. **Accessibility** - Design works for all users, all devices
4. **Delight** - Subtle animations and polish create engaging experience

**User Experience Goals**:
- Minimize cognitive load - don't make users think
- Provide clear visual hierarchy - important things stand out
- Give immediate feedback - users know when they interact with something
- Support mobile learners - responsive design is essential

---

## Color Palette

### Primary Colors
```
Purple Gradient Background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Primary Purple: #667eea  (buttons, headings, interactive elements)
Deep Purple: #764ba2     (gradient end, accents)
```

### Neutral Colors
```
Text Dark: #333          (primary text)
Text Medium: #495057     (secondary text)
Text Light: #6c757d      (subtle text)
Text Subtle: #64748b     (hints, metadata)
Background White: #ffffff
Background Light: #f8f9fa (sections, cards)
Background Gray: #e9ecef  (dividers, borders)
```

### Accent Colors
```
Success Green: #10b981   (correct answers, positive feedback)
Blue: #1e40af            (links, info)
Dark Blue: #1e293b       (strong emphasis)
```

### Usage Guidelines
- **Primary Purple (#667eea)** for all primary actions (buttons, nav, headings)
- **White (#ffffff)** for content backgrounds
- **Light Gray (#f8f9fa)** for section backgrounds
- **Dark (#333)** for body text
- **Green (#10b981)** only for success/correct states

---

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
             'Helvetica Neue', Arial, sans-serif;
```

**Rationale**: System fonts for speed, native feel, excellent readability

### Font Sizes
```
Page Title (h1): 2.5em         (40px at default)
Section Heading (h2): 2em      (32px at default)
Subsection (h3): 1.5em         (24px at default)
Body Text: 1em / 16px          (default)
Large Text: 1.2em              (19px - subtitles)
Small Text: 0.9em              (14px - metadata)
```

### Japanese Text Sizing
- **Kanji/Kana**: Same size as English or slightly larger for readability
- **Furigana**: 0.6em (60% of base text size)
- **Romaji**: 0.9em (90% of base text size)

### Line Height
```
Body Text: 1.6              (relaxed reading)
Headings: 1.2               (tighter spacing)
Japanese Text: 1.8          (extra space for complexity)
```

### Font Weights
```
Regular: 400                (body text)
Semi-Bold: 600              (buttons, nav, emphasis)
Bold: 700                   (headings)
```

---

## Spacing System

Use consistent spacing multiples for visual rhythm:

```
Tiny: 5px       (tight gaps)
Small: 10px     (element padding)
Medium: 20px    (section padding, standard gaps)
Large: 30px     (major sections)
XL: 50px        (page-level spacing)
XXL: 60px       (landing page spacing)
```

### Padding Standards
```
Buttons: 12px 24px          (vertical horizontal)
Cards: 20-30px all sides
Sections: 20px
Container: 20px
```

### Margin Standards
```
Between sections: 20-30px
Between cards: 15-20px
Between paragraphs: 15px
Between related elements: 10px
```

---

## Layout & Structure

### Container
```css
max-width: 1400px          (prevents too-wide content)
margin: 0 auto             (centers content)
border-radius: 20px        (rounded corners)
background: white          (content background)
```

### Grid Patterns
```
Card Grids: grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))
Responsive: Adapts number of columns based on screen width
Gap: 20-30px between items
```

### Section Organization
```
1. Header (gradient background, white text)
2. Navigation (light gray background, centered)
3. Content Area (white background, centered)
4. Cards/Tabs (organized sections within content)
```

---

## Interactive Elements

### Buttons

**Primary Buttons** (Main actions):
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
color: white
border-radius: 25px        (pill shape)
padding: 12px 24px
font-weight: 600
transition: all 0.3s ease
```

**Secondary Buttons** (Navigation, less emphasis):
```css
background: white
color: #667eea
border: 2px solid #667eea
border-radius: 25px
padding: 12px 24px
```

**Hover States**:
- Primary: slightly darker, slight scale (1.05), lifted shadow
- Secondary: filled background (#667eea), white text

**Active States**:
- Add visual feedback (scale, color change, shadow)
- Never leave users wondering if click registered

### Links
```css
color: #1e40af              (blue for links)
text-decoration: none       (clean look)
hover: underline            (indicate clickability)
```

### Form Elements
*To be defined when forms are added*

---

## Cards & Containers

### Standard Card
```css
background: white
border-radius: 15-20px
padding: 20-30px
box-shadow: 0 4px 6px rgba(0,0,0,0.1)
transition: all 0.3s ease
```

**Hover Effect**:
```css
transform: translateY(-5px)
box-shadow: 0 10px 20px rgba(102, 126, 234, 0.2)
```

### Content Cards (Kanji, Phrases, etc.)
```css
background: #f8f9fa         (light gray)
border-left: 4px solid #667eea (accent stripe)
border-radius: 10px
padding: 15-20px
margin-bottom: 15px
```

---

## Responsive Design

### Breakpoints
```css
Mobile: < 768px            (phone)
Tablet: 768px - 1024px     (tablet)
Desktop: > 1024px          (desktop/laptop)
```

### Mobile Adaptations
- **Navigation**: Stack vertically or collapse to hamburger (if needed)
- **Grid**: Single column on mobile
- **Font sizes**: Slightly smaller but still readable (minimum 16px)
- **Touch targets**: Minimum 44x44px for buttons
- **Padding**: Reduce to 15-20px on mobile

### Responsive Patterns
```css
@media (max-width: 768px) {
    /* Mobile styles */
    body { padding: 10px; }
    .header h1 { font-size: 2em; }
    .container { border-radius: 10px; }
}
```

---

## Animations & Transitions

### Standard Transitions
```css
transition: all 0.3s ease;   (default for most elements)
```

### Specific Animations

**Fade In** (page load):
```css
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
animation: fadeIn 0.8s ease-in-out;
```

**Pulse** (draw attention):
```css
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}
```

### Animation Guidelines
- Keep animations subtle (0.3-0.8 seconds)
- Use easing functions (ease, ease-in-out)
- Don't animate everything - only meaningful interactions
- Respect user motion preferences (prefers-reduced-motion)

---

## Accessibility Standards

### Color Contrast
- Text on white: minimum 4.5:1 ratio (WCAG AA)
- Large text (18px+): minimum 3:1 ratio
- Test: Use browser DevTools or online contrast checkers

### Interactive Elements
- **Buttons**: Clear hover/focus states
- **Focus indicators**: Visible outline for keyboard navigation
- **Touch targets**: Minimum 44x44px (iOS guidelines)
- **Error states**: Don't rely on color alone (use text/icons)

### Text Readability
- Line length: 50-75 characters ideal
- Line height: 1.6 for body text
- Font size: minimum 16px (1em) for body text
- Avoid pure black (#000) on pure white - use softer contrast

### Screen Readers
- Use semantic HTML (header, nav, main, article, etc.)
- Add alt text to images
- Use aria-labels where needed
- Maintain logical heading hierarchy (h1 → h2 → h3)

---

## Component Patterns

### Home Icon (Fixed Position)
```css
position: fixed
top: 20px
left: 20px
z-index: 1000
font-size: 2.5em
background: white
width: 60px
height: 60px
border-radius: 50%         (circle)
box-shadow: 0 4px 12px rgba(0,0,0,0.15)
```

### Navigation Bar
```css
background: #f8f9fa
padding: 20px
display: flex
gap: 10px
justify-content: center
flex-wrap: wrap
```

### Content Tabs (Modality Selector)
```css
display: flex
gap: 10px
padding: 15px
background: #f8f9fa
border-radius: 10px
```

### Tense Selector (Sub-navigation)
```css
display: flex
gap: 10px
margin: 15px 0
justify-content: center
flex-wrap: wrap
```

---

## Japanese-Specific Design

### Furigana Display
```css
Position above kanji
Font size: 0.6em
Color: #64748b (subtle)
Line height: minimal (keep close to kanji)
```

### Ruby Text (HTML)
```html
<ruby>
    漢字
    <rt>かんじ</rt>
</ruby>
```

### Audio Buttons
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
color: white
border-radius: 50%         (circle)
width: 30-40px
height: 30-40px
font-size: 18px
```

### Hint Buttons
```css
background: white
border: 2px solid #667eea
color: #667eea
border-radius: 50%         (circle)
width: 30px
height: 30px
font-weight: 700
```

---

## File References

- **Primary CSS**: `css/shared.css` (all pages must link this)
- **Page-specific styles**: Use `<style>` tag in `<head>` only when necessary
- **Never duplicate**: Styles in shared.css should never be recreated in individual pages

---

## Design Checklist

When creating new pages:
- [ ] Links to `css/shared.css`
- [ ] Uses established color palette
- [ ] Follows typography standards
- [ ] Consistent spacing (multiples of 5/10px)
- [ ] Buttons have hover/active states
- [ ] Responsive on mobile (<768px)
- [ ] Animations are subtle (0.3-0.8s)
- [ ] Text contrast meets WCAG AA
- [ ] Touch targets are 44x44px minimum
- [ ] Semantic HTML structure

---

*Last Updated: 2026-01-19*
*Next Review: When new patterns emerge or user feedback indicates changes needed*
