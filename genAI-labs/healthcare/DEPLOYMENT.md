# Healthcare ChatGPT Clone - Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Deployment](#detailed-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Post-Deployment Setup](#post-deployment-setup)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

## Prerequisites

### Required Tools

Before deploying the Healthcare ChatGPT Clone, ensure you have the following tools installed:

- **AWS CLI v2**: For AWS resource management
- **Terraform**: For infrastructure provisioning
- **Docker**: For container management
- **Git**: For source code management
- **Python 3.9+**: For local development (optional)

### AWS Account Setup

1. **Create AWS Account**: Sign up for an AWS account if you don't have one
2. **Configure AWS CLI**: Set up AWS credentials
   ```bash
   aws configure
   ```
3. **Create IAM User**: Create a dedicated IAM user with appropriate permissions
4. **Generate Key Pair**: Create an EC2 key pair for SSH access

### Required Permissions

The IAM user needs the following permissions:
- EC2 (Full Access)
- RDS (Full Access)
- S3 (Full Access)
- VPC (Full Access)
- IAM (Limited - for role creation)
- CloudWatch (Full Access)
- Secrets Manager (Full Access)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd aws-genai-labs-builder/genAI-labs/healthcare
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"
export AWS_REGION="us-east-1"
export ENVIRONMENT="dev"
```

### 3. Deploy Infrastructure

```bash
cd infrastructure
terraform init
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"
```

### 4. Deploy Application

```bash
./scripts/deployment/deploy.sh dev
```

### 5. Access the Application

- **OpenWebUI**: `http://<ec2-public-ip>:8080`
- **Backend API**: `http://<ec2-public-ip>:8000`
- **API Documentation**: `http://<ec2-public-ip>:8000/docs`

## Detailed Deployment

### Step 1: Infrastructure Setup

#### 1.1 Configure Terraform Backend

Create an S3 bucket for Terraform state:

```bash
aws s3 mb s3://healthcare-chatgpt-terraform-state-$(date +%s)
```

#### 1.2 Initialize Terraform

```bash
cd infrastructure
terraform init
```

#### 1.3 Plan Deployment

```bash
terraform plan -var-file="environments/dev.tfvars"
```

#### 1.4 Apply Infrastructure

```bash
terraform apply -var-file="environments/dev.tfvars"
```

### Step 2: Application Deployment

#### 2.1 Run Deployment Script

```bash
./scripts/deployment/deploy.sh dev
```

#### 2.2 Verify Deployment

Check if services are running:

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@<ec2-public-ip>

# Check Docker containers
sudo docker ps

# Check application logs
sudo docker logs healthcare-openwebui
sudo docker logs healthcare-backend-api
```

### Step 3: Knowledge Base Setup

#### 3.1 Upload Knowledge Base

```bash
# Get S3 bucket name from Terraform outputs
BUCKET_NAME=$(cd infrastructure && terraform output -raw knowledge_base_bucket_name)

# Upload sample knowledge base
aws s3 sync data/knowledge_base/ s3://$BUCKET_NAME/
```

#### 3.2 Configure Knowledge Base

Access the knowledge base management interface and configure:
- Medical guidelines
- FAQ documents
- Healthcare policies
- Procedure documents

## Environment Configuration

### Development Environment

The development environment is configured for:
- Single EC2 instance (t3.medium)
- RDS Aurora Serverless (0.5-4 ACU)
- S3 bucket for knowledge base
- Basic monitoring

### Staging Environment

The staging environment includes:
- Load balancer
- Multiple EC2 instances
- RDS Aurora cluster
- Enhanced monitoring
- SSL certificates

### Production Environment

The production environment features:
- High availability setup
- Auto-scaling groups
- Multi-AZ RDS cluster
- Comprehensive monitoring
- Security hardening

## Post-Deployment Setup

### 1. SSL Certificate Setup

For production environments, set up SSL certificates:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 2. Domain Configuration

Configure your domain to point to the EC2 instance:

```bash
# Get EC2 public IP
EC2_IP=$(cd infrastructure && terraform output -raw ec2_public_ip)

# Update DNS records
# A record: your-domain.com -> $EC2_IP
```

### 3. Security Hardening

#### 3.1 Update Security Groups

Restrict access to specific IP ranges:

```bash
# Update security group rules
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
```

#### 3.2 Configure Firewall

```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@<ec2-public-ip>

