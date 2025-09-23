# 🚀 GenAI Customer Service Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the GenAI Customer Service solution to production environments using AWS services.

## Prerequisites

### AWS Account Setup
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Required AWS services enabled:
  - Amazon Bedrock (with Claude model access)
  - Amazon Comprehend
  - Amazon Transcribe
  - Amazon Polly
  - Amazon DynamoDB
  - Amazon S3
  - Amazon OpenSearch
  - AWS Lambda
  - Amazon API Gateway
  - Amazon ElastiCache

### Local Environment
- Python 3.11+
- Node.js 18+
- AWS CDK or Terraform
- Docker (optional)

## Deployment Options

### Option 1: AWS CDK Deployment

#### 1.1 Setup CDK Environment
```bash
# Install AWS CDK
npm install -g aws-cdk

# Bootstrap CDK (first time only)
cdk bootstrap

# Install dependencies
cd infrastructure/cdk
pip install -r requirements.txt
```

#### 1.2 Deploy Infrastructure
```bash
# Deploy the stack
cdk deploy GenaiCustomerServiceStack

# Verify deployment
cdk list
```

#### 1.3 Configure Environment Variables
After deployment, update your environment variables with the outputs:
```bash
# Get stack outputs
aws cloudformation describe-stacks \
  --stack-name GenaiCustomerServiceStack \
  --query 'Stacks[0].Outputs'
```

### Option 2: Terraform Deployment

#### 2.1 Setup Terraform
```bash
# Initialize Terraform
cd infrastructure/terraform
terraform init

# Plan deployment
terraform plan

# Deploy infrastructure
terraform apply
```

#### 2.2 Get Outputs
```bash
# Get outputs
terraform output
```

### Option 3: Docker Deployment

#### 3.1 Build and Deploy with Docker Compose
```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

## Production Configuration

### Environment Variables
Create a production environment file:

```env
# Production Configuration
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=your-production-secret-key

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-production-access-key
AWS_SECRET_ACCESS_KEY=your-production-secret-key

# Database Configuration
MONGODB_URL=mongodb://your-production-mongodb:27017
REDIS_URL=redis://your-production-redis:6379

# AI Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
CONFIDENCE_THRESHOLD=0.85
ESCALATION_THRESHOLD=0.7

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
```

### Security Configuration

#### SSL/TLS Setup
```bash
# Generate SSL certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Update nginx configuration
cp nginx.conf.production nginx.conf
```

#### IAM Roles and Policies
```bash
# Create IAM role for Lambda
aws iam create-role --role-name GenAICustomerServiceRole

# Attach policies
aws iam attach-role-policy \
  --role-name GenAICustomerServiceRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

## Database Setup

### MongoDB Configuration
```bash
# Connect to MongoDB
mongo mongodb://your-mongodb-endpoint:27017

# Create database and collections
use customer_service
db.createCollection("conversations")
db.createCollection("customers")
db.createCollection("knowledge_base")

# Create indexes
db.conversations.createIndex({"customer_id": 1, "session_id": 1})
db.customers.createIndex({"customer_id": 1})
db.knowledge_base.createIndex({"title": "text", "content": "text"})
```

### Redis Configuration
```bash
# Connect to Redis
redis-cli -h your-redis-endpoint -p 6379

# Configure Redis
CONFIG SET maxmemory 1gb
CONFIG SET maxmemory-policy allkeys-lru
```

## Monitoring and Logging

### CloudWatch Setup
```bash
# Create log groups
aws logs create-log-group --log-group-name /aws/lambda/genai-cs-api
aws logs create-log-group --log-group-name /aws/lambda/genai-cs-ai-processing

# Set retention policy
aws logs put-retention-policy \
  --log-group-name /aws/lambda/genai-cs-api \
  --retention-in-days 30
```

### Monitoring Dashboard
```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name GenAI-Customer-Service \
  --dashboard-body file://dashboard.json
```

## Performance Optimization

