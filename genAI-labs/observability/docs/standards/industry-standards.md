# Observability Industry Standards & Frameworks

| Domain | Standard / Framework | Relevance |
|--------|----------------------|-----------|
| Observability | **OpenTelemetry (CNCF)** | Vendor-neutral instrumentation for traces, metrics, logs. Adopt SDK v1.24; follow semantic conventions for GenAI workloads (`genai.*`). |
| Logging | **CNCF Observability Framework** | Defines maturity levels (L0-L3) for log pipelines, schema, governance. |
| Security | **SOC 2 CC7.2**, **ISO/IEC 27001 A.12.4** | Requires continuous monitoring, logging, incident alerting, retention policies. |
| Cloud | **AWS Well-Architected Framework – Operations Excellence & Reliability Pillars** | Key design principles: observability, automation, incident response, testing. |
| FinTech | **FINRA Rule 4370**, **PCI DSS 12.10** | Incident response, log monitoring requirements for regulated industries. |
| Public Sector | **NIST 800-53 rev5 (AU, IR, CP families)** | Mandatory controls for federal workloads; map controls to Terraform modules. |

## Implementation Guidance

1. **OpenTelemetry**
   - Adopt semantic conventions for HTTP, messaging, databases, AI operations.
   - Enforce resource attributes (`service.name`, `deployment.environment`).
   - Use OTLP exporters with TLS + auth (mTLS or SigV4).

2. **Logging Compliance**
   - Structured JSON logs with signed digests (tamper detection via AWS CloudTrail).
   - Retention: 30 days hot, 1 year warm, 7 years archive (tune per regulation).
   - Audit trail access recorded via CloudTrail and integrated with IAM Access Analyzer.

3. **Metrics & SLOs**
   - Implement RED + USE + business KPIs.
   - Define SLOs with burn-rate alerts (multi-window, multi-burn rate as per SRE books).
   - Align with ITIL/ITSM for incident lifecycle.

4. **Tracing**
   - 100% sampling in non-prod; adaptive sampling in prod (1-10%) with tail-based sampling for critical errors.
   - Mask prompt payloads to remain compliant with GDPR/CCPA.

5. **AI Observability**
   - Track token usage, latency, toxicity scores, and prompt drift metrics.
   - Align with **NIST AI RMF**, **EU AI Act** risk classifications (documented in `resources/knowledge-base/ai-observability-controls.md`).

6. **Automation**
   - Use Infrastructure as Code (Terraform) with policy-as-code (AWS Config, HashiCorp Sentinel) to enforce observability standards.
   - Set up CI/CD checks for telemetry schema changes, SLO definitions, dashboard configuration.

## Certification & Audit Checklist

- [ ] OpenTelemetry instrumentation coverage report generated (`tests/test_tracing.py`).
- [ ] CloudWatch metrics mapped to business KPIs.
- [ ] Incident runbooks reviewed quarterly.
- [ ] Access reviews for observability tooling (Grafana, AMP) performed monthly.
- [ ] Evidence packs exported (log samples, alarm history, incident reports).
