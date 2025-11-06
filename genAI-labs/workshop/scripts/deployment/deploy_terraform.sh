#!/bin/bash
# Deploy Claude Code Workshop using Terraform

set -e

echo "🚀 Deploying Claude Code Workshop with Terraform..."

# Check prerequisites
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is not installed"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured"
    exit 1
fi

# Navigate to Terraform directory
cd infrastructure/terraform

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Plan deployment
echo "📝 Planning deployment..."
terraform plan

# Apply deployment
echo "🚀 Applying deployment..."
read -p "Do you want to deploy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    terraform apply -auto-approve
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📋 Getting outputs..."
    terraform output
else
    echo "Deployment cancelled"
fi

