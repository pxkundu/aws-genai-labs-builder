from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.main.opensearch_client.fetch_logs")
@patch("app.main.bedrock_client.analyze_logs")
def test_query_insights(mock_bedrock, mock_fetch_logs):
    mock_fetch_logs.return_value = [{"message": "error", "severity": "ERROR"}]
    mock_bedrock.return_value = {
        "content": [
            {
                "text": "{\"summary\": \"All good\", \"cause\": \"Test\", \"remediation\": [\"Fix\"], \"severity\": \"Low\"}"
            }
        ]
    }

    payload = {
        "start_time": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
        "end_time": datetime.utcnow().isoformat(),
        "filters": {},
        "question": "What happened?",
    }
    response = client.post("/api/insights/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "Low"
    assert data["remediation"] == ["Fix"]


@patch("app.main.opensearch_client.fetch_logs", return_value=[{"alarm": "HighLatency"}])
@patch("app.main.bedrock_client.analyze_logs")
def test_alert_enrich(mock_bedrock, _mock_logs):
    mock_bedrock.return_value = {"content": [{"text": "**Summary**\n- Issue"}]}
    payload = {
        "alarm_name": "HighLatency",
        "state": "ALARM",
        "detail": {"severity": "High", "dashboard_link": "https://example"},
    }
    response = client.post("/api/alerts/enrich", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Summary" in data["markdown"]
    assert data["severity"] == "High"
