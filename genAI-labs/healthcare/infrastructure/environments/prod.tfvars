# Production Environment Configuration
# Healthcare ChatGPT Clone - Production Environment

# General Configuration
aws_region = "us-east-1"
environment = "prod"
project_name = "healthcare-chatgpt"
owner = "healthcare-team"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"
public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.10.0/24", "10.0.20.0/24"]

# EC2 Configuration
instance_type = "t3.large"  # Larger instance for production
key_pair_name = "healthcare-prod-key"  # Replace with your key pair name
ami_id = ""  # Will use latest Ubuntu 22.04 LTS

# Application Configuration
openwebui_port = 8080
api_port = 8000

# Database Configuration
db_instance_class = "db.r6g.large"  # Larger database instance
db_engine_version = "15.4"
db_username = "postgres"
db_password = ""  # Will be generated automatically
db_name = "healthcare_chat"

# Backup and Maintenance
backup_retention_period = 30  # Longer retention for production
backup_window = "03:00-04:00"
maintenance_window = "sun:04:00-sun:05:00"

# API Keys (set these via environment variables or Terraform CLI)
openai_api_key = ""  # Set via TF_VAR_openai_api_key environment variable

# Monitoring Configuration
log_retention_days = 90  # Longer retention for production

# Environment-specific overrides
enable_deletion_protection = true  # Enable deletion protection for production
enable_performance_insights = true
enable_encryption = true

# Scaling Configuration
min_capacity = 2  # Higher minimum capacity for production
max_capacity = 16

# Security Configuration
allowed_cidr_blocks = ["10.0.0.0/16"]  # Restrict to VPC only

# Cost Optimization
enable_spot_instances = false
enable_auto_shutdown = false  # No auto shutdown for production
