from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

OUTPUT_DIR = Path(__file__).resolve().parent

CUSTOMER_COUNT = 1_000
PRODUCT_COUNT = 200
ORDER_COUNT = 10_000
USER_BEHAVIOR_COUNT = 20_000

CATEGORIES = [
    "Electronics",
    "Home & Kitchen",
    "Office Supplies",
    "Sports",
    "Beauty",
    "Books",
    "Clothing",
    "Toys",
]
CUSTOMER_SEGMENTS = ["Consumer", "Small Business", "Enterprise", "VIP"]
ORDER_STATUSES = ["completed", "processing", "cancelled", "returned"]
PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "bank_transfer"]
DEVICE_TYPES = ["desktop", "mobile", "tablet"]
EVENT_TYPES = ["page_view", "product_view", "add_to_cart", "checkout_start", "purchase"]
TRAFFIC_SOURCES = ["direct", "organic_search", "paid_search", "email", "social", "referral"]
REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]


def utc_now() -> datetime:
    return datetime.now(UTC)


def generate_customers() -> pd.DataFrame:
    rows = []

    for customer_id in range(1, CUSTOMER_COUNT + 1):
        profile = fake.simple_profile()
        signup_date = fake.date_between(start_date="-3y", end_date="today")

        rows.append(
            {
                "id": customer_id,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": f"customer{customer_id}.{profile['username']}@example.com",
                "phone": fake.phone_number(),
                "country": fake.country(),
                "city": fake.city(),
                "customer_segment": random.choices(
                    CUSTOMER_SEGMENTS,
                    weights=[0.55, 0.25, 0.15, 0.05],
                    k=1,
                )[0],
                "signup_date": signup_date.isoformat(),
                "created_at": utc_now().isoformat(timespec="seconds"),
            }
        )

    return pd.DataFrame(rows)


def generate_products() -> pd.DataFrame:
    rows = []

    for product_id in range(1, PRODUCT_COUNT + 1):
        category = random.choice(CATEGORIES)
        unit_price = round(random.uniform(8.0, 850.0), 2)

        rows.append(
            {
                "id": product_id,
                "product_name": f"{fake.company()} {category} Item {product_id}",
                "category": category,
                "brand": fake.company(),
                "unit_price": unit_price,
                "stock_quantity": random.randint(0, 1_500),
                "created_at": utc_now().isoformat(timespec="seconds"),
            }
        )

    return pd.DataFrame(rows)


def generate_orders(products: pd.DataFrame) -> pd.DataFrame:
    rows = []
    product_prices = products.set_index("id")["unit_price"].to_dict()

    for order_id in range(1, ORDER_COUNT + 1):
        product_id = random.randint(1, PRODUCT_COUNT)
        quantity = random.choices([1, 2, 3, 4, 5], weights=[0.5, 0.25, 0.13, 0.08, 0.04], k=1)[0]
        unit_price = product_prices[product_id]
        order_date = utc_now() - timedelta(days=random.randint(0, 730), seconds=random.randint(0, 86_400))

        rows.append(
            {
                "id": order_id,
                "customer_id": random.randint(1, CUSTOMER_COUNT),
                "product_id": product_id,
                "order_date": order_date.isoformat(timespec="seconds"),
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": round(unit_price * quantity, 2),
                "order_status": random.choices(
                    ORDER_STATUSES,
                    weights=[0.78, 0.12, 0.06, 0.04],
                    k=1,
                )[0],
                "payment_method": random.choice(PAYMENT_METHODS),
                "region": random.choice(REGIONS),
            }
        )

    return pd.DataFrame(rows)


def generate_user_behavior() -> pd.DataFrame:
    rows = []

    for event_id in range(1, USER_BEHAVIOR_COUNT + 1):
        event_type = random.choices(EVENT_TYPES, weights=[0.42, 0.32, 0.14, 0.08, 0.04], k=1)[0]
        product_id = random.randint(1, PRODUCT_COUNT) if event_type != "page_view" else None
        timestamp = utc_now() - timedelta(days=random.randint(0, 730), seconds=random.randint(0, 86_400))

        rows.append(
            {
                "id": event_id,
                "customer_id": random.randint(1, CUSTOMER_COUNT),
                "product_id": product_id,
                "session_id": fake.uuid4(),
                "event_type": event_type,
                "event_timestamp": timestamp.isoformat(timespec="seconds"),
                "page_url": f"/{event_type.replace('_', '-')}/{product_id or 'home'}",
                "device_type": random.choice(DEVICE_TYPES),
                "traffic_source": random.choice(TRAFFIC_SOURCES),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    customers = generate_customers()
    products = generate_products()
    orders = generate_orders(products)
    user_behavior = generate_user_behavior()

    customers.to_csv(OUTPUT_DIR / "customers.csv", index=False)
    products.to_csv(OUTPUT_DIR / "products.csv", index=False)
    orders.to_csv(OUTPUT_DIR / "orders.csv", index=False)
    user_behavior.to_csv(OUTPUT_DIR / "user_behavior.csv", index=False)

    print("Sample data generated:")
    print(f"- customers: {len(customers)} rows")
    print(f"- products: {len(products)} rows")
    print(f"- orders: {len(orders)} rows")
    print(f"- user_behavior: {len(user_behavior)} rows")


if __name__ == "__main__":
    main()
