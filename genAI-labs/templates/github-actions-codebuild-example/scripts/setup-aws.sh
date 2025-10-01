#!/bin/bash

# GitHub Actions + AWS CodeBuild Setup Script
# This script sets up the AWS infrastructure for GitHub Actions integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check AWS CLI configuration
check_aws_config() {
    print_status "Checking AWS CLI configuration..."
    
    if ! command_exists aws; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "AWS CLI is configured correctly"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_tools=()
    
    if ! command_exists aws; then
        missing_tools+=("aws-cli")
    fi
    
    if ! command_exists jq; then
        missing_tools+=("jq")
    fi
    
    if ! command_exists docker; then
        missing_tools+=("docker")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        print_error "Please install them before proceeding."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to create ECR repository
create_ecr_repository() {
    local repository_name="$1"
    
    print_status "Creating ECR repository: $repository_name"
    
    if aws ecr describe-repositories --repository-names "$repository_name" >/dev/null 2>&1; then
        print_warning "ECR repository $repository_name already exists"
    else
        aws ecr create-repository --repository-name "$repository_name"
        print_success "ECR repository $repository_name created"
    fi
}

# Function to create DynamoDB table
create_dynamodb_table() {
    local table_name="$1"
    
    print_status "Creating DynamoDB table: $table_name"
    
    if aws dynamodb describe-table --table-name "$table_name" >/dev/null 2>&1; then
        print_warning "DynamoDB table $table_name already exists"
    else
        aws dynamodb create-table \
            --table-name "$table_name" \
            --attribute-definitions \
                AttributeName=event_id,AttributeType=S \
                AttributeName=timestamp,AttributeType=S \
            --key-schema \
                AttributeName=event_id,KeyType=HASH \
                AttributeName=timestamp,KeyType=RANGE \
            --billing-mode PAY_PER_REQUEST \
            --time-to-live-specification \
                AttributeName=ttl,Enabled=true
        
        print_success "DynamoDB table $table_name created"
    fi
}

# Function to create S3 bucket
create_s3_bucket() {
    local bucket_name="$1"
    local region="$2"
    
    print_status "Creating S3 bucket: $bucket_name"
    
    if aws s3api head-bucket --bucket "$bucket_name" 2>/dev/null; then
        print_warning "S3 bucket $bucket_name already exists"
    else
        if [ "$region" = "us-east-1" ]; then
            aws s3api create-bucket --bucket "$bucket_name"
        else
            aws s3api create-bucket --bucket "$bucket_name" --region "$region" \
                --create-bucket-configuration LocationConstraint="$region"
        fi
        
        # Enable versioning
        aws s3api put-bucket-versioning --bucket "$bucket_name" \
            --versioning-configuration Status=Enabled
        
        # Enable encryption
        aws s3api put-bucket-encryption --bucket "$bucket_name" \
            --server-side-encryption-configuration '{
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }'
        
        print_success "S3 bucket $bucket_name created with versioning and encryption"
    fi
}

# Function to deploy infrastructure
deploy_infrastructure() {
    local deployment_method="$1"
    local environment="$2"
    
    print_status "Deploying infrastructure using $deployment_method"
    
    case "$deployment_method" in
        "cdk")
            deploy_cdk "$environment"
            ;;
        "terraform")
            deploy_terraform "$environment"
            ;;
        "cloudformation")
            deploy_cloudformation "$environment"
            ;;
        *)
            print_error "Invalid deployment method: $deployment_method"
            print_error "Supported methods: cdk, terraform, cloudformation"
            exit 1
            ;;
    esac
}

# Function to deploy using CDK
deploy_cdk() {
    local environment="$1"
    
    print_status "Deploying infrastructure using AWS CDK"
    
    cd infrastructure/cdk
    
    if [ ! -f "package.json" ]; then
        print_error "package.json not found in infrastructure/cdk directory"
        exit 1
    fi
    
    # Install dependencies
    npm install
    
    # Bootstrap CDK if needed
    npx cdk bootstrap
    
    # Deploy the stack
    npx cdk deploy --all --context environment="$environment"
    
    print_success "CDK deployment completed"
}