# Configure UFW
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8080
sudo ufw allow 8000
```

### 4. Monitoring Setup

#### 4.1 Configure CloudWatch Alarms

```bash
# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "High CPU Utilization" \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

#### 4.2 Set Up Log Aggregation

```bash
# Install CloudWatch agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
  -s
```

## Troubleshooting

### Common Issues

#### 1. Terraform State Lock

If Terraform state is locked:

```bash
# Force unlock (use with caution)
terraform force-unlock <lock-id>
```

#### 2. EC2 Instance Not Starting

Check EC2 instance logs:

```bash
# Get instance ID
INSTANCE_ID=$(cd infrastructure && terraform output -raw ec2_instance_id)

# Get system logs
aws ec2 get-console-output --instance-id $INSTANCE_ID
```

#### 3. Application Not Accessible

Check security groups and network ACLs:

```bash
# Check security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx

# Check network ACLs
aws ec2 describe-network-acls --network-acl-ids acl-xxxxxxxxx
```

#### 4. Database Connection Issues

Check RDS connectivity:

```bash
# Get RDS endpoint
RDS_ENDPOINT=$(cd infrastructure && terraform output -raw rds_cluster_endpoint)

# Test connection
psql -h $RDS_ENDPOINT -U postgres -d healthcare_chat
```

### Log Analysis

#### Application Logs

```bash
# View OpenWebUI logs
sudo docker logs healthcare-openwebui

# View backend API logs
sudo docker logs healthcare-backend-api

# View system logs
sudo journalctl -u healthcare-chatgpt.service
```

#### Infrastructure Logs

```bash
# View CloudWatch logs
aws logs describe-log-groups
aws logs get-log-events --log-group-name /aws/ec2/healthcare-chatgpt-dev
```

## Maintenance

### Regular Maintenance Tasks

#### 1. Database Maintenance

```bash
# Connect to database
psql -h $RDS_ENDPOINT -U postgres -d healthcare_chat

# Run maintenance queries
VACUUM ANALYZE;
REINDEX DATABASE healthcare_chat;
```

#### 2. Application Updates

```bash
# Pull latest changes
git pull origin main

# Update application
./scripts/deployment/deploy.sh dev
```

#### 3. Security Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
sudo docker pull ghcr.io/open-webui/open-webui:main
sudo docker-compose pull
sudo docker-compose up -d
```

### Backup Procedures

#### 1. Database Backup

```bash
# Create manual backup
aws rds create-db-cluster-snapshot \
  --db-cluster-identifier healthcare-chatgpt-dev-aurora-cluster \
  --db-cluster-snapshot-identifier manual-backup-$(date +%Y%m%d)
```

#### 2. Application Backup

```bash
# Backup application data
sudo docker exec healthcare-openwebui tar -czf /tmp/backup.tar.gz /app/backend/data
sudo docker cp healthcare-openwebui:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz
```

#### 3. Configuration Backup

```bash
# Backup Terraform state
aws s3 cp terraform.tfstate s3://your-terraform-state-bucket/backups/
```

### Monitoring and Alerting

#### 1. Set Up Alerts

```bash
# Create SNS topic
aws sns create-topic --name healthcare-chatgpt-alerts

# Subscribe to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:healthcare-chatgpt-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

#### 2. Configure CloudWatch Alarms

```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "High CPU Utilization" \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:healthcare-chatgpt-alerts
```

## Support and Resources

### Documentation

- [Architecture Guide](architecture.md)
- [Customization Guide](CUSTOMIZATION.md)
- [API Documentation](docs/api/)
- [User Guide](docs/user-guide/)

### Community Support

- GitHub Issues: Report bugs and request features
- Documentation: Comprehensive guides and tutorials
- Examples: Sample configurations and use cases

### Professional Support

For enterprise support and custom implementations, contact the development team.

## Conclusion

This deployment guide provides comprehensive instructions for deploying the Healthcare ChatGPT Clone application. Follow the steps carefully, and refer to the troubleshooting section if you encounter any issues.

For additional support or questions, please refer to the documentation or create an issue in the project repository.
