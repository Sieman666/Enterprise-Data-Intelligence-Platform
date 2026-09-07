import argparse
import json
import logging
from collections.abc import Callable
from pathlib import Path

import pandas as pd

from pipeline.cleaning.cleaner import clean_dataframe
from pipeline.ingestion.csv_loader import load_csv
from pipeline.load_to_database import load_dataframe_to_db, truncate_tables
from pipeline.transformation.transformer import (
    transform_customers,
    transform_orders,
    transform_products,
    transform_user_behavior,
)
from pipeline.validation.validator import validate_dataframe

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "sample"

DATASETS: dict[str, dict[str, str | Callable[[pd.DataFrame], pd.DataFrame]]] = {
    "customers": {
        "file": "customers.csv",
        "transform": transform_customers,
    },
    "products": {
        "file": "products.csv",
        "transform": transform_products,
    },
    "orders": {
        "file": "orders.csv",
        "transform": transform_orders,
    },
    "user_behavior": {
        "file": "user_behavior.csv",
        "transform": transform_user_behavior,
    },
}


def run_etl(
    input_dir: Path = DEFAULT_INPUT_DIR,
    datasets: list[str] | None = None,
    load_database: bool = True,
    replace: bool = False,
) -> dict[str, dict]:
    selected_datasets = datasets or list(DATASETS.keys())
    results = {}

    if replace and load_database:
        truncate_tables(selected_datasets)

    for dataset_name in selected_datasets:
        if dataset_name not in DATASETS:
            raise ValueError(f"Unsupported dataset: {dataset_name}")

        dataset_config = DATASETS[dataset_name]
        file_name = str(dataset_config["file"])
        transform = dataset_config["transform"]
        csv_path = input_dir / file_name

        logger.info("Starting ETL for %s", file_name)
        loaded = load_csv(csv_path)
        cleaned = clean_dataframe(loaded)
        validation = validate_dataframe(cleaned)
        transformed = transform(cleaned)
        transformed_validation = validate_dataframe(transformed)

        if load_database:
            inserted_rows = load_dataframe_to_db(transformed, dataset_name)
        else:
            inserted_rows = 0
            logger.info("Skipped database insert for %s", dataset_name)

        results[dataset_name] = {
            "source_file": file_name,
            "loaded_rows": len(loaded),
            "cleaned_validation": validation,
            "transformed_validation": transformed_validation,
            "inserted_rows": inserted_rows,
        }

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the lightweight ETL pipeline.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing source CSV files.",
    )
    parser.add_argument(
        "--datasets",
        nargs="+",
        choices=list(DATASETS.keys()),
        default=list(DATASETS.keys()),
        help="Datasets to process in dependency-safe order.",
    )
    parser.add_argument(
        "--skip-db-load",
        action="store_true",
        help="Run load, clean, validate, and transform steps without inserting into PostgreSQL.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Truncate target tables before loading to make the ETL run idempotent.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run_etl(
        input_dir=args.input_dir,
        datasets=args.datasets,
        load_database=not args.skip_db_load,
        replace=args.replace,
    )
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
