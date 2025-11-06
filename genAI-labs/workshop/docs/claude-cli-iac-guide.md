# Claude CLI for Infrastructure as Code (IaC) Guide

This guide demonstrates how to use Claude CLI to design and develop cloud infrastructure using Infrastructure as Code (IaC) tools like AWS CDK and Terraform.

## Overview

Claude CLI provides powerful capabilities for generating, refactoring, and maintaining infrastructure code. This guide shows you how to leverage Claude Code for AWS infrastructure development.

## Prerequisites

- Claude CLI installed and configured
- AWS Account with appropriate permissions
- AWS CDK or Terraform installed
- Basic understanding of cloud infrastructure concepts

## Installation

### Install Claude CLI

```bash
# Install Claude CLI
npm install -g @anthropic-ai/claude-cli

# Or using pip
pip install anthropic-cli

# Verify installation
claude --version
```

## Using Claude CLI for IaC Development

### 1. Generate Infrastructure Code

#### Generate AWS CDK Stack

```bash
# Generate a basic CDK stack
claude code generate \
  --prompt "Create an AWS CDK stack in Python with Lambda function, API Gateway, and DynamoDB table" \
  --language python \
  --output infrastructure/cdk/generated_stack.py

# Generate a more complex stack
claude code generate \
  --prompt "Create AWS CDK stack with:
  - Lambda function with Python 3.11 runtime
  - API Gateway REST API with CORS enabled
  - DynamoDB table with GSI
  - S3 bucket for code storage
  - CloudWatch alarms for monitoring" \
  --language python \
  --output infrastructure/cdk/complex_stack.py
```

#### Generate Terraform Configuration

```bash
# Generate Terraform configuration
claude code generate \
  --prompt "Create Terraform configuration for:
  - AWS Lambda function
  - API Gateway REST API
  - DynamoDB table
  - S3 bucket
  - IAM roles and policies" \
  --language hcl \
  --output infrastructure/terraform/generated/main.tf

# Generate with variables
claude code generate \
  --prompt "Create Terraform configuration with variables for:
  - aws_region (default: us-east-1)
  - environment (default: workshop)
  - lambda_memory (default: 512)
  - lambda_timeout (default: 300)" \
  --language hcl \
  --output infrastructure/terraform/variables.tf
```

### 2. Refactor Infrastructure Code

#### Improve Existing CDK Code

```bash
# Refactor CDK stack to add best practices
claude code refactor \
  --file infrastructure/cdk/claude_code_stack.py \
  --instructions "Add:
  1. CloudWatch alarms for Lambda errors
  2. SNS topic for alerts
  3. Cost optimization tags
  4. Better error handling
  5. Documentation comments" \
  --output infrastructure/cdk/improved_stack.py

# Refactor to use best practices
claude code refactor \
  --file infrastructure/cdk/claude_code_stack.py \
  --instructions "Follow AWS CDK best practices:
  - Use constructs for reusability
  - Add proper resource naming
  - Implement security best practices
  - Add monitoring and logging" \
  --output infrastructure/cdk/refactored_stack.py
```

#### Improve Terraform Code

```bash
# Refactor Terraform configuration
claude code refactor \
  --file infrastructure/terraform/main.tf \
  --instructions "Improve Terraform code:
  1. Use modules for reusability
  2. Add data sources where appropriate
  3. Implement proper variable validation
  4. Add comprehensive outputs
  5. Follow Terraform best practices" \
  --output infrastructure/terraform/improved/main.tf
```

### 3. Review Infrastructure Code

```bash
# Review CDK stack for issues
claude code review \
  --file infrastructure/cdk/claude_code_stack.py \
  --output review_report.md

# Review Terraform configuration
claude code review \
  --file infrastructure/terraform/main.tf \
  --checklist "security,cost,performance,best-practices" \
  --output terraform_review.md
```

### 4. Generate Tests for Infrastructure

```bash
# Generate unit tests for CDK stack
claude code generate \
  --prompt "Create pytest unit tests for AWS CDK stack that test:
  - Stack creation
  - Resource configuration
  - IAM permissions
  - Outputs" \
  --language python \
  --output tests/infrastructure/test_cdk_stack.py

# Generate integration tests for Terraform
claude code generate \
  --prompt "Create Terraform integration tests using Terratest that:
  - Test resource creation
  - Verify resource properties
  - Test resource deletion" \
  --language go \
  --output tests/infrastructure/terraform_test.go
```

### 5. Generate Documentation

```bash
# Generate README for infrastructure
claude code generate \
  --prompt "Create comprehensive README for AWS CDK infrastructure that includes:
  - Overview and architecture
  - Prerequisites
  - Deployment instructions
  - Configuration options
  - Troubleshooting guide" \
  --language markdown \
  --output infrastructure/cdk/README.md

# Generate architecture documentation
claude code generate \
  --prompt "Create architecture documentation with:
  - Architecture diagram (Mermaid)
  - Component descriptions
  - Data flow diagrams
  - Security considerations
  - Cost estimation" \
  --language markdown \
  --output docs/architecture.md
```

## Step-by-Step Workflow

### Workflow 1: Design New Infrastructure

1. **Define Requirements**:
   ```bash
   # Create requirements document
   claude code generate \
     --prompt "Create infrastructure requirements document for:
     - Serverless API with Lambda
     - REST API Gateway
     - DynamoDB for data storage
     - S3 for file storage
     - CloudWatch for monitoring" \
     --language markdown \
     --output docs/requirements.md
   ```

2. **Generate Initial Infrastructure Code**:
   ```bash
   # Generate CDK stack
   claude code generate \
     --prompt "Create AWS CDK stack based on requirements in docs/requirements.md" \
     --language python \
     --output infrastructure/cdk/initial_stack.py
   ```

