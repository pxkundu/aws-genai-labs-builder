# AWS IoT End-to-End Workshop

An end-to-end AWS IoT reference implementation with Terraform that provisions a complete workflow:

- AWS IoT Core (registry, policy, thing type, fleet provisioning template, device shadow, topic rules)
- Data ingestion and storage (Amazon Kinesis Data Streams, Amazon Kinesis Data Firehose, Amazon S3)
- Real-time processing (AWS Lambda)
- Time-series analytics (AWS IoT Analytics)
- Event detection and response (AWS IoT Events)
- Security and fleet posture (AWS IoT Device Defender)
- Optional search and visualization (Amazon OpenSearch Service)
- Observability (Amazon CloudWatch, AWS CloudTrail, AWS X-Ray)

This workshop provides:

- Terraform IaC in `infrastructure/terraform`
- Step-by-step workshop in `docs/workshop.md`
- Architecture deep dive in `docs/architecture.md`
- Helper scripts in `scripts/`

## Quick start

Prerequisites:

- Terraform >= 1.5
- AWS CLI v2 configured with an account and region
- jq

Bootstrap:

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars to set project_name, region, and enable/disable optional services
terraform init
terraform apply -auto-approve
```

Next steps:

- Follow the hands-on flow in `docs/workshop.md` to simulate devices, publish telemetry, see data flow, run analytics and events, and review security posture.

## Contents

- `docs/architecture.md` – High-level and detailed architecture with simplified Mermaid diagrams
- `docs/workshop.md` – Step-by-step labs (device provisioning, shadow, rules, analytics, events, defender)
- `infrastructure/terraform` – Composable Terraform modules and environment entrypoint
- `scripts/` – Helper deploy/destroy and device simulation snippets

## Costs

This stack provisions multiple managed services that may incur charges. Use the provided `scripts/destroy.sh` to remove resources after use.


