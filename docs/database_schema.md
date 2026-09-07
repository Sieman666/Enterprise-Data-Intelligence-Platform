# Database Schema

The analytical database is designed around a lightweight ecommerce domain. It supports customer, product, order, and user behavior analysis.

## Tables

### customers

Customer master data.

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER | Primary key |
| first_name | VARCHAR(100) | Customer first name |
| last_name | VARCHAR(100) | Customer last name |
| email | VARCHAR(255) | Unique customer email |
| phone | VARCHAR(50) | Optional phone number |
| country | VARCHAR(100) | Customer country |
| city | VARCHAR(100) | Customer city |
| customer_segment | VARCHAR(50) | Segment such as Consumer, Small Business, Enterprise, or VIP |
| signup_date | DATE | Customer signup date |
| created_at | TIMESTAMP WITH TIME ZONE | Record creation timestamp |

### products

Product master data.

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER | Primary key |
| product_name | VARCHAR(255) | Product name |
| category | VARCHAR(100) | Product category |
| brand | VARCHAR(100) | Product brand |
| unit_price | NUMERIC(10, 2) | Product unit price |
| stock_quantity | INTEGER | Current stock quantity |
| created_at | TIMESTAMP WITH TIME ZONE | Record creation timestamp |

### orders

Order fact table.

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER | Primary key |
| customer_id | INTEGER | Foreign key to customers.id |
| product_id | INTEGER | Foreign key to products.id |
| order_date | TIMESTAMP WITH TIME ZONE | Order timestamp |
| quantity | INTEGER | Units ordered |
| unit_price | NUMERIC(10, 2) | Unit price at purchase time |
| total_amount | NUMERIC(12, 2) | Quantity multiplied by unit price |
| order_status | VARCHAR(50) | completed, processing, cancelled, or returned |
| payment_method | VARCHAR(50) | Payment method |
| region | VARCHAR(100) | Sales region |

### user_behavior

User behavior event table.

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER | Primary key |
| customer_id | INTEGER | Foreign key to customers.id |
| product_id | INTEGER | Optional foreign key to products.id |
| session_id | VARCHAR(100) | User session identifier |
| event_type | VARCHAR(50) | page_view, product_view, add_to_cart, checkout_start, or purchase |
| event_timestamp | TIMESTAMP WITH TIME ZONE | Event timestamp |
| page_url | VARCHAR(500) | Page path |
| device_type | VARCHAR(50) | desktop, mobile, or tablet |
| traffic_source | VARCHAR(100) | Marketing or traffic source |

## Relationships

```text
customers.id  -> orders.customer_id
products.id   -> orders.product_id
customers.id  -> user_behavior.customer_id
products.id   -> user_behavior.product_id
```

`orders` is the primary revenue fact table. `user_behavior` supports funnel and conversion analysis and may contain events that do not reference a specific product.
