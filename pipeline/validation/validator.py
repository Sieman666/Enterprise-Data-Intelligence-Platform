from typing import Any

import pandas as pd


def validate_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "missing_values": {
            column: int(count) for column, count in df.isna().sum().to_dict().items()
        },
        "duplicates": int(df.duplicated().sum()),
    }
