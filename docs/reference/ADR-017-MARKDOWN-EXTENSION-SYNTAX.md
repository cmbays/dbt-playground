# ADR-017: Markdown Extension Syntax for Interactive Elements

## Status

**Accepted**

## Context

Standard markdown cannot express interactive elements like tooltips, expandable sections, quizzes, or embedded widgets. The Learning Playground needs a syntax extension to embed rich interactive components within markdown content.

### Requirements

1. **Readable in raw form** - Documents should still make sense when viewed as plain text
2. **No conflict with standard markdown** - Must not break existing parsers
3. **Support complex parameters** - Widgets need configuration (type, options, content)
4. **Parseable with reasonable effort** - Should not require complex grammar
5. **Familiar to developers** - Use patterns developers already know
6. **Graceful degradation** - Unknown widgets should not break rendering

### Options Considered

1. **HTML comments** - `<!-- widget: {...} -->`
2. **Fenced code blocks** - ` ```widget:type ... ``` `
3. **Directive syntax** - `:::widget{type="diagram"}`
4. **Custom tags** - `<Widget type="diagram">...</Widget>`
5. **Frontmatter per block** - `---widget--- ... ---`

## Decision

Use **fenced code blocks with custom language identifiers** for block widgets, plus **HTML comments for inline annotations**.

### Syntax Specification

#### Block Widgets

Use fenced code blocks with `widget:TYPE` as the language identifier:

````markdown
```widget:diagram
type: mermaid
interactive: true
content: |
  graph LR
    A[Source] --> B[Transform]
    B --> C[Output]
```
````

The content inside the fence is parsed as YAML configuration.

#### Inline Annotations

Use HTML comments with a specific pattern:

```markdown
This concept<!--tooltip: "A brief explanation"--> needs clarification.
```

The comment is processed and replaced with interactive element.

#### Complete Example

````markdown
---
tags: [dbt, modeling]
title: Layer Architecture
---

# Three-Layer Architecture

The dbt project uses a Bronze-Silver-Gold<!--tooltip: "Also called medallion architecture"--> pattern.

---

## Data Flow

```widget:diagram
type: mermaid
interactive: true
clickable: true
content: |
  graph LR
    A[stg_] --> B[int_]
    B --> C[fct_/dim_]
```

Click any node to learn more.

---

## Key Concepts

```widget:expandable
title: "What is staging?"
expanded: false
content: |
  Staging models are 1:1 with source tables.
  They handle:
  - Column renaming
  - Type casting
  - Basic filtering
```

---

## Knowledge Check

```widget:quiz
question: "Which layer contains business logic?"
options:
  - "Bronze (staging)"
  - "Silver (intermediate)"
  - "Gold (marts)"
correct: 1
feedback: |
  Silver/intermediate layer is where business
  transformations happen.
```
````

## Rationale

### Comparison Matrix

| Criterion | HTML Comments | Fenced Code | Directives | Custom Tags |
|-----------|---------------|-------------|------------|-------------|
| Raw readability | Good | Excellent | Poor | Fair |
| Markdown compat | Excellent | Excellent | Limited | Poor |
| Complex params | Limited | YAML/JSON | YAML | Attributes |
| Parse complexity | Medium | Low | Medium | High |
| Tool familiarity | High | High | Low | Medium |
| Syntax highlighting | None | Possible | None | None |
| Copy-paste friendly | Yes | Yes | No | No |

### Why Fenced Code Blocks

1. **Standard Markdown Feature**

   Every markdown parser understands fenced code blocks. The language identifier (`widget:type`) is typically ignored by parsers that do not recognize it, making this backward-compatible.

2. **YAML Configuration**

   YAML is familiar, readable, and supports complex structures:

   ```yaml
   type: quiz
   question: "What is 2+2?"
   options:
     - "3"
     - "4"
     - "5"
   correct: 1
   ```

3. **Syntax Highlighting in Editors**

   IDEs can potentially provide syntax highlighting for the YAML content inside the fence.

4. **Clear Visual Boundary**

   The triple backticks clearly delineate where the widget starts and ends.

5. **Copy-Paste Friendly**

   Can copy widget definitions between documents without breaking.

### Why HTML Comments for Inline

1. **Invisible in Standard Rendering**

   HTML comments are hidden when markdown is rendered normally, so documents still read well.

2. **No Markdown Interference**

   Comments cannot accidentally trigger markdown formatting.

3. **Simple Pattern**

   `<!--key: "value"-->` is easy to parse with regex.

### Why Not Directive Syntax (:::)

The `:::` directive syntax (used by some markdown extensions) has issues:

```markdown
:::widget{type="diagram"}
content here
:::
```

- Not standard markdown
- Many parsers do not recognize it
- Looks foreign to most developers
- Attribute syntax varies between implementations

### Why Not Custom Tags

```markdown
<Widget type="diagram">
  <Config>type: mermaid</Config>
  <Content>graph LR A-->B</Content>
</Widget>
```

- HTML tags in markdown are often stripped
- Verbose syntax
- Parsing is complex (nested tags)
- Raw readability suffers

## Consequences

### Positive

- **Backward compatible**: Standard markdown parsers show raw widget config as code block (graceful degradation)
- **Familiar syntax**: Developers know fenced blocks and YAML
- **Clean documents**: Raw markdown remains readable
- **Easy parsing**: Regex for block extraction, YAML library for config
- **Flexible**: Can extend with new widget types without syntax changes

