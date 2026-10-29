from app.core.config import Settings
from sqlalchemy import create_engine


def test_postgres_urls_use_installed_psycopg2_driver():
    settings = Settings(
        database_url="postgresql://user:password@localhost/db",
        readonly_database_url="postgresql://reader:password@localhost/db",
    )

    for url in (settings.database_url, settings.readonly_database_url):
        assert create_engine(url).dialect.driver == "psycopg2"


def test_explicit_driver_is_preserved():
    url = "postgresql+psycopg://user:password@localhost/db"
    assert Settings(database_url=url).database_url == url
