import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import Base


def get_database_schema() -> str:
    tables = []

    for table in Base.metadata.sorted_tables:
        columns = []
        for column in table.columns:
            nullable = "nullable" if column.nullable else "not nullable"
            columns.append(f"  - {column.name}: {column.type} ({nullable})")

        tables.append(f"Table: {table.name}\nColumns:\n" + "\n".join(columns))

    return "\n\n".join(tables)
