from unittest.mock import patch

import pytest

from llm.text_to_sql.generator import generate_sql
from llm.text_to_sql.validator import SQLValidationError


def test_generate_sql_returns_validated_query_with_row_limit():
    with (
        patch(
            "llm.text_to_sql.generator.get_database_schema", return_value="schema text"
        ),
        patch(
            "llm.text_to_sql.generator.generate_text",
            return_value="SELECT id FROM orders",
        ),
    ):
        sql = generate_sql("List order IDs")

    assert sql == "SELECT id FROM orders LIMIT 1000"


def test_generate_sql_preserves_existing_limit():
    with (
        patch(
            "llm.text_to_sql.generator.get_database_schema", return_value="schema text"
        ),
        patch(
            "llm.text_to_sql.generator.generate_text",
            return_value="SELECT id FROM orders LIMIT 50",
        ),
    ):
        sql = generate_sql("List order IDs")

    assert sql == "SELECT id FROM orders LIMIT 50"


def test_generate_sql_rejects_unsafe_generated_sql():
    with (
        patch(
            "llm.text_to_sql.generator.get_database_schema", return_value="schema text"
        ),
        patch(
            "llm.text_to_sql.generator.generate_text", return_value="DROP TABLE orders"
        ),
        pytest.raises(SQLValidationError),
    ):
        generate_sql("Delete orders")


def test_generate_sql_builds_prompt_with_schema_and_question():
    with (
        patch(
            "llm.text_to_sql.generator.get_database_schema", return_value="schema text"
        ) as mock_schema,
        patch(
            "llm.text_to_sql.generator.generate_text", return_value="SELECT 1"
        ) as mock_generate_text,
        patch(
            "llm.text_to_sql.generator.validate_sql", return_value="SELECT 1"
        ) as mock_validate,
    ):
        generate_sql("What is revenue?")

    mock_schema.assert_called_once()
    mock_generate_text.assert_called_once()
    prompt = mock_generate_text.call_args[0][0]
    assert "schema text" in prompt
    assert "What is revenue?" in prompt
    mock_validate.assert_called_once_with("SELECT 1")
