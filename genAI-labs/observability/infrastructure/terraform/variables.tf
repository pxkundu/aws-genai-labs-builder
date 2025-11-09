variable "aws_region" {
  description = "AWS region for the observability stack"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention period"
  type        = number
  default     = 30
}

variable "prompt_latency_threshold_ms" {
  description = "Latency threshold for CloudWatch alarm"
  type        = number
  default     = 1500
}

variable "custom_metric_namespace" {
  description = "Namespace for custom GenAI metrics"
  type        = string
  default     = "GenAI/Observability"
}

variable "enable_ai_ops" {
  description = "Deploy AI Ops Lambda workflow"
  type        = bool
  default     = true
}

variable "ai_ops_lambda_role_arn" {
  description = "IAM role ARN for AI Ops Lambda"
  type        = string
  default     = ""
}

variable "ai_ops_lambda_package" {
  description = "Path to zipped Lambda package"
  type        = string
  default     = "../scripts/monitoring/ai_ops_lambda.zip"
}

variable "security_lambda_arn" {
  description = "Lambda ARN for log subscription filter destination"
  type        = string
  default     = ""
}

variable "kms_key_id" {
  description = "Optional KMS key for log encryption"
  type        = string
  default     = null
}

variable "bedrock_model_id" {
  description = "Bedrock model used for AI Ops summaries"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "GenAI-Observability"
    ManagedBy   = "Terraform"
    CostCenter  = "AI-Platform"
  }
}
