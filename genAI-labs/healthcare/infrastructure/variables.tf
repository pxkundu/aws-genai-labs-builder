# Healthcare ChatGPT Clone - Terraform Variables
# This file defines all the variables used in the Terraform configuration

# General Configuration
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "healthcare-chatgpt"
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = "healthcare-team"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

# EC2 Configuration
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_pair_name" {
  description = "Name of the AWS key pair"
  type        = string
  default     = ""
}

variable "ami_id" {
  description = "AMI ID for EC2 instance (Ubuntu 22.04 LTS)"
  type        = string
  default     = "ami-0c02fb55956c7d316" # Ubuntu 22.04 LTS in us-east-1
}

# Application Configuration
variable "openwebui_port" {
  description = "Port for OpenWebUI application"
  type        = number
  default     = 8080
}

variable "api_port" {
  description = "Port for backend API"
  type        = number
  default     = 8000
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS Aurora instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
  default     = ""
}

variable "db_name" {
  description = "Initial database name"
  type        = string
  default     = "healthcare_chat"
}

variable "backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Backup window"
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Maintenance window"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

# API Keys and Secrets
variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
  default     = ""
}

# Monitoring Configuration
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

# Environment-specific overrides
variable "enable_deletion_protection" {
  description = "Enable deletion protection for RDS cluster"
  type        = bool
  default     = false
}

variable "enable_performance_insights" {
  description = "Enable Performance Insights for RDS"
  type        = bool
  default     = true
}

variable "enable_encryption" {
  description = "Enable encryption for RDS and S3"
  type        = bool
  default     = true
}

# Scaling Configuration
variable "min_capacity" {
  description = "Minimum Aurora Serverless capacity"
  type        = number
  default     = 0.5
}

variable "max_capacity" {
  description = "Maximum Aurora Serverless capacity"
  type        = number
  default     = 16
}

# Security Configuration
variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Restrict this in production
}

variable "enable_ssl" {
  description = "Enable SSL/TLS for the application"
  type        = bool
  default     = true
}

# Cost Optimization
variable "enable_spot_instances" {
  description = "Use spot instances for cost optimization"
  type        = bool
  default     = false
}

variable "enable_auto_shutdown" {
  description = "Enable automatic shutdown for dev environments"
  type        = bool
  default     = false
}
