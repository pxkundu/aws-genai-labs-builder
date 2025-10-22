# Multi-Agentic E-Commerce Platform Infrastructure
# Terraform configuration for AWS services

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Application = "Multi-Agent-Ecommerce"
      ManagedBy   = "Terraform"
      Project     = "AWS-GenAI-Labs"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# Local values
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Environment = var.environment
    Application = "Multi-Agent-Ecommerce"
    ManagedBy   = "Terraform"
    Project     = var.project_name
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  name_prefix = local.name_prefix
  vpc_cidr    = var.vpc_cidr
  azs         = slice(data.aws_availability_zones.available.names, 0, var.availability_zones_count)
  
  public_subnets = var.public_subnets
  private_subnets = var.private_subnets
  database_subnets = var.database_subnets
  
  enable_nat_gateway = var.enable_nat_gateway
  enable_vpn_gateway = var.enable_vpn_gateway
  enable_dns_hostnames = true
  enable_dns_support = true
  
  tags = local.common_tags
}

# KMS Module
module "kms" {
  source = "./modules/kms"
  
  name_prefix = local.name_prefix
  description = "KMS key for Multi-Agent E-commerce platform encryption"
  
  tags = local.common_tags
}

# S3 Module
module "s3" {
  source = "./modules/s3"
  
  name_prefix = local.name_prefix
  kms_key_id = module.kms.key_id
  
  tags = local.common_tags
}

# RDS Module
module "rds" {
  source = "./modules/rds"
  
  name_prefix = local.name_prefix
  vpc_id = module.vpc.vpc_id
  vpc_cidr = module.vpc.vpc_cidr_block
  private_subnet_ids = module.vpc.private_subnet_ids
  database_subnet_ids = module.vpc.database_subnet_ids
  
  db_instance_class = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_max_allocated_storage = var.db_max_allocated_storage
  db_engine_version = var.db_engine_version
  
  kms_key_id = module.kms.key_id
  
  tags = local.common_tags
}

# ElastiCache Module
module "elasticache" {
  source = "./modules/elasticache"
  
  name_prefix = local.name_prefix
  vpc_id = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  
  node_type = var.redis_node_type
  num_cache_nodes = var.redis_num_cache_nodes
  parameter_group_name = var.redis_parameter_group_name
  
  tags = local.common_tags
}

# OpenSearch Module
module "opensearch" {
  source = "./modules/opensearch"
  
  name_prefix = local.name_prefix
  kms_key_id = module.kms.key_id
  
  tags = local.common_tags
}

# Lambda Module
module "lambda" {
  source = "./modules/lambda"
  
  name_prefix = local.name_prefix
  vpc_id = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  
  kms_key_id = module.kms.key_id
  data_bucket_arn = module.s3.data_bucket_arn
  
  tags = local.common_tags
}

# Bedrock Module
module "bedrock" {
  source = "./modules/bedrock"
  
  name_prefix = local.name_prefix
  kms_key_id = module.kms.key_id
  data_bucket_arn = module.s3.data_bucket_arn
  data_bucket_name = module.s3.data_bucket_name
  
  lambda_functions = module.lambda.function_arns
  
  tags = local.common_tags
}

# API Gateway Module
module "api_gateway" {
  source = "./modules/api-gateway"
  
  name_prefix = local.name_prefix
  lambda_functions = module.lambda.function_arns
  
  tags = local.common_tags
}

# CloudWatch Module
module "cloudwatch" {
  source = "./modules/cloudwatch"
  
  name_prefix = local.name_prefix
  
  rds_instance_id = module.rds.db_instance_id
  elasticache_replication_group_id = module.elasticache.replication_group_id
  opensearch_collection_id = module.opensearch.collection_id
  
  tags = local.common_tags
}

# SNS Module
module "sns" {
  source = "./modules/sns"
  
  name_prefix = local.name_prefix
  
  tags = local.common_tags
}

# SQS Module
module "sqs" {
  source = "./modules/sqs"
  
  name_prefix = local.name_prefix
  kms_key_id = module.kms.key_id
  
  tags = local.common_tags
}
