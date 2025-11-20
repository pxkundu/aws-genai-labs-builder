# Module 3: Infrastructure as Code

## Overview

In this module, you'll provision AWS infrastructure using Terraform to support your application deployment. This includes VPC, ECS cluster, ECR repositories, and Application Load Balancer.

**Duration**: 90 minutes  
**Difficulty**: Intermediate

## Learning Objectives

By the end of this module, you will:
- Understand Infrastructure as Code concepts
- Provision AWS VPC and networking
- Create ECR repositories for container images
- Set up ECS cluster with Fargate
- Configure Application Load Balancer
- Understand Terraform best practices

## Prerequisites

- Terraform >= 1.5 installed
- AWS CLI configured
- AWS account with appropriate permissions
- Completed Module 1 and 2

## Step 1: Terraform Setup

### 1.1 Install Terraform

```bash
# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installation
terraform version
```

### 1.2 Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-1)
# Enter output format (json)

# Verify configuration
aws sts get-caller-identity
```

## Step 2: Configure Terraform Variables

### 2.1 Create Variables File

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
```

### 2.2 Edit terraform.tfvars

```hcl
project_name = "harness-workshop"
environment  = "dev"
aws_region   = "us-east-1"
vpc_cidr     = "10.0.0.0/16"

tags = {
  Owner      = "Your Name"
  CostCenter = "Engineering"
  Project    = "Harness Workshop"
}
```

## Step 3: Initialize Terraform

### 3.1 Initialize Backend

```bash
terraform init
```

This will:
- Download AWS provider
- Initialize backend (if configured)
- Set up modules

### 3.2 Verify Configuration

```bash
terraform validate
```

## Step 4: Review Infrastructure Plan

### 4.1 Generate Plan

```bash
terraform plan
```

Review the plan to understand what will be created:
- VPC and subnets
- ECR repositories
- ECS cluster
- Application Load Balancer
- Security groups
- IAM roles

### 4.2 Save Plan (Optional)

```bash
terraform plan -out=tfplan
```

## Step 5: Deploy Infrastructure

### 5.1 Apply Configuration

```bash
terraform apply
```

Type `yes` when prompted to confirm.

### 5.2 Monitor Deployment

The deployment will take approximately 10-15 minutes. Monitor progress in the terminal.

### 5.3 Verify Outputs

After completion, note the outputs:
- ECR repository URLs
- ECS cluster name
- ALB DNS name

```bash
terraform output
```

## Step 6: Verify Resources

### 6.1 Verify ECR Repositories

```bash
aws ecr describe-repositories --region us-east-1
```

You should see:
- `harness-workshop-dev-backend`
- `harness-workshop-dev-frontend`

### 6.2 Verify ECS Cluster

```bash
aws ecs list-clusters
aws ecs describe-clusters --clusters harness-workshop-dev-cluster
```

### 6.3 Verify VPC

```bash
aws ec2 describe-vpcs --filters "Name=tag:Project,Values=harness-workshop"
```

### 6.4 Verify ALB

```bash
aws elbv2 describe-load-balancers
```

## Step 7: Configure ECR Authentication

### 7.1 Get ECR Login Token

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### 7.2 Test ECR Access

```bash
# List repositories
aws ecr describe-repositories

# Test push (after building image)
docker tag backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/harness-workshop-dev-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/harness-workshop-dev-backend:latest
```

## Step 8: Update Harness Connectors

### 8.1 Update AWS Connector

1. In Harness, navigate to your AWS connector
2. Verify it can access the created resources
3. Test connection

### 8.2 Note ECR Registry URL

Save the ECR registry URL for use in pipelines:
```
<account-id>.dkr.ecr.<region>.amazonaws.com
```

## Troubleshooting

### Terraform Errors

**Issue**: Provider authentication errors

**Solution**:
- Verify AWS credentials: `aws sts get-caller-identity`
- Check IAM permissions
- Verify region configuration

**Issue**: Resource creation timeouts

**Solution**:
- Check AWS service quotas
- Verify network connectivity
- Review CloudWatch logs

### ECR Access Issues

**Issue**: Cannot push to ECR

**Solution**:
- Run `aws ecr get-login-password` command
- Verify IAM permissions
- Check repository policies

### ECS Cluster Issues

**Issue**: Cluster not visible

**Solution**:
- Verify cluster was created: `aws ecs list-clusters`
- Check region matches
- Review Terraform outputs

## Best Practices

1. **State Management**: Use S3 backend for state
2. **Version Control**: Commit Terraform files to Git
3. **Modularity**: Use modules for reusability
4. **Tagging**: Tag all resources for cost tracking
5. **Security**: Use least privilege IAM policies
6. **Backup**: Enable versioning on state bucket

## Cleanup (Optional)

If you need to destroy resources:

```bash
terraform destroy
```

**Warning**: This will delete all resources. Only run if you're sure.

## Next Steps

Congratulations! You've completed Module 3. You now have:
- ✅ VPC and networking configured
- ✅ ECR repositories created
- ✅ ECS cluster provisioned
- ✅ Application Load Balancer set up
- ✅ Infrastructure ready for deployment

**Proceed to [Module 4: Harness CI Pipeline](./module-4-ci-pipeline.md)** to create your CI pipeline! 🚀

## Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)

