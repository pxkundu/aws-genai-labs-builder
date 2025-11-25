# Module 1: Environment Setup

## Learning Objectives

By the end of this module, you will be able to:

- Set up AWS IoT Core for device connectivity
- Configure Timestream database for time-series data
- Set up Kinesis streams for data ingestion
- Configure your local development environment
- Register IoT devices and test connectivity
- Load sample sensor data for testing
- Verify your setup with basic API calls

## Prerequisites

- AWS Account with admin access
- AWS CLI installed and configured
- Python 3.11+ installed
- Git installed
- Code editor (VS Code recommended)

## Duration

**Estimated Time**: 60 minutes

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

## Step 3: Set Up AWS IoT Core

### 3.1 Create IoT Thing Group

```bash
# Create thing group for manufacturing equipment
aws iot create-thing-group \
  --thing-group-name ManufacturingEquipment \
  --thing-group-properties thingGroupDescription="Manufacturing equipment group"
```

### 3.2 Create IoT Thing Type

```bash
# Create thing type for sensors
aws iot create-thing-type \
  --thing-type-name ManufacturingSensor \
  --thing-type-properties thingTypeDescription="Manufacturing sensor device"
```

### 3.3 Create IoT Policy

```bash
# Create IoT policy document
cat > config/iot-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect",
        "iot:Publish",
        "iot:Subscribe",
        "iot:Receive"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Create IoT policy
aws iot create-policy \
  --policy-name ManufacturingDevicePolicy \
  --policy-document file://config/iot-policy.json
```

### 3.4 Get IoT Endpoint

```bash
# Get IoT endpoint
IOT_ENDPOINT=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query 'endpointAddress' --output text)
echo "IoT Endpoint: $IOT_ENDPOINT"
```

## Step 4: Set Up Timestream Database

### 4.1 Create Timestream Database

```bash
# Create Timestream database
aws timestream-write create-database \
  --database-name manufacturing-sensors \
  --region us-east-1

# Verify database creation
aws timestream-write describe-database \
  --database-name manufacturing-sensors \
  --region us-east-1
```

### 4.2 Create Timestream Table

```bash
# Create table for sensor data
aws timestream-write create-table \
  --database-name manufacturing-sensors \
  --table-name equipment-sensors \
  --retention-properties MemoryStoreRetentionPeriodInHours=24,MagneticStoreRetentionPeriodInDays=365 \
  --region us-east-1

# Verify table creation
aws timestream-write describe-table \
  --database-name manufacturing-sensors \
  --table-name equipment-sensors \
  --region us-east-1
```

## Step 5: Set Up Kinesis Streams

### 5.1 Create Kinesis Streams

```bash
# Create stream for image data
aws kinesis create-stream \
  --stream-name manufacturing-images \
  --shard-count 5 \
  --region us-east-1

# Create stream for process data
aws kinesis create-stream \
  --stream-name manufacturing-process \
  --shard-count 3 \
  --region us-east-1

# Verify streams
aws kinesis describe-stream --stream-name manufacturing-images
aws kinesis describe-stream --stream-name manufacturing-process
```

## Step 6: Local Development Setup

### 6.1 Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd genAI-labs/manufacturing

# Verify structure
ls -la
```

### 6.2 Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 6.3 Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install IoT SDK
pip install aws-iot-device-sdk-python-v2

# Verify installation
python -c "import boto3; print(boto3.__version__)"
```

### 6.4 Configure Environment Variables

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
DYNAMODB_TABLE_PREFIX=manufacturing-dev
S3_BUCKET_PREFIX=manufacturing-dev
TIMESTREAM_DB_NAME=manufacturing-sensors
IOT_ENDPOINT=your-iot-endpoint
```

## Step 7: Register IoT Device

### 7.1 Create IoT Thing

```bash
# Create IoT thing
aws iot create-thing \
  --thing-name sensor-001 \
  --thing-type-name ManufacturingSensor \
  --thing-group-names ManufacturingEquipment
```

### 7.2 Create Device Certificate

```bash
# Create keys and certificate
aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile device-cert.pem \
  --public-key-outfile device-public-key.pem \
  --private-key-outfile device-private-key.pem

# Save certificate ARN
CERT_ARN=$(aws iot list-certificates --query 'certificates[0].certificateArn' --output text)
echo "Certificate ARN: $CERT_ARN"
```

### 7.3 Attach Policy to Certificate

```bash
# Attach policy to certificate
aws iot attach-policy \
  --policy-name ManufacturingDevicePolicy \
  --target $CERT_ARN
