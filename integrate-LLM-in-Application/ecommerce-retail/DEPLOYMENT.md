# Deployment Guide

This guide covers deploying the E-Commerce AI Platform to production environments.

## Prerequisites

- AWS Account with appropriate permissions
- Terraform 1.5+ installed
- Docker and Docker Compose
- AWS CLI configured
- Domain name (optional, for production)

## Local Development

### Quick Start

1. **Clone and setup environment**

```bash
cd ecommerce-retail
cp config/.env.example config/.env
# Edit config/.env with your API keys
```

2. **Start services with Docker Compose**

```bash
docker-compose up -d
```

3. **Access services**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Manual Setup

1. **Backend Setup**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

2. **Frontend Setup**

```bash
cd frontend
npm install
npm start
```

## AWS Deployment

### Infrastructure Setup with Terraform

1. **Initialize Terraform**

```bash
cd infrastructure/terraform
terraform init
```

2. **Configure Variables**

Edit `terraform.tfvars`:

```hcl
aws_region = "us-east-1"
environment = "production"
openai_api_key = "your-key"
bedrock_enabled = true
```

3. **Plan and Apply**

```bash
terraform plan
terraform apply
```

### Infrastructure Components

The Terraform configuration creates:

- **VPC** with public and private subnets
- **RDS PostgreSQL** database
- **ElastiCache Redis** cluster
- **EC2** instances for application
- **Application Load Balancer**
- **S3** bucket for assets
- **IAM** roles and policies
- **CloudWatch** logging and monitoring

### Application Deployment

1. **Build Docker Images**

```bash
docker build -t ecommerce-backend:latest ./backend
docker build -t ecommerce-frontend:latest ./frontend
```

2. **Push to ECR**

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag ecommerce-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ecommerce-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ecommerce-backend:latest
```

3. **Deploy to ECS/EKS**

Follow your container orchestration platform's deployment process.

## Environment Configuration

### Required Environment Variables

```env
# Application
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379/0

# LLM Providers
OPENAI_API_KEY=sk-...
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# S3
AWS_S3_BUCKET=your-bucket-name
```

### Secrets Management

For production, use AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name ecommerce/api-keys \
  --secret-string '{"OPENAI_API_KEY":"..."}'
```

## Database Migration

1. **Run migrations**

```bash
cd backend
alembic upgrade head
```

2. **Seed initial data** (optional)

```bash
python scripts/seed_data.py
```

## Monitoring and Logging

### CloudWatch Setup

- Application logs are automatically sent to CloudWatch
- Set up CloudWatch alarms for:
  - API error rates
  - Response times
  - LLM API failures
  - Database connection issues

### Health Checks

- Liveness: `/api/v1/health/live`
- Readiness: `/api/v1/health/ready`
- Full health: `/api/v1/health`

## Scaling

### Horizontal Scaling

1. **Auto Scaling Groups**

Configure ASG for EC2 instances based on:
- CPU utilization
- Request count
- Response time

2. **Load Balancer**

Application Load Balancer distributes traffic across instances.

### Database Scaling

- Enable read replicas for read-heavy workloads
- Use connection pooling
- Implement database sharding if needed

## Security Best Practices

1. **Network Security**
   - Use VPC with private subnets
   - Security groups with least privilege
   - WAF for DDoS protection

2. **Data Security**
   - Encrypt data at rest (RDS encryption)
   - Encrypt data in transit (TLS)
   - Use AWS KMS for key management

3. **API Security**
   - Rate limiting
   - API authentication (JWT)
   - Input validation
   - CORS configuration

## Cost Optimization

1. **LLM Costs**
   - Use caching for common queries
   - Select appropriate models (GPT-3.5 for simple, GPT-4 for complex)
   - Batch requests when possible

2. **Infrastructure Costs**
   - Use reserved instances for production
   - Auto-scaling to reduce idle resources
   - S3 lifecycle policies for old data

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check security groups
   - Verify database credentials
   - Ensure database is accessible

2. **LLM API Errors**
   - Verify API keys
   - Check rate limits
   - Review error logs

3. **High Latency**
   - Enable caching
   - Optimize database queries
   - Use CDN for static assets

## Rollback Procedure

1. **Application Rollback**

```bash
# Revert to previous Docker image
docker tag ecommerce-backend:previous ecommerce-backend:latest
# Redeploy
```

2. **Database Rollback**

```bash
# Restore from backup
aws rds restore-db-instance-from-db-snapshot ...
```

## Backup and Recovery

1. **Database Backups**
   - Automated daily backups
   - Point-in-time recovery enabled
   - Cross-region replication

2. **Application Backups**
   - Infrastructure as Code (Terraform)
   - Configuration backups
   - Docker image registry

## Support

For issues or questions:
- Check logs in CloudWatch
- Review API documentation at `/docs`
- Contact DevOps team

