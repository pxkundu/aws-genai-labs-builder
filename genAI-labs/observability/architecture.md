# Observability Architecture

## High-Level Diagram

```mermaid
graph LR
    subgraph Application Layer
        A[FastAPI GenAI Service]
        B[Claude Prompt Orchestrator]
    end

    subgraph Observability SDK
        C[OpenTelemetry SDK]
        D[Structured Logging (JSON)]
        E[Metrics Middleware]
    end

    subgraph Telemetry Pipeline
        F[AWS Distro for OpenTelemetry Collector]
        G[Prometheus Remote Write]
        H[Firehose -> S3 -> OpenSearch]
    end

    subgraph AWS Native Sinks
        I[CloudWatch Logs]
        J[CloudWatch Metrics]
        K[AWS X-Ray]
    end

    subgraph Analytics & Insights
        L[Amazon Managed Grafana]
        M[Amazon QuickSight]
        N[Amazon Bedrock + Claude]
    end

    subgraph Incident Response
        O[Amazon EventBridge]
        P[AWS Lambda]
        Q[SNS / Slack / PagerDuty]
    end

    A --> C
    B --> C
    C --> D
    C --> E
    C --> F
    F --> I
    F --> J
    F --> K
    F --> G
    G --> L
    H --> L
    H --> M
    I --> N
    J --> N
    L --> N
    N --> O
    O --> P
    P --> Q
```

## Component Breakdown

### Application Layer
- **FastAPI GenAI Service**: Reference application exposing GenAI endpoints (chat completion, embeddings) instrumented with OpenTelemetry
- **Claude Prompt Orchestrator**: Middleware capturing prompt/response metadata, token usage, and cost metrics; provides hooks for redaction

### Observability SDK
- **OpenTelemetry SDK**: Python instrumentation (HTTP, FastAPI, Asyncio, boto3) with context propagation; OTLP exporter
- **Structured Logging**: Logging via `structlog` with JSON format, correlation IDs, and PII redaction rules (GDPR/CCPA compliant)
- **Metrics Middleware**: RED metrics, business KPIs (prompts per minute, Claude cost), SLO calculations

### Telemetry Pipeline
- **AWS Distro for OpenTelemetry (ADOT) Collector**: Runs as sidecar/DaemonSet; receives OTLP, exports to CloudWatch, X-Ray, Prometheus, S3
- **Prometheus Remote Write**: Sends metrics to Amazon Managed Service for Prometheus (AMP)
- **Firehose -> S3 -> OpenSearch**: Long-term log retention, search, ML-based anomaly detection

### AWS Native Sinks
- **CloudWatch Logs**: Centralized logs, subscription filters to Lambda for security analytics
- **CloudWatch Metrics**: Custom namespaces for GenAI metrics, alarm definitions, anomaly detection models
- **AWS X-Ray**: Distributed tracing with service map, upstream/downstream dependencies

### Analytics & Insights
- **Amazon Managed Grafana**: Dashboards for SLO burn rates, token utilization, infrastructure health
- **Amazon QuickSight**: Executive KPIs, cost analytics (FinOps), trend analysis
- **Amazon Bedrock + Claude**: AI Ops copilot summarizing incidents, suggesting remediation, and providing natural language queries over logs/metrics

### Incident Response
- **Amazon EventBridge**: Routing anomalies, CloudWatch alarms, and AI-detected incidents to automation workflows
- **AWS Lambda**: Event enrichment, runbook execution, ticket automation (ServiceNow/Jira integration hooks)
- **SNS / Slack / PagerDuty**: Notifications, escalation policies, ChatOps interactions

## Data Flows

1. **Tracing Flow**
   - FastAPI service emits spans via OTLP -> ADOT Collector -> AWS X-Ray
   - Span attributes include trace IDs, prompt metadata, Claude model IDs, latency, error codes
   - Trace analytics feed into CloudWatch Contributor Insights for anomaly detection

