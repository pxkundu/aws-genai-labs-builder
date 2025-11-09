"""Structured logging example using structlog and OpenTelemetry context."""

from __future__ import annotations

import asyncio
import structlog
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from logging_config import configure_logging

configure_logging()

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
logger = structlog.get_logger()


async def main() -> None:
    with tracer.start_as_current_span("sample_operation") as span:
        span.set_attribute("component", "sample-code")
        structlog.contextvars.bind_contextvars(trace_id=span.get_span_context().trace_id)
        logger.info("operation.started", detail="Structured logging demo")
        await asyncio.sleep(0.1)
        logger.info("operation.completed", result="success")


if __name__ == "__main__":
    asyncio.run(main())
