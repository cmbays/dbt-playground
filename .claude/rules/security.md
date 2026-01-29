# Security Rules

Security guidelines for the Japanese learning website.

## Threat Model

### Current Context

- Static website (no backend currently)
- Client-side JavaScript only
- localStorage for user data
- No authentication (yet)
- Public educational content

### Primary Threats

| Threat | Risk Level | Mitigation |
|--------|------------|------------|
| XSS (Cross-site Scripting) | High | Sanitize dynamic content |
| Data Tampering (localStorage) | Medium | Validate stored data |
| Resource Integrity | Medium | SRI for external scripts |
| Clickjacking | Low | X-Frame-Options |
| Information Disclosure | Low | No sensitive data in source |

## Content Security

### Dynamic Content

```javascript
// NEVER use innerHTML with untrusted data
element.innerHTML = userInput; // DANGEROUS

// SAFE alternatives
element.textContent = userInput; // For text
element.setAttribute('data-value', sanitize(input)); // For attributes
```

### Sanitization

When innerHTML is necessary:

```javascript
// Use DOMPurify or similar
const clean = DOMPurify.sanitize(dirty);
element.innerHTML = clean;

// Or build DOM programmatically
const el = document.createElement('div');
el.textContent = userInput;
parent.appendChild(el);
```

### External Links

```html
<!-- Always use noopener noreferrer -->
<a href="https://external.com" target="_blank" rel="noopener noreferrer">
  External Link
</a>
```

## Data Storage

### localStorage Security

```javascript
// Always validate data from localStorage
function getSafeData(key, defaultValue) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return defaultValue;

    const data = JSON.parse(raw);

    // Validate structure
    if (typeof data !== 'object') return defaultValue;

    // Validate expected properties
    if (!isValidData(data)) return defaultValue;

    return data;
  } catch (e) {
    console.error('Invalid stored data:', e);
    return defaultValue;
  }
}
```

### Data Validation

```javascript
// Validate before use
function isValidProgress(data) {
  return (
    data &&
    typeof data.level === 'string' &&
    ['N5', 'N4', 'N3', 'N2', 'N1'].includes(data.level) &&
    typeof data.index === 'number' &&
    data.index >= 0
  );
}
```

### Never Store

- Passwords or credentials
- API keys or tokens
- Personally identifiable information
- Session data (when auth is added)

## External Resources

### Subresource Integrity (SRI)

```html
<!-- Always use integrity attribute for external scripts -->
<script
  src="https://cdn.example.com/lib.min.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/..."
  crossorigin="anonymous">
</script>

<link
  rel="stylesheet"
  href="https://cdn.example.com/style.css"
  integrity="sha384-..."
  crossorigin="anonymous">
```

### CDN Best Practices

- Use reputable CDNs (cdnjs, unpkg, jsdelivr)
- Always include integrity hashes
- Have fallback to local copy if critical
- Version pin dependencies

## Headers (When Server Control Available)

### Recommended Headers

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.trusted.com; style-src 'self' 'unsafe-inline'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

## Input Handling

### Form Inputs

```javascript
// Always sanitize and validate
function handleInput(input) {
  // Trim whitespace
  const value = input.trim();

  // Validate length
  if (value.length > MAX_LENGTH) {
    return { error: 'Input too long' };
  }

  // Validate format if needed
  if (!VALID_PATTERN.test(value)) {
    return { error: 'Invalid format' };
  }

  // Escape for display
  return { value: escapeHtml(value) };
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
```

### URL Parameters

```javascript
// Validate URL parameters
const params = new URLSearchParams(window.location.search);
const level = params.get('level');

// Whitelist valid values
const validLevels = ['N5', 'N4', 'N3', 'N2', 'N1'];
if (!validLevels.includes(level)) {
  // Use default or show error
  level = 'N5';
}
```

## Secure Patterns

### Event Handlers

```javascript
// AVOID inline handlers with dynamic data
element.setAttribute('onclick', 'doSomething("' + userInput + '")'); // DANGEROUS

// USE addEventListener
element.addEventListener('click', () => doSomething(userInput));
```

### JSON Parsing

```javascript
// Always wrap in try/catch
try {
  const data = JSON.parse(jsonString);
  // Validate structure before use
  if (isValidData(data)) {
    processData(data);
  }
} catch (e) {
  console.error('Invalid JSON:', e);
  handleError();
}
```

### Error Messages

```javascript
// Don't expose internal details
// BAD
catch (e) {
  showError('Database error: ' + e.message);
}

// GOOD
catch (e) {
  console.error('Internal error:', e); // Log for debugging
  showError('Something went wrong. Please try again.');
}
```

## Code Review Checklist

### For Every Change

- [ ] No `eval()` or `new Function()` with user input
- [ ] innerHTML only with sanitized content
- [ ] External links have `rel="noopener noreferrer"`
- [ ] localStorage data validated before use
- [ ] No sensitive data in console.log
- [ ] No hardcoded credentials/keys
- [ ] Form inputs validated
- [ ] Error messages don't expose internals

### For External Resources

- [ ] SRI hashes included
- [ ] Loaded from reputable sources
- [ ] Version pinned
- [ ] Fallback available if critical

## Future Considerations

When authentication is added:

- Use secure session management
- Implement CSRF protection
- Use HTTPS only
- Secure cookie flags (HttpOnly, Secure, SameSite)
- Rate limiting for login attempts
- Password hashing (bcrypt)

When backend is added:

- Input validation on server
- Parameterized queries
- API authentication
- Request rate limiting
- Logging and monitoring
