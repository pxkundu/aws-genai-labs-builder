# Legal Compliance AI Platform - Infrastructure as Code
# Terraform configuration for AWS deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    # Configure your S3 backend here
    # bucket = "your-terraform-state-bucket"
    # key    = "legal-compliance/terraform.tfstate"
    # region = "us-east-1"
  }
}

# Provider configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "Legal-Compliance-AI"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Local values
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"
  
  name_prefix = local.name_prefix
  cidr_block  = var.vpc_cidr
  
  availability_zones = data.aws_availability_zones.available.names
  public_subnets     = var.public_subnets
  private_subnets    = var.private_subnets
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  
  tags = local.common_tags
}

# Security Groups
module "security_groups" {
  source = "./modules/security"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  
  tags = local.common_tags
}

# RDS Database
module "database" {
  source = "./modules/rds"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
  
  security_group_ids = [module.security_groups.database_security_group_id]
  
  database_name     = var.database_name
  database_username = var.database_username
  database_password = var.database_password
  
  instance_class    = var.database_instance_class
  allocated_storage = var.database_allocated_storage
  max_allocated_storage = var.database_max_allocated_storage
  
  backup_retention_period = var.database_backup_retention_period
  backup_window          = var.database_backup_window
  maintenance_window     = var.database_maintenance_window
  
  tags = local.common_tags
}

# ElastiCache Redis
module "redis" {
  source = "./modules/redis"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
  
  security_group_ids = [module.security_groups.redis_security_group_id]
  
  node_type            = var.redis_node_type
  num_cache_nodes      = var.redis_num_cache_nodes
  parameter_group_name = var.redis_parameter_group_name
  
  tags = local.common_tags
}

# S3 Buckets
module "storage" {
  source = "./modules/s3"
  
  name_prefix = local.name_prefix
  
  # Legal documents bucket
  documents_bucket_name = "${local.name_prefix}-legal-documents"
  
  # Application logs bucket
  logs_bucket_name = "${local.name_prefix}-application-logs"
  
  # Legal knowledge base bucket
  knowledge_bucket_name = "${local.name_prefix}-legal-knowledge"
  
  tags = local.common_tags
}

# Application Load Balancer
module "alb" {
  source = "./modules/alb"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.public_subnet_ids
  
  security_group_ids = [module.security_groups.alb_security_group_id]
  
  # SSL Certificate (you'll need to create this separately)
  certificate_arn = var.ssl_certificate_arn
  
  tags = local.common_tags
}

# ECS Cluster
module "ecs" {
  source = "./modules/ecs"
  
  name_prefix = local.name_prefix
  
