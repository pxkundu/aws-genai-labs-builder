# Outputs for GitHub Actions CodeBuild Infrastructure

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.vpc.private_subnet_ids
}

output "artifacts_bucket_name" {
  description = "Name of the artifacts bucket"
  value       = module.s3.artifacts_bucket_name
}

output "artifacts_bucket_arn" {
  description = "ARN of the artifacts bucket"
  value       = module.s3.artifacts_bucket_arn
}

output "logs_bucket_name" {
  description = "Name of the logs bucket"
  value       = module.s3.logs_bucket_name
}

output "logs_bucket_arn" {
  description = "ARN of the logs bucket"
  value       = module.s3.logs_bucket_arn
}

output "codebuild_project_name" {
  description = "Name of the CodeBuild project"
  value       = module.codebuild.project_name
}

output "codebuild_project_arn" {
  description = "ARN of the CodeBuild project"
  value       = module.codebuild.project_arn
}

output "codebuild_webhook_url" {
  description = "URL of the CodeBuild webhook"
  value       = module.codebuild.webhook_url
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = module.cloudwatch.log_group_name
}

output "cloudwatch_dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = module.cloudwatch.dashboard_url
}

output "kms_key_id" {
  description = "ID of the KMS key"
  value       = module.kms.key_id
}

output "kms_key_arn" {
  description = "ARN of the KMS key"
  value       = module.kms.key_arn
}