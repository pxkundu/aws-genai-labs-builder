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

- **Terraform IaC** in `infrastructure/terraform` – Complete infrastructure as code with modular design
- **Step-by-step workshop** in `docs/workshop.md` – Detailed hands-on labs with commands and troubleshooting
- **Architecture documentation** in `docs/architecture.md` – Comprehensive architecture with Mermaid diagrams
- **Device simulator** in `scripts/device_simulator.py` – Python script to simulate IoT devices
- **Helper scripts** in `scripts/` – Deployment, testing, and infrastructure validation
- **Code examples** in `code/` – Lambda functions, SQL queries, and integration patterns
- **Sample data** in `data/` – Sample telemetry payloads for testing
- **CI/CD workflows** in `.github/workflows/` – Automated Terraform validation and deployment

## Quick start

### Prerequisites

- Terraform >= 1.5
- AWS CLI v2 configured with an account and region
- Python 3.8+ (for device simulator)
- jq (for JSON processing)

### Bootstrap Infrastructure

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars to set project_name, region, and enable/disable optional services
terraform init
terraform apply -auto-approve
```

### Simulate Device

```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Get IoT endpoint
IOT_ENDPOINT=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text)

# Run device simulator
python scripts/device_simulator.py \
  --endpoint $IOT_ENDPOINT \
  --cert deviceCert.pem \
  --key privateKey.pem \
  --root-ca AmazonRootCA1.pem \
  --thing-name my-device-001 \
  --device-type temperature_sensor \
  --interval 5
```

### Test Infrastructure

```bash
# Run infrastructure validation tests
./scripts/test_infrastructure.sh
```

## Contents

### Documentation

- **`docs/architecture.md`** – High-level and detailed architecture with Mermaid diagrams broken down by component
- **`docs/workshop.md`** – Step-by-step labs covering device provisioning, shadow, rules, analytics, events, defender, and observability
- **`docs/cost-estimation.md`** – Detailed cost breakdown and optimization tips
- **`docs/security-best-practices.md`** – Security guidelines and best practices
- **`docs/integrations.md`** – Integration examples with other AWS services and third-party tools

### Infrastructure

- **`infrastructure/terraform/`** – Composable Terraform modules:
  - `modules/iot-core/` – IoT Core resources (policies, rules, thing types, fleet provisioning)
  - `modules/streaming/` – Kinesis Data Streams, Firehose, S3 data lake
  - `modules/lambda-processor/` – Lambda function for data processing
  - `modules/analytics/` – IoT Analytics (channel, pipeline, datastore, dataset)
  - `modules/events/` – IoT Events (input, detector model)
  - `modules/defender/` – Device Defender security profiles
  - `modules/monitoring/` – CloudWatch dashboards and alarms

### Code Examples

- **`code/lambda_functions/`**:
  - `enrichment_processor.py` – Enhanced Lambda with anomaly detection and enrichment
  - `analytics_queries.sql` – Sample SQL queries for IoT Analytics

### Scripts

- **`scripts/device_simulator.py`** – Python device simulator supporting multiple device types
- **`scripts/deploy.sh`** – Infrastructure deployment helper
- **`scripts/destroy.sh`** – Infrastructure cleanup helper
- **`scripts/test_infrastructure.sh`** – Infrastructure validation and testing

### Data

- **`data/sample_telemetry.json`** – Sample telemetry payloads for testing

### CI/CD

- **`.github/workflows/terraform-ci.yml`** – GitHub Actions workflow for Terraform validation and deployment

## Features

### Core Capabilities

✅ **Device Management** – Thing registry, thing types, fleet provisioning  
✅ **Secure Connectivity** – X.509 certificates, IoT policies, TLS 1.2+  
✅ **Data Ingestion** – MQTT over TLS, device shadows, topic rules  
✅ **Streaming** – Kinesis Data Streams for real-time processing  
✅ **Data Lake** – S3 via Firehose for durable storage  
✅ **Processing** – Lambda functions for enrichment and transformation  
✅ **Analytics** – IoT Analytics for time-series SQL queries  
✅ **Event Detection** – IoT Events for stateful event processing  
✅ **Security** – Device Defender for fleet posture monitoring  
✅ **Observability** – CloudWatch dashboards, metrics, and alarms  

### Advanced Features

✅ **Device Simulator** – Python-based simulator with multiple device types  
✅ **Anomaly Detection** – Built-in threshold-based anomaly detection  
✅ **Integration Examples** – 15+ AWS service integration patterns  
✅ **Cost Optimization** – Detailed cost breakdown and optimization tips  
✅ **Security Best Practices** – Comprehensive security guidelines  
✅ **CI/CD Integration** – GitHub Actions workflows  
✅ **Testing Tools** – Infrastructure validation scripts  

## Costs

This stack provisions multiple managed services that may incur charges. See `docs/cost-estimation.md` for detailed cost breakdown:

- **Small scale (1-10 devices)**: ~$15-20/month
- **Medium scale (100 devices)**: ~$32-35/month
- **Large scale (1,000 devices)**: ~$144-150/month

**Always destroy resources when not in use:**
```bash
cd infrastructure/terraform
terraform destroy -auto-approve
```

## Next Steps

1. **Deploy Infrastructure** – Follow the quick start guide above
2. **Run Workshop** – Complete the step-by-step labs in `docs/workshop.md`
3. **Explore Architecture** – Review `docs/architecture.md` for detailed diagrams
4. **Simulate Devices** – Use `scripts/device_simulator.py` to generate test data
5. **Integrate Services** – Explore `docs/integrations.md` for integration patterns
6. **Optimize Costs** – Review `docs/cost-estimation.md` for optimization tips
7. **Secure Deployment** – Follow `docs/security-best-practices.md` guidelines

## Support

For issues, questions, or contributions, please refer to the main repository documentation.


