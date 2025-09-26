#!/bin/bash

# Healthcare ChatGPT Clone - Deployment Script
# This script deploys the complete healthcare ChatGPT clone application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-us-east-1}

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if required tools are installed
    command -v terraform >/dev/null 2>&1 || { log_error "Terraform is required but not installed. Aborting."; exit 1; }
    command -v aws >/dev/null 2>&1 || { log_error "AWS CLI is required but not installed. Aborting."; exit 1; }
    command -v docker >/dev/null 2>&1 || { log_error "Docker is required but not installed. Aborting."; exit 1; }
    
    # Check AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

validate_environment() {
    log_info "Validating environment configuration..."
    
    if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
        log_error "Invalid environment: $ENVIRONMENT. Must be one of: dev, staging, prod"
        exit 1
    fi
    
    # Check if environment file exists
    if [[ ! -f "$PROJECT_ROOT/infrastructure/environments/$ENVIRONMENT.tfvars" ]]; then
        log_error "Environment file not found: $PROJECT_ROOT/infrastructure/environments/$ENVIRONMENT.tfvars"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

setup_terraform_backend() {
    log_info "Setting up Terraform backend..."
    
    cd "$PROJECT_ROOT/infrastructure"
    
    # Create S3 bucket for Terraform state if it doesn't exist
    BUCKET_NAME="healthcare-chatgpt-terraform-state-$(date +%s)"
    
    if ! aws s3 ls "s3://$BUCKET_NAME" 2>/dev/null; then
        log_info "Creating S3 bucket for Terraform state: $BUCKET_NAME"
        aws s3 mb "s3://$BUCKET_NAME" --region "$AWS_REGION"
        aws s3api put-bucket-versioning --bucket "$BUCKET_NAME" --versioning-configuration Status=Enabled
        aws s3api put-bucket-encryption --bucket "$BUCKET_NAME" --server-side-encryption-configuration '{
            "Rules": [{
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }]
        }'
    fi
    
    # Create terraform.tf file for backend configuration
    cat > terraform.tf << EOF
terraform {
  backend "s3" {
    bucket = "$BUCKET_NAME"
    key    = "healthcare-chatgpt-clone/$ENVIRONMENT/terraform.tfstate"
    region = "$AWS_REGION"
  }
}
EOF
    
    log_success "Terraform backend configured"
}

deploy_infrastructure() {
    log_info "Deploying infrastructure for environment: $ENVIRONMENT"
    
    cd "$PROJECT_ROOT/infrastructure"
    
    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    log_info "Planning Terraform deployment..."
    terraform plan -var-file="environments/$ENVIRONMENT.tfvars" -out=tfplan
    
    # Apply deployment
    log_info "Applying Terraform deployment..."
    terraform apply tfplan
    
    # Get outputs
    log_info "Getting Terraform outputs..."
    terraform output -json > outputs.json
    
    log_success "Infrastructure deployed successfully"
}

setup_knowledge_base() {
    log_info "Setting up knowledge base in S3..."
    
    # Get S3 bucket name from Terraform outputs
    BUCKET_NAME=$(cd "$PROJECT_ROOT/infrastructure" && terraform output -raw knowledge_base_bucket_name)
    
    if [[ -z "$BUCKET_NAME" ]]; then
        log_error "Could not get S3 bucket name from Terraform outputs"
        exit 1
    fi
    
    # Upload sample knowledge base data
    if [[ -d "$PROJECT_ROOT/data/knowledge_base" ]]; then
        log_info "Uploading knowledge base data to S3..."
        aws s3 sync "$PROJECT_ROOT/data/knowledge_base/" "s3://$BUCKET_NAME/" --delete
        log_success "Knowledge base uploaded to S3"
    else
        log_warning "Knowledge base directory not found. Creating sample data..."
        mkdir -p "$PROJECT_ROOT/data/knowledge_base/sample"
        echo "Sample healthcare knowledge base content" > "$PROJECT_ROOT/data/knowledge_base/sample/README.txt"
        aws s3 sync "$PROJECT_ROOT/data/knowledge_base/" "s3://$BUCKET_NAME/" --delete
    fi
}

deploy_application() {
    log_info "Deploying application to EC2..."
    
    # Get EC2 public IP from Terraform outputs
    EC2_IP=$(cd "$PROJECT_ROOT/infrastructure" && terraform output -raw ec2_public_ip)
    
    if [[ -z "$EC2_IP" ]]; then
        log_error "Could not get EC2 public IP from Terraform outputs"
        exit 1
    fi
    
    # Wait for EC2 instance to be ready
    log_info "Waiting for EC2 instance to be ready..."
    sleep 60
    
    # Check if application is running
    log_info "Checking application status..."
    if curl -f "http://$EC2_IP:8080/health" >/dev/null 2>&1; then
        log_success "Application is running successfully"
    else
        log_warning "Application may still be starting up. Please check manually."
    fi
}

display_deployment_info() {
    log_info "Deployment completed successfully!"
    echo ""
    echo "=========================================="
    echo "Healthcare ChatGPT Clone Deployment Info"
    echo "=========================================="
    echo ""
    
    cd "$PROJECT_ROOT/infrastructure"
    
    # Display key information
    echo "Environment: $ENVIRONMENT"
    echo "AWS Region: $AWS_REGION"
    echo ""
    echo "Application URLs:"
    echo "  OpenWebUI: http://$(terraform output -raw ec2_public_ip):8080"
    echo "  Backend API: http://$(terraform output -raw ec2_public_ip):8000"
    echo ""
    echo "Database:"
    echo "  Endpoint: $(terraform output -raw rds_cluster_endpoint)"
    echo "  Port: $(terraform output -raw rds_cluster_port)"
    echo ""
    echo "S3 Knowledge Base:"
    echo "  Bucket: $(terraform output -raw knowledge_base_bucket_name)"
    echo ""
    echo "CloudWatch Dashboard:"
    echo "  URL: $(terraform output -raw cloudwatch_dashboard_url)"
    echo ""
    echo "Next Steps:"
    echo "1. SSH into the EC2 instance to check logs:"
    echo "   ssh -i your-key.pem ubuntu@$(terraform output -raw ec2_public_ip)"
    echo ""
    echo "2. Check application status:"
    echo "   sudo docker ps"
    echo ""
    echo "3. View application logs:"
    echo "   sudo docker logs healthcare-openwebui"
    echo ""
    echo "4. Configure your knowledge base in S3 bucket"
    echo ""
    echo "5. Set up SSL certificates for production use"
    echo ""
    echo "For more information, see the documentation in the docs/ folder."
    echo ""
}

# Main deployment flow
main() {
    log_info "Starting Healthcare ChatGPT Clone deployment for environment: $ENVIRONMENT"
    
    check_prerequisites
    validate_environment
    setup_terraform_backend
    deploy_infrastructure
    setup_knowledge_base
    deploy_application
    display_deployment_info
    
    log_success "Deployment completed successfully!"
}

# Run main function
main "$@"
