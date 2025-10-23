# Production Environment Configuration

# Basic Configuration
environment = "prod"
aws_region  = "us-east-1"
project_name = "github-actions-codebuild"

# VPC Configuration
vpc_cidr = "10.1.0.0/16"
availability_zones_count = 3
public_subnets  = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
private_subnets = ["10.1.11.0/24", "10.1.12.0/24", "10.1.13.0/24"]

# Network Configuration
enable_nat_gateway = true

# GitHub Configuration
github_owner = "your-github-username"
github_repo = "your-repository"
github_token = ""  # Set this in your environment or use AWS Secrets Manager

# Monitoring Configuration
log_retention_days = 30
alarm_actions = []  # Add SNS topic ARNs for notifications
