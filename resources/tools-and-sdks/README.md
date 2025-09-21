# 🛠️ AWS GenAI Tools & SDKs

> **Comprehensive toolkit for AWS GenAI development and deployment**

## 🎯 Overview

This directory provides a curated collection of tools, SDKs, frameworks, and utilities for building production-ready AWS GenAI solutions. From development to deployment and monitoring, find everything you need to accelerate your GenAI journey.

## 🧰 Development Tools

### 🐍 **Python SDK & Libraries**

#### Core AWS SDKs
```python
# Essential AWS SDKs for GenAI
pip install boto3                    # AWS SDK for Python
pip install aws-cdk-lib             # AWS CDK for Infrastructure
pip install awscli                  # AWS Command Line Interface
```

#### GenAI-Specific Libraries
```python
# Bedrock and GenAI libraries
pip install boto3[bedrock]          # Bedrock-specific extensions
pip install langchain               # LLM application framework
pip install langchain-aws           # AWS integrations for LangChain
pip install llama-index             # Data framework for LLMs
pip install chromadb                # Vector database for RAG
```

#### Production-Ready Stack
```python
# requirements.txt for production GenAI applications
boto3==1.34.0
langchain==0.1.0
langchain-aws==0.1.0
fastapi==0.100.0
uvicorn==0.23.0
pydantic==2.5.0
redis==5.0.0
numpy==1.24.0
pandas==2.1.0
scikit-learn==1.3.0
```

### 📱 **JavaScript/TypeScript SDK**

#### Core Libraries
```bash
# Essential Node.js packages
npm install @aws-sdk/client-bedrock-runtime
npm install @aws-sdk/client-textract
npm install @aws-sdk/client-comprehend
npm install @aws-cdk/aws-lambda
npm install @aws-cdk/aws-apigateway
```

#### GenAI Framework
```typescript
// TypeScript GenAI wrapper
import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';

export class GenAIClient {
    private bedrock: BedrockRuntimeClient;
    
    constructor(region: string = 'us-east-1') {
        this.bedrock = new BedrockRuntimeClient({ region });
    }
    
    async generateResponse(prompt: string, modelId: string): Promise<string> {
        const command = new InvokeModelCommand({
            modelId,
            body: JSON.stringify({
                anthropic_version: 'bedrock-2023-05-31',
                max_tokens: 1000,
                messages: [{ role: 'user', content: prompt }]
            })
        });
        
        const response = await this.bedrock.send(command);
        const result = JSON.parse(new TextDecoder().decode(response.body));
        
        return result.content[0].text;
    }
}
```

## 🏗️ Infrastructure as Code

### ☁️ **AWS CDK Constructs**

#### Custom GenAI Constructs
```typescript
// lib/genai-constructs.ts
import { Construct } from 'constructs';
import { Function, Runtime, Code } from '@aws-cdk/aws-lambda';
import { RestApi, LambdaIntegration } from '@aws-cdk/aws-apigateway';

export class GenAIChatbotConstruct extends Construct {
    constructor(scope: Construct, id: string) {
        super(scope, id);
        
        // Lambda function for GenAI processing
        const genaiFunction = new Function(this, 'GenAIFunction', {
            runtime: Runtime.PYTHON_3_9,
            handler: 'index.handler',
            code: Code.fromAsset('lambda'),
            environment: {
                BEDROCK_REGION: 'us-east-1',
                MODEL_ID: 'anthropic.claude-3-5-sonnet-20241022-v2:0'
            }
        });
        
        // API Gateway for REST API
        const api = new RestApi(this, 'GenAIAPI', {
            restApiName: 'GenAI Chatbot API'
        });
        
        const integration = new LambdaIntegration(genaiFunction);
        api.root.addMethod('POST', integration);
    }
}
```

#### Reusable Patterns
```typescript
// lib/patterns/rag-pattern.ts
export class RAGPattern extends Construct {
    constructor(scope: Construct, id: string, props: RAGPatternProps) {
        super(scope, id);
        
        // Document processing pipeline
        const documentBucket = new Bucket(this, 'DocumentBucket');
        
        // Vector database (OpenSearch)
        const vectorDB = new Domain(this, 'VectorDB', {
            version: EngineVersion.OPENSEARCH_2_3,
            capacity: {
                dataNodes: 2,
                dataNodeInstanceType: 't3.small.search'
            }
        });
        
        // Processing Lambda
        const processor = new Function(this, 'DocumentProcessor', {
            runtime: Runtime.PYTHON_3_9,
            handler: 'processor.handler',
            code: Code.fromAsset('src/document-processor')
        });
        
        // S3 trigger for document processing
        documentBucket.addEventNotification(
            EventType.OBJECT_CREATED,
            new LambdaDestination(processor)
        );
    }
}
```

