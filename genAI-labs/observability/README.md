# 🔍 Observability, Logging & Monitoring Lab

## Overview

This lab delivers an enterprise-ready observability reference implementation for GenAI workloads on AWS. It demonstrates how to instrument applications, capture high-fidelity telemetry (logs, metrics, traces), and build actionable insights with dashboards, alerting, and AI-assisted operations. The lab aligns with the AWS Well-Architected Framework and industry standards such as OpenTelemetry, CNCF Observability Framework, and ISO/IEC 27002 operational monitoring controls.

## Lab Objectives

- Implement distributed tracing, structured logging, and metrics collection with OpenTelemetry
- Centralize telemetry in AWS services (CloudWatch, X-Ray, CloudTrail) and open-source stacks (Prometheus, OpenSearch, Grafana)
- Automate observability infrastructure using Terraform
- Build AI-assisted diagnostics using Amazon Bedrock and Claude
- Operationalize runbooks, SLOs, and incident response workflows

## Architecture Summary

Key components:

- **Application Layer**: FastAPI service with OpenTelemetry SDK, structured logging (JSON), and context propagation
- **Telemetry Pipelines**:
  - OTLP -> AWS Distro for OpenTelemetry Collector -> CloudWatch Logs, CloudWatch Metrics, AWS X-Ray
  - Prometheus remote write to Amazon Managed Service for Prometheus (AMP)
  - Logs replication to Amazon OpenSearch Service (Elastic compatibility) for long-term analytics
- **Analytics & Visualization**:
  - Amazon Managed Grafana dashboards
  - CloudWatch dashboards & alarms
  - Amazon QuickSight for executive KPIs
- **AI Ops**:
  - Amazon Bedrock + Claude 3.5 Sonnet for anomaly summarization & remediation recommendations
  - EventBridge -> Lambda -> Bedrock workflow for intelligent alert enrichment

See `architecture.md` for detailed diagrams and data flows.

## Folder Structure

```
genAI-labs/observability/
├── README.md
├── architecture.md
├── backend/
│   ├── logging_config.py
│   ├── main.py
│   ├── otel_config.py
│   └── requirements.txt
├── docs/
│   ├── knowledge-base/
│   │   ├── industry-standards.md
│   │   └── observability-maturity-model.md
│   └── workshop/
│       ├── README.md
│       ├── module-1-foundations.md
│       ├── module-2-instrumentation.md
│       ├── module-3-pipelines.md
│       └── module-4-analytics.md
├── infrastructure/
│   └── terraform/
│       ├── README.md
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── resources/
│   ├── dashboards/
│   │   └── cloudwatch-dashboard.json
│   └── runbooks/
│       └── incident-response.md
├── scripts/
│   ├── deploy.sh
│   └── cleanup.sh
└── tests/
    └── test_tracing.py
```

## Getting Started

1. **Prerequisites**
   - AWS account with permissions for CloudWatch, X-Ray, AMP, Grafana, Lambda, IAM, S3
   - Terraform ≥ 1.5, Python 3.11, Docker (for local collector)
   - AWS CLI and cdk-aws-otel-asset module access

2. **Setup**
   ```bash
   cd genAI-labs/observability
   python -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   export AWS_REGION=us-east-1
   ```

3. **Deploy Infrastructure**
   ```bash
   cd infrastructure/terraform
   terraform init
   terraform apply -var="environment=dev"
   ```

4. **Run the Instrumented Service**
   ```bash
   cd ../..
   uvicorn backend.main:app --reload
   ```

5. **Explore Dashboards & Alerts**
   - Open CloudWatch dashboard (`resources/dashboards/cloudwatch-dashboard.json`)
   - Access Grafana workspace (AMP datasource preconfigured)
   - Review runbook in `resources/runbooks/incident-response.md`

## Key Features

- **End-to-End Tracing**: Context propagation across synchronous and async operations with Claude prompts embedded in spans
- **Structured Logging**: JSON logs enriched with correlation IDs, user/session metadata, and Bedrock inference results
- **Metrics & KPIs**: RED (Rate, Errors, Duration) + custom GenAI metrics (token usage, prompt latency, cost per request)
- **Alerting**: Multi-channel alerts (SNS, Slack webhook) with Claude-generated summaries
- **Automated Remediation**: EventBridge rules invoking Lambda + Bedrock to suggest fixes and update incident tickets
- **Compliance**: Mapping to SOC 2 CC7.2, ISO/IEC 27001 A.12.4, NIST 800-53 AU-6, and FINRA 4370 supervision guidance

## Workshop Path

A 4-module workshop (approx. 6 hours) covers foundations, instrumentation, pipeline deployment, and analytics. See `docs/workshop/README.md` for agenda and labs.

## Next Steps

- Customize Terraform variables for your environment
- Plug in your existing GenAI workloads by reusing `otel_config.py`
- Extend the AI Ops workflow to integrate with ServiceNow, Jira, PagerDuty
- Benchmark observability maturity using `docs/knowledge-base/observability-maturity-model.md`

## Support & Contributions

- Submit issues or feature requests via GitHub
- Contributions must align with the AWS Well-Architected and OpenTelemetry specifications
- For professional services inquiries contact observability-labs@yourcompany.com
