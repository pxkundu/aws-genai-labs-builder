# Module 6: Production Deployment

## Learning Objectives

By the end of this module, you will be able to:

- Deploy infrastructure using Infrastructure as Code (Terraform/CDK)
- Set up CI/CD pipelines for media workloads
- Configure comprehensive monitoring and alerting
- Implement security best practices for media content
- Optimize performance and costs for production
- Ensure production readiness and disaster recovery

## Prerequisites

- Completed all previous modules (1-5)
- Terraform or AWS CDK installed
- GitHub Actions or similar CI/CD platform access
- Production AWS account with appropriate permissions
- Understanding of production deployment practices

## Duration

**Estimated Time**: 60 minutes

## Step 1: Infrastructure as Code

### 1.1 Deploy with Terraform

```bash
# Navigate to infrastructure directory
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review deployment plan
terraform plan -out=production.tfplan

# Deploy to production
terraform apply production.tfplan

# Save outputs
terraform output -json > ../../config/production-outputs.json
```

### 1.2 Terraform Configuration Example

```hcl
# infrastructure/terraform/main.tf
terraform {
  required_version = ">= 1.5"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "media-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Buckets
resource "aws_s3_bucket" "media_raw" {
  bucket = "${var.project_name}-raw-${var.environment}"
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket" "media_processed" {
  bucket = "${var.project_name}-processed-${var.environment}"
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_s3_bucket" "media_generated" {
  bucket = "${var.project_name}-generated-${var.environment}"
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "media_cdn" {
  origin {
    domain_name = aws_s3_bucket.media_processed.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.media_processed.id}"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.media_oai.cloudfront_access_identity_path
    }
  }
  
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.media_processed.id}"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Lambda Functions
resource "aws_lambda_function" "script_generator" {
  filename         = "lambda/script_generator.zip"
  function_name    = "${var.project_name}-script-generator"
  role            = aws_iam_role.lambda_execution.arn
  handler         = "script_generator.lambda_handler"
  runtime         = "python3.11"
  timeout         = 60
  memory_size     = 512
  
  environment {
    variables = {
      AWS_REGION = var.aws_region
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# API Gateway
resource "aws_apigatewayv2_api" "media_api" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = var.allowed_origins
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["content-type", "authorization"]
  }
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# DynamoDB Tables
resource "aws_dynamodb_table" "content_metadata" {
  name           = "${var.project_name}-content-metadata"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "content_id"
  
  attribute {
    name = "content_id"
    type = "S"
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# OpenSearch Domain
resource "aws_opensearch_domain" "content_search" {
  domain_name    = "${var.project_name}-search"
  engine_version = "OpenSearch_2.11"
  
  cluster_config {
    instance_type  = "t3.small.search"
    instance_count = 2
  }
  
  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 20
  }
  
  node_to_node_encryption {
    enabled = true
  }
  
  encrypt_at_rest {
    enabled = true
  }
  
  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
  
  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = true
    
    master_user_options {
      master_user_name     = var.opensearch_master_user
      master_user_password = var.opensearch_master_password
    }
  }
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
```

### 1.3 Deploy with AWS CDK

```python
# infrastructure/cdk/media_stack.py
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigw,
    aws_dynamodb as dynamodb,
    aws_cloudfront as cloudfront,
    CfnOutput
)
from constructs import Construct

class MediaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # S3 Buckets
        raw_bucket = s3.Bucket(
            self, "MediaRawBucket",
            bucket_name=f"media-raw-{self.account}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED
        )
        
        processed_bucket = s3.Bucket(
            self, "MediaProcessedBucket",
            bucket_name=f"media-processed-{self.account}",
            encryption=s3.BucketEncryption.S3_MANAGED
        )
        
        # Lambda Functions
        script_generator = lambda_.Function(
            self, "ScriptGenerator",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="script_generator.lambda_handler",
            code=lambda_.Code.from_asset("lambda"),
            timeout=Duration.minutes(1),
            memory_size=512,
            environment={
                "AWS_REGION": self.region
            }
        )
        
        # API Gateway
        api = apigw.HttpApi(
            self, "MediaApi",
            cors_preflight=apigw.CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[apigw.CorsHttpMethod.GET, apigw.CorsHttpMethod.POST],
                allow_headers=["content-type"]
            )
        )
        
        # Add Lambda integration
        api.add_routes(
            path="/generate-script",
            methods=[apigw.HttpMethod.POST],
            integration=apigw.HttpLambdaIntegration(
                "ScriptGeneratorIntegration",
                script_generator
            )
        )
        
        # DynamoDB
        content_table = dynamodb.Table(
            self, "ContentMetadata",
            table_name="media-content-metadata",
            partition_key=dynamodb.Attribute(
                name="content_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True
        )
        
        # Outputs
        CfnOutput(
            self, "ApiEndpoint",
            value=api.url,
            description="API Gateway endpoint URL"
        )
```

## Step 2: Set Up CI/CD Pipeline

