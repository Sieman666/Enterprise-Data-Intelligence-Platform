from typing import Any

import pandas as pd


def calculate_ecommerce_kpis(
    orders_df: pd.DataFrame,
    customers_df: pd.DataFrame,
    behavior_df: pd.DataFrame,
) -> dict[str, Any]:
    orders = orders_df.copy()
    customers = customers_df.copy()
    behavior = behavior_df.copy()

    orders["total_amount"] = pd.to_numeric(
        orders["total_amount"], errors="coerce"
    ).fillna(0)
    completed_orders = orders[
        orders["order_status"].astype(str).str.lower() == "completed"
    ]

    revenue = float(completed_orders["total_amount"].sum())
    order_count = len(completed_orders)
    average_order_value = revenue / order_count if order_count else 0.0
    customer_count = (
        int(customers["id"].nunique()) if "id" in customers.columns else len(customers)
    )

    purchase_events = 0
    total_sessions = 0

    if not behavior.empty:
        if "event_type" in behavior.columns:
            purchase_events = int(
                (behavior["event_type"].astype(str).str.lower() == "purchase").sum()
            )
        if "session_id" in behavior.columns:
            total_sessions = int(behavior["session_id"].nunique())

    purchase_conversion_rate = (
        purchase_events / total_sessions if total_sessions else 0.0
    )

    return {
        "revenue": round(revenue, 2),
        "order_count": order_count,
        "average_order_value": round(average_order_value, 2),
        "customer_count": customer_count,
        "purchase_conversion_rate": round(purchase_conversion_rate, 4),
        "purchase_events": purchase_events,
        "behavior_sessions": total_sessions,
    }
