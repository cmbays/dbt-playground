# Future Features & Enhancement Ideas
**Living Document** - Updated as new ideas emerge
**Created:** 2026-01-20
**Last Updated:** 2026-01-24

---

## GitHub Tracking

Features are tracked through GitHub milestones and issues:
- **Roadmap**: [docs/ROADMAP.md](../ROADMAP.md)
- **Milestones**: [View All](https://github.com/cmbays/japanese-study-site/milestones)
- **Active PRDs**: [Phase 1 Issues](https://github.com/cmbays/japanese-study-site/issues?q=is%3Aissue+label%3Aphase%3A1)

### Feature → PRD → Issue Flow
1. Features are documented here by priority tier
2. High-priority features get full PRDs in `docs/specs/PRD-*.md`
3. Each PRD creates a GitHub issue linked to a milestone
4. Issues track implementation through labels (`status:*`, `persona:*`)

---

## Overview

This document tracks feature ideas and enhancements for the Japanese Study Site. Features are prioritized based on:
1. **Scientific evidence** of learning effectiveness
2. **User engagement** patterns from successful products (Duolingo, WaniKani, Anki)
3. **Technical feasibility** for a static/client-side implementation
4. **Value-to-effort ratio** for a solo developer project

---

## Research-Backed Priorities

### The Science of Language Learning

| Principle | Evidence | Application |
|-----------|----------|-------------|
| **Spaced Repetition** | Ebbinghaus forgetting curve; PNAS research shows optimized SRS outperforms all heuristics | Core study mode must use SRS |
| **Active Recall** | Testing effect - actively retrieving information strengthens memory | Flashcard flipping, quiz modes |
| **Mnemonics** | Story-based associations significantly improve retention | Kanji mnemonics like WaniKani |
| **Comprehensible Input** | Krashen's i+1; 70-90% comprehension optimal | Content at appropriate JLPT level |
| **Habit Formation** | Cue-routine-reward loops drive long-term engagement | Streaks, daily goals, notifications |
| **Loss Aversion** | People work harder to avoid losing than to gain | Streak protection mechanics |
| **Progress Visualization** | Tangible evidence of improvement fuels motivation | XP, levels, progress bars, heatmaps |

### Competitor Feature Analysis

| App | Strengths | Weaknesses | Learn From |
|-----|-----------|------------|------------|
| **Duolingo** | Gamification, habit formation, 128M MAU | No grammar explanation, "too easy" | Streak system, XP, daily goals |
| **WaniKani** | Mnemonics, structured kanji progression | Kanji-only, subscription cost | Story-based memorization |
| **Anki** | Powerful SRS, full customization | Steep learning curve | SM-2 algorithm |
| **Bunpro** | Grammar focus, SRS for grammar | Narrow scope | Grammar point structure |

---

## Tier 1: Core Learning Engine (v0.3 - v0.5)
*These features form the scientific foundation of effective learning*

### 🔴 Spaced Repetition System (SRS)
**Priority:** CRITICAL | **Effort:** High | **Version:** v0.3-v0.4

The backbone of language learning retention. Research proves SRS is the most effective method for vocabulary memorization.

**Implementation:**
- **SM-2 Algorithm** (Anki-style) or **MEMORIZE Algorithm** (Duolingo research)
- Track per-card: last review date, interval, ease factor, repetitions
- Store in localStorage with export capability
- Cards scheduled based on predicted forgetting point

**Self-Assessment Buttons:**
- **Again** (0%) - Complete fail, reset interval
- **Hard** (50%) - Struggled, short interval
- **Good** (80%) - Knew with effort, standard interval
- **Easy** (100%) - Instant recall, extended interval

**Due Cards System:**
- Dashboard showing "X cards due today"
- Overdue cards highlighted
- Session complete celebration when all due cards reviewed

### 🔴 Streak & Habit System
**Priority:** CRITICAL | **Effort:** Medium | **Version:** v0.3

Research shows streaks increase commitment by 60%. The cue-routine-reward loop is essential for habit formation.

**Core Features:**
- **Daily Streak Counter** - Consecutive days of study
- **Streak Freeze** - Protect streak (1 free per week, or earn through XP)
- **Daily Goal** - "Study X cards today" (user-configurable)
- **Study Reminder** - Browser notification at user-set time (with permission)

**Visual Feedback:**
- Fire/flame animation for active streak
- Streak milestone celebrations (7, 30, 100, 365 days)
- "Streak at risk!" warning if no study by evening

### 🔴 Mastery Tracking System
**Priority:** CRITICAL | **Effort:** Medium | **Version:** v0.3-v0.4

Track true knowledge state with bidirectional progress—mastery earned through success, lost through failure. This creates meaningful stakes and accurate progress representation.

**Kanji Mastery Stages (WaniKani-inspired):**
| Stage | Mastery % | Behavior |
|-------|-----------|----------|
| **Locked** | 0% | Not yet introduced |
| **Lesson** | 0% | First encounter, learning |
| **Apprentice 1-4** | 10-40% | Frequent reviews, volatile |
| **Guru 1-2** | 50-70% | Less frequent, stabilizing |
| **Master** | 80% | Infrequent reviews |
| **Enlightened** | 90% | Very infrequent |
| **Burned** | 100% | Mastered, retired from SRS |

**Mastery Progression Rules:**
- **Correct Answer** → Advance one stage (e.g., Apprentice 2 → Apprentice 3)
- **Wrong Answer (Again)** → Drop 2 stages (e.g., Guru 1 → Apprentice 3)
- **Wrong Answer (Hard)** → Drop 1 stage
- **Burned items** → Can be "resurrected" if user wants to re-study

**Topic Mastery Aggregation:**
```
Topic Mastery % = (Sum of all kanji mastery %) / (Total kanji in topic)

Example: Shopping Topic (40 kanji)
- 10 kanji at Burned (100%) = 1000
- 15 kanji at Master (80%) = 1200
- 10 kanji at Guru (60%) = 600
- 5 kanji at Apprentice (25%) = 125
Total = 2925 / 4000 = 73% Topic Mastery
```

**Visual Representation:**
- **Kanji Card Badge** - Current stage icon/color
- **Topic Progress Ring** - Circular progress indicator
- **JLPT Mastery Bar** - Aggregate of all kanji at that level
- **Mastery History Graph** - Track progression over time
- **"At Risk" Indicator** - Kanji dropping in mastery

**Decay Prevention:**
- Items in Enlightened/Burned don't decay automatically
- But if reviewed and failed, they drop stages
- Optional "refresh" mode to re-test Burned items periodically

### 🔴 Progress Visualization
**Priority:** CRITICAL | **Effort:** Medium | **Version:** v0.4

Tangible evidence of improvement fuels motivation. Users need to SEE their progress.

**Features:**
- **XP System** - Points for cards studied, bonuses for perfect sessions
- **Level System** - XP thresholds unlock levels (1-60 like WaniKani)
- **JLPT Progress Bars** - Visual % completion of N5, N4, N3, N2, N1
- **Topic Mastery Dashboard** - Per-topic mastery rings with drill-down
- **Mastery State Distribution** - Pie/bar chart of cards by stage
- **Study Heatmap** - GitHub-style calendar showing study activity
- **Mastery Trend Line** - Are you gaining or losing ground?

---

## Tier 2: Enhanced Learning Experience (v0.5 - v0.7)
*Features that significantly improve learning quality*

### 🟠 Mnemonic System
**Priority:** HIGH | **Effort:** Very High | **Version:** v0.5

WaniKani's signature feature. Story-based mnemonics significantly improve kanji retention.

**Implementation:**
- Pre-written mnemonics for all N5-N4 kanji (169 current kanji)
- Radical breakdown: 明 = 日 (sun) + 月 (moon) = bright
- Visual stories connecting meaning to form
- Future: User-submitted mnemonics, AI-generated personalized stories

**Example:**
```
休 (rest) - A person (人) leaning against a tree (木) to rest.
Think of a tired hiker finding a tree for shade.
```

### 🟠 Radical & Component System
**Priority:** HIGH | **Effort:** High | **Version:** v0.5

Understanding kanji components unlocks pattern recognition for new kanji.

**Features:**
- Teach 50+ core radicals first
- Show radical breakdown on every kanji card
- "Kanji containing this radical" cross-references
- Radical meanings and mnemonics

### 🟠 Quiz & Active Recall Modes
**Priority:** HIGH | **Effort:** Medium | **Version:** v0.6

Active recall through testing strengthens memory more than passive review.

**Quiz Types:**
- **Meaning → Kanji** (show English, pick kanji from 4 options)
- **Kanji → Reading** (show kanji, pick reading from 4 options)
- **Kanji → Meaning** (show kanji, pick meaning from 4 options)
- **Audio → Kanji** (hear reading, pick kanji)
- **Timed Challenge** - Speed rounds with XP bonus

### 🟠 Similar Kanji Comparison
**Priority:** MEDIUM | **Effort:** Medium | **Version:** v0.6

Explicit contrast learning reduces confusion between lookalike kanji.

**Features:**
- Auto-detect confusable pairs (末/未/失, 待/持/特)
- Side-by-side comparison with differences highlighted
- "Watch out for" warnings on card back
- Quiz mode specifically for confusable pairs

---

## Tier 3: Audio & Pronunciation (v0.6 - v0.8)
*Quality audio is essential for proper pronunciation*

### 🟡 Pre-recorded Audio Library
**Priority:** MEDIUM | **Effort:** High (sourcing) | **Version:** v0.6

Native speaker audio far superior to TTS for pronunciation learning.

**Approach:**
- Source from open projects (Forvo, Tatoeba) or commission
- Top 500 kanji and their vocabulary first
- Multiple voice options (male/female) ideal
- Fallback to Web Speech API for uncovered items

### 🟡 Audio Playback Enhancements
**Priority:** MEDIUM | **Effort:** Low | **Version:** v0.6

**Features:**
- Auto-play pronunciation on card flip (toggleable)
- Speed controls (0.5x, 1x, 1.5x)
- Repeat button for drilling
- Play example sentence audio

---

## Tier 4: Content Expansion (v0.7 - v1.0)
*Broader and deeper content*

### 🟡 Vocabulary Mode (Beyond Kanji)
**Priority:** MEDIUM | **Effort:** High | **Version:** v0.7

Extend study system to vocabulary, not just kanji.

**Features:**
- Vocabulary cards with readings, meanings, examples
- Hiragana/katakana-only words included
- Compound words using known kanji
- Same SRS, streaks, XP system

### 🟡 Grammar Points Integration
**Priority:** MEDIUM | **Effort:** Very High | **Version:** v0.8

Bunpro-style grammar study mode.

**Features:**
- SRS for grammar patterns
- Fill-in-the-blank exercises
- Example sentences with grammar highlighted
- Progressive difficulty (N5 → N1)

### 🟡 Reading Practice
**Priority:** MEDIUM | **Effort:** High | **Version:** v0.8

Comprehensible input at i+1 level for reading development.

**Features:**
- Short passages using learned kanji/vocabulary
- Hover for word definitions
- Comprehension questions
- Graded readers by JLPT level

### 🟡 Additional Topics
**Priority:** MEDIUM | **Effort:** Very High | **Version:** v0.9-v1.0

Expand content library:
- Weather & Nature
- Work & Business
- Health & Body
- Hobbies & Sports
- Technology & Internet

---

## Tier 5: Social & Engagement (v1.0+)
*Features that add stickiness through social mechanics*

### 🟢 Achievements & Badges
**Priority:** LOW | **Effort:** Medium | **Version:** v1.0

Research shows badges boost completion rates by 30%.

**Achievement Categories:**
- **Streak Milestones** - 7, 30, 100, 365 days
- **Volume Milestones** - 100, 500, 1000 cards mastered
- **JLPT Milestones** - Complete N5, N4, etc.
- **Perfect Sessions** - 10, 50, 100 perfect reviews
- **Speed Demon** - Complete session under X minutes

### 🟢 Daily Challenges
**Priority:** LOW | **Effort:** Medium | **Version:** v1.0

Variety and bonus XP drive engagement.

**Examples:**
- "Study 10 food-related kanji"
- "Perfect score on 5 reviews in a row"
- "Study for 15 minutes total today"
- Bonus XP for challenge completion

### 🟢 Leaderboards (Optional)
**Priority:** LOW | **Effort:** High | **Version:** v1.0+

If user accounts are implemented, leaderboards drive competitive engagement.

**Types:**
- Weekly XP rankings
- Streak hall of fame
- JLPT level progress race

---

## Tier 6: Platform & Infrastructure (v1.0+)
*Features requiring significant infrastructure*

### 🔵 User Accounts & Sync
**Priority:** LOW (unless scaling) | **Effort:** Very High | **Version:** v1.0+

Required for multi-device sync and social features.

**Options:**
- Firebase Auth + Firestore (serverless)
- Supabase (open source alternative)
- Custom backend (most control)

### 🔵 Progressive Web App (PWA)
**Priority:** MEDIUM | **Effort:** Medium | **Version:** v0.8

App-like experience without app store submission.

**Features:**
- Installable on mobile home screen
- Offline functionality via service worker
- Push notifications for reminders

### 🔵 Export/Import Data
**Priority:** MEDIUM | **Effort:** Low | **Version:** v0.5

Interim solution before user accounts.

**Features:**
- Export localStorage as JSON
- Import to restore progress
- Anki deck export format

---

## Tier 7: Accessibility & Polish (Ongoing)
*Quality-of-life improvements*

### 🔵 Dark Mode
**Priority:** LOW | **Effort:** Low | **Version:** v0.5

- Light/dark theme toggle
- Respect system preference
- Store in localStorage

### 🔵 Keyboard Shortcuts
**Priority:** LOW | **Effort:** Low | **Version:** v0.5

Power user efficiency:
- `Space` - Flip card
- `1/2/3/4` - Again/Hard/Good/Easy
- `←/→` - Previous/Next
- `Escape` - End session

### 🔵 Screen Reader Support
**Priority:** MEDIUM | **Effort:** Medium | **Version:** v0.6

Accessibility for visually impaired learners:
- ARIA labels on all interactive elements
- Logical focus order
- Audio alternatives for visual content

### 🔵 Font Size & Display Options
**Priority:** LOW | **Effort:** Low | **Version:** v0.5

- Adjustable font size
- Show/hide furigana by default
- Show/hide romaji by default

---

## AI Integration Opportunities (Future)
*Emerging technology to monitor*

### 🔮 AI-Powered Features
**Note:** These require backend/API integration

- **"Explain My Answer"** - LLM explains why answer was wrong (Duolingo Max feature)
- **AI Conversation Practice** - Chat with AI tutor in Japanese
- **Personalized Mnemonics** - AI generates stories based on user interests
- **Adaptive Difficulty** - AI adjusts content to individual learning curves
- **Writing Feedback** - AI corrects Japanese writing attempts

---

## Research Sources

- [Spaced Repetition - Wikipedia](https://en.wikipedia.org/wiki/Spaced_repetition)
- [Enhancing human learning via spaced repetition optimization - PNAS](https://www.pnas.org/doi/10.1073/pnas.1815156116)
- [Duolingo Case Study 2025: How Gamification Made Learning Addictive](https://www.youngurbanproject.com/duolingo-case-study/)
- [How Duolingo Used Psychology to Make Learning Addictive](https://www.psychologs.com/how-duolingo-used-psychology-to-make-learning-addictive/)
- [Best Japanese Learning Apps: Real Comparison for 2025 & 2026](https://migaku.com/blog/japanese/best-japanese-learning-apps-comparison)
- [The Ultimate Guide to the Best Japanese Learning Apps in 2026](https://jlptsamurai.com/2025/12/25/the-ultimate-guide-to-the-best-japanese-learning-apps-in-2026-ranked-and-reviewed/)
- [Critical review of L2 teaching research in Japan 2019-2023 - Cambridge](https://www.cambridge.org/core/journals/language-teaching/article/critical-review-of-l2-teaching-and-learning-research-in-japan-20192023/C5B410EAC57A0874B8E5D1602B908723)
- [Beyond comprehensible input: neuro-ecological critique - Frontiers 2025](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1636777/full)

---

## Notes

- Features organized by research-backed priority tiers
- Version numbers are targets, not commitments
- Dependencies between features noted where applicable
- Revisit priorities as user feedback emerges
- Focus on Tier 1-2 before expanding to Tier 3+

---

**Next Review:** After v0.3 completion