### Lambda Configuration
```python
# Optimize Lambda settings
{
    "MemorySize": 2048,
    "Timeout": 300,
    "ReservedConcurrency": 50,
    "Environment": {
        "Variables": {
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1"
        }
    }
}
```

### API Gateway Optimization
```bash
# Enable caching
aws apigateway create-deployment \
  --rest-api-id your-api-id \
  --stage-name production \
  --cache-cluster-enabled \
  --cache-cluster-size 0.5
```

## Scaling Configuration

### Auto Scaling
```yaml
# Auto Scaling configuration
AutoScalingTarget:
  Type: AWS::ApplicationAutoScaling::ScalableTarget
  Properties:
    MinCapacity: 2
    MaxCapacity: 100
    ResourceId: !Sub "table/${DynamoDBTable}"
    ScalableDimension: dynamodb:table:ReadCapacityUnits
    ServiceNamespace: dynamodb
```

### Load Balancing
```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name genai-cs-alb \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-12345
```

## Backup and Recovery

### Database Backup
```bash
# MongoDB backup
mongodump --host your-mongodb-endpoint --db customer_service --out backup/

# Redis backup
redis-cli --rdb backup.rdb
```

### Infrastructure Backup
```bash
# Terraform state backup
terraform state pull > terraform-state.json

# CDK state backup
cdk synth > cdk-output.json
```

## Security Hardening

### Network Security
```bash
# Create security groups
aws ec2 create-security-group \
  --group-name genai-cs-sg \
  --description "Security group for GenAI Customer Service"

# Configure security group rules
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

### Encryption
```bash
# Enable encryption at rest
aws kms create-key --description "GenAI Customer Service encryption key"

# Enable encryption in transit
aws s3api put-bucket-encryption \
  --bucket your-bucket-name \
  --server-side-encryption-configuration file://encryption.json
```

## Health Checks

### Application Health
```bash
# Health check endpoint
curl -f http://your-api-endpoint/api/v1/health

# Database connectivity
curl -f http://your-api-endpoint/api/v1/health/database

# AI services health
curl -f http://your-api-endpoint/api/v1/health/ai-services
```

### Infrastructure Health
```bash
# Check Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `genai-cs`)]'

# Check DynamoDB tables
aws dynamodb list-tables --query 'TableNames[?contains(@, `genai-cs`)]'

# Check API Gateway
aws apigateway get-rest-apis --query 'items[?contains(name, `GenAI`)]'
```

## Troubleshooting

### Common Issues

#### Lambda Timeout
```bash
# Increase timeout
aws lambda update-function-configuration \
  --function-name genai-cs-api \
  --timeout 300
```

#### Memory Issues
```bash
# Increase memory
aws lambda update-function-configuration \
  --function-name genai-cs-api \
  --memory-size 2048
```

#### Database Connection Issues
```bash
# Check VPC configuration
aws ec2 describe-vpcs --vpc-ids vpc-12345

# Check security groups
aws ec2 describe-security-groups --group-ids sg-12345
```

## Rollback Procedures

### Application Rollback
```bash
# Rollback Lambda function
aws lambda update-function-code \
  --function-name genai-cs-api \
  --zip-file fileb://previous-version.zip
```

### Infrastructure Rollback
```bash
# Terraform rollback
terraform plan -destroy
terraform destroy

# CDK rollback
cdk destroy GenaiCustomerServiceStack
```

## Maintenance

### Regular Tasks
- Monitor CloudWatch metrics
- Review and rotate API keys
- Update dependencies
- Backup databases
- Review security groups
- Update SSL certificates

### Performance Monitoring
```bash
# Monitor API Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=GenAI-Customer-Service-API \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Support and Resources

### Documentation
- [AWS GenAI Documentation](https://docs.aws.amazon.com/bedrock/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://create-react-app.dev/docs/production-build/)

### Support Channels
- AWS Support
- Community Forums
- GitHub Issues

---

**Deployment completed successfully! 🎉**

Your GenAI Customer Service solution is now running in production with:
- ✅ Scalable infrastructure
- ✅ AI-powered customer support
- ✅ Real-time monitoring
- ✅ Security best practices
- ✅ High availability
