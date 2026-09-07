import logging
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.query import QueryRequest, QueryResponse
from llm.client import LLMClientError
from llm.insight_generation.generator import generate_insight
from llm.text_to_sql.executor import SQLExecutionError, execute_sql
from llm.text_to_sql.generator import generate_sql
from llm.text_to_sql.validator import SQLValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["text-to-sql"])


@router.post("/query", response_model=QueryResponse)
def query_data(payload: QueryRequest) -> QueryResponse:
    try:
        sql = generate_sql(payload.question)
        result_df = execute_sql(sql)
        data = result_df.to_dict(orient="records")

        if result_df.empty:
            logger.info("Generated query returned an empty result")

        insight = ""
        try:
            insight = generate_insight(
                question=payload.question,
                sql_result=data,
                context=None,
            )
        except LLMClientError as exc:
            logger.warning(
                "Insight generation failed after successful SQL execution: %s", exc
            )

        return QueryResponse(
            question=payload.question,
            sql=sql,
            data=data,
            insight=insight,
        )

    except LLMClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM failure: {exc}",
        ) from exc
    except SQLValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid SQL: {exc}",
        ) from exc
    except SQLExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SQL execution failed: {exc}",
        ) from exc
