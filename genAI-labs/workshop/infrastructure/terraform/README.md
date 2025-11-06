# Terraform Infrastructure for Claude Code Workshop

This directory contains Terraform configuration for deploying the Claude Code Workshop infrastructure.

## Structure

- `main.tf` - Main Terraform configuration
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `terraform.tfvars.example` - Example variable values

## Deployment

### Prerequisites

1. AWS CLI configured
2. Terraform 1.0+ installed
3. Python 3.11+
4. Bedrock access with Claude models

### Steps

1. **Initialize Terraform**:
   ```bash
   terraform init
   ```

2. **Plan deployment**:
   ```bash
   terraform plan
   ```

3. **Deploy infrastructure**:
   ```bash
   terraform apply
   ```

4. **Get outputs**:
   ```bash
   terraform output
   ```

## Using Claude Code CLI to Generate Infrastructure

You can use Claude Code CLI to generate and modify this Terraform code:

```bash
# Generate new Terraform configuration
claude code generate --prompt "Create Terraform configuration for Lambda with API Gateway"

# Refactor existing code
claude code refactor --file main.tf --instructions "Add CloudWatch alarms"

# Review generated code
claude code review --file main.tf
```

## Resources Created

- **Lambda Function**: `claude-code-generator` - Handles code generation requests
- **API Gateway**: REST API for code generation endpoints
- **DynamoDB Table**: `claude-code-results` - Stores generation metadata
- **S3 Bucket**: `claude-code-workshop-{account}` - Stores generated code files
- **IAM Roles**: Lambda execution role with necessary permissions

## Customization

Edit `main.tf` or create `terraform.tfvars` to customize:
- AWS region
- Lambda configuration
- API Gateway settings
- DynamoDB table configuration
- S3 bucket settings

## Cleanup

To remove all resources:

```bash
terraform destroy
```

