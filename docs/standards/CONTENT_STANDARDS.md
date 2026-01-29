---
audience: [sensei, developer]
priority: medium
size: medium
dependencies: []
last_updated: 2026-01-25
status: active
tags: [standards, japanese, jlpt, content]
---

# Japanese Content Standards

## Purpose

This document defines standards for Japanese language content on the website, including writing conventions, JLPT level guidelines, and pedagogical approaches.

---

## Current Content Level

**Target Learner**: Duolingo level 42 (approximate JLPT N5/N4 range)
**Primary Focus**: Practical, conversational Japanese for travel and daily life

**Future Enhancement**: JLPT level toggle (N5 → N1) to adjust content difficulty dynamically

---

## JLPT Level Guidelines

### JLPT N5 (Beginner)
**Characteristics**:
- ~800 vocabulary words
- ~100 kanji
- Basic grammar particles (は, を, に, で, が, etc.)
- Present and past tense
- Simple sentence structures

**Content Examples**:
- こんにちは (Hello)
- これはいくらですか (How much is this?)
- トイレはどこですか (Where is the bathroom?)

**When to use**: First-time learners, basic phrases, simple dialogues

---

### JLPT N4 (Elementary)
**Characteristics**:
- ~1,500 vocabulary words
- ~300 kanji
- て-form, た-form, casual vs. polite speech
- More complex particles (から, まで, と, や, etc.)
- Can describe experiences and give reasons

**Content Examples**:
- この服を試着してもいいですか (May I try on these clothes?)
- 昨日友達と映画を見に行きました (Yesterday I went to see a movie with a friend)

**Current Primary Level**: Most content should be N4 level

---

### JLPT N3 (Intermediate)
**Characteristics**:
- ~3,700 vocabulary words
- ~650 kanji
- Conditional forms (たら, ば, なら, と)
- Passive and causative forms
- Can understand everyday conversation fairly well

**Content Examples**:
- もし時間があれば、京都に行きたいです (If I have time, I want to go to Kyoto)
- 予約をキャンセルしなければなりません (I must cancel my reservation)

**When to use**: "Advanced" tense tabs, complex scenarios

---

### JLPT N2 & N1 (Advanced/Fluent)
**Characteristics**:
- N2: ~6,000 words, ~1,000 kanji
- N1: ~10,000 words, ~2,000 kanji
- Keigo (honorific language), formal business language
- Complex expressions, idioms, nuance

**Current Status**: Not yet implemented
**Future Use**: Toggle for advanced learners

---

## Writing Conventions

### Japanese Script Mix

**Standard Format**: Kanji + Hiragana + Katakana (as appropriate)

**Kanji Usage**:
- Use kanji for common words that learners should recognize
- Match JLPT level (N5: ~100 kanji, N4: ~300 kanji, etc.)
- Always provide furigana for kanji at N5/N4 levels

**Hiragana Usage**:
- Grammar particles (は, が, を, に, etc.)
- Verb endings and inflections
- Words without common kanji
- Function words (です, ます, etc.)

**Katakana Usage**:
- Foreign loanwords (コーヒー coffee, レストラン restaurant)
- Emphasis (optional, limited use)
- Onomatopoeia

**Examples**:
```
Good: 私は学生です (わたし, がくせい with furigana)
Avoid: わたしはがくせいです (too childish, no kanji practice)
```

---

### Furigana Standards

**When to Provide Furigana**:
- ALL kanji at N5/N4 levels (current primary audience)
- First occurrence of kanji in a section
- Uncommon or difficult readings

**HTML Format**:
```html
<ruby>
    漢字
    <rt>かんじ</rt>
</ruby>
```

**Visual Standards**:
- Font size: 0.6em (60% of kanji size)
- Color: #64748b (subtle gray, per design principles)
- Position: Directly above kanji
- Spacing: Minimal line height

**Furigana Toggle** (future feature):
- Allow users to show/hide furigana
- Default: Show (for beginners)
- Advanced learners can hide for practice

---

### Romaji Standards

