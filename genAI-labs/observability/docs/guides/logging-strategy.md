# Enterprise Logging Strategy

## Purpose

This guide outlines the logging strategy implemented in the Observability Lab. It can be used as a blueprint for enterprise GenAI workloads that require resilient, compliant, and actionable log telemetry.

## Logging Principles

1. **Structured** – All logs emitted in JSON format with consistent schema.
2. **Contextual** – Every log carries correlation identifiers (trace_id, span_id) and business metadata (tenant, workload, Claude model).
3. **Secure** – PII redaction, secrets masking, access controls, encryption in transit/at rest.
4. **Actionable** – Severity levels, standardized event names, remediation hints.
5. **Cost Aware** – Intelligent sampling, aggregation, lifecycle policies.

## Log Schema

| Field | Description | Example |
|-------|-------------|---------|
| `timestamp` | ISO-8601 timestamp (UTC) | `2025-11-08T10:15:31.123Z` |
| `level` | Log level (`DEBUG`..`FATAL`) | `INFO` |
| `service` | Service emitting the log | `genai-observability-service` |
| `environment` | Deployment environment | `production` |
| `trace_id` | W3C trace ID | `4bf92f3577b34da6a3ce929d0e0e4736` |
| `span_id` | W3C span ID | `00f067aa0ba902b7` |
| `message` | Event name | `prompt.completed` |
| `metadata` | Additional context (dict) | `{ "model": "claude-3.5-sonnet" }` |

## Redaction Policy

- Automatic redaction enforced for keys: `authorization`, `api_key`, `password`, `secret`, `ssn`, `credit_card`.
- PII detection via regex patterns executed in `logging_config.py`.
- Optionally integrate AWS Macie / Comprehend PII for advanced detection.

## Log Routing

1. **Primary sink**: CloudWatch Logs (retention 30 days) with KMS encryption.
2. **Analytics sink**: Amazon OpenSearch Service for full-text search, ML anomaly detection.
3. **Long-term archive**: Amazon S3 (Glacier Deep Archive after 365 days).
4. **Security sink**: AWS Security Lake or Splunk via Firehose subscriptions.

## Alerting & Diagnostics

- CloudWatch Metric Filters map log patterns to metrics (e.g., `ERROR` -> `error_count`).
- Bedrock-powered Lambda summarizes spikes, adds root-cause hypotheses.
- Runbooks stored under `resources/runbooks/` detail triage steps.

## Compliance Mapping

| Control Framework | Mapping |
|-------------------|---------|
| SOC 2 CC7.2 | Continuous monitoring, alerting, incident response |
| ISO/IEC 27001 A.12.4 | Event logging, log protection, administrator logs |
| NIST 800-53 AU-6 | Audit review, analysis, reporting |
| FINRA 4370 | Business continuity supervision, incident traceability |

## Implementation Checklist

- [x] JSON logging enabled with structlog.
- [x] Correlation IDs injected via middleware.
- [x] Log sampling rules defined (TRACE/DEBUG in non-prod only).
- [x] Retention policies aligned with compliance requirements.
- [x] Guardrails for log volume and cost monitoring.
- [x] Automated quality checks (linting, schema validation).

## References

- AWS Logging Best Practices (re:Invent 2024, OPN305)
- CNCF Observability Whitepaper
- OpenTelemetry Logging Specification 1.24
- AWS Security Reference Architecture (2025 edition)
