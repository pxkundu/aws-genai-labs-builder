# Outputs for Multi-Agentic E-Commerce Platform

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.vpc.private_subnet_ids
}

output "database_subnet_ids" {
  description = "IDs of the database subnets"
  value       = module.vpc.database_subnet_ids
}

# KMS Outputs
output "kms_key_id" {
  description = "ID of the KMS key"
  value       = module.kms.key_id
  sensitive   = true
}

output "kms_key_arn" {
  description = "ARN of the KMS key"
  value       = module.kms.key_arn
  sensitive   = true
}

# S3 Outputs
output "data_bucket_name" {
  description = "Name of the data S3 bucket"
  value       = module.s3.data_bucket_name
}

output "data_bucket_arn" {
  description = "ARN of the data S3 bucket"
  value       = module.s3.data_bucket_arn
}

output "logs_bucket_name" {
  description = "Name of the logs S3 bucket"
  value       = module.s3.logs_bucket_name
}

output "logs_bucket_arn" {
  description = "ARN of the logs S3 bucket"
  value       = module.s3.logs_bucket_arn
}

# RDS Outputs
output "db_instance_id" {
  description = "ID of the RDS instance"
  value       = module.rds.db_instance_id
}

output "db_instance_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = module.rds.db_instance_endpoint
}

output "db_instance_arn" {
  description = "ARN of the RDS instance"
  value       = module.rds.db_instance_arn
}

output "db_security_group_id" {
  description = "ID of the database security group"
  value       = module.rds.db_security_group_id
}

# ElastiCache Outputs
output "redis_endpoint" {
  description = "Endpoint of the Redis cluster"
  value       = module.elasticache.redis_endpoint
}

output "redis_port" {
  description = "Port of the Redis cluster"
  value       = module.elasticache.redis_port
}

output "redis_replication_group_id" {
  description = "ID of the Redis replication group"
  value       = module.elasticache.replication_group_id
}

# OpenSearch Outputs
output "opensearch_collection_id" {
  description = "ID of the OpenSearch collection"
  value       = module.opensearch.collection_id
}

output "opensearch_collection_endpoint" {
  description = "Endpoint of the OpenSearch collection"
  value       = module.opensearch.collection_endpoint
}

output "opensearch_dashboard_endpoint" {
  description = "Dashboard endpoint of the OpenSearch collection"
  value       = module.opensearch.dashboard_endpoint
}

# Lambda Outputs
output "lambda_function_arns" {
  description = "ARNs of the Lambda functions"
  value       = module.lambda.function_arns
}

output "lambda_function_names" {
  description = "Names of the Lambda functions"
  value       = module.lambda.function_names
}

# Bedrock Outputs
output "bedrock_agent_ids" {
  description = "IDs of the Bedrock agents"
  value       = module.bedrock.agent_ids
}

output "bedrock_agent_arns" {
  description = "ARNs of the Bedrock agents"
  value       = module.bedrock.agent_arns
}

output "bedrock_knowledge_base_ids" {
  description = "IDs of the Bedrock knowledge bases"
  value       = module.bedrock.knowledge_base_ids
}

# API Gateway Outputs
output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = module.api_gateway.api_gateway_id
}

output "api_gateway_execution_arn" {
  description = "Execution ARN of the API Gateway"
  value       = module.api_gateway.api_gateway_execution_arn
}

output "api_gateway_invoke_url" {
  description = "Invoke URL of the API Gateway"
  value       = module.api_gateway.api_gateway_invoke_url
}

# CloudWatch Outputs
output "cloudwatch_dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = module.cloudwatch.dashboard_url
}

output "cloudwatch_alarm_arns" {
  description = "ARNs of the CloudWatch alarms"
  value       = module.cloudwatch.alarm_arns
}

# SNS Outputs
output "sns_topic_arns" {
  description = "ARNs of the SNS topics"
  value       = module.sns.topic_arns
}

# SQS Outputs
output "sqs_queue_arns" {
  description = "ARNs of the SQS queues"
  value       = module.sqs.queue_arns
}

output "sqs_queue_urls" {
  description = "URLs of the SQS queues"
  value       = module.sqs.queue_urls
}

# Security Outputs
output "security_group_ids" {
  description = "IDs of the security groups"
  value       = {
    vpc_security_group_id = module.vpc.vpc_security_group_id
    db_security_group_id  = module.rds.db_security_group_id
    redis_security_group_id = module.elasticache.security_group_id
  }
}

# IAM Outputs
output "iam_role_arns" {
  description = "ARNs of the IAM roles"
  value       = {
    lambda_execution_role_arn = module.lambda.execution_role_arn
    bedrock_agent_role_arn   = module.bedrock.agent_role_arn
  }
}

# Cost and Resource Information
output "estimated_monthly_cost" {
  description = "Estimated monthly cost for the infrastructure"
  value       = {
    rds_cost = "$${var.db_instance_class == \"db.t3.medium\" ? \"50-100\" : \"100-200\"}"
    elasticache_cost = "$${var.redis_node_type == \"cache.t3.micro\" ? \"20-40\" : \"40-80\"}"
    lambda_cost = "$${var.environment == \"prod\" ? \"50-100\" : \"10-20\"}"
    bedrock_cost = "$${var.environment == \"prod\" ? \"100-300\" : \"20-50\"}"
    total_estimated = "$${var.environment == \"prod\" ? \"220-720\" : \"100-190\"}"
  }
}

# Environment Information
output "environment_info" {
  description = "Information about the deployed environment"
  value       = {
    environment = var.environment
    region      = var.aws_region
    account_id  = data.aws_caller_identity.current.account_id
    project_name = var.project_name
    deployment_time = timestamp()
  }
}

# Connection Information
output "connection_info" {
  description = "Connection information for the deployed resources"
  value       = {
    database_endpoint = module.rds.db_instance_endpoint
    redis_endpoint    = module.elasticache.redis_endpoint
    api_endpoint      = module.api_gateway.api_gateway_invoke_url
    opensearch_endpoint = module.opensearch.collection_endpoint
  }
  sensitive = true
}

# Monitoring Information
output "monitoring_info" {
  description = "Monitoring and observability information"
  value       = {
    cloudwatch_dashboard = module.cloudwatch.dashboard_url
    log_groups = [
      "/aws/lambda/${local.name_prefix}-recommendation-handler",
      "/aws/lambda/${local.name_prefix}-customer-support-handler",
      "/aws/lambda/${local.name_prefix}-inventory-handler",
      "/aws/lambda/${local.name_prefix}-order-handler",
      "/aws/lambda/${local.name_prefix}-pricing-handler",
      "/aws/lambda/${local.name_prefix}-marketing-handler"
    ]
  }
}
