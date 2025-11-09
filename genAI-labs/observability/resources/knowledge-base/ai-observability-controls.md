# AI Observability Controls & Metrics

## Control Objectives

1. **Transparency** – Provide traceability for every prompt/response, including model, version, and applied guardrails.
2. **Reliability** – Monitor latency, error rates, drift, and prompt retries (NIST AI RMF).
3. **Safety** – Detect toxicity, PII leakage, hallucinations using automated classifiers.
4. **Accountability** – Maintain audit logs, approvals, and incident tracebacks (EU AI Act obligations).
5. **FinOps** – Track cost per prompt, token usage, and budget adherence.

## Metrics Catalog

| Category | Metric | Description |
|----------|--------|-------------|
| Latency | `genai_prompt_latency_ms` | End-to-end latency per prompt, exported via OpenTelemetry histogram |
| Quality | `genai_prompt_toxicity_score` | Score from content moderation pipeline |
| Cost | `genai_prompt_cost_usd` | Cost per prompt calculated from token usage & pricing |
| Reliability | `genai_prompt_error_total` | Count of failed prompts (timeouts, guardrail blocks) |
| Drift | `genai_prompt_topic_distribution` | Jensen-Shannon divergence comparing prompt topics over time |

## Controls Implementation

- **Instrumentation**: `backend/main.py` binds metrics and log attributes to every prompt lifecycle event.
- **Tracing**: Spans include `genai.model`, `genai.prompt.length`, `genai.guardrail.status` attributes.
- **Logging**: Structured logs capture detection results, classification outcomes, redaction flags.
- **Dashboards**: Grafana panels show SLO compliance, toxicity trends, cost burn-down.
- **Alerting**: CloudWatch alarms trigger when toxicity score > threshold or cost anomalies detected.
- **AI Guardrails**: Integrate Amazon Bedrock Guardrails or custom moderation workflows.

## Compliance References

- NIST AI Risk Management Framework (RMF) – Govern, Map, Measure, Manage functions.
- EU AI Act Articles 12-15 – Record-keeping, transparency, human oversight.
- ISO/IEC 42001 – AI management system controls.

## Automation Patterns

1. EventBridge rule triggers Lambda when `genai_prompt_error_total` spikes.
2. Lambda aggregates context, queries Claude for root cause summary, posts to Slack.
3. Step Functions orchestrate remediation runbooks (restart service, roll back model).
4. FinOps pipeline sends daily cost anomaly report to QuickSight.

## Validation Checklist

- [ ] Prompt telemetry sampled and stored for at least 90 days.
- [ ] Toxicity classifier integrated (AWS Comprehend or third-party).
- [ ] Data residency controls configured via Terraform variables.
- [ ] Access to observability data audited (CloudTrail, IAM Access Analyzer).
- [ ] AI incident playbooks reviewed quarterly.
