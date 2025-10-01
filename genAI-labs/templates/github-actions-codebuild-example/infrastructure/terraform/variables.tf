variable "vpc_id" {
  description = "VPC ID for CodeBuild project"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for CodeBuild project"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security Group IDs for CodeBuild project"
  type        = list(string)
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "your-github-username"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "your-repository"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "github-actions-codebuild"
}
