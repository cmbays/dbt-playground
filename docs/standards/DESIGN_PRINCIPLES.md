---
audience: [design, developer]
priority: medium
size: medium
dependencies: []
last_updated: 2026-01-29
status: active
tags: [standards, dbt, data-modeling, design]
---

# Design Principles & Standards

## Purpose

This document defines design standards for both **data modeling** and **exposure layer** (dashboards, visualizations, apps, narratives) in the healthcare_analytics project. These principles ensure consistency, professional quality, and engaging user experiences.

---

## Design Philosophy

**Core Values**:

1. **Clarity** - Models should be easy to read and understand
2. **Consistency** - Similar patterns used across all layers
3. **Modularity** - Small, focused models that compose well
4. **Testability** - Every model should be testable

**Data Modeling Goals**:

- Single source of truth for each entity
- Clear lineage from source to consumption
- Self-documenting code with meaningful names
- Minimal duplication of logic

---

## Naming Conventions

### Model Prefixes

| Prefix | Layer | Purpose |
|--------|-------|---------|
| `stg_` | Staging | 1:1 with source, renamed/retyped |
| `int_` | Intermediate | Business logic, joins, aggregations |
| `fct_` | Facts | Measures, events, transactions |
| `dim_` | Dimensions | Descriptive attributes, slowly changing |

### Model Naming Pattern

```
{prefix}_{source}__{entity}
```

**Examples**:

```
stg_synthea__patients      # Staging model for patients from synthea
int_encounters__enriched   # Intermediate enriched encounters
fct_clinical_events        # Fact table for clinical events
dim_patients               # Patient dimension
```

### Column Naming

```
Primary Keys:     {entity}_id           (patient_id, encounter_id)
Foreign Keys:     {entity}_id           (same as primary)
Dates:            {event}_date          (encounter_date, birth_date)
Timestamps:       {event}_timestamp     (created_at, updated_at)
Booleans:         is_{condition}        (is_active, is_deceased)
Counts:           {entity}_count        (encounter_count)
Amounts:          {measure}_amount      (claim_amount)
```

---

## Model Layer Architecture

### Staging Layer

**Purpose**: Clean, rename, and type-cast source data.

**Rules**:

- One model per source table
- No joins between sources
- Only rename and retype columns
- Add metadata columns (`_loaded_at`)

```sql
with source as (
    select * from {{ source('synthea_raw', 'patients') }}
),

renamed as (
    select
        -- Primary key
        id as patient_id,

        -- Attributes
        first as first_name,
        last as last_name,
        birthdate as birth_date,

        -- Metadata
        current_timestamp as _loaded_at
    from source
)

select * from renamed
```

### Intermediate Layer

**Purpose**: Apply business logic, join related data.

**Rules**:

- Can join multiple staging models
- Apply business calculations
- Create reusable building blocks
- Name describes transformation (e.g., `_enriched`, `_pivoted`)

### Marts Layer

**Purpose**: Final consumption layer for analytics.

**Rules**:

- Optimized for query patterns
- Denormalized where appropriate
- Include all necessary context
- Materialized as tables for performance

---

## CTE Structure

### Standard Pattern

```sql
with

source as (
    -- First CTE: source data
    select * from {{ ref('stg_synthea__patients') }}
),

filtered as (
    -- Second CTE: apply filters
    select *
    from source
    where birth_date is not null
),

calculated as (
    -- Third CTE: add calculations
    select
        *,
        date_diff('year', birth_date, current_date) as age
    from filtered
),

final as (
    -- Final CTE: select output columns
    select
        patient_id,
        first_name,
        last_name,
        birth_date,
        age
    from calculated
)

select * from final
```

### CTE Naming Guidelines

| CTE Name | Purpose |
|----------|---------|
| `source` | Raw data reference |
| `renamed` | Column renaming |
| `filtered` | Row filtering |
| `calculated` | Add derived columns |
| `joined` | After joining data |
| `aggregated` | After aggregation |
| `final` | Final output selection |

---

## Documentation Standards

### Model Documentation

Every model requires:

```yaml
version: 2

models:
  - name: stg_synthea__patients
    description: >
      Staging model for patient demographics from Synthea.
      One row per patient.

    columns:
      - name: patient_id
        description: Unique patient identifier (UUID)
        data_tests:
          - unique
          - not_null

      - name: birth_date
        description: Patient date of birth
```

### Required Documentation

- [ ] Model description (what and why)
- [ ] Primary key identified
- [ ] All columns documented
- [ ] Tests defined for critical columns

---

## Testing Standards

### Required Tests

| Column Type | Tests |
|-------------|-------|
| Primary Key | `unique`, `not_null` |
| Foreign Key | `relationships` |
| Categorical | `accepted_values` |
| Dates | `not_null`, range checks |
| Amounts | `not_null`, `>= 0` |

### Example

