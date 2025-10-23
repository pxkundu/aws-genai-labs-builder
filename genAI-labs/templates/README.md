# 🗂️ GenAI Project Templates

> **Ready-to-use project templates for rapid AWS GenAI development**

## 🎯 Overview

This directory contains production-ready project templates that serve as starting points for various GenAI use cases. Each template includes complete infrastructure, application code, documentation, and deployment scripts.

## 📁 Available Templates

### 🤖 [Bedrock Chatbot Template](./bedrock-chatbot/)
Complete chatbot implementation with Bedrock integration
- **Technologies**: AWS Bedrock, Lambda, API Gateway, DynamoDB
- **Features**: Conversation memory, multiple models, streaming responses
- **Use Cases**: Customer service, internal Q&A, virtual assistants

### 🔍 [RAG Knowledge Base Template](./rag-knowledge-base/)
Retrieval-Augmented Generation system for document Q&A
- **Technologies**: Bedrock, OpenSearch, Textract, S3
- **Features**: Document ingestion, semantic search, source attribution
- **Use Cases**: Technical documentation, policy Q&A, research assistance

### 📊 [Document Analysis Pipeline](./document-analysis/)
Automated document processing and analysis
- **Technologies**: Textract, Comprehend, Bedrock, Step Functions
- **Features**: OCR, entity extraction, sentiment analysis, summarization
- **Use Cases**: Contract analysis, medical records, financial documents

### 🔄 [Multi-Agent Workflow](./multi-agent-workflow/)
Coordinated multi-agent system for complex tasks
- **Technologies**: Bedrock Agents, Step Functions, EventBridge
- **Features**: Agent orchestration, workflow management, state persistence
- **Use Cases**: Research automation, content creation, data analysis

### 📈 [Real-Time Analytics](./real-time-analytics/)
Streaming data analysis with GenAI insights
- **Technologies**: Kinesis, Lambda, Bedrock, CloudWatch
- **Features**: Real-time processing, anomaly detection, automated alerts
- **Use Cases**: Monitoring, fraud detection, operational intelligence

### 🛒 [Multi-Agentic E-Commerce](./multi-agent-ecommerce/)
Intelligent e-commerce platform with coordinated AI agents
- **Technologies**: Bedrock Agents, Lambda, RDS, ElastiCache, OpenSearch, Terraform
- **Features**: Multi-agent orchestration, personalized recommendations, dynamic pricing
- **Use Cases**: E-commerce platforms, retail automation, customer experience

## 🚀 Quick Start Guide

### Prerequisites
```bash
# Required tools
AWS CLI v2.x
Python 3.9+
Node.js 18+
Docker
Terraform >= 1.0
```

### Template Usage
```bash
# 1. Choose and copy template
cp -r templates/multi-agent-ecommerce my-ecommerce-project
cd my-ecommerce-project

# 2. Configure project
./scripts/configure.sh

# 3. Deploy infrastructure (Terraform)
cd infrastructure/terraform
terraform init
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"

# 4. Deploy application
./scripts/deploy-app.sh
```

## 📋 Template Structure

Each template follows a standardized structure:

```
template-name/
├── README.md                 # Template-specific documentation
├── architecture/             # Architecture diagrams and docs
│   ├── solution-overview.md
│   ├── data-flow.md
│   └── security-model.md
├── infrastructure/           # Infrastructure as Code
│   ├── terraform/           # Terraform configurations
│   ├── cloudformation/      # CloudFormation templates
│   └── cdk/                 # AWS CDK constructs
├── src/                     # Application source code
│   ├── lambda/              # Lambda functions
│   ├── api/                 # API implementations
│   ├── shared/              # Shared utilities
│   └── frontend/            # UI components (if applicable)
├── tests/                   # Test suites
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
├── docs/                    # Additional documentation
│   ├── deployment.md        # Deployment guide
│   ├── configuration.md     # Configuration options
│   ├── api-reference.md     # API documentation
│   └── troubleshooting.md   # Common issues and solutions
├── scripts/                 # Utility scripts
│   ├── configure.sh         # Project configuration
│   ├── deploy.sh           # Deployment automation
│   ├── test.sh             # Test execution
│   └── cleanup.sh          # Resource cleanup
├── config/                  # Configuration files
│   ├── dev.json            # Development settings
│   ├── staging.json        # Staging settings
│   └── prod.json           # Production settings
└── package.json            # Dependencies and scripts
```

## 🔧 Customization Guide

### 1. **Configuration**
Each template includes environment-specific configuration files:

