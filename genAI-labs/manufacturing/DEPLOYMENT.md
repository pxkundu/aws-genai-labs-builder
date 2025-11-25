# Manufacturing AI Solution - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Manufacturing AI Solution on AWS. The deployment supports both development and production environments with infrastructure as code using Terraform and AWS CDK, with a focus on IoT integration and real-time processing.

## Prerequisites

### Required Tools

- **AWS CLI** (v2.0+): [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **Terraform** (v1.5+): [Installation Guide](https://developer.hashicorp.com/terraform/downloads)
- **Python** (3.11+): [Download Python](https://www.python.org/downloads/)
- **Node.js** (18+): [Download Node.js](https://nodejs.org/)
- **Docker** (optional, for local development): [Install Docker](https://docs.docker.com/get-docker/)
- **Git**: [Install Git](https://git-scm.com/downloads)

### AWS Account Requirements

- AWS Account with admin access
- Access to the following AWS services:
  - Amazon Bedrock (with model access enabled)
  - Amazon SageMaker
  - Amazon Rekognition
  - Amazon Lookout for Equipment
  - Amazon Comprehend
  - Amazon Forecast
  - AWS IoT Core
  - Amazon Timestream
  - Amazon Kinesis
  - Amazon DynamoDB
  - Amazon S3
  - Amazon API Gateway
  - AWS Lambda
  - Amazon EventBridge
  - Amazon CloudWatch
  - AWS IAM
  - Amazon VPC

### AWS CLI Configuration

```bash
# Configure AWS CLI
aws configure

# Verify configuration
aws sts get-caller-identity

# Set default region
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
```

## Quick Start Deployment

### 1. Clone Repository

```bash
git clone <repository-url>
cd genAI-labs/manufacturing
```

### 2. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Terraform providers (if using Terraform)
cd infrastructure/terraform
terraform init
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp config/environments/development.env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

**Required Environment Variables**:
```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id
ENVIRONMENT=development
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
DYNAMODB_TABLE_PREFIX=manufacturing-dev
S3_BUCKET_PREFIX=manufacturing-dev
TIMESTREAM_DB_NAME=manufacturing-sensors
```

### 4. Deploy Infrastructure

#### Option A: Using Terraform (Recommended)

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review deployment plan
terraform plan

# Deploy infrastructure
terraform apply

# Save outputs
terraform output -json > ../../config/infrastructure-outputs.json
```

#### Option B: Using AWS CDK

```bash
cd infrastructure/cdk

# Install CDK dependencies
npm install

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy stack
cdk deploy --all
```

### 5. Deploy Application Code

```bash
# Deploy Lambda functions
./scripts/deploy-lambdas.sh

# Deploy API Gateway
./scripts/deploy-api.sh

# Load sample data
python scripts/load-sample-data.py
```

### 6. Verify Deployment

```bash
# Check API health
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/health

# Test maintenance endpoint
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/maintenance \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "EQ-001",
    "sensor_data": {
      "temperature": 75.5,
      "vibration": 2.3,
      "pressure": 10.2
    }
  }'
```

## Detailed Deployment Steps

### Infrastructure Deployment

#### 1. IoT Core Setup

```bash
# Create IoT thing group
aws iot create-thing-group \
  --thing-group-name ManufacturingEquipment \
  --thing-group-properties thingGroupDescription="Manufacturing equipment group"

# Create IoT policy
aws iot create-policy \
  --policy-name ManufacturingDevicePolicy \
  --policy-document file://config/iot-policy.json

# Create thing type
aws iot create-thing-type \
  --thing-type-name ManufacturingSensor \
  --thing-type-properties thingTypeDescription="Manufacturing sensor device"
```

#### 2. Timestream Database

```bash
# Create Timestream database
aws timestream-write create-database \
  --database-name manufacturing-sensors \
  --region us-east-1

# Create table for sensor data
aws timestream-write create-table \
  --database-name manufacturing-sensors \
  --table-name equipment-sensors \
  --retention-properties MemoryStoreRetentionPeriodInHours=24,MagneticStoreRetentionPeriodInDays=365 \
  --region us-east-1
```

#### 3. Kinesis Streams

```bash
# Create stream for image data
aws kinesis create-stream \
  --stream-name manufacturing-images \
  --shard-count 5 \
  --region us-east-1

# Create stream for process data
aws kinesis create-stream \
  --stream-name manufacturing-process \
  --shard-count 3 \
  --region us-east-1
```

#### 4. Lookout for Equipment

```bash
# Create Lookout for Equipment dataset
aws lookout-equipment create-dataset \
  --dataset-name manufacturing-equipment \
  --dataset-schema file://config/lookout-schema.json

# Import training data
aws lookout-equipment import-dataset \
  --dataset-name manufacturing-equipment \
  --input-data-config file://config/lookout-input-config.json
```

#### 5. Lambda Functions

```bash
# Package and deploy Lambda functions
./scripts/deploy-lambdas.sh --environment development

# Or deploy individually
cd backend/lambda
zip -r predictive-maintenance.zip .
aws lambda update-function-code \
  --function-name manufacturing-predictive-maintenance \
  --zip-file fileb://predictive-maintenance.zip
```

**Lambda Functions**:
- `predictive-maintenance`: Equipment failure prediction
- `quality-control`: Visual inspection and defect detection
- `process-optimization`: Manufacturing process optimization
- `safety-monitoring`: Safety violation detection
- `supply-chain`: Demand forecasting and inventory
- `event-processor`: Kinesis stream processing

#### 6. API Gateway

```bash
# Deploy API Gateway
cd infrastructure/terraform/modules/api
terraform apply

# Or using CDK
cd infrastructure/cdk
cdk deploy ManufacturingApiStack
```

### Application Deployment

#### 1. Backend Services

```bash
# Deploy backend API
cd backend
pip install -r requirements.txt

# Run database migrations
python scripts/migrate-database.py

# Start API server (development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. IoT Device Configuration

```bash
# Register IoT device
aws iot create-thing \
  --thing-name sensor-001 \
  --thing-type-name ManufacturingSensor

# Create device certificate
aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile device-cert.pem \
  --public-key-outfile device-public-key.pem \
  --private-key-outfile device-private-key.pem

# Attach policy to certificate
aws iot attach-policy \
  --policy-name ManufacturingDevicePolicy \
  --target <certificate-arn>
```

### Configuration Management

#### Environment-Specific Configuration

**Development** (`config/environments/development.env`):
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
MAINTENANCE_THRESHOLD=0.7
QUALITY_THRESHOLD=0.95
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

**Production** (`config/environments/production.env`):
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
MAINTENANCE_THRESHOLD=0.8
QUALITY_THRESHOLD=0.98
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
ENABLE_MONITORING=true
```

## Production Deployment

### Pre-Production Checklist

- [ ] All tests passing
- [ ] Security scan completed
- [ ] Performance testing completed
- [ ] IoT device connectivity verified
- [ ] Backup strategy configured
- [ ] Monitoring and alerting set up
- [ ] Disaster recovery plan documented
- [ ] Cost optimization reviewed
- [ ] Documentation updated

### Production Deployment Steps

#### 1. Blue-Green Deployment

```bash
# Deploy to staging environment first
./scripts/deploy.sh --environment staging

# Run smoke tests
./scripts/smoke-tests.sh --environment staging

# Deploy to production
./scripts/deploy.sh --environment production --blue-green
```

#### 2. Database Migration

```bash
# Backup production database
aws timestream-write describe-database \
  --database-name manufacturing-sensors

# Run migrations
python scripts/migrate-database.py --environment production
```

## Monitoring and Validation

### Health Checks

```bash
# API health check
curl https://api.example.com/health

# Lambda function health
aws lambda invoke \
  --function-name manufacturing-predictive-maintenance \
  --payload '{"test": true}' \
  response.json

# IoT Core connectivity
aws iot describe-endpoint --endpoint-type iot:Data-ATS
```

### Performance Testing

```bash
# Run load tests
npm run load-test -- --target https://api.example.com

# Monitor CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=manufacturing-predictive-maintenance \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Average,Maximum
```

### IoT Device Testing

```bash
# Test IoT device connection
python scripts/test-iot-device.py \
  --thing-name sensor-001 \
  --certificate device-cert.pem \
  --private-key device-private-key.pem

# Verify data ingestion
aws timestream-query query \
  --query-string "SELECT * FROM manufacturing-sensors.equipment-sensors LIMIT 10"
```

## Troubleshooting

### Common Issues

#### 1. IoT Device Connection Issues

```bash
# Check IoT policy
aws iot get-policy --policy-name ManufacturingDevicePolicy

# Verify certificate
aws iot describe-certificate --certificate-id <cert-id>

# Check thing registration
aws iot describe-thing --thing-name sensor-001
```

#### 2. Timestream Write Issues

```bash
# Check database and table
aws timestream-write describe-database --database-name manufacturing-sensors
aws timestream-write describe-table --database-name manufacturing-sensors --table-name equipment-sensors

# Verify IAM permissions
aws iam get-role-policy --role-name TimestreamWriteRole --policy-name TimestreamAccess
```

#### 3. Lambda Timeout

```bash
# Increase timeout
aws lambda update-function-configuration \
  --function-name manufacturing-predictive-maintenance \
  --timeout 60

# Check CloudWatch logs
aws logs tail /aws/lambda/manufacturing-predictive-maintenance --follow
```

#### 4. Lookout for Equipment Issues

```bash
# Check dataset status
aws lookout-equipment describe-dataset --dataset-name manufacturing-equipment

# Check model training status
aws lookout-equipment describe-model --model-name manufacturing-model
```

## Rollback Procedures

### Infrastructure Rollback

```bash
# Rollback Terraform changes
cd infrastructure/terraform
terraform plan -out=previous.tfplan
terraform apply previous.tfplan
```

### Application Rollback

```bash
# Rollback Lambda function
aws lambda update-function-code \
  --function-name manufacturing-predictive-maintenance \
  --zip-file fileb://previous-version.zip
```

## Cleanup

### Development Environment

```bash
# Destroy infrastructure
cd infrastructure/terraform
terraform destroy

# Delete S3 buckets
aws s3 rb s3://manufacturing-dev --force

# Delete Timestream database
aws timestream-write delete-database --database-name manufacturing-sensors
```

## Best Practices

### Security

1. **Never commit secrets**: Use AWS Secrets Manager
2. **Enable encryption**: All data encrypted at rest and in transit
3. **Least privilege**: IAM roles with minimal required permissions
4. **Regular audits**: Review access logs and permissions quarterly

### Performance

1. **Optimize Lambda**: Use appropriate memory and timeout settings
2. **Batch processing**: Process data in batches for efficiency
3. **Caching**: Implement caching for frequently accessed data
4. **Monitoring**: Set up comprehensive monitoring and alerting

### Cost Optimization

1. **Right-sizing**: Use appropriate instance types
2. **Reserved capacity**: For predictable workloads
3. **Auto-scaling**: Scale down during low-traffic periods
4. **Cost alerts**: Set up budget alerts

## Support and Resources

### Documentation

- [Architecture Guide](./architecture.md)
- [API Documentation](./docs/api/)
- [Workshop Guide](./docs/workshop/)
- [Troubleshooting Guide](./docs/troubleshooting.md)

### AWS Resources

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS IoT Core Documentation](https://docs.aws.amazon.com/iot/)
- [Amazon Lookout for Equipment](https://docs.aws.amazon.com/lookout-for-equipment/)
- [Amazon Timestream Documentation](https://docs.aws.amazon.com/timestream/)

### Getting Help

- GitHub Issues: Report bugs and request features
- AWS Support: For AWS service-specific issues
- Community Forums: For general questions

---

**Ready to deploy? Start with the [Quick Start](#quick-start-deployment) section! 🚀**

