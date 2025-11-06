# Scripts Directory

This directory contains utility scripts for setting up, deploying, and managing the Claude Code Workshop.

## Setup Scripts

### `setup/setup_environment.sh`

Initial setup script for the workshop environment.

**Usage**:
```bash
bash scripts/setup/setup_environment.sh
```

**What it does**:
- Checks prerequisites (Python, AWS CLI, Git)
- Creates Python virtual environment
- Installs dependencies
- Configures AWS credentials
- Verifies Bedrock access
- Creates necessary directories

### `setup/verify_bedrock_access.sh`

Verifies Amazon Bedrock access and Claude model availability.

**Usage**:
```bash
bash scripts/setup/verify_bedrock_access.sh
```

**What it does**:
- Checks AWS credentials
- Lists available Claude models
- Tests Bedrock access
- Verifies model permissions

## Deployment Scripts

### `deployment/deploy_cdk.sh`

Deploys infrastructure using AWS CDK.

**Usage**:
```bash
bash scripts/deployment/deploy_cdk.sh
```

**What it does**:
- Checks prerequisites
- Installs CDK dependencies
- Bootstraps CDK (if needed)
- Synthesizes CloudFormation
- Deploys stack
- Displays outputs

### `deployment/deploy_terraform.sh`

Deploys infrastructure using Terraform.

**Usage**:
```bash
bash scripts/deployment/deploy_terraform.sh
```

**What it does**:
- Checks prerequisites
- Initializes Terraform
- Plans deployment
- Applies changes
- Displays outputs

### `deployment/cleanup.sh`

Removes all deployed infrastructure.

**Usage**:
```bash
bash scripts/deployment/cleanup.sh
```

**What it does**:
- Detects deployment method (CDK or Terraform)
- Destroys all resources
- Confirms before deletion

## Prerequisites

All scripts require:
- AWS CLI configured
- Python 3.11+
- Appropriate AWS permissions
- Bedrock access (for setup scripts)

## Permissions Required

- CloudFormation (for CDK)
- Lambda (for deployment)
- API Gateway
- DynamoDB
- S3
- IAM
- Bedrock

## Troubleshooting

### Script Execution Errors

If scripts fail with permission errors:
```bash
chmod +x scripts/**/*.sh
```

### AWS Credentials Not Found

If AWS credentials are not configured:
```bash
aws configure
```

### Bedrock Access Denied

If Bedrock access is denied:
1. Request model access in Bedrock console
2. Verify IAM permissions
3. Check region support

## Additional Resources

- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Terraform Documentation](https://www.terraform.io/docs)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)

