# Legal Compliance AI Platform - Variables

# General Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "legal-compliance-ai"
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

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnets" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

# Database Configuration
variable "database_name" {
  description = "Name of the database"
  type        = string
  default     = "legal_compliance"
}

variable "database_username" {
  description = "Database username"
  type        = string
  default     = "legal_user"
}

variable "database_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "database_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "database_allocated_storage" {
  description = "Initial allocated storage for RDS instance (GB)"
  type        = number
  default     = 20
}

variable "database_max_allocated_storage" {
  description = "Maximum allocated storage for RDS instance (GB)"
  type        = number
  default     = 100
}

variable "database_backup_retention_period" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 7
}

variable "database_backup_window" {
  description = "Daily time range for database backups"
  type        = string
  default     = "03:00-04:00"
}

variable "database_maintenance_window" {
  description = "Weekly time range for database maintenance"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

# Redis Configuration
variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes"
  type        = number
  default     = 1
}

variable "redis_parameter_group_name" {
  description = "Redis parameter group name"
  type        = string
  default     = "default.redis7"
}

# ECS Configuration
variable "backend_cpu" {
  description = "CPU units for backend task"
  type        = number
  default     = 512
}

variable "backend_memory" {
  description = "Memory for backend task (MB)"
  type        = number
  default     = 1024
}

variable "frontend_cpu" {
  description = "CPU units for frontend task"
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Memory for frontend task (MB)"
  type        = number
  default     = 512
}

# SSL Certificate
variable "ssl_certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS"
  type        = string
  default     = ""
}

# DNS Configuration
variable "create_dns" {
  description = "Whether to create Route 53 DNS records"
  type        = bool
  default     = false
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

# CloudFront Configuration
variable "enable_cloudfront" {
  description = "Whether to enable CloudFront distribution"
  type        = bool
  default     = false
}

# Logging Configuration
variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

# API Keys (sensitive)
variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "google_api_key" {
  description = "Google API key"
  type        = string
  sensitive   = true
  default     = ""
}

# Scaling Configuration
variable "min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 10
}

variable "target_cpu_utilization" {
  description = "Target CPU utilization for auto scaling"
  type        = number
  default     = 70
}

variable "target_memory_utilization" {
  description = "Target memory utilization for auto scaling"
  type        = number
  default     = 80
}

# Monitoring Configuration
variable "enable_detailed_monitoring" {
  description = "Enable detailed CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarms"
  type        = string
  default     = ""
}

# Security Configuration
variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "enable_waf" {
  description = "Enable AWS WAF for the application"
  type        = bool
  default     = false
}

# Cost Optimization
variable "enable_spot_instances" {
  description = "Enable spot instances for cost optimization"
  type        = bool
  default     = false
}

variable "reserved_capacity" {
  description = "Enable reserved capacity for cost optimization"
  type        = bool
  default     = false
}

# Backup Configuration
variable "enable_automated_backups" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "backup_schedule" {
  description = "Cron expression for backup schedule"
  type        = string
  default     = "0 2 * * *"  # Daily at 2 AM
}

# Compliance Configuration
variable "enable_encryption_at_rest" {
  description = "Enable encryption at rest for all resources"
  type        = bool
  default     = true
}

variable "enable_encryption_in_transit" {
  description = "Enable encryption in transit"
  type        = bool
  default     = true
}

variable "compliance_standard" {
  description = "Compliance standard to follow (SOC2, HIPAA, GDPR)"
  type        = string
  default     = "SOC2"
  
  validation {
    condition     = contains(["SOC2", "HIPAA", "GDPR", "NONE"], var.compliance_standard)
    error_message = "Compliance standard must be one of: SOC2, HIPAA, GDPR, NONE."
  }
}

# Performance Configuration
variable "enable_gpu_acceleration" {
  description = "Enable GPU acceleration for AI workloads"
  type        = bool
  default     = false
}

variable "cache_ttl" {
  description = "Default cache TTL in seconds"
  type        = number
  default     = 3600
}

variable "rate_limit_requests_per_minute" {
  description = "Rate limit for requests per minute"
  type        = number
  default     = 100
}

# Development Configuration
variable "enable_debug_logging" {
  description = "Enable debug logging"
  type        = bool
  default     = false
}

variable "enable_development_tools" {
  description = "Enable development tools and debugging"
  type        = bool
  default     = false
}

# Multi-region Configuration
variable "enable_multi_region" {
  description = "Enable multi-region deployment"
  type        = bool
  default     = false
}

variable "secondary_regions" {
  description = "List of secondary regions for deployment"
  type        = list(string)
  default     = []
}

# Disaster Recovery
variable "enable_disaster_recovery" {
  description = "Enable disaster recovery setup"
  type        = bool
  default     = false
}

variable "dr_backup_retention_days" {
  description = "Number of days to retain DR backups"
  type        = number
  default     = 30
}
