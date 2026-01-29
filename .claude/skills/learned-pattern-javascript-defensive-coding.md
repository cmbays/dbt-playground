# Learned Pattern: JavaScript Defensive Coding

**Purpose**: Checklist and patterns to prevent common JavaScript bugs, especially in multi-module codebases.

**Owner**: Developer persona

**Extracted from**: Phase 1 JLPT Mastery Engine browser testing (5 bugs fixed)

**Proven in**: v0.3 Phase 1 implementation

---

## When to Use

**Trigger conditions**:

- Writing JavaScript that handles default values
- Creating interfaces between modules
- Building sorting/comparison logic
- Writing or debugging tests

**Proactive use**:

- Code review checklist item
- Pre-commit verification
- Post-bug-fix pattern reinforcement

---

## Pattern 1: Nullish Coalescing for Zero-Valid Defaults

### The Problem

`||` operator treats `0`, `""`, and `false` as falsy, triggering unexpected fallbacks.

### Detection Checklist

- [ ] Does this code use `||` for default values?
- [ ] Could the left-hand value legitimately be `0`, `""`, or `false`?
- [ ] Is the fallback triggering when it shouldn't?

### The Fix

```javascript
// BEFORE (BUG): Zero triggers fallback
const value = lookup[key] || defaultValue;

// AFTER (FIX): Only null/undefined trigger fallback
const value = lookup[key] ?? defaultValue;
```

### Quick Decision Guide

| Use `||` when... | Use `??` when... |
|------------------|------------------|
| Any falsy value should use default | Only missing values should use default |
| `0`, `""`, `false` are "empty" | `0`, `""`, `false` are valid values |
| Example: `userName || 'Guest'` | Example: `sortOrder ?? 0` |

### Real Example (from Phase 1)

```javascript
// JLPT levels: N5=0, N4=1, N3=2, N2=3, N1=4
const jlptOrder = { 'N5': 0, 'N4': 1, 'N3': 2, 'N2': 3, 'N1': 4 };

// BUG: N5 (value 0) was treated as falsy, sorted last
items.sort((a, b) => (jlptOrder[a.level] || 5) - (jlptOrder[b.level] || 5));

// FIX: Nullish coalescing preserves intentional 0
items.sort((a, b) => (jlptOrder[a.level] ?? 5) - (jlptOrder[b.level] ?? 5));
```

---

## Pattern 2: Property Naming Consistency

### The Problem

Module A expects `camelCase`, Module B returns `snake_case` - silent `undefined` values.

### Detection Checklist

- [ ] Are values showing as `0`, `undefined`, or `NaN` unexpectedly?
- [ ] Did you console.log the actual object to see property names?
- [ ] Do producer and consumer modules use the same naming convention?

### The Fix

```javascript
// Step 1: Console.log to see actual structure
const status = SessionManager.getQueueStatus();
console.log('Actual status object:', status);
// Output: { due_count: 5, new_available: 10 }  <-- snake_case!

// Step 2: Use correct property names
updateDisplay(status.due_count);       // Not status.dueCount
updateDisplay(status.new_available);   // Not status.newAvailable
```

### Prevention Strategies

1. **Document interfaces with JSDoc**:

   ```javascript
   /**
    * @returns {{due_count: number, new_available: number}} Queue status
    */
   function getQueueStatus() { ... }
   ```

2. **Establish project convention**:
   - Internal JS: camelCase
   - Data/JSON: snake_case
   - Document in CLAUDE.md or coding-style.md

3. **Type checking** (if available):

   ```typescript
   interface QueueStatus {
     due_count: number;
     new_available: number;
   }
   ```

### Real Example (from Phase 1)

```javascript
// session-manager.js returns:
{ due_count: 5, new_available: 10 }

// dashboard.js expected (BUG):
status.dueCount     // undefined
status.newAvailable // undefined

// Fixed dashboard.js to match API:
status.due_count     // 5
status.new_available // 10
```

---

## Pattern 3: Test Expectations Verification

### The Problem

Test expects wrong value based on incorrect mental model of implementation.

### Detection Checklist

- [ ] Does the test fail? Did you verify the expectation is correct?
- [ ] Can you trace through the implementation to calculate expected value?
- [ ] Did you check the indexing/math in the implementation?

### The Fix

```javascript
// Step 1: Trace through implementation manually
// STAGES = ['apprentice_1', 'apprentice_2', 'apprentice_3', 'apprentice_4', 'guru_1', ...]
// guru_1 is index 4
// AGAIN drops 2 stages: 4 - 2 = 2
// Index 2 = 'apprentice_3'

// Step 2: Update test expectation to match
expect(result.stage).toBe('apprentice_3');  // Not 'apprentice_4'

// Step 3: Add comment explaining the calculation
// guru_1 (index 4) - 2 stages = apprentice_3 (index 2)
```

### Prevention Strategies

1. **Calculate expected values by hand** before writing assertions
2. **Use implementation constants** in tests when possible:

   ```javascript
   const expectedStage = STAGES[STAGES.indexOf('guru_1') - 2];
   expect(result.stage).toBe(expectedStage);
   ```

3. **Add comments** explaining non-obvious expected values
4. **Test the test** - verify it fails for the right reasons

---

## Pattern 4: Browser Module Exports

### The Problem

