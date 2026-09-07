import json
from typing import Any


def build_insight_prompt(
    question: str,
    sql_result: list[dict[str, Any]],
    context: dict[str, Any] | None = None,
) -> str:
    limited_result = sql_result[:50]
    omitted_rows = max(len(sql_result) - len(limited_result), 0)

    payload = {
        "question": question,
        "sql_result": limited_result,
        "omitted_result_rows": omitted_rows,
        "context": context or {},
    }

    return f"""
You are an enterprise data analyst.

Analyze the query result and provide business-level analytical insight.

Use only the numbers and facts present in the provided data or context.
Do not hallucinate numbers.
Do not invent unsupported facts.
If the result is empty or insufficient, say that clearly.

Provide the response with these sections:
1. Key findings
2. Possible reasons
3. Business recommendations

Input payload:
{json.dumps(payload, indent=2, default=str)}
""".strip()
