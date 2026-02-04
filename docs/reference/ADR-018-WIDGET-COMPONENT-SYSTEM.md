# ADR-018: Widget Component System Architecture

## Status

**Accepted**

## Context

The Interactive Learning Playground must support multiple widget types (diagrams, quizzes, mock UIs, code blocks, etc.) with the ability to easily add new widget types without modifying core code. This requires a component architecture that provides:

1. **Declarative registration** - Add widgets without touching core code
2. **Isolated rendering** - Widgets do not interfere with each other
3. **Lifecycle management** - Clean up resources when widgets are destroyed
4. **State persistence** - Remember widget state across slide navigation
5. **Lazy loading** - Load heavy widgets (mermaid) only when needed
6. **Graceful degradation** - Unknown widgets show fallback, not errors

### Options Considered

1. **Registry pattern** - Central map of type -> handler
2. **Web Components** - Native custom elements
3. **Class inheritance** - Base widget class with overrides
4. **Functional components** - Pure render functions
5. **Hybrid** - Registry + Web Component fallback

## Decision

Implement a **registry-based widget system** with a defined handler interface. Web Components can be used for individual widgets but are not required.

## Rationale

### Comparison Matrix

| Criterion | Registry | Web Components | Inheritance | Functional |
|-----------|----------|----------------|-------------|------------|
| Simplicity | High | Medium | Medium | High |
| Encapsulation | Good | Excellent | Good | Poor |
| Browser support | All | Modern only | All | All |
| Learning curve | Low | Medium | Medium | Low |
| Lifecycle hooks | Manual | Built-in | Manual | None |
| State management | Manual | Manual | Manual | External |
| Testing | Easy | Medium | Easy | Easy |

### Why Registry Pattern

1. **Simplicity**

   A Map of type names to handler objects is the simplest possible design:

   ```javascript
   const WidgetRegistry = {
     widgets: new Map(),

     register(type, handler) {
       this.widgets.set(type, handler);
     },

     get(type) {
       return this.widgets.get(type);
     }
   };
   ```

2. **No Build Step**

   Unlike Web Components with decorators or class-based inheritance with transpilation, plain objects work in all browsers immediately.

3. **Easy Testing**

   Handlers are simple objects that can be tested in isolation:

   ```javascript
   // Test a widget handler directly
   const container = document.createElement('div');
   await DiagramWidget.render({ type: 'mermaid', content: 'graph LR A-->B' }, container);
   assert(container.querySelector('svg'));
   ```

4. **Flexible Handler Interface**

   Handlers can be objects, classes, or factory functions:

   ```javascript
   // Object handler
   WidgetRegistry.register('simple', {
     render(config, container) { /* ... */ }
   });

   // Class handler
   WidgetRegistry.register('complex', new ComplexWidget());

   // Factory handler
   WidgetRegistry.register('dynamic', createWidget('dynamic'));
   ```

5. **Graceful Degradation**

   Unknown widget types get a consistent fallback without throwing errors.

### Why Not Pure Web Components

Web Components have benefits but introduce friction:

- **Safari caveats**: Some lifecycle differences
- **Verbose boilerplate**: Custom element registration ceremony
- **Learning curve**: Shadow DOM, slots, templates
- **Overkill**: We do not need true encapsulation for this use case

However, individual widgets CAN use Web Components internally if beneficial.

### Why Not Class Inheritance

```javascript
class Widget {
  render() { throw new Error('Abstract'); }
}

class DiagramWidget extends Widget {
  render() { /* ... */ }
}
```

- Requires class syntax (minor friction)
- Encourages deep hierarchies
- Less flexible than composition

## Consequences

### Positive

- **Easy to add widgets**: Just call `WidgetRegistry.register(type, handler)`
- **Independent development**: Widgets can be built/tested in isolation
- **No framework lock-in**: Plain JavaScript objects
- **Graceful failures**: Unknown types show fallback instead of errors
- **Lazy loading ready**: Handlers can be async, loading on first use

### Negative

