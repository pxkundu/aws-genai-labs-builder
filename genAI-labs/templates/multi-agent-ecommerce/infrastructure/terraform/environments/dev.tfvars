# Development Environment Configuration

# Basic Configuration
environment = "dev"
aws_region  = "us-east-1"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"
availability_zones_count = 2
public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]
database_subnets = ["10.0.21.0/24", "10.0.22.0/24"]

# Network Configuration
enable_nat_gateway = true
enable_vpn_gateway = false

# RDS Configuration
db_instance_class = "db.t3.medium"
db_allocated_storage = 100
db_max_allocated_storage = 500
db_engine_version = "15.4"

# ElastiCache Configuration
redis_node_type = "cache.t3.micro"
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
log_retention_days = 7
enable_detailed_monitoring = false

# Security Configuration
enable_encryption = true
enable_backup = true
backup_retention_days = 3

# Cost Optimization
enable_auto_scaling = false
min_capacity = 1
max_capacity = 3

# Notification Configuration
notification_email = ""
enable_alerts = false

# Performance Configuration
enable_performance_insights = false
enable_enhanced_monitoring = false

# Compliance Configuration
enable_audit_logging = false
enable_data_classification = false

# Development Configuration
enable_debug_logging = true
enable_tracing = true
