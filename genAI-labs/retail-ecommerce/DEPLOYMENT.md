# Retail & E-commerce AI Solution - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Retail & E-commerce AI Solution on AWS. The deployment supports both development and production environments with infrastructure as code using Terraform and AWS CDK.

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
  - Amazon Rekognition
  - Amazon Kinesis
  - Amazon DynamoDB
  - Amazon S3
  - Amazon ElastiCache
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
cd genAI-labs/retail-ecommerce
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
DYNAMODB_TABLE_PREFIX=retail-ecommerce
S3_BUCKET_PREFIX=retail-ecommerce
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

# Test personalization endpoint
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/recommendations \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user", "context": {"page_type": "homepage"}}'
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
- Security Groups
- Route Tables

#### 2. Data Storage

```bash
# Deploy data storage
cd infrastructure/terraform/modules/storage
terraform apply
```

**Components Created**:
- DynamoDB tables (users, products, transactions, inventory)
- S3 buckets (product images, data lake, content)
- ElastiCache Redis cluster
- OpenSearch domain

#### 3. AI Services Configuration

```bash
# Configure Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Request model access (if needed)
aws bedrock put-model-invocation-logging-configuration \
  --logging-config file://config/bedrock-logging.json
```

#### 4. Lambda Functions

```bash
# Package and deploy Lambda functions
./scripts/deploy-lambdas.sh --environment development

# Or deploy individually
cd backend/lambda
zip -r personalization-engine.zip .
aws lambda update-function-code \
  --function-name retail-personalization-engine \
  --zip-file fileb://personalization-engine.zip
```

**Lambda Functions**:
- `personalization-engine`: Real-time recommendations
- `inventory-forecaster`: Demand forecasting
- `content-generator`: AI content generation
- `conversational-commerce`: Chat assistant
- `event-processor`: Kinesis stream processing

#### 5. API Gateway

```bash
# Deploy API Gateway
cd infrastructure/terraform/modules/api
terraform apply

# Or using CDK
cd infrastructure/cdk
cdk deploy RetailApiStack
```

#### 6. Kinesis Streams

```bash
# Create Kinesis streams
aws kinesis create-stream \
  --stream-name retail-user-events \
  --shard-count 2

aws kinesis create-stream \
  --stream-name retail-product-events \
  --shard-count 1
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

#### 2. Frontend Application

```bash
# Deploy frontend
cd frontend
npm install
npm run build

# Deploy to S3 + CloudFront
aws s3 sync dist/ s3://your-frontend-bucket/
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

### Configuration Management

#### Environment-Specific Configuration

**Development** (`config/environments/development.env`):
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CACHE_TTL=300
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

**Production** (`config/environments/production.env`):
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
CACHE_TTL=3600
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
ENABLE_MONITORING=true
```

#### Secrets Management

```bash
# Store secrets in AWS Secrets Manager
aws secrets-manager create-secret \
  --name retail-ecommerce/api-keys \
  --secret-string '{"openai_key": "your-key", "stripe_key": "your-key"}'

# Retrieve secrets in application
aws secrets-manager get-secret-value \
  --secret-id retail-ecommerce/api-keys
```

## Production Deployment

### Pre-Production Checklist

- [ ] All tests passing
- [ ] Security scan completed
- [ ] Performance testing completed
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
aws dynamodb create-backup \
  --table-name retail-users \
  --backup-name pre-migration-backup-$(date +%Y%m%d)

# Run migrations
python scripts/migrate-database.py --environment production
```

#### 3. Canary Deployment

```bash
# Deploy canary version (10% traffic)
./scripts/deploy-canary.sh --traffic-percent 10

# Monitor metrics
./scripts/monitor-deployment.sh

# Gradually increase traffic
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
  --function-name retail-personalization-engine \
  --payload '{"test": true}' \
  response.json

# Database connectivity
aws dynamodb describe-table --table-name retail-users
```

### Performance Testing

```bash
# Run load tests
npm run load-test -- --target https://api.example.com

# Monitor CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=retail-personalization-engine \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Average,Maximum
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
  --function-name retail-personalization-engine \
  --timeout 30

# Check CloudWatch logs
aws logs tail /aws/lambda/retail-personalization-engine --follow
```

#### 3. DynamoDB Throttling

```bash
# Enable auto-scaling
aws application-autoscaling register-scalable-target \
  --service-namespace dynamodb \
  --scalable-dimension dynamodb:table:WriteCapacityUnits \
  --resource-id table/retail-users \
  --min-capacity 5 \
  --max-capacity 100
```

#### 4. Kinesis Stream Issues

```bash
# Check stream status
aws kinesis describe-stream --stream-name retail-user-events

# Increase shard count if needed
aws kinesis update-shard-count \
  --stream-name retail-user-events \
  --target-shard-count 4 \
  --scaling-type UNIFORM_SCALING
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
  --function-name retail-personalization-engine \
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
  --target-table-name retail-users-restored \
  --backup-arn arn:aws:dynamodb:us-east-1:ACCOUNT:table/retail-users/backup/BACKUP_ID
```

## Cleanup

### Development Environment

```bash
# Destroy infrastructure
cd infrastructure/terraform
terraform destroy

# Delete S3 buckets
aws s3 rb s3://retail-ecommerce-dev --force

# Delete CloudWatch log groups
aws logs delete-log-group --log-group-name /aws/lambda/retail-personalization-engine
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
- [Troubleshooting Guide](./docs/troubleshooting.md)

### AWS Resources

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Amazon SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)

### Getting Help

- GitHub Issues: Report bugs and request features
- AWS Support: For AWS service-specific issues
- Community Forums: For general questions

---

**Ready to deploy? Start with the [Quick Start](#quick-start-deployment) section! 🚀**

