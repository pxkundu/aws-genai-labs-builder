# Module 1: Environment & Content Pipeline Setup

## Learning Objectives

By the end of this module, you will be able to:

- Set up S3 buckets and CloudFront for media storage and delivery
- Configure MediaConvert for video transcoding
- Create a basic content ingestion and processing pipeline
- Configure your local development environment
- Load sample media assets and metadata
- Verify your setup with basic API calls

## Prerequisites

- AWS Account with admin access
- AWS CLI installed and configured
- Python 3.11+ installed
- Git installed
- Code editor (VS Code recommended)

## Duration

**Estimated Time**: 60 minutes

## Step 1: AWS Account & CLI Setup

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

1. Navigate to the **Amazon Bedrock Console**
2. Go to **Model access** in the left navigation
3. Request access to:
   - Claude 3.5 Sonnet
   - Claude 3 Haiku

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
cd genAI-labs/media-entertainment

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

**Required Variables** (example):

```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id
ENVIRONMENT=development
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
S3_RAW_BUCKET=media-dev-raw
S3_PROCESSED_BUCKET=media-dev-processed
S3_GENERATED_BUCKET=media-dev-generated
```

## Step 4: Create S3 Buckets

### 4.1 Create Buckets for Media Assets

```bash
# Raw assets (uploads, source)
aws s3 mb s3://media-dev-raw --region us-east-1

# Processed assets (transcoded)
aws s3 mb s3://media-dev-processed --region us-east-1

# Generated assets (AI outputs)
aws s3 mb s3://media-dev-generated --region us-east-1

# Enable versioning (recommended for generated content)
aws s3api put-bucket-versioning \
  --bucket media-dev-generated \
  --versioning-configuration Status=Enabled
```

## Step 5: Configure CloudFront

> In most setups, CloudFront is provisioned via Terraform/CDK. For this module we’ll just verify configuration.

```bash
# List CloudFront distributions (if any)
aws cloudfront list-distributions
```

If using Terraform/CDK, ensure:
- An origin for `media-dev-processed` (and optionally `media-dev-generated`)
- Proper cache behaviors for media content

## Step 6: Configure MediaConvert

### 6.1 Get MediaConvert Endpoint

```bash
aws mediaconvert describe-endpoints \
  --region us-east-1
```

Save the endpoint URL in `config/mediaconvert-endpoint.json` or as an environment variable used by your code/scripts.

### 6.2 Create Basic Job Template (via console or IaC)

For this module, ensure at least one job template exists that:
- Takes input from `media-dev-raw`
- Outputs to `media-dev-processed`
- Produces H.264/H.265 MP4 outputs at desired resolutions

## Step 7: Set Up Basic Content Ingestion

### 7.1 Upload Sample Media

```bash
# Upload sample videos and images
aws s3 sync data/sample/videos/ s3://media-dev-raw/videos/
aws s3 sync data/sample/images/ s3://media-dev-raw/images/
```

### 7.2 Run Initial Content Pipeline Script

```bash
# Run setup script if provided
python scripts/setup-content-pipeline.py \
  --raw-bucket media-dev-raw \
  --processed-bucket media-dev-processed
```

This script typically:
- Creates initial folders/prefixes
- Optionally triggers sample MediaConvert jobs

## Step 8: Test MediaConvert Integration

### 8.1 Trigger Test Job

```bash
python scripts/test-mediaconvert-job.py \
  --input s3://media-dev-raw/videos/sample.mp4 \
  --output-prefix s3://media-dev-processed/tests/
```

### 8.2 Verify Output

```bash
aws s3 ls s3://media-dev-processed/tests/
```

## Step 9: Basic API Health Check

If a simple health endpoint is provided:

```bash
# Start local API (if applicable)
python backend/main.py

# Test locally
curl http://localhost:8000/health
```

## Step 10: Validation Checklist

Before proceeding to Module 2, verify:

- [ ] AWS CLI configured and working
- [ ] Bedrock model access enabled
- [ ] Python virtual environment created and activated
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] S3 buckets for raw/processed/generated created
- [ ] MediaConvert endpoint configured
- [ ] Sample media uploaded
- [ ] Test MediaConvert job succeeded
- [ ] (Optional) Local API health check passes

## Troubleshooting

### Issue: MediaConvert Job Fails

**Solution**:
1. Verify IAM role permissions for MediaConvert
2. Check input and output S3 paths
3. Review job details in the MediaConvert console

### Issue: Bedrock Access Denied

**Solution**:
1. Ensure model access is requested and approved
2. Check IAM permissions for Bedrock
3. Verify region (Bedrock may not be available in all regions)

### Issue: S3 Permission Errors

**Solution**:
1. Check bucket policies and IAM roles
2. Ensure your user/role has `s3:PutObject` and `s3:GetObject`

## Next Steps

Congratulations! You've completed Module 1. You're now ready to:

1. **Proceed to Module 2**: [AI Content Studio](./module-2-content-studio.md)
2. **Explore the Codebase**: Review the project structure and scripts
3. **Review Architecture**: Read the [Architecture Guide](../../architecture.md)

## Additional Resources

- [AWS Media Services Documentation](https://aws.amazon.com/media-services/resources/)
- [Amazon MediaConvert Documentation](https://docs.aws.amazon.com/mediaconvert/)
- [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Amazon CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)

---

**Ready for Module 2? Let’s build the AI Content Studio! 🎥🚀**


