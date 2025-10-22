# 🏗️ Multi-Agentic E-Commerce Infrastructure

> **Terraform infrastructure for AWS multi-agentic e-commerce platform**

## 📋 Overview

This Terraform configuration deploys a comprehensive multi-agentic e-commerce platform on AWS using Bedrock Agents, Lambda functions, RDS, ElastiCache, OpenSearch, and other AWS services.

## 🏗️ Architecture

### **Infrastructure Components**

- **VPC**: Multi-AZ VPC with public, private, and database subnets
- **RDS**: PostgreSQL database with encryption and monitoring
- **ElastiCache**: Redis cluster for caching
- **OpenSearch**: Serverless search and analytics
- **Lambda**: Serverless functions for agent actions
- **Bedrock**: AI agents and knowledge bases
- **API Gateway**: RESTful API endpoints
- **S3**: Data and log storage with lifecycle policies
- **KMS**: Encryption key management
- **CloudWatch**: Monitoring and logging
- **SNS/SQS**: Event-driven messaging

## 🚀 Quick Start

### **Prerequisites**

```bash
# Required tools
terraform >= 1.0
aws-cli >= 2.0
aws-vault (optional, for credential management)
```

### **Configuration**

1. **Clone and navigate to the infrastructure directory:**
   ```bash
   cd infrastructure/terraform
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   # OR
   aws-vault add your-profile
   ```

3. **Initialize Terraform:**
   ```bash
   terraform init
   ```

4. **Plan the deployment:**
   ```bash
   terraform plan -var-file="environments/dev.tfvars"
   ```

5. **Deploy the infrastructure:**
   ```bash
   terraform apply -var-file="environments/dev.tfvars"
   ```

## 🌍 Environment Configuration

### **Available Environments**

| Environment | Configuration File | Purpose |
|-------------|-------------------|---------|
| **Development** | `environments/dev.tfvars` | Local development and testing |
| **Staging** | `environments/staging.tfvars` | Pre-production testing |
| **Production** | `environments/prod.tfvars` | Live production environment |

### **Environment-Specific Deployment**

```bash
# Development
terraform apply -var-file="environments/dev.tfvars"

# Staging
terraform apply -var-file="environments/staging.tfvars"

# Production
terraform apply -var-file="environments/prod.tfvars"
```

## 📊 Infrastructure Modules

### **Core Modules**

| Module | Purpose | Resources |
|--------|---------|-----------|
| **VPC** | Network infrastructure | VPC, subnets, gateways, security groups |
| **KMS** | Encryption management | KMS keys, policies |
| **S3** | Object storage | Data and log buckets with policies |
| **RDS** | Database | PostgreSQL with encryption and monitoring |
| **ElastiCache** | Caching layer | Redis cluster |
| **OpenSearch** | Search and analytics | Serverless OpenSearch collection |
| **Lambda** | Serverless compute | Agent action functions |
| **Bedrock** | AI agents | Agents and knowledge bases |
| **API Gateway** | API management | RESTful endpoints |
| **CloudWatch** | Monitoring | Dashboards, alarms, log groups |
| **SNS** | Notifications | Topics and subscriptions |
| **SQS** | Message queuing | Queues for event processing |

## 🔧 Configuration Options

### **Key Variables**

```hcl
# Environment Configuration
environment = "dev"           # dev, staging, prod
aws_region  = "us-east-1"    # AWS region

# VPC Configuration
vpc_cidr = "10.0.0.0/16"     # VPC CIDR block
availability_zones_count = 3  # Number of AZs

# Database Configuration
db_instance_class = "db.t3.medium"  # RDS instance type
db_allocated_storage = 100           # Initial storage (GB)
db_max_allocated_storage = 1000     # Max storage (GB)

# Cache Configuration
redis_node_type = "cache.t3.micro"  # ElastiCache node type
redis_num_cache_nodes = 2           # Number of cache nodes

# Lambda Configuration
lambda_memory_size = 1024           # Lambda memory (MB)
lambda_timeout = 300                # Lambda timeout (seconds)

# Bedrock Configuration
bedrock_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
bedrock_embedding_model_id = "amazon.titan-embed-text-v1"
```

### **Security Configuration**

```hcl
# Encryption
enable_encryption = true      # Enable encryption for all resources
kms_key_id = "alias/..."     # KMS key for encryption

# Backup
enable_backup = true         # Enable automated backups
backup_retention_days = 7    # Backup retention period

# Monitoring
enable_detailed_monitoring = true    # Detailed RDS monitoring
enable_performance_insights = true   # RDS Performance Insights
enable_enhanced_monitoring = true    # Enhanced monitoring
```

## 📈 Cost Optimization

### **Estimated Monthly Costs**

| Environment | Estimated Cost | Components |
|-------------|---------------|------------|
| **Development** | $100-200 | Small instances, minimal resources |
| **Staging** | $300-500 | Medium instances, full monitoring |
| **Production** | $800-1500 | Large instances, high availability |

