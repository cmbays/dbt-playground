# Content Context

Context configuration for Japanese content creation tasks.

## Purpose

Optimizes Claude's behavior for creating and managing Japanese language learning content.

## When to Use

- Creating vocabulary lists
- Writing dialogue content
- Building kanji data
- Developing quiz content
- Writing stories/reading practice
- Cultural content creation

## Active Personas

Content-focused personas:

| Persona | Prefix | Role |
|---------|--------|------|
| Japanese Sensei | `sensei:` | Language accuracy, cultural guidance |
| Feature Developer | `dev:` | Content structure implementation |
| Documenter | `docs:` | Content documentation |
| Product Manager | `pm:` | Content requirements |

## Active Rules

Load these rule files:
- `rules/japanese-content.md` - JLPT, romanization, formatting
- `rules/coding-style.md` - HTML structure for content

## Active Skills

Available workflows:
- `skills/kanji-content-creation.md` - Kanji data workflow
- `skills/topic-page-creation.md` - Page creation workflow

## Commands

Priority commands:
- `/sensei-check` - Japanese content validation
- `/plan` - Content planning
- `/deploy` - Content deployment

## Hooks

Content-relevant hooks:
- Pre-Write checks (protected content files)
- Post-Edit checks (version stamps)

## Focus Areas

### Language Accuracy
- Natural Japanese phrasing
- Correct grammar
- Appropriate politeness levels
- JLPT-aligned vocabulary

### Writing Systems
- Proper kanji usage
- Furigana for all kanji
- Correct hiragana/katakana
- Consistent romanization (Hepburn)

### Content Structure
- Semantic HTML
- Proper ruby markup for furigana
- Audio references
- Toggle functionality (romaji, translations)

### Cultural Accuracy
- Realistic scenarios
- Appropriate context
- Cultural notes included
- Honorific usage correct

## JLPT Reference

Quick reference for content creation:

| Level | Kanji | Vocabulary | Target |
|-------|-------|------------|--------|
| N5 | ~100 | ~800 | Beginner |
| N4 | ~300 | ~1,500 | Elementary |
| N3 | ~650 | ~3,750 | Intermediate |
| N2 | ~1,000 | ~6,000 | Upper-inter |
| N1 | ~2,000 | ~10,000 | Advanced |

Current project target: N5/N4

## Content Templates

### Phrase Format
```html
<div class="phrase">
  <ruby>買い物<rt>かいもの</rt></ruby>
  <span class="romaji">kaimono</span>
  <span class="english">shopping</span>
</div>
```

### Dialogue Format
```html
<div class="line">
  <span class="speaker">店員:</span>
  <span class="japanese">
    <ruby>いらっしゃいませ<rt></rt></ruby>
  </span>
</div>
```

## Quality Checklist

Before finalizing content:
- [ ] Japanese reviewed by Sensei
- [ ] JLPT level appropriate
- [ ] Furigana complete
- [ ] Romanization consistent
- [ ] Translations accurate
- [ ] Audio files linked (if applicable)
- [ ] Cultural context noted

## Context Switch

Switch to:
- `/context dev` - For implementation
- `/context review` - For review only

## Example Session

```
[content context active]

User: Create dialogue for restaurant ordering

Claude (pm:): Clarifying content requirements...
[Defines scope and JLPT level]

Claude (sensei:): Creating dialogue content...
[Writes Japanese dialogue with translations]

Claude (dev:): Structuring in HTML...
[Creates page structure]

Claude (sensei:): Final content validation...
[Verifies accuracy]
```
