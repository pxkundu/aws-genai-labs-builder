# CloudWatch Module Outputs

output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.codebuild.name
}

output "log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.codebuild.arn
}

output "dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = "https://${data.aws_region.current.name}.console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "alarm_names" {
  description = "Names of the CloudWatch alarms"
  value       = [
    aws_cloudwatch_metric_alarm.build_failure_rate.alarm_name,
    aws_cloudwatch_metric_alarm.build_duration.alarm_name
  ]
}
