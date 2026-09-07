from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)


class QueryResponse(BaseModel):
    question: str
    sql: str
    data: list[dict[str, Any]]
    insight: str
