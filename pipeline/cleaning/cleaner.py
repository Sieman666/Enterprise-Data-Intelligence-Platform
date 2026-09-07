import logging
import re

import pandas as pd

logger = logging.getLogger(__name__)

DATE_COLUMN_HINTS = ("date", "time", "timestamp", "created_at")


def _normalize_column_name(column: str) -> str:
    normalized = column.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_")


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    cleaned.columns = [_normalize_column_name(column) for column in cleaned.columns]
    logger.info("Normalized column names")

    before_dedup = len(cleaned)
    cleaned = cleaned.drop_duplicates()
    removed_duplicates = before_dedup - len(cleaned)
    logger.info("Removed %s duplicated rows", removed_duplicates)

    cleaned = cleaned.replace(r"^\s*$", pd.NA, regex=True)

    for column in cleaned.select_dtypes(include=["object"]).columns:
        cleaned[column] = cleaned[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    for column in cleaned.columns:
        if any(hint in column for hint in DATE_COLUMN_HINTS):
            cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce", utc=True)
            continue

        numeric_candidate = pd.to_numeric(cleaned[column], errors="coerce")
        non_missing_values = cleaned[column].notna()
        if (
            non_missing_values.any()
            and numeric_candidate[non_missing_values].notna().all()
        ):
            cleaned[column] = numeric_candidate

    for column in cleaned.select_dtypes(include=["object", "string"]).columns:
        cleaned[column] = cleaned[column].fillna("unknown")

    logger.info("Handled missing values and converted data types where possible")
    return cleaned
