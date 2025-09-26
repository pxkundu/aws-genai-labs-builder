# S3 Module Variables

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "knowledge_base_bucket_name" {
  description = "Name of the knowledge base S3 bucket"
  type        = string
}

variable "enable_logging_bucket" {
  description = "Enable S3 bucket for application logs"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
