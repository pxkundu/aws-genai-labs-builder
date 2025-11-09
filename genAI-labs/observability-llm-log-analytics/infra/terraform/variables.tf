variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region"
}

variable "project" {
  type        = string
  default     = "llm-log-analytics"
}

variable "environment" {
  type        = string
  default     = "dev"
}

variable "bedrock_model_id" {
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
}

variable "opensearch_endpoint" {
  type        = string
  description = "OpenSearch HTTPS endpoint"
}

variable "opensearch_read_arn" {
  type        = string
  description = "ARN of OpenSearch index or domain for read access"
}

variable "lambda_package_key" {
  type        = string
  description = "S3 key for Lambda deployment package"
}

variable "slack_webhook_url" {
  type        = string
  default     = ""
}

variable "metric_namespace" {
  type        = string
  default     = "GenAI/Observability"
}

variable "latency_threshold_ms" {
  type        = number
  default     = 1500
}

variable "tags" {
  type = map(string)
  default = {
    Project   = "LLM-Log-Analytics"
    ManagedBy = "Terraform"
  }
}
