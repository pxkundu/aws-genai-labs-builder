"""Prometheus metrics export example for GenAI workloads."""

from __future__ import annotations

import random
import time
from contextlib import contextmanager

from prometheus_client import Counter, Histogram, start_http_server

PROMPT_COUNTER = Counter(
    "genai_sample_prompt_total",
    "Total prompts processed in sample exporter",
)
PROMPT_LATENCY = Histogram(
    "genai_sample_prompt_latency_seconds",
    "Prompt latency distribution",
    buckets=(0.1, 0.2, 0.5, 1, 2, 3),
)


@contextmanager
def prompt_timer():
    start = time.perf_counter()
    yield
    duration = time.perf_counter() - start
    PROMPT_LATENCY.observe(duration)


def process_prompt() -> None:
    with prompt_timer():
        time.sleep(random.uniform(0.1, 0.8))
        PROMPT_COUNTER.inc()


def main() -> None:
    start_http_server(9100)
    print("Prometheus exporter running on :9100/metrics")
    while True:
        process_prompt()


if __name__ == "__main__":
    main()
