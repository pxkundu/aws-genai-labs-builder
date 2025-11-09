# Observability Terraform Stack

This Terraform configuration provisions the observability platform for the GenAI lab.

## Components

- CloudWatch Log Group (JSON logs, retention, KMS optional)
- AWS X-Ray group (Insights enabled)
- Amazon Managed Service for Prometheus (AMP)
- Amazon Managed Grafana workspace (with API key)
- CloudWatch dashboard and latency alarm
- SNS topic for alert fan-out
- Optional AI Ops Lambda workflow (Claude summaries)

## Prerequisites

- Terraform ≥ 1.5
- AWS CLI configured with sufficient permissions
- Lambda package for AI Ops workflow (optional)
- KMS key ARN (optional)

## Usage

```bash
cd genAI-labs/observability/infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply -var="environment=dev"
```

> Disable AI Ops workflow by setting `enable_ai_ops = false` in `terraform.tfvars`.

## Important Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | Deployment region | `us-east-1` |
| `environment` | Environment name | `dev` |
| `prompt_latency_threshold_ms` | Alarm threshold | `1500` |
| `ai_ops_lambda_role_arn` | IAM role for AI Ops Lambda | `""` |
| `security_lambda_arn` | Destination for log subscription | `""` |

## Outputs

| Output | Description |
|--------|-------------|
| `log_group_name` | CloudWatch log group name |
| `xray_group_name` | X-Ray group name |
| `amp_workspace_id` | Prometheus workspace ID |
| `grafana_workspace_id` | Grafana workspace ID |
| `grafana_api_key` | API key (sensitive) |
| `alerts_topic_arn` | SNS topic ARN |

## Cleanup

```bash
terraform destroy
```

Ensure the Grafana API key is rotated or deleted after workshop completion.
