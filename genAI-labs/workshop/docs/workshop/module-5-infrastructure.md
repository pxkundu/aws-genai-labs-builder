# Module 5: Infrastructure Deployment

## Overview
This module covers deploying Claude Code applications using Infrastructure as Code (IaC). You'll learn how to use AWS CDK and Terraform to deploy production-ready infrastructure for Claude Code applications.

## Learning Objectives
- Deploy infrastructure using AWS CDK
- Deploy infrastructure using Terraform
- Configure CI/CD pipelines
- Set up monitoring and alerting
- Optimize infrastructure costs
- Implement best practices for production deployment

## Prerequisites
- Completed Module 4: AWS Services Integration
- Understanding of AWS CDK or Terraform
- Basic knowledge of CI/CD pipelines
- Familiarity with AWS CloudFormation

## Step 1: AWS CDK Deployment

### 1.1 Create CDK Stack
Create `infrastructure/cdk/claude_code_stack.py`:

```python
"""
AWS CDK Stack for Claude Code Workshop
Deploys Lambda, API Gateway, DynamoDB, and S3
"""

from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_logs as logs,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct


class ClaudeCodeStack(Stack):
    """CDK Stack for Claude Code Workshop"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create S3 bucket for code storage
        code_bucket = s3.Bucket(
            self,
            "ClaudeCodeBucket",
            bucket_name=f"claude-code-workshop-{self.account}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=True
        )
        
        # Create DynamoDB table
        code_table = dynamodb.Table(
            self,
            "ClaudeCodeTable",
            table_name="claude-code-results",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl"
        )
        
        # Add GSI for querying by language
        code_table.add_global_secondary_index(
            index_name="language-index",
            partition_key=dynamodb.Attribute(
                name="language",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="generated_at",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # Create Lambda execution role
        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ]
        )
        
        # Add Bedrock permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=[
                    "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
                ]
            )
        )
        
        # Add DynamoDB permissions
        code_table.grant_read_write_data(lambda_role)
        
        # Add S3 permissions
        code_bucket.grant_read_write(lambda_role)
        
        # Create Lambda function
        code_generator_lambda = lambda_.Function(
            self,
            "ClaudeCodeGenerator",
            function_name="claude-code-generator",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_claude_code.lambda_handler",
            code=lambda_.Code.from_asset("code/lambda"),
            role=lambda_role,
            timeout=Duration.seconds(300),
            memory_size=512,
            environment={
                "AWS_REGION": self.region,
                "BEDROCK_MODEL_ID": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "TABLE_NAME": code_table.table_name,
                "BUCKET_NAME": code_bucket.bucket_name
            },
            log_retention=logs.RetentionDays.ONE_WEEK
        )
        
        # Create API Gateway
        api = apigateway.RestApi(
            self,
            "ClaudeCodeAPI",
            rest_api_name="Claude Code API",
            description="API for Claude Code generation",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization"]
            )
        )
        
        # Create /generate endpoint
        generate_resource = api.root.add_resource("generate")
        generate_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(code_generator_lambda)
        )
        
        # Create /health endpoint
        health_resource = api.root.add_resource("health")
        health_resource.add_method("GET")
        
        # Outputs
        CfnOutput(
            self,
            "ApiEndpoint",
            value=api.url,
            description="API Gateway endpoint URL"
        )
        
        CfnOutput(
            self,
            "CodeBucketName",
            value=code_bucket.bucket_name,
            description="S3 bucket for code storage"
        )
        
        CfnOutput(
            self,
            "TableName",
            value=code_table.table_name,
            description="DynamoDB table name"
        )


# CDK App
from aws_cdk import App

app = App()
ClaudeCodeStack(app, "ClaudeCodeStack")
app.synth()
```

### 1.2 CDK Deployment Script
Create `scripts/deployment/deploy_cdk.sh`:

```bash
#!/bin/bash
# Deploy Claude Code Workshop using AWS CDK

set -e

echo "🚀 Deploying Claude Code Workshop with CDK..."

# Install CDK dependencies
echo "📦 Installing CDK dependencies..."
npm install -g aws-cdk
cd infrastructure/cdk
pip install -r requirements.txt

# Bootstrap CDK (if not already bootstrapped)
echo "🔧 Bootstrapping CDK..."
cdk bootstrap aws://ACCOUNT_ID/REGION

# Synthesize CloudFormation template
echo "📝 Synthesizing CloudFormation template..."
cdk synth

# Deploy stack
echo "🚀 Deploying stack..."
cdk deploy --require-approval never

echo "✅ Deployment complete!"
echo "📋 Check outputs for API endpoint and resource names"
```

## Step 2: Terraform Deployment

### 2.1 Create Terraform Configuration
Create `infrastructure/terraform/main.tf`:

```hcl
# Terraform configuration for Claude Code Workshop

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket for code storage
resource "aws_s3_bucket" "code_bucket" {
  bucket = "claude-code-workshop-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name        = "Claude Code Workshop"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "code_bucket_versioning" {
  bucket = aws_s3_bucket.code_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# DynamoDB table
resource "aws_dynamodb_table" "code_table" {
  name           = "claude-code-results"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }
  
  attribute {
    name = "language"
    type = "S"
  }
  
  attribute {
    name = "generated_at"
    type = "S"
  }
  
  global_secondary_index {
    name     = "language-index"
    hash_key = "language"
    range_key = "generated_at"
  }
  
  tags = {
    Name        = "Claude Code Results"
    Environment = var.environment
  }
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "claude-code-lambda-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_bedrock" {
  name = "lambda-bedrock-policy"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ]
      Resource = "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_dynamodb" {
  name = "lambda-dynamodb-policy"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ]
      Resource = [
        aws_dynamodb_table.code_table.arn,
        "${aws_dynamodb_table.code_table.arn}/index/*"
      ]
    }]
  })
}

resource "aws_iam_role_policy" "lambda_s3" {
  name = "lambda-s3-policy"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ]
      Resource = "${aws_s3_bucket.code_bucket.arn}/*"
    }]
  })
}

# Lambda function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../code/lambda"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "code_generator" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "claude-code-generator"
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_claude_code.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.11"
  timeout         = 300
  memory_size     = 512
  
  environment {
    variables = {
      AWS_REGION       = var.aws_region
      BEDROCK_MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"
      TABLE_NAME       = aws_dynamodb_table.code_table.name
      BUCKET_NAME      = aws_s3_bucket.code_bucket.id
    }
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "code_api" {
  name        = "claude-code-api"
  description = "API for Claude Code generation"
}

resource "aws_api_gateway_resource" "generate" {
  rest_api_id = aws_api_gateway_rest_api.code_api.id
  parent_id   = aws_api_gateway_rest_api.code_api.root_resource_id
  path_part   = "generate"
}

resource "aws_api_gateway_method" "generate_post" {
  rest_api_id   = aws_api_gateway_rest_api.code_api.id
  resource_id   = aws_api_gateway_resource.generate.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.code_api.id
  resource_id = aws_api_gateway_resource.generate.id
  http_method = aws_api_gateway_method.generate_post.http_method
  
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.code_generator.invoke_arn
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.code_generator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.code_api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_method.generate_post,
    aws_api_gateway_integration.lambda_integration
  ]
  
  rest_api_id = aws_api_gateway_rest_api.code_api.id
  stage_name  = "prod"
}

# Data sources
data "aws_caller_identity" "current" {}

# Outputs
output "api_endpoint" {
  value = "${aws_api_gateway_deployment.api_deployment.invoke_url}/generate"
  description = "API Gateway endpoint URL"
}

output "code_bucket_name" {
  value = aws_s3_bucket.code_bucket.id
  description = "S3 bucket name for code storage"
}

output "table_name" {
  value = aws_dynamodb_table.code_table.name
  description = "DynamoDB table name"
}
```

### 2.2 Terraform Variables
Create `infrastructure/terraform/variables.tf`:

```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "workshop"
}
```

### 2.3 Terraform Deployment Script
Create `scripts/deployment/deploy_terraform.sh`:

```bash
#!/bin/bash
# Deploy Claude Code Workshop using Terraform

set -e

echo "🚀 Deploying Claude Code Workshop with Terraform..."

cd infrastructure/terraform

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Plan deployment
echo "📝 Planning deployment..."
terraform plan

# Apply deployment
echo "🚀 Applying deployment..."
terraform apply -auto-approve

echo "✅ Deployment complete!"
echo "📋 Check outputs for API endpoint and resource names"
```

## Step 3: CI/CD Pipeline

### 3.1 GitHub Actions Workflow
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Claude Code Workshop

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install aws-cdk-lib constructs
      
      - name: Deploy with CDK
        run: |
          cd infrastructure/cdk
          npm install -g aws-cdk
          cdk deploy --require-approval never
```

## Step 4: Monitoring and Alerting

### 4.1 CloudWatch Alarms
Create `infrastructure/cdk/monitoring.py`:

```python
"""
CloudWatch Monitoring and Alarms for Claude Code Workshop
"""

from aws_cdk import (
    Stack,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
    Duration
)
from constructs import Construct


class MonitoringStack(Stack):
    """CloudWatch monitoring stack"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create SNS topic for alerts
        alert_topic = sns.Topic(
            self,
            "AlertTopic",
            topic_name="claude-code-alerts"
        )
        
        # Lambda error alarm
        lambda_errors = cloudwatch.Alarm(
            self,
            "LambdaErrors",
            metric=cloudwatch.Metric(
                namespace="AWS/Lambda",
                metric_name="Errors",
                dimensions_map={
                    "FunctionName": "claude-code-generator"
                },
                statistic="Sum",
                period=Duration.minutes(5)
            ),
            threshold=5,
            evaluation_periods=1,
            alarm_description="Lambda function has errors"
        )
        
        lambda_errors.add_alarm_action(
            cw_actions.SnsAction(alert_topic)
        )
        
        # Lambda duration alarm
        lambda_duration = cloudwatch.Alarm(
            self,
            "LambdaDuration",
            metric=cloudwatch.Metric(
                namespace="AWS/Lambda",
                metric_name="Duration",
                dimensions_map={
                    "FunctionName": "claude-code-generator"
                },
                statistic="Average",
                period=Duration.minutes(5)
            ),
            threshold=250000,  # 250 seconds
            evaluation_periods=2,
            alarm_description="Lambda function duration is high"
        )
        
        lambda_duration.add_alarm_action(
            cw_actions.SnsAction(alert_topic)
        )
```

## Step 5: Cost Optimization

### 5.1 Cost Optimization Strategies

1. **Use Appropriate Model**: Use Haiku for simple tasks, Sonnet for complex
2. **Implement Caching**: Cache generated code for repeated requests
3. **Optimize Lambda**: Right-size memory and timeout
4. **Use DynamoDB On-Demand**: Pay per request instead of provisioned capacity
5. **S3 Lifecycle Policies**: Move old code to cheaper storage classes

## Step 6: Exercises

### Exercise 1: Deploy with CDK
Deploy the Claude Code workshop using AWS CDK.

### Exercise 2: Deploy with Terraform
Deploy the Claude Code workshop using Terraform.

### Exercise 3: Set up CI/CD
Create a CI/CD pipeline for automated deployment.

### Exercise 4: Add Monitoring
Add CloudWatch alarms and SNS notifications.

## Troubleshooting

### Common Issues

#### CDK Deployment Fails
- Check AWS credentials
- Verify region support
- Check IAM permissions
- Review CloudFormation errors

#### Terraform State Issues
- Use remote state backend
- Lock state file
- Review state conflicts

#### Lambda Deployment Fails
- Check code size limits
- Verify dependencies
- Review IAM permissions
- Check timeout settings

## Next Steps

✅ **Module 5 Complete!**

You have successfully:
- Deployed infrastructure with CDK
- Deployed infrastructure with Terraform
- Set up CI/CD pipelines
- Added monitoring and alerting

**Ready for [Module 6: Testing and Optimization](./module-6-testing.md)?**

## Additional Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)

