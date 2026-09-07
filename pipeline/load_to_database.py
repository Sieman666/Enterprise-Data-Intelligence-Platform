import logging
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import engine

logger = logging.getLogger(__name__)

SUPPORTED_TABLES = {
    "customers",
    "products",
    "orders",
    "user_behavior",
}


def load_dataframe_to_db(
    df: pd.DataFrame,
    table_name: str,
    if_exists: str = "append",
) -> int:
    if table_name not in SUPPORTED_TABLES:
        raise ValueError(f"Unsupported table name: {table_name}")

    if if_exists not in {"append", "replace", "fail"}:
        raise ValueError("if_exists must be one of: append, replace, fail")

    rows_to_insert = len(df)
    prepared = df.where(pd.notna(df), None)

    with engine.begin() as connection:
        prepared.to_sql(
            table_name,
            con=connection,
            if_exists=if_exists,
            index=False,
            method="multi",
            chunksize=1_000,
        )

    logger.info("Inserted %s rows into %s", rows_to_insert, table_name)
    return rows_to_insert


def truncate_tables(table_names: list[str]) -> None:
    unsupported = set(table_names) - SUPPORTED_TABLES
    if unsupported:
        raise ValueError(f"Unsupported table names: {unsupported}")

    with engine.begin() as connection:
        for table_name in reversed(table_names):
            connection.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))

    logger.info("Truncated tables: %s", table_names)
