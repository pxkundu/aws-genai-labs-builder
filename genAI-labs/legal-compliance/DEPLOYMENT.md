# Legal Compliance AI Platform - Deployment Guide

## 🚀 Quick Start Deployment

This guide will help you deploy the Legal Compliance AI Platform to AWS using Terraform and Docker.

### Prerequisites

Before starting, ensure you have:

- **AWS Account** with appropriate permissions
- **AWS CLI** configured with your credentials
- **Terraform** >= 1.0 installed
- **Docker** and **Docker Compose** installed
- **Node.js** >= 18.0.0 installed
- **Python** >= 3.9 installed

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd genAI-labs/legal-compliance

# Copy environment template
cp .env.example .env
```

### Step 2: Configure Environment Variables

Edit `.env` file with your configuration:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id

# Database Configuration
DATABASE_NAME=legal_compliance
DATABASE_USERNAME=legal_user
DATABASE_PASSWORD=your-secure-password

# LLM API Keys
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key

# SSL Certificate (for production)
SSL_CERTIFICATE_ARN=arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012

# Domain Configuration (optional)
DOMAIN_NAME=your-domain.com
CREATE_DNS=true
```

### Step 3: Deploy Infrastructure

```bash
# Navigate to infrastructure directory
cd infrastructure

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan -var-file="environments/dev.tfvars"

# Deploy infrastructure
terraform apply -var-file="environments/dev.tfvars"

# Note the outputs for the next steps
terraform output
```

### Step 4: Build and Push Docker Images

```bash
# Return to project root
cd ..

# Login to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend image
docker build -f Dockerfile.backend -t legal-compliance-ai-backend .
docker tag legal-compliance-ai-backend:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/legal-compliance-ai-dev-backend:latest
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/legal-compliance-ai-dev-backend:latest

# Build and push frontend image
docker build -f Dockerfile.frontend -t legal-compliance-ai-frontend .
docker tag legal-compliance-ai-frontend:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/legal-compliance-ai-dev-frontend:latest
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/legal-compliance-ai-dev-frontend:latest
```

### Step 5: Deploy Applications

```bash
# Update ECS services to use new images
aws ecs update-service --cluster legal-compliance-ai-dev-cluster --service legal-compliance-ai-dev-backend --force-new-deployment
aws ecs update-service --cluster legal-compliance-ai-dev-cluster --service legal-compliance-ai-dev-frontend --force-new-deployment

# Check deployment status
aws ecs describe-services --cluster legal-compliance-ai-dev-cluster --services legal-compliance-ai-dev-backend legal-compliance-ai-dev-frontend
```

### Step 6: Verify Deployment

```bash
# Get application URL
ALB_DNS=$(terraform output -raw alb_dns_name)
echo "Application URL: https://$ALB_DNS"

# Test health endpoint
curl https://$ALB_DNS/api/v1/health

# Test legal question endpoint
curl -X POST https://$ALB_DNS/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the requirements for a valid contract?",
    "jurisdiction": "US",
    "practice_area": "contract"
  }'
```

## 🏗️ Detailed Deployment Options

### Local Development

For local development, use Docker Compose:

```bash
# Start all services locally
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Staging Deployment

```bash
# Deploy to staging
terraform apply -var-file="environments/staging.tfvars"

# Run tests
npm run test:e2e

# Deploy applications
./scripts/deploy-staging.sh
```

### Production Deployment

```bash
# Deploy to production (with confirmation)
terraform apply -var-file="environments/prod.tfvars"

# Run production tests
npm run test:production

# Deploy applications with blue-green deployment
./scripts/deploy-production.sh
```

## 🔧 Configuration Options

### Infrastructure Configuration

Edit `infrastructure/variables.tf` to customize:

```hcl
# Database Configuration
variable "database_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.small"  # Upgrade for production
}

# Scaling Configuration
variable "min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 2  # Increase for production
}

variable "max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 20  # Increase for production
}
```

### Application Configuration

Edit `backend/core/config.py`:

```python
# Production settings
class ProductionSettings(Settings):
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Increase rate limits for production
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 3600
    
    # Enable monitoring
    SENTRY_DSN: str = "your-sentry-dsn"
    PROMETHEUS_ENABLED: bool = True
