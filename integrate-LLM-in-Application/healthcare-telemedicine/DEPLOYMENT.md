# Healthcare Telemedicine AI - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Healthcare Telemedicine AI Support System on AWS with HIPAA compliance considerations.

## Prerequisites

### Required Tools

```bash
# AWS CLI (v2.0+)
aws --version

# Python (3.11+)
python3 --version

# Node.js (18+)
node --version

# Docker (optional)
docker --version
```

### AWS Account Requirements

- AWS Account with appropriate permissions
- Access to AWS GenAI services:
  - Amazon Bedrock (Claude model access)
  - Amazon Comprehend Medical
  - Amazon Textract
- HIPAA-eligible AWS services enabled

### Enable Bedrock Model Access

```bash
# List available models
aws bedrock list-foundation-models --region us-east-1

# Request access via AWS Console:
# Bedrock > Model Access > Request Access
```

## Quick Start Deployment

### 1. Clone and Setup

```bash
# Navigate to project
cd integrate-LLM-in-Application/healthcare-telemedicine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file:
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# DynamoDB Tables
DYNAMODB_PATIENTS_TABLE=telemedicine-patients
DYNAMODB_SESSIONS_TABLE=telemedicine-sessions
DYNAMODB_ASSESSMENTS_TABLE=telemedicine-assessments

# S3 Buckets
S3_DOCUMENTS_BUCKET=telemedicine-documents-dev

# Security
ENCRYPTION_KEY_ID=alias/telemedicine-key
```

### 3. Deploy Infrastructure

```bash
# Deploy CloudFormation stack
cd infrastructure/cloudformation
aws cloudformation deploy \
  --template-file main.yaml \
  --stack-name telemedicine-ai-dev \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides Environment=development
```

### 4. Run Application

```bash
# Start backend
cd backend
python app.py

# In another terminal, serve frontend
cd frontend
python -m http.server 3000
```

### 5. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Test symptom checker
curl -X POST http://localhost:8000/api/symptoms/assess \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "headache and fever for 2 days"}'
```

## Detailed Deployment Steps

### Phase 1: Foundation Infrastructure

#### 1.1 Create KMS Key

```bash
aws kms create-key \
  --description "Telemedicine encryption key" \
  --key-usage ENCRYPT_DECRYPT \
  --origin AWS_KMS

# Create alias
aws kms create-alias \
  --alias-name alias/telemedicine-key \
  --target-key-id <key-id>
```

#### 1.2 Create DynamoDB Tables

```bash
# Patients table
aws dynamodb create-table \
  --table-name telemedicine-patients \
  --attribute-definitions \
    AttributeName=patient_id,AttributeType=S \
  --key-schema \
    AttributeName=patient_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --sse-specification Enabled=true

# Sessions table
aws dynamodb create-table \
  --table-name telemedicine-sessions \
  --attribute-definitions \
    AttributeName=session_id,AttributeType=S \
    AttributeName=patient_id,AttributeType=S \
  --key-schema \
    AttributeName=session_id,KeyType=HASH \
  --global-secondary-indexes \
    "[{\"IndexName\":\"patient-index\",\"KeySchema\":[{\"AttributeName\":\"patient_id\",\"KeyType\":\"HASH\"}],\"Projection\":{\"ProjectionType\":\"ALL\"}}]" \
  --billing-mode PAY_PER_REQUEST \
  --sse-specification Enabled=true

# Assessments table
aws dynamodb create-table \
  --table-name telemedicine-assessments \
  --attribute-definitions \
    AttributeName=assessment_id,AttributeType=S \
    AttributeName=patient_id,AttributeType=S \
  --key-schema \
    AttributeName=assessment_id,KeyType=HASH \
  --global-secondary-indexes \
    "[{\"IndexName\":\"patient-index\",\"KeySchema\":[{\"AttributeName\":\"patient_id\",\"KeyType\":\"HASH\"}],\"Projection\":{\"ProjectionType\":\"ALL\"}}]" \
  --billing-mode PAY_PER_REQUEST \
  --sse-specification Enabled=true
```

#### 1.3 Create S3 Bucket

```bash
# Create bucket with encryption
aws s3api create-bucket \
  --bucket telemedicine-documents-dev \
  --region us-east-1

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket telemedicine-documents-dev \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "alias/telemedicine-key"
      }
    }]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket telemedicine-documents-dev \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

#### 1.4 Create Cognito User Pool