**When to Provide Romaji**:
- Key phrases section (helps absolute beginners)
- First encounter with important expressions
- Audio pronunciation guides

**Romaji System**: Modified Hepburn (most common for learners)

**Format**:
```
Japanese: こんにちは
Furigana: (built into kanji if applicable)
Romaji: Konnichiwa
English: Hello
```

**Romaji Toggle** (future feature):
- Allow users to show/hide romaji
- Default: Show for beginners
- Encourages transition away from romaji over time

**Important**: Don't rely solely on romaji - always include Japanese script

---

### Translation Standards

**English Translations**:
- Provide for all phrases and sentences
- Natural English (not word-for-word literal)
- Context-appropriate

**Format**:
```
いくらですか
Ikura desu ka?
How much is it?
```

**Translation Levels**:
1. **Word-for-word** (for grammar lessons): "How much / is / question"
2. **Natural translation** (for conversation): "How much is it?"
3. **Cultural notes** (when needed): "In Japan, haggling is not common"

**Current Standard**: Use natural translation unless explicitly teaching grammar

---

## Content Types Standards

### 1. Phrases (phrases.html)

**Purpose**: Key vocabulary and common expressions

**Format**:
```html
<div class="phrase-card">
    <div class="phrase-japanese">
        <ruby>日本語<rt>にほんご</rt></ruby>
    </div>
    <div class="phrase-romaji">Nihongo</div>
    <div class="phrase-english">Japanese language</div>
    <button class="audio-btn" onclick="speak('日本語')">🔊</button>
</div>
```

**Guidelines**:
- 10-20 essential phrases per topic
- Progress from simple to complex
- Include pronunciation audio
- Group related phrases together

---

### 2. Dialogue (dialogue.html)

**Purpose**: Conversational practice with back-and-forth exchanges

**Format**:
```html
<div class="dialogue-exchange">
    <div class="speaker">Person A:</div>
    <div class="japanese-text">
        <ruby>質問<rt>しつもん</rt></ruby>します。
    </div>
    <div class="translation">I have a question.</div>
</div>
```

**Guidelines**:
- Natural conversation flow
- Realistic scenarios (not textbook-stiff)
- 6-10 exchanges per dialogue
- Different speakers clearly identified
- Include response patterns learners can reuse

**Tense Progression**:
- **Present**: Happening now scenarios
- **Past**: Completed actions, experiences
- **Future**: Plans, intentions
- **Advanced**: Mixed tenses, complex grammar

---

### 3. Story (story.html)

**Purpose**: Narrative reading comprehension

**Format**:
```html
<div class="story-content">
    <p class="story-paragraph">
        <ruby>今日<rt>きょう</rt></ruby>は
        <ruby>天気<rt>てんき</rt></ruby>がいいです。
    </p>
    <p class="translation">The weather is nice today.</p>
</div>
```

**Guidelines**:
- 5-10 sentences per story
- Narrative arc (beginning, middle, end)
- Uses vocabulary from phrases section
- Can include descriptions, actions, dialogue
- Translation after each paragraph or section

---

### 4. Manga (manga.html)

**Purpose**: Visual storytelling with Japanese text

**Format**: *To be defined when implemented*

**Guidelines** (proposed):
- Speech bubbles with Japanese text
- Furigana in bubbles
- Translation panel below or beside
- Visual context aids comprehension
- Cultural elements in illustrations

---

### 5. Quiz (quiz.html)

**Purpose**: Interactive knowledge testing

**Format**: *To be defined when implemented*

**Guidelines** (proposed):
- Multiple choice questions
- Fill-in-the-blank exercises
- Matching exercises (Japanese ↔ English)
- Audio comprehension questions
- Immediate feedback
- Score tracking

---

### 6. Tips (tips.html)

**Purpose**: Cultural notes and learning guidance

**Format**:
```html
<div class="tip-card">
    <h3 class="tip-title">💡 Cultural Note: Bowing</h3>
    <p class="tip-content">
        In Japan, bowing is a common greeting...
    </p>
</div>
```

