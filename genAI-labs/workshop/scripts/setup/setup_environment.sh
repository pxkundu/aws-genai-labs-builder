#!/bin/bash
# Setup script for Claude Code Workshop environment

set -e

echo "🚀 Setting up Claude Code Workshop Environment..."

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install AWS CLI"
    exit 1
fi
echo "✅ AWS CLI found: $(aws --version)"

# Check Git
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git"
    exit 1
fi
echo "✅ Git found: $(git --version)"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Configure AWS credentials
echo "🔧 Configuring AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "⚠️  AWS credentials not configured. Please run: aws configure"
    echo "   Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
else
    echo "✅ AWS credentials configured"
    aws sts get-caller-identity
fi

# Check Bedrock access
echo "🔍 Checking Amazon Bedrock access..."
if aws bedrock list-foundation-models --region us-east-1 --query 'modelSummaries[?contains(modelId, `claude`)]' &> /dev/null; then
    echo "✅ Bedrock access verified"
else
    echo "⚠️  Bedrock access may not be configured. Please check Bedrock console"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp resources/configs/.env.example .env
    echo "⚠️  Please edit .env file with your AWS credentials and configuration"
else
    echo "✅ .env file already exists"
fi

# Create directories
echo "📁 Creating necessary directories..."
mkdir -p code/examples/aws
mkdir -p code/examples/infrastructure
mkdir -p code/exercises
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p resources/datasets
mkdir -p logs

echo "✅ Environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Edit .env file with your AWS credentials"
echo "3. Start with Module 1: docs/workshop/module-1-setup.md"
echo ""
echo "🎉 Ready to begin the workshop!"

