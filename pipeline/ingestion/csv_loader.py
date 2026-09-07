import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

SUPPORTED_FILES = {
    "customers.csv",
    "products.csv",
    "orders.csv",
    "user_behavior.csv",
}


def load_csv(path: str | Path) -> pd.DataFrame:
    csv_path = Path(path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    if csv_path.name not in SUPPORTED_FILES:
        logger.warning("Loading unsupported CSV filename: %s", csv_path.name)

    df = pd.read_csv(csv_path)
    logger.info(
        "Loaded %s with %s rows and %s columns", csv_path.name, len(df), len(df.columns)
    )
    logger.info("Detected columns for %s: %s", csv_path.name, list(df.columns))

    return df