2. **Logging Flow**
   - Application emits JSON logs with schema `{timestamp, level, logger, trace_id, span_id, message, metadata}`
   - Logs stream to CloudWatch; subscription filter sends to Lambda that classifies severity using Claude
   - Optionally archived to S3 with lifecycle policies and indexed in OpenSearch

3. **Metrics Flow**
   - Metrics exported via Prometheus exporter to ADOT Collector -> AMP
   - Custom metrics: `genai_prompt_latency_seconds`, `genai_token_usage_total`, `genai_cost_usd_total`
   - Alerting via CloudWatch Alarms and Prometheus alert manager (hooked to SNS/PagerDuty)

4. **AI Ops Flow**
   - EventBridge triggers Lambda on specific alarms/anomalies
   - Lambda aggregates related telemetry, queries Claude via Bedrock prompt template
   - Claude returns summary, likely cause, remediation steps, and updates ChatOps channel & incident ticket

## Security & Compliance Controls

- **Access Control**: IAM least-privilege policies for collectors, Grafana, X-Ray, Bedrock
- **Encryption**: TLS in transit, KMS at rest for CloudWatch Logs, S3, OpenSearch, AMP
- **Auditability**: CloudTrail enabled, audit logs stored in dedicated S3 bucket with retention policies
- **Data Governance**: PII masking, prompt payload redaction, data residency configuration via Terraform variables
- **Regulatory Mapping**:
  - SOC 2 CC7.2 Monitoring
  - ISO/IEC 27001 A.12.4 Logging & Monitoring
  - NIST 800-53 AU family controls
  - FINRA Rule 4370 Business Continuity Planning

## Deployment Topology

- **Core Services**: Deployed in primary region (default `us-east-1`) with cross-region replication options
- **ADOT Collector**: ECS/Fargate task or EKS DaemonSet
- **Data Stores**: 
  - CloudWatch (regional)
  - AMP/Grafana (managed services)
  - OpenSearch with Multi-AZ deployment
  - S3 with lifecycle policies (Standard -> Glacier Deep Archive)

## Extensibility Patterns

- **Multi-Account Observability**: Use AWS Observability Accelerator or cross-account CloudWatch/AMP access
- **Hybrid / Multi-Cloud**: Leverage OpenTelemetry Collector exporters for Datadog, New Relic, Elastic, Splunk
- **Custom AI Insights**: Extend Claude prompt templates for root cause analysis, RCA documentation automation

## Reference Integrations

- AWS Distro for OpenTelemetry (ADOT) 1.29+
- Amazon Managed Service for Prometheus & Grafana
- AWS X-Ray, CloudWatch Metrics, Logs, Contributor Insights, Synthetics
- Amazon OpenSearch Service (Elastic 8.x compatible)
- AWS Lambda, EventBridge, SNS, Step Functions for automation
- Amazon Bedrock (Claude 3.5 Sonnet, Haiku for cost-effective summarization)

## SLIs, SLOs, and Alerts

- **SLIs**: Request latency (p95), error rate, Claude prompt success rate, token cost per request, inference latency
- **SLOs**: 99% of prompts < 1.5s latency, error rate < 0.5%, cost per prompt < $0.05 USD
- **Alerts**:
  - `prompt_latency_p95 > 1.5s for 5m`
  - `error_rate > 1% for 10m`
  - `daily_cost_usd > budget threshold`
  - `OTLP ingestion failures > 100/min`
  - `Claude anomaly score > 0.8`

## Dependencies & Assumptions

- AWS Organizations for centralized logging optional but recommended
- VPC endpoints for CloudWatch, X-Ray, S3 in private subnets
- Service-linked roles for Grafana, AMP, X-Ray enabled
- Bedrock access approved for target region (model IDs specified in Terraform variable defaults)

## Future Enhancements

- Integrate with ServiceNow/Jira for automatic incident ticket creation
- Add chaos engineering hooks to test observability coverage
- Include FinOps dashboards correlating telemetry with cost and usage reports
- Provide multi-cloud adapters (Azure Monitor, Google Cloud Operations Suite)
