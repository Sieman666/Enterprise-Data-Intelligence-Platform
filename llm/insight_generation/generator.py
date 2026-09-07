import logging
from typing import Any

import pandas as pd

from llm.client import generate_text
from llm.insight_generation.prompt import build_insight_prompt

logger = logging.getLogger(__name__)


def _normalize_sql_result(
    sql_result: pd.DataFrame | list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if isinstance(sql_result, pd.DataFrame):
        return sql_result.to_dict(orient="records")
    return sql_result


def generate_insight(
    question: str,
    sql_result: pd.DataFrame | list[dict[str, Any]],
    context: dict[str, Any] | None = None,
) -> str:
    normalized_result = _normalize_sql_result(sql_result)
    prompt = build_insight_prompt(
        question=question,
        sql_result=normalized_result,
        context=context,
    )

    insight = generate_text(
        prompt,
        system_prompt=(
            "You are an enterprise data analyst who explains query results "
            "without inventing unsupported facts."
        ),
    )
    logger.info("Generated insight for question: %s", question)
    return insight
