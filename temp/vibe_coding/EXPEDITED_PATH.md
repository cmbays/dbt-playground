# Expedited Path for Trivial Bugs

**Version**: 1.0
**Status**: Active
**Created**: 2026-02-04
**Related**: WAVE3-002 (GitHub #224)

---

## Purpose

This document defines an expedited 3-step debugging path for trivial bugs that do not warrant the full 7-step Debug Agent protocol. The goal is to reduce friction on quick fixes while maintaining protocol rigor for complex issues.

**Philosophy**: Not every bug needs a 7-step investigation. Simple problems deserve simple solutions.

---

## Section 1: Trivial Bug Criteria

A bug qualifies for the expedited path if it meets ALL of the following:

### Mandatory Criteria

| Criterion | Verification |
|-----------|--------------|
| **Single-file scope** | Change touches only ONE file |
| **Obvious cause** | Root cause identifiable in <2 minutes |
| **No side effects** | Fix cannot break other systems |
| **No data migration** | No schema/database changes required |
| **No API changes** | Public interfaces remain unchanged |

### Qualifying Bug Categories

The following bug types typically qualify for expedited handling:

#### 1. Off-by-One Errors

```javascript
// BUG: Loop ends one iteration early
for (let i = 0; i < items.length - 1; i++)  // Wrong
for (let i = 0; i < items.length; i++)      // Fixed
```

#### 2. Typos in Strings/Messages

```python
# BUG: Misspelled word in user-facing message
print("Sucessfully saved")   # Wrong
print("Successfully saved")  # Fixed
```

#### 3. Missing Newlines/Formatting

```sql
-- BUG: Missing newline before FROM
select column1, column2from table  -- Wrong
select column1, column2
from table                         -- Fixed
```

#### 4. Simple Config Mismatches

```yaml
# BUG: Wrong environment value
environment: producton   # Wrong (typo)
environment: production  # Fixed
```

#### 5. Obvious Null/Undefined Handling

```javascript
// BUG: Missing null check on optional property
const name = user.profile.name;           // Crashes if profile is null
const name = user.profile?.name ?? '';    // Fixed
```

#### 6. Import/Require Path Errors

```python
# BUG: Wrong import path
from utils.hlpers import sanitize   # Wrong (typo in path)
from utils.helpers import sanitize  # Fixed
```

#### 7. Hardcoded Magic Numbers/Strings

```javascript
// BUG: Hardcoded timeout should use constant
setTimeout(callback, 5000);           // Hardcoded
setTimeout(callback, TIMEOUT_MS);     // Fixed (uses constant)
```

#### 8. Incorrect Boolean Logic

```python
# BUG: Wrong boolean operator
if user.is_admin and user.is_active:   # Wrong logic
if user.is_admin or user.is_active:    # Fixed (or was intended)
```

#### 9. Missing Return Statement

```javascript
// BUG: Function doesn't return the value
function double(x) {
    x * 2;        // Wrong (missing return)
}
function double(x) {
    return x * 2; // Fixed
}
```

#### 10. Incorrect Variable Reference

```python
# BUG: Using wrong variable name
total = price * quanity   # Wrong (typo: quanity vs quantity)
total = price * quantity  # Fixed
```

---

## Section 2: 3-Step Expedited Protocol

When a bug meets the trivial criteria, use this streamlined process:

### Step 1: IDENTIFY (2 minutes max)

**Actions**:
1. Verify bug against criteria checklist (Section 1)
2. Confirm single-file scope
3. Identify exact line(s) to change
4. Classify as trivial (document why)

**Output**: One-line classification statement

```markdown
TRIVIAL: [filename]:[line] - [category] - [brief description]
```

**Example**:
```markdown
TRIVIAL: utils/helpers.py:42 - typo - "recieve" should be "receive"
```

**Abort condition**: If verification takes >2 minutes or reveals complexity, STOP and use full 7-step protocol.

### Step 2: FIX (5 minutes max)

**Actions**:
1. Make the single change
2. Apply ONLY the fix (no refactoring)
3. No additional "improvements"

**Rules**:
- **Single responsibility**: Fix ONE thing only
- **No scope creep**: If you see other issues, note them separately
- **No refactoring**: Working code is sacred
- **Exact change**: Change only what's broken

**Anti-patterns** (require full protocol instead):
- "While I'm here, let me also..."
- "This would be cleaner if I..."
- "I noticed this other issue..."

### Step 3: VERIFY (3 minutes max)

**Actions**:
1. Quick manual test of the fix
2. Confirm the bug no longer occurs
3. Log the fix using the expedited format

**Verification options** (choose one):
- Run the specific failing case
- Execute targeted test
- Manual browser/console check
- Quick syntax validation

**What you DON'T need**:
- Full regression test suite
- Integration testing
- Performance benchmarks
- Code review

---

## Section 3: Disqualifiers

The following scenarios REQUIRE the full 7-step Debug Agent protocol. Do NOT use the expedited path.

### Automatic Disqualifiers

#### 1. Multi-File Changes
If the fix requires modifying more than one file, it's not trivial.

```markdown
# DISQUALIFIED: Multi-file scope
Files involved:
- src/api/handlers.py
- src/models/user.py
- tests/test_user.py
```

#### 2. Database Migration Required
Any change to schema, data, or database state requires full protocol.

```markdown
# DISQUALIFIED: Schema change
Requires: ALTER TABLE users ADD COLUMN last_login TIMESTAMP
```

#### 3. API Contract Changes
Changes to public interfaces, function signatures, or response formats need full analysis.

```markdown
# DISQUALIFIED: API change
Before: GET /users returns { users: [] }
After:  GET /users returns { data: { users: [] } }
```

#### 4. Upstream/Downstream Dependencies
If other systems depend on the affected code, blast radius analysis is required.

```markdown
# DISQUALIFIED: Downstream dependencies
This function is called by:
- PaymentProcessor.validate()
- OrderService.checkout()
- ReportGenerator.summarize()
```

#### 5. New Dependencies Required
If fixing the bug requires adding a new package or library, use full protocol.

```markdown
# DISQUALIFIED: New dependency
Requires: npm install lodash
```

#### 6. Security-Sensitive Code
Authentication, authorization, encryption, or data validation changes need review.

```markdown
# DISQUALIFIED: Security scope
Affects: User authentication flow
```

#### 7. Uncertain Root Cause
If you're not 100% sure what's causing the bug, you need the full investigation.

```markdown
# DISQUALIFIED: Uncertain cause
Symptom: Intermittent timeout
Possible causes: Network, database, memory
```

#### 8. Affects Multiple Environments
If the bug behaves differently in dev/staging/production, full investigation needed.

```markdown
# DISQUALIFIED: Environment-specific
Bug appears in production only
```

### Disqualifier Decision Flow

```text
Is it a single file?
├── No → FULL PROTOCOL
└── Yes → Does it require database changes?
    ├── Yes → FULL PROTOCOL
    └── No → Does it change API contracts?
        ├── Yes → FULL PROTOCOL
        └── No → Are there downstream dependencies?
            ├── Yes → FULL PROTOCOL
            └── No → Do you know the exact root cause?
                ├── No → FULL PROTOCOL
                └── Yes → Is it security-related?
                    ├── Yes → FULL PROTOCOL
                    └── No → EXPEDITED PATH OK ✓
```

---

## Section 4: Logging Format

### Expedited Fix Log Entry

Use this single-line format for expedited fixes:

```text
EXPEDITED: [YYYY-MM-DD] [filename]:[line] - [category] - [description] - verified
```

### Field Definitions

| Field | Description | Example |
|-------|-------------|---------|
| Date | ISO date of fix | 2026-02-04 |
| Filename | Relative path to file | src/utils.py |
| Line | Line number(s) changed | 42 or 42-44 |
| Category | Bug category from Section 1 | typo, off-by-one |
| Description | One-line description | "recieve" to "receive" |
| Status | Always "verified" | verified |

### Examples

```text
EXPEDITED: 2026-02-04 models/user.py:127 - null-check - added optional chaining for profile.name - verified
EXPEDITED: 2026-02-04 config/settings.yaml:15 - typo - "producton" to "production" - verified
EXPEDITED: 2026-02-04 utils/math.js:42 - off-by-one - loop index < length not <= length - verified
EXPEDITED: 2026-02-04 templates/email.html:89 - formatting - added missing closing </div> tag - verified
```

### Where to Log

Log expedited fixes in ONE of these locations (project-specific):

| Project Type | Log Location |
|--------------|--------------|
| Vibe Code projects | `progress.txt` (append to end) |
| dbt-playground | `memory/[date].md` (Quick Fixes section) |
| General | `LESSONS.md` (if pattern emerges from 2+ similar fixes) |

### Batch Logging

For multiple expedited fixes in one session, batch them:

```markdown
## Expedited Fixes - 2026-02-04

EXPEDITED: 2026-02-04 src/api.py:45 - typo - "responsee" to "response" - verified
EXPEDITED: 2026-02-04 src/api.py:89 - null-check - added None guard for user.email - verified
EXPEDITED: 2026-02-04 tests/test_api.py:12 - import - fixed relative import path - verified

Total: 3 expedited fixes, ~10 minutes
```

---

## Quick Reference Card

### Qualification Checklist (30 seconds)

- [ ] Single file only?
- [ ] No database changes?
- [ ] No API changes?
- [ ] No downstream dependencies?
- [ ] Root cause is obvious?
- [ ] Not security-related?

**All checked? → EXPEDITED PATH**
**Any unchecked? → FULL 7-STEP PROTOCOL**

### Time Limits

| Step | Max Time | Abort If Exceeded |
|------|----------|-------------------|
| IDENTIFY | 2 min | Switch to full protocol |
| FIX | 5 min | Switch to full protocol |
| VERIFY | 3 min | Switch to full protocol |
| **Total** | **10 min** | **Must complete in 10 minutes** |

### Log Format Template

```text
EXPEDITED: [YYYY-MM-DD] [file]:[line] - [category] - [description] - verified
```

---

## When in Doubt

**Default to the full 7-step protocol.**

The expedited path exists for clear-cut cases. If you're questioning whether a bug qualifies, it probably doesn't.

**Ask yourself**: "If this fix breaks something else, will I regret not doing the full investigation?"

- If yes → Full protocol
- If no → Expedited path

---

## Related Documentation

- **Full 7-Step Protocol**: `temp/vibe_coding/x_post_backend.txt`
- **LESSONS.md Pattern Extraction**: `docs/reference/LEARNINGS.md`
- **Wave 3 Task Queue**: `temp/vibe_coding/WAVE3_TASK_QUEUE.md`

---

*This document is part of the Wave 3 Backend Leveling initiative.*
*Created as WAVE3-002 to reduce friction on simple fixes.*
