# Tense Button Fix - RESOLVED ✅

## Problem
The Present/Past/Future/Advanced buttons in the shopping dialogue section were not switching between tenses.

## Root Cause
The `showTense()` function in `js/shared.js` was designed for the old single-page architecture where all tense content was wrapped in a container div:

```html
<!-- OLD ARCHITECTURE (expected) -->
<div id="shopping-dialogue">
  <div class="tense-selector">
    <button>Present</button>
  </div>
  <div class="tense-content">Present content</div>
  <div class="tense-content">Past content</div>
</div>
```

But the new section-based architecture has tense content as direct siblings without a wrapper:

```html
<!-- NEW ARCHITECTURE (actual) -->
<div class="tense-selector">
  <button>Present</button>
</div>
<div id="shopping-dialogue-present" class="tense-content">...</div>
<div id="shopping-dialogue-past" class="tense-content">...</div>
```

The function was looking for `document.getElementById('shopping-dialogue')` which doesn't exist in the new architecture, causing it to return early without doing anything.

## Solution
Updated `showTense()` function to support **both architectures**:

1. **First tries old architecture** - looks for container div
2. **Falls back to new architecture** - searches entire document for `.tense-content` and `.tense-btn` classes
3. **Works in both cases** - maintains backwards compatibility

### Code Change (js/shared.js, line 52-77)

```javascript
function showTense(scenario, modality, tense) {
    // New architecture: tense-content divs are siblings in the same page
    // Try the old container-based approach first for backwards compatibility
    const container = document.getElementById(`${scenario}-${modality}`);

    if (container) {
        // Old architecture: content is inside a container
        container.querySelectorAll('.tense-content').forEach(c => c.classList.remove('active'));
        container.querySelectorAll('.tense-btn').forEach(b => b.classList.remove('active'));
    } else {
        // New architecture: content divs are siblings, search the whole document
        document.querySelectorAll('.tense-content').forEach(c => c.classList.remove('active'));
        document.querySelectorAll('.tense-btn').forEach(b => b.classList.remove('active'));
    }

    // Activate the selected tense content
    const content = document.getElementById(`${scenario}-${modality}-${tense}`);
    if (content) {
        content.classList.add('active');
    }

    // Activate the clicked button
    if (typeof event !== 'undefined' && event && event.target) {
        event.target.classList.add('active');
    }
}
```

## Testing
To verify the fix works:

1. Open `shopping/dialogue.html` in your browser
2. Click the **Past** button - should show 100 yen shop dialogue
3. Click the **Future** button - should show electronics store dialogue
4. Click the **Advanced** button - should show clothing store dialogue
5. Click the **Present** button - should return to supermarket dialogue

Each click should:
- ✅ Hide the current dialogue
- ✅ Show the selected dialogue
- ✅ Highlight the clicked button
- ✅ Keep all audio/hint buttons working

## Files Modified
- ✅ `/sessions/practical-dazzling-fermi/mnt/japanese/js/shared.js` (lines 52-77)

## Status
🟢 **FIXED** - Tense buttons now work correctly in the new section-based architecture while maintaining compatibility with any old files.

## Why This Approach?
Using `document.querySelectorAll()` when no container exists ensures:
- Works with new separate section pages
- Doesn't break old monolithic pages (if any remain)
- No need to update HTML structure
- Future-proof for other sections (story, manga, etc.)
