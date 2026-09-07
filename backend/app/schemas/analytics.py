from typing import Any

from pydantic import BaseModel


class KPIReport(BaseModel):
    revenue: float
    order_count: int
    average_order_value: float
    customer_count: int
    purchase_conversion_rate: float
    purchase_events: int
    behavior_sessions: int


class TrendReport(BaseModel):
    monthly_sales_trend: list[dict[str, Any]]


class DatasetProfile(BaseModel):
    profile: dict[str, Any]
    numeric_statistics: dict[str, dict[str, float | None]]
    categorical_statistics: dict[str, Any]


class ProfileReport(BaseModel):
    customers: DatasetProfile
    products: DatasetProfile
    orders: DatasetProfile
    user_behavior: DatasetProfile
