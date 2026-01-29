# Japanese Content Rules

Guidelines for Japanese language content accuracy and presentation.

## JLPT Level System

### Level Overview
| Level | Kanji | Vocabulary | Grammar | Target Audience |
|-------|-------|------------|---------|-----------------|
| N5 | ~100 | ~800 | Basic | Absolute beginner |
| N4 | ~300 | ~1,500 | Elementary | Beginner |
| N3 | ~650 | ~3,750 | Intermediate | Pre-intermediate |
| N2 | ~1,000 | ~6,000 | Upper-intermediate | Intermediate |
| N1 | ~2,000 | ~10,000 | Advanced | Advanced |

### Current Project Level
- Target: N5/N4 (Duolingo level 42 equivalent)
- Future: Progressive difficulty (N5 → N1 toggle)

### Level Enforcement
- Tag all content with JLPT level
- Don't mix levels without indication
- Provide furigana for above-level kanji
- Include vocabulary level in data

## Writing Systems

### Kanji (漢字)
- Include furigana (reading) for all kanji
- Indicate JLPT level
- Provide stroke order for study modules
- Common readings: on'yomi and kun'yomi

### Hiragana (ひらがな)
- Used for:
  - Native Japanese words without kanji
  - Grammatical particles
  - Verb and adjective endings
  - Furigana readings

### Katakana (カタカナ)
- Used for:
  - Foreign loanwords (外来語)
  - Emphasis (like italics)
  - Onomatopoeia
  - Scientific/technical terms

### Mixed Text
```html
<!-- Correct format with furigana -->
<ruby>日本語<rt>にほんご</rt></ruby>を<ruby>勉強<rt>べんきょう</rt></ruby>しています。
```

## Romanization (Rōmaji)

### System: Modified Hepburn
- Most widely used internationally
- Consistent with English pronunciation intuition

### Key Rules
| Japanese | Romanization |
|----------|--------------|
| し | shi (not si) |
| ち | chi (not ti) |
| つ | tsu (not tu) |
| ふ | fu (not hu) |
| じ | ji (not zi) |
| しゃ | sha |
| ちゃ | cha |

### Long Vowels
| Type | Example | Romanization |
|------|---------|--------------|
| おう | 東京 | Tōkyō or Toukyou |
| おお | 大きい | ōkii or ookii |
| えい | 先生 | sensei |
| ああ | お母さん | okaasan |

### Particles
- は (topic) → wa
- を (object) → o
- へ (direction) → e

## Politeness Levels

### Keigo (敬語) Categories
| Level | Usage | Example |
|-------|-------|---------|
| **丁寧語** (teineigo) | Polite, general use | です、ます forms |
| **尊敬語** (sonkeigo) | Respect to others | いらっしゃる |
| **謙譲語** (kenjōgo) | Humble about self | 参る |

### Context Matching
- Customer service: 丁寧語 + 尊敬語
- Casual dialogue: Plain form
- Business: 丁寧語 minimum
- Friends: Plain/casual

### Consistency
- Match politeness to scenario
- Don't mix registers inappropriately
- Note context in content metadata

## Content Types

### Phrases (phrases.html)
- Key vocabulary grouped by theme
- Include: Japanese, furigana, romaji, English
- Audio pronunciation for each phrase
- Usage notes where relevant

### Dialogue (dialogue.html)
- Natural conversation flow
- Character names/roles
- Context setting
- Audio for full dialogue and individual lines

### Story (story.html)
- Narrative reading practice
- Graded by JLPT level
- Vocabulary notes sidebar
- Comprehension questions

### Manga (manga.html)
- Visual storytelling
- Natural speech patterns
- Onomatopoeia explained
- Cultural context notes

### Quiz (quiz.html)
- Tests content from other pages
- Multiple question types
- Immediate feedback
- Progress tracking

### Tips (tips.html)
- Cultural notes
- Grammar explanations
- Learning strategies
- Mnemonics

## Data Structure

### Kanji Data
```javascript
{
  character: '日',
  meanings: ['day', 'sun', 'Japan'],
  readings: {
    onyomi: ['ニチ', 'ジツ'],
    kunyomi: ['ひ', 'か']
  },
  level: 'N5',
  strokeCount: 4,
  examples: [
    { word: '日本', reading: 'にほん', meaning: 'Japan' }
  ]
}
```

### Vocabulary Data
```javascript
{
  japanese: '食べる',
  reading: 'たべる',
  romaji: 'taberu',
  english: 'to eat',
  partOfSpeech: 'verb-ichidan',
  level: 'N5',
  examples: [
    {
      japanese: 'りんごを食べます',
      english: 'I eat an apple'
    }
  ]
}
```

### Dialogue Data
```javascript
{
  id: 'restaurant-01',
  title: 'At a Restaurant',
  context: 'Ordering food at a casual restaurant',
  level: 'N5',
  lines: [
    {
      speaker: 'Staff',
      japanese: 'いらっしゃいませ！',
      romaji: 'Irasshaimase!',
      english: 'Welcome!'
    }
  ]
}
```

## Audio Requirements

### Format
- MP3 for broad compatibility
- 44.1kHz, 128kbps minimum
- Clear pronunciation
- Natural speed (not too slow)

### Naming
```
topics/[topic]/audio/[content]-[id].mp3
kanji/audio/[character].mp3
```

### Quality
- Native speaker preferred
- Clear enunciation
- Appropriate pitch accent
- No background noise

## Common Mistakes to Check

### Grammar
- Particle errors (は vs が, に vs で)
- Verb conjugation mistakes
- Adjective i/na confusion
- て-form errors

### Vocabulary
- Unnatural word combinations
- Archaic expressions in modern context
- Too formal/casual for situation
- Katakana for native words

### Cultural
- Inappropriate directness
- Wrong bowing/greeting context
- Seasonal inappropriateness
- Gender-specific language misuse

## Quality Checklist

### For All Japanese Content
- [ ] JLPT level appropriate
- [ ] Furigana for all kanji
- [ ] Romanization follows Hepburn
- [ ] Natural phrasing (not textbook stiff)
- [ ] Politeness level matches context
- [ ] Cultural accuracy verified
- [ ] Audio quality acceptable
- [ ] Examples are realistic

### For Dialogues
- [ ] Speaker roles clear
- [ ] Conversation flows naturally
- [ ] Appropriate responses
- [ ] Cultural context noted

### For Kanji/Vocabulary
- [ ] All readings included
- [ ] Meanings accurate
- [ ] Examples useful
- [ ] Stroke order correct (kanji)
