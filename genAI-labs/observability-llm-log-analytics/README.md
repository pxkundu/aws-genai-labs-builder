# 🛰️ LLM Log Analytics & Intelligent Monitoring POC

## Overview

This proof-of-concept demonstrates an enterprise-grade observability solution that combines traditional telemetry pipelines with Large Language Models (LLMs) for intelligent log analytics, proactive monitoring, and AI-assisted operations. The POC is designed to run on AWS and leverages Amazon Bedrock (Claude), Amazon OpenSearch Service, Amazon CloudWatch, and event-driven automation for smart alerting.

## Key Capabilities

- **LLM Log Insights** – Summarize, cluster, and explain log anomalies using Amazon Bedrock (Claude 3.5).
- **Unified Observability Data Lake** – Stream application logs via Kinesis Firehose to Amazon OpenSearch Service and S3.
- **Intelligent Dashboard UI** – React dashboard with conversational analytics, interactive timelines, and remediation recommendations.
- **Smart Alerting** – EventBridge + Lambda automation automatically triages CloudWatch alarms and enriches incidents with LLM summaries.
- **Enterprise Controls** – Encryption, IAM least privilege, audit logging, policy-as-code, and FinOps/AI risk guardrails.

## Architecture

| Layer | Components |
|-------|------------|
| Ingestion | AWS Distro for OpenTelemetry Collector, Amazon Kinesis Data Firehose |
| Storage & Search | Amazon OpenSearch Service (managed cluster), Amazon S3 for archival |
| Analytics | Amazon Bedrock (Claude), Amazon CloudWatch Logs Insights, AWS Glue |
| Automation | Amazon EventBridge, AWS Lambda, AWS Step Functions |
| UI | Next.js dashboard with Bedrock conversational widgets |

Detailed architecture diagrams and data flows are in `docs/architecture.md`.

## Folder Structure

```
observability-llm-log-analytics/
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── bedrock_client.py
│   │   ├── opensearch_client.py
│   │   └── schemas.py
│   ├── requirements.txt
│   └── tests/
│       └── test_bedrock_analysis.py
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.tsx
│       └── components/LogInsightPanel.tsx
├── docs/
│   ├── architecture.md
│   ├── deployment-guide.md
│   └── llm-prompts.md
├── infra/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── cdk/
│       └── README.md
├── resources/
│   └── datasets/
│       └── sample_logs.jsonl
├── scripts/
│   ├── bootstrap.sh
│   └── deploy_terraform.sh
└── config/
    └── env.example
```

## Solution Highlights

- **AI-driven Insights**: Backend service orchestrates log retrieval from OpenSearch, performs aggregation, and submits context-aware prompts to Claude for summarization and remediation suggestions.
- **Smart Alert Pipeline**: CloudWatch alarms publish to EventBridge, which triggers a Lambda function that collects related logs, generates a natural-language summary via Bedrock, and sends enriched alerts to Slack / Opsgenie.
- **FinOps & Compliance**: LLM prompts constrained via guardrails; logs filtered for PII, redacted before analysis; cost monitoring metrics exported to CloudWatch.

## Deployment Steps

1. **Clone repo & install tooling**: Terraform ≥ 1.5, AWS CLI v2, Node.js 18, Python 3.11.
2. **Configure environment variables** using `config/env.example`.
3. **Deploy infrastructure**: `scripts/deploy_terraform.sh` (creates OpenSearch, Kinesis Firehose, Lambda, EventBridge, Bedrock permissions).
4. **Start backend**: `uvicorn backend.app.main:app --reload`.
5. **Start frontend**: `npm install && npm run dev` inside `frontend`.
6. **Send sample logs**: Use sample dataset or integrate with existing OTel pipeline.

## Smart Alert Workflow

1. Metrics/log anomalies trigger CloudWatch alarm.
2. EventBridge routes event to `llm-alert-processor` Lambda.
3. Lambda retrieves related logs from OpenSearch, crafts Bedrock prompt, receives summary.
4. Summary and remediation steps posted to Slack & ticketing system (ServiceNow/Jira integration hooks).

## Extensibility

- **Model Choice**: Swap Amazon Bedrock Claude for custom fine-tuned LLM or third-party via LangChain.
- **Data Sources**: Add support for container logs (EKS), application traces, or SIEM feeds.
- **Multi-tenant**: Tag-based access control with AWS Lake Formation & OpenSearch Index-level security.

## Security Considerations

- IAM scoped to minimum required (OpenSearch read-only for Lambda, Bedrock invocation permissions).
- Logs encrypted at rest (KMS), TLS in transit (OpenSearch, Bedrock).
- Prompt payload redaction of sensitive fields before LLM calls.
- Audit logging via CloudTrail, Config rules for drift detection.

## Next Steps

- Implement chaos testing scenarios to validate alerting fidelity.
- Integrate with ServiceNow or PagerDuty for enterprise ticketing.
- Extend UI with time-travel queries and RCA knowledge base.

For full operational guidance, see `docs/deployment-guide.md` and `docs/llm-prompts.md`.
