output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "${aws_api_gateway_stage.api_stage.invoke_url}/generate"
}

output "code_bucket_name" {
  description = "S3 bucket name for code storage"
  value       = aws_s3_bucket.code_bucket.id
}

output "table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.code_table.name
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.code_generator.function_name
}

