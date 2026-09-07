from typing import Any

import pandas as pd


def monthly_sales_trend(orders_df: pd.DataFrame) -> list[dict[str, Any]]:
    orders = orders_df.copy()
    orders["order_date"] = pd.to_datetime(
        orders["order_date"], errors="coerce", utc=True
    )
    orders["total_amount"] = pd.to_numeric(
        orders["total_amount"], errors="coerce"
    ).fillna(0)

    if "order_status" in orders.columns:
        orders = orders[orders["order_status"].astype(str).str.lower() == "completed"]

    orders = orders.dropna(subset=["order_date"])
    if orders.empty:
        return []

    orders["month"] = orders["order_date"].dt.strftime("%Y-%m")
    trend = (
        orders.groupby("month")
        .agg(
            monthly_revenue=("total_amount", "sum"),
            monthly_order_count=("id", "count"),
        )
        .reset_index()
        .sort_values("month")
    )
    trend["monthly_revenue"] = trend["monthly_revenue"].round(2)

    return [
        {
            "month": row["month"],
            "monthly_revenue": float(row["monthly_revenue"]),
            "monthly_order_count": int(row["monthly_order_count"]),
        }
        for _, row in trend.iterrows()
    ]