```

## 📊 Monitoring and Observability

### CloudWatch Dashboards

Access the CloudWatch dashboard:

```bash
# Get dashboard URL
DASHBOARD_URL=$(terraform output -raw cloudwatch_dashboard_url)
echo "Dashboard: $DASHBOARD_URL"
```

### Key Metrics to Monitor

- **ECS Service Health**: Task count, CPU/Memory utilization
- **ALB Metrics**: Request count, response times, error rates
- **Database Metrics**: Connection count, CPU utilization, storage
- **Redis Metrics**: Memory usage, hit ratio, connection count
- **LLM API Metrics**: Response times, error rates, token usage

### Logging

```bash
# View application logs
aws logs tail /aws/ecs/legal-compliance-ai-dev-backend --follow

# View error logs only
aws logs filter-log-events \
  --log-group-name /aws/ecs/legal-compliance-ai-dev-backend \
  --filter-pattern "ERROR"
```

## 🔒 Security Configuration

### SSL/TLS Setup

1. **Request SSL Certificate**:
```bash
# Request certificate via AWS Certificate Manager
aws acm request-certificate \
  --domain-name your-domain.com \
  --validation-method DNS \
  --region us-east-1
```

2. **Update Terraform variables**:
```hcl
ssl_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012"
```

### Security Groups

Review and update security groups in `infrastructure/modules/security/main.tf`:

```hcl
# Restrict database access
resource "aws_security_group_rule" "database_inbound" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  security_group_id = aws_security_group.database.id
  source_security_group_id = aws_security_group.ecs.id  # Only ECS can access
}
```

### Secrets Management

```bash
# Update API keys in Secrets Manager
aws secretsmanager update-secret \
  --secret-id legal-compliance-ai-dev-openai-api-key \
  --secret-string "your-new-openai-key"

# Rotate secrets
aws secretsmanager rotate-secret \
  --secret-id legal-compliance-ai-dev-database-password
```

## 🚨 Troubleshooting

### Common Issues

#### 1. ECS Tasks Failing to Start

```bash
# Check task definition
aws ecs describe-task-definition --task-definition legal-compliance-ai-dev-backend

# Check service events
aws ecs describe-services --cluster legal-compliance-ai-dev-cluster --services legal-compliance-ai-dev-backend

# Check logs
aws logs tail /aws/ecs/legal-compliance-ai-dev-backend --follow
```

#### 2. Database Connection Issues

```bash
# Test database connectivity
aws rds describe-db-instances --db-instance-identifier legal-compliance-ai-dev-db

# Check security groups
aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx
```

#### 3. Load Balancer Health Checks Failing

```bash
# Check target group health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/legal-compliance-ai-dev-tg/xxxxxxxxx

# Check security group rules
aws ec2 describe-security-group-rules --group-ids sg-xxxxxxxxx
```

### Performance Optimization

#### 1. Database Optimization

```bash
# Enable performance insights
aws rds modify-db-instance \
  --db-instance-identifier legal-compliance-ai-dev-db \
  --enable-performance-insights \
  --performance-insights-retention-period 7
```

#### 2. Caching Optimization

```bash
# Check Redis metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name CacheHitRate \
  --dimensions Name=CacheClusterId,Value=legal-compliance-ai-dev-redis \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

## 📈 Scaling and Performance

### Auto Scaling Configuration

```bash
# Update auto scaling settings
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/legal-compliance-ai-dev-cluster/legal-compliance-ai-dev-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name legal-compliance-ai-dev-backend-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

### Cost Optimization

```bash
# Enable cost allocation tags
aws ce create-cost-category-definition \
  --name "Legal Compliance AI" \
  --rules file://cost-category-rules.json

# Set up billing alerts
aws budgets create-budget \
  --account-id 123456789012 \
  --budget file://budget-config.json
```

## 🔄 CI/CD Pipeline

### GitHub Actions Setup

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Legal Compliance AI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          npm install
          npm test
          cd backend && python -m pytest

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
          aws-region: us-east-1
      
      - name: Deploy infrastructure
        run: |
          cd infrastructure
          terraform init
          terraform apply -auto-approve
      
      - name: Deploy applications
        run: |
          ./scripts/deploy-production.sh
```

## 📚 Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

## 🆘 Support

For deployment issues:

1. Check the troubleshooting section above
2. Review CloudWatch logs
3. Check AWS service health dashboard
4. Open an issue in the repository

---

**Ready to deploy your Legal Compliance AI Platform! 🚀**
