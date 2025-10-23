# GitHub Actions CodeBuild Integration Infrastructure
# Terraform configuration for AWS services

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Application = "GitHub-Actions-CodeBuild"
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
    Application = "GitHub-Actions-CodeBuild"
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
  
  enable_nat_gateway = var.enable_nat_gateway
  enable_dns_hostnames = true
  enable_dns_support = true
  
  tags = local.common_tags
}

# KMS Module
module "kms" {
  source = "./modules/kms"
  
  name_prefix = local.name_prefix
  description = "KMS key for GitHub Actions CodeBuild encryption"
  
  tags = local.common_tags
}

# S3 Module
module "s3" {
  source = "./modules/s3"
  
  name_prefix = local.name_prefix
  kms_key_id = module.kms.key_id
  
  tags = local.common_tags
}

# CodeBuild Module
module "codebuild" {
  source = "./modules/codebuild"
  
  name_prefix = local.name_prefix
  vpc_id = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  security_group_ids = module.vpc.security_group_ids
  
  artifacts_bucket_arn = module.s3.artifacts_bucket_arn
  artifacts_bucket_name = module.s3.artifacts_bucket_name
  
  github_owner = var.github_owner
  github_repo = var.github_repo
  github_token = var.github_token
  
  kms_key_id = module.kms.key_id
  
  tags = local.common_tags
}

# CloudWatch Module
module "cloudwatch" {
  source = "./modules/cloudwatch"
  
  name_prefix = local.name_prefix
  
  codebuild_project_name = module.codebuild.project_name
  
  tags = local.common_tags
}