  # Backend service
  backend_task_definition = {
    family                   = "${local.name_prefix}-backend"
    cpu                     = var.backend_cpu
    memory                  = var.backend_memory
    requires_compatibilities = ["FARGATE"]
    network_mode            = "awsvpc"
    execution_role_arn      = aws_iam_role.ecs_execution_role.arn
    task_role_arn          = aws_iam_role.ecs_task_role.arn
    
    container_definitions = jsonencode([
      {
        name  = "backend"
        image = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${local.name_prefix}-backend:latest"
        
        portMappings = [
          {
            containerPort = 8000
            protocol      = "tcp"
          }
        ]
        
        environment = [
          {
            name  = "DATABASE_URL"
            value = "postgresql://${var.database_username}:${var.database_password}@${module.database.endpoint}:5432/${var.database_name}"
          },
          {
            name  = "REDIS_URL"
            value = "redis://${module.redis.endpoint}:6379/0"
          },
          {
            name  = "ENVIRONMENT"
            value = var.environment
          },
          {
            name  = "AWS_REGION"
            value = var.aws_region
          }
        ]
        
        secrets = [
          {
            name      = "OPENAI_API_KEY"
            valueFrom = aws_secretsmanager_secret.openai_api_key.arn
          },
          {
            name      = "ANTHROPIC_API_KEY"
            valueFrom = aws_secretsmanager_secret.anthropic_api_key.arn
          },
          {
            name      = "GOOGLE_API_KEY"
            valueFrom = aws_secretsmanager_secret.google_api_key.arn
          }
        ]
        
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group         = aws_cloudwatch_log_group.backend_logs.name
            awslogs-region        = var.aws_region
            awslogs-stream-prefix = "ecs"
          }
        }
        
        healthCheck = {
          command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
          interval    = 30
          timeout     = 5
          retries     = 3
          startPeriod = 60
        }
      }
    ])
  }
  
  # Frontend service
  frontend_task_definition = {
    family                   = "${local.name_prefix}-frontend"
    cpu                     = var.frontend_cpu
    memory                  = var.frontend_memory
    requires_compatibilities = ["FARGATE"]
    network_mode            = "awsvpc"
    execution_role_arn      = aws_iam_role.ecs_execution_role.arn
    task_role_arn          = aws_iam_role.ecs_task_role.arn
    
    container_definitions = jsonencode([
      {
        name  = "frontend"
        image = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${local.name_prefix}-frontend:latest"
        
        portMappings = [
          {
            containerPort = 3000
            protocol      = "tcp"
          }
        ]
        
        environment = [
          {
            name  = "NEXT_PUBLIC_API_URL"
            value = "https://${module.alb.dns_name}"
          },
          {
            name  = "NODE_ENV"
            value = var.environment == "production" ? "production" : "development"
          }
        ]
        
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group         = aws_cloudwatch_log_group.frontend_logs.name
            awslogs-region        = var.aws_region
            awslogs-stream-prefix = "ecs"
          }
        }
      }
    ])
  }
  
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
  
  security_group_ids = [module.security_groups.ecs_security_group_id]
  
  alb_target_group_arn = module.alb.target_group_arn
  
  tags = local.common_tags
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "backend_logs" {
  name              = "/aws/ecs/${local.name_prefix}-backend"
  retention_in_days = var.log_retention_days
  
  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "frontend_logs" {
  name              = "/aws/ecs/${local.name_prefix}-frontend"
  retention_in_days = var.log_retention_days
  
  tags = local.common_tags
}

# IAM Roles
resource "aws_iam_role" "ecs_execution_role" {
  name = "${local.name_prefix}-ecs-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_secrets" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = aws_iam_role_policy.ecs_secrets_access.arn
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${local.name_prefix}-ecs-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy" "ecs_task_policy" {
  name = "${local.name_prefix}-ecs-task-policy"
  role = aws_iam_role.ecs_task_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          module.storage.documents_bucket_arn,
          "${module.storage.documents_bucket_arn}/*",
          module.storage.logs_bucket_arn,
          "${module.storage.logs_bucket_arn}/*",
          module.storage.knowledge_bucket_arn,
          "${module.storage.knowledge_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_secrets_access" {
  name = "${local.name_prefix}-ecs-secrets-access"
  role = aws_iam_role.ecs_execution_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.openai_api_key.arn,
          aws_secretsmanager_secret.anthropic_api_key.arn,
          aws_secretsmanager_secret.google_api_key.arn
        ]
      }
    ]
  })
}

# Secrets Manager
resource "aws_secretsmanager_secret" "openai_api_key" {
  name        = "${local.name_prefix}-openai-api-key"
  description = "OpenAI API key for GPT models"
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "openai_api_key" {
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = var.openai_api_key
}

resource "aws_secretsmanager_secret" "anthropic_api_key" {
  name        = "${local.name_prefix}-anthropic-api-key"
  description = "Anthropic API key for Claude models"
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "anthropic_api_key" {
  secret_id     = aws_secretsmanager_secret.anthropic_api_key.id
  secret_string = var.anthropic_api_key
}

resource "aws_secretsmanager_secret" "google_api_key" {
  name        = "${local.name_prefix}-google-api-key"
  description = "Google API key for Gemini models"
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "google_api_key" {
  secret_id     = aws_secretsmanager_secret.google_api_key.id
  secret_string = var.google_api_key
}

# Route 53 (if using custom domain)
resource "aws_route53_zone" "main" {
  count = var.create_dns ? 1 : 0
  name  = var.domain_name
  
  tags = local.common_tags
}

resource "aws_route53_record" "app" {
  count   = var.create_dns ? 1 : 0
  zone_id = aws_route53_zone.main[0].zone_id
  name    = var.domain_name
  type    = "A"
  
  alias {
    name                   = module.alb.dns_name
    zone_id                = module.alb.zone_id
    evaluate_target_health = true
  }
}

# CloudFront Distribution (for better performance)
resource "aws_cloudfront_distribution" "app" {
  count = var.enable_cloudfront ? 1 : 0
  
  origin {
    domain_name = module.alb.dns_name
    origin_id   = "${local.name_prefix}-alb"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  
  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "${local.name_prefix}-alb"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
    
    forwarded_values {
      query_string = true
      cookies {
        forward = "none"
      }
    }
    
    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }
  
  tags = local.common_tags
}
