# Kanji Content Creation Skill

Workflow for creating and validating kanji study content.

## Overview

This skill manages the creation of kanji data, flashcard content, and study materials for the kanji module.

## Trigger

Invoke when:
- Adding new kanji sets
- Creating JLPT level data
- Building flashcard content
- Updating kanji metadata

## Data Structure

### Kanji Object
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
  radical: '日',
  frequency: 1,  // Newspaper frequency rank
  examples: [
    {
      word: '日本',
      reading: 'にほん',
      meaning: 'Japan',
      sentence: '日本に行きたいです。',
      sentenceReading: 'にほんにいきたいです。',
      sentenceMeaning: 'I want to go to Japan.'
    }
  ]
}
```

### JLPT Level Files
```
kanji/data/
├── n5-kanji.js   (~100 kanji)
├── n4-kanji.js   (~200 additional)
├── n3-kanji.js   (~350 additional)
├── n2-kanji.js   (~350 additional)
├── n1-kanji.js   (~1000 additional)
└── kanji-index.js (combined reference)
```

## Workflow

### Phase 1: Source Data

1. **Identify Kanji Set**
   - JLPT level
   - Topic-based subset
   - Custom selection

2. **Gather Source Data**
   - Official JLPT lists
   - Frequency rankings
   - Meaning references

3. **Create Base List**
   ```javascript
   // temp/[level]-kanji-base.js
   const kanjiList = [
     { character: '日', level: 'N5' },
     { character: '月', level: 'N5' },
     // ...
   ];
   ```

### Phase 2: Enrich Data

1. **Add Readings**
   - On'yomi (Chinese reading)
   - Kun'yomi (Japanese reading)
   - Special readings for compounds

2. **Add Meanings**
   - Primary meanings
   - Secondary meanings
   - Context notes

3. **Add Metadata**
   - Stroke count
   - Radical
   - Frequency rank

### Phase 3: Generate Examples

1. **Common Words**
   - 2-3 example words per kanji
   - JLPT-appropriate vocabulary
   - Clear meanings

2. **Example Sentences**
   - Simple context
   - Match JLPT level
   - Natural usage

3. **Audio References** (if applicable)
   - Word pronunciation
   - Sentence pronunciation

### Phase 4: Validation

1. **Data Integrity**
   - All required fields present
   - Valid JLPT levels
   - Correct data types

2. **Content Accuracy**
   - Readings correct
   - Meanings accurate
   - Examples natural

3. **Sensei Review**
   - Japanese accuracy check
   - Cultural appropriateness
   - Level appropriateness

### Phase 5: Integration

1. **Generate JavaScript File**
   ```javascript
   // kanji/data/n5-kanji.js
   const N5_KANJI = [
     // ...kanji objects
   ];

   // Export for use
   if (typeof module !== 'undefined') {
     module.exports = N5_KANJI;
   }
   ```

2. **Update Index**
   ```javascript
   // kanji/data/kanji-index.js
   const ALL_KANJI = [
     ...N5_KANJI,
     ...N4_KANJI,
     // ...
   ];
   ```

3. **Test in UI**
   - Flashcard display
   - Filter functionality
   - Search works

## Validation Checklist

### Data Structure
- [ ] Character is single kanji
- [ ] Meanings is non-empty array
- [ ] Readings has onyomi and/or kunyomi
- [ ] Level is valid (N5-N1)
- [ ] StrokeCount is positive integer
- [ ] Examples have all required fields

### Content Accuracy
- [ ] Readings match references
- [ ] Meanings are accurate
- [ ] Examples are natural
- [ ] JLPT level correct
- [ ] No duplicate entries

### Japanese Quality
- [ ] Readings in correct script (カタカナ for on, ひらがな for kun)
- [ ] Example sentences grammatically correct
- [ ] Vocabulary appropriate for level
- [ ] Furigana matches kanji

## Generation Script

```javascript
// temp/generate-kanji-data.js

const fs = require('fs');

function validateKanji(kanji) {
  const required = ['character', 'meanings', 'readings', 'level'];
  for (const field of required) {
    if (!kanji[field]) {
      throw new Error(`Missing ${field} for ${kanji.character}`);
    }
  }

  if (!['N5', 'N4', 'N3', 'N2', 'N1'].includes(kanji.level)) {
    throw new Error(`Invalid level for ${kanji.character}`);
  }

  return true;
}

function generateDataFile(kanjiList, outputPath) {
  kanjiList.forEach(validateKanji);

  const content = `// Generated: ${new Date().toISOString()}
// Count: ${kanjiList.length} kanji

const KANJI_DATA = ${JSON.stringify(kanjiList, null, 2)};

if (typeof module !== 'undefined') {
  module.exports = KANJI_DATA;
}
`;

  fs.writeFileSync(outputPath, content);
}
```

## Integration

- **Entry**: Requirements defined (Architect/PM)
- **Persona**: Developer + Sensei
- **Tools**: Python/JS data generation scripts
- **Exit**: To verification, then code review

## Exit Criteria

Kanji content complete when:
- [ ] All kanji in set defined
- [ ] Data structure valid
- [ ] Content accuracy verified
- [ ] Sensei review passed
- [ ] Integration tested
- [ ] Ready for deployment
