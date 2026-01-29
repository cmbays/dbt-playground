# Topic Page Creation Skill

Workflow for creating new topic content pages.

## Overview

This skill manages the creation of content pages within topic folders, ensuring consistency with established patterns.

## Trigger

Invoke when:
- Creating new topic folder
- Adding content page to existing topic
- Building dialogue, phrases, quiz, etc.

## Page Types

| Type | Purpose | Key Elements |
|------|---------|--------------|
| index.html | Topic landing | Navigation, overview |
| phrases.html | Vocabulary list | Terms, translations, audio |
| dialogue.html | Conversation practice | Speakers, lines, context |
| story.html | Reading practice | Narrative, vocabulary notes |
| manga.html | Visual storytelling | Panels, speech bubbles |
| quiz.html | Knowledge testing | Questions, feedback |
| tips.html | Cultural/learning notes | Explanations, advice |

## Workflow

### Phase 1: Preparation

1. **Identify Prototype**
   - Find existing page of same type
   - Review patterns and structure
   - Note required elements

2. **Gather Content**
   - Japanese text
   - Furigana readings
   - Romanization
   - English translations
   - Audio files (if needed)

3. **Verify JLPT Level**
   - Content matches target level
   - Vocabulary appropriate
   - Grammar appropriate

### Phase 2: Create Structure

1. **Copy Prototype**
   ```bash
   cp topics/[existing-topic]/[type].html temp/[new-topic]-[type].html
   ```

2. **Update Metadata**
   - Title
   - Version comment
   - Navigation links

3. **Clear Content Sections**
   - Keep structure
   - Remove specific content
   - Preserve patterns

### Phase 3: Populate Content

1. **Add Japanese Content**
   ```html
   <div class="phrase">
     <ruby>買い物<rt>かいもの</rt></ruby>
     <span class="romaji">kaimono</span>
     <span class="english">shopping</span>
   </div>
   ```

2. **Add Audio References** (if applicable)
   ```html
   <button class="audio-btn" data-audio="audio/phrase-01.mp3">
     ▶️
   </button>
   ```

3. **Add Interactivity**
   - Toggle buttons (romaji, translations)
   - Quiz interactions
   - Navigation controls

### Phase 4: Apply Styling

1. **Use shared.css**
   - No page-specific styles unless necessary
   - Follow existing class patterns
   - Consistent spacing

2. **Responsive Design**
   - Mobile-first
   - Test breakpoints
   - Touch-friendly targets

### Phase 5: Test & Verify

1. **Content Verification**
   - Japanese accuracy (sensei check)
   - Translation accuracy
   - Audio plays correctly

2. **Functionality**
   - All interactions work
   - No console errors
   - Navigation complete

3. **Cross-browser**
   - Chrome, Firefox, Safari
   - Mobile, tablet, desktop

### Phase 6: Integrate

1. **Update Topic Index**
   ```html
   <!-- topics/[topic]/index.html -->
   <nav>
     <a href="phrases.html">Phrases</a>
     <a href="dialogue.html">Dialogue</a> <!-- New -->
   </nav>
   ```

2. **Move to Final Location**
   ```bash
   mv temp/[topic]-[type].html topics/[topic]/[type].html
   ```

3. **Update Version**
   - Add version comment to new file
   - Update CHANGELOG

## Page Templates

### Phrases Page
```html
<!-- Version: vX.Y.Z - Updated: YYYY-MM-DD -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Topic] - Phrases</title>
  <link rel="stylesheet" href="../../css/shared.css">
</head>
<body>
  <header>
    <nav class="breadcrumb">
      <a href="../../index.html">Home</a> /
      <a href="index.html">[Topic]</a> /
      Phrases
    </nav>
  </header>

  <main>
    <h1>[Topic] Phrases</h1>

    <div class="controls">
      <button id="toggle-romaji">Show Romaji</button>
      <button id="toggle-english">Show English</button>
    </div>

    <section class="phrase-list">
      <!-- Phrases here -->
    </section>
  </main>

  <script src="../../js/shared.js"></script>
</body>
</html>
```

### Dialogue Page
```html
<!-- Similar structure with dialogue-specific elements -->
<section class="dialogue">
  <div class="context">[Setting description]</div>

  <div class="line">
    <span class="speaker">Person A:</span>
    <span class="japanese">
      <ruby>こんにちは<rt></rt></ruby>
    </span>
    <span class="romaji hidden">Konnichiwa</span>
    <span class="english hidden">Hello</span>
  </div>
</section>
```

## Content Checklist

### All Pages
- [ ] Version comment at top
- [ ] Proper DOCTYPE and meta tags
- [ ] Linked to shared.css
- [ ] Linked to shared.js
- [ ] Breadcrumb navigation
- [ ] Main heading (h1)
- [ ] Responsive layout

### Japanese Content
- [ ] Furigana for all kanji
- [ ] Romanization available
- [ ] English translations
- [ ] Audio files (if applicable)
- [ ] JLPT level appropriate

### Functionality
- [ ] Toggle buttons work
- [ ] Audio plays
- [ ] Quiz feedback (if quiz)
- [ ] No console errors

### Navigation
- [ ] Links to index
- [ ] Links from index
- [ ] Breadcrumb correct
- [ ] All links work

## Integration

- **Entry**: Topic requirements defined
- **Persona**: Developer
- **Sensei**: Content validation
- **Exit**: To verification, then code review

## Exit Criteria

Page complete when:
- [ ] Follows prototype pattern
- [ ] All content populated
- [ ] Styling consistent
- [ ] Functionality tested
- [ ] Navigation connected
- [ ] Sensei approved
- [ ] Ready for deployment
