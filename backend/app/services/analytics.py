import logging

import pandas as pd
from sqlalchemy import text

from analytics.analysis.kpi import calculate_ecommerce_kpis
from analytics.analysis.statistics import (
    analyze_categorical_columns,
    analyze_numeric_columns,
)
from analytics.analysis.trend import monthly_sales_trend
from analytics.profiling.profiler import generate_profile
from app.database.session import readonly_engine

logger = logging.getLogger(__name__)


def _load_table(table_name: str) -> pd.DataFrame:
    with readonly_engine.connect() as connection:
        return pd.read_sql_query(text(f"SELECT * FROM {table_name}"), connection)


def get_kpi_report() -> dict:
    orders = _load_table("orders")
    customers = _load_table("customers")
    behavior = _load_table("user_behavior")
    return calculate_ecommerce_kpis(orders, customers, behavior)


def get_trend_report() -> dict:
    orders = _load_table("orders")
    return {"monthly_sales_trend": monthly_sales_trend(orders)}


def get_profile_report() -> dict:
    datasets = {
        "customers": _load_table("customers"),
        "products": _load_table("products"),
        "orders": _load_table("orders"),
        "user_behavior": _load_table("user_behavior"),
    }

    return {
        dataset_name: {
            "profile": generate_profile(df),
            "numeric_statistics": analyze_numeric_columns(df),
            "categorical_statistics": analyze_categorical_columns(df),
        }
        for dataset_name, df in datasets.items()
    }
