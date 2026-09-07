import logging

import pandas as pd

logger = logging.getLogger(__name__)


def _select_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    missing_columns = [column for column in columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    return df[columns].copy()


def _coerce_integer_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
    return df


def _coerce_decimal_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").round(2)
    return df


def _coerce_datetime_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        df[column] = pd.to_datetime(df[column], errors="coerce", utc=True)
    return df


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "country",
        "city",
        "customer_segment",
        "signup_date",
        "created_at",
    ]
    transformed = _select_columns(df, columns)
    transformed = _coerce_integer_columns(transformed, ["id"])
    transformed["signup_date"] = pd.to_datetime(
        transformed["signup_date"], errors="coerce"
    ).dt.date
    transformed = _coerce_datetime_columns(transformed, ["created_at"])
    transformed = transformed.dropna(subset=["id", "email", "signup_date"])
    logger.info("Transformed customers dataset")
    return transformed


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "id",
        "product_name",
        "category",
        "brand",
        "unit_price",
        "stock_quantity",
        "created_at",
    ]
    transformed = _select_columns(df, columns)
    transformed = _coerce_integer_columns(transformed, ["id", "stock_quantity"])
    transformed = _coerce_decimal_columns(transformed, ["unit_price"])
    transformed = _coerce_datetime_columns(transformed, ["created_at"])
    transformed = transformed.dropna(
        subset=["id", "product_name", "category", "unit_price"]
    )
    logger.info("Transformed products dataset")
    return transformed


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "id",
        "customer_id",
        "product_id",
        "order_date",
        "quantity",
        "unit_price",
        "total_amount",
        "order_status",
        "payment_method",
        "region",
    ]
    transformed = _select_columns(df, columns)
    transformed = _coerce_integer_columns(
        transformed, ["id", "customer_id", "product_id", "quantity"]
    )
    transformed = _coerce_decimal_columns(transformed, ["unit_price", "total_amount"])
    transformed = _coerce_datetime_columns(transformed, ["order_date"])
    transformed = transformed.dropna(
        subset=["id", "customer_id", "product_id", "order_date"]
    )
    logger.info("Transformed orders dataset")
    return transformed


def transform_user_behavior(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "id",
        "customer_id",
        "product_id",
        "session_id",
        "event_type",
        "event_timestamp",
        "page_url",
        "device_type",
        "traffic_source",
    ]
    transformed = _select_columns(df, columns)
    transformed = _coerce_integer_columns(
        transformed, ["id", "customer_id", "product_id"]
    )
    transformed = _coerce_datetime_columns(transformed, ["event_timestamp"])
    transformed = transformed.dropna(
        subset=["id", "customer_id", "session_id", "event_timestamp"]
    )
    logger.info("Transformed user_behavior dataset")
    return transformed