### **Cost Optimization Features**

- **Auto-scaling**: Dynamic resource allocation
- **Reserved Instances**: Cost-effective for predictable workloads
- **Spot Instances**: Reduced costs for non-critical workloads
- **Storage Lifecycle**: Automatic data archiving
- **Resource Tagging**: Cost allocation and tracking

## 🔒 Security Features

### **Built-in Security**

- **Encryption**: End-to-end encryption with KMS
- **Network Security**: VPC isolation, security groups, NACLs
- **Access Control**: IAM roles and policies
- **Secrets Management**: AWS Secrets Manager integration
- **Audit Logging**: Comprehensive activity tracking
- **Compliance**: GDPR, CCPA, PCI DSS ready

### **Security Best Practices**

```hcl
# Network Security
enable_nat_gateway = true     # Private subnet internet access
enable_vpn_gateway = false   # VPN access (optional)

# Database Security
multi_az = true              # High availability
deletion_protection = true   # Prevent accidental deletion
backup_retention_period = 7  # Automated backups

# Monitoring Security
enable_audit_logging = true      # Audit trail
enable_data_classification = true # Data governance
```

## 📊 Monitoring and Observability

### **Monitoring Stack**

- **CloudWatch**: Metrics, logs, and alarms
- **X-Ray**: Distributed tracing
- **Performance Insights**: Database performance
- **Custom Dashboards**: Real-time monitoring
- **Automated Alerts**: Incident response

### **Key Metrics**

| Metric | Threshold | Action |
|--------|-----------|--------|
| **CPU Utilization** | > 80% | Scale up |
| **Memory Usage** | > 85% | Scale up |
| **Database Connections** | > 80% | Alert |
| **Error Rate** | > 1% | Alert |
| **Response Time** | > 2s | Alert |

## 🚀 Deployment Strategies

### **Deployment Options**

1. **Manual Deployment**
   ```bash
   terraform apply -var-file="environments/prod.tfvars"
   ```

2. **Automated Deployment**
   ```bash
   # Using CI/CD pipeline
   terraform plan -var-file="environments/prod.tfvars"
   terraform apply -auto-approve -var-file="environments/prod.tfvars"
   ```

3. **Blue/Green Deployment**
   ```bash
   # Deploy to staging first
   terraform apply -var-file="environments/staging.tfvars"
   
   # Validate and promote to production
   terraform apply -var-file="environments/prod.tfvars"
   ```

### **State Management**

```hcl
# Backend configuration (recommended for production)
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "multi-agent-ecommerce/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

## 🧪 Testing

### **Infrastructure Testing**

```bash
# Validate configuration
terraform validate

# Plan changes
terraform plan -var-file="environments/dev.tfvars"

# Apply changes
terraform apply -var-file="environments/dev.tfvars"

# Destroy resources (cleanup)
terraform destroy -var-file="environments/dev.tfvars"
```

### **Testing Checklist**

- [ ] Terraform configuration validates
- [ ] All resources deploy successfully
- [ ] Security groups allow expected traffic
- [ ] Database connectivity works
- [ ] Lambda functions execute
- [ ] Bedrock agents respond
- [ ] Monitoring dashboards load
- [ ] Alerts trigger correctly

## 🔧 Troubleshooting

### **Common Issues**

1. **Resource Limits**
   ```bash
   # Check AWS service limits
   aws service-quotas get-service-quota --service-code ec2 --quota-code L-0263D0A3
   ```

2. **Permission Issues**
   ```bash
   # Verify IAM permissions
   aws sts get-caller-identity
   ```

3. **State Conflicts**
   ```bash
   # Refresh state
   terraform refresh
   
   # Import existing resources
   terraform import aws_instance.example i-1234567890abcdef0
   ```

### **Debug Commands**

```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform apply

# Check resource state
terraform state list
terraform state show aws_instance.example

# Validate configuration
terraform validate
terraform fmt -check
```

## 📚 Documentation

### **Additional Resources**

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)

### **Module Documentation**

Each module includes detailed documentation:
- `modules/vpc/README.md` - VPC configuration
- `modules/rds/README.md` - Database setup
- `modules/bedrock/README.md` - AI agents configuration
- `modules/lambda/README.md` - Serverless functions

## 🤝 Contributing

### **Development Workflow**

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### **Code Standards**

- Use consistent naming conventions
- Add comments for complex logic
- Validate all configurations
- Test in development first
- Document any breaking changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../../LICENSE) file for details.

## 🆘 Support

- **Documentation**: [README.md](./README.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/aws-genai-labs-builder/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/aws-genai-labs-builder/discussions)

---

**Ready to deploy your multi-agentic e-commerce platform? Start with the development environment and scale up! 🚀**
