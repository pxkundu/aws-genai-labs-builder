"""OpenTelemetry configuration for the observability lab."""

from __future__ import annotations

import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

SERVICE_NAME = os.getenv("SERVICE_NAME", "genai-observability-service")
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEPLOYMENT_VERSION = os.getenv("DEPLOYMENT_VERSION", "v0.1.0")


def configure_tracing() -> None:
    resource = Resource.create(
        {
            "service.name": SERVICE_NAME,
            "service.namespace": "genai-labs",
            "service.version": DEPLOYMENT_VERSION,
            "deployment.environment": ENVIRONMENT,
        }
    )

    trace_provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter(endpoint=f"{OTLP_ENDPOINT}/v1/traces")
    span_processor = BatchSpanProcessor(span_exporter)
    trace_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(trace_provider)


def configure_metrics(interval: Optional[int] = 60000) -> None:
    resource = Resource.create(
        {
            "service.name": SERVICE_NAME,
            "service.namespace": "genai-labs",
            "deployment.environment": ENVIRONMENT,
        }
    )

    exporter = OTLPMetricExporter(endpoint=f"{OTLP_ENDPOINT}/v1/metrics")
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=interval)
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    # For compatibility with instrumentation packages
    from opentelemetry import metrics  # type: ignore

    metrics.set_meter_provider(meter_provider)
