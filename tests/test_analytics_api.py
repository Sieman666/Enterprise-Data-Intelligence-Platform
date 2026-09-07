from unittest.mock import patch

from app.main import app
from fastapi.testclient import TestClient


def test_read_kpis_endpoint_returns_report():
    client = TestClient(app)
    mock_report = {
        "revenue": 12345.67,
        "order_count": 100,
        "average_order_value": 123.46,
        "customer_count": 50,
        "purchase_conversion_rate": 0.1234,
        "purchase_events": 10,
        "behavior_sessions": 80,
    }

    with patch("app.api.analytics.get_kpi_report", return_value=mock_report):
        response = client.get("/api/analytics/kpis")

    assert response.status_code == 200
    assert response.json() == mock_report


def test_read_trends_endpoint_returns_report():
    client = TestClient(app)
    mock_report = {
        "monthly_sales_trend": [
            {"month": "2024-01", "monthly_revenue": 1000.0, "monthly_order_count": 10},
        ],
    }

    with patch("app.api.analytics.get_trend_report", return_value=mock_report):
        response = client.get("/api/analytics/trends")

    assert response.status_code == 200
    assert response.json() == mock_report


def test_read_profile_endpoint_returns_report():
    client = TestClient(app)
    mock_report = {
        "customers": {
            "profile": {"rows": 10},
            "numeric_statistics": {},
            "categorical_statistics": {},
        },
        "products": {
            "profile": {"rows": 10},
            "numeric_statistics": {},
            "categorical_statistics": {},
        },
        "orders": {
            "profile": {"rows": 10},
            "numeric_statistics": {},
            "categorical_statistics": {},
        },
        "user_behavior": {
            "profile": {"rows": 10},
            "numeric_statistics": {},
            "categorical_statistics": {},
        },
    }

    with patch("app.api.analytics.get_profile_report", return_value=mock_report):
        response = client.get("/api/analytics/profile")

    assert response.status_code == 200
    assert response.json() == mock_report