```bash
# Create user pool
aws cognito-idp create-user-pool \
  --pool-name telemedicine-users \
  --policies '{
    "PasswordPolicy": {
      "MinimumLength": 12,
      "RequireUppercase": true,
      "RequireLowercase": true,
      "RequireNumbers": true,
      "RequireSymbols": true
    }
  }' \
  --mfa-configuration ON \
  --auto-verified-attributes email

# Create app client
aws cognito-idp create-user-pool-client \
  --user-pool-id <pool-id> \
  --client-name telemedicine-web \
  --generate-secret \
  --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH
```

### Phase 2: Deploy Lambda Functions

#### 2.1 Create IAM Role

```bash
# Create Lambda execution role
aws iam create-role \
  --role-name telemedicine-lambda-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policies
aws iam attach-role-policy \
  --role-name telemedicine-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name telemedicine-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy \
  --role-name telemedicine-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name telemedicine-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam attach-role-policy \
  --role-name telemedicine-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/ComprehendMedicalFullAccess
```

#### 2.2 Deploy Symptom Checker Lambda

```bash
# Package function
cd backend/services
zip -r symptom_checker.zip symptom_checker.py

# Create function
aws lambda create-function \
  --function-name telemedicine-symptom-checker \
  --runtime python3.11 \
  --role arn:aws:iam::<account-id>:role/telemedicine-lambda-role \
  --handler symptom_checker.handler \
  --zip-file fileb://symptom_checker.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables='{
    "BEDROCK_MODEL_ID":"anthropic.claude-3-sonnet-20240229-v1:0",
    "DYNAMODB_TABLE":"telemedicine-assessments"
  }'
```

### Phase 3: Deploy API Gateway

```bash
# Create REST API
aws apigateway create-rest-api \
  --name telemedicine-api \
  --endpoint-configuration types=REGIONAL

# Create resources and methods
# (Use CloudFormation template for complete setup)
```

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t telemedicine-ai .

# Run container
docker run -d \
  -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  telemedicine-ai
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Production Deployment

### Pre-Production Checklist

- [ ] HIPAA compliance review completed
- [ ] Security audit passed
- [ ] Penetration testing completed
- [ ] Backup strategy configured
- [ ] Disaster recovery plan documented
- [ ] Monitoring and alerting configured
- [ ] Load testing completed
- [ ] Documentation updated

### Production Configuration

```bash
# Deploy production stack
aws cloudformation deploy \
  --template-file main.yaml \
  --stack-name telemedicine-ai-prod \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    Environment=production \
    EnableMultiAZ=true \
    EnableBackup=true \
    EnableWAF=true
```

### Enable CloudWatch Monitoring

```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name telemedicine-monitoring \
  --dashboard-body file://cloudwatch-dashboard.json

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name telemedicine-high-latency \
  --metric-name Latency \
  --namespace AWS/ApiGateway \
  --statistic Average \
  --period 300 \
  --threshold 1000 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:<region>:<account>:alerts
```

## Troubleshooting

### Common Issues

#### Bedrock Access Denied
```bash
# Verify model access
aws bedrock list-foundation-models --region us-east-1

# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::<account>:role/telemedicine-lambda-role \
  --action-names bedrock:InvokeModel
```

#### DynamoDB Throttling
```bash
# Check table metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ThrottledRequests \
  --dimensions Name=TableName,Value=telemedicine-assessments \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Sum
```

#### Lambda Timeout
```bash
# Increase timeout
aws lambda update-function-configuration \
  --function-name telemedicine-symptom-checker \
  --timeout 60

# Check logs
aws logs tail /aws/lambda/telemedicine-symptom-checker --follow
```

## Cleanup

### Development Environment

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name telemedicine-ai-dev

# Delete S3 bucket (empty first)
aws s3 rm s3://telemedicine-documents-dev --recursive
aws s3api delete-bucket --bucket telemedicine-documents-dev

# Delete DynamoDB tables
aws dynamodb delete-table --table-name telemedicine-patients
aws dynamodb delete-table --table-name telemedicine-sessions
aws dynamodb delete-table --table-name telemedicine-assessments
```

## Security Best Practices

1. **Enable MFA** for all user accounts
2. **Rotate credentials** regularly
3. **Enable CloudTrail** for audit logging
4. **Use VPC endpoints** for AWS services
5. **Implement least privilege** IAM policies
6. **Enable encryption** for all data at rest and in transit
7. **Regular security audits** and penetration testing

## Support

- **Documentation**: See [architecture.md](./architecture.md)
- **Issues**: Report via GitHub Issues
- **AWS Support**: For AWS service-specific issues

---

**Ready to deploy? Start with the [Quick Start](#quick-start-deployment) section! 🚀**
