# Demo

This demo shows the end-to-end analytics flow for the Enterprise Data Intelligence Platform using the sample ecommerce dataset.

## Demo Scenario

A business user wants to identify the product with the highest completed-order revenue and receive a concise business interpretation of the result.

The platform flow is:

```text
Natural language question
-> Text-to-SQL generation
-> SQL safety validation
-> PostgreSQL execution
-> AI business insight generation
```

## Example Natural Language Question

```text
Which product generated highest revenue?
```

## Generated SQL Example

```sql
SELECT
    p.product_name,
    SUM(o.total_amount) AS revenue
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE o.order_status = 'completed'
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 1;
```

## Returned Data Example

```json
[
  {
    "product_name": "Example Product",
    "revenue": 6375986.17
  }
]
```

## AI Insight Example

```text
1. Key findings
Example Product generated the highest revenue in the query result, with revenue of 6375986.17.

2. Possible reasons
The available result only supports that this product ranked first by completed-order revenue. Additional product category, pricing, promotion, and traffic data would be needed to explain the underlying cause.

3. Business recommendations
Review inventory availability for this product, compare its revenue performance with margin and return rates, and investigate whether similar products can benefit from the same demand drivers.
```

## Fixed Analytics Reports

The platform also exposes pre-computed analytics reports directly from PostgreSQL:

```text
GET /api/analytics/kpis
GET /api/analytics/trends
GET /api/analytics/profile
```

These endpoints reuse the same profiling, KPI, and trend logic as `analytics.run_analysis` but return results through the REST API.

## Notes

- The exact generated SQL may vary by model, but it must pass the SQL validator and remain a single PostgreSQL `SELECT` query.
- The insight should only reference numbers present in the returned data or supplied context.
- The demo assumes PostgreSQL has been initialized and sample data has been loaded through the ETL pipeline.
