import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
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


settings = Settings()
