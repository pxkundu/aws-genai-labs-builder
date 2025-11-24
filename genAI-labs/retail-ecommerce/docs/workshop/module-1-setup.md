# Module 1: Environment Setup

## Learning Objectives

By the end of this module, you will be able to:

- Set up your AWS account and configure required services
- Enable access to Amazon Bedrock foundation models
- Configure your local development environment
- Load sample data for testing
- Verify your setup with basic API calls

## Prerequisites

- AWS Account with admin access
- AWS CLI installed and configured
- Python 3.11+ installed
- Git installed
- Code editor (VS Code recommended)

## Duration

**Estimated Time**: 30 minutes

## Step 1: AWS Account Setup

### 1.1 Verify AWS CLI Configuration

```bash
# Check AWS CLI version
aws --version

# Verify credentials
aws sts get-caller-identity

# Set default region
export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1
```

### 1.2 Configure AWS Credentials

```bash
# Configure AWS CLI (if not already done)
aws configure

# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

## Step 2: Enable Amazon Bedrock Access

### 2.1 Request Model Access

1. Navigate to [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Go to **Model access** in the left navigation
3. Select the following models and click **Request model access**:
   - Claude 3.5 Sonnet
   - Claude 3 Haiku
   - Titan Text G1 - Large

### 2.2 Verify Model Access

```bash
# List available foundation models
aws bedrock list-foundation-models \
  --region us-east-1 \
  --query 'modelSummaries[?contains(modelId, `claude`)].{ModelId:modelId,ModelName:modelName}'

# Test Bedrock access
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --region us-east-1 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
  --cli-binary-format raw-in-base64-out \
  response.json

cat response.json
```

## Step 3: Local Development Setup

### 3.1 Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd genAI-labs/retail-ecommerce

# Verify structure
ls -la
```

### 3.2 Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 3.3 Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import boto3; print(boto3.__version__)"
```

### 3.4 Configure Environment Variables

```bash
# Copy example environment file
cp config/environments/development.env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Required Variables**:
```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id
ENVIRONMENT=development
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
DYNAMODB_TABLE_PREFIX=retail-ecommerce-dev
S3_BUCKET_PREFIX=retail-ecommerce-dev
```

## Step 4: Load Sample Data

### 4.1 Create S3 Bucket

```bash
# Create S3 bucket for sample data
aws s3 mb s3://retail-ecommerce-dev-sample-data \
  --region us-east-1

# Upload sample data
aws s3 cp data/sample/products.json \
  s3://retail-ecommerce-dev-sample-data/products.json
```

### 4.2 Create DynamoDB Tables

```bash
# Create users table
aws dynamodb create-table \
  --table-name retail-ecommerce-dev-users \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Create products table
aws dynamodb create-table \
  --table-name retail-ecommerce-dev-products \
  --attribute-definitions AttributeName=product_id,AttributeType=S \
  --key-schema AttributeName=product_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 4.3 Load Sample Data

```bash
# Run data loading script
python scripts/load-sample-data.py \
  --environment development \
  --data-dir data/sample
```

## Step 5: Verify Setup

### 5.1 Test AWS Services

```bash
# Test Bedrock
python scripts/test-bedrock.py

# Test DynamoDB
python scripts/test-dynamodb.py

# Test S3
python scripts/test-s3.py
```

### 5.2 Run Basic API Test

```bash
# Start local API server (if available)
python backend/main.py

# In another terminal, test API
curl http://localhost:8000/health

# Test personalization endpoint
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-1",
    "context": {
      "page_type": "homepage",
      "session_id": "test-session-1"
    }
  }'
```

## Step 6: Verify CloudWatch Access

```bash
# Create CloudWatch log group
aws logs create-log-group \
  --log-group-name /aws/lambda/retail-ecommerce-dev \
  --region us-east-1

# Verify log group exists
aws logs describe-log-groups \
  --log-group-name-prefix /aws/lambda/retail-ecommerce-dev
```

## Troubleshooting

### Issue: Bedrock Access Denied

**Solution**:
1. Ensure model access is requested and approved
2. Check IAM permissions for Bedrock
3. Verify region (Bedrock may not be available in all regions)

```bash
# Check IAM permissions
aws iam get-user-policy \
  --user-name YOUR_USERNAME \
  --policy-name BedrockAccess
```

### Issue: DynamoDB Table Creation Fails

**Solution**:
1. Check IAM permissions for DynamoDB
2. Verify table name doesn't already exist
3. Ensure billing mode is set correctly

```bash
# List existing tables
aws dynamodb list-tables --region us-east-1
```

### Issue: Python Dependencies Fail

**Solution**:
1. Ensure Python 3.11+ is installed
2. Upgrade pip: `pip install --upgrade pip`
3. Install dependencies one by one to identify issues

```bash
# Check Python version
python --version

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

## Validation Checklist

Before proceeding to Module 2, verify:

- [ ] AWS CLI configured and working
- [ ] Bedrock model access enabled
- [ ] Python virtual environment created and activated
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Sample data loaded
- [ ] Basic API tests passing
- [ ] CloudWatch access verified

## Next Steps

Congratulations! You've completed Module 1. You're now ready to:

1. **Proceed to Module 2**: [Personalization Engine](./module-2-personalization.md)
2. **Explore the Codebase**: Review the project structure
3. **Review Architecture**: Read the [Architecture Guide](../../architecture.md)

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS CLI User Guide](https://docs.aws.amazon.com/cli/latest/userguide/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

**Ready for Module 2? Let's build the personalization engine! 🚀**

