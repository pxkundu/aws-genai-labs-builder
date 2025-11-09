# Deployment Guide

## Prerequisites

- AWS account with permissions for IAM, CloudWatch, Kinesis, OpenSearch, Bedrock, Lambda, EventBridge, S3.
- Terraform ≥ 1.5, AWS CLI v2, Python 3.11, Node.js 18.
- Access to Amazon Bedrock in target region (model ID defaults to Claude 3.5 Sonnet).
- Docker (optional) for local OpenTelemetry collector.

## Step 1 – Configure Environment

```bash
cd genAI-labs/observability-llm-log-analytics
cp config/env.example .env
# update AWS credentials, Bedrock model ID, OpenSearch endpoint, Slack webhook, etc.
```

## Step 2 – Deploy Infrastructure

```bash
cd infra/terraform
cp ../../config/templates/terraform.tfvars.example terraform.tfvars
terraform init
terraform apply -var="environment=dev"
```

Resources provisioned:
- OpenSearch domain with fine-grained access.
- Kinesis Firehose + CloudWatch Logs.
- Lambda functions (LLM summarizer, alert enricher).
- EventBridge rules, SNS topics, IAM roles.
- S3 buckets for archival and static assets.

## Step 3 – Seed Sample Logs (Optional)

```bash
aws firehose put-record-batch \
  --delivery-stream-name llm-log-stream \
  --records fileb://../../resources/datasets/sample_logs.jsonl
```

## Step 4 – Launch Backend API

```bash
cd ../../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API Endpoints:
- `POST /api/insights/query` – LLM summary for time range / filters.
- `GET /api/alerts/recent` – Latest smart alerts with remediation suggestions.
- `POST /api/feedback` – Capture analyst feedback for continuous improvement.

## Step 5 – Launch Frontend Dashboard

```bash
cd ../frontend
npm install
npm run dev
```

Dashboard features:
- Conversational log analysis panel (Claude-powered)
- KPI widgets (latency, error rate, anomaly scores)
- Alert timeline with remediation actions and runbook links

## Step 6 – Configure ChatOps (Optional)

Update `config/env.example` with Slack webhook or Opsgenie API key. Lambda uses these values to deliver enriched alerts.

## Step 7 – Validate Smart Alert Flow

1. Trigger synthetic error or anomaly (provided script `scripts/trigger_anomaly.py`).
2. Confirm EventBridge rule fired, Lambda executed, Bedrock summary generated.
3. Verify Slack/Opsgenie/Ticket receives enriched alert.

## Cleanup

```bash
cd infra/terraform
terraform destroy
```

Revoke API keys and rotate secrets after completing the POC.