### 2.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Media AI Platform

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  PYTHON_VERSION: '3.11'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ --cov=./ --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install linting tools
        run: |
          pip install flake8 black isort
      
      - name: Run linters
        run: |
          flake8 lambda/
          black --check lambda/
          isort --check-only lambda/

  deploy-staging:
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: staging
      url: https://staging-api.example.com
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Deploy with Terraform
        run: |
          cd infrastructure/terraform
          terraform init
          terraform workspace select staging
          terraform plan -out=staging.tfplan
          terraform apply staging.tfplan
      
      - name: Deploy Lambda functions
        run: |
          ./scripts/deploy-lambdas.sh staging
      
      - name: Run integration tests
        run: |
          pytest tests/integration/ --env=staging

  deploy-production:
    needs: [deploy-staging]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://api.example.com
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Deploy with Terraform
        run: |
          cd infrastructure/terraform
          terraform init
          terraform workspace select production
          terraform plan -out=production.tfplan
          terraform apply production.tfplan
      
      - name: Deploy Lambda functions
        run: |
          ./scripts/deploy-lambdas.sh production
      
      - name: Run smoke tests
        run: |
          pytest tests/smoke/ --env=production
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment completed'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 2.2 Lambda Deployment Script

```bash
#!/bin/bash
# scripts/deploy-lambdas.sh

ENVIRONMENT=$1

if [ -z "$ENVIRONMENT" ]; then
  echo "Usage: ./deploy-lambdas.sh [staging|production]"
  exit 1
fi

echo "Deploying Lambda functions to $ENVIRONMENT..."

# List of Lambda functions
LAMBDAS=(
  "script-generator"
  "storyboard-generator"
  "voiceover-synthesizer"
  "content-generator"
  "semantic-search"
  "visual-search"
  "audience-insights-generator"
)

for LAMBDA in "${LAMBDAS[@]}"; do
  echo "Deploying $LAMBDA..."
  
  # Create deployment package
  cd lambda/$LAMBDA
  zip -r ../../deployments/$LAMBDA.zip .
  cd ../..
  
  # Update Lambda function
  aws lambda update-function-code \
    --function-name media-$LAMBDA-$ENVIRONMENT \
    --zip-file fileb://deployments/$LAMBDA.zip \
    --region us-east-1
  
  # Wait for update to complete
  aws lambda wait function-updated \
    --function-name media-$LAMBDA-$ENVIRONMENT
  
  echo "$LAMBDA deployed successfully"
done

echo "All Lambda functions deployed!"
```

## Step 3: Configure Monitoring and Alerting

### 3.1 CloudWatch Dashboards

```python
# scripts/create_dashboards.py
import boto3
import json

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
                    [".", "Errors", {"stat": "Sum"}],
                    [".", "Duration", {"stat": "Average"}]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "us-east-1",
                "title": "Lambda Performance"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/ApiGateway", "Count", {"stat": "Sum"}],
                    [".", "4XXError", {"stat": "Sum"}],
                    [".", "5XXError", {"stat": "Sum"}],
                    [".", "Latency", {"stat": "Average"}]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "us-east-1",
                "title": "API Gateway Metrics"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/S3", "BucketSizeBytes", {"stat": "Average", "dimensions": [["BucketName", "media-processed"]]}],
                    [".", "NumberOfObjects", {"stat": "Average", "dimensions": [["BucketName", "media-processed"]]}]
                ],
                "period": 86400,
                "stat": "Average",
                "region": "us-east-1",
                "title": "S3 Storage Metrics"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/Bedrock", "ModelInvocationCount", {"stat": "Sum"}],
                    [".", "ModelInvocationLatency", {"stat": "Average"}]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "us-east-1",
                "title": "Bedrock Usage"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='media-ai-platform',
    DashboardBody=json.dumps(dashboard_body)
)
```

### 3.2 CloudWatch Alarms

```python
# scripts/create_alarms.py
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

# Create SNS topic for alerts
topic_arn = sns.create_topic(Name='media-platform-alerts')['TopicArn']

# Lambda error rate alarm
cloudwatch.put_metric_alarm(
    AlarmName='lambda-high-error-rate',
    AlarmDescription='Alert when Lambda error rate exceeds 5%',
    MetricName='Errors',
    Namespace='AWS/Lambda',
    Statistic='Sum',
    Period=300,
    EvaluationPeriods=2,
    Threshold=10,
    ComparisonOperator='GreaterThanThreshold',
    Dimensions=[
        {'Name': 'FunctionName', 'Value': 'media-script-generator'}
    ],
    AlarmActions=[topic_arn]
)

# API Gateway latency alarm
cloudwatch.put_metric_alarm(
    AlarmName='api-high-latency',
    AlarmDescription='Alert when API latency exceeds 2 seconds',
    MetricName='Latency',
    Namespace='AWS/ApiGateway',
    Statistic='Average',
    Period=300,
    EvaluationPeriods=2,
    Threshold=2000,
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=[topic_arn]
)

# Bedrock cost alarm
cloudwatch.put_metric_alarm(
    AlarmName='bedrock-high-usage',
    AlarmDescription='Alert when Bedrock invocations exceed threshold',
    MetricName='ModelInvocationCount',
    Namespace='AWS/Bedrock',
    Statistic='Sum',
    Period=3600,
    EvaluationPeriods=1,
    Threshold=10000,
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=[topic_arn]
)
```