```json
{
  "environment": "production",
  "region": "us-east-1",
  "bedrock": {
    "models": {
      "chat": "anthropic.claude-3-5-sonnet-20241022-v2:0",
      "embeddings": "amazon.titan-embed-text-v1"
    },
    "max_tokens": 4000,
    "temperature": 0.7
  },
  "security": {
    "encryption": true,
    "vpc_enabled": true,
    "multi_az": true
  },
  "monitoring": {
    "cloudwatch_logs": true,
    "x_ray_tracing": true,
    "custom_metrics": true
  }
}
```

### 2. **Infrastructure Customization**
Modify Terraform modules for your specific requirements:

```hcl
# infrastructure/terraform/main.tf
module "vpc" {
  source = "./modules/vpc"
  
  name_prefix = "${var.project_name}-${var.environment}"
  vpc_cidr    = var.vpc_cidr
  azs         = var.availability_zones
  
  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets
  
  enable_nat_gateway = var.enable_nat_gateway
  enable_dns_hostnames = true
  enable_dns_support = true
  
  tags = local.common_tags
}

module "lambda" {
  source = "./modules/lambda"
  
  name_prefix = local.name_prefix
  vpc_id = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  
  kms_key_id = module.kms.key_id
  
  tags = local.common_tags
}
```

### 3. **Application Logic**
Customize the core GenAI logic for your use case:

```python
# src/lambda/genai_processor.py
class GenAIProcessor:
    def __init__(self, config):
        self.bedrock = boto3.client('bedrock-runtime')
        self.config = config
        
    def process_request(self, event):
        """Customize this method for your specific use case"""
        
        # Extract user input
        user_input = event.get('prompt', '')
        
        # Apply custom preprocessing
        processed_input = self.preprocess_input(user_input)
        
        # Generate response with custom parameters
        response = self.generate_response(
            processed_input,
            model_id=self.config['model_id'],
            temperature=self.config['temperature']
        )
        
        # Apply custom postprocessing
        final_response = self.postprocess_response(response)
        
        return final_response
```

## 📊 Performance Optimization

### Template Performance Targets
- **Cold Start**: < 2 seconds for Lambda functions
- **Response Time**: < 500ms for API endpoints
- **Throughput**: 1000+ requests per minute
- **Availability**: 99.9% uptime SLA

### Optimization Techniques
```python
# Performance optimization examples
class PerformanceOptimizations:
    def __init__(self):
        # Connection pooling
        self.bedrock = boto3.client(
            'bedrock-runtime',
            config=Config(
                retries={'max_attempts': 3},
                max_pool_connections=50
            )
        )
        
        # Caching layer
        self.cache = redis.Redis(
            host='elasticache-endpoint',
            port=6379,
            decode_responses=True
        )
    
    def cached_response(self, prompt_hash):
        """Implement intelligent caching"""
        cached = self.cache.get(f"response:{prompt_hash}")
        if cached:
            return json.loads(cached)
        return None
    
    def batch_processing(self, requests):
        """Batch similar requests for efficiency"""
        # Group similar requests
        batches = self.group_similar_requests(requests)
        
        # Process batches concurrently
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(self.process_batch, batch) 
                for batch in batches
            ]
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        
        return results
```

## 🔒 Security Best Practices

### Built-in Security Features
- **IAM Roles**: Least privilege access patterns
- **VPC Integration**: Network isolation
- **Encryption**: At-rest and in-transit encryption
- **Secrets Management**: AWS Secrets Manager integration
- **Audit Logging**: Comprehensive activity tracking

### Security Configuration
```python
# Security configuration example
security_config = {
    "iam_policies": {
        "lambda_execution_role": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "*"
                }
            ]
        }
    },
    "vpc_security_groups": {
        "lambda_sg": {
            "ingress_rules": [],
            "egress_rules": [
                {
                    "protocol": "https",
                    "port": 443,
                    "destination": "0.0.0.0/0"
                }
            ]
        }
    },
    "encryption": {
        "dynamodb_encryption": True,
        "s3_encryption": "AES256",
        "lambda_env_encryption": True
    }
}
```

## 📈 Monitoring & Observability

### Built-in Monitoring
Each template includes comprehensive monitoring:

```python
# Monitoring setup
class TemplateMonitoring:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        
    def setup_dashboards(self):
        """Create monitoring dashboards"""
        
        dashboard_config = {
            "widgets": [
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            ["AWS/Lambda", "Duration"],
                            ["AWS/Lambda", "Errors"],
                            ["AWS/Lambda", "Invocations"],
                            ["GenAI/Custom", "ResponseQuality"],
                            ["GenAI/Custom", "TokenUsage"],
                            ["GenAI/Custom", "CostPerRequest"]
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": "us-east-1",
                        "title": "GenAI Application Metrics"
                    }
                }
            ]
        }
        
        self.cloudwatch.put_dashboard(
            DashboardName="GenAI-Template-Dashboard",
            DashboardBody=json.dumps(dashboard_config)
        )
    
    def setup_alarms(self):
        """Create CloudWatch alarms"""
        
        alarms = [
            {
                "AlarmName": "GenAI-HighErrorRate",
                "MetricName": "Errors",
                "Threshold": 5.0,
                "ComparisonOperator": "GreaterThanThreshold"
            },
            {
                "AlarmName": "GenAI-HighLatency", 
                "MetricName": "Duration",
                "Threshold": 30000,  # 30 seconds
                "ComparisonOperator": "GreaterThanThreshold"
            }
        ]
        
        for alarm in alarms:
            self.cloudwatch.put_metric_alarm(**alarm)
```

## 💰 Cost Optimization

### Cost Management Features
- **Resource right-sizing** based on usage patterns
- **Auto-scaling** to match demand
- **Reserved capacity** for predictable workloads
- **Cost monitoring** and alerting

### Cost Optimization Script
```bash
#!/bin/bash
# scripts/optimize-costs.sh

# Analyze Lambda function performance
aws logs filter-log-events \
  --log-group-name "/aws/lambda/genai-processor" \
  --start-time $(date -d '7 days ago' +%s)000 \
  --filter-pattern "[REPORT]" \
  | jq '.events[].message' \
  | grep -E "(Duration|Billed Duration|Memory Size|Max Memory Used)" \
  > lambda-performance.log

# Analyze DynamoDB usage
aws dynamodb describe-table --table-name genai-sessions \
  | jq '.Table.BillingModeSummary'

# Generate cost report
python scripts/generate-cost-report.py
```

## 🧪 Testing Framework

### Comprehensive Testing
Each template includes:

```python
# tests/integration/test_genai_workflow.py
import pytest
import boto3
from moto import mock_bedrock, mock_dynamodb

class TestGenAIWorkflow:
    @mock_bedrock
    @mock_dynamodb  
    def test_end_to_end_workflow(self):
        """Test complete GenAI workflow"""
        
        # Setup test environment
        self.setup_test_resources()
        
        # Test user interaction
        response = self.client.post('/generate', json={
            'prompt': 'Test prompt',
            'model_id': 'test-model'
        })
        
        # Validate response
        assert response.status_code == 200
        assert 'response' in response.json()
        assert response.json()['confidence_score'] > 0.8
        
    def test_error_handling(self):
        """Test error scenarios"""
        
        # Test invalid input
        response = self.client.post('/generate', json={
            'prompt': '',  # Empty prompt
            'model_id': 'invalid-model'
        })
        
        assert response.status_code == 400
        assert 'error' in response.json()
        
    def test_performance_benchmarks(self):
        """Test performance requirements"""
        
        start_time = time.time()
        
        response = self.client.post('/generate', json={
            'prompt': 'Performance test prompt',
            'model_id': 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        })
        
        response_time = time.time() - start_time
        
        assert response_time < 2.0  # Max 2 seconds
        assert response.status_code == 200
```

---

## 🔗 Template Selection Guide

| Template | Complexity | Setup Time | Best For |
|----------|------------|------------|----------|
| **Bedrock Chatbot** | Low | 1-2 hours | Interactive AI assistants |
| **RAG Knowledge Base** | Medium | 4-6 hours | Document Q&A systems |
| **Document Analysis** | Medium | 3-4 hours | Automated document processing |
| **Multi-Agent Workflow** | High | 8-12 hours | Complex automation tasks |
| **Real-Time Analytics** | High | 6-8 hours | Streaming data analysis |
| **Multi-Agentic E-Commerce** | High | 12-16 hours | E-commerce platforms, retail automation |

---

**Ready to accelerate your GenAI development? Choose a template and start building! 🚀**

## 🔗 Next Steps

1. **[Choose a Template](./bedrock-chatbot/)** - Select the best template for your use case
2. **[Review Architecture](./architecture/)** - Understand the solution design
3. **[Deploy and Test](./deployment/)** - Get your solution running
4. **[Customize and Extend](./customization/)** - Adapt to your specific needs

---

**Transform your ideas into production-ready GenAI solutions in hours, not weeks! 💪**
