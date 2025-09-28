# Legal Compliance AI Platform - Outputs

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

# Database Outputs
output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = module.database.endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS instance port"
  value       = module.database.port
}

output "database_name" {
  description = "Database name"
  value       = module.database.database_name
}

# Redis Outputs
output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = module.redis.endpoint
  sensitive   = true
}

output "redis_port" {
  description = "Redis cluster port"
  value       = module.redis.port
}

# S3 Outputs
output "documents_bucket_name" {
  description = "Name of the legal documents S3 bucket"
  value       = module.storage.documents_bucket_name
}

output "documents_bucket_arn" {
  description = "ARN of the legal documents S3 bucket"
  value       = module.storage.documents_bucket_arn
}

output "logs_bucket_name" {
  description = "Name of the application logs S3 bucket"
  value       = module.storage.logs_bucket_name
}

output "logs_bucket_arn" {
  description = "ARN of the application logs S3 bucket"
  value       = module.storage.logs_bucket_arn
}

output "knowledge_bucket_name" {
  description = "Name of the legal knowledge base S3 bucket"
  value       = module.storage.knowledge_bucket_name
}

output "knowledge_bucket_arn" {
  description = "ARN of the legal knowledge base S3 bucket"
  value       = module.storage.knowledge_bucket_arn
}

# Load Balancer Outputs
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = module.alb.zone_id
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = module.alb.arn
}

# ECS Outputs
output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = module.ecs.cluster_id
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = module.ecs.cluster_arn
}

output "backend_service_name" {
  description = "Name of the backend ECS service"
  value       = module.ecs.backend_service_name
}

output "frontend_service_name" {
  description = "Name of the frontend ECS service"
  value       = module.ecs.frontend_service_name
}

# Security Group Outputs
output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = module.security_groups.alb_security_group_id
}

output "ecs_security_group_id" {
  description = "ID of the ECS security group"
  value       = module.security_groups.ecs_security_group_id
}

output "database_security_group_id" {
  description = "ID of the database security group"
  value       = module.security_groups.database_security_group_id
}

output "redis_security_group_id" {
  description = "ID of the Redis security group"
  value       = module.security_groups.redis_security_group_id
}

# CloudWatch Outputs
output "backend_log_group_name" {
  description = "Name of the backend CloudWatch log group"
  value       = aws_cloudwatch_log_group.backend_logs.name
}

output "frontend_log_group_name" {
  description = "Name of the frontend CloudWatch log group"
  value       = aws_cloudwatch_log_group.frontend_logs.name
}

# IAM Outputs
output "ecs_execution_role_arn" {
  description = "ARN of the ECS execution role"
  value       = aws_iam_role.ecs_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task_role.arn
}

# Secrets Manager Outputs
output "openai_secret_arn" {
  description = "ARN of the OpenAI API key secret"
  value       = aws_secretsmanager_secret.openai_api_key.arn
}

output "anthropic_secret_arn" {
  description = "ARN of the Anthropic API key secret"
  value       = aws_secretsmanager_secret.anthropic_api_key.arn
}

output "google_secret_arn" {
  description = "ARN of the Google API key secret"
  value       = aws_secretsmanager_secret.google_api_key.arn
}

# Route 53 Outputs
output "hosted_zone_id" {
  description = "ID of the Route 53 hosted zone"
  value       = var.create_dns ? aws_route53_zone.main[0].zone_id : null
}

output "domain_name" {
  description = "Domain name of the application"
  value       = var.create_dns ? var.domain_name : null
}

# CloudFront Outputs
output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.app[0].id : null
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = var.enable_cloudfront ? aws_cloudfront_distribution.app[0].domain_name : null
}

# Application URLs
output "application_url" {
  description = "URL of the deployed application"
  value       = var.create_dns ? "https://${var.domain_name}" : "https://${module.alb.dns_name}"
}

output "api_url" {
  description = "URL of the API endpoint"
  value       = var.create_dns ? "https://${var.domain_name}/api" : "https://${module.alb.dns_name}/api"
}

# Connection Information
output "database_connection_string" {
  description = "Database connection string (sensitive)"
  value       = "postgresql://${var.database_username}:${var.database_password}@${module.database.endpoint}:5432/${var.database_name}"
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis connection string (sensitive)"
  value       = "redis://${module.redis.endpoint}:6379/0"
  sensitive   = true
}

# Deployment Information
output "deployment_timestamp" {
  description = "Timestamp of the deployment"
  value       = timestamp()
}

output "terraform_version" {
  description = "Terraform version used for deployment"
  value       = ">= 1.0"
}

output "aws_provider_version" {
  description = "AWS provider version used for deployment"
  value       = "~> 5.0"
}

# Monitoring Information
output "cloudwatch_dashboard_url" {
  description = "URL to the CloudWatch dashboard"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${local.name_prefix}-dashboard"
}

output "ecs_console_url" {
  description = "URL to the ECS console"
  value       = "https://${var.aws_region}.console.aws.amazon.com/ecs/v2/clusters/${module.ecs.cluster_name}/services"
}

# Cost Information
output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown"
  value = {
    ecs_fargate = "~$50-100 (depending on usage)"
    rds         = "~$20-50 (depending on instance size)"
    redis       = "~$15-30 (depending on node size)"
    alb         = "~$20-40 (depending on traffic)"
    s3          = "~$5-20 (depending on storage)"
    cloudwatch  = "~$10-30 (depending on logs)"
    secrets     = "~$5-10 (depending on API calls)"
    total       = "~$125-280/month"
  }
}

# Security Information
output "security_notes" {
  description = "Important security considerations"
  value = {
    database_password = "Store in AWS Secrets Manager or use RDS IAM authentication"
    api_keys         = "All API keys are stored in AWS Secrets Manager"
    ssl_certificate  = "Ensure SSL certificate is properly configured for production"
    security_groups  = "Review security group rules for production deployment"
    waf             = "Consider enabling AWS WAF for additional protection"
  }
}

# Troubleshooting Information
output "troubleshooting_commands" {
  description = "Useful commands for troubleshooting"
  value = {
    check_ecs_tasks = "aws ecs list-tasks --cluster ${module.ecs.cluster_name}"
    check_logs      = "aws logs describe-log-groups --log-group-name-prefix /aws/ecs/${local.name_prefix}"
    check_alb       = "aws elbv2 describe-load-balancers --names ${local.name_prefix}-alb"
    check_rds       = "aws rds describe-db-instances --db-instance-identifier ${local.name_prefix}-db"
    check_redis     = "aws elasticache describe-cache-clusters --cache-cluster-id ${local.name_prefix}-redis"
  }
}
