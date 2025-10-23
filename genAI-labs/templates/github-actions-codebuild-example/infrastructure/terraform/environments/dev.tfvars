# Development Environment Configuration

# Basic Configuration
environment = "dev"
aws_region  = "us-east-1"
project_name = "github-actions-codebuild"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"
availability_zones_count = 2
public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]

# Network Configuration
enable_nat_gateway = true

# GitHub Configuration
github_owner = "your-github-username"
github_repo = "your-repository"
github_token = ""  # Set this in your environment or use AWS Secrets Manager

# Monitoring Configuration
log_retention_days = 7
alarm_actions = []  # Add SNS topic ARNs for notifications
