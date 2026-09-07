from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)

_readonly_url = settings.readonly_database_url or settings.database_url
_readonly_connect_args: dict = {}
if _readonly_url.startswith("postgresql"):
    _readonly_connect_args = {
        "options": f"-c statement_timeout={settings.query_timeout_ms}",
    }

readonly_engine = create_engine(
    _readonly_url,
    pool_pre_ping=True,
    connect_args=_readonly_connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
