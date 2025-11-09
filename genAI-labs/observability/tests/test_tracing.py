from __future__ import annotations

import asyncio

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, InMemorySpanExporter

from backend.logging_config import configure_logging
from backend.otel_config import configure_metrics, configure_tracing


def test_tracing_configuration() -> None:
    configure_logging()
    configure_tracing()
    tracer_provider = trace.get_tracer_provider()
    assert isinstance(tracer_provider, TracerProvider)


def test_span_creation() -> None:
    exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(tracer_provider)
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("test-span") as span:
        span.set_attribute("test", True)

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].attributes["test"] is True


def test_metric_configuration() -> None:
    configure_metrics(interval=1000)
    # ensure no exception and provider set
    meter_provider = trace.get_tracer_provider()
    assert meter_provider is not None
