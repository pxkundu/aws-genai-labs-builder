# AWS CDK Infrastructure for Claude Code Workshop

This directory contains AWS CDK code for deploying the Claude Code Workshop infrastructure.

## Structure

- `app.py` - Main CDK application entry point
- `claude_code_stack.py` - CDK stack definition with all resources
- `cdk.json` - CDK configuration
- `requirements.txt` - Python dependencies

## Deployment

### Prerequisites

1. AWS CLI configured
2. AWS CDK installed: `npm install -g aws-cdk`
3. Python 3.11+
4. Bedrock access with Claude models

### Steps

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Bootstrap CDK** (first time only):
   ```bash
   cdk bootstrap aws://ACCOUNT_ID/us-east-1
   ```

3. **Synthesize CloudFormation**:
   ```bash
   cdk synth
   ```

4. **Deploy stack**:
   ```bash
   cdk deploy
   ```

5. **Get outputs**:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name ClaudeCodeWorkshopStack \
     --query 'Stacks[0].Outputs'
   ```

## Using Claude Code CLI to Generate Infrastructure

You can use Claude Code CLI to generate and modify this infrastructure code:

```bash
# Generate new infrastructure code
claude code generate --prompt "Create a CDK stack with Lambda and API Gateway"

# Refactor existing code
claude code refactor --file claude_code_stack.py --instructions "Add CloudWatch alarms"

# Review generated code
claude code review --file claude_code_stack.py
```

## Resources Created

- **Lambda Function**: `claude-code-generator` - Handles code generation requests
- **API Gateway**: REST API for code generation endpoints
- **DynamoDB Table**: `claude-code-results` - Stores generation metadata
- **S3 Bucket**: `claude-code-workshop-{account}` - Stores generated code files
- **IAM Roles**: Lambda execution role with necessary permissions

## Customization

Edit `claude_code_stack.py` to customize:
- Lambda configuration (memory, timeout)
- API Gateway settings
- DynamoDB table configuration
- S3 bucket settings
- IAM permissions

## Cleanup

To remove all resources:

```bash
cdk destroy
```