- **Manual lifecycle**: Must remember to call destroy() when needed
- **No built-in encapsulation**: CSS can leak between widgets
- **Convention over enforcement**: Handler interface is not enforced by TypeScript

### Mitigation

1. **Manual Lifecycle**
   - Provide clear destroy() hook documentation
   - Clean up in slidechanged event listener
   - Use WeakMap for widget-to-container associations

2. **CSS Encapsulation**
   - Prefix all widget CSS with `.lp-widget-{type}`
   - Document BEM-style naming convention
   - Consider CSS containment for isolation

3. **Interface Enforcement**
   - Document required vs optional methods clearly
   - Provide TypeScript types (JSDoc comments)
   - Create widget test harness that validates interface

## Implementation

### Core Registry

```javascript
/**
 * Widget Registry - Central registration point for all widget types
 */
const WidgetRegistry = {
  /** @type {Map<string, WidgetHandler>} */
  widgets: new Map(),

  /** @type {Map<string, object>} */
  widgetStates: new Map(),

  /**
   * Register a widget handler
   * @param {string} type - Widget type identifier
   * @param {WidgetHandler} handler - Handler object
   */
  register(type, handler) {
    if (this.widgets.has(type)) {
      console.warn(`Widget type "${type}" already registered, overwriting`);
    }
    this.widgets.set(type, handler);
  },

  /**
   * Render a widget into a container
   * @param {string} type - Widget type
   * @param {object} config - Widget configuration
   * @param {HTMLElement} container - DOM container
   * @returns {Promise<void>}
   */
  async render(type, config, container) {
    const handler = this.widgets.get(type);

    if (!handler) {
      console.warn(`Unknown widget type: ${type}`);
      return this.renderFallback(type, config, container);
    }

    try {
      // Restore state if exists
      const widgetId = container.dataset.widgetId;
      const savedState = this.widgetStates.get(widgetId);
      if (savedState && handler.setState) {
        handler.setState(container, savedState);
      }

      await handler.render(config, container);
      container.dataset.rendered = 'true';
    } catch (error) {
      console.error(`Widget render error (${type}):`, error);
      this.renderError(type, error, container);
    }
  },

  /**
   * Destroy a widget and clean up resources
   * @param {string} type - Widget type
   * @param {HTMLElement} container - DOM container
   */
  destroy(type, container) {
    const handler = this.widgets.get(type);

    // Save state before destroying
    if (handler?.getState) {
      const widgetId = container.dataset.widgetId;
      const state = handler.getState(container);
      if (state) {
        this.widgetStates.set(widgetId, state);
      }
    }

    if (handler?.destroy) {
      handler.destroy(container);
    }

    container.innerHTML = '';
    container.dataset.rendered = 'false';
  },

  /**
   * Render fallback for unknown widget types
   */
  renderFallback(type, config, container) {
    container.innerHTML = `
      <div class="lp-widget lp-widget-fallback">
        <div class="lp-widget-fallback-header">
          Unknown widget: ${escapeHtml(type)}
        </div>
        <pre class="lp-widget-fallback-config">${escapeHtml(JSON.stringify(config, null, 2))}</pre>
      </div>
    `;
  },

  /**
   * Render error state
   */
  renderError(type, error, container) {
    container.innerHTML = `
      <div class="lp-widget lp-widget-error">
        <div class="lp-widget-error-header">
          Widget error: ${escapeHtml(type)}
        </div>
        <pre class="lp-widget-error-message">${escapeHtml(error.message)}</pre>
      </div>
    `;
  },

  /**
   * Get all registered widget types
   * @returns {string[]}
   */
  getRegisteredTypes() {
    return Array.from(this.widgets.keys());
  }
};
```

### Widget Handler Interface

