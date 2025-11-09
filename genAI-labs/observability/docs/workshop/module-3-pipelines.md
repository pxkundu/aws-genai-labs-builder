# Module 3 – Telemetry Pipelines & Infrastructure

**Duration:** 120 minutes  
**Objective:** Deploy enterprise observability infrastructure with Terraform and validate telemetry flow.

## Agenda

1. **Infrastructure Overview (15 min)**
   - Terraform modules (ADOT collector, AMP, Grafana, CloudWatch, OpenSearch)
   - Network architecture & security controls

2. **Hands-On Deployment (75 min)**
   - Configure `infrastructure/terraform/variables.tf`
   - Deploy telemetry stack with Terraform
   - Provision Grafana workspace and AMP data source
   - Configure ADOT Collector (ECS/Fargate or EC2) via Terraform modules

3. **Validation (30 min)**
   - Confirm OTLP ingestion (CloudWatch/X-Ray dashboards)
   - Load Grafana dashboards (`resources/dashboards/cloudwatch-dashboard.json`)
   - Verify alerts triggered for simulated errors

## Lab Commands

```bash
cd genAI-labs/observability/infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply -var="environment=dev"
```

## Verification Checklist

- [ ] CloudWatch log groups/metrics created (`/aws/observability/genai-service`).
- [ ] AWS X-Ray service map displays `genai-observability-service`.
- [ ] AMP workspace provisioned; Grafana data source configured.
- [ ] Lambda alert enrichment function deployed (if `enable_ai_ops = true`).
- [ ] OpenSearch domain accessible (VPC/SG rules verified).

## Troubleshooting

- Use `terraform output` to retrieve resource ARNs.
- Check ADOT collector logs for exporter failures.
- Ensure Bedrock access for AI Ops Lambda role (`iam-policy-bedrock.json`).
