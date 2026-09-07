from urllib.parse import urlparse

from sqlalchemy import text

from app.core.config import settings
from app.database.session import Base, engine

READONLY_USER = "enterprise_readonly"


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def create_readonly_user() -> None:
    readonly_url = settings.readonly_database_url
    if not readonly_url:
        return

    parsed = urlparse(readonly_url)
    password = parsed.password
    if not password:
        return

    with engine.begin() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
            {"name": READONLY_USER},
        ).scalar()

        if not exists:
            connection.execute(
                text(f"CREATE ROLE {READONLY_USER} WITH LOGIN PASSWORD :password"),
                {"password": password},
            )

        for table in Base.metadata.sorted_tables:
            connection.execute(
                text(f"GRANT SELECT ON {table.name} TO {READONLY_USER}"),
            )


if __name__ == "__main__":
    create_tables()
    create_readonly_user()