### 🏭 **Terraform Modules**

#### GenAI Infrastructure Module
```hcl
# modules/genai-infrastructure/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Lambda function for GenAI processing
resource "aws_lambda_function" "genai_processor" {
  filename         = "genai_processor.zip"
  function_name    = "${var.project_name}-genai-processor"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "index.handler"
  runtime         = "python3.9"
  timeout         = 300
  memory_size     = 1024

  environment {
    variables = {
      BEDROCK_REGION = var.aws_region
      MODEL_ID       = var.bedrock_model_id
      LOG_LEVEL      = var.log_level
    }
  }
}

# API Gateway
resource "aws_api_gateway_rest_api" "genai_api" {
  name        = "${var.project_name}-genai-api"
  description = "GenAI API for ${var.project_name}"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# DynamoDB for session management
resource "aws_dynamodb_table" "sessions" {
  name           = "${var.project_name}-sessions"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "session_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}
```

### 📋 **CloudFormation Templates**

#### Complete GenAI Stack
```yaml
# cloudformation/genai-stack.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Complete GenAI application stack'

Parameters:
  ProjectName:
    Type: String
    Default: 'genai-app'
    Description: 'Project name for resource naming'
  
  BedrockModelId:
    Type: String
    Default: 'anthropic.claude-3-5-sonnet-20241022-v2:0'
    Description: 'Bedrock model ID to use'

Resources:
  # Lambda Execution Role
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: BedrockAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - bedrock:InvokeModel
                  - bedrock:InvokeModelWithResponseStream
                Resource: '*'

  # GenAI Processing Function
  GenAIFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${ProjectName}-genai-processor'
      Runtime: python3.9
      Handler: index.handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Timeout: 300
      MemorySize: 1024
      Environment:
        Variables:
          BEDROCK_MODEL_ID: !Ref BedrockModelId
          LOG_LEVEL: INFO
      Code:
        ZipFile: |
          import json
          import boto3
          import os
          
          bedrock = boto3.client('bedrock-runtime')
          
          def handler(event, context):
              try:
                  # Extract prompt from request
                  body = json.loads(event['body'])
                  prompt = body.get('prompt', '')
                  
                  # Generate response with Bedrock
                  response = bedrock.invoke_model(
                      modelId=os.environ['BEDROCK_MODEL_ID'],
                      body=json.dumps({
                          'anthropic_version': 'bedrock-2023-05-31',
                          'max_tokens': 1000,
                          'messages': [{'role': 'user', 'content': prompt}]
                      })
                  )
                  
                  result = json.loads(response['body'].read())
                  
                  return {
                      'statusCode': 200,
                      'headers': {
                          'Content-Type': 'application/json',
                          'Access-Control-Allow-Origin': '*'
                      },
                      'body': json.dumps({
                          'response': result['content'][0]['text']
                      })
                  }
                  
              except Exception as e:
                  return {
                      'statusCode': 500,
                      'body': json.dumps({'error': str(e)})
                  }

Outputs:
  LambdaFunctionArn:
    Description: 'ARN of the GenAI Lambda function'
    Value: !GetAtt GenAIFunction.Arn
```

## 🔧 Development Utilities

### 🧪 **Testing Frameworks**

