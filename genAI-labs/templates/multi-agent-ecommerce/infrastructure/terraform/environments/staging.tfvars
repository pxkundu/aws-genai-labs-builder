# Staging Environment Configuration

# Basic Configuration
environment = "staging"
aws_region  = "us-east-1"

# VPC Configuration
vpc_cidr = "10.1.0.0/16"
availability_zones_count = 3
public_subnets  = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
private_subnets = ["10.1.11.0/24", "10.1.12.0/24", "10.1.13.0/24"]
database_subnets = ["10.1.21.0/24", "10.1.22.0/24", "10.1.23.0/24"]

# Network Configuration
enable_nat_gateway = true
enable_vpn_gateway = false

# RDS Configuration
db_instance_class = "db.t3.large"
db_allocated_storage = 200
db_max_allocated_storage = 1000
db_engine_version = "15.4"

# ElastiCache Configuration
redis_node_type = "cache.t3.small"
redis_num_cache_nodes = 2
redis_parameter_group_name = "default.redis7"

# Lambda Configuration
lambda_runtime = "python3.11"
lambda_memory_size = 1024
lambda_timeout = 300

# Bedrock Configuration
bedrock_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
bedrock_embedding_model_id = "amazon.titan-embed-text-v1"

# Monitoring Configuration
log_retention_days = 14
enable_detailed_monitoring = true

# Security Configuration
enable_encryption = true
enable_backup = true
backup_retention_days = 7

# Cost Optimization
enable_auto_scaling = true
min_capacity = 2
max_capacity = 5

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
