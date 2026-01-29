# Sensei Check Command

Validate Japanese language content for accuracy and appropriateness.

## Usage
```
/sensei-check [file or content]
```

## Examples
```
/sensei-check topics/shopping/dialogue.html
/sensei-check "いらっしゃいませ、何名様ですか？"
/sensei-check kanji/data/n5-kanji.js
```

## Validation Areas

### 1. Language Accuracy
- [ ] Grammar correctness
- [ ] Natural phrasing (not textbook stiff)
- [ ] Appropriate politeness level
- [ ] Context-appropriate vocabulary

### 2. Writing Systems
- [ ] Kanji appropriate for JLPT level
- [ ] Furigana provided for all kanji
- [ ] Hiragana/katakana correct
- [ ] No mixing errors (ず/づ, じ/ぢ)

### 3. Romanization
- [ ] Consistent romanization system (Hepburn)
- [ ] Long vowels handled correctly
- [ ] Particles romanized appropriately

### 4. Cultural Context
- [ ] Culturally appropriate scenarios
- [ ] Realistic dialogue situations
- [ ] Proper honorific usage
- [ ] Seasonal/situational awareness

### 5. JLPT Alignment
- [ ] Content matches stated JLPT level
- [ ] Vocabulary within level
- [ ] Grammar within level
- [ ] Kanji within level

## JLPT Level Reference

| Level | Kanji | Vocabulary | Description |
|-------|-------|------------|-------------|
| N5 | ~100 | ~800 | Basic, beginner |
| N4 | ~300 | ~1,500 | Elementary |
| N3 | ~650 | ~3,750 | Intermediate |
| N2 | ~1,000 | ~6,000 | Upper intermediate |
| N1 | ~2,000 | ~10,000 | Advanced |

## Validation Report Format

```markdown
## Sensei Check: [File/Content]

### Summary
[Overall assessment]

### Language Issues
| Location | Issue | Correction | Severity |
|----------|-------|------------|----------|
| Line X | Issue | Fix | High/Med/Low |

### Writing System Issues
| Location | Issue | Correction |
|----------|-------|------------|

### Cultural Notes
- Note 1
- Note 2

### JLPT Alignment
- Current content level: [estimated]
- Stated level: [if specified]
- Mismatches: [list any]

### Recommendations
1. Recommendation
2. Recommendation

### Verdict
- [ ] Approved
- [ ] Minor corrections needed
- [ ] Significant revision needed
```

## Common Issues

### Grammar
- て形 (te-form) errors
- Particle misuse (は vs が, に vs で)
- Verb conjugation mistakes
- Adjective conjugation errors

### Vocabulary
- Over-formal for casual context
- Too casual for formal context
- Archaic expressions
- Unnatural word combinations

### Cultural
- Inappropriate directness
- Missing expected phrases
- Wrong politeness level for relationship
- Seasonal inappropriateness

## Persona Integration

This command activates the **Japanese Sensei** (`sensei:`) persona for content validation.

## Integration Points

The Sensei Check should be invoked:
- After dialogue content creation
- Before vocabulary lists are finalized
- During flashcard data validation
- As part of the review process for Japanese content

## Usage in Orchestration

In the assembly line workflow, Sensei Check is typically called:
1. During TDD phase for content requirements
2. As a parallel review alongside Code Review
3. Before final deployment of content pages