```typescript
/**
 * Widget Handler Interface (TypeScript definition for documentation)
 */
interface WidgetHandler {
  /** Unique widget type identifier */
  type: string;

  /**
   * Render the widget into a container
   * @param config - Parsed YAML configuration
   * @param container - DOM element to render into
   */
  render(config: object, container: HTMLElement): void | Promise<void>;

  /**
   * Clean up resources when widget is destroyed (optional)
   * Called when navigating away from slide
   */
  destroy?(container: HTMLElement): void;

  /**
   * Get serializable widget state (optional)
   * Used to restore state when returning to slide
   */
  getState?(container: HTMLElement): object | null;

  /**
   * Restore widget state (optional)
   * Called before render if state exists
   */
  setState?(container: HTMLElement, state: object): void;
}
```

### Example Widget Implementations

#### Diagram Widget

```javascript
const DiagramWidget = {
  type: 'diagram',
  mermaidLoaded: false,

  async render(config, container) {
    if (config.type === 'mermaid') {
      await this.renderMermaid(config, container);
    } else {
      container.innerHTML = `<pre>Unsupported diagram type: ${config.type}</pre>`;
    }
  },

  async renderMermaid(config, container) {
    // Lazy load mermaid
    if (!this.mermaidLoaded) {
      await this.loadMermaid();
    }

    const id = `mermaid-${Date.now()}`;
    const { svg } = await mermaid.render(id, config.content);

    container.innerHTML = `
      <div class="lp-widget lp-widget-diagram">
        <div class="lp-diagram-container">${svg}</div>
      </div>
    `;

    if (config.interactive) {
      this.attachInteractivity(container, config);
    }
  },

  async loadMermaid() {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js';
      script.onload = () => {
        mermaid.initialize({ startOnLoad: false, theme: 'neutral' });
        this.mermaidLoaded = true;
        resolve();
      };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  },

  attachInteractivity(container, config) {
    const nodes = container.querySelectorAll('.node');
    nodes.forEach(node => {
      node.style.cursor = 'pointer';
      node.addEventListener('click', () => {
        const nodeId = node.id;
        if (config.clickable) {
          this.handleNodeClick(nodeId, config);
        }
      });
      node.addEventListener('mouseenter', () => {
        node.classList.add('lp-diagram-node-hover');
      });
      node.addEventListener('mouseleave', () => {
        node.classList.remove('lp-diagram-node-hover');
      });
    });
  },

  handleNodeClick(nodeId, config) {
    // Emit custom event for parent to handle
    const event = new CustomEvent('lp-diagram-click', {
      detail: { nodeId, config }
    });
    document.dispatchEvent(event);
  },

  destroy(container) {
    // Remove event listeners
    const nodes = container.querySelectorAll('.node');
    nodes.forEach(node => {
      node.replaceWith(node.cloneNode(true));
    });
  }
};

WidgetRegistry.register('diagram', DiagramWidget);
```

#### Quiz Widget

