# Security Module - Healthcare ChatGPT Clone
# This module creates security groups and IAM roles for the healthcare application

# Security Group for EC2 (OpenWebUI)
resource "aws_security_group" "ec2" {
  name_prefix = "${var.environment}-ec2-"
  vpc_id      = var.vpc_id
  description = "Security group for EC2 instances running OpenWebUI"

  # HTTP access for OpenWebUI
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "OpenWebUI HTTP access"
  }

  # HTTPS access for OpenWebUI (if SSL is configured)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "OpenWebUI HTTPS access"
  }

  # Backend API access
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "Backend API access"
  }

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "SSH access"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-sg"
  })
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name_prefix = "${var.environment}-rds-"
  vpc_id      = var.vpc_id
  description = "Security group for RDS Aurora PostgreSQL"

  # PostgreSQL access from EC2
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2.id]
    description     = "PostgreSQL access from EC2"
  }

  # No outbound rules for RDS
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(var.tags, {
    Name = "${var.environment}-rds-sg"
  })
}

# IAM Role for EC2 Instance
resource "aws_iam_role" "ec2_role" {
  name = "${var.environment}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-role"
  })
}

# IAM Policy for EC2 to access S3
resource "aws_iam_policy" "ec2_s3_policy" {
  name        = "${var.environment}-ec2-s3-policy"
  description = "Policy for EC2 to access S3 knowledge base"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:GetObjectVersion"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-knowledge-base-${var.environment}-*",
          "arn:aws:s3:::${var.project_name}-knowledge-base-${var.environment}-*/*"
        ]
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-s3-policy"
  })
}

# IAM Policy for EC2 to access RDS
resource "aws_iam_policy" "ec2_rds_policy" {
  name        = "${var.environment}-ec2-rds-policy"
  description = "Policy for EC2 to access RDS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "rds-db:connect"
        ]
        Resource = [
          "arn:aws:rds-db:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:dbuser:${var.environment}-aurora-cluster/*"
        ]
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-rds-policy"
  })
}

# IAM Policy for EC2 to access Secrets Manager
resource "aws_iam_policy" "ec2_secrets_policy" {
  name        = "${var.environment}-ec2-secrets-policy"
  description = "Policy for EC2 to access Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:${var.environment}-rds-credentials*"
        ]
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-secrets-policy"
  })
}

# IAM Policy for EC2 to access Bedrock
resource "aws_iam_policy" "ec2_bedrock_policy" {
  name        = "${var.environment}-ec2-bedrock-policy"
  description = "Policy for EC2 to access AWS Bedrock"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-bedrock-policy"
  })
}

# IAM Policy for EC2 to access CloudWatch
resource "aws_iam_policy" "ec2_cloudwatch_policy" {
  name        = "${var.environment}-ec2-cloudwatch-policy"
  description = "Policy for EC2 to access CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams",
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-cloudwatch-policy"
  })
}

# Attach policies to EC2 role
resource "aws_iam_role_policy_attachment" "ec2_s3_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_s3_policy.arn
}

resource "aws_iam_role_policy_attachment" "ec2_rds_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_rds_policy.arn
}

resource "aws_iam_role_policy_attachment" "ec2_secrets_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_secrets_policy.arn
}

resource "aws_iam_role_policy_attachment" "ec2_bedrock_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_bedrock_policy.arn
}

resource "aws_iam_role_policy_attachment" "ec2_cloudwatch_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_cloudwatch_policy.arn
}

# Attach AWS managed policies
resource "aws_iam_role_policy_attachment" "ec2_ssm_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Instance Profile for EC2
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.environment}-ec2-profile"
  role = aws_iam_role.ec2_role.name

  tags = merge(var.tags, {
    Name = "${var.environment}-ec2-profile"
  })
}

# Data sources
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
