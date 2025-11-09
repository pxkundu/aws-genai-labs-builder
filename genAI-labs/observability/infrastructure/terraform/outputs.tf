output "log_group_name" {
  value       = aws_cloudwatch_log_group.app.name
  description = "Application CloudWatch log group"
}

output "xray_group_name" {
  value       = aws_xray_group.app.group_name
  description = "AWS X-Ray group name"
}

output "amp_workspace_id" {
  value       = aws_amp_workspace.this.id
  description = "Amazon Managed Service for Prometheus workspace ID"
}

output "grafana_workspace_id" {
  value       = aws_grafana_workspace.this.id
  description = "Amazon Managed Grafana workspace ID"
}

output "grafana_api_key" {
  value       = aws_grafana_workspace_api_key.datasource_writer.key
  description = "Grafana API key for data source provisioning"
  sensitive   = true
}

output "alerts_topic_arn" {
  value       = aws_sns_topic.alerts.arn
  description = "SNS topic ARN for alerts"
}
