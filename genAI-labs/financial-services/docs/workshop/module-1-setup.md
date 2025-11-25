# Module 1: Environment Setup

## Learning Objectives

By the end of this module, you will be able to:

- Set up your AWS account with secure configuration
- Enable access to Amazon Bedrock foundation models
- Configure AWS Fraud Detector
- Set up secure VPC and networking
- Configure KMS encryption keys
- Set up your local development environment
- Load sample data for testing
- Verify your setup with basic API calls

## Prerequisites

- AWS Account with admin access
- AWS CLI installed and configured
- Python 3.11+ installed
- Git installed
- Code editor (VS Code recommended)

## Duration

**Estimated Time**: 45 minutes

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

## Step 3: Set Up VPC and Networking

### 3.1 Create VPC

```bash
# Create VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=financial-services-vpc}]'

# Note the VPC ID from output
VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=tag:Name,Values=financial-services-vpc" \
  --query 'Vpcs[0].VpcId' \
  --output text)

echo $VPC_ID
```

### 3.2 Create Subnets

```bash
# Create public subnet
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=financial-services-public}]'

# Create private subnet
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.10.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=financial-services-private}]'
```

### 3.3 Create Internet Gateway

```bash
# Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=financial-services-igw}]'

# Attach to VPC
IGW_ID=$(aws ec2 describe-internet-gateways \
  --filters "Name=tag:Name,Values=financial-services-igw" \
  --query 'InternetGateways[0].InternetGatewayId' \
  --output text)

aws ec2 attach-internet-gateway \
  --internet-gateway-id $IGW_ID \
  --vpc-id $VPC_ID
```

## Step 4: Configure KMS Encryption

### 4.1 Create KMS Key

```bash
# Create KMS key for encryption
aws kms create-key \
  --description "Financial Services Encryption Key" \
  --key-usage ENCRYPT_DECRYPT \
  --key-spec SYMMETRIC_DEFAULT \
  --tags TagKey=Name,TagValue=financial-services-key

# Create alias
KMS_KEY_ID=$(aws kms list-keys \
  --query 'Keys[0].KeyId' \
  --output text)

aws kms create-alias \
  --alias-name alias/financial-services-key \
  --target-key-id $KMS_KEY_ID
```

### 4.2 Verify KMS Key

```bash
# Verify key exists
aws kms describe-key \
  --key-id alias/financial-services-key
```

## Step 5: Local Development Setup

### 5.1 Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd genAI-labs/financial-services

# Verify structure
ls -la
```

### 5.2 Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 5.3 Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import boto3; print(boto3.__version__)"
```

### 5.4 Configure Environment Variables

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
DYNAMODB_TABLE_PREFIX=financial-services-dev
S3_BUCKET_PREFIX=financial-services-dev
KMS_KEY_ALIAS=alias/financial-services-key
VPC_ID=your-vpc-id
```

## Step 6: Create DynamoDB Tables

### 6.1 Create Tables with Encryption

```bash
# Create transactions table
aws dynamodb create-table \
  --table-name financial-services-dev-transactions \
  --attribute-definitions \
    AttributeName=transaction_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=transaction_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --sse-specification Enabled=true,SSEType=KMS \
  --region us-east-1

# Create customers table
aws dynamodb create-table \
  --table-name financial-services-dev-customers \
  --attribute-definitions \
    AttributeName=customer_id,AttributeType=S \
  --key-schema \
    AttributeName=customer_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --sse-specification Enabled=true,SSEType=KMS \
  --region us-east-1

# Create fraud events table
aws dynamodb create-table \
  --table-name financial-services-dev-fraud-events \
  --attribute-definitions \
    AttributeName=event_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=event_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --sse-specification Enabled=true,SSEType=KMS \
  --region us-east-1
