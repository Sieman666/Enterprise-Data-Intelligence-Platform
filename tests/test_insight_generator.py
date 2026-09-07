from unittest.mock import patch

import pandas as pd

from llm.insight_generation.generator import generate_insight


def test_generate_insight_calls_llm_with_prompt():
    with patch(
        "llm.insight_generation.generator.generate_text",
        return_value="Top product is A.",
    ) as mock_generate_text:
        result = generate_insight(
            "What is the top product?", [{"product_name": "A", "revenue": 1000}]
        )

    assert result == "Top product is A."
    mock_generate_text.assert_called_once()
    prompt = mock_generate_text.call_args[0][0]
    assert "What is the top product?" in prompt
    assert "A" in prompt


def test_generate_insight_accepts_dataframe_input():
    df = pd.DataFrame([{"product_name": "B", "revenue": 500}])

    with patch(
        "llm.insight_generation.generator.generate_text",
        return_value="Product B insight.",
    ):
        result = generate_insight("Analyze products", df)

    assert result == "Product B insight."