```yaml
columns:
  - name: patient_id
    data_tests:
      - unique
      - not_null

  - name: gender
    data_tests:
      - accepted_values:
          values: ['M', 'F', 'O']

  - name: organization_id
    data_tests:
      - relationships:
          to: ref('dim_organizations')
          field: organization_id
```

---

## SQL Style Guide

### Formatting

- Keywords in lowercase
- One column per line
- Leading commas (optional but consistent)
- 4-space indentation

```sql
select
    patient_id
    , first_name
    , last_name
    , birth_date
from {{ ref('stg_synthea__patients') }}
where birth_date >= '2000-01-01'
order by last_name, first_name
```

### Comments

```sql
-- Model: dim_patients
-- Description: Patient dimension with demographics
-- Source: stg_synthea__patients

{#
    Complex business logic explanation
    goes in Jinja comments
#}
```

---

## File Organization

### Directory Structure

```
models/
├── staging/
│   └── synthea/
│       ├── _synthea__sources.yml
│       ├── _synthea__models.yml
│       ├── stg_synthea__patients.sql
│       └── stg_synthea__encounters.sql
├── intermediate/
│   └── healthcare/
│       └── int_encounters__enriched.sql
└── marts/
    └── core/
        ├── _core__models.yml
        ├── dim_patients.sql
        └── fct_encounters.sql
```

### YAML File Naming

- `_<source>__sources.yml` - Source definitions
- `_<source>__models.yml` - Model documentation
- `_<mart>__models.yml` - Mart documentation

---

## Design Checklist

When creating new models:

- [ ] Follows naming conventions
- [ ] Uses appropriate layer (staging/intermediate/marts)
- [ ] CTE structure is clear and logical
- [ ] All columns have meaningful names
- [ ] Primary key defined and tested
- [ ] Foreign keys have relationship tests
- [ ] Model is documented in YAML
- [ ] All columns are documented
- [ ] No duplicate logic (use macros)
- [ ] Performance considered (materialization)

---

## Anti-Patterns to Avoid

### Don't Do This

```sql
-- ❌ SELECT * in final model
select * from staging

-- ❌ Hardcoded values
where status = 'active'

-- ❌ Logic in staging layer
where birth_date > '2000-01-01'

-- ❌ Joining in staging
from patients p
join encounters e on p.id = e.patient_id
```

### Do This Instead

```sql
-- ✅ Explicit columns
select patient_id, first_name, last_name from staging

-- ✅ Use variables
where status = '{{ var("active_status") }}'

-- ✅ Logic in intermediate layer
-- (staging is 1:1 with source)

-- ✅ Join in intermediate/marts
-- Keep staging models simple
```

---

## Part 2: Exposure Layer Design

## Exposure Layer Philosophy

**Core Values**:

1. **Clarity** - Visualizations should communicate insights instantly
2. **Consistency** - Same metrics look the same across all dashboards
3. **Accessibility** - Design for all users, all devices
4. **Engagement** - Create delight through thoughtful interaction

**User Experience Goals**:

- Minimize cognitive load - don't make users think
- Provide clear visual hierarchy - important insights stand out
- Give immediate feedback - users know when interactions register
- Support mobile users - responsive design is essential

---

## Visual Design System

### Color Palette

#### Primary Colors

```
Primary Blue:    #1e40af  (KPIs, primary actions)
Success Green:   #10b981  (positive trends, targets met)
Warning Amber:   #f59e0b  (attention needed)
Danger Red:      #ef4444  (negative trends, alerts)
```

#### Neutral Colors

```
Text Dark:       #1e293b  (headings, primary text)
Text Medium:     #475569  (secondary text)
Text Light:      #94a3b8  (labels, metadata)
Background:      #f8fafc  (page background)
Card White:      #ffffff  (card backgrounds)
Border:          #e2e8f0  (dividers, borders)
```

#### Healthcare-Specific

```
Patient Blue:    #3b82f6  (patient-related metrics)
Provider Teal:   #14b8a6  (provider metrics)
Encounter Purple:#8b5cf6  (encounter/visit data)
Clinical Green:  #22c55e  (clinical outcomes)
```

### Typography

```css
/* System font stack for performance */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
             'Helvetica Neue', Arial, sans-serif;

/* Sizes */
--font-kpi:      2.5rem    /* 40px - Big numbers */
--font-title:    1.5rem    /* 24px - Dashboard titles */
--font-heading:  1.125rem  /* 18px - Card headings */
--font-body:     1rem      /* 16px - Default text */
--font-small:    0.875rem  /* 14px - Labels, metadata */
--font-tiny:     0.75rem   /* 12px - Axis labels */
```

### Spacing System

```
--space-xs:  4px    (tight gaps)
--space-sm:  8px    (element padding)
--space-md:  16px   (card padding)
--space-lg:  24px   (section gaps)
--space-xl:  32px   (major sections)
--space-2xl: 48px   (page margins)
```

---

## Dashboard Layout Patterns

