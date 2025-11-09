output "sns_topic_arn" {
  value       = aws_sns_topic.alerts.arn
  description = "SNS topic for smart alerts"
}

output "lambda_function_name" {
  value       = aws_lambda_function.llm_alert.function_name
  description = "LLM enrichment Lambda"
}

output "eventbridge_rule_arn" {
  value       = aws_eventbridge_rule.cloudwatch_alarm.arn
  description = "EventBridge rule ARN"
}
