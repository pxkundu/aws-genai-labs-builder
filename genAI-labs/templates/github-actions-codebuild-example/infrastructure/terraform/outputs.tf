output "codebuild_project_name" {
  description = "CodeBuild Project Name"
  value       = aws_codebuild_project.github_actions.name
}

output "codebuild_project_arn" {
  description = "CodeBuild Project ARN"
  value       = aws_codebuild_project.github_actions.arn
}

output "codebuild_service_role_arn" {
  description = "CodeBuild Service Role ARN"
  value       = aws_iam_role.codebuild.arn
}

output "artifacts_bucket_name" {
  description = "S3 Bucket for Build Artifacts"
  value       = aws_s3_bucket.artifacts.bucket
}

output "artifacts_bucket_arn" {
  description = "S3 Bucket ARN for Build Artifacts"
  value       = aws_s3_bucket.artifacts.arn
}

output "log_group_name" {
  description = "CloudWatch Log Group Name"
  value       = aws_cloudwatch_log_group.codebuild.name
}

output "webhook_url" {
  description = "CodeBuild Webhook URL"
  value       = aws_codebuild_webhook.github_actions.payload_url
}

output "webhook_secret" {
  description = "CodeBuild Webhook Secret"
  value       = aws_codebuild_webhook.github_actions.secret
  sensitive   = true
}