```javascript
const QuizWidget = {
  type: 'quiz',

  render(config, container) {
    const { question, options, correct, feedback } = config;

    const optionsHtml = options.map((opt, i) => {
      const isCorrect = i === correct;
      const label = opt.replace(' (correct)', '');
      return `
        <div class="lp-quiz-option" data-index="${i}" data-correct="${isCorrect}">
          <span class="lp-quiz-option-marker">${String.fromCharCode(65 + i)}</span>
          <span class="lp-quiz-option-text">${escapeHtml(label)}</span>
        </div>
      `;
    }).join('');

    container.innerHTML = `
      <div class="lp-widget lp-widget-quiz">
        <div class="lp-quiz-question">${escapeHtml(question)}</div>
        <div class="lp-quiz-options">${optionsHtml}</div>
        <div class="lp-quiz-feedback" hidden>${escapeHtml(feedback || '')}</div>
        <button class="lp-quiz-submit" disabled>Check Answer</button>
      </div>
    `;

    this.attachListeners(container);
  },

  attachListeners(container) {
    const options = container.querySelectorAll('.lp-quiz-option');
    const submitBtn = container.querySelector('.lp-quiz-submit');
    const feedbackEl = container.querySelector('.lp-quiz-feedback');
    let selectedIndex = null;

    options.forEach(opt => {
      opt.addEventListener('click', () => {
        // Deselect all
        options.forEach(o => o.classList.remove('selected'));
        // Select clicked
        opt.classList.add('selected');
        selectedIndex = parseInt(opt.dataset.index);
        submitBtn.disabled = false;
      });
    });

    submitBtn.addEventListener('click', () => {
      if (selectedIndex === null) return;

      options.forEach(opt => {
        const isCorrect = opt.dataset.correct === 'true';
        const isSelected = parseInt(opt.dataset.index) === selectedIndex;

        if (isCorrect) {
          opt.classList.add('correct');
        } else if (isSelected) {
          opt.classList.add('incorrect');
        }
        opt.style.pointerEvents = 'none';
      });

      feedbackEl.hidden = false;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Answered';
    });
  },

  getState(container) {
    const selected = container.querySelector('.lp-quiz-option.selected');
    const answered = container.querySelector('.lp-quiz-submit').disabled &&
                     container.querySelector('.lp-quiz-submit').textContent === 'Answered';

    return {
      selectedIndex: selected ? parseInt(selected.dataset.index) : null,
      answered
    };
  },

  setState(container, state) {
    // State will be applied during render via getState check
    container.dataset.savedState = JSON.stringify(state);
  },

  destroy(container) {
    // Event listeners are on DOM elements that will be removed
    // No additional cleanup needed
  }
};

WidgetRegistry.register('quiz', QuizWidget);
```

#### Code Widget

```javascript
const CodeWidget = {
  type: 'code',

  render(config, container) {
    const { content, language = 'sql', highlight = [], showLineNumbers = true } = config;

    const lines = content.trim().split('\n');
    const numberedLines = lines.map((line, i) => {
      const lineNum = i + 1;
      const isHighlighted = highlight.includes(lineNum);
      const highlightClass = isHighlighted ? 'lp-code-line-highlight' : '';
      const lineNumHtml = showLineNumbers
        ? `<span class="lp-code-line-number">${lineNum}</span>`
        : '';

      return `
        <div class="lp-code-line ${highlightClass}">
          ${lineNumHtml}
          <span class="lp-code-line-content">${escapeHtml(line)}</span>
        </div>
      `;
    }).join('');

    container.innerHTML = `
      <div class="lp-widget lp-widget-code">
        <div class="lp-code-header">
          <span class="lp-code-language">${escapeHtml(language)}</span>
          <button class="lp-code-copy" title="Copy code">Copy</button>
        </div>
        <pre class="lp-code-content" data-language="${language}">${numberedLines}</pre>
      </div>
    `;

    this.attachListeners(container, content);
  },

  attachListeners(container, content) {
    const copyBtn = container.querySelector('.lp-code-copy');
    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(content);
        copyBtn.textContent = 'Copied!';
        setTimeout(() => {
          copyBtn.textContent = 'Copy';
        }, 2000);
      } catch (err) {
        copyBtn.textContent = 'Failed';
      }
    });
  }
};

WidgetRegistry.register('code', CodeWidget);
```

#### Expandable Widget

```javascript
const ExpandableWidget = {
  type: 'expandable',

  render(config, container) {
    const { title, content, expanded = false } = config;

    container.innerHTML = `
      <div class="lp-widget lp-widget-expandable ${expanded ? 'expanded' : ''}">
        <button class="lp-expandable-header">
          <span class="lp-expandable-icon">${expanded ? '-' : '+'}</span>
          <span class="lp-expandable-title">${escapeHtml(title)}</span>
        </button>
        <div class="lp-expandable-content" ${expanded ? '' : 'hidden'}>
          ${this.renderContent(content)}
        </div>
      </div>
    `;

    this.attachListeners(container);
  },

  renderContent(content) {
    // Simple markdown rendering for content
    return content
      .replace(/\n\n/g, '</p><p>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>');
  },

  attachListeners(container) {
    const header = container.querySelector('.lp-expandable-header');
    const content = container.querySelector('.lp-expandable-content');
    const icon = container.querySelector('.lp-expandable-icon');
    const widget = container.querySelector('.lp-widget-expandable');

    header.addEventListener('click', () => {
      const isExpanded = widget.classList.toggle('expanded');
      content.hidden = !isExpanded;
      icon.textContent = isExpanded ? '-' : '+';
    });
  },

  getState(container) {
    const widget = container.querySelector('.lp-widget-expandable');
    return { expanded: widget?.classList.contains('expanded') ?? false };
  }
};

WidgetRegistry.register('expandable', ExpandableWidget);
```

