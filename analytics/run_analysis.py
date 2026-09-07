import argparse
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from analytics.analysis.kpi import calculate_ecommerce_kpis
from analytics.analysis.statistics import (
    analyze_categorical_columns,
    analyze_numeric_columns,
)
from analytics.analysis.trend import monthly_sales_trend
from analytics.profiling.profiler import generate_profile

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DEFAULT_SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reports"

DATASET_FILES = {
    "customers": "customers.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "user_behavior": "user_behavior.csv",
}


def _resolve_data_dir(data_dir: Path | None = None) -> Path:
    if data_dir:
        return data_dir

    processed_files_exist = all(
        (DEFAULT_PROCESSED_DIR / file_name).exists()
        for file_name in DATASET_FILES.values()
    )
    if processed_files_exist:
        return DEFAULT_PROCESSED_DIR

    return DEFAULT_SAMPLE_DIR


def _load_datasets(data_dir: Path) -> dict[str, pd.DataFrame]:
    datasets = {}

    for dataset_name, file_name in DATASET_FILES.items():
        path = data_dir / file_name
        if not path.exists():
            raise FileNotFoundError(f"Required dataset not found: {path}")

        datasets[dataset_name] = pd.read_csv(path)
        logger.info("Loaded %s with %s rows", file_name, len(datasets[dataset_name]))

    return datasets


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    logger.info("Saved report: %s", path)


def run_analysis(
    data_dir: Path | None = None,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
) -> dict[str, Any]:
    resolved_data_dir = _resolve_data_dir(data_dir)
    logger.info("Using data directory: %s", resolved_data_dir)

    datasets = _load_datasets(resolved_data_dir)

    profile_report = {
        dataset_name: {
            "profile": generate_profile(df),
            "numeric_statistics": analyze_numeric_columns(df),
            "categorical_statistics": analyze_categorical_columns(df),
        }
        for dataset_name, df in datasets.items()
    }

    kpi_report = calculate_ecommerce_kpis(
        orders_df=datasets["orders"],
        customers_df=datasets["customers"],
        behavior_df=datasets["user_behavior"],
    )

    trend_report = {
        "monthly_sales_trend": monthly_sales_trend(datasets["orders"]),
    }

    _write_json(reports_dir / "profile_report.json", profile_report)
    _write_json(reports_dir / "kpi_report.json", kpi_report)
    _write_json(reports_dir / "trend_report.json", trend_report)

    return {
        "profile_report": profile_report,
        "kpi_report": kpi_report,
        "trend_report": trend_report,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run automated ecommerce analytics.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory containing customers, products, orders, and user_behavior CSV files.",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=DEFAULT_REPORTS_DIR,
        help="Directory where JSON reports will be saved.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run_analysis(data_dir=args.data_dir, reports_dir=args.reports_dir)
    print(
        json.dumps(
            {
                "reports_generated": [
                    "profile_report.json",
                    "kpi_report.json",
                    "trend_report.json",
                ],
                "kpi_summary": results["kpi_report"],
                "trend_months": len(results["trend_report"]["monthly_sales_trend"]),
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
