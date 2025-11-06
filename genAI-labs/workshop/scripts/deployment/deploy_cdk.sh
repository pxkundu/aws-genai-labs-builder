#!/bin/bash
# Deploy Claude Code Workshop using AWS CDK

set -e

echo "🚀 Deploying Claude Code Workshop with CDK..."

# Check prerequisites
if ! command -v cdk &> /dev/null; then
    echo "❌ AWS CDK is not installed. Installing..."
    npm install -g aws-cdk
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured"
    exit 1
fi

# Navigate to CDK directory
cd infrastructure/cdk

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -d "venv" ]; then
    source venv/bin/activate
else
    python3 -m venv venv
    source venv/bin/activate
fi

pip install -r requirements.txt

# Bootstrap CDK (if not already bootstrapped)
echo "🔧 Bootstrapping CDK (if needed)..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=${AWS_REGION:-us-east-1}

cdk bootstrap aws://$ACCOUNT_ID/$REGION || echo "CDK already bootstrapped"

# Synthesize CloudFormation template
echo "📝 Synthesizing CloudFormation template..."
cdk synth

# Deploy stack
echo "🚀 Deploying stack..."
read -p "Do you want to deploy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cdk deploy --require-approval never
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📋 Getting outputs..."
    aws cloudformation describe-stacks \
        --stack-name ClaudeCodeWorkshopStack \
        --query 'Stacks[0].Outputs' \
        --output table
else
    echo "Deployment cancelled"
fi