#### GenAI Testing Utility
```python
# utils/genai_testing.py
import boto3
import json
import time
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class TestResult:
    test_name: str
    success: bool
    response_time: float
    response_quality: float
    error_message: str = None

class GenAITestFramework:
    def __init__(self, region: str = 'us-east-1'):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
        self.test_results = []
    
    def test_model_response(self, model_id: str, test_cases: List[Dict[str, Any]]) -> List[TestResult]:
        """Test GenAI model with multiple test cases"""
        
        results = []
        
        for test_case in test_cases:
            start_time = time.time()
            
            try:
                response = self.bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        'anthropic_version': 'bedrock-2023-05-31',
                        'max_tokens': test_case.get('max_tokens', 1000),
                        'messages': [{'role': 'user', 'content': test_case['prompt']}]
                    })
                )
                
                response_time = time.time() - start_time
                result = json.loads(response['body'].read())
                response_text = result['content'][0]['text']
                
                # Evaluate response quality
                quality_score = self.evaluate_response_quality(
                    test_case['prompt'], 
                    response_text, 
                    test_case.get('expected_criteria', {})
                )
                
                results.append(TestResult(
                    test_name=test_case['name'],
                    success=True,
                    response_time=response_time,
                    response_quality=quality_score
                ))
                
            except Exception as e:
                results.append(TestResult(
                    test_name=test_case['name'],
                    success=False,
                    response_time=time.time() - start_time,
                    response_quality=0.0,
                    error_message=str(e)
                ))
        
        self.test_results.extend(results)
        return results
    
    def evaluate_response_quality(self, prompt: str, response: str, criteria: Dict[str, Any]) -> float:
        """Evaluate response quality based on criteria"""
        
        quality_score = 0.0
        total_criteria = 0
        
        # Check response length
        if 'min_length' in criteria:
            total_criteria += 1
            if len(response) >= criteria['min_length']:
                quality_score += 1
        
        # Check for required keywords
        if 'required_keywords' in criteria:
            total_criteria += 1
            keywords_found = sum(1 for keyword in criteria['required_keywords'] 
                               if keyword.lower() in response.lower())
            quality_score += keywords_found / len(criteria['required_keywords'])
        
        # Check response relevance (simple keyword matching)
        if 'relevance_keywords' in criteria:
            total_criteria += 1
            relevance_score = sum(1 for keyword in criteria['relevance_keywords'] 
                                if keyword.lower() in response.lower())
            quality_score += min(relevance_score / len(criteria['relevance_keywords']), 1.0)
        
        return quality_score / max(total_criteria, 1)
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.success)
        average_response_time = sum(result.response_time for result in self.test_results) / total_tests
        average_quality = sum(result.response_quality for result in self.test_results) / total_tests
        
        report = f"""
GenAI Model Test Report
======================

Summary:
- Total Tests: {total_tests}
- Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)
- Average Response Time: {average_response_time:.2f} seconds
- Average Quality Score: {average_quality:.2f}

Detailed Results:
"""
        
        for result in self.test_results:
            status = "✅" if result.success else "❌"
            report += f"{status} {result.test_name}: {result.response_time:.2f}s, Quality: {result.response_quality:.2f}\n"
            if result.error_message:
                report += f"   Error: {result.error_message}\n"
        
        return report
```

### 📊 **Performance Monitoring**

#### GenAI Performance Monitor
```python
# utils/performance_monitor.py
import boto3
import time
import json
from typing import Dict, Any

class GenAIPerformanceMonitor:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.metrics = []
    
    def monitor_genai_call(self, operation_name: str):
        """Decorator to monitor GenAI operations"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    
                    # Calculate metrics
                    response_time = (end_time - start_time) * 1000  # milliseconds
                    
                    # Publish metrics to CloudWatch
                    self.publish_metrics(operation_name, {
                        'ResponseTime': response_time,
                        'Success': 1,
                        'TokenCount': self.extract_token_count(result)
                    })
                    
                    return result
                    
                except Exception as e:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    # Publish error metrics
                    self.publish_metrics(operation_name, {
                        'ResponseTime': response_time,
                        'Success': 0,
                        'ErrorCount': 1
                    })
                    
                    raise
            
            return wrapper
        return decorator
    
    def publish_metrics(self, operation_name: str, metrics: Dict[str, float]):
        """Publish metrics to CloudWatch"""
        
        metric_data = []
        
        for metric_name, value in metrics.items():
            metric_data.append({
                'MetricName': metric_name,
                'Value': value,
                'Unit': self.get_metric_unit(metric_name),
                'Dimensions': [
                    {
                        'Name': 'Operation',
                        'Value': operation_name
                    }
                ]
            })
        
        self.cloudwatch.put_metric_data(
            Namespace='GenAI/Performance',
            MetricData=metric_data
        )
    
    def get_metric_unit(self, metric_name: str) -> str:
        """Get appropriate unit for metric"""
        units = {
            'ResponseTime': 'Milliseconds',
            'TokenCount': 'Count',
            'Success': 'Count',
            'ErrorCount': 'Count',
            'Cost': 'None'
        }
        return units.get(metric_name, 'None')
```

### 🔍 **Debugging Tools**

#### GenAI Debug Utility
```python
# utils/debug_tools.py
import json
import logging
from typing import Dict, Any

class GenAIDebugger:
    def __init__(self, log_level: str = 'INFO'):
        self.logger = logging.getLogger('GenAIDebugger')
        self.logger.setLevel(getattr(logging, log_level))
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_prompt_and_response(self, prompt: str, response: str, model_id: str):
        """Log prompt and response for debugging"""
        
        debug_data = {
            'model_id': model_id,
            'prompt_length': len(prompt),
            'response_length': len(response),
            'prompt_preview': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'response_preview': response[:200] + '...' if len(response) > 200 else response
        }
        
        self.logger.info(f"GenAI Call Debug: {json.dumps(debug_data, indent=2)}")
    
    def analyze_token_usage(self, prompt: str, response: str) -> Dict[str, int]:
        """Analyze token usage (approximate)"""
        
        # Simple token estimation (more accurate counting would use tiktoken)
        prompt_tokens = len(prompt.split()) * 1.3  # Rough estimation
        response_tokens = len(response.split()) * 1.3
        total_tokens = prompt_tokens + response_tokens
        
        usage = {
            'prompt_tokens': int(prompt_tokens),
            'response_tokens': int(response_tokens),
            'total_tokens': int(total_tokens)
        }
        
        self.logger.debug(f"Token Usage: {json.dumps(usage)}")
        return usage
    
    def validate_response_structure(self, response: str, expected_format: str = 'json') -> bool:
        """Validate response structure"""
        
        if expected_format == 'json':
            try:
                json.loads(response)
                self.logger.debug("Response is valid JSON")
                return True
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON response: {e}")
                return False
        
        return True
```

