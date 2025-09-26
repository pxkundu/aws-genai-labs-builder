# Healthcare ChatGPT Clone - Main Terraform Configuration
# This file defines the main infrastructure for the healthcare AI chat application

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "Healthcare-ChatGPT-Clone"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.owner
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  environment          = var.environment
  vpc_cidr            = var.vpc_cidr
  availability_zones  = data.aws_availability_zones.available.names
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  
  tags = {
    Name = "${var.project_name}-vpc-${var.environment}"
  }
}

# S3 Module for Knowledge Base
module "s3" {
  source = "./modules/s3"
  
  environment = var.environment
  project_name = var.project_name
  
  # Knowledge base bucket
  knowledge_base_bucket_name = "${var.project_name}-knowledge-base-${var.environment}-${random_id.bucket_suffix.hex}"
  
  tags = {
    Name = "${var.project_name}-s3-${var.environment}"
  }
}

# Security Module
module "security" {
  source = "./modules/security"
  
  environment = var.environment
  project_name = var.project_name
  vpc_id = module.vpc.vpc_id
  vpc_cidr = var.vpc_cidr
  allowed_cidr_blocks = var.allowed_cidr_blocks
  
  tags = {
    Name = "${var.project_name}-security-${var.environment}"
  }
}

# RDS Aurora PostgreSQL Module
module "rds" {
  source = "./modules/rds"
  
  environment = var.environment
  project_name = var.project_name
  
  # VPC Configuration
  vpc_id = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  security_group_ids = [module.security.rds_security_group_id]
  
  # Database Configuration
  db_instance_class = var.db_instance_class
  db_engine_version = var.db_engine_version
  db_username = var.db_username
  db_password = var.db_password
  db_name = var.db_name
  
  # Backup and Maintenance
  backup_retention_period = var.backup_retention_period
  backup_window = var.backup_window
  maintenance_window = var.maintenance_window
  enable_deletion_protection = var.enable_deletion_protection
  enable_performance_insights = var.enable_performance_insights
  min_capacity = var.min_capacity
  max_capacity = var.max_capacity
  
  tags = {
    Name = "${var.project_name}-rds-${var.environment}"
  }
}

# EC2 Module for OpenWebUI
module "ec2" {
  source = "./modules/ec2"
  
  environment = var.environment
  project_name = var.project_name
  
  # VPC Configuration
  vpc_id = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  security_group_ids = [module.security.ec2_security_group_id]
  
  # EC2 Configuration
  instance_type = var.instance_type
  key_pair_name = var.key_pair_name
  ami_id = var.ami_id
  
  # Application Configuration
  openwebui_port = var.openwebui_port
  api_port = var.api_port
  
  # Database Configuration
  db_endpoint = module.rds.cluster_endpoint
  db_username = var.db_username
  db_password = var.db_password
  db_name = var.db_name
  
  # S3 Configuration
  knowledge_base_bucket = module.s3.knowledge_base_bucket_name
  
  # API Keys
  openai_api_key = var.openai_api_key
  aws_region = var.aws_region
  
  tags = {
    Name = "${var.project_name}-ec2-${var.environment}"
  }
}

# Random ID for unique bucket naming
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "application_logs" {
  name              = "/aws/ec2/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_days
  
  tags = {
    Name = "${var.project_name}-logs-${var.environment}"
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-${var.environment}-dashboard"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        
        properties = {
          metrics = [
            ["AWS/EC2", "CPUUtilization", "InstanceId", module.ec2.instance_id],
            [".", "NetworkIn", "InstanceId", module.ec2.instance_id],
            [".", "NetworkOut", "InstanceId", module.ec2.instance_id]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "EC2 Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        
        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBClusterIdentifier", module.rds.cluster_identifier],
            [".", "DatabaseConnections", "DBClusterIdentifier", module.rds.cluster_identifier],
            [".", "FreeableMemory", "DBClusterIdentifier", module.rds.cluster_identifier]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "RDS Aurora Metrics"
          period  = 300
        }
      }
    ]
  })
}
