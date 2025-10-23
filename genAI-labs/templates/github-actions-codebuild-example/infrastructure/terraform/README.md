# 🏗️ GitHub Actions CodeBuild Infrastructure

> **Terraform infrastructure for AWS GitHub Actions CodeBuild integration**

## 📋 Overview

This Terraform configuration deploys a comprehensive GitHub Actions CodeBuild integration platform on AWS, providing secure, scalable, and monitored CI/CD capabilities.

## 🏗️ Architecture

### **Infrastructure Components**

- **VPC**: Multi-AZ VPC with public and private subnets
- **CodeBuild**: Build and test environment with VPC integration
- **S3**: Artifacts and logs storage with encryption
- **KMS**: Encryption key management
- **CloudWatch**: Monitoring, logging, and alerting
- **IAM**: Secure role-based access control

## 🚀 Quick Start

### **Prerequisites**

```bash
# Required tools
terraform >= 1.0
aws-cli >= 2.0
```

### **Configuration**

1. **Clone and navigate to the infrastructure directory:**
   ```bash
   cd infrastructure/terraform
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
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
| **Production** | `environments/prod.tfvars` | Live production environment |

### **Environment-Specific Deployment**

```bash
# Development
terraform apply -var-file="environments/dev.tfvars"

# Production
terraform apply -var-file="environments/prod.tfvars"
```

## 📊 Infrastructure Modules

### **Core Modules**

| Module | Purpose | Resources |
|--------|---------|-----------|
| **VPC** | Network infrastructure | VPC, subnets, gateways, security groups |
| **KMS** | Encryption management | KMS keys, policies |
| **S3** | Object storage | Artifacts and logs buckets with policies |
| **CodeBuild** | Build environment | CodeBuild project, IAM roles, webhooks |
| **CloudWatch** | Monitoring | Dashboards, alarms, log groups |

## 🔧 Configuration Options

### **Key Variables**

```hcl
# Environment Configuration
environment = "dev"           # dev, prod
aws_region  = "us-east-1"    # AWS region

# VPC Configuration
vpc_cidr = "10.0.0.0/16"     # VPC CIDR block
availability_zones_count = 2  # Number of AZs

# GitHub Configuration
github_owner = "your-username"  # GitHub repository owner
github_repo = "your-repo"       # GitHub repository name
github_token = "your-token"     # GitHub personal access token

# Monitoring Configuration
log_retention_days = 30         # Log retention period
alarm_actions = []              # SNS topic ARNs for alerts
```

### **Security Configuration**

```hcl
# Encryption
kms_key_id = "alias/..."       # KMS key for encryption

# Network Security
enable_nat_gateway = true      # Private subnet internet access
security_groups = [...]        # Security group rules

# Access Control
iam_roles = [...]              # IAM roles and policies
```

## 📈 Cost Optimization

### **Estimated Monthly Costs**

| Environment | Estimated Cost | Components |
|-------------|---------------|------------|
| **Development** | $50-100 | Small instances, minimal resources |
| **Production** | $200-400 | Medium instances, full monitoring |

### **Cost Optimization Features**

- **Auto-scaling**: Dynamic resource allocation
- **Lifecycle Policies**: Automatic data archiving
- **Resource Tagging**: Cost allocation and tracking
- **Monitoring**: Cost alerts and optimization

## 🔒 Security Features

### **Built-in Security**

- **Encryption**: End-to-end encryption with KMS
- **Network Security**: VPC isolation, security groups
- **Access Control**: IAM roles and policies
- **Audit Logging**: Comprehensive activity tracking
- **Compliance**: Security best practices

### **Security Best Practices**

```hcl
# Network Security
enable_nat_gateway = true     # Private subnet internet access
security_groups = [...]       # Restrictive security group rules

# Access Control
iam_roles = [...]             # Least privilege access
kms_encryption = true         # Encrypt all data

# Monitoring Security
cloudwatch_logs = true        # Audit trail
alarm_notifications = true    # Security alerts
```

## 📊 Monitoring and Observability

### **Monitoring Stack**

- **CloudWatch**: Metrics, logs, and alarms
- **Dashboards**: Real-time monitoring
- **Automated Alerts**: Incident response
- **Log Aggregation**: Centralized logging

### **Key Metrics**

| Metric | Threshold | Action |
|--------|-----------|--------|
| **Build Duration** | > 30 minutes | Alert |
| **Build Failure Rate** | > 3 failures | Alert |
| **Artifact Storage** | > 80% capacity | Alert |

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
   # Deploy to development first
   terraform apply -var-file="environments/dev.tfvars"
   
   # Validate and promote to production
   terraform apply -var-file="environments/prod.tfvars"
   ```

### **State Management**

```hcl
# Backend configuration (recommended for production)
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "github-actions-codebuild/terraform.tfstate"
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
- [ ] CodeBuild project executes builds
- [ ] CloudWatch monitoring works
- [ ] Alerts trigger correctly

## 🔧 Troubleshooting

### **Common Issues**

1. **Resource Limits**
   ```bash
   # Check AWS service limits
   aws service-quotas get-service-quota --service-code codebuild
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
   terraform import aws_codebuild_project.example project-name
   ```

### **Debug Commands**

```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform apply

# Check resource state
terraform state list
terraform state show aws_codebuild_project.example

# Validate configuration
terraform validate
terraform fmt -check
```

## 📚 Documentation

### **Additional Resources**

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS CodeBuild Documentation](https://docs.aws.amazon.com/codebuild/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### **Module Documentation**

Each module includes detailed documentation:
- `modules/vpc/README.md` - VPC configuration
- `modules/codebuild/README.md` - CodeBuild setup
- `modules/s3/README.md` - S3 storage configuration
- `modules/cloudwatch/README.md` - Monitoring setup

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

**Ready to deploy your GitHub Actions CodeBuild integration? Start with the development environment and scale up! 🚀**