# Function to deploy using Terraform
deploy_terraform() {
    local environment="$1"
    
    print_status "Deploying infrastructure using Terraform"
    
    cd infrastructure/terraform
    
    if [ ! -f "main.tf" ]; then
        print_error "main.tf not found in infrastructure/terraform directory"
        exit 1
    fi
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan -var="environment=$environment"
    
    # Apply deployment
    terraform apply -var="environment=$environment" -auto-approve
    
    print_success "Terraform deployment completed"
}

# Function to deploy using CloudFormation
deploy_cloudformation() {
    local environment="$1"
    
    print_status "Deploying infrastructure using CloudFormation"
    
    cd infrastructure/cloudformation
    
    if [ ! -f "codebuild-project.yml" ]; then
        print_error "codebuild-project.yml not found in infrastructure/cloudformation directory"
        exit 1
    fi
    
    local stack_name="github-actions-codebuild-$environment"
    
    # Deploy the stack
    aws cloudformation deploy \
        --template-file codebuild-project.yml \
        --stack-name "$stack_name" \
        --capabilities CAPABILITY_NAMED_IAM \
        --parameter-overrides Environment="$environment"
    
    print_success "CloudFormation deployment completed"
}

# Function to display setup summary
display_summary() {
    local environment="$1"
    local region="$2"
    
    print_success "Setup completed successfully!"
    echo
    print_status "Environment: $environment"
    print_status "AWS Region: $region"
    print_status "Account ID: $(aws sts get-caller-identity --query Account --output text)"
    echo
    print_status "Next steps:"
    echo "1. Configure GitHub repository secrets:"
    echo "   - AWS_ACCESS_KEY_ID"
    echo "   - AWS_SECRET_ACCESS_KEY"
    echo "   - AWS_ACCOUNT_ID"
    echo "2. Update GitHub repository configuration in infrastructure files"
    echo "3. Push your code to trigger the first build"
    echo
    print_status "Useful commands:"
    echo "- View CodeBuild logs: aws logs tail /aws/codebuild/github-actions-runner --follow"
    echo "- List builds: aws codebuild list-builds-for-project --project-name github-actions-runner-$environment"
    echo "- Get build details: aws codebuild batch-get-builds --ids <build-id>"
}

# Main function
main() {
    local environment="${1:-development}"
    local region="${2:-us-east-1}"
    local deployment_method="${3:-cdk}"
    
    print_status "Starting GitHub Actions + AWS CodeBuild setup"
    print_status "Environment: $environment"
    print_status "Region: $region"
    print_status "Deployment method: $deployment_method"
    echo
    
    # Check prerequisites
    check_prerequisites
    check_aws_config
    
    # Create required AWS resources
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    local ecr_repo="github-actions-app"
    local dynamodb_table="github-actions-logs-$environment"
    local s3_bucket="github-actions-artifacts-$account_id-$region"
    
    create_ecr_repository "$ecr_repo"
    create_dynamodb_table "$dynamodb_table"
    create_s3_bucket "$s3_bucket" "$region"
    
    # Deploy infrastructure
    deploy_infrastructure "$deployment_method" "$environment"
    
    # Display summary
    display_summary "$environment" "$region"
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 [environment] [region] [deployment-method]"
    echo
    echo "Arguments:"
    echo "  environment        Environment name (default: development)"
    echo "  region            AWS region (default: us-east-1)"
    echo "  deployment-method Deployment method: cdk, terraform, cloudformation (default: cdk)"
    echo
    echo "Examples:"
    echo "  $0 development us-east-1 cdk"
    echo "  $0 production us-west-2 terraform"
    echo "  $0 staging eu-west-1 cloudformation"
    exit 1
fi

# Run main function
main "$@"
