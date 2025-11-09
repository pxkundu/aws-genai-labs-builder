# Observability Maturity Model for GenAI Platforms

| Level | Name | Characteristics | KPIs |
|-------|------|-----------------|------|
| L0 | **Telemetry Ad-Hoc** | Minimal logs, no tracing, manual incident response, no AI observability. | MTTR > 4h, no SLOs, unknown token cost |
| L1 | **Instrumented** | Structured logs, basic metrics, manual dashboards, limited tracing coverage. | MTTR 2-4h, initial SLOs, partial trace coverage |
| L2 | **Managed** | Full OpenTelemetry coverage, automated dashboards/alerts, GenAI metrics, AI prompt redaction. | MTTR < 1h, SLO compliance > 95%, trace coverage > 80% |
| L3 | **Intelligent** | AI-assisted diagnostics (Claude), proactive anomaly detection, automated runbooks, FinOps integration. | MTTR < 30m, SLO compliance > 99%, cost per prompt optimized |
| L4 | **Autonomous** | Closed-loop remediation, predictive analytics, multi-cloud observability, governance automation. | MTTR < 10m, zero toil, cost anomaly detection < 5m |

## Assessment Dimensions

1. **Instrumentation Coverage** – % services with OpenTelemetry, custom GenAI metrics.
2. **Telemetry Governance** – Schema validation, data residency, retention policies.
3. **Analytics & Dashboards** – Grafana/QuickSight coverage, SLO dashboards, executive KPIs.
4. **Automation & AI Ops** – Event-driven runbooks, Bedrock-assisted diagnostics, ChatOps integration.
5. **Compliance & Risk** – Alignment with SOC2/ISO, audit trail completeness, toxic content monitoring.
6. **FinOps** – Token usage tracking, cost per prompt, anomaly detection, optimization recommendations.

## Maturity Roadmap

- **Quick Wins** (L0→L1): Enable JSON logging, integrate OTLP exporter, deploy prebuilt dashboards.
- **Phase 2** (L1→L2): Implement tracing, SLOs, automated alerts, Claude prompt metadata instrumentation.
- **Phase 3** (L2→L3): Deploy Bedrock summarization of incidents, integrate ServiceNow/Jira, FinOps dashboards.
- **Phase 4** (L3→L4): Tail-based sampling, predictive maintenance, self-healing via Step Functions.

## Benchmarking Checklist

- [ ] Telemetry coverage report reviewed monthly.
- [ ] Incident postmortem template populated with trace + log links.
- [ ] SLO burn rate alerts tested quarterly.
- [ ] Compliance evidence stored in secured S3 bucket.
- [ ] Claude AI Ops prompts validated for hallucination risk.
