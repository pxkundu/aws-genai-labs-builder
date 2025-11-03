# Module 1: Environment Setup

## Overview
This module will guide you through setting up your development environment and AWS account for working with Claude Code on AWS. You'll configure Amazon Bedrock, set up local development tools, and verify your environment is ready for the workshop.

## Learning Objectives
- Set up AWS account with proper permissions for Claude Code
- Configure Amazon Bedrock with Claude model access
- Set up local development environment
- Initialize project structure and dependencies
- Verify Claude Code integration

## Prerequisites
- AWS Account
- AWS CLI installed
- Python 3.11+
- Code editor (VS Code recommended)
- Git

## Step 1: AWS Account Setup

### 1.1 Create AWS Account
If you don't have an AWS account:
1. Go to [AWS Console](https://aws.amazon.com/console/)
2. Click "Create an AWS Account"
3. Follow the registration process
4. Complete identity verification

### 1.2 Configure AWS CLI
```bash
# Install AWS CLI (if not already installed)
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download and run the AWS CLI MSI installer

# Configure AWS CLI
aws configure
```

Enter your credentials:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

### 1.3 Verify AWS Access
```bash
# Test AWS CLI configuration
aws sts get-caller-identity

# List available regions
aws ec2 describe-regions --query 'Regions[].RegionName'
```

## Step 2: Amazon Bedrock Setup

### 2.1 Enable Amazon Bedrock
1. Go to [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click "Get started" or "Launch Bedrock"
3. Accept the terms of service

### 2.2 Request Claude Model Access
1. Navigate to **Model access** in the Bedrock console
2. Click **Request model access**
3. Select the following Claude models:
   - **Claude 3.5 Sonnet** (recommended for Claude Code)
   - **Claude 3 Haiku** (for faster, cost-effective tasks)
   - **Claude 3 Opus** (for complex code generation)
4. Click **Request access**
5. Wait for approval (usually instant for most regions)

### 2.3 Verify Model Access
```bash
# List available foundation models
aws bedrock list-foundation-models \
  --region us-east-1 \
  --query 'modelSummaries[?contains(modelId, `claude`)].{Name:modelName,ID:modelId}' \
  --output table

# Test Bedrock access
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --region us-east-1 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
  --cli-binary-format raw-in-base64-out \
  output.json && cat output.json
```

## Step 3: IAM Permissions Setup

### 3.1 Create IAM Policy for Bedrock
Create a policy file `bedrock-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:GetFoundationModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3.2 Attach Policy to User/Role
```bash
# Create policy (if using IAM user)
aws iam create-policy \
  --policy-name BedrockClaudeCodePolicy \
  --policy-document file://bedrock-policy.json

# Attach to user
aws iam attach-user-policy \
  --user-name YOUR_USERNAME \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/BedrockClaudeCodePolicy
```

## Step 4: Local Development Environment

### 4.1 Install Python Dependencies
```bash
# Navigate to workshop directory
cd genAI-labs/workshop

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.2 Install Additional Tools (Optional)
```bash
# AWS CDK (for infrastructure examples)
npm install -g aws-cdk

# Verify installation
cdk --version

# Docker (for containerization examples)
# macOS: brew install docker
# Linux: sudo apt-get install docker.io
# Windows: Download Docker Desktop
```

## Step 5: Project Structure Overview

```
workshop/
├── docs/
│   └── workshop/          # Workshop module documentation
├── code/
│   ├── examples/          # Code examples
│   └── exercises/         # Hands-on exercises
├── resources/
│   ├── configs/           # Configuration files
│   └── datasets/          # Sample datasets
├── infrastructure/
│   ├── cdk/               # AWS CDK infrastructure
│   └── terraform/         # Terraform infrastructure
├── scripts/
│   ├── setup/             # Setup scripts
│   └── deployment/        # Deployment scripts
├── tests/
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── requirements.txt       # Python dependencies
└── README.md              # Main workshop README
```

## Step 6: Environment Configuration

### 6.1 Create Environment File
```bash
# Copy example environment file
cp resources/configs/.env.example .env
```

### 6.2 Configure Environment Variables
Edit `.env` file with your configuration:

```env
# Application
DEBUG=true
ENVIRONMENT=development

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Bedrock Configuration
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Claude Code Configuration
MAX_TOKENS=4000
TEMPERATURE=0.7
TOP_P=0.9

# Application Settings
LOG_LEVEL=INFO
```

### 6.3 Create .env.example Template
Create `resources/configs/.env.example`:
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# Bedrock Configuration
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Claude Code Configuration
MAX_TOKENS=4000
TEMPERATURE=0.7
```

## Step 7: Verify Setup

### 7.1 Test Bedrock Connection
Create a test script `test_bedrock.py`:
```python
import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_bedrock_access():
    """Test Bedrock access and Claude model"""
    try:
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('BEDROCK_REGION', 'us-east-1')
        )
        
        response = bedrock.invoke_model(
            modelId=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0'),
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 100,
                'messages': [{
                    'role': 'user',
                    'content': 'Say hello and confirm you can generate code.'
                }]
            })
        )
        
        result = json.loads(response['body'].read())
        print("✅ Bedrock access successful!")
        print(f"Response: {result['content'][0]['text']}")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock access failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_bedrock_access()
```

Run the test:
```bash
python test_bedrock.py
```

### 7.2 Test Python Environment
```bash
# Test Python version
python --version  # Should be 3.11+

# Test dependencies
python -c "import boto3; print(f'boto3 version: {boto3.__version__}')"
python -c "import anthropic; print('anthropic SDK installed')"
```

### 7.3 Verify Project Structure
```bash
# Check directory structure
tree -L 2 -I '__pycache__|*.pyc|venv|.git'

# Or use ls
ls -la
```

## Troubleshooting

### Common Issues

#### AWS Access Denied
```bash
# Check your AWS credentials
aws sts get-caller-identity

# Verify region
aws configure get region

# Check IAM permissions
aws iam get-user
```

#### Bedrock Model Access Denied
- Ensure you've requested access to Claude models in Bedrock console
- Check if your region supports Bedrock (us-east-1, us-west-2, etc.)
- Verify IAM permissions include Bedrock invoke actions
- Wait a few minutes after requesting access if it was just approved

#### Python Dependencies Issues
```bash
# Update pip
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Environment Variables Not Loading
```bash
# Verify .env file exists
ls -la .env

# Test loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('AWS_REGION'))"
```

## Next Steps

✅ **Module 1 Complete!**

You have successfully:
- Set up AWS account and Bedrock access
- Configured local development environment
- Initialized project structure
- Verified Claude Code integration

**Ready for [Module 2: Claude Code Basics](./module-2-claude-code-basics.md)?**

## Additional Resources

- [AWS CLI User Guide](https://docs.aws.amazon.com/cli/latest/userguide/)
- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs/claude-code)

