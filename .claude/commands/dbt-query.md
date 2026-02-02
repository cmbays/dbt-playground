# dbt-query Command

Natural language to SQL query generation using the dbt Semantic Layer.

## Usage

```
/dbt-query "[natural language question]"
/dbt-query "revenue by month for 2024"
/dbt-query "top 10 customers by order count"
/dbt-query "compare Q4 revenue vs Q3"
```

## Examples

### Simple Metric Query

```
/dbt-query "total revenue last month"
```

Output:

```
Query: "total revenue last month"

Interpreted:
- Metric: revenue
- Time: last_month
- Dimensions: none

Generated SQL:
SELECT
    SUM(total_amount) as revenue
FROM fct_orders
WHERE order_status = 'completed'
  AND order_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND order_date < DATE_TRUNC('month', CURRENT_DATE)

Result:
┌──────────────┐
│ revenue      │
├──────────────┤
│ $1,234,567   │
└──────────────┘
```

### Metric with Dimensions

```
/dbt-query "revenue by product category for Q4 2024"
```

Output:

```
Query: "revenue by product category for Q4 2024"

Interpreted:
- Metric: revenue
- Time: Q4 2024 (Oct-Dec)
- Dimensions: product_category

Generated SQL:
SELECT
    product_category,
    SUM(total_amount) as revenue
FROM fct_orders
WHERE order_status = 'completed'
  AND order_date >= '2024-10-01'
  AND order_date < '2025-01-01'
GROUP BY 1
ORDER BY 2 DESC

Result:
┌───────────────────┬──────────────┐
│ product_category  │ revenue      │
├───────────────────┼──────────────┤
│ Electronics       │ $456,789     │
│ Clothing          │ $234,567     │
│ Home & Garden     │ $123,456     │
└───────────────────┴──────────────┘
```

### Comparison Query

```
/dbt-query "compare monthly revenue 2024 vs 2023"
```

Output:

```
Query: "compare monthly revenue 2024 vs 2023"

Interpreted:
- Metric: revenue
- Comparison: year_over_year
- Dimensions: month

Generated SQL:
SELECT
    DATE_TRUNC('month', order_date) as month,
    SUM(CASE WHEN YEAR(order_date) = 2024 THEN total_amount END) as revenue_2024,
    SUM(CASE WHEN YEAR(order_date) = 2023 THEN total_amount END) as revenue_2023,
    (revenue_2024 - revenue_2023) / revenue_2023 * 100 as yoy_change_pct
FROM fct_orders
WHERE order_status = 'completed'
GROUP BY 1
ORDER BY 1

Result:
┌─────────────┬──────────────┬──────────────┬────────────────┐
│ month       │ revenue_2024 │ revenue_2023 │ yoy_change_pct │
├─────────────┼──────────────┼──────────────┼────────────────┤
│ 2024-01     │ $100,000     │ $85,000      │ +17.6%         │
│ 2024-02     │ $110,000     │ $90,000      │ +22.2%         │
│ ...         │ ...          │ ...          │ ...            │
└─────────────┴──────────────┴──────────────┴────────────────┘
```

### Top N Query

```
/dbt-query "top 10 customers by total orders"
```

Output:

```
Query: "top 10 customers by total orders"

Interpreted:
- Metric: order_count
- Dimensions: customer_name
- Limit: 10
- Sort: descending

Generated SQL:
SELECT
    c.customer_name,
    COUNT(o.order_id) as order_count
FROM fct_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10

Result:
┌──────────────────────┬─────────────┐
│ customer_name        │ order_count │
├──────────────────────┼─────────────┤
│ Acme Corp            │ 1,234       │
│ Global Industries    │ 987         │
│ ...                  │ ...         │
└──────────────────────┴─────────────┘
```

## Query Patterns

### Time Filters

| Natural Language | Interpretation |
|------------------|----------------|
| "last month" | Previous calendar month |
| "this quarter" | Current quarter to date |
| "YTD" / "year to date" | Jan 1 to today |
| "Q4 2024" | Oct 1 - Dec 31, 2024 |
| "last 7 days" | Rolling 7 days |
| "2024" | Full year 2024 |

### Aggregations

| Natural Language | SQL |
|------------------|-----|
| "total" / "sum of" | SUM() |
| "average" / "avg" | AVG() |
| "count of" | COUNT() |
| "unique" / "distinct" | COUNT(DISTINCT) |
| "maximum" / "highest" | MAX() |
| "minimum" / "lowest" | MIN() |

### Comparisons

| Natural Language | Query Type |
|------------------|------------|
| "compare X vs Y" | Side-by-side |
| "X vs last year" | Year-over-year |
| "change from" | Delta calculation |
| "growth rate" | Percentage change |

## Available Metrics

```
/dbt-query list metrics
```

Output:

```
Available Metrics:

Revenue Metrics:
- revenue: Total completed order revenue
- average_order_value: Revenue per order
- net_revenue: Revenue minus refunds

Customer Metrics:
- customer_count: Unique customers
- new_customer_count: First-time buyers
- repeat_rate: Repeat purchase percentage

Order Metrics:
- order_count: Number of orders
- units_sold: Total quantity sold

Use: /dbt-query "[metric] by [dimension] for [time period]"
```

## Available Dimensions

```
/dbt-query list dimensions
```

Output:

```
Available Dimensions:

Time:
- order_date (day, week, month, quarter, year)
- created_at

Customer:
- customer_segment
- customer_country
- customer_region

Product:
- product_category
- product_name
- brand

Order:
- order_status
- channel
- payment_method
```

## Error Handling

### Unknown Metric

```
/dbt-query "profit by month"

⚠️  Metric 'profit' not found

Available similar metrics:
- revenue
- net_revenue
- gross_margin

Did you mean one of these?
```

### Ambiguous Query

```
/dbt-query "sales"

⚠️  Ambiguous query. Please clarify:

1. "total revenue" - Sum of order amounts
2. "order count" - Number of orders
3. "units sold" - Total quantity

Example: /dbt-query "total revenue last month"
```

### Missing Time Filter

```
/dbt-query "revenue by category"

⚠️  No time filter specified

This query would scan all historical data.

Suggestions:
- "revenue by category for last month"
- "revenue by category YTD"
- "revenue by category for 2024"
```

## Interactive Mode

```
/dbt-query

What would you like to know?
> revenue trends

I can help with revenue queries. What specifically?

1. Total revenue for a time period
2. Revenue by dimension (category, region, etc.)
3. Revenue comparison (vs prior period)
4. Revenue growth rate

Select or describe: _
```

## Persona Integration

This command activates the **Semantic Analyst** (`semantic:`) persona for natural language understanding and query generation.

## Related

- [[dbt-docs.md]] - View metric definitions
- [[dbt-run.md]] - Execute underlying models
- [[../skills/dbt-semantic-layer.md]] - Semantic layer workflow
- [[../agents/semantic-analyst.md]] - Semantic Analyst persona
