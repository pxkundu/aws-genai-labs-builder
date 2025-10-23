# Setup Guide

This guide will walk you through setting up GitHub Actions with AWS CodeBuild integration.

## Prerequisites

### Required Tools

- **AWS CLI v2.x** - [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **Terraform >= 1.0** - [Download](https://terraform.io/downloads)
- **Python 3.11+** - [Download](https://python.org/)
- **Docker** - [Installation Guide](https://docs.docker.com/get-docker/)
- **Git** - [Download](https://git-scm.com/)

### AWS Account Setup

1. **Create AWS Account**
   - Sign up for an AWS account if you don't have one
   - Complete the account verification process

2. **Create IAM User**
   ```bash
   # Create IAM user with programmatic access
   aws iam create-user --user-name github-actions-user
   
   # Attach policies
   aws iam attach-user-policy \
     --user-name github-actions-user \
     --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
   
   # Create access keys
   aws iam create-access-key --user-name github-actions-user
   ```

3. **Configure AWS CLI**
   ```bash
   aws configure
   # Enter your Access Key ID, Secret Access Key, Region, and Output format
   ```

## Quick Setup

### Option 1: Automated Setup (Recommended)

Run the setup script to automatically configure everything:

```bash
# Basic setup with defaults
./scripts/setup-aws.sh

# Custom environment and region
./scripts/setup-aws.sh production us-west-2

# Using different deployment method
./scripts/setup-aws.sh development us-east-1 terraform
```

### Option 2: Manual Setup

Follow these steps to set up the infrastructure manually.

## Manual Setup Steps

### Step 1: Clone and Prepare

```bash
git clone <your-repository-url>
cd github-actions-codebuild-example
```

### Step 2: Configure Environment

Create environment configuration files:

```bash
# Create environment config
cp config/development.json.example config/development.json
```

Edit `config/development.json`:
```json
{
  "environment": "development",
  "region": "us-east-1",
  "aws": {
    "account_id": "123456789012",
    "region": "us-east-1"
  },
  "github": {
    "owner": "your-github-username",
    "repo": "your-repository-name"
  },
  "codebuild": {
    "project_name": "github-actions-runner",
    "compute_type": "BUILD_GENERAL1_LARGE",
    "image": "aws/codebuild/standard:7.0"
  }
}
```

### Step 3: Deploy Infrastructure

Choose your preferred deployment method:

#### Using Terraform (Recommended)

```bash
cd infrastructure/terraform
terraform init
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"
```

#### Using CloudFormation

```bash
aws cloudformation deploy \
  --template-file infrastructure/cloudformation/codebuild-project.yml \
  --stack-name github-actions-codebuild \
  --capabilities CAPABILITY_NAMED_IAM
```

### Step 4: Configure GitHub Repository

1. **Add Repository Secrets**
   - Go to your GitHub repository
   - Navigate to Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `AWS_ACCESS_KEY_ID`: Your AWS access key
     - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
     - `AWS_ACCOUNT_ID`: Your AWS account ID

2. **Update Repository Configuration**
   - Update the GitHub owner and repository name in your infrastructure files
   - Commit and push the changes

### Step 5: Test the Setup

1. **Push to Main Branch**
   ```bash
   git add .
   git commit -m "Initial setup"
   git push origin main
   ```

2. **Monitor the Build**
   ```bash
   # Watch CodeBuild logs
   aws logs tail /aws/codebuild/github-actions-runner --follow
   
   # Check build status
   aws codebuild list-builds-for-project --project-name github-actions-runner
   ```

## Configuration Options

### Environment Variables

Set these environment variables for customization:

```bash
export AWS_REGION=us-east-1
export ENVIRONMENT=development
export CODEBUILD_PROJECT_NAME=github-actions-runner
export ECR_REPOSITORY=github-actions-app
export DYNAMODB_TABLE=github-actions-logs
export S3_BUCKET=github-actions-artifacts
```

### GitHub Actions Variables

Configure these in your GitHub repository:

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | `us-east-1` |
| `ECR_REPOSITORY` | ECR repository name | `github-actions-app` |
| `CODEBUILD_PROJECT` | CodeBuild project name | `github-actions-runner` |

### CodeBuild Environment

Customize the CodeBuild environment:

```yaml
environment:
  computeType: BUILD_GENERAL1_LARGE  # or BUILD_GENERAL1_MEDIUM
  image: aws/codebuild/standard:7.0
  type: LINUX_CONTAINER
  privilegedMode: true
  environmentVariables:
    - name: CUSTOM_VAR
      value: custom-value
```

## Verification

### Check Infrastructure

```bash
# Verify CodeBuild project
aws codebuild describe-projects --names github-actions-runner

# Check ECR repository
aws ecr describe-repositories --repository-names github-actions-app

# Verify DynamoDB table
aws dynamodb describe-table --table-name github-actions-logs

# Check S3 bucket
aws s3api head-bucket --bucket github-actions-artifacts-123456789012-us-east-1
```

### Test GitHub Integration

1. **Create a test commit**
   ```bash
   echo "# Test" > test.md
   git add test.md
   git commit -m "Test GitHub Actions integration"
   git push origin main
   ```

2. **Monitor the workflow**
   - Go to your GitHub repository
   - Click on the "Actions" tab
   - Watch the workflow execution

3. **Check build logs**
   ```bash
   # Get latest build ID
   BUILD_ID=$(aws codebuild list-builds-for-project \
     --project-name github-actions-runner \
     --query 'ids[0]' --output text)
   
   # Get build details
   aws codebuild batch-get-builds --ids $BUILD_ID
   ```

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   ```bash
   # Check IAM permissions
   aws sts get-caller-identity
   aws iam list-attached-user-policies --user-name github-actions-user
   ```

2. **VPC Connectivity Issues**
   ```bash
   # Verify VPC configuration
   aws ec2 describe-vpcs --vpc-ids vpc-xxxxxxxxx
   aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx
   ```

3. **Build Failures**
   ```bash
   # Check build logs
   aws logs describe-log-streams \
     --log-group-name /aws/codebuild/github-actions-runner
   
   # Get specific log events
   aws logs get-log-events \
     --log-group-name /aws/codebuild/github-actions-runner \
     --log-stream-name <log-stream-name>
   ```

### Debug Commands

```bash
# Test AWS connectivity
aws sts get-caller-identity

# Test GitHub connectivity
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user

# Test Docker build locally
docker build -t test-app .

# Test application locally
python src/app/main.py
```

## Next Steps

After successful setup:

1. **Customize the Application**
   - Modify `src/app/main.py` for your specific use case
   - Update tests in `src/tests/`
   - Add additional endpoints as needed

2. **Configure Monitoring**
   - Set up CloudWatch alarms
   - Configure log aggregation
   - Set up cost monitoring

3. **Implement Security**
   - Review IAM policies
   - Enable VPC flow logs
   - Set up security scanning

4. **Scale and Optimize**
   - Adjust CodeBuild compute types
   - Optimize Docker images
   - Implement caching strategies

## Support

For additional help:

- Check the [Troubleshooting Guide](troubleshooting.md)
- Review [Architecture Documentation](architecture.md)
- Open an issue in the repository
- Consult AWS and GitHub documentation
