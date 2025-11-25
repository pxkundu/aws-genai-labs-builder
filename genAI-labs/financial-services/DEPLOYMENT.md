# Financial Services AI Solution - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Financial Services AI Solution on AWS. The deployment supports both development and production environments with infrastructure as code using Terraform and AWS CDK, with a focus on security and regulatory compliance.

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
  - Amazon Comprehend
  - AWS Fraud Detector
  - Amazon Textract
  - Amazon Kinesis
  - Amazon DynamoDB
  - Amazon S3
  - AWS KMS
  - Amazon API Gateway
  - AWS Lambda
  - Amazon EventBridge
  - Amazon CloudWatch
  - AWS CloudTrail
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
cd genAI-labs/financial-services
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
DYNAMODB_TABLE_PREFIX=financial-services-dev
S3_BUCKET_PREFIX=financial-services-dev
KMS_KEY_ALIAS=financial-services-key
VPC_ID=vpc-xxxxxxxxx
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

# Test fraud detection endpoint
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/fraud-detection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "transaction_id": "test-txn-1",
    "amount": 1000.00,
    "merchant": "test-merchant",
    "customer_id": "test-customer-1"
  }'
```

## Detailed Deployment Steps

### Infrastructure Deployment

#### 1. VPC and Networking

```bash
# Deploy VPC infrastructure
cd infrastructure/terraform/modules/networking
terraform init
terraform apply
```

**Components Created**:
- VPC with public and private subnets
- Internet Gateway
- NAT Gateway
- Security Groups (strict rules)
- Route Tables
- VPC Endpoints for AWS services

#### 2. KMS Keys for Encryption

```bash
# Create KMS key for encryption
aws kms create-key \
  --description "Financial Services Encryption Key" \
  --key-usage ENCRYPT_DECRYPT \
  --key-spec SYMMETRIC_DEFAULT

# Create alias
aws kms create-alias \
  --alias-name alias/financial-services-key \
  --target-key-id <key-id>
```

#### 3. Data Storage

```bash
# Deploy data storage
cd infrastructure/terraform/modules/storage
terraform apply
```

**Components Created**:
- DynamoDB tables (transactions, customers, risk_data, fraud_events) with encryption
- S3 buckets (data lake, audit logs) with encryption and versioning
- ElastiCache Redis cluster (if needed)
- OpenSearch domain (if needed)

#### 4. AI Services Configuration

```bash
# Configure Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Request model access (if needed)
aws bedrock put-model-invocation-logging-configuration \
  --logging-config file://config/bedrock-logging.json

# Create Fraud Detector model
aws frauddetector create-model \
  --model-id transaction-fraud-detector \
  --event-type-name transaction \
  --model-type ONLINE_FRAUD_INSIGHTS
```

#### 5. Lambda Functions

```bash
# Package and deploy Lambda functions
./scripts/deploy-lambdas.sh --environment development

# Or deploy individually
cd backend/lambda
zip -r fraud-detection.zip .
aws lambda update-function-code \
  --function-name financial-fraud-detection \
  --zip-file fileb://fraud-detection.zip
```

**Lambda Functions**:
- `fraud-detection`: Real-time fraud analysis
- `risk-assessment`: Credit risk evaluation
- `investment-research`: Financial analysis
- `customer-advisory`: Financial planning
- `event-processor`: Kinesis stream processing
- `audit-logger`: Compliance logging

#### 6. API Gateway

```bash
# Deploy API Gateway
cd infrastructure/terraform/modules/api
terraform apply

# Or using CDK
cd infrastructure/cdk
cdk deploy FinancialApiStack
```

#### 7. Kinesis Streams

```bash
# Create Kinesis stream for transactions
aws kinesis create-stream \
  --stream-name financial-transactions \
  --shard-count 5

# Create stream for events
aws kinesis create-stream \
  --stream-name financial-events \
  --shard-count 2
```

#### 8. CloudTrail for Audit

```bash
# Create CloudTrail
aws cloudtrail create-trail \
  --name financial-services-audit \
  --s3-bucket-name financial-services-audit-logs \
  --include-global-service-events \
  --is-multi-region-trail

# Start logging
aws cloudtrail start-logging \
  --name financial-services-audit
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

#### 2. Fraud Detector Model Training

```bash
# Train fraud detection model
python scripts/train-fraud-model.py \
  --training-data s3://financial-services-data/training/fraud-data.csv \
  --model-name transaction-fraud-detector
```

### Configuration Management

#### Environment-Specific Configuration

**Development** (`config/environments/development.env`):
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
FRAUD_THRESHOLD=0.7
ENABLE_AUDIT=true
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

**Production** (`config/environments/production.env`):
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
FRAUD_THRESHOLD=0.8
ENABLE_AUDIT=true
ENABLE_COMPLIANCE_CHECKS=true
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
ENABLE_MONITORING=true
```

#### Secrets Management

```bash
# Store secrets in AWS Secrets Manager
aws secrets-manager create-secret \
  --name financial-services/api-keys \
  --secret-string '{"fraud_api_key": "your-key", "external_api_key": "your-key"}'

# Retrieve secrets in application
aws secrets-manager get-secret-value \
  --secret-id financial-services/api-keys
```

## Production Deployment

### Pre-Production Checklist

- [ ] All tests passing
- [ ] Security scan completed
- [ ] Compliance review completed
- [ ] Performance testing completed
- [ ] Backup strategy configured
- [ ] Monitoring and alerting set up
- [ ] Disaster recovery plan documented
- [ ] Cost optimization reviewed
- [ ] Documentation updated
- [ ] Audit logging verified

### Production Deployment Steps

#### 1. Blue-Green Deployment

```bash
# Deploy to staging environment first
./scripts/deploy.sh --environment staging

