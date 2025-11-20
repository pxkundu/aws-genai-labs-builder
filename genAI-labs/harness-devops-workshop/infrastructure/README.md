# Infrastructure as Code

This directory contains Terraform configurations for provisioning AWS infrastructure required for the Harness DevOps workshop.

## Structure

```
infrastructure/
├── terraform/
│   ├── main.tf              # Main Terraform configuration
│   ├── variables.tf         # Variable definitions
│   ├── outputs.tf           # Output values
│   ├── terraform.tfvars.example  # Example variables file
│   └── modules/             # Terraform modules
│       ├── vpc/            # VPC and networking
│       ├── ecr/            # ECR repositories
│       ├── ecs/            # ECS cluster and services
│       └── alb/            # Application Load Balancer
```

## Prerequisites

- Terraform >= 1.5
- AWS CLI configured
- Appropriate AWS IAM permissions
- S3 bucket for Terraform state (optional but recommended)

## Quick Start

### 1. Configure Variables

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan Deployment

```bash
terraform plan
```

### 4. Apply Configuration

```bash
terraform apply
```

### 5. Get Outputs

```bash
terraform output
```

## Modules

### VPC Module

Creates:
- VPC with public and private subnets
- Internet Gateway
- NAT Gateway
- Route tables
- Security groups

### ECR Module

Creates:
- ECR repositories for backend and frontend
- Lifecycle policies
- Repository policies

### ECS Module

Creates:
- ECS cluster (Fargate)
- Task definitions
- ECS services
- IAM roles
- Security groups

### ALB Module

Creates:
- Application Load Balancer
- Target groups
- Listeners
- Security groups

## Outputs

After deployment, Terraform outputs:
- VPC ID
- ECR repository URLs
- ECS cluster name
- ALB DNS name
- Service names

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all resources created by Terraform.

## Cost Estimation

Approximate monthly costs:
- VPC and networking: ~$30-50
- ECS Fargate (2 services): ~$50-100
- ALB: ~$20-30
- ECR storage: ~$1-5
- CloudWatch logs: ~$5-10

**Total**: ~$100-200/month (depending on usage)

## Next Steps

1. Deploy infrastructure
2. Configure Harness connectors
3. Set up CI/CD pipelines
4. Deploy applications

