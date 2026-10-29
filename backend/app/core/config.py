import os

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, field_validator

load_dotenv()


class Settings(BaseModel):
    model_config = ConfigDict(validate_default=True)

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://enterprise_user:enterprise_password@localhost:5432/enterprise_dw",
    )
    readonly_database_url: str = os.getenv(
        "READONLY_DATABASE_URL",
        "",
    )
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "")
    llm_base_url: str = os.getenv(
        "LLM_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    query_timeout_ms: int = int(os.getenv("QUERY_TIMEOUT_MS", "10000"))
    max_query_rows: int = int(os.getenv("MAX_QUERY_ROWS", "1000"))

    @field_validator("database_url", "readonly_database_url")
    @classmethod
    def use_installed_postgres_driver(cls, url: str) -> str:
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url


settings = Settings()