# Run compliance tests
./scripts/compliance-tests.sh --environment staging

# Run security tests
./scripts/security-tests.sh --environment staging

# Deploy to production
./scripts/deploy.sh --environment production --blue-green
```

#### 2. Database Migration

```bash
# Backup production database
aws dynamodb create-backup \
  --table-name financial-transactions \
  --backup-name pre-migration-backup-$(date +%Y%m%d)

# Run migrations
python scripts/migrate-database.py --environment production
```

#### 3. Canary Deployment

```bash
# Deploy canary version (5% traffic)
./scripts/deploy-canary.sh --traffic-percent 5

# Monitor metrics
./scripts/monitor-deployment.sh

# Gradually increase traffic
./scripts/increase-canary-traffic.sh --percent 10
./scripts/increase-canary-traffic.sh --percent 25
./scripts/increase-canary-traffic.sh --percent 50
./scripts/increase-canary-traffic.sh --percent 100
```

## Monitoring and Validation

### Health Checks

```bash
# API health check
curl https://api.example.com/health

# Lambda function health
aws lambda invoke \
  --function-name financial-fraud-detection \
  --payload '{"test": true}' \
  response.json

# Database connectivity
aws dynamodb describe-table --table-name financial-transactions
```

### Performance Testing

```bash
# Run load tests
npm run load-test -- --target https://api.example.com

# Monitor CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=financial-fraud-detection \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Average,Maximum
```

### Compliance Validation

```bash
# Run compliance checks
./scripts/compliance-check.sh

# Verify audit logging
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=PutItem \
  --max-results 10

# Check encryption
aws dynamodb describe-table \
  --table-name financial-transactions \
  --query 'Table.SSEDescription'
```

### Cost Monitoring

```bash
# Check current costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Set up cost alerts
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://config/budget.json
```

## Troubleshooting

### Common Issues

#### 1. Bedrock Access Denied

```bash
# Verify model access
aws bedrock list-foundation-models --region us-east-1

# Request access if needed
# Go to AWS Console > Bedrock > Model Access
```

#### 2. Lambda Timeout

```bash
# Increase timeout
aws lambda update-function-configuration \
  --function-name financial-fraud-detection \
  --timeout 30

# Check CloudWatch logs
aws logs tail /aws/lambda/financial-fraud-detection --follow
```

#### 3. DynamoDB Throttling

```bash
# Enable auto-scaling
aws application-autoscaling register-scalable-target \
  --service-namespace dynamodb \
  --scalable-dimension dynamodb:table:WriteCapacityUnits \
  --resource-id table/financial-transactions \
  --min-capacity 10 \
  --max-capacity 100
```

#### 4. Kinesis Stream Issues

```bash
# Check stream status
aws kinesis describe-stream --stream-name financial-transactions

# Increase shard count if needed
aws kinesis update-shard-count \
  --stream-name financial-transactions \
  --target-shard-count 10 \
  --scaling-type UNIFORM_SCALING
```

#### 5. Fraud Detector Model Issues

```bash
# Check model status
aws frauddetector describe-model-versions \
  --model-id transaction-fraud-detector

# Retrain model if needed
python scripts/train-fraud-model.py --retrain
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
  --function-name financial-fraud-detection \
  --zip-file fileb://previous-version.zip

# Rollback API Gateway
aws apigateway create-deployment \
  --rest-api-id YOUR_API_ID \
  --stage-name previous
```

### Database Rollback

```bash
# Restore from backup
aws dynamodb restore-table-from-backup \
  --target-table-name financial-transactions-restored \
  --backup-arn arn:aws:dynamodb:us-east-1:ACCOUNT:table/financial-transactions/backup/BACKUP_ID
```

## Cleanup

### Development Environment

```bash
# Destroy infrastructure
cd infrastructure/terraform
terraform destroy

# Delete S3 buckets
aws s3 rb s3://financial-services-dev --force

# Delete CloudWatch log groups
aws logs delete-log-group --log-group-name /aws/lambda/financial-fraud-detection
```

### Production Environment

⚠️ **Warning**: Only run cleanup after proper backup and verification

```bash
# Backup all data first
./scripts/backup-all.sh

# Verify backups
./scripts/verify-backups.sh

# Destroy infrastructure (with caution)
terraform destroy -var="environment=production"
```

## Best Practices

### Security

1. **Never commit secrets**: Use AWS Secrets Manager
2. **Enable encryption**: All data encrypted at rest and in transit
3. **Least privilege**: IAM roles with minimal required permissions
4. **Regular audits**: Review access logs and permissions quarterly
5. **MFA required**: Multi-factor authentication for all admin access

### Compliance

1. **Audit logging**: Enable CloudTrail for all actions
2. **Data retention**: Follow regulatory requirements
3. **Access controls**: Implement role-based access control
4. **Regular reviews**: Quarterly compliance audits
5. **Documentation**: Maintain compliance documentation

### Performance

1. **Caching**: Implement multi-layer caching strategy
2. **Connection pooling**: Reuse database connections
3. **Async processing**: Use async operations for non-blocking tasks
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
- [Compliance Guide](./docs/compliance.md)
- [Troubleshooting Guide](./docs/troubleshooting.md)

### AWS Resources

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Fraud Detector Documentation](https://docs.aws.amazon.com/frauddetector/)
- [Amazon SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)

### Getting Help

- GitHub Issues: Report bugs and request features
- AWS Support: For AWS service-specific issues
- Community Forums: For general questions

---

**Ready to deploy? Start with the [Quick Start](#quick-start-deployment) section! 🚀**