```

## Step 7: Create S3 Buckets

### 7.1 Create Encrypted S3 Buckets

```bash
# Create data lake bucket
aws s3 mb s3://financial-services-dev-data-lake \
  --region us-east-1

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket financial-services-dev-data-lake \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "alias/financial-services-key"
      }
    }]
  }'

# Create audit logs bucket
aws s3 mb s3://financial-services-dev-audit-logs \
  --region us-east-1

# Enable versioning for audit logs
aws s3api put-bucket-versioning \
  --bucket financial-services-dev-audit-logs \
  --versioning-configuration Status=Enabled
```

## Step 8: Set Up CloudTrail

### 8.1 Create CloudTrail

```bash
# Create CloudTrail
aws cloudtrail create-trail \
  --name financial-services-audit \
  --s3-bucket-name financial-services-dev-audit-logs \
  --include-global-service-events \
  --is-multi-region-trail

# Start logging
aws cloudtrail start-logging \
  --name financial-services-audit
```

## Step 9: Load Sample Data

### 9.1 Upload Sample Data

```bash
# Upload sample transaction data
aws s3 cp data/sample/transactions.json \
  s3://financial-services-dev-data-lake/sample/transactions.json

# Upload sample customer data
aws s3 cp data/sample/customers.json \
  s3://financial-services-dev-data-lake/sample/customers.json
```

### 9.2 Load Sample Data

```bash
# Run data loading script
python scripts/load-sample-data.py \
  --environment development \
  --data-dir data/sample
```

## Step 10: Verify Setup

### 10.1 Test AWS Services

```bash
# Test Bedrock
python scripts/test-bedrock.py

# Test DynamoDB
python scripts/test-dynamodb.py

# Test S3
python scripts/test-s3.py

# Test KMS
python scripts/test-kms.py
```

### 10.2 Run Basic API Test

```bash
# Start local API server (if available)
python backend/main.py

# In another terminal, test API
curl http://localhost:8000/health

# Test fraud detection endpoint (with authentication)
curl -X POST http://localhost:8000/api/v1/fraud-detection \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "transaction_id": "test-txn-1",
    "amount": 1000.00,
    "merchant": "test-merchant",
    "customer_id": "test-customer-1"
  }'
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

### Issue: KMS Key Access Denied

**Solution**:
1. Check IAM permissions for KMS
2. Verify key policy allows your user/role
3. Ensure key is in the same region

```bash
# Check key policy
aws kms get-key-policy \
  --key-id alias/financial-services-key \
  --policy-name default
```

### Issue: DynamoDB Table Creation Fails

**Solution**:
1. Check IAM permissions for DynamoDB
2. Verify table name doesn't already exist
3. Ensure KMS key permissions are correct

```bash
# List existing tables
aws dynamodb list-tables --region us-east-1
```

## Validation Checklist

Before proceeding to Module 2, verify:

- [ ] AWS CLI configured and working
- [ ] Bedrock model access enabled
- [ ] VPC and subnets created
- [ ] KMS key created and accessible
- [ ] Python virtual environment created and activated
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] DynamoDB tables created with encryption
- [ ] S3 buckets created with encryption
- [ ] CloudTrail configured
- [ ] Sample data loaded
- [ ] Basic API tests passing

## Security Best Practices

✅ **Implemented in this module**:
- VPC isolation for network security
- KMS encryption for all data
- Encrypted DynamoDB tables
- Encrypted S3 buckets
- CloudTrail audit logging
- Least privilege IAM roles

## Next Steps

Congratulations! You've completed Module 1. You're now ready to:

1. **Proceed to Module 2**: [Fraud Detection](./module-2-fraud-detection.md)
2. **Explore the Codebase**: Review the project structure
3. **Review Architecture**: Read the [Architecture Guide](../../architecture.md)

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS KMS Documentation](https://docs.aws.amazon.com/kms/)
- [AWS VPC Documentation](https://docs.aws.amazon.com/vpc/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

**Ready for Module 2? Let's build the fraud detection system! 🚀**

