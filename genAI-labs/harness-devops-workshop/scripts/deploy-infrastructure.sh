#!/bin/bash

# Infrastructure Deployment Script
# This script deploys AWS infrastructure using Terraform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$SCRIPT_DIR/../infrastructure/terraform"

echo "========================================="
echo "Infrastructure Deployment"
echo "========================================="

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Error: Terraform is not installed. Please install Terraform >= 1.5"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS CLI is not configured. Please run 'aws configure'"
    exit 1
fi

cd "$INFRA_DIR"

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "Warning: terraform.tfvars not found. Creating from example..."
    cp terraform.tfvars.example terraform.tfvars
    echo "Please edit terraform.tfvars with your values before continuing."
    read -p "Press Enter to continue after editing terraform.tfvars..."
fi

echo ""
echo "Initializing Terraform..."
terraform init

echo ""
echo "Validating Terraform configuration..."
terraform validate

echo ""
echo "Planning infrastructure deployment..."
terraform plan -out=tfplan

echo ""
read -p "Do you want to apply these changes? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "Applying infrastructure changes..."
terraform apply tfplan

echo ""
echo "========================================="
echo "Infrastructure deployment complete!"
echo "========================================="
echo ""
echo "Outputs:"
terraform output

echo ""
echo "Next steps:"
echo "1. Note the ECR repository URLs"
echo "2. Note the ECS cluster name"
echo "3. Note the ALB DNS name"
echo "4. Configure Harness connectors with these values"