## Step 4: Security Best Practices

### 4.1 IAM Roles and Policies

```python
# scripts/setup_security.py
import boto3
import json

iam = boto3.client('iam', region_name='us-east-1')

# Lambda execution role with least privilege
lambda_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::media-*/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:Query"
            ],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:*:table/media-*"
            ]
        }
    ]
}

iam.put_role_policy(
    RoleName='lambda-execution-role',
    PolicyName='media-platform-policy',
    PolicyDocument=json.dumps(lambda_policy)
)
```

### 4.2 Enable AWS WAF

```bash
# Create WAF Web ACL
aws wafv2 create-web-acl \
  --name media-platform-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://config/waf-rules.json \
  --visibility-config \
    SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=MediaPlatformWAF
```

### 4.3 Enable CloudTrail

```bash
# Enable CloudTrail logging
aws cloudtrail create-trail \
  --name media-platform-trail \
  --s3-bucket-name media-cloudtrail-logs \
  --is-multi-region-trail \
  --enable-log-file-validation

aws cloudtrail start-logging --name media-platform-trail
```

## Step 5: Cost Optimization

### 5.1 Lambda Reserved Concurrency

```bash
# Set reserved concurrency to control costs
aws lambda put-function-concurrency \
  --function-name media-script-generator \
  --reserved-concurrent-executions 10
```

### 5.2 S3 Lifecycle Policies

```python
# scripts/setup_s3_lifecycle.py
import boto3

s3 = boto3.client('s3', region_name='us-east-1')

lifecycle_config = {
    'Rules': [
        {
            'Id': 'ArchiveOldContent',
            'Status': 'Enabled',
            'Prefix': 'raw/',
            'Transitions': [
                {
                    'Days': 90,
                    'StorageClass': 'STANDARD_IA'
                },
                {
                    'Days': 180,
                    'StorageClass': 'GLACIER'
                }
            ]
        },
        {
            'Id': 'DeleteOldLogs',
            'Status': 'Enabled',
            'Prefix': 'logs/',
            'Expiration': {
                'Days': 30
            }
        }
    ]
}

s3.put_bucket_lifecycle_configuration(
    Bucket='media-dev-raw',
    LifecycleConfiguration=lifecycle_config
)
```

## Step 6: Production Readiness Checklist

### 6.1 Pre-Deployment Checklist

- [ ] All infrastructure deployed via IaC
- [ ] CI/CD pipeline configured and tested
- [ ] Monitoring and alerting set up
- [ ] Security policies and WAF configured
- [ ] Backup and disaster recovery plan in place
- [ ] Cost monitoring and budgets configured
- [ ] Documentation updated
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Team trained on operations

### 6.2 Post-Deployment Validation

```bash
# Run smoke tests
pytest tests/smoke/ --env=production

# Check API health
curl https://api.example.com/health

# Verify monitoring
aws cloudwatch get-dashboard --dashboard-name media-ai-platform

# Check costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

## Best Practices

### Infrastructure
- Use Infrastructure as Code for all resources
- Implement environment separation (dev/staging/prod)
- Enable version control for infrastructure changes
- Use tagging for resource management

### CI/CD
- Automate all deployments
- Implement blue/green deployments for zero downtime
- Run tests before deployment
- Use feature flags for gradual rollouts

### Monitoring
- Set up comprehensive dashboards
- Configure alerts for critical metrics
- Implement log aggregation
- Monitor costs continuously

### Security
- Follow least privilege principle
- Enable encryption at rest and in transit
- Implement network security (VPC, security groups)
- Regular security audits

### Cost Optimization
- Use reserved capacity where applicable
- Implement auto-scaling
- Set up cost budgets and alerts
- Regular cost reviews

## Troubleshooting

### Common Issues

**Deployment Failures**
- Check Terraform/CDK state
- Verify IAM permissions
- Review CloudWatch logs
- Validate configuration files

**Performance Issues**
- Review Lambda memory and timeout
- Check API Gateway throttling
- Optimize database queries
- Review CloudFront cache settings

**Cost Overruns**
- Review CloudWatch cost metrics
- Check for unused resources
- Optimize Lambda concurrency
- Review S3 storage classes

## Next Steps

- **Optimization**: Fine-tune performance and costs
- **Scaling**: Implement auto-scaling for high traffic
- **Enhancements**: Add new features based on feedback
- **Documentation**: Keep documentation up to date

---

**Congratulations! You've completed the Media & Entertainment AI Workshop! 🎉**

You now have a production-ready AI-powered media platform. Continue to iterate, optimize, and enhance based on your specific needs.

