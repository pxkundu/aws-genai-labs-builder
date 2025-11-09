# Module 2 – Application Instrumentation

**Duration:** 90 minutes  
**Objective:** Instrument GenAI services with structured logging, metrics, and distributed tracing.

## Agenda

1. **Review Instrumentation Patterns (10 min)**
   - Logging strategy (`docs/guides/logging-strategy.md`)
   - OpenTelemetry configuration (`backend/otel_config.py`)
   - Metrics & tracing design

2. **Hands-On Lab (65 min)**
   - Configure structured logging (`logging_config.py`)
   - Implement OpenTelemetry tracing & metrics (`main.py`)
   - Add custom GenAI attributes (token usage, latency)
   - Emit sample telemetry via `/prompts` endpoint

3. **Validation (15 min)**
   - Review traces in AWS X-Ray (if available) or local collector
   - Inspect JSON logs
   - Verify metrics with Prometheus client

## Lab Instructions

```bash
cd genAI-labs/observability
uvicorn backend.main:app --reload

# Trigger sample request
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{"type": "chat", "prompt": "How do I build observability?", "estimated_cost": 0.003}'
```

### Expected Output

- JSON log entry printed with correlation IDs.
- `/metrics` endpoint exposes `genai_prompt_total`, `genai_prompt_latency_ms`.
- Trace recorded with attributes `genai.prompt.type`, `genai.model`.

## Success Criteria

- All telemetry types emitted for sample requests.
- Sensitive data redacted from logs.
- Custom metrics visible via Prometheus scrape or OTLP exporter.
