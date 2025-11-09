# Observability Lab Workshop

This workshop guides teams through implementing end-to-end observability, logging, and monitoring for GenAI applications on AWS.

## Workshop Structure

| Module | Focus | Duration |
|--------|-------|----------|
| 1 | Observability Foundations & Standards | 60 min |
| 2 | Application Instrumentation (Logs, Metrics, Traces) | 90 min |
| 3 | Telemetry Pipelines & Infrastructure | 120 min |
| 4 | Analytics, AI Ops & Incident Response | 90 min |

Estimated total time: **6 hours**.

## Learning Outcomes

- Understand industry standards (OpenTelemetry, AWS Well-Architected) and compliance mappings.
- Instrument GenAI services with structured logging and OpenTelemetry.
- Deploy observability infrastructure with Terraform (CloudWatch, X-Ray, AMP, Grafana, OpenSearch).
- Build dashboards, alerts, and AI-assisted incident response workflows.

## Prerequisites

- AWS account with permissions for observability services.
- Terraform ≥ 1.5, Python 3.11, Docker (optional for local collector).
- Access to Amazon Bedrock (Claude models).

## Workshop Assets

- `module-1-foundations.md` – Slide deck outline, hands-on checks.
- `module-2-instrumentation.md` – Coding labs for logging, metrics, tracing.
- `module-3-pipelines.md` – Terraform deployment & validation tasks.
- `module-4-analytics.md` – Dashboard creation, AI Ops workflows.

Participants clone the repository, follow module instructions, and use the provided scripts/configurations to deploy and validate the observability stack.
