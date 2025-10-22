# Production Environment Configuration

# Basic Configuration
environment = "prod"
aws_region  = "us-east-1"

# VPC Configuration
vpc_cidr = "10.2.0.0/16"
availability_zones_count = 3
public_subnets  = ["10.2.1.0/24", "10.2.2.0/24", "10.2.3.0/24"]
private_subnets = ["10.2.11.0/24", "10.2.12.0/24", "10.2.13.0/24"]
database_subnets = ["10.2.21.0/24", "10.2.22.0/24", "10.2.23.0/24"]

# Network Configuration
enable_nat_gateway = true
enable_vpn_gateway = false

# RDS Configuration
db_instance_class = "db.r6g.large"
db_allocated_storage = 500
db_max_allocated_storage = 2000
db_engine_version = "15.4"

# ElastiCache Configuration
redis_node_type = "cache.r6g.large"
redis_num_cache_nodes = 3
redis_parameter_group_name = "default.redis7"

# Lambda Configuration
lambda_runtime = "python3.11"
lambda_memory_size = 2048
lambda_timeout = 300

# Bedrock Configuration
bedrock_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
bedrock_embedding_model_id = "amazon.titan-embed-text-v1"

# Monitoring Configuration
log_retention_days = 30
enable_detailed_monitoring = true

# Security Configuration
enable_encryption = true
enable_backup = true
backup_retention_days = 30

# Cost Optimization
enable_auto_scaling = true
min_capacity = 3
max_capacity = 10

# Notification Configuration
notification_email = "admin@company.com"
enable_alerts = true

# Performance Configuration
enable_performance_insights = true
enable_enhanced_monitoring = true

# Compliance Configuration
enable_audit_logging = true
enable_data_classification = true

# Development Configuration
enable_debug_logging = false
enable_tracing = true