3. **Review and Refine**:
   ```bash
   # Review generated code
   claude code review \
     --file infrastructure/cdk/initial_stack.py \
     --output review.md
   
   # Refine based on review
   claude code refactor \
     --file infrastructure/cdk/initial_stack.py \
     --instructions "Address issues in review.md" \
     --output infrastructure/cdk/refined_stack.py
   ```

4. **Generate Tests**:
   ```bash
   # Generate tests
   claude code generate \
     --prompt "Create tests for CDK stack in infrastructure/cdk/refined_stack.py" \
     --language python \
     --output tests/infrastructure/test_refined_stack.py
   ```

5. **Generate Deployment Scripts**:
   ```bash
   # Generate deployment script
   claude code generate \
     --prompt "Create bash script to deploy CDK stack with:
     - Environment validation
     - Dependency installation
     - Stack deployment
     - Output verification" \
     --language bash \
     --output scripts/deployment/deploy.sh
   ```

### Workflow 2: Migrate to Terraform

1. **Analyze Existing CDK Stack**:
   ```bash
   # Analyze CDK stack
   claude code analyze \
     --file infrastructure/cdk/claude_code_stack.py \
     --output analysis.md
   ```

2. **Generate Terraform Equivalent**:
   ```bash
   # Generate Terraform from CDK
   claude code generate \
     --prompt "Convert AWS CDK stack in infrastructure/cdk/claude_code_stack.py to Terraform configuration" \
     --language hcl \
     --output infrastructure/terraform/main.tf
   ```

3. **Generate Terraform Variables**:
   ```bash
   # Generate variables file
   claude code generate \
     --prompt "Create Terraform variables file for main.tf with:
     - aws_region
     - environment
     - resource naming conventions" \
     --language hcl \
     --output infrastructure/terraform/variables.tf
   ```

### Workflow 3: Add New Features

1. **Generate Feature Code**:
   ```bash
   # Add new feature to existing stack
   claude code generate \
     --prompt "Add CloudWatch alarms and SNS notifications to existing CDK stack in infrastructure/cdk/claude_code_stack.py" \
     --language python \
     --output infrastructure/cdk/enhanced_stack.py
   ```

2. **Merge Changes**:
   ```bash
   # Review and merge
   claude code review \
     --file infrastructure/cdk/enhanced_stack.py \
     --compare infrastructure/cdk/claude_code_stack.py
   ```

## Best Practices

### 1. Prompt Engineering

**Good Prompts**:
- Specific and detailed
- Include all requirements
- Specify output format
- Include examples

**Example**:
```bash
claude code generate \
  --prompt "Create AWS CDK stack in Python with:
  1. Lambda function:
     - Runtime: Python 3.11
     - Handler: lambda_handler
     - Memory: 512 MB
     - Timeout: 300 seconds
     - Environment variables: TABLE_NAME, BUCKET_NAME
  2. API Gateway:
     - REST API
     - CORS enabled
     - Integration with Lambda
  3. DynamoDB:
     - Table name: users-table
     - Partition key: user_id (String)
     - Billing mode: PAY_PER_REQUEST
  4. IAM:
     - Lambda execution role
     - Bedrock invoke permissions
     - DynamoDB read/write permissions
     - S3 read/write permissions
  Requirements:
  - Use AWS CDK v2
  - Include proper imports
  - Add comments
  - Export outputs" \
  --language python
```

### 2. Iterative Development

1. Generate initial code
2. Review and test
3. Refine based on feedback
4. Repeat until satisfied

### 3. Code Review

Always review generated code:
- Check for security issues
- Verify resource configurations
- Ensure best practices
- Test before deployment

### 4. Documentation

Generate documentation for:
- Architecture diagrams
- Deployment guides
- Configuration options
- Troubleshooting

## Examples

### Example 1: Generate Complete Infrastructure

```bash
# Complete infrastructure generation
claude code generate \
  --prompt "Create complete AWS infrastructure for Claude Code workshop:
  - CDK stack with all resources
  - Deployment scripts
  - Test files
  - Documentation
  - Configuration files" \
  --language python \
  --output infrastructure/complete/
```

### Example 2: Refactor for Cost Optimization

```bash
# Optimize for cost
claude code refactor \
  --file infrastructure/cdk/claude_code_stack.py \
  --instructions "Optimize infrastructure for cost:
  1. Use appropriate instance sizes
  2. Implement auto-scaling
  3. Add cost tags
  4. Use spot instances where possible
  5. Implement caching strategies" \
  --output infrastructure/cdk/cost_optimized_stack.py
```

### Example 3: Add Multi-Region Support

```bash
# Add multi-region support
claude code refactor \
  --file infrastructure/cdk/claude_code_stack.py \
  --instructions "Add multi-region support:
  1. Parameterize region
  2. Add region-specific configurations
  3. Implement cross-region replication
  4. Add region selection logic" \
  --output infrastructure/cdk/multi_region_stack.py
```

## Troubleshooting

### Common Issues

1. **Generated code doesn't compile**:
   - Review prompt for clarity
   - Check language specification
   - Verify requirements

2. **Missing dependencies**:
   - Generate requirements file
   - Check imports
   - Verify package versions

3. **Incorrect resource configuration**:
   - Review AWS documentation
   - Refine prompts
   - Test incrementally

## Additional Resources

- [Claude CLI Documentation](https://docs.anthropic.com/claude/docs/claude-cli)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Infrastructure as Code Best Practices](https://docs.aws.amazon.com/whitepapers/latest/iac-best-practices/)

## Next Steps

1. Practice generating infrastructure code
2. Refactor existing code
3. Generate tests and documentation
4. Deploy and validate
5. Iterate and improve

