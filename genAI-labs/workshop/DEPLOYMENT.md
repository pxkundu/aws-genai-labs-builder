# Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Claude Code on AWS Workshop infrastructure.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Python 3.11+ installed
- Node.js 18+ installed (for CDK)
- Terraform 1.0+ installed (optional, for Terraform deployment)

## Deployment Options

### Option 1: AWS CDK Deployment

#### Step 1: Install Dependencies

```bash
# Install AWS CDK globally
npm install -g aws-cdk

# Verify installation
cdk --version

# Install Python dependencies
pip install -r requirements.txt
cd infrastructure/cdk
pip install -r requirements.txt
```

#### Step 2: Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Verify credentials
aws sts get-caller-identity
```

#### Step 3: Bootstrap CDK (First Time Only)

```bash
cd infrastructure/cdk
cdk bootstrap aws://ACCOUNT_ID/REGION
```

#### Step 4: Deploy Stack

```bash
# Synthesize CloudFormation template
cdk synth

# Deploy stack
cdk deploy --require-approval never

# Or use deployment script
cd ../..
bash scripts/deployment/deploy_cdk.sh
```

#### Step 5: Verify Deployment

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name ClaudeCodeStack

# Get outputs
aws cloudformation describe-stacks \
  --stack-name ClaudeCodeStack \
  --query 'Stacks[0].Outputs'
```

### Option 2: Terraform Deployment

#### Step 1: Install Dependencies

```bash
# Install Terraform
# macOS
brew install terraform

# Linux
# Download from https://www.terraform.io/downloads

# Verify installation
terraform version
```

#### Step 2: Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=us-east-1
```

#### Step 3: Initialize Terraform

```bash
cd infrastructure/terraform
terraform init
```

#### Step 4: Plan Deployment

```bash
# Review deployment plan
terraform plan

# Review specific resources
terraform plan -target=aws_lambda_function.code_generator
```

#### Step 5: Deploy Infrastructure

```bash
# Deploy all resources
terraform apply -auto-approve

# Or use deployment script
cd ../..
bash scripts/deployment/deploy_terraform.sh
```

#### Step 6: Verify Deployment

```bash
# Check Terraform state
terraform show

# Get outputs
terraform output
```

## Configuration

### Environment Variables

Create a `.env` file in the workshop root:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Bedrock Configuration
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Claude Code Configuration
MAX_TOKENS=4000
TEMPERATURE=0.7
```

### Lambda Configuration

Update Lambda environment variables in `infrastructure/cdk/claude_code_stack.py` or `infrastructure/terraform/main.tf`:

```python
environment={
    "AWS_REGION": "us-east-1",
    "BEDROCK_MODEL_ID": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "TABLE_NAME": "claude-code-results",
    "BUCKET_NAME": "claude-code-workshop"
}
```

## Post-Deployment

### 1. Test API Endpoint

```bash
# Get API endpoint from outputs
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ClaudeCodeStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

# Test health endpoint
curl $API_ENDPOINT/health

# Test code generation
curl -X POST $API_ENDPOINT/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Generate a Python function to calculate factorial",
    "language": "python",
    "max_tokens": 1000
  }'
```

### 2. Verify Lambda Function

```bash
# Test Lambda function directly
aws lambda invoke \
  --function-name claude-code-generator \
  --payload '{"body":"{\"prompt\":\"Generate hello world\",\"language\":\"python\"}"}' \
  response.json

cat response.json
```

### 3. Verify DynamoDB Table

```bash
# Check table exists
aws dynamodb describe-table --table-name claude-code-results

# List items (if any)
aws dynamodb scan --table-name claude-code-results
```

### 4. Verify S3 Bucket

```bash
# List buckets
aws s3 ls | grep claude-code-workshop

# List objects (if any)
aws s3 ls s3://claude-code-workshop-ACCOUNT_ID/
```

## Monitoring

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/claude-code-generator --follow

# View API Gateway logs
aws logs tail /aws/apigateway/claude-code-api --follow
```

### CloudWatch Metrics

```bash
# View Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=claude-code-generator \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

## Troubleshooting

### Common Issues

#### Deployment Fails

1. **Check AWS Credentials**:
   ```bash
   aws sts get-caller-identity
   ```

2. **Check IAM Permissions**:
   - Ensure you have permissions for CloudFormation, Lambda, API Gateway, DynamoDB, S3, and Bedrock

3. **Check Region Support**:
   - Ensure Bedrock is available in your region (us-east-1, us-west-2, etc.)

#### Lambda Function Fails

1. **Check Lambda Logs**:
   ```bash
   aws logs tail /aws/lambda/claude-code-generator --follow
   ```

2. **Check IAM Permissions**:
   - Verify Lambda role has Bedrock, DynamoDB, and S3 permissions

3. **Check Environment Variables**:
   - Verify environment variables are set correctly

#### API Gateway Errors

1. **Check Integration**:
   - Verify Lambda integration is configured correctly

2. **Check CORS**:
   - Verify CORS configuration if accessing from browser

3. **Check Permissions**:
   - Verify API Gateway has permission to invoke Lambda

## Cleanup

### CDK Cleanup

```bash
cd infrastructure/cdk
cdk destroy
```

### Terraform Cleanup

```bash
cd infrastructure/terraform
terraform destroy -auto-approve
```

### Manual Cleanup

```bash
# Delete Lambda function
aws lambda delete-function --function-name claude-code-generator

# Delete API Gateway
aws apigateway delete-rest-api --rest-api-id API_ID

# Delete DynamoDB table
aws dynamodb delete-table --table-name claude-code-results

# Delete S3 bucket and contents
aws s3 rb s3://claude-code-workshop-ACCOUNT_ID --force
```

## Additional Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