```

## Step 8: Create DynamoDB Tables

### 8.1 Create Tables

```bash
# Create equipment table
aws dynamodb create-table \
  --table-name manufacturing-dev-equipment \
  --attribute-definitions \
    AttributeName=equipment_id,AttributeType=S \
  --key-schema \
    AttributeName=equipment_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Create maintenance table
aws dynamodb create-table \
  --table-name manufacturing-dev-maintenance \
  --attribute-definitions \
    AttributeName=work_order_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=work_order_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

## Step 9: Create S3 Buckets

### 9.1 Create Buckets

```bash
# Create data lake bucket
aws s3 mb s3://manufacturing-dev-data-lake \
  --region us-east-1

# Create images bucket
aws s3 mb s3://manufacturing-dev-images \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket manufacturing-dev-data-lake \
  --versioning-configuration Status=Enabled
```

## Step 10: Load Sample Data

### 10.1 Upload Sample Data

```bash
# Upload sample sensor data
aws s3 cp data/sample/sensor-data.json \
  s3://manufacturing-dev-data-lake/sample/sensor-data.json

# Upload sample equipment data
aws s3 cp data/sample/equipment-data.json \
  s3://manufacturing-dev-data-lake/sample/equipment-data.json
```

### 10.2 Load Sample Data

```bash
# Run data loading script
python scripts/load-sample-data.py \
  --environment development \
  --data-dir data/sample
```

## Step 11: Test IoT Connection

### 11.1 Test Device Connection

```bash
# Test IoT device connection
python scripts/test-iot-device.py \
  --thing-name sensor-001 \
  --certificate device-cert.pem \
  --private-key device-private-key.pem \
  --endpoint $IOT_ENDPOINT
```

### 11.2 Send Test Data

```bash
# Send test sensor data
python scripts/send-sensor-data.py \
  --thing-name sensor-001 \
  --certificate device-cert.pem \
  --private-key device-private-key.pem \
  --endpoint $IOT_ENDPOINT \
  --data '{"temperature": 75.5, "vibration": 2.3, "pressure": 10.2}'
```

## Step 12: Verify Setup

### 12.1 Test AWS Services

```bash
# Test Bedrock
python scripts/test-bedrock.py

# Test Timestream
python scripts/test-timestream.py

# Test Kinesis
python scripts/test-kinesis.py

# Test IoT Core
python scripts/test-iot-core.py
```

### 12.2 Run Basic API Test

```bash
# Start local API server (if available)
python backend/main.py

# In another terminal, test API
curl http://localhost:8000/health

# Test maintenance endpoint
curl -X POST http://localhost:8000/api/v1/maintenance \
  -H "Content-Type: application/json" \
  -d '{
    "equipment_id": "EQ-001",
    "sensor_data": {
      "temperature": 75.5,
      "vibration": 2.3,
      "pressure": 10.2
    }
  }'
```

## Troubleshooting

### Issue: IoT Device Connection Failed

**Solution**:
1. Verify certificate and private key files exist
2. Check IoT endpoint is correct
3. Ensure policy is attached to certificate
4. Verify thing is registered

```bash
# Check thing registration
aws iot describe-thing --thing-name sensor-001

# Check certificate
aws iot describe-certificate --certificate-id <cert-id>
```

### Issue: Timestream Access Denied

**Solution**:
1. Check IAM permissions for Timestream
2. Verify database and table exist
3. Ensure region is correct

```bash
# Check IAM permissions
aws iam get-role-policy \
  --role-name YOUR_ROLE \
  --policy-name TimestreamAccess
```

### Issue: Kinesis Stream Not Found

**Solution**:
1. Verify stream name is correct
2. Check stream exists in the region
3. Ensure IAM permissions are set

```bash
# List streams
aws kinesis list-streams --region us-east-1
```

## Validation Checklist

Before proceeding to Module 2, verify:

- [ ] AWS CLI configured and working
- [ ] Bedrock model access enabled
- [ ] IoT Core thing group and policy created
- [ ] Timestream database and table created
- [ ] Kinesis streams created
- [ ] Python virtual environment created and activated
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] IoT device registered and connected
- [ ] Sample data loaded
- [ ] Basic API tests passing

## Next Steps

Congratulations! You've completed Module 1. You're now ready to:

1. **Proceed to Module 2**: [Predictive Maintenance](./module-2-predictive-maintenance.md)
2. **Explore the Codebase**: Review the project structure
3. **Review Architecture**: Read the [Architecture Guide](../../architecture.md)

## Additional Resources

- [AWS IoT Core Documentation](https://docs.aws.amazon.com/iot/)
- [Amazon Timestream Documentation](https://docs.aws.amazon.com/timestream/)
- [Amazon Kinesis Documentation](https://docs.aws.amazon.com/kinesis/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

**Ready for Module 2? Let's build the predictive maintenance system! 🚀**