Using `const` at file scope does NOT create `window` properties. Other modules cannot access the exported object.

### Detection Checklist

- [ ] Does this script define objects/functions for other modules to use?
- [ ] Can you access `window.ModuleName` in browser console after loading?
- [ ] Are consuming modules getting `undefined` when accessing exports?

### The Fix

```javascript
// BEFORE (BUG): const doesn't create window property
const homeLifeKanji = [
  { character: '家', jlpt_level: 'N4' },
  // ...
];
// window.homeLifeKanji is undefined!

// AFTER (FIX): Explicit window export
const homeLifeKanji = [
  { character: '家', jlpt_level: 'N4' },
  // ...
];
window.homeLifeKanji = homeLifeKanji;  // Now accessible globally
```

### Module Export Pattern

For complex modules, use the revealing module pattern with explicit export:

```javascript
const MyModule = (function() {
  // Private variables
  const privateData = [];

  // Private functions
  function privateHelper() { }

  // Public interface
  return {
    publicMethod: function() { },
    publicData: getData
  };
})();

// CRITICAL: Explicit export for browser access
window.MyModule = MyModule;
```

### Real Example (from Phase 1)

```javascript
// kanji-metadata.js
const homeLifeKanji = [
  { character: '家', meanings: ['house', 'home'], jlpt_level: 'N4' },
  { character: '食', meanings: ['eat', 'food'], jlpt_level: 'N4' },
  // ... 167 more kanji
];

// BUG: Dashboard couldn't find kanji, showed "0 lessons available"
// window.homeLifeKanji was undefined

// FIX: Added explicit export
window.homeLifeKanji = homeLifeKanji;
// Dashboard now shows "169 lessons available"
```

---

## Pattern 5: Initialization Error Handling

### The Problem

Initialization code fails silently without try-catch, making debugging nearly impossible.

### Detection Checklist

- [ ] Does the page load with no errors but broken functionality?
- [ ] Are there any console errors on load?
- [ ] Did you add console.log statements to trace initialization flow?

### The Fix

```javascript
// BEFORE (BUG): Silent failure
function initDashboard() {
  const schema = Storage.loadSchema();  // If this throws, page breaks silently
  updateStats(schema);
}

// AFTER (FIX): Comprehensive error handling with logging
function initDashboard() {
  try {
    console.log('Initializing dashboard...');

    console.log('Loading schema...');
    let schema = Storage.loadSchema();

    if (!schema) {
      console.log('No existing schema, creating default...');
      schema = Storage.createDefaultSchema();
      Storage.saveSchema(schema);
      console.log('Created and saved new schema');
    }

    console.log('Schema loaded:', schema);
    updateStats(schema);
    console.log('Dashboard initialized successfully');

  } catch (error) {
    console.error('Dashboard initialization failed:', error);
    console.error('Error details:', {
      message: error.message,
      stack: error.stack
    });
    // Show user-friendly error OR attempt recovery
    showErrorState('Unable to load progress data');
  }
}
```

### Key Logging Points

Add `console.log` statements at these critical points:

1. **Before critical operations**: `console.log('Attempting to load schema...')`
2. **After successful operations**: `console.log('Schema loaded:', schema)`
3. **At decision points**: `console.log('No schema found, creating default')`
4. **On errors (with context)**: `console.error('Failed to load:', error)`

### Real Example (from Phase 1)

```javascript
// dashboard initialization
function loadOrCreateSchema() {
  try {
    console.log('Loading schema...');
    const schema = KanjiStorage.loadSchema();

    if (!schema) {
      console.log('No existing schema, creating default...');
      const defaultSchema = KanjiStorage.createDefaultSchema();
      KanjiStorage.saveSchema(defaultSchema);
      console.log('Created default schema:', defaultSchema);
      return defaultSchema;
    }

    console.log('Loaded existing schema:', schema);
    return schema;
  } catch (error) {
    console.error('Failed to load/create schema:', error);
    // This error message helped identify the window export bug!
    throw error;
  }
}
```

---

## Pre-Commit Checklist

Before committing JavaScript changes:

- [ ] **Default values**: Any `||` that should be `??`?
- [ ] **Property access**: Console.log complex objects to verify property names
- [ ] **Module interfaces**: Do property names match between producer and consumer?
- [ ] **Test expectations**: Are assertions based on traced-through calculations?
- [ ] **Zero handling**: Could any value legitimately be `0`?
- [ ] **Module exports**: Does each module have explicit `window.ModuleName = ModuleName`?
- [ ] **Error handling**: Is initialization wrapped in try-catch with logging?
- [ ] **Console debugging**: Can you trace the initialization flow via console.log?

---

## Integration with Code Review

When reviewing JavaScript code, check for:

1. **Operator choice**: `||` vs `??` for defaults
2. **Property naming**: Consistency between modules
3. **Test accuracy**: Expectations match implementation logic
4. **Module exports**: Explicit `window.` exports for browser modules
5. **Error handling**: Try-catch around initialization and localStorage operations

Add these to `/review` persona checklist.

---

## See Also

- `docs/reference/LEARNINGS.md#javascript-defensive-coding-patterns` - Technical patterns reference
- `.claude/rules/coding-style.md` - JavaScript naming conventions
- `.claude/rules/testing.md` - Test writing guidelines
- MDN: [Nullish coalescing operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)