**Content Types**:
- Cultural context (bowing, removing shoes, etc.)
- Grammar explanations (particle usage, etc.)
- Pronunciation tips
- Common mistakes to avoid
- Learning strategies

---

## Audio Standards

### Audio File Format
**Preferred**: MP3 (universal browser support)
**Alternative**: OGG (for future optimization)

### Audio File Naming
```
Format: [topic]_[contenttype]_[phrase-id].mp3

Examples:
shopping_phrase_01.mp3
restaurant_dialogue_greeting.mp3
travel_story_airport.mp3
```

### Audio Implementation
```javascript
function speak(text, button) {
    // Use Web Speech API for dynamic pronunciation
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ja-JP';  // Japanese
    utterance.rate = 0.8;       // Slightly slower for learners
    speechSynthesis.speak(utterance);
}
```

**Guidelines**:
- Native or near-native pronunciation
- Clear enunciation (slightly slower than native speed)
- Natural intonation (not robotic)
- Consistent voice across content

---

## Grammar Explanation Standards

**When to Explain Grammar**:
- First use of new grammar pattern
- In "Tips" section
- In "Advanced" content with complex structures

**Format**:
```
Grammar Pattern: [Japanese pattern]
Meaning: [What it expresses]
Usage: [When/how to use]
Example: [Japanese sentence with translation]
```

**Example**:
```
Grammar Pattern: ～てもいいですか
Meaning: "Is it okay if I...?" (asking permission)
Usage: Use when requesting permission politely
Example: 写真を撮ってもいいですか
         (Shashin o totte mo ii desu ka?)
         May I take a photo?
```

---

## Cultural Notes Standards

**When to Include**:
- Customs that differ significantly from Western culture
- Etiquette important for travelers
- Context that helps understand language use

**Format**:
```
🏯 Cultural Note: [Title]
[2-4 sentence explanation]
[Practical tip if applicable]
```

**Examples**:
- Removing shoes indoors
- Honorific language with service staff
- Gift-giving etiquette
- Onsen (hot spring) rules
- Train etiquette

**Tone**: Informative, non-judgmental, practical

---

## Content Consistency Checklist

When creating new content:
- [ ] Appropriate JLPT level (primarily N5/N4)
- [ ] Kanji + Hiragana mix (not all hiragana)
- [ ] Furigana provided for all kanji
- [ ] Romaji included for key phrases
- [ ] Natural English translation
- [ ] Audio pronunciation available
- [ ] Cultural context when relevant
- [ ] Consistent formatting with existing pages
- [ ] HTML ruby tags for furigana
- [ ] Semantic HTML structure

---

## Vocabulary Tracking

**Future Enhancement**: Track vocabulary across topics

Maintain a master vocabulary list:
- Word (kanji + kana)
- Reading (hiragana)
- Meaning (English)
- JLPT level
- Topic(s) where it appears
- First introduced (which page)

**Purpose**:
- Ensure consistent usage across pages
- Build progressive vocabulary
- Enable vocabulary quizzes
- Support spaced repetition features

---

## Content Review Process

**Before Publishing New Content**:
1. Check JLPT level appropriateness
2. Verify furigana accuracy
3. Test audio pronunciation
4. Review translation naturalness
5. Confirm cultural notes accuracy
6. Get native speaker review (if possible)

**Periodic Review**:
- Quarterly content audit
- Update based on user feedback
- Refine based on learning outcomes

---

## Resources for Content Creation

**Dictionaries**:
- Jisho.org - Japanese-English dictionary
- Tangorin.com - Vocabulary and example sentences
- NHK News Web Easy - Simplified Japanese news (N5-N3)

**Grammar Resources**:
- Tae Kim's Guide to Japanese Grammar
- Imabi.net - Comprehensive grammar guide
- Bunpro.jp - Grammar point database

**JLPT Resources**:
- JLPT official website (jlpt.jp/e/)
- JLPT Sensei - Study materials by level

**Cultural Resources**:
- Japan Guide (japan-guide.com)
- Tofugu - Japanese culture and language blog

---

*Last Updated: 2026-01-19*
*Next Review: After first complete topic (Home or Shopping)*