### Executive Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  [Logo]  Healthcare Analytics    [Date Range] [Export] │
├─────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│ │ Patients │ │Encounters│ │ Revenue  │ │ Quality  │    │
│ │  12,450  │ │   8,234  │ │  $2.1M   │ │   94%    │    │
│ │   ↑ 5%   │ │   ↓ 2%   │ │   ↑ 8%   │ │   → 0%   │    │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────┐ ┌─────────────────────────┐│
│ │     Trend Chart         │ │   Provider Breakdown    ││
│ │     ───────────         │ │   ▓▓▓▓▓▓▓▓▓▓  45%     ││
│ │    /          \         │ │   ▓▓▓▓▓▓▓▓    35%     ││
│ │   /            \        │ │   ▓▓▓▓▓▓      20%     ││
│ └─────────────────────────┘ └─────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Card Structure

```css
/* Standard dashboard card */
.dashboard-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.card-title {
  font-size: 0.875rem;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.card-value {
  font-size: 2rem;
  font-weight: 600;
  color: #1e293b;
}

.card-trend {
  font-size: 0.875rem;
  margin-top: 4px;
}

.trend-positive { color: #10b981; }
.trend-negative { color: #ef4444; }
.trend-neutral  { color: #94a3b8; }
```

---

## Chart Design Standards

### Line Charts (Trends)

- Use for time-series data
- Limit to 5 lines maximum
- Include reference lines for targets
- Show data point markers on hover only

### Bar Charts (Comparisons)

- Use for categorical comparisons
- Horizontal for long labels
- Sort by value (descending) unless logical order exists
- Include value labels for clarity

### Pie/Donut Charts (Composition)

- Use sparingly (max 5 segments)
- Always include percentages
- Order clockwise by size
- Consider alternatives (stacked bar, treemap)

### Tables (Detail)

- Right-align numbers
- Left-align text
- Include sorting
- Limit visible rows (pagination or scroll)
- Highlight rows on hover

### Chart Accessibility

- Don't rely on color alone
- Include patterns or labels
- Ensure sufficient contrast
- Provide alt text descriptions
- Support keyboard navigation

---

## Interactive Elements

### Filters

```
- Date range picker at top (global)
- Category filters in sidebar
- Reset to defaults button
- Filter state visible in URL
```

### Drill-Down

```
Dashboard → Chart → Detail Table → Individual Record

Each level should:
- Show breadcrumb trail
- Allow back navigation
- Preserve context
```

### Tooltips

```
Show on hover:
- Exact value (formatted)
- Comparison to target/previous
- Percentage of total
- Click hint for drill-down
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile first approach */
@media (min-width: 640px)  { /* sm - Tablet portrait */ }
@media (min-width: 768px)  { /* md - Tablet landscape */ }
@media (min-width: 1024px) { /* lg - Desktop */ }
@media (min-width: 1280px) { /* xl - Large desktop */ }
```

### Mobile Adaptations

- KPI cards: 2 per row → 1 per row
- Charts: Full width, reduced height
- Tables: Horizontal scroll or card view
- Filters: Collapsible drawer
- Touch targets: 44px minimum

---

## Performance Guidelines

### Target Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Initial Load | < 3s | Time to first meaningful paint |
| Filter Response | < 500ms | Time to update after filter |
| Chart Render | < 1s | Time to display visualization |
| Memory Usage | < 100MB | Browser memory footprint |

### Optimization Strategies

- Pre-aggregate data in dbt (don't calculate in browser)
- Lazy load below-fold charts
- Use pagination for large tables
- Cache frequently accessed dashboards
- Compress data payloads

---

## Narrative Design (Evidence/Reports)

### Story Structure

```markdown
1. Hook       - Key insight that grabs attention
2. Context    - Background and comparison points
3. Analysis   - Data exploration and findings
4. Conclusion - Actionable recommendations
```

### Writing Style

- Active voice ("Encounters increased" not "An increase was observed")
- Specific numbers ("23% increase" not "significant growth")
- Compare to benchmarks ("vs. target of 20%")
- Call out anomalies ("unusually high for Q3")

### Visual Narrative Flow

```
Big Number → Supporting Chart → Detail Table → Action Items
```

---

## Exposure Layer Checklist

### Dashboard

- [ ] Follows color palette
- [ ] Uses typography scale
- [ ] Consistent spacing
- [ ] KPIs above the fold
- [ ] Responsive on mobile
- [ ] Accessible (WCAG 2.1 AA)
- [ ] Load time < 3 seconds
- [ ] Filters work correctly
- [ ] Drill-down paths clear

### Individual Chart

- [ ] Clear title describes insight
- [ ] Axis labels readable
- [ ] Legend positioned well
- [ ] Tooltips informative
- [ ] Colors meaningful
- [ ] Data source cited

### Narrative/Report

- [ ] Key insight in first paragraph
- [ ] Data supports conclusions
- [ ] Visualizations enhance story
- [ ] Actionable recommendations
- [ ] Date of analysis noted

---

*Last Updated: 2026-01-29*
*Next Review: When new patterns emerge or project requirements change*
