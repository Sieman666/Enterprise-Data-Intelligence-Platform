import logging
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import readonly_engine

logger = logging.getLogger(__name__)


class SQLExecutionError(RuntimeError):
    pass


def execute_sql(sql: str) -> pd.DataFrame:
    try:
        with readonly_engine.connect() as connection:
            df = pd.read_sql_query(text(sql), connection)

        logger.info("Executed SQL and returned %s rows", len(df))
        return df
    except SQLAlchemyError as exc:
        logger.exception("SQL execution failed")
        raise SQLExecutionError(str(exc)) from exc
