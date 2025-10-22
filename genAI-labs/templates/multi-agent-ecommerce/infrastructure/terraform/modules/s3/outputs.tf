# Outputs for S3 Module

output "data_bucket_name" {
  description = "Name of the data S3 bucket"
  value       = aws_s3_bucket.data.bucket
}

output "data_bucket_arn" {
  description = "ARN of the data S3 bucket"
  value       = aws_s3_bucket.data.arn
}

output "data_bucket_domain_name" {
  description = "Domain name of the data S3 bucket"
  value       = aws_s3_bucket.data.bucket_domain_name
}

output "data_bucket_regional_domain_name" {
  description = "Regional domain name of the data S3 bucket"
  value       = aws_s3_bucket.data.bucket_regional_domain_name
}

output "logs_bucket_name" {
  description = "Name of the logs S3 bucket"
  value       = aws_s3_bucket.logs.bucket
}

output "logs_bucket_arn" {
  description = "ARN of the logs S3 bucket"
  value       = aws_s3_bucket.logs.arn
}

output "logs_bucket_domain_name" {
  description = "Domain name of the logs S3 bucket"
  value       = aws_s3_bucket.logs.bucket_domain_name
}

output "logs_bucket_regional_domain_name" {
  description = "Regional domain name of the logs S3 bucket"
  value       = aws_s3_bucket.logs.bucket_regional_domain_name
}
