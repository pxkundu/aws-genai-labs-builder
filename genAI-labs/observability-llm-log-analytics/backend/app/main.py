"""FastAPI backend for LLM-based log analytics."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List

import structlog
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from . import bedrock_client, opensearch_client, schemas

logger = structlog.get_logger()

def get_settings() -> Dict[str, Any]:
    return {
        "environment": os.getenv("ENVIRONMENT", "dev"),
        "service_name": os.getenv("SERVICE_NAME", "llm-log-analytics-api"),
    }

app = FastAPI(title="LLM Log Analytics API", version="0.1.0")


def build_prompt(logs: List[Dict[str, Any]], insight_request: schemas.InsightRequest) -> str:
    snippet = json.dumps(logs[:20], indent=2)
    return (
        f"Analyze the following logs between {insight_request.start_time} and {insight_request.end_time}.\n"
        f"Filters: {insight_request.filters.model_dump()}\n"
        f"Question: {insight_request.question or 'Provide incident summary.'}\n"
        f"Logs:\n{snippet}"
    )


@app.post("/api/insights/query", response_model=schemas.InsightResponse)
async def query_insights(
    request: schemas.InsightRequest,
    settings: Dict[str, Any] = Depends(get_settings),
) -> schemas.InsightResponse:
    query = {
        "bool": {
            "must": [
                {"range": {"@timestamp": {"gte": request.start_time.isoformat(), "lte": request.end_time.isoformat()}}}
            ],
            "filter": [],
        }
    }
    if request.filters.service:
        query["bool"]["filter"].append({"term": {"service": request.filters.service}})
    if request.filters.severity:
        query["bool"]["filter"].append({"term": {"severity": request.filters.severity}})
    if request.filters.keywords:
        query["bool"]["must"].append({"query_string": {"query": " OR ".join(request.filters.keywords)}})

    logs = opensearch_client.fetch_logs(query)
    if not logs:
        raise HTTPException(status_code=404, detail="No logs found for the specified window")

    prompt = build_prompt(logs, request)
    logger.info("bedrock.request", log_count=len(logs))
    bedrock_response = bedrock_client.analyze_logs(
        prompt,
        {
            "system_prompt": "You are a senior SRE assisting with incident response."
        },
    )
    try:
        content = bedrock_response["content"][0]["text"]  # anthropic response format
        parsed = json.loads(content)
    except Exception as exc:  # pragma: no cover
        logger.error("bedrock.parse_error", error=str(exc))
        raise HTTPException(status_code=500, detail="Failed to parse Bedrock response")

    return schemas.InsightResponse(
        summary=parsed.get("summary", ""),
        cause=parsed.get("cause", ""),
        remediation=parsed.get("remediation", []),
        severity=parsed.get("severity", "Unknown"),
        follow_up_queries=parsed.get("follow_up_queries", []),
        raw_logs=logs[:20],
    )


@app.post("/api/alerts/enrich", response_model=schemas.AlertResponse)
async def enrich_alert(payload: schemas.AlertPayload) -> schemas.AlertResponse:
    alarm_name = payload.alarm_name
    detail = payload.detail

    query = {
        "bool": {
            "must": [{"range": {"@timestamp": {"gte": "now-15m", "lte": "now"}}}],
            "filter": [{"term": {"alarm": alarm_name}}],
        }
    }
    logs = opensearch_client.fetch_logs(query, size=50)

    prompt = json.dumps(
        {
            "alarm": detail,
            "logs": logs,
        },
        indent=2,
    )
    bedrock_response = bedrock_client.analyze_logs(
        prompt,
        {"system_prompt": "Create an incident summary for Slack."},
    )
    try:
        text = bedrock_response["content"][0]["text"]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Bedrock error: {exc}")

    return schemas.AlertResponse(
        markdown=text,
        severity=detail.get("severity", "Unknown"),
        dashboard_links=[detail.get("dashboard_link", "")],
    )


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "timestamp": datetime.utcnow().isoformat()})