### Negative

- **Two syntaxes**: Block (fenced) vs inline (comments) are different patterns
- **YAML parsing required**: Need a YAML parser (js-yaml via CDN)
- **No IDE preview**: Standard markdown previewers show raw config

### Mitigation

1. **Two Syntaxes**
   - Inline annotations are optional enhancement
   - Block widgets cover 90% of use cases
   - Document both patterns clearly

2. **YAML Parsing**
   - Use js-yaml from CDN (~10KB)
   - Implement simple parser as fallback for basic configs

3. **IDE Preview**
   - Consider VS Code extension in future
   - Accept that raw preview shows config (still informative)

## Implementation Notes

### Widget Block Extraction

```javascript
const WIDGET_PATTERN = /```widget:(\w+)\n([\s\S]*?)```/g;

function extractWidgets(markdown) {
  const widgets = [];
  let index = 0;

  const processed = markdown.replace(WIDGET_PATTERN, (match, type, config) => {
    const id = `widget-${index++}`;
    widgets.push({
      id,
      type,
      config: parseYAML(config)
    });
    return `<div class="widget-placeholder" data-widget-id="${id}"></div>`;
  });

  return { processed, widgets };
}
```

### Inline Annotation Extraction

```javascript
const TOOLTIP_PATTERN = /<!--tooltip:\s*"([^"]+)"-->/g;

function processTooltips(markdown) {
  return markdown.replace(TOOLTIP_PATTERN, (match, text) => {
    const escaped = escapeHtml(text);
    return `<span class="lp-tooltip" data-tooltip="${escaped}"></span>`;
  });
}
```

### YAML Parsing

```javascript
// Using js-yaml from CDN
async function loadYAMLParser() {
  if (window.jsyaml) return window.jsyaml;

  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js';
    script.onload = () => resolve(window.jsyaml);
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

async function parseYAML(content) {
  const yaml = await loadYAMLParser();
  return yaml.load(content);
}
```

### Supported Widget Types

| Type | Purpose | Required Config | Optional Config |
|------|---------|-----------------|-----------------|
| `diagram` | Mermaid/D2 diagrams | `content` | `type`, `interactive`, `clickable` |
| `quiz` | Knowledge checks | `question`, `options` | `correct`, `feedback`, `shuffle` |
| `code` | Syntax-highlighted code | `content` | `language`, `highlight`, `showLineNumbers` |
| `expandable` | Collapsible sections | `title`, `content` | `expanded` |
| `terminal` | Command examples | `commands` | `animation`, `speed` |
| `mock-ui` | Embedded UI components | `component` | `data`, `editable` |
| `comparison` | Before/after | `before`, `after` | `mode` (slider/toggle) |

### Validation

```javascript
const REQUIRED_CONFIG = {
  diagram: ['content'],
  quiz: ['question', 'options'],
  code: ['content'],
  expandable: ['title', 'content'],
  terminal: ['commands'],
  'mock-ui': ['component'],
  comparison: ['before', 'after']
};

function validateWidget(type, config) {
  const required = REQUIRED_CONFIG[type] || [];
  const missing = required.filter(key => !(key in config));

  if (missing.length > 0) {
    console.warn(`Widget ${type} missing required config: ${missing.join(', ')}`);
    return false;
  }
  return true;
}
```

## Examples

### Diagram Widget

````markdown
```widget:diagram
type: mermaid
interactive: true
content: |
  graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```
````

### Quiz Widget

````markdown
```widget:quiz
question: "What prefix do staging models use?"
options:
  - "int_"
  - "stg_"
  - "fct_"
  - "dim_"
correct: 1
feedback: |
  Staging models use the stg_ prefix.
  They are 1:1 with source tables.
shuffle: true
```
````

### Code Widget with Highlighting

````markdown
```widget:code
language: sql
highlight: [3, 4]
showLineNumbers: true
content: |
  select
      customer_id,
      customer_name,  -- highlighted
      created_at      -- highlighted
  from {{ ref('stg_customers') }}
```
````

### Expandable Widget

````markdown
```widget:expandable
title: "Advanced: SCD Type 2 Details"
expanded: false
content: |
  Type 2 slowly changing dimensions track history
  by adding new rows with effective dates.

  | Column | Purpose |
  |--------|---------|
  | valid_from | Row start date |
  | valid_to | Row end date |
  | is_current | Active flag |
```
````

### Terminal Widget

````markdown
```widget:terminal
animation: true
speed: 50
commands:
  - "dbt run --select stg_customers"
  - "dbt test --select stg_customers"
  - "dbt docs generate"
```
````

## Related

- **TDD**: [TDD-031-LEARNING-PLAYGROUND.md](../specs/TDD-031-LEARNING-PLAYGROUND.md)
- **ADR-16**: [Rendering Framework Selection](ADR-016-RENDERING-FRAMEWORK.md)
- **ADR-18**: [Widget Component System](ADR-018-WIDGET-COMPONENT-SYSTEM.md)
- **js-yaml**: https://github.com/nodeca/js-yaml
- **CommonMark Spec**: https://spec.commonmark.org/

## Approval

- **Decision Level**: Medium (cross-cutting content format)
- **Approver**: Architect
- **Date**: 2026-02-04
