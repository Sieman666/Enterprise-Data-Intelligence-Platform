from typing import Any

import pandas as pd


def generate_profile(df: pd.DataFrame) -> dict[str, Any]:
    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    return {
        "rows": len(df),
        "columns": df.columns.tolist(),
        "missing_values": {
            column: int(count) for column, count in df.isna().sum().to_dict().items()
        },
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
    }