## 🚀 Deployment Tools

### 📦 **CI/CD Pipeline Templates**

#### GitHub Actions Workflow
```yaml
# .github/workflows/genai-deploy.yml
name: Deploy GenAI Application

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  PYTHON_VERSION: 3.9

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
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          pytest tests/ -v --cov=src/
          
      - name: Run GenAI integration tests
        run: |
          python -m pytest tests/integration/ -v
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Install CDK
        run: npm install -g aws-cdk
      
      - name: Deploy infrastructure
        run: |
          cd infrastructure
          npm install
          cdk deploy --require-approval never
      
      - name: Deploy application code
        run: |
          zip -r genai-app.zip src/
          aws lambda update-function-code \
            --function-name genai-processor \
            --zip-file fileb://genai-app.zip
```

### 🐳 **Docker Containers**

#### GenAI Application Container
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV AWS_DEFAULT_REGION=us-east-1

# Create non-root user
RUN useradd -m -u 1000 genai && chown -R genai:genai /app
USER genai

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 📋 **Deployment Scripts**

#### Automated Deployment Script
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# Configuration
PROJECT_NAME="genai-app"
AWS_REGION="us-east-1"
ENVIRONMENT=${1:-"dev"}

echo "🚀 Deploying $PROJECT_NAME to $ENVIRONMENT environment..."

# Validate AWS credentials
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

# Package Lambda function
echo "📦 Packaging Lambda function..."
mkdir -p dist
cd src
zip -r ../dist/genai-function.zip . -x "tests/*" "__pycache__/*"
cd ..

# Deploy infrastructure
echo "🏗️ Deploying infrastructure..."
cd infrastructure
npm install
cdk deploy --context environment=$ENVIRONMENT --require-approval never
cd ..

# Update Lambda function code
echo "🔄 Updating Lambda function..."
aws lambda update-function-code \
    --function-name "$PROJECT_NAME-genai-processor-$ENVIRONMENT" \
    --zip-file fileb://dist/genai-function.zip \
    --region $AWS_REGION

# Run smoke tests
echo "🔍 Running smoke tests..."
python scripts/smoke_tests.py --environment $ENVIRONMENT

echo "✅ Deployment completed successfully!"
echo "🌐 API Endpoint: $(aws cloudformation describe-stacks \
    --stack-name $PROJECT_NAME-$ENVIRONMENT \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text \
    --region $AWS_REGION)"
```

---

## 📚 Documentation Tools

### 📖 **API Documentation Generator**

#### FastAPI Integration
```python
# src/api_docs.py
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

def custom_openapi(app: FastAPI):
    """Generate custom OpenAPI schema"""
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="GenAI API",
        version="1.0.0",
        description="Production-ready GenAI API with AWS Bedrock integration",
        routes=app.routes,
    )
    
    # Add custom examples
    openapi_schema["paths"]["/generate"]["post"]["requestBody"]["content"]["application/json"]["examples"] = {
        "simple_query": {
            "summary": "Simple query example",
            "value": {
                "prompt": "What is artificial intelligence?",
                "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "max_tokens": 1000
            }
        },
        "complex_analysis": {
            "summary": "Complex analysis example", 
            "value": {
                "prompt": "Analyze the following financial data and provide insights...",
                "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "max_tokens": 2000,
                "temperature": 0.7
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
```

---

**Accelerate your AWS GenAI development with these production-ready tools and frameworks! 🚀**

## 🔗 Quick Access

- **[Python Utilities](./python/)** - Python development tools
- **[Infrastructure Templates](./infrastructure/)** - IaC templates and modules
- **[Testing Frameworks](./testing/)** - Comprehensive testing tools
- **[Monitoring Tools](./monitoring/)** - Performance and observability
- **[CI/CD Pipelines](./cicd/)** - Automated deployment workflows

---

**Next Steps**: Choose the tools that match your development workflow and start building! 💪
