from __future__ import annotations

import asyncio
import os
import time
from typing import Any, Dict

import boto3
import structlog
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Span

from logging_config import configure_logging
from otel_config import configure_metrics, configure_tracing

configure_logging()
configure_tracing()
configure_metrics()

LoggingInstrumentor().instrument(set_logging_format=True)

logger = structlog.get_logger()

SERVICE_NAME = os.getenv("SERVICE_NAME", "genai-observability-service")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3 haiku")

app = FastAPI(title="GenAI Observability Lab", version="1.0.0")
FastAPIInstrumentor.instrument_app(app, excluded_urls="/health")

meter = metrics.get_meter_provider().get_meter("genai.observability", "1.0.0")
prompt_counter = meter.create_counter(
    "genai_prompt_total",
    description="Total number of prompts processed",
)
prompt_latency_histogram = meter.create_histogram(
    "genai_prompt_latency_ms",
    description="Prompt latency in milliseconds",
)
prompt_cost_counter = meter.create_counter(
    "genai_prompt_cost_usd",
    description="Cost in USD per prompt",
)


async def bedrock_client() -> boto3.client:
    session = boto3.session.Session(region_name=AWS_REGION)
    return session.client("bedrock-runtime")


async def set_context(request: Request) -> Dict[str, Any]:
    trace_id = trace.format_trace_id(trace.get_current_span().get_span_context().trace_id)
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        trace_id=trace_id,
        path=request.url.path,
        method=request.method,
    )
    return {"trace_id": trace_id}


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME, "environment": ENVIRONMENT}


@app.post("/prompts")
async def generate_prompt(
    payload: Dict[str, Any],
    request_context: Dict[str, Any] = Depends(set_context),
    client: boto3.client = Depends(bedrock_client),
) -> JSONResponse:
    start_time = time.perf_counter()
    span: Span = trace.get_current_span()
    span.set_attribute("genai.prompt.type", payload.get("type", "text"))
    span.set_attribute("genai.model", BEDROCK_MODEL_ID)

    logger.info("prompt.received", payload=payload)

    # Simulate Bedrock invocation
    try:
        await asyncio.sleep(0.2)
        # Example: client.invoke_model(...)
        response = {
            "completion": "Claude response placeholder",
            "usage": {"input_tokens": 200, "output_tokens": 180},
        }
    except Exception as exc:  # pragma: no cover - network errors
        span.record_exception(exc)
        span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, str(exc)))
        logger.error("prompt.failed", error=str(exc))
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    prompt_counter.add(1, attributes={"prompt_type": payload.get("type", "text")})
    prompt_latency_histogram.record(duration_ms)
    cost_usd = payload.get("estimated_cost", 0.002)
    prompt_cost_counter.add(cost_usd)

    logger.info(
        "prompt.completed",
        latency_ms=duration_ms,
        cost_usd=cost_usd,
        usage=response["usage"],
    )

    return JSONResponse(
        status_code=200,
        content={
            "trace_id": request_context["trace_id"],
            "response": response,
            "latency_ms": duration_ms,
            "cost_usd": cost_usd,
        },
    )


@app.get("/traces/{trace_id}")
async def get_trace(trace_id: str) -> Dict[str, Any]:
    logger.info("trace.lookup", trace_id=trace_id)
    return {"trace_id": trace_id, "status": "lookup_placeholder"}


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("service.startup", service=SERVICE_NAME, environment=ENVIRONMENT)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("service.shutdown", service=SERVICE_NAME)
