"""OpenTelemetry tracing example with nested spans."""

from __future__ import annotations

import time

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

resource = Resource.create({"service.name": "observability-tracing-sample"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)


def handle_prompt(prompt: str) -> str:
    time.sleep(0.05)
    return prompt.upper()


def process_request(prompt: str) -> str:
    with tracer.start_as_current_span("process_request") as span:
        span.set_attribute("prompt.length", len(prompt))
        span.set_attribute("prompt.preview", prompt[:20])
        with tracer.start_as_current_span("call_model") as child:
            child.set_attribute("model", "claude-3-sonnet")
            response = handle_prompt(prompt)
        return response


if __name__ == "__main__":
    result = process_request("Observability makes GenAI reliable")
    print(result)
