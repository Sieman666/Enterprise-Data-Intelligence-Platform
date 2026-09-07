from unittest.mock import patch

import pandas as pd
from app.main import app
from fastapi.testclient import TestClient

from llm.client import LLMClientError
from llm.text_to_sql.executor import SQLExecutionError
from llm.text_to_sql.validator import SQLValidationError


def test_root_endpoint_returns_health_message():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Enterprise Data Intelligence Platform API running"
    }


def test_query_endpoint_returns_sql_data_and_insight():
    client = TestClient(app)
    question = "Which product generated the highest revenue?"
    generated_sql = "SELECT product_name FROM products LIMIT 1"
    query_result = pd.DataFrame([{"product_name": "Example Product"}])
    generated_insight = "Example Product is the top performer."

    with (
        patch(
            "app.api.query.generate_sql", return_value=generated_sql
        ) as mock_generate_sql,
        patch(
            "app.api.query.execute_sql", return_value=query_result
        ) as mock_execute_sql,
        patch(
            "app.api.query.generate_insight", return_value=generated_insight
        ) as mock_generate_insight,
    ):
        response = client.post("/api/query", json={"question": question})

    assert response.status_code == 200
    body = response.json()
    assert body["question"] == question
    assert body["sql"] == generated_sql
    assert body["data"] == [{"product_name": "Example Product"}]
    assert body["insight"] == generated_insight
    mock_generate_sql.assert_called_once_with(question)
    mock_execute_sql.assert_called_once_with(generated_sql)
    mock_generate_insight.assert_called_once()


def test_query_endpoint_returns_empty_insight_when_llm_fails():
    client = TestClient(app)

    with (
        patch("app.api.query.generate_sql", return_value="SELECT 1"),
        patch("app.api.query.execute_sql", return_value=pd.DataFrame([{"n": 1}])),
        patch(
            "app.api.query.generate_insight",
            side_effect=LLMClientError("LLM unavailable"),
        ),
    ):
        response = client.post("/api/query", json={"question": "test"})

    assert response.status_code == 200
    assert response.json()["insight"] == ""


def test_query_endpoint_returns_503_when_llm_fails_during_sql_generation():
    client = TestClient(app)

    with patch(
        "app.api.query.generate_sql", side_effect=LLMClientError("API key missing")
    ):
        response = client.post("/api/query", json={"question": "test"})

    assert response.status_code == 503
    assert "LLM failure" in response.json()["detail"]


def test_query_endpoint_returns_400_when_sql_validation_fails():
    client = TestClient(app)

    with patch(
        "app.api.query.generate_sql",
        side_effect=SQLValidationError("Only SELECT allowed"),
    ):
        response = client.post("/api/query", json={"question": "test"})

    assert response.status_code == 400
    assert "Invalid SQL" in response.json()["detail"]


def test_query_endpoint_returns_500_when_sql_execution_fails():
    client = TestClient(app)

    with (
        patch("app.api.query.generate_sql", return_value="SELECT * FROM orders"),
        patch(
            "app.api.query.execute_sql",
            side_effect=SQLExecutionError("Connection refused"),
        ),
    ):
        response = client.post("/api/query", json={"question": "test"})

    assert response.status_code == 500
    assert "SQL execution failed" in response.json()["detail"]
