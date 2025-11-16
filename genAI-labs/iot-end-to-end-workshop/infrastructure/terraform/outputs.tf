output "iot_endpoint" {
  value       = aws_iot_endpoint.data.endpoint_address
  description = "AWS IoT Data-ATS endpoint."
}

output "iot_policy_name" {
  value       = module.iot_core.policy_name
  description = "IoT policy attached to devices."
}

output "kinesis_stream_name" {
  value       = module.streaming.kinesis_stream_name
  description = "Telemetry Kinesis Data Stream name."
}

output "firehose_bucket_name" {
  value       = module.streaming.firehose_bucket_name
  description = "S3 bucket name for raw telemetry (via Firehose)."
}

output "lambda_processor_arn" {
  value       = module.lambda_processor.lambda_function_arn
  description = "Lambda processor ARN."
}

output "iot_analytics_datastore_name" {
  value       = module.analytics.datastore_name
  description = "IoT Analytics datastore."
}

output "iot_events_detector_name" {
  value       = module.events.detector_model_name
  description = "IoT Events detector model."
}


