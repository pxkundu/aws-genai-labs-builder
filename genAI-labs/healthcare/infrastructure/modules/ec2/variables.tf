# EC2 Module Variables

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where EC2 will be created"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for EC2"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group IDs for EC2"
  type        = list(string)
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_pair_name" {
  description = "Name of the AWS key pair"
  type        = string
  default     = ""
}

variable "ami_id" {
  description = "AMI ID for EC2 instance"
  type        = string
  default     = ""
}

variable "openwebui_port" {
  description = "Port for OpenWebUI application"
  type        = number
  default     = 8080
}

variable "api_port" {
  description = "Port for backend API"
  type        = number
  default     = 8000
}

variable "db_endpoint" {
  description = "Database endpoint"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "knowledge_base_bucket" {
  description = "S3 bucket name for knowledge base"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "ec2_instance_profile_name" {
  description = "EC2 instance profile name"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
