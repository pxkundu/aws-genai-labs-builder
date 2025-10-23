# CodeBuild Module Outputs

output "project_name" {
  description = "Name of the CodeBuild project"
  value       = aws_codebuild_project.main.name
}

output "project_arn" {
  description = "ARN of the CodeBuild project"
  value       = aws_codebuild_project.main.arn
}

output "role_arn" {
  description = "ARN of the CodeBuild IAM role"
  value       = aws_iam_role.codebuild.arn
}

output "webhook_url" {
  description = "URL of the CodeBuild webhook"
  value       = aws_codebuild_webhook.main.payload_url
}
