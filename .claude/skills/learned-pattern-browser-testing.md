# Learned Pattern: Browser Testing Workflow

**Purpose**: Systematic browser testing workflow for JavaScript modules, with emphasis on debugging initialization and cross-module issues.

**Owner**: Tester persona

**Extracted from**: Phase 1 JLPT Mastery Engine browser testing (5 bugs found and fixed)

**Proven in**: v0.3 Phase 1 implementation

---

## When to Use

**Trigger conditions**:

- After implementing JavaScript modules for browser use
- When functionality works in tests but breaks in browser
- Debugging "silent failures" (page loads but features don't work)
- Verifying module loading order and dependencies

**Proactive use**:

- Part of VERIFY phase for any JavaScript changes
- After any localStorage-related changes
- Before deployment of new modules

---

## Prerequisites

**Required**:

- Access to browser DevTools (F12 or Cmd+Opt+I)
- Local development server running (`python -m http.server 8000`)
- Understanding of module dependency order

**Recommended**:

- Multiple browsers installed (Chrome, Firefox, Safari)
- Mobile device or responsive design mode

---

## Process

### Step 1: Console Startup Check

**Purpose**: Identify errors that occur during page load

**Actions**:

1. Open browser DevTools (F12)
2. Go to Console tab
3. Check "Preserve log" option
4. Clear console
5. Reload the page (Cmd+Shift+R for hard refresh)

**What to look for**:

- Red error messages
- Yellow warning messages
- Failed network requests
- "undefined" errors during initialization

**Common findings**:

```
// Module not found
Uncaught ReferenceError: ModuleName is not defined

// Property access on undefined
Uncaught TypeError: Cannot read properties of undefined (reading 'method')

// Script loading error
GET http://localhost:8000/js/missing-file.js net::ERR_ABORTED 404
```

**Output**: List of console errors to investigate

---

### Step 2: Module Export Verification

**Purpose**: Verify all modules are properly exported to window scope

**Actions**:

1. In console, type each module name: `window.ModuleName`
2. Verify it returns an object (not `undefined`)
3. Check specific functions exist: `window.ModuleName.methodName`

**Checklist for Phase 1 modules**:

```javascript
// Type each of these in console:
window.SRSEngine              // Should return object
window.KanjiStorage           // Should return object
window.MasteryCalculator      // Should return object
window.SessionManager         // Should return object
window.homeLifeKanji          // Should return array
```

**If undefined**: Check that the source file has explicit `window.ModuleName = ModuleName`

**Output**: Confirmation that all modules are accessible

---

### Step 3: Data Flow Verification

**Purpose**: Verify data is flowing correctly between modules

**Actions**:

1. Call functions that fetch/process data
2. Log the actual return values
3. Compare property names between producer and consumer

**Example verification sequence**:

```javascript
// Step 1: Check raw data
console.log('Kanji data:', window.homeLifeKanji);
console.log('Count:', window.homeLifeKanji?.length);

// Step 2: Check storage
const schema = KanjiStorage.loadSchema();
console.log('Schema:', schema);

// Step 3: Check session manager output
const status = SessionManager.getQueueStatus();
console.log('Queue status:', status);
// IMPORTANT: Check actual property names!
// Is it status.dueCount or status.due_count?

// Step 4: Check mastery calculations
const mastery = MasteryCalculator.calculateOverallMastery(schema);
console.log('Mastery:', mastery);
```

**Property name mismatch detection**:

```javascript
// If you expect camelCase but see snake_case:
console.log(Object.keys(status));
// Output: ['due_count', 'new_available'] - NOT camelCase!
```

**Output**: Verified data flow with correct property names

---

### Step 4: Initialization Flow Tracing

**Purpose**: Understand the order of operations during page load

**Actions**:

1. Add strategic `console.log` statements to initialization code
2. Reload page and observe console output
3. Verify expected sequence of operations

**Standard logging pattern**:

```javascript
function initializeDashboard() {
  console.log('1. Dashboard init starting...');

  console.log('2. Loading schema...');
  const schema = loadOrCreateSchema();
  console.log('3. Schema loaded:', schema);

  console.log('4. Updating stats...');
  updateDashboardStats(schema);
  console.log('5. Stats updated');

  console.log('6. Dashboard init complete');
}
```

**Expected console output**:

```
1. Dashboard init starting...
2. Loading schema...
3. Schema loaded: {version: '1.0.0', kanji: {}, ...}
4. Updating stats...
5. Stats updated
6. Dashboard init complete
```

**If sequence breaks**: The last logged step indicates where failure occurred

**Output**: Verified initialization sequence

---

### Step 5: Edge Case Testing

**Purpose**: Verify handling of common edge cases

**Test cases to run manually**:

1. **First-time user (no localStorage)**:

   ```javascript
   localStorage.clear();
   location.reload();
   // Should: Create default schema, show 0 progress
   ```

2. **Corrupted localStorage**:

   ```javascript
   localStorage.setItem('jlpt-mastery-schema', 'not valid json');
   location.reload();
   // Should: Handle gracefully, create new schema
   ```

3. **Empty data**:

   ```javascript
   // Test with no kanji loaded
   window.homeLifeKanji = [];
   // Should: Show "no lessons available", not crash
   ```

4. **Zero values**:

   ```javascript
   // Verify zero doesn't trigger fallback
   const result = someFunction(); // Where 0 is valid
   console.log('Result:', result, 'Type:', typeof result);
   ```

**Output**: Edge cases handled correctly

---

### Step 6: Cross-Browser Verification

**Purpose**: Ensure consistency across browsers

**Minimum browser matrix**:

| Browser | Priority | Notes |
|---------|----------|-------|
| Chrome | Primary | DevTools are excellent |
| Firefox | Secondary | Different JS engine |
| Safari | If on Mac | Mobile Safari differs |

**Per-browser checklist**:

- [ ] Console errors on load
- [ ] All modules accessible
- [ ] UI renders correctly
- [ ] Interactions work
- [ ] localStorage persists

**Common browser differences**:

- Safari: Stricter CSP, private mode blocks localStorage
- Firefox: Different date handling in some cases
- Chrome: Most permissive, may hide issues

**Output**: Verified cross-browser compatibility

---

## Common Browser Testing Bugs

### Bug 1: Silent Module Load Failure

**Symptom**: Page loads, no errors, but nothing works
**Cause**: `const ModuleName = {}` doesn't create `window.ModuleName`
**Fix**: Add `window.ModuleName = ModuleName`

### Bug 2: Property Name Mismatch

**Symptom**: Values show as `undefined`, `NaN`, or `0`
**Cause**: camelCase vs snake_case mismatch between modules
**Fix**: Console.log the actual object, match property names

### Bug 3: Falsy Zero in Defaults

**Symptom**: Zero values get replaced with fallback
**Cause**: Using `||` instead of `??`
**Fix**: Use nullish coalescing for intentional zero values

### Bug 4: Test Expectation Wrong

**Symptom**: Test fails but implementation is correct
**Cause**: Mental model doesn't match actual indexing
**Fix**: Trace through implementation manually, verify expectation

### Bug 5: Initialization Error Swallowed

**Symptom**: Page loads but broken, no console errors
**Cause**: No try-catch, error happens during initialization
**Fix**: Add try-catch with console.error logging

---

## Quick Debug Checklist

When functionality breaks in browser:

1. [ ] Open DevTools Console - any red errors?
2. [ ] Check `window.ModuleName` - undefined?
3. [ ] Console.log the data object - correct property names?
4. [ ] Add console.log to initialization - where does it stop?
5. [ ] Check `typeof value` - is `0` being treated as falsy?
6. [ ] Try in another browser - browser-specific?
7. [ ] Clear localStorage and reload - first-time user flow?

---

## See Also

- `.claude/skills/learned-pattern-javascript-defensive-coding.md` - Defensive coding patterns
- `docs/reference/LEARNINGS.md#javascript-defensive-coding-patterns` - Technical patterns reference
- `docs/standards/TESTING.md#bug-learnings` - Bug documentation
- `.claude/rules/testing.md` - Testing requirements
