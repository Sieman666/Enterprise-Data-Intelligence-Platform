from typing import Any

import pandas as pd


def analyze_numeric_columns(df: pd.DataFrame) -> dict[str, dict[str, float | None]]:
    numeric_df = df.select_dtypes(include=["number"])
    results: dict[str, dict[str, float | None]] = {}

    for column in numeric_df.columns:
        series = numeric_df[column].dropna()
        if series.empty:
            results[column] = {
                "mean": None,
                "median": None,
                "std": None,
                "min": None,
                "max": None,
            }
            continue

        results[column] = {
            "mean": float(series.mean()),
            "median": float(series.median()),
            "std": float(series.std()) if len(series) > 1 else 0.0,
            "min": float(series.min()),
            "max": float(series.max()),
        }

    return results


def analyze_categorical_columns(
    df: pd.DataFrame,
    top_n: int = 10,
) -> dict[str, dict[str, Any]]:
    categorical_df = df.select_dtypes(include=["object", "category", "bool"])
    results: dict[str, dict[str, Any]] = {}

    for column in categorical_df.columns:
        counts = categorical_df[column].fillna("missing").value_counts().head(top_n)
        results[column] = {
            "unique_count": int(categorical_df[column].nunique(dropna=True)),
            "top_categories": {
                str(category): int(count)
                for category, count in counts.to_dict().items()
            },
        }

    return results
