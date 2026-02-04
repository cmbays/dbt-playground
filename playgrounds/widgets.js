/**
 * Learning Playground - Slide Widgets Module
 * Provides slide content and interactive widgets for each topic
 */

window.Widgets = {
  /**
   * Get slides for a specific topic
   * @param {string} topicId - The topic ID
   * @returns {Object} Object with {title, subtitle, slides: []}
   */
  getSlidesForTopic: (topicId) => {
    const slides = {
      intro: {
        title: 'Welcome to dbt',
        subtitle: 'A framework for analytics engineering',
        slides: [
          {
            title: 'What is dbt?',
            subtitle: 'data build tool',
            content: `
              <h3>dbt helps analytics engineers transform data in the warehouse</h3>
              <ul class="slide-list">
                <li><strong>SQL</strong> for transformation logic</li>
                <li><strong>Version control</strong> for all analytics code</li>
                <li><strong>Testing</strong> for data quality</li>
                <li><strong>Documentation</strong> that stays in sync</li>
                <li><strong>Deployment</strong> workflows for production</li>
              </ul>
            `
          },
          {
            title: 'The dbt Philosophy',
            subtitle: 'Treat data like software',
            content: `
              <h3>Key principles:</h3>
              <ul class="slide-list">
                <li>Data transformations are code</li>
                <li>Code should be tested, documented, and version controlled</li>
                <li>Analytics should move from notebooks to production SQL</li>
                <li>Data quality is everyone's responsibility</li>
                <li>Modern data teams deserve great developer tooling</li>
              </ul>
            `
          },
          {
            title: 'How dbt Fits In',
            subtitle: 'The dbt stack',
            content: `
              <h3>Data flow:</h3>
              <pre class="data-flow">
Raw Data Source
    ↓
dbt (Transformation)
    ├─ Staging (clean, standardize)
    ├─ Intermediate (business logic)
    └─ Marts (final analytics layer)
    ↓
Analytics/BI Layer
              </pre>
            `
          }
        ]
      },

      philosophy: {
        title: 'The Analytics Engineering Philosophy',
        subtitle: 'Bridging analytics and software engineering',
        slides: [
          {
            title: 'Analytics Engineering',
            subtitle: 'What is it?',
            content: `
              <h3>Analytics engineering is the blend of:</h3>
              <ul class="slide-list">
                <li><strong>Data Analysis</strong> - Understanding business questions</li>
                <li><strong>Software Engineering</strong> - Building reliable systems</li>
                <li><strong>Data Engineering</strong> - Managing data infrastructure</li>
              </ul>
              <p>Analytics engineers build the transformation layer that makes raw data useful for decision-making.</p>
            `
          },
          {
            title: 'Key Principles',
            subtitle: 'The foundation',
            content: `
              <h3>Core tenets:</h3>
              <ol class="slide-list">
                <li>Write modular, reusable code</li>
                <li>Version control everything</li>
                <li>Test your transformations</li>
                <li>Document your logic</li>
                <li>Deploy to production safely</li>
              </ol>
            `
          }
        ]
      },

      setup: {
        title: 'Setting Up Your dbt Project',
        subtitle: 'From zero to first model',
        slides: [
          {
            title: 'Installation',
            subtitle: 'Getting started',
            content: `
              <h3>Quick start:</h3>
              <pre class="code-block">
# Using pip
pip install dbt-core dbt-postgres

# Or use a database adapter
pip install dbt-duckdb
              </pre>
            `
          },
          {
            title: 'Project Structure',
            subtitle: 'Organizing your code',
            content: `
              <h3>Key directories:</h3>
              <pre class="code-block">
dbt-project/
  ├── models/           # SQL transformation files
  ├── tests/            # dbt tests
  ├── data/             # CSV seed data
  ├── macros/           # reusable logic
  ├── analyses/         # exploratory queries
  └── dbt_project.yml   # project config
              </pre>
            `
          }
        ]
      },

      models: {
        title: 'dbt Models Fundamentals',
        subtitle: 'The core building block',
        slides: [
          {
            title: 'What is a Model?',
            subtitle: 'The basics',
            content: `
              <h3>A dbt model is:</h3>
              <ul class="slide-list">
                <li>A <strong>.sql file</strong> with a SELECT statement</li>
                <li>Transforms source data and produces a table or view</li>
                <li>Defines dependencies using <code>ref()</code> and <code>source()</code></li>
                <li>Documented in YAML</li>
              </ul>
            `
          },
          {
            title: 'Model Materialization',
            subtitle: 'How models are built',
            content: `
              <h3>Four materialization types:</h3>
              <ul class="slide-list">
                <li><strong>View</strong> - Query executed every time (default)</li>
                <li><strong>Table</strong> - Built once, persists (use for large datasets)</li>
                <li><strong>Incremental</strong> - Only build new/changed rows</li>
                <li><strong>Ephemeral</strong> - Compiled inline (no object in DB)</li>
              </ul>
            `
          },
          {
            title: 'Writing Your First Model',
            subtitle: 'Step by step',
            content: `
              <h3>models/stg_customers.sql</h3>
              <pre class="code-block">
select
    id as customer_id,
    name as customer_name,
    email,
    created_at
from {{ source('raw', 'customers') }}
              </pre>
              <p>✓ Uses <code>source()</code> to reference raw data</p>
              <p>✓ Renames columns for clarity</p>
              <p>✓ Ready to be tested and documented</p>
            `
          }
        ]
      },

      naming: {
        title: 'Naming Conventions',
        subtitle: 'Make your code readable',
        slides: [
          {
            title: 'Model Prefixes',
            subtitle: 'Organize by layer',
            content: `
              <h3>Layer naming convention:</h3>
              <ul class="slide-list">
                <li><code>stg_</code> - <strong>Staging</strong>: 1:1 with source, minimal transformations</li>
                <li><code>int_</code> - <strong>Intermediate</strong>: Business logic, joins, aggregations</li>
                <li><code>fct_</code> - <strong>Facts</strong>: Events, measures, transactions</li>
                <li><code>dim_</code> - <strong>Dimensions</strong>: Attributes, descriptive data</li>
              </ul>
            `
          },
          {
            title: 'Column Naming',
            subtitle: 'Clarity in every field',
            content: `
              <h3>Best practices:</h3>
              <ul class="slide-list">
                <li>Use <strong>snake_case</strong> (not camelCase)</li>
                <li>Use <strong>descriptive names</strong> (customer_id, not c_id)</li>
                <li>Add <strong>_id suffix</strong> for foreign keys</li>
                <li>Use <strong>_at suffix</strong> for timestamps</li>
                <li>Use <strong>_flag suffix</strong> for booleans</li>
              </ul>
            `
          }
        ]
      },

      testing: {
        title: 'Testing Data Quality',
        subtitle: 'Ensure reliable transformations',
        slides: [
          {
            title: 'Why Test?',
            subtitle: 'Data quality is critical',
            content: `
              <h3>Tests catch problems early:</h3>
              <ul class="slide-list">
                <li>Duplicate or missing data</li>
                <li>Unexpected NULL values</li>
                <li>Invalid relationships</li>
                <li>Out-of-range values</li>
                <li>Breaking changes in source data</li>
              </ul>
            `
          },
          {
            title: 'Generic Tests',
            subtitle: 'Quick quality checks',
            content: `
              <h3>Built-in tests:</h3>
              <pre class="code-block">
models:
  - name: stg_customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
      - name: email
        tests:
          - unique
      - name: status
        tests:
          - accepted_values:
              values: ['active', 'inactive']
              </pre>
            `
          },
          {
            title: 'Singular Tests',
            subtitle: 'Complex validation logic',
            content: `
              <h3>tests/no_duplicate_emails.sql</h3>
              <pre class="code-block">
select email
from {{ ref('stg_customers') }}
group by 1
having count(*) > 1
              </pre>
              <p>This test passes if it returns 0 rows.</p>
            `
          }
        ]
      },

      documentation: {
        title: 'Documenting Your Models',
        subtitle: 'Knowledge that stays in sync',
        slides: [
          {
            title: 'Why Document?',
            subtitle: 'Future you will thank you',
            content: `
              <h3>Good documentation:</h3>
              <ul class="slide-list">
                <li>Explains <strong>business logic</strong> (not just SQL syntax)</li>
                <li>Lives <strong>next to your code</strong> (in YAML)</li>
                <li>Gets <strong>auto-generated</strong> into a shared site</li>
                <li>Is <strong>always up-to-date</strong> (enforced by version control)</li>
              </ul>
            `
          },
          {
            title: 'Model Documentation',
            subtitle: 'Document structure',
            content: `
              <h3>models/schema.yml</h3>
              <pre class="code-block">
models:
  - name: customers
    description: >
      Customer dimension table.
      One row per customer.
    columns:
      - name: customer_id
        description: Primary key
        tests:
          - unique
          - not_null
      - name: name
        description: Customer full name
              </pre>
            `
          }
        ]
      },

      incremental: {
        title: 'Incremental Models',
        subtitle: 'Scale your pipelines',
        slides: [
          {
            title: 'When to Use Incremental',
            subtitle: 'Optimize for performance',
            content: `
              <h3>Use incremental when:</h3>
              <ul class="slide-list">
                <li>Table has billions of rows</li>
                <li>Only new/recent data changes</li>
                <li>Full refresh would be slow</li>
              </ul>
              <h3>Example:</h3>
              <p>Events table - add today's events, don't rebuild entire history</p>
            `
          },
          {
            title: 'Incremental Syntax',
            subtitle: 'How to build them',
            content: `
              <h3>models/events.sql</h3>
              <pre class="code-block">
{{
  config(
    materialized='incremental'
  )
}}

select
    event_id,
    event_at
from {{ source('raw', 'events') }}

{% if execute and execute %}
  where event_at > (select max(event_at) from {{ this }})
{% endif %}
              </pre>
            `
          }
        ]
      },

      deployment: {
        title: 'Deploying to Production',
        subtitle: 'From development to live',
        slides: [
          {
            title: 'Environments',
            subtitle: 'Dev vs. Production',
            content: `
              <h3>Typical setup:</h3>
              <ul class="slide-list">
                <li><strong>Dev Schema</strong> - Your laptop, for experimentation</li>
                <li><strong>Staging Schema</strong> - Testing environment, CI runs here</li>
                <li><strong>Prod Schema</strong> - Live data, production queries</li>
              </ul>
            `
          },
          {
            title: 'Deployment Workflow',
            subtitle: 'Safe rollouts',
            content: `
              <h3>Standard process:</h3>
              <ol class="slide-list">
                <li>Open a PR with changes</li>
                <li>Run tests in CI (staging environment)</li>
                <li>Get code reviewed by team</li>
                <li>Merge to main</li>
                <li>Deploy job runs on main (production)</li>
              </ol>
            `
          }
        ]
      }
    };

    return slides[topicId] || {
      title: 'Coming Soon',
      subtitle: `Topic: ${topicId}`,
      slides: [
        {
          title: 'Under Development',
          subtitle: 'Check back soon',
          content: `<p>This topic content is being prepared.</p>`
        }
      ]
    };
  }
};
