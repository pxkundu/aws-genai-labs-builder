# S3 Module Outputs

output "artifacts_bucket_id" {
  description = "ID of the artifacts bucket"
  value       = aws_s3_bucket.artifacts.id
}

output "artifacts_bucket_arn" {
  description = "ARN of the artifacts bucket"
  value       = aws_s3_bucket.artifacts.arn
}

output "artifacts_bucket_name" {
  description = "Name of the artifacts bucket"
  value       = aws_s3_bucket.artifacts.bucket
}

output "logs_bucket_id" {
  description = "ID of the logs bucket"
  value       = aws_s3_bucket.logs.id
}

output "logs_bucket_arn" {
  description = "ARN of the logs bucket"
  value       = aws_s3_bucket.logs.arn
}

output "logs_bucket_name" {
  description = "Name of the logs bucket"
  value       = aws_s3_bucket.logs.bucket
}