### Integration with Slide System

```javascript
// Initialize widgets when reveal.js is ready
Reveal.on('ready', event => {
  renderWidgetsInSlide(event.currentSlide);
});

// Render widgets when navigating to new slide
Reveal.on('slidechanged', event => {
  // Destroy widgets in previous slide
  if (event.previousSlide) {
    destroyWidgetsInSlide(event.previousSlide);
  }

  // Render widgets in current slide
  renderWidgetsInSlide(event.currentSlide);
});

function renderWidgetsInSlide(slide) {
  const placeholders = slide.querySelectorAll('.widget-placeholder:not([data-rendered="true"])');

  placeholders.forEach(async placeholder => {
    const widgetId = placeholder.dataset.widgetId;
    const widgetData = window.widgetData?.[widgetId];

    if (widgetData) {
      await WidgetRegistry.render(widgetData.type, widgetData.config, placeholder);
    }
  });
}

function destroyWidgetsInSlide(slide) {
  const placeholders = slide.querySelectorAll('.widget-placeholder[data-rendered="true"]');

  placeholders.forEach(placeholder => {
    const widgetId = placeholder.dataset.widgetId;
    const widgetData = window.widgetData?.[widgetId];

    if (widgetData) {
      WidgetRegistry.destroy(widgetData.type, placeholder);
    }
  });
}
```

## Testing

### Widget Test Harness

```javascript
class WidgetTestHarness {
  constructor() {
    this.results = [];
  }

  async testWidget(type, config, assertions) {
    const container = document.createElement('div');
    document.body.appendChild(container);

    try {
      await WidgetRegistry.render(type, config, container);

      for (const assertion of assertions) {
        assertion(container);
      }

      this.results.push({ type, status: 'pass' });
    } catch (error) {
      this.results.push({ type, status: 'fail', error: error.message });
    } finally {
      WidgetRegistry.destroy(type, container);
      container.remove();
    }
  }

  async runAll() {
    // Test diagram widget
    await this.testWidget('diagram', {
      type: 'mermaid',
      content: 'graph LR A-->B'
    }, [
      c => assert(c.querySelector('svg'), 'Should render SVG'),
      c => assert(c.querySelector('.lp-widget-diagram'), 'Should have widget class')
    ]);

    // Test quiz widget
    await this.testWidget('quiz', {
      question: 'Test?',
      options: ['A', 'B', 'C'],
      correct: 1
    }, [
      c => assert(c.querySelectorAll('.lp-quiz-option').length === 3, 'Should render 3 options'),
      c => assert(c.querySelector('.lp-quiz-submit'), 'Should have submit button')
    ]);

    // Test unknown widget fallback
    await this.testWidget('unknown-type', {
      foo: 'bar'
    }, [
      c => assert(c.querySelector('.lp-widget-fallback'), 'Should render fallback')
    ]);

    return this.results;
  }
}
```

## Related

- **TDD**: [TDD-031-LEARNING-PLAYGROUND.md](../specs/TDD-031-LEARNING-PLAYGROUND.md)
- **ADR-16**: [Rendering Framework Selection](ADR-016-RENDERING-FRAMEWORK.md)
- **ADR-17**: [Markdown Extension Syntax](ADR-017-MARKDOWN-EXTENSION-SYNTAX.md)
- **Web Components**: https://developer.mozilla.org/en-US/docs/Web/Web_Components

## Approval

- **Decision Level**: Medium (cross-cutting architecture pattern)
- **Approver**: Architect
- **Date**: 2026-02-04
