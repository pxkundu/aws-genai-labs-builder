# S3 Module Outputs

output "knowledge_base_bucket_name" {
  description = "Name of the knowledge base S3 bucket"
  value       = aws_s3_bucket.knowledge_base.bucket
}

output "knowledge_base_bucket_arn" {
  description = "ARN of the knowledge base S3 bucket"
  value       = aws_s3_bucket.knowledge_base.arn
}

output "knowledge_base_bucket_domain_name" {
  description = "Domain name of the knowledge base S3 bucket"
  value       = aws_s3_bucket.knowledge_base.bucket_domain_name
}

output "knowledge_base_bucket_regional_domain_name" {
  description = "Regional domain name of the knowledge base S3 bucket"
  value       = aws_s3_bucket.knowledge_base.bucket_regional_domain_name
}

output "application_logs_bucket_name" {
  description = "Name of the application logs S3 bucket"
  value       = var.enable_logging_bucket ? aws_s3_bucket.application_logs[0].bucket : null
}

output "application_logs_bucket_arn" {
  description = "ARN of the application logs S3 bucket"
  value       = var.enable_logging_bucket ? aws_s3_bucket.application_logs[0].arn : null
}
