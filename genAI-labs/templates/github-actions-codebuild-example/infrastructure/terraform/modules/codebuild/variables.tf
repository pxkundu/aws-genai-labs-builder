# CodeBuild Module Variables

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for CodeBuild project"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for CodeBuild project"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security group IDs for CodeBuild project"
  type        = list(string)
}

variable "artifacts_bucket_arn" {
  description = "ARN of the artifacts bucket"
  type        = string
}

variable "artifacts_bucket_name" {
  description = "Name of the artifacts bucket"
  type        = string
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "github_token" {
  description = "GitHub personal access token"
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
