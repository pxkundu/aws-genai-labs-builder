# Healthcare ChatGPT Clone - Terraform Outputs
# This file defines all the outputs from the Terraform configuration

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

# EC2 Outputs
output "ec2_instance_id" {
  description = "ID of the EC2 instance"
  value       = module.ec2.instance_id
}

output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = module.ec2.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = module.ec2.public_dns
}

output "openwebui_url" {
  description = "URL to access OpenWebUI"
  value       = "http://${module.ec2.public_ip}:${var.openwebui_port}"
}

output "api_url" {
  description = "URL to access the backend API"
  value       = "http://${module.ec2.public_ip}:${var.api_port}"
}

# RDS Outputs
output "rds_cluster_id" {
  description = "ID of the RDS Aurora cluster"
  value       = module.rds.cluster_identifier
}

output "rds_cluster_endpoint" {
  description = "RDS Aurora cluster endpoint"
  value       = module.rds.cluster_endpoint
  sensitive   = true
}

output "rds_cluster_reader_endpoint" {
  description = "RDS Aurora cluster reader endpoint"
  value       = module.rds.cluster_reader_endpoint
  sensitive   = true
}

output "rds_cluster_port" {
  description = "RDS Aurora cluster port"
  value       = module.rds.cluster_port
}

# S3 Outputs
output "knowledge_base_bucket_name" {
  description = "Name of the S3 bucket for knowledge base"
  value       = module.s3.knowledge_base_bucket_name
}

output "knowledge_base_bucket_arn" {
  description = "ARN of the S3 bucket for knowledge base"
  value       = module.s3.knowledge_base_bucket_arn
}

output "knowledge_base_bucket_domain_name" {
  description = "Domain name of the S3 bucket for knowledge base"
  value       = module.s3.knowledge_base_bucket_domain_name
}

# Security Outputs
output "ec2_security_group_id" {
  description = "ID of the EC2 security group"
  value       = module.security.ec2_security_group_id
}

output "rds_security_group_id" {
  description = "ID of the RDS security group"
  value       = module.security.rds_security_group_id
}

# CloudWatch Outputs
output "cloudwatch_dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.application_logs.name
}

# Application Configuration Outputs
output "database_connection_string" {
  description = "Database connection string (without password)"
  value       = "postgresql://${var.db_username}@${module.rds.cluster_endpoint}:${module.rds.cluster_port}/${var.db_name}"
  sensitive   = true
}

output "application_config" {
  description = "Application configuration summary"
  value = {
    environment = var.environment
    region = var.aws_region
    openwebui_url = "http://${module.ec2.public_ip}:${var.openwebui_port}"
    api_url = "http://${module.ec2.public_ip}:${var.api_port}"
    database_host = module.rds.cluster_endpoint
    database_port = module.rds.cluster_port
    database_name = var.db_name
    knowledge_base_bucket = module.s3.knowledge_base_bucket_name
  }
  sensitive = true
}

# Deployment Instructions
output "deployment_instructions" {
  description = "Instructions for deploying the application"
  value = <<-EOT
    Healthcare ChatGPT Clone has been deployed successfully!
    
    Access URLs:
    - OpenWebUI: http://${module.ec2.public_ip}:${var.openwebui_port}
    - Backend API: http://${module.ec2.public_ip}:${var.api_port}
    - CloudWatch Dashboard: https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}
    
    Next Steps:
    1. SSH into the EC2 instance: ssh -i your-key.pem ubuntu@${module.ec2.public_ip}
    2. Check application status: sudo docker ps
    3. View logs: sudo docker logs healthcare-openwebui
    4. Configure your knowledge base in S3 bucket: ${module.s3.knowledge_base_bucket_name}
    
    Security Notes:
    - Change default database password
    - Configure proper SSL certificates
    - Restrict security group access in production
    - Enable CloudTrail for audit logging
    
    For more information, see the documentation in the docs/ folder.
  EOT
}
