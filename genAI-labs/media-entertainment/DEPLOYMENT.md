# Media & Entertainment AI Solution - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Media & Entertainment AI Solution on AWS. The deployment supports both development and production environments with infrastructure as code using Terraform and AWS CDK, focused on high-volume media processing and AI-powered content workflows.

## Prerequisites

### Required Tools

- **AWS CLI** (v2.0+)
- **Terraform** (v1.5+)
- **Python** (3.11+)
- **Node.js** (18+)
- **Docker** (optional, for local encoding/testing)
- **Git**

### AWS Account Requirements

- AWS Account with admin access
- Access to the following AWS services:
  - Amazon Bedrock (with model access enabled)
  - Amazon SageMaker
  - Amazon Rekognition
  - Amazon Transcribe
  - Amazon Polly
  - AWS Elemental MediaConvert
  - Amazon S3
  - Amazon CloudFront
  - Amazon OpenSearch Service (optional for discovery)
  - Amazon Kinesis (optional for event streams)
  - Amazon API Gateway
  - AWS Lambda
  - AWS Step Functions
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
cd genAI-labs/media-entertainment
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

**Required Environment Variables** (example):

```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id
ENVIRONMENT=development
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
S3_RAW_BUCKET=media-dev-raw
S3_PROCESSED_BUCKET=media-dev-processed
S3_GENERATED_BUCKET=media-dev-generated
CLOUDFRONT_DISTRIBUTION_ID=YOUR_DISTRIBUTION_ID
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
# From project root
cd genAI-labs/media-entertainment

# Deploy Lambda functions
./scripts/deploy-lambdas.sh

# Deploy API Gateway routes
./scripts/deploy-api.sh

# Load sample media content and metadata
python scripts/load-sample-content.py
```

### 6. Verify Deployment

```bash
# Check API health
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/health

# Test Content Studio endpoint
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/content-studio/create-video \
  -H "Content-Type: application/json" \
  -d '{
    "script": "Short promo for our new sci-fi series...",
    "style": "dramatic",
    "duration": 60
  }'
```

## Detailed Deployment Steps

### 1. S3 & CloudFront

```bash
# Create S3 buckets
aws s3 mb s3://media-dev-raw --region us-east-1
aws s3 mb s3://media-dev-processed --region us-east-1
aws s3 mb s3://media-dev-generated --region us-east-1

# (CloudFront typically provisioned via Terraform/CDK)
```

### 2. MediaConvert Setup

```bash
# Get MediaConvert endpoint
aws mediaconvert describe-endpoints

# Save endpoint URL in config/mediaconvert-endpoint.json or env var
```

Use Terraform/CDK modules to:
- Create MediaConvert job templates for different renditions (1080p, 720p, etc.).
- Configure IAM roles for MediaConvert access to S3.

### 3. AI Services Configuration

#### Bedrock

```bash
# List available models
aws bedrock list-foundation-models --region us-east-1
```

Ensure access to:
- Claude 3.5 Sonnet (scripts, storyboards, campaigns)
- Optional image models (if used)

#### Rekognition, Transcribe, Polly

No special provisioning required beyond IAM permissions, but you may:
- Create custom Rekognition projects (labels) for content QA.
- Configure default Transcribe job settings.
- Choose Polly voices for default styles.

### 4. Lambda Functions & APIs

Key functions (names are illustrative):
- `media-content-studio`: Script → storyboard → video pipeline
- `media-discovery`: Semantic & visual search
- `media-generation`: Marketing & social content generation
- `media-audience-analytics`: Engagement metrics and predictions

Deployed via:

```bash
./scripts/deploy-lambdas.sh --environment development
```

API Gateway routes (e.g. via Terraform/CDK):
- `POST /content-studio/create-video`
- `POST /discovery/search`
- `POST /generation/social-post`
- `GET /analytics/engagement`

### 5. Sample Content & Metadata

```bash
# Upload sample assets
aws s3 sync data/sample/videos/ s3://media-dev-raw/videos/
aws s3 sync data/sample/images/ s3://media-dev-raw/images/

# Load metadata
python scripts/load-sample-metadata.py \
  --bucket media-dev-raw \
  --metadata-file data/sample/metadata.json
```

## Production Deployment

### Pre-Production Checklist

- [ ] All unit and integration tests passing
- [ ] Content pipelines validated with sample assets
- [ ] API latency within targets
- [ ] CloudFront and caching validated
- [ ] Monitoring dashboards created
- [ ] Logging and tracing enabled
- [ ] Cost and throughput estimates reviewed

### Blue-Green or Canary Deployment

Use your CI/CD system (e.g. GitHub Actions) to:
- Deploy new Lambda versions behind a new stage/alias.
- Shift traffic gradually using API Gateway stages or Lambda aliases.

Example (Lambda alias traffic shifting):

```bash
aws lambda update-alias \
  --function-name media-content-studio \
  --name prod \
  --routing-config '{"AdditionalVersionWeights":{"2":0.1}}'
```

Monitor metrics, then increase to 100% if healthy.

## Monitoring & Observability

### CloudWatch Dashboards

Track:
- Content Studio: job counts, errors, duration
- Discovery: latency, error rates, result counts
- Generation: request counts, latency
- MediaConvert: job status, failures

### Alarms

Example alarms:

```bash
# Discovery latency alarm
aws cloudwatch put-metric-alarm \
  --alarm-name media-discovery-latency-high \
  --metric-name Latency \
  --namespace AWS/ApiGateway \
  --statistic Average \
  --period 300 \
  --threshold 0.5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=ApiName,Value=media-entertainment-api
```

## Security & Rights Considerations

- Use KMS for bucket and object encryption.
- Implement signed URLs for content delivery where appropriate.
- Restrict access to MediaConvert and media buckets via IAM and resource policies.
- Use Rekognition/Comprehend for:
  - PII detection and redaction.
  - Content appropriateness checks (e.g., age ratings workflows).

## Troubleshooting

### MediaConvert Job Failures

- Check IAM role permissions.
- Verify input/output bucket paths.
- Review MediaConvert job logs in CloudWatch.

### Bedrock Invocation Errors

- Verify model access in Bedrock console.
- Check request body format and token limits.

### High API Latency

- Enable Lambda provisioned concurrency for hot paths.
- Increase memory for CPU-bound functions.
- Use CloudFront caching where possible.

## Cleanup

### Development Environment

```bash
# Destroy infrastructure
cd infrastructure/terraform
terraform destroy

# Remove sample content
aws s3 rb s3://media-dev-raw --force
aws s3 rb s3://media-dev-processed --force
aws s3 rb s3://media-dev-generated --force
```

Only clean up production environments after:
- Backups are verified.
- All stakeholders confirm decommissioning.

## Best Practices

- Keep content pipelines idempotent and retry-safe.
- Separate raw vs. processed vs. generated content buckets.
- Tag resources by environment, workload, and cost center.
- Use feature flags for enabling new AI features gradually.

## Support & Resources

- **Architecture Guide**: `architecture.md`
- **Workshop Guide**: `docs/workshop/README.md` (once created)
- **AWS Docs**:
  - Bedrock, MediaConvert, Rekognition, Transcribe, Polly, CloudFront

--- 

**Ready to deploy? Start with the [Quick Start Deployment](#quick-start-deployment) section and validate with the sample content workflows. 🚀**